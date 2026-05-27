#!/usr/bin/env python3
"""compute_per_question_reliability.py

Compute per-question discriminative-judge reliability (r_q) and weight (w_q)
for ChronoLogic 0.2, stratified by reasoning_type and length_decile.

For each question, apply the logistic calibrator to gt/distractor pair deltas.
A pair is "correctly rejected" if P(anachronic | delta_clamped) > 0.5.
  delta_clamped = max(0, delta)   (candidate beating GT counts as zero gap)

raw_acc_q = correct_pairs / total_pairs

Stratified accuracies:
  reasoning_type_acc[t] = mean(raw_acc_q) over questions with that type
  length_decile_acc[d]  = mean(raw_acc_q) over questions in that decile

Per-question:
  r_q = min(reasoning_type_acc, length_decile_acc)
  w_q = max(2 * r_q - 1, 0) ** 2

Questions with no anachronic pairs get r_q = 0, w_q = 0.

Outputs:
  calibration/per_question_reliability_chronologic-0.2.jsonl

Usage:
    python modelasjudge/compute_per_question_reliability.py \\
        [--benchmark-data PATH] [--scored-anachronic PATH] \\
        [--calibrator PATH] [--out PATH]
"""

import argparse
import json
import pickle
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).parent
DEFAULT_BDATA = SCRIPT_DIR / "calibration" / "benchmark_data_for_discrim_calibration.jsonl"
DEFAULT_BDATA_NOMANUAL = SCRIPT_DIR / "calibration" / "benchmark_data_for_discrim_calibration_nomanual.jsonl"
DEFAULT_SCORED = SCRIPT_DIR / "calibration" / "anachronic_pairs_scored.jsonl"
DEFAULT_SCORED_NOMANUAL = SCRIPT_DIR / "calibration" / "anachronic_pairs_scored_nomanual.jsonl"
DEFAULT_CALIB = SCRIPT_DIR / "calibration" / "logistic_calibrator.pkl"
DEFAULT_CALIB_NOMANUAL = SCRIPT_DIR / "calibration" / "logistic_calibrator_nomanual.pkl"
DEFAULT_OUT = SCRIPT_DIR / "calibration" / "per_question_reliability_chronologic-0.2.jsonl"
DEFAULT_OUT_NOMANUAL = SCRIPT_DIR / "calibration" / "per_question_reliability_chronologic-0.2_nomanual.jsonl"
BERTCLASSIFY_DIR = SCRIPT_DIR.parent / "bertclassify"


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Compute per-question discriminative-judge reliability")
    p.add_argument("--benchmark-data", default=None, dest="benchmark_data",
                   help="Benchmark data JSONL (default depends on --nomanual)")
    p.add_argument("--scored-anachronic", default=None, dest="scored_anachronic",
                   help="Scored anachronic pairs JSONL (default depends on --nomanual)")
    p.add_argument("--calibrator", default=None, metavar="PATH",
                   help="Logistic calibrator pickle (default depends on --nomanual)")
    p.add_argument("--out", default=None, metavar="PATH",
                   help="Output JSONL path (default depends on --nomanual)")
    p.add_argument("--nomanual", action="store_true",
                   help="Use nomanual variants for all inputs and output.")
    args = p.parse_args(argv)
    if args.benchmark_data is None:
        args.benchmark_data = str(DEFAULT_BDATA_NOMANUAL if args.nomanual else DEFAULT_BDATA)
    if args.scored_anachronic is None:
        args.scored_anachronic = str(DEFAULT_SCORED_NOMANUAL if args.nomanual else DEFAULT_SCORED)
    if args.calibrator is None:
        args.calibrator = str(DEFAULT_CALIB_NOMANUAL if args.nomanual else DEFAULT_CALIB)
    if args.out is None:
        args.out = str(DEFAULT_OUT_NOMANUAL if args.nomanual else DEFAULT_OUT)
    return args


def make_features(deltas: np.ndarray) -> np.ndarray:
    return np.column_stack([deltas, deltas ** 2])


def main(argv=None):
    args = parse_args(argv)

    bdata_path = Path(args.benchmark_data)
    scored_path = Path(args.scored_anachronic)
    calib_path = Path(args.calibrator)
    out_path = Path(args.out)

    for p in [bdata_path, scored_path, calib_path]:
        if not p.exists():
            raise FileNotFoundError(f"Not found: {p}")

    # Load calibrator
    with open(calib_path, "rb") as f:
        artifact = pickle.load(f)
    clf = artifact["model"]

    # Load benchmark metadata (question → reasoning_type, length_decile)
    q_meta: dict[int, dict] = {}
    with open(bdata_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            qnum = rec["question_number"]
            q_meta[qnum] = {
                "reasoning_type": rec["reasoning_type"],
                "length_decile": rec["length_decile"],
            }

    # Group scored pair deltas by question_number
    q_deltas: dict[int, list[float]] = defaultdict(list)
    with open(scored_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            qnum = rec["question_number"]
            q_deltas[qnum].append(rec["delta"])

    # Compute raw_acc_q for each question (also store integer counts for Beta posteriors)
    q_raw_acc: dict[int, float] = {}
    q_counts: dict[int, tuple[int, int]] = {}  # (correct, total) per question
    for qnum, meta in q_meta.items():
        deltas = q_deltas.get(qnum, [])
        if not deltas:
            q_raw_acc[qnum] = 0.0
            q_counts[qnum] = (0, 0)
            continue
        arr = np.array(deltas)
        # delta_clamped: if distractor logit < gt logit (negative delta), clamp to 0
        arr_clamped = np.maximum(arr, 0.0)
        X = make_features(arr_clamped)
        probs = clf.predict_proba(X)[:, 1]
        correct = int((probs > 0.5).sum())
        q_raw_acc[qnum] = correct / len(deltas)
        q_counts[qnum] = (correct, len(deltas))

    # Stratify by reasoning_type — accumulate integer k/n per stratum for Beta posteriors
    type_groups: dict[str, list[float]] = defaultdict(list)
    type_kn: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for qnum, meta in q_meta.items():
        if q_deltas.get(qnum):   # only questions with at least one pair
            type_groups[meta["reasoning_type"]].append(q_raw_acc[qnum])
            type_kn[meta["reasoning_type"]].append(q_counts[qnum])
    type_acc: dict[str, float] = {t: float(np.mean(vs)) for t, vs in type_groups.items()}
    type_stratum_kn: dict[str, tuple[int, int]] = {
        t: (sum(k for k, _ in pairs), sum(n for _, n in pairs))
        for t, pairs in type_kn.items()
    }

    # Stratify by length_decile
    decile_groups: dict[int, list[float]] = defaultdict(list)
    decile_kn: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for qnum, meta in q_meta.items():
        if q_deltas.get(qnum):
            decile_groups[meta["length_decile"]].append(q_raw_acc[qnum])
            decile_kn[meta["length_decile"]].append(q_counts[qnum])
    decile_acc: dict[int, float] = {d: float(np.mean(vs)) for d, vs in decile_groups.items()}
    decile_stratum_kn: dict[int, tuple[int, int]] = {
        d: (sum(k for k, _ in pairs), sum(n for _, n in pairs))
        for d, pairs in decile_kn.items()
    }

    # Compute r_q and w_q for each question
    results = []
    for qnum, meta in sorted(q_meta.items()):
        rtype = meta["reasoning_type"]
        decile = meta["length_decile"]
        r_type = type_acc.get(rtype, 0.0)
        r_decile = decile_acc.get(decile, 0.0)
        r_q = min(r_type, r_decile)
        w_q = max(2 * r_q - 1, 0.0) ** 2
        t_k, t_n = type_stratum_kn.get(rtype, (0, 0))
        d_k, d_n = decile_stratum_kn.get(decile, (0, 0))
        results.append({
            "question_number": qnum,
            "reasoning_type": rtype,
            "length_decile": decile,
            "raw_acc_q": round(q_raw_acc[qnum], 6),
            "r_q": round(r_q, 6),
            "w_q": round(w_q, 6),
            "reasoning_type_k": t_k,
            "reasoning_type_n": t_n,
            "length_decile_k": d_k,
            "length_decile_n": d_n,
        })

    # Print stratum tables
    print("\nreliability by reasoning_type:")
    print(f"  {'reasoning_type':30s}  {'r_q':>8s}  {'n_questions':>11s}")
    for rtype in sorted(type_acc, key=lambda t: -type_acc[t]):
        n = len(type_groups[rtype])
        print(f"  {rtype:30s}  {type_acc[rtype]:8.4f}  {n:>11d}")

    print("\nreliability by length_decile:")
    print(f"  {'decile':>8s}  {'r_q':>8s}  {'n_questions':>11s}")
    for d in sorted(decile_acc):
        n = len(decile_groups[d])
        print(f"  {d:>8d}  {decile_acc[d]:8.4f}  {n:>11d}")

    # Write output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        from naming import benchmark_version
        bversion = benchmark_version(args.out)
        model_tag = artifact.get("tag") or Path(args.calibrator).stem
        meta_line = {
            "_meta": f"discriminative-judge reliability for chronologic-{bversion}",
            "model_dir": model_tag,
            "created": datetime.now(timezone.utc).isoformat(),
            "calibrator": str(calib_path),
        }
        f.write(json.dumps(meta_line) + "\n")
        for rec in results:
            f.write(json.dumps(rec) + "\n")

    print(f"\nWrote {len(results):,} question reliability records → {out_path}")
    all_w = [r["w_q"] for r in results]
    nonzero = sum(1 for w in all_w if w > 0)
    print(f"w_q > 0: {nonzero}/{len(all_w)} questions  "
          f"(mean w_q = {np.mean(all_w):.4f})")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""compute_per_question_reliability.py

Compute per-question discriminative-judge reliability (r_q) and weight (w_q)
for ChronoLogic 0.2, stratified by the joint (reasoning_type, length_decile) cell.

For each question, apply the logistic calibrator to gt/distractor pair deltas.
A pair is "correctly rejected" if P(anachronic | delta_clamped) > 0.5.
  delta_clamped = max(0, delta)   (candidate beating GT counts as zero gap)

raw_acc_q = correct_pairs / total_pairs

Stratification: pool all (k, n) counts within each (reasoning_type, length_decile)
cell and apply Laplace smoothing:
  r_q = (cell_k + 1) / (cell_n + 2)

This avoids the need to combine independent marginal estimates and naturally
handles interactions between the two stratification variables. Sparse cells
are regularised toward 0.5 by the Laplace prior.

Questions with no anachronic pairs get r_q = 0, w_q = 0.
  w_q = max(2 * r_q - 1, 0) ** 2

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

    # Stratify by joint (reasoning_type, length_decile) cell
    # Accumulate integer k/n counts per cell for Laplace-smoothed posterior
    Cell = tuple[str, int]
    cell_kn: dict[Cell, tuple[int, int]] = defaultdict(lambda: (0, 0))
    cell_n_questions: dict[Cell, int] = defaultdict(int)
    for qnum, meta in q_meta.items():
        if q_deltas.get(qnum):
            cell: Cell = (meta["reasoning_type"], meta["length_decile"])
            k, n = q_counts[qnum]
            ck, cn = cell_kn[cell]
            cell_kn[cell] = (ck + k, cn + n)
            cell_n_questions[cell] += 1

    # Laplace-smoothed reliability per cell, pooling across adjacent deciles
    # (width-3 sliding window along the ordered decile axis)
    def smoothed_kn(rtype: str, decile: int) -> tuple[int, int]:
        k = n = 0
        for d in (decile - 1, decile, decile + 1):
            ck, cn = cell_kn.get((rtype, d), (0, 0))
            k += ck
            n += cn
        return k, n

    cell_r: dict[Cell, float] = {
        cell: (smoothed_kn(*cell)[0] + 1) / (smoothed_kn(*cell)[1] + 2)
        for cell in cell_kn
    }

    # Compute r_q and w_q for each question
    results = []
    for qnum, meta in sorted(q_meta.items()):
        rtype = meta["reasoning_type"]
        decile = meta["length_decile"]
        cell = (rtype, decile)
        has_pairs = bool(q_deltas.get(qnum))
        if not has_pairs:
            r_q = 0.0
            cell_k, cell_n = 0, 0
        else:
            r_q = cell_r[cell]
            cell_k, cell_n = smoothed_kn(rtype, decile)
        w_q = max(2 * r_q - 1, 0.0) ** 2
        results.append({
            "question_number": qnum,
            "reasoning_type": rtype,
            "length_decile": decile,
            "raw_acc_q": round(q_raw_acc[qnum], 6),
            "r_q": round(r_q, 6),
            "w_q": round(w_q, 6),
            "cell_k": cell_k,
            "cell_n": cell_n,
        })

    # Print joint-cell table (k/n are smoothed pooled counts, matching r_q)
    print("\nreliability by (reasoning_type, length_decile) cell:")
    print(f"  {'reasoning_type':30s}  {'decile':>6s}  {'r_q':>8s}  {'k(smoothed)':>12s}  {'n(smoothed)':>12s}  {'n_q':>6s}")
    for cell in sorted(cell_r, key=lambda c: (-cell_r[c], c)):
        rtype, decile = cell
        ck, cn = smoothed_kn(rtype, decile)
        nq = cell_n_questions[cell]
        print(f"  {rtype:30s}  {decile:>6d}  {cell_r[cell]:8.4f}  {ck:>12d}  {cn:>12d}  {nq:>6d}")

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
    above_cutoff = [r["raw_acc_q"] for r in results if r["r_q"] >= 0.7]
    print(f"r_q >= 0.7: {len(above_cutoff)}/{len(results)} questions  "
          f"(mean raw_acc_q = {np.mean(above_cutoff):.4f})" if above_cutoff else "r_q >= 0.7: 0 questions")


if __name__ == "__main__":
    main()

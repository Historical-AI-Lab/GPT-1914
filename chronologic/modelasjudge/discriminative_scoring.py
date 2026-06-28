"""
discriminative_scoring.py — Score free-generated answers using the DeBERTa discriminative judge.

For each question the script computes the log-odds gap Δ = logit(Q_m) − logit(Q_gt)
using a fine-tuned DeBERTa classifier (trained to distinguish period text from LLM
imitations), then applies a logistic calibrator to get P(anachronic | Δ_clamped).

The continuous style score is 1 − P(anachronic).  Binarization (threshold 0.5) is
left to score_calculation.py, consistent with the way judge_scoring.py defers
the final pass/fail decision.

For questions with multiple ground truths, each GT is scored separately.  The
per-question summary uses the mean of the per-GT continuous scores.  Per-GT values
are preserved in the output for bootstrap uncertainty estimation (tests against
separate GTs are independent; repeated tests of the same GT are not).

Questions where per-question discriminative reliability r_q ≤ 0.70 are collected in
"below_threshold" — their style scores should be treated as NA by score_calculation.py.

Usage
-----
  python discriminative_scoring.py FREE_GEN_FILE [options]

  FREE_GEN_FILE             JSON output from free_generation.py.
  --calibrator PATH         Logistic calibrator pickle
                            (default: calibration/logistic_calibrator.pkl)
  --reliability PATH        Per-question discriminative reliability JSONL
                            (default: calibration/per_question_reliability_chronologic-0.2.jsonl)
  --model-dir PATH          DeBERTa model directory
                            (default: ../bertclassify/baseline)
  --batch-size INT          Inference batch size (default: 64)
  --max-length INT          Tokenizer max length (default: 256)
  --device STR              mps | cuda | cpu | auto (default: auto)
  --nomanual                Use nomanual calibrator and reliability variants.
  --output PATH             Override output file path.
  --limit N                 Process only N questions (for testing).

Output
------
Written to scored_answers/discrim_{deberta_tag}__{candidate}__{version}.json:

{
  "judge_kind": "discriminative",
  "judge_tag": "deberta-baseline-2026-04",
  "candidate_model": "...",
  "candidate_reasoning_effort": "none",
  "benchmark_version": "0.2",
  "calibrator": "calibration/logistic_calibrator.pkl",
  "reliability_source": "calibration/per_question_reliability_chronologic-0.2.jsonl",
  "thresholds": {"style": 0.70},
  "style": {
    "<qnum>": {
      "judge": "deberta-baseline-2026-04",
      "r_q": 0.78,
      "w_q": 0.31,
      "gt_indices":        [0, 1],
      "deltas":            [0.32, 0.41],
      "p_anachronic":      [0.61, 0.74],
      "continuous_scores": [0.39, 0.26],
      "continuous":        0.325
    }, ...
  },
  "below_threshold": ["0123", ...]
}

deltas and p_anachronic are per-GT values.
continuous_scores = 1 - p_anachronic per GT.
continuous = mean of continuous_scores.
below_threshold: qnums where r_q <= 0.70 (treat style as NA).

Examples
--------
  # Smoke test (3 questions):
  python discriminative_scoring.py generated_answers/free_gen_gpt-4.1-2025-04-14__0.2.json \\
      --limit 3

  # Full run with nomanual calibrator:
  python discriminative_scoring.py generated_answers/free_gen_gpt-4.1-2025-04-14__0.2.json \\
      --nomanual
"""

import json
import pickle
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
BERTCLASSIFY_DIR = SCRIPT_DIR.parent / "bertclassify"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(BERTCLASSIFY_DIR))

import numpy as np

from naming import candidate_tag as _candidate_tag, sanitize as _sanitize, benchmark_version as _benchmark_version_from_path
from run_deberta_pairs import load_deberta, score_pairs, select_device
from filter_balance_clean import normalize_text

SCORED_DIR = SCRIPT_DIR / "scored_answers"
CALIBRATION_DIR = SCRIPT_DIR / "calibration"

_STYLE_THRESHOLD = 0.70

DEFAULT_CALIBRATOR = CALIBRATION_DIR / "logistic_calibrator.pkl"
DEFAULT_CALIBRATOR_NOMANUAL = CALIBRATION_DIR / "logistic_calibrator_nomanual.pkl"
DEFAULT_RELIABILITY = CALIBRATION_DIR / "per_question_reliability_chronologic-0.2.jsonl"
DEFAULT_RELIABILITY_NOMANUAL = CALIBRATION_DIR / "per_question_reliability_chronologic-0.2_nomanual.jsonl"
DEFAULT_MODEL_DIR = BERTCLASSIFY_DIR / "baseline"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_calibrator(path):
    """Load sklearn calibrator artifact from pickle.

    Returns (model, tag) where tag may be None if absent from the artifact.
    """
    with open(path, "rb") as fh:
        artifact = pickle.load(fh)
    return artifact["model"], artifact.get("tag")


def _load_reliability(path):
    """Load per-question discriminative reliability as dict {qnum: {r_q, w_q, ...}}."""
    path = Path(path)
    if not path.exists():
        return {}
    rel = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                obj = json.loads(line)
                qnum = str(obj.get("question_number", obj.get("qnum", "")))
                if qnum:
                    rel[qnum] = obj
    return rel


def _make_features(deltas: np.ndarray) -> np.ndarray:
    return np.column_stack([deltas, deltas ** 2])


def _p_anachronic(calibrator, delta_clamped: float) -> float:
    X = _make_features(np.array([[delta_clamped]]))
    return float(calibrator.predict_proba(X)[0, 1])


def _auto_output_path(judge_tag: str, candidate_model: str, benchmark_version: str) -> Path:
    SCORED_DIR.mkdir(exist_ok=True)
    ctag = _candidate_tag(candidate_model)
    jtag = _sanitize(judge_tag)
    return SCORED_DIR / f"discrim_{jtag}__{ctag}__{benchmark_version}.json"


def _benchmark_version_from_free_gen(free_gen: dict) -> str:
    """Try to infer benchmark version from the free_gen metadata or filename."""
    import re
    bv = free_gen.get("benchmark_version")
    if bv:
        return bv
    return "unknown"


def _write_output(path, data):
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Core scoring
# ---------------------------------------------------------------------------

def score_candidate(
    answers: dict,
    calibrator,
    reliability: dict,
    deberta_model,
    tokenizer,
    device,
    batch_size: int = 64,
    max_length: int = 256,
    limit: int = None,
    judge_tag: str = "unknown",
) -> dict:
    """Score all candidate answers against their ground truths.

    Batches all DeBERTa inference across all questions and GTs for efficiency.

    Args:
        answers:     dict {qnum: {ground_truths: list[str], answer: str, ...}}.
        calibrator:  fitted sklearn model (from calibration pickle).
        reliability: dict {qnum: {r_q: float, w_q: float}}.
        deberta_model, tokenizer, device: DeBERTa inference resources.
        batch_size, max_length: inference parameters.
        limit:       optional cap on number of questions.
        judge_tag:   string identifying this calibrator version.

    Returns:
        dict {qnum: {judge, r_q, w_q, gt_indices, deltas, p_anachronic,
                     continuous_scores, continuous}}.
    """
    qnums = list(answers.keys())
    if limit is not None:
        qnums = qnums[:limit]

    # Build flat lists for batch inference.
    # For each (qnum, gt_index) pair, we record the gt and candidate texts.
    pair_keys = []   # (qnum, gt_index)
    texts_a = []     # gt text
    texts_b = []     # candidate text

    for qnum in qnums:
        entry = answers[qnum]
        ground_truths = entry.get("ground_truths") or [entry.get("ground_truth", "")]
        candidate = entry.get("answer", "")
        for gt_idx, gt in enumerate(ground_truths):
            pair_keys.append((qnum, gt_idx))
            texts_a.append(gt)
            texts_b.append(candidate)

    if not pair_keys:
        return {}

    print(f"Running DeBERTa inference on {len(pair_keys)} pairs...")
    deltas_flat = score_pairs(texts_a, texts_b, deberta_model, tokenizer, device,
                              batch_size, max_length)

    # Group results back by qnum.
    from collections import defaultdict
    per_qnum = defaultdict(list)
    for (qnum, gt_idx), delta in zip(pair_keys, deltas_flat):
        per_qnum[qnum].append((gt_idx, delta))

    style = {}
    for qnum in qnums:
        entry = answers[qnum]
        pairs = per_qnum.get(qnum, [])
        gt_indices = [p[0] for p in pairs]
        raw_deltas = [p[1] for p in pairs]

        # Clamp: model beating GT counts as no gap.
        clamped = [max(0.0, d) for d in raw_deltas]

        p_anach_list = [_p_anachronic(calibrator, d) for d in clamped]
        continuous_list = [1.0 - p for p in p_anach_list]
        continuous_mean = float(np.mean(continuous_list)) if continuous_list else None

        rel = reliability.get(str(qnum), {})
        r_q = rel.get("r_q", None)
        w_q = rel.get("w_q", None)

        style[qnum] = {
            "judge": judge_tag,
            "r_q": r_q,
            "w_q": w_q,
            "gt_indices": gt_indices,
            "deltas": [round(d, 6) for d in raw_deltas],
            "p_anachronic": [round(p, 6) for p in p_anach_list],
            "continuous_scores": [round(c, 6) for c in continuous_list],
            "continuous": round(continuous_mean, 6) if continuous_mean is not None else None,
        }

    return style


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Score free-generated answers using the DeBERTa discriminative judge.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("free_gen_file", metavar="FREE_GEN_FILE")
    parser.add_argument("--calibrator", metavar="PATH", default=None)
    parser.add_argument("--reliability", metavar="PATH", default=None)
    parser.add_argument("--model-dir", metavar="PATH", default=str(DEFAULT_MODEL_DIR),
                        dest="model_dir")
    parser.add_argument("--batch-size", type=int, default=64, dest="batch_size")
    parser.add_argument("--max-length", type=int, default=256, dest="max_length")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--nomanual", action="store_true",
                        help="Use nomanual calibrator and reliability variants.")
    parser.add_argument("--output", metavar="PATH", default=None)
    parser.add_argument("--limit", type=int, default=None)

    args = parser.parse_args()

    if args.calibrator is None:
        args.calibrator = str(DEFAULT_CALIBRATOR_NOMANUAL if args.nomanual else DEFAULT_CALIBRATOR)
    if args.reliability is None:
        args.reliability = str(DEFAULT_RELIABILITY_NOMANUAL if args.nomanual else DEFAULT_RELIABILITY)

    with open(args.free_gen_file, encoding="utf-8") as fh:
        free_gen = json.load(fh)
    answers = free_gen.get("answers", {})
    # Prefer candidate_label (set by free_generation.py when a display name differs
    # from the raw model id) so the ctag matches judge_scoring output.
    candidate_model = free_gen.get("candidate_label") or free_gen.get("model", "unknown")
    candidate_re = free_gen.get("reasoning_effort", "none")

    # Prefer benchmark_version stored in the JSON; fall back to filename parsing.
    benchmark_version = (free_gen.get("benchmark_version")
                         or _benchmark_version_from_path(args.free_gen_file))

    calibrator, calib_tag = _load_calibrator(args.calibrator)
    jtag = calib_tag or Path(args.calibrator).stem
    print(f"Calibrator tag: {jtag!r}")

    output_path = (
        Path(args.output) if args.output
        else _auto_output_path(jtag, candidate_model, benchmark_version)
    )

    reliability = _load_reliability(args.reliability)
    if not reliability:
        print(f"Warning: no reliability data found at {args.reliability}. "
              "All questions will have r_q=null.")

    device = select_device(args.device)
    print(f"Device: {device}")
    print(f"Loading DeBERTa from {args.model_dir}...")
    tokenizer, deberta_model = load_deberta(args.model_dir, device)

    style = score_candidate(
        answers=answers,
        calibrator=calibrator,
        reliability=reliability,
        deberta_model=deberta_model,
        tokenizer=tokenizer,
        device=device,
        batch_size=args.batch_size,
        max_length=args.max_length,
        limit=args.limit,
        judge_tag=jtag,
    )

    below_threshold = [
        qnum for qnum, v in style.items()
        if v["r_q"] is None or v["r_q"] <= _STYLE_THRESHOLD
    ]

    output_data = {
        "judge_kind": "discriminative",
        "judge_tag": jtag,
        "candidate_model": candidate_model,
        "candidate_reasoning_effort": candidate_re,
        "benchmark_version": benchmark_version,
        "calibrator": args.calibrator,
        "reliability_source": args.reliability,
        "thresholds": {"style": _STYLE_THRESHOLD},
        "style": style,
        "below_threshold": sorted(below_threshold),
    }

    _write_output(output_path, output_data)
    print(f"\nDone. {len(style)} questions scored.")
    print(f"  below_threshold (style NA): {len(below_threshold)}")
    print(f"Output: {output_path.resolve()}")


if __name__ == "__main__":
    main()

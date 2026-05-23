#!/usr/bin/env python3
"""build_anachronic_pairs.py

Produce one pair per (ground_truth × anachronistic_distractor) within each
benchmark question, score via DeBERTa, and write results.

text_a = ground truth, text_b = anachronistic distractor
delta = logit_b - logit_a  (positive means distractor is more "imitation-like")

Inputs:
  calibration/benchmark_data_for_discrim_calibration.jsonl

Outputs:
  calibration/anachronic_pairs.jsonl         (unscored pairs)
  calibration/anachronic_pairs_scored.jsonl  (after DeBERTa)

Usage:
    python modelasjudge/build_anachronic_pairs.py \\
        [--benchmark-data PATH] [--out-dir PATH] \\
        [--model-dir PATH] [--batch-size 64] [--max-length 256] [--device auto]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).parent
DEFAULT_BDATA = SCRIPT_DIR / "calibration" / "benchmark_data_for_discrim_calibration.jsonl"
DEFAULT_BDATA_NOMANUAL = SCRIPT_DIR / "calibration" / "benchmark_data_for_discrim_calibration_nomanual.jsonl"
DEFAULT_OUT_DIR = SCRIPT_DIR / "calibration"
BERTCLASSIFY_DIR = SCRIPT_DIR.parent / "bertclassify"


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Build and score anachronic gt/distractor pairs")
    p.add_argument("--benchmark-data", default=None, dest="benchmark_data",
                   help="Per-question benchmark data JSONL (default depends on --nomanual)")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), dest="out_dir")
    p.add_argument("--nomanual", action="store_true",
                   help="Use nomanual variant: read *_nomanual benchmark data, write *_nomanual pair files.")
    p.add_argument("--model-dir", default=str(BERTCLASSIFY_DIR / "baseline"), dest="model_dir")
    p.add_argument("--batch-size", type=int, default=64, dest="batch_size")
    p.add_argument("--max-length", type=int, default=256, dest="max_length")
    p.add_argument("--device", default="auto")
    args = p.parse_args(argv)
    if args.benchmark_data is None:
        args.benchmark_data = str(DEFAULT_BDATA_NOMANUAL if args.nomanual else DEFAULT_BDATA)
    return args


def main(argv=None):
    args = parse_args(argv)
    bdata_path = Path(args.benchmark_data)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not bdata_path.exists():
        print(f"ERROR: {bdata_path} not found.  Run build_benchmark_data.py first.", file=sys.stderr)
        sys.exit(1)

    pairs = []
    with open(bdata_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            q = json.loads(line)
            qnum = q["question_number"]
            for gi, gt in enumerate(q["ground_truths"]):
                for di, dist in enumerate(q["anachronistic_distractors"]):
                    pairs.append({
                        "pair_id": f"{qnum}:{gi}:{di}",
                        "question_number": qnum,
                        "text_a": gt,
                        "text_b": dist,
                        "mean_len": (len(gt) + len(dist)) / 2,
                        "len_diff": abs(len(gt) - len(dist)),
                        "ends_with_period_a": gt.rstrip().endswith((".", "?", "!")),
                        "ends_with_period_b": dist.rstrip().endswith((".", "?", "!")),
                    })

    suffix = "_nomanual" if args.nomanual else ""
    pairs_path = out_dir / f"anachronic_pairs{suffix}.jsonl"
    with open(pairs_path, "w", encoding="utf-8") as f:
        for p in pairs:
            f.write(json.dumps(p) + "\n")
    print(f"Wrote {len(pairs):,} pairs → {pairs_path}")

    scored_path = out_dir / f"anachronic_pairs_scored{suffix}.jsonl"
    print(f"Scoring via DeBERTa …")
    cmd = [
        sys.executable,
        str(SCRIPT_DIR / "run_deberta_pairs.py"),
        str(pairs_path),
        str(scored_path),
        "--model-dir", args.model_dir,
        "--batch-size", str(args.batch_size),
        "--max-length", str(args.max_length),
        "--device", args.device,
    ]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("ERROR: run_deberta_pairs.py failed", file=sys.stderr)
        sys.exit(1)

    # Read and report distribution
    deltas = []
    with open(scored_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                deltas.append(json.loads(line)["delta"])

    arr = np.array(deltas)
    print(f"\nΔ_anachronic distribution ({len(arr):,} pairs):")
    print(f"  mean = {arr.mean():.4f}")
    print(f"  std  = {arr.std():.4f}")
    print(f"  min  = {arr.min():.4f}  max = {arr.max():.4f}")
    print(f"\nScored pairs → {scored_path}")


if __name__ == "__main__":
    main()

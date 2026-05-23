#!/usr/bin/env python3
"""build_benchmark_data.py

Extract per-question records from chronologic_en_0.2.jsonl needed for
discriminative-judge calibration.

For each question records:
  question_number, reasoning_type, ground_truths, anachronistic_distractors,
  mean_answer_length_chars, length_decile

Anachronistic distractors include answer_types that are exactly "manual" or
that contain the substring "anachronistic" (case-insensitive).
Other types (same_book, same_character, negation, other_book_*, …) are excluded.

Output: calibration/benchmark_data_for_discrim_calibration.jsonl
        (one JSON per line; length_decile appended after all records read)

Usage:
    python modelasjudge/build_benchmark_data.py [--benchmark PATH] [--out PATH]
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).parent
DEFAULT_BENCHMARK = SCRIPT_DIR.parent / "booksample" / "chronologic_en_0.2.jsonl"
DEFAULT_OUT = SCRIPT_DIR / "calibration" / "benchmark_data_for_discrim_calibration.jsonl"
DEFAULT_OUT_NOMANUAL = SCRIPT_DIR / "calibration" / "benchmark_data_for_discrim_calibration_nomanual.jsonl"


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Build per-question benchmark data for discrim calibration")
    p.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK), metavar="PATH")
    p.add_argument("--out", default=None, metavar="PATH",
                   help="Output JSONL path (default depends on --nomanual)")
    p.add_argument("--nomanual", action="store_true",
                   help="Exclude answer_type=='manual' distractors; keep only types containing 'anachronistic'. "
                        "Switches default output to *_nomanual.jsonl.")
    args = p.parse_args(argv)
    if args.out is None:
        args.out = str(DEFAULT_OUT_NOMANUAL if args.nomanual else DEFAULT_OUT)
    return args


def is_anachronistic(answer_type: str, nomanual: bool = False) -> bool:
    t = answer_type.strip().lower()
    if nomanual:
        return "anachronistic" in t
    return t == "manual" or "anachronistic" in t


def main(argv=None):
    args = parse_args(argv)
    bpath = Path(args.benchmark)
    out_path = Path(args.out)

    if not bpath.exists():
        print(f"ERROR: benchmark not found: {bpath}", file=sys.stderr)
        sys.exit(1)

    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Mode: {'nomanual (anachronistic-only)' if args.nomanual else 'default (anachronistic + manual)'}")

    records = []
    skipped_no_gt = 0
    skipped_no_dist = 0
    skipped_no_either = 0

    with open(bpath, encoding="utf-8") as f:
        for line_idx, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            q = json.loads(line)

            types = q.get("answer_types", [])
            strings = q.get("answer_strings", [])
            qnum = q.get("question_number", line_idx + 1)
            rtype = q.get("reasoning_type", "unknown")

            gts = [s for s, t in zip(strings, types) if t == "ground_truth"]
            distractors = [s for s, t in zip(strings, types) if is_anachronistic(t, args.nomanual)]

            has_gt = bool(gts)
            has_dist = bool(distractors)

            if not has_gt and not has_dist:
                skipped_no_either += 1
                continue
            if not has_gt:
                skipped_no_gt += 1
                continue
            if not has_dist:
                skipped_no_dist += 1
                continue

            mean_len = sum(len(s) for s in strings) / len(strings) if strings else 0.0

            records.append({
                "question_number": qnum,
                "reasoning_type": rtype,
                "ground_truths": gts,
                "anachronistic_distractors": distractors,
                "mean_answer_length_chars": mean_len,
                "length_decile": None,   # filled below
            })

    if skipped_no_gt:
        print(f"WARNING: skipped {skipped_no_gt} questions with no ground_truth answers", file=sys.stderr)
    if skipped_no_dist:
        print(f"Skipped {skipped_no_dist} questions with no anachronistic distractors (excluded from calibration)")
    if skipped_no_either:
        print(f"WARNING: skipped {skipped_no_either} questions with neither gt nor distractors", file=sys.stderr)

    means = [r["mean_answer_length_chars"] for r in records]
    deciles = pd.qcut(means, q=10, labels=False, duplicates="drop")

    for rec, dec in zip(records, deciles):
        rec["length_decile"] = int(dec)

    with open(out_path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")

    print(f"Wrote {len(records):,} questions → {out_path}")
    print(f"reasoning_type counts:")
    from collections import Counter
    for rtype, n in sorted(Counter(r["reasoning_type"] for r in records).items()):
        print(f"  {rtype}: {n}")
    print(f"length_decile range: {min(r['length_decile'] for r in records)}–"
          f"{max(r['length_decile'] for r in records)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""score_pairs.py

Pairwise discrimination scoring for free-generation evaluation.

Reads a predictions TSV produced by run_deberta.py (from a fordeberta.tsv input
where rows alternate ground_truth/model_answer for the same question) and counts
how many pairs are correctly discriminated — i.e., the model answer receives a
higher imitation probability than the ground truth.

This pairwise rate is the key statistic for estimating an upper bound on
free-generation accuracy under the indistinguishability assumption.

Usage:
    python bertclassify/score_pairs.py PREDICTIONS_TSV [--output PATH]

Positional:
    PREDICTIONS_TSV     Predictions TSV from run_deberta.py

Options:
    --output PATH       Write per-pair results to this TSV (optional)

Examples:
    python bertclassify/score_pairs.py \\
        bertclassify/forscoring/free_gen_gpt-5.4_20260318_180622_fordeberta_predictions.tsv
"""

import argparse
import csv
import sys
from pathlib import Path


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Pairwise discrimination scoring for DeBERTa predictions.",
    )
    parser.add_argument(
        "predictions_tsv",
        metavar="PREDICTIONS_TSV",
        help="Predictions TSV from run_deberta.py",
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="PATH",
        help="Write per-pair results to this TSV (optional)",
    )
    return parser.parse_args(argv)


def load_predictions(path):
    """Read predictions TSV; return list of dicts with text, prediction, probability."""
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    return rows


def score_pairs(rows):
    """Compute pairwise discrimination from alternating gt/model rows.

    Returns list of dicts with per-pair results.
    """
    if len(rows) % 2 != 0:
        raise ValueError(
            f"Expected even number of rows (gt/model pairs), got {len(rows)}. "
            "Check that the input was produced by free_gen_triage.py."
        )

    results = []
    for i in range(0, len(rows), 2):
        gt_row    = rows[i]
        model_row = rows[i + 1]
        gt_prob    = float(gt_row["probability"])
        model_prob = float(model_row["probability"])
        correct = model_prob > gt_prob
        results.append({
            "pair_index":  i // 2,
            "gt_prob":     gt_prob,
            "model_prob":  model_prob,
            "correct":     correct,
            "gt_text":     gt_row["text"],
            "model_text":  model_row["text"],
        })
    return results


def write_pair_tsv(results, output_path):
    """Write per-pair results to a TSV."""
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["pair_index", "gt_prob", "model_prob", "correct", "gt_text", "model_text"],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(results)


def print_summary(results):
    total   = len(results)
    correct = sum(1 for r in results if r["correct"])
    rate    = correct / total if total else float("nan")

    gt_probs    = [r["gt_prob"]    for r in results]
    model_probs = [r["model_prob"] for r in results]
    mean_gt    = sum(gt_probs)    / len(gt_probs)    if gt_probs    else float("nan")
    mean_model = sum(model_probs) / len(model_probs) if model_probs else float("nan")

    print(f"Total pairs:          {total}")
    print(f"Correctly ranked:     {correct}  ({rate:.1%})")
    print(f"Mean gt imitation p:  {mean_gt:.4f}")
    print(f"Mean model imitation p: {mean_model:.4f}")


def main(argv=None):
    args = parse_args(argv)

    path = Path(args.predictions_tsv)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    rows = load_predictions(path)
    if not rows:
        print("Error: no rows found in predictions file.", file=sys.stderr)
        sys.exit(1)

    results = score_pairs(rows)
    print_summary(results)

    if args.output:
        write_pair_tsv(results, Path(args.output))
        print(f"\nPer-pair results written → {args.output}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""free_gen_triage.py

Triage free-generation evaluation output for DeBERTa scoring vs. manual review.

Usage:
    python bertclassify/free_gen_triage.py INPUT_FILE [--benchmark PATH]

Positional:
    INPUT_FILE       Free-gen JSON result file

Options:
    --benchmark PATH  Benchmark JSONL (default: booksample/chronologic_en_0.1.jsonl)

Examples:
    python bertclassify/free_gen_triage.py booksample/free_gen_gpt-5.4_20260318_180622.json
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from filter_balance_clean import normalize_text

FORSCORING_DIR = SCRIPT_DIR / "forscoring"
FORMANUAL_DIR = SCRIPT_DIR / "formanual"

# Matching outer quote pairs to strip
_QUOTE_PAIRS = [
    ('"', '"'),
    ("'", "'"),
    ("\u201c", "\u201d"),  # curly double
    ("\u2018", "\u2019"),  # curly single
]


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Triage free-gen output for DeBERTa scoring vs. manual review.",
    )
    parser.add_argument(
        "input_file",
        metavar="INPUT_FILE",
        help="Free-gen JSON result file",
    )
    parser.add_argument(
        "--benchmark",
        default=str(REPO_ROOT / "booksample" / "chronologic_en_0.1.jsonl"),
        metavar="PATH",
        help="Benchmark JSONL (default: booksample/chronologic_en_0.1.jsonl)",
    )
    return parser.parse_args(argv)


def load_benchmark(path):
    """Read benchmark JSONL; return dict keyed by question_number (str)."""
    benchmark = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            qnum = str(record["question_number"])
            benchmark[qnum] = {
                "answer_length": record.get("answer_length", ""),
                "answer_strings": record.get("answer_strings", []),
                "answer_types": record.get("answer_types", []),
            }
    return benchmark


def count_words(text):
    """Return word count via simple split."""
    return len(text.split())


def trim_quotes(text):
    """Strip matching outer quote pair if present (curly or straight)."""
    if len(text) < 2:
        return text
    for open_q, close_q in _QUOTE_PAIRS:
        if text.startswith(open_q) and text.endswith(close_q):
            # Avoid stripping identical single-char quotes that are also the same char
            # but only strip if the string is at least 2 chars (already checked above)
            if open_q == close_q:
                # e.g. straight single or double: only strip if both ends match
                return text[len(open_q):-len(close_q)]
            return text[len(open_q):-len(close_q)]
    return text


def triage(answers, benchmark):
    """Apply triage criteria; return (deberta_items, manual_items).

    Each deberta item: dict with question_number, ground_truth, model_answer,
    plus all free-gen fields.
    Each manual item: same plus benchmark fields and triage_reason.
    """
    deberta_items = []
    manual_items = []

    for qnum_raw, entry in answers.items():
        qnum = str(qnum_raw)
        ground_truth = entry.get("ground_truth", "")
        model_answer = entry.get("answer", "")
        reasoning_type = entry.get("reasoning_type", "")

        bench = benchmark.get(qnum, {})
        answer_length = bench.get("answer_length", "")

        # Determine triage reason (first failing criterion wins)
        triage_reason = None
        if count_words(ground_truth) < 5:
            triage_reason = "short_ground_truth"
        elif count_words(model_answer) < 5:
            triage_reason = "short_answer"
        elif reasoning_type == "abstention":
            triage_reason = "abstention"
        elif answer_length == "short_answer":
            triage_reason = "short_answer_length"

        item = {
            "question_number": qnum,
            "metadata_frame": entry.get("metadata_frame", ""),
            "main_question": entry.get("main_question", ""),
            "ground_truth": ground_truth,
            "model_answer": model_answer,
            "reasoning_type": reasoning_type,
            "length_spec": entry.get("length_spec", ""),
        }

        if triage_reason is None:
            deberta_items.append(item)
        else:
            manual_item = dict(item)
            manual_item["answer_strings"] = bench.get("answer_strings", [])
            manual_item["answer_types"] = bench.get("answer_types", [])
            manual_item["answer_length"] = answer_length
            manual_item["triage_reason"] = triage_reason
            manual_items.append(manual_item)

    return deberta_items, manual_items


def write_deberta_tsv(items, output_path):
    """Write labeled TSV: two rows per question (ground_truth=0, model_answer=1)."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("text\tlabel\n")
        for item in items:
            gt = normalize_text(trim_quotes(item["ground_truth"]))
            ma = normalize_text(trim_quotes(item["model_answer"]))
            # Replace any embedded tabs/newlines to keep TSV valid
            gt = gt.replace("\t", " ").replace("\n", " ")
            ma = ma.replace("\t", " ").replace("\n", " ")
            f.write(f"{gt}\t0\n")
            f.write(f"{ma}\t1\n")


def write_manual_jsonl(items, output_path):
    """Write JSONL with enriched fields for manual review."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def _derive_output_stem(input_path):
    """Return the base stem (without extension) from the input filename."""
    return Path(input_path).stem


def main(argv=None):
    args = parse_args(argv)

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    benchmark_path = Path(args.benchmark)
    if not benchmark_path.exists():
        print(f"Error: benchmark file not found: {benchmark_path}", file=sys.stderr)
        sys.exit(1)

    # Load inputs
    with open(input_path, encoding="utf-8") as f:
        free_gen = json.load(f)
    answers = free_gen.get("answers", {})

    benchmark = load_benchmark(benchmark_path)

    # Triage
    deberta_items, manual_items = triage(answers, benchmark)

    # Derive output paths
    stem = _derive_output_stem(input_path)
    deberta_path = FORSCORING_DIR / f"{stem}_fordeberta.tsv"
    manual_path = FORMANUAL_DIR / f"{stem}_formanual.jsonl"

    # Write outputs
    write_deberta_tsv(deberta_items, deberta_path)
    write_manual_jsonl(manual_items, manual_path)

    # Summary
    total = len(answers)
    n_deberta = len(deberta_items)
    n_manual = len(manual_items)

    reason_counts: dict = {}
    for item in manual_items:
        r = item["triage_reason"]
        reason_counts[r] = reason_counts.get(r, 0) + 1

    print(f"Total questions:    {total}")
    print(f"Sent to DeBERTa:    {n_deberta}  → {deberta_path}")
    print(f"Sent to manual:     {n_manual}  → {manual_path}")
    if reason_counts:
        print("Manual triage breakdown:")
        for reason, count in sorted(reason_counts.items()):
            print(f"  {reason}: {count}")


if __name__ == "__main__":
    main()

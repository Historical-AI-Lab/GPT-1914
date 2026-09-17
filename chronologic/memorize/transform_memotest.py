"""Transform memorize/memotest.jsonl into benchmark-compatible JSONL.

Usage:
    python memorize/transform_memotest.py INPUT OUTPUT

Example:
    python memorize/transform_memotest.py memorize/memotest.jsonl memorize/memotest_benchmark.jsonl
"""

import argparse
import json
import sys

SUFFIX = "\n\nWhat proper noun or noun phrase would best fill in the blank occupied above by [masked proper noun]?"


def transform_entry(entry: dict, question_number: int) -> dict:
    """Convert a single memotest entry to benchmark question format."""
    # Normalize any data errors: [masked proper name] -> [masked proper noun]
    passage = entry["passage"].replace("[masked proper name]", "[masked proper noun]")

    ground_truth = entry["ground_truth"]
    distractors = [d for d in entry["distractors"] if d != ground_truth]

    answer_strings = [ground_truth] + distractors
    n = len(answer_strings)

    return {
        "metadata_frame": entry["author"],
        "main_question": passage + SUFFIX,
        "answer_strings": answer_strings,
        "answer_types": ["ground_truth"] + ["manual"] * (n - 1),
        "answer_probabilities": [1.0] + [0.0] * (n - 1),
        "question_category": "phrase_cloze",
        "reasoning_type": "phrase_cloze",
        "answer_length": "short_answer",
        "frame_type": "book_context",
        "question_number": question_number,
    }


def main():
    parser = argparse.ArgumentParser(description="Transform memotest.jsonl to benchmark format")
    parser.add_argument("input", help="Input JSONL file (memotest format)")
    parser.add_argument("output", help="Output JSONL file (benchmark format)")
    args = parser.parse_args()

    count = 0
    with open(args.input, encoding="utf-8") as fin, open(args.output, "w", encoding="utf-8") as fout:
        for question_number, line in enumerate(fin, start=1):
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            transformed = transform_entry(entry, question_number)
            fout.write(json.dumps(transformed, ensure_ascii=False) + "\n")
            count += 1

    print(f"Wrote {count} questions to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()

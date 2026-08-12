"""
bin_counter.py — distribution of training data across length/digit bins
Reads every file in bertclassify/authentic and bertclassify/imitation.
"""

import os
import re
import nltk
from pathlib import Path

nltk.download("punkt_tab", quiet=True)

SCRIPT_DIR = Path(__file__).parent
DIRS = {
    "authentic": SCRIPT_DIR / "authentic",
    "imitation": SCRIPT_DIR / "imitation",
}


def count_sentences(text: str) -> int:
    return len(nltk.sent_tokenize(text))


def count_words(text: str) -> int:
    return len(text.split())


def digit_fraction(text: str) -> float:
    if not text:
        return 0.0
    digits = sum(1 for c in text if c.isdigit())
    return digits / len(text)


def word_bin(n: int) -> str:
    if n < 10:
        return "< 10"
    elif n < 15:
        return "10-14"
    elif n < 20:
        return "15-19"
    elif n < 30:
        return "20-29"
    elif n < 40:
        return "30-39"
    elif n < 50:
        return "40-49"
    elif n < 75:
        return "50-74"
    elif n < 100:
        return "75-99"
    else:
        return "100+"


WORD_BINS = ["< 10", "10-14", "15-19", "20-29", "30-39", "40-49", "50-74", "75-99", "100+"]

DIGIT_BINS = ["0%", "0-2%", "2-5%", "5-10%", ">10%"]


def digit_bin(frac: float) -> str:
    if frac == 0.0:
        return "0%"
    elif frac < 0.02:
        return "0-2%"
    elif frac < 0.05:
        return "2-5%"
    elif frac < 0.10:
        return "5-10%"
    else:
        return ">10%"


def collect_lines(directory: Path) -> list[str]:
    lines = []
    for path in sorted(directory.iterdir()):
        if path.is_file():
            with open(path, encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.rstrip("\n")
                    if line.strip():
                        lines.append(line)
    return lines


def analyze(lines: list[str]) -> dict:
    total = len(lines)
    sent_counts = {1: 0, 2: 0, 3: 0, "4+": 0}
    total_sentences = 0
    word_counts = {b: 0 for b in WORD_BINS}
    digit_counts = {b: 0 for b in DIGIT_BINS}
    single_sentence_lines = 0

    for line in lines:
        nsent = count_sentences(line)
        total_sentences += nsent
        if nsent == 1:
            sent_counts[1] += 1
            single_sentence_lines += 1
            nwords = count_words(line)
            word_counts[word_bin(nwords)] += 1
        elif nsent == 2:
            sent_counts[2] += 1
        elif nsent == 3:
            sent_counts[3] += 1
        else:
            sent_counts["4+"] += 1

        frac = digit_fraction(line)
        digit_counts[digit_bin(frac)] += 1

    return {
        "total": total,
        "total_sentences": total_sentences,
        "sent_counts": sent_counts,
        "single_sentence_lines": single_sentence_lines,
        "word_counts": word_counts,
        "digit_counts": digit_counts,
    }


def pct(n, total):
    if total == 0:
        return "  n/a"
    return f"{100 * n / total:5.1f}%"


def print_report(label: str, stats: dict):
    total = stats["total"]
    ss = stats["single_sentence_lines"]
    print(f"\n{'='*60}")
    print(f"  {label.upper()}  ({total:,} lines total)")
    print(f"{'='*60}")

    print("\n--- Sentence bins ---")
    print(f"  Total sentences: {stats['total_sentences']:,}")
    for key in [1, 2, 3, "4+"]:
        n = stats["sent_counts"][key]
        label_str = f"{key} sentence{'s' if key != 1 else ''}"
        print(f"  {label_str:<15} {n:6,}  ({pct(n, total)} of lines)")

    print(f"\n--- Word bins (single-sentence lines only, n={ss:,}) ---")
    for b in WORD_BINS:
        n = stats["word_counts"][b]
        print(f"  {b:<8} {n:6,}  ({pct(n, ss)})")

    print(f"\n--- Digit frequency bins (all lines, n={total:,}) ---")
    for b in DIGIT_BINS:
        n = stats["digit_counts"][b]
        print(f"  {b:<8} {n:6,}  ({pct(n, total)})")


def main():
    for group, directory in DIRS.items():
        if not directory.exists():
            print(f"WARNING: {directory} not found, skipping.")
            continue
        lines = collect_lines(directory)
        stats = analyze(lines)
        print_report(group, stats)
    print()


if __name__ == "__main__":
    main()

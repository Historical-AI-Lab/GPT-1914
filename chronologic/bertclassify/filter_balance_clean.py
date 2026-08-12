#!/usr/bin/env python3
"""filter_balance_clean.py

Filter, balance, and clean authentic/imitation text for DeBERTa fine-tuning.

Usage:
    python bertclassify/filter_balance_clean.py [options]

Options:
    -n, --n-per-side N        Target examples per side (default: 5000)
    --seed INT                Random seed (default: 42)
    --val-fraction FLOAT      Fraction of barcodes held out for val (default: 0.2)
    --output-dir PATH         Where to write TSVs (default: bertclassify/)
    --log-dropped             Write dropped_lines.tsv with rejected lines + reasons
    --verbose                 Per-barcode statistics

Examples:
    python bertclassify/filter_balance_clean.py
    python bertclassify/filter_balance_clean.py -n 1000
    python bertclassify/filter_balance_clean.py -n 5000 --log-dropped --verbose
    python bertclassify/filter_balance_clean.py -n 3000 --seed 99 --output-dir bertclassify/data/
"""

import argparse
import random
import re
import sys
from pathlib import Path
from typing import Optional

import nltk

for _res in ("punkt", "punkt_tab"):
    try:
        nltk.data.find(f"tokenizers/{_res}")
        break
    except LookupError:
        try:
            nltk.download(_res, quiet=True)
        except Exception:
            pass

# Add bertclassify dir to path so bin_counter is importable
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from bin_counter import count_words, digit_fraction

AUTHENTIC_DIR = SCRIPT_DIR / "authentic"
IMITATION_DIR = SCRIPT_DIR / "imitation"


# ---------------------------------------------------------------------------
# 2. Cleaning — normalize_text (importable for inference)
# ---------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """Normalize Unicode characters and whitespace.

    Pure string operations; no external dependencies. Safe to apply at
    training time and inference time.
    """
    # Curly single quotes / apostrophes
    for ch in "\u2018\u2019\u201a\u201b":
        text = text.replace(ch, "'")
    # Curly double quotes
    for ch in "\u201c\u201d\u201e\u201f":
        text = text.replace(ch, '"')
    # Em dash, en dash -> hyphen
    text = text.replace("\u2014", "-").replace("\u2013", "-")
    # Tab -> space
    text = text.replace("\t", " ")
    # Non-breaking, em, en, thin, hair, zero-width, figure spaces -> space
    for ch in "\u00a0\u2003\u2002\u2009\u200a\u200b\u2007\ufeff":
        text = text.replace(ch, " ")
    # Ellipsis character
    text = text.replace("\u2026", "...")
    # Collapse multiple spaces
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# 1. Filtering (training-time only)
# ---------------------------------------------------------------------------

_LATEX_PATTERNS = [
    re.compile(r"\\\("),
    re.compile(r"\\\)"),
    re.compile(r"\\\["),
    re.compile(r"\\\]"),
    re.compile(r"\\[A-Za-z]+"),   # \frac, \log, \sqrt, etc.
]

_NON_ASCII_MATH = re.compile(
    r"[∀∃∈∉∋∌∩∪⊂⊃⊆⊇⊕⊗⊥∥∠∧∨¬→↔∑∏∫∂∇√±×÷≤≥≠≈≡∞]"
)


def latex_score(text: str) -> int:
    """Count LaTeX-like signals in text."""
    score = 0
    for pat in _LATEX_PATTERNS:
        score += len(pat.findall(text))
    score += text.count("{") + text.count("}")
    score += text.count("^") + text.count("_")
    score += len(_NON_ASCII_MATH.findall(text))
    return score


def _digit_ratio(text: str) -> float:
    chars = [c for c in text if not c.isspace()]
    if not chars:
        return 0.0
    return sum(c.isdigit() for c in chars) / len(chars)


def _punctuation_ratio(text: str, punct_set: set) -> float:
    chars = [c for c in text if not c.isspace()]
    if not chars:
        return 0.0
    return sum(c in punct_set for c in chars) / len(chars)


def looks_like_index_line(text: str) -> bool:
    """True for index/TOC/bibliography lines with high digit ratio or many short comma-separated fragments."""
    comma_count = text.count(",")
    num_groups = len(re.findall(r"\b\d+\b", text))
    short_chunks = sum(1 for chunk in text.split(",") if len(chunk.split()) <= 4)
    return (
        _digit_ratio(text) > 0.12
        or (comma_count >= 4 and num_groups >= 4 and short_chunks >= 4)
    )


def looks_like_formula_or_table(text: str) -> bool:
    """True for lines with heavy LaTeX, math symbols, or formula-like character ratios."""
    upper_alpha = len(re.findall(r"\b[A-Z][A-Za-z0-9\-]*\b", text))
    symbol_ratio = _punctuation_ratio(text, set("()[]{}=+-/%"))
    dr = _digit_ratio(text)
    return (
        latex_score(text) >= 2
        or (dr > 0.10 and symbol_ratio > 0.12)
        or (upper_alpha >= 4 and dr > 0.08)
    )


def looks_like_markup_or_code(text: str) -> bool:
    """True for lines with URLs, code fences, or JSON-like structure."""
    stripped = text.strip()
    return any([
        "http://" in text,
        "https://" in text,
        "```" in text,
        stripped.startswith("{") and ":" in text,
        stripped.startswith("[") and stripped.endswith("]"),
    ])


def should_drop(text: str) -> Optional[str]:
    """Return drop reason string, or None if line is acceptable."""
    if len(text.split()) < 5:
        return "too_short"
    if looks_like_markup_or_code(text):
        return "markup"
    if looks_like_formula_or_table(text):
        return "formula_table"
    if looks_like_index_line(text):
        return "index"
    return None


# ---------------------------------------------------------------------------
# 0. Selection — file I/O
# ---------------------------------------------------------------------------

_BARCODE_RE = re.compile(r"^(\d{14,})")


def extract_barcode(filename: str) -> Optional[str]:
    """Extract 14+-digit barcode prefix from a filename."""
    m = _BARCODE_RE.match(filename)
    return m.group(1) if m else None


def load_side(
    directory: Path,
    max_lines: int = 80,
) -> tuple[dict[str, list[str]], dict[str, tuple[str, list[str]]]]:
    """Read up to max_lines non-empty lines from each .txt file in directory.

    Returns:
        barcode_lines: dict[barcode, list[str]] — lines merged across all files
                       sharing the same barcode prefix.
        file_data: dict[filename_stem, (barcode, list[str])] — per-file data
                   used for per-file drop-rate tracking.
    """
    barcode_lines: dict[str, list[str]] = {}
    file_data: dict[str, tuple[str, list[str]]] = {}

    if not directory.exists():
        return barcode_lines, file_data

    for path in sorted(directory.iterdir()):
        if not path.is_file() or not path.name.endswith(".txt"):
            continue
        barcode = extract_barcode(path.name)
        if barcode is None:
            continue
        lines: list[str] = []
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.rstrip("\n")
                if line.strip():
                    lines.append(line)
                    if len(lines) >= max_lines:
                        break
        file_data[path.stem] = (barcode, lines)
        barcode_lines.setdefault(barcode, []).extend(lines)

    return barcode_lines, file_data


# ---------------------------------------------------------------------------
# 1. Filter side
# ---------------------------------------------------------------------------

def filter_side(
    file_data: dict[str, tuple[str, list[str]]],
    side_name: str,
    log_dropped: bool = False,
) -> tuple[dict[str, list[str]], set[str], list[tuple]]:
    """Filter lines per file; flag barcodes where any file has >30% drop rate.

    Returns:
        filtered:      dict[barcode, list[str]] of kept lines (bad barcodes excluded)
        bad_barcodes:  set of barcode strings where any file had >30% drop rate
        dropped_log:   list of (side_name, barcode, line_text, reason) tuples
    """
    per_barcode_kept: dict[str, list[str]] = {}
    bad_barcodes: set[str] = set()
    dropped_log: list[tuple] = []
    # Track which barcodes were seen to log barcode_dropped entries if needed
    kept_before_cross_drop: dict[str, list[tuple[str, str]]] = {}  # barcode -> [(line, reason)]

    for filestem, (barcode, lines) in file_data.items():
        kept: list[str] = []
        file_dropped: list[tuple[str, str]] = []

        for line in lines:
            reason = should_drop(line)
            if reason is not None:
                file_dropped.append((line, reason))
            else:
                kept.append(line)

        total = len(lines)
        if total > 0 and len(file_dropped) / total > 0.50:
            bad_barcodes.add(barcode)
            if log_dropped:
                for line, reason in file_dropped:
                    dropped_log.append((side_name, barcode, line, reason))
                for line in kept:
                    dropped_log.append((side_name, barcode, line, "barcode_dropped"))
        else:
            per_barcode_kept.setdefault(barcode, []).extend(kept)
            if log_dropped:
                for line, reason in file_dropped:
                    dropped_log.append((side_name, barcode, line, reason))

    # Remove bad barcodes from filtered output
    filtered = {
        bc: lines
        for bc, lines in per_barcode_kept.items()
        if bc not in bad_barcodes
    }
    return filtered, bad_barcodes, dropped_log


# ---------------------------------------------------------------------------
# Sentence tokenizer (local — avoids pulling in the full bert_data_prep chain)
# ---------------------------------------------------------------------------

def sentence_tokenize(text: str) -> list[str]:
    """Tokenize text into sentences, filtering empty strings."""
    return [s for s in nltk.sent_tokenize(text) if s.strip()]


# ---------------------------------------------------------------------------
# Clause extraction
# ---------------------------------------------------------------------------

def extract_clause(text: str) -> Optional[str]:
    """Return text after the first comma if text has 20+ words and remainder has 5+ words."""
    if count_words(text) < 20:
        return None
    idx = text.find(",")
    if idx == -1:
        return None
    remainder = text[idx + 1:].strip()
    if count_words(remainder) < 5:
        return None
    return remainder


def _try_clause(text: str) -> Optional[str]:
    """Try clause extraction on the text or its individual sentences."""
    # Try whole text first (works for single-sentence texts)
    clause = extract_clause(text)
    if clause:
        return clause
    # Try each sentence within a multi-sentence text
    for sent in sentence_tokenize(text):
        clause = extract_clause(sent)
        if clause:
            return clause
    return None


# ---------------------------------------------------------------------------
# 3. Balancing
# ---------------------------------------------------------------------------

BIN_NAMES = ["short", "clause", "medium", "long", "multi"]
BIN_TARGETS = {
    "short": 0.10,
    "clause": 0.10,
    "medium": 0.40,
    "long": 0.20,
    "multi": 0.20,
}
# Word-count ranges for natural-fit classification (clause is post-extraction, any length)
_BIN_RANGES = {
    "short":  (0,  14),
    "medium": (15, 34),
    "long":   (35, 54),
    "multi":  (55, 100),
}

_DIGIT_THRESH_HIGH = 0.05   # "high digit" = digit_fraction > 5%
_CAP_HIGH_DIGIT    = 0.02   # at most 2% of n may be high-digit
_CAP_ANY_DIGIT     = 0.07   # at most 7% of n may have any digits


def _natural_bin(nwords: int) -> Optional[str]:
    """Return the natural bin name for a word count, or None if >100."""
    if nwords <= 14:
        return "short"
    if nwords <= 34:
        return "medium"
    if nwords <= 54:
        return "long"
    if nwords <= 100:
        return "multi"
    return None


def _fit_candidate(
    text: str,
    bin_counts: dict[str, int],
    bin_caps: dict[str, int],
) -> Optional[tuple[str, str]]:
    """Try to fit text (or a transformation) into an open bin.

    Returns (bin_name, final_text) or None if no open bin can accept it.
    """
    nwords = count_words(text)
    clause_needed = bin_counts["clause"] < bin_caps["clause"]

    # 1. If clause bin is lagging behind the fill rate of other bins, try clause first.
    #    This ensures clause reaches its target rather than always losing to natural fits.
    if clause_needed:
        other_filled = sum(bin_counts[b] for b in BIN_NAMES if b != "clause")
        other_cap    = sum(bin_caps[b]    for b in BIN_NAMES if b != "clause")
        clause_ratio = bin_counts["clause"] / bin_caps["clause"] if bin_caps["clause"] else 1.0
        other_ratio  = other_filled / other_cap if other_cap else 1.0
        if clause_ratio < other_ratio:
            clause = _try_clause(text)
            if clause:
                return ("clause", clause)

    # 2. Natural fit
    nat = _natural_bin(nwords)
    if nat and bin_counts[nat] < bin_caps[nat]:
        return (nat, text)

    # 3. Clause extraction as fallback when natural bin is full
    if clause_needed:
        clause = _try_clause(text)
        if clause:
            return ("clause", clause)

    # 3. Very long text (>100 words): select first N sentences to fit an open bin
    if nwords > 100:
        sentences = sentence_tokenize(text)
        for target_bin in ("multi", "long", "medium", "short"):
            if bin_counts[target_bin] >= bin_caps[target_bin]:
                continue
            lo, hi = _BIN_RANGES[target_bin]
            accum = ""
            for sent in sentences:
                candidate = (accum + " " + sent).strip() if accum else sent
                cw = count_words(candidate)
                if lo <= cw <= hi:
                    return (target_bin, candidate)
                if cw > hi:
                    # Current sentence overshot; try what we had before
                    if accum and lo <= count_words(accum) <= hi:
                        return (target_bin, accum)
                    break
                accum = candidate

    # 4. Long/multi candidate (>=35 words) whose natural bin is full: truncate down
    if nwords >= 35:
        sentences = sentence_tokenize(text)
        for target_bin in ("long", "medium", "short"):
            if bin_counts[target_bin] >= bin_caps[target_bin]:
                continue
            lo, hi = _BIN_RANGES[target_bin]
            accum = ""
            for sent in sentences:
                candidate = (accum + " " + sent).strip() if accum else sent
                cw = count_words(candidate)
                if lo <= cw <= hi:
                    return (target_bin, candidate)
                if cw > hi:
                    if accum and lo <= count_words(accum) <= hi:
                        return (target_bin, accum)
                    break
                accum = candidate

    # 5. Medium candidate (15-34 words) whose medium bin is full: try clause
    if 15 <= nwords <= 34 and bin_counts["clause"] < bin_caps["clause"]:
        clause = _try_clause(text)
        if clause:
            return ("clause", clause)

    return None


def balance_side(
    barcode_lines: dict[str, list[str]],
    n: int,
    rng: random.Random,
    consumed: Optional[list] = None,
) -> list[tuple[str, str, str]]:
    """Select n examples balanced across length bins and digit constraints.

    Returns a list of (normalized_text, barcode, bin_name) tuples.
    If consumed is a list, every raw text popped from the pool is appended to
    it (including popped-then-rejected items), letting callers track which
    source chunks the rng drew.
    """
    if n <= 0 or not barcode_lines:
        return []

    # Bin capacities — round targets, put remainder in medium
    bin_caps = {name: round(n * BIN_TARGETS[name]) for name in BIN_NAMES}
    diff = n - sum(bin_caps.values())
    if diff != 0:
        bin_caps["medium"] += diff

    bin_counts = {name: 0 for name in BIN_NAMES}

    cap_high = max(1, round(n * _CAP_HIGH_DIGIT))
    cap_any  = max(1, round(n * _CAP_ANY_DIGIT))
    digit_high_count = 0
    digit_any_count  = 0

    # Per-barcode tracking for round-robin
    barcode_accepted: dict[str, int] = {bc: 0 for bc in barcode_lines}
    # Shuffle each pool independently
    barcode_pools: dict[str, list[str]] = {
        bc: rng.sample(lines, len(lines))
        for bc, lines in barcode_lines.items()
        if lines
    }

    results: list[tuple[str, str, str]] = []
    max_iters = max(n * 30, 10000)
    iters = 0

    def all_bins_full() -> bool:
        return all(bin_counts[b] >= bin_caps[b] for b in BIN_NAMES)

    while barcode_pools and not all_bins_full() and iters < max_iters:
        iters += 1

        # Round-robin: pick barcode with fewest accepted samples
        bc = min(barcode_pools, key=lambda b: barcode_accepted.get(b, 0))

        text = barcode_pools[bc].pop()
        if consumed is not None:
            consumed.append(text)
        if not barcode_pools[bc]:
            del barcode_pools[bc]

        # Normalize
        text = normalize_text(text)
        if not text or len(text.split()) < 5:
            continue

        # Digit constraint checks
        df = digit_fraction(text)
        is_high_digit = df > _DIGIT_THRESH_HIGH
        has_any_digit = df > 0.0

        if is_high_digit:
            if digit_high_count >= cap_high:
                continue
            if digit_any_count >= cap_any:
                continue
        elif has_any_digit:
            if digit_any_count >= cap_any:
                continue

        # Try to fit into a bin
        fit = _fit_candidate(text, bin_counts, bin_caps)
        if fit is None:
            continue

        bin_name, final_text = fit
        bin_counts[bin_name] += 1
        if is_high_digit:
            digit_high_count += 1
            digit_any_count += 1
        elif has_any_digit:
            digit_any_count += 1

        barcode_accepted[bc] = barcode_accepted.get(bc, 0) + 1
        results.append((final_text, bc, bin_name))

    return results


# ---------------------------------------------------------------------------
# 4. Train / val split
# ---------------------------------------------------------------------------

def train_val_split(
    auth_balanced: list[tuple[str, str, str]],
    imit_balanced: list[tuple[str, str, str]],
    val_fraction: float,
    rng: random.Random,
    return_val_barcodes: bool = False,
):
    """Split into train/val by barcode (prevents same-book leakage).

    Returns (train_rows, val_rows) where each row is (text, label).
    Label 0 = authentic, 1 = imitation.
    If return_val_barcodes is True, returns (train_rows, val_rows, val_barcodes).
    """
    all_barcodes = sorted(set(bc for _, bc, _ in auth_balanced + imit_balanced))
    rng.shuffle(all_barcodes)
    n_val = max(1, round(len(all_barcodes) * val_fraction))
    val_barcodes = set(all_barcodes[:n_val])

    train_rows: list[tuple[str, int]] = []
    val_rows: list[tuple[str, int]] = []

    for text, bc, _ in auth_balanced:
        (val_rows if bc in val_barcodes else train_rows).append((text, 0))

    for text, bc, _ in imit_balanced:
        (val_rows if bc in val_barcodes else train_rows).append((text, 1))

    if return_val_barcodes:
        return train_rows, val_rows, val_barcodes
    return train_rows, val_rows


# ---------------------------------------------------------------------------
# 5. Output
# ---------------------------------------------------------------------------

def write_tsv(rows: list[tuple[str, int]], path: Path) -> None:
    """Write (text, label) rows as a TSV file with header."""
    with open(path, "w", encoding="utf-8") as f:
        f.write("text\tlabel\n")
        for text, label in rows:
            clean = text.replace("\t", " ").replace("\n", " ")
            f.write(f"{clean}\t{label}\n")


def write_dropped_tsv(dropped_log: list[tuple], path: Path) -> None:
    """Write dropped-lines log as TSV."""
    with open(path, "w", encoding="utf-8") as f:
        f.write("side\tbarcode\tline_text\tdrop_reason\n")
        for side, bc, text, reason in dropped_log:
            clean = text.replace("\t", " ").replace("\n", " ")
            f.write(f"{side}\t{bc}\t{clean}\t{reason}\n")


# ---------------------------------------------------------------------------
# 6. Verification report
# ---------------------------------------------------------------------------

def _bin_census(samples: list[tuple[str, str, str]]) -> dict:
    """Compute bin census for a list of (text, barcode, bin_name) tuples."""
    counts = {name: 0 for name in BIN_NAMES}
    digit_high = 0
    digit_any  = 0
    total_words = 0
    for text, _, bin_name in samples:
        nw = count_words(text)
        total_words += nw
        df = digit_fraction(text)
        if df > _DIGIT_THRESH_HIGH:
            digit_high += 1
        if df > 0:
            digit_any += 1
        counts[bin_name] += 1
    return {
        "counts": counts,
        "digit_high": digit_high,
        "digit_any": digit_any,
        "total": len(samples),
        "mean_words": total_words / len(samples) if samples else 0.0,
    }


def print_report(
    auth_balanced: list,
    imit_balanced: list,
    train_rows: list,
    val_rows: list,
    auth_read_total: int,
    imit_read_total: int,
    auth_drop_total: int,
    imit_drop_total: int,
    auth_bad_barcodes: set,
    imit_bad_barcodes: set,
    verbose: bool = False,
    auth_barcode_accepted: Optional[dict] = None,
    imit_barcode_accepted: Optional[dict] = None,
) -> None:
    print("\n" + "=" * 62)
    print("  FILTER / BALANCE / CLEAN  REPORT")
    print("=" * 62)

    # Lines read / dropped
    def pct(n, total):
        return f"{100 * n / total:.1f}%" if total else "n/a"

    print(f"\n{'Side':<12} {'Lines read':>12} {'Dropped':>10} {'Drop%':>7}")
    print("-" * 44)
    print(f"{'Authentic':<12} {auth_read_total:>12,} {auth_drop_total:>10,} {pct(auth_drop_total, auth_read_total):>7}")
    print(f"{'Imitation':<12} {imit_read_total:>12,} {imit_drop_total:>10,} {pct(imit_drop_total, imit_read_total):>7}")

    cross_bad = auth_bad_barcodes | imit_bad_barcodes
    if cross_bad:
        print(f"\nBarcodes dropped (>50% filter rate on any file): {', '.join(sorted(cross_bad))}")

    # Length + digit census per side
    for side_label, samples in [("Authentic", auth_balanced), ("Imitation", imit_balanced)]:
        stats = _bin_census(samples)
        n = stats["total"]
        print(f"\n--- {side_label} length bins (n={n:,}, mean {stats['mean_words']:.1f} words) ---")
        print(f"  {'Bin':<10} {'Count':>8}  {'Actual':>7}  {'Target':>7}")
        for bname in BIN_NAMES:
            c = stats["counts"].get(bname, 0)
            tgt = BIN_TARGETS[bname]
            actual = f"{100 * c / n:.1f}%" if n else "n/a"
            print(f"  {bname:<10} {c:>8,}  {actual:>7}  {100*tgt:>6.0f}%")
        dh = stats["digit_high"]
        da = stats["digit_any"]
        print(f"  {'digit >5%':<10} {dh:>8,}  {pct(dh,n):>7}  {'2%':>7}  (cap)")
        print(f"  {'digit >0':<10} {da:>8,}  {pct(da,n):>7}  {'7%':>7}  (cap)")

    # Train / val sizes
    n_train_auth = sum(1 for _, lbl in train_rows if lbl == 0)
    n_train_imit = sum(1 for _, lbl in train_rows if lbl == 1)
    n_val_auth   = sum(1 for _, lbl in val_rows   if lbl == 0)
    n_val_imit   = sum(1 for _, lbl in val_rows   if lbl == 1)
    print(f"\n--- Train / val split ---")
    print(f"  Train: {len(train_rows):,} rows  ({n_train_auth:,} authentic + {n_train_imit:,} imitation)")
    print(f"  Val:   {len(val_rows):,} rows  ({n_val_auth:,} authentic + {n_val_imit:,} imitation)")

    # Per-barcode verbose output
    if verbose and auth_barcode_accepted:
        print("\n--- Authentic per-barcode accepted counts (desc) ---")
        for bc, cnt in sorted(auth_barcode_accepted.items(), key=lambda x: -x[1]):
            print(f"  {bc}: {cnt}")
    if verbose and imit_barcode_accepted:
        print("\n--- Imitation per-barcode accepted counts (desc) ---")
        for bc, cnt in sorted(imit_barcode_accepted.items(), key=lambda x: -x[1]):
            print(f"  {bc}: {cnt}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Filter, balance, and clean authentic/imitation text for DeBERTa training.",
    )
    parser.add_argument(
        "-n", "--n-per-side", type=int, default=5000, dest="n_per_side", metavar="N",
        help="Target examples per side (default: 5000)",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed (default: 42)",
    )
    parser.add_argument(
        "--val-fraction", type=float, default=0.2, dest="val_fraction",
        help="Fraction of barcodes held out for validation (default: 0.2)",
    )
    parser.add_argument(
        "--output-dir", default=None, dest="output_dir",
        help="Directory for output TSVs (default: bertclassify/)",
    )
    parser.add_argument(
        "--log-dropped", action="store_true", dest="log_dropped",
        help="Write dropped_lines.tsv listing every rejected line and reason",
    )
    parser.add_argument(
        "--lines-per-file", type=int, default=80, dest="lines_per_file", metavar="N",
        help="Max non-empty lines to read from each file (default: 80)",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Print per-barcode accepted counts",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    rng = random.Random(args.seed)

    output_dir = Path(args.output_dir) if args.output_dir else SCRIPT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- 0. Load ---
    print("Loading authentic side ...")
    auth_barcode_lines, auth_file_data = load_side(AUTHENTIC_DIR, args.lines_per_file)
    print("Loading imitation side ...")
    imit_barcode_lines, imit_file_data = load_side(IMITATION_DIR, args.lines_per_file)

    auth_read_total = sum(len(lines) for _, lines in auth_file_data.values())
    imit_read_total = sum(len(lines) for _, lines in imit_file_data.values())
    print(f"  Authentic: {auth_read_total:,} lines, {len(auth_file_data)} files, "
          f"{len(auth_barcode_lines)} barcodes")
    print(f"  Imitation: {imit_read_total:,} lines, {len(imit_file_data)} files, "
          f"{len(imit_barcode_lines)} barcodes")

    # --- 1. Filter ---
    print("\nFiltering ...")
    auth_filtered, auth_bad, auth_dropped_log = filter_side(
        auth_file_data, "authentic", args.log_dropped
    )
    imit_filtered, imit_bad, imit_dropped_log = filter_side(
        imit_file_data, "imitation", args.log_dropped
    )

    # Cross-side barcode drop: if bad on either side, remove from both
    cross_bad = auth_bad | imit_bad
    auth_filtered = {bc: lines for bc, lines in auth_filtered.items() if bc not in cross_bad}
    imit_filtered = {bc: lines for bc, lines in imit_filtered.items() if bc not in cross_bad}

    auth_kept = sum(len(l) for l in auth_filtered.values())
    imit_kept = sum(len(l) for l in imit_filtered.values())
    auth_drop_total = auth_read_total - auth_kept
    imit_drop_total = imit_read_total - imit_kept
    print(f"  Authentic: {auth_kept:,} lines kept after filtering "
          f"({len(cross_bad)} barcodes dropped)")
    print(f"  Imitation: {imit_kept:,} lines kept after filtering")

    # --- 2+3. Normalize + Balance ---
    print("\nBalancing ...")
    auth_balanced = balance_side(auth_filtered, args.n_per_side, rng)
    imit_balanced = balance_side(imit_filtered, args.n_per_side, rng)
    print(f"  Authentic: {len(auth_balanced):,} examples selected")
    print(f"  Imitation: {len(imit_balanced):,} examples selected")

    # --- 4. Train / val split ---
    train_rows, val_rows = train_val_split(
        auth_balanced, imit_balanced, args.val_fraction, rng
    )
    rng.shuffle(train_rows)
    rng.shuffle(val_rows)

    # --- 5. Write output ---
    train_path = output_dir / "train.tsv"
    val_path   = output_dir / "val.tsv"
    write_tsv(train_rows, train_path)
    write_tsv(val_rows,   val_path)
    print(f"\nWrote {len(train_rows):,} rows → {train_path}")
    print(f"Wrote {len(val_rows):,} rows → {val_path}")

    if args.log_dropped:
        dropped_path = output_dir / "dropped_lines.tsv"
        all_dropped = auth_dropped_log + imit_dropped_log
        write_dropped_tsv(all_dropped, dropped_path)
        print(f"Wrote {len(all_dropped):,} dropped lines → {dropped_path}")

    # --- 6. Report ---
    auth_barcode_accepted: dict[str, int] = {}
    imit_barcode_accepted: dict[str, int] = {}
    for _, bc, _ in auth_balanced:
        auth_barcode_accepted[bc] = auth_barcode_accepted.get(bc, 0) + 1
    for _, bc, _ in imit_balanced:
        imit_barcode_accepted[bc] = imit_barcode_accepted.get(bc, 0) + 1

    print_report(
        auth_balanced, imit_balanced,
        train_rows, val_rows,
        auth_read_total, imit_read_total,
        auth_drop_total, imit_drop_total,
        auth_bad, imit_bad,
        verbose=args.verbose,
        auth_barcode_accepted=auth_barcode_accepted,
        imit_barcode_accepted=imit_barcode_accepted,
    )


if __name__ == "__main__":
    main()

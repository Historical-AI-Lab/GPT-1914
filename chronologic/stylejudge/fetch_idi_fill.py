"""
fetch_idi_fill.py

Phase B.4 of the style judge (see phase-b-plan.md, NOTES.md).

Fills the holes the census found in the dating corpus -- 1831-1869 has essentially
nothing, and the 1925-1930 edge is thin -- by selecting volumes from the IDI catalog
and extracting their text off /Volumes/SeagateVault.

This is NOT a download. The text is already on the drive (70,097 records in
from1800to1850-*, 101,272 in from1851to1880-*), and situate/getIDI/get_idi.py already
streamed the HuggingFace dataset to completion. This is selection plus extraction.

Two subcommands so candidates can be inspected before a long extraction:

    fetch_idi_fill.py sample     # parquet -> idi_fill_metadata.csv
    fetch_idi_fill.py extract    # metadata + byte-offset indexes -> {BARCODE}.txt

Sampling logic mirrors booksample/edge_sampler.py: a two-pass probabilistic draw
rather than "first N per year", because the parquet has an underlying ordering
(more famous books were digitized first) that a greedy sample would inherit.

Vetting is mechanical. The include_yn workflow in booksample/ exists because the
*benchmark* sample was deliberately oversampled so interesting volumes could be
hand-picked; date prediction has no such requirement. Anything real, English, and not
degenerate (e.g. almost no text because the volume is plates) is fine.

Run from the repo root with the py310hf interpreter:

    ~/Dropbox/python/py310hf/bin/python3 stylejudge/fetch_idi_fill.py sample
    ~/Dropbox/python/py310hf/bin/python3 stylejudge/fetch_idi_fill.py extract
"""

import argparse
import csv
import json
import os
import pickle
import random
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_corpus_manifest import (            # noqa: E402
    REPO_ROOT, SEAGATE, IDI_PARQUET,
    normalize_barcode, parse_year, build_forbidden_set, is_english,
)

HOME = os.path.expanduser("~")
FILL_ROOT = f"{HOME}/workdata/chronologic-dating-corpus"
DEFAULT_OUT_DIR = f"{FILL_ROOT}/idi_fill"

# One metadata CSV per sample run, named for its ranges. A single shared default
# path let a second run silently clobber the first one's metadata and orphan its
# already-extracted text; `extract` and the manifest both read the whole glob.
META_GLOB = f"{FILL_ROOT}/idi_fill_metadata*.csv"


def default_meta_path(ranges):
    span = "_".join(f"{lo}-{hi}" for lo, hi, _cap in ranges)
    return f"{FILL_ROOT}/idi_fill_metadata_{span}.csv"

# The two byte-offset index pickles. They cover DISJOINT jsonl files; merged they
# span every bucket 1831-1930 needs, so extraction can seek() instead of scanning
# ~400 GB the way booksample/edge_extractor.py does.
INDEX_PICKLES = [
    os.path.join(REPO_ROOT, "booksample", "barcode_index.pkl"),
    f"{HOME}/Library/CloudStorage/Dropbox/python/situate/pubdate/work/pubdate_barcode_index.pkl",
]

# Metadata whose barcodes must not be re-drawn. The first two are the permitted
# extractions (no point duplicating); full_edge_metadata.csv is the 749-row edge
# oversample, avoided as free insurance since those candidates may still be drawn
# into the benchmark later.
EXTRA_EXCLUSION_META = [
    "booksample/sample1000_metadata.csv",
    "booksample/avery_metadata.csv",
    "booksample/full_edge_metadata.csv",
    "booksample/edgesample/edge_metadata_annotated.csv",
]

DEFAULT_RANGES = ["1831-1869:15", "1925-1930:15"]

# Buckets covering the default ranges, for the --allow-scan fallback only.
SCAN_FILES = [
    "from1800to1850-0.jsonl", "from1800to1850-1.jsonl", "from1800to1850-2.jsonl",
    "from1851to1880-0.jsonl", "from1851to1880-1.jsonl", "from1851to1880-2.jsonl",
    "from1901to1930-0.jsonl", "from1901to1930-1.jsonl", "from1901to1930-2.jsonl",
]

BATCH_SIZE = 5000
SAFETY_FRACTION = 0.6           # from edge_sampler: quota expected to fill by 60% of pool
MAX_BOOKS_PER_AUTHOR = 2
DEFAULT_SEED = 20260809

# Filters standing in for manual vetting. page_count and token_count together are
# what catch plate books and near-empty scans.
DEFAULT_MIN_PAGES = 40
DEFAULT_MIN_TOKENS = 10000
OCR_AUTO_PERCENTILE = 10        # --min-ocr-score auto -> drop the worst 10% of scans

PASS1_COLS = [
    "barcode_src", "date1_src", "language_distribution_gen",
    "page_count_src", "token_count_o200k_base_gen", "ocr_score_gen",
]
LOAD_COLS = PASS1_COLS + [
    "title_src", "author_src", "date2_src", "date_types_src", "language_src",
    "topic_or_subject_gen", "genre_or_form_src", "ocr_score_src",
    "likely_duplicates_barcodes_gen",
]
OUT_COLS = [
    "barcode_src", "title_src", "author_src", "date1_src", "date2_src",
    "date_types_src", "page_count_src", "token_count_o200k_base_gen",
    "language_src", "topic_or_subject_gen", "genre_or_form_src",
    "ocr_score_src", "ocr_score_gen", "likely_duplicates_barcodes_gen",
]


def require_drive():
    if not os.path.isdir(SEAGATE):
        sys.exit(f"ERROR: {SEAGATE} is not mounted. Both subcommands need it.")


def parse_ranges(specs):
    """['1831-1869:15'] -> [(1831, 1869, 15)]. A cap of 0 means no cap."""
    out = []
    for s in specs:
        try:
            span, cap = s.split(":")
            lo, hi = span.split("-")
            out.append((int(lo), int(hi), int(cap) or None))
        except ValueError:
            sys.exit(f"ERROR: bad --ranges value {s!r}; expected LO-HI:MAX_PER_YEAR")
    return out


def find_range(year, ranges):
    for r in ranges:
        if r[0] <= year <= r[1]:
            return r
    return None


def is_continuing_resource(date_types_src):
    """IDI's `date_types_src` marks serials ('Continuing resource ...') whose
    single-year `date1_src` is the least trustworthy in the catalog — a
    periodical run coded to one nominal year, not a monograph's actual
    publication date. Flagged so `--continuing-resource-cap-fraction` can
    throttle them at draw time instead of the reviewer catching it by hand
    later (measured at 27.6% of the two existing idi_fill batches).
    """
    return "continuing resource" in str(date_types_src or "").lower()


def is_exempt_author(author):
    """Blank, unknown, or anonymous authors are exempt from the per-author cap."""
    if author is None:
        return True
    s = str(author).strip().lower()
    return s in ("", "nan", "none", "unknown") or "anonymous" in s


def percentile(values, q):
    if not values:
        return 0.0
    s = sorted(values)
    idx = (q / 100.0) * (len(s) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] * (1 - (idx - lo)) + s[hi] * (idx - lo)


def as_float(v, default=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def as_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


# --------------------------------------------------------------------------
# sample
# --------------------------------------------------------------------------

def load_extra_exclusions(root):
    """Union of normalized barcode_src across the extra metadata CSVs."""
    out = set()
    for rel in EXTRA_EXCLUSION_META:
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            print(f"  WARNING: {rel} not found, skipping")
            continue
        n = 0
        with open(path, newline="", encoding="utf-8-sig", errors="replace") as fh:
            for row in csv.DictReader(fh):
                bc = row.get("barcode_src") or row.get("﻿barcode_src")
                if bc:
                    out.add(normalize_barcode(bc))
                    n += 1
        print(f"  {rel}: {n} barcodes")
    return out


def pass_one(pf, ranges, exclusions, min_pages, min_tokens):
    """Collect per-year ocr_score_gen for every row passing the hard filters.

    The ocr threshold is derived from this distribution, so it can't be applied
    yet; storing the scores lets pass 1's eligible counts be recomputed exactly
    once the threshold is known.
    """
    scores_by_year = defaultdict(list)
    rejected = Counter()
    scanned = 0

    for batch in pf.iter_batches(batch_size=BATCH_SIZE, columns=PASS1_COLS):
        d = batch.to_pydict()
        for i in range(len(d["barcode_src"])):
            scanned += 1
            year = parse_year(d["date1_src"][i])
            if year is None or find_range(year, ranges) is None:
                continue
            if normalize_barcode(d["barcode_src"][i]) in exclusions:
                rejected["excluded"] += 1
                continue
            if not is_english(d["language_distribution_gen"][i]):
                rejected["not_english"] += 1
                continue
            if as_int(d["page_count_src"][i]) < min_pages:
                rejected["too_few_pages"] += 1
                continue
            if as_int(d["token_count_o200k_base_gen"][i]) < min_tokens:
                rejected["too_few_tokens"] += 1
                continue
            scores_by_year[year].append(as_float(d["ocr_score_gen"][i], 0.0))
        if scanned % 200000 < BATCH_SIZE:
            print(f"    ...{scanned:,} rows")

    return scores_by_year, rejected, scanned


def acceptance_probabilities(eligible, ranges):
    """Bernoulli p per year, calibrated so the quota fills by SAFETY_FRACTION of the pool."""
    probs = {}
    for lo, hi, cap in ranges:
        for year in range(lo, hi + 1):
            n = eligible.get(year, 0)
            if cap is None or n == 0:
                probs[year] = 1.0
            else:
                probs[year] = min(1.0, cap / max(n * SAFETY_FRACTION, 1))
    return probs


def cmd_sample(args):
    import pyarrow.parquet as pq

    require_drive()
    ranges = parse_ranges(args.ranges)
    rng = random.Random(args.seed)

    out_path = args.out or default_meta_path(ranges)
    if os.path.exists(out_path) and not args.force:
        sys.exit(f"ERROR: {out_path} already exists. Overwriting it would orphan any "
                 "text already extracted from it. Pass --force to replace, or --out to "
                 "write elsewhere.")
    args.out = out_path

    print("Building forbidden set (benchmark ground-truth sources)...")
    forbidden, _reason, fstats = build_forbidden_set(REPO_ROOT)
    print(f"  {len(forbidden)} forbidden ids")
    print("Loading extra exclusions (already-extracted and oversampled)...")
    exclusions = forbidden | load_extra_exclusions(REPO_ROOT)
    # plus everything previous sample runs already drew, so ranges can overlap safely
    import glob as _glob
    for p in sorted(_glob.glob(META_GLOB)):
        with open(p, newline="", encoding="utf-8-sig") as fh:
            prev = {normalize_barcode(r["barcode_src"])
                    for r in csv.DictReader(fh) if r.get("barcode_src")}
        exclusions |= prev
        print(f"  {os.path.basename(p)}: {len(prev)} already sampled")
    print(f"  {len(exclusions)} barcodes excluded in total")

    print(f"\nRanges: {', '.join(f'{lo}-{hi} (max {cap or 0}/yr)' for lo, hi, cap in ranges)}")
    pf = pq.ParquetFile(IDI_PARQUET)

    print("\nPass 1: counting eligible candidates per year...")
    scores_by_year, rejected, scanned = pass_one(
        pf, ranges, exclusions, args.min_pages, args.min_tokens)
    all_scores = [s for v in scores_by_year.values() for s in v]
    print(f"  scanned {scanned:,} rows; {len(all_scores):,} pass the hard filters")
    for k, v in rejected.most_common():
        print(f"    rejected {k:16s} {v:,}")

    # ---- ocr threshold, read off the observed distribution ---------------
    print("\n  ocr_score_gen distribution over eligible rows:")
    for q in (1, 5, 10, 25, 50, 75, 90):
        print(f"    p{q:<3} {percentile(all_scores, q):.4f}")
    if args.min_ocr_score == "auto":
        min_ocr = percentile(all_scores, OCR_AUTO_PERCENTILE)
        print(f"  --min-ocr-score auto -> p{OCR_AUTO_PERCENTILE} = {min_ocr:.4f}")
    else:
        min_ocr = float(args.min_ocr_score)
        print(f"  --min-ocr-score {min_ocr:.4f} (explicit)")

    eligible = {y: sum(1 for s in v if s >= min_ocr) for y, v in scores_by_year.items()}
    print(f"  {sum(eligible.values()):,} eligible after the ocr floor")
    probs = acceptance_probabilities(eligible, ranges)

    # ---- pass 2 ----------------------------------------------------------
    print("\nPass 2: drawing the sample...")
    selected = []
    per_year = Counter()
    continuing_resource_per_year = Counter()
    author_counts = Counter()
    dup_seen = set()
    dropped = Counter()
    scanned = 0

    for batch in pf.iter_batches(batch_size=BATCH_SIZE, columns=LOAD_COLS):
        d = batch.to_pydict()
        for i in range(len(d["barcode_src"])):
            scanned += 1
            year = parse_year(d["date1_src"][i])
            if year is None:
                continue
            rng_tuple = find_range(year, ranges)
            if rng_tuple is None:
                continue
            cap = rng_tuple[2]
            if cap is not None and per_year[year] >= cap:
                continue

            if is_continuing_resource(d["date_types_src"][i]):
                cr_cap = cap * args.continuing_resource_cap_fraction if cap is not None else None
                if cr_cap is not None and continuing_resource_per_year[year] >= cr_cap:
                    dropped["continuing_resource_capped"] += 1
                    continue

            bc = normalize_barcode(d["barcode_src"][i])
            if bc in exclusions:
                continue
            if not is_english(d["language_distribution_gen"][i]):
                continue
            if as_int(d["page_count_src"][i]) < args.min_pages:
                continue
            if as_int(d["token_count_o200k_base_gen"][i]) < args.min_tokens:
                continue
            if as_float(d["ocr_score_gen"][i], 0.0) < min_ocr:
                continue
            if bc in dup_seen:
                dropped["duplicate"] += 1
                continue

            author = d["author_src"][i]
            if not is_exempt_author(author):
                key = str(author).strip().lower()
                if author_counts[key] >= args.max_per_author:
                    dropped["author_cap"] += 1
                    continue

            if rng.random() > probs.get(year, 1.0):
                continue

            row = {c: d[c][i] for c in OUT_COLS if c in d}
            row["barcode_src"] = bc
            selected.append(row)
            per_year[year] += 1
            if is_continuing_resource(d["date_types_src"][i]):
                continuing_resource_per_year[year] += 1
            if not is_exempt_author(author):
                author_counts[str(author).strip().lower()] += 1
            dup_seen.add(bc)
            # a volume's known duplicates are never drawn afterwards
            for dbc in (d["likely_duplicates_barcodes_gen"][i] or []):
                dup_seen.add(normalize_barcode(dbc))
        if scanned % 200000 < BATCH_SIZE:
            print(f"    ...{scanned:,} rows, {len(selected)} selected")

    for k, v in dropped.most_common():
        print(f"  dropped {k:12s} {v:,}")

    # ---- write ----------------------------------------------------------
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=OUT_COLS, extrasaction="ignore")
        w.writeheader()
        for r in sorted(selected, key=lambda x: (parse_year(x["date1_src"]) or 0,
                                                 x["barcode_src"])):
            w.writerow({k: (json.dumps(v) if isinstance(v, (list, dict)) else v)
                        for k, v in r.items()})
    n_cr = sum(continuing_resource_per_year.values())
    print(f"\n{len(selected)} volumes written to {args.out} "
          f"({n_cr} continuing-resource, cap fraction {args.continuing_resource_cap_fraction})")

    print("\nPer-year yield:")
    empty = []
    for lo, hi, cap in ranges:
        for year in range(lo, hi + 1):
            n = per_year[year]
            flag = "  <-- EMPTY" if n == 0 else ""
            if n == 0:
                empty.append(year)
            print(f"  {year}  {n:3d} / {cap or '-'}   (eligible {eligible.get(year, 0):,}){flag}")
    if empty:
        print(f"\nWARNING: {len(empty)} year(s) yielded nothing: {empty}")

    # exclusion invariant, asserted rather than assumed
    picked = {r["barcode_src"] for r in selected}
    leak = picked & exclusions
    assert not leak, f"EXCLUSION LEAK: {len(leak)} selected volumes are excluded ids"
    print("Exclusion check passed: no selected volume is a benchmark source or a re-draw.")


# --------------------------------------------------------------------------
# extract
# --------------------------------------------------------------------------

def load_merged_index():
    """Merge the two byte-offset pickles. They cover disjoint jsonl files."""
    index = {}
    for path in INDEX_PICKLES:
        if not os.path.exists(path):
            print(f"  WARNING: index not found: {path}")
            continue
        with open(path, "rb") as fh:
            part = pickle.load(fh)
        overlap = len(set(part) & set(index))
        index.update({normalize_barcode(k): v for k, v in part.items()})
        print(f"  {os.path.basename(path)}: {len(part):,} barcodes"
              f"{f' ({overlap:,} overlapping)' if overlap else ''}")
    return index


def write_volume(barcode, rec, out_dir):
    """Write one record's text. Returns True if a file was written."""
    pages = rec.get("text_by_page_gen") or rec.get("text_by_page_src")
    if not pages:
        return False
    text = pages if isinstance(pages, str) else "\n".join(pages)
    with open(os.path.join(out_dir, f"{barcode}.txt"), "w") as out:
        out.write(text)
    return True


def scan_jsonl_for(filenames, wanted, out_dir):
    """Linear-scan fallback (edge_extractor.py's strategy), draining `wanted`.

    Only worth it for IDIsupplement.jsonl (~400 lines) or with --allow-scan; the
    big buckets are hundreds of GB apiece.
    """
    found = 0
    for fname in filenames:
        if not wanted:
            break
        path = os.path.join(SEAGATE, "IDI", fname)
        if not os.path.exists(path):
            continue
        with open(path, "rb") as fh:
            for raw in fh:
                if not wanted:
                    break
                # cheap prefilter: skip json.loads unless a wanted id is in the head
                head = raw[:400].decode("utf-8", "replace").upper()
                hit = next((b for b in wanted if b in head), None)
                if hit is None:
                    continue
                try:
                    rec = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                bc = normalize_barcode(rec.get("barcode_src", ""))
                if bc not in wanted:
                    continue
                wanted.discard(bc)
                if write_volume(bc, rec, out_dir):
                    found += 1
    return found


def cmd_extract(args):
    require_drive()
    os.makedirs(args.out_dir, exist_ok=True)

    import glob as _glob
    paths = sorted(_glob.glob(args.metadata)) if any(c in args.metadata for c in "*?") \
        else [args.metadata]
    if not paths:
        sys.exit(f"ERROR: no metadata files matched {args.metadata}")
    wanted = []
    for p in paths:
        with open(p, newline="", encoding="utf-8-sig") as fh:
            n = [normalize_barcode(r["barcode_src"])
                 for r in csv.DictReader(fh) if r.get("barcode_src")]
        print(f"  {os.path.basename(p)}: {len(n)} barcodes")
        wanted.extend(n)
    wanted = list(dict.fromkeys(wanted))          # de-dup, keep order
    print(f"{len(wanted)} barcodes wanted from {len(paths)} metadata file(s)")

    todo = [b for b in wanted
            if not os.path.exists(os.path.join(args.out_dir, f"{b}.txt"))]
    print(f"{len(wanted) - len(todo)} already extracted; {len(todo)} to go")
    if not todo:
        return

    print("\nLoading byte-offset indexes...")
    index = load_merged_index()
    print(f"  merged: {len(index):,} barcodes")

    missing = [b for b in todo if b not in index]
    if missing:
        print(f"\nWARNING: {len(missing)} wanted barcodes are not in either index"
              f"{' (use --allow-scan to fall back)' if not args.allow_scan else ''}")
        print(f"  e.g. {missing[:5]}")

    # group by source file so each jsonl is opened once, and seek forward in order
    by_file = defaultdict(list)
    for b in todo:
        info = index.get(b)
        if info:
            by_file[info["file"]].append((info["offset"], info["length"], b))

    written = empty = failed = 0

    # IDIsupplement.jsonl is only ~400 lines and is indexed by nothing; always try
    # it for index misses before considering the expensive full scan.
    if missing:
        found = scan_jsonl_for(["IDIsupplement.jsonl"], set(missing), args.out_dir)
        written += found
        missing = [b for b in missing
                   if not os.path.exists(os.path.join(args.out_dir, f"{b}.txt"))]
        print(f"  IDIsupplement.jsonl: recovered {found}; {len(missing)} still missing")

    if missing and args.allow_scan:
        print(f"\nLinear-scanning the big buckets for {len(missing)} barcodes "
              "(this reads hundreds of GB)...")
        found = scan_jsonl_for(SCAN_FILES, set(missing), args.out_dir)
        written += found
        missing = [b for b in missing
                   if not os.path.exists(os.path.join(args.out_dir, f"{b}.txt"))]
        print(f"  recovered {found}; {len(missing)} still missing")

    for fname in sorted(by_file):
        entries = sorted(by_file[fname])
        path = os.path.join(SEAGATE, "IDI", fname)
        if not os.path.exists(path):
            print(f"  WARNING: {path} missing, skipping {len(entries)} volumes")
            failed += len(entries)
            continue
        print(f"  {fname}: {len(entries)} volumes")
        with open(path, "rb") as fh:
            for offset, length, bc in entries:
                fh.seek(offset)
                raw = fh.read(length)
                try:
                    rec = json.loads(raw)
                except json.JSONDecodeError:
                    failed += 1
                    continue
                if write_volume(bc, rec, args.out_dir):
                    written += 1
                else:
                    empty += 1

    print(f"\nWritten {written}; {empty} had no text; {failed} failed; "
          f"{len(missing)} not in any index")
    print(f"Output: {args.out_dir}")


# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("sample", help="select candidates from the IDI parquet")
    s.add_argument("--ranges", action="append", default=None,
                   metavar="LO-HI:MAX_PER_YEAR",
                   help=f"repeatable; default {' '.join(DEFAULT_RANGES)}")
    s.add_argument("--out", default=None,
                   help="default: idi_fill_metadata_<ranges>.csv in the fill root")
    s.add_argument("--force", action="store_true",
                   help="overwrite an existing metadata CSV (orphans its extracted text)")
    s.add_argument("--min-pages", type=int, default=DEFAULT_MIN_PAGES)
    s.add_argument("--min-tokens", type=int, default=DEFAULT_MIN_TOKENS)
    s.add_argument("--min-ocr-score", default="auto",
                   help=f"float, or 'auto' for the p{OCR_AUTO_PERCENTILE} of eligible rows")
    s.add_argument("--max-per-author", type=int, default=MAX_BOOKS_PER_AUTHOR)
    s.add_argument("--seed", type=int, default=DEFAULT_SEED)
    s.add_argument("--continuing-resource-cap-fraction", type=float, default=0.0,
                    help="cap on `date_types_src` = 'Continuing resource ...' rows, as a "
                         "fraction of each year's --ranges cap; 0.0 (default) skips them "
                         "entirely -- their date1_src is a serial's nominal year, not a "
                         "monograph's actual publication date, and is the most work to "
                         "hand-verify in export-for-review")
    s.set_defaults(func=cmd_sample)

    e = sub.add_parser("extract", help="pull text for the sampled barcodes")
    e.add_argument("--metadata", default=META_GLOB,
                   help="a path or a glob; default reads every sample run's CSV")
    e.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    e.add_argument("--allow-scan", action="store_true",
                   help="linear-scan the jsonl files for barcodes missing from the index")
    e.set_defaults(func=cmd_extract)

    args = ap.parse_args()
    if getattr(args, "ranges", None) is None and args.cmd == "sample":
        args.ranges = DEFAULT_RANGES
    args.func(args)


if __name__ == "__main__":
    main()

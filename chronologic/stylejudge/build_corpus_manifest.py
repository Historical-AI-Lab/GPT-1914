"""
build_corpus_manifest.py

Phase B.2 of the style judge (see new-style-judge-spec.md, phase-b-plan.md, NOTES.md).

Walks every collection of human-written text materialized on local disk, joins each
volume to its metadata, and emits a single manifest plus a per-decade census. The
census is what Phase B.3 reads to decide where supplementation is needed.

A manifest row means "usable text, on disk, right now." IDI's ~460k on-drive volumes
are *supply*, not corpus; they get a separate per-decade capacity table streamed from
the IDI parquet (--skip-supply to omit).

Benchmark contamination is the hard constraint: volumes used as benchmark ground-truth
sources must never train a judge that will later score imitations of those same
passages. Excluded volumes stay in the manifest, flagged, so the exclusion is auditable
rather than invisible.

Run from the repo root with the py310hf interpreter:

    ~/Dropbox/python/py310hf/bin/python3 stylejudge/build_corpus_manifest.py
"""

import argparse
import csv
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime

csv.field_size_limit(10_000_000)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.expanduser("~")

SEAGATE = "/Volumes/SeagateVault"
IDI_PARQUET = f"{SEAGATE}/IDI/train-00000-of-00001.parquet"
ECCO_DIR = f"{SEAGATE}/tardis_backup/imac/JointCorpus/eccofull"

WEB_ERA = f"{HOME}/workdata/21c-corpus"
CHICAGO = f"{HOME}/Dropbox/CHICAGO_CORPUS"
FILL_DIR = f"{HOME}/workdata/chronologic-dating-corpus/idi_fill"

FIELDS = [
    "volume_id", "collection", "path", "title", "author", "date", "date_source",
    "word_count", "word_count_method", "language", "excluded", "exclusion_reason",
    "duplicate_of",
]

# Collections can overlap: booksample/averybooks is a strict subset of
# booksample/sample1000books (all 393 barcodes, byte-identical files), so counting
# both double-counts ~38.8M words squarely in the 1875-1924 band. Rows for a
# volume_id already seen in an earlier collection here are kept but flagged
# `duplicate_of`, and the census counts them once.
COLLECTION_PRIORITY = [
    "idi_sample1000", "idi_avery", "idi_fill",
    "idi_benchmark_1875", "idi_edge",
]

# Volumes actually used as benchmark ground-truth sources. Everything else in
# booksample/ is permitted -- verified: sample1000books, averybooks, and
# bertclassify/authentic have zero overlap with any source_htid.
FORBIDDEN_DIRS = {
    "booksample/IDI_sample_1875-25": "benchmark_source_1875-25",
    "booksample/edgebooks": "benchmark_source_edgebooks",
}
FORBIDDEN_META = [
    "booksample/1875-1924/1875-1924_primary_metadata.csv",
    "booksample/1875-1924/1875-1924_metadata_history.csv",
    "booksample/edge_metadata.csv",
    "booksample/primary_metadata.csv",
    "booksample/metadata_history.csv",
]
BENCHMARK_QUESTION_GLOBS = [
    "booksample/chronologic_en_*.jsonl",
    "booksample/*.jsonl",
    "booksample/*/process_files/*.jsonl",
    "booksample/*/old_process_files/*.jsonl",
    "booksample/*/old_files/*.jsonl",
]

DECADE_MIN, DECADE_MAX = 1700, 2030
PLATEAU = (1831, 1930)          # the span the authenticity detector needs
TARGET_PER_DECADE = 150         # the fill target agreed for 1831-1869

# Files sampled per collection when calibrating a bytes-per-word ratio.
CALIBRATION_SAMPLE = 50


# --------------------------------------------------------------------------
# small shared helpers
# --------------------------------------------------------------------------

def normalize_barcode(barcode):
    """Canonical id form. Must be applied to BOTH sides of every join/exclusion.

    Ids appear as 14-digit numerics (32044004376976) and as alphanumerics
    (hvd.hn1eg5 / HN1EG5); this collapses them to one space.
    """
    return str(barcode).replace("hvd.", "").replace("HVD.", "").upper().strip()


YEAR_RE = re.compile(r"(1[6789]\d\d|20\d\d)")


def parse_year(value):
    """First plausible 4-digit year in a string, or None.

    IDI's date1_src carries fill characters ('18uu', '187?'), so a regex beats int().
    """
    if value is None:
        return None
    m = YEAR_RE.search(str(value))
    return int(m.group(1)) if m else None


def read_csv_rows(path, encoding="utf-8-sig"):
    """Rows of a CSV as dicts, tolerating CR-only line endings and odd encodings.

    newline='' lets the csv module do its own line-ending detection, which is the
    only thing that reads the classic-Mac CR-only Chicago and ECCO files correctly.
    """
    with open(path, newline="", encoding=encoding, errors="replace") as fh:
        for row in csv.DictReader(fh):
            yield row


def count_words_in_file(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return sum(len(line.split()) for line in fh)
    except OSError:
        return None


def calibrate_bytes_per_word(paths, sample=CALIBRATION_SAMPLE, seed=1914):
    """Bytes-per-word ratio measured on a sample, rather than a guessed constant.

    Used for the two collections where counting every file is a bad idea: Chicago
    (4.7 GB of Dropbox-backed files -- an exact pass risks rehydration) and ECCO
    (on the external drive).
    """
    import random
    rng = random.Random(seed)
    picks = rng.sample(paths, min(sample, len(paths)))
    total_bytes = total_words = 0
    for p in picks:
        w = count_words_in_file(p)
        if not w:
            continue
        total_bytes += os.path.getsize(p)
        total_words += w
    if not total_words:
        return 6.0
    return total_bytes / total_words


# --------------------------------------------------------------------------
# the forbidden set
# --------------------------------------------------------------------------

def build_forbidden_set(root):
    """(forbidden_ids, reason_by_id, stats) -- benchmark ground-truth sources.

    Three contributions, unioned: the two forbidden directories' filenames, the
    barcodes in the benchmark metadata CSVs, and every source_htid appearing in any
    question JSONL. All normalized with normalize_barcode().
    """
    reason = {}
    stats = Counter()

    for rel, why in FORBIDDEN_DIRS.items():
        for p in glob.glob(os.path.join(root, rel, "*")):
            if os.path.isdir(p):
                continue
            bid = normalize_barcode(os.path.splitext(os.path.basename(p))[0])
            reason.setdefault(bid, why)
            stats[why] += 1

    for rel in FORBIDDEN_META:
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            continue
        n = 0
        for row in read_csv_rows(path):
            bc = row.get("barcode_src") or row.get("﻿barcode_src") or row.get("htid")
            if bc:
                reason.setdefault(normalize_barcode(bc), f"metadata:{os.path.basename(rel)}")
                n += 1
        stats[f"metadata:{os.path.basename(rel)}"] = n

    seen_files = set()
    for pattern in BENCHMARK_QUESTION_GLOBS:
        seen_files.update(glob.glob(os.path.join(root, pattern)))
    n_ids = 0
    for f in sorted(seen_files):
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    for key in ("source_htid", "htid", "barcode"):
                        if rec.get(key):
                            bid = normalize_barcode(rec[key])
                            reason.setdefault(bid, "benchmark_source_htid")
                            n_ids += 1
        except (json.JSONDecodeError, OSError):
            continue          # tagged-sentence and intermediate files aren't questions
    stats["question_files_scanned"] = len(seen_files)
    stats["source_htid_hits"] = n_ids

    return set(reason), reason, stats


# --------------------------------------------------------------------------
# collection loaders -- each yields partial rows; word counts are filled in later
# --------------------------------------------------------------------------

def _idi_collection(root, name, text_dir, meta_rel, encoding="utf-8-sig"):
    """One of the IDI extractions: {BARCODE}.txt joined to a *_metadata.csv."""
    meta = {}
    path = os.path.join(root, meta_rel)
    if os.path.exists(path):
        for row in read_csv_rows(path, encoding=encoding):
            bc = row.get("barcode_src") or row.get("﻿barcode_src")
            if bc:
                meta[normalize_barcode(bc)] = row
    rows = []
    for p in sorted(glob.glob(os.path.join(root, text_dir, "*.txt"))):
        vid = normalize_barcode(os.path.splitext(os.path.basename(p))[0])
        m = meta.get(vid, {})
        rows.append({
            "volume_id": vid, "collection": name, "path": p,
            "title": (m.get("title_src") or "").strip(),
            "author": (m.get("author_src") or "").strip(),
            "date": parse_year(m.get("date1_src") or m.get("firstpub")),
            "date_source": "catalog_date1_src" if m else "missing",
            "language": (m.get("language_src") or "eng").strip() or "eng",
        })
    return rows


def load_idi_collections(root):
    rows = []
    rows += _idi_collection(root, "idi_sample1000",
                            "booksample/sample1000books", "booksample/sample1000_metadata.csv")
    rows += _idi_collection(root, "idi_avery",
                            "booksample/averybooks", "booksample/avery_metadata.csv")
    rows += _idi_collection(root, "idi_edge",
                            "booksample/edgebooks", "booksample/edge_metadata.csv")
    rows += _idi_collection(root, "idi_benchmark_1875",
                            "booksample/IDI_sample_1875-25",
                            "booksample/1875-1924/1875-1924_metadata_history.csv")
    return rows


def load_idi_fill(root):
    """The Phase B.4 output, once it exists."""
    if not os.path.isdir(FILL_DIR):
        return []
    # one CSV per sample run (idi_fill_metadata_<ranges>.csv); read them all
    meta = {}
    for mpath in sorted(glob.glob(os.path.join(os.path.dirname(FILL_DIR),
                                               "idi_fill_metadata*.csv"))):
        for row in read_csv_rows(mpath):
            bc = row.get("barcode_src")
            if bc:
                meta[normalize_barcode(bc)] = row
    rows = []
    for p in sorted(glob.glob(os.path.join(FILL_DIR, "*.txt"))):
        vid = normalize_barcode(os.path.splitext(os.path.basename(p))[0])
        m = meta.get(vid, {})
        rows.append({
            "volume_id": vid, "collection": "idi_fill", "path": p,
            "title": (m.get("title_src") or "").strip(),
            "author": (m.get("author_src") or "").strip(),
            "date": parse_year(m.get("date1_src")),
            "date_source": "catalog_date1_src" if m else "missing",
            "language": "eng",
        })
    return rows


COHA_NAME_RE = re.compile(r"^(?P<genre>[a-z]+)_(?P<year>\d{4})_(?P<id>\d+)")


def load_coha(root):
    """COHA: date lives in the filename, genre_yyyy_sourceid.txt."""
    coha_dir = os.path.join(os.path.dirname(root), "anachronism", "coha")
    rows = []
    for p in sorted(glob.glob(os.path.join(coha_dir, "*.txt"))):
        stem = os.path.basename(p)[:-4]
        m = COHA_NAME_RE.match(stem)
        if not m:
            continue
        rows.append({
            "volume_id": stem, "collection": f"coha_{m.group('genre')}", "path": p,
            "title": "", "author": "",
            "date": int(m.group("year")), "date_source": "filename",
            "language": "eng",
        })
    return rows


def load_web_era(root):
    """OAPEN + Common Crawl. Their manifests already carry word_count."""
    rows = []
    specs = [
        ("oapen_web", "web_era_corpus/oapen/manifest.csv", "publication_year"),
        ("oapen_1925_1990", "web_era_corpus/oapen_1925_1990/manifest.csv", "publication_year"),
        # crawl_timestamp is empty in this manifest (it was reconstructed from disk);
        # crawl_year is the populated column
        ("commoncrawl", "web_era_corpus/commoncrawl/manifest.csv", "crawl_year"),
    ]
    for name, rel, date_col in specs:
        mpath = os.path.join(WEB_ERA, rel)
        if not os.path.exists(mpath):
            print(f"  WARNING: missing {mpath}")
            continue
        for i, row in enumerate(read_csv_rows(mpath)):
            tp = (row.get("text_path") or "").strip()
            if not tp:
                continue
            # text_path is relative to the 21c-corpus root, not to the manifest
            path = tp if os.path.isabs(tp) else os.path.join(WEB_ERA, tp)
            wc = row.get("word_count")
            rows.append({
                "volume_id": os.path.splitext(os.path.basename(path))[0][:120] or f"{name}_{i}",
                "collection": name, "path": path,
                "title": (row.get("title") or "").strip(),
                "author": (row.get("author") or "").strip(),
                "date": parse_year(row.get(date_col)),
                "date_source": "manifest_year" if date_col == "publication_year" else "crawl_year",
                "language": "eng",
                "word_count": int(wc) if wc and str(wc).strip().isdigit() else None,
                "word_count_method": "manifest",
            })
    return rows


def load_chicago(root):
    """Chicago novels. CSV is latin-1 with CR-only line endings and quoted commas."""
    meta_path = os.path.join(CHICAGO, "CHICAGO_NOVEL_CORPUS_METADATA",
                             "CHICAGO_CORPUS_NOVELS.csv")
    text_dir = os.path.join(CHICAGO, "CHICAGO_NOVEL_CORPUS")
    if not os.path.exists(meta_path):
        print(f"  WARNING: missing {meta_path}")
        return []
    rows = []
    for row in read_csv_rows(meta_path, encoding="latin-1"):
        fn = (row.get("FILENAME") or "").strip()
        if not fn:
            continue
        # 9,153 files but 9,089 volumes: the extras are unpadded-id duplicates
        if not fn.startswith("0"):
            continue
        path = os.path.join(text_dir, fn)
        author = " ".join(x for x in [(row.get("AUTH_FIRST") or "").strip(),
                                      (row.get("AUTH_LAST") or "").strip()] if x)
        rows.append({
            "volume_id": os.path.splitext(fn)[0], "collection": "chicago_fiction",
            "path": path,
            "title": (row.get("TITLE") or "").strip(), "author": author,
            "date": parse_year(row.get("PUBL_DATE")),
            "date_source": "chicago_publ_date", "language": "eng",
        })
    return rows


def load_ecco(root):
    """TCP-ECCO, 1701-1800. Metadata is CR-only TSV and carries numwords."""
    meta_path = os.path.join(ECCO_DIR, "ECCOfullmeta.txt")
    src_dir = os.path.join(ECCO_DIR, "EccoSource")
    if not os.path.exists(meta_path):
        print(f"  WARNING: missing {meta_path}")
        return []
    on_disk = {os.path.splitext(f)[0]: os.path.join(src_dir, f)
               for f in os.listdir(src_dir) if f.endswith(".txt")}
    rows = []
    with open(meta_path, newline="", encoding="latin-1", errors="replace") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            # files are named by fileID or, for some, by localID
            path = on_disk.get((row.get("fileID") or "").strip()) \
                or on_disk.get((row.get("localID") or "").strip())
            if not path:
                continue
            nw = (row.get("numwords") or "").strip()
            rows.append({
                "volume_id": os.path.splitext(os.path.basename(path))[0],
                "collection": "ecco", "path": path,
                "title": (row.get("title") or "").strip()[:300],
                "author": (row.get("author") or "").strip(),
                "date": parse_year(row.get("date")),
                "date_source": "ecco_meta", "language": "eng",
                "word_count": int(nw) if nw.isdigit() else None,
                "word_count_method": "manifest",
            })
    return rows


# --------------------------------------------------------------------------
# word counts
# --------------------------------------------------------------------------

# Collections too large or too slow to count exactly: estimate from file size,
# using a ratio calibrated per collection rather than a guessed constant.
ESTIMATE_COLLECTIONS = {"chicago_fiction", "ecco"}


def fill_word_counts(rows, cache, recount):
    by_collection = defaultdict(list)
    for r in rows:
        by_collection[r["collection"]].append(r)

    ratios = {}
    for name, group in sorted(by_collection.items()):
        needed = [r for r in group if r.get("word_count") in (None, "")]
        if not recount:
            for r in needed:
                hit = cache.get((r["collection"], r["volume_id"]))
                if hit:
                    r["word_count"], r["word_count_method"] = hit
            needed = [r for r in group if r.get("word_count") in (None, "")]
        if not needed:
            continue

        if name in ESTIMATE_COLLECTIONS:
            paths = [r["path"] for r in needed if os.path.exists(r["path"])]
            if not paths:
                continue
            ratio = calibrate_bytes_per_word(paths)
            ratios[name] = ratio
            print(f"  {name}: estimating from size, {ratio:.2f} bytes/word "
                  f"(calibrated on {min(CALIBRATION_SAMPLE, len(paths))} files)")
            for r in needed:
                try:
                    r["word_count"] = int(os.path.getsize(r["path"]) / ratio)
                    r["word_count_method"] = "estimated"
                except OSError:
                    r["word_count"], r["word_count_method"] = None, "missing"
        else:
            print(f"  {name}: counting {len(needed)} files exactly...")
            for r in needed:
                w = count_words_in_file(r["path"])
                r["word_count"] = w
                r["word_count_method"] = "exact" if w is not None else "missing"
    return ratios


def load_cache(path):
    cache = {}
    if not os.path.exists(path):
        return cache
    for row in read_csv_rows(path):
        wc = (row.get("word_count") or "").strip()
        if wc.isdigit():
            cache[(row["collection"], row["volume_id"])] = (
                int(wc), row.get("word_count_method") or "cached")
    return cache


# --------------------------------------------------------------------------
# IDI supply
# --------------------------------------------------------------------------

def idi_supply_by_decade(forbidden):
    """Per-decade count of English IDI volumes on the drive, post-exclusion.

    This is capacity, not corpus: it tells B.3 whether a shortfall is fixable.
    """
    import pyarrow.parquet as pq

    counts = Counter()
    pf = pq.ParquetFile(IDI_PARQUET)
    cols = ["barcode_src", "date1_src", "language_distribution_gen"]
    seen = 0
    for batch in pf.iter_batches(batch_size=5000, columns=cols):
        d = batch.to_pydict()
        for bc, date, langdist in zip(d["barcode_src"], d["date1_src"],
                                      d["language_distribution_gen"]):
            seen += 1
            year = parse_year(date)
            if year is None or not (DECADE_MIN <= year < DECADE_MAX):
                continue
            if normalize_barcode(bc) in forbidden:
                continue
            if not is_english(langdist):
                continue
            counts[(year // 10) * 10] += 1
        if seen % 200000 < 5000:
            print(f"    ...{seen:,} parquet rows")
    return counts, seen


def is_english(langdist, threshold=0.75):
    """eng proportion > threshold in IDI's language_distribution_gen."""
    if not langdist:
        return False
    try:
        langs = langdist.get("language") or []
        props = langdist.get("proportion") or []
        for lg, pr in zip(langs, props):
            if str(lg).lower().startswith("eng"):
                return float(pr) > threshold
    except (AttributeError, TypeError, ValueError):
        return False
    return False


# --------------------------------------------------------------------------
# report
# --------------------------------------------------------------------------

def decade_table(rows):
    """{decade: {collection: [volumes, words]}} over permitted, dated rows."""
    table = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for r in rows:
        if r["excluded"] or r["duplicate_of"] or not r["date"]:
            continue
        dec = (int(r["date"]) // 10) * 10
        if not (DECADE_MIN <= dec < DECADE_MAX):
            continue
        cell = table[dec][r["collection"]]
        cell[0] += 1
        cell[1] += int(r["word_count"] or 0)
    return table


def write_report(path, rows, table, supply, forbidden_stats, ratios, args):
    L = []
    a = L.append
    permitted = [r for r in rows if not r["excluded"] and not r["duplicate_of"]]
    excluded = [r for r in rows if r["excluded"]]

    a("# Dating-corpus census\n")
    a(f"Generated {datetime.now().isoformat(timespec='seconds')} by "
      "`stylejudge/build_corpus_manifest.py`.\n")
    a(f"**{len(permitted):,} permitted volumes** on local disk, "
      f"{sum(int(r['word_count'] or 0) for r in permitted):,} words. "
      f"{len(excluded):,} volumes excluded as benchmark sources.\n")

    a("## Exclusions\n")
    a("Volumes used as benchmark ground-truth sources are forbidden: a judge that scores "
      "imitations of a passage must not have trained on that passage.\n")
    a("| Reason | Volumes in manifest |")
    a("|---|---|")
    for why, c in Counter(r["exclusion_reason"] for r in excluded).most_common():
        a(f"| `{why}` | {c} |")
    a("")
    a(f"Forbidden-id set built from {forbidden_stats['question_files_scanned']} question "
      f"files ({forbidden_stats['source_htid_hits']} `source_htid` mentions), the two "
      "forbidden directories, and the benchmark metadata CSVs.\n")

    a("## Volumes per decade\n")
    collections = sorted({c for d in table.values() for c in d})
    a("| Decade | " + " | ".join(collections) + " | **total** |")
    a("|---" * (len(collections) + 2) + "|")
    for dec in sorted(table):
        cells = [str(table[dec][c][0] or "") for c in collections]
        tot = sum(table[dec][c][0] for c in collections)
        a(f"| {dec}s | " + " | ".join(cells) + f" | **{tot}** |")
    a("")

    a("## Words per decade (millions)\n")
    a("| Decade | " + " | ".join(collections) + " | **total** |")
    a("|---" * (len(collections) + 2) + "|")
    for dec in sorted(table):
        cells = [(f"{table[dec][c][1]/1e6:.1f}" if table[dec][c][1] else "")
                 for c in collections]
        tot = sum(table[dec][c][1] for c in collections)
        a(f"| {dec}s | " + " | ".join(cells) + f" | **{tot/1e6:.1f}** |")
    a("")

    a("## Gap analysis: the 1831-1930 plateau\n")
    a(f"Target {TARGET_PER_DECADE} volumes/decade, prorated for the two partial decades "
      f"({PLATEAU[0]}-1839 is 9 years, 1930 alone is 1). Counts here are restricted to "
      "years inside the plateau, so they differ from the full-decade tables above. The "
      "existing 1870-1924 core runs higher than target, ~250/decade; 150 is the agreed "
      "conservative fill level.\n")
    a("| Decade | years in plateau | volumes held | words held | target | deficit | IDI supply |")
    a("|---|---|---|---|---|---|---|")
    for dec in range(PLATEAU[0] // 10 * 10, PLATEAU[1] + 1, 10):
        lo, hi = max(dec, PLATEAU[0]), min(dec + 9, PLATEAU[1])
        n_years = hi - lo + 1
        inrange = [r for r in rows if not r["excluded"] and not r["duplicate_of"]
                   and r["date"] and lo <= int(r["date"]) <= hi]
        held = len(inrange)
        words = sum(int(r["word_count"] or 0) for r in inrange)
        target = round(TARGET_PER_DECADE * n_years / 10)
        deficit = max(0, target - held)
        sup = f"{supply.get(dec, 0):,}" if supply else "not computed"
        flag = " **needs fill**" if deficit else ""
        a(f"| {dec}s | {lo}-{hi} ({n_years}) | {held} | {words/1e6:.1f}M | {target} | "
          f"{deficit}{flag} | {sup} |")
    a("")
    n_fill = sum(1 for r in rows if r["collection"] == "idi_fill" and not r["duplicate_of"])
    if n_fill:
        fill_words = sum(int(r["word_count"] or 0) for r in rows
                         if r["collection"] == "idi_fill" and not r["duplicate_of"])
        a(f"`idi_fill` contributes {n_fill} volumes / {fill_words/1e6:.1f}M words, "
          "extracted by `fetch_idi_fill.py` into "
          "`/Users/tunder/workdata/chronologic-dating-corpus/idi_fill/`.\n")

    # ---- holes outside the plateau ---------------------------------------
    THIN = 30
    holes = []
    for dec in range(DECADE_MIN, DECADE_MAX, 10):
        if PLATEAU[0] - 10 < dec <= PLATEAU[1]:
            continue
        held = sum(table[dec][c][0] for c in table.get(dec, {}))
        if held < THIN:
            holes.append((dec, held, supply.get(dec, 0) if supply else None))
    if holes:
        a("## Holes outside the plateau\n")
        a(f"The spec tolerates lumpy tails outside {PLATEAU[0]}-{PLATEAU[1]}, but a decade "
          "with *no* anchor is worse than lumpy: the date model has nothing to interpolate "
          f"from. Decades below {THIN} volumes:\n")
        a("| Decade | volumes held | IDI supply |")
        a("|---|---|---|")
        for dec, held, sup in holes:
            a(f"| {dec}s | {held} | {sup:,} |" if sup is not None
              else f"| {dec}s | {held} | not computed |")
        a("")
        gap = [d for d, h, _ in holes if 1800 <= d <= 1820]
        if gap:
            a("**The 1801-1830 gap is the notable one.** ECCO stops at 1800 and the IDI "
              "sampling started at 1831, so there is a ~30-year void between the two. IDI "
              "supply there is ample, and closing it costs one flag: "
              "`fetch_idi_fill.py sample --ranges 1801-1830:10` (~300 volumes).\n")

    if supply:
        a("## IDI supply per decade (capacity, not corpus)\n")
        a("English (eng > 0.75) volumes catalogued in the IDI parquet, post-exclusion. "
          "These are candidates `fetch_idi_fill.py` can draw from.\n")
        a("| Decade | candidates |")
        a("|---|---|")
        for dec in sorted(supply):
            a(f"| {dec}s | {supply[dec]:,} |")
        a("")

    a("## Date quality\n")
    ds = Counter(r["date_source"] for r in permitted)
    a("| date_source | volumes |")
    a("|---|---|")
    for k, v in ds.most_common():
        a(f"| `{k}` | {v:,} |")
    a("")
    wm = Counter(r["word_count_method"] for r in permitted)
    a("Word counts: " + ", ".join(f"{k} {v:,}" for k, v in wm.most_common()) + ".")
    if ratios:
        a("Estimated collections used a calibrated bytes/word ratio: " +
          ", ".join(f"{k} {v:.2f}" for k, v in ratios.items()) + ".")
    a("")

    with open(path, "w") as fh:
        fh.write("\n".join(L))


def make_plot(table, out_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    decades = sorted(table)
    collections = sorted({c for d in table.values() for c in d})
    # tab10 recycles after 10 series and we have 11+, which made chicago_fiction and
    # oapen_1925_1990 the same blue; tab20 keeps every collection distinguishable.
    palette = {c: matplotlib.colormaps["tab20"](i % 20)
               for i, c in enumerate(collections)}
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9), sharex=True)
    x = np.arange(len(decades))

    for ax, idx, label in ((ax1, 0, "Volumes"), (ax2, 1, "Words (millions)")):
        bottom = np.zeros(len(decades))
        for c in collections:
            vals = np.array([table[d][c][idx] / (1e6 if idx else 1) for d in decades],
                            dtype=float)
            if not vals.any():
                continue
            ax.bar(x, vals, bottom=bottom, label=c, width=0.85, color=palette[c])
            bottom += vals
        ax.set_ylabel(label, fontsize=12)
        ax.axvspan(x[decades.index(1830)] - 0.5 if 1830 in decades else -1,
                   x[decades.index(1930)] + 0.5 if 1930 in decades else -1,
                   color="grey", alpha=0.10, zorder=0)

    ax1.set_title("Dating corpus: permitted volumes and words per decade "
                  "(shaded = the 1831-1930 plateau)", fontsize=13)
    ax1.legend(fontsize=8, ncol=3)
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{d}s" for d in decades], rotation=90, fontsize=8)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    print(f"Plot written to {out_path}")


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="stylejudge/corpus_manifest.csv")
    ap.add_argument("--report", default="stylejudge/decade_census_report.md")
    ap.add_argument("--plot", default="stylejudge/decade_census.png")
    ap.add_argument("--recount", action="store_true",
                    help="ignore cached word counts and recount")
    ap.add_argument("--skip-supply", action="store_true",
                    help="skip the streaming pass over the 983k-row IDI parquet")
    ap.add_argument("--no-plot", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(SEAGATE):
        sys.exit(f"ERROR: {SEAGATE} is not mounted. ECCO and the IDI parquet live there.")

    print("Building forbidden set (benchmark ground-truth sources)...")
    forbidden, reason_by_id, fstats = build_forbidden_set(REPO_ROOT)
    print(f"  {len(forbidden)} forbidden ids from "
          f"{fstats['question_files_scanned']} question files + metadata + 2 directories")

    print("\nLoading collections...")
    rows = []
    for loader in (load_idi_collections, load_idi_fill, load_coha,
                   load_web_era, load_chicago, load_ecco):
        got = loader(REPO_ROOT)
        rows.extend(got)
        if got:
            print(f"  {loader.__name__}: {len(got)} volumes")

    for r in rows:
        r.setdefault("word_count", None)
        r.setdefault("word_count_method", None)
        why = reason_by_id.get(r["volume_id"])
        r["excluded"] = 1 if why else 0
        r["exclusion_reason"] = why or ""
        r["duplicate_of"] = ""

    # ---- flag cross-collection duplicates ------------------------------
    def prio(row):
        c = row["collection"]
        return (COLLECTION_PRIORITY.index(c) if c in COLLECTION_PRIORITY else 99, c)

    first_seen = {}
    for r in sorted(rows, key=prio):
        vid = r["volume_id"]
        if vid in first_seen:
            r["duplicate_of"] = first_seen[vid]
        else:
            first_seen[vid] = r["collection"]
    n_dup = sum(1 for r in rows if r["duplicate_of"])
    if n_dup:
        pairs = Counter((r["collection"], r["duplicate_of"])
                        for r in rows if r["duplicate_of"])
        print("\nDuplicate volumes (same id in two collections; counted once):")
        for (dupc, keptc), n in pairs.most_common():
            print(f"  {n:5d}  {dupc} already in {keptc}")

    print("\nWord counts...")
    cache = {} if args.recount else load_cache(args.out)
    ratios = fill_word_counts(rows, cache, args.recount)

    # ---- assertions the plan calls for --------------------------------
    missing_path = [r for r in rows if not os.path.exists(r["path"])]
    undated = [r for r in rows if not r["date"]]
    if missing_path:
        print(f"\nWARNING: {len(missing_path)} rows point at a nonexistent path, e.g. "
              f"{missing_path[0]['path']}")
    if undated:
        print(f"WARNING: {len(undated)} rows have no date "
              f"({Counter(r['collection'] for r in undated).most_common(3)})")

    permitted_ids = {r["volume_id"] for r in rows if not r["excluded"]}
    n_unique = len({r["volume_id"] for r in rows
                    if not r["excluded"] and not r["duplicate_of"]})
    leaked = permitted_ids & forbidden
    assert not leaked, f"BENCHMARK LEAK: {len(leaked)} permitted volumes are forbidden ids"

    with open(args.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in sorted(rows, key=lambda x: (x["collection"], str(x["volume_id"]))):
            w.writerow(r)
    print(f"\nManifest written to {args.out} ({len(rows):,} rows)")

    supply = {}
    if not args.skip_supply:
        print("\nStreaming the IDI parquet for per-decade supply "
              "(983k rows, a few minutes)...")
        supply, seen = idi_supply_by_decade(forbidden)
        print(f"  {seen:,} rows scanned; {sum(supply.values()):,} English candidates "
              f"in {DECADE_MIN}-{DECADE_MAX}")

    table = decade_table(rows)
    write_report(args.report, rows, table, supply, fstats, ratios, args)
    print(f"Report written to {args.report}")
    if not args.no_plot:
        make_plot(table, args.plot)

    # ---- console summary ------------------------------------------------
    n_excl = sum(1 for r in rows if r["excluded"])
    n_dupe = sum(1 for r in rows if r["duplicate_of"])
    print(f"\n=== {n_unique:,} distinct permitted volumes "
          f"({n_excl} excluded, {n_dupe} duplicate rows) ===")
    print(f"Plateau ({PLATEAU[0]}-{PLATEAU[1]}), permitted volumes per decade "
          "(plateau years only; target prorated for partial decades):")
    for dec in range(PLATEAU[0] // 10 * 10, PLATEAU[1] + 1, 10):
        lo, hi = max(dec, PLATEAU[0]), min(dec + 9, PLATEAU[1])
        inrange = [r for r in rows if not r["excluded"] and not r["duplicate_of"]
                   and r["date"] and lo <= int(r["date"]) <= hi]
        words = sum(int(r["word_count"] or 0) for r in inrange)
        target = round(TARGET_PER_DECADE * (hi - lo + 1) / 10)
        mark = "  <-- NEEDS FILL" if len(inrange) < target else ""
        print(f"  {dec}s ({lo}-{hi})  {len(inrange):5d} vols  "
              f"{words/1e6:7.1f}M words  target {target}{mark}")


if __name__ == "__main__":
    main()

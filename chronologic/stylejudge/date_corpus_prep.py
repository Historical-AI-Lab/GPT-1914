#!/usr/bin/env python3
"""date_corpus_prep.py — Phase E3 metadata prep for the DeBERTa date predictor.

Two pure-metadata subcommands, no text I/O:

  roster        corpus_roster.csv -> corpus_roster_dated.csv, adding `date_catalog`
                and `date_type`, dropping IDI volumes whose MARC date type is a
                continuing resource (or otherwise unreliable), and folding
                situate's `fpub_final` corrected dates in *before* sampling.

  length-table  length_distribution.json -> length_distribution_sentences.json,
                a byte-for-byte copy with every `joint` entry's `fragment_share`
                forced to 0.0, so `sample_length()` only ever draws complete
                sentences.

See `stylejudge/phase-e3-plan.md` Step 1 for the full rationale.
"""

import argparse
import csv
import glob
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from build_corpus_manifest import normalize_barcode            # noqa: E402

REPO_ROOT = SCRIPT_DIR.parent
WORKDATA = Path.home() / "workdata/chronologic-dating-corpus"

DEFAULT_ROSTER = SCRIPT_DIR / "corpus_roster.csv"
DEFAULT_ROSTER_OUT = SCRIPT_DIR / "corpus_roster_dated.csv"
DEFAULT_SAMPLE1000 = REPO_ROOT / "booksample" / "sample1000_metadata.csv"
DEFAULT_IDI_FILL_GLOB = str(WORKDATA / "idi_fill_metadata_*.csv")
DEFAULT_CALIBRATED_DATES = (Path.home() / "Library/CloudStorage/Dropbox/python"
                            / "situate/wikimeta/full_record_list_calibrated.csv")

DEFAULT_LENGTH_TABLE = SCRIPT_DIR / "length_distribution.json"
DEFAULT_LENGTH_TABLE_OUT = SCRIPT_DIR / "length_distribution_sentences.json"

# MARC date types kept for training. Everything else with a *known* IDI date type
# (the three "Continuing resource ..." variants, "Questionable date",
# "Dates unknown", "No attempt to code", the blank "unknown code:  ") is dropped —
# serials carry unreliable catalog dates and the residue is too small to model.
DEFAULT_KEEP_DATE_TYPES = (
    "Single known date/probable date",
    "Multiple dates",
    "Reprint/reissue date (Date 1) and original date (Date 2)",
    "Publication date and copyright date",
)

IDI_TIER = "idi"

ROSTER_COLUMNS = ["volume_id", "collection", "tier", "path", "title", "author",
                  "date", "decade", "selection_rank", "word_count"]
OUT_COLUMNS = ROSTER_COLUMNS + ["date_catalog", "date_type"]


# ---------------------------------------------------------------------------
# date-type metadata
# ---------------------------------------------------------------------------

def load_date_types(sample1000_path, idi_fill_glob):
    """{normalized_barcode: marc_date_type} from the two IDI metadata sources.

    `sample1000_metadata.csv` (column `date_format`) and the
    `idi_fill_metadata_*.csv` family (column `date_types_src`) use the same
    controlled vocabulary and, in practice, disjoint barcode sets. First value
    wins; genuine conflicts are collected and returned for the caller to report.
    """
    date_types = {}
    conflicts = []

    def add(barcode, value, source):
        if not value:
            return
        key = normalize_barcode(barcode)
        if key in date_types and date_types[key] != value:
            conflicts.append((key, date_types[key], value, source))
            return
        date_types.setdefault(key, value)

    with open(sample1000_path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            add(row["barcode_src"], (row.get("date_format") or "").strip(),
                "sample1000")

    fill_paths = sorted(glob.glob(idi_fill_glob))
    for path in fill_paths:
        with open(path, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                add(row["barcode_src"], (row.get("date_types_src") or "").strip(),
                    Path(path).name)

    return date_types, conflicts, fill_paths


# ---------------------------------------------------------------------------
# fpub_final corrected dates
# ---------------------------------------------------------------------------

def load_corrected_dates(path):
    """{normalized_barcode: fpub_final_year} from situate's calibrated record list.

    `fpub_final` is a metadata-triangulation estimate (Wikidata / OpenLibrary /
    IDI cross-referencing), never a text-model prediction — the `txt_*` columns
    in the same file are that project's own predictions and must not be used.
    """
    corrected = {}
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            value = (row.get("fpub_final") or "").strip()
            if not value:
                continue
            try:
                corrected[normalize_barcode(row["barcode"])] = float(value)
            except ValueError:
                continue
    return corrected


# ---------------------------------------------------------------------------
# roster
# ---------------------------------------------------------------------------

def _decade_of(year):
    return (int(float(year)) // 10) * 10


def build_dated_roster(roster_rows, date_types, corrected, keep_types,
                       apply_correction=True):
    """Return (kept_rows, stats).

    kept_rows are dicts over OUT_COLUMNS. `date_catalog` always holds the
    pre-correction catalog year; `date`/`decade` hold the corrected values where
    a `fpub_final` match exists, the catalog values otherwise. `date_type` is the
    MARC string for IDI volumes, "" for every other tier.
    """
    keep_types = set(keep_types)
    kept = []
    dropped_by_type = Counter()
    idi_without_type = []
    n_corrected = 0
    n_moved = 0
    n_moved_gt20 = 0
    n_cross_decade = 0
    before_by_decade = Counter()
    after_by_decade = Counter()

    for row in roster_rows:
        is_idi = row["tier"] == IDI_TIER
        key = normalize_barcode(row["volume_id"])
        date_type = date_types.get(key, "") if is_idi else ""

        try:
            before_by_decade[_decade_of(row["date"])] += 1
        except (ValueError, TypeError):
            before_by_decade["(unparsed)"] += 1

        if is_idi:
            if not date_type:
                idi_without_type.append(row["volume_id"])
                continue
            if date_type not in keep_types:
                dropped_by_type[date_type] += 1
                continue

        catalog_date = row["date"]
        out_date = catalog_date
        out_decade = row["decade"]
        if apply_correction and key in corrected:
            new_date = corrected[key]
            n_corrected += 1
            try:
                old = float(catalog_date)
                if abs(new_date - old) >= 0.5:
                    n_moved += 1
                if abs(new_date - old) > 20:
                    n_moved_gt20 += 1
                if _decade_of(old) != _decade_of(new_date):
                    n_cross_decade += 1
            except (ValueError, TypeError):
                pass
            out_date = f"{new_date:g}"
            out_decade = str(_decade_of(new_date))

        out = {c: row.get(c, "") for c in ROSTER_COLUMNS}
        out["date"] = out_date
        out["decade"] = out_decade
        out["date_catalog"] = catalog_date
        out["date_type"] = date_type
        kept.append(out)
        try:
            after_by_decade[_decade_of(out_date)] += 1
        except (ValueError, TypeError):
            after_by_decade["(unparsed)"] += 1

    stats = dict(
        n_input=len(roster_rows),
        n_kept=len(kept),
        dropped_by_type=dict(dropped_by_type.most_common()),
        n_dropped=sum(dropped_by_type.values()),
        idi_without_type=idi_without_type,
        n_corrected=n_corrected,
        n_moved=n_moved,
        n_moved_gt20=n_moved_gt20,
        n_cross_decade=n_cross_decade,
        before_by_decade=before_by_decade,
        after_by_decade=after_by_decade,
    )
    return kept, stats


def _decade_table_md(before, after):
    keys = sorted(k for k in set(before) | set(after) if isinstance(k, int))
    lines = ["| decade | before | after | delta |", "|---|---|---|---|"]
    for k in keys:
        b, a = before.get(k, 0), after.get(k, 0)
        lines.append(f"| {k}s | {b} | {a} | {a - b:+d} |")
    for k in (x for x in set(before) | set(after) if not isinstance(x, int)):
        lines.append(f"| {k} | {before.get(k, 0)} | {after.get(k, 0)} | "
                     f"{after.get(k, 0) - before.get(k, 0):+d} |")
    lines.append(f"| **total** | **{sum(v for v in before.values())}** | "
                 f"**{sum(v for v in after.values())}** | "
                 f"**{sum(after.values()) - sum(before.values()):+d}** |")
    return "\n".join(lines)


def cmd_roster(args):
    with open(args.roster, encoding="utf-8", newline="") as f:
        roster_rows = list(csv.DictReader(f))

    date_types, conflicts, fill_paths = load_date_types(
        args.sample1000_metadata, args.idi_fill_metadata)
    print(f"date-type sources: {Path(args.sample1000_metadata).name} + "
          f"{len(fill_paths)} idi_fill file(s); {len(date_types)} barcodes",
          file=sys.stderr)
    if conflicts:
        print(f"WARNING: {len(conflicts)} barcode(s) with conflicting date types "
              f"(first-wins): {conflicts[:5]}", file=sys.stderr)

    corrected = ({} if args.no_date_correction
                 else load_corrected_dates(args.calibrated_dates))
    if not args.no_date_correction:
        print(f"corrected-date source: {len(corrected)} barcodes with fpub_final",
              file=sys.stderr)

    keep_types = [s.strip() for s in args.keep_date_types.split(",") if s.strip()]
    kept, stats = build_dated_roster(roster_rows, date_types, corrected, keep_types,
                                     apply_correction=not args.no_date_correction)

    if stats["idi_without_type"]:
        n = len(stats["idi_without_type"])
        print(f"ERROR: {n} IDI volume(s) with no MARC date-type match — the plan "
              f"assumes 100% coverage. Sample: {stats['idi_without_type'][:10]}",
              file=sys.stderr)
        return 1

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=OUT_COLUMNS)
        w.writeheader()
        w.writerows(kept)

    table = _decade_table_md(stats["before_by_decade"], stats["after_by_decade"])
    print(f"\nwrote {out_path}", file=sys.stderr)
    print(f"kept {stats['n_kept']} of {stats['n_input']} volumes "
          f"({stats['n_dropped']} dropped by date type)", file=sys.stderr)
    for dt, n in stats["dropped_by_type"].items():
        print(f"  dropped {n:5d}  {dt}", file=sys.stderr)
    print(f"fpub_final: {stats['n_corrected']} joined, {stats['n_moved']} moved, "
          f"{stats['n_moved_gt20']} by >20 yr, {stats['n_cross_decade']} across a "
          f"decade boundary", file=sys.stderr)
    print("\nper-decade volume count, before vs. after:", file=sys.stderr)
    print(table, file=sys.stderr)

    if args.report:
        md = ["# Phase E3 dated-roster preparation", "",
              f"Input: `{args.roster}` ({stats['n_input']} volumes)  ",
              f"Output: `{out_path}` ({stats['n_kept']} volumes)  ",
              f"Date correction: {'disabled' if args.no_date_correction else 'fpub_final'}",
              "",
              "## Dropped by MARC date type", "",
              "| date type | dropped |", "|---|---|"]
        for dt, n in stats["dropped_by_type"].items():
            md.append(f"| {dt} | {n} |")
        md += ["", "## fpub_final corrected dates", "",
               f"- joined: {stats['n_corrected']}",
               f"- moved (>= 0.5 yr): {stats['n_moved']}",
               f"- moved > 20 yr: {stats['n_moved_gt20']}",
               f"- across a decade boundary: {stats['n_cross_decade']}",
               "", "## Per-decade volume count", "", table, ""]
        Path(args.report).write_text("\n".join(md) + "\n", encoding="utf-8")
        print(f"wrote {args.report}", file=sys.stderr)
    return 0


# ---------------------------------------------------------------------------
# length-table
# ---------------------------------------------------------------------------

def cmd_length_table(args):
    with open(args.in_path, encoding="utf-8") as f:
        table = json.load(f)

    joint = table.get("joint", [])
    n_nonzero = sum(1 for e in joint if e.get("fragment_share", 0.0) != args.fragment_share)
    for entry in joint:
        entry["fragment_share"] = args.fragment_share

    weight_sum = sum(e.get("weight", 0.0) for e in joint)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(table, f, indent=2)
    print(f"wrote {out_path}: {len(joint)} joint entries, fragment_share forced to "
          f"{args.fragment_share} ({n_nonzero} changed); weights untouched, "
          f"sum = {weight_sum:.6f}", file=sys.stderr)
    return 0


# ---------------------------------------------------------------------------
# argparse
# ---------------------------------------------------------------------------

def build_parser():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)

    rp = sub.add_parser("roster", help="corpus_roster.csv -> corpus_roster_dated.csv")
    rp.add_argument("--roster", default=str(DEFAULT_ROSTER))
    rp.add_argument("--sample1000-metadata", default=str(DEFAULT_SAMPLE1000),
                    dest="sample1000_metadata")
    rp.add_argument("--idi-fill-metadata", default=DEFAULT_IDI_FILL_GLOB,
                    dest="idi_fill_metadata", help="glob for idi_fill_metadata_*.csv")
    rp.add_argument("--calibrated-dates", default=str(DEFAULT_CALIBRATED_DATES),
                    dest="calibrated_dates")
    rp.add_argument("--no-date-correction", action="store_true",
                    help="skip the fpub_final join (diagnostic)")
    rp.add_argument("--keep-date-types", default=",".join(DEFAULT_KEEP_DATE_TYPES),
                    dest="keep_date_types",
                    help="comma-separated MARC date types to retain")
    rp.add_argument("--report", default=None, help="also write a markdown report here")
    rp.add_argument("--out", default=str(DEFAULT_ROSTER_OUT))
    rp.set_defaults(func=cmd_roster)

    lp = sub.add_parser("length-table",
                        help="length_distribution.json -> *_sentences.json (fragment_share=0)")
    lp.add_argument("--in", dest="in_path", default=str(DEFAULT_LENGTH_TABLE))
    lp.add_argument("--out", default=str(DEFAULT_LENGTH_TABLE_OUT))
    lp.add_argument("--fragment-share", type=float, default=0.0, dest="fragment_share")
    lp.set_defaults(func=cmd_length_table)

    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())

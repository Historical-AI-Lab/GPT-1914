#!/usr/bin/env python3
"""reuse_bertclassify.py — Phase D2 §3: recycle `bertclassify/imitation/` as negatives.

167 imitation files sit line-aligned with `bertclassify/authentic/` over 119
permitted volumes. Reusing them is free, but the material is concentrated —
one generator vintage, mostly 1875–1924, and chunks built to a flat ~100-word
target rather than the Phase A distribution. Uncapped it would put a third of the
negative pool in one decade band. So §3 sets a policy this module implements:

- **Cap at 6,400 rows** (half the infill quota, 20% of all negatives).
- **Drop every Google file.** Google is an eval-only family (§4.4); reused Google
  output would contaminate the family holdout. On disk that is 17 files, not the
  12 the plan estimated — 12 `-infill` plus 5 `-infill2`.
- **Re-cut to the Phase A length distribution** and re-normalize, since these rows
  predate Phase C and carry pre-normalization typography.
- Spread the cap evenly over generators and decades rather than taking the first
  6,400 lines, which would over-weight whichever model happens to sort first.

Filename grammar, verified against `bertclassify/bert_data_prep.py:818-883`:

    imitation/{barcode}_{model}.txt          <-> authentic/{barcode}.txt
    imitation/{barcode}-{model}-infill.txt   <-> authentic/{barcode}-infill.txt
    imitation/{barcode}-{model}-infill2.txt  <-> authentic/{barcode}-infill2.txt

Note the separator differs by mode — `_` for continuation, `-` for infill — which
the plan's single-pattern sketch did not capture.

**The authentic continuation file holds the prompt chunk, not the real
continuation.** So for continuation rows the 8-gram guard can only detect the
model echoing its own prompt; the true continuation was never saved and genuine
memorization is undetectable there. Infill rows are unaffected: their authentic
file *is* the withheld gap text, so the guard works as designed. Continuation
rows are tagged `leakage_checkable: false` so a later audit can tell the two
apart instead of assuming both were checked.

CLI
    python reuse_bertclassify.py [--dry-run] [--report-only] [--cap N] ...
"""

import argparse
import fnmatch
import json
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from negative_qc import fit_length, qc_negative, sample_fitted_length  # noqa: E402
from normalize import load_lexicon                                    # noqa: E402
from sample_passages import load_length_table, write_jsonl            # noqa: E402

DEFAULT_IMITATION_DIR = REPO_ROOT / "bertclassify" / "imitation"
DEFAULT_AUTHENTIC_DIR = REPO_ROOT / "bertclassify" / "authentic"
DEFAULT_METADATA = REPO_ROOT / "booksample" / "sample1000_metadata.csv"
DEFAULT_LENGTH_TABLE = SCRIPT_DIR / "length_distribution.json"
DEFAULT_OUT = Path.home() / "workdata" / "chronologic-dating-corpus" / "passages" / "negatives.jsonl"

DEFAULT_CAP = 6400
DEFAULT_SEED = 20260809
DEFAULT_EXCLUDE = ["*gemma*"]

#: The negative pool is 1831-1930, matching the positives.
DATE_LO, DATE_HI = 1831, 1930

CONTINUATION = "continuation"
INFILL = "infill"


# ---------------------------------------------------------------------------
# Provenance reconstruction
# ---------------------------------------------------------------------------

def parse_imitation_filename(name):
    """Split an imitation filename into (barcode, model_safe, mode, gap_sentences).

    Returns None if the name does not match the grammar.
    """
    if not name.endswith(".txt"):
        return None
    stem = name[:-4]
    for suffix, gap in (("-infill2", 2), ("-infill", 1)):
        if stem.endswith(suffix):
            rest = stem[:-len(suffix)]
            barcode, sep, model = rest.partition("-")
            if not sep:
                return None
            return barcode, model, INFILL, gap
    barcode, sep, model = stem.partition("_")
    if not sep:
        return None
    return barcode, model, CONTINUATION, None


def authentic_filename(barcode, mode, gap_sentences):
    if mode == CONTINUATION:
        return f"{barcode}.txt"
    return f"{barcode}-infill{'2' if gap_sentences == 2 else ''}.txt"


def load_metadata(path=DEFAULT_METADATA):
    """barcode -> {date, title, author}. Keyed on `barcode_src`, uppercased."""
    import pandas as pd

    df = pd.read_csv(path)
    out = {}
    for _, row in df.iterrows():
        key = str(row["barcode_src"]).replace("hvd.", "").upper()
        date = row.get("firstpub")
        if date is None or (isinstance(date, float) and date != date):
            date = row.get("date1_src")
        try:
            date = int(date)
        except (TypeError, ValueError):
            date = None
        out[key] = {"date": date,
                    "title": str(row.get("title_src") or ""),
                    "author": str(row.get("author_src") or "")}
    return out


def read_lines(path):
    with open(path, encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f]


def is_excluded(model_safe, patterns):
    lowered = model_safe.lower()
    return any(fnmatch.fnmatch(lowered, p.lower()) for p in patterns)


def enumerate_pairs(imitation_dir, authentic_dir, exclude_patterns):
    """Yield one dict per usable imitation file, with its authentic counterpart.

    Skipping is reported rather than silent: `--report-only` should be able to
    account for all 167 files.
    """
    imitation_dir, authentic_dir = Path(imitation_dir), Path(authentic_dir)
    files, skipped = [], Counter()
    for path in sorted(imitation_dir.glob("*.txt")):
        parsed = parse_imitation_filename(path.name)
        if parsed is None:
            skipped["unparseable_filename"] += 1
            continue
        barcode, model_safe, mode, gap = parsed
        if is_excluded(model_safe, exclude_patterns):
            skipped["excluded_model"] += 1
            continue
        auth = authentic_dir / authentic_filename(barcode, mode, gap)
        if not auth.exists():
            skipped["missing_authentic_pair"] += 1
            continue
        imit_lines, auth_lines = read_lines(path), read_lines(auth)
        if len(imit_lines) != len(auth_lines):
            # Line alignment is the whole basis of the pairing; a mismatch means
            # the two files came from different runs and cannot be trusted.
            skipped["line_count_mismatch"] += 1
            continue
        files.append({"path": path, "authentic_path": auth, "barcode": barcode,
                      "model_safe": model_safe, "mode": mode, "gap_sentences": gap,
                      "imitation_lines": imit_lines, "authentic_lines": auth_lines})
    return files, skipped


# ---------------------------------------------------------------------------
# Row building
# ---------------------------------------------------------------------------

def build_candidates(files, metadata, length_table, lexicon, rng,
                     date_lo=DATE_LO, date_hi=DATE_HI, stats=None):
    """Run QC over every line pair and return the surviving candidate rows."""
    stats = stats if stats is not None else Counter()
    out = []
    for entry in files:
        meta = metadata.get(entry["barcode"].upper())
        if meta is None or meta["date"] is None:
            stats["no_metadata"] += len(entry["imitation_lines"])
            continue
        date = meta["date"]
        if not (date_lo <= date <= date_hi):
            stats["out_of_date_range"] += len(entry["imitation_lines"])
            continue
        decade = (date // 10) * 10
        mode = entry["mode"]

        for idx, (raw, reference) in enumerate(zip(entry["imitation_lines"],
                                                   entry["authentic_lines"])):
            if not raw.strip():
                stats["blank_line"] += 1
                continue

            if mode == INFILL:
                # The authentic line is the withheld gap: a real leakage check.
                references, bookend_before, checkable = [reference], "", True
            else:
                # The authentic line is the prompt chunk. Treat it as a bookend
                # (echo detection), never as a leakage reference — echoing the
                # prompt is a formatting failure, not memorization.
                references, bookend_before, checkable = [], reference, False

            # Two passes: QC the text at its natural length, then pick a Phase A
            # target it can actually reach and trim to that. Drawing the target
            # blind would reject 40% of the material for being shorter than a
            # cell it never had a chance of filling.
            verdict = qc_negative(
                raw, lexicon=lexicon, references=references,
                bookend_before=bookend_before,
                target_sentences=None, target_words=None)
            if not verdict["ok"]:
                stats[verdict["reason"]] += 1
                continue

            target = sample_fitted_length(length_table, rng,
                                          verdict["n_sentences"], verdict["n_words"])
            if target is None:
                stats["no_reachable_length_cell"] += 1
                continue
            target_sentences, target_words = target

            fitted, reason = fit_length(verdict["text"], target_sentences, target_words)
            if reason:
                stats[reason] += 1
                continue
            verdict = qc_negative(
                fitted, lexicon=lexicon, references=references,
                bookend_before=bookend_before,
                target_sentences=None, target_words=None)
            if not verdict["ok"]:
                stats[f"post_trim_{verdict['reason']}"] += 1
                continue

            out.append({
                "negative_id": f"reuse_{entry['barcode']}_{mode}"
                               f"{entry['gap_sentences'] or ''}_{entry['model_safe']}_{idx}",
                "elicitation_strategy": mode,
                "prompt_variant": "explicit_length",
                "date_in_prompt": False,
                "model_id": entry["model_safe"],
                "endpoint": "chat",
                "temperature": None,
                "reasoning_effort": None,
                "source_passage_id": f"{entry['barcode']}_{mode}_{idx}",
                "source_volume_id": entry["barcode"],
                "source_collection": "bertclassify",
                "source_date": date,
                "source_decade": decade,
                "source_title": meta["title"],
                "raw_response": raw,
                "text": verdict["text"],
                "n_sentences": verdict["n_sentences"],
                "n_words": verdict["n_words"],
                "gap_sentences": entry["gap_sentences"],
                "leakage_checkable": checkable,
                "provenance": "bertclassify_reuse",
                "split_role": "train",
                "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            })
            stats["accepted"] += 1
    return out, stats


def spread_cap(candidates, cap, rng):
    """Take `cap` rows, round-robin over (model, decade, modality) buckets.

    Taking the first N would over-weight whichever generator sorts first and
    whichever decade happens to be densest. Round-robin over buckets keeps the
    reused slice as close to balanced as its supply allows.
    """
    if cap is None or len(candidates) <= cap:
        return list(candidates)
    buckets = defaultdict(list)
    for row in candidates:
        buckets[(row["model_id"], row["source_decade"],
                 row["elicitation_strategy"])].append(row)
    for rows in buckets.values():
        rng.shuffle(rows)
    keys = sorted(buckets)
    rng.shuffle(keys)

    taken, exhausted = [], set()
    while len(taken) < cap and len(exhausted) < len(keys):
        for key in keys:
            if key in exhausted:
                continue
            if not buckets[key]:
                exhausted.add(key)
                continue
            taken.append(buckets[key].pop())
            if len(taken) >= cap:
                break
    return taken


def summarize(rows):
    return {
        "n_rows": len(rows),
        "by_model": dict(Counter(r["model_id"] for r in rows).most_common()),
        "by_decade": dict(sorted(Counter(r["source_decade"] for r in rows).items())),
        "by_modality": dict(Counter(r["elicitation_strategy"] for r in rows)),
        "by_gap_sentences": dict(sorted(
            Counter(r["gap_sentences"] for r in rows if r["gap_sentences"]).items())),
        "n_volumes": len({r["source_volume_id"] for r in rows}),
        "leakage_checkable_rows": sum(1 for r in rows if r["leakage_checkable"]),
        "median_words": (sorted(r["n_words"] for r in rows)[len(rows) // 2]
                         if rows else 0),
    }


def append_jsonl(rows, path):
    """Append, never truncate — `negatives.jsonl` is shared with elicitation."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--imitation-dir", default=str(DEFAULT_IMITATION_DIR))
    ap.add_argument("--authentic-dir", default=str(DEFAULT_AUTHENTIC_DIR))
    ap.add_argument("--metadata", default=str(DEFAULT_METADATA))
    ap.add_argument("--cap", type=int, default=DEFAULT_CAP,
                    help="max rows emitted (0 or negative means no cap)")
    ap.add_argument("--exclude-model", action="append", default=None,
                    metavar="GLOB",
                    help=f"repeatable; default {DEFAULT_EXCLUDE} (the Google holdout)")
    ap.add_argument("--length-table", default=str(DEFAULT_LENGTH_TABLE))
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--dry-run", action="store_true",
                    help="parse, QC and report, but write nothing")
    ap.add_argument("--report-only", action="store_true",
                    help="print per-model/decade/modality counts and exit")
    args = ap.parse_args(argv)

    exclude = args.exclude_model if args.exclude_model is not None else DEFAULT_EXCLUDE
    rng = random.Random(args.seed)
    lexicon = load_lexicon()
    length_table = load_length_table(args.length_table)
    metadata = load_metadata(args.metadata)

    files, skipped = enumerate_pairs(args.imitation_dir, args.authentic_dir, exclude)
    candidates, stats = build_candidates(files, metadata, length_table, lexicon, rng)
    cap = args.cap if args.cap and args.cap > 0 else None
    rows = spread_cap(candidates, cap, rng)

    report = {
        "files_used": len(files),
        "files_skipped": dict(skipped),
        "models_present": sorted({f["model_safe"] for f in files}),
        "line_pairs_considered": sum(len(f["imitation_lines"]) for f in files),
        "qc": dict(stats.most_common()),
        "candidates_after_qc": len(candidates),
        "cap": cap,
        "emitted": summarize(rows),
    }
    print(json.dumps(report, indent=2), file=sys.stderr)

    if args.report_only or args.dry_run:
        print(f"dry run: would write {len(rows)} rows to {args.out}", file=sys.stderr)
        return 0

    append_jsonl(rows, args.out)
    print(f"appended {len(rows)} rows to {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""build_ground_truth_pairs.py

Sample pairs of passages from the IDI_sample_1875-25 period source texts that
match the length distribution of anachronic_pairs_scored.jsonl, then score them
via DeBERTa to produce Δ_gt.

Both passages in a pair are drawn from the same .txt file.
Length is measured in characters; matching targets mean_len and len_diff.
~50% of candidate fragments are phrase-level (no end punctuation); the rest
are sentence-level.

Outputs:
  calibration/ground_truth_pairs.jsonl         (unscored)
  calibration/ground_truth_pairs_scored.jsonl  (after DeBERTa)

Usage:
    python modelasjudge/build_ground_truth_pairs.py \\
        [--idi-dir PATH] [--scored-anachronic PATH] \\
        [--out-dir PATH] [--n INT] [--exclude FILE[,FILE,...]] \\
        [--model-dir PATH] [--batch-size 64] [--max-length 256] [--device auto] [--seed INT]
"""

import argparse
import json
import random
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

try:
    import nltk
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    import nltk
    nltk.download("punkt_tab", quiet=True)

from nltk.tokenize import sent_tokenize

SCRIPT_DIR = Path(__file__).parent
IDI_DIR = SCRIPT_DIR.parent / "booksample" / "IDI_sample_1875-25"
DEFAULT_SCORED_ANACH = SCRIPT_DIR / "calibration" / "anachronic_pairs_scored.jsonl"
DEFAULT_SCORED_ANACH_NOMANUAL = SCRIPT_DIR / "calibration" / "anachronic_pairs_scored_nomanual.jsonl"
DEFAULT_OUT_DIR = SCRIPT_DIR / "calibration"
BERTCLASSIFY_DIR = SCRIPT_DIR.parent / "bertclassify"

DEFAULT_EXCLUDE = {"notes.txt", "washingtonpost.txt"}


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Build + score ground-truth period pairs matched to anachronic distribution")
    p.add_argument("--idi-dir", default=str(IDI_DIR), dest="idi_dir")
    p.add_argument("--scored-anachronic", default=None, dest="scored_anachronic",
                   help="Scored anachronic pairs JSONL (default depends on --nomanual)")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), dest="out_dir")
    p.add_argument("--nomanual", action="store_true",
                   help="Use nomanual variant: read *_nomanual scored anachronic pairs, write *_nomanual gt pair files.")
    p.add_argument("--n", type=int, default=None, help="Total pairs to produce (default: same as anachronic)")
    p.add_argument("--exclude", default="", help="Comma-separated filenames to skip")
    p.add_argument("--model-dir", default=str(BERTCLASSIFY_DIR / "baseline"), dest="model_dir")
    p.add_argument("--batch-size", type=int, default=64, dest="batch_size")
    p.add_argument("--max-length", type=int, default=256, dest="max_length")
    p.add_argument("--device", default="auto")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args(argv)
    if args.scored_anachronic is None:
        args.scored_anachronic = str(DEFAULT_SCORED_ANACH_NOMANUAL if args.nomanual else DEFAULT_SCORED_ANACH)
    return args


def split_to_fragments(text: str) -> list[str]:
    """Return sentence and phrase-level fragments from raw text."""
    sentences = sent_tokenize(text)
    fragments = []
    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 10:
            continue
        fragments.append(sent)
        # split ~half the sentences into phrase fragments on internal punctuation
        parts = re.split(r"(?<=[^,;:\s]),\s|;\s|:\s", sent)
        if len(parts) > 1:
            for part in parts:
                part = part.strip().rstrip(",;:")
                if len(part) >= 10:
                    fragments.append(part)
    return fragments


def ends_with_sentence_punct(text: str) -> bool:
    return text.rstrip().endswith((".", "?", "!"))


def assign_buckets(anachronic_records: list[dict]) -> tuple[list, list, list]:
    """Return (mean_len_edges, len_diff_edges, punct_sigs) for bucket assignment."""
    mean_lens = [r["mean_len"] for r in anachronic_records]
    len_diffs = [r["len_diff"] for r in anachronic_records]

    mean_lens_sorted = sorted(set(mean_lens))
    len_diffs_sorted = sorted(set(len_diffs))

    # 5-quantile edges for each dimension
    mean_edges = [np.percentile(mean_lens, q) for q in [0, 20, 40, 60, 80, 100]]
    diff_edges = [np.percentile(len_diffs, q) for q in [0, 20, 40, 60, 80, 100]]

    return mean_edges, diff_edges


def bucket_id(mean_len, len_diff, ep_a, ep_b, mean_edges, diff_edges):
    mi = min(4, sum(mean_len > e for e in mean_edges[:-1]) - 1)
    di = min(4, sum(len_diff > e for e in diff_edges[:-1]) - 1)
    mi = max(0, mi)
    di = max(0, di)
    return (mi, di, bool(ep_a), bool(ep_b))


def load_idi_fragments(idi_dir: Path, exclude: set[str]) -> dict[str, list[str]]:
    """Load all .txt files and return {filename: [fragment, …]}."""
    per_file = {}
    txt_files = sorted(idi_dir.glob("*.txt"))
    for fp in txt_files:
        if fp.name in exclude:
            continue
        text = fp.read_text(encoding="utf-8", errors="replace")
        frags = split_to_fragments(text)
        if frags:
            per_file[fp.name] = frags
    return per_file


def main(argv=None):
    args = parse_args(argv)
    rng = random.Random(args.seed)

    idi_dir = Path(args.idi_dir)
    scored_anach_path = Path(args.scored_anachronic)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not idi_dir.exists():
        print(f"ERROR: IDI dir not found: {idi_dir}", file=sys.stderr)
        sys.exit(1)
    if not scored_anach_path.exists():
        print(f"ERROR: {scored_anach_path} not found.  Run build_anachronic_pairs.py first.", file=sys.stderr)
        sys.exit(1)

    exclude = DEFAULT_EXCLUDE | set(args.exclude.split(",")) if args.exclude else DEFAULT_EXCLUDE

    # Load anachronic scored pairs for distribution
    anach_records = []
    with open(scored_anach_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                anach_records.append(json.loads(line))

    n_target = args.n if args.n else len(anach_records)
    print(f"Targeting {n_target:,} ground-truth pairs (same as anachronic count)")

    mean_edges, diff_edges = assign_buckets(anach_records)

    # Build target bucket counts
    target_bucket_counts: dict[tuple, int] = defaultdict(int)
    for r in anach_records:
        bid = bucket_id(
            r["mean_len"], r["len_diff"],
            r["ends_with_period_a"], r["ends_with_period_b"],
            mean_edges, diff_edges,
        )
        target_bucket_counts[bid] += 1

    print(f"Loading IDI fragments from {idi_dir} …")
    per_file = load_idi_fragments(idi_dir, exclude)
    n_files = len(per_file)
    print(f"  {n_files} files loaded")

    # Pairs per file: floor + remainder to first files
    base = n_target // n_files
    remainder = n_target % n_files
    file_quotas = {}
    for i, fname in enumerate(sorted(per_file)):
        file_quotas[fname] = base + (1 if i < remainder else 0)

    # Greedy bucket-fill
    remaining_buckets = dict(target_bucket_counts)
    all_pairs = []

    for fname, frags in sorted(per_file.items()):
        quota = file_quotas[fname]
        if quota == 0 or len(frags) < 2:
            continue

        # Shuffle fragments for randomness
        frags_shuffled = frags[:]
        rng.shuffle(frags_shuffled)

        added = 0
        tried_pairs = set()
        # Attempt to fill quota by trying fragment combinations
        max_attempts = quota * 20
        attempt = 0
        while added < quota and attempt < max_attempts:
            attempt += 1
            fa = rng.choice(frags_shuffled)
            fb = rng.choice(frags_shuffled)
            if fa == fb:
                continue
            key = (fa, fb)
            if key in tried_pairs:
                continue
            tried_pairs.add(key)

            mean_len = (len(fa) + len(fb)) / 2
            len_diff = abs(len(fa) - len(fb))
            ep_a = ends_with_sentence_punct(fa)
            ep_b = ends_with_sentence_punct(fb)
            bid = bucket_id(mean_len, len_diff, ep_a, ep_b, mean_edges, diff_edges)

            if remaining_buckets.get(bid, 0) > 0:
                remaining_buckets[bid] -= 1
            # Accept even if bucket is "overfull" once we've tried hard enough
            pair_idx = len(all_pairs)
            all_pairs.append({
                "pair_id": f"gt:{fname}:{pair_idx}",
                "source_file": fname,
                "text_a": fa,
                "text_b": fb,
                "mean_len": mean_len,
                "len_diff": len_diff,
                "ends_with_period_a": ep_a,
                "ends_with_period_b": ep_b,
            })
            added += 1

    print(f"Assembled {len(all_pairs):,} ground-truth pairs across {n_files} files")

    suffix = "_nomanual" if args.nomanual else ""
    pairs_path = out_dir / f"ground_truth_pairs{suffix}.jsonl"
    with open(pairs_path, "w", encoding="utf-8") as f:
        for pair in all_pairs:
            f.write(json.dumps(pair) + "\n")
    print(f"Unscored pairs → {pairs_path}")

    # Score via DeBERTa
    scored_path = out_dir / f"ground_truth_pairs_scored{suffix}.jsonl"
    print("Scoring via DeBERTa …")
    cmd = [
        sys.executable,
        str(SCRIPT_DIR / "run_deberta_pairs.py"),
        str(pairs_path),
        str(scored_path),
        "--model-dir", args.model_dir,
        "--batch-size", str(args.batch_size),
        "--max-length", str(args.max_length),
        "--device", args.device,
    ]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("ERROR: run_deberta_pairs.py failed", file=sys.stderr)
        sys.exit(1)

    # Report + compare distributions
    gt_deltas = []
    with open(scored_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                gt_deltas.append(json.loads(line)["delta"])

    anach_deltas = [r["delta"] for r in anach_records]
    ag = np.array(anach_deltas)
    gg = np.array(gt_deltas)

    print(f"\nΔ distribution comparison:")
    print(f"{'':20s}  {'Δ_anachronic':>14s}  {'Δ_gt':>14s}")
    print(f"{'mean':20s}  {ag.mean():>14.4f}  {gg.mean():>14.4f}")
    print(f"{'std':20s}  {ag.std():>14.4f}  {gg.std():>14.4f}")
    print(f"{'min':20s}  {ag.min():>14.4f}  {gg.min():>14.4f}")
    print(f"{'max':20s}  {ag.max():>14.4f}  {gg.max():>14.4f}")
    print(f"\nGround-truth pairs scored → {scored_path}")


if __name__ == "__main__":
    main()

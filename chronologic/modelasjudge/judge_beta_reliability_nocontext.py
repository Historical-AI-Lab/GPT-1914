"""
judge_beta_reliability_nocontext.py — Measure type-II (tie-blindness) error for
ChronoLogic judges (question fit only).

For each pair of equally-valid ground truths, asks the LLM judge to compare them
in both orderings (GT1-vs-GT2 and GT2-vs-GT1).  Any declared winner is a failure;
only "C" (tie) counts as a correct judgment.

The observed failure rate is 2β (symmetric: failures preferring slot A + slot B);
β itself = failure_rate / 2.  Results are stratified into two length bins by the
original-ground-truth character length, balanced by rank-based median split.

GT-vs-GT pairs are drawn from two sources:
  1. Questions in the main benchmark with ≥2 answer_strings typed "ground_truth".
  2. Records in the companion *_alternateGT.jsonl file (original_gt / alternate_gt).

Results feed the per-stratum (n_tie_trials, k_nontie) arrays consumed by the
Bayesian bias-correction model in bayesian_correction_spec_with_gt_ties.md.

Usage
-----
  python judge_beta_reliability_nocontext.py --judge MODEL_ID [options]

  --judge MODEL_ID              (required) Judge model, e.g. anthropic/claude-opus-4-7
  --benchmark PATH              Main benchmark JSONL
                                (default: ../booksample/chronologic_en_0.3.jsonl)
  --alternate-gt PATH           Alternate-GT JSONL. Default: derived by inserting
                                "_alternateGT" before ".jsonl" in --benchmark path.
  --openrouter-credentials PATH (default: ../bertclassify/OpenRouterCredentials.txt)
  --openai-credentials PATH     (default: ../evalcode/credentials.txt)
  --reasoning-effort LEVEL      none|low|medium|high (default: none)
  --output PATH                 Override output file path.
  --limit N                     Process only first N pairs (bins still computed from
                                the full pool so they stay consistent).
  --seed INT                    RNG seed (default: 17; positions are forced so has
                                minimal effect in practice).
  --debug                       Print raw judge responses.
  --dry-run                     Build pairs, print counts and length split, then exit
                                without making any judge calls.

Output
------
Written to beta_reliability/{judge}__{version}.json:
{
  "judge_model": "...",
  "reasoning_effort": "none",
  "benchmark_version": "0.3",
  "length_threshold_chars": 33,
  "n_pairs": 84,
  "sources": {"main": 16, "alt": 68},
  "completed_pair_ids": [...],
  "overall": {
    "question_fit": {"n_tie_trials": 168, "k_nontie": 47, "two_beta": 0.28, "beta": 0.14,
                     "k_A": 24, "k_B": 23, "invalid": 0}
  },
  "by_length_bin": {
    "short": {"n_pairs": 42,
              "question_fit": {"n_tie_trials": ..., "k_nontie": ..., ...}},
    "long":  {"n_pairs": 42, ...}
  }
}

k_A + k_B == k_nontie always.  two_beta == k_nontie / n_tie_trials; beta == two_beta / 2.

Examples
--------
  # Dry-run: confirm pair counts and length split (no judge calls):
  python judge_beta_reliability_nocontext.py --judge anthropic/claude-opus-4-7 --dry-run

  # Smoke test (6 pairs):
  python judge_beta_reliability_nocontext.py --judge openai/gpt-4o-mini --limit 6 --debug

  # Full run:
  python judge_beta_reliability_nocontext.py --judge anthropic/claude-opus-4-7
"""

import json
import random
import signal
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from judge_prompts_nocontext import score_one_comparison
from judge_alpha_reliability_nocontext import (
    _make_judge_call,
    _sanitize,
    _parse_benchmark_version,
    _load_benchmark,
    _write_output,
)

BETA_RELIABILITY_DIR = SCRIPT_DIR / "beta_reliability"
DEFAULT_BENCHMARK = SCRIPT_DIR.parent / "booksample" / "chronologic_en_0.3.jsonl"


# ---------------------------------------------------------------------------
# Pair construction (unchanged from deprecated version)
# ---------------------------------------------------------------------------

def _derive_alt_gt_path(benchmark_path):
    """Insert '_alternateGT' before the .jsonl suffix."""
    p = Path(benchmark_path)
    return p.parent / (p.stem + "_alternateGT" + p.suffix)


def _load_alt_gt(path):
    """Load alternate-GT JSONL; returns list of record dicts."""
    path = Path(path)
    if not path.exists():
        print(f"  [warning] alternate-GT file not found: {path}")
        return []
    records = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def build_gt_pairs(main_records, alt_records):
    """Build a list of GT-vs-GT pair dicts.

    Sources:
      - main_records: benchmark JSONL records; questions with >=2 answer_strings
        typed 'ground_truth' yield pairs (first GT as 'original').
      - alt_records: alternate-GT JSONL records (keys: original_gt, alternate_gt,
        question_number, metadata_frame, question); metadata and reasoning_type
        are joined from main_records by question_number.

    Each returned dict has:
      pair_id, question_number, source ('main' or 'alt'),
      original_gt, other_gt, orig_len,
      context, question, reasoning_type.
    """
    main_index = {}
    for i, r in enumerate(main_records):
        qnum = str(r.get("question_number", i))
        main_index[qnum] = r

    pairs = []

    for i, r in enumerate(main_records):
        qnum = str(r.get("question_number", i))
        strings = r.get("answer_strings", [])
        types   = r.get("answer_types", [])
        gts = [s for s, t in zip(strings, types) if t == "ground_truth"]
        if len(gts) < 2:
            continue
        original_gt = gts[0]
        context        = r.get("metadata_frame", "")
        question       = r.get("main_question", "")
        reasoning_type = r.get("reasoning_type", "")
        for k, other_gt in enumerate(gts[1:], start=1):
            pairs.append({
                "pair_id":       f"main:{qnum}:{k}",
                "question_number": qnum,
                "source":        "main",
                "original_gt":   original_gt,
                "other_gt":      other_gt,
                "orig_len":      len(original_gt),
                "context":       context,
                "question":      question,
                "reasoning_type": reasoning_type,
            })

    for alt in alt_records:
        original_gt = alt.get("original_gt") or alt.get("original_GT") or ""
        other_gt    = alt.get("alternate_gt") or alt.get("alternate_GT") or ""
        if not original_gt or not other_gt:
            continue
        qnum = str(alt.get("question_number", ""))
        main_rec = main_index.get(qnum, {})
        context        = main_rec.get("metadata_frame") or alt.get("metadata_frame", "")
        question       = main_rec.get("main_question")  or alt.get("question", "")
        reasoning_type = main_rec.get("reasoning_type", "")
        pairs.append({
            "pair_id":       f"alt:{qnum}",
            "question_number": qnum,
            "source":        "alt",
            "original_gt":   original_gt,
            "other_gt":      other_gt,
            "orig_len":      len(original_gt),
            "context":       context,
            "question":      question,
            "reasoning_type": reasoning_type,
        })

    return pairs


# ---------------------------------------------------------------------------
# Length binning (unchanged)
# ---------------------------------------------------------------------------

def assign_length_bins(pairs):
    """Assign a 'bin' field ('short' or 'long') to each pair in-place.

    Uses a rank-based median split so bins are always as balanced as possible.
    Returns (pairs, threshold_chars).
    """
    n = len(pairs)
    if n == 0:
        return pairs, 0
    n_short = n // 2
    sorted_lens = sorted(p["orig_len"] for p in pairs)
    threshold = sorted_lens[n_short - 1] if n_short > 0 else 0

    indexed = sorted(
        range(n),
        key=lambda i: (pairs[i]["orig_len"], pairs[i]["pair_id"]),
    )
    for rank, pair_idx in enumerate(indexed):
        pairs[pair_idx]["bin"] = "short" if rank < n_short else "long"

    return pairs, threshold


# ---------------------------------------------------------------------------
# Tally helpers
# ---------------------------------------------------------------------------

def _make_empty_tally():
    return {"n_tie_trials": 0, "k_nontie": 0, "k_A": 0, "k_B": 0, "invalid": 0}


def _finalize_tally(t):
    """Return a copy of a raw tally dict with two_beta and beta appended."""
    d = {k: t.get(k, 0) for k in ("n_tie_trials", "k_nontie", "k_A", "k_B", "invalid")}
    n = d["n_tie_trials"]
    k = d["k_nontie"]
    d["two_beta"] = round(k / n, 4) if n > 0 else None
    d["beta"]     = round(k / (2 * n), 4) if n > 0 else None
    return d


def _merge_tallies(t1, t2):
    """Sum the five integer fields from two tally dicts."""
    return {
        field: t1.get(field, 0) + t2.get(field, 0)
        for field in ("n_tie_trials", "k_nontie", "k_A", "k_B", "invalid")
    }


# ---------------------------------------------------------------------------
# Core tally
# ---------------------------------------------------------------------------

def compute_beta_reliability(pairs, judge_call, limit=None, debug=False, on_progress=None):
    """Run GT-vs-GT comparisons and return raw tally dicts (question fit only).

    Each pair generates 2 judge calls (force_gt_position A then B).

    Success (tie detected):    outcome == 'tie'       → n_tie_trials += 1
    Failure (winner declared): outcome in {win,loss}  → k_nontie += 1;
        winner slot recorded for k_A / k_B position-symmetry diagnostic.
    Parse failure:             outcome == 'invalid'   → invalid += 1 (not in denominator).

    Args:
        pairs:      list of pair dicts with 'bin' field already set.
        judge_call: callable(user_prompt: str) -> str.
        limit:      process only first N pairs (None = all).
        debug:      print raw judge responses.
        on_progress: optional callback(pair_dict, overall_tallies, bin_tallies).

    Returns:
        (overall_tallies, bin_tallies, completed_pair_ids)
        overall_tallies:  {"question_fit": raw_tally}
        bin_tallies:      {"short": {"n_pairs": int, "question_fit": raw_tally},
                           "long": {...}}
        completed_pair_ids: list[str] in processing order.
    """
    rng = random.Random(42)

    overall = {"question_fit": _make_empty_tally()}
    bin_tallies = {
        "short": {"n_pairs": 0, "question_fit": _make_empty_tally()},
        "long":  {"n_pairs": 0, "question_fit": _make_empty_tally()},
    }
    completed = []

    if limit is not None:
        pairs = pairs[:limit]

    total = len(pairs)
    for idx, pair in enumerate(pairs):
        b = pair["bin"]
        bin_tallies[b]["n_pairs"] += 1

        for force_pos in ("A", "B"):
            result = score_one_comparison(
                judge_call,
                context=pair["context"],
                question=pair["question"],
                reasoning_type=pair["reasoning_type"],
                gt=pair["original_gt"],
                candidate=pair["other_gt"],
                rng=rng,
                force_gt_position=force_pos,
            )
            if debug:
                print(f"  [debug] pair={pair['pair_id']} pos={force_pos}")
                print(f"    orig_gt={pair['original_gt'][:50]!r}")
                print(f"    other_gt={pair['other_gt'][:50]!r}")
                print(f"    raw={result.get('raw', '')!r}")

            gt_pos = result["gt_position"]

            outcome = result["question_outcome"]
            t_ov  = overall["question_fit"]
            t_bin = bin_tallies[b]["question_fit"]

            if outcome == "invalid":
                t_ov["invalid"]  += 1
                t_bin["invalid"] += 1
            else:
                t_ov["n_tie_trials"]  += 1
                t_bin["n_tie_trials"] += 1
                if outcome in ("win", "loss"):
                    t_ov["k_nontie"]  += 1
                    t_bin["k_nontie"] += 1
                    winner_slot = gt_pos if outcome == "loss" else (
                        "A" if gt_pos == "B" else "B"
                    )
                    if winner_slot == "A":
                        t_ov["k_A"]  += 1
                        t_bin["k_A"] += 1
                    else:
                        t_ov["k_B"]  += 1
                        t_bin["k_B"] += 1

        completed.append(pair["pair_id"])

        q = overall["question_fit"]
        print(
            f"  [{idx + 1}/{total}] {pair['pair_id']!r:35s} "
            f"q_fail={q['k_nontie']}/{q['n_tie_trials']}  "
            f"bin={b} orig_len={pair['orig_len']}"
        )

        if on_progress:
            on_progress(pair, overall, bin_tallies)

    return overall, bin_tallies, completed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Measure type-II (tie-blindness) judge error (question fit only).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--judge", required=True, metavar="MODEL_ID")
    parser.add_argument("--benchmark", metavar="PATH", default=str(DEFAULT_BENCHMARK))
    parser.add_argument("--alternate-gt", metavar="PATH", default=None,
                        dest="alternate_gt")
    parser.add_argument("--openrouter-credentials", metavar="PATH", default=None,
                        dest="openrouter_cred")
    parser.add_argument("--openai-credentials", metavar="PATH", default=None,
                        dest="openai_cred")
    parser.add_argument("--reasoning-effort", metavar="LEVEL", default="none",
                        choices=["none", "low", "medium", "high"],
                        dest="reasoning_effort")
    parser.add_argument("--output", metavar="PATH", default=None)
    parser.add_argument("--limit", metavar="N", type=int, default=None)
    parser.add_argument("--seed", metavar="INT", type=int, default=17)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--dry-run", action="store_true", dest="dry_run")

    args = parser.parse_args()

    benchmark_version = _parse_benchmark_version(args.benchmark)
    alt_gt_path = args.alternate_gt or str(_derive_alt_gt_path(args.benchmark))
    output_path = (
        Path(args.output) if args.output
        else BETA_RELIABILITY_DIR / f"{_sanitize(args.judge)}__{benchmark_version}.json"
    )

    print(f"Loading benchmark: {args.benchmark}")
    main_records = _load_benchmark(args.benchmark)
    print(f"  {len(main_records)} questions loaded.")

    print(f"Loading alternate-GT: {alt_gt_path}")
    alt_records = _load_alt_gt(alt_gt_path)
    print(f"  {len(alt_records)} alternate-GT records loaded.")

    pairs = build_gt_pairs(main_records, alt_records)
    n_main = sum(1 for p in pairs if p["source"] == "main")
    n_alt  = sum(1 for p in pairs if p["source"] == "alt")
    print(f"GT-vs-GT pairs: {len(pairs)} total  ({n_main} from main, {n_alt} from alternate-GT)")

    if len(pairs) == 0:
        sys.exit("No GT-vs-GT pairs found. Check benchmark and alternate-GT paths.")

    pairs, threshold = assign_length_bins(pairs)
    n_short = sum(1 for p in pairs if p["bin"] == "short")
    n_long  = sum(1 for p in pairs if p["bin"] == "long")
    print(f"Length split (threshold ≤ {threshold} chars): short={n_short}, long={n_long}")

    if args.dry_run:
        print("\n-- dry-run: no judge calls --")
        print(f"Would process {min(len(pairs), args.limit) if args.limit else len(pairs)} pairs.")
        return

    completed_ids_existing = set()
    existing_overall = {}
    existing_bins = {}
    if output_path.exists():
        with open(output_path, encoding="utf-8") as fh:
            existing = json.load(fh)
        completed_ids_existing = set(existing.get("completed_pair_ids", []))
        existing_overall = existing.get("overall", {})
        existing_bins    = existing.get("by_length_bin", {})
        existing_effort  = existing.get("reasoning_effort")
        if existing_effort is not None and existing_effort != args.reasoning_effort:
            sys.exit(
                f"ERROR: {output_path} was produced with reasoning_effort={existing_effort!r} "
                f"but this run uses {args.reasoning_effort!r}. "
                "Pass --output PATH to write to a different file."
            )
        print(f"Resuming: {len(completed_ids_existing)} pairs already done.")

    new_pairs = [p for p in pairs if p["pair_id"] not in completed_ids_existing]
    if not new_pairs:
        print("All pairs already completed.")
        return

    judge_call = _make_judge_call(
        args.judge, args.openrouter_cred, args.openai_cred,
        debug=args.debug, reasoning_effort=args.reasoning_effort,
    )

    output_data = {
        "judge_model": args.judge,
        "reasoning_effort": args.reasoning_effort,
        "benchmark_version": benchmark_version,
        "length_threshold_chars": threshold,
        "n_pairs": len(pairs),
        "sources": {"main": n_main, "alt": n_alt},
        "completed_pair_ids": list(completed_ids_existing),
        "overall": {},
        "by_length_bin": {},
    }

    def _recompute_and_write(new_overall, new_bin_tallies, new_completed):
        merged_overall = {
            "question_fit": _finalize_tally(
                _merge_tallies(
                    existing_overall.get("question_fit", _make_empty_tally()),
                    new_overall.get("question_fit", _make_empty_tally()),
                )
            )
        }
        merged_bins = {}
        for b in ("short", "long"):
            ext_b = existing_bins.get(b, {})
            new_b = new_bin_tallies.get(b, {})
            merged_bins[b] = {
                "n_pairs": ext_b.get("n_pairs", 0) + new_b.get("n_pairs", 0),
                "question_fit": _finalize_tally(
                    _merge_tallies(
                        ext_b.get("question_fit", _make_empty_tally()),
                        new_b.get("question_fit", _make_empty_tally()),
                    )
                ),
            }
        output_data["overall"] = merged_overall
        output_data["by_length_bin"] = merged_bins
        output_data["completed_pair_ids"] = (
            list(completed_ids_existing) + new_completed
        )
        _write_output(output_path, output_data)

    def _save_and_exit(sig, frame):
        print("\nInterrupted — saving partial results...")
        _recompute_and_write(current_overall[0], current_bins[0], current_completed[0])
        print(f"Saved to {output_path}")
        sys.exit(0)

    current_overall   = [{}]
    current_bins      = [{}]
    current_completed = [[]]
    signal.signal(signal.SIGINT, _save_and_exit)

    def on_progress(pair, ov, bins):
        current_overall[0]   = ov
        current_bins[0]      = bins
        current_completed[0] = list(pair_completed_so_far)
        n_done = len(completed_ids_existing) + len(pair_completed_so_far)
        if n_done % 10 == 0:
            _recompute_and_write(ov, bins, current_completed[0])

    pair_completed_so_far = []

    def _on_progress_wrapper(pair, ov, bins):
        pair_completed_so_far.append(pair["pair_id"])
        on_progress(pair, ov, bins)

    print(f"\nScoring {len(new_pairs)} pairs with judge: {args.judge}")
    try:
        new_overall, new_bin_tallies, new_completed = compute_beta_reliability(
            new_pairs, judge_call,
            limit=args.limit,
            debug=args.debug,
            on_progress=_on_progress_wrapper,
        )
    except Exception as exc:
        print(f"\nError: {type(exc).__name__}: {exc}")
        _recompute_and_write(current_overall[0], current_bins[0], current_completed[0])
        print(f"Partial results saved to {output_path}. Re-run to resume.")
        raise

    _recompute_and_write(new_overall, new_bin_tallies, new_completed)

    final = output_data["overall"]
    print(f"\nDone. {len(output_data['completed_pair_ids'])} pairs evaluated.")
    t = final["question_fit"]
    if t["n_tie_trials"]:
        print(
            f"  question_fit: n={t['n_tie_trials']}  k_nontie={t['k_nontie']}  "
            f"2β={t['two_beta']:.3f}  β={t['beta']:.3f}  "
            f"k_A={t['k_A']} k_B={t['k_B']}  invalid={t['invalid']}"
        )
    print(f"Output: {output_path.resolve()}")


if __name__ == "__main__":
    main()

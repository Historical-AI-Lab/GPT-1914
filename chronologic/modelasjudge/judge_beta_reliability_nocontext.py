"""
judge_beta_reliability_nocontext.py — Collect GT-vs-GT judge comparison outcomes
for the ChronoLogic β (tie-blindness) reliability estimation pipeline.

For each pair of equally-valid ground truths, asks the LLM judge to compare them
in both orderings (GT1-vs-GT2 and GT2-vs-GT1).  Any declared winner is a failure;
only "C" (tie) counts as a correct judgment.

The observed per-trial failure rate is 2β (symmetric: failures preferring slot A
+ slot B); β itself = failure_rate / 2.  Results are written as a per-pair JSONL
for downstream analysis by fit_beta_regression_nocontext.py, which fits a PyMC
hierarchical logistic regression and post-stratifies over the full benchmark
population to produce per-question 2β estimates.

GT-vs-GT pairs are drawn from two sources:
  1. Questions in the main benchmark with ≥2 answer_strings typed "ground_truth".
  2. Records in the companion *_alternateGT.jsonl file (original_gt / alternate_gt).

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
  --output PATH                 Override output JSONL path.
  --limit N                     Process only first N pairs.
  --seed INT                    RNG seed (default: 17; positions are forced so has
                                minimal effect in practice).
  --debug                       Print raw judge responses.
  --dry-run                     Build pairs, print counts and frame_type distribution,
                                then exit without making any judge calls.

Output
------
Written to beta_reliability/gt_pairs_{judge}__{version}.jsonl, one JSON per line:
{
  "pair_id": "alt:7",
  "question_number": "7",
  "source": "alt",
  "frame_type": "world_context",
  "reasoning_type": "knowledge",
  "orig_len": 17,
  "n_valid_trials": 2,
  "k_nontie": 1,
  "k_A": 1,
  "k_B": 0,
  "invalid": 0,
  "judge_model": "anthropic/claude-opus-4-7",
  "reasoning_effort": "none",
  "benchmark_version": "0.3"
}

k_A + k_B == k_nontie always.  n_valid_trials + invalid == 2 (one per ordering).

Feed this JSONL to fit_beta_regression_nocontext.py to infer per-question 2β.

Examples
--------
  # Dry-run: check pair counts and frame_type distribution
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
)

BETA_RELIABILITY_DIR = SCRIPT_DIR / "beta_reliability"
DEFAULT_BENCHMARK = SCRIPT_DIR.parent / "booksample" / "chronologic_en_0.3.jsonl"

# Derived deterministically from reasoning_type; mirrors QuestionCategorizer.py.
_REASONING_TO_FRAME = {
    "knowledge":             "world_context",
    "refusal":               "world_context",
    "inference":             "world_context",
    "character_modeling":    "book_context",
    "constrained_generation":"book_context",
    "topic_sentence":        "book_context",
    "phrase_cloze":          "passage_context",
    "sentence_cloze":        "passage_context",
}


def _infer_frame_type(reasoning_type):
    """Return frame_type string from reasoning_type; empty string if unknown."""
    return _REASONING_TO_FRAME.get(reasoning_type, "")


# ---------------------------------------------------------------------------
# Pair construction
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
        question_number, metadata_frame, question); metadata, reasoning_type, and
        frame_type are joined from main_records by question_number.

    Each returned dict has:
      pair_id, question_number, source ('main' or 'alt'),
      original_gt, other_gt, orig_len,
      frame_type, context, question, reasoning_type.
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
        original_gt    = gts[0]
        context        = r.get("substantive_metadata_frame") or r.get("metadata_frame", "")
        question       = r.get("main_question", "")
        reasoning_type = r.get("reasoning_type", "")
        frame_type     = r.get("frame_type") or _infer_frame_type(reasoning_type)
        for k, other_gt in enumerate(gts[1:], start=1):
            pairs.append({
                "pair_id":        f"main:{qnum}:{k}",
                "question_number": qnum,
                "source":         "main",
                "original_gt":    original_gt,
                "other_gt":       other_gt,
                "orig_len":       len(original_gt),
                "frame_type":     frame_type,
                "context":        context,
                "question":       question,
                "reasoning_type": reasoning_type,
            })

    for alt in alt_records:
        original_gt = alt.get("original_gt") or alt.get("original_GT") or ""
        other_gt    = alt.get("alternate_gt") or alt.get("alternate_GT") or ""
        if not original_gt or not other_gt:
            continue
        qnum       = str(alt.get("question_number", ""))
        main_rec   = main_index.get(qnum, {})
        context    = (main_rec.get("substantive_metadata_frame")
                      or main_rec.get("metadata_frame")
                      or alt.get("substantive_metadata_frame")
                      or alt.get("metadata_frame", ""))
        question   = main_rec.get("main_question")  or alt.get("question", "")
        reasoning_type = main_rec.get("reasoning_type", "")
        frame_type = main_rec.get("frame_type") or _infer_frame_type(reasoning_type)
        pairs.append({
            "pair_id":        f"alt:{qnum}",
            "question_number": qnum,
            "source":         "alt",
            "original_gt":    original_gt,
            "other_gt":       other_gt,
            "orig_len":       len(original_gt),
            "frame_type":     frame_type,
            "context":        context,
            "question":       question,
            "reasoning_type": reasoning_type,
        })

    return pairs


# ---------------------------------------------------------------------------
# JSONL resume helpers
# ---------------------------------------------------------------------------

def _load_existing_pair_ids(path):
    """Return (pair_ids_set, first_reasoning_effort_seen_or_None) from existing JSONL."""
    path = Path(path)
    if not path.exists():
        return set(), None
    pair_ids = set()
    effort = None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                pair_ids.add(rec["pair_id"])
                if effort is None:
                    effort = rec.get("reasoning_effort")
            except (json.JSONDecodeError, KeyError):
                pass
    return pair_ids, effort


def _build_pair_record(pair, outcome, judge_model, reasoning_effort, benchmark_version):
    """Merge pair metadata and outcome counts into a single JSONL record."""
    return {
        "pair_id":         pair["pair_id"],
        "question_number": pair["question_number"],
        "source":          pair["source"],
        "frame_type":      pair.get("frame_type", ""),
        "reasoning_type":  pair.get("reasoning_type", ""),
        "orig_len":        pair["orig_len"],
        "n_valid_trials":  outcome["n_valid_trials"],
        "k_nontie":        outcome["k_nontie"],
        "k_A":             outcome["k_A"],
        "k_B":             outcome["k_B"],
        "invalid":         outcome["invalid"],
        "judge_model":     judge_model,
        "reasoning_effort":reasoning_effort,
        "benchmark_version": benchmark_version,
    }


# ---------------------------------------------------------------------------
# Core collection
# ---------------------------------------------------------------------------

def collect_pair_outcomes(pairs, judge_call, limit=None, debug=False, on_pair_done=None):
    """Run GT-vs-GT comparisons and return per-pair outcome records.

    Each pair generates 2 judge calls (force_gt_position A then B).
    Outcome per trial:
      tie    → n_valid_trials += 1
      win/loss → n_valid_trials += 1, k_nontie += 1, winner slot → k_A or k_B
      invalid → invalid += 1 (not in n_valid_trials)

    Args:
        pairs:        list of pair dicts (from build_gt_pairs).
        judge_call:   callable(user_prompt: str) -> str.
        limit:        process only first N pairs (None = all).
        debug:        print raw judge responses.
        on_pair_done: optional callback(pair_dict, outcome_dict) called after each pair.

    Returns:
        (outcome_records, completed_pair_ids)
        outcome_records:    list[dict] with n_valid_trials/k_nontie/k_A/k_B/invalid.
        completed_pair_ids: list[str] in processing order.
    """
    rng = random.Random(42)
    outcome_records = []
    completed = []

    if limit is not None:
        pairs = pairs[:limit]

    total = len(pairs)
    running_trials = 0
    running_failures = 0
    for idx, pair in enumerate(pairs):
        k_nontie = k_A = k_B = invalid = n_valid = 0

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

            outcome = result["question_outcome"]
            if outcome == "invalid":
                invalid += 1
            else:
                n_valid += 1
                if outcome in ("win", "loss"):
                    k_nontie += 1
                    gt_pos = result["gt_position"]
                    winner_slot = gt_pos if outcome == "loss" else (
                        "A" if gt_pos == "B" else "B"
                    )
                    if winner_slot == "A":
                        k_A += 1
                    else:
                        k_B += 1

        rec = {
            "n_valid_trials": n_valid,
            "k_nontie":       k_nontie,
            "k_A":            k_A,
            "k_B":            k_B,
            "invalid":        invalid,
        }
        outcome_records.append(rec)
        completed.append(pair["pair_id"])

        running_trials += n_valid
        running_failures += k_nontie
        print(
            f"  [{idx + 1}/{total}] {pair['pair_id']!r:35s} "
            f"fail={k_nontie}/{n_valid}  "
            f"running={running_failures}/{running_trials}  "
            f"frame={pair.get('frame_type', '?')} len={pair['orig_len']}"
        )

        if on_pair_done:
            on_pair_done(pair, rec)

    return outcome_records, completed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Collect GT-vs-GT judge comparison outcomes (per-pair JSONL).",
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
        else BETA_RELIABILITY_DIR / f"gt_pairs_{_sanitize(args.judge)}__{benchmark_version}.jsonl"
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

    if pairs:
        from collections import Counter
        frame_counts = Counter(p.get("frame_type", "") for p in pairs)
        print("  frame_type distribution:", dict(frame_counts))

    if len(pairs) == 0:
        sys.exit("No GT-vs-GT pairs found. Check benchmark and alternate-GT paths.")

    if args.dry_run:
        print("\n-- dry-run: no judge calls --")
        n_to_process = min(len(pairs), args.limit) if args.limit else len(pairs)
        print(f"Would process {n_to_process} pairs.")
        return

    BETA_RELIABILITY_DIR.mkdir(exist_ok=True)

    completed_ids_existing, existing_effort = _load_existing_pair_ids(output_path)
    if completed_ids_existing:
        if existing_effort is not None and existing_effort != args.reasoning_effort:
            sys.exit(
                f"ERROR: {output_path} was produced with reasoning_effort={existing_effort!r} "
                f"but this run uses {args.reasoning_effort!r}. "
                "Pass --output PATH to write to a different file."
            )
        print(f"Resuming: {len(completed_ids_existing)} pairs already written.")

    new_pairs = [p for p in pairs if p["pair_id"] not in completed_ids_existing]
    if not new_pairs:
        print("All pairs already completed.")
        return

    judge_call = _make_judge_call(
        args.judge, args.openrouter_cred, args.openai_cred,
        debug=args.debug, reasoning_effort=args.reasoning_effort,
    )

    out_fh = open(output_path, "a", encoding="utf-8")

    def on_pair_done(pair, outcome):
        record = _build_pair_record(
            pair, outcome, args.judge, args.reasoning_effort, benchmark_version
        )
        out_fh.write(json.dumps(record) + "\n")
        out_fh.flush()

    def _sigint_handler(sig, frame):
        print(f"\nInterrupted — partial results in {output_path}")
        out_fh.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, _sigint_handler)

    print(f"\nScoring {len(new_pairs)} pairs with judge: {args.judge}")
    print(f"Output: {output_path}")
    try:
        _, new_completed = collect_pair_outcomes(
            new_pairs, judge_call,
            limit=args.limit,
            debug=args.debug,
            on_pair_done=on_pair_done,
        )
    except Exception as exc:
        print(f"\nError: {type(exc).__name__}: {exc}")
        print(f"Partial results saved to {output_path}. Re-run to resume.")
        out_fh.close()
        raise
    finally:
        out_fh.close()

    total_done = len(completed_ids_existing) + len(new_completed)
    print(f"\nDone. {total_done} pairs written to {output_path.resolve()}")
    print("Run fit_beta_regression_nocontext.py on this file to infer per-question 2β.")


if __name__ == "__main__":
    main()

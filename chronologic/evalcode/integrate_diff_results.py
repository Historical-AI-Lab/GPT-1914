"""
Stage C: Integrate stage-B diff results with old 0.2 results to produce 0.4 files.

Takes an old result file (against 0.2), a diff result file (against the
mini-benchmark produced by make_benchmark_diff.py), the diff_manifest.json,
and the 0.4 benchmark JSONL.  Produces a merged 0.4 result file in --out-dir
with recomputed confidence intervals keyed to the 0.4 question set.

Usage — single file
-------------------
python evalcode/integrate_diff_results.py \\
    --old   evalcode/prob_02/eval_results_full_Qwen_Qwen2.5-32B-Instruct_20260329_124736.json \\
    --diff  evalcode/prob_04_diff/eval_results_full_Qwen_Qwen2.5-32B-Instruct_<ts>.json \\
    --manifest evalcode/diff_0.2_to_0.4/diff_manifest.json \\
    --benchmark booksample/chronologic_en_0.4.jsonl \\
    --out-dir evalcode/prob_04

Usage — batch (all models in a folder)
---------------------------------------
python evalcode/integrate_diff_results.py \\
    --batch-old   evalcode/mcq_02 \\
    --batch-diff  evalcode/mcq_04_diff \\
    --manifest    evalcode/diff_0.2_to_0.4/diff_manifest.json \\
    --benchmark   booksample/chronologic_en_0.4.jsonl \\
    --out-dir     evalcode/mcq_04

Batch mode matches old and diff files by model_safe slug (the string between
`eval_results_{mcq|full}_` and the timestamp).  If multiple diff files match
the same slug the most recent (by embedded timestamp) is used.

Notes
-----
- MCQ integration is fully exact: only the boolean `correct` is needed.
- Probabilistic integration is approximate for Brier CIs: old 0.2 prob files
  store only normalized model_probs, not raw log-likelihoods.  This script
  reconstructs per-option logprobs as log(model_probs) (exact up to a per-
  question additive constant that cancels in within-question comparisons).
  Accuracy and skill-score CIs are computed exactly.  Metadata flags
  `brier_ci_approximate: true` when any old-path question contributes.
- New diff results produced with the patched benchmark_evaluation.py carry a
  `model_logprobs` key; these are used as-is (no reconstruction).
"""

import argparse
import datetime
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Import shared eval helpers from benchmark_evaluation.py in the same folder
# ---------------------------------------------------------------------------
_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))
from benchmark_evaluation import (
    build_subset_index,
    bootstrap_evaluate,
    write_json_report,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path):
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def model_safe_slug(model_id, lora_adapter=None):
    """Replicate benchmark_evaluation.py's filename slug logic."""
    slug = model_id.replace(":", "_").replace("/", "_")
    if lora_adapter:
        slug += "_" + Path(lora_adapter).name
    return slug


def extract_slug_from_filename(fname):
    """
    Extract model_safe slug from an eval result filename.

    Patterns:
      eval_results_mcq_{slug}_{timestamp}.json
      eval_results_full_{slug}_{timestamp}.json
    Timestamp is always 15 chars: YYYYMMDD_HHMMSS
    """
    stem = Path(fname).stem  # drop .json
    for prefix in ("eval_results_mcq_", "eval_results_full_", "eval_results_"):
        if stem.startswith(prefix):
            rest = stem[len(prefix):]
            # Timestamp is last 15 chars (YYYYMMDD_HHMMSS); slug is everything before
            if len(rest) > 16 and rest[-15].isdigit():
                return rest[:-16]  # drop _YYYYMMDD_HHMMSS
            return rest
    return stem


def count_non_negation_options(question):
    """Return the number of answer options that aren't 'negation' type."""
    types = question.get("answer_types", [])
    return sum(1 for t in types if t != "negation")


def reconstruct_logprobs(model_probs):
    """
    Approximate per-option log-likelihoods from a saved model_probs vector.

    The original logprobs were converted via softmax, so we can only recover
    them up to a shared additive constant.  log(p) is exact up to that constant,
    which cancels within any single question's comparisons (argmax, Brier).
    """
    eps = 1e-12
    return [math.log(max(p, eps)) for p in model_probs]


# ---------------------------------------------------------------------------
# Core integration logic
# ---------------------------------------------------------------------------

def integrate(old_path, diff_path, manifest_path, benchmark_path,
              out_dir, n_bootstrap=1000, reasoning_effort=None):
    """
    Merge one old result file with one diff result file and write 0.4 output.

    Returns the path to the written file.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    old_result  = load_json(old_path)
    diff_result = load_json(diff_path) if diff_path else None
    manifest    = load_json(manifest_path)
    questions04 = load_jsonl(benchmark_path)

    old_meta  = old_result["metadata"]
    eval_mode = old_meta["eval_mode"]

    # -----------------------------------------------------------------------
    # Validation
    # -----------------------------------------------------------------------
    old_qnum_order  = manifest["old_qnum_order"]
    new_qnum_order  = manifest["new_qnum_order"]
    rerun_qnums     = manifest["rerun_qnums"]
    deleted_qnums   = set(manifest["deleted_qnums"])
    rerun_set       = set(rerun_qnums)

    n_old = len(old_result["per_question_results"])
    if n_old != len(old_qnum_order):
        raise ValueError(
            f"Old result has {n_old} entries but manifest old_qnum_order has "
            f"{len(old_qnum_order)} entries.  Wrong manifest or result file?"
        )

    if diff_result is not None:
        diff_meta = diff_result["metadata"]
        if diff_meta.get("model_id") != old_meta["model_id"]:
            raise ValueError(
                f"Model ID mismatch:\n  old:  {old_meta['model_id']}\n"
                f"  diff: {diff_meta['model_id']}\n"
                "Ensure the diff result was produced for the same model."
            )
        if diff_meta.get("eval_mode") != eval_mode:
            raise ValueError(
                f"Eval mode mismatch: old={eval_mode}, diff={diff_meta['eval_mode']}"
            )
        n_diff = len(diff_result["per_question_results"])
        if n_diff != len(rerun_qnums):
            raise ValueError(
                f"Diff result has {n_diff} entries but manifest rerun_qnums has "
                f"{len(rerun_qnums)} entries.  Wrong diff file?"
            )
    elif rerun_qnums:
        raise ValueError(
            f"Manifest lists {len(rerun_qnums)} questions to re-run but no --diff "
            "file was supplied.  Provide --diff or use --no-diff (only valid when "
            "rerun_qnums is empty)."
        )

    n_new = len(new_qnum_order)
    if len(questions04) != n_new:
        raise ValueError(
            f"Benchmark 0.4 has {len(questions04)} questions but manifest "
            f"new_qnum_order has {n_new} entries."
        )

    # -----------------------------------------------------------------------
    # Index old and diff results by question_number
    # -----------------------------------------------------------------------
    old_by_qnum = {}
    for i, qn in enumerate(old_qnum_order):
        old_by_qnum[qn] = old_result["per_question_results"][i]

    diff_by_qnum = {}
    if diff_result is not None:
        for i, qn in enumerate(rerun_qnums):
            diff_by_qnum[qn] = diff_result["per_question_results"][i]

    # -----------------------------------------------------------------------
    # Build merged per-question list in 0.4 order
    # -----------------------------------------------------------------------
    merged = []   # one entry per 0.4 question
    for qn in new_qnum_order:
        if qn in rerun_set:
            merged.append(diff_by_qnum[qn])
        else:
            merged.append(old_by_qnum[qn])

    assert len(merged) == n_new

    # -----------------------------------------------------------------------
    # Recompute confidence intervals against 0.4
    # -----------------------------------------------------------------------
    subset_index = build_subset_index(questions04)

    if eval_mode == "mcq":
        # Recover k (option count) from the 0.4 benchmark
        model_results_for_bootstrap = [
            {
                "is_correct": entry["correct"],
                "k": count_non_negation_options(questions04[i]),
            }
            for i, entry in enumerate(merged)
        ]
        gt_probs_list = [q["answer_probabilities"] for q in questions04]

        confidence_intervals = bootstrap_evaluate(
            gt_probs_list,
            model_results_for_bootstrap,
            subset_index,
            mode="mcq",
            n_bootstrap=n_bootstrap,
        )
        correct_vector = [bool(e["correct"]) for e in merged]
        brier_approximate = False
        n_reconstructed = 0

    else:  # probabilistic
        gt_probs_list    = [q["answer_probabilities"] for q in questions04]
        model_probs_list = [e["model_probs"] for e in merged]

        # Use saved logprobs where available (new diff entries), reconstruct otherwise
        model_logprobs_list = []
        n_reconstructed = 0
        for qn, entry in zip(new_qnum_order, merged):
            if "model_logprobs" in entry and entry["model_logprobs"] is not None:
                model_logprobs_list.append(entry["model_logprobs"])
            else:
                model_logprobs_list.append(reconstruct_logprobs(entry["model_probs"]))
                n_reconstructed += 1

        brier_approximate = n_reconstructed > 0

        correct_vector = [
            bool(np.argmax(mp) == np.argmax(gt))
            for mp, gt in zip(model_probs_list, gt_probs_list)
        ]

        confidence_intervals = bootstrap_evaluate(
            gt_probs_list,
            model_probs_list,
            subset_index,
            mode="probabilistic",
            n_bootstrap=n_bootstrap,
            model_logprobs=model_logprobs_list,
        )

    # -----------------------------------------------------------------------
    # Write output
    # -----------------------------------------------------------------------
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = model_safe_slug(old_meta["model_id"])
    if eval_mode == "mcq":
        out_filename = f"eval_results_mcq_{slug}_{timestamp}.json"
    else:
        out_filename = f"eval_results_full_{slug}_{timestamp}.json"
    out_path = out_dir / out_filename

    meta = {
        "model_id": old_meta["model_id"],
        "benchmark_file": str(Path(benchmark_path).resolve()),
        "eval_mode": eval_mode,
        "timestamp": timestamp,
        "n_questions": n_new,
        "n_bootstrap": n_bootstrap,
        # Provenance
        "derived_from": {
            "old_result": str(Path(old_path).resolve()),
            "diff_result": str(Path(diff_path).resolve()) if diff_path else None,
            "manifest": str(Path(manifest_path).resolve()),
        },
        "integration": "diff_0.2_to_0.4",
    }
    if reasoning_effort is not None:
        meta["reasoning_effort"] = reasoning_effort
    if old_meta.get("api"):
        meta["api"] = old_meta["api"]
    if eval_mode == "probabilistic":
        meta["brier_ci_approximate"] = brier_approximate
        meta["n_logprobs_reconstructed"] = n_reconstructed
        meta["n_logprobs_exact"] = n_new - n_reconstructed

    write_json_report(out_path, meta, merged, confidence_intervals, correct_vector)
    print(f"Written: {out_path}")
    if eval_mode == "probabilistic" and brier_approximate:
        print(
            f"  Note: Brier CIs are approximate "
            f"({n_reconstructed}/{n_new} questions used reconstructed logprobs)"
        )
    return out_path


# ---------------------------------------------------------------------------
# Batch mode: pair old files with diff files by model slug
# ---------------------------------------------------------------------------

def find_diff_for_slug(slug, diff_dir, eval_mode):
    """Return the most recent diff result file matching a model slug."""
    if eval_mode == "mcq":
        prefix = "eval_results_mcq_"
    else:
        prefix = "eval_results_full_"
    candidates = []
    for p in Path(diff_dir).glob(f"{prefix}*.json"):
        file_slug = extract_slug_from_filename(p.name)
        if file_slug == slug:
            candidates.append(p)
    if not candidates:
        return None
    # Most recent by embedded timestamp (last 15 chars of stem)
    candidates.sort(key=lambda p: p.stem[-15:])
    return candidates[-1]


def run_batch(batch_old_dir, batch_diff_dir, manifest_path, benchmark_path,
              out_dir, n_bootstrap=1000):
    """Integrate all old result files in batch_old_dir with matching diff files."""
    old_dir = Path(batch_old_dir)
    all_old = sorted(old_dir.glob("eval_results_*.json"))
    if not all_old:
        print(f"No eval_results_*.json files found in {batch_old_dir}")
        return

    successes, skipped = [], []
    for old_path in all_old:
        slug = extract_slug_from_filename(old_path.name)
        # Determine eval_mode from filename
        if "eval_results_full_" in old_path.name:
            eval_mode = "probabilistic"
        elif "eval_results_mcq_" in old_path.name:
            eval_mode = "mcq"
        else:
            print(f"  Skipping (unknown prefix): {old_path.name}")
            skipped.append(old_path.name)
            continue

        diff_path = find_diff_for_slug(slug, batch_diff_dir, eval_mode)
        if diff_path is None:
            print(f"  No diff file for slug '{slug}' — skipping {old_path.name}")
            skipped.append(old_path.name)
            continue

        print(f"Integrating: {old_path.name}")
        print(f"  diff: {diff_path.name}")
        try:
            integrate(
                old_path=str(old_path),
                diff_path=str(diff_path),
                manifest_path=manifest_path,
                benchmark_path=benchmark_path,
                out_dir=out_dir,
                n_bootstrap=n_bootstrap,
            )
            successes.append(old_path.name)
        except Exception as e:
            print(f"  ERROR: {e}")
            skipped.append(old_path.name)

    print()
    print(f"Batch complete: {len(successes)} succeeded, {len(skipped)} skipped/failed")
    if skipped:
        print("Skipped:", skipped)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Integrate benchmark diff results to produce 0.4 eval files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Single-file mode
    single = parser.add_argument_group("Single-file mode")
    single.add_argument("--old",  help="Path to old (0.2) result JSON")
    single.add_argument("--diff", help="Path to stage-B diff result JSON")

    # Batch mode
    batch = parser.add_argument_group("Batch mode")
    batch.add_argument("--batch-old",  help="Directory of old (0.2) result JSONs")
    batch.add_argument("--batch-diff", help="Directory of stage-B diff result JSONs")

    # Shared
    parser.add_argument(
        "--manifest",  required=True, help="Path to diff_manifest.json"
    )
    parser.add_argument(
        "--benchmark", required=True, help="Path to chronologic_en_0.4.jsonl"
    )
    parser.add_argument(
        "--out-dir", required=True, help="Output directory for integrated files"
    )
    parser.add_argument(
        "--n-bootstrap", type=int, default=1000,
        help="Bootstrap iterations for CIs (default 1000)"
    )
    parser.add_argument(
        "--reasoning-effort",
        help="OpenAI reasoning effort used in the original run (recorded in metadata)"
    )
    parser.add_argument(
        "--no-diff", action="store_true",
        help="Allow integration with no diff file (only valid when rerun_qnums is empty)"
    )

    args = parser.parse_args()

    if args.batch_old:
        if not args.batch_diff:
            parser.error("--batch-old requires --batch-diff")
        run_batch(
            batch_old_dir=args.batch_old,
            batch_diff_dir=args.batch_diff,
            manifest_path=args.manifest,
            benchmark_path=args.benchmark,
            out_dir=args.out_dir,
            n_bootstrap=args.n_bootstrap,
        )
    elif args.old:
        if not args.diff and not args.no_diff:
            parser.error("--old requires --diff (or --no-diff if rerun_qnums is empty)")
        integrate(
            old_path=args.old,
            diff_path=args.diff,
            manifest_path=args.manifest,
            benchmark_path=args.benchmark,
            out_dir=args.out_dir,
            n_bootstrap=args.n_bootstrap,
            reasoning_effort=args.reasoning_effort,
        )
    else:
        parser.error("Provide either --old (single-file mode) or --batch-old (batch mode)")


if __name__ == "__main__":
    main()

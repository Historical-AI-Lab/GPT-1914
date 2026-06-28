"""
score_calculation.py — Compute weighted aspect scores and overall binary accuracy.

Combines the LLM judge file with the discriminative judge file (style) to produce
weighted aspect means plus an overall binary accuracy score.

question_fit is scored by the LLM judge for all questions.
context_fit is scored by a human judge for book_context questions only; it is
absent (None) for world_context and passage_context questions, which count as a
pass on context (NA).
style is scored by the discriminative judge for all questions.

Two weighting schemes are reported for the aspect means:
  squared  — max(2*r_q − 1, 0)²   (inverse-variance under noisy-channel model)
  linear   — max(2*r_q − 1, 0)    (simpler alternative)

The overall binary accuracy is unweighted: a question passes iff it gets ≥ 0.5
on every non-NA aspect.  Style NA (r_q ≤ 0.70 per discriminative calibration)
counts as a pass.

Usage
-----
  python score_calculation.py [TAG] [options]

  TAG                     {candidate}__{version}, e.g. gpt-4.1-2025-04-14__0.2
                          (if omitted, supply --candidate and --version)
  --candidate MODEL_ID    Candidate model id (sanitized via naming.candidate_tag)
  --version STR           Benchmark version string, e.g. 0.2
  --judge-file PATH       Override LLM judge file (auto-located if omitted,
                          preferring *_human.json)
  --discrim-file PATH     Override discriminative judge file
  --output PATH           Override output path
  --quiet                 Print summary only; suppress per-question table

Output
------
Written to scored_answers/final_{candidate}__{version}.json:

{
  "candidate_model": "...",
  "candidate_reasoning_effort": "...",
  "benchmark_version": "0.2",
  "sources": {
    "judge_file": "...",
    "discrim_file": "...",
    "judge_used_human": true
  },
  "weighted_means": {
    "question_fit": {"squared": 0.83, "linear": 0.80},
    "context_fit":  {"squared": 0.91, "linear": 0.89},
    "style":        {"squared": 0.62, "linear": 0.60}
  },
  "overall_binary_accuracy": 0.74,
  "per_question": {
    "<qnum>": {
      "question_fit": {"score": 1.0, "r_q": 0.91, "weight_sq": 0.67,
                       "weight_lin": 0.82, "pass": true},
      "context_fit":  {"score": 0.5, "r_q": 0.88, "weight_sq": 0.58,
                       "weight_lin": 0.76, "pass": true},
      "style":        {"score": 0.42, "r_q": 0.78, "weight_sq": 0.31,
                       "weight_lin": 0.56, "pass": false, "na": false},
      "overall_pass": false
    }
  }
}

Examples
--------
  # By tag
  python score_calculation.py gpt-4.1-2025-04-14__0.2

  # By parts
  python score_calculation.py --candidate gpt-4.1-2025-04-14 --version 0.2
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from naming import candidate_tag as _candidate_tag

SCORED_DIR = SCRIPT_DIR / "scored_answers"


# ---------------------------------------------------------------------------
# Weight functions (public so tests can import them)
# ---------------------------------------------------------------------------

def weight_sq(r_q) -> float:
    """Squared inverse-variance weight: max(2*r_q − 1, 0)^2."""
    if r_q is None:
        return 0.0
    return max(2.0 * r_q - 1.0, 0.0) ** 2


def weight_lin(r_q) -> float:
    """Linear weight: max(2*r_q − 1, 0)."""
    if r_q is None:
        return 0.0
    return max(2.0 * r_q - 1.0, 0.0)


# ---------------------------------------------------------------------------
# Per-question score helpers (public for testing)
# ---------------------------------------------------------------------------

def question_score(scores_list: list) -> float:
    """Mean of the scores list (handles multi-GT comparisons)."""
    if not scores_list:
        return 0.0
    return sum(scores_list) / len(scores_list)


def aspect_pass(score: float) -> bool:
    """A question passes an aspect if its score is ≥ 0.5."""
    return score >= 0.5


# ---------------------------------------------------------------------------
# Weighted mean (public for testing)
# ---------------------------------------------------------------------------

def weighted_mean(pairs) -> float | None:
    """Weighted mean of (score, weight) pairs, skipping NA (weight==0 included, None excluded).

    Args:
        pairs: iterable of (score, weight) where score is float or None.
               None score → skip entirely (NA); weight of 0 still counts as zero
               contribution but doesn't add to denominator if score is None.

    Returns:
        float or None if total weight is 0.
    """
    total_w = 0.0
    total_sw = 0.0
    for score, w in pairs:
        if score is None:
            continue
        total_w += w
        total_sw += score * w
    if total_w == 0.0:
        return None
    return total_sw / total_w


# ---------------------------------------------------------------------------
# Auto-locate files
# ---------------------------------------------------------------------------

def _locate_judge_file(ctag: str, version: str) -> tuple[Path, bool]:
    """Return (path, used_human).  Prefers *_human.json.

    Matches both old naming (judge_*__{ctag}__{version}.json) and new naming
    that appends effort tokens (judge_*__{ctag}__{version}__c-*__j-*.json).
    """
    human_matches = sorted(SCORED_DIR.glob(f"judge_*__{ctag}__{version}*_human.json"))
    if human_matches:
        if len(human_matches) > 1:
            names = ", ".join(p.name for p in human_matches)
            raise ValueError(
                f"Ambiguous: multiple human judge files match {ctag}__{version}:\n"
                f"  {names}\nUse --judge-file to specify one."
            )
        return human_matches[0], True

    base_matches = sorted(SCORED_DIR.glob(f"judge_*__{ctag}__{version}*.json"))
    if not base_matches:
        raise FileNotFoundError(
            f"No judge file found in {SCORED_DIR} matching "
            f"judge_*__{ctag}__{version}[*].json"
        )
    if len(base_matches) > 1:
        names = ", ".join(p.name for p in base_matches)
        raise ValueError(
            f"Ambiguous: multiple judge files match {ctag}__{version}:\n"
            f"  {names}\nUse --judge-file to specify one."
        )
    return base_matches[0], False


def _locate_discrim_file(ctag: str, version: str) -> Path:
    matches = sorted(SCORED_DIR.glob(f"discrim_*__{ctag}__{version}.json"))
    if not matches:
        raise FileNotFoundError(
            f"No discriminative file found in {SCORED_DIR} matching "
            f"discrim_*__{ctag}__{version}.json"
        )
    if len(matches) > 1:
        names = ", ".join(p.name for p in matches)
        raise ValueError(
            f"Ambiguous: multiple discrim files match {ctag}__{version}:\n"
            f"  {names}\nUse --discrim-file to specify one."
        )
    return matches[0]


# ---------------------------------------------------------------------------
# Core computation (public for testing)
# ---------------------------------------------------------------------------

def compute_per_question(judge_data: dict, discrim_data: dict) -> dict:
    """Build the per_question result dict.

    Args:
        judge_data:   parsed judge JSON (question_fit / context_fit sections).
        discrim_data: parsed discrim JSON (style section + below_threshold).

    Returns:
        dict {qnum: {question_fit, context_fit, style, overall_pass}}
    """
    qf_section = judge_data.get("question_fit", {})
    ctx_section = judge_data.get("context_fit", {})
    style_section = discrim_data.get("style", {})
    below_threshold = set(str(q) for q in discrim_data.get("below_threshold", []))

    all_qnums = set(qf_section) | set(ctx_section) | set(style_section)
    per_q = {}

    for qnum in all_qnums:
        row = {}

        # question_fit
        qf = qf_section.get(qnum)
        if qf is not None:
            s = question_score(qf.get("scores", []))
            r = qf.get("r_q")
            row["question_fit"] = {
                "score": s,
                "r_q": r,
                "weight_sq": weight_sq(r),
                "weight_lin": weight_lin(r),
                "pass": aspect_pass(s),
            }
        else:
            row["question_fit"] = None

        # context_fit
        ctx = ctx_section.get(qnum)
        if ctx is not None:
            s = question_score(ctx.get("scores", []))
            r = ctx.get("r_q")
            row["context_fit"] = {
                "score": s,
                "r_q": r,
                "weight_sq": weight_sq(r),
                "weight_lin": weight_lin(r),
                "pass": aspect_pass(s),
            }
        else:
            row["context_fit"] = None

        # style
        st = style_section.get(qnum)
        is_na = qnum in below_threshold or st is None
        if is_na:
            row["style"] = {"score": None, "r_q": None, "weight_sq": 0.0,
                            "weight_lin": 0.0, "pass": True, "na": True}
        else:
            s = st.get("continuous")
            r = st.get("r_q")
            row["style"] = {
                "score": s,
                "r_q": r,
                "weight_sq": weight_sq(r),
                "weight_lin": weight_lin(r),
                "pass": aspect_pass(s) if s is not None else True,
                "na": False,
            }

        # overall_pass
        qf_pass = row["question_fit"]["pass"] if row["question_fit"] else True
        ctx_pass = row["context_fit"]["pass"] if row["context_fit"] else True
        style_pass = row["style"]["pass"]
        row["overall_pass"] = qf_pass and ctx_pass and style_pass

        per_q[qnum] = row

    return per_q


def compute_aspect_means(per_q: dict) -> dict:
    """Compute weighted means for each aspect under both schemes.

    Returns:
        {"question_fit": {"squared": float|None, "linear": float|None}, ...}
    """
    results = {}
    for aspect in ("question_fit", "context_fit", "style"):
        pairs_sq = []
        pairs_lin = []
        for row in per_q.values():
            entry = row.get(aspect)
            if entry is None:
                continue
            score = entry["score"]
            if score is None:
                continue
            pairs_sq.append((score, entry["weight_sq"]))
            pairs_lin.append((score, entry["weight_lin"]))
        results[aspect] = {
            "squared": weighted_mean(pairs_sq),
            "linear": weighted_mean(pairs_lin),
        }
    return results


def compute_overall_binary(per_q: dict) -> float | None:
    """Fraction of questions that overall_pass."""
    if not per_q:
        return None
    n_pass = sum(1 for row in per_q.values() if row.get("overall_pass", False))
    return n_pass / len(per_q)


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def _write_output(path: Path, data: dict) -> None:
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def _print_summary(weighted_means: dict, overall: float | None, quiet: bool,
                   per_q: dict) -> None:
    if not quiet:
        print(f"\n{'qnum':>8}  {'QF':>5}  {'CF':>5}  {'ST':>5}  pass")
        print("-" * 40)
        for qnum in sorted(per_q):
            row = per_q[qnum]
            qf_s = f"{row['question_fit']['score']:.2f}" if row.get("question_fit") else "  NA"
            cf_s = f"{row['context_fit']['score']:.2f}" if row.get("context_fit") else "  NA"
            st_entry = row.get("style", {})
            st_s = " NA" if st_entry.get("na") else (
                f"{st_entry['score']:.2f}" if st_entry.get("score") is not None else " NA"
            )
            passed = "✓" if row.get("overall_pass") else "✗"
            print(f"{qnum:>8}  {qf_s:>5}  {cf_s:>5}  {st_s:>5}  {passed}")

    print("\nWeighted means (squared / linear weighting):")
    for asp, v in weighted_means.items():
        sq = f"{v['squared']:.4f}" if v["squared"] is not None else "  null"
        lin = f"{v['linear']:.4f}" if v["linear"] is not None else "  null"
        print(f"  {asp:<14}: {sq}  /  {lin}")
    ov = f"{overall:.4f}" if overall is not None else "null"
    print(f"\nOverall binary accuracy: {ov}  (n={len(per_q)})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Compute weighted aspect scores and overall binary accuracy.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("tag", metavar="TAG", nargs="?", default=None,
                        help="{candidate}__{version} tag; alternative to --candidate/--version")
    parser.add_argument("--candidate", metavar="MODEL_ID", default=None)
    parser.add_argument("--version", metavar="STR", default=None)
    parser.add_argument("--judge-file", metavar="PATH", default=None, dest="judge_file")
    parser.add_argument("--discrim-file", metavar="PATH", default=None, dest="discrim_file")
    parser.add_argument("--output", metavar="PATH", default=None)
    parser.add_argument("--quiet", action="store_true")

    args = parser.parse_args()

    # Resolve candidate tag and version
    if args.tag:
        parts = args.tag.rsplit("__", 1)
        if len(parts) != 2:
            parser.error("TAG must be {candidate}__{version}, e.g. gpt-4.1-2025-04-14__0.2")
        ctag, version = parts
    elif args.candidate and args.version:
        ctag = _candidate_tag(args.candidate)
        version = args.version
    else:
        parser.error("Provide TAG or both --candidate and --version.")

    # Locate input files
    used_human = False
    if args.judge_file:
        judge_path = Path(args.judge_file)
        if not judge_path.exists():
            print(f"Error: judge file not found: {judge_path}", file=sys.stderr)
            sys.exit(1)
        used_human = "_human" in judge_path.stem
    else:
        judge_path, used_human = _locate_judge_file(ctag, version)

    if args.discrim_file:
        discrim_path = Path(args.discrim_file)
        if not discrim_path.exists():
            print(f"Error: discrim file not found: {discrim_path}", file=sys.stderr)
            sys.exit(1)
    else:
        discrim_path = _locate_discrim_file(ctag, version)

    print(f"Judge file:  {judge_path}")
    print(f"Discrim file:{discrim_path}")
    print(f"Human scores:{used_human}")

    with open(judge_path, encoding="utf-8") as fh:
        judge_data = json.load(fh)
    with open(discrim_path, encoding="utf-8") as fh:
        discrim_data = json.load(fh)

    candidate_model = judge_data.get("candidate_model",
                                     discrim_data.get("candidate_model", "unknown"))
    candidate_re = judge_data.get("candidate_reasoning_effort",
                                  discrim_data.get("candidate_reasoning_effort", "none"))
    bv = judge_data.get("benchmark_version",
                        discrim_data.get("benchmark_version", version))

    # Output path
    if args.output:
        output_path = Path(args.output)
    else:
        SCORED_DIR.mkdir(exist_ok=True)
        output_path = SCORED_DIR / f"final_{ctag}__{version}.json"

    # Compute
    per_q = compute_per_question(judge_data, discrim_data)
    means = compute_aspect_means(per_q)
    overall = compute_overall_binary(per_q)

    _print_summary(means, overall, args.quiet, per_q)

    output_data = {
        "candidate_model": candidate_model,
        "candidate_reasoning_effort": candidate_re,
        "benchmark_version": bv,
        "sources": {
            "judge_file": str(judge_path),
            "discrim_file": str(discrim_path),
            "judge_used_human": used_human,
        },
        "weighted_means": means,
        "overall_binary_accuracy": overall,
        "per_question": per_q,
    }
    _write_output(output_path, output_data)
    print(f"\nOutput: {output_path.resolve()}")


if __name__ == "__main__":
    main()

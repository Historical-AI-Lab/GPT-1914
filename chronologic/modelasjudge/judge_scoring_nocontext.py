"""
judge_scoring_nocontext.py — Score free-generated answers using an LLM judge
(question fit only).

Pairs a free-generation output file (from free_generation.py) with an LLM judge to
evaluate each candidate answer against the ground truth on question fit only.

Context fit is NOT scored by the LLM judge.  Instead, context_fit judgments are
collected by human_scoring.py for questions that are both frame_type "book_context"
AND reasoning_type "constrained_generation" (~98 questions).  Other book_context
reasoning types (character_modeling, topic_sentence) receive no context score
(NA → treated as a pass downstream), as do "world_context" and "passage_context"
questions.

For questions with multiple ground truths the judge runs multiple comparisons:
  - Odd #GTs: each GT tested once (random A/B position).
  - Even #GTs: one GT (chosen at random) is tested twice (both positions) as a
    tie-breaker; the rest are tested once. This ensures an odd total comparison
    count so a single answer cannot produce a 50/50 split.

Per-question LLM-judge reliability (q_r) is joined from the pre-computed
reliability file in llm_reliability/.  Questions below the reliability threshold
(0.65) are collected in a "needs_human" list so human_scoring.py knows which to
re-judge.  Constrained-generation book_context questions also appear in needs_human
with aspect "context_fit" so human_scoring.py requests context judgments for them.

Usage
-----
  python judge_scoring_nocontext.py FREE_GEN_FILE --judge MODEL_ID [options]

  --judge MODEL_ID          Judge model (e.g. anthropic/claude-opus-4-7, gpt-4.1-2025-04-14)
  --benchmark PATH          Benchmark JSONL; used to derive version string AND to load
                            frame_type per question.
                            (default: ../booksample/chronologic_en_0.2.jsonl)
  --reliability PATH        Pre-computed LLM reliability JSON; auto-located if omitted.
  --openrouter-credentials PATH
                            (default: ../bertclassify/OpenRouterCredentials.txt)
  --openai-credentials PATH (default: ../evalcode/credentials.txt)
  --reasoning-effort LEVEL  Reasoning effort for the JUDGE: none, low, medium, high
                            (default: none).
  --output PATH             Override output file path.
  --start QNUM              Resume from this question number (skip earlier).
  --limit N                 Process only N questions (useful for testing).
  --seed INT                Random seed for A/B position assignment (default: 17).
  --debug                   Print full judge responses.

Output
------
Written to scored_answers/judge_{judge}__{candidate}__{version}.json:

{
  "judge_model": "...",
  "candidate_model": "...",
  "candidate_reasoning_effort": "none",
  "benchmark_version": "0.2",
  "reasoning_effort": "none",
  "reliability_source": "llm_reliability/...",
  "thresholds": {"question_fit": 0.65},
  "question_fit": {
    "<qnum>": {
      "judge": "...",
      "r_q": 0.91,
      "judgments":   ["GT", "model", "tie"],
      "scores":      [0, 1, 1],
      "gt_positions":["B", "A", "B"],
      "gt_indices":  [0, 1, 1]
    }, ...
  },
  "context_fit": {},          // populated later by human_scoring.py for constrained_generation
  "book_context_qnums": [...],// qnums with frame_type == "book_context" AND reasoning_type == "constrained_generation"
  "needs_human": [
    {"qnum": "0123", "aspects": ["question_fit"]},
    {"qnum": "0456", "aspects": ["context_fit"]},
    {"qnum": "0789", "aspects": ["question_fit", "context_fit"]}
  ]
}

judgments use "GT" / "model" / "tie" / "invalid".
scores: 1 if the candidate wins or ties, else 0.
gt_indices: which entry in the ground_truths list (0-based) was used in each comparison.

Examples
--------
  # Smoke test (1 question):
  python judge_scoring_nocontext.py generated_answers/free_gen_gpt-4.1-2025-04-14__0.2.json \\
      --judge anthropic/claude-opus-4-7 --limit 1

  # Full run:
  python judge_scoring_nocontext.py generated_answers/free_gen_gpt-4.1-2025-04-14__0.2.json \\
      --judge anthropic/claude-opus-4-7
"""

import json
import random
import re
import signal
import string
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from judge_prompts_nocontext import score_one_comparison
from openrouter_client import is_openrouter_model, make_openrouter_client
from naming import judge_tag as _judge_tag, candidate_tag as _candidate_tag, sanitize as _sanitize

SCORED_DIR = SCRIPT_DIR / "scored_answers"
RELIABILITY_DIR = SCRIPT_DIR / "llm_reliability"

_QUESTION_FIT_THRESHOLD = 0.65


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PUNCT_TABLE = str.maketrans("", "", string.punctuation)


def _normalize_for_identity(s):
    return (s or "").lower().translate(_PUNCT_TABLE).strip()


def _parse_benchmark_version(path):
    name = Path(path).stem
    m = re.search(r"(\d+\.\d+)", name)
    return m.group(1) if m else "unknown"


def _is_openai_model(model_id):
    openai_prefixes = ("gpt-", "o1", "o3", "o4", "text-")
    return any(model_id.startswith(p) for p in openai_prefixes)


def _load_openai_credentials(cred_path=None):
    if cred_path is None:
        cred_path = SCRIPT_DIR.parent / "evalcode" / "credentials.txt"
    lines = [l.strip() for l in Path(cred_path).read_text(encoding="utf-8").splitlines() if l.strip()]
    if len(lines) < 2:
        raise ValueError(f"Expected 2 non-empty lines (org_id, api_key) in {cred_path}")
    return lines[0], lines[1]


def _make_judge_call(judge_model, openrouter_cred=None, openai_cred=None, debug=False,
                     reasoning_effort="none"):
    """Return a callable(user_prompt) -> str for the given judge model."""
    if judge_model.startswith("openai/"):
        judge_model = judge_model[len("openai/"):]
    if is_openrouter_model(judge_model):
        from openrouter_client import call_openrouter_chat
        client = make_openrouter_client(openrouter_cred)
        # visible-answer caps; call_openrouter_chat adds +2048 thinking headroom when effort != "none"
        _max_tokens = {"none": 50, "low": 1024, "medium": 4096, "high": 16000}[reasoning_effort]
        def judge_call(prompt):
            return call_openrouter_chat(
                client, judge_model, prompt, system_content="",
                max_tokens=_max_tokens, debug=debug, reasoning_effort=reasoning_effort,
            )
        return judge_call
    elif _is_openai_model(judge_model):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("pip install openai") from exc
        org_id, api_key = _load_openai_credentials(openai_cred)
        client = OpenAI(organization=org_id, api_key=api_key)
        _token_key = (
            "max_completion_tokens"
            if re.match(r"o\d|gpt-[5-9]", judge_model)
            else "max_tokens"
        )
        _token_limit = {"none": 50, "low": 1024, "medium": 4096, "high": 16000}[reasoning_effort]
        def judge_call(prompt):
            kwargs = {
                "model": judge_model,
                "messages": [{"role": "user", "content": prompt}],
                _token_key: _token_limit,
            }
            if reasoning_effort != "none":
                kwargs["reasoning_effort"] = reasoning_effort
            resp = client.chat.completions.create(**kwargs)
            return resp.choices[0].message.content or ""
        return judge_call
    else:
        raise ValueError(
            f"Unknown judge backend for model '{judge_model}'. "
            "Use an OpenRouter model (e.g. anthropic/claude-opus-4-7) or an OpenAI model."
        )


def _auto_output_path(judge_model, candidate_model, benchmark_version):
    SCORED_DIR.mkdir(exist_ok=True)
    j = _judge_tag(judge_model)
    c = _candidate_tag(candidate_model)
    return SCORED_DIR / f"judge_{j}__{c}__{benchmark_version}.json"


def _reliability_path(judge_model, benchmark_version):
    j = _sanitize(judge_model)
    return RELIABILITY_DIR / f"{j}__{benchmark_version}.json"


def _load_reliability(path):
    """Load per_question reliability dict from an llm_reliability JSON file.

    Returns dict mapping qnum (str) -> {"question_r": float, ...}, or empty dict.
    """
    path = Path(path)
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("per_question", {})


def _load_context_scored_qnums(benchmark_path):
    """Return qnums (str) that receive human context scoring.

    A question is context-scored only when it is both:
      - frame_type == 'book_context'  (has a book passage to evaluate against)
      - reasoning_type == 'constrained_generation'

    Other book_context reasoning types (character_modeling, topic_sentence) get no
    context score; absent context_fit is treated as an automatic pass downstream.
    world_context/constrained_generation is excluded because there is no book passage
    to judge context against.
    """
    qnums = set()
    with open(benchmark_path, encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            qnum = str(rec.get("question_number", i))
            if (rec.get("frame_type") == "book_context"
                    and rec.get("reasoning_type") == "constrained_generation"):
                qnums.add(qnum)
    return qnums


def _load_benchmark_frames(benchmark_path):
    """Return {qnum: substantive_metadata_frame or metadata_frame}."""
    frames = {}
    with open(benchmark_path, encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            qnum = str(rec.get("question_number", i))
            frames[qnum] = (rec.get("substantive_metadata_frame")
                            or rec.get("metadata_frame", ""))
    return frames


def _write_output(path, data):
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Multi-GT comparison planning
# ---------------------------------------------------------------------------

def _build_comparison_plan(n_gts, rng):
    """Return a list of (gt_index, force_position) pairs for a question.

    force_position is None (random), "A", or "B".

    Rule: if n_gts is even, one GT (chosen at random) is asked twice with
    both positions to guarantee an odd total comparison count (tiebreaker).
    If n_gts is odd, each GT is asked once with a random position.
    """
    if n_gts == 0:
        return []
    if n_gts % 2 == 1:
        return [(i, None) for i in range(n_gts)]
    else:
        doubled = rng.randrange(n_gts)
        plan = []
        for i in range(n_gts):
            if i == doubled:
                plan.append((i, "A"))
                plan.append((i, "B"))
            else:
                plan.append((i, None))
        return plan


# ---------------------------------------------------------------------------
# Core scoring logic
# ---------------------------------------------------------------------------

def run_panel(
    judge_model,
    answers,
    judge_call_factory,
    reliability,
    seed=17,
    start_qnum=None,
    limit=None,
    on_progress=None,
    debug=False,
    frame_overrides=None,
):
    """Score answers against ground truth using an LLM judge (question fit only).

    Args:
        judge_model:        judge model ID string.
        answers:            dict {qnum: {metadata_frame, main_question, ground_truths,
                                        reasoning_type, answer}}.
        judge_call_factory: callable(judge_model_id) -> judge_call_fn.
        reliability:        dict {qnum: {question_r}} from llm_reliability/.
        seed:               int, base RNG seed.
        start_qnum:         str question number to resume from (skip earlier).
        limit:              max questions to process.
        on_progress:        optional callback(qnum, qf_entry).
        debug:              passed to judge_call_factory.

    Returns:
        dict mapping qnum -> {judge, r_q, judgments, scores, gt_positions, gt_indices}.
    """
    qf_scores = {}

    qnums = list(answers.keys())
    if start_qnum is not None:
        try:
            idx = qnums.index(str(start_qnum))
            qnums = qnums[idx:]
        except ValueError:
            pass
    if limit is not None:
        qnums = qnums[:limit]

    jcall = judge_call_factory(judge_model)

    for qnum in qnums:
        entry = answers[qnum]
        rng = random.Random(seed + hash(qnum) % (2 ** 31))

        ground_truths = entry.get("ground_truths") or [entry.get("ground_truth", "")]
        candidate = entry.get("answer", "")
        context = (frame_overrides or {}).get(qnum) or entry.get("metadata_frame", "")
        question = entry.get("main_question", "")
        reasoning_type = entry.get("reasoning_type", "")

        rel = reliability.get(str(qnum), {})
        q_r = rel.get("question_r", None)

        plan = _build_comparison_plan(len(ground_truths), rng)

        norm_candidate = _normalize_for_identity(candidate)
        identity_match = norm_candidate != "" and any(
            _normalize_for_identity(gt) == norm_candidate for gt in ground_truths
        )

        qf_judgments = []
        qf_scores_list = []
        qf_positions = []
        gt_indices = []

        if identity_match:
            for gt_idx, force_pos in plan:
                pos = force_pos if force_pos is not None else rng.choice(("A", "B"))
                qf_judgments.append("tie")
                qf_scores_list.append(1)
                qf_positions.append(pos)
                gt_indices.append(gt_idx)
        else:
            for gt_idx, force_pos in plan:
                gt = ground_truths[gt_idx]
                result = score_one_comparison(
                    jcall,
                    context=context,
                    question=question,
                    reasoning_type=reasoning_type,
                    gt=gt,
                    candidate=candidate,
                    rng=rng,
                    force_gt_position=force_pos,
                )
                raw = result.pop("raw", None)
                if debug and raw:
                    print(f"  [debug] raw judge response: {raw!r}")

                qf_judgments.append(result["question_outcome"])
                qf_scores_list.append(result["question_pass"])
                qf_positions.append(result["gt_position"])
                gt_indices.append(gt_idx)

        effective_judge = "identity" if identity_match else judge_model
        effective_r_q = 0.999 if identity_match else q_r

        qf_entry = {
            "judge": effective_judge,
            "r_q": effective_r_q,
            "judgments": qf_judgments,
            "scores": qf_scores_list,
            "gt_positions": qf_positions,
            "gt_indices": gt_indices,
        }
        qf_scores[qnum] = qf_entry

        if on_progress:
            on_progress(qnum, qf_entry)

    return qf_scores


# ---------------------------------------------------------------------------
# needs_human builder
# ---------------------------------------------------------------------------

def _rebuild_needs_human(output_data):
    """Recompute the needs_human list.

    question_fit: added for any qnum whose r_q is missing or below threshold.
    context_fit:  added for every book_context qnum not yet judged by a human.
    """
    q_thresh = output_data["thresholds"]["question_fit"]
    book_ctx = set(output_data.get("book_context_qnums", []))

    needs = []
    all_qnums = set(output_data["question_fit"]) | book_ctx
    for qnum in sorted(all_qnums):
        aspects = []
        qf = output_data["question_fit"].get(qnum, {})
        if qf.get("r_q") is None or qf["r_q"] <= q_thresh:
            aspects.append("question_fit")
        ctx = output_data["context_fit"].get(qnum, {})
        if qnum in book_ctx and ctx.get("judge") != "human":
            aspects.append("context_fit")
        if aspects:
            needs.append({"qnum": qnum, "aspects": aspects})
    output_data["needs_human"] = needs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Score free-generated answers using an LLM judge (question fit only).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("free_gen_file", metavar="FREE_GEN_FILE",
                        help="JSON output file from free_generation.py")
    parser.add_argument("--judge", required=True, metavar="MODEL_ID",
                        help="Judge model ID (OpenRouter or OpenAI)")
    parser.add_argument("--benchmark", metavar="PATH",
                        default=None,
                        help="Benchmark JSONL (version string + frame_type per question). "
                             "If omitted, inferred from the version suffix in FREE_GEN_FILE "
                             "(e.g. __0.4.json → chronologic_en_0.4.jsonl); "
                             "falls back to chronologic_en_0.2.jsonl.")
    parser.add_argument("--reliability", metavar="PATH", default=None,
                        help="Pre-computed LLM reliability JSON; auto-located from "
                             "llm_reliability/{judge}__{version}.json if omitted")
    parser.add_argument("--openrouter-credentials", metavar="PATH", default=None,
                        dest="openrouter_cred")
    parser.add_argument("--openai-credentials", metavar="PATH", default=None,
                        dest="openai_cred")
    parser.add_argument("--reasoning-effort", metavar="LEVEL", default="none",
                        choices=["none", "low", "medium", "high"],
                        dest="reasoning_effort",
                        help="Reasoning effort for the JUDGE (not the evaluated model)")
    parser.add_argument("--output", metavar="PATH", default=None)
    parser.add_argument("--start", metavar="QNUM", default=None,
                        help="Resume from this question number")
    parser.add_argument("--limit", metavar="N", type=int, default=None)
    parser.add_argument("--seed", metavar="INT", type=int, default=17)
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    with open(args.free_gen_file, encoding="utf-8") as fh:
        free_gen = json.load(fh)
    answers = free_gen.get("answers", {})
    candidate_model = free_gen.get("model", "unknown")
    candidate_reasoning_effort = free_gen.get("reasoning_effort", "none")

    if args.benchmark is None:
        inferred_version = _parse_benchmark_version(args.free_gen_file)
        candidate_path = SCRIPT_DIR.parent / "booksample" / f"chronologic_en_{inferred_version}.jsonl"
        if candidate_path.exists():
            args.benchmark = str(candidate_path)
        else:
            args.benchmark = str(SCRIPT_DIR.parent / "booksample" / "chronologic_en_0.2.jsonl")
            print(f"Warning: could not find {candidate_path}; falling back to 0.2 benchmark.")

    benchmark_version = _parse_benchmark_version(args.benchmark)

    # Load benchmark to determine constrained_generation context-scored questions,
    # and substantive frames.
    print(f"Loading benchmark: {args.benchmark}")
    book_context_qnums = sorted(_load_context_scored_qnums(args.benchmark))
    print(f"  {len(book_context_qnums)} constrained_generation context-scored questions found.")
    bench_frames = _load_benchmark_frames(args.benchmark)

    output_path = (
        Path(args.output) if args.output
        else _auto_output_path(args.judge, candidate_model, benchmark_version)
    )

    reliability_path = (
        Path(args.reliability) if args.reliability
        else _reliability_path(args.judge, benchmark_version)
    )
    reliability = _load_reliability(reliability_path)
    if not reliability:
        print(f"Warning: no reliability data found at {reliability_path}. "
              "All questions will have r_q=null and be added to needs_human.")

    # Load existing scores for resume.
    if output_path.exists():
        with open(output_path, encoding="utf-8") as fh:
            existing = json.load(fh)
        qf_scores = existing.get("question_fit", {})
        ctx_scores = existing.get("context_fit", {})
        # Preserve book_context_qnums from existing file if present; update if changed.
        existing_bctx = existing.get("book_context_qnums", book_context_qnums)
        book_context_qnums = sorted(set(existing_bctx) | set(book_context_qnums))
        print(f"Resuming: {len(qf_scores)} questions already scored.")
        answers = {k: v for k, v in answers.items() if k not in qf_scores}
    else:
        qf_scores = {}
        ctx_scores = {}

    output_data = {
        "judge_model": args.judge,
        "candidate_model": candidate_model,
        "candidate_reasoning_effort": candidate_reasoning_effort,
        "benchmark_version": benchmark_version,
        "reasoning_effort": args.reasoning_effort,
        "reliability_source": str(reliability_path),
        "thresholds": {"question_fit": _QUESTION_FIT_THRESHOLD},
        "question_fit": qf_scores,
        "context_fit": ctx_scores,
        "book_context_qnums": book_context_qnums,
        "needs_human": [],
    }

    def _save_and_exit(sig, frame):
        print("\nInterrupted — saving partial results...")
        _rebuild_needs_human(output_data)
        _write_output(output_path, output_data)
        print(f"Saved to {output_path}")
        sys.exit(0)
    signal.signal(signal.SIGINT, _save_and_exit)

    total = min(len(answers), args.limit) if args.limit else len(answers)
    counter = [0]

    def on_progress(qnum, qf_entry):
        counter[0] += 1
        qf_scores[qnum] = qf_entry
        q_mean = sum(qf_entry["scores"]) / len(qf_entry["scores"]) if qf_entry["scores"] else 0
        print(f"  [{counter[0]}/{total}] qnum={qnum} "
              f"q_mean={q_mean:.2f} r_q={qf_entry['r_q']}")
        if counter[0] % 10 == 0:
            _rebuild_needs_human(output_data)
            _write_output(output_path, output_data)

    def judge_factory(model_id):
        return _make_judge_call(model_id, args.openrouter_cred, args.openai_cred, args.debug,
                                args.reasoning_effort)

    print(f"Scoring {total} questions with judge: {args.judge}")
    run_panel(
        judge_model=args.judge,
        answers=answers,
        judge_call_factory=judge_factory,
        reliability=reliability,
        seed=args.seed,
        start_qnum=args.start,
        limit=args.limit,
        on_progress=on_progress,
        debug=args.debug,
        frame_overrides=bench_frames,
    )

    _rebuild_needs_human(output_data)
    _write_output(output_path, output_data)

    total_scored = len(qf_scores)
    needs_human_count = len(output_data["needs_human"])
    book_ctx_needing_context = sum(
        1 for item in output_data["needs_human"] if "context_fit" in item["aspects"]
    )
    print(f"\nDone. {total_scored} questions scored.")
    print(f"  needs_human: {needs_human_count} questions")
    print(f"    of which {book_ctx_needing_context} need human context_fit judgment")
    print(f"Output: {output_path.resolve()}")


if __name__ == "__main__":
    main()

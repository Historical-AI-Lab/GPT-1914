"""
judge_alpha_reliability_nocontext.py — Compute per-question LLM-judge reliability
(question fit only) for ChronoLogic.

For each benchmark question, compares the ground truth answer against every distractor
(all answer_strings[1:]) in both slot orderings (GT in A, GT in B).

Every distractor contributes to the question-fit denominator.  The distractor type
(from distractor_penalties.txt) controls only whether a *tie* counts as a correct
judgment on question fit:

  "both"     → tie is wrong on question fit
  "question" → tie is wrong on question fit
  "context"  → tie is CORRECT on question fit

A distractor-wins outcome is always wrong regardless of type.

Per-question weight: max(2*r - 1, 0)²

See model_as_judge_overview.md for details.

Usage
-----
  python judge_alpha_reliability_nocontext.py --judge MODEL_ID [options]

  --judge MODEL_ID          Judge model (e.g. anthropic/claude-opus-4-7)
  --benchmark PATH          Benchmark JSONL
                            (default: ../booksample/chronologic_en_0.2.jsonl)
  --openrouter-credentials PATH
                            (default: ../bertclassify/OpenRouterCredentials.txt)
  --openai-credentials PATH (default: ../evalcode/credentials.txt)
  --reasoning-effort LEVEL  Reasoning effort: none, low, medium, high (default: none).
                            Forwarded to OpenRouter's reasoning.effort for Anthropic/Gemini,
                            or to OpenAI's reasoning_effort for o-series/gpt-5 models.
  --output PATH             Override output file path.
  --limit N                 Process only N questions (for testing).
  --seed INT                RNG seed (default: 17; unused here since positions are forced).
  --debug                   Print full judge responses.

Output
------
Written to llm_reliability/{judge}__{version}.json:
{
  "judge_model": "...",
  "benchmark_version": "0.2",
  "per_question": {
    "<qnum>": {
      "question_correct": int,   # serves as k_q for bootstrap Beta posterior
      "question_total":   int,   # serves as n_q for bootstrap Beta posterior
      "question_r":       float,
      "question_invalid": int,
      "question_weight":  float
    }, ...
  }
}

Examples
--------
  # Smoke test (5 questions):
  python judge_alpha_reliability_nocontext.py --judge anthropic/claude-opus-4-7 --limit 5

  # Full run:
  python judge_alpha_reliability_nocontext.py --judge anthropic/claude-opus-4-7
"""

import json
import random
import re
import signal
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from judge_prompts_nocontext import score_one_comparison
from openrouter_client import is_openrouter_model, make_openrouter_client

RELIABILITY_DIR = SCRIPT_DIR / "llm_reliability"
DEFAULT_BENCHMARK = SCRIPT_DIR.parent / "booksample" / "chronologic_en_0.2.jsonl"
PENALTIES_PATH = SCRIPT_DIR / "distractor_penalties.txt"

# ---------------------------------------------------------------------------
# Helpers (exported for judge_beta_reliability_nocontext.py)
# ---------------------------------------------------------------------------

def _sanitize(s):
    return re.sub(r"[^a-zA-Z0-9_\-.]", "_", s)


def _parse_benchmark_version(path):
    name = Path(path).stem
    m = re.search(r'(\d+\.\d+)', name)
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
    if judge_model.startswith("openai/"):
        judge_model = judge_model[len("openai/"):]
    if is_openrouter_model(judge_model):
        from openrouter_client import call_openrouter_chat
        client = make_openrouter_client(openrouter_cred)
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
            "Use an OpenRouter model or an OpenAI model."
        )


def _load_benchmark(path):
    questions = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                questions.append(json.loads(line))
    return questions


def _write_output(path, data):
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def _load_distractor_penalties(path=PENALTIES_PATH):
    """Return {answer_type: 'both'|'question'|'context'} from the TSV file."""
    penalties = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            atype, penalty = parts[0].strip(), parts[1].strip().lower()
            if penalty in ("both", "question", "context"):
                penalties[atype] = penalty
    return penalties


# ---------------------------------------------------------------------------
# Core reliability computation
# ---------------------------------------------------------------------------

def compute_reliability(questions, judge_call, distractor_penalties=None,
                        limit=None, debug=False, on_progress=None):
    """Compute per-question judge reliability (question fit only).

    For each distractor the judge is called *twice*: once with GT in slot A and
    once with GT in slot B.  The penalty type controls whether a tie counts as
    correct on question fit:

      "both" or "question" → tie is wrong on question fit
      "context"            → tie is CORRECT on question fit

    A distractor-wins outcome is always wrong.  Distractors with an unknown
    type are skipped with a one-time warning.

    Args:
        questions:              list of benchmark question dicts.
        judge_call:             callable(user_prompt: str) -> str.
        distractor_penalties:   dict {answer_type: penalty} or None (auto-load).
        limit:                  max questions to process (None = all).
        debug:                  if True, print raw responses.
        on_progress:            optional callback(qnum, per_q_result).

    Returns:
        dict {qnum: {question_correct, question_total, question_r,
                     question_invalid, question_weight}}
    """
    if distractor_penalties is None:
        distractor_penalties = _load_distractor_penalties()

    per_question = {}
    if limit is not None:
        questions = questions[:limit]

    rng = random.Random(42)
    unknown_types = set()

    total = len(questions)
    for i, q in enumerate(questions):
        qnum = str(q.get("question_number", i))
        answer_strings = q.get("answer_strings", [])
        answer_types = q.get("answer_types", [])
        context = q.get("metadata_frame", "")
        question_text = q.get("main_question", "")
        reasoning_type = q.get("reasoning_type", "")

        gts = [s for s, t in zip(answer_strings, answer_types) if t == "ground_truth"]
        distractor_pairs = [
            (s, t) for s, t in zip(answer_strings, answer_types) if t != "ground_truth"
        ]
        if not gts and answer_strings:
            gts = [answer_strings[0]]
            distractor_pairs = list(zip(answer_strings[1:], answer_types[1:]))

        q_correct = q_total = 0
        q_invalid = 0

        for distractor, atype in distractor_pairs:
            penalty = distractor_penalties.get(atype)
            if penalty is None:
                if atype not in unknown_types:
                    print(f"  [warning] unknown distractor type '{atype}' — skipping")
                    unknown_types.add(atype)
                continue

            # Tie is correct on question fit only when the distractor doesn't
            # penalize question fit (i.e., its penalty is "context").
            q_tie_ok = (penalty == "context")

            for gt in gts:
                for gt_pos in ("A", "B"):
                    result = score_one_comparison(
                        judge_call,
                        context=context,
                        question=question_text,
                        reasoning_type=reasoning_type,
                        gt=gt,
                        candidate=distractor,
                        rng=rng,
                        force_gt_position=gt_pos,
                    )
                    if debug:
                        raw = result.get("raw", "")
                        print(f"  [debug] q={qnum} gt_pos={gt_pos} type={atype} "
                              f"gt={gt[:40]!r} distractor={distractor[:40]!r}")
                        print(f"  [debug] response: {raw!r}")

                    q_outcome = result["question_outcome"]
                    q_total += 1

                    if q_outcome == "loss" or (q_outcome == "tie" and q_tie_ok):
                        q_correct += 1
                    elif q_outcome == "invalid":
                        q_invalid += 1

        q_r = q_correct / q_total if q_total > 0 else 0.0
        w_q = max(2 * q_r - 1, 0) ** 2

        entry = {
            "question_correct": q_correct,
            "question_total":   q_total,
            "question_r":       round(q_r, 4),
            "question_invalid": q_invalid,
            "question_weight":  round(w_q, 4),
        }
        per_question[qnum] = entry

        invalid_note = f" q_invalid={q_invalid}" if q_invalid else ""
        print(f"  [{i+1}/{total}] qnum={qnum} "
              f"q_r={q_r:.3f} ({q_correct}/{q_total})"
              + invalid_note)

        if on_progress:
            on_progress(qnum, entry)

    if unknown_types:
        print(f"\n[warning] {len(unknown_types)} unknown distractor type(s) were skipped: "
              f"{sorted(unknown_types)}")

    return per_question


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Compute per-question LLM-judge reliability (question fit only).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--judge", required=True, metavar="MODEL_ID",
                        help="Judge model ID (OpenRouter or OpenAI)")
    parser.add_argument("--benchmark", metavar="PATH",
                        default=str(DEFAULT_BENCHMARK))
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

    args = parser.parse_args()

    benchmark_version = _parse_benchmark_version(args.benchmark)
    output_path = (
        Path(args.output) if args.output
        else RELIABILITY_DIR / f"{_sanitize(args.judge)}__{benchmark_version}.json"
    )

    existing_per_question = {}
    if output_path.exists():
        with open(output_path, encoding="utf-8") as fh:
            existing = json.load(fh)
        existing_per_question = existing.get("per_question", {})
        existing_effort = existing.get("reasoning_effort")
        if existing_effort is not None and existing_effort != args.reasoning_effort:
            sys.exit(
                f"ERROR: existing file {output_path} was produced with "
                f"reasoning_effort={existing_effort!r}, but this run uses "
                f"{args.reasoning_effort!r}. Pass --output PATH to write to a "
                f"different file."
            )
        print(f"Resuming from existing file: {output_path}")
        print(f"  {len(existing_per_question)} questions already scored "
              f"(pass --output PATH to a new file to force a fresh run).")
    else:
        print(f"Writing reliability output to: {output_path}")

    distractor_penalties = _load_distractor_penalties()
    print(f"Loaded {len(distractor_penalties)} distractor penalty entries from "
          f"{PENALTIES_PATH.name}")

    questions = _load_benchmark(args.benchmark)
    print(f"Loaded {len(questions)} questions from {args.benchmark}")

    if existing_per_question:
        before = len(questions)
        questions = [
            q for i, q in enumerate(questions)
            if str(q.get("question_number", i)) not in existing_per_question
        ]
        print(f"  Skipping {before - len(questions)} already-completed; "
              f"{len(questions)} remaining.")

    judge_call = _make_judge_call(
        args.judge, args.openrouter_cred, args.openai_cred, args.debug,
        args.reasoning_effort,
    )

    output_data = {
        "judge_model": args.judge,
        "reasoning_effort": args.reasoning_effort,
        "benchmark_version": benchmark_version,
        "per_question": dict(existing_per_question),
    }

    def _save_and_exit(sig, frame):
        print("\nInterrupted — saving partial results...")
        _write_output(output_path, output_data)
        print(f"Saved to {output_path}")
        sys.exit(0)
    signal.signal(signal.SIGINT, _save_and_exit)

    def on_progress(qnum, entry):
        output_data["per_question"][qnum] = entry
        if len(output_data["per_question"]) % 10 == 0:
            _write_output(output_path, output_data)

    print(f"Computing reliability with judge: {args.judge}")
    try:
        compute_reliability(
            questions, judge_call,
            distractor_penalties=distractor_penalties,
            limit=args.limit, debug=args.debug, on_progress=on_progress,
        )
    except Exception as exc:
        print(f"\nError during scoring: {type(exc).__name__}: {exc}")
        print(f"Saving partial results "
              f"({len(output_data['per_question'])} questions) to {output_path} ...")
        _write_output(output_path, output_data)
        print(f"Saved. Re-run the same command to resume.")
        raise

    _write_output(output_path, output_data)
    all_per_question = output_data["per_question"]
    n = len(all_per_question)
    if n:
        mean_q_r = sum(v["question_r"]      for v in all_per_question.values()) / n
        mean_q_w = sum(v["question_weight"] for v in all_per_question.values()) / n
        print(f"\nDone. {n} questions evaluated.")
        print(f"  mean question_r:      {mean_q_r:.3f}")
        print(f"  mean question_weight: {mean_q_w:.3f}")
    print(f"Output: {output_path.resolve()}")


if __name__ == "__main__":
    main()

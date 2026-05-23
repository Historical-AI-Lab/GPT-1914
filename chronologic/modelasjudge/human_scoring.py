"""
human_scoring.py — Interactive human judging for questions flagged by judge_scoring.

When judge_scoring.py finds that the LLM judge's per-question reliability is
below the threshold (0.65) for question_fit or context_fit, it records those
questions in a `needs_human` list.  This script works through that list
interactively, replacing each low-reliability LLM score with a human judgment.

Judgment vocabulary mirrors judge_scoring: the human is asked whether the
model answer ties the ground truth.
  - "y" / yes  → judgment "tie",  score 1
  - "n" / no   → judgment "GT",   score 0
There is no "model wins" outcome: the human knows which answer is ground truth
and has no reason to prefer anything over it.

Every judgment is appended to a cumulative cross-model log
(human_judgments.jsonl) so future sessions can show precedents for the same
question.

Usage
-----
  python human_scoring.py JUDGE_FILE [options]

  JUDGE_FILE        scored_answers/judge_{judge}__{candidate}__{version}.json
  --free-gen PATH   Free-gen JSON for displaying question context; auto-located
                    from generated_answers/free_gen_{candidate}__{version}.json
                    if omitted.
  --log PATH        Cumulative human-judgment log
                    (default: human_judgments.jsonl in this directory)
  --output PATH     Override output path (default: JUDGE_FILE with _human.json)
  --reliability F   Provide human_reliability without an interactive prompt.
  --resume          If output already exists, skip (qnum, aspect) pairs whose
                    judge is already "human"; only ask for remaining ones.

Output
------
Written to scored_answers/judge_{judge}__{candidate}__{version}_human.json.
Schema is identical to the input judge file, plus:
  "human_reliability": <float>
For each re-judged (qnum, aspect), the entry is overwritten with:
  {"judge": "human", "r_q": <human_reliability>,
   "judgments": ["tie"|"GT"], "scores": [1|0],
   "gt_positions": [null], "gt_indices": [null]}

Examples
--------
  # Full interactive run
  python human_scoring.py \\
      scored_answers/judge_anthropic_claude-sonnet-4-6__gpt-4.1-2025-04-14__0.2.json

  # Non-interactive (supply reliability, useful for tests / CI)
  python human_scoring.py JUDGE_FILE --reliability 0.9
"""

import argparse
import json
import re
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from naming import candidate_tag as _candidate_tag, sanitize as _sanitize

GENERATED_DIR = SCRIPT_DIR / "generated_answers"
DEFAULT_LOG = SCRIPT_DIR / "human_judgments.jsonl"

_ASPECT_LABELS = {
    "question_fit": "Question fit",
    "context_fit": "Context fit",
}

# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def _auto_free_gen(judge_path: Path) -> Path:
    """Derive free_gen path from judge filename.

    E.g.  judge_anthropic_claude-sonnet-4-6__gpt-4.1-2025-04-14__0.2.json
          →  generated_answers/free_gen_gpt-4.1-2025-04-14__0.2.json
    """
    stem = judge_path.stem  # strip .json
    # Remove optional _human suffix
    stem = re.sub(r"_human$", "", stem)
    # Pattern: judge_{judge}__{candidate}__{version}
    m = re.match(r"judge_.+__(.+__\d+\.\d+)$", stem)
    if m:
        candidate_version = m.group(1)
        return GENERATED_DIR / f"free_gen_{candidate_version}.json"
    raise ValueError(
        f"Cannot derive free_gen path from judge filename: {judge_path.name}\n"
        "Use --free-gen to specify it explicitly."
    )


def _auto_output(judge_path: Path) -> Path:
    stem = judge_path.stem
    stem = re.sub(r"_human$", "", stem)  # idempotent
    return judge_path.parent / f"{stem}_human.json"


def _load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def _load_log(log_path: Path) -> list:
    """Load all records from the cumulative human_judgments.jsonl."""
    if not log_path.exists():
        return []
    records = []
    with open(log_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


def _append_log(log_path: Path, record: dict) -> None:
    log_path.parent.mkdir(exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

_SEP = "-" * 70


def _print_question_context(qnum: str, free_gen_answers: dict, judge_data: dict) -> None:
    entry = free_gen_answers.get(str(qnum), {})
    print(f"\n{'=' * 70}")
    print(f"Question {qnum}")
    print(_SEP)
    meta = entry.get("metadata_frame", "(metadata not available)")
    print(f"Context:\n{meta}")
    print(_SEP)
    q = entry.get("main_question", judge_data.get("question", "(question not available)"))
    print(f"Question:\n{q}")
    print(_SEP)
    gts = entry.get("ground_truths", [])
    if gts:
        print("Ground truth answer(s):")
        for i, gt in enumerate(gts):
            print(f"  [{i}] {gt}")
    else:
        print("Ground truth: (not available)")
    print(_SEP)
    candidate = entry.get("answer", "(candidate answer not available)")
    print(f"Candidate answer:\n{candidate}")


def _print_precedents(log_records: list, qnum: str, aspect: str) -> None:
    matches = [
        r for r in log_records
        if str(r.get("qnum")) == str(qnum) and r.get("aspect") == aspect
    ]
    recent = matches[-5:] if len(matches) > 5 else matches
    if not recent:
        print("  (no prior judgments for this question/aspect)")
        return
    print(f"  Prior judgments ({len(matches)} total; showing most recent {len(recent)}):")
    for r in recent:
        score_word = "TIE (1)" if r.get("score") == 1 else "GT wins (0)"
        model = r.get("candidate_model", "?")
        reason = r.get("reason", "").strip() or "(no reason)"
        print(f"    [{score_word}] {model}: {reason}")


# ---------------------------------------------------------------------------
# Interactive prompt
# ---------------------------------------------------------------------------

def _prompt_reliability() -> float:
    while True:
        raw = input("\nEnter human reliability (float in [0,1]): ").strip()
        try:
            v = float(raw)
            if 0.0 <= v <= 1.0:
                return v
        except ValueError:
            pass
        print("  Please enter a number between 0 and 1.")


def _prompt_score(aspect_label: str) -> tuple[int, str]:
    """Ask whether the model answer ties ground truth.  Returns (score, reason)."""
    print(f"\n  [{aspect_label}]")
    print("  Does the model answer tie ground truth? (y = tie/1, n = GT wins/0)")
    while True:
        raw = input("  Score [y/n]: ").strip().lower()
        if raw in ("y", "yes", "1"):
            score = 1
            break
        elif raw in ("n", "no", "0"):
            score = 0
            break
        else:
            print("  Please enter y or n.")
    reason = input("  Reason (optional): ").strip()
    return score, reason


# ---------------------------------------------------------------------------
# needs_human recompute (mirrors judge_scoring._rebuild_needs_human)
# ---------------------------------------------------------------------------

def _rebuild_needs_human(data: dict) -> None:
    q_thresh = data.get("thresholds", {}).get("question_fit", 0.65)
    ctx_thresh = data.get("thresholds", {}).get("context_fit", 0.65)
    needs = []
    all_qnums = set(data.get("question_fit", {})) | set(data.get("context_fit", {}))
    for qnum in sorted(all_qnums):
        aspects = []
        qf = data.get("question_fit", {}).get(qnum, {})
        if qf.get("judge") != "human":
            r = qf.get("r_q")
            if r is None or r <= q_thresh:
                aspects.append("question_fit")
        ctx = data.get("context_fit", {}).get(qnum, {})
        if ctx.get("judge") != "human":
            r = ctx.get("r_q")
            if r is None or r <= ctx_thresh:
                aspects.append("context_fit")
        if aspects:
            needs.append({"qnum": qnum, "aspects": aspects})
    data["needs_human"] = needs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Interactive human judging for questions flagged by judge_scoring.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("judge_file", metavar="JUDGE_FILE",
                        help="Output file from judge_scoring.py")
    parser.add_argument("--free-gen", metavar="PATH", default=None, dest="free_gen",
                        help="Free-gen JSON; auto-located if omitted")
    parser.add_argument("--log", metavar="PATH", default=str(DEFAULT_LOG),
                        help=f"Cumulative judgment log (default: {DEFAULT_LOG})")
    parser.add_argument("--output", metavar="PATH", default=None)
    parser.add_argument("--reliability", metavar="F", type=float, default=None,
                        help="Human reliability value; skips interactive prompt")
    parser.add_argument("--resume", action="store_true",
                        help="Skip (qnum, aspect) pairs already marked judge=human")

    args = parser.parse_args()

    judge_path = Path(args.judge_file)
    if not judge_path.exists():
        print(f"Error: judge file not found: {judge_path}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) if args.output else _auto_output(judge_path)

    # If resume mode and output exists, start from that file
    if args.resume and output_path.exists():
        print(f"Resuming from: {output_path}")
        data = _load_json(output_path)
    else:
        data = _load_json(judge_path)

    needs_human = data.get("needs_human", [])
    if not needs_human:
        print("needs_human is empty — nothing to judge. Exiting.")
        sys.exit(0)

    # Load free_gen for display
    try:
        free_gen_path = Path(args.free_gen) if args.free_gen else _auto_free_gen(judge_path)
        free_gen = _load_json(free_gen_path)
        free_gen_answers = free_gen.get("answers", {})
    except (ValueError, FileNotFoundError) as exc:
        print(f"Warning: could not load free_gen file ({exc}). "
              "Question context will not be displayed.", file=sys.stderr)
        free_gen_answers = {}

    candidate_model = data.get("candidate_model", "unknown")
    replaced_judge = data.get("judge_model", "unknown")
    log_path = Path(args.log)
    log_records = _load_log(log_path)

    # Get human reliability
    if args.reliability is not None:
        human_reliability = args.reliability
        print(f"Using human_reliability={human_reliability}")
    else:
        human_reliability = _prompt_reliability()

    data["human_reliability"] = human_reliability

    # Save-on-interrupt
    def _save_and_exit(sig, frame):
        print("\nInterrupted — saving partial results...")
        _rebuild_needs_human(data)
        _write_json(output_path, data)
        print(f"Saved to {output_path}")
        sys.exit(0)
    signal.signal(signal.SIGINT, _save_and_exit)

    # Filter needs_human if resuming (skip already-judged)
    pending = needs_human
    if args.resume:
        pending = []
        for item in needs_human:
            qnum = item["qnum"]
            remaining_aspects = []
            for asp in item["aspects"]:
                entry = data.get(asp, {}).get(qnum, {})
                if entry.get("judge") != "human":
                    remaining_aspects.append(asp)
            if remaining_aspects:
                pending.append({"qnum": qnum, "aspects": remaining_aspects})

    print(f"\n{len(pending)} question(s) need human judgment.")

    for i, item in enumerate(pending, 1):
        qnum = item["qnum"]
        aspects = item["aspects"]

        print(f"\n--- Question {i}/{len(pending)} ---")
        _print_question_context(qnum, free_gen_answers, data)

        for aspect in aspects:
            aspect_label = _ASPECT_LABELS.get(aspect, aspect)
            print(f"\n{_SEP}")
            print(f"Aspect: {aspect_label}")
            _print_precedents(log_records, qnum, aspect)

            score, reason = _prompt_score(aspect_label)
            judgment = "tie" if score == 1 else "GT"

            # Update judge file entry
            data.setdefault(aspect, {})[qnum] = {
                "judge": "human",
                "r_q": human_reliability,
                "judgments": [judgment],
                "scores": [score],
                "gt_positions": [None],
                "gt_indices": [None],
            }

            # Append to cumulative log
            log_record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "qnum": str(qnum),
                "aspect": aspect,
                "candidate_model": candidate_model,
                "candidate_answer": free_gen_answers.get(str(qnum), {}).get("answer", ""),
                "score": score,
                "judgment": judgment,
                "reason": reason,
                "human_reliability": human_reliability,
                "replaced_judge": replaced_judge,
            }
            _append_log(log_path, log_record)
            log_records.append(log_record)

        # Save after each question
        _rebuild_needs_human(data)
        _write_json(output_path, data)

    _rebuild_needs_human(data)
    _write_json(output_path, data)

    remaining = len(data.get("needs_human", []))
    print(f"\nDone. Judged {len(pending)} question(s).")
    if remaining:
        print(f"  Still needs_human: {remaining} (aspects not yet covered)")
    else:
        print("  needs_human is now empty — ready for score_calculation.")
    print(f"Output: {output_path.resolve()}")
    print(f"Log: {log_path.resolve()}")


if __name__ == "__main__":
    main()

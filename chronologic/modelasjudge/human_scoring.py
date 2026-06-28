"""
human_scoring.py — Interactive human judging for questions flagged by judge_scoring.

This script handles two kinds of human judgment:

1. **Question fit re-judging**: when judge_scoring_nocontext.py finds the LLM
   judge's per-question reliability is below 0.65 for question_fit, it records
   those questions in `needs_human`.  This script replaces the low-reliability
   LLM score with a human judgment.

2. **Context fit judging**: all questions with frame_type "book_context" need a
   human context judgment regardless of reliability.  judge_scoring_nocontext.py
   records them in needs_human with aspect "context_fit".  The human judges
   whether the candidate answer is something the specified source might say.

Judgment vocabulary:
  - "y" / yes  → judgment "tie",  score 1
  - "n" / no   → judgment "GT",   score 0
There is no "model wins" outcome: the human knows which answer is ground truth.

Multiple human judges can score the same file.  Each judge's rating is stored
under `human_judges[judge_id]` within each entry.  The first judge's rating
becomes the representative top-level value that score_calculation.py reads;
subsequent judges extend `human_judges` without overwriting it.

Blinding: when two judge files are provided, questions are interleaved in random
order and model identity is never displayed.  Precedents from other models are
shown with the label "another model".

Every judgment is appended to a cumulative cross-model log
(human_judgments.jsonl) so future sessions can show precedents and support
inter-rater reliability analysis.

Usage
-----
  python human_scoring.py JUDGE_FILE [JUDGE_FILE2] [options]

  JUDGE_FILE        scored_answers/judge_{judge}__{candidate}__{version}.json
  JUDGE_FILE2       Optional second judge file; enables blinded dual-file mode.

  --judge-id ID     Identifier for this human judge (default: "human").
  --free-gen PATH   free_gen JSON for JUDGE_FILE; auto-located if omitted.
  --free-gen-2 PATH free_gen JSON for JUDGE_FILE2; auto-located if omitted.
  --log PATH        Cumulative human-judgment log
                    (default: human_judgments.jsonl in this directory)
  --output PATH     Override output path for JUDGE_FILE
                    (default: JUDGE_FILE with _human suffix)
  --output-2 PATH   Override output path for JUDGE_FILE2.
  --reliability F       Provide human_reliability without an interactive prompt.
  --resume              Skip (qnum, aspect) pairs already judged by this --judge-id.
  --show-precedents     Display up to 3 prior judgments from other models before
                        each prompt. Off by default; judgments are always logged.
  --seed N              Random seed for reproducible shuffle (testing).

Output
------
Written to scored_answers/judge_{judge}__{candidate}__{version}_human.json.
Schema is identical to the input judge file, with each (qnum, aspect) entry
extended by a `human_judges` sub-dict:

  {
    "judge": "human",
    "r_q": <first_judge_reliability>,
    "judgments": ["tie"|"GT"],
    "scores": [1|0],
    "gt_positions": [null],
    "gt_indices": [null],
    "human_judges": {
      "alice": {"score": 1, "judgment": "tie", "reason": "...",
                "r_q": 0.9, "timestamp": "..."},
      "bob":   {"score": 0, "judgment": "GT",  "reason": "...",
                "r_q": 0.9, "timestamp": "..."}
    }
  }

The first judge recorded sets the representative top-level fields that
score_calculation.py consumes; later judges only extend `human_judges`.

Examples
--------
  # Single file, named judge
  python human_scoring.py \\
      scored_answers/judge_anthropic_claude-sonnet-4-6__gpt-5.4__0.2.json \\
      --judge-id alice

  # Blinded dual-file, non-interactive reliability
  python human_scoring.py \\
      scored_answers/judge_..._A__0.2.json \\
      scored_answers/judge_..._B__0.2.json \\
      --judge-id bob --reliability 0.9

  # Second judge resumes onto same output files
  python human_scoring.py judge_..._A__0.2.json judge_..._B__0.2.json \\
      --judge-id carol --resume
"""

import argparse
import json
import random
import re
import signal
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from naming import candidate_tag as _candidate_tag

GENERATED_DIR = SCRIPT_DIR / "generated_answers"
DEFAULT_LOG = SCRIPT_DIR / "human_judgments.jsonl"

_ASPECT_LABELS = {
    "question_fit": "Question fit",
    "context_fit": "Context fit",
}

# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def _free_gen_from_meta(candidate_model: str, version: str,
                         effort: str = "none") -> Optional[Path]:
    """Locate free_gen JSON from JSON-derived metadata rather than filename.

    Tries in order:
      1. free_gen_{ctag}__{version}.json
      2. free_gen_{ctag}_{effort}__{version}.json
      3. glob free_gen_{ctag}*__{version}.json (single or effort-matched)
    Returns None if nothing found.
    """
    ctag = _candidate_tag(candidate_model)
    direct = [
        GENERATED_DIR / f"free_gen_{ctag}__{version}.json",
        GENERATED_DIR / f"free_gen_{ctag}_{effort}__{version}.json",
    ]
    for p in direct:
        if p.exists():
            return p
    matches = sorted(GENERATED_DIR.glob(f"free_gen_{ctag}*__{version}*.json"))
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        for m in matches:
            if effort and f"_{effort}__" in m.stem:
                return m
        return matches[0]
    return None


def _auto_free_gen(judge_path: Path, data: dict) -> Path:
    """Derive free_gen path, preferring JSON metadata over filename parsing."""
    candidate_model = data.get("candidate_model")
    version = data.get("benchmark_version")
    effort = data.get("candidate_reasoning_effort", "none")

    if candidate_model and version:
        p = _free_gen_from_meta(candidate_model, version, effort)
        if p:
            return p

    # Fallback: filename parsing (for non-anonymized inputs).
    # The stem may now have effort tokens: judge_J__C__ver__c-X__j-Y[_human]
    stem = re.sub(r"_human$", "", judge_path.stem)
    m = re.match(r"judge_.+__(.+)__(\d+\.\d+)(?:__.*)?$", stem)
    if m:
        candidate_tag_str = m.group(1)
        ver = m.group(2)
        p = GENERATED_DIR / f"free_gen_{candidate_tag_str}__{ver}.json"
        if p.exists():
            return p
    raise ValueError(
        f"Cannot locate free_gen for {judge_path.name} "
        f"(candidate_model={candidate_model!r}, version={version!r}). "
        "Use --free-gen to specify it explicitly."
    )


def _auto_output(judge_path: Path) -> Path:
    stem = re.sub(r"_human$", "", judge_path.stem)  # idempotent
    return judge_path.parent / f"{stem}_human.json"


def _infer_candidate_model(judge_path: Path) -> Optional[str]:
    """Infer candidate_model from filename.

    Handles both old format (judge_J__C__ver.json) and new format
    (judge_J__C__ver__c-X__j-Y.json).
    """
    stem = re.sub(r"_human$", "", judge_path.stem)
    m = re.match(r"judge_.+__(.+)__\d+\.\d+(?:__.*)?$", stem)
    return m.group(1) if m else None


def _load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def _load_log(log_path: Path) -> list:
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
# Migration helpers
# ---------------------------------------------------------------------------

def _migrate_entry(entry: dict, default_judge_id: str = "human") -> None:
    """Wrap a legacy single-human entry into the human_judges sub-dict in place.

    If the entry has judge="human" but no human_judges key, promote the
    existing top-level fields into human_judges[default_judge_id].
    """
    if entry.get("judge") != "human":
        return
    if "human_judges" in entry:
        return
    entry["human_judges"] = {
        default_judge_id: {
            "score": entry["scores"][0] if entry.get("scores") else None,
            "judgment": (entry["judgments"][0]
                         if entry.get("judgments") else None),
            "reason": "",
            "r_q": entry.get("r_q"),
            "timestamp": None,
        }
    }


def _migrate_data(data: dict, default_judge_id: str = "human") -> None:
    """Migrate all entries in a judge file to the multi-judge schema."""
    for aspect in ("question_fit", "context_fit"):
        for entry in data.get(aspect, {}).values():
            _migrate_entry(entry, default_judge_id)


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

_SEP = "-" * 70


def _print_question_context(qnum: str, free_gen_answers: dict,
                              judge_data: dict) -> None:
    entry = free_gen_answers.get(str(qnum), {})
    print(f"\n{'=' * 70}")
    print(f"Question {qnum}")
    print(_SEP)
    meta = entry.get("metadata_frame", "(metadata not available)")
    print(f"Context:\n{meta}")
    print(_SEP)
    q = entry.get("main_question",
                  judge_data.get("question", "(question not available)"))
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


def _print_precedents(log_records: list, qnum: str, aspect: str,
                       current_model: str) -> None:
    """Print precedents, excluding same-model rows and hiding model identity."""
    matches = [
        r for r in log_records
        if str(r.get("qnum")) == str(qnum)
        and r.get("aspect") == aspect
        and r.get("candidate_model") != current_model
    ]
    recent = matches[-3:] if len(matches) > 3 else matches
    if not recent:
        print("  (no prior judgments for this question/aspect from other models)")
        return
    print(f"  Prior judgments ({len(matches)} total; showing most recent"
          f" {len(recent)}):")
    for r in recent:
        score_word = "TIE (1)" if r.get("score") == 1 else "GT wins (0)"
        reason = r.get("reason", "").strip() or "(no reason)"
        print(f"    [{score_word}] another model: {reason}")


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
# needs_human recompute + per-judge pending
# ---------------------------------------------------------------------------

def _rebuild_needs_human(data: dict) -> None:
    """Recompute needs_human — aspect is done once any human entry exists."""
    q_thresh = data.get("thresholds", {}).get("question_fit", 0.65)
    book_ctx = set(str(q) for q in data.get("book_context_qnums", []))

    needs = []
    all_qnums = set(data.get("question_fit", {})) | book_ctx
    for qnum in sorted(all_qnums, key=lambda x: int(x) if x.isdigit() else x):
        aspects = []
        qf = data.get("question_fit", {}).get(str(qnum), {})
        if qf.get("judge") != "human":
            r = qf.get("r_q")
            if r is None or r <= q_thresh:
                aspects.append("question_fit")
        ctx = data.get("context_fit", {}).get(str(qnum), {})
        if str(qnum) in book_ctx and ctx.get("judge") != "human":
            aspects.append("context_fit")
        if aspects:
            needs.append({"qnum": str(qnum), "aspects": aspects})
    data["needs_human"] = needs


def _pending_for_judge(data: dict, judge_id: str) -> list[tuple[str, str]]:
    """Return (qnum, aspect) pairs pending for this specific judge.

    A pair is pending if the original human-judging gate holds AND judge_id
    has not yet scored it.

    question_fit gate: entry already upgraded to judge="human" by a prior judge,
                       OR original LLM r_q is missing/below threshold.
    context_fit gate:  qnum is in book_context_qnums.
    """
    q_thresh = data.get("thresholds", {}).get("question_fit", 0.65)
    book_ctx = set(str(q) for q in data.get("book_context_qnums", []))
    pending = []

    all_qnums = set(data.get("question_fit", {})) | book_ctx
    for qnum in sorted(all_qnums, key=lambda x: int(x) if x.isdigit() else x):
        qnum = str(qnum)
        qf = data.get("question_fit", {}).get(qnum, {})
        qf_gate = (
            qf.get("judge") == "human"  # prior human already scored it
            or qf.get("r_q") is None
            or qf.get("r_q", 1.0) <= q_thresh
        )
        if qf_gate and judge_id not in qf.get("human_judges", {}):
            pending.append((qnum, "question_fit"))

        if qnum in book_ctx:
            ctx = data.get("context_fit", {}).get(qnum, {})
            if judge_id not in ctx.get("human_judges", {}):
                pending.append((qnum, "context_fit"))

    return pending


# ---------------------------------------------------------------------------
# File context
# ---------------------------------------------------------------------------

@dataclass
class FileCtx:
    judge_path: Path
    output_path: Path
    data: dict
    free_gen_answers: dict
    candidate_model: str
    candidate_reasoning_effort: str


def _load_file_ctx(judge_path: Path, output_path: Path,
                    free_gen_override: Optional[str],
                    resume: bool, judge_id: str) -> FileCtx:
    """Load a judge file, apply migration, set up for this judge session."""
    if resume and output_path.exists():
        print(f"Resuming from: {output_path}")
        data = _load_json(output_path)
    else:
        data = _load_json(judge_path)

    # Defensive: ensure candidate_model is present
    if not data.get("candidate_model"):
        inferred = _infer_candidate_model(judge_path)
        if inferred:
            data["candidate_model"] = inferred
            print(f"Warning: inferred candidate_model={inferred!r} from filename.",
                  file=sys.stderr)
        else:
            data["candidate_model"] = "unknown"

    candidate_model = data["candidate_model"]
    effort = data.get("candidate_reasoning_effort", "none")

    _migrate_data(data, default_judge_id="human")

    free_gen_answers: dict = {}
    try:
        fg_path = (Path(free_gen_override) if free_gen_override
                   else _auto_free_gen(judge_path, data))
        fg = _load_json(fg_path)
        free_gen_answers = fg.get("answers", {})
    except (ValueError, FileNotFoundError) as exc:
        print(f"Warning: could not load free_gen ({exc}). "
              "Question context will not be displayed.", file=sys.stderr)

    return FileCtx(
        judge_path=judge_path,
        output_path=output_path,
        data=data,
        free_gen_answers=free_gen_answers,
        candidate_model=candidate_model,
        candidate_reasoning_effort=effort,
    )


# ---------------------------------------------------------------------------
# Core recording
# ---------------------------------------------------------------------------

def _record_judgment(ctx: FileCtx, qnum: str, aspect: str,
                      judge_id: str, score: int, reason: str,
                      human_reliability: float,
                      log_path: Path, log_records: list) -> None:
    """Write judgment into the file's data and append to the cumulative log."""
    judgment = "tie" if score == 1 else "GT"
    ts = datetime.now(timezone.utc).isoformat()

    entry = ctx.data.setdefault(aspect, {}).setdefault(str(qnum), {})

    entry.setdefault("human_judges", {})[judge_id] = {
        "score": score,
        "judgment": judgment,
        "reason": reason,
        "r_q": human_reliability,
        "timestamp": ts,
    }

    # Set representative top-level only for the first human judge
    if entry.get("judge") != "human":
        entry["judge"] = "human"
        entry["r_q"] = human_reliability
        entry["judgments"] = [judgment]
        entry["scores"] = [score]
        entry["gt_positions"] = [None]
        entry["gt_indices"] = [None]

    log_record = {
        "timestamp": ts,
        "qnum": str(qnum),
        "aspect": aspect,
        "judge_id": judge_id,
        "candidate_model": ctx.candidate_model,
        "candidate_reasoning_effort": ctx.candidate_reasoning_effort,
        "candidate_answer": ctx.free_gen_answers.get(str(qnum), {}).get("answer", ""),
        "score": score,
        "judgment": judgment,
        "reason": reason,
        "human_reliability": human_reliability,
        "replaced_judge": ctx.data.get("judge_model", "unknown"),
    }
    _append_log(log_path, log_record)
    log_records.append(log_record)


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
                        help="First scored judge file (scored_answers/judge_*.json)")
    parser.add_argument("judge_file_2", metavar="JUDGE_FILE2", nargs="?",
                        default=None,
                        help="Optional second judge file — enables blinded dual-file mode")
    parser.add_argument("--judge-id", metavar="ID", default="human",
                        dest="judge_id",
                        help="Identifier for this human judge (default: 'human')")
    parser.add_argument("--free-gen", metavar="PATH", default=None,
                        dest="free_gen",
                        help="free_gen JSON for JUDGE_FILE; auto-located if omitted")
    parser.add_argument("--free-gen-2", metavar="PATH", default=None,
                        dest="free_gen_2",
                        help="free_gen JSON for JUDGE_FILE2; auto-located if omitted")
    parser.add_argument("--log", metavar="PATH", default=str(DEFAULT_LOG),
                        help=f"Cumulative judgment log (default: {DEFAULT_LOG})")
    parser.add_argument("--output", metavar="PATH", default=None,
                        help="Override output path for JUDGE_FILE")
    parser.add_argument("--output-2", metavar="PATH", default=None,
                        dest="output_2",
                        help="Override output path for JUDGE_FILE2")
    parser.add_argument("--reliability", metavar="F", type=float, default=None,
                        help="Human reliability value; skips interactive prompt")
    parser.add_argument("--resume", action="store_true",
                        help="Skip (qnum, aspect) pairs already judged by --judge-id")
    parser.add_argument("--show-precedents", action="store_true",
                        dest="show_precedents",
                        help="Display up to 3 prior judgments from other models "
                             "before each prompt (off by default; always logged)")
    parser.add_argument("--seed", metavar="N", type=int, default=None,
                        help="Random seed for reproducible shuffle (testing)")

    args = parser.parse_args()

    judge_path1 = Path(args.judge_file)
    if not judge_path1.exists():
        print(f"Error: judge file not found: {judge_path1}", file=sys.stderr)
        sys.exit(1)

    output_path1 = Path(args.output) if args.output else _auto_output(judge_path1)
    ctx1 = _load_file_ctx(judge_path1, output_path1, args.free_gen,
                           args.resume, args.judge_id)
    contexts = [ctx1]

    if args.judge_file_2:
        judge_path2 = Path(args.judge_file_2)
        if not judge_path2.exists():
            print(f"Error: JUDGE_FILE2 not found: {judge_path2}", file=sys.stderr)
            sys.exit(1)
        output_path2 = (Path(args.output_2) if args.output_2
                        else _auto_output(judge_path2))
        ctx2 = _load_file_ctx(judge_path2, output_path2, args.free_gen_2,
                               args.resume, args.judge_id)
        contexts.append(ctx2)
        print(f"\nDual-file mode: {len(contexts)} model files (blinded).")

    log_path = Path(args.log)
    log_records = _load_log(log_path)

    if args.reliability is not None:
        human_reliability = args.reliability
        print(f"Using human_reliability={human_reliability}")
    else:
        human_reliability = _prompt_reliability()

    # Build combined pending pool grouped by aspect, shuffled within each group
    rng = random.Random(args.seed)
    pending_by_aspect: dict[str, list[tuple[int, str]]] = {
        "question_fit": [],
        "context_fit": [],
    }
    for fi, ctx in enumerate(contexts):
        for qnum, aspect in _pending_for_judge(ctx.data, args.judge_id):
            pending_by_aspect[aspect].append((fi, qnum))
    for items in pending_by_aspect.values():
        rng.shuffle(items)

    total = sum(len(v) for v in pending_by_aspect.values())
    if total == 0:
        print(f"Nothing pending for judge '{args.judge_id}'. Exiting.")
        sys.exit(0)

    print(f"\n{total} judgment(s) pending for judge '{args.judge_id}'.")

    def _do_save(interrupted: bool = False) -> None:
        if interrupted:
            print("\nInterrupted — saving partial results...")
        for ctx in contexts:
            _rebuild_needs_human(ctx.data)
            _write_json(ctx.output_path, ctx.data)
            if interrupted:
                print(f"Saved to {ctx.output_path}")
        if interrupted:
            sys.exit(0)

    signal.signal(signal.SIGINT, lambda sig, frame: _do_save(interrupted=True))

    item_num = 0
    for aspect in ("question_fit", "context_fit"):
        items = pending_by_aspect[aspect]
        if not items:
            continue
        aspect_label = _ASPECT_LABELS.get(aspect, aspect)
        print(f"\n{'=' * 70}")
        print(f"  Aspect: {aspect_label}  ({len(items)} question(s))")
        print(f"{'=' * 70}")

        for fi, qnum in items:
            item_num += 1
            ctx = contexts[fi]
            print(f"\n--- Item {item_num}/{total} ---")
            _print_question_context(qnum, ctx.free_gen_answers, ctx.data)

            print(f"\n{_SEP}")
            print(f"Aspect: {aspect_label}")
            if args.show_precedents:
                _print_precedents(log_records, qnum, aspect, ctx.candidate_model)

            score, reason = _prompt_score(aspect_label)
            _record_judgment(ctx, qnum, aspect, args.judge_id, score, reason,
                             human_reliability, log_path, log_records)
            _do_save()

    _do_save()

    print(f"\nDone. Judged {item_num} item(s) as '{args.judge_id}'.")
    for ctx in contexts:
        remaining = len(ctx.data.get("needs_human", []))
        if remaining:
            print(f"  {ctx.candidate_model}: still needs_human for"
                  f" {remaining} question(s)")
        else:
            print(f"  {ctx.candidate_model}: needs_human is empty"
                  f" — ready for score_calculation")
        print(f"  Output: {ctx.output_path.resolve()}")
    print(f"Log: {log_path.resolve()}")


if __name__ == "__main__":
    main()

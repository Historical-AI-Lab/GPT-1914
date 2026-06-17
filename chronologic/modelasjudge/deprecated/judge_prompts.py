"""
judge_prompts.py — Shared judging primitives for the ChronoLogic LLM-as-judge pipeline.

Pure module: no network calls, no file I/O.  Imported by judge_scoring.py and
judge_reliability.py so prompt strings and scoring logic are never duplicated.

Public API
----------
build_judge_prompt(context, question, answer_a, answer_b, reasoning_type) -> str
parse_judge_response(raw: str) -> dict | None
assign_positions(rng, gt, candidate) -> (answer_a, answer_b, gt_letter)
score_one_comparison(judge_call, context, question, reasoning_type,
                     gt, candidate, rng, *, force_gt_position=None) -> dict
"""

import json
import re

# ---------------------------------------------------------------------------
# Prompt constants
# ---------------------------------------------------------------------------

_ABSTENTION_CLAUSE = (
    "If the question could not be answered in the specified historical context "
    "or makes no sense there, 'insufficient information' is a valid response. "
    "It is also acceptable to explain why the question could not be answered.\n\n"
)

_QUALIFICATIONS = {
    "character_modeling": "Which fits the character and situation described?",
    "topic_sentence": (
        "Which provides a more appropriate introduction to the paragraph "
        "and better conveys its meaning?"
    ),
    "knowledge": "Which is more accurate?",
    "abstention": "Which is more accurate?",
    "inference": (
        "Which reasons more accurately and better fulfills any specified conditions?"
    ),
    "sentence_cloze": "Which better completes the passage?",
    "phrase_cloze": "Which better completes the passage?",
    "constrained_generation": (
        "Which makes more sense, and better fulfills any specified constraints?"
    ),
}

_DEFAULT_QUALIFICATION = "Which better fits the question?"

_PROMPT_TEMPLATE = """\
You will be asked to choose between two answers to a question.

Question: {question}

Answer A: {answer_a}

Answer B: {answer_b}

1. Question fit.
Which answer better fits the question itself? {added_qualification}
- Choose A or B if one answer is more appropriate.
- Choose C if the two answers are both accurate and relevant to the question.

2. Context fit.
Now consider this historical context for the question:

Source: {context}

Ignore your previous decision. Now decide which answer is something the specified \
source might say. An incorrect answer to the question could still be \
typical of the source.
- Choose A or B if one is more typical.
- Choose C if either answer could be found in the source.

{abstention_clause}\
Respond in JSON: {{"question fit": "A"|"B"|"C", "context fit": "A"|"B"|"C"}}

Your response:"""

_RETRY_SUFFIX = (
    "\n\nIMPORTANT: Your previous response was not valid JSON. "
    'Respond ONLY with this exact format: {"question fit": "A", "context fit": "B"} '
    "(substituting A, B, or C for each letter)."
)

_REASONING_TYPES_NEEDING_ABSTENTION = {"knowledge", "abstention"}


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def build_judge_prompt(context, question, answer_a, answer_b, reasoning_type):
    """Build the full judge prompt for one A/B comparison.

    Args:
        context:        The metadata_frame string for this question.
        question:       The main_question string.
        answer_a:       Text placed in the "Answer A" slot.
        answer_b:       Text placed in the "Answer B" slot.
        reasoning_type: Question reasoning_type (e.g. "knowledge", "inference").

    Returns:
        str: fully formatted judge prompt.
    """
    abstention_clause = (
        _ABSTENTION_CLAUSE
        if reasoning_type in _REASONING_TYPES_NEEDING_ABSTENTION
        else ""
    )
    qualification = _QUALIFICATIONS.get(reasoning_type, _DEFAULT_QUALIFICATION)
    return _PROMPT_TEMPLATE.format(
        abstention_clause=abstention_clause,
        context=context,
        question=question,
        answer_a=answer_a,
        answer_b=answer_b,
        added_qualification=qualification,
    )


def parse_judge_response(raw):
    """Extract {"question fit": letter, "context fit": letter} from a judge reply.

    Tolerant of markdown code fences, leading/trailing prose, and lowercase letters.

    Args:
        raw: raw string returned by the judge model.

    Returns:
        dict with keys "question fit" and "context fit" (values uppercase A/B/C),
        or None if parsing fails.
    """
    if not raw:
        return None
    text = re.sub(r"```(?:json)?", "", raw).strip()
    match = re.search(r'\{[^{}]*\}', text)
    if not match:
        return None
    try:
        obj = json.loads(match.group())
    except json.JSONDecodeError:
        return None
    # Accept both "question fit" and "question_fit" key styles.
    qf = obj.get("question fit") or obj.get("question_fit")
    cf = obj.get("context fit") or obj.get("context_fit")
    if not qf or not cf:
        return None
    qf = str(qf).strip().upper()
    cf = str(cf).strip().upper()
    if qf not in ("A", "B", "C") or cf not in ("A", "B", "C"):
        return None
    return {"question fit": qf, "context fit": cf}


def assign_positions(rng, gt, candidate):
    """Randomly assign gt and candidate to the A / B answer slots.

    Args:
        rng:       random.Random instance (or the random module).
        gt:        ground-truth answer string.
        candidate: model answer string.

    Returns:
        tuple: (answer_a, answer_b, gt_letter) where gt_letter ∈ {"A", "B"}.
    """
    if rng.random() < 0.5:
        return gt, candidate, "A"
    return candidate, gt, "B"


def score_one_comparison(
    judge_call, context, question, reasoning_type, gt, candidate, rng,
    *, force_gt_position=None,
):
    """Submit one A/B comparison and return a structured outcome dict.

    Retries once with a stricter reminder if the judge returns malformed JSON.

    Args:
        judge_call:        callable(user_prompt: str) -> str.
        context:           metadata_frame string.
        question:          main_question string.
        reasoning_type:    question reasoning_type string.
        gt:                ground-truth answer string.
        candidate:         model (candidate) answer string.
        rng:               random.Random instance for position randomization.
        force_gt_position: "A", "B", or None (randomize with rng).

    Returns:
        dict:
            question_outcome  — "win" | "tie" | "loss" | "invalid"
            context_outcome   — same
            question_pass     — 1 if candidate wins or ties, else 0
            context_pass      — 1 if candidate wins or ties, else 0
            gt_position       — "A" | "B"
            raw               — last raw judge response string
    """
    # Determine slot assignment.
    if force_gt_position is not None:
        gt_letter = force_gt_position
        if force_gt_position == "A":
            answer_a, answer_b = gt, candidate
        else:
            answer_a, answer_b = candidate, gt
    else:
        answer_a, answer_b, gt_letter = assign_positions(rng, gt, candidate)

    candidate_letter = "B" if gt_letter == "A" else "A"

    prompt = build_judge_prompt(context, question, answer_a, answer_b, reasoning_type)
    raw = judge_call(prompt)
    parsed = parse_judge_response(raw)

    if parsed is None:
        raw = judge_call(prompt + _RETRY_SUFFIX)
        parsed = parse_judge_response(raw)

    if parsed is None:
        return {
            "question_outcome": "invalid",
            "context_outcome": "invalid",
            "question_pass": 0,
            "context_pass": 0,
            "gt_position": gt_letter,
            "raw": raw,
        }

    def _outcome(choice):
        if choice == "C":
            return "tie"
        if choice == candidate_letter:
            return "win"
        if choice == gt_letter:
            return "loss"
        return "invalid"

    q_outcome = _outcome(parsed["question fit"])
    ctx_outcome = _outcome(parsed["context fit"])

    return {
        "question_outcome": q_outcome,
        "context_outcome": ctx_outcome,
        "question_pass": 1 if q_outcome in ("win", "tie") else 0,
        "context_pass": 1 if ctx_outcome in ("win", "tie") else 0,
        "gt_position": gt_letter,
        "raw": raw,
    }

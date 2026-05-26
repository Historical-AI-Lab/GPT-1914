"""
judge_prompts_nocontext.py — Question-only judging primitives (no context fit).

For use by judge_scoring_nocontext.py, judge_alpha_reliability_nocontext.py,
and judge_beta_reliability_nocontext.py.

Identical public API to judge_prompts.py but evaluates only question fit.
The prompt does not show the source/context to the judge, preserving calibrated
question-accuracy behavior (the ~0.92 reliability was measured without it).
The context parameter is accepted for signature compatibility but ignored.

Public API
----------
build_judge_prompt(context, question, answer_a, answer_b, reasoning_type) -> str
parse_judge_response(raw: str) -> dict | None   # {"question fit": "A"|"B"|"C"}
assign_positions(rng, gt, candidate) -> (answer_a, answer_b, gt_letter)
score_one_comparison(judge_call, context, question, reasoning_type,
                     gt, candidate, rng, *, force_gt_position=None) -> dict
"""

import json
import re

from judge_prompts import assign_positions  # aspect-agnostic utility; reuse directly

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
You will be asked to evaluate two answers to a question. Focus on the substantive content of the answers rather than style.

Context: {context}
Question: {question}

Answer A: {answer_a}

Answer B: {answer_b}

Which answer is a better substantive fit for the question? {added_qualification}
- Choose A or B if one answer is more accurate or more relevant.
- Choose C if both answers are accurate and relevant to the question.

{abstention_clause}\
Respond in JSON: {{"question fit": "A"|"B"|"C"}}

Your response:"""

_RETRY_SUFFIX = (
    "\n\nIMPORTANT: Your previous response was not valid JSON. "
    'Respond ONLY with this exact format: {"question fit": "A"} '
    "(substituting A, B, or C)."
)

_REASONING_TYPES_NEEDING_ABSTENTION = {"knowledge", "abstention"}


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def build_judge_prompt(context, question, answer_a, answer_b, reasoning_type):
    """Build the question-only judge prompt for one A/B comparison.

    Args:
        context:        is still used, even though we don't judge it separately..
        question:       The main_question string.
        answer_a:       Text placed in the "Answer A" slot.
        answer_b:       Text placed in the "Answer B" slot.
        reasoning_type: Question reasoning_type string.

    Returns:
        str: fully formatted judge prompt (question fit only).
    """
    abstention_clause = (
        _ABSTENTION_CLAUSE
        if reasoning_type in _REASONING_TYPES_NEEDING_ABSTENTION
        else ""
    )
    qualification = _QUALIFICATIONS.get(reasoning_type, _DEFAULT_QUALIFICATION)
    return _PROMPT_TEMPLATE.format(
        question=question,
        context=context,
        answer_a=answer_a,
        answer_b=answer_b,
        added_qualification=qualification,
        abstention_clause=abstention_clause,
    )


def parse_judge_response(raw):
    """Extract {"question fit": letter} from a judge reply.

    Tolerant of markdown code fences, leading/trailing prose, and lowercase.

    Args:
        raw: raw string returned by the judge model.

    Returns:
        dict with key "question fit" (value uppercase A/B/C), or None if parsing fails.
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
    qf = obj.get("question fit") or obj.get("question_fit")
    if not qf:
        return None
    qf = str(qf).strip().upper()
    if qf not in ("A", "B", "C"):
        return None
    return {"question fit": qf}


def score_one_comparison(
    judge_call, context, question, reasoning_type, gt, candidate, rng,
    *, force_gt_position=None,
):
    """Submit one A/B comparison and return a structured outcome dict.

    Retries once with a stricter reminder if the judge returns malformed JSON.

    Args:
        judge_call:        callable(user_prompt: str) -> str.
        context:           Accepted for API symmetry; not passed to the prompt.
        question:          main_question string.
        reasoning_type:    question reasoning_type string.
        gt:                ground-truth answer string.
        candidate:         model (candidate) answer string.
        rng:               random.Random instance for position randomization.
        force_gt_position: "A", "B", or None (randomize with rng).

    Returns:
        dict:
            question_outcome  — "win" | "tie" | "loss" | "invalid"
            question_pass     — 1 if candidate wins or ties, else 0
            gt_position       — "A" | "B"
            raw               — last raw judge response string
    """
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
            "question_pass": 0,
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

    return {
        "question_outcome": q_outcome,
        "question_pass": 1 if q_outcome in ("win", "tie") else 0,
        "gt_position": gt_letter,
        "raw": raw,
    }

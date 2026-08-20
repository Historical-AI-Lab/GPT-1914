"""
judge_prompts_nocontext.py — Judging primitives for the PASS/FAIL path.

For use by judge_scoring_nocontext.py, judge_alpha_reliability_nocontext.py,
and judge_beta_reliability_nocontext.py.

Identical public API to judge_prompts.py, but asks for a single verdict rather
than two. The criteria are factual accuracy and relevance to the question
(instruction following); the prompt explicitly tells the judge NOT to weigh
period style. The historical context is still shown, because accuracy is
judged *within* it -- an answer can only be right or wrong relative to the
source's period and situation.

The richer criteria -- fit to the discursive and socio-historical context,
resolved on a continuous scale -- belong to the partial-credit path
(bt_context_scoring.py). That path covers a superset of what this one covers.
The "nocontext" in this filename is historical: it means "does not emit a
separate context verdict", not "ignores the context".

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

# _QUALIFICATIONS = {
#     "character_modeling": "Which fits the character and situation described?",
#     "topic_sentence": (
#         "Which provides a more appropriate introduction to the paragraph "
#         "and better conveys its meaning?"
#     ),
#     "knowledge": "Which is more accurate?",
#     "abstention": "Which is more accurate?",
#     "inference": (
#         "Which reasons more accurately and better fulfills any specified conditions?"
#     ),
#     "sentence_cloze": "Which better completes the passage?",
#     "phrase_cloze": "Which better completes the passage?",
#     "constrained_generation": (
#         "Which makes more sense, and better fulfills any specified constraints?"
#     ),
# }

# _QUALIFICATIONS = {
#     "character_modeling": "Which fits the character and situation described?",
#     "topic_sentence": (
#         "Which provides a more appropriate introduction to the paragraph "
#         "and better conveys its meaning?"
#     ),
#     "knowledge": "Which is more accurate?",
#     "abstention": "Which is more accurate?",
#     "inference": (
#         "Which reasons more accurately and better fulfills any specified conditions?"
#     ),
#     "sentence_cloze": "Which better completes the passage?",
#     "phrase_cloze": "Which better completes the passage?",
#     "constrained_generation": (
#         "Which makes more sense, and better fulfills any specified constraints?"
#     ),
# }

_QUALIFICATIONS = {
    "character_modeling": "The only thing the character could say in that situation?",
    "topic_sentence": "The only appropriate introduction to the paragraph?",
    "knowledge": "More accurate?",
    "abstention": "More accurate?",
    "inference": "More accurate?",
    "sentence_cloze": "The only logical completion of the passage?",
    "phrase_cloze": "The only logical completion of the passage?",
    "constrained_generation": "The only match for the source and constraints?"
}

_DEFAULT_QUALIFICATION = ""

_PROMPT_TEMPLATE = """\
You will receive a question and two answers to evaluate. The criteria for evaluation are factual accuracy (in the specified historical context) and relevance to the question (correctly following instructions). Do not try to judge whether the style fits the period. At least one answer is a valid response; both may be valid.

Context: {context}
Question: {question}

Answer A: {answer_a}

Answer B: {answer_b}

- Choose A or B if only one answer is accurate and relevant.
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
    """Build the pass/fail judge prompt for one A/B comparison.

    Args:
        context:        shown to the judge -- accuracy is judged *within* the
                        period context -- but not scored as a separate verdict.
        question:       The main_question string.
        answer_a:       Text placed in the "Answer A" slot.
        answer_b:       Text placed in the "Answer B" slot.
        reasoning_type: Question reasoning_type string.

    Returns:
        str: fully formatted pass/fail judge prompt.
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

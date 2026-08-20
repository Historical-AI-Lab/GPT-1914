"""substantive/groups.py — the reasoning-type breakdown grouping (three
headings: cloze, constrained generation, knowledge and inference).

Single source of truth for the mapping. `reasoning_type` alone determines
the group -- verified exhaustive against booksample/chronologic_en_0.7.jsonl
(866/866 records mapped, zero misses) -- so no second `question_category`
table is needed. `refusal` and `abstention` both map to knowledge_inference:
0.7 uses `abstention`, the in-progress 1875 benchmark uses `refusal` for the
same reasoning type.
"""

from __future__ import annotations

GROUPS = ["cloze", "constrained_generation", "knowledge_inference"]

GROUP_LABELS = {
    "cloze": "cloze",
    "constrained_generation": "constrained generation",
    "knowledge_inference": "knowledge and inference",
}

REASONING_TO_GROUP = {
    "phrase_cloze": "cloze",
    "sentence_cloze": "cloze",
    "topic_sentence": "cloze",
    "constrained_generation": "constrained_generation",
    "character_modeling": "constrained_generation",
    "knowledge": "knowledge_inference",
    "inference": "knowledge_inference",
    "abstention": "knowledge_inference",
    "refusal": "knowledge_inference",   # 1875-era slug for abstention
}

# Ledger/report column prefixes -- distinct from the reasoning_type value
# "constrained_generation" itself, so grp_congen_* can't be confused with a
# raw reasoning_type-keyed column elsewhere in the row dict.
LEDGER_PREFIX = {
    "cloze": "grp_cloze",
    "constrained_generation": "grp_congen",
    "knowledge_inference": "grp_knowinf",
}


class UnmappedReasoningType(KeyError):
    """A question's reasoning_type has no entry in REASONING_TO_GROUP."""


def group_of(rec: dict, *, qnum: str = "") -> str:
    """Which of GROUPS `rec` belongs to, keyed on rec['reasoning_type'].

    Raises rather than falling back to an "other" bucket (spec §8.9): a
    reasoning_type this map doesn't know about should stop the run, not
    silently vanish from every group's count.
    """
    rt = rec.get("reasoning_type")
    try:
        return REASONING_TO_GROUP[rt]
    except KeyError:
        where = f" (question {qnum})" if qnum else ""
        raise UnmappedReasoningType(
            f"reasoning_type {rt!r} not in REASONING_TO_GROUP{where}"
        ) from None

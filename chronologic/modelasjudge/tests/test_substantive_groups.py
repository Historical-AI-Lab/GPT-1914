"""test_substantive_groups.py — the reasoning-type breakdown mapping.

Verifies substantive/groups.py maps every reasoning_type value that
appears on the live benchmark to exactly one of the three groups (cloze,
constrained_generation, knowledge_inference), and that group_of fails
loud rather than silently dropping an unmapped value.
"""

import json
import sys
from pathlib import Path

import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from substantive.groups import (
    GROUP_LABELS, GROUPS, LEDGER_PREFIX, REASONING_TO_GROUP,
    UnmappedReasoningType, group_of,
)


class TestMappingShape:
    def test_every_group_has_a_label_and_ledger_prefix(self):
        for g in GROUPS:
            assert g in GROUP_LABELS
            assert g in LEDGER_PREFIX

    def test_every_mapped_value_targets_a_known_group(self):
        assert set(REASONING_TO_GROUP.values()) <= set(GROUPS)

    def test_both_abstention_slugs_map_to_knowledge_inference(self):
        assert REASONING_TO_GROUP["abstention"] == "knowledge_inference"
        assert REASONING_TO_GROUP["refusal"] == "knowledge_inference"


class TestGroupOf:
    def test_maps_known_reasoning_type(self):
        assert group_of({"reasoning_type": "phrase_cloze"}) == "cloze"
        assert group_of({"reasoning_type": "character_modeling"}) == "constrained_generation"
        assert group_of({"reasoning_type": "inference"}) == "knowledge_inference"

    def test_raises_on_unknown_reasoning_type(self):
        with pytest.raises(UnmappedReasoningType):
            group_of({"reasoning_type": "some_future_type"})

    def test_raises_on_missing_reasoning_type(self):
        with pytest.raises(UnmappedReasoningType):
            group_of({})

    def test_error_names_the_offending_value_and_qnum(self):
        with pytest.raises(UnmappedReasoningType, match="bogus_type"):
            group_of({"reasoning_type": "bogus_type"}, qnum="42")


class TestRealBenchmark:
    """Exhaustiveness against the live benchmark -- every reasoning_type
    that actually appears must be mapped, with no unmapped stragglers."""

    def test_chronologic_0_7_is_fully_mapped_and_partitions_as_expected(self):
        bm = MODELASJUDGE.parent / "booksample" / "chronologic_en_0.7.jsonl"
        if not bm.exists():
            pytest.skip(f"{bm} not present")
        recs = [json.loads(line) for line in bm.read_text(encoding="utf-8").splitlines() if line.strip()]

        counts = {g: 0 for g in GROUPS}
        for rec in recs:
            counts[group_of(rec)] += 1

        assert sum(counts.values()) == len(recs)
        assert counts["cloze"] == 359
        assert counts["constrained_generation"] == 273
        assert counts["knowledge_inference"] == 234

    def test_chronologic_1875_is_fully_mapped(self):
        """The in-progress 1875 benchmark uses `refusal` rather than
        `abstention` -- this is exactly the case the dual mapping exists
        for."""
        bm = MODELASJUDGE.parent / "booksample" / "chronologic_en_1875.jsonl"
        if not bm.exists():
            pytest.skip(f"{bm} not present")
        recs = [json.loads(line) for line in bm.read_text(encoding="utf-8").splitlines() if line.strip()]
        for rec in recs:
            group_of(rec)  # must not raise

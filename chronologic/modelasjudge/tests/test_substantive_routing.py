"""test_substantive_routing.py — the plan §0 regression test.

Verifies the shared routing helper reproduces the correct partition on
synthetic benchmarks at each precedence rung, and on the two real
benchmarks that motivated the fix: ChronoLogic 0.7 (partial_credit) and
the BT pilot (context_judged, since it predates partial_credit).
"""

import json
import sys
from pathlib import Path

import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from substantive.routing import assert_partition, route_questions, routing_basis


def _write(tmp_path, recs):
    p = tmp_path / "b.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in recs))
    return p


class TestPrecedence:
    def test_partial_credit_wins_when_present(self, tmp_path):
        recs = [
            {"question_number": 1, "partial_credit": 1, "context_judged": 0,
             "frame_type": "book_context", "reasoning_type": "constrained_generation"},
            {"question_number": 2, "partial_credit": 0, "context_judged": 1,
             "frame_type": "world_context", "reasoning_type": "knowledge"},
        ]
        routing = route_questions(_write(tmp_path, recs))
        assert routing.basis == "partial_credit"
        assert set(routing.partial) == {"1"}
        assert set(routing.pass_fail) == {"2"}

    def test_context_judged_used_when_no_partial_credit_field(self, tmp_path):
        recs = [
            {"question_number": 1, "context_judged": 1,
             "frame_type": "world_context", "reasoning_type": "knowledge"},
            {"question_number": 2, "context_judged": 0,
             "frame_type": "book_context", "reasoning_type": "constrained_generation"},
        ]
        routing = route_questions(_write(tmp_path, recs))
        assert routing.basis == "context_judged"
        # context_judged==1 wins even though reasoning_type would say otherwise
        assert set(routing.partial) == {"1"}
        assert set(routing.pass_fail) == {"2"}

    def test_legacy_rule_used_when_neither_field_present(self, tmp_path):
        recs = [
            {"question_number": 1, "frame_type": "book_context",
             "reasoning_type": "constrained_generation"},
            {"question_number": 2, "frame_type": "world_context",
             "reasoning_type": "knowledge"},
        ]
        routing = route_questions(_write(tmp_path, recs))
        assert routing.basis == "legacy"
        assert set(routing.partial) == {"1"}
        assert set(routing.pass_fail) == {"2"}

    def test_a_flagged_file_is_taken_at_its_word(self, tmp_path):
        """Presence of the field anywhere switches off the fallback, so a 0
        is honoured even on a question the legacy rule would have selected."""
        recs = [
            {"question_number": 1, "partial_credit": 0, "frame_type": "book_context",
             "reasoning_type": "constrained_generation"},
            {"question_number": 2, "partial_credit": 1, "frame_type": "world_context",
             "reasoning_type": "knowledge"},
        ]
        routing = route_questions(_write(tmp_path, recs))
        assert routing.basis == "partial_credit"
        assert set(routing.partial) == {"2"}
        assert set(routing.pass_fail) == {"1"}

    def test_routing_basis_matches_route_questions(self, tmp_path):
        recs = [{"question_number": 1, "context_judged": 1}]
        assert routing_basis(recs) == "context_judged"


class TestRealBenchmarks:
    def test_chronologic_0_7_yields_554_and_310(self):
        bm = MODELASJUDGE.parent / "booksample" / "chronologic_en_0.7.jsonl"
        if not bm.exists():
            pytest.skip(f"{bm} not present")
        routing = route_questions(bm)
        assert routing.basis == "partial_credit"
        assert len(routing.pass_fail) == 554
        assert len(routing.partial) == 310

    def test_pilot_benchmark_yields_40_via_context_judged(self):
        bm = MODELASJUDGE.parent / "booksample" / "chronologic_btpilot_0.1.jsonl"
        if not bm.exists():
            pytest.skip(f"{bm} not present")
        routing = route_questions(bm)
        assert routing.basis == "context_judged"
        assert len(routing.partial) == 40


class TestAssertPartition:
    def test_raises_on_unrouted_answered_qnum(self, tmp_path):
        recs = [{"question_number": 1, "partial_credit": 1}]
        routing = route_questions(_write(tmp_path, recs))
        with pytest.raises(ValueError, match="not routed"):
            assert_partition(routing, {"1", "99"})

    def test_passes_when_every_answered_qnum_is_routed(self, tmp_path):
        recs = [
            {"question_number": 1, "partial_credit": 1},
            {"question_number": 2, "partial_credit": 0},
        ]
        routing = route_questions(_write(tmp_path, recs))
        assert_partition(routing, {"1", "2"})  # no raise

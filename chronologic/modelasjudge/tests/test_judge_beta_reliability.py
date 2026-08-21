"""test_judge_beta_reliability.py — Unit tests for judge_beta_reliability_nocontext.py.

Pure-function tests; no network calls, no LLM.

Run with:
    pytest modelasjudge/tests/test_judge_beta_reliability.py -v
"""

import sys
from pathlib import Path

import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from judge_beta_reliability_nocontext import (
    build_gt_pairs,
    collect_pair_outcomes,
    _infer_frame_type,
    _derive_alt_gt_path,
)


# ---------------------------------------------------------------------------
# Fixtures: fake records
# ---------------------------------------------------------------------------

def _main_rec(qnum, gts, reasoning_type="knowledge", metadata_frame="Context.",
              question="Q?", frame_type=None):
    """Build a minimal main-benchmark record."""
    strings = list(gts) + ["distractor"]
    types   = ["ground_truth"] * len(gts) + ["manual"]
    rec = {
        "question_number": qnum,
        "answer_strings":  strings,
        "answer_types":    types,
        "metadata_frame":  metadata_frame,
        "main_question":   question,
        "reasoning_type":  reasoning_type,
    }
    if frame_type is not None:
        rec["frame_type"] = frame_type
    return rec


def _alt_rec(qnum, original_gt, alternate_gt, metadata_frame="AltCtx.", question="AltQ?"):
    return {
        "question_number": qnum,
        "original_gt":     original_gt,
        "alternate_gt":    alternate_gt,
        "metadata_frame":  metadata_frame,
        "question":        question,
    }


# ---------------------------------------------------------------------------
# build_gt_pairs
# ---------------------------------------------------------------------------

class TestBuildGtPairs:
    def test_single_gt_skipped(self):
        main = [_main_rec(1, ["Only GT"])]
        pairs = build_gt_pairs(main, [])
        assert pairs == []

    def test_two_gts_yields_one_pair(self):
        main = [_main_rec(10, ["Short GT", "Another GT"])]
        pairs = build_gt_pairs(main, [])
        assert len(pairs) == 1
        p = pairs[0]
        assert p["source"] == "main"
        assert p["original_gt"] == "Short GT"
        assert p["other_gt"] == "Another GT"
        assert p["orig_len"] == len("Short GT")
        assert p["question_number"] == "10"
        assert p["pair_id"] == "main:10:1"

    def test_three_gts_yields_two_pairs(self):
        main = [_main_rec(5, ["GT0", "GT1", "GT2"])]
        pairs = build_gt_pairs(main, [])
        assert len(pairs) == 2
        assert pairs[0]["original_gt"] == "GT0"
        assert pairs[0]["other_gt"] == "GT1"
        assert pairs[0]["pair_id"] == "main:5:1"
        assert pairs[1]["original_gt"] == "GT0"
        assert pairs[1]["other_gt"] == "GT2"
        assert pairs[1]["pair_id"] == "main:5:2"

    def test_alt_record_yields_pair(self):
        alt = [_alt_rec(7, "Original answer", "Alternate answer")]
        pairs = build_gt_pairs([], alt)
        assert len(pairs) == 1
        p = pairs[0]
        assert p["source"] == "alt"
        assert p["original_gt"] == "Original answer"
        assert p["other_gt"] == "Alternate answer"
        assert p["orig_len"] == len("Original answer")
        assert p["pair_id"] == "alt:7"

    def test_alt_record_missing_field_skipped(self):
        alt = [
            {"question_number": 8, "original_gt": "Good", "alternate_gt": ""},
            {"question_number": 9, "original_gt": "", "alternate_gt": "Also good"},
            {"question_number": 10},
        ]
        pairs = build_gt_pairs([], alt)
        assert pairs == []

    def test_metadata_joined_from_main_for_alt(self):
        main = [_main_rec(7, ["GT only"], reasoning_type="inference",
                          metadata_frame="Main context.", question="Main Q?")]
        alt  = [_alt_rec(7, "Alt original", "Alt alternate",
                         metadata_frame="Alt context.", question="Alt Q?")]
        pairs = build_gt_pairs(main, alt)
        assert len(pairs) == 1
        p = pairs[0]
        assert p["reasoning_type"] == "inference"
        assert p["context"] == "Main context."
        assert p["question"] == "Main Q?"

    def test_no_overlap_main_and_alt(self):
        main = [_main_rec(1, ["A", "B"]), _main_rec(2, ["C", "D"])]
        alt  = [_alt_rec(3, "E", "F"), _alt_rec(4, "G", "H")]
        pairs = build_gt_pairs(main, alt)
        assert len(pairs) == 4
        sources = [p["source"] for p in pairs]
        assert sources.count("main") == 2
        assert sources.count("alt") == 2

    def test_combined_count_matches_plan(self):
        main = [_main_rec(i, [f"GT{i}A", f"GT{i}B"]) for i in range(16)]
        alt  = [_alt_rec(100 + i, f"orig{i}" * 3, f"alt{i}" * 3) for i in range(68)]
        pairs = build_gt_pairs(main, alt)
        assert len(pairs) == 84

    def test_frame_type_inferred_from_reasoning_type(self):
        """Pairs get frame_type from _infer_frame_type when record lacks frame_type."""
        main = [_main_rec(1, ["GT1", "GT2"], reasoning_type="knowledge")]
        pairs = build_gt_pairs(main, [])
        assert pairs[0]["frame_type"] == "world_context"

    def test_frame_type_taken_from_main_record_directly(self):
        """Explicit frame_type field on main record takes precedence."""
        main = [_main_rec(1, ["GT1", "GT2"], reasoning_type="knowledge",
                          frame_type="book_context")]
        pairs = build_gt_pairs(main, [])
        assert pairs[0]["frame_type"] == "book_context"

    def test_frame_type_on_alt_pairs_joined_from_main(self):
        """Alt-source pairs get frame_type from main record via question_number join."""
        main = [_main_rec(7, ["Single GT"], reasoning_type="phrase_cloze",
                          frame_type="passage_context")]
        alt  = [_alt_rec(7, "Original", "Alternate")]
        pairs = build_gt_pairs(main, alt)
        assert len(pairs) == 1
        assert pairs[0]["frame_type"] == "passage_context"

    def test_frame_type_alt_inferred_when_no_main_match(self):
        """Alt pair with no main record still gets frame_type via reasoning_type fallback."""
        alt = [_alt_rec(999, "Original", "Alternate")]
        # alt record has no reasoning_type; main has no matching qnum
        pairs = build_gt_pairs([], alt)
        assert len(pairs) == 1
        assert "frame_type" in pairs[0]   # may be empty string, but key exists

    def test_frame_type_all_reasoning_types(self):
        """All known reasoning_types produce expected frame_type on pairs."""
        expected = {
            "knowledge": "world_context",
            "inference": "world_context",
            "character_modeling": "book_context",
            "phrase_cloze": "passage_context",
            "sentence_cloze": "passage_context",
        }
        for rt, expected_ft in expected.items():
            main = [_main_rec(1, ["G1", "G2"], reasoning_type=rt)]
            pairs = build_gt_pairs(main, [])
            assert pairs[0]["frame_type"] == expected_ft, f"failed for {rt}"


# ---------------------------------------------------------------------------
# collect_pair_outcomes (stub judges; question_fit only)
# ---------------------------------------------------------------------------

def _make_always_tie_judge():
    """Judge always responds 'C' (tie) for question fit."""
    def judge_call(prompt):
        return '{"question fit": "C"}'
    return judge_call


def _make_always_a_judge():
    """Judge always chooses slot A."""
    def judge_call(prompt):
        return '{"question fit": "A"}'
    return judge_call


def _make_always_b_judge():
    """Judge always chooses slot B."""
    def judge_call(prompt):
        return '{"question fit": "B"}'
    return judge_call


def _make_test_pair(frame_type="world_context"):
    return {
        "pair_id":        "main:1:1",
        "question_number": "1",
        "source":         "main",
        "original_gt":    "The answer is X.",
        "other_gt":       "The answer is also X.",
        "orig_len":       16,
        "frame_type":     frame_type,
        "context":        "Historical context.",
        "question":       "What is X?",
        "reasoning_type": "knowledge",
    }


class TestCollectPairOutcomes:
    def test_always_tie_judge_no_failures(self):
        pairs = [_make_test_pair()]
        outcome_records, completed = collect_pair_outcomes(pairs, _make_always_tie_judge())
        assert len(outcome_records) == 1
        rec = outcome_records[0]
        assert rec["k_nontie"] == 0
        assert rec["n_valid_trials"] == 2     # 2 orderings
        assert rec["invalid"] == 0
        assert completed == ["main:1:1"]

    def test_always_a_judge_all_failures_ka(self):
        pairs = [_make_test_pair()]
        outcome_records, _ = collect_pair_outcomes(pairs, _make_always_a_judge())
        rec = outcome_records[0]
        assert rec["n_valid_trials"] == 2
        assert rec["k_nontie"] == 2
        assert rec["k_A"] == 2
        assert rec["k_B"] == 0

    def test_always_b_judge_all_failures_kb(self):
        pairs = [_make_test_pair()]
        outcome_records, _ = collect_pair_outcomes(pairs, _make_always_b_judge())
        rec = outcome_records[0]
        assert rec["k_nontie"] == 2
        assert rec["k_A"] == 0
        assert rec["k_B"] == 2

    def test_ka_plus_kb_equals_k_nontie(self):
        pairs = [
            _make_test_pair(),
            {**_make_test_pair(), "pair_id": "main:2:1"},
        ]
        outcome_records, _ = collect_pair_outcomes(pairs, _make_always_a_judge())
        for rec in outcome_records:
            assert rec["k_A"] + rec["k_B"] == rec["k_nontie"]

    def test_limit_respected(self):
        pairs = [{**_make_test_pair(), "pair_id": f"main:{i}:1"} for i in range(10)]
        _, completed = collect_pair_outcomes(pairs, _make_always_tie_judge(), limit=3)
        assert len(completed) == 3

    def test_invalid_judge_excluded_from_n_valid(self):
        def bad_judge(prompt):
            return "not json at all"
        outcome_records, _ = collect_pair_outcomes([_make_test_pair()], bad_judge)
        rec = outcome_records[0]
        assert rec["n_valid_trials"] == 0
        assert rec["invalid"] == 2

    def test_on_pair_done_callback_called_for_each_pair(self):
        pairs = [{**_make_test_pair(), "pair_id": f"main:{i}:1"} for i in range(3)]
        called = []
        def on_done(pair, rec):
            called.append((pair["pair_id"], rec["n_valid_trials"]))
        collect_pair_outcomes(pairs, _make_always_tie_judge(), on_pair_done=on_done)
        assert len(called) == 3
        assert all(n_valid == 2 for _, n_valid in called)

    def test_on_pair_done_receives_full_outcome_dict(self):
        pairs = [_make_test_pair()]
        received = []
        def on_done(pair, rec):
            received.append(dict(rec))
        collect_pair_outcomes(pairs, _make_always_a_judge(), on_pair_done=on_done)
        assert len(received) == 1
        rec = received[0]
        for key in ("n_valid_trials", "k_nontie", "k_A", "k_B", "invalid"):
            assert key in rec

    def test_multiple_pairs_order_preserved(self):
        pairs = [
            {**_make_test_pair(), "pair_id": "main:1:1", "original_gt": "short"},
            {**_make_test_pair(), "pair_id": "main:2:1",
             "original_gt": "a somewhat longer answer"},
        ]
        _, completed = collect_pair_outcomes(pairs, _make_always_tie_judge())
        assert completed == ["main:1:1", "main:2:1"]


# ---------------------------------------------------------------------------
# _infer_frame_type
# ---------------------------------------------------------------------------

class TestInferFrameType:
    def test_world_context_types(self):
        for rt in ("knowledge", "inference", "refusal"):
            assert _infer_frame_type(rt) == "world_context", f"failed for {rt}"

    def test_book_context_types(self):
        for rt in ("character_modeling", "constrained_generation", "topic_sentence"):
            assert _infer_frame_type(rt) == "book_context", f"failed for {rt}"

    def test_passage_context_types(self):
        for rt in ("phrase_cloze", "sentence_cloze"):
            assert _infer_frame_type(rt) == "passage_context", f"failed for {rt}"

    def test_unknown_returns_empty(self):
        assert _infer_frame_type("unknown_type") == ""
        assert _infer_frame_type("") == ""


# ---------------------------------------------------------------------------
# _derive_alt_gt_path
# ---------------------------------------------------------------------------

class TestHelpers:
    def test_derive_alt_gt_path(self, tmp_path):
        p = tmp_path / "chronologic_en_0.3.jsonl"
        result = _derive_alt_gt_path(str(p))
        assert result.name == "chronologic_en_0.3_alternateGT.jsonl"
        assert result.parent == tmp_path

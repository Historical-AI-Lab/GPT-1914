"""test_remerge.py — Unit tests for remerge_human_scores.py.

Run with:
    pytest modelasjudge/tests/test_remerge.py -v
"""

import json
import sys
from pathlib import Path

import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from remerge_human_scores import merge_human_scores


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_old(qf_entries: dict, cf_entries: dict, bctx: list) -> dict:
    return {
        "judge_model": "anthropic/claude-sonnet-4-6",
        "candidate_model": "model-x",
        "benchmark_version": "0.2",   # wrong — the contaminated value
        "reliability_source": "/path/llm_reliability/judge__0.2.json",
        "thresholds": {"question_fit": 0.65},
        "question_fit": qf_entries,
        "context_fit": cf_entries,
        "book_context_qnums": bctx,
        "needs_human": [],
    }


def _make_new(qf_entries: dict, bctx: list) -> dict:
    return {
        "judge_model": "anthropic/claude-sonnet-4-6",
        "candidate_model": "model-x",
        "benchmark_version": "0.4",   # correct
        "reliability_source": "/path/llm_reliability/judge__0.4.json",
        "thresholds": {"question_fit": 0.65},
        "question_fit": qf_entries,
        "context_fit": {},
        "book_context_qnums": bctx,
        "needs_human": [],
    }


def _llm_entry(score: int = 1, r_q: float = 0.9) -> dict:
    return {
        "judge": "anthropic/claude-sonnet-4-6",
        "r_q": r_q,
        "judgments": ["tie" if score else "GT"],
        "scores": [score],
        "gt_positions": ["A"],
        "gt_indices": [0],
    }


def _human_entry(score: int = 1, judge_id: str = "TU") -> dict:
    entry = {
        "judge": "human",
        "r_q": 0.9,
        "judgments": ["tie" if score else "GT"],
        "scores": [score],
        "gt_positions": [None],
        "gt_indices": [None],
        "human_judges": {
            judge_id: {
                "score": score,
                "judgment": "tie" if score else "GT",
                "reason": "test",
                "r_q": 0.9,
                "timestamp": "2026-01-01T00:00:00+00:00",
            }
        },
    }
    return entry


def _cf_human_entry(score: int = 1, judge_id: str = "TU") -> dict:
    return {
        "judge": "human",
        "r_q": 0.9,
        "judgments": ["tie" if score else "GT"],
        "scores": [score],
        "gt_positions": [None],
        "gt_indices": [None],
        "human_judges": {
            judge_id: {
                "score": score,
                "judgment": "tie" if score else "GT",
                "reason": "context ok",
                "r_q": 0.9,
                "timestamp": "2026-01-01T00:00:00+00:00",
            }
        },
    }


# ---------------------------------------------------------------------------
# Tests: human question_fit entries are carried over
# ---------------------------------------------------------------------------

def test_human_qf_overrides_new_llm():
    """A human-judged entry from old replaces the LLM entry in new."""
    old = _make_old(
        qf_entries={"1": _human_entry(score=0)},
        cf_entries={},
        bctx=[],
    )
    new = _make_new(
        qf_entries={"1": _llm_entry(score=1)},  # LLM said pass; human said fail
        bctx=[],
    )
    merged = merge_human_scores(old, new)
    assert merged["question_fit"]["1"]["judge"] == "human"
    assert merged["question_fit"]["1"]["scores"] == [0]


def test_llm_only_qf_kept_when_no_human():
    """A qnum with no human_judges keeps the new LLM result."""
    old = _make_old(
        qf_entries={"2": _llm_entry(score=0)},  # old LLM (contaminated); no human
        cf_entries={},
        bctx=[],
    )
    new = _make_new(
        qf_entries={"2": _llm_entry(score=1)},  # new correct LLM
        bctx=[],
    )
    merged = merge_human_scores(old, new)
    assert merged["question_fit"]["2"]["judge"] != "human"
    assert merged["question_fit"]["2"]["scores"] == [1]


def test_empty_human_judges_not_carried():
    """An entry with human_judges={} (empty) is treated as no human judgment."""
    entry = _llm_entry()
    entry["human_judges"] = {}
    old = _make_old(qf_entries={"3": entry}, cf_entries={}, bctx=[])
    new = _make_new(qf_entries={"3": _llm_entry(score=0)}, bctx=[])
    merged = merge_human_scores(old, new)
    # empty human_judges → keep new LLM result
    assert "human_judges" not in merged["question_fit"]["3"] or \
           not merged["question_fit"]["3"].get("human_judges")
    assert merged["question_fit"]["3"]["scores"] == [0]


# ---------------------------------------------------------------------------
# Tests: context_fit taken wholesale from old
# ---------------------------------------------------------------------------

def test_context_fit_taken_from_old():
    old = _make_old(
        qf_entries={},
        cf_entries={"10": _cf_human_entry(score=1), "11": _cf_human_entry(score=0)},
        bctx=["10", "11"],
    )
    new = _make_new(qf_entries={}, bctx=["10", "11"])
    merged = merge_human_scores(old, new)
    assert set(merged["context_fit"].keys()) == {"10", "11"}
    assert merged["context_fit"]["10"]["scores"] == [1]
    assert merged["context_fit"]["11"]["scores"] == [0]


def test_context_fit_empty_in_old_produces_empty_merged():
    old = _make_old(qf_entries={}, cf_entries={}, bctx=[])
    new = _make_new(qf_entries={}, bctx=[])
    merged = merge_human_scores(old, new)
    assert merged["context_fit"] == {}


# ---------------------------------------------------------------------------
# Tests: provenance comes from the new file
# ---------------------------------------------------------------------------

def test_benchmark_version_from_new():
    old = _make_old({}, {}, [])
    new = _make_new({}, [])
    merged = merge_human_scores(old, new)
    assert merged["benchmark_version"] == "0.4"


def test_reliability_source_from_new():
    old = _make_old({}, {}, [])
    new = _make_new({}, [])
    merged = merge_human_scores(old, new)
    assert "0.4" in merged["reliability_source"]


def test_book_context_qnums_from_new():
    old = _make_old({}, {}, ["10", "11", "99"])  # old (wrong) set had extra qnum 99
    new = _make_new({}, ["10", "11"])              # new (correct) set
    merged = merge_human_scores(old, new)
    assert merged["book_context_qnums"] == ["10", "11"]


# ---------------------------------------------------------------------------
# Tests: needs_human recomputed
# ---------------------------------------------------------------------------

def test_needs_human_recomputed_not_copied_from_old():
    """needs_human should reflect the merged state, not the old or new lists."""
    # Old file had needs_human that included context qnum "10" (not yet judged in old)
    old = _make_old(
        qf_entries={"1": _llm_entry(r_q=0.9)},
        cf_entries={},                          # "10" not yet judged in old
        bctx=["10"],
    )
    old["needs_human"] = [{"qnum": "10", "aspects": ["context_fit"]}]

    # New file has no human judgments yet
    new = _make_new(
        qf_entries={"1": _llm_entry(r_q=0.9)},
        bctx=["10"],
    )
    new["needs_human"] = [{"qnum": "10", "aspects": ["context_fit"]}]

    # We now inject a human context_fit for "10" into old's context_fit
    old["context_fit"] = {"10": _cf_human_entry(score=1)}

    merged = merge_human_scores(old, new)
    # "10" is in book_context_qnums AND has a human judgment → not in needs_human
    cf_needed = [item for item in merged["needs_human"] if "context_fit" in item["aspects"]]
    assert len(cf_needed) == 0


def test_high_r_q_not_in_needs_human():
    """A question with r_q well above 0.65 is not flagged."""
    old = _make_old(qf_entries={}, cf_entries={}, bctx=[])
    new = _make_new(qf_entries={"5": _llm_entry(r_q=0.95)}, bctx=[])
    merged = merge_human_scores(old, new)
    qnums_needed = {item["qnum"] for item in merged["needs_human"]}
    assert "5" not in qnums_needed


def test_low_r_q_without_human_is_in_needs_human():
    """A question with r_q below 0.65 and no human judgment is flagged."""
    old = _make_old(qf_entries={}, cf_entries={}, bctx=[])
    new = _make_new(qf_entries={"7": _llm_entry(r_q=0.50)}, bctx=[])
    merged = merge_human_scores(old, new)
    qnums_needed = {item["qnum"] for item in merged["needs_human"]}
    assert "7" in qnums_needed


def test_low_r_q_with_human_not_in_needs_human():
    """A question below threshold that has a human judgment is not re-flagged."""
    old = _make_old(
        qf_entries={"7": _human_entry(score=1)},  # human already judged
        cf_entries={},
        bctx=[],
    )
    new = _make_new(qf_entries={"7": _llm_entry(r_q=0.50)}, bctx=[])
    merged = merge_human_scores(old, new)
    qnums_needed = {item["qnum"] for item in merged["needs_human"]}
    assert "7" not in qnums_needed


# ---------------------------------------------------------------------------
# Tests: mixed realistic scenario
# ---------------------------------------------------------------------------

def test_mixed_scenario():
    """Realistic mix: some human qf, full cf, some LLM-only qf."""
    old_qf = {
        "1": _human_entry(score=1),   # human-judged (carry over)
        "2": _llm_entry(score=1),     # LLM only (use new)
        "3": _human_entry(score=0),   # human-judged (carry over)
    }
    old_cf = {
        "10": _cf_human_entry(score=1),
        "11": _cf_human_entry(score=0),
    }
    old = _make_old(old_qf, old_cf, bctx=["10", "11"])

    new_qf = {
        "1": _llm_entry(score=0),          # LLM disagrees with human — human should win
        "2": _llm_entry(score=0, r_q=0.8),
        "3": _llm_entry(score=1),          # LLM disagrees with human — human should win
        # book_context_qnums must also appear in question_fit (as in real files)
        "10": _llm_entry(score=1, r_q=0.9),
        "11": _llm_entry(score=1, r_q=0.9),
    }
    new = _make_new(new_qf, bctx=["10", "11"])
    # context_fit in new starts empty (as it would after a fresh automated run)
    new["context_fit"] = {}

    merged = merge_human_scores(old, new)

    # Human entries preserved
    assert merged["question_fit"]["1"]["judge"] == "human"
    assert merged["question_fit"]["1"]["scores"] == [1]
    assert merged["question_fit"]["3"]["judge"] == "human"
    assert merged["question_fit"]["3"]["scores"] == [0]

    # LLM-only entry kept from new
    assert "human_judges" not in merged["question_fit"]["2"]
    assert merged["question_fit"]["2"]["scores"] == [0]

    # Context fit wholesale from old
    assert len(merged["context_fit"]) == 2
    assert merged["context_fit"]["10"]["scores"] == [1]

    # Provenance from new
    assert merged["benchmark_version"] == "0.4"
    assert "0.4" in merged["reliability_source"]
    assert merged["book_context_qnums"] == ["10", "11"]

    # needs_human: qnums 1 and 3 are human-judged → not flagged;
    # context "10" and "11" are human-judged → not flagged;
    # qnum "2" has r_q=0.8 → not flagged.
    assert merged["needs_human"] == []

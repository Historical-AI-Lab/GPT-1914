"""test_human_scoring.py — Unit tests for revised human_scoring.py.

All tests are pure Python: no network, no LLM calls, no interactive I/O.

Run with:
    pytest modelasjudge/tests/test_human_scoring.py -v
"""

import json
import sys
import tempfile
from pathlib import Path
from io import StringIO
from unittest.mock import patch

import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from human_scoring import (
    _migrate_entry,
    _migrate_data,
    _pending_for_judge,
    _print_precedents,
    _record_judgment,
    _rebuild_needs_human,
    _auto_output,
    _free_gen_from_meta,
    FileCtx,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_judge_data(qf_entries=None, ctx_entries=None,
                     book_ctx_qnums=None, q_thresh=0.65,
                     candidate_model="model-A"):
    return {
        "judge_model": "test_judge",
        "candidate_model": candidate_model,
        "candidate_reasoning_effort": "none",
        "benchmark_version": "0.2",
        "thresholds": {"question_fit": q_thresh, "context_fit": q_thresh},
        "book_context_qnums": book_ctx_qnums or [],
        "question_fit": qf_entries or {},
        "context_fit": ctx_entries or {},
        "needs_human": [],
    }


def _llm_entry(r_q=1.0, score=1):
    return {
        "judge": "test_judge",
        "r_q": r_q,
        "judgments": ["tie" if score else "GT"],
        "scores": [score],
        "gt_positions": ["B"],
        "gt_indices": [0],
    }


def _human_entry_legacy(score=1, r_q=0.9):
    """Pre-migration human entry without human_judges."""
    judgment = "tie" if score else "GT"
    return {
        "judge": "human",
        "r_q": r_q,
        "judgments": [judgment],
        "scores": [score],
        "gt_positions": [None],
        "gt_indices": [None],
    }


def _make_file_ctx(data, tmp_path, candidate_model="model-A"):
    p = tmp_path / "judge_test.json"
    p.write_text(json.dumps(data))
    return FileCtx(
        judge_path=p,
        output_path=tmp_path / "judge_test_human.json",
        data=data,
        free_gen_answers={"1": {"answer": "test answer", "main_question": "Q?",
                                 "metadata_frame": "ctx", "ground_truths": ["GT"]}},
        candidate_model=candidate_model,
        candidate_reasoning_effort="none",
    )


# ---------------------------------------------------------------------------
# _migrate_entry
# ---------------------------------------------------------------------------

class TestMigrateEntry:
    def test_legacy_entry_wrapped(self):
        entry = _human_entry_legacy(score=1, r_q=0.9)
        _migrate_entry(entry, "alice")
        assert "human_judges" in entry
        assert "alice" in entry["human_judges"]
        assert entry["human_judges"]["alice"]["score"] == 1
        assert entry["human_judges"]["alice"]["judgment"] == "tie"
        assert entry["human_judges"]["alice"]["r_q"] == 0.9

    def test_non_human_entry_untouched(self):
        entry = _llm_entry(r_q=0.5)
        original = dict(entry)
        _migrate_entry(entry, "alice")
        assert "human_judges" not in entry
        assert entry == original

    def test_already_migrated_not_double_wrapped(self):
        entry = _human_entry_legacy(score=0)
        _migrate_entry(entry, "alice")
        first = entry["human_judges"]["alice"]["score"]
        _migrate_entry(entry, "bob")  # should not overwrite
        assert entry["human_judges"]["alice"]["score"] == first
        assert "bob" not in entry["human_judges"]

    def test_migrate_data_applies_to_all_aspects(self):
        data = _make_judge_data(
            qf_entries={"1": _human_entry_legacy(score=1)},
            ctx_entries={"2": _human_entry_legacy(score=0)},
        )
        _migrate_data(data, "alice")
        assert "human_judges" in data["question_fit"]["1"]
        assert "human_judges" in data["context_fit"]["2"]


# ---------------------------------------------------------------------------
# _pending_for_judge
# ---------------------------------------------------------------------------

class TestPendingForJudge:
    def test_low_r_q_is_pending(self):
        data = _make_judge_data(
            qf_entries={"1": _llm_entry(r_q=0.5)},
        )
        pending = _pending_for_judge(data, "alice")
        assert ("1", "question_fit") in pending

    def test_high_r_q_not_pending(self):
        data = _make_judge_data(
            qf_entries={"1": _llm_entry(r_q=0.9)},
        )
        pending = _pending_for_judge(data, "alice")
        assert ("1", "question_fit") not in pending

    def test_missing_r_q_is_pending(self):
        entry = {"judge": "test_judge", "scores": [1], "judgments": ["tie"],
                 "gt_positions": ["A"], "gt_indices": [0]}
        data = _make_judge_data(qf_entries={"1": entry})
        pending = _pending_for_judge(data, "alice")
        assert ("1", "question_fit") in pending

    def test_already_judged_by_alice_not_pending(self):
        # Simulate entry already scored by alice: judge="human", human_judges set
        entry = _llm_entry(r_q=0.5)
        entry["judge"] = "human"
        entry["r_q"] = 0.9
        entry["human_judges"] = {"alice": {"score": 1, "judgment": "tie",
                                            "reason": "", "r_q": 0.9,
                                            "timestamp": None}}
        data = _make_judge_data(qf_entries={"1": entry})
        pending = _pending_for_judge(data, "alice")
        assert ("1", "question_fit") not in pending

    def test_second_judge_still_pending_after_first(self):
        entry = _llm_entry(r_q=0.5)
        # Simulate first judge having scored it (representative top-level set)
        entry["judge"] = "human"
        entry["r_q"] = 0.9
        entry["human_judges"] = {"alice": {"score": 1, "judgment": "tie",
                                            "reason": "", "r_q": 0.9,
                                            "timestamp": None}}
        data = _make_judge_data(qf_entries={"1": entry})
        pending = _pending_for_judge(data, "bob")
        assert ("1", "question_fit") in pending

    def test_book_context_always_pending(self):
        data = _make_judge_data(
            qf_entries={"5": _llm_entry(r_q=1.0)},
            ctx_entries={"5": _llm_entry(r_q=1.0)},
            book_ctx_qnums=[5],
        )
        pending = _pending_for_judge(data, "alice")
        qnums_aspects = [(q, a) for q, a in pending]
        assert ("5", "context_fit") in qnums_aspects
        # question_fit with high r_q is NOT pending
        assert ("5", "question_fit") not in qnums_aspects

    def test_book_context_not_pending_if_already_judged(self):
        ctx_entry = _llm_entry(r_q=1.0)
        ctx_entry["judge"] = "human"
        ctx_entry["human_judges"] = {"alice": {"score": 0, "judgment": "GT",
                                                "reason": "", "r_q": 0.9,
                                                "timestamp": None}}
        data = _make_judge_data(
            ctx_entries={"5": ctx_entry},
            book_ctx_qnums=[5],
        )
        pending = _pending_for_judge(data, "alice")
        assert ("5", "context_fit") not in pending


# ---------------------------------------------------------------------------
# _record_judgment — multi-judge schema
# ---------------------------------------------------------------------------

class TestRecordJudgment:
    def test_first_judge_sets_representative(self, tmp_path):
        data = _make_judge_data(qf_entries={"1": _llm_entry(r_q=0.5)})
        ctx = _make_file_ctx(data, tmp_path, "model-A")
        log_path = tmp_path / "log.jsonl"
        log_records = []

        _record_judgment(ctx, "1", "question_fit", "alice", 1, "good", 0.9,
                         log_path, log_records)

        entry = data["question_fit"]["1"]
        assert entry["judge"] == "human"
        assert entry["scores"] == [1]
        assert entry["r_q"] == 0.9
        assert "alice" in entry["human_judges"]

    def test_second_judge_does_not_overwrite_representative(self, tmp_path):
        data = _make_judge_data(qf_entries={"1": _llm_entry(r_q=0.5)})
        ctx = _make_file_ctx(data, tmp_path, "model-A")
        log_path = tmp_path / "log.jsonl"
        log_records = []

        _record_judgment(ctx, "1", "question_fit", "alice", 1, "good", 0.9,
                         log_path, log_records)
        _record_judgment(ctx, "1", "question_fit", "bob", 0, "disagree", 0.85,
                         log_path, log_records)

        entry = data["question_fit"]["1"]
        # Top-level remains from alice (first writer)
        assert entry["scores"] == [1]
        assert entry["r_q"] == 0.9
        # Both judges in human_judges
        assert entry["human_judges"]["alice"]["score"] == 1
        assert entry["human_judges"]["bob"]["score"] == 0

    def test_log_records_judge_id_and_model(self, tmp_path):
        data = _make_judge_data(qf_entries={"1": _llm_entry(r_q=0.5)})
        ctx = _make_file_ctx(data, tmp_path, "model-X")
        log_path = tmp_path / "log.jsonl"
        log_records = []

        _record_judgment(ctx, "1", "question_fit", "carol", 0, "reason", 0.8,
                         log_path, log_records)

        assert len(log_records) == 1
        r = log_records[0]
        assert r["judge_id"] == "carol"
        assert r["candidate_model"] == "model-X"
        assert r["score"] == 0
        assert "timestamp" in r

        # Also written to file
        lines = log_path.read_text().strip().split("\n")
        assert len(lines) == 1
        parsed = json.loads(lines[0])
        assert parsed["judge_id"] == "carol"

    def test_log_contains_candidate_reasoning_effort(self, tmp_path):
        data = _make_judge_data(qf_entries={"1": _llm_entry(r_q=0.5)})
        data["candidate_reasoning_effort"] = "medium"
        ctx = _make_file_ctx(data, tmp_path, "model-A")
        ctx = FileCtx(
            judge_path=ctx.judge_path,
            output_path=ctx.output_path,
            data=data,
            free_gen_answers=ctx.free_gen_answers,
            candidate_model="model-A",
            candidate_reasoning_effort="medium",
        )
        log_path = tmp_path / "log.jsonl"
        _record_judgment(ctx, "1", "question_fit", "alice", 1, "", 0.9,
                         log_path, [])
        r = json.loads(log_path.read_text())
        assert r["candidate_reasoning_effort"] == "medium"


# ---------------------------------------------------------------------------
# _print_precedents — blinding + same-model exclusion
# ---------------------------------------------------------------------------

class TestPrintPrecedents:
    def _capture(self, log_records, qnum, aspect, current_model):
        buf = StringIO()
        with patch("sys.stdout", buf):
            _print_precedents(log_records, qnum, aspect, current_model)
        return buf.getvalue()

    def test_same_model_excluded(self):
        records = [
            {"qnum": "1", "aspect": "question_fit", "score": 1,
             "candidate_model": "model-A", "reason": "good"},
        ]
        out = self._capture(records, "1", "question_fit", current_model="model-A")
        assert "good" not in out
        assert "no prior judgments" in out

    def test_other_model_shown_as_another_model(self):
        records = [
            {"qnum": "1", "aspect": "question_fit", "score": 1,
             "candidate_model": "model-B", "reason": "fits well"},
        ]
        out = self._capture(records, "1", "question_fit", current_model="model-A")
        assert "another model" in out
        assert "model-B" not in out
        assert "fits well" in out

    def test_capped_at_three(self):
        records = [
            {"qnum": "1", "aspect": "question_fit", "score": 1,
             "candidate_model": "model-B", "reason": f"reason-{i}"}
            for i in range(5)
        ]
        out = self._capture(records, "1", "question_fit", current_model="model-A")
        # Only last 3 should appear
        assert "reason-4" in out
        assert "reason-3" in out
        assert "reason-2" in out
        assert "reason-1" not in out
        assert "reason-0" not in out

    def test_no_records_shows_empty_message(self):
        out = self._capture([], "99", "question_fit", current_model="model-A")
        assert "no prior judgments" in out

    def test_model_name_never_printed(self):
        records = [
            {"qnum": "1", "aspect": "context_fit", "score": 0,
             "candidate_model": "secret-model-Z", "reason": "mismatch"},
        ]
        out = self._capture(records, "1", "context_fit", current_model="model-A")
        assert "secret-model-Z" not in out


# ---------------------------------------------------------------------------
# _rebuild_needs_human
# ---------------------------------------------------------------------------

class TestRebuildNeedsHuman:
    def test_human_judged_removed(self):
        entry = _llm_entry(r_q=0.5)
        entry["judge"] = "human"
        entry["human_judges"] = {"alice": {}}
        data = _make_judge_data(qf_entries={"1": entry})
        _rebuild_needs_human(data)
        assert data["needs_human"] == []

    def test_low_r_q_still_in_needs_human(self):
        data = _make_judge_data(qf_entries={"1": _llm_entry(r_q=0.4)})
        _rebuild_needs_human(data)
        assert any(item["qnum"] == "1" for item in data["needs_human"])

    def test_book_context_included(self):
        data = _make_judge_data(
            ctx_entries={"5": _llm_entry(r_q=0.9)},
            book_ctx_qnums=[5],
        )
        _rebuild_needs_human(data)
        item = next(i for i in data["needs_human"] if i["qnum"] == "5")
        assert "context_fit" in item["aspects"]


# ---------------------------------------------------------------------------
# Migration integration
# ---------------------------------------------------------------------------

class TestMigrationIntegration:
    def test_legacy_file_second_judge_does_not_clobber(self, tmp_path):
        """A pre-existing _human.json without human_judges should be migrated
        so a second judge's record accumulates rather than destroying the first."""
        # Simulate what's on disk: already-judged by first judge, no human_judges
        entry = _human_entry_legacy(score=1, r_q=0.9)
        data = _make_judge_data(qf_entries={"1": entry})

        _migrate_data(data, default_judge_id="human")

        # Now second judge scores
        ctx = _make_file_ctx(data, tmp_path)
        log_records = []
        _record_judgment(ctx, "1", "question_fit", "bob", 0, "disagree", 0.85,
                         tmp_path / "log.jsonl", log_records)

        entry_out = data["question_fit"]["1"]
        # First-writer top-level preserved (was "human" / alice legacy)
        assert entry_out["scores"] == [1]
        assert entry_out["r_q"] == 0.9
        # Bob's entry added
        assert entry_out["human_judges"]["bob"]["score"] == 0
        # Original legacy judge also present
        assert "human" in entry_out["human_judges"]


# ---------------------------------------------------------------------------
# _auto_output
# ---------------------------------------------------------------------------

class TestAutoOutput:
    def test_adds_human_suffix(self, tmp_path):
        p = tmp_path / "judge_foo__bar__0.2.json"
        assert _auto_output(p).name == "judge_foo__bar__0.2_human.json"

    def test_idempotent_on_human_suffix(self, tmp_path):
        p = tmp_path / "judge_foo__bar__0.2_human.json"
        assert _auto_output(p).name == "judge_foo__bar__0.2_human.json"

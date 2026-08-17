"""test_substantive_ledger.py — CSV upsert semantics (spec §6, plan §6)."""

import csv
import sys
from pathlib import Path

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from substantive.ledger import KEY_COLUMNS, append_history, upsert_row


def _row(**overrides):
    base = dict(benchmark_version="0.7", candidate_label="gpt-5.4", candidate_effort="medium",
               judge="anthropic/claude-sonnet-4-6", judge_effort="medium", bt_tag="tag1",
               passfail=0.5, run_date="2026-08-17")
    base.update(overrides)
    return base


def _read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


class TestUpsert:
    def test_upsert_twice_same_key_replaces(self, tmp_path):
        path = tmp_path / "ledger.csv"
        upsert_row(_row(passfail=0.5), path=path)
        upsert_row(_row(passfail=0.7), path=path)
        rows = _read(path)
        assert len(rows) == 1
        assert rows[0]["passfail"] == "0.7"

    def test_different_bt_tag_makes_two_rows(self, tmp_path):
        path = tmp_path / "ledger.csv"
        upsert_row(_row(bt_tag="tag1"), path=path)
        upsert_row(_row(bt_tag="tag2"), path=path)
        rows = _read(path)
        assert len(rows) == 2

    def test_run_date_not_in_key_still_replaces(self, tmp_path):
        """run_date, seed, n_boot are deliberately not part of the key."""
        path = tmp_path / "ledger.csv"
        upsert_row(_row(run_date="2026-08-01"), path=path)
        upsert_row(_row(run_date="2026-08-17"), path=path)
        rows = _read(path)
        assert len(rows) == 1
        assert rows[0]["run_date"] == "2026-08-17"

    def test_unknown_preexisting_column_preserved(self, tmp_path):
        path = tmp_path / "ledger.csv"
        upsert_row(_row(some_future_column="kept"), path=path)
        upsert_row(_row(bt_tag="tag2"), path=path)
        rows = _read(path)
        assert all(r.get("some_future_column", "") in ("kept", "") for r in rows)
        kept_rows = [r for r in rows if r.get("some_future_column") == "kept"]
        assert len(kept_rows) == 1

    def test_new_column_backfilled_on_old_rows(self, tmp_path):
        path = tmp_path / "ledger.csv"
        upsert_row(_row(bt_tag="tag1"), path=path)
        upsert_row(_row(bt_tag="tag2", brand_new_metric=0.9), path=path)
        rows = _read(path)
        by_tag = {r["bt_tag"]: r for r in rows}
        assert by_tag["tag1"]["brand_new_metric"] == ""
        assert by_tag["tag2"]["brand_new_metric"] == "0.9"

    def test_no_tmp_file_left_behind(self, tmp_path):
        path = tmp_path / "ledger.csv"
        upsert_row(_row(), path=path)
        upsert_row(_row(bt_tag="tag2"), path=path)
        assert not path.with_suffix(".csv.tmp").exists()
        assert not list(tmp_path.glob("*.tmp"))

    def test_deterministic_row_order(self, tmp_path):
        path = tmp_path / "ledger.csv"
        for tag in ("zzz", "aaa", "mmm"):
            upsert_row(_row(bt_tag=tag), path=path)
        rows = _read(path)
        assert [r["bt_tag"] for r in rows] == ["aaa", "mmm", "zzz"]

    def test_key_columns_are_the_documented_six(self):
        assert KEY_COLUMNS == ["benchmark_version", "candidate_label", "candidate_effort",
                               "judge", "judge_effort", "bt_tag"]


class TestAppendHistory:
    def test_appends_one_line_per_call(self, tmp_path):
        path = tmp_path / "history.jsonl"
        append_history({"a": 1}, path=path)
        append_history({"a": 2}, path=path)
        lines = path.read_text().strip().split("\n")
        assert len(lines) == 2

    def test_never_rewrites_prior_lines(self, tmp_path):
        path = tmp_path / "history.jsonl"
        append_history({"a": 1}, path=path)
        first_write = path.read_text()
        append_history({"a": 2}, path=path)
        assert path.read_text().startswith(first_write)

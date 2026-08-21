"""test_substantive_ledger.py — CSV upsert semantics (spec §6, plan §6)."""

import csv
import sys
from pathlib import Path

import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from substantive.ledger import KEY_COLUMNS, RETIRED_COLUMNS, append_history, merge_columns, upsert_row


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


class TestUpsertPreservesStyleColumns:
    def test_upsert_preserves_style_columns_from_replaced_row(self, tmp_path):
        """The wipe regression pin: re-running a stage that writes no
        style_* keys (e.g. score_substantive.py stage 11) must NOT blank
        out style columns written by a different stage/process earlier."""
        path = tmp_path / "ledger.csv"
        upsert_row(_row(style_period_fidelity="82.4", style_w1="0.071"), path=path)
        # A later upsert (simulating score_substantive re-run) supplies no
        # style_* keys at all.
        upsert_row(_row(passfail=0.9), path=path)
        rows = _read(path)
        assert len(rows) == 1
        assert rows[0]["style_period_fidelity"] == "82.4"
        assert rows[0]["style_w1"] == "0.071"
        assert rows[0]["passfail"] == "0.9"

    def test_upsert_does_not_preserve_columns_the_new_row_supplies(self, tmp_path):
        path = tmp_path / "ledger.csv"
        upsert_row(_row(style_period_fidelity="82.4"), path=path)
        upsert_row(_row(style_period_fidelity="91.0"), path=path)
        rows = _read(path)
        assert len(rows) == 1
        assert rows[0]["style_period_fidelity"] == "91.0"

    def test_retired_column_dropped_from_header(self, tmp_path):
        path = tmp_path / "ledger.csv"
        # Simulate an old CSV on disk carrying the retired column as a header.
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(KEY_COLUMNS + ["passfail", "style_p_fused"])
            writer.writerow(["0.7", "gpt-5.4", "medium", "j", "medium", "tag1", "0.5", "0.3"])
        upsert_row(_row(bt_tag="tag2"), path=path)
        rows = _read(path)
        assert "style_p_fused" not in rows[0].keys()

    def test_rogan_gladen_era_columns_are_retired(self, tmp_path):
        """direct-binary-scoring-spec.md retires the correction; its six
        columns (plus the two already-dead mean_beta/mean_informativeness
        headers) must never resurrect as empty columns."""
        rg_columns = {"alpha_prior", "n_excluded_floor", "clip_rate",
                     "near_floor_frac", "sigma_u", "mean_alpha",
                     "mean_beta", "mean_informativeness"}
        assert rg_columns <= RETIRED_COLUMNS

        path = tmp_path / "ledger.csv"
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(KEY_COLUMNS + ["passfail", "alpha_prior", "sigma_u"])
            writer.writerow(["0.7", "gpt-5.4", "medium", "j", "medium", "tag1", "0.5", "jeffreys", "0.4"])
        upsert_row(_row(bt_tag="tag2"), path=path)
        rows = _read(path)
        assert "alpha_prior" not in rows[0].keys()
        assert "sigma_u" not in rows[0].keys()

    def test_new_binary_columns_present(self, tmp_path):
        path = tmp_path / "ledger.csv"
        upsert_row(_row(n_binary_pass=500, n_binary_fail=40, n_binary_split=7,
                        scoring_version="direct_binary_v1"), path=path)
        rows = _read(path)
        assert rows[0]["n_binary_pass"] == "500"
        assert rows[0]["n_binary_fail"] == "40"
        assert rows[0]["n_binary_split"] == "7"
        assert rows[0]["scoring_version"] == "direct_binary_v1"


class TestMergeColumns:
    def test_merge_only_touches_named_columns(self, tmp_path):
        path = tmp_path / "ledger.csv"
        upsert_row(_row(passfail=0.5, run_date="2026-08-01"), path=path)
        key = {c: _row()[c] for c in KEY_COLUMNS}
        ok = merge_columns(key, {"style_period_fidelity": "82.4"}, path=path)
        assert ok
        rows = _read(path)
        assert len(rows) == 1
        assert rows[0]["style_period_fidelity"] == "82.4"
        assert rows[0]["passfail"] == "0.5"
        assert rows[0]["run_date"] == "2026-08-01"

    def test_incomplete_key_raises(self, tmp_path):
        path = tmp_path / "ledger.csv"
        upsert_row(_row(), path=path)
        incomplete_key = {c: _row()[c] for c in KEY_COLUMNS[:-1]}  # missing bt_tag
        with pytest.raises(ValueError):
            merge_columns(incomplete_key, {"style_w1": "0.07"}, path=path)

    def test_updates_touching_a_key_column_raises(self, tmp_path):
        path = tmp_path / "ledger.csv"
        upsert_row(_row(), path=path)
        key = {c: _row()[c] for c in KEY_COLUMNS}
        with pytest.raises(ValueError):
            merge_columns(key, {"bt_tag": "other-tag"}, path=path)

    def test_absent_key_returns_false_and_writes_nothing(self, tmp_path):
        path = tmp_path / "ledger.csv"
        upsert_row(_row(bt_tag="tag1"), path=path)
        before = path.read_text()
        key = {c: _row(bt_tag="tag-nonexistent")[c] for c in KEY_COLUMNS}
        ok = merge_columns(key, {"style_w1": "0.07"}, path=path)
        assert ok is False
        assert path.read_text() == before

    def test_create_missing_inserts_a_new_row(self, tmp_path):
        path = tmp_path / "ledger.csv"
        upsert_row(_row(bt_tag="tag1"), path=path)
        key = {c: _row(bt_tag="tag-new")[c] for c in KEY_COLUMNS}
        ok = merge_columns(key, {"style_w1": "0.07"}, path=path, create_missing=True)
        assert ok
        rows = _read(path)
        assert len(rows) == 2
        new_row = next(r for r in rows if r["bt_tag"] == "tag-new")
        assert new_row["style_w1"] == "0.07"

    def test_key_values_compared_as_strings(self, tmp_path):
        path = tmp_path / "ledger.csv"
        upsert_row(_row(candidate_effort="medium"), path=path)
        key = {c: _row()[c] for c in KEY_COLUMNS}
        key["prior_scale_typo"] = None  # noise key, ignored since not in updates check
        ok = merge_columns(key, {"style_w1": "0.07"}, path=path)
        assert ok
        rows = _read(path)
        assert rows[0]["style_w1"] == "0.07"


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

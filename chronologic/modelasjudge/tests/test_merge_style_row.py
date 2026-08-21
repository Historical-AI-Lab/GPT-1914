"""test_merge_style_row.py — key resolution + STYLE_LEDGER_MAP correctness
for merge_style_row.py (plan §4/§6)."""

import json
import sys
from pathlib import Path

import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

import merge_style_row as msr
from substantive import ledger


def _synthetic_style_json(**overrides):
    data = {
        "schema_version": "stylejudge-2.0",
        "model": {"name": "gpt-5.4", "candidate_label": "gpt-5.4", "candidate_model": "gpt-5.4-raw",
                  "benchmark_version": "0.7", "n_answers": 662},
        "e1": {
            "headline": {"name": "period_fidelity", "score": 89.1, "ci95": [83.6, 93.2]},
            "wasserstein": {"w1_observed": 0.0652, "w1_ci95": [0.045, 0.092],
                           "w1_null_mean": 0.0122, "w1_null_sd": 0.0051,
                           "w1_null_ci95": [0.006, 0.023], "normalized_excess_distance": 0.109},
            "years": {"drift_mean": -5.96, "drift_ci95": [-8.01, -4.14],
                     "dispersion_mae": 19.12, "dispersion_ci95": [18.04, 20.24],
                     "drift_mean_raw": -19.36, "dispersion_mae_raw": 29.47,
                     "null_drift_mean": -13.36, "null_dispersion_mae": 27.08,
                     "baseline_correction": "per_answer_window_mean"},
            "conformal": {"drift": 0.4348, "drift_ci95": [0.4081, 0.4547], "drift_null_center": 0.5,
                         "dispersion": 0.2495, "dispersion_ci95": [0.2401, 0.2618],
                         "dispersion_null_center": 0.25},
        },
        "e2": {
            "headline": {"name": "authenticity_fidelity", "score": 28.0, "ci95": [24.2, 30.9]},
            "conformal": {"mean_q": 0.8578, "mean_q_ci95": [0.8431, 0.8773],
                         "null_center": 0.4926, "null_center_source": "pseudo_model_mean"},
        },
        "diagnostics": {"ks": 0.1071, "ks_null_mean": 0.0342,
                       "median_window_n_volumes": 73, "thin_cell_frac": 0.024},
        "bootstrap": {"n_boot": 1000, "seed": 20260809},
        "provenance": {"style_run_id": "abc123def4567890"},
    }
    data.update(overrides)
    return data


# ---------------------------------------------------------------------------
# STYLE_LEDGER_MAP coverage
# ---------------------------------------------------------------------------

def test_style_ledger_map_covers_every_style_column_in_ledger_columns():
    style_columns = [c for c in ledger.COLUMNS if c.startswith("style_")]
    assert set(style_columns) == set(msr.STYLE_LEDGER_MAP.keys())


# ---------------------------------------------------------------------------
# _get_path / build_updates mapping correctness
# ---------------------------------------------------------------------------

def test_build_updates_maps_every_field_correctly():
    style_data = _synthetic_style_json()
    updates = msr.build_updates(style_data)
    assert updates["style_cohort_id"] == "abc123def4567890"
    assert updates["style_period_fidelity"] == 89.1
    assert updates["style_period_fidelity_lo"] == 83.6
    assert updates["style_period_fidelity_hi"] == 93.2
    assert updates["style_authenticity_fidelity"] == 28.0
    assert updates["style_authenticity_fidelity_lo"] == 24.2
    assert updates["style_authenticity_fidelity_hi"] == 30.9
    assert updates["style_w1"] == 0.0652
    assert updates["style_w1_null_mean"] == 0.0122
    assert updates["style_drift_years"] == -5.96
    assert updates["style_dispersion_mae"] == 19.12
    assert updates["style_T_drift"] == 0.4348
    assert updates["style_T_disp"] == 0.2495
    assert updates["style_T_E2"] == 0.8578
    assert updates["style_T_KS"] == 0.1071


# ---------------------------------------------------------------------------
# key resolution
# ---------------------------------------------------------------------------

class _Args:
    scored_file = None
    benchmark_version = None
    candidate_label = None
    candidate_effort = None
    judge = None
    judge_effort = None
    bt_tag = None


def test_resolve_key_from_style_json_alone_is_incomplete():
    args = _Args()
    key = msr.resolve_key(args, _synthetic_style_json())
    assert key["benchmark_version"] == "0.7"
    assert key["candidate_label"] == "gpt-5.4"
    assert msr._missing_key_columns(key) == ["candidate_effort", "judge", "judge_effort", "bt_tag"]


def test_resolve_key_from_scored_file(tmp_path):
    scored_path = tmp_path / "judge_j__gpt-5.4__0.7__c-medium__j-medium.json"
    scored_path.write_text(json.dumps({
        "judge_model": "anthropic/claude-sonnet-4-6", "candidate_label": "gpt-5.4",
        "candidate_model": "gpt-5.4-raw", "candidate_reasoning_effort": "medium",
        "benchmark_version": "0.7", "reasoning_effort": "medium",
    }), encoding="utf-8")
    bt_path = tmp_path / f"{scored_path.stem}_btcontext.json"
    bt_path.write_text(json.dumps({"bt_context": {"artifacts_tag": "tag-xyz"}}), encoding="utf-8")

    args = _Args()
    args.scored_file = str(scored_path)
    key = msr.resolve_key(args, _synthetic_style_json())
    assert key == {
        "benchmark_version": "0.7", "candidate_label": "gpt-5.4", "candidate_effort": "medium",
        "judge": "anthropic/claude-sonnet-4-6", "judge_effort": "medium", "bt_tag": "tag-xyz",
    }
    assert msr._missing_key_columns(key) == []


def test_explicit_flags_override_scored_file(tmp_path):
    scored_path = tmp_path / "judge_j__gpt-5.4__0.7__c-medium__j-medium.json"
    scored_path.write_text(json.dumps({
        "judge_model": "anthropic/claude-sonnet-4-6", "candidate_label": "gpt-5.4",
        "candidate_reasoning_effort": "medium", "benchmark_version": "0.7",
        "reasoning_effort": "medium",
    }), encoding="utf-8")

    args = _Args()
    args.scored_file = str(scored_path)
    args.bt_tag = "explicit-tag-wins"
    key = msr.resolve_key(args, _synthetic_style_json())
    assert key["bt_tag"] == "explicit-tag-wins"


# ---------------------------------------------------------------------------
# main(): schema rejection, incomplete key, dry-run, exit codes
# ---------------------------------------------------------------------------

def test_main_rejects_wrong_schema_version(tmp_path, capsys):
    style_path = tmp_path / "style.json"
    style_path.write_text(json.dumps(_synthetic_style_json(schema_version="typicality-1.0")),
                          encoding="utf-8")
    with pytest.raises(SystemExit):
        msr.main(["--style-json", str(style_path)])


def test_main_incomplete_key_exits_zero_and_writes_nothing(tmp_path, monkeypatch, capsys):
    style_path = tmp_path / "style.json"
    style_path.write_text(json.dumps(_synthetic_style_json()), encoding="utf-8")
    ledger_path = tmp_path / "ledger.csv"
    monkeypatch.setattr(msr.substantive_artifacts, "ledger_path", lambda: ledger_path)

    rc = msr.main(["--style-json", str(style_path)])
    assert rc == 0
    assert not ledger_path.exists()
    out = capsys.readouterr().out
    assert "incomplete key" in out


def test_main_incomplete_key_with_require_ledger_exits_one(tmp_path):
    style_path = tmp_path / "style.json"
    style_path.write_text(json.dumps(_synthetic_style_json()), encoding="utf-8")
    rc = msr.main(["--style-json", str(style_path), "--require-ledger"])
    assert rc == 1


def test_main_dry_run_writes_nothing_even_with_complete_key(tmp_path, monkeypatch):
    style_path = tmp_path / "style.json"
    style_path.write_text(json.dumps(_synthetic_style_json()), encoding="utf-8")
    ledger_path = tmp_path / "ledger.csv"
    monkeypatch.setattr(msr.substantive_artifacts, "ledger_path", lambda: ledger_path)

    rc = msr.main(["--style-json", str(style_path), "--dry-run",
                  "--candidate-effort", "medium", "--judge", "j", "--judge-effort", "medium",
                  "--bt-tag", "tag1"])
    assert rc == 0
    assert not ledger_path.exists()


def test_main_complete_key_no_matching_row_exits_two(tmp_path, monkeypatch):
    style_path = tmp_path / "style.json"
    style_path.write_text(json.dumps(_synthetic_style_json()), encoding="utf-8")
    ledger_path = tmp_path / "ledger.csv"
    monkeypatch.setattr(msr.substantive_artifacts, "ledger_path", lambda: ledger_path)

    rc = msr.main(["--style-json", str(style_path), "--candidate-effort", "medium",
                  "--judge", "j", "--judge-effort", "medium", "--bt-tag", "tag1"])
    assert rc == 2


def test_main_complete_key_with_create_missing_writes_row(tmp_path, monkeypatch):
    style_path = tmp_path / "style.json"
    style_path.write_text(json.dumps(_synthetic_style_json()), encoding="utf-8")
    ledger_path = tmp_path / "ledger.csv"
    monkeypatch.setattr(msr.substantive_artifacts, "ledger_path", lambda: ledger_path)

    rc = msr.main(["--style-json", str(style_path), "--candidate-effort", "medium",
                  "--judge", "j", "--judge-effort", "medium", "--bt-tag", "tag1",
                  "--create-missing"])
    assert rc == 0
    assert ledger_path.exists()

    import csv
    rows = list(csv.DictReader(open(ledger_path, newline="")))
    assert len(rows) == 1
    assert rows[0]["style_period_fidelity"] == "89.1"
    assert rows[0]["candidate_label"] == "gpt-5.4"


def test_main_merges_into_existing_row_leaving_other_columns(tmp_path, monkeypatch):
    style_path = tmp_path / "style.json"
    style_path.write_text(json.dumps(_synthetic_style_json()), encoding="utf-8")
    ledger_path = tmp_path / "ledger.csv"
    monkeypatch.setattr(msr.substantive_artifacts, "ledger_path", lambda: ledger_path)

    ledger.upsert_row({
        "benchmark_version": "0.7", "candidate_label": "gpt-5.4", "candidate_effort": "medium",
        "judge": "j", "judge_effort": "medium", "bt_tag": "tag1", "passfail": "0.62",
    }, path=ledger_path)

    rc = msr.main(["--style-json", str(style_path), "--candidate-effort", "medium",
                  "--judge", "j", "--judge-effort", "medium", "--bt-tag", "tag1"])
    assert rc == 0

    import csv
    rows = list(csv.DictReader(open(ledger_path, newline="")))
    assert len(rows) == 1
    assert rows[0]["passfail"] == "0.62"
    assert rows[0]["style_period_fidelity"] == "89.1"

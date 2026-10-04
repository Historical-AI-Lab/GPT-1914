"""
Unit tests for stylejudge/date_corpus_prep.py and stylejudge/date_predictor_deberta.py.

Fixture-only, no GPU, no network, no model artifact. Exercises the Phase E3
metadata + split + abstention logic:

  - MARC date-type exclusion set and barcode normalization
  - fpub_final override + date_catalog preservation
  - length-table fragment_share zeroing (weights untouched, still sum to 1)
  - split inheritance from an E1 splits.json (author-group adoption + conflicts)
  - soft-label construction against the shared date_predictor grid
  - the fragment abstention predicate used by `score`

Run:
    pytest stylejudge/tests/test_date_predictor_deberta.py -v
"""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "stylejudge"))

import date_corpus_prep as dcp          # noqa: E402
import date_predictor_deberta as dpd    # noqa: E402
import date_predictor as dp             # noqa: E402


# ---------------------------------------------------------------------------
# date-type exclusion + barcode normalization
# ---------------------------------------------------------------------------

def _roster_row(vid, tier="idi", date="1850", decade="1850"):
    return {"volume_id": vid, "collection": "idi_fill", "tier": tier,
            "path": f"/x/{vid}.txt", "title": "T", "author": "A",
            "date": date, "decade": decade, "selection_rank": "1", "word_count": "500"}


def test_build_dated_roster_drops_continuing_resources_keeps_singles():
    rows = [_roster_row("AAA"), _roster_row("BBB"), _roster_row("CCC")]
    date_types = {
        "AAA": "Single known date/probable date",
        "BBB": "Continuing resource ceased publication (Dead status)",
        "CCC": "Multiple dates",
    }
    kept, stats = dcp.build_dated_roster(rows, date_types, corrected={},
                                         keep_types=dcp.DEFAULT_KEEP_DATE_TYPES,
                                         apply_correction=False)
    kept_ids = {r["volume_id"] for r in kept}
    assert kept_ids == {"AAA", "CCC"}
    assert stats["n_dropped"] == 1
    assert stats["dropped_by_type"] == {
        "Continuing resource ceased publication (Dead status)": 1}
    assert stats["idi_without_type"] == []


def test_non_idi_tiers_never_excluded_and_get_empty_date_type():
    rows = [_roster_row("COHA1", tier="additive"),
            _roster_row("ECCO1", tier="ecco")]
    kept, stats = dcp.build_dated_roster(rows, date_types={}, corrected={},
                                         keep_types=dcp.DEFAULT_KEEP_DATE_TYPES,
                                         apply_correction=False)
    assert len(kept) == 2
    assert all(r["date_type"] == "" for r in kept)
    assert stats["idi_without_type"] == []


def test_idi_volume_without_date_type_is_flagged_not_silently_kept():
    rows = [_roster_row("AAA"), _roster_row("NOCODE")]
    date_types = {"AAA": "Single known date/probable date"}
    kept, stats = dcp.build_dated_roster(rows, date_types, corrected={},
                                         keep_types=dcp.DEFAULT_KEEP_DATE_TYPES,
                                         apply_correction=False)
    assert {r["volume_id"] for r in kept} == {"AAA"}
    assert stats["idi_without_type"] == ["NOCODE"]


def test_load_date_types_normalizes_barcodes(tmp_path):
    s1000 = tmp_path / "sample1000.csv"
    s1000.write_text(
        "﻿barcode_src,date_format\n"
        "hvd.hn1eg5,Single known date/probable date\n",
        encoding="utf-8")
    fill = tmp_path / "idi_fill_metadata_1800-1899.csv"
    fill.write_text(
        "barcode_src,date_types_src\n"
        "HW3PYH,Multiple dates\n",
        encoding="utf-8")
    date_types, conflicts, paths = dcp.load_date_types(str(s1000),
                                                       str(tmp_path / "idi_fill_metadata_*.csv"))
    assert date_types == {"HN1EG5": "Single known date/probable date",
                          "HW3PYH": "Multiple dates"}
    assert conflicts == []
    assert len(paths) == 1


def test_load_date_types_reports_conflicts_first_wins(tmp_path):
    s1000 = tmp_path / "sample1000.csv"
    s1000.write_text("barcode_src,date_format\nAAA,Single known date/probable date\n",
                     encoding="utf-8")
    fill = tmp_path / "idi_fill_metadata_x.csv"
    fill.write_text("barcode_src,date_types_src\nAAA,Multiple dates\n", encoding="utf-8")
    date_types, conflicts, _ = dcp.load_date_types(
        str(s1000), str(tmp_path / "idi_fill_metadata_*.csv"))
    assert date_types["AAA"] == "Single known date/probable date"  # first wins
    assert len(conflicts) == 1


# ---------------------------------------------------------------------------
# fpub_final override + date_catalog preservation
# ---------------------------------------------------------------------------

def test_fpub_final_override_preserves_catalog_date():
    rows = [_roster_row("AAA", date="1855", decade="1850"),
            _roster_row("BBB", date="1855", decade="1850")]
    date_types = {"AAA": "Multiple dates", "BBB": "Multiple dates"}
    corrected = {"AAA": 1832.0}  # moves > 20 yr, crosses a decade boundary
    kept, stats = dcp.build_dated_roster(rows, date_types, corrected,
                                         keep_types=dcp.DEFAULT_KEEP_DATE_TYPES,
                                         apply_correction=True)
    by_id = {r["volume_id"]: r for r in kept}
    assert by_id["AAA"]["date_catalog"] == "1855"
    assert by_id["AAA"]["date"] == "1832"
    assert by_id["AAA"]["decade"] == "1830"
    # unmatched row keeps catalog date, but still records date_catalog
    assert by_id["BBB"]["date_catalog"] == "1855"
    assert by_id["BBB"]["date"] == "1855"
    assert stats["n_corrected"] == 1
    assert stats["n_moved"] == 1
    assert stats["n_moved_gt20"] == 1
    assert stats["n_cross_decade"] == 1


def test_no_date_correction_flag_skips_join():
    rows = [_roster_row("AAA", date="1855")]
    kept, stats = dcp.build_dated_roster(rows, {"AAA": "Multiple dates"},
                                         corrected={"AAA": 1800.0},
                                         keep_types=dcp.DEFAULT_KEEP_DATE_TYPES,
                                         apply_correction=False)
    assert kept[0]["date"] == "1855"
    assert kept[0]["date_catalog"] == "1855"
    assert stats["n_corrected"] == 0


# ---------------------------------------------------------------------------
# length-table
# ---------------------------------------------------------------------------

def test_length_table_zeros_fragment_share_leaves_weights(tmp_path):
    src = {
        "word_bin_edges": [5, 10, 15],
        "joint": [
            {"sentences": 1, "word_bin": [5, 10], "weight": 0.4, "fragment_share": 0.61},
            {"sentences": 1, "word_bin": [10, 15], "weight": 0.35, "fragment_share": 0.29},
            {"sentences": 2, "word_bin": [15, 25], "weight": 0.25, "fragment_share": 0.0},
        ],
    }
    in_path = tmp_path / "length_distribution.json"
    out_path = tmp_path / "length_distribution_sentences.json"
    in_path.write_text(json.dumps(src), encoding="utf-8")

    rc = dcp.main(["length-table", "--in", str(in_path), "--out", str(out_path)])
    assert rc == 0
    out = json.loads(out_path.read_text())
    assert all(e["fragment_share"] == 0.0 for e in out["joint"])
    assert [e["weight"] for e in out["joint"]] == [0.4, 0.35, 0.25]
    assert [e["word_bin"] for e in out["joint"]] == [[5, 10], [10, 15], [15, 25]]
    assert sum(e["weight"] for e in out["joint"]) == pytest.approx(1.0)
    assert out["word_bin_edges"] == [5, 10, 15]  # untouched


def test_length_table_custom_fragment_share(tmp_path):
    src = {"joint": [{"sentences": 1, "word_bin": [5, 10], "weight": 1.0,
                      "fragment_share": 0.6}]}
    in_path = tmp_path / "in.json"
    out_path = tmp_path / "out.json"
    in_path.write_text(json.dumps(src), encoding="utf-8")
    dcp.main(["length-table", "--in", str(in_path), "--out", str(out_path),
              "--fragment-share", "0.1"])
    out = json.loads(out_path.read_text())
    assert out["joint"][0]["fragment_share"] == 0.1


# ---------------------------------------------------------------------------
# split inheritance
# ---------------------------------------------------------------------------

def _pool_row(vid, decade, date=None):
    return {"volume_id": vid, "decade": decade,
            "date": date if date is not None else decade + 5,
            "text": "x", "passage_id": vid + "-p", "purposes": ["date_predictor"]}


def test_split_inherits_e1_assignments_verbatim():
    rows = [_pool_row(f"V{i}", 1850) for i in range(10)]
    authors = {f"V{i}": f"auth{i}" for i in range(10)}  # every volume its own group
    inherit = {"V0": "train", "V1": "val", "V2": "test"}
    assignment, stats = dpd.inherited_grouped_split(rows, authors, inherit, seed=1)
    assert assignment["V0"] == "train"
    assert assignment["V1"] == "val"
    assert assignment["V2"] == "test"
    assert stats["n_inherited"] == 3
    assert stats["n_fresh"] == 7
    assert set(assignment) == {f"V{i}" for i in range(10)}


def test_split_author_group_adopts_inherited_member():
    # V0 and V1 share an author; only V0 is in the E1 split -> V1 adopts it.
    rows = [_pool_row("V0", 1850), _pool_row("V1", 1850), _pool_row("V2", 1850)]
    authors = {"V0": "shared", "V1": "shared", "V2": "solo"}
    inherit = {"V0": "test"}
    assignment, stats = dpd.inherited_grouped_split(rows, authors, inherit, seed=1)
    assert assignment["V0"] == "test"
    assert assignment["V1"] == "test"          # adopted, not drawn fresh
    assert stats["n_inherited"] == 2
    assert stats["n_conflicts"] == 0


def test_split_reports_conflicting_inherited_assignments():
    rows = [_pool_row("V0", 1850), _pool_row("V1", 1850)]
    authors = {"V0": "shared", "V1": "shared"}
    inherit = {"V0": "train", "V1": "test"}   # same group, disagreeing
    assignment, stats = dpd.inherited_grouped_split(rows, authors, inherit, seed=1)
    assert assignment["V0"] == assignment["V1"]        # group forced consistent
    assert assignment["V0"] in {"train", "test"}
    assert stats["n_conflicts"] == 1


def test_split_no_inherit_assigns_all_fresh():
    rows = [_pool_row(f"V{i}", 1850) for i in range(20)]
    authors = {f"V{i}": f"auth{i}" for i in range(20)}
    assignment, stats = dpd.inherited_grouped_split(rows, authors, inherit={}, seed=3)
    assert stats["n_inherited"] == 0
    assert stats["n_fresh"] == 20
    assert set(assignment.values()) <= {"train", "val", "test"}


# ---------------------------------------------------------------------------
# soft labels against the shared grid
# ---------------------------------------------------------------------------

def test_soft_label_uses_shared_date_predictor_grid():
    edges, midpoints = dp.build_bin_grid(1680, 2040, 10)
    assert len(midpoints) == 36
    y = dp.soft_label(1883.0, 15.0, midpoints)
    assert y.shape == (36,)
    assert y.sum() == pytest.approx(1.0)
    assert int(np.argmax(y)) == dp.date_to_bin(1883.0, edges)


def test_train_script_imports_grid_helpers_from_date_predictor():
    bert_dir = REPO_ROOT / "bertclassify"
    sys.path.insert(0, str(bert_dir))
    import importlib
    tdd = importlib.import_module("train_date_deberta")
    assert tdd.soft_label is dp.soft_label
    assert tdd.build_bin_grid is dp.build_bin_grid
    assert tdd.crps_binned is dp.crps_binned


# ---------------------------------------------------------------------------
# fragment abstention path in `score`
# ---------------------------------------------------------------------------

def test_is_fragment_row_flags_explicit_flag():
    assert dpd._is_fragment_row({"fragment": True, "text": "The house stood firm."})


def test_is_fragment_row_flags_lowercase_sub_sentential():
    assert dpd._is_fragment_row({"text": "and then he wandered off toward the river"})


def test_is_fragment_row_passes_complete_sentence():
    assert not dpd._is_fragment_row(
        {"fragment": False, "text": "The house stood at the end of the lane."})


def test_is_fragment_row_missing_text_is_not_fragment():
    assert not dpd._is_fragment_row({"passage_id": "x"})


# ---------------------------------------------------------------------------
# is_deberta_dir: lexical vs DeBERTa run-dir detection
# ---------------------------------------------------------------------------

def test_is_deberta_dir_false_when_vectorizer_present(tmp_path):
    (tmp_path / "vectorizer.joblib").write_bytes(b"x")
    # even with a misleading config.json, vectorizer.joblib wins
    (tmp_path / "config.json").write_text('{"date_grid_lo": 1680}', encoding="utf-8")
    assert dpd.is_deberta_dir(tmp_path) is False


def test_is_deberta_dir_true_on_safetensors(tmp_path):
    (tmp_path / "model.safetensors").write_bytes(b"x")
    assert dpd.is_deberta_dir(tmp_path) is True


def test_is_deberta_dir_true_on_pytorch_bin(tmp_path):
    (tmp_path / "pytorch_model.bin").write_bytes(b"x")
    assert dpd.is_deberta_dir(tmp_path) is True


def test_is_deberta_dir_true_on_config_grid_key(tmp_path):
    (tmp_path / "config.json").write_text(
        '{"date_grid_lo": 1680, "date_grid_hi": 2040, "date_bin_width": 10}', encoding="utf-8")
    assert dpd.is_deberta_dir(tmp_path) is True


def test_is_deberta_dir_false_on_lexical_config_without_grid_key(tmp_path):
    # the real lexical config.json carries grid_lo, not date_grid_lo
    (tmp_path / "config.json").write_text(
        '{"feature_type": "tfidf", "n_bins": 36, "grid_lo": 1680}', encoding="utf-8")
    assert dpd.is_deberta_dir(tmp_path) is False


def test_is_deberta_dir_false_on_empty_dir(tmp_path):
    assert dpd.is_deberta_dir(tmp_path) is False


# ---------------------------------------------------------------------------
# score_e1 / score_e1_with_probs: fragment abstention, model calls mocked
# ---------------------------------------------------------------------------

def _stub_run_dir(monkeypatch):
    midpoints = np.array([1750.0, 1850.0, 1950.0])
    edges = np.array([1700.0, 1800.0, 1900.0, 2000.0])
    monkeypatch.setattr(dpd, "load_run_dir", lambda rd: (object(), object(), edges, midpoints))
    monkeypatch.setattr(dpd, "_resolve_device", lambda d: "cpu")
    return edges, midpoints


def test_score_e1_returns_none_at_fragment_and_triple_elsewhere(monkeypatch):
    _stub_run_dir(monkeypatch)

    def fake_predict(model, tok, texts, edges, midpoints, **kw):
        return np.tile(np.array([0.2, 0.3, 0.5]), (len(texts), 1))

    monkeypatch.setattr(dpd, "predict_probs", fake_predict)
    texts = ["and then he wandered off toward the river",      # fragment
             "The house stood at the end of the lane.",         # sentence
             "she said nothing more that evening"]              # fragment
    out = dpd.score_e1(texts, "/fake/run", temperature=1.0)
    assert out[0] is None
    assert out[2] is None
    assert out[1] is not None and len(out[1]) == 3


def test_score_e1_with_probs_full_length_nan_rows_for_fragments(monkeypatch):
    _stub_run_dir(monkeypatch)

    def fake_logits(model, tok, texts, **kw):
        return np.tile(np.array([0.1, 0.2, 0.7]), (len(texts), 1))

    monkeypatch.setattr(dpd, "_predict_logits", fake_logits)
    texts = ["and then he wandered off toward the river",
             "The house stood at the end of the lane."]
    triples, logits, edges, midpoints = dpd.score_e1_with_probs(texts, "/fake/run")
    assert triples[0] is None
    assert triples[1] is not None
    assert np.isnan(logits[0]).all()
    assert not np.isnan(logits[1]).any()
    assert logits.shape == (2, 3)

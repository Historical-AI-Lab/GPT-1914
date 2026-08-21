"""test_sanity_bounds.py — End-to-end sanity checks on calibration artifacts.

All tests are automatically skipped if the calibration directory or required
artifacts are absent (run the calibration pipeline first).

Run with:
    pytest modelasjudge/tests/test_sanity_bounds.py -v
"""

import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pytest

MODELASJUDGE = Path(__file__).parent.parent
CALIB_DIR = MODELASJUDGE / "calibration"

# Artifact paths
ANACH_SCORED = CALIB_DIR / "anachronic_pairs_scored.jsonl"
GT_SCORED = CALIB_DIR / "ground_truth_pairs_scored.jsonl"
LOGISTIC_PKL = CALIB_DIR / "logistic_calibrator.pkl"
LOGISTIC_JSON = CALIB_DIR / "logistic_calibrator.json"
RELIABILITY_OUT = CALIB_DIR / "per_question_reliability_chronologic-0.2.jsonl"


def _require(*paths):
    """Skip test if any path is missing."""
    for p in paths:
        if not p.exists():
            pytest.skip(f"Artifact not found (run pipeline first): {p}")


def load_deltas(path: Path) -> np.ndarray:
    deltas = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                deltas.append(json.loads(line)["delta"])
    return np.array(deltas)


def load_reliability_records() -> tuple[dict, list[dict]]:
    """Return (meta, [question_records])."""
    meta = None
    records = []
    with open(RELIABILITY_OUT, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if "_meta" in rec:
                meta = rec
            else:
                records.append(rec)
    return meta, records


# ---------------------------------------------------------------------------
# Δ direction
# ---------------------------------------------------------------------------

class TestDeltaDirection:
    def test_anachronic_mean_greater_than_gt_mean(self):
        _require(ANACH_SCORED, GT_SCORED)
        anach = load_deltas(ANACH_SCORED)
        gt = load_deltas(GT_SCORED)
        assert anach.mean() > gt.mean(), (
            f"Expected mean(Δ_anachronic)={anach.mean():.4f} > mean(Δ_gt)={gt.mean():.4f}"
        )

    def test_gap_exceeds_half_std_of_gt(self):
        _require(ANACH_SCORED, GT_SCORED)
        anach = load_deltas(ANACH_SCORED)
        gt = load_deltas(GT_SCORED)
        gap = anach.mean() - gt.mean()
        assert gap > 0.5 * gt.std(), (
            f"Gap {gap:.4f} should exceed 0.5 std of Δ_gt ({gt.std():.4f})"
        )


# ---------------------------------------------------------------------------
# Logistic model accuracy and coefficients
# ---------------------------------------------------------------------------

class TestLogisticModel:
    def test_cv_accuracy_in_range(self):
        _require(LOGISTIC_JSON)
        with open(LOGISTIC_JSON, encoding="utf-8") as f:
            coefs = json.load(f)
        acc = coefs["cv_accuracy_mean"]
        assert 0.55 <= acc <= 0.95, f"CV accuracy {acc:.4f} not in [0.55, 0.95]"

    def test_beta1_positive(self):
        """β1 (coefficient for Δ) must be positive — more anachronic as Δ grows."""
        _require(LOGISTIC_JSON)
        with open(LOGISTIC_JSON, encoding="utf-8") as f:
            coefs = json.load(f)
        beta1 = coefs["beta1_delta"]
        assert beta1 > 0, f"β1 should be positive, got {beta1}"

    def test_pickle_loadable(self):
        _require(LOGISTIC_PKL)
        with open(LOGISTIC_PKL, "rb") as f:
            artifact = pickle.load(f)
        assert "model" in artifact
        assert "cv_accuracy_mean" in artifact
        assert artifact["benchmark"] == "chronologic-0.2"


# ---------------------------------------------------------------------------
# Per-question reliability file
# ---------------------------------------------------------------------------

class TestReliabilityFile:
    def test_file_exists_with_meta(self):
        _require(RELIABILITY_OUT)
        meta, records = load_reliability_records()
        assert meta is not None, "Missing _meta line in reliability output"
        assert "chronologic-0.2" in meta.get("_meta", "")

    def test_all_weights_in_unit_interval(self):
        _require(RELIABILITY_OUT)
        _, records = load_reliability_records()
        for rec in records:
            w = rec["w_q"]
            assert 0.0 <= w <= 1.0, f"w_q={w} out of [0,1] for question {rec['question_number']}"

    def test_weight_zero_iff_r_q_at_most_half(self):
        _require(RELIABILITY_OUT)
        _, records = load_reliability_records()
        for rec in records:
            r = rec["r_q"]
            w = rec["w_q"]
            if r <= 0.5:
                assert w == pytest.approx(0.0, abs=1e-6), (
                    f"r_q={r} ≤ 0.5 but w_q={w} (q={rec['question_number']})"
                )
            else:
                assert w > 0.0, (
                    f"r_q={r} > 0.5 but w_q={w} (q={rec['question_number']})"
                )

    def test_nonzero_questions_present(self):
        _require(RELIABILITY_OUT)
        _, records = load_reliability_records()
        assert len(records) > 0, "No question records in reliability file"


# ---------------------------------------------------------------------------
# Reasoning-type stratification
# ---------------------------------------------------------------------------

class TestReasoningTypeStratification:
    def _stratum_acc(self):
        _require(RELIABILITY_OUT)
        from collections import defaultdict
        _, records = load_reliability_records()
        groups = defaultdict(list)
        for rec in records:
            groups[rec["reasoning_type"]].append(rec["r_q"])
        return {t: float(np.mean(vs)) for t, vs in groups.items()}

    def test_knowledge_below_threshold(self):
        acc = self._stratum_acc()
        if "knowledge" not in acc:
            pytest.skip("No knowledge questions in reliability file")
        assert acc["knowledge"] < 0.7, (
            f"knowledge r_q={acc['knowledge']:.4f} expected < 0.7 (style-uninformative)"
        )

    def test_abstention_below_threshold(self):
        acc = self._stratum_acc()
        if "abstention" not in acc:
            pytest.skip("No abstention questions in reliability file")
        assert acc["abstention"] < 0.7, (
            f"abstention r_q={acc['abstention']:.4f} expected < 0.7"
        )

    def test_at_least_one_cloze_type_above_threshold(self):
        acc = self._stratum_acc()
        cloze_types = {"sentence_cloze", "phrase_cloze"}
        present = cloze_types & acc.keys()
        if not present:
            pytest.skip("No sentence_cloze or phrase_cloze in reliability file")
        max_cloze = max(acc[t] for t in present)
        assert max_cloze > 0.7, (
            f"Expected at least one cloze type r_q > 0.7, got max={max_cloze:.4f}"
        )


# ---------------------------------------------------------------------------
# Length-decile stratification (loose monotone check)
# ---------------------------------------------------------------------------

class TestLengthDecileStratification:
    def test_r_q_loosely_increases_with_length(self):
        """Spearman rank correlation between decile index and r_q ≥ 0.4."""
        _require(RELIABILITY_OUT)
        from collections import defaultdict
        from scipy.stats import spearmanr

        _, records = load_reliability_records()
        groups = defaultdict(list)
        for rec in records:
            groups[rec["length_decile"]].append(rec["r_q"])
        decile_acc = {d: float(np.mean(vs)) for d, vs in groups.items()}

        if len(decile_acc) < 3:
            pytest.skip("Too few deciles to test correlation")

        deciles = sorted(decile_acc)
        accs = [decile_acc[d] for d in deciles]
        rho, _ = spearmanr(deciles, accs)
        assert rho >= 0.4, (
            f"Spearman ρ(decile, r_q) = {rho:.4f} < 0.4 — expected loose monotone increase"
        )

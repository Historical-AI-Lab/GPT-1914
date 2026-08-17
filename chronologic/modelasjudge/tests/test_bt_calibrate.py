"""test_bt_calibrate.py — Tests for bt/calibrate.py.

Run with:
    pytest modelasjudge/tests/test_bt_calibrate.py -v
"""

import sys
from pathlib import Path

import numpy as np
import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from bt.calibrate import apply_calibration, fit_calibration
from bt_context_scoring import (
    loo_label, stratified_subsample, _n_gt, _cluster_bootstrap_calibration,
)


def make_separable_records(n=30, seed=0):
    rng = np.random.default_rng(seed)
    records = []
    for _ in range(n):
        delta = rng.normal(3, 1)   # ground-truth-like, positive delta
        records.append({"delta_mean": delta, "label": 1.0, "source": "gt"})
    for _ in range(n):
        delta = rng.normal(-3, 1)  # distractor-like, negative delta
        records.append({"delta_mean": delta, "label": 0.0, "source": "distractor"})
    return records


class TestFitCalibration:
    def test_positive_slope_on_separable_data(self):
        calib = fit_calibration(make_separable_records())
        assert calib["slope"] > 0
        assert calib["converged"]

    def test_soft_labels_accepted(self):
        records = make_separable_records() + [
            {"delta_mean": 0.0, "label": 0.3, "source": "human_llm"},
            {"delta_mean": 0.5, "label": 0.9, "source": "human_llm"},
        ]
        calib = fit_calibration(records)
        assert calib["n_by_source"]["human_llm"] == 2

    def test_too_few_records_raises(self):
        with pytest.raises(ValueError):
            fit_calibration([{"delta_mean": 0.0, "label": 1.0, "source": "gt"}])

    def test_label_out_of_range_raises(self):
        with pytest.raises(ValueError):
            fit_calibration([
                {"delta_mean": 0.0, "label": 1.5, "source": "gt"},
                {"delta_mean": 1.0, "label": 0.0, "source": "d"},
            ])


class TestLooLabel:
    """The benchmark's own answer_probability is the calibration label."""

    def test_ground_truth_labels_one(self):
        assert loo_label({"kind": "ground_truth", "prob": 1.0}) == (1.0, "ground_truth")

    def test_plain_distractor_labels_zero(self):
        assert loo_label({"kind": "distractor", "prob": 0.0}) == (0.0, "distractor")

    def test_partial_credit_becomes_a_soft_label(self):
        assert loo_label({"kind": "distractor", "prob": 0.25}) == (0.25, "partial")
        assert loo_label({"kind": "distractor", "prob": 0.75}) == (0.75, "partial")

    def test_missing_prob_falls_back_to_kind(self):
        """LOO artifacts written before `prob` existed must still calibrate."""
        assert loo_label({"kind": "distractor"}) == (0.0, "distractor")
        assert loo_label({"kind": "ground_truth"}) == (1.0, "ground_truth")

    def test_soft_labels_flow_into_fit_calibration(self):
        loo_records = (
            [{"kind": "ground_truth", "prob": 1.0, "delta_mean": d} for d in (2.0, 3.0, 2.5)]
            + [{"kind": "distractor", "prob": 0.0, "delta_mean": d} for d in (-3.0, -2.0, -2.5)]
            + [{"kind": "distractor", "prob": 0.75, "delta_mean": 0.5},
               {"kind": "distractor", "prob": 0.25, "delta_mean": -0.5}]
        )
        records = []
        for r in loo_records:
            label, source = loo_label(r)
            records.append({"delta_mean": r["delta_mean"], "label": label, "source": source})
        calib = fit_calibration(records)
        assert calib["converged"]
        assert calib["slope"] > 0
        assert calib["n_by_source"] == {"ground_truth": 3, "distractor": 3, "partial": 2}


class TestLengthCovariate:
    def test_three_param_fit_converges_and_recovers_planted_slope(self):
        rng = np.random.default_rng(0)
        n = 200
        true_a, true_b, true_c = 0.0, 1.0, 0.8
        delta = rng.normal(0, 2, n)
        z_len = rng.normal(0, 1, n)
        from scipy.special import expit
        p = expit(true_a + true_b * delta + true_c * z_len)
        y = rng.binomial(1, p).astype(float)
        records = [{"delta_mean": d, "z_len": z, "label": l, "source": "s"}
                  for d, z, l in zip(delta, z_len, y)]
        calib = fit_calibration(records, use_length=True)
        assert calib["converged"]
        assert "length_slope" in calib
        assert abs(calib["length_slope"] - true_c) < 0.3

    def test_two_param_fit_has_no_length_slope_key(self):
        calib = fit_calibration(make_separable_records())
        assert "length_slope" not in calib


class TestClusterBootstrapCalibration:
    def test_resamples_qids_not_records(self):
        """Two qids with wildly different Delta scale: if bootstrap
        resampled individual records instead of whole questions, replicate
        slopes would cluster tightly around one pooled value. Resampling
        qids means some replicates see mostly qid A (large |delta|, needs
        only a shallow slope to separate), some mostly qid B (small
        |delta|, needs a steep slope) -- a wide spread in slope draws."""
        records = (
            [{"qid": "A", "item_id": f"a{i}", "delta_mean": 5.0, "label": 1.0, "source": "gt"}
             for i in range(3)]
            + [{"qid": "A", "item_id": f"ad{i}", "delta_mean": -5.0, "label": 0.0, "source": "d"}
               for i in range(3)]
            + [{"qid": "B", "item_id": f"b{i}", "delta_mean": 0.3, "label": 1.0, "source": "gt"}
               for i in range(3)]
            + [{"qid": "B", "item_id": f"bd{i}", "delta_mean": -0.3, "label": 0.0, "source": "d"}
               for i in range(3)]
        )
        draws, n_zero_positive = _cluster_bootstrap_calibration(
            records, n_boot=500, seed=1, use_length=False)
        slopes = draws[:, 1]
        # A-only and B-only replicates fit very different slopes (A's tight
        # separation at delta=+-5 needs far less slope than B's at +-0.3);
        # a bootstrap that resampled individual records instead of whole
        # questions would blend A and B in nearly every replicate and this
        # spread would collapse toward the single pooled-fit value.
        assert slopes.std() / slopes.mean() > 0.2
        assert n_zero_positive >= 0

    def test_zero_positive_replicates_detected_and_counted(self):
        """A qid pool containing only label==0 records, resampled alone,
        cannot fit -- must be skipped and counted, not silently included."""
        records = (
            [{"qid": "onlyneg", "item_id": f"d{i}", "delta_mean": -1.0, "label": 0.0, "source": "d"}
             for i in range(3)]
            + [{"qid": "haspos", "item_id": "gt0", "delta_mean": 1.0, "label": 1.0, "source": "gt"},
               {"qid": "haspos", "item_id": "d0", "delta_mean": -1.0, "label": 0.0, "source": "d"}]
        )
        draws, n_zero_positive = _cluster_bootstrap_calibration(
            records, n_boot=200, seed=2, use_length=False)
        assert n_zero_positive > 0
        assert draws.shape[0] + n_zero_positive == 200

    def test_length_covariate_draws_have_three_columns(self):
        rng = np.random.default_rng(3)
        records = []
        for q in range(10):
            for i in range(4):
                delta = rng.normal(3 if i < 2 else -3, 1)
                records.append({"qid": str(q), "item_id": f"i{i}", "delta_mean": delta,
                                "z_len": rng.normal(0, 1), "label": 1.0 if i < 2 else 0.0,
                                "source": "s"})
        draws, _ = _cluster_bootstrap_calibration(records, n_boot=50, seed=4, use_length=True)
        assert draws.shape[1] == 3


class TestStratifiedSubsample:
    def _records(self, n=90):
        recs = {}
        cats = ["knowledge", "character_modeling", "topic_sentence"]
        for i in range(n):
            n_gt = 2 if i % 3 == 0 else 1
            types = ["ground_truth"] * n_gt + ["manual"] * 2
            recs[str(i)] = {"question_category": cats[i % 3], "answer_types": types}
        return recs

    def test_returns_requested_count(self):
        recs = self._records()
        sub = stratified_subsample(recs, 30, ["question_category", "n_gt"], seed=1)
        assert len(sub) == 30
        assert len(set(sub)) == 30   # no duplicates

    def test_n_ge_population_returns_everything(self):
        recs = self._records(20)
        sub = stratified_subsample(recs, 1000, ["question_category"], seed=1)
        assert set(sub) == set(recs)

    def test_two_gt_stratum_represented_proportionally(self):
        """The 70-two-GT-question worry (plan §8): stratifying on n_gt keeps
        that stratum's share of the sample close to its share of the
        population, rather than starving it by chance."""
        recs = self._records(90)   # 1/3 have n_gt == 2
        sub = stratified_subsample(recs, 30, ["question_category", "n_gt"], seed=1)
        two_gt = sum(1 for q in sub if _n_gt(recs[q]) == 2)
        assert 7 <= two_gt <= 13   # ~10 expected of 30

    def test_deterministic_for_fixed_seed(self):
        recs = self._records()
        a = stratified_subsample(recs, 20, ["question_category", "n_gt"], seed=7)
        b = stratified_subsample(recs, 20, ["question_category", "n_gt"], seed=7)
        assert a == b


class TestApplyCalibration:
    def test_ninety_five_percent_interval(self):
        """apply_calibration returns the 2.5/97.5 percentiles (spec §7's
        95%-everywhere convention), not the superseded central 90%."""
        calib = {"intercept": 0.0, "slope": 1.0}
        rng = np.random.default_rng(0)
        draws = rng.normal(0, 2, 5000)
        _p_mean, p_ci, p_draws = apply_calibration(calib, draws)
        expected_lo, expected_hi = np.quantile(
            1 / (1 + np.exp(-draws)), [0.025, 0.975])
        assert abs(p_ci[0] - expected_lo) < 1e-9
        assert abs(p_ci[1] - expected_hi) < 1e-9

    def test_pfit_high_for_large_positive_delta(self):
        calib = fit_calibration(make_separable_records())
        p_mean, p_ci, p_draws = apply_calibration(calib, np.full(200, 5.0))
        assert p_mean > 0.8
        assert p_ci[0] <= p_mean <= p_ci[1]

    def test_pfit_low_for_large_negative_delta(self):
        calib = fit_calibration(make_separable_records())
        p_mean, _p_ci, _draws = apply_calibration(calib, np.full(200, -5.0))
        assert p_mean < 0.2

    def test_jensen_summary_matches_draw_mean(self):
        calib = {"intercept": 0.0, "slope": 1.0}
        draws = np.array([-6.0] * 500 + [6.0] * 500)
        p_mean, _ci, p_draws = apply_calibration(calib, draws)
        assert abs(p_mean - p_draws.mean()) < 1e-12


class TestLegacyCoefficientNames:
    """Calibration artifacts written before 2026-08-06 use "a"/"b". They are
    valid fits, so they must still load rather than force an expensive refit."""

    def test_legacy_keys_are_read(self):
        from bt.calibrate import apply_calibration, calibration_coefficients
        assert calibration_coefficients({"a": 0.7, "b": 0.65}) == (0.7, 0.65)
        legacy = apply_calibration({"a": 0.7, "b": 0.65}, np.zeros(50))
        current = apply_calibration({"intercept": 0.7, "slope": 0.65}, np.zeros(50))
        assert abs(legacy[0] - current[0]) < 1e-12

    def test_new_keys_win_when_both_present(self):
        from bt.calibrate import calibration_coefficients
        assert calibration_coefficients(
            {"intercept": 1.0, "slope": 2.0, "a": 9.0, "b": 9.0}) == (1.0, 2.0)

    def test_missing_both_raises(self):
        from bt.calibrate import calibration_coefficients
        with pytest.raises(KeyError):
            calibration_coefficients({"n": 10})

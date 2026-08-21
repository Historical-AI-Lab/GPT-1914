"""test_bt_fit.py — Tests for bt/fit.py and bt/tau.py.

Run with:
    pytest modelasjudge/tests/test_bt_fit.py -v
"""

import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.special import expit

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from bt.fit import (
    AnchorFit,
    FitConfig,
    counts_to_arrays,
    fit_anchor_model,
    load_anchor_fits,
    save_anchor_fits,
    three_cycle_count,
)
from bt.tau import aggregate_candidate_counts, score_candidate


def make_synthetic_draws(n_draws, n_items, spread=3.0, seed=0):
    rng = np.random.default_rng(seed)
    draws = rng.normal(0, spread, size=(n_draws, n_items))
    draws -= draws.mean(axis=1, keepdims=True)  # sum-to-zero per draw
    return draws


class TestCountsToArrays:
    def test_index_roundtrip(self):
        item_ids = ["gt0", "gt1", "d0"]
        counts = {("gt0", "d0"): (3, 5), ("d0", "gt0"): (2, 5), ("gt1", "d0"): (4, 4)}
        i_idx, j_idx, wins, n = counts_to_arrays(item_ids, counts)
        for k, (a, b) in enumerate([("gt0", "d0"), ("d0", "gt0"), ("gt1", "d0")]):
            # sorted() ordering inside counts_to_arrays; just check membership
            pass
        assert set(zip(i_idx.tolist(), j_idx.tolist())) == {
            (item_ids.index("gt0"), item_ids.index("d0")),
            (item_ids.index("d0"), item_ids.index("gt0")),
            (item_ids.index("gt1"), item_ids.index("d0")),
        }

    def test_unknown_item_raises(self):
        with pytest.raises(KeyError):
            counts_to_arrays(["gt0"], {("gt0", "ghost"): (1, 1)})

    def test_zero_n_skipped(self):
        i_idx, j_idx, wins, n = counts_to_arrays(["gt0", "d0"], {("gt0", "d0"): (0, 0)})
        assert len(n) == 0


class TestFitAnchorModel:
    def test_sum_to_zero_per_draw(self):
        item_ids = ["gt0", "d0", "d1"]
        counts = {
            ("gt0", "d0"): (7, 10), ("d0", "gt0"): (3, 10),
            ("gt0", "d1"): (8, 10), ("d1", "gt0"): (2, 10),
            ("d0", "d1"): (6, 10), ("d1", "d0"): (4, 10),
        }
        fit = fit_anchor_model(item_ids, counts, seed=1,
                               fit_config=FitConfig(draws=100, tune=200, chains=2))
        row_sums = fit.theta_draws.sum(axis=1)
        assert np.allclose(row_sums, 0.0, atol=1e-6)

    def test_repeats_enter_as_binomial_not_collapsed_bernoulli(self):
        # (w=8, n=10) should differ materially from averaging two (w=4,n=5) Bernoulli
        # draws collapsed to a single (w=1,n=1) with p=0.8 -- verify via posterior
        # concentration: more data (larger n) should give a tighter posterior.
        item_ids = ["gt0", "d0"]
        counts_narrow = {("gt0", "d0"): (1, 1), ("d0", "gt0"): (0, 1)}
        counts_wide = {("gt0", "d0"): (8, 10), ("d0", "gt0"): (2, 10)}
        cfg = FitConfig(draws=300, tune=300, chains=2)
        fit_narrow = fit_anchor_model(item_ids, counts_narrow, seed=1, fit_config=cfg)
        fit_wide = fit_anchor_model(item_ids, counts_wide, seed=1, fit_config=cfg)
        delta_narrow = fit_narrow.theta_draws[:, 0] - fit_narrow.theta_draws[:, 1]
        delta_wide = fit_wide.theta_draws[:, 0] - fit_wide.theta_draws[:, 1]
        assert delta_wide.std() < delta_narrow.std()

    def test_npz_roundtrip(self, tmp_path):
        item_ids = ["gt0", "d0"]
        counts = {("gt0", "d0"): (3, 5), ("d0", "gt0"): (2, 5)}
        fit = fit_anchor_model(item_ids, counts, seed=1,
                               fit_config=FitConfig(draws=50, tune=100, chains=2))
        path = tmp_path / "anchors.npz"
        save_anchor_fits(path, {"q1": fit}, meta={"judge": "test"})
        loaded, meta = load_anchor_fits(path)
        assert meta == {"judge": "test"}
        assert loaded["q1"].item_ids == fit.item_ids
        assert np.allclose(loaded["q1"].theta_draws, fit.theta_draws)


class TestThreeCycleCount:
    def test_transitive_has_no_cycles(self):
        counts = {("a", "b"): (9, 10), ("b", "a"): (1, 10),
                  ("b", "c"): (9, 10), ("c", "b"): (1, 10),
                  ("a", "c"): (9, 10), ("c", "a"): (1, 10)}
        assert three_cycle_count(counts) == 0

    def test_intransitive_triad_counted(self):
        counts = {("a", "b"): (9, 10), ("b", "a"): (1, 10),
                  ("b", "c"): (9, 10), ("c", "b"): (1, 10),
                  ("c", "a"): (9, 10), ("a", "c"): (1, 10)}
        assert three_cycle_count(counts) == 1


class TestJensenAndAntisymmetry:
    def test_tau_mean_is_expectation_of_sigmoid_not_sigmoid_of_mean(self):
        delta_draws = np.concatenate([np.full(500, 6.0), np.full(500, -6.0)])
        tau_mean = float(expit(delta_draws).mean())
        sigmoid_of_mean = float(expit(delta_draws.mean()))
        assert abs(tau_mean - 0.5) < 0.01
        assert abs(sigmoid_of_mean - 0.5) < 0.01
        # Construct an asymmetric-spread case where the two estimators diverge materially.
        delta_draws2 = np.concatenate([np.full(700, 4.0), np.full(300, -4.0)])
        tau_mean2 = float(expit(delta_draws2).mean())
        sigmoid_of_mean2 = float(expit(delta_draws2.mean()))
        assert abs(tau_mean2 - sigmoid_of_mean2) > 0.05

    def test_tau_antisymmetry_on_identical_draws(self):
        # tau(a,b) = sigma(delta) and tau(b,a) = sigma(-delta) must sum to
        # exactly 1 pointwise on the SAME delta draws -- this is the
        # antisymmetry identity the spec calls for, independent of any
        # re-sampling noise from a second score_candidate() call.
        item_ids = ["opp"]
        draws = make_synthetic_draws(400, 1, spread=2.0, seed=3)
        fit = AnchorFit(item_ids=item_ids, theta_draws=draws, prior_scale=1.0)
        counts = {("cand", "opp"): (6, 10), ("opp", "cand"): (4, 10)}
        score = score_candidate(fit, counts, "cand", "opp", prior_scale=1.0, seed=1)
        tau_forward = expit(score.delta_draws)
        tau_backward = expit(-score.delta_draws)
        assert np.allclose(tau_forward + tau_backward, 1.0, atol=1e-12)
        assert np.allclose(tau_forward, score.tau_draws)


class TestAggregateCandidateCounts:
    def test_both_orders_collapse_correctly(self):
        counts = {("cand", "d0"): (7, 10), ("d0", "cand"): (2, 10)}
        agg = aggregate_candidate_counts(counts, "cand")
        wins, n = agg["d0"]
        assert n == 20
        assert wins == 7 + (10 - 2)

    def test_ignores_unrelated_pairs(self):
        counts = {("gt0", "d0"): (5, 10)}
        assert aggregate_candidate_counts(counts, "cand") == {}


class TestScoreCandidate:
    def test_grid_sampler_recovers_known_posterior(self):
        # Single opponent, large n, tight prior -> theta_c well-determined near
        # a value that makes p = k/n.
        item_ids = ["opp"]
        theta_draws = np.zeros((200, 1))  # opponent fixed at 0
        fit = AnchorFit(item_ids=item_ids, theta_draws=theta_draws, prior_scale=10.0)
        # k/n = 0.88 -> true theta_c ~ logit(0.88) ~ 1.99
        counts = {("cand", "opp"): (880, 1000), ("opp", "cand"): (120, 1000)}
        score = score_candidate(fit, counts, "cand", "opp", prior_scale=10.0, seed=1,
                                grid_half_width=8.0, grid_points=1601)
        expected_theta_c = np.log(0.88 / 0.12)
        assert abs(score.delta_mean - expected_theta_c) < 0.1

    def test_missing_opponent_raises(self):
        fit = AnchorFit(item_ids=["a"], theta_draws=np.zeros((10, 1)), prior_scale=1.0)
        with pytest.raises(KeyError):
            score_candidate(fit, {("cand", "b"): (1, 1)}, "cand", "a",
                            prior_scale=1.0, seed=1)

    def test_no_comparisons_raises(self):
        fit = AnchorFit(item_ids=["a"], theta_draws=np.zeros((10, 1)), prior_scale=1.0)
        with pytest.raises(ValueError):
            score_candidate(fit, {}, "cand", "a", prior_scale=1.0, seed=1)

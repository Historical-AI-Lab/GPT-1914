"""test_substantive_estimator.py — pins the spec's algebra (§2, §4, §6, §8).

Each class targets one claim from substantive-uncertainty-spec.md that a
future "simplification" could quietly break:

  - the Rogan-Gladen display-posterior identity (§2)
  - clip the aggregate, never the per-question value (§8.3)
  - instrument draws are shared per replicate, not per question (§4, §6)
  - BT Delta draws are independent per question (§6 step 4)
  - beta's per-question residual averages away at the aggregate but not
    within a small slice (§4)
  - monotonicity of the RG transform under shared alpha, beta (§2)
  - the informativeness floor excludes rather than clips or downweights
    (§8.2, §8.4)
  - beta_q is structurally bounded to [0, 0.5]
  - the pooled-score arithmetic (count-weighted and equal-weight)
"""

import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.special import expit, logit

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from substantive.estimator import (
    alpha_draws, alpha_point, beta_from_coefs, bootstrap, display_posteriors,
    floor_mask, plugin_point, rogan_gladen, slice_scores,
)


def _binary_inputs(n_pf, *, alpha_shared=0.08, beta_shared=0.12, seed=0,
                   n_alpha_trials=40, n_v_trials=9, instrument_sd=0.0, n_coef_draws=500):
    """Homogeneous synthetic binary-channel questions under shared alpha, beta."""
    rng = np.random.default_rng(seed)
    true_p = rng.uniform(0.2, 0.8, size=n_pf)
    v_hat = true_p * (1 - beta_shared) + (1 - true_p) * alpha_shared
    n_v = np.full(n_pf, n_v_trials)
    a0 = 0.5
    n_alpha = np.full(n_pf, n_alpha_trials)
    k_alpha = np.round(alpha_shared * (2 * a0 + n_alpha) - a0).astype(int)
    frame_idx = np.zeros(n_pf, dtype=int)
    z_loglen = np.zeros(n_pf)
    eta_shared = logit(2 * beta_shared)
    coef_rng = np.random.default_rng(seed + 9000)
    coef_b0 = (coef_rng.normal(eta_shared, instrument_sd, size=n_coef_draws)
              if instrument_sd > 0 else np.full(n_coef_draws, eta_shared))
    coef_b_len = np.zeros(n_coef_draws)
    coef_u_frame = np.zeros((n_coef_draws, 1))
    return dict(v_hat=v_hat, n_v=n_v, k_alpha=k_alpha, n_alpha=n_alpha, frame_idx=frame_idx,
                z_loglen=z_loglen, excluded_mask=np.zeros(n_pf, dtype=bool),
                coef_b0=coef_b0, coef_b_len=coef_b_len, coef_u_frame=coef_u_frame,
                true_p=true_p)


def _bt_inputs(n_pc, *, seed=0, n_delta_draws=1000, n_cal_draws=500, cal_sd=0.0):
    rng = np.random.default_rng(seed)
    delta_true = rng.normal(0.5, 1.0, size=n_pc)
    delta_draws = delta_true[:, None] + rng.normal(0, 1.0, size=(n_pc, n_delta_draws))
    cal_rng = np.random.default_rng(seed + 8000)
    cal_a = (cal_rng.normal(0.0, cal_sd, size=n_cal_draws) if cal_sd > 0
            else np.zeros(n_cal_draws))
    cal_b = np.ones(n_cal_draws)
    return dict(delta_draws=delta_draws, cal_a=cal_a, cal_b=cal_b)


def _empty_binary():
    return dict(v_hat=np.zeros(0), n_v=np.zeros(0), k_alpha=np.zeros(0), n_alpha=np.zeros(0),
                frame_idx=np.zeros(0, dtype=int), z_loglen=np.zeros(0),
                excluded_mask=np.zeros(0, dtype=bool),
                coef_b0=np.zeros(10), coef_b_len=np.zeros(10), coef_u_frame=np.zeros((10, 1)))


def _empty_bt():
    return dict(delta_draws=np.zeros((0, 10)), cal_a=np.zeros(10), cal_b=np.zeros(10))


def _pp_kwargs(binary):
    return {k: v for k, v in binary.items() if k not in ("true_p", "excluded_mask")}


class TestRoganGladenIdentity:
    def test_mean_display_posterior_equals_plugin_passfail(self):
        binary = _binary_inputs(300, alpha_shared=0.08, beta_shared=0.12, seed=1)
        pt = plugin_point(**_pp_kwargs(binary), **_empty_bt())
        beta_shared_arr = np.full(pt.n_passfail, 0.12)
        disp = display_posteriors(binary["v_hat"][~pt.excluded_mask], beta_shared_arr,
                                  pt.passfail, pt.q_bar)
        assert abs(disp.mean() - pt.passfail) < 1e-12

    def test_display_posteriors_are_genuine_probabilities(self):
        binary = _binary_inputs(300, seed=2)
        pt = plugin_point(**_pp_kwargs(binary), **_empty_bt())
        beta_shared_arr = np.full(pt.n_passfail, 0.12)
        disp = display_posteriors(binary["v_hat"][~pt.excluded_mask], beta_shared_arr,
                                  pt.passfail, pt.q_bar)
        assert np.all(disp >= 0.0) and np.all(disp <= 1.0)


class TestClipAggregateOnly:
    def test_rogan_gladen_does_not_clip(self):
        rng = np.random.default_rng(3)
        v = rng.uniform(0, 1, 200)
        alpha = np.full(200, 0.3)
        beta = np.full(200, 0.3)
        p = rogan_gladen(v, alpha, beta)
        assert (p < 0).any() or (p > 1).any()

    def test_per_question_clipping_biases_the_mean_inward(self):
        """Asymmetric alpha/beta (0.30 vs 0.05) so far more mass falls
        below 0 than above 1 under v ~ Uniform(0,1); per-question clipping
        then predictably raises the mean relative to clipping the
        aggregate once. Large n keeps the direction seed-independent."""
        rng = np.random.default_rng(4)
        n = 3000
        v = rng.uniform(0, 1, n)
        alpha, beta = np.full(n, 0.30), np.full(n, 0.05)
        p = rogan_gladen(v, alpha, beta)
        aggregate_clip = np.clip(p.mean(), 0.0, 1.0)
        per_question_clip = np.clip(p, 0.0, 1.0).mean()
        assert per_question_clip > aggregate_clip

    def test_channel_mean_matches_closed_form(self):
        binary = _binary_inputs(150, seed=5)
        pt = plugin_point(**_pp_kwargs(binary), **_empty_bt())
        closed_form = np.clip(rogan_gladen(
            binary["v_hat"], np.full(150, alpha_point(binary["k_alpha"], binary["n_alpha"])[0]),
            np.full(150, expit(binary["coef_b0"].mean()) / 2)).mean(), 0, 1)
        assert abs(pt.passfail - closed_form) < 1e-9


class TestInstrumentSharedPerReplicate:
    def test_indices_are_scalar_per_replicate(self):
        binary = _binary_inputs(50, instrument_sd=0.1, seed=6)
        bt = _bt_inputs(20, cal_sd=0.1, seed=6)
        res = bootstrap(**{k: v for k, v in binary.items() if k != "true_p"}, **bt,
                        n_boot=100, seed=1, return_indices=True)
        assert res.cal_idx.shape == (100,)
        assert res.beta_idx.shape == (100,)

    def test_width_ratio_with_and_without_instrument_noise(self):
        """Layer 2 (instrument) is a floor that doesn't average away: the
        554/5000-vs-50/500-style width ratio stays well above the pure
        1/sqrt(n) rate when instrument noise is on, and matches it closely
        when instrument is dropped."""
        def width(n_pf, layers, seed):
            binary = _binary_inputs(n_pf, instrument_sd=0.15, seed=seed)
            res = bootstrap(**{k: v for k, v in binary.items() if k != "true_p"}, **_empty_bt(),
                            n_boot=3000, seed=seed + 500, layers=layers)
            lo, hi = np.percentile(res.passfail, [2.5, 97.5])
            return hi - lo

        with_instrument = [width(5000, ("judgment", "instrument", "item"), s) / width(500, ("judgment", "instrument", "item"), s)
                           for s in range(4)]
        without_instrument = [width(5000, ("judgment", "item"), s) / width(500, ("judgment", "item"), s)
                              for s in range(4)]
        assert np.mean(with_instrument) > 0.5
        assert np.mean(without_instrument) < 0.4
        assert np.mean(with_instrument) > np.mean(without_instrument) + 0.15


class TestDeltaIndependence:
    def test_distinct_index_per_question(self):
        bt = _bt_inputs(30, seed=7)
        res = bootstrap(**_empty_binary(), **bt, n_boot=50, seed=1,
                        layers=("judgment", "instrument", "item"))
        # p_partial_qr varies question-to-question within a fixed replicate
        # column -- if the same index were shared, every question's value
        # under a shared instrument draw would move in lockstep.
        col = res.p_partial_qr[:, 0]
        assert np.std(col) > 0

    def test_two_identical_questions_pick_different_delta_indices(self):
        """Duplicate one question's Delta draws across two rows: if the
        draw index were shared (a shared-instrument-style bug applied to
        judgment noise), both rows would be identical in every replicate.
        Independent per-question indices decorrelate them instead."""
        rng = np.random.default_rng(0)
        one_question = rng.normal(0.5, 1.0, size=1000)
        delta_draws = np.tile(one_question, (2, 1))
        bt = dict(delta_draws=delta_draws, cal_a=np.zeros(50), cal_b=np.ones(50))
        res = bootstrap(**_empty_binary(), **bt, n_boot=200, seed=2,
                        layers=("judgment", "instrument", "item"))
        assert not np.allclose(res.p_partial_qr[0], res.p_partial_qr[1])

    def test_width_scales_as_inverse_sqrt_m(self):
        def width(m, seed):
            bt = _bt_inputs(m, seed=seed)
            res = bootstrap(**_empty_binary(), **bt, n_boot=3000, seed=seed + 50,
                            layers=("judgment", "instrument", "item"))
            lo, hi = np.percentile(res.partial, [2.5, 97.5])
            return hi - lo

        ratio = width(400, 1) / width(40, 1)
        assert abs(ratio - 1 / np.sqrt(10)) < 0.08


class TestResidualInertAtAggregateLiveAtSlice:
    def test_absolute_width_contribution_shrinks_with_more_questions(self):
        """beta's per-question residual is layer-1 noise: its marginal
        contribution to the bootstrap width is a per-question quantity
        averaged over n questions, so it shrinks as 1/sqrt(n) -- exactly
        the sense in which it is 'inert at the aggregate' (554 questions)
        while still moving a 20-question slice."""
        def width(n_pf, sigma_u, seed):
            binary = _binary_inputs(n_pf, n_alpha_trials=100000, n_v_trials=100000, seed=seed)
            res = bootstrap(**{k: v for k, v in binary.items() if k != "true_p"}, **_empty_bt(),
                            sigma_u=sigma_u, n_boot=4000, seed=200,
                            layers=("judgment",))
            lo, hi = np.percentile(res.passfail, [2.5, 97.5])
            return hi - lo

        sigma_hi = 0.5
        added_large = width(554, sigma_hi, 1) - width(554, 0.0, 1)
        added_small = width(20, sigma_hi, 1) - width(20, 0.0, 1)
        ratio = added_small / added_large
        # theory: sqrt(554/20) ~= 5.26
        assert 3.0 < ratio < 8.0


class TestMonotonicity:
    def test_rank_correlation_with_raw_verdict_rate_is_one(self):
        from scipy.stats import spearmanr
        rng = np.random.default_rng(8)
        alpha, beta = 0.08, 0.12
        raw_means, corrected_means = [], []
        for _ in range(20):
            n = 100
            true_p = rng.uniform(0.05, 0.95, size=n)
            v = true_p * (1 - beta) + (1 - true_p) * alpha
            p = rogan_gladen(v, np.full(n, alpha), np.full(n, beta))
            raw_means.append(v.mean())
            corrected_means.append(p.mean())
        rho, _ = spearmanr(raw_means, corrected_means)
        assert rho == pytest.approx(1.0)


class TestFloorExclusion:
    def test_excluded_question_is_dropped_not_clipped_or_downweighted(self):
        n = 5
        v_hat = np.full(n, 0.5)
        n_v = np.full(n, 9)
        a0 = 0.5
        n_alpha = np.full(n, 1000)
        target_alphas = np.array([0.1, 0.1, 0.1, 0.1, 0.45])
        k_alpha = np.round(target_alphas * (2 * a0 + n_alpha) - a0).astype(int)
        etas = logit(2 * np.array([0.1, 0.1, 0.1, 0.1, 0.4]))
        frame_idx = np.arange(n)
        coef_u_frame = etas.reshape(1, n)
        pt = plugin_point(v_hat=v_hat, n_v=n_v, k_alpha=k_alpha, n_alpha=n_alpha,
                          frame_idx=frame_idx, z_loglen=np.zeros(n),
                          coef_b0=np.zeros(1), coef_b_len=np.zeros(1),
                          coef_u_frame=coef_u_frame, floor=0.2, **_empty_bt())
        assert pt.n_excluded_floor == 1
        assert pt.excluded_mask.tolist() == [False, False, False, False, True]
        assert pt.n_passfail == 4

    def test_no_question_weight_parameter_exists(self):
        import inspect
        for fn in (plugin_point, bootstrap, rogan_gladen):
            params = inspect.signature(fn).parameters
            assert not any("weight" in p.lower() for p in params)


class TestBetaBounds:
    def test_point_beta_bounded(self):
        binary = _binary_inputs(100, seed=9)
        b = beta_from_coefs(binary["coef_b0"].mean(), 0.0, binary["coef_u_frame"].mean(axis=0),
                            frame_idx=binary["frame_idx"], z_loglen=binary["z_loglen"])
        assert np.all(b >= 0.0) and np.all(b <= 0.5)

    def test_draws_bounded_including_residual(self):
        rng = np.random.default_rng(10)
        n_q, R = 50, 200
        b0 = rng.normal(0, 1, size=R)
        b_len = rng.normal(0, 0.3, size=R)
        u_frame = rng.normal(0, 1, size=(R, 3))
        frame_idx = rng.integers(0, 3, size=n_q)
        z_loglen = rng.normal(0, 1, size=n_q)
        residual = rng.normal(0, 3.0, size=(n_q, R))  # deliberately large residual
        b = beta_from_coefs(b0, b_len, u_frame, frame_idx=frame_idx, z_loglen=z_loglen,
                            residual=residual)
        assert np.all(b >= 0.0) and np.all(b <= 0.5)


class TestPooledVariants:
    def test_pooled_formulas_hold_per_replicate(self):
        binary = _binary_inputs(80, instrument_sd=0.1, seed=11)
        bt = _bt_inputs(40, cal_sd=0.1, seed=11)
        res = bootstrap(**{k: v for k, v in binary.items() if k != "true_p"}, **bt,
                        n_boot=500, seed=2)
        n_pf, n_pc = 80, 40
        expected_pooled_count = np.clip(
            (n_pf * res.passfail + n_pc * res.partial) / (n_pf + n_pc), 0.0, 1.0)
        expected_pooled_equal = np.clip((res.passfail + res.partial) / 2.0, 0.0, 1.0)
        # Recomposed from the already-clipped channel means; equality holds
        # whenever neither channel mean was itself clipped this replicate.
        unclipped = (res.passfail > 1e-9) & (res.passfail < 1 - 1e-9)
        assert np.allclose(expected_pooled_count[unclipped], res.pooled_count[unclipped])
        assert np.allclose(expected_pooled_equal, res.pooled_equal)

"""test_substantive_estimator.py — pins direct-binary-scoring-spec.md's algebra.

Each class targets one claim from direct-binary-scoring-spec.md section 20 that a
future "simplification" could quietly break:

  - binary_score == mean(v_q), exactly (section 1, 3-4)
  - every binary per-question value is in [0,1]; no clipping anywhere (section 1, 3)
  - automatic passes/fails land exactly on 1/0 (section 3)
  - identical verdict evidence gives identical credit regardless of candidate
    identity (section 1 -- the score is a pure function of v_q)
  - the partition identity S = sum(n_g * S_g) / sum(n_g) over a complete
    reasoning-group partition (section 12-13)
  - item resampling is the binary channel's only source of bootstrap
    variance -- disabling it collapses every replicate to the point
    estimate; enabling it varies only which questions were sampled
    (section 9)
  - the BT channel's three-layer bootstrap is unchanged
  - all-pass data scores 1 with a zero-width interval; all-fail scores 0
"""

import sys
from pathlib import Path

import numpy as np
import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from substantive.estimator import bootstrap, group_scores, plugin_point


def _bt_inputs(n_pc, *, seed=0, n_delta_draws=1000, n_cal_draws=500, cal_sd=0.0):
    rng = np.random.default_rng(seed)
    delta_true = rng.normal(0.5, 1.0, size=n_pc)
    delta_draws = delta_true[:, None] + rng.normal(0, 1.0, size=(n_pc, n_delta_draws))
    cal_rng = np.random.default_rng(seed + 8000)
    cal_a = (cal_rng.normal(0.0, cal_sd, size=n_cal_draws) if cal_sd > 0
            else np.zeros(n_cal_draws))
    cal_b = np.ones(n_cal_draws)
    return dict(delta_draws=delta_draws, cal_a=cal_a, cal_b=cal_b)


def _empty_bt():
    return dict(delta_draws=np.zeros((0, 10)), cal_a=np.zeros(10), cal_b=np.zeros(10))


class TestBinaryScoreIsTheMean:
    def test_passfail_equals_mean_v_q_exactly(self):
        rng = np.random.default_rng(1)
        v_hat = rng.uniform(0, 1, size=547)
        pt = plugin_point(v_hat=v_hat, **_empty_bt())
        assert pt.passfail == v_hat.mean()

    def test_exact_on_zero_one_verdicts(self):
        rng = np.random.default_rng(2)
        v_hat = rng.integers(0, 2, size=300).astype(float)
        pt = plugin_point(v_hat=v_hat, **_empty_bt())
        assert pt.passfail == v_hat.mean()
        assert pt.n_passfail == 300

    def test_all_pass_scores_one_with_zero_width_interval(self):
        v_hat = np.ones(50)
        pt = plugin_point(v_hat=v_hat, **_empty_bt())
        assert pt.passfail == 1.0
        boot = bootstrap(v_hat=v_hat, n_boot=200, seed=0, **_empty_bt())
        assert np.all(boot.passfail == 1.0)

    def test_all_fail_scores_zero_with_zero_width_interval(self):
        v_hat = np.zeros(50)
        pt = plugin_point(v_hat=v_hat, **_empty_bt())
        assert pt.passfail == 0.0
        boot = bootstrap(v_hat=v_hat, n_boot=200, seed=0, **_empty_bt())
        assert np.all(boot.passfail == 0.0)

    def test_identical_verdicts_give_identical_credit_regardless_of_candidate(self):
        """The binary score is a pure function of v_q -- nothing about which
        candidate produced it enters the computation."""
        v_hat = np.array([1.0, 0.0, 1.0, 1.0, 0.0])
        pt_a = plugin_point(v_hat=v_hat.copy(), **_empty_bt())
        pt_b = plugin_point(v_hat=v_hat.copy(), **_empty_bt())
        assert pt_a.passfail == pt_b.passfail
        assert np.array_equal(pt_a.p_binary, pt_b.p_binary)


class TestNoClippingAnywhere:
    def test_binary_values_stay_in_unit_interval(self):
        rng = np.random.default_rng(3)
        v_hat = rng.uniform(0, 1, size=200)
        pt = plugin_point(v_hat=v_hat, **_empty_bt())
        assert np.all(pt.p_binary >= 0.0) and np.all(pt.p_binary <= 1.0)

    def test_no_clip_call_anywhere_in_the_module(self):
        import inspect

        import substantive.estimator as est
        assert "np.clip" not in inspect.getsource(est)

    def test_bootstrap_replicates_stay_in_unit_interval(self):
        rng = np.random.default_rng(4)
        v_hat = rng.uniform(0, 1, size=200)
        res = bootstrap(v_hat=v_hat, n_boot=500, seed=1, **_empty_bt())
        assert np.all(res.passfail >= 0.0) and np.all(res.passfail <= 1.0)
        assert np.all(res.p_binary_qr >= 0.0) and np.all(res.p_binary_qr <= 1.0)

    def test_no_question_weight_parameter_exists(self):
        import inspect
        for fn in (plugin_point, bootstrap):
            params = inspect.signature(fn).parameters
            assert not any("weight" in p.lower() for p in params)


class TestAutomaticVerdicts:
    def test_pass_lands_exactly_on_one(self):
        v_hat = np.full(5, 0.37)
        auto_pf = np.array([1.0, np.nan, np.nan, np.nan, np.nan])
        pt = plugin_point(v_hat=v_hat, auto_pf=auto_pf, **_empty_bt())
        assert pt.p_binary[0] == 1.0

    def test_fail_lands_exactly_on_zero(self):
        v_hat = np.full(5, 0.37)
        auto_pf = np.array([0.0, np.nan, np.nan, np.nan, np.nan])
        pt = plugin_point(v_hat=v_hat, auto_pf=auto_pf, **_empty_bt())
        assert pt.p_binary[0] == 0.0

    def test_all_nan_reproduces_the_baseline(self):
        """Back-compat: every artifact written before automatic verdicts
        existed must produce bit-identical numbers."""
        v_hat = np.linspace(0, 1, 20)
        base = plugin_point(v_hat=v_hat, **_empty_bt())
        nan = plugin_point(v_hat=v_hat, auto_pf=np.full(20, np.nan), **_empty_bt())
        assert nan.passfail == base.passfail

    def test_empty_array_treated_as_absent(self):
        v_hat = np.linspace(0, 1, 20)
        base = plugin_point(v_hat=v_hat, **_empty_bt())
        empty = plugin_point(v_hat=v_hat, auto_pf=np.zeros(0), **_empty_bt())
        assert empty.passfail == base.passfail

    def test_wrong_length_override_raises(self):
        v_hat = np.linspace(0, 1, 5)
        with pytest.raises(ValueError):
            plugin_point(v_hat=v_hat, auto_pf=np.array([1.0, 0.0]), **_empty_bt())

    def test_partial_credit_auto_verdict_lands_exactly(self):
        bt = _bt_inputs(5, seed=1)
        auto_pc = np.full(5, np.nan)
        auto_pc[0] = 1.0
        pt = plugin_point(v_hat=np.zeros(0), auto_pc=auto_pc, **bt)
        assert pt.p_partial[0] == 1.0

    def test_bootstrap_override_removes_judgment_layer_variance(self):
        """A string comparison is not a noisy measurement, so the overridden
        BT row must be constant across replicates. Item resampling still
        runs over it."""
        bt = _bt_inputs(5, seed=1)
        auto_pc = np.full(5, np.nan)
        auto_pc[0] = 1.0
        res = bootstrap(v_hat=np.zeros(0), n_boot=200, seed=1, auto_pc=auto_pc, **bt)
        assert res.p_partial_qr[0].std() == 0.0
        assert res.p_partial_qr[1].std() > 0.0


class TestItemResamplingIsTheOnlyBinaryVariance:
    def test_item_disabled_collapses_every_replicate_to_the_point_estimate(self):
        rng = np.random.default_rng(5)
        v_hat = rng.uniform(0, 1, size=100)
        pt = plugin_point(v_hat=v_hat, **_empty_bt())
        res = bootstrap(v_hat=v_hat, n_boot=200, seed=1,
                        layers=("judgment", "instrument"), **_empty_bt())
        # np.allclose, not ==: summing the same values via .mean(axis=0) on a
        # (100, 200) array vs plain .mean() on a (100,) array can differ in
        # the last bit or two from floating-point summation order -- not a
        # sign anything was clipped or resampled.
        assert np.allclose(res.passfail, pt.passfail, atol=1e-12)

    def test_item_enabled_varies_only_by_which_questions_are_sampled(self):
        rng = np.random.default_rng(6)
        v_hat = rng.uniform(0, 1, size=100)
        res = bootstrap(v_hat=v_hat, n_boot=500, seed=1, layers=("item",), **_empty_bt())
        assert np.std(res.passfail) > 0
        assert np.all(res.passfail >= 0.0) and np.all(res.passfail <= 1.0)

    def test_fixed_seed_reproduces_intervals_exactly(self):
        rng = np.random.default_rng(7)
        v_hat = rng.uniform(0, 1, size=100)
        res_a = bootstrap(v_hat=v_hat, n_boot=500, seed=42, **_empty_bt())
        res_b = bootstrap(v_hat=v_hat, n_boot=500, seed=42, **_empty_bt())
        assert np.array_equal(res_a.passfail, res_b.passfail)

    def test_judgment_and_instrument_layers_do_not_move_the_binary_channel(self):
        """There is no per-question judge-error model left on the binary
        side, so toggling 'judgment'/'instrument' must leave it
        byte-identical -- only 'item' can move it. The two channels draw
        from independent generators, so BT-layer toggles cannot leak into
        the binary channel's stream either."""
        rng = np.random.default_rng(8)
        v_hat = rng.uniform(0, 1, size=100)
        with_all = bootstrap(v_hat=v_hat, n_boot=300, seed=3,
                             layers=("judgment", "instrument", "item"), **_empty_bt())
        item_only = bootstrap(v_hat=v_hat, n_boot=300, seed=3, layers=("item",), **_empty_bt())
        assert np.array_equal(with_all.passfail, item_only.passfail)


class TestDeltaIndependence:
    def test_distinct_index_per_question(self):
        bt = _bt_inputs(30, seed=7)
        res = bootstrap(v_hat=np.zeros(0), n_boot=50, seed=1,
                        layers=("judgment", "instrument", "item"), **bt)
        # p_partial_qr varies question-to-question within a fixed replicate
        # column -- if the same index were shared, every question's value
        # under a shared instrument draw would move in lockstep.
        col = res.p_partial_qr[:, 0]
        assert np.std(col) > 0

    def test_two_identical_questions_pick_different_delta_indices(self):
        """Duplicate one question's Delta draws across two rows: if the
        draw index were shared, both rows would be identical in every
        replicate. Independent per-question indices decorrelate them."""
        rng = np.random.default_rng(0)
        one_question = rng.normal(0.5, 1.0, size=1000)
        delta_draws = np.tile(one_question, (2, 1))
        bt = dict(delta_draws=delta_draws, cal_a=np.zeros(50), cal_b=np.ones(50))
        res = bootstrap(v_hat=np.zeros(0), n_boot=200, seed=2,
                        layers=("judgment", "instrument", "item"), **bt)
        assert not np.allclose(res.p_partial_qr[0], res.p_partial_qr[1])

    def test_width_scales_as_inverse_sqrt_m(self):
        def width(m, seed):
            bt = _bt_inputs(m, seed=seed)
            res = bootstrap(v_hat=np.zeros(0), n_boot=3000, seed=seed + 50,
                            layers=("judgment", "instrument", "item"), **bt)
            lo, hi = np.percentile(res.partial, [2.5, 97.5])
            return hi - lo

        ratio = width(400, 1) / width(40, 1)
        assert abs(ratio - 1 / np.sqrt(10)) < 0.08


class TestBTInstrumentLayer:
    """BT keeps the full three-layer bootstrap; beta_idx is always None now
    (no beta coefficient bank in this scorer)."""

    def test_cal_idx_present_beta_idx_absent(self):
        bt = _bt_inputs(20, cal_sd=0.1, seed=6)
        res = bootstrap(v_hat=np.zeros(0), n_boot=100, seed=1, return_indices=True, **bt)
        assert res.cal_idx.shape == (100,)
        assert res.beta_idx is None

    def test_width_grows_with_instrument_noise(self):
        def width(cal_sd, seed):
            bt = _bt_inputs(300, cal_sd=cal_sd, seed=seed)
            res = bootstrap(v_hat=np.zeros(0), n_boot=2000, seed=seed + 500, **bt)
            lo, hi = np.percentile(res.partial, [2.5, 97.5])
            return hi - lo

        noisy = np.mean([width(0.3, s) for s in range(3)])
        quiet = np.mean([width(0.0, s) for s in range(3)])
        assert noisy > quiet


class TestPooledVariants:
    def test_pooled_formulas_hold_per_replicate(self):
        rng = np.random.default_rng(11)
        v_hat = rng.uniform(0, 1, size=80)
        bt = _bt_inputs(40, cal_sd=0.1, seed=11)
        res = bootstrap(v_hat=v_hat, n_boot=500, seed=2, **bt)
        n_pf, n_pc = 80, 40
        expected_pooled_count = (n_pf * res.passfail + n_pc * res.partial) / (n_pf + n_pc)
        expected_pooled_equal = (res.passfail + res.partial) / 2.0
        assert np.allclose(expected_pooled_count, res.pooled_count)
        assert np.allclose(expected_pooled_equal, res.pooled_equal)


class TestGroupScores:
    """substantive/groups.py's reasoning-type breakdown: group_scores
    combines both channels count-weighted within a group. Points come from
    the plugin arrays (not the bootstrap qr mean) specifically so a
    count-weighted average of group points reconstructs pooled_count
    exactly -- an identity, not an approximation."""

    def _bank(self, n_pf=80, n_pc=40, seed=11):
        rng = np.random.default_rng(seed)
        v_hat = rng.uniform(0, 1, size=n_pf)
        bt = _bt_inputs(n_pc, cal_sd=0.1, seed=seed)
        pt = plugin_point(v_hat=v_hat, **bt)
        boot = bootstrap(v_hat=v_hat, n_boot=500, seed=2, **bt)
        return pt, boot

    def test_partition_reconstructs_pooled_count_exactly(self):
        """Splitting the pass/fail and partial questions into two disjoint
        groups (by an arbitrary parity split within each channel) and
        count-weighting the two group points must reproduce pt.pooled_count
        exactly, since the groups partition every question."""
        pt, boot = self._bank()
        n_pf, n_pc = pt.n_passfail, pt.n_partial
        rng = np.random.default_rng(0)
        mask_pf_a = np.arange(n_pf) % 2 == 0
        mask_pc_a = np.arange(n_pc) % 2 == 0
        mask_pf_b, mask_pc_b = ~mask_pf_a, ~mask_pc_a

        a = group_scores(pt.p_binary, pt.p_partial, boot.p_binary_qr, boot.p_partial_qr,
                         mask_pf_a, mask_pc_a, rng=rng)
        b = group_scores(pt.p_binary, pt.p_partial, boot.p_binary_qr, boot.p_partial_qr,
                         mask_pf_b, mask_pc_b, rng=rng)

        assert a.n_pf + b.n_pf == n_pf
        assert a.n_pc + b.n_pc == n_pc
        recombined = (a.n * a.point + b.n * b.point) / (a.n + b.n)
        assert abs(recombined - pt.pooled_count) < 1e-12

    def test_three_way_partition_over_a_complete_group_split(self):
        """Not special to two groups: an arbitrary three-way complete split
        of both channels reconstructs pooled_count to the same tolerance."""
        pt, boot = self._bank(n_pf=90, n_pc=45)
        n_pf, n_pc = pt.n_passfail, pt.n_partial
        rng = np.random.default_rng(1)
        group_pf = np.arange(n_pf) % 3
        group_pc = np.arange(n_pc) % 3
        weighted_sum, total_n = 0.0, 0
        for g in range(3):
            gr = group_scores(pt.p_binary, pt.p_partial, boot.p_binary_qr, boot.p_partial_qr,
                              group_pf == g, group_pc == g, rng=rng)
            weighted_sum += gr.n * gr.point
            total_n += gr.n
        assert total_n == n_pf + n_pc
        assert abs(weighted_sum / total_n - pt.pooled_count) < 1e-12

    def test_single_channel_group_matches_that_channels_mean(self):
        """A group with only pass/fail questions (empty partial mask)
        returns exactly that channel's plugin mean."""
        pt, boot = self._bank()
        mask_pf = np.ones(pt.n_passfail, dtype=bool)
        mask_pc = np.zeros(pt.n_partial, dtype=bool)
        g = group_scores(pt.p_binary, pt.p_partial, boot.p_binary_qr, boot.p_partial_qr,
                         mask_pf, mask_pc, rng=np.random.default_rng(1))
        assert g.n_pf == pt.n_passfail
        assert g.n_pc == 0
        assert abs(g.point - pt.p_binary.mean()) < 1e-12

    def test_empty_group_is_all_nan_with_zero_n(self):
        pt, boot = self._bank()
        mask_pf = np.zeros(pt.n_passfail, dtype=bool)
        mask_pc = np.zeros(pt.n_partial, dtype=bool)
        g = group_scores(pt.p_binary, pt.p_partial, boot.p_binary_qr, boot.p_partial_qr,
                         mask_pf, mask_pc, rng=np.random.default_rng(1))
        assert g.n == 0 and g.n_pf == 0 and g.n_pc == 0
        assert np.isnan(g.point) and np.isnan(g.lo) and np.isnan(g.hi)

    def test_ci_brackets_point_estimate(self):
        pt, boot = self._bank(n_pf=200, n_pc=100)
        n_pf, n_pc = pt.n_passfail, pt.n_partial
        rng = np.random.default_rng(3)
        mask_pf = np.arange(n_pf) < n_pf // 2
        mask_pc = np.arange(n_pc) < n_pc // 2
        g = group_scores(pt.p_binary, pt.p_partial, boot.p_binary_qr, boot.p_partial_qr,
                         mask_pf, mask_pc, rng=rng)
        assert g.lo <= g.point <= g.hi

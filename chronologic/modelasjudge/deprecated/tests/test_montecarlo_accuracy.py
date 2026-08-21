"""Tests for montecarlo_accuracy.py — pure numpy, no PyMC required."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from montecarlo_accuracy import (
    _collapse_verdicts,
    _mom_bsc,
    corrected_probabilities,
    point_estimates,
    bootstrap_ci,
    raw_observed,
    score_ranges,
    range_normalize,
)


# ---------------------------------------------------------------------------
# _collapse_verdicts
# ---------------------------------------------------------------------------

def test_collapse_single_win():
    assert _collapse_verdicts([1], [0]) == 1.0

def test_collapse_single_loss():
    assert _collapse_verdicts([0], [0]) == 0.0

def test_collapse_paired_agree_win():
    # Both orderings of the same gt agree on a win
    assert _collapse_verdicts([1, 1], [0, 0]) == 1.0

def test_collapse_paired_split_dropped():
    # Paired ordering splits (0.5 block) → no surviving verdicts → 0.5 (uninformative)
    assert _collapse_verdicts([1, 0], [0, 0]) == 0.5

def test_collapse_two_gt_indices():
    # gt_index 0 → win, gt_index 1 → loss → mean([1,0]) = 0.5
    assert _collapse_verdicts([1, 0], [0, 1]) == 0.5

def test_collapse_two_gt_indices_both_win():
    # gt_index 0 → win, gt_index 1 → win
    assert _collapse_verdicts([1, 0, 1, 1], [0, 0, 1, 1]) == 1.0
    # Block 0: [1,0] → 0.5 → dropped; Block 1: [1,1] → 1.0 → win
    # Only block 1 survives → 1.0
    assert _collapse_verdicts([1, 0, 1, 1], [0, 0, 1, 1]) == 1.0

def test_collapse_empty():
    assert _collapse_verdicts([], []) == 0.5


# ---------------------------------------------------------------------------
# _mom_bsc (method-of-moments channel inversion)
# ---------------------------------------------------------------------------

def test_mom_high_reliability_win():
    # r=0.95, obs=1.0 → π̂ = 0.95/0.9 ≈ 1.056 → clamped to 1.0
    assert _mom_bsc(1.0, 0.95) == pytest.approx(1.0)

def test_mom_high_reliability_loss():
    # r=0.95, obs=0.0 → π̂ = -0.05/0.9 → clamped to 0.0
    assert _mom_bsc(0.0, 0.95) == pytest.approx(0.0)

def test_mom_upward_correction():
    # obs=0.7, r=0.8 → π̂ = (0.7 - 0.2) / 0.6 = 0.5/0.6 ≈ 0.833
    assert _mom_bsc(0.7, 0.8) == pytest.approx(0.5 / 0.6, rel=1e-6)

def test_mom_half_channel():
    # r=0.5 → degenerate channel, return obs unchanged
    assert _mom_bsc(0.7, 0.5) == pytest.approx(0.7)

def test_mom_clamp_upper():
    assert _mom_bsc(1.0, 0.99) == pytest.approx(1.0)

def test_mom_clamp_lower():
    assert _mom_bsc(0.0, 0.99) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Helpers to build minimal synthetic judge/discrim dicts
# ---------------------------------------------------------------------------

def _make_data(n: int, *, qf_score=1, r_q=0.99, style_score=0.9, r_s=0.8,
               n_ctx=0, ctx_score=1, r_c=0.9, style_na_ids=None):
    """Build minimal judge + discrim dicts for n questions, IDs '1'..'n'."""
    judge = {"question_fit": {}, "context_fit": {}, "book_context_qnums": []}
    discrim = {"style": {}, "below_threshold": style_na_ids or []}
    for i in range(1, n + 1):
        q = str(i)
        qf_val = qf_score[i - 1] if isinstance(qf_score, list) else qf_score
        judge["question_fit"][q] = {
            "r_q": r_q, "scores": [qf_val], "gt_indices": [0],
        }
        style_val = style_score[i - 1] if isinstance(style_score, list) else style_score
        discrim["style"][q] = {"r_q": r_s, "continuous_scores": [style_val], "gt_indices": [0]}

    for i in range(1, n_ctx + 1):
        q = str(i)
        judge["book_context_qnums"].append(q)
        judge["context_fit"][q] = {
            "r_q": r_c, "scores": [ctx_score], "gt_indices": [0],
        }
    return judge, discrim


# ---------------------------------------------------------------------------
# corrected_probabilities
# ---------------------------------------------------------------------------

def test_corrected_probs_all_pass():
    judge, discrim = _make_data(5, qf_score=1, r_q=0.99, style_score=0.9, r_s=0.8)
    qnums, probs = corrected_probabilities(judge, discrim)
    assert qnums == ["1", "2", "3", "4", "5"]
    for q in qnums:
        pi_q, pi_c, pi_s = probs[q]
        assert pi_q == pytest.approx(0.99)  # obs=1, posterior = r_q
        assert pi_c == pytest.approx(1.0)   # context NA → auto-pass
        assert pi_s == pytest.approx(0.8)   # obs≥0.5, posterior = r_s

def test_corrected_probs_style_na():
    judge, discrim = _make_data(3, style_na_ids=["2"])
    qnums, probs = corrected_probabilities(judge, discrim)
    assert probs["2"][2] == pytest.approx(1.0)   # style NA → auto-pass
    assert probs["1"][2] != pytest.approx(1.0)
    assert probs["3"][2] != pytest.approx(1.0)

def test_corrected_probs_context_scored():
    judge, discrim = _make_data(4, n_ctx=2, ctx_score=1, r_c=0.9)
    qnums, probs = corrected_probabilities(judge, discrim)
    # Questions 1 and 2 have real context scores; 3 and 4 auto-pass
    pi_c_1 = probs["1"][1]
    pi_c_3 = probs["3"][1]
    assert pi_c_1 == pytest.approx(0.9)   # obs=1, posterior = r_c = 0.9
    assert pi_c_3 == pytest.approx(1.0)   # NA → auto-pass

def test_corrected_probs_context_fail():
    judge, discrim = _make_data(2, n_ctx=1, ctx_score=0, r_c=0.9)
    _, probs = corrected_probabilities(judge, discrim)
    # q "1" has context fail: obs=0, posterior = 1 − r_c = 0.1
    assert probs["1"][1] == pytest.approx(0.1)
    # q "2" has no context: auto-pass
    assert probs["2"][1] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# raw_observed
# ---------------------------------------------------------------------------

def test_raw_all_pass():
    judge, discrim = _make_data(10, qf_score=1, style_score=0.9)
    qnums, _ = corrected_probabilities(judge, discrim)
    assert raw_observed(qnums, judge, discrim)["binary_accuracy"] == pytest.approx(1.0)

def test_raw_all_fail():
    judge, discrim = _make_data(10, qf_score=0, style_score=0.1)
    qnums, _ = corrected_probabilities(judge, discrim)
    assert raw_observed(qnums, judge, discrim)["binary_accuracy"] == pytest.approx(0.0)

def test_raw_style_na_auto_pass():
    # With style NA, binary accuracy depends only on question_fit
    judge, discrim = _make_data(4, qf_score=1, style_na_ids=["1","2","3","4"])
    qnums, _ = corrected_probabilities(judge, discrim)
    assert raw_observed(qnums, judge, discrim)["binary_accuracy"] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# point_estimates
# ---------------------------------------------------------------------------

def test_point_estimate_all_pass():
    judge, discrim = _make_data(10, qf_score=1, r_q=0.99, style_score=0.9, r_s=0.8)
    qnums, probs = corrected_probabilities(judge, discrim)
    ctx_qs = set(judge["book_context_qnums"])
    below  = set(str(q) for q in discrim["below_threshold"])
    pts = point_estimates(qnums, probs, ctx_qs, below)
    # pi_q=0.99, pi_c=1.0 (NA), pi_s=0.8 → binary_accuracy = 0.99*1.0*0.8 = 0.792
    assert pts["binary_accuracy"] == pytest.approx(0.99 * 0.8, rel=1e-5)
    assert pts["question_fit"]    == pytest.approx(0.99)

def test_point_estimate_matches_product():
    # Verify binary_accuracy point = mean_q(pi_q * pi_c * pi_s)
    judge, discrim = _make_data(
        6,
        qf_score=[1,1,0,0,1,0],   # type: ignore[arg-type]
        r_q=0.8,
        style_score=[0.8, 0.6, 0.4, 0.9, 0.7, 0.3],
    )
    qnums, probs = corrected_probabilities(judge, discrim)
    ctx_qs = set(judge["book_context_qnums"])
    below  = set(str(q) for q in discrim["below_threshold"])
    pts = point_estimates(qnums, probs, ctx_qs, below)
    manual = np.mean([probs[q][0] * probs[q][1] * probs[q][2] for q in qnums])
    assert pts["binary_accuracy"] == pytest.approx(float(manual), rel=1e-9)


# ---------------------------------------------------------------------------
# bootstrap_ci
# ---------------------------------------------------------------------------

def test_bootstrap_mean_approx_point():
    """Bootstrap mean of binary_accuracy should track the point estimate."""
    judge, discrim = _make_data(50, qf_score=1, r_q=0.95, style_score=0.75)
    qnums, probs = corrected_probabilities(judge, discrim)
    ctx_qs = set(judge["book_context_qnums"])
    below  = set(str(q) for q in discrim["below_threshold"])
    pts = point_estimates(qnums, probs, ctx_qs, below)
    cis = bootstrap_ci(qnums, probs, ctx_qs, below, n_iterations=2000, seed=7)
    # Bootstrap mean should be within 3 pp of the deterministic point estimate
    assert abs(cis["binary_accuracy"]["mean"] - pts["binary_accuracy"]) < 0.03

def test_bernoulli_ci_wider_than_product_ci():
    """CI from Bernoulli-AND bootstrap should be wider than a pure-product bootstrap
    for questions near the decision threshold (where per-question uncertainty is real)."""
    # Mix of borderline pi values to maximise Bernoulli variance
    style_scores = [0.55, 0.45, 0.52, 0.48, 0.51, 0.49] * 10
    judge, discrim = _make_data(
        60,
        qf_score=[1, 0] * 30,
        r_q=0.7,                  # low reliability → MOM pi near threshold
        style_score=style_scores,
    )
    qnums, probs = corrected_probabilities(judge, discrim)
    ctx_qs = set(judge["book_context_qnums"])
    below  = set(str(q) for q in discrim["below_threshold"])

    # Bernoulli-AND bootstrap (our method)
    cis_ba = bootstrap_ci(qnums, probs, ctx_qs, below, n_iterations=3000, seed=1)
    width_ba = cis_ba["binary_accuracy"]["ci_upper"] - cis_ba["binary_accuracy"]["ci_lower"]

    # Pure product bootstrap (resample questions, mean of products — no Bernoulli)
    rng = np.random.default_rng(1)
    joints = np.array([probs[q][0] * probs[q][1] * probs[q][2] for q in qnums])
    N = len(qnums)
    prod_samples = [np.mean(joints[rng.integers(0, N, N)]) for _ in range(3000)]
    width_prod = np.percentile(prod_samples, 97.5) - np.percentile(prod_samples, 2.5)

    assert width_ba > width_prod, (
        f"Bernoulli CI width {width_ba:.4f} should exceed product CI width {width_prod:.4f}"
    )

def test_ci_contains_point_estimate():
    judge, discrim = _make_data(30, qf_score=1, r_q=0.9, style_score=0.8)
    qnums, probs = corrected_probabilities(judge, discrim)
    ctx_qs = set(judge["book_context_qnums"])
    below  = set(str(q) for q in discrim["below_threshold"])
    pts = point_estimates(qnums, probs, ctx_qs, below)
    cis = bootstrap_ci(qnums, probs, ctx_qs, below, n_iterations=2000, seed=3)
    ba  = cis["binary_accuracy"]
    # The deterministic point (mean of products) should lie within the bootstrap CI
    assert ba["ci_lower"] <= pts["binary_accuracy"] <= ba["ci_upper"]


# ---------------------------------------------------------------------------
# score_ranges
# ---------------------------------------------------------------------------

def test_score_ranges_constant_reliability():
    """Per-aspect (min, max) = (1-r, r) when all questions share the same reliability."""
    r_q, r_s = 0.8, 0.75
    judge, discrim = _make_data(10, r_q=r_q, style_score=0.9, r_s=r_s)
    qnums, _ = corrected_probabilities(judge, discrim)
    ctx_qs = set(judge["book_context_qnums"])
    below  = set(str(q) for q in discrim["below_threshold"])
    rngs = score_ranges(qnums, judge, discrim, ctx_qs, below)

    lo_q, hi_q = rngs["question_fit"]
    assert lo_q == pytest.approx(1 - r_q)
    assert hi_q == pytest.approx(r_q)

    lo_s, hi_s = rngs["style"]
    assert lo_s == pytest.approx(1 - r_s)
    assert hi_s == pytest.approx(r_s)

    # context has no scored questions → (nan, nan)
    lo_c, hi_c = rngs["context_fit"]
    assert lo_c != lo_c  # nan
    assert hi_c != hi_c


def test_score_ranges_all_style_na():
    """When all questions are style-NA, style range is (nan, nan)."""
    n = 5
    ids = [str(i) for i in range(1, n + 1)]
    judge, discrim = _make_data(n, style_na_ids=ids)
    qnums, _ = corrected_probabilities(judge, discrim)
    ctx_qs = set(judge["book_context_qnums"])
    below  = set(str(q) for q in discrim["below_threshold"])
    rngs = score_ranges(qnums, judge, discrim, ctx_qs, below)

    lo_s, hi_s = rngs["style"]
    assert lo_s != lo_s   # nan
    assert hi_s != hi_s

    # AND ceiling for style-NA questions: style contributes 1.0; only r_q and context
    # r_q default is 0.99 in _make_data
    lo_and, hi_and = rngs["binary_accuracy"]
    assert lo_and == pytest.approx(1 - 0.99)  # (1-r_q) * 1 * 1
    assert hi_and == pytest.approx(0.99)       # r_q * 1 * 1


def test_score_ranges_and_ceiling_product():
    """AND ceiling = mean(r_q * r_c * r_s) over all questions; NA-aspects use 1.0."""
    r_q, r_c, r_s = 0.9, 0.85, 0.80
    n_ctx = 4
    judge, discrim = _make_data(8, r_q=r_q, n_ctx=n_ctx, ctx_score=1, r_c=r_c,
                                style_score=0.9, r_s=r_s)
    qnums, _ = corrected_probabilities(judge, discrim)
    ctx_qs = set(judge["book_context_qnums"])  # "1".."4"
    below  = set(str(q) for q in discrim["below_threshold"])
    rngs = score_ranges(qnums, judge, discrim, ctx_qs, below)

    # Questions 1-4 have context: ceil = r_q * r_c * r_s
    # Questions 5-8 no context:   ceil = r_q * 1.0 * r_s
    expected_ceil = (4 * r_q * r_c * r_s + 4 * r_q * 1.0 * r_s) / 8
    expected_floor = (4 * (1-r_q) * (1-r_c) * (1-r_s) + 4 * (1-r_q) * 1.0 * (1-r_s)) / 8

    lo_and, hi_and = rngs["binary_accuracy"]
    assert hi_and == pytest.approx(expected_ceil, rel=1e-6)
    assert lo_and == pytest.approx(expected_floor, rel=1e-6)


# ---------------------------------------------------------------------------
# range_normalize
# ---------------------------------------------------------------------------

def test_range_normalize_endpoints():
    """norm(lo) = 0, norm(hi) = 1 exactly."""
    nr = range_normalize(0.5, 0.2, 0.8, lo=0.2, hi=0.8)
    assert nr["norm_ci_lower"] == pytest.approx(0.0)
    assert nr["norm_ci_upper"] == pytest.approx(1.0)
    assert nr["norm_point"]    == pytest.approx(0.5)


def test_range_normalize_interior():
    nr = range_normalize(0.6, 0.4, 0.8, lo=0.2, hi=0.8)
    # (0.6-0.2)/(0.8-0.2) = 0.4/0.6 ≈ 0.6667
    assert nr["norm_point"] == pytest.approx(0.4 / 0.6, rel=1e-6)


def test_range_normalize_degenerate():
    """hi == lo → all nan."""
    nr = range_normalize(0.5, 0.4, 0.6, lo=0.7, hi=0.7)
    assert nr["norm_point"]    != nr["norm_point"]   # nan
    assert nr["norm_ci_lower"] != nr["norm_ci_lower"]
    assert nr["norm_ci_upper"] != nr["norm_ci_upper"]


def test_range_normalize_all_pass_saturates_to_one():
    """When adjusted score equals the ceiling (fully passing), norm_point ≈ 1.0."""
    # r=0.8, all pass → adjusted = 0.8 = ceiling; floor = 0.2
    r = 0.8
    nr = range_normalize(r, r - 0.01, r, lo=1 - r, hi=r)
    assert nr["norm_point"] == pytest.approx(1.0)


def test_range_normalize_clamps():
    """Values outside [lo, hi] due to CI sampling are clamped to [0, 1]."""
    nr = range_normalize(0.5, 0.1, 0.9, lo=0.2, hi=0.8)
    # ci_lower 0.1 < lo 0.2 → clamp to 0
    assert nr["norm_ci_lower"] == pytest.approx(0.0)
    # ci_upper 0.9 > hi 0.8 → clamp to 1
    assert nr["norm_ci_upper"] == pytest.approx(1.0)

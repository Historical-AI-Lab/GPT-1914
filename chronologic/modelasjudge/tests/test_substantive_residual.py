"""test_substantive_residual.py — pins the sigma_u moment-match solve.

Three properties matter: (1) a planted sigma_u is recoverable on average
over many seeds, since a single 100-pair/n=2 draw is far too noisy to pin
down alone; (2) noiseless data (no extra-binomial variance at all) is
flagged underdispersed rather than fit to a spurious sigma_u; (3) the
reported overdispersion ratio reproduces the textbook 1 + (n-1)*rho
formula for exchangeable binary trials, again averaged over seeds.

Throughout, p = expit(eta + u) with NO division by 2: eta and the k/n data
here live on the logit(2*beta) scale fit_beta_regression_nocontext.py's
PyMC model actually fits (k_i ~ Binomial(n_i, sigmoid(eta_i)), no factor
of two in that likelihood either). Dividing by 2 inside this module was
tried and empirically falsified: against the real
gt_pairs_anthropic_claude-sonnet-4-6__0.4.jsonl data (k-distribution
{0:84, 1:9, 2:7} at n=2, matching deprecated/substantive-uncertainty-spec.md's own
example) it produced a 3.0x overdispersion ratio against the spec-quoted
1.36-1.6x; removing the /2 reproduced 1.555x exactly in range.
"""

import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.special import expit, logit

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from substantive.residual import logitnormal_moments, solve_sigma_u


class TestRecoverPlantedSigma:
    def test_recovers_within_monte_carlo_tolerance_over_20_seeds(self):
        true_sigma = 0.8
        n_pairs = 100
        n = np.full(n_pairs, 2)
        recovered = []
        for seed in range(20):
            rng = np.random.default_rng(seed)
            eta = rng.normal(logit(0.115), 0.5, size=n_pairs)
            u = rng.normal(0, true_sigma, size=n_pairs)
            p_true = expit(eta + u)
            k = rng.binomial(n, p_true)
            sigma_u, _ = solve_sigma_u(k, n, eta)
            recovered.append(sigma_u)
        assert abs(np.mean(recovered) - true_sigma) < 0.15


class TestUnderdispersed:
    def test_noiseless_data_is_flagged_not_fit(self):
        """k_i pinned to its point prediction (no binomial sampling noise at
        all) is less dispersed than even sigma_u=0 predicts, so no root
        exists and the solver must not fabricate a sigma_u."""
        rng = np.random.default_rng(0)
        n_pairs = 100
        n = np.full(n_pairs, 2)
        eta = rng.normal(logit(0.115), 0.3, size=n_pairs)
        p0 = expit(eta)
        k = np.round(n * p0).astype(int)
        sigma_u, diagnostics = solve_sigma_u(k, n, eta)
        assert sigma_u == 0.0
        assert diagnostics["underdispersed"] is True

    def test_never_raises_on_pathological_input(self):
        # n=0 pairs alongside real ones; degenerate but must not raise.
        k = np.array([0, 2, 1])
        n = np.array([0, 2, 2])
        eta = np.array([0.0, -1.0, 1.0])
        sigma_u, diagnostics = solve_sigma_u(k, n, eta)
        assert sigma_u >= 0.0
        assert "underdispersed" in diagnostics


class TestOverdispersionRatio:
    @pytest.mark.parametrize("rho_true", [0.2, 0.4, 0.6])
    def test_ratio_reproduces_1_plus_n_minus_1_rho(self, rho_true):
        mean_p = 0.115
        n_trials = 2
        ab_sum = 1.0 / rho_true - 1.0
        a, b = mean_p * ab_sum, (1 - mean_p) * ab_sum
        n_pairs = 200
        n = np.full(n_pairs, n_trials)
        eta = np.full(n_pairs, logit(mean_p))

        ratios = []
        for seed in range(50):
            rng = np.random.default_rng(seed)
            p_true = rng.beta(a, b, size=n_pairs)
            k = rng.binomial(n, p_true)
            _, diagnostics = solve_sigma_u(k, n, eta)
            ratios.append(diagnostics["overdispersion_ratio"])

        predicted = 1 + (n_trials - 1) * rho_true
        assert abs(np.mean(ratios) - predicted) < 0.05

    def test_real_gt_pair_data_reproduces_spec_quoted_range(self):
        """The exact scenario that caught the /2 bug: real GT-vs-GT pairs,
        k-distribution {0:84, 1:9, 2:7} at n=2 (matching
        deprecated/substantive-uncertainty-spec.md's own worked example), should give
        an overdispersion ratio in the spec-quoted 1.36-1.6 range."""
        path = MODELASJUDGE / "beta_reliability" / "gt_pairs_anthropic_claude-sonnet-4-6__0.4.jsonl"
        if not path.exists():
            pytest.skip(f"{path} not present")
        import json
        recs = [json.loads(l) for l in path.open() if l.strip()]
        k = np.array([r["k_nontie"] for r in recs], dtype=float)
        n = np.array([r["n_valid_trials"] for r in recs], dtype=float)
        mean_p = float(k.sum() / n.sum())
        eta = np.full(len(recs), logit(mean_p))
        _, diagnostics = solve_sigma_u(k, n, eta)
        assert 1.3 < diagnostics["overdispersion_ratio"] < 1.7


class TestLogitnormalMoments:
    def test_sigma_zero_collapses_to_point_mass(self):
        eta = np.array([-2.0, 0.0, 2.0])
        p_bar, e_p2 = logitnormal_moments(eta, 0.0)
        expected = expit(eta)
        assert np.allclose(p_bar, expected)
        assert np.allclose(e_p2, expected ** 2)

    def test_bounded_by_unit_interval(self):
        eta = np.array([-5.0, 0.0, 5.0, 20.0])
        p_bar, e_p2 = logitnormal_moments(eta, 1.5)
        assert np.all(p_bar >= 0.0) and np.all(p_bar <= 1.0)
        assert np.all(e_p2 >= 0.0) and np.all(e_p2 <= 1.0)

    def test_larger_sigma_pulls_mean_toward_half(self):
        """expit is S-shaped, so averaging over wider noise pulls p_bar
        toward 0.5 (Jensen), regardless of sign of eta."""
        eta = np.array([3.0])
        p_small, _ = logitnormal_moments(eta, 0.1)
        p_large, _ = logitnormal_moments(eta, 4.0)
        assert p_large[0] < p_small[0]
        assert p_large[0] > 0.5

"""test_substantive_residual.py — pins the sigma_u moment-match solve.

Three properties matter: (1) a planted sigma_u is recoverable on average
over many seeds, since a single 100-pair/n=2 draw is far too noisy to pin
down alone; (2) noiseless data (no extra-binomial variance at all) is
flagged underdispersed rather than fit to a spurious sigma_u; (3) the
reported overdispersion ratio reproduces the textbook 1 + (n-1)*rho
formula for exchangeable binary trials, again averaged over seeds.
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
            eta = rng.normal(logit(0.23), 0.5, size=n_pairs)
            u = rng.normal(0, true_sigma, size=n_pairs)
            p_true = expit(eta + u) / 2
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
        eta = rng.normal(logit(0.23), 0.3, size=n_pairs)
        p0 = expit(eta) / 2.0
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
        eta = np.full(n_pairs, logit(2 * mean_p))

        ratios = []
        for seed in range(50):
            rng = np.random.default_rng(seed)
            p_true = rng.beta(a, b, size=n_pairs)
            k = rng.binomial(n, p_true)
            _, diagnostics = solve_sigma_u(k, n, eta)
            ratios.append(diagnostics["overdispersion_ratio"])

        predicted = 1 + (n_trials - 1) * rho_true
        assert abs(np.mean(ratios) - predicted) < 0.05


class TestLogitnormalMoments:
    def test_sigma_zero_collapses_to_point_mass(self):
        eta = np.array([-2.0, 0.0, 2.0])
        p_bar, e_p2 = logitnormal_moments(eta, 0.0)
        expected = expit(eta) / 2.0
        assert np.allclose(p_bar, expected)
        assert np.allclose(e_p2, expected ** 2)

    def test_bounded_by_one_half(self):
        eta = np.array([-5.0, 0.0, 5.0, 20.0])
        p_bar, e_p2 = logitnormal_moments(eta, 1.5)
        assert np.all(p_bar <= 0.5)
        assert np.all(e_p2 <= 0.25)

    def test_larger_sigma_pulls_mean_toward_quarter(self):
        """expit is S-shaped, so averaging over wider noise pulls p_bar
        toward the midpoint of [0, 0.5] (Jensen), regardless of sign of eta."""
        eta = np.array([3.0])
        p_small, _ = logitnormal_moments(eta, 0.1)
        p_large, _ = logitnormal_moments(eta, 4.0)
        assert p_large[0] < p_small[0]

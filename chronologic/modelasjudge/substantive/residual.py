"""substantive/residual.py — the sigma_u moment-match solve (spec §4).

beta is instrument-level, not per-question: only ~100 GT-vs-GT pairs were
ever tested, at 2 trials each, and fit_beta_regression_nocontext.py
post-stratifies them through one shared regression. The complete scheme is
a shared coefficient draw plus an independent per-question residual term,
because true beta_q scatters around its predicted value (R^2 < 1).

The regression targets 2*beta directly: fit_beta_regression_nocontext.py's
PyMC likelihood is k_i ~ Binomial(n_i, sigmoid(eta_i)) with no factor of
two anywhere, because k_i/n_i (non-tie count over valid trials) *is* an
observation of 2*beta_i. So this module's residual u_q lives on that same
logit(2*beta) scale as eta_i, and everything here -- logitnormal_moments,
solve_sigma_u -- operates on p = expit(eta + u) with no division. Only the
*downstream* consumer (substantive.estimator.beta_from_coefs) halves the
result once, at the very end, to get the actual beta_q <= 0.5 that
Rogan-Gladen needs; halving here as well would silently refit sigma_u
against a mean half the size of the real k_i/n_i rate, inflating the
apparent overdispersion (caught empirically: fitting against real
GT-vs-GT pairs gave a 3.0x ratio against a /2 version of this code,
against the spec-quoted 1.36-1.6x once the /2 was removed).

eta_i is the posterior-mean linear predictor for GT-vs-GT pair i; sigma_u
is solved so the model's implied aggregate variance across all pairs
matches the observed one, via Gauss-Hermite quadrature (nonlinear in u, so
the mean itself shifts with sigma -- a closed form does not exist) and a
Brent root-find. Never raises: an already-underdispersed calibration set
(or one whose dispersion exceeds anything sigma_u in [0, 5] can produce)
yields sigma_u = 0 and a diagnostic flag instead of a spurious "fit".
"""

from __future__ import annotations

import numpy as np
from numpy.polynomial.hermite import hermgauss
from scipy.optimize import brentq
from scipy.special import expit

_GH_DEGREE = 40
_GH_NODES, _GH_WEIGHTS = hermgauss(_GH_DEGREE)

_SIGMA_MAX = 5.0
_ROOT_TOL = 1e-9


def logitnormal_moments(eta, sigma, *, n_quad: int = _GH_DEGREE):
    """E[p] and E[p^2] for p = expit(eta + u), u ~ N(0, sigma^2).

    p is on the same scale as eta -- the logit(2*beta) scale the regression
    fits on, i.e. what k_i/n_i in the GT-pair data actually measures. No
    factor of two: see the module docstring for why that would be wrong.

    Gauss-Hermite quadrature: E[f(u)] = (1/sqrt(pi)) * sum_j w_j f(sqrt(2)*sigma*x_j).
    sigma <= 0 collapses to the point mass at u = 0 (no quadrature needed).
    """
    eta = np.asarray(eta, dtype=float)
    if sigma <= 0:
        p = expit(eta)
        return p, p ** 2

    nodes, weights = (_GH_NODES, _GH_WEIGHTS) if n_quad == _GH_DEGREE else hermgauss(n_quad)
    u = np.sqrt(2.0) * sigma * nodes                       # (n_quad,)
    z = eta[:, None] + u[None, :]                          # (n_pairs, n_quad)
    p = expit(z)
    w = weights / np.sqrt(np.pi)
    p_bar = p @ w
    e_p2 = (p ** 2) @ w
    return p_bar, e_p2


def _model_var(eta, sigma, n, *, n_quad):
    p_bar, e_p2 = logitnormal_moments(eta, sigma, n_quad=n_quad)
    return float(np.sum(n * p_bar * (1 - p_bar) + n * (n - 1) * (e_p2 - p_bar ** 2)))


def solve_sigma_u(k, n, eta, *, n_quad: int = _GH_DEGREE, sigma_max: float = _SIGMA_MAX):
    """Moment-match sigma_u across a set of GT-vs-GT calibration pairs.

    k, n, eta: equal-length arrays, one entry per pair (observed successes,
    trials, posterior-mean linear predictor on the logit(2*beta) scale).

    Var_obs is fixed at the sigma=0 (point-prediction) residual sum of
    squares; Var_model(sigma) is solved to match it by Brent on
    [0, sigma_max]. Returns (sigma_u, diagnostics); diagnostics always
    carries "overdispersion_ratio" = Var_obs / Var_model(0) and
    "underdispersed" (True when no root exists in range, including the
    case where the data is less dispersed than pure binomial sampling
    predicts). Never raises.
    """
    k = np.asarray(k, dtype=float)
    n = np.asarray(n, dtype=float)
    eta = np.asarray(eta, dtype=float)

    p0, _ = logitnormal_moments(eta, 0.0, n_quad=n_quad)
    var_binom = float(np.sum(n * p0 * (1 - p0)))
    var_obs = float(np.sum((k - n * p0) ** 2))

    def f(sigma):
        return _model_var(eta, sigma, n, n_quad=n_quad) - var_obs

    diagnostics = {
        "var_obs": var_obs,
        "var_binomial": var_binom,
        "overdispersion_ratio": (var_obs / var_binom) if var_binom > 0 else float("nan"),
    }

    f0 = f(0.0)
    if f0 > _ROOT_TOL:
        # Var_obs < Var_model(0): already at or below the binomial-only
        # floor. No sigma_u >= 0 can shrink the model variance further.
        diagnostics["underdispersed"] = True
        return 0.0, diagnostics
    if abs(f0) <= _ROOT_TOL:
        diagnostics["underdispersed"] = False
        return 0.0, diagnostics

    f_max = f(sigma_max)
    if f_max < 0:
        # Var_model is non-decreasing in sigma; even sigma_max isn't enough.
        diagnostics["underdispersed"] = True
        return 0.0, diagnostics

    sigma_u = float(brentq(f, 0.0, sigma_max))
    diagnostics["underdispersed"] = False
    return sigma_u, diagnostics

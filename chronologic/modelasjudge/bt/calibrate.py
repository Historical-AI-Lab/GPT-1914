"""bt/calibrate.py — map Delta_cg to a context-fit probability p_fit.

p_fit = sigma(a + b * Delta_cg), fit by weighted binary cross-entropy so
soft labels (e.g. 0.3 for a 1-of-3 human consensus, 0.9 for full
consensus) enter natively — sklearn's logistic regression cannot take
fractional targets.  A small ridge keeps (a, b) finite when the 0/1
anchor labels are linearly separable in Delta, which they often will be.

p_fit — not tau — is the statistic the context judge reports.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, log_expit


def fit_calibration(records: list[dict], *, l2: float = 1e-2) -> dict:
    """Fit (a, b) from records {qid, item_id, delta_mean, label, source}.

    label in [0, 1]: distractors 0, ground truths 1, human-judged LLM
    answers fractional.  Returns a JSON-serializable dict.
    """
    if len(records) < 2:
        raise ValueError("calibration needs at least two records")
    delta = np.array([r["delta_mean"] for r in records], dtype=float)
    y = np.array([r["label"] for r in records], dtype=float)
    if np.any((y < 0) | (y > 1)):
        raise ValueError("labels must lie in [0, 1]")

    def loss_grad(params):
        a, b = params
        z = a + b * delta
        # BCE with soft labels: -[y*log sig(z) + (1-y)*log sig(-z)]
        loss = -(y * log_expit(z) + (1 - y) * log_expit(-z)).sum()
        loss += l2 * (a * a + b * b)
        resid = expit(z) - y
        grad = np.array([resid.sum() + 2 * l2 * a,
                         (resid * delta).sum() + 2 * l2 * b])
        return loss, grad

    res = minimize(loss_grad, x0=np.array([0.0, 1.0]), jac=True, method="BFGS")
    a, b = res.x
    n_by_source: dict[str, int] = {}
    for r in records:
        n_by_source[r.get("source", "unknown")] = n_by_source.get(r.get("source", "unknown"), 0) + 1
    # Named "intercept"/"slope", not "a"/"b": a results block already carries
    # alpha and beta (judge error rates at t*), and four unrelated quantities
    # sharing two letters misled a reader of the pilot findings.
    return {"intercept": float(a), "slope": float(b), "l2": l2, "n": len(records),
            "n_by_source": n_by_source, "loss": float(res.fun),
            "converged": bool(res.success)}


def calibration_coefficients(calib: dict) -> tuple[float, float]:
    """(intercept, slope), accepting the superseded "a"/"b" key names.

    Calibration artifacts written before 2026-08-06 use "a" and "b".  They
    are still perfectly valid fits, so read them rather than forcing a
    refit; new writes always use the long names.
    """
    if "intercept" in calib and "slope" in calib:
        return float(calib["intercept"]), float(calib["slope"])
    if "a" in calib and "b" in calib:
        return float(calib["a"]), float(calib["b"])
    raise KeyError(
        "calibration dict has neither intercept/slope nor legacy a/b keys"
    )


def apply_calibration(calib: dict, delta_draws: np.ndarray) -> tuple[float, tuple[float, float], np.ndarray]:
    """p_fit as a per-draw quantity, then summarized (Jensen, again).

    Returns (p_fit_mean, central 95% interval, p_fit_draws).
    """
    intercept, slope = calibration_coefficients(calib)
    p_draws = expit(intercept + slope * np.asarray(delta_draws, dtype=float))
    return (float(p_draws.mean()),
            (float(np.quantile(p_draws, 0.025)), float(np.quantile(p_draws, 0.975))),
            p_draws)

"""bt/calibrate.py — map Delta_cg to the partial-credit score p_fit.

p_fit = sigma(a + b * Delta_cg), fit by weighted binary cross-entropy so
soft labels (e.g. 0.3 for a 1-of-3 human consensus, 0.9 for full
consensus) enter natively — sklearn's logistic regression cannot take
fractional targets.  A small ridge keeps (a, b) finite when the 0/1
anchor labels are linearly separable in Delta, which they often will be.

p_fit — not tau — is the statistic the partial-credit path reports.

The anchored scale (`pin_p` and `class_balance`)
------------------------------------------------
Delta is defined as theta_candidate - mean(theta of all ground truths)
(bt/tau.py), so "as good as ground truth" is Delta = 0 *by construction*
and a ground-truth-quality answer scores sigma(a).  Left free, `a` is
largely a sampling artifact: it absorbs log(good:bad odds) of whatever
label mix the calibration set happens to have, which is a benchmark
design choice rather than a fact about answer quality.  Between
ChronoLogic 0.1 and 0.7 the held-out-GT Delta distributions were nearly
identical, yet `a` moved -1.341 -- 78% of that explained purely by the
label mix going from 60:148 to 38:336.  Ground-truth parity scored 0.669
on one version and 0.345 on the other for no reason connected to the
judge.

Two settings remove that:

  pin_p          fixes a := logit(pin_p) and solves for the slope only
                 (a GLM offset), making ground-truth parity a declared
                 constant with no estimation error.  Production pins at
                 0.90; see bt_context_scoring.py's `calibrate`.
  class_balance  gives ground truths and non-ground-truths (distractors
                 plus partial-credit answers) equal *total* weight, so
                 336 distractors cannot outvote 38 ground truths.

Both default to off here so a bare call still fits the plain curve; the
production defaults live at the CLI layer, deliberately, so that flipping
them cannot silently change what other bare callers fit.

Neither setting changes any ranking -- they are monotone re-scalings of
the same Delta, and AUC is identical either way.  What changes is what
the number means.  See estimator_and_calibration_explained.md.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, log_expit, logit


def class_weights(records: list[dict]) -> np.ndarray:
    """Per-record weights equalizing the total weight of the two classes.

    Ground truths are one class; distractors and partial-credit answers
    together are the other (grouped that way deliberately -- a partial is
    a distractor human judges scored as partly satisfactory, and it
    carries its soft label into the loss regardless of its weight).

    Total weight is held at len(records) so the ridge stays on the same
    footing as an unweighted fit.  Falls back to flat weights when either
    class is empty, which happens in bootstrap replicates.
    """
    n = len(records)
    is_gt = np.array([r.get("source") == "ground_truth" for r in records], dtype=bool)
    n_gt = int(is_gt.sum())
    n_non = n - n_gt
    if n_gt == 0 or n_non == 0:
        return np.ones(n, dtype=float)
    return np.where(is_gt, (n / 2.0) / n_gt, (n / 2.0) / n_non).astype(float)


def fit_calibration(records: list[dict], *, l2: float = 1e-2, use_length: bool = False,
                    pin_p: float | None = None, class_balance: bool = False) -> dict:
    """Fit (a, b[, c]) from records {qid, item_id, delta_mean, label, source[, z_len]}.

    label in [0, 1]: distractors 0, ground truths 1, human-judged LLM
    answers fractional.  Returns a JSON-serializable dict.

    use_length=True fits sigma(a + b*delta + c*z_len) instead of the plain
    2-parameter curve (spec §2.1's length-covariate remedy: the BT judge
    prefers the longer answer 61.8% of the time, an additive shift in
    theta no global 2-parameter curve can absorb). Every record must then
    carry a standardized log-length `z_len`.

    pin_p in (0, 1) fixes the intercept at logit(pin_p) and solves for the
    slope (and length slope) only, so p_fit at Delta=0 -- ground-truth
    parity -- is exactly pin_p.  The ridge then applies to the free
    parameters only; penalizing a constant would add a constant to the
    objective and not move the optimum.

    class_balance=True weights records by class_weights() above.

    Both default off: a bare call fits exactly what it always did.
    """
    if len(records) < 2:
        raise ValueError("calibration needs at least two records")
    delta = np.array([r["delta_mean"] for r in records], dtype=float)
    y = np.array([r["label"] for r in records], dtype=float)
    if np.any((y < 0) | (y > 1)):
        raise ValueError("labels must lie in [0, 1]")
    if pin_p is not None and not 0.0 < pin_p < 1.0:
        raise ValueError(f"pin_p must lie strictly in (0, 1); got {pin_p}")

    n_by_source: dict[str, int] = {}
    for r in records:
        n_by_source[r.get("source", "unknown")] = n_by_source.get(r.get("source", "unknown"), 0) + 1

    w = class_weights(records) if class_balance else np.ones(len(records), dtype=float)

    # One optimizer for all four (pinned x balanced) combinations: the free
    # parameters are the columns of X, and a pinned intercept becomes a
    # constant offset on the linear predictor rather than a fitted column.
    pinned = pin_p is not None
    offset = float(logit(pin_p)) if pinned else 0.0
    cols = [] if pinned else [np.ones(len(records), dtype=float)]
    cols.append(delta)
    x0 = [1.0] if pinned else [0.0, 1.0]
    if use_length:
        cols.append(np.array([r["z_len"] for r in records], dtype=float))
        x0.append(0.0)
    X = np.column_stack(cols)

    def loss_grad(params):
        z = offset + X @ params
        # BCE with soft labels: -[y*log sig(z) + (1-y)*log sig(-z)]
        loss = -(w * (y * log_expit(z) + (1 - y) * log_expit(-z))).sum()
        loss += l2 * float(params @ params)
        resid = w * (expit(z) - y)
        return loss, X.T @ resid + 2 * l2 * params

    res = minimize(loss_grad, x0=np.array(x0, dtype=float), jac=True, method="BFGS")
    params = res.x
    a = offset if pinned else float(params[0])
    b = float(params[0] if pinned else params[1])

    # Named "intercept"/"slope", not "a"/"b": a results block already carries
    # alpha and beta (judge error rates at t*), and four unrelated quantities
    # sharing two letters misled a reader of the pilot findings.
    out = {"intercept": float(a), "slope": b, "l2": l2, "n": len(records),
           "n_by_source": n_by_source, "loss": float(res.fun),
           "converged": bool(res.success),
           "pin_p": float(pin_p) if pinned else None,
           "class_balance": bool(class_balance)}
    if use_length:
        out["length_slope"] = float(params[-1])
    return out


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

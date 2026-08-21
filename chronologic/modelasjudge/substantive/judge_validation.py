"""substantive/judge_validation.py — instrument validation, not scoring.

alpha (false-pass rate: the judge passes a distractor it should have
failed) and beta (false-fail rate: the judge splits a tied GT-vs-GT pair)
characterize the *judge*, not a candidate. Direct binary scoring
(direct-binary-scoring-spec.md §1-§4) never applies them to a score --
they are reported here, separately, as validation evidence.

Nothing in `drawbank`, `estimator`, `report`, or `score_substantive` imports
this module: that import boundary is the enforcement mechanism for "judge
error rates characterize the evaluator and are not used to adjust model
scores."

beta is halved on the way out of `pooled_beta` (and in `beta_from_coefs`)
because a GT-vs-GT tie pair gives the judge two independent chances to
mis-rank -- the observed non-tie fraction estimates 2*beta, not beta.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.special import expit
from scipy.stats import beta as beta_dist


def _alpha_prior_a0(prior: str) -> float:
    if prior == "jeffreys":
        return 0.5
    if prior == "uniform":
        return 1.0
    raise ValueError(f"unknown alpha prior {prior!r}")


def alpha_point(k, n, *, prior: str = "jeffreys"):
    """Posterior mean of alpha_q, closed form: (a0+k)/(2*a0+n)."""
    a0 = _alpha_prior_a0(prior)
    k = np.asarray(k, dtype=float)
    n = np.asarray(n, dtype=float)
    return (a0 + k) / (2 * a0 + n)


def alpha_draws(k, n, *, prior: str = "jeffreys", n_draws: int = 2000, rng=None):
    """Beta posterior draws for alpha_q, shape (n_questions, n_draws)."""
    a0 = _alpha_prior_a0(prior)
    rng = rng or np.random.default_rng()
    k = np.asarray(k, dtype=float)
    n = np.asarray(n, dtype=float)
    return rng.beta(a0 + k[:, None], a0 + (n - k)[:, None], size=(len(k), n_draws))


def beta_from_coefs(b0, b_len, u_frame, *, frame_idx, z_loglen, residual=0.0):
    """beta_q = expit(eta_q + residual) / 2, eta_q = b0 + u_frame[frame_idx] + b_len*z_loglen.

    Structurally bounded to (0, 0.5) by construction -- the regression
    targets 2*beta.

    b0, b_len: scalar, or shape (R,) for R replicate/coefficient draws.
    u_frame: shape (K,) for one draw, or (R, K) for R draws.
    frame_idx, z_loglen: shape (n_questions,).
    residual: 0.0, or broadcastable to the output shape.

    Returns (n_questions,) for the scalar/1-D case, (n_questions, R) for
    the batched case.
    """
    frame_idx = np.asarray(frame_idx, dtype=int)
    z_loglen = np.asarray(z_loglen, dtype=float)
    u_frame = np.asarray(u_frame, dtype=float)
    b0 = np.asarray(b0, dtype=float)
    b_len = np.asarray(b_len, dtype=float)

    if u_frame.ndim == 1:
        eta = b0 + u_frame[frame_idx] + b_len * z_loglen
    else:
        u_q = u_frame[:, frame_idx].T                       # (n_questions, R)
        eta = b0[None, :] + u_q + b_len[None, :] * z_loglen[:, None]
    return expit(eta + residual) / 2.0


# ---------------------------------------------------------------------------
# Pooled rates + Jeffreys intervals (the judge_validation_report.py numbers)
# ---------------------------------------------------------------------------

@dataclass
class Rate:
    k: int
    n: int
    rate: float
    lo: float
    hi: float
    n_questions: int


def jeffreys_interval(k, n, ci=(2.5, 97.5)) -> tuple[float, float]:
    """Beta(0.5 + k, 0.5 + n - k) percentiles."""
    a, b = 0.5 + k, 0.5 + (n - k)
    lo, hi = beta_dist.ppf([ci[0] / 100.0, ci[1] / 100.0], a, b)
    return float(lo), float(hi)


def pooled_alpha(reliability_path) -> Rate:
    """k = sum(question_total - question_correct), n = sum(question_total)."""
    data = json.loads(Path(reliability_path).read_text(encoding="utf-8"))
    per_question = data.get("per_question", {})
    k = sum(r["question_total"] - r["question_correct"] for r in per_question.values())
    n = sum(r["question_total"] for r in per_question.values())
    lo, hi = jeffreys_interval(k, n)
    rate = (k / n) if n else float("nan")
    return Rate(k=int(k), n=int(n), rate=rate, lo=lo, hi=hi, n_questions=len(per_question))


def pooled_beta(gt_pairs_path) -> Rate:
    """k = sum(k_nontie), n = sum(n_valid_trials); rate halved on the way out."""
    records = []
    with open(gt_pairs_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    k = sum(r["k_nontie"] for r in records)
    n = sum(r["n_valid_trials"] for r in records)
    lo, hi = jeffreys_interval(k, n)
    rate = (k / n / 2.0) if n else float("nan")
    return Rate(k=int(k), n=int(n), rate=rate, lo=lo / 2.0, hi=hi / 2.0, n_questions=len(records))

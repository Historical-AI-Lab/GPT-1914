"""substantive/estimator.py — the spec's algebra, in numpy.

One quantity throughout: p_q, the probability a candidate's answer to
question q is substantively as good as the ground truth (spec §1). Both
channels feed it through Rogan-Gladen; the bootstrap resamples the three
layers of uncertainty spec §3 names (judgment, instrument, item) and
never clips a per-question value, only the replicate mean (§8.3).

Pure numpy + scipy; every source of randomness is an injected
np.random.Generator, so nothing here is flaky across runs unless the seed
changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.special import expit


# ---------------------------------------------------------------------------
# The core transform (spec §2)
# ---------------------------------------------------------------------------

def rogan_gladen(v, alpha, beta):
    """p_q = (v_q - alpha_q) / (1 - alpha_q - beta_q). Never clips.

    Individual excursions outside [0, 1] are legitimate and cancel in the
    mean (spec §8.3) -- clip the aggregate, never this.
    """
    v = np.asarray(v, dtype=float)
    alpha = np.asarray(alpha, dtype=float)
    beta = np.asarray(beta, dtype=float)
    return (v - alpha) / (1.0 - alpha - beta)


def informativeness(alpha, beta):
    """1 - alpha - beta: how far the judge is from a coin flip on a question."""
    return 1.0 - np.asarray(alpha, dtype=float) - np.asarray(beta, dtype=float)


def floor_mask(alpha, beta, floor: float = 0.2):
    """True where informativeness < floor -- excluded, not clipped (spec §8.2)."""
    return informativeness(alpha, beta) < floor


def display_posteriors(v, beta, pi_hat: float, q_bar: float):
    """Per-question probabilities that average back to pi_hat exactly (spec §2).

    display_q = v_q * pi_hat*(1-beta_q)/q_bar + (1-v_q) * pi_hat*beta_q/(1-q_bar)

    v_q=1 (a pure pass) collapses to the Bayes update P(good | pass); v_q=0
    to P(good | fail); intermediate v_q linearly interpolates, which is
    what makes the mean-back-to-pi_hat identity exact whenever beta is
    shared across the averaged questions (alpha need not be).
    """
    v = np.asarray(v, dtype=float)
    beta = np.asarray(beta, dtype=float)
    return v * (pi_hat * (1 - beta) / q_bar) + (1 - v) * (pi_hat * beta / (1 - q_bar))


# ---------------------------------------------------------------------------
# alpha (closed form, never persisted -- spec §5) and beta (shared instrument
# plus per-question residual -- spec §4)
# ---------------------------------------------------------------------------

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
    targets 2*beta (spec §4).

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
# Plug-in point estimate (spec §6: "computed separately", no resampling)
# ---------------------------------------------------------------------------

@dataclass
class PlugPoint:
    passfail: float
    partial: float
    pooled_count: float
    pooled_equal: float
    p_binary: np.ndarray
    p_partial: np.ndarray
    q_bar: float
    n_passfail: int
    n_partial: int
    n_excluded_floor: int
    excluded_mask: np.ndarray


def _as_auto(auto, n):
    """Normalize an optional override array to shape (n,), all-NaN when absent."""
    if auto is None:
        return np.full(n, np.nan)
    auto = np.asarray(auto, dtype=float)
    if auto.size == 0:
        return np.full(n, np.nan)
    if auto.shape[0] != n:
        raise ValueError(f"auto override has {auto.shape[0]} entries, expected {n}")
    return auto


def plugin_point(*, v_hat, n_v, k_alpha, n_alpha, frame_idx, z_loglen,
                 delta_draws, coef_b0, coef_b_len, coef_u_frame, cal_a, cal_b,
                 alpha_prior: str = "jeffreys", floor: float = 0.2,
                 auto_pf=None, auto_pc=None) -> PlugPoint:
    """Posterior-mean everything, no resampling -- the number to actually quote.

    auto_pf / auto_pc carry automatic verdicts (1.0 or 0.0) for questions whose
    answer was verbatim identical to a ground truth or to a probability-0
    distractor, NaN elsewhere. Those are certainties, not judge readings, so
    they replace the corrected value rather than being corrected: Rogan-Gladen
    on a v_hat of 1.0 returns (1-alpha)/(1-alpha-beta) > 1, which is a real
    number this pipeline used to emit. They are also exempt from the
    informativeness floor, which measures the *judge* -- no judge was consulted.
    """
    v_hat = np.asarray(v_hat, dtype=float)
    frame_idx = np.asarray(frame_idx, dtype=int)
    z_loglen = np.asarray(z_loglen, dtype=float)
    delta_draws = np.asarray(delta_draws, dtype=float)
    auto_pf = _as_auto(auto_pf, v_hat.shape[0])
    auto_pc = _as_auto(auto_pc, delta_draws.shape[0])

    a_pt = alpha_point(k_alpha, n_alpha, prior=alpha_prior)
    b_pt = beta_from_coefs(coef_b0.mean(), coef_b_len.mean(), coef_u_frame.mean(axis=0),
                           frame_idx=frame_idx, z_loglen=z_loglen)
    excluded = floor_mask(a_pt, b_pt, floor) & np.isnan(auto_pf)
    keep = ~excluded

    p_binary_all = rogan_gladen(v_hat, a_pt, b_pt)
    p_binary_all = np.where(np.isnan(auto_pf), p_binary_all, auto_pf)
    p_binary = p_binary_all[keep]
    p_partial = expit(cal_a.mean() + cal_b.mean() * delta_draws.mean(axis=1))
    p_partial = np.where(np.isnan(auto_pc), p_partial, auto_pc)

    n_pf, n_pc = int(p_binary.size), int(p_partial.size)
    passfail = float(np.clip(p_binary.mean(), 0.0, 1.0)) if n_pf else float("nan")
    partial = float(np.clip(p_partial.mean(), 0.0, 1.0)) if n_pc else float("nan")
    pooled_count = (float(np.clip((p_binary.sum() + p_partial.sum()) / (n_pf + n_pc), 0.0, 1.0))
                    if (n_pf + n_pc) else float("nan"))
    pooled_equal = float(np.clip((passfail + partial) / 2.0, 0.0, 1.0))
    q_bar = float(v_hat[keep].mean()) if keep.any() else float("nan")

    return PlugPoint(passfail=passfail, partial=partial, pooled_count=pooled_count,
                     pooled_equal=pooled_equal, p_binary=p_binary, p_partial=p_partial,
                     q_bar=q_bar, n_passfail=n_pf, n_partial=n_pc,
                     n_excluded_floor=int(excluded.sum()), excluded_mask=excluded)


# ---------------------------------------------------------------------------
# The bootstrap (spec §6, one replicate step by step)
# ---------------------------------------------------------------------------

@dataclass
class BootstrapResult:
    passfail: np.ndarray
    partial: np.ndarray
    pooled_count: np.ndarray
    pooled_equal: np.ndarray
    p_binary_qr: np.ndarray            # (n_passfail, n_boot), pre item-resampling
    p_partial_qr: np.ndarray           # (n_partial, n_boot), pre item-resampling
    cal_idx: np.ndarray | None = None
    beta_idx: np.ndarray | None = None


def bootstrap(*, v_hat, n_v, k_alpha, n_alpha, frame_idx, z_loglen, excluded_mask,
             delta_draws, coef_b0, coef_b_len, coef_u_frame, cal_a, cal_b,
             sigma_u: float = 0.0, alpha_prior: str = "jeffreys",
             layers=("judgment", "instrument", "item"),
             n_boot: int = 2000, seed: int = 0, return_indices: bool = False,
             auto_pf=None, auto_pc=None) -> BootstrapResult:
    """One call = n_boot replicates over both channels at once.

    layers is a tuple, not three booleans (plan §1): dropping "instrument"
    pins the coefficient/calibration draw to its posterior mean for every
    replicate instead of drawing a fresh index; dropping "item" replaces
    the with-replacement question resample by the identity (arange), so
    composition is fixed instead of resampled; dropping "judgment" pins
    alpha_q, v_q, the beta residual, and the BT Delta-draw index to their
    point values. All three present is the full estimate.
    """
    rng = np.random.default_rng(seed)
    v_hat = np.asarray(v_hat, dtype=float)
    n_v = np.asarray(n_v, dtype=float)
    k_alpha = np.asarray(k_alpha, dtype=float)
    n_alpha = np.asarray(n_alpha, dtype=float)
    frame_idx = np.asarray(frame_idx, dtype=int)
    z_loglen = np.asarray(z_loglen, dtype=float)
    delta_draws = np.asarray(delta_draws, dtype=float)
    auto_pf = _as_auto(auto_pf, v_hat.shape[0])
    auto_pc = _as_auto(auto_pc, delta_draws.shape[0])
    # excluded_mask comes from plugin_point, which already exempts automatic
    # verdicts from the floor; re-exempt defensively so a caller that passes a
    # bare floor_mask cannot drop a question whose verdict is certain.
    keep = ~np.asarray(excluded_mask, dtype=bool) | ~np.isnan(auto_pf)
    auto_pf_k = auto_pf[keep]

    has_judgment = "judgment" in layers
    has_instrument = "instrument" in layers
    has_item = "item" in layers

    k_k, n_k = k_alpha[keep], n_alpha[keep]
    v_k, nv_k = v_hat[keep], n_v[keep]
    fidx_k, zlen_k = frame_idx[keep], z_loglen[keep]
    n_pf, n_pc = int(k_k.size), int(delta_draws.shape[0])
    R = n_boot
    D, C = coef_b0.shape[0], cal_a.shape[0]

    # ---- layer 2: one shared instrument draw per replicate ----
    if has_instrument:
        beta_idx = rng.integers(0, D, size=R)
        cal_idx = rng.integers(0, C, size=R)
        b0_r, blen_r, uframe_r = coef_b0[beta_idx], coef_b_len[beta_idx], coef_u_frame[beta_idx]
        cal_a_r, cal_b_r = cal_a[cal_idx], cal_b[cal_idx]
    else:
        beta_idx = np.zeros(R, dtype=int)
        cal_idx = np.zeros(R, dtype=int)
        b0_r = np.full(R, coef_b0.mean())
        blen_r = np.full(R, coef_b_len.mean())
        uframe_r = np.tile(coef_u_frame.mean(axis=0), (R, 1))
        cal_a_r = np.full(R, cal_a.mean())
        cal_b_r = np.full(R, cal_b.mean())

    # ---- binary channel: layer 1 (judgment) per question, per replicate ----
    a0 = _alpha_prior_a0(alpha_prior)
    if has_judgment:
        alpha_qr = rng.beta(a0 + k_k[:, None], a0 + (n_k - k_k)[:, None], size=(n_pf, R))
        v_qr = rng.binomial(nv_k[:, None].astype(int), v_k[:, None], size=(n_pf, R)) / nv_k[:, None]
        u_qr = rng.normal(0.0, sigma_u, size=(n_pf, R)) if sigma_u > 0 else np.zeros((n_pf, R))
    else:
        alpha_qr = np.tile(alpha_point(k_k, n_k, prior=alpha_prior)[:, None], (1, R))
        v_qr = np.tile(v_k[:, None], (1, R))
        u_qr = np.zeros((n_pf, R))

    beta_qr = beta_from_coefs(b0_r, blen_r, uframe_r, frame_idx=fidx_k, z_loglen=zlen_k,
                              residual=u_qr)
    p_binary_qr = rogan_gladen(v_qr, alpha_qr, beta_qr)          # (n_pf, R)
    # Applied to the per-question replicate array, not the channel mean:
    # slice_scores and group_scores consume p_binary_qr / p_partial_qr, so
    # overriding only the aggregate would make every breakdown disagree with
    # the headline it decomposes.
    p_binary_qr = np.where(np.isnan(auto_pf_k)[:, None], p_binary_qr,
                           auto_pf_k[:, None])

    # ---- BT channel: layer 1, one Delta index per question, per replicate ----
    n_delta = delta_draws.shape[1]
    if has_judgment:
        delta_idx = rng.integers(0, n_delta, size=(n_pc, R))
    else:
        delta_idx = np.zeros((n_pc, R), dtype=int)
    delta_qr = np.take_along_axis(delta_draws, delta_idx, axis=1)  # (n_pc, R)
    p_partial_qr = expit(cal_a_r[None, :] + cal_b_r[None, :] * delta_qr)
    p_partial_qr = np.where(np.isnan(auto_pc)[:, None], p_partial_qr, auto_pc[:, None])

    # ---- layer 3: item resampling, separately per channel (spec §6 step 3) ----
    if has_item:
        pf_pick = rng.integers(0, n_pf, size=(n_pf, R)) if n_pf else np.zeros((0, R), dtype=int)
        pc_pick = rng.integers(0, n_pc, size=(n_pc, R)) if n_pc else np.zeros((0, R), dtype=int)
    else:
        pf_pick = np.tile(np.arange(n_pf)[:, None], (1, R))
        pc_pick = np.tile(np.arange(n_pc)[:, None], (1, R))

    pf_resampled = np.take_along_axis(p_binary_qr, pf_pick, axis=0) if n_pf else p_binary_qr
    pc_resampled = np.take_along_axis(p_partial_qr, pc_pick, axis=0) if n_pc else p_partial_qr

    passfail_r = pf_resampled.mean(axis=0) if n_pf else np.full(R, np.nan)
    partial_r = pc_resampled.mean(axis=0) if n_pc else np.full(R, np.nan)
    pooled_count_r = ((n_pf * passfail_r + n_pc * partial_r) / (n_pf + n_pc)
                      if (n_pf + n_pc) else np.full(R, np.nan))
    pooled_equal_r = (passfail_r + partial_r) / 2.0

    return BootstrapResult(
        passfail=np.clip(passfail_r, 0.0, 1.0),
        partial=np.clip(partial_r, 0.0, 1.0),
        pooled_count=np.clip(pooled_count_r, 0.0, 1.0),
        pooled_equal=np.clip(pooled_equal_r, 0.0, 1.0),
        p_binary_qr=p_binary_qr,
        p_partial_qr=p_partial_qr,
        cal_idx=cal_idx if return_indices else None,
        beta_idx=beta_idx if return_indices else None,
    )


# ---------------------------------------------------------------------------
# Per-slice scores, from an already-computed per-question-per-replicate bank
# ---------------------------------------------------------------------------

@dataclass
class SliceResult:
    point: float
    lo: float
    hi: float
    n: int


def slice_scores(p_qr, mask, *, item_resample: bool = True, rng=None,
                 ci=(2.5, 97.5)) -> SliceResult:
    """Point + percentile interval for a subset of questions.

    p_qr: (n_questions, n_boot) probabilities with layers 1(+2) already
    applied (a bootstrap() result's p_binary_qr or p_partial_qr).
    Resampling item-membership within the slice (layer 3, scoped to just
    this slice) is optional so callers can compare with and without it --
    e.g. spec §10's sigma_u-inert-at-aggregate-but-live-per-slice check.
    """
    mask = np.asarray(mask, dtype=bool)
    sub = np.asarray(p_qr)[mask]
    n_slice = sub.shape[0]
    point = float(np.clip(sub.mean(), 0.0, 1.0)) if n_slice else float("nan")

    if item_resample and n_slice:
        rng = rng or np.random.default_rng()
        idx = rng.integers(0, n_slice, size=(n_slice, sub.shape[1]))
        sub = np.take_along_axis(sub, idx, axis=0)

    rep_means = np.clip(sub.mean(axis=0), 0.0, 1.0) if n_slice else np.full(p_qr.shape[1], np.nan)
    lo, hi = np.percentile(rep_means, ci) if n_slice else (float("nan"), float("nan"))
    return SliceResult(point=point, lo=float(lo), hi=float(hi), n=n_slice)


# ---------------------------------------------------------------------------
# Group scores (reasoning-type breakdown), combining both channels per group
# ---------------------------------------------------------------------------

@dataclass
class GroupResult:
    point: float
    lo: float
    hi: float
    n: int
    n_pf: int
    n_pc: int


def group_scores(p_binary_pt, p_partial_pt, p_binary_qr, p_partial_qr,
                 mask_pf, mask_pc, *, rng=None, ci=(2.5, 97.5)) -> GroupResult:
    """Count-weighted score for a group spanning both scoring channels.

    p_binary_pt / p_partial_pt: the plugin-point per-question arrays
    (PlugPoint.p_binary / p_partial). p_binary_pt is aligned to the *kept*
    pass/fail questions (excluded_mask already applied); p_partial_pt is
    aligned to bank.qnums_pc. mask_pf / mask_pc select this group's
    questions from those same alignments.

    p_binary_qr / p_partial_qr: the corresponding bootstrap replicate
    arrays (BootstrapResult.p_binary_qr / p_partial_qr) -- same row
    alignment as the _pt arrays, R columns shared across channels within
    one bootstrap() call (same beta_idx/cal_idx per replicate), so column
    r is a coherent joint replicate.

    The point estimate is taken from the plugin arrays rather than the
    mean of the qr arrays: Rogan-Gladen is nonlinear in alpha, so the qr
    mean is Jensen-biased relative to the plugin point, and these numbers
    get quoted directly (report + ledger). This also means a count-weighted
    average of GroupResult.point over a partition of groups reconstructs
    the aggregate pooled_count exactly (modulo aggregate clipping).
    Intervals come from the qr arrays: item-resample within group-and-
    channel separately (layer 3, scoped to the group), then combine per
    replicate the same way pooled_count combines channels.
    """
    mask_pf = np.asarray(mask_pf, dtype=bool)
    mask_pc = np.asarray(mask_pc, dtype=bool)

    pf_pt = np.asarray(p_binary_pt)[mask_pf]
    pc_pt = np.asarray(p_partial_pt)[mask_pc]
    n_pf, n_pc = int(pf_pt.size), int(pc_pt.size)
    n = n_pf + n_pc

    if n == 0:
        return GroupResult(point=float("nan"), lo=float("nan"), hi=float("nan"),
                           n=0, n_pf=0, n_pc=0)

    point = float(np.clip((pf_pt.sum() + pc_pt.sum()) / n, 0.0, 1.0))

    pf_qr = np.asarray(p_binary_qr)[mask_pf] if n_pf else None
    pc_qr = np.asarray(p_partial_qr)[mask_pc] if n_pc else None
    R = pf_qr.shape[1] if pf_qr is not None else pc_qr.shape[1]
    rng = rng or np.random.default_rng()

    if pf_qr is not None:
        idx = rng.integers(0, n_pf, size=(n_pf, R))
        pf_means = np.take_along_axis(pf_qr, idx, axis=0).mean(axis=0)
    else:
        pf_means = np.zeros(R)

    if pc_qr is not None:
        idx = rng.integers(0, n_pc, size=(n_pc, R))
        pc_means = np.take_along_axis(pc_qr, idx, axis=0).mean(axis=0)
    else:
        pc_means = np.zeros(R)

    rep = np.clip((n_pf * pf_means + n_pc * pc_means) / n, 0.0, 1.0)
    lo, hi = np.percentile(rep, ci)
    return GroupResult(point=point, lo=float(lo), hi=float(hi), n=n, n_pf=n_pf, n_pc=n_pc)

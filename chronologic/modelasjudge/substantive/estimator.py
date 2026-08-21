"""substantive/estimator.py — direct binary scoring + BT partial credit, in numpy.

The binary (pass/fail) channel is the arithmetic mean of the observed
per-question judge verdicts v_q -- no Rogan-Gladen correction, no clipping,
no informativeness floor (direct-binary-scoring-spec.md §1-§4). alpha and
beta are judge-validation quantities now; they live in
substantive/judge_validation.py and are never applied to a candidate score.

The BT (partial-credit) channel is unchanged: p_partial = expit(cal_a +
cal_b * Delta), bootstrapped over the judgment (Delta draw), instrument
(calibration draw), and item (question resample) layers.

Pure numpy + scipy; every source of randomness is an injected
np.random.Generator (or a seed that is split into two independent
generators, one per channel -- see `bootstrap`), so nothing here is flaky
across runs unless the seed changes.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.special import expit


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


# ---------------------------------------------------------------------------
# Plug-in point estimate (no resampling)
# ---------------------------------------------------------------------------

@dataclass
class PlugPoint:
    passfail: float
    partial: float
    pooled_count: float
    pooled_equal: float
    p_binary: np.ndarray
    p_partial: np.ndarray
    n_passfail: int
    n_partial: int


def plugin_point(*, v_hat, delta_draws, cal_a, cal_b, auto_pf=None, auto_pc=None) -> PlugPoint:
    """The number to actually quote.

    auto_pf / auto_pc carry automatic verdicts (1.0 or 0.0) for questions whose
    answer was verbatim identical to a ground truth or to a probability-0
    distractor, NaN elsewhere. Those are certainties, not judge readings, so
    they override v_q / p_partial_q outright rather than being blended with
    them -- `judge_scoring_nocontext.py` already writes v_q == the override
    for these questions, so this is a documented no-op on the pass/fail side
    and load-bearing on the partial-credit side, where `delta__{q}` is an
    all-NaN row.
    """
    v_hat = np.asarray(v_hat, dtype=float)
    delta_draws = np.asarray(delta_draws, dtype=float)
    auto_pf = _as_auto(auto_pf, v_hat.shape[0])
    auto_pc = _as_auto(auto_pc, delta_draws.shape[0])

    p_binary = np.where(np.isnan(auto_pf), v_hat, auto_pf)
    p_partial = expit(cal_a.mean() + cal_b.mean() * delta_draws.mean(axis=1))
    p_partial = np.where(np.isnan(auto_pc), p_partial, auto_pc)

    n_pf, n_pc = int(p_binary.size), int(p_partial.size)
    passfail = float(p_binary.mean()) if n_pf else float("nan")
    partial = float(p_partial.mean()) if n_pc else float("nan")
    pooled_count = ((p_binary.sum() + p_partial.sum()) / (n_pf + n_pc)
                    if (n_pf + n_pc) else float("nan"))
    pooled_count = float(pooled_count)
    pooled_equal = float((passfail + partial) / 2.0)

    return PlugPoint(passfail=passfail, partial=partial, pooled_count=pooled_count,
                     pooled_equal=pooled_equal, p_binary=p_binary, p_partial=p_partial,
                     n_passfail=n_pf, n_partial=n_pc)


# ---------------------------------------------------------------------------
# The bootstrap
# ---------------------------------------------------------------------------

@dataclass
class BootstrapResult:
    passfail: np.ndarray
    partial: np.ndarray
    pooled_count: np.ndarray
    pooled_equal: np.ndarray
    p_binary_qr: np.ndarray            # (n_passfail, n_boot)
    p_partial_qr: np.ndarray           # (n_partial, n_boot)
    cal_idx: np.ndarray | None = None
    beta_idx: np.ndarray | None = None  # always None -- no beta bank in this scorer


def bootstrap(*, v_hat, delta_draws, cal_a, cal_b,
             layers=("judgment", "instrument", "item"),
             n_boot: int = 2000, seed: int = 0, return_indices: bool = False,
             auto_pf=None, auto_pc=None) -> BootstrapResult:
    """One call = n_boot replicates over both channels at once.

    The binary channel is conditioned on the observed v_q (there is no
    judge-error model left to resample from) so "judgment" / "instrument" do
    nothing to it; its only source of variation is "item" (which questions
    were sampled). The BT channel keeps its full three-layer structure:
    dropping "instrument" pins the calibration draw to its posterior mean
    for every replicate instead of drawing a fresh index; dropping "item"
    replaces the with-replacement question resample by the identity
    (arange); dropping "judgment" pins the Delta-draw index to a fixed
    value (index 0) for every replicate.

    The two channels draw from independent generators (spawned from one
    seed via np.random.SeedSequence) so that removing the binary channel's
    old alpha/v/u draws does not shift the BT channel's random stream --
    the BT point estimate is deterministic and reproduces exactly; only its
    Monte-Carlo interval moves, and only because the underlying stream
    changed, not because of anything statistical.
    """
    ss_bin, ss_bt = np.random.SeedSequence(seed).spawn(2)
    rng_bin, rng_bt = np.random.default_rng(ss_bin), np.random.default_rng(ss_bt)

    v_hat = np.asarray(v_hat, dtype=float)
    delta_draws = np.asarray(delta_draws, dtype=float)
    auto_pf = _as_auto(auto_pf, v_hat.shape[0])
    auto_pc = _as_auto(auto_pc, delta_draws.shape[0])

    n_pf = v_hat.shape[0]
    n_pc = delta_draws.shape[0]
    R = n_boot
    C = cal_a.shape[0]

    has_judgment = "judgment" in layers
    has_instrument = "instrument" in layers
    has_item = "item" in layers

    # ---- BT channel: instrument layer -> shared calibration draw per replicate ----
    if has_instrument:
        cal_idx = rng_bt.integers(0, C, size=R)
        cal_a_r, cal_b_r = cal_a[cal_idx], cal_b[cal_idx]
    else:
        cal_idx = np.zeros(R, dtype=int)
        cal_a_r = np.full(R, cal_a.mean())
        cal_b_r = np.full(R, cal_b.mean())

    # ---- BT channel: judgment layer -> per-question Delta draw index ----
    if has_judgment and n_pc:
        n_delta = delta_draws.shape[1]
        delta_idx = rng_bt.integers(0, n_delta, size=(n_pc, R))
    else:
        delta_idx = np.zeros((n_pc, R), dtype=int)
    delta_qr = np.take_along_axis(delta_draws, delta_idx, axis=1) if n_pc else np.zeros((n_pc, R))
    p_partial_qr = expit(cal_a_r[None, :] + cal_b_r[None, :] * delta_qr)
    if n_pc:
        p_partial_qr = np.where(np.isnan(auto_pc)[:, None], p_partial_qr, auto_pc[:, None])

    # ---- BT channel: item layer ----
    if has_item and n_pc:
        pc_pick = rng_bt.integers(0, n_pc, size=(n_pc, R))
    else:
        pc_pick = np.tile(np.arange(n_pc)[:, None], (1, R))
    pc_resampled = np.take_along_axis(p_partial_qr, pc_pick, axis=0) if n_pc else p_partial_qr

    # ---- binary channel: constant across replicates, item layer only ----
    p_binary = np.where(np.isnan(auto_pf), v_hat, auto_pf)
    p_binary_qr = np.tile(p_binary[:, None], (1, R)) if n_pf else np.zeros((0, R))
    if has_item and n_pf:
        pf_pick = rng_bin.integers(0, n_pf, size=(n_pf, R))
    else:
        pf_pick = np.tile(np.arange(n_pf)[:, None], (1, R))
    pf_resampled = np.take_along_axis(p_binary_qr, pf_pick, axis=0) if n_pf else p_binary_qr

    passfail_r = pf_resampled.mean(axis=0) if n_pf else np.full(R, np.nan)
    partial_r = pc_resampled.mean(axis=0) if n_pc else np.full(R, np.nan)
    pooled_count_r = ((n_pf * passfail_r + n_pc * partial_r) / (n_pf + n_pc)
                      if (n_pf + n_pc) else np.full(R, np.nan))
    pooled_equal_r = (passfail_r + partial_r) / 2.0

    return BootstrapResult(
        passfail=passfail_r, partial=partial_r,
        pooled_count=pooled_count_r, pooled_equal=pooled_equal_r,
        p_binary_qr=p_binary_qr, p_partial_qr=p_partial_qr,
        cal_idx=cal_idx if return_indices else None,
        beta_idx=None,
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

    p_qr: (n_questions, n_boot) probabilities with the other layers already
    applied (a bootstrap() result's p_binary_qr or p_partial_qr).
    Resampling item-membership within the slice (scoped to just this slice)
    is optional so callers can compare with and without it.
    """
    mask = np.asarray(mask, dtype=bool)
    sub = np.asarray(p_qr)[mask]
    n_slice = sub.shape[0]
    point = float(sub.mean()) if n_slice else float("nan")

    if item_resample and n_slice:
        rng = rng or np.random.default_rng()
        idx = rng.integers(0, n_slice, size=(n_slice, sub.shape[1]))
        sub = np.take_along_axis(sub, idx, axis=0)

    rep_means = sub.mean(axis=0) if n_slice else np.full(p_qr.shape[1], np.nan)
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
    (PlugPoint.p_binary / p_partial), aligned to bank.qnums_pf / qnums_pc.
    mask_pf / mask_pc select this group's questions from those alignments.

    p_binary_qr / p_partial_qr: the corresponding bootstrap replicate
    arrays (BootstrapResult.p_binary_qr / p_partial_qr) -- same row
    alignment as the _pt arrays, R columns shared across channels within
    one bootstrap() call.

    The point estimate is taken from the plugin arrays rather than the mean
    of the qr arrays. On the binary side the two agree exactly (the
    per-question value never changes across replicates); on the BT side
    p_partial_qr's per-replicate mean is Jensen-biased relative to the
    plugin point because expit is nonlinear, so the plugin point remains
    the number that gets quoted. A count-weighted average of
    GroupResult.point over a partition of groups reconstructs the aggregate
    pooled_count exactly.
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

    point = float((pf_pt.sum() + pc_pt.sum()) / n)

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

    rep = (n_pf * pf_means + n_pc * pc_means) / n
    lo, hi = np.percentile(rep, ci)
    return GroupResult(point=point, lo=float(lo), hi=float(hi), n=n, n_pf=n_pf, n_pc=n_pc)

"""bt/tau.py — cut-inference candidate scoring.

The candidate's strength theta_c is estimated conditional on stored
anchor draws: for each anchor draw the 1-D conditional posterior
p(theta_c | theta_anchor, data) is evaluated on a fixed grid and sampled
by inverse CDF.  Candidate data never updates the anchors, so scores
stay comparable across candidates (anchors are infrastructure).

tau is computed per draw and then summarized — E[sigma(delta)], never
sigma(E[delta]) (Jensen).  The resulting tau posterior is deliberately
NOT the posterior of the joint model; its validation is frequentist
coverage (bt.simulate.run_tau_coverage), not SBC.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.special import expit, log_expit

from .fit import AnchorFit


@dataclass
class CandidateScore:
    tau_draws: np.ndarray
    delta_draws: np.ndarray
    tau_mean: float
    tau_ci: tuple[float, float]          # central 95%
    delta_mean: float
    delta_ci: tuple[float, float]
    reference_gt: str
    n_comparisons: int


def aggregate_candidate_counts(counts: dict, candidate_id: str) -> dict[str, tuple[int, int]]:
    """Ordered-pair counts -> per-opponent (candidate_wins, n_total).

    Both presentation orders collapse into one binomial per opponent for
    the likelihood (P(c beats j) is order-free under the model); the
    AB/BA balance was enforced upstream at collection time.
    """
    agg: dict[str, tuple[int, int]] = {}
    for (first, second), (w, n) in counts.items():
        if first == candidate_id:
            opp, wins_c = second, w
        elif second == candidate_id:
            opp, wins_c = first, n - w
        else:
            continue
        cw, cn = agg.get(opp, (0, 0))
        agg[opp] = (cw + wins_c, cn + n)
    return agg


def score_candidate(anchor: AnchorFit, counts: dict, candidate_id: str,
                    reference_gt, *, prior_scale: float, seed: int,
                    grid_half_width: float = 8.0, grid_points: int = 801,
                    chunk: int = 512, prior_dist: str = "normal",
                    prior_df: float = 3.0) -> CandidateScore:
    """Score one candidate against stored anchor draws.

    counts: ordered-pair counts involving candidate_id (from bt.collect).
    """
    opp_counts = aggregate_candidate_counts(counts, candidate_id)
    if not opp_counts:
        raise ValueError(f"no comparisons involving candidate {candidate_id!r}")
    for opp in opp_counts:
        if opp not in anchor.item_ids:
            raise KeyError(f"opponent {opp!r} not among anchor items")
    # reference_gt may be a single id or a list; Delta is taken against the
    # MEAN theta of the references, per draw. mean_i(theta_c - theta_i) is
    # identical to theta_c - mean_i(theta_i), so this is one subtraction.
    ref_ids = [reference_gt] if isinstance(reference_gt, str) else list(reference_gt)
    if not ref_ids:
        raise ValueError("no reference ground truth supplied")
    for r in ref_ids:
        if r not in anchor.item_ids:
            raise KeyError(f"reference GT {r!r} not among anchor items")

    opp_ids = sorted(opp_counts)
    k = np.array([opp_counts[o][0] for o in opp_ids], dtype=float)   # candidate wins
    m = np.array([opp_counts[o][1] for o in opp_ids], dtype=float)
    opp_cols = [anchor.index_of(o) for o in opp_ids]
    ref_cols = [anchor.index_of(r) for r in ref_ids]

    grid = np.linspace(-grid_half_width, grid_half_width, grid_points)
    cell = grid[1] - grid[0]
    # The candidate's prior must match the one the anchors were fitted under,
    # or Delta mixes two scales.
    if prior_dist == "studentt":
        log_prior = -0.5 * (prior_df + 1) * np.log1p((grid / prior_scale) ** 2 / prior_df)
    elif prior_dist == "normal":
        log_prior = -0.5 * (grid / prior_scale) ** 2
    else:
        raise ValueError(f"unknown prior_dist {prior_dist!r}")

    rng = np.random.default_rng(seed)
    n_draws = anchor.theta_draws.shape[0]
    theta_c = np.empty(n_draws)

    for start in range(0, n_draws, chunk):
        theta_opp = anchor.theta_draws[start:start + chunk][:, opp_cols]  # (S, J)
        # diff[s, g, j] = grid[g] - theta_opp[s, j]
        diff = grid[None, :, None] - theta_opp[:, None, :]
        loglik = (k[None, None, :] * log_expit(diff)
                  + (m - k)[None, None, :] * log_expit(-diff)).sum(axis=2)  # (S, G)
        logpost = loglik + log_prior[None, :]
        logpost -= logpost.max(axis=1, keepdims=True)
        weights = np.exp(logpost)
        cdf = np.cumsum(weights, axis=1)
        cdf /= cdf[:, -1:]
        u = rng.random(theta_opp.shape[0])
        idx = np.argmax(cdf >= u[:, None], axis=1)
        rows = np.arange(theta_opp.shape[0])
        # linear interpolation within the selected grid cell
        cdf_prev = np.where(idx > 0, cdf[rows, np.maximum(idx - 1, 0)], 0.0)
        cell_mass = cdf[rows, idx] - cdf_prev
        frac = np.where(cell_mass > 0, (u - cdf_prev) / np.maximum(cell_mass, 1e-300), 0.5)
        theta_c[start:start + theta_opp.shape[0]] = grid[idx] + (frac - 0.5) * cell

    delta_draws = theta_c - anchor.theta_draws[:, ref_cols].mean(axis=1)
    tau_draws = expit(delta_draws)
    return CandidateScore(
        tau_draws=tau_draws,
        delta_draws=delta_draws,
        tau_mean=float(tau_draws.mean()),
        tau_ci=(float(np.quantile(tau_draws, 0.025)), float(np.quantile(tau_draws, 0.975))),
        delta_mean=float(delta_draws.mean()),
        delta_ci=(float(np.quantile(delta_draws, 0.025)), float(np.quantile(delta_draws, 0.975))),
        reference_gt=",".join(ref_ids),
        n_comparisons=int(m.sum()),
    )

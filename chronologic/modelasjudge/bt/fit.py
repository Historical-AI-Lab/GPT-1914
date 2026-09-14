"""bt/fit.py — Bayesian Bradley-Terry anchor fit in PyMC.

theta ~ ZeroSumNormal(prior_scale): the zero-centered weakly-informative
prior handles separation (an item that wins every contest), and the
sum-to-zero constraint pins the additive-constant non-identifiability
explicitly.  Ordered-pair judgments enter as binomial counts.

Also holds the two question-level QC diagnostics — posterior-predictive
pair checks and three-cycle counts — whose alarm sensitivity is measured
in bt.simulate.run_misspec_sweep.
"""

from __future__ import annotations

import itertools
import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .design import assert_connected


@dataclass
class FitConfig:
    draws: int = 500
    tune: int = 1000
    chains: int = 4
    cores: int = 1
    target_accept: float = 0.9


# Fast settings for simulation/tests, where hundreds of tiny fits run.
FAST_FIT = FitConfig(draws=250, tune=400, chains=2)


@dataclass
class AnchorFit:
    item_ids: list[str]
    theta_draws: np.ndarray          # (n_draws_total, n_items), sum-to-zero per draw
    prior_scale: float
    diagnostics: dict = field(default_factory=dict)

    def index_of(self, item_id: str) -> int:
        return self.item_ids.index(item_id)


def counts_to_arrays(item_ids: list[str], counts: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Ordered-pair counts -> (i_idx, j_idx, wins, n) index arrays.

    The i-th row says: item i_idx[r] beat item j_idx[r] wins[r] times out
    of n[r] presentations with i first.  Index<->id mapping follows
    item_ids order; tests assert the round-trip.
    """
    index = {item_id: k for k, item_id in enumerate(item_ids)}
    i_idx, j_idx, wins, n = [], [], [], []
    for (a, b), (w, m) in sorted(counts.items()):
        if m == 0:
            continue
        if a not in index or b not in index:
            raise KeyError(f"counts reference unknown item: {(a, b)}")
        i_idx.append(index[a])
        j_idx.append(index[b])
        wins.append(w)
        n.append(m)
    return (np.array(i_idx, dtype=int), np.array(j_idx, dtype=int),
            np.array(wins, dtype=int), np.array(n, dtype=int))


def fit_anchor_model(item_ids: list[str], counts: dict, *,
                     prior_scale: float = 1.0, seed: int = 0,
                     fit_config: FitConfig | None = None,
                     prior_dist: str = "normal", prior_df: float = 3.0) -> AnchorFit:
    """Fit the per-question BT model and return flattened posterior draws.

    prior_dist="studentt" replaces the ZeroSumNormal with a zero-sum
    Student-t of `prior_df` degrees of freedom, implemented as a scale
    mixture of normals (t = Normal(0, s) with s^2 ~ InvGamma(nu/2, nu/2)),
    which keeps the sum-to-zero constraint PyMC provides.

    Why it matters: under the near-complete separation this judge produces,
    a unimodal prior cannot represent two tight clusters far apart, so the
    fitted gap is partly a property of the prior's tail. A change of prior
    *scale* is affine in theta and is cancelled exactly by refitting the
    calibration; a change of *shape* need not be. See the pilot findings.
    """
    import pymc as pm  # deferred: heavy import

    assert_connected(item_ids, counts)
    cfg = fit_config or FitConfig()
    i_idx, j_idx, wins, n = counts_to_arrays(item_ids, counts)
    if len(n) == 0:
        raise ValueError("no observed comparisons to fit")

    if prior_dist not in ("normal", "studentt"):
        raise ValueError(f"unknown prior_dist {prior_dist!r}")

    with pm.Model():
        if prior_dist == "studentt":
            tau = pm.InverseGamma("tau", alpha=prior_df / 2, beta=prior_df / 2)
            sigma = prior_scale * pm.math.sqrt(tau)
        else:
            sigma = prior_scale
        theta = pm.ZeroSumNormal("theta", sigma=sigma, shape=len(item_ids))
        logit_p = theta[i_idx] - theta[j_idx]
        pm.Binomial("wins", n=n, p=pm.math.sigmoid(logit_p), observed=wins)
        idata = pm.sample(
            draws=cfg.draws, tune=cfg.tune, chains=cfg.chains, cores=cfg.cores,
            target_accept=cfg.target_accept, random_seed=int(seed) % (2**32),
            progressbar=False, compute_convergence_checks=False,
        )

    posterior = idata.posterior["theta"]  # (chain, draw, item)
    theta_draws = posterior.values.reshape(-1, len(item_ids))

    diagnostics = {}
    try:
        import arviz as az
        summ = az.summary(idata, var_names=["theta"])
        diagnostics = {
            "r_hat_max": float(summ["r_hat"].max()),
            "ess_bulk_min": float(summ["ess_bulk"].min()),
            "divergences": int(idata.sample_stats["diverging"].values.sum()),
        }
    except Exception as exc:  # diagnostics are advisory, never fatal
        diagnostics = {"error": str(exc)}

    return AnchorFit(item_ids=list(item_ids), theta_draws=theta_draws,
                     prior_scale=prior_scale, diagnostics=diagnostics)


def save_anchor_fits(path: Path, fits: dict[str, AnchorFit], meta: dict) -> None:
    """Save multiple per-question AnchorFits into one npz archive.

    Arrays are namespaced `theta__{qid}` / `items__{qid}`; a JSON `meta`
    string (one dict) plus per-question `prior_scale__{qid}` and
    `diagnostics__{qid}` (JSON strings) round out the archive.
    """
    arrays = {"meta": np.array(json.dumps(meta))}
    for qid, fit in fits.items():
        arrays[f"theta__{qid}"] = fit.theta_draws
        arrays[f"items__{qid}"] = np.array(fit.item_ids)
        arrays[f"prior_scale__{qid}"] = np.array(fit.prior_scale)
        arrays[f"diagnostics__{qid}"] = np.array(json.dumps(fit.diagnostics))
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.npz")
    np.savez(tmp, **arrays)
    tmp.replace(path)


def load_anchor_fits(path: Path) -> tuple[dict[str, AnchorFit], dict]:
    data = np.load(path, allow_pickle=False)
    meta = json.loads(str(data["meta"]))
    qids = sorted({key.split("__", 1)[1] for key in data.files if key.startswith("theta__")})
    fits = {}
    for qid in qids:
        fits[qid] = AnchorFit(
            item_ids=[str(x) for x in data[f"items__{qid}"]],
            theta_draws=data[f"theta__{qid}"],
            prior_scale=float(data[f"prior_scale__{qid}"]),
            diagnostics=json.loads(str(data[f"diagnostics__{qid}"])),
        )
    return fits, meta


def _unordered_counts(counts: dict) -> dict:
    """Aggregate ordered-pair counts to unordered: (a,b) a<b -> (wins_a, n)."""
    agg: dict = {}
    for (first, second), (w, n) in counts.items():
        a, b = sorted((first, second))
        wa, m = agg.get((a, b), (0, 0))
        wa += w if first == a else (n - w)
        agg[(a, b)] = (wa, m + n)
    return agg


def ppc_pair_check(fit: AnchorFit, counts: dict, *, seed: int = 0,
                   alarm_p: float = 0.05, max_draws: int = 1000) -> dict:
    """Posterior-predictive two-sided tail probability per unordered pair.

    Flags pairs whose observed win count is in the tails of the model's
    predictive distribution — evidence of BT violation for that pair.
    """
    from scipy.special import expit

    rng = np.random.default_rng(seed)
    idx = {item_id: k for k, item_id in enumerate(fit.item_ids)}
    draws = fit.theta_draws
    if draws.shape[0] > max_draws:
        sel = rng.choice(draws.shape[0], size=max_draws, replace=False)
        draws = draws[sel]

    pvals, alarms = {}, []
    for (a, b), (wa, m) in _unordered_counts(counts).items():
        if m == 0:
            continue
        p = expit(draws[:, idx[a]] - draws[:, idx[b]])
        k_sim = rng.binomial(m, p)
        p_low = float(np.mean(k_sim <= wa))
        p_high = float(np.mean(k_sim >= wa))
        pval = min(1.0, 2.0 * min(p_low, p_high))
        pvals[f"{a}|{b}"] = pval
        if pval < alarm_p:
            alarms.append(f"{a}|{b}")
    return {"pvals": pvals, "alarms": alarms, "alarm": bool(alarms)}


def three_cycle_count(counts: dict) -> int:
    """Count directed 3-cycles in the majority-preference digraph."""
    beats = set()
    for (a, b), (wa, m) in _unordered_counts(counts).items():
        if wa * 2 > m:
            beats.add((a, b))
        elif wa * 2 < m:
            beats.add((b, a))
    nodes = sorted({x for pair in beats for x in pair})
    cycles = 0
    for x, y, z in itertools.combinations(nodes, 3):
        for a, b, c in ((x, y, z), (x, z, y)):
            if (a, b) in beats and (b, c) in beats and (c, a) in beats:
                cycles += 1
    return cycles


def three_cycle_check(fit: AnchorFit, counts: dict, *, seed: int = 0,
                      n_sims: int = 200, alarm_quantile: float = 0.95) -> dict:
    """Compare observed 3-cycle count to its posterior-predictive distribution."""
    from scipy.special import expit

    rng = np.random.default_rng(seed)
    idx = {item_id: k for k, item_id in enumerate(fit.item_ids)}
    observed = three_cycle_count(counts)
    unordered = _unordered_counts(counts)
    sims = []
    draw_sel = rng.choice(fit.theta_draws.shape[0], size=n_sims, replace=True)
    for s in draw_sel:
        theta = fit.theta_draws[s]
        sim_counts = {}
        for (a, b), (_wa, m) in unordered.items():
            p = expit(theta[idx[a]] - theta[idx[b]])
            sim_counts[(a, b)] = (int(rng.binomial(m, p)), m)
        sims.append(three_cycle_count(sim_counts))
    threshold = float(np.quantile(sims, alarm_quantile))
    return {"observed": observed, "predictive_quantile_threshold": threshold,
            "predictive_mean": float(np.mean(sims)),
            "alarm": observed > threshold}

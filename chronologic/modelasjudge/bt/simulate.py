"""bt/simulate.py — recovery-test machinery. PRODUCTION code.

Fully synthetic, no network, deterministic under a master seed. Exercises
the real design-table generator, likelihood, fit, LOO, and tau code with
only the judge call replaced by a stub drawing from a known model — a
convenience reimplementation of the design table would defeat the point,
since indexing errors in the pair table are exactly what this catches.

Both tests/test_bt_recovery.py (small R, loose CI gate) and the
`simulate` CLI subcommand (large R, reported artifacts) call into this
module; nothing here is test-only.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.special import expit

from .collect import run_comparisons
from .design import (
    Item,
    build_anchor_design,
    build_candidate_design,
    derive_seed,
    select_reference_gt,
)
from .fit import FAST_FIT, fit_anchor_model, ppc_pair_check, three_cycle_check
from .prompts import build_bt_prompt, build_exemplar_block
from .tau import score_candidate
from .validate import roc_from_loo, LooRecord


def make_stub_judge(theta_by_id: dict[str, float], *, gamma: float = 0.0,
                    omega: float = 0.0, master_seed: int = 0):
    """A deterministic judge_call(comparison, system, user) -> "A"|"B" stub.

    w ~ Bernoulli(sigma(theta_first - theta_second + gamma)); when omega>0
    an antisymmetric pair-specific term eps_ij = -eps_ji ~ N(0, omega) is
    added, which generates genuine BT-model violation for misspecification
    sweeps. Deterministic per (qid, phase, first, second, repeat) via the
    same derive_seed used by production code, so reruns are bitwise
    identical.
    """
    eps_cache: dict[tuple[str, str], float] = {}

    def eps(qid: str, a: str, b: str) -> float:
        if omega == 0.0:
            return 0.0
        key = tuple(sorted((a, b)))
        if key not in eps_cache:
            rng = np.random.default_rng(derive_seed(master_seed, qid, "eps", *key))
            eps_cache[key] = float(rng.normal(0, omega))
        sign = 1.0 if (a, b) == tuple(sorted((a, b))) else -1.0
        return sign * eps_cache[key]

    def judge_call(comp, system, user):
        rng = np.random.default_rng(comp.seed)
        logit = theta_by_id[comp.first] - theta_by_id[comp.second] + gamma
        logit += eps(comp.qid, comp.first, comp.second)
        p_first = expit(logit)
        choice = "A" if rng.random() < p_first else "B"
        return f'{{"context fit": "{choice}"}}'

    return judge_call


def _items_from_theta(theta_by_id: dict[str, float], gt_ids: list[str]) -> list[Item]:
    items = []
    gt_i, d_i = 0, 0
    for item_id in theta_by_id:
        if item_id in gt_ids:
            items.append(Item(item_id, f"text {item_id}", "ground_truth", ""))
            gt_i += 1
        else:
            items.append(Item(item_id, f"text {item_id}", "distractor", "synthetic reason"))
            d_i += 1
    return items


def _prompt_builder(items_by_id):
    def build(comp):
        # explicit: synthetic items carry no reject_reason, so the rubric mode is
        # immaterial to the stub judge -- pin it so a policy change to the
        # default never silently alters a recovery run.
        block = build_exemplar_block(list(items_by_id.values()),
                                     {comp.first, comp.second}, set(), "exemplars")
        return build_bt_prompt("synthetic context", "synthetic question", block,
                               items_by_id[comp.first].text, items_by_id[comp.second].text)
    return build


def simulate_question(theta_by_id: dict[str, float], gt_ids: list[str], qid: str,
                      master_seed: int, *, gamma: float = 0.0, omega: float = 0.0,
                      repeats: int = 1, prior_scale: float = 1.0,
                      fit_config=None):
    """Simulate anchor comparisons for one question and fit the model.

    Returns (fit, counts, items_by_id, collect_result).
    """
    items = _items_from_theta(theta_by_id, gt_ids)
    items_by_id = {it.item_id: it for it in items}
    comps = build_anchor_design(qid, items, repeats, master_seed)
    judge = make_stub_judge(theta_by_id, gamma=gamma, omega=omega, master_seed=master_seed)
    result = run_comparisons(comps, items_by_id, _prompt_builder(items_by_id), judge,
                             cache=None, max_retries=0)
    fit = fit_anchor_model([it.item_id for it in items], result.counts,
                           prior_scale=prior_scale,
                           seed=derive_seed(master_seed, qid, "fit"),
                           fit_config=fit_config or FAST_FIT)
    return fit, result.counts, items_by_id, result


@dataclass
class SbcReport:
    n_replicates: int
    rank_uniformity_pvalue: float
    coverage: dict          # {"50%": frac, "90%": frac}
    ranks: list


def run_sbc(n_items: int, replicates: int, master_seed: int, *,
           n_thin: int = 50, repeats: int = 1, prior_scale: float = 1.0,
           n_gt: int = 2, fit_config=None) -> SbcReport:
    """Simulation-based calibration of the anchor fit.

    theta_true is drawn from the SAME centered parameterization as the
    fitted ZeroSumNormal (iid Normal, then subtract the mean) -- drawing
    from an unconstrained Normal and fitting a centered model produces
    non-uniform ranks with entirely correct code, which is the spec's
    explicit trap.
    """
    from scipy.stats import chisquare

    gt_ids = [f"gt{i}" for i in range(n_gt)]
    d_ids = [f"d{i}" for i in range(n_items - n_gt)]
    all_ids = gt_ids + d_ids
    ranks_per_item = {i: [] for i in range(n_items)}

    for r in range(replicates):
        rng = np.random.default_rng(derive_seed(master_seed, "sbc", str(r)))
        theta_true = rng.normal(0, prior_scale, size=n_items)
        theta_true -= theta_true.mean()
        theta_by_id = dict(zip(all_ids, theta_true))

        fit, counts, _, _ = simulate_question(
            theta_by_id, gt_ids, f"sbc{r}", derive_seed(master_seed, "sbc", str(r), "fit"),
            repeats=repeats, prior_scale=prior_scale, fit_config=fit_config,
        )
        draws = fit.theta_draws
        thin_idx = np.linspace(0, draws.shape[0] - 1, min(n_thin, draws.shape[0])).astype(int)
        thinned = draws[thin_idx]
        for i, item_id in enumerate(all_ids):
            col = fit.index_of(item_id)
            rank = int(np.sum(thinned[:, col] < theta_by_id[item_id]))
            ranks_per_item[i].append(rank)

    all_ranks = [rank for ranks in ranks_per_item.values() for rank in ranks]
    n_bins = min(20, n_thin + 1)
    hist, _ = np.histogram(all_ranks, bins=n_bins, range=(0, n_thin + 1))
    chi2, pval = chisquare(hist)

    coverage = {}
    for level, lo_q, hi_q in [("50%", 0.25, 0.75), ("90%", 0.05, 0.95)]:
        covered = 0
        total = 0
        for i in range(n_items):
            for rank in ranks_per_item[i]:
                total += 1
                frac = rank / n_thin
                if lo_q <= frac <= hi_q:
                    covered += 1
        coverage[level] = covered / total if total else float("nan")

    return SbcReport(n_replicates=replicates, rank_uniformity_pvalue=float(pval),
                     coverage=coverage, ranks=all_ranks)


@dataclass
class CoverageReport:
    n_replicates: int
    bias: float
    se_delta: float
    coverage_90: float
    stratified: dict


def run_tau_coverage(theta_config: dict[str, float], gt_ids: list[str], reference_gt: str,
                     replicates: int, master_seed: int, *, repeats: int = 1,
                     prior_scale: float = 1.0, cand_theta_values: list[float] | None = None,
                     fit_config=None) -> CoverageReport:
    """Frequentist coverage of tau/Delta intervals under repeated sampling
    with theta held fixed.

    SBC does not apply here: theta_c is estimated conditional on anchor
    draws (cut inference), so its posterior is deliberately not the joint
    posterior. Approximate (not exact) nominal coverage is the pass
    condition, stratified by true Delta.
    """
    if cand_theta_values is None:
        cand_theta_values = [theta_config[reference_gt] + d for d in (-3, -1.5, 0, 1.5, 3)]

    errors, covered_90, stratified = [], [], {}
    for true_theta_c in cand_theta_values:
        errs_here, cov_here = [], []
        for r in range(replicates):
            seed_r = derive_seed(master_seed, "cov", str(true_theta_c), str(r))
            fit, anchor_counts, items_by_id, _ = simulate_question(
                theta_config, gt_ids, "cov", seed_r, repeats=repeats,
                prior_scale=prior_scale, fit_config=fit_config,
            )
            cand = Item("cand", "candidate", "candidate")
            comps, _withdrawn = build_candidate_design(
                "cov", list(items_by_id.values()), cand, reference_gt, repeats, seed_r,
            )
            theta_full = dict(theta_config)
            theta_full["cand"] = true_theta_c
            judge = make_stub_judge(theta_full, master_seed=seed_r)
            items_with_cand = dict(items_by_id)
            items_with_cand["cand"] = cand
            result = run_comparisons(comps, items_with_cand, _prompt_builder(items_with_cand),
                                     judge, cache=None, max_retries=0)
            if not result.counts:
                continue
            score = score_candidate(fit, result.counts, "cand", reference_gt,
                                    prior_scale=prior_scale, seed=seed_r + 1)
            true_delta = true_theta_c - theta_config[reference_gt]
            errs_here.append(score.delta_mean - true_delta)
            cov_here.append(score.delta_ci[0] <= true_delta <= score.delta_ci[1])
        if errs_here:
            errors.extend(errs_here)
            covered_90.extend(cov_here)
            stratified[round(true_theta_c - theta_config[reference_gt], 3)] = {
                "bias": float(np.mean(errs_here)),
                "se": float(np.std(errs_here)),
                "coverage_90": float(np.mean(cov_here)),
                "n": len(errs_here),
            }

    return CoverageReport(
        n_replicates=replicates,
        bias=float(np.mean(errors)) if errors else float("nan"),
        se_delta=float(np.std(errors)) if errors else float("nan"),
        coverage_90=float(np.mean(covered_90)) if covered_90 else float("nan"),
        stratified=stratified,
    )


def structured_theta_config(n_distractors: int = 4, kappa: float = 1.0) -> dict[str, float]:
    """Reference GT well above the field, second GT close, distractors spread."""
    base = {"gt0": 2.0, "gt1": 1.6}
    spread = np.linspace(-0.5, -3.5, n_distractors)
    for i, v in enumerate(spread):
        base[f"d{i}"] = float(v)
    centered = {k: v - np.mean(list(base.values())) for k, v in base.items()}
    return {k: v * kappa for k, v in centered.items()}


def run_kappa_sweep(kappas: tuple[float, ...], replicates: int, master_seed: int, *,
                    n_distractors: int = 4, repeats: int = 1, fit_config=None) -> dict:
    """Sweep the scale of a structured theta configuration; report bias,
    SE(Delta_hat), and coverage stratified by true Delta at each kappa."""
    out = {}
    gt_ids = ["gt0", "gt1"]
    for kappa in kappas:
        theta_config = structured_theta_config(n_distractors, kappa)
        report = run_tau_coverage(theta_config, gt_ids, "gt0", replicates,
                                  derive_seed(master_seed, "kappa", str(kappa)),
                                  repeats=repeats, fit_config=fit_config)
        out[kappa] = {"bias": report.bias, "se_delta": report.se_delta,
                     "coverage_90": report.coverage_90, "stratified": report.stratified}
    return out


def run_misspec_sweep(gammas: tuple[float, ...], omegas: tuple[float, ...],
                      replicates: int, master_seed: int, *, n_items: int = 6,
                      n_gt: int = 2, repeats: int = 1, prior_scale: float = 1.0,
                      fit_config=None) -> dict:
    """Sweep position-effect (gamma) and BT-violation (omega) misspecification;
    report PPC / three-cycle alarm rates, including the gamma=omega=0 false-alarm rate."""
    gt_ids = [f"gt{i}" for i in range(n_gt)]
    d_ids = [f"d{i}" for i in range(n_items - n_gt)]
    all_ids = gt_ids + d_ids
    out = {}
    for gamma in gammas:
        for omega in omegas:
            ppc_alarms, cycle_alarms = 0, 0
            n_ok = 0
            for r in range(replicates):
                seed_r = derive_seed(master_seed, "misspec", str(gamma), str(omega), str(r))
                theta_true = np.random.default_rng(seed_r).normal(0, prior_scale, n_items)
                theta_true -= theta_true.mean()
                theta_by_id = dict(zip(all_ids, theta_true))
                try:
                    fit, counts, _, _ = simulate_question(
                        theta_by_id, gt_ids, f"m{r}", seed_r, gamma=gamma, omega=omega,
                        repeats=repeats, prior_scale=prior_scale, fit_config=fit_config,
                    )
                except Exception:
                    continue
                n_ok += 1
                ppc = ppc_pair_check(fit, counts, seed=seed_r)
                cyc = three_cycle_check(fit, counts, seed=seed_r)
                ppc_alarms += int(ppc["alarm"])
                cycle_alarms += int(cyc["alarm"])
            out[(gamma, omega)] = {
                "ppc_alarm_rate": ppc_alarms / n_ok if n_ok else float("nan"),
                "three_cycle_alarm_rate": cycle_alarms / n_ok if n_ok else float("nan"),
                "n": n_ok,
            }
    return out


def run_full_chain(theta_config: dict[str, float], gt_ids: list[str],
                   n_questions: int, replicates: int, master_seed: int, *,
                   n_distractors: int = 4, repeats: int = 1, prior_scale: float = 1.0,
                   fit_config=None) -> dict:
    """simulate -> anchors -> LOO tau -> calibration -> AUC, compared to the
    AUC implied by the true theta under the same design. Includes the null
    (all theta equal) and sign (negate theta) controls."""
    from .fit import fit_anchor_model as _fit
    from .validate import restrict_counts

    def one_replicate(theta_by_id, seed):
        records = []
        calib_rows = []
        for q in range(n_questions):
            qid = f"fc{q}"
            seed_q = derive_seed(seed, qid)
            fit, counts, items_by_id, _ = simulate_question(
                theta_by_id, gt_ids, qid, seed_q, repeats=repeats,
                prior_scale=prior_scale, fit_config=fit_config,
            )
            item_list = list(items_by_id.values())
            for held_out in item_list:
                if held_out.kind == "ground_truth" and len(gt_ids) < 2:
                    continue
                reduced_ids = [it.item_id for it in item_list if it.item_id != held_out.item_id]
                reduced_counts = restrict_counts(counts, held_out.item_id)
                try:
                    # `or FAST_FIT` to match simulate_question's anchor fit: this
                    # refit runs once per held-out item per question per
                    # replicate, so it is the bulk of the simulation's cost and
                    # the production sampler settings are wasted on it.
                    reduced_fit = _fit(reduced_ids, reduced_counts, prior_scale=prior_scale,
                                       seed=seed_q + 1, fit_config=fit_config or FAST_FIT)
                except Exception:
                    continue
                if held_out.kind == "ground_truth":
                    ref = select_reference_gt(qid, [g for g in gt_ids if g != held_out.item_id], seed_q)
                else:
                    ref = select_reference_gt(qid, gt_ids, seed_q)
                loo_items = [it for it in item_list if it.item_id != held_out.item_id]
                loo_items_by_id = {it.item_id: it for it in loo_items}
                loo_items_by_id[held_out.item_id] = held_out
                comps, _w = build_candidate_design(qid, loo_items, held_out, ref, repeats, seed_q,
                                                   phase=f"loo:{held_out.item_id}")
                judge = make_stub_judge(theta_by_id, master_seed=seed_q)
                loo_result = run_comparisons(comps, loo_items_by_id, _prompt_builder(loo_items_by_id),
                                             judge, cache=None, max_retries=0)
                if not loo_result.counts:
                    continue
                score = score_candidate(reduced_fit, loo_result.counts, held_out.item_id, ref,
                                        prior_scale=prior_scale, seed=seed_q + 2)
                records.append(LooRecord(qid=qid, item_id=held_out.item_id,
                                         kind=held_out.kind, reference_gt=ref, score=score))
                label = 1.0 if held_out.kind == "ground_truth" else 0.0
                calib_rows.append({"qid": qid, "item_id": held_out.item_id,
                                   "delta_mean": score.delta_mean, "label": label,
                                   "source": held_out.kind})
        return records, calib_rows

    theta_by_id_all = dict(theta_config)
    recovered_aucs = []
    for r in range(replicates):
        seed_r = derive_seed(master_seed, "fullchain", str(r))
        records, calib_rows = one_replicate(theta_by_id_all, seed_r)
        by_q: dict[str, list] = {}
        for rec in records:
            by_q.setdefault(rec.qid, []).append(rec)
        try:
            roc = roc_from_loo(records)
            recovered_aucs.append(roc["auc"])
        except ValueError:
            continue

    # AUC implied by true theta directly (no estimation noise)
    gt_theta = np.array([theta_config[g] for g in gt_ids])
    d_theta = np.array([v for k, v in theta_config.items() if k not in gt_ids])
    # true AUC: P(true GT tau > true distractor tau) using a fixed arbitrary reference
    ref_theta = gt_theta[0]
    gt_true_tau = expit(gt_theta[1:] - ref_theta) if len(gt_theta) > 1 else np.array([])
    d_true_tau = expit(d_theta - ref_theta)
    if len(gt_true_tau) and len(d_true_tau):
        wins = sum((g > d_true_tau).sum() + 0.5 * (g == d_true_tau).sum() for g in gt_true_tau)
        true_auc = float(wins / (len(gt_true_tau) * len(d_true_tau)))
    else:
        true_auc = float("nan")

    return {
        "recovered_auc_mean": float(np.mean(recovered_aucs)) if recovered_aucs else float("nan"),
        "recovered_auc_std": float(np.std(recovered_aucs)) if recovered_aucs else float("nan"),
        "true_auc": true_auc,
        "n_replicates_with_auc": len(recovered_aucs),
    }


def run_null_control(n_items: int, replicates: int, master_seed: int, *,
                     n_gt: int = 2, repeats: int = 1, fit_config=None) -> dict:
    """All theta equal: tau should concentrate near 0.5, calibration slope
    near zero, AUC near 0.5. Any signal here is label leakage."""
    gt_ids = [f"gt{i}" for i in range(n_gt)]
    d_ids = [f"d{i}" for i in range(n_items - n_gt)]
    theta_config = {k: 0.0 for k in gt_ids + d_ids}
    result = run_full_chain(theta_config, gt_ids, n_questions=max(4, replicates // 5),
                            replicates=max(1, replicates // 10), master_seed=master_seed,
                            n_distractors=len(d_ids), repeats=repeats, fit_config=fit_config)
    return result


def run_sign_control(theta_config: dict[str, float], gt_ids: list[str],
                     n_questions: int, replicates: int, master_seed: int, *,
                     repeats: int = 1, fit_config=None) -> dict:
    """Negate all theta: Delta_hat should flip sign, AUC -> 1 - AUC."""
    pos = run_full_chain(theta_config, gt_ids, n_questions, replicates, master_seed,
                         repeats=repeats, fit_config=fit_config)
    neg_theta = {k: -v for k, v in theta_config.items()}
    neg = run_full_chain(neg_theta, gt_ids, n_questions, replicates,
                         derive_seed(master_seed, "sign"), repeats=repeats,
                         fit_config=fit_config)
    return {"positive": pos, "negated": neg}

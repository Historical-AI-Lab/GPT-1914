#!/usr/bin/env python3
"""bayes_correction.py — Hierarchical Bayesian bias correction for ChronoLogic.

Estimates bias-corrected latent population proportions for the three ChronoLogic
aspects (question_fit, context_fit, style) and overall binary accuracy, using a
block-structured IRT-style model fit with PyMC.

The model places three independent latent abilities on each question:
  theta_q ~ N(0, 1)  — drives question_fit (LLM-judged, all 712 questions)
  theta_c ~ N(0, 1)  — drives context_fit (human-judged, ~98 constrained_generation
                        questions only; absent context_fit → automatic pass downstream)
  theta_s ~ N(0, 1)  — drives style fit (independent)

Per-aspect pass probabilities are
  p_{q,a} = sigmoid(alpha_a + beta_a * theta_{*})

and the observation likelihood marginalizes the latent verdict:
  P(v = 1 | p, r) = p * r + (1 - p) * (1 - r)

For style, by default the calibrated continuous DeBERTa probability is used
directly via a logit-Normal likelihood with sigma = 1 / (2*r - 1).  Pass
``--style-likelihood binary`` to threshold continuous scores at 0.5 and use a
Bernoulli likelihood instead (ablation).

See ``modelasjudge/pymc_bias_correction_brief_revised.md`` for the spec.

Usage
-----
  python bayes_correction.py --candidate <ctag> --version <ver> [options]

Examples
--------
  # Smoke test (short chain)
  python bayes_correction.py --candidate gpt-5.4 --version 0.2 \\
      --n-draws 500 --n-tune 500 --n-chains 2

  # Full run with reliability uncertainty
  python bayes_correction.py --candidate gpt-5.4 --version 0.2 \\
      --include-r-uncertainty

  # Binary-style ablation
  python bayes_correction.py --candidate gpt-5.4 --version 0.2 \\
      --style-likelihood binary \\
      --output scored_answers/bayes_gpt-5.4__0.2_binary.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from naming import candidate_tag as _candidate_tag
from bayes_io import (
    SCORED_DIR,
    compute_raw_observed,
    load_inputs,
)


# ---------------------------------------------------------------------------
# Data preparation
# ---------------------------------------------------------------------------

@dataclass
class PreparedData:
    """Flat arrays passed to the PyMC model."""

    n_questions: int
    qnums: list[str]

    # question_fit observations (LLM-judged; may carry r_uncertainty)
    qf_obs_idx:     np.ndarray   # int64 — question index
    qf_obs_verdict: np.ndarray   # int64 in {0, 1}
    qf_obs_r:       np.ndarray   # float64

    # context_fit observations (human-judged; r_q is reliable and fixed — no r_uncertainty)
    cf_obs_idx:     np.ndarray   # int64
    cf_obs_verdict: np.ndarray   # int64
    cf_obs_r:       np.ndarray   # float64

    # style observations
    style_obs_qidx:   np.ndarray  # int64
    style_obs_logit:  np.ndarray  # float64 (only used in continuous mode)
    style_obs_binary: np.ndarray  # int64 in {0, 1} (only used in binary mode)
    style_obs_r:      np.ndarray  # float64
    style_na:         np.ndarray  # bool, shape (n_questions,)
    context_na:       np.ndarray  # bool, shape (n_questions,) — True when no context_fit obs

    # r_uncertainty bookkeeping for question_fit only.
    # Context uses fixed human r_q; style has its own (style_kn_a/b) bookkeeping.
    qf_kn:       np.ndarray  # int64 shape (n_unique_qf_r, 2) — (k, n)
    qf_r_idx:    np.ndarray  # int64, qf obs -> row in qf_kn
    style_kn_a:  np.ndarray  # int64 shape (n_unique_style_a, 2) — reasoning-type stratum
    style_kn_b:  np.ndarray  # int64 shape (n_unique_style_b, 2) — length-decile stratum
    style_a_idx: np.ndarray  # int64, style obs -> row in style_kn_a
    style_b_idx: np.ndarray  # int64, style obs -> row in style_kn_b


def _collapse_qc_block(scores: list[int]) -> int | None:
    """Collapse a same-gt_index block of judge scores.

    Returns 0 or 1 if the block has consistent evidence, or None if a pair
    splits (one 0, one 1) — in which case we drop it per the brief's
    Preprocessing section (the two orderings cancel; they tell us about judge
    order-bias on this item, not about the latent verdict).
    """
    if len(scores) == 0:
        return None
    if len(scores) == 1:
        return int(scores[0])
    s_set = set(int(s) for s in scores)
    if s_set == {0}:
        return 0
    if s_set == {1}:
        return 1
    # Mixed pair (or rare >2 mixed observation) — drop.
    return None


def _avg_style_block(scores: list[float]) -> float | None:
    if len(scores) == 0:
        return None
    return float(np.mean(scores))


def prepare_data(
    judge_data: dict,
    discrim_data: dict,
    below_threshold: set[str],
    llm_rel: dict,
    discrim_rel: dict,
    style_likelihood: str,
    include_r_uncertainty: bool,
) -> PreparedData:
    """Build flat observation arrays for the PyMC model."""

    qnums = sorted(judge_data.get("question_fit", {}).keys(), key=lambda x: int(x))
    n_q = len(qnums)

    # Per-question style NA flag
    style_na = np.array([q in below_threshold for q in qnums], dtype=bool)

    # Per-question context NA flag — True when no context_fit observation exists
    ctx_section = judge_data.get("context_fit", {})
    context_na = np.array([q not in ctx_section for q in qnums], dtype=bool)

    qf_q_idx:   list[int]   = []
    qf_verdict: list[int]   = []
    qf_r:       list[float] = []
    cf_q_idx:   list[int]   = []
    cf_verdict: list[int]   = []
    cf_r:       list[float] = []

    style_qidx:   list[int]   = []
    style_logit:  list[float] = []
    style_binary: list[int]   = []
    style_r:      list[float] = []

    # (k, n) tracking for question_fit --include-r-uncertainty only.
    # Context is human-judged (r_q already reliable and fixed; no Beta posterior needed).
    qf_kn_map:   dict[tuple[int, int], int] = {}
    style_a_map: dict[tuple[int, int], int] = {}
    style_b_map: dict[tuple[int, int], int] = {}
    qf_r_idx:    list[int] = []
    style_a_idx: list[int] = []
    style_b_idx: list[int] = []

    def _intern(d: dict, key: tuple[int, int]) -> int:
        if key not in d:
            d[key] = len(d)
        return d[key]

    for qi, qnum in enumerate(qnums):
        for aspect_idx, aspect in enumerate(("question_fit", "context_fit")):
            rec = judge_data.get(aspect, {}).get(qnum, {})
            r_q = rec.get("r_q")
            scores     = rec.get("scores", []) or []
            gt_indices = rec.get("gt_indices", []) or []
            if r_q is None or len(scores) == 0:
                continue

            # Group scores by gt_index (None counts as its own block)
            blocks: dict[object, list[int]] = {}
            for s, g in zip(scores, gt_indices):
                blocks.setdefault(g, []).append(int(s))

            r_clamped = float(np.clip(r_q, 0.501, 0.999))
            for block in blocks.values():
                collapsed = _collapse_qc_block(block)
                if collapsed is None:
                    continue
                if aspect_idx == 0:  # question_fit — LLM-judged
                    qf_q_idx.append(qi)
                    qf_verdict.append(collapsed)
                    qf_r.append(r_clamped)
                    if include_r_uncertainty:
                        pq = llm_rel.get("per_question", {}).get(qnum, {})
                        k = int(pq.get("question_correct", 0))
                        n = int(pq.get("question_total",   1))
                        qf_r_idx.append(_intern(qf_kn_map, (k, n)))
                else:                # context_fit — human-judged, r_q is fixed
                    cf_q_idx.append(qi)
                    cf_verdict.append(collapsed)
                    cf_r.append(r_clamped)

        # ---- style observations ----
        if style_na[qi]:
            continue

        sf = discrim_data.get("style", {}).get(qnum, {})
        r_sf = sf.get("r_q")
        cont = sf.get("continuous_scores", []) or []
        gt_s = sf.get("gt_indices", []) or []
        if r_sf is None or len(cont) == 0:
            # Treat as NA if we have no usable style data
            style_na[qi] = True
            continue

        # Average continuous scores within each gt_index block
        s_blocks: dict[object, list[float]] = {}
        for s, g in zip(cont, gt_s):
            s_blocks.setdefault(g, []).append(float(s))

        r_clamped = float(np.clip(r_sf, 0.501, 0.999))
        had_obs = False
        for block in s_blocks.values():
            avg = _avg_style_block(block)
            if avg is None:
                continue
            had_obs = True
            style_qidx.append(qi)
            style_r.append(r_clamped)
            # Continuous: clip and take logit
            avg_clip = float(np.clip(avg, 1e-3, 1 - 1e-3))
            style_logit.append(float(np.log(avg_clip / (1 - avg_clip))))
            # Binary: threshold at 0.5
            style_binary.append(int(avg >= 0.5))

            if include_r_uncertainty:
                dr = discrim_rel.get(qnum, {})
                ka = int(dr.get("reasoning_type_k", 0))
                na = int(dr.get("reasoning_type_n", 1))
                kb = int(dr.get("length_decile_k",  0))
                nb = int(dr.get("length_decile_n",  1))
                style_a_idx.append(_intern(style_a_map, (ka, na)))
                style_b_idx.append(_intern(style_b_map, (kb, nb)))

        if not had_obs:
            style_na[qi] = True

    def _kn_array(m: dict[tuple[int, int], int]) -> np.ndarray:
        if not m:
            return np.zeros((0, 2), dtype=np.int64)
        arr = np.zeros((len(m), 2), dtype=np.int64)
        for (k, n), idx in m.items():
            arr[idx] = (k, n)
        return arr

    return PreparedData(
        n_questions=n_q,
        qnums=qnums,
        qf_obs_idx=np.asarray(qf_q_idx, dtype=np.int64),
        qf_obs_verdict=np.asarray(qf_verdict, dtype=np.int64),
        qf_obs_r=np.asarray(qf_r, dtype=np.float64),
        cf_obs_idx=np.asarray(cf_q_idx, dtype=np.int64),
        cf_obs_verdict=np.asarray(cf_verdict, dtype=np.int64),
        cf_obs_r=np.asarray(cf_r, dtype=np.float64),
        style_obs_qidx=np.asarray(style_qidx, dtype=np.int64),
        style_obs_logit=np.asarray(style_logit, dtype=np.float64),
        style_obs_binary=np.asarray(style_binary, dtype=np.int64),
        style_obs_r=np.asarray(style_r, dtype=np.float64),
        style_na=style_na,
        context_na=context_na,
        qf_kn=_kn_array(qf_kn_map),
        qf_r_idx=np.asarray(qf_r_idx, dtype=np.int64),
        style_kn_a=_kn_array(style_a_map),
        style_kn_b=_kn_array(style_b_map),
        style_a_idx=np.asarray(style_a_idx, dtype=np.int64),
        style_b_idx=np.asarray(style_b_idx, dtype=np.int64),
    )


# ---------------------------------------------------------------------------
# PyMC model
# ---------------------------------------------------------------------------

def build_and_sample(
    data: PreparedData,
    *,
    style_likelihood: str = "continuous",
    include_r_uncertainty: bool = False,
    n_draws: int = 2000,
    n_tune: int = 1000,
    n_chains: int = 4,
    target_accept: float = 0.9,
    seed: int = 0,
    progressbar: bool = True,
):
    """Build the PyMC model and run NUTS.  Returns (model, idata)."""
    import pymc as pm
    import pytensor.tensor as pt

    N = data.n_questions
    style_na_arr = data.style_na.astype(np.float64)

    coords = {
        "aspect": ["question_fit", "context_fit", "style"],
        "question": list(range(N)),
    }

    with pm.Model(coords=coords) as model:
        alpha = pm.Normal("alpha", mu=0.0, sigma=2.0, dims="aspect")
        beta  = pm.HalfNormal("beta", sigma=2.0, dims="aspect")

        # Independent latent abilities — question, context, and style are not coupled.
        # Context is human-judged and covers only constrained_generation questions;
        # there is no empirical basis for treating it as correlated with LLM question fit.
        theta_q = pm.Normal("theta_q", mu=0.0, sigma=1.0, dims="question")
        theta_c = pm.Normal("theta_c", mu=0.0, sigma=1.0, dims="question")
        theta_s = pm.Normal("theta_s", mu=0.0, sigma=1.0, dims="question")

        p_q = pm.Deterministic("p_question",
                               pm.math.sigmoid(alpha[0] + beta[0] * theta_q),
                               dims="question")
        p_c = pm.Deterministic("p_context",
                               pm.math.sigmoid(alpha[1] + beta[1] * theta_c),
                               dims="question")
        p_s = pm.Deterministic("p_style",
                               pm.math.sigmoid(alpha[2] + beta[2] * theta_s),
                               dims="question")

        # ---- question_fit: Bernoulli with optional Beta r_uncertainty ----
        if data.qf_obs_idx.size > 0:
            if include_r_uncertainty and data.qf_kn.shape[0] > 0:
                qf_k = data.qf_kn[:, 0]
                qf_n = data.qf_kn[:, 1]
                r_qf_post = pm.Beta(
                    "r_qf",
                    alpha=1.0 + qf_k.astype(np.float64),
                    beta=1.0 + np.maximum(qf_n - qf_k, 0).astype(np.float64),
                    shape=data.qf_kn.shape[0],
                )
                r_qf = pt.clip(r_qf_post[data.qf_r_idx], 0.501, 0.999)
            else:
                r_qf = pt.as_tensor_variable(data.qf_obs_r)
            qf_p = p_q[data.qf_obs_idx]
            pm.Bernoulli("obs_question",
                         p=qf_p * r_qf + (1.0 - qf_p) * (1.0 - r_qf),
                         observed=data.qf_obs_verdict)

        # ---- context_fit: Bernoulli with fixed human r_q (no r_uncertainty) ----
        if data.cf_obs_idx.size > 0:
            r_cf = pt.as_tensor_variable(data.cf_obs_r)
            cf_p = p_c[data.cf_obs_idx]
            pm.Bernoulli("obs_context",
                         p=cf_p * r_cf + (1.0 - cf_p) * (1.0 - r_cf),
                         observed=data.cf_obs_verdict)

        # ---- style ----
        if data.style_obs_qidx.size > 0:
            if include_r_uncertainty and data.style_kn_a.shape[0] > 0:
                a_k = data.style_kn_a[:, 0]
                a_n = data.style_kn_a[:, 1]
                b_k = data.style_kn_b[:, 0]
                b_n = data.style_kn_b[:, 1]
                r_a = pm.Beta(
                    "r_style_type",
                    alpha=1.0 + a_k.astype(np.float64),
                    beta=1.0 + np.maximum(a_n - a_k, 0).astype(np.float64),
                    shape=data.style_kn_a.shape[0],
                )
                r_b = pm.Beta(
                    "r_style_decile",
                    alpha=1.0 + b_k.astype(np.float64),
                    beta=1.0 + np.maximum(b_n - b_k, 0).astype(np.float64),
                    shape=data.style_kn_b.shape[0],
                )
                obs_r_style = pt.clip(
                    pm.math.minimum(r_a[data.style_a_idx], r_b[data.style_b_idx]),
                    0.501, 0.999,
                )
            else:
                obs_r_style = pt.as_tensor_variable(data.style_obs_r)

            p_s_obs = p_s[data.style_obs_qidx]
            if style_likelihood == "continuous":
                # Logit-Normal likelihood on calibrated DeBERTa probability.
                logit_p_s = pt.log(p_s_obs / (1.0 - p_s_obs))
                sigma_s = 1.0 / (2.0 * obs_r_style - 1.0)
                pm.Normal(
                    "obs_style",
                    mu=logit_p_s,
                    sigma=sigma_s,
                    observed=data.style_obs_logit,
                )
            elif style_likelihood == "binary":
                style_l = p_s_obs * obs_r_style + (1.0 - p_s_obs) * (1.0 - obs_r_style)
                pm.Bernoulli("obs_style", p=style_l, observed=data.style_obs_binary)
            else:
                raise ValueError(f"unknown style_likelihood: {style_likelihood!r}")

        # ---- quantities of interest ----
        style_na_t   = pt.as_tensor_variable(style_na_arr)
        context_na_t = pt.as_tensor_variable(data.context_na.astype(np.float64))

        # Threshold-AND binary accuracy (headline metric, matches compute_raw_observed).
        # For each question, threshold each de-noised aspect posterior at 0.5 (hard
        # pass/fail) then AND the three indicators and average over questions.  NA aspects
        # (style below reliability threshold, or context not applicable) count as automatic
        # passes, exactly as in the raw threshold-AND count.  This is the correct estimand
        # for disattenuation upward away from the (0.5)³ noise floor; see
        # pymc_bias_correction_brief_revised.md.
        z_q = pt.ge(p_q, 0.5)
        z_c = pt.where(pt.eq(context_na_t, 1.0), 1.0, pt.ge(p_c, 0.5))
        z_s = pt.where(pt.eq(style_na_t,   1.0), 1.0, pt.ge(p_s, 0.5))
        pm.Deterministic("binary_accuracy", pm.math.mean(z_q * z_c * z_s))

        # Legacy product metric (retained for backward comparison with prior runs).
        # Computes mean(p_q · p_c · p_s) — deflates because products of sub-1
        # probabilities are always < any individual factor.
        style_eff   = pt.where(pt.eq(style_na_t,   1.0), 1.0, p_s)
        context_eff = pt.where(pt.eq(context_na_t, 1.0), 1.0, p_c)
        pm.Deterministic("binary_accuracy_product", pm.math.mean(p_q * context_eff * style_eff))
        pm.Deterministic("accuracy_question", pm.math.mean(p_q))
        # accuracy_context: average only over the questions that were actually
        # context-scored (constrained_generation subset); the remaining questions
        # have independent theta_c and a prior-only p_c — averaging them in would
        # dilute the estimate toward 0.5 without adding information.
        n_ctx = float((data.context_na == False).sum())  # noqa: E712
        if n_ctx > 0:
            pm.Deterministic(
                "accuracy_context",
                pm.math.sum(p_c * (1.0 - context_na_t)) / n_ctx,
            )
        n_non_na = float((data.style_na == False).sum())  # noqa: E712
        if n_non_na > 0:
            pm.Deterministic(
                "accuracy_style",
                pm.math.sum(p_s * (1.0 - style_na_t)) / n_non_na,
            )

        idata = pm.sample(
            draws=n_draws,
            tune=n_tune,
            chains=n_chains,
            target_accept=target_accept,
            random_seed=seed,
            progressbar=progressbar,
        )

    return model, idata


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

ASPECT_VAR_TO_RAW_KEY = {
    "accuracy_question":    "question_fit_quadratic",
    "accuracy_context":     "context_fit_quadratic",
    "accuracy_style":       "style_quadratic",
    "binary_accuracy":      "binary_accuracy",
    "binary_accuracy_product": "binary_accuracy",  # both compare against the raw AND-count
}


def _percentile_summary(samples: np.ndarray, alpha: float = 0.05) -> dict:
    lo = 100 * alpha / 2
    hi = 100 * (1 - alpha / 2)
    return {
        "mean":     float(np.mean(samples)),
        "ci_lower": float(np.percentile(samples, lo)),
        "ci_upper": float(np.percentile(samples, hi)),
    }


def summarize(idata, raw_observed: dict, alpha: float = 0.05) -> dict:
    import arviz as az

    bias_corrected: dict[str, dict] = {}
    bias_estimate:  dict[str, float] = {}

    for var, raw_key in ASPECT_VAR_TO_RAW_KEY.items():
        if var not in idata.posterior:
            continue
        samples = idata.posterior[var].values.reshape(-1)
        summ = _percentile_summary(samples, alpha=alpha)
        out_key = {
            "accuracy_question":       "question_fit",
            "accuracy_context":        "context_fit",
            "accuracy_style":          "style",
            "binary_accuracy":         "binary_accuracy",
            "binary_accuracy_product": "binary_accuracy_product",
        }[var]
        bias_corrected[out_key] = summ
        bias_estimate[out_key] = round(summ["mean"] - raw_observed.get(raw_key, float("nan")), 6)

    # Diagnostics
    diag_vars = [v for v in ASPECT_VAR_TO_RAW_KEY if v in idata.posterior]
    if "alpha" in idata.posterior:
        diag_vars = diag_vars + ["alpha", "beta"]
    n_divergent = int(idata.sample_stats["diverging"].values.sum()) \
        if "diverging" in getattr(idata, "sample_stats", {}) else 0
    rhat = az.rhat(idata, var_names=diag_vars)
    ess  = az.ess(idata,  var_names=diag_vars)
    max_rhat = float(np.nanmax(rhat.to_array().values))
    min_ess  = float(np.nanmin(ess.to_array().values))

    return {
        "bias_corrected": bias_corrected,
        "estimated_bias": bias_estimate,
        "diagnostics": {
            "n_divergent": n_divergent,
            "min_ess":     min_ess,
            "max_rhat":    max_rhat,
        },
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Hierarchical Bayesian bias correction for ChronoLogic scores",
    )
    p.add_argument("--candidate", required=True)
    p.add_argument("--version",   required=True)
    p.add_argument("--judge-file",  default=None, dest="judge_file", metavar="PATH")
    p.add_argument("--discrim-file", default=None, dest="discrim_file", metavar="PATH")
    p.add_argument("--judge-reliability",   default=None, dest="judge_reliability",   metavar="PATH")
    p.add_argument("--discrim-reliability", default=None, dest="discrim_reliability", metavar="PATH")
    p.add_argument("--style-likelihood", choices=["continuous", "binary"], default="continuous",
                   help="Style observation model (default: continuous logit-Normal)")
    p.add_argument("--include-r-uncertainty", action="store_true", dest="include_r_uncertainty",
                   help="Put Beta(1+k, 1+n-k) posteriors on reliability values")
    p.add_argument("--n-draws",  type=int, default=2000, dest="n_draws")
    p.add_argument("--n-tune",   type=int, default=1000, dest="n_tune")
    p.add_argument("--n-chains", type=int, default=4,    dest="n_chains")
    p.add_argument("--target-accept", type=float, default=0.9, dest="target_accept")
    p.add_argument("--alpha", type=float, default=0.05, help="Two-tailed CI alpha (default 0.05 → 95%% CI)")
    p.add_argument("--seed",  type=int, default=0)
    p.add_argument("--no-progress", action="store_true", dest="no_progress")
    p.add_argument("--output", default=None, metavar="PATH",
                   help="Output JSON path (default: scored_answers/bayes_{candidate}__{version}.json)")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    ctag = _candidate_tag(args.candidate)

    print(f"Loading inputs for {ctag} v{args.version} …")
    judge_data, discrim_data, below_threshold, llm_rel, discrim_rel, judge_model = load_inputs(args)
    discrim_tag = discrim_data.get("judge_tag", "unknown")
    n_q = len(judge_data.get("question_fit", {}))
    print(f"  {n_q} questions  |  judge: {judge_model}  |  discrim: {discrim_tag}")
    print(f"  below_threshold (style NA): {len(below_threshold)}")
    print(f"  style likelihood: {args.style_likelihood}"
          + ("  |  reliability uncertainty: on" if args.include_r_uncertainty else ""))

    data = prepare_data(
        judge_data, discrim_data, below_threshold,
        llm_rel, discrim_rel,
        style_likelihood=args.style_likelihood,
        include_r_uncertainty=args.include_r_uncertainty,
    )
    print(f"  obs: {data.qf_obs_idx.size} question_fit / {data.cf_obs_idx.size} context_fit / "
          f"{data.style_obs_qidx.size} style "
          f"(after collapsing paired orderings; "
          f"{int(data.style_na.sum())} questions have style NA)")

    raw_observed = compute_raw_observed(judge_data, discrim_data, below_threshold)

    print(f"\nSampling NUTS: {args.n_chains} chains × {args.n_draws} draws "
          f"(tune={args.n_tune}, target_accept={args.target_accept}, seed={args.seed}) …")

    _, idata = build_and_sample(
        data,
        style_likelihood=args.style_likelihood,
        include_r_uncertainty=args.include_r_uncertainty,
        n_draws=args.n_draws,
        n_tune=args.n_tune,
        n_chains=args.n_chains,
        target_accept=args.target_accept,
        seed=args.seed,
        progressbar=not args.no_progress,
    )

    summary = summarize(idata, raw_observed, alpha=args.alpha)
    ci_pct = int(round((1 - args.alpha) * 100))

    output = {
        "candidate":              ctag,
        "version":                args.version,
        "judge_model":            judge_model,
        "discrim_tag":            discrim_tag,
        "style_likelihood":       args.style_likelihood,
        "include_r_uncertainty":  args.include_r_uncertainty,
        "n_draws":                args.n_draws,
        "n_tune":                 args.n_tune,
        "n_chains":               args.n_chains,
        "target_accept":          args.target_accept,
        "seed":                   args.seed,
        "alpha":                  args.alpha,
        "raw_observed":           {k: round(v, 6) for k, v in raw_observed.items()},
        "bias_corrected":         {
            k: {kk: round(vv, 6) for kk, vv in v.items()}
            for k, v in summary["bias_corrected"].items()
        },
        "estimated_bias":         summary["estimated_bias"],
        "diagnostics":            summary["diagnostics"],
    }

    # Stdout summary
    print(f"\nChronoLogic Bayesian bias-correction — {ctag}, v{args.version}")
    header = f"{'aspect':18s}  {'raw':>7s}  {'corrected':>9s}  {ci_pct}% CI"
    print(header)
    print("-" * len(header))
    pairs = [
        ("question_fit",            "question_fit_quadratic"),
        ("context_fit",             "context_fit_quadratic"),
        ("style",                   "style_quadratic"),
        ("binary_accuracy",         "binary_accuracy"),
        ("binary_accuracy_product", "binary_accuracy"),
    ]
    for out_key, raw_key in pairs:
        bc = summary["bias_corrected"].get(out_key)
        raw = raw_observed.get(raw_key)
        if bc is None or raw is None:
            continue
        label = out_key.replace("binary_accuracy_product", "binary_acc (product)")
        print(f"{label:26s}  {raw:7.3f}  {bc['mean']:9.3f}  "
              f"[{bc['ci_lower']:.3f}, {bc['ci_upper']:.3f}]")

    ba_bias = summary["estimated_bias"].get("binary_accuracy", float("nan"))
    prod_bias = summary["estimated_bias"].get("binary_accuracy_product", float("nan"))
    print(f"\nBias on binary_accuracy (threshold-AND): {ba_bias:+.3f}")
    print(f"Bias on binary_acc (product, legacy):    {prod_bias:+.3f}"
          f"  ← deflation from probability multiplication")
    d = summary["diagnostics"]
    print(f"Diagnostics: divergent={d['n_divergent']}  "
          f"max R̂={d['max_rhat']:.3f}  min ESS={d['min_ess']:.0f}")

    out_path = Path(args.output) if args.output else \
        SCORED_DIR / f"bayes_{ctag}__{args.version}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()

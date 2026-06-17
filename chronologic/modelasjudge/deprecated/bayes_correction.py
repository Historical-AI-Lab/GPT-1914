#!/usr/bin/env python3
"""bayes_correction.py — Hierarchical Bayesian bias correction for ChronoLogic.

Estimates bias-corrected latent population proportions for the three ChronoLogic
aspects (question_fit, context_fit, style) and overall binary accuracy, using a
block-structured IRT-style model fit with PyMC.

The model places two latent abilities on each question:
  theta_qc ~ N(0, 1)  — drives question_fit and context_fit (induces the
                         empirically observed correlation between them)
  theta_s  ~ N(0, 1)  — drives style fit (independent by default)

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
from bootstrap_confidence import (
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

    # question_fit + context_fit (aspect 0 / 1)
    obs_question_idx: np.ndarray   # int64
    obs_aspect_idx:   np.ndarray   # int64 in {0, 1}
    obs_verdict:      np.ndarray   # int64 in {0, 1}
    obs_r:            np.ndarray   # float64

    # style observations
    style_obs_qidx:     np.ndarray  # int64
    style_obs_logit:    np.ndarray  # float64 (only used in continuous mode)
    style_obs_binary:   np.ndarray  # int64 in {0, 1} (only used in binary mode)
    style_obs_r:        np.ndarray  # float64
    style_na:           np.ndarray  # bool, shape (n_questions,)

    # Optional reliability-uncertainty bookkeeping (k, n per observation).
    # When the user passes --include-r-uncertainty we put a Beta posterior on
    # each *unique* (k, n) pair and index into it from each observation.
    qc_kn:        np.ndarray  # int64 shape (n_unique_qc_r, 2) — (k, n)
    qc_r_idx:     np.ndarray  # int64, observation -> row in qc_kn
    style_kn_a:   np.ndarray  # int64 shape (n_unique_style_a, 2) — reasoning-type stratum
    style_kn_b:   np.ndarray  # int64 shape (n_unique_style_b, 2) — length-decile stratum
    style_a_idx:  np.ndarray  # int64, style obs -> row in style_kn_a
    style_b_idx:  np.ndarray  # int64, style obs -> row in style_kn_b


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

    obs_q_idx:  list[int]   = []
    obs_a_idx:  list[int]   = []
    obs_verdict: list[int]  = []
    obs_r:      list[float] = []

    style_qidx:    list[int]   = []
    style_logit:   list[float] = []
    style_binary:  list[int]   = []
    style_r:       list[float] = []

    # (k, n) tracking for --include-r-uncertainty.  We key on the integer pair.
    qc_kn_map:      dict[tuple[int, int], int] = {}
    style_a_map:    dict[tuple[int, int], int] = {}
    style_b_map:    dict[tuple[int, int], int] = {}
    qc_r_idx:    list[int] = []
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

            for block in blocks.values():
                collapsed = _collapse_qc_block(block)
                if collapsed is None:
                    continue
                obs_q_idx.append(qi)
                obs_a_idx.append(aspect_idx)
                obs_verdict.append(collapsed)
                # clamp r away from {0, 0.5, 1} to keep likelihoods finite
                r_clamped = float(np.clip(r_q, 0.501, 0.999))
                obs_r.append(r_clamped)

                if include_r_uncertainty:
                    pq = llm_rel.get("per_question", {}).get(qnum, {})
                    if aspect_idx == 0:
                        k = int(pq.get("question_correct", 0))
                        n = int(pq.get("question_total",   1))
                    else:
                        k = int(pq.get("context_correct", 0))
                        n = int(pq.get("context_total",   1))
                    qc_r_idx.append(_intern(qc_kn_map, (k, n)))

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
        obs_question_idx=np.asarray(obs_q_idx, dtype=np.int64),
        obs_aspect_idx=np.asarray(obs_a_idx, dtype=np.int64),
        obs_verdict=np.asarray(obs_verdict, dtype=np.int64),
        obs_r=np.asarray(obs_r, dtype=np.float64),
        style_obs_qidx=np.asarray(style_qidx, dtype=np.int64),
        style_obs_logit=np.asarray(style_logit, dtype=np.float64),
        style_obs_binary=np.asarray(style_binary, dtype=np.int64),
        style_obs_r=np.asarray(style_r, dtype=np.float64),
        style_na=style_na,
        qc_kn=_kn_array(qc_kn_map),
        qc_r_idx=np.asarray(qc_r_idx, dtype=np.int64),
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

        # Non-centered latent abilities for sampler stability
        theta_qc = pm.Normal("theta_qc", mu=0.0, sigma=1.0, dims="question")
        theta_s  = pm.Normal("theta_s",  mu=0.0, sigma=1.0, dims="question")

        p_q = pm.Deterministic("p_question",
                               pm.math.sigmoid(alpha[0] + beta[0] * theta_qc),
                               dims="question")
        p_c = pm.Deterministic("p_context",
                               pm.math.sigmoid(alpha[1] + beta[1] * theta_qc),
                               dims="question")
        p_s = pm.Deterministic("p_style",
                               pm.math.sigmoid(alpha[2] + beta[2] * theta_s),
                               dims="question")

        # ---- reliability: fixed or Beta posterior ----
        if include_r_uncertainty and data.qc_kn.shape[0] > 0:
            qc_k = data.qc_kn[:, 0]
            qc_n = data.qc_kn[:, 1]
            r_qc_post = pm.Beta(
                "r_qc",
                alpha=1.0 + qc_k.astype(np.float64),
                beta=1.0 + np.maximum(qc_n - qc_k, 0).astype(np.float64),
                shape=data.qc_kn.shape[0],
            )
            obs_r_qc = pt.clip(r_qc_post[data.qc_r_idx], 0.501, 0.999)
        else:
            obs_r_qc = pt.as_tensor_variable(data.obs_r)

        # ---- question + context: Bernoulli with marginalized verdict ----
        if data.obs_question_idx.size > 0:
            p_qc_stack = pt.stack([p_q, p_c], axis=1)  # (N, 2)
            obs_p = p_qc_stack[data.obs_question_idx, data.obs_aspect_idx]
            obs_likelihood = obs_p * obs_r_qc + (1.0 - obs_p) * (1.0 - obs_r_qc)
            pm.Bernoulli("obs_qc", p=obs_likelihood, observed=data.obs_verdict)

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
        style_na_t = pt.as_tensor_variable(style_na_arr)
        style_eff = pt.where(pt.eq(style_na_t, 1.0), 1.0, p_s)
        pm.Deterministic("binary_accuracy", pm.math.mean(p_q * p_c * style_eff))
        pm.Deterministic("accuracy_question", pm.math.mean(p_q))
        pm.Deterministic("accuracy_context",  pm.math.mean(p_c))
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
    "accuracy_question": "question_fit_quadratic",
    "accuracy_context":  "context_fit_quadratic",
    "accuracy_style":    "style_quadratic",
    "binary_accuracy":   "binary_accuracy",
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
            "accuracy_question": "question_fit",
            "accuracy_context":  "context_fit",
            "accuracy_style":    "style",
            "binary_accuracy":   "binary_accuracy",
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
    print(f"  obs: {data.obs_question_idx.size} qc / {data.style_obs_qidx.size} style "
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
        ("question_fit",    "question_fit_quadratic"),
        ("context_fit",     "context_fit_quadratic"),
        ("style",           "style_quadratic"),
        ("binary_accuracy", "binary_accuracy"),
    ]
    for out_key, raw_key in pairs:
        bc = summary["bias_corrected"].get(out_key)
        raw = raw_observed.get(raw_key)
        if bc is None or raw is None:
            continue
        print(f"{out_key:18s}  {raw:7.3f}  {bc['mean']:9.3f}  "
              f"[{bc['ci_lower']:.3f}, {bc['ci_upper']:.3f}]")

    print(f"\nEstimated bias on binary_accuracy: "
          f"{summary['estimated_bias'].get('binary_accuracy', float('nan')):+.3f}")
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

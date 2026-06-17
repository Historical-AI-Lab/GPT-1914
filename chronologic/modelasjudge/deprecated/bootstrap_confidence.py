#!/usr/bin/env python3
"""bootstrap_confidence.py — Stage 5: bootstrap CIs for ChronoLogic model-as-judge scores.

For each of N bootstrap iterations: resample questions with replacement, then for
each sampled question draw latent verdicts from their posterior given observed
judge verdicts and per-question reliability r_q.  Reports bias-corrected point
estimates and percentile CIs for the three aspect scores (linear and quadratic
weighting) plus overall binary accuracy.

The binary-accuracy estimate is automatically bias-corrected for the multiplicative
compression introduced by AND-aggregation across noisy gates (Bernoulli draws).
Per-aspect scores use continuous posteriors directly — no Bernoulli sampling —
which produces narrower CIs that accurately reflect the information content.

Usage
-----
  python bootstrap_confidence.py
      --candidate CANDIDATE
      --version VERSION
      [--n-iterations 10000]
      [--alpha 0.05]
      [--seed 42]
      [--prior {uniform|empirical}]
      [--include-r-uncertainty]
      [--judge-reliability PATH]
      [--discrim-reliability PATH]
      [--judge-file PATH]
      [--discrim-file PATH]
      [--output PATH]

Examples
--------
  python bootstrap_confidence.py --candidate gpt-5.4 --version 0.2
  python bootstrap_confidence.py --candidate gpt-5.4 --version 0.2 \\
      --n-iterations 2000 --seed 17 --include-r-uncertainty
"""

import argparse
import json
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy.special import expit

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from naming import candidate_tag as _candidate_tag

SCORED_DIR  = SCRIPT_DIR / "scored_answers"
LLM_REL_DIR = SCRIPT_DIR / "llm_reliability"
CALIB_DIR   = SCRIPT_DIR / "calibration"


# ---------------------------------------------------------------------------
# Bayesian posterior helpers
# ---------------------------------------------------------------------------

def posterior_z_llm(aspect_record: dict, r_q: float, prior_log_odds: float = 0.0) -> float:
    """Posterior P(z=1) for one question on question_fit or context_fit.

    Within each gt_index block: if both orderings agree, count as one observation.
    If they split (mean == 0.5), contribute zero — the orderings cancel.
    Across distinct gt_index values, blocks are independent (sum log-odds).
    """
    scores     = aspect_record.get("scores", [])
    gt_indices = aspect_record.get("gt_indices", [])
    if r_q is None or len(scores) == 0:
        return float(expit(prior_log_odds))

    r = float(np.clip(r_q, 1e-6, 1 - 1e-6))
    if r < 0.5:
        warnings.warn(f"r_q={r_q:.4f} < 0.5; check the data", stacklevel=2)
    logit_r = float(np.log(r / (1 - r)))

    blocks: dict[int, list] = {}
    for s, idx in zip(scores, gt_indices):
        blocks.setdefault(idx, []).append(s)

    log_odds = prior_log_odds
    for block in blocks.values():
        mean = float(np.mean(block))
        if mean == 0.5:
            continue  # split pair — no evidence (order bias, not quality)
        if mean not in (0.0, 1.0):
            mean = 1.0 if mean > 0.5 else 0.0  # majority for >2 observations (rare)
        log_odds += (2 * mean - 1) * logit_r

    return float(expit(log_odds))


def posterior_z_style(style_record: dict, r_q: float, prior_log_odds: float = 0.0) -> float:
    """Posterior P(z=1) for one question on style, using continuous logistic output.

    Each continuous score s (= P(not anachronic)) contributes
        -logit(s) * (2*r_q - 1)
    to the log-odds of z=1.  Within-block: average the continuous scores first.
    """
    scores     = style_record.get("continuous_scores", [])
    gt_indices = style_record.get("gt_indices", [])
    if r_q is None or len(scores) == 0:
        return float(expit(prior_log_odds))

    r = float(np.clip(r_q, 1e-6, 1 - 1e-6))
    scale = 2 * r - 1  # may be ≤ 0 for pathological r < 0.5

    blocks: dict[int, list] = {}
    for s, idx in zip(scores, gt_indices):
        blocks.setdefault(idx, []).append(s)

    log_odds = prior_log_odds
    for block in blocks.values():
        s_mean = float(np.clip(np.mean(block), 1e-6, 1 - 1e-6))
        log_odds += -np.log(s_mean / (1 - s_mean)) * scale

    return float(expit(log_odds))


# ---------------------------------------------------------------------------
# Beta posterior sampler (for --include-r-uncertainty)
# ---------------------------------------------------------------------------

def _build_beta_counts(qnums: list[str],
                       llm_rel: dict,
                       discrim_rel: dict) -> dict[str, dict[str, tuple[int, int]]]:
    """Build {qnum: {aspect: (k, n)}} for Beta posterior sampling.

    LLM aspects ('question_fit', 'context_fit'): read from llm_rel per-question
    fields question_correct/question_total and context_correct/context_total.
    Style: read stratum counts from discrim_rel; k/n are stratum totals, not per-question.
    """
    counts: dict[str, dict[str, tuple[int, int]]] = {}
    for qnum in qnums:
        entry: dict[str, tuple[int, int]] = {}
        pq = llm_rel.get("per_question", {}).get(qnum, {})
        entry["question_fit"] = (
            int(pq.get("question_correct", 0)),
            int(pq.get("question_total",   1)),
        )
        entry["context_fit"] = (
            int(pq.get("context_correct", 0)),
            int(pq.get("context_total",   1)),
        )
        # Style: use stratum-level counts from discrim_rel
        dr = discrim_rel.get(qnum)
        if dr is not None:
            entry["style_type_k"]    = int(dr.get("reasoning_type_k", 0))
            entry["style_type_n"]    = int(dr.get("reasoning_type_n", 1))
            entry["style_decile_k"]  = int(dr.get("length_decile_k", 0))
            entry["style_decile_n"]  = int(dr.get("length_decile_n", 1))
        else:
            entry["style_type_k"]    = 0
            entry["style_type_n"]    = 1
            entry["style_decile_k"]  = 0
            entry["style_decile_n"]  = 1
        counts[qnum] = entry
    return counts


def sample_beta_r(k: int, n: int, rng: np.random.Generator) -> float:
    """Sample r from Beta(1+k, 1+n-k) — Beta(1,1) prior."""
    return float(rng.beta(1 + k, 1 + max(n - k, 0)))


# ---------------------------------------------------------------------------
# Weighted mean helper
# ---------------------------------------------------------------------------

def _weighted_mean(values: list, weights: list, mask: list | None = None) -> float | None:
    """Weighted mean; mask selects which positions to include."""
    total_w = 0.0
    total_sw = 0.0
    for i, (v, w) in enumerate(zip(values, weights)):
        if mask is not None and not mask[i]:
            continue
        if v is None:
            continue
        total_w += w
        total_sw += v * w
    if total_w == 0.0:
        return None
    return total_sw / total_w


# ---------------------------------------------------------------------------
# Input loading
# ---------------------------------------------------------------------------

def _locate_judge_file(ctag: str, version: str) -> Path:
    human = sorted(SCORED_DIR.glob(f"judge_*__{ctag}__{version}_human.json"))
    if human:
        return human[0]
    plain = sorted(SCORED_DIR.glob(f"judge_*__{ctag}__{version}.json"))
    if plain:
        return plain[0]
    raise FileNotFoundError(
        f"No judge file found for {ctag}__{version} in {SCORED_DIR}"
    )


def _locate_discrim_file(ctag: str, version: str) -> Path:
    matches = sorted(SCORED_DIR.glob(f"discrim_*__{ctag}__{version}.json"))
    if matches:
        return matches[0]
    raise FileNotFoundError(
        f"No discrim file found for {ctag}__{version} in {SCORED_DIR}"
    )


def _locate_llm_reliability(judge_model: str, version: str,
                             override: str | None) -> dict:
    if override:
        p = Path(override)
    else:
        from naming import candidate_tag
        tag = candidate_tag(judge_model)
        p = LLM_REL_DIR / f"{tag}__{version}.json"
    if not p.exists():
        raise FileNotFoundError(f"LLM reliability file not found: {p}")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _load_discrim_reliability(version: str, override: str | None) -> dict:
    """Return {str(qnum): record} from the per-question reliability JSONL."""
    if override:
        p = Path(override)
    else:
        candidates = sorted(CALIB_DIR.glob(f"*per_question_reliability_chronologic-{version}.jsonl"))
        if not candidates:
            raise FileNotFoundError(
                f"No per-question reliability JSONL found in {CALIB_DIR} for version {version}"
            )
        # prefer non-nomanual if both exist
        non_nm = [c for c in candidates if "_nomanual" not in c.name]
        p = non_nm[0] if non_nm else candidates[0]
    out: dict[str, dict] = {}
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if "_meta" in rec:
                continue
            out[str(rec["question_number"])] = rec
    return out


def load_inputs(args) -> tuple[dict, dict, set[str], dict, dict, str]:
    """Load and return (judge_data, discrim_data, below_threshold, llm_rel, discrim_rel, judge_model)."""
    ctag = _candidate_tag(args.candidate)

    judge_path  = Path(args.judge_file)  if args.judge_file  else _locate_judge_file(ctag, args.version)
    discrim_path = Path(args.discrim_file) if args.discrim_file else _locate_discrim_file(ctag, args.version)

    with open(judge_path, encoding="utf-8") as f:
        judge_data = json.load(f)
    with open(discrim_path, encoding="utf-8") as f:
        discrim_data = json.load(f)

    below_threshold: set[str] = set(str(q) for q in discrim_data.get("below_threshold", []))
    judge_model: str = judge_data.get("judge_model", "")

    llm_rel    = _locate_llm_reliability(judge_model, args.version, args.judge_reliability)
    discrim_rel = _load_discrim_reliability(args.version, args.discrim_reliability)

    return judge_data, discrim_data, below_threshold, llm_rel, discrim_rel, judge_model


# ---------------------------------------------------------------------------
# Raw observed scores (from final file or recomputed)
# ---------------------------------------------------------------------------

def compute_raw_observed(judge_data: dict, discrim_data: dict,
                         below_threshold: set[str]) -> dict[str, float]:
    """Recompute the raw observed scores without bootstrap (matches score_calculation.py)."""
    qnums = sorted(judge_data.get("question_fit", {}).keys(), key=lambda x: int(x))
    q_sq  = []
    c_sq  = []
    s_sq  = []
    s_lin = []
    q_lin = []
    c_lin = []
    binary_passes = 0

    for qnum in qnums:
        qf = judge_data["question_fit"].get(qnum, {})
        cf = judge_data["context_fit"].get(qnum, {})
        sf = discrim_data["style"].get(qnum, {})

        r_qf = qf.get("r_q", 0.0)
        r_cf = cf.get("r_q", 0.0)
        r_sf = sf.get("r_q", 0.0) if qnum not in below_threshold else None

        def _mean(lst):
            return sum(lst) / len(lst) if lst else 0.0

        score_qf = _mean(qf.get("scores", []))
        score_cf = _mean(cf.get("scores", []))

        # style: continuous score
        cont = sf.get("continuous_scores", [])
        score_sf_raw = sum(cont) / len(cont) if cont else 0.5

        wq_sq  = max(2 * r_qf - 1, 0.0) ** 2
        wq_lin = max(2 * r_qf - 1, 0.0)
        wc_sq  = max(2 * r_cf - 1, 0.0) ** 2
        wc_lin = max(2 * r_cf - 1, 0.0)

        q_sq.append((score_qf, wq_sq))
        q_lin.append((score_qf, wq_lin))
        c_sq.append((score_cf, wc_sq))
        c_lin.append((score_cf, wc_lin))

        if qnum not in below_threshold and r_sf is not None:
            ws_sq  = max(2 * r_sf - 1, 0.0) ** 2
            ws_lin = max(2 * r_sf - 1, 0.0)
            s_sq.append((score_sf_raw, ws_sq))
            s_lin.append((score_sf_raw, ws_lin))

        pass_qf = score_qf >= 0.5
        pass_cf = (not cf) or (score_cf >= 0.5)   # absent context_fit → NA pass
        pass_sf = (qnum in below_threshold) or (score_sf_raw >= 0.5)
        if pass_qf and pass_cf and pass_sf:
            binary_passes += 1

    def wm(pairs):
        tw = sum(w for _, w in pairs)
        return sum(s * w for s, w in pairs) / tw if tw > 0 else 0.0

    n = len(qnums)
    return {
        "question_fit_linear":    wm(q_lin),
        "question_fit_quadratic": wm(q_sq),
        "context_fit_linear":     wm(c_lin),
        "context_fit_quadratic":  wm(c_sq),
        "style_linear":           wm(s_lin) if s_lin else 0.0,
        "style_quadratic":        wm(s_sq)  if s_sq  else 0.0,
        "binary_accuracy":        binary_passes / n if n > 0 else 0.0,
    }


# ---------------------------------------------------------------------------
# Bootstrap main loop
# ---------------------------------------------------------------------------

def run_bootstrap(
    judge_data: dict,
    discrim_data: dict,
    below_threshold: set[str],
    llm_rel: dict,
    discrim_rel: dict,
    n_iterations: int,
    alpha: float,
    seed: int,
    include_r_uncertainty: bool,
) -> list[dict]:
    """Run the bootstrap and return one record per iteration."""
    rng = np.random.default_rng(seed)

    qnums = sorted(judge_data.get("question_fit", {}).keys(), key=lambda x: int(x))
    n_q = len(qnums)

    beta_counts = _build_beta_counts(qnums, llm_rel, discrim_rel) if include_r_uncertainty else {}

    # Pre-compute observed r_q values (used for weights in ALL cases, even --include-r-uncertainty)
    r_qf_obs = {q: float(judge_data["question_fit"].get(q, {}).get("r_q") or 0.0) for q in qnums}
    r_cf_obs = {q: float(judge_data["context_fit"].get(q, {}).get("r_q") or 0.0) for q in qnums}
    r_sf_obs = {q: float((discrim_data["style"].get(q, {}).get("r_q")) or 0.0) for q in qnums}

    records = []

    for _ in range(n_iterations):
        sampled = [qnums[i] for i in rng.integers(0, n_q, size=n_q)]

        p_question: list[float] = []
        p_context:  list[float] = []
        p_style:    list[float | None] = []
        style_na:   list[bool] = []
        w_lin:      list[list[float]] = []
        w_quad:     list[list[float]] = []
        binary_passes = 0

        for qnum in sampled:
            qf = judge_data["question_fit"].get(qnum, {})
            cf = judge_data["context_fit"].get(qnum, {})
            sf = discrim_data["style"].get(qnum, {})

            # Optionally redraw r from Beta posterior
            if include_r_uncertainty:
                bc = beta_counts.get(qnum, {})
                k, n = bc.get("question_fit", (0, 1))
                r_q_q = sample_beta_r(k, n, rng)
                k, n = bc.get("context_fit", (0, 1))
                r_q_c = sample_beta_r(k, n, rng)
                # Style: sample both strata, take min (preserving r_q = min definition)
                r1 = sample_beta_r(bc.get("style_type_k", 0),   bc.get("style_type_n", 1),   rng)
                r2 = sample_beta_r(bc.get("style_decile_k", 0), bc.get("style_decile_n", 1), rng)
                r_q_s = min(r1, r2)
            else:
                r_q_q = r_qf_obs[qnum]
                r_q_c = r_cf_obs[qnum]
                r_q_s = r_sf_obs[qnum]

            # Continuous posteriors
            pq = posterior_z_llm(qf, r_q_q)
            pc = posterior_z_llm(cf, r_q_c)

            is_na = qnum in below_threshold
            ps: float | None = None if is_na else posterior_z_style(sf, r_q_s)

            p_question.append(pq)
            p_context.append(pc)
            p_style.append(ps)
            style_na.append(is_na)

            # Weights use OBSERVED r_q — a property of the scoring rule, not the data
            wq_lin  = max(2 * r_qf_obs[qnum] - 1, 0.0)
            wc_lin  = max(2 * r_cf_obs[qnum] - 1, 0.0)
            ws_lin  = max(2 * r_sf_obs[qnum] - 1, 0.0)
            w_lin.append( [wq_lin,  wc_lin,  ws_lin])
            w_quad.append([wq_lin**2, wc_lin**2, ws_lin**2])

            # Binary AND — discrete Bernoulli draws per aspect
            zq = int(rng.random() < pq)
            zc = 1 if not cf else int(rng.random() < pc)   # absent context_fit → NA pass
            zs = 1 if is_na else int(rng.random() < ps)
            if zq and zc and zs:
                binary_passes += 1

        style_mask = [not na for na in style_na]

        rec = {
            "question_fit_linear":    _weighted_mean(p_question, [w[0] for w in w_lin]),
            "question_fit_quadratic": _weighted_mean(p_question, [w[0] for w in w_quad]),
            "context_fit_linear":     _weighted_mean(p_context,  [w[1] for w in w_lin]),
            "context_fit_quadratic":  _weighted_mean(p_context,  [w[1] for w in w_quad]),
            "style_linear":           _weighted_mean(p_style, [w[2] for w in w_lin],  mask=style_mask),
            "style_quadratic":        _weighted_mean(p_style, [w[2] for w in w_quad], mask=style_mask),
            "binary_accuracy":        binary_passes / n_q,
        }
        records.append(rec)

    return records


# ---------------------------------------------------------------------------
# Summarise bootstrap records
# ---------------------------------------------------------------------------

METRICS = [
    "question_fit_linear", "question_fit_quadratic",
    "context_fit_linear",  "context_fit_quadratic",
    "style_linear",        "style_quadratic",
    "binary_accuracy",
]


def summarize(records: list[dict], raw_observed: dict, alpha: float) -> dict:
    lo_p = 100 * alpha / 2
    hi_p = 100 * (1 - alpha / 2)

    bias_corrected: dict[str, float] = {}
    ci_lower:       dict[str, float] = {}
    ci_upper:       dict[str, float] = {}
    bias_estimate:  dict[str, float] = {}

    for m in METRICS:
        vals = [r[m] for r in records if r.get(m) is not None]
        if not vals:
            continue
        arr = np.array(vals)
        mean = float(np.mean(arr))
        bias_corrected[m] = mean
        ci_lower[m]       = float(np.percentile(arr, lo_p))
        ci_upper[m]       = float(np.percentile(arr, hi_p))
        bias_estimate[m]  = round(mean - raw_observed.get(m, float("nan")), 6)

    return {
        "bias_corrected": bias_corrected,
        "ci_lower":       ci_lower,
        "ci_upper":       ci_upper,
        "bias_estimate":  bias_estimate,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Bootstrap CIs for model-as-judge scores")
    p.add_argument("--candidate", required=True, help="Candidate model ID (or tag)")
    p.add_argument("--version",   required=True, help="Benchmark version, e.g. 0.2")
    p.add_argument("--n-iterations", type=int, default=10000, dest="n_iterations")
    p.add_argument("--alpha",  type=float, default=0.05,
                   help="Two-tailed CI alpha (default 0.05 → 95%% CI)")
    p.add_argument("--seed",   type=int,   default=42)
    p.add_argument("--prior",  choices=["uniform", "empirical"], default="uniform",
                   help="Prior on z (only 'uniform' is implemented in v1)")
    p.add_argument("--include-r-uncertainty", action="store_true", dest="include_r_uncertainty",
                   help="Also sample r_q from its Beta posterior each iteration")
    p.add_argument("--judge-reliability", default=None, dest="judge_reliability",
                   metavar="PATH", help="Override LLM-judge reliability JSON path")
    p.add_argument("--discrim-reliability", default=None, dest="discrim_reliability",
                   metavar="PATH", help="Override discriminative-judge reliability JSONL path")
    p.add_argument("--judge-file",  default=None, dest="judge_file",  metavar="PATH")
    p.add_argument("--discrim-file", default=None, dest="discrim_file", metavar="PATH")
    p.add_argument("--output", default=None, metavar="PATH",
                   help="Output JSON path (default: scored_answers/bootstrap_{candidate}__{version}.json)")
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

    raw_observed = compute_raw_observed(judge_data, discrim_data, below_threshold)

    print(f"\nRunning {args.n_iterations:,} bootstrap iterations (seed={args.seed}) …")
    if args.include_r_uncertainty:
        print("  (sampling r_q from Beta posterior each iteration)")

    records = run_bootstrap(
        judge_data, discrim_data, below_threshold,
        llm_rel, discrim_rel,
        n_iterations=args.n_iterations,
        alpha=args.alpha,
        seed=args.seed,
        include_r_uncertainty=args.include_r_uncertainty,
    )

    summary = summarize(records, raw_observed, args.alpha)
    ci_pct = int(round((1 - args.alpha) * 100))

    # Build output document
    output = {
        "candidate":              ctag,
        "version":                args.version,
        "judge":                  judge_model,
        "discrim_tag":            discrim_tag,
        "n_iterations":           args.n_iterations,
        "alpha":                  args.alpha,
        "include_r_uncertainty":  args.include_r_uncertainty,
        "raw_observed":           {k: round(v, 6) for k, v in raw_observed.items()},
        "bias_corrected":         {k: round(v, 6) for k, v in summary["bias_corrected"].items()},
        "ci_lower":               {k: round(v, 6) for k, v in summary["ci_lower"].items()},
        "ci_upper":               {k: round(v, 6) for k, v in summary["ci_upper"].items()},
        "bias_estimate":          summary["bias_estimate"],
    }

    # Stdout table
    print(f"\nChronoLogic bootstrap CIs — {ctag}, v{args.version} ({args.n_iterations} iterations)\n")
    header = f"{'metric':30s}  {'raw':>7s}  {'corrected':>9s}  {ci_pct}% CI"
    print(header)
    print("-" * len(header))
    for m in METRICS:
        raw = raw_observed.get(m)
        cor = summary["bias_corrected"].get(m)
        lo  = summary["ci_lower"].get(m)
        hi  = summary["ci_upper"].get(m)
        if raw is None or cor is None:
            continue
        label = (m.replace("question_fit_linear",    "question_fit (linear)")
                  .replace("question_fit_quadratic", "question_fit (quad)")
                  .replace("context_fit_linear",     "context_fit  (linear)")
                  .replace("context_fit_quadratic",  "context_fit  (quad)")
                  .replace("style_linear",           "style        (linear)")
                  .replace("style_quadratic",        "style        (quad)")
                  .replace("binary_accuracy",        "binary_accuracy"))
        print(f"{label:30s}  {raw:7.3f}  {cor:9.3f}  [{lo:.3f}, {hi:.3f}]")

    print(f"\nEstimated multiplicative bias on binary_accuracy: "
          f"{summary['bias_estimate'].get('binary_accuracy', float('nan')):.3f}")

    # Write JSON output
    out_path = Path(args.output) if args.output else \
        SCORED_DIR / f"bootstrap_{ctag}__{args.version}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()

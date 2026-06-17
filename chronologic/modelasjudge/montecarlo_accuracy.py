#!/usr/bin/env python3
"""montecarlo_accuracy.py — Bias-corrected AND-accuracy via MOM + Bernoulli bootstrap.

For each question, inverts the observation channel (method of moments) to obtain a
bias-corrected per-question pass probability for each aspect, then estimates the overall
binary AND-accuracy and its confidence interval via a two-level bootstrap: resample
questions, then draw a Bernoulli pass/fail per aspect per resampled question, AND them.

See corrected_and_accuracy_rationale.md for why this approach was chosen and why earlier
approaches (Bayesian product, Bayesian threshold-AND) failed.

Usage
-----
  python montecarlo_accuracy.py --candidate MODEL_ID --version VERSION [options]

Examples
--------
  python montecarlo_accuracy.py \\
      --candidate "ft:gpt-4.1-2025-04-14:tedunderwood::DNkT25IC" --version 0.4

  python montecarlo_accuracy.py \\
      --candidate gpt-5.4 --version 0.4 --n-iterations 20000 --seed 42
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from naming import candidate_tag as _ctag

SCORED_DIR = SCRIPT_DIR / "scored_answers"


# ---------------------------------------------------------------------------
# File location
# ---------------------------------------------------------------------------

def _locate_judge(ctag: str, version: str, override: str | None) -> Path:
    if override:
        return Path(override)
    human = sorted(SCORED_DIR.glob(f"judge_*__{ctag}__{version}_human.json"))
    if human:
        return human[0]
    plain = sorted(SCORED_DIR.glob(f"judge_*__{ctag}__{version}.json"))
    if plain:
        return plain[0]
    raise FileNotFoundError(f"No judge file for {ctag} v{version} in {SCORED_DIR}")


def _locate_discrim(ctag: str, version: str, override: str | None) -> Path:
    if override:
        return Path(override)
    matches = sorted(SCORED_DIR.glob(f"discrim_*__{ctag}__{version}.json"))
    if matches:
        return matches[0]
    raise FileNotFoundError(f"No discrim file for {ctag} v{version} in {SCORED_DIR}")


# ---------------------------------------------------------------------------
# Per-question observation collapse and MOM inversion
# ---------------------------------------------------------------------------

def _collapse_verdicts(scores: list, gt_indices: list) -> float:
    """Collapse paired-ordering blocks into a single observed pass probability.

    Within each gt_index block, average the scores. If the average is exactly 0.5
    (paired orderings split), the block carries no information and is dropped.
    Otherwise binarise (> 0.5 → 1, < 0.5 → 0). Return the mean of surviving
    block verdicts, or 0.5 (no information) if all blocks split.
    """
    blocks: dict[int, list] = {}
    for s, idx in zip(scores, gt_indices):
        blocks.setdefault(0 if idx is None else int(idx), []).append(float(s))
    verdicts: list[float] = []
    for block in blocks.values():
        m = sum(block) / len(block)
        if m != 0.5:
            verdicts.append(1.0 if m > 0.5 else 0.0)
    return sum(verdicts) / len(verdicts) if verdicts else 0.5


def _mom_bsc(obs: float, r: float) -> float:
    """MOM inversion of a binary-symmetric channel.

    π̂ = clamp( (obs − (1−r)) / (2r − 1), 0, 1 )

    When obs > 0.5 and r > 0.5, π̂ > obs — the correction is upward, recovering
    the true pass rate from a noisy channel that compresses toward 0.5.
    """
    if r <= 0.5:
        return float(np.clip(obs, 0.0, 1.0))
    pi = (obs - (1.0 - r)) / (2.0 * r - 1.0)
    return float(np.clip(pi, 0.0, 1.0))


# ---------------------------------------------------------------------------
# Build per-question corrected probabilities
# ---------------------------------------------------------------------------

def corrected_probabilities(
    judge_data: dict,
    discrim_data: dict,
) -> tuple[list[str], dict[str, tuple[float, float, float]]]:
    """Return (sorted qnums, {qnum: (pi_q, pi_c, pi_s)}).

    NA aspects use 1.0 (auto-pass), matching the raw AND-count convention:
      context NA  — question not scored for context fit (non book-context)
      style NA    — question's discriminator reliability below threshold
    """
    qnums = sorted(judge_data["question_fit"].keys(), key=lambda x: int(x))
    below_threshold = set(str(q) for q in discrim_data.get("below_threshold", []))
    context_qs = set(str(q) for q in judge_data.get("book_context_qnums", []))

    probs: dict[str, tuple[float, float, float]] = {}
    for q in qnums:
        # Question fit — binary-symmetric channel.
        # Use the Bayesian posterior P(z=1|obs, r) with a flat prior:
        #   obs > 0.5  →  pi = r_q   (judge said pass; true pass prob = reliability)
        #   obs < 0.5  →  pi = 1−r_q (judge said fail; true pass prob = 1−reliability)
        #   obs = 0.5  →  pi = 0.5   (uninformative — all paired blocks split)
        # This keeps per-question uncertainty proportional to judge reliability,
        # matching the same treatment applied to style below.
        qf = judge_data["question_fit"].get(q, {})
        scores = qf.get("scores", [])
        gt_idx = qf.get("gt_indices", list(range(len(scores))))
        r_q = float(qf.get("r_q") or 0.75)
        obs_q = _collapse_verdicts(scores, gt_idx) if scores else 0.5
        pi_q = r_q if obs_q > 0.5 else (1.0 - r_q if obs_q < 0.5 else 0.5)

        # Context fit — same treatment; auto-pass if not a context-scored question
        if q in context_qs:
            cf = judge_data["context_fit"].get(q, {})
            cf_scores = cf.get("scores", [])
            cf_idx = cf.get("gt_indices", list(range(len(cf_scores))))
            r_c = float(cf.get("r_q") or 0.75)
            obs_c = _collapse_verdicts(cf_scores, cf_idx) if cf_scores else 0.5
            pi_c = r_c if obs_c > 0.5 else (1.0 - r_c if obs_c < 0.5 else 0.5)
        else:
            pi_c = 1.0

        # Style — the DeBerTa score is treated as a binary classifier (threshold 0.5).
        # We use the same posterior logic: reliability tells us how often the binary
        # decision is correct, not what the continuous probability calibration is.
        # Auto-pass if below the reliability threshold.
        if q in below_threshold:
            pi_s = 1.0
        else:
            sf = discrim_data["style"].get(q, {})
            cont = sf.get("continuous_scores", [])
            r_s = float(sf.get("r_q") or 0.75)
            mean_score = float(np.mean(cont)) if cont else 0.5
            pi_s = r_s if mean_score > 0.5 else (1.0 - r_s if mean_score < 0.5 else 0.5)

        probs[q] = (pi_q, pi_c, pi_s)
    return qnums, probs


# ---------------------------------------------------------------------------
# Per-question reliability extraction
# ---------------------------------------------------------------------------

def _question_reliabilities(
    qnums: list[str],
    judge_data: dict,
    discrim_data: dict,
    context_qs: set[str],
    style_na: set[str],
) -> dict[str, tuple[float, float | None, float | None]]:
    """Return {qnum: (r_q, r_c_or_None, r_s_or_None)}.

    None marks an NA aspect (context not scored; style below reliability threshold).
    NA aspects auto-pass deterministically and contribute 1.0 to both floor and ceiling
    in score_ranges().  Reliability defaults mirror corrected_probabilities(): 0.75.
    """
    result: dict[str, tuple[float, float | None, float | None]] = {}
    for q in qnums:
        qf = judge_data["question_fit"].get(q, {})
        r_q = float(qf.get("r_q") or 0.75)

        if q in context_qs:
            cf = judge_data["context_fit"].get(q, {})
            r_c: float | None = float(cf.get("r_q") or 0.75)
        else:
            r_c = None

        if q in style_na:
            r_s: float | None = None
        else:
            sf = discrim_data["style"].get(q, {})
            r_s = float(sf.get("r_q") or 0.75)

        result[q] = (r_q, r_c, r_s)
    return result


# ---------------------------------------------------------------------------
# Score range (floor / ceiling) given judge reliabilities
# ---------------------------------------------------------------------------

def score_ranges(
    qnums: list[str],
    judge_data: dict,
    discrim_data: dict,
    context_qs: set[str],
    style_na: set[str],
) -> dict[str, tuple[float, float]]:
    """Compute per-metric (min, max) of the reliability-adjusted score.

    Under the symmetric per-verdict reliability model an observed pass maps to r and
    an observed fail maps to 1-r, so the achievable range for each aspect is
    [mean(1-r), mean(r)] over the questions that aspect covers.  NA aspects contribute
    1.0 to both floor and ceiling (they auto-pass by benchmark design).

    Returns {metric: (min, max)} for
        "binary_accuracy", "question_fit", "context_fit", "style".
    Returns (nan, nan) for an aspect with no covered questions.
    """
    nan = float("nan")
    reliabilities = _question_reliabilities(
        qnums, judge_data, discrim_data, context_qs, style_na
    )

    qf_r, cf_r, sty_r = [], [], []
    and_ceil, and_floor = [], []

    for q in qnums:
        r_q, r_c, r_s = reliabilities[q]

        qf_r.append(r_q)

        if r_c is not None:
            cf_r.append(r_c)

        if r_s is not None:
            sty_r.append(r_s)

        # AND-accuracy: NA aspects contribute 1.0 to both bounds
        ceil_q  = r_q  * (r_c  if r_c  is not None else 1.0) * (r_s  if r_s  is not None else 1.0)
        floor_q = (1 - r_q) * ((1 - r_c) if r_c is not None else 1.0) * ((1 - r_s) if r_s is not None else 1.0)
        and_ceil.append(ceil_q)
        and_floor.append(floor_q)

    def _bounds(rs: list[float]) -> tuple[float, float]:
        if not rs:
            return nan, nan
        mean_r = float(np.mean(rs))
        return 1.0 - mean_r, mean_r

    return {
        "binary_accuracy": (float(np.mean(and_floor)), float(np.mean(and_ceil))),
        "question_fit":    _bounds(qf_r),
        "context_fit":     _bounds(cf_r),
        "style":           _bounds(sty_r),
    }


# ---------------------------------------------------------------------------
# Range normalization
# ---------------------------------------------------------------------------

def range_normalize(
    point: float,
    ci_lower: float,
    ci_upper: float,
    lo: float,
    hi: float,
) -> dict[str, float]:
    """Linearly rescale point and CI endpoints into [0, 1] relative to (lo, hi).

    norm(x) = clip((x - lo) / (hi - lo), 0, 1)

    Returns {"norm_point", "norm_ci_lower", "norm_ci_upper"}, all nan when
    hi <= lo or any input is nan.
    """
    nan = float("nan")
    if not (hi > lo) or any(v != v for v in (point, ci_lower, ci_upper, lo, hi)):
        return {"norm_point": nan, "norm_ci_lower": nan, "norm_ci_upper": nan}
    span = hi - lo

    def _n(x: float) -> float:
        return float(np.clip((x - lo) / span, 0.0, 1.0))

    return {
        "norm_point":    _n(point),
        "norm_ci_lower": _n(ci_lower),
        "norm_ci_upper": _n(ci_upper),
    }


# ---------------------------------------------------------------------------
# Raw binary accuracy (threshold-AND on observed means, for comparison)
# ---------------------------------------------------------------------------

def raw_observed(
    qnums: list[str],
    judge_data: dict,
    discrim_data: dict,
) -> dict[str, float]:
    """Compute raw observed scores for all aspects plus binary_accuracy.

    Per-aspect scores are simple (unweighted) means of observed verdicts over the
    questions each aspect covers.  binary_accuracy is the threshold-AND count.
    """
    below = set(str(q) for q in discrim_data.get("below_threshold", []))
    ctx_qs = set(str(q) for q in judge_data.get("book_context_qnums", []))

    qf_obs, cf_obs, sty_obs = [], [], []
    passes = 0

    for q in qnums:
        qf = judge_data["question_fit"].get(q, {})
        scores = qf.get("scores", [])
        gt_idx = qf.get("gt_indices", list(range(len(scores))))
        obs_q = _collapse_verdicts(scores, gt_idx) if scores else 0.5
        qf_obs.append(obs_q)

        if q in ctx_qs:
            cf = judge_data["context_fit"].get(q, {})
            cs = cf.get("scores", [])
            ci = cf.get("gt_indices", list(range(len(cs))))
            obs_c = _collapse_verdicts(cs, ci) if cs else 0.5
            cf_obs.append(obs_c)
        else:
            obs_c = 1.0

        if q in below:
            obs_s = 1.0
        else:
            sf = discrim_data["style"].get(q, {})
            cont = sf.get("continuous_scores", [])
            mean_cont = float(np.mean(cont)) if cont else 0.5
            obs_s = 1.0 if mean_cont >= 0.5 else 0.0
            sty_obs.append(obs_s)

        if obs_q >= 0.5 and obs_c >= 0.5 and obs_s >= 0.5:
            passes += 1

    n = len(qnums)
    return {
        "binary_accuracy": passes / n if n else 0.0,
        "question_fit":    float(np.mean(qf_obs))  if qf_obs  else float("nan"),
        "context_fit":     float(np.mean(cf_obs))  if cf_obs  else float("nan"),
        "style":           float(np.mean(sty_obs)) if sty_obs else float("nan"),
    }


# ---------------------------------------------------------------------------
# Point estimates
# ---------------------------------------------------------------------------

def point_estimates(
    qnums: list[str],
    probs: dict[str, tuple[float, float, float]],
    context_qs: set[str],
    style_na: set[str],
) -> dict[str, float]:
    """Deterministic point estimates: mean of per-question products / means."""
    joints, pqs, pcs, pss = [], [], [], []
    for q in qnums:
        pi_q, pi_c, pi_s = probs[q]
        joints.append(pi_q * pi_c * pi_s)
        pqs.append(pi_q)
        if q in context_qs:
            pcs.append(pi_c)
        if q not in style_na:
            pss.append(pi_s)
    return {
        "binary_accuracy": float(np.mean(joints)),
        "question_fit":    float(np.mean(pqs)),
        "context_fit":     float(np.mean(pcs))  if pcs  else float("nan"),
        "style":           float(np.mean(pss))  if pss  else float("nan"),
    }


# ---------------------------------------------------------------------------
# Bootstrap CI
# ---------------------------------------------------------------------------

def bootstrap_ci(
    qnums: list[str],
    probs: dict[str, tuple[float, float, float]],
    context_qs: set[str],
    style_na: set[str],
    n_iterations: int = 10_000,
    alpha: float = 0.05,
    seed: int = 0,
) -> dict[str, dict[str, float]]:
    """Two-level bootstrap CI.

    binary_accuracy: resample questions, then draw Bernoulli pass/fail per aspect
        per resampled question, AND the three draws. This captures both question-
        sampling variability and per-question pass/fail uncertainty (questions near the
        0.5 threshold contribute genuine CI width; confident passes/fails do not).
        NA aspects have pi=1.0 so their Bernoulli draws are always 1 — no penalty.

    Per-aspect scores: resample questions only (continuous mean, no Bernoulli).
    """
    rng = np.random.default_rng(seed)
    N = len(qnums)

    pi_q = np.array([probs[q][0] for q in qnums])
    pi_c = np.array([probs[q][1] for q in qnums])
    pi_s = np.array([probs[q][2] for q in qnums])
    ctx_mask = np.array([q in context_qs for q in qnums])
    sty_mask = np.array([q not in style_na  for q in qnums])

    ba_samp  = np.empty(n_iterations)
    qf_samp  = np.empty(n_iterations)
    cf_samp  = np.empty(n_iterations)
    sty_samp = np.empty(n_iterations)

    for i in range(n_iterations):
        idx = rng.integers(0, N, size=N)
        pq = pi_q[idx];  pc = pi_c[idx];  ps = pi_s[idx]
        cm = ctx_mask[idx];  sm = sty_mask[idx]

        # Bernoulli draws — context/style NA have pi=1 → always pass
        zq = rng.random(N) < pq
        zc = rng.random(N) < pc
        zs = rng.random(N) < ps

        ba_samp[i]  = np.mean(zq & zc & zs)
        qf_samp[i]  = np.mean(pq)                        # continuous, no Bernoulli
        cf_samp[i]  = np.mean(pc[cm]) if cm.any() else np.nan
        sty_samp[i] = np.mean(ps[sm]) if sm.any() else np.nan

    lo, hi = 100 * alpha / 2, 100 * (1 - alpha / 2)

    def _ci(arr: np.ndarray) -> dict[str, float]:
        v = arr[np.isfinite(arr)]
        if len(v) == 0:
            return {"mean": float("nan"), "ci_lower": float("nan"), "ci_upper": float("nan")}
        return {
            "mean":     float(np.mean(v)),
            "ci_lower": float(np.percentile(v, lo)),
            "ci_upper": float(np.percentile(v, hi)),
        }

    return {
        "binary_accuracy": _ci(ba_samp),
        "question_fit":    _ci(qf_samp),
        "context_fit":     _ci(cf_samp),
        "style":           _ci(sty_samp),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="MOM-corrected AND-accuracy with Bernoulli bootstrap CI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--candidate",   required=True, metavar="MODEL_ID",
                        help="Candidate model ID (e.g. gpt-5.4 or full ft: string)")
    parser.add_argument("--version",     required=True, metavar="VER",
                        help="Benchmark version (e.g. 0.4)")
    parser.add_argument("--judge-file",  default=None, dest="judge_file",  metavar="PATH",
                        help="Override auto-located judge scored file")
    parser.add_argument("--discrim-file", default=None, dest="discrim_file", metavar="PATH",
                        help="Override auto-located discrim scored file")
    parser.add_argument("--n-iterations", type=int, default=10_000, dest="n_iterations",
                        help="Bootstrap iterations (default: 10000)")
    parser.add_argument("--alpha", type=float, default=0.05,
                        help="CI alpha — e.g. 0.05 → 95%% CI (default: 0.05)")
    parser.add_argument("--seed",  type=int, default=0)
    parser.add_argument("--output", default=None, metavar="PATH",
                        help="Output JSON path (default: scored_answers/mcacc_{ctag}__{version}.json)")
    args = parser.parse_args()

    ctag        = _ctag(args.candidate)
    judge_path  = _locate_judge(ctag, args.version, args.judge_file)
    discrim_path = _locate_discrim(ctag, args.version, args.discrim_file)

    with open(judge_path,  encoding="utf-8") as f: judge_data  = json.load(f)
    with open(discrim_path, encoding="utf-8") as f: discrim_data = json.load(f)

    judge_model     = judge_data.get("judge_model", "")
    below_threshold = set(str(q) for q in discrim_data.get("below_threshold", []))
    context_qs      = set(str(q) for q in judge_data.get("book_context_qnums", []))

    print(f"Judge:   {judge_path.name}")
    print(f"Discrim: {discrim_path.name}")

    qnums, probs = corrected_probabilities(judge_data, discrim_data)
    n_style_na = sum(1 for q in qnums if q in below_threshold)
    print(f"Questions: {len(qnums)}  |  style NA: {n_style_na}  |  context scored: {len(context_qs)}")

    raw    = raw_observed(qnums, judge_data, discrim_data)
    raw_ba = raw["binary_accuracy"]
    pts    = point_estimates(qnums, probs, context_qs, below_threshold)

    print(f"Running bootstrap ({args.n_iterations} iterations, seed={args.seed}) …")
    cis = bootstrap_ci(
        qnums, probs, context_qs, below_threshold,
        n_iterations=args.n_iterations, alpha=args.alpha, seed=args.seed,
    )

    # Range-normalized reporting
    ranges = score_ranges(qnums, judge_data, discrim_data, context_qs, below_threshold)
    norms: dict[str, dict[str, float]] = {}
    for key in ("binary_accuracy", "question_fit", "context_fit", "style"):
        lo, hi = ranges[key]
        ci = cis[key]
        norms[key] = range_normalize(pts[key], ci["ci_lower"], ci["ci_upper"], lo, hi)

    # --- stdout ---
    ci_pct = int(round((1 - args.alpha) * 100))
    print(f"\nChronoLogic MOM accuracy — {ctag}, v{args.version}")

    # Table 1: raw + corrected
    hdr1 = f"{'metric':20s}  {'raw':>7s}  {'corrected':>9s}  {ci_pct}% CI"
    print(hdr1)
    print("-" * len(hdr1))
    for key, raw_val in [
        ("binary_accuracy", raw["binary_accuracy"]),
        ("question_fit",    raw["question_fit"]),
        ("context_fit",     raw["context_fit"]),
        ("style",           raw["style"]),
    ]:
        pt = pts[key]
        ci = cis[key]
        raw_str = f"{raw_val:7.3f}" if raw_val is not None else "      —"
        if not (pt == pt):  # nan
            continue
        print(f"{key:20s}  {raw_str}  {pt:9.3f}  [{ci['ci_lower']:.3f}, {ci['ci_upper']:.3f}]")
    print(f"\nEstimated bias on binary_accuracy: {pts['binary_accuracy'] - raw_ba:+.3f}")

    # Table 2: range-normalized
    print(f"\nRange-normalized (% of possible score range given judge reliability)")
    hdr2 = f"{'metric':20s}  {'min':>7s}  {'max':>7s}  {'corrected':>9s}  {'% of range':>10s}  {ci_pct}% CI"
    print(hdr2)
    print("-" * len(hdr2))
    for key in ("binary_accuracy", "question_fit", "context_fit", "style"):
        pt = pts[key]
        if not (pt == pt):  # nan aspect
            continue
        lo, hi = ranges[key]
        nr = norms[key]
        np_val = nr["norm_point"]
        if not (np_val == np_val):
            rng_str = f"  {'—':>7s}  {'—':>7s}"
            norm_str = f"  {'—':>10s}  {'—':>14s}"
        else:
            rng_str  = f"  {lo:7.3f}  {hi:7.3f}"
            norm_str = (f"  {np_val:10.3f}"
                        f"  [{nr['norm_ci_lower']:.3f}, {nr['norm_ci_upper']:.3f}]")
        print(f"{key:20s}{rng_str}  {pt:9.3f}{norm_str}")

    # --- output JSON ---
    def _r6(x: float) -> float:
        return round(x, 6) if x == x else x  # preserve nan as-is

    output = {
        "candidate":           ctag,
        "version":             args.version,
        "judge_model":         judge_model,
        "judge_file":          str(judge_path),
        "discrim_file":        str(discrim_path),
        "n_questions":         len(qnums),
        "n_style_na":          n_style_na,
        "n_context_scored":    len(context_qs),
        "raw": {k: round(v, 6) for k, v in raw.items()},
        "corrected": {
            k: {
                "point":          round(pts[k], 6),
                "ci_lower":       round(cis[k]["ci_lower"], 6),
                "ci_upper":       round(cis[k]["ci_upper"], 6),
                "bootstrap_mean": round(cis[k]["mean"], 6),
            }
            for k in ("binary_accuracy", "question_fit", "context_fit", "style")
        },
        "range_normalized": {
            k: {
                "min":           _r6(ranges[k][0]),
                "max":           _r6(ranges[k][1]),
                "norm_point":    _r6(norms[k]["norm_point"]),
                "norm_ci_lower": _r6(norms[k]["norm_ci_lower"]),
                "norm_ci_upper": _r6(norms[k]["norm_ci_upper"]),
            }
            for k in ("binary_accuracy", "question_fit", "context_fit", "style")
        },
        "settings": {
            "n_iterations": args.n_iterations,
            "alpha":        args.alpha,
            "seed":         args.seed,
            "ci_pct":       ci_pct,
        },
    }

    out_path = (Path(args.output) if args.output
                else SCORED_DIR / f"mcacc_{ctag}__{args.version}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()

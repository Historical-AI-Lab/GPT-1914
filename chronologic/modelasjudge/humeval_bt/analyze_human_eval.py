#!/usr/bin/env python3
"""analyze_human_eval.py — fit the human-choice calibration model for p_fit.

Implements spec sections 2-6 of human-validation-for-pfit-spec.md:

  1. Decode each rater's *_annotated.jsonl (from rate_pairs.py) against
     master_pairs.jsonl (from sample_pairs.py) to recover Y_ir = 1 iff the
     rater chose the higher-p_fit candidate, plus x_i = |Delta logit(p_fit)|,
     m_i = midpoint, side_ir = which slot (A/B, coded +-1) the higher-p_fit
     candidate was shown in for that rater.
  2. Fit a hierarchical logistic model in PyMC:
       logit P(Y_ir=1) = beta_x*x_i + beta_xm*x_i*(m_i-0.5)
                         + u_i + a_r + gamma*side_ir
       u_i ~ Normal(0, sigma_u)   (pair random effect)
       a_r ~ Normal(0, sigma_a)   (rater random effect)
     No global intercept and no midpoint main effect -- both terms multiply
     x_i, so f(0, m) = 0 by construction: at zero delta a random human
     agrees with a random human with probability exactly 0.5 in expectation.
  3. Posterior-predictive q_MH(d) (random human vs. the higher-p_fit answer)
     and q_HH(d) (two random humans agree with each other).
  4. Invert those curves for d_detect and d_75 (with CIs from the posterior
     bands).
  5. Propagate the fitted curve to all C(12,2) candidate-pair comparisons
     over the full 346-question benchmark: W_AB and P(majority prefers A).
  6. Solve for d_346, the homogeneous per-question p_fit gap that would give
     95% majority-level discrimination if spread evenly across 346 questions.

Usage
-----
  python analyze_human_eval.py [options]

  --annotated-dir PATH   Default: modelasjudge/humeval_bt/round1/
                          (globs *_annotated.jsonl there)
  --master PATH          Default: <--annotated-dir>/master_pairs.jsonl
  --scored-glob PATTERN  Default: judge_*__*__0.8__c-*__j-medium_btcontext.json
  --d75-threshold FLOAT  Default: 0.75
  --majority-z FLOAT     Default: 1.96
  --n-questions INT...   Question count(s) N for the homogeneous-gap
                          resolution d_N (spec section 6). Space-separated;
                          one d_N block is emitted per value. Default: the
                          --question-subset size if given, else 346.
  --question-subset PATH File of benchmark question_numbers (whitespace or
                          comma separated). Restricts m_ref and the model-
                          pair comparison channel to those questions.
  --n-draws INT          Monte Carlo nuisance draws per posterior sample.
  --save-posterior PATH  Write retained posterior draws to .npz.
                          Default: 200
  --mcmc-draws INT       Default: 2000
  --mcmc-tune INT        Default: 1000
  --target-accept FLOAT  NUTS target acceptance. Default: 0.9
  --seed INT             Default: 1914
  --out-dir PATH         Default: <--annotated-dir>/analysis/

Example
-------
  cd modelasjudge/humeval_bt
  ~/Dropbox/python/py310hf/bin/python3 analyze_human_eval.py
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq
from scipy.special import expit, logit

SCRIPT_DIR = Path(__file__).resolve().parent
MODELASJUDGE_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(MODELASJUDGE_DIR))
sys.path.insert(0, str(SCRIPT_DIR))

from sample_pairs import (  # noqa: E402
    DEFAULT_SCORED_DIR, DEFAULT_GENERATED_DIR, DEFAULT_SCORED_GLOB,
    load_candidates,
)

DEFAULT_ANNOTATED_DIR = SCRIPT_DIR / "round1"
MAX_POSTERIOR_SUBSET = 300  # posterior draws used for MC curve/prediction work
D_GRID_MAX = 12.0
D_GRID_N = 240
EPS = 1e-6


# ---------------------------------------------------------------------------
# 1. Decode judgments
# ---------------------------------------------------------------------------

def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def decode_judgments(master_by_id: dict, annotated_dir: Path) -> tuple[list[dict], dict]:
    files = sorted(annotated_dir.glob("*_annotated.jsonl"))
    if not files:
        raise SystemExit(f"No *_annotated.jsonl files found in {annotated_dir}")

    rows = []
    rater_counts: dict[str, int] = {}
    for f in files:
        n = 0
        for rec in load_jsonl(f):
            pair_id, rater_id = rec["pair_id"], rec["rater_id"]
            m_row = master_by_id.get(pair_id)
            if m_row is None:
                print(f"Warning: {pair_id} in {f.name} not in master -- skipping",
                      file=sys.stderr)
                continue
            rater_entry = next((r for r in m_row["raters"] if r["rater_id"] == rater_id), None)
            if rater_entry is None:
                print(f"Warning: rater {rater_id} not assigned to {pair_id} per master "
                      "-- skipping", file=sys.stderr)
                continue
            side_of_hi = rater_entry["side_of_hi"]
            y = 1 if rec["choice"] == side_of_hi else 0
            side_code = 1.0 if side_of_hi == "A" else -1.0
            rows.append({
                "pair_id": pair_id, "rater_id": rater_id,
                "x": m_row["x"], "m": m_row["m"], "y": y, "side": side_code,
                "stratum": m_row["stratum"],
            })
            n += 1
        rater_counts[rater_id_from_filename(f)] = n
    return rows, rater_counts


def rater_id_from_filename(path: Path) -> str:
    # humeval_pfit_{rater}_annotated.jsonl
    stem = path.stem
    if stem.startswith("humeval_pfit_") and stem.endswith("_annotated"):
        return stem[len("humeval_pfit_"):-len("_annotated")]
    return stem


def pair_agreement_rows(master: list[dict], judgments: list[dict]) -> list[dict]:
    """One row per pair with exactly 2 recorded judgments: did the two raters agree?"""
    by_pair: dict[str, list[dict]] = {}
    for j in judgments:
        by_pair.setdefault(j["pair_id"], []).append(j)
    out = []
    for pair_id, js in by_pair.items():
        if len(js) != 2:
            continue
        agree = 1 if js[0]["y"] == js[1]["y"] else 0
        out.append({"pair_id": pair_id, "x": js[0]["x"], "m": js[0]["m"],
                    "stratum": js[0]["stratum"], "agree": agree})
    return out


# ---------------------------------------------------------------------------
# 2. Fit the hierarchical model
# ---------------------------------------------------------------------------

def fit_model(judgments: list[dict], mcmc_draws: int, mcmc_tune: int, seed: int,
              target_accept: float = 0.9):
    import pymc as pm
    import arviz as az

    pair_ids = sorted({j["pair_id"] for j in judgments})
    rater_ids = sorted({j["rater_id"] for j in judgments})
    pair_idx_of = {p: i for i, p in enumerate(pair_ids)}
    rater_idx_of = {r: i for i, r in enumerate(rater_ids)}

    x = np.array([j["x"] for j in judgments])
    m = np.array([j["m"] for j in judgments])
    y = np.array([j["y"] for j in judgments])
    side = np.array([j["side"] for j in judgments])
    pair_idx = np.array([pair_idx_of[j["pair_id"]] for j in judgments])
    rater_idx = np.array([rater_idx_of[j["rater_id"]] for j in judgments])

    n_pairs, n_raters = len(pair_ids), len(rater_ids)

    with pm.Model() as model:
        beta_x = pm.Normal("beta_x", 0.0, 2.0)
        beta_xm = pm.Normal("beta_xm", 0.0, 2.0)
        gamma = pm.Normal("gamma", 0.0, 2.0)
        sigma_u = pm.HalfNormal("sigma_u", 1.0)
        sigma_a = pm.HalfNormal("sigma_a", 1.0)

        # Non-centered: pairs carry 1-2 obs each, so the centered form funnels
        # (184 divergences, sigma_u r_hat 1.08). Same prior, reparameterized.
        u_raw = pm.Normal("u_raw", 0.0, 1.0, shape=n_pairs)
        a_raw = pm.Normal("a_raw", 0.0, 1.0, shape=n_raters)
        u = pm.Deterministic("u", sigma_u * u_raw)
        a = pm.Deterministic("a", sigma_a * a_raw)

        eta = (beta_x * x + beta_xm * x * (m - 0.5)
               + u[pair_idx] + a[rater_idx] + gamma * side)
        pm.Bernoulli("Y_obs", logit_p=eta, observed=y)

        trace = pm.sample(draws=mcmc_draws, tune=mcmc_tune, chains=4,
                          target_accept=target_accept, random_seed=seed,
                          progressbar=False)

    summary = az.summary(trace, var_names=["beta_x", "beta_xm", "gamma", "sigma_u", "sigma_a"])
    return trace, summary


def get_posterior_arrays(trace, max_draws: int, rng: np.random.Generator) -> dict:
    post = trace.posterior
    flat = {k: post[k].values.reshape(-1)
            for k in ("beta_x", "beta_xm", "gamma", "sigma_u", "sigma_a")}
    n_total = len(flat["beta_x"])
    if n_total > max_draws:
        idx = rng.choice(n_total, size=max_draws, replace=False)
        flat = {k: v[idx] for k, v in flat.items()}
    return flat


# ---------------------------------------------------------------------------
# 3. Posterior-predictive curves over a d grid (marginalized over midpoint)
# ---------------------------------------------------------------------------

def compute_curve(flat: dict, m_pool: np.ndarray, d_grid: np.ndarray, n_mc: int,
                   rng: np.random.Generator, two_rater: bool) -> np.ndarray:
    P = len(flat["beta_x"])
    curves = np.zeros((P, len(d_grid)))
    for p in range(P):
        bx, bxm, g = flat["beta_x"][p], flat["beta_xm"][p], flat["gamma"][p]
        su, sa = flat["sigma_u"][p], flat["sigma_a"][p]
        m_s = rng.choice(m_pool, size=n_mc)
        u = rng.normal(0.0, su, size=n_mc)
        if not two_rater:
            a = rng.normal(0.0, sa, size=n_mc)
            side = rng.choice([-1.0, 1.0], size=n_mc)
            for j, d in enumerate(d_grid):
                eta = bx * d + bxm * d * (m_s - 0.5) + u + a + g * side
                curves[p, j] = expit(eta).mean()
        else:
            a1 = rng.normal(0.0, sa, size=n_mc)
            a2 = rng.normal(0.0, sa, size=n_mc)
            s1 = rng.choice([-1.0, 1.0], size=n_mc)
            s2 = rng.choice([-1.0, 1.0], size=n_mc)
            for j, d in enumerate(d_grid):
                mu = bx * d + bxm * d * (m_s - 0.5)
                p1 = expit(mu + u + a1 + g * s1)
                p2 = expit(mu + u + a2 + g * s2)
                curves[p, j] = (p1 * p2 + (1 - p1) * (1 - p2)).mean()
    return curves


# ---------------------------------------------------------------------------
# 4. Threshold inversion
# ---------------------------------------------------------------------------

def raw_delta_at(x: float | None, m: float) -> float | None:
    """Convert a |Delta logit(p_fit)| gap x, at reference midpoint m, to the
    corresponding raw |Delta p_fit| -- the quantity the spec says to report
    to readers. Solves expit(b) + expit(b+x) = 2m for b (monotone in b),
    then returns expit(b+x) - expit(b).
    """
    if x is None:
        return None
    m = min(max(m, EPS), 1 - EPS)
    if x <= 0:
        return 0.0
    b = brentq(lambda bb: expit(bb) + expit(bb + x) - 2 * m, -50.0, 50.0)
    return float(expit(b + x) - expit(b))


def first_crossing(curve: np.ndarray, d_grid: np.ndarray, target: float) -> float | None:
    above = curve >= target
    if not above.any():
        return None
    return float(d_grid[int(np.argmax(above))])


def thresholds_from_curve(curves: np.ndarray, d_grid: np.ndarray, detect_target: float,
                          d_x_target: float) -> dict:
    mean_curve = curves.mean(axis=0)
    lower = np.quantile(curves, 0.025, axis=0)
    upper = np.quantile(curves, 0.975, axis=0)
    return {
        "d_detect": first_crossing(lower, d_grid, detect_target),
        "d_x_point": first_crossing(mean_curve, d_grid, d_x_target),
        "d_x_ci_lo": first_crossing(upper, d_grid, d_x_target),
        "d_x_ci_hi": first_crossing(lower, d_grid, d_x_target),
        "mean_curve": mean_curve, "lower": lower, "upper": upper,
    }


# ---------------------------------------------------------------------------
# 5. Model-pair comparisons over the full 346-question channel
# ---------------------------------------------------------------------------

def predict_q_signed(x_arr: np.ndarray, m_arr: np.ndarray, sign_arr: np.ndarray,
                      flat: dict, n_mc: int, rng: np.random.Generator) -> np.ndarray:
    """P(prefer A) for each posterior draw x each (question, model-pair)."""
    P, N = len(flat["beta_x"]), len(x_arr)
    out = np.zeros((P, N))
    for p in range(P):
        bx, bxm, g = flat["beta_x"][p], flat["beta_xm"][p], flat["gamma"][p]
        su, sa = flat["sigma_u"][p], flat["sigma_a"][p]
        u = rng.normal(0.0, su, size=n_mc)
        a = rng.normal(0.0, sa, size=n_mc)
        side = rng.choice([-1.0, 1.0], size=n_mc)
        mu = bx * x_arr + bxm * x_arr * (m_arr - 0.5)
        eta = mu[:, None] + u[None, :] + a[None, :] + g * side[None, :]
        q = expit(eta).mean(axis=1)
        out[p] = np.where(sign_arr > 0, q, 1.0 - q)
    return out


def model_pair_comparisons(candidates: dict, flat: dict, n_mc: int,
                           rng: np.random.Generator,
                           qsubset: set[str] | None = None) -> list[dict]:
    labels = sorted(candidates)
    rows = []
    for la, lb in itertools.combinations(labels, 2):
        qnums = set(candidates[la]["p_fit"]) & set(candidates[lb]["p_fit"])
        if qsubset is not None:
            qnums &= qsubset
        qnums = sorted(qnums, key=int)
        if not qnums:
            continue
        pa = np.array([candidates[la]["p_fit"][q] for q in qnums])
        pb = np.array([candidates[lb]["p_fit"][q] for q in qnums])
        pa_c = np.clip(pa, EPS, 1 - EPS)
        pb_c = np.clip(pb, EPS, 1 - EPS)
        x_arr = np.abs(logit(pa_c) - logit(pb_c))
        m_arr = (pa + pb) / 2.0
        d_arr = pa - pb
        sign_arr = np.sign(d_arr)
        sign_arr[sign_arr == 0] = 1.0  # exact ties: arbitrary but consistent

        q_matrix = predict_q_signed(x_arr, m_arr, sign_arr, flat, n_mc, rng)
        w_ab = float(q_matrix.mean())
        n = len(qnums)
        u_draws = rng.random(q_matrix.shape)
        h = (u_draws < q_matrix).astype(int)
        p_majority = float((h.sum(axis=1) > n / 2.0).mean())

        rows.append({
            "candidate_A": la, "candidate_B": lb, "n_questions": n,
            "D_AB_mean_raw_delta": float(d_arr.mean()),
            "W_AB": w_ab, "P_majority_A_preferred": p_majority,
        })
    rows.sort(key=lambda r: r["W_AB"], reverse=True)
    return rows


# ---------------------------------------------------------------------------
# 6. d_346 homogeneous-gap resolution
# ---------------------------------------------------------------------------

def solve_d_346(flat: dict, m_ref: float, n: int, z: float, d_grid: np.ndarray,
                n_mc: int, rng: np.random.Generator) -> dict:
    """Solve for d_346 on the logit-x grid, then convert to the raw |Delta p_fit|
    scale at m_ref -- the spec's d_346 is defined as a raw per-question p_fit
    advantage, not a logit-scale one.
    """
    target = 0.5 + z / (2.0 * np.sqrt(n))
    curves = compute_curve(flat, np.array([m_ref]), d_grid, n_mc, rng, two_rater=False)
    mean_curve = curves.mean(axis=0)
    lower = np.quantile(curves, 0.025, axis=0)
    upper = np.quantile(curves, 0.975, axis=0)
    x_point = first_crossing(mean_curve, d_grid, target)
    x_ci_lo = first_crossing(upper, d_grid, target)
    x_ci_hi = first_crossing(lower, d_grid, target)
    return {
        "target_q": target, "m_ref": m_ref, "n": n,
        "x_346_point": x_point, "x_346_ci_lo": x_ci_lo, "x_346_ci_hi": x_ci_hi,
        "d_346_point": raw_delta_at(x_point, m_ref),
        "d_346_ci_lo": raw_delta_at(x_ci_lo, m_ref),
        "d_346_ci_hi": raw_delta_at(x_ci_hi, m_ref),
    }


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_curves(d_grid, qmh, qhh, empirical_mh, empirical_hh, out_path: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available -- skipping curve plot", file=sys.stderr)
        return

    fig, ax = plt.subplots(figsize=(9, 6), dpi=150)
    for curves, color, label in ((qmh, "#4C78A8", "q_MH(d): human vs. higher-p_fit"),
                                  (qhh, "#E45756", "q_HH(d): human vs. human")):
        mean_c = curves.mean(axis=0)
        lo = np.quantile(curves, 0.025, axis=0)
        hi = np.quantile(curves, 0.975, axis=0)
        ax.plot(d_grid, mean_c, color=color, label=label)
        ax.fill_between(d_grid, lo, hi, color=color, alpha=0.2)

    if empirical_mh:
        xs, ys = zip(*empirical_mh)
        ax.scatter(xs, ys, color="#4C78A8", marker="o", zorder=5, label="empirical q_MH (per stratum)")
    if empirical_hh:
        xs, ys = zip(*empirical_hh)
        ax.scatter(xs, ys, color="#E45756", marker="s", zorder=5, label="empirical q_HH (per stratum)")

    ax.axhline(0.5, color="gray", ls=":", lw=1)
    ax.set_xlabel("d = |Delta logit(p_fit)|")
    ax.set_ylabel("agreement probability")
    ax.set_ylim(0.3, 1.02)
    ax.set_title("Human-model and human-human agreement vs. p_fit gap")
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(
        description="Fit the p_fit human-choice calibration model and propagate it.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--annotated-dir", default=str(DEFAULT_ANNOTATED_DIR))
    p.add_argument("--master", default=None)
    p.add_argument("--scored-glob", default=DEFAULT_SCORED_GLOB)
    p.add_argument("--d75-threshold", type=float, default=0.75)
    p.add_argument("--majority-z", type=float, default=1.96)
    p.add_argument("--n-questions", type=int, nargs="+", default=None,
                   help="Question count(s) N for the homogeneous-gap resolution "
                        "d_N (spec section 6); pass several to solve each. "
                        "Defaults to the --question-subset size if given, else 346.")
    p.add_argument("--question-subset", default=None,
                   help="Path to a file of benchmark question_numbers (whitespace/"
                        "comma separated). Restricts m_ref AND the model-pair "
                        "comparison channel (W_AB, P_majority) to those questions.")
    p.add_argument("--n-draws", type=int, default=200)
    p.add_argument("--mcmc-draws", type=int, default=2000)
    p.add_argument("--mcmc-tune", type=int, default=1000)
    p.add_argument("--target-accept", type=float, default=0.9)
    p.add_argument("--seed", type=int, default=1914)
    p.add_argument("--out-dir", default=None)
    p.add_argument("--save-posterior", default=None,
                   help="Write the retained posterior draws (beta_x, beta_xm, "
                        "gamma, sigma_u, sigma_a) to this .npz so downstream "
                        "tools (pair_confirmation.py) need not refit.")
    args = p.parse_args()

    annotated_dir = Path(args.annotated_dir)
    master_path = Path(args.master) if args.master else annotated_dir / "master_pairs.jsonl"
    out_dir = Path(args.out_dir) if args.out_dir else annotated_dir / "analysis"
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    qsubset: set[str] | None = None
    if args.question_subset:
        raw = Path(args.question_subset).read_text().replace(",", " ").split()
        qsubset = {s.strip() for s in raw if s.strip()}
        print(f"Question subset: {len(qsubset)} question_number(s) from {args.question_subset}")
    n_questions = args.n_questions or ([len(qsubset)] if qsubset else [346])

    print(f"Loading master pairs from {master_path} ...")
    master = load_jsonl(master_path)
    master_by_id = {r["pair_id"]: r for r in master}
    total_per_rater: dict[str, int] = {}
    for row in master:
        for r in row["raters"]:
            total_per_rater[r["rater_id"]] = total_per_rater.get(r["rater_id"], 0) + 1

    print(f"Decoding judgments from {annotated_dir} ...")
    judgments, rater_counts = decode_judgments(master_by_id, annotated_dir)
    print(f"  {len(judgments)} judgment(s) decoded from {len(rater_counts)} rater file(s)")
    for rid, n in sorted(rater_counts.items()):
        print(f"    {rid}: {n}/{total_per_rater.get(rid, '?')}")
    if not judgments:
        raise SystemExit("No judgments decoded -- nothing to fit.")

    print("Fitting hierarchical model in PyMC (this may take a minute)...")
    trace, summary = fit_model(judgments, args.mcmc_draws, args.mcmc_tune, args.seed,
                               args.target_accept)
    (out_dir / "fitted_model_summary.txt").write_text(summary.to_string() + "\n", encoding="utf-8")
    print(summary.to_string())

    flat = get_posterior_arrays(trace, MAX_POSTERIOR_SUBSET, rng)
    if args.save_posterior:
        post_path = Path(args.save_posterior)
        post_path.parent.mkdir(parents=True, exist_ok=True)
        np.savez(post_path, **flat)
        print(f"Saved {len(flat['beta_x'])} posterior draws to {post_path}")
    d_grid = np.linspace(0.0, D_GRID_MAX, D_GRID_N)
    m_pool = np.array([j["m"] for j in judgments])

    print("Computing posterior-predictive q_MH(d) and q_HH(d) curves...")
    qmh = compute_curve(flat, m_pool, d_grid, args.n_draws, rng, two_rater=False)
    qhh = compute_curve(flat, m_pool, d_grid, args.n_draws, rng, two_rater=True)

    thr_mh = thresholds_from_curve(qmh, d_grid, detect_target=0.5, d_x_target=args.d75_threshold)
    median_m = float(np.median(m_pool))

    # Empirical per-stratum overlay points
    empirical_mh = []
    by_stratum_j: dict[int, list[dict]] = {}
    for j in judgments:
        by_stratum_j.setdefault(j["stratum"], []).append(j)
    for s, js in sorted(by_stratum_j.items()):
        empirical_mh.append((float(np.mean([j["x"] for j in js])), float(np.mean([j["y"] for j in js]))))

    pair_rows = pair_agreement_rows(master, judgments)
    empirical_hh = []
    by_stratum_p: dict[int, list[dict]] = {}
    for r in pair_rows:
        by_stratum_p.setdefault(r["stratum"], []).append(r)
    for s, rs in sorted(by_stratum_p.items()):
        empirical_hh.append((float(np.mean([r["x"] for r in rs])), float(np.mean([r["agree"] for r in rs]))))

    plot_curves(d_grid, qmh, qhh, empirical_mh, empirical_hh, out_dir / "qmh_qhh_curve.png")

    raw_detect = raw_delta_at(thr_mh["d_detect"], median_m)
    raw_75 = raw_delta_at(thr_mh["d_x_point"], median_m)
    raw_75_lo = raw_delta_at(thr_mh["d_x_ci_lo"], median_m)
    raw_75_hi = raw_delta_at(thr_mh["d_x_ci_hi"], median_m)
    thresholds_lines = [
        "# Thresholds\n",
        "All raw |Delta p_fit| conversions below are evaluated at the median "
        f"calibration-sample midpoint m={median_m:.4f} (spec section 4: 'Raw Delta "
        "p_fit remains the quantity you report to readers').\n",
        f"- d_detect (lower-95% q_MH crosses 0.5): x={thr_mh['d_detect']} "
        f"(logit scale)  |  raw |Delta p_fit|={raw_detect}",
        f"- d_{args.d75_threshold:.2f} point estimate (mean q_MH crosses {args.d75_threshold}): "
        f"x={thr_mh['d_x_point']} (logit scale)  |  raw |Delta p_fit|={raw_75}",
        f"  95% CI (logit scale): [{thr_mh['d_x_ci_lo']}, {thr_mh['d_x_ci_hi']}]  |  "
        f"raw |Delta p_fit| CI: [{raw_75_lo}, {raw_75_hi}]",
    ]

    print("Loading all scored candidates for model-pair comparisons (spec section 5)...")
    candidates, coverage_lines = load_candidates(
        DEFAULT_SCORED_DIR, args.scored_glob, None, DEFAULT_GENERATED_DIR
    )
    print(f"  {len(candidates)} candidate(s) loaded")

    comparisons = model_pair_comparisons(candidates, flat, args.n_draws, rng, qsubset)
    csv_path = out_dir / "model_pair_comparisons.csv"
    with open(csv_path, "w", encoding="utf-8") as fh:
        fh.write("candidate_A,candidate_B,n_questions,D_AB_mean_raw_delta,W_AB,P_majority_A_preferred\n")
        for r in comparisons:
            fh.write(f"{r['candidate_A']},{r['candidate_B']},{r['n_questions']},"
                     f"{r['D_AB_mean_raw_delta']:.4f},{r['W_AB']:.4f},"
                     f"{r['P_majority_A_preferred']:.4f}\n")
    print(f"  wrote {csv_path} ({len(comparisons)} model pairs)")

    print(f"Solving for d_N at N={n_questions} (spec section 6)...")
    all_m = []
    for la, lb in itertools.combinations(sorted(candidates), 2):
        qnums = set(candidates[la]["p_fit"]) & set(candidates[lb]["p_fit"])
        if qsubset is not None:
            qnums &= qsubset
        for q in qnums:
            all_m.append((candidates[la]["p_fit"][q] + candidates[lb]["p_fit"][q]) / 2.0)
    m_ref = float(np.median(all_m)) if all_m else 0.9
    for n_ref in n_questions:
        dN = solve_d_346(flat, m_ref, n_ref, args.majority_z, d_grid, args.n_draws, rng)
        thresholds_lines.append(
            f"\n- d_{n_ref} (homogeneous per-question raw |Delta p_fit| advantage giving "
            f"{dN['target_q']:.4f} majority-level support over {n_ref} questions, "
            f"at m_ref={m_ref:.4f}): raw |Delta p_fit|={dN['d_346_point']} "
            f"(x={dN['x_346_point']} logit scale)"
        )
        thresholds_lines.append(
            f"  95% CI, raw |Delta p_fit|: [{dN['d_346_ci_lo']}, {dN['d_346_ci_hi']}]  |  "
            f"x (logit scale): [{dN['x_346_ci_lo']}, {dN['x_346_ci_hi']}]"
        )
    (out_dir / "thresholds.md").write_text("\n".join(thresholds_lines) + "\n", encoding="utf-8")
    print("\n".join(thresholds_lines))

    report_lines = ["# Human validation of p_fit -- analysis report\n"]
    report_lines.append("## Data\n")
    report_lines.append(f"- {len(judgments)} judgments decoded from {len(rater_counts)} rater file(s):")
    for rid, n in sorted(rater_counts.items()):
        report_lines.append(f"  - {rid}: {n}/{total_per_rater.get(rid, '?')}")
    report_lines.append("")
    report_lines.append("## Fitted model\n")
    report_lines.append("```\n" + summary.to_string() + "\n```\n")
    report_lines.append("## Thresholds\n")
    report_lines.extend(thresholds_lines[1:])
    _channel = (f"question subset from {Path(args.question_subset).name}"
                if qsubset else "full benchmark channel")
    report_lines.append(f"\n## Model-pair comparisons ({_channel})\n")
    report_lines.append("| A | B | n | D_AB | W_AB | P(majority prefers A) |")
    report_lines.append("|---|---|---|------|------|------------------------|")
    for r in comparisons:
        report_lines.append(
            f"| {r['candidate_A']} | {r['candidate_B']} | {r['n_questions']} | "
            f"{r['D_AB_mean_raw_delta']:.4f} | {r['W_AB']:.4f} | "
            f"{r['P_majority_A_preferred']:.4f} |"
        )
    report_lines.append(
        "\nNote: the further empirical step of relating *observed* model-pair score "
        "gaps to their P(majority) across many real comparisons (spec section 6, final "
        "paragraph) is a natural follow-up once several models are compared this way, "
        "and is not computed here -- the table above is exactly what that follow-up "
        "would consume."
    )
    (out_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"\nDone. See {out_dir}/report.md")


if __name__ == "__main__":
    main()

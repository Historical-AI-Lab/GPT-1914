"""
fit_beta_regression_nocontext.py — Hierarchical logistic regression for judge β.

Reads the per-pair GT-vs-GT outcome JSONL produced by
judge_beta_reliability_nocontext.py, fits a PyMC hierarchical logistic regression
to estimate how the per-trial tie-miss probability (2β) depends on ground-truth
answer length and question frame_type, then post-stratifies the fitted model over
every question in the main benchmark to produce per-question 2β estimates.

Model
-----
logit(p[i]) = b0 + u_frame[frame_idx[i]] + b_len * z_loglen[i]
k[i]        ~ Binomial(n_valid_trials[i], p[i])

where p[i] is the per-trial probability of declaring a winner on a GT-vs-GT pair
(i.e. p = 2β under position symmetry) and z_loglen is standardized
log(original-GT character length).  u_frame is a fixed weakly-informative
intercept per frame_type (world_context / book_context / passage_context) with
prior u_frame ~ Normal(0, 0.5) — a regularizing prior that shrinks frame offsets
toward the global mean without estimating a between-group variance (partial pooling
buys little with only 3 groups and introduces funnel geometry).

Post-stratification
-------------------
For every benchmark question, the posterior draws of
  two_beta_q = sigmoid(b0 + u_frame[frame[q]] + b_len * z[q])
give a per-question 2β distribution.  β_q = two_beta_q / 2.  Population β is
the mean over all questions per posterior draw, summarized as mean + CI.

Usage
-----
  python fit_beta_regression_nocontext.py PAIRS_JSONL [options]

  PAIRS_JSONL                   Per-pair JSONL from judge_beta_reliability_nocontext.py

  --benchmark PATH              Main benchmark JSONL for post-stratification
                                (default: ../booksample/chronologic_en_0.3.jsonl)
  --output PATH                 Output JSON; default:
                                beta_reliability/beta_regression_{judge}__{version}.json
  --draws INT                   MCMC draws per chain (default: 2000)
  --tune  INT                   Tuning steps (default: 1000)
  --chains INT                  MCMC chains (default: 4)
  --target-accept FLOAT         (default: 0.9)
  --seed INT                    (default: 17)
  --dry-run                     Print data summaries; no sampling

Output
------
beta_reliability/beta_regression_{judge}__{version}.json:
{
  "judge_model": "...",
  "benchmark_version": "0.3",
  "reasoning_effort": "none",
  "sources": {"main": 16, "alt": 68},
  "raw_counts": {"n_pairs":84,"n_trials":168,"k_nontie":47,"invalid":0,"k_A":24,"k_B":23},
  "standardization": {"mu_loglen": 2.9, "sd_loglen": 0.8},
  "population": {
    "two_beta_mean": 0.26, "two_beta_ci": [0.20, 0.34], "beta_mean": 0.13
  },
  "by_frame_type": {
    "world_context":   {"two_beta_mean":0.22,"two_beta_ci":[0.14,0.31],"beta_mean":0.11},
    "book_context":    {"two_beta_mean":0.29,"two_beta_ci":[0.18,0.43],"beta_mean":0.15},
    "passage_context": {"two_beta_mean":0.27,"two_beta_ci":[0.18,0.39],"beta_mean":0.14}
  },
  "coefficients": {
    "b0":          {"mean":-1.2,"ci":[-1.8,-0.6]},
    "b_len":       {"mean": 0.3,"ci":[ 0.0, 0.6]},
    "u_frame": {
      "world_context":   {"mean":-0.1,"ci":[-0.4,0.2]},
      "book_context":    {"mean": 0.1,"ci":[-0.2,0.4]},
      "passage_context": {"mean": 0.0,"ci":[-0.3,0.3]}
    }
  },
  "per_question": {
    "7": {
      "two_beta_mean":0.22,"two_beta_ci":[0.14,0.32],"beta_mean":0.11,
      "frame_type":"world_context","gt_len":17,
      "n_trials":2,"k_nontie":1,
      "two_beta_beta_dist":{"alpha":4.1,"beta":11.6}
    }
  },
  "position_symmetry": {"k_A":24,"k_B":23,"binomial_p":1.0},
  "diagnostics": {"n_divergent":0,"min_ess":1250,"max_rhat":1.003}
}

per_question covers ALL benchmark questions (post-stratified generalization).
n_trials / k_nontie are filled for questions that contributed GT-vs-GT pairs;
null for prediction-only questions.
two_beta_beta_dist gives a moment-matched Beta(alpha,beta) for downstream
uncertainty propagation.

Examples
--------
  python fit_beta_regression_nocontext.py \\
      beta_reliability/gt_pairs_anthropic_claude-opus-4-7__0.3.jsonl

  python fit_beta_regression_nocontext.py PAIRS.jsonl --dry-run

  python fit_beta_regression_nocontext.py PAIRS.jsonl --draws 4000 --target-accept 0.95
"""

import json
import math
import sys
import argparse
from collections import defaultdict
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).parent
BETA_RELIABILITY_DIR = SCRIPT_DIR / "beta_reliability"
DEFAULT_BENCHMARK = SCRIPT_DIR.parent / "booksample" / "chronologic_en_0.3.jsonl"

FRAME_TYPES = ["world_context", "book_context", "passage_context"]
_FRAME_IDX = {f: i for i, f in enumerate(FRAME_TYPES)}

_REASONING_TO_FRAME = {
    "knowledge":             "world_context",
    "refusal":               "world_context",
    "inference":             "world_context",
    "character_modeling":    "book_context",
    "constrained_generation":"book_context",
    "topic_sentence":        "book_context",
    "phrase_cloze":          "passage_context",
    "sentence_cloze":        "passage_context",
}


def _infer_frame_type(reasoning_type):
    return _REASONING_TO_FRAME.get(reasoning_type, "")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_pairs(path):
    """Load per-pair JSONL; return list of record dicts."""
    records = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def load_benchmark(path):
    """Load main benchmark JSONL; return list of question records."""
    records = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


# ---------------------------------------------------------------------------
# Data preparation
# ---------------------------------------------------------------------------

def prepare_data(pair_records, benchmark_records):
    """Build arrays for the PyMC model and post-stratification.

    Returns a dict with:
      Fitting arrays (pairs with n_valid_trials > 0 and known frame_type):
        n[i], k[i], frame_idx[i], z_loglen[i]

      Population arrays (all benchmark questions with known frame_type):
        pop_qnums, pop_frame_idxs, pop_z_loglen, pop_gt_len

      Standardization constants (computed from population):
        mu_loglen, sd_loglen

      Per-question pair lookup:
        pair_by_qnum: {qnum -> list[pair_record]}

      Summary fields:
        raw_counts, sources, judge_model, reasoning_effort, benchmark_version
    """
    # --- Population log-length for standardization ---
    pop_lens_all = []
    for q in benchmark_records:
        strings = q.get("answer_strings") or []
        gt_len = max(len(strings[0]), 1) if strings else 1
        pop_lens_all.append(gt_len)

    pop_loglen_all = np.log(np.array(pop_lens_all, dtype=float))
    mu_loglen = float(np.mean(pop_loglen_all))
    sd_loglen  = float(np.std(pop_loglen_all))
    if sd_loglen == 0.0:
        sd_loglen = 1.0

    # --- Fitting arrays from pairs ---
    n_arr, k_arr, frame_arr, z_arr = [], [], [], []
    pair_by_qnum = defaultdict(list)
    skipped_frame = 0

    for rec in pair_records:
        pair_by_qnum[str(rec["question_number"])].append(rec)
        if rec.get("n_valid_trials", 0) == 0:
            continue
        frame = rec.get("frame_type") or _infer_frame_type(rec.get("reasoning_type", ""))
        if frame not in _FRAME_IDX:
            skipped_frame += 1
            continue
        n_arr.append(rec["n_valid_trials"])
        k_arr.append(rec["k_nontie"])
        frame_arr.append(_FRAME_IDX[frame])
        log_len = math.log(max(rec["orig_len"], 1))
        z_arr.append((log_len - mu_loglen) / sd_loglen)

    if skipped_frame:
        print(f"  [warning] {skipped_frame} pairs skipped: unknown frame_type.")

    # --- Population arrays for post-stratification ---
    pop_qnums, pop_frame_idxs, pop_z_loglen, pop_gt_len = [], [], [], []
    for q in benchmark_records:
        qnum = str(q.get("question_number", ""))
        if not qnum:
            continue
        frame = q.get("frame_type") or _infer_frame_type(q.get("reasoning_type", ""))
        if frame not in _FRAME_IDX:
            continue
        strings = q.get("answer_strings") or []
        gt_len = max(len(strings[0]), 1) if strings else 1
        log_len = math.log(gt_len)
        z = (log_len - mu_loglen) / sd_loglen
        pop_qnums.append(qnum)
        pop_frame_idxs.append(_FRAME_IDX[frame])
        pop_z_loglen.append(z)
        pop_gt_len.append(gt_len)

    # --- Raw counts ---
    n_trials_total = sum(r.get("n_valid_trials", 0) for r in pair_records)
    k_nontie_total = sum(r.get("k_nontie", 0) for r in pair_records)
    invalid_total  = sum(r.get("invalid", 0) for r in pair_records)
    k_A_total      = sum(r.get("k_A", 0) for r in pair_records)
    k_B_total      = sum(r.get("k_B", 0) for r in pair_records)
    n_main = sum(1 for r in pair_records if r.get("source") == "main")
    n_alt  = sum(1 for r in pair_records if r.get("source") == "alt")

    meta = pair_records[0] if pair_records else {}

    return {
        "n":             np.array(n_arr, dtype=int),
        "k":             np.array(k_arr, dtype=int),
        "frame_idx":     np.array(frame_arr, dtype=int),
        "z_loglen":      np.array(z_arr, dtype=float),
        "pop_qnums":     pop_qnums,
        "pop_frame_idxs":np.array(pop_frame_idxs, dtype=int),
        "pop_z_loglen":  np.array(pop_z_loglen, dtype=float),
        "pop_gt_len":    pop_gt_len,
        "mu_loglen":     mu_loglen,
        "sd_loglen":     sd_loglen,
        "pair_by_qnum":  dict(pair_by_qnum),
        "raw_counts": {
            "n_pairs":   len(pair_records),
            "n_trials":  n_trials_total,
            "k_nontie":  k_nontie_total,
            "invalid":   invalid_total,
            "k_A":       k_A_total,
            "k_B":       k_B_total,
        },
        "sources":          {"main": n_main, "alt": n_alt},
        "judge_model":      meta.get("judge_model", ""),
        "reasoning_effort": meta.get("reasoning_effort", ""),
        "benchmark_version":meta.get("benchmark_version", ""),
    }


def print_data_summary(data):
    """Print a human-readable summary of the prepared data."""
    rc = data["raw_counts"]
    print(f"\nPair data:")
    print(f"  {rc['n_pairs']} pairs  |  {rc['n_trials']} valid trials  |  "
          f"{rc['k_nontie']} non-tie  |  {rc['invalid']} invalid")
    print(f"  sources: {data['sources']}")
    n_fit = len(data["n"])
    print(f"  pairs used in regression (n_valid>0, known frame): {n_fit}")
    if n_fit:
        from collections import Counter
        fc = Counter(FRAME_TYPES[i] for i in data["frame_idx"])
        print(f"  frame_type in fitting set: {dict(fc)}")
    print(f"\nPopulation: {len(data['pop_qnums'])} questions")
    from collections import Counter
    pc = Counter(FRAME_TYPES[i] for i in data["pop_frame_idxs"])
    print(f"  frame_type distribution: {dict(pc)}")
    print(f"\nLog-length standardization (population):")
    print(f"  mu_loglen={data['mu_loglen']:.3f}  sd_loglen={data['sd_loglen']:.3f}")
    print(f"  gt_len range (fitting pairs): "
          f"[{min((r['orig_len'] for r in data.get('_raw_records', [])), default=0)}, "
          f"{max((r['orig_len'] for r in data.get('_raw_records', [])), default=0)}]"
          if data.get("_raw_records") else "")


# ---------------------------------------------------------------------------
# PyMC model
# ---------------------------------------------------------------------------

def fit_model(data, draws=2000, tune=1000, chains=4, target_accept=0.9, seed=17):
    """Fit the hierarchical logistic regression; return the ArviZ InferenceData trace."""
    import pymc as pm

    n          = data["n"]
    k          = data["k"]
    frame_idx  = data["frame_idx"]
    z          = data["z_loglen"]
    n_frames   = len(FRAME_TYPES)

    with pm.Model(coords={"frame": FRAME_TYPES}) as model:  # noqa: F841
        b0 = pm.Normal("b0", mu=0, sigma=1.5)

        u_frame = pm.Normal("u_frame", mu=0, sigma=0.5, shape=n_frames)

        b_len = pm.Normal("b_len", mu=0, sigma=1.0)

        logit_p = b0 + u_frame[frame_idx] + b_len * z
        pm.Binomial("k_obs", n=n, p=pm.math.sigmoid(logit_p), observed=k)

        trace = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            target_accept=target_accept,
            random_seed=seed,
            progressbar=True,
        )

    return trace


# ---------------------------------------------------------------------------
# Post-stratification and output assembly
# ---------------------------------------------------------------------------

def _moment_match_beta(mu, var):
    """Moment-match a Beta(alpha,beta) to mean=mu, variance=var. Returns dict or None."""
    if var <= 0 or mu <= 0 or mu >= 1:
        return None
    c = mu * (1.0 - mu) / var - 1.0
    if c <= 0:
        return None
    return {"alpha": round(mu * c, 3), "beta": round((1.0 - mu) * c, 3)}


def _ci(draws_1d, lo=3.0, hi=97.0):
    """Return [lo-percentile, hi-percentile] rounded to 4dp."""
    return [round(float(np.percentile(draws_1d, lo)), 4),
            round(float(np.percentile(draws_1d, hi)), 4)]


def _summarize_two_beta_draws(draws_1d):
    """Return {two_beta_mean, two_beta_ci, beta_mean} from per-draw 2β values."""
    mean_2b = float(np.mean(draws_1d))
    return {
        "two_beta_mean": round(mean_2b, 4),
        "two_beta_ci":   _ci(draws_1d),
        "beta_mean":     round(mean_2b / 2.0, 4),
    }


def post_stratify(trace, data):
    """Compute per-question 2β and population summaries from posterior draws.

    Returns a dict suitable for JSON serialization with keys:
      population, by_frame_type, per_question, position_symmetry, coefficients.
    """
    from scipy.special import expit  # sigmoid
    from scipy.stats import binomtest

    # Extract flattened posterior draws
    b0_draws     = trace.posterior["b0"].values.flatten()
    b_len_draws  = trace.posterior["b_len"].values.flatten()
    u_frame_draws = trace.posterior["u_frame"].values.reshape(-1, len(FRAME_TYPES))
    n_draws = len(b0_draws)

    pop_frame  = data["pop_frame_idxs"]   # (N_pop,)
    pop_z      = data["pop_z_loglen"]     # (N_pop,)
    pop_qnums  = data["pop_qnums"]
    n_pop      = len(pop_qnums)

    # Per-question 2β draws: shape (n_draws, n_pop)
    two_beta_draws = expit(
        b0_draws[:, None]
        + u_frame_draws[:, pop_frame]          # (n_draws, n_pop)
        + b_len_draws[:, None] * pop_z[None, :]
    )

    # Population: mean over questions per draw, then summarize
    pop_mean_draws = np.mean(two_beta_draws, axis=1)   # (n_draws,)
    population = _summarize_two_beta_draws(pop_mean_draws)

    # By frame_type
    by_frame_type = {}
    for fi, fname in enumerate(FRAME_TYPES):
        mask = (pop_frame == fi)
        if not np.any(mask):
            by_frame_type[fname] = None
            continue
        frame_mean_draws = np.mean(two_beta_draws[:, mask], axis=1)
        by_frame_type[fname] = _summarize_two_beta_draws(frame_mean_draws)

    # Per-question summaries
    per_q_mean   = np.mean(two_beta_draws, axis=0)   # (n_pop,)
    per_q_ci_lo  = np.percentile(two_beta_draws, 3,  axis=0)
    per_q_ci_hi  = np.percentile(two_beta_draws, 97, axis=0)
    per_q_var    = np.var(two_beta_draws, axis=0)

    pair_by_qnum = data["pair_by_qnum"]

    per_question = {}
    for qi, qnum in enumerate(pop_qnums):
        mean_2b = float(per_q_mean[qi])
        ci_2b   = [round(float(per_q_ci_lo[qi]), 4), round(float(per_q_ci_hi[qi]), 4)]

        pairs_q = pair_by_qnum.get(qnum, [])
        if pairs_q:
            n_trials_q = int(sum(p.get("n_valid_trials", 0) for p in pairs_q))
            k_q        = int(sum(p.get("k_nontie", 0) for p in pairs_q))
        else:
            n_trials_q = None
            k_q        = None

        per_question[qnum] = {
            "two_beta_mean":       round(mean_2b, 4),
            "two_beta_ci":         ci_2b,
            "beta_mean":           round(mean_2b / 2.0, 4),
            "frame_type":          FRAME_TYPES[int(pop_frame[qi])],
            "gt_len":              int(data["pop_gt_len"][qi]),
            "n_trials":            n_trials_q,
            "k_nontie":            k_q,
            "two_beta_beta_dist":  _moment_match_beta(mean_2b, float(per_q_var[qi])),
        }

    # Position-symmetry test
    k_A = data["raw_counts"]["k_A"]
    k_B = data["raw_counts"]["k_B"]
    k_total = k_A + k_B
    if k_total > 0:
        sym_p = round(float(binomtest(k_A, k_total, 0.5).pvalue), 4)
    else:
        sym_p = None

    # Coefficient summaries
    def _coef_summary(name):
        vals = trace.posterior[name].values.flatten()
        return {"mean": round(float(np.mean(vals)), 4),
                "ci":  _ci(vals)}

    coeff = {
        "b0":    _coef_summary("b0"),
        "b_len": _coef_summary("b_len"),
        "u_frame": {
            fname: _coef_summary("u_frame")  # overridden below
            for fname in FRAME_TYPES
        },
    }
    # u_frame is shape (n_draws, n_frames); summarize per frame
    u_draws_flat = trace.posterior["u_frame"].values.reshape(-1, len(FRAME_TYPES))
    for fi, fname in enumerate(FRAME_TYPES):
        coeff["u_frame"][fname] = {
            "mean": round(float(np.mean(u_draws_flat[:, fi])), 4),
            "ci":   _ci(u_draws_flat[:, fi]),
        }

    return {
        "population":         population,
        "by_frame_type":      by_frame_type,
        "per_question":       per_question,
        "position_symmetry":  {"k_A": k_A, "k_B": k_B, "binomial_p": sym_p},
        "coefficients":       coeff,
    }


def compute_diagnostics(trace):
    """Return {n_divergent, min_ess, max_rhat} from the trace."""
    import arviz as az

    rhat_ds = az.rhat(trace)
    ess_ds  = az.ess(trace)

    watch_vars = ["b0", "b_len"]
    rhat_vals, ess_vals = [], []
    for v in watch_vars:
        rhat_vals.append(float(np.max(rhat_ds[v].values)))
        ess_vals.append(float(np.min(ess_ds[v].values)))
    # u_frame has shape (n_frames,)
    rhat_vals.append(float(np.max(rhat_ds["u_frame"].values)))
    ess_vals.append(float(np.min(ess_ds["u_frame"].values)))

    n_div = int(trace.sample_stats["diverging"].values.sum())

    return {
        "n_divergent": n_div,
        "min_ess":     round(min(ess_vals)),
        "max_rhat":    round(max(rhat_vals), 4),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Fit hierarchical logistic regression on GT-vs-GT pair outcomes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("pairs_jsonl", metavar="PAIRS_JSONL",
                        help="Per-pair JSONL from judge_beta_reliability_nocontext.py")
    parser.add_argument("--benchmark", metavar="PATH", default=str(DEFAULT_BENCHMARK))
    parser.add_argument("--output", metavar="PATH", default=None)
    parser.add_argument("--draws",   metavar="INT", type=int, default=2000)
    parser.add_argument("--tune",    metavar="INT", type=int, default=1000)
    parser.add_argument("--chains",  metavar="INT", type=int, default=4)
    parser.add_argument("--target-accept", metavar="FLOAT", type=float, default=0.9,
                        dest="target_accept")
    parser.add_argument("--seed",    metavar="INT", type=int, default=17)
    parser.add_argument("--dry-run", action="store_true", dest="dry_run")

    args = parser.parse_args()

    # --- Load data ---
    pairs_path = Path(args.pairs_jsonl)
    if not pairs_path.exists():
        sys.exit(f"ERROR: pairs JSONL not found: {pairs_path}")

    print(f"Loading pairs: {pairs_path}")
    pair_records = load_pairs(pairs_path)
    print(f"  {len(pair_records)} pair records loaded.")

    print(f"Loading benchmark: {args.benchmark}")
    benchmark_records = load_benchmark(args.benchmark)
    print(f"  {len(benchmark_records)} benchmark questions loaded.")

    # --- Prepare ---
    data = prepare_data(pair_records, benchmark_records)
    n_fit = len(data["n"])
    print(f"\nPairs usable for regression (n_valid > 0, known frame_type): {n_fit}")

    if n_fit == 0:
        sys.exit("ERROR: no usable pairs for regression.")

    # Print summary
    rc = data["raw_counts"]
    print(f"Raw counts: {rc['n_pairs']} pairs | {rc['n_trials']} trials | "
          f"{rc['k_nontie']} non-tie | {rc['invalid']} invalid | "
          f"k_A={rc['k_A']} k_B={rc['k_B']}")
    from collections import Counter
    fc = Counter(FRAME_TYPES[i] for i in data["frame_idx"])
    print(f"Frame distribution (fitting): {dict(fc)}")
    pc = Counter(FRAME_TYPES[i] for i in data["pop_frame_idxs"])
    print(f"Frame distribution (population): {dict(pc)}")
    print(f"Standardization: mu_loglen={data['mu_loglen']:.3f}  "
          f"sd_loglen={data['sd_loglen']:.3f}")

    if args.dry_run:
        print("\n-- dry-run: no sampling --")
        return

    # --- Derive output path ---
    judge_model     = data["judge_model"]
    bench_version   = data["benchmark_version"]

    def _sanitize(s):
        return s.replace("/", "_").replace(":", "_").replace(" ", "_")

    output_path = (
        Path(args.output) if args.output
        else BETA_RELIABILITY_DIR / (
            f"beta_regression_{_sanitize(judge_model)}__{bench_version}.json"
        )
    )
    BETA_RELIABILITY_DIR.mkdir(exist_ok=True)

    # --- Fit ---
    print(f"\nFitting PyMC model ({args.chains} chains × {args.draws} draws, "
          f"tune={args.tune})...")
    trace = fit_model(
        data,
        draws=args.draws, tune=args.tune, chains=args.chains,
        target_accept=args.target_accept, seed=args.seed,
    )

    # --- Post-stratify ---
    print("Post-stratifying over benchmark population...")
    results = post_stratify(trace, data)

    # --- Diagnostics ---
    diagnostics = compute_diagnostics(trace)
    print(f"\nDiagnostics: n_divergent={diagnostics['n_divergent']}  "
          f"min_ess={diagnostics['min_ess']}  max_rhat={diagnostics['max_rhat']}")
    if diagnostics["n_divergent"] > 0:
        print("  [warning] Divergences detected. Consider raising --target-accept.")
    if diagnostics["max_rhat"] > 1.01:
        print("  [warning] R-hat > 1.01. Consider more tuning or --draws.")

    # --- Assemble output ---
    output = {
        "judge_model":      judge_model,
        "benchmark_version":bench_version,
        "reasoning_effort": data["reasoning_effort"],
        "sources":          data["sources"],
        "raw_counts":       data["raw_counts"],
        "standardization":  {
            "mu_loglen": round(data["mu_loglen"], 4),
            "sd_loglen":  round(data["sd_loglen"], 4),
        },
        **results,
        "diagnostics": diagnostics,
    }

    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"\nOutput: {output_path.resolve()}")

    # Human-readable summary
    pop = results["population"]
    print(f"\nPopulation β: {pop['beta_mean']} (2β={pop['two_beta_mean']}, "
          f"CI=[{pop['two_beta_ci'][0]}, {pop['two_beta_ci'][1]}])")
    print("By frame_type:")
    for fname, v in results["by_frame_type"].items():
        if v:
            print(f"  {fname:20s}  β={v['beta_mean']}  (2β CI {v['two_beta_ci']})")
    print(f"\n{len(results['per_question'])} questions have per-question 2β estimates.")


if __name__ == "__main__":
    main()

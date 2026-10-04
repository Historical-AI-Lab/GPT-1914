#!/usr/bin/env python3
"""pair_confirmation.py — model-pair discriminative power on the congen BT channel.

For every pair of candidates scored under benchmark 0.8, ask two questions about
the constrained_generation group (reasoning_type constrained_generation or
character_modeling):

  P_confirm  Simulating one human reader per question, how often does the
             readers' majority agree with the direction of the models'
             difference in mean p_fit?  This is a SIGN TEST on W_AB: it asks
             whether W_AB > 0.5, not by how much, and it climbs toward 1 with
             the question count for any W_AB != 0.5.

  W_AB       Pick one question at random, pick one reader at random, show them
             both answers blind: the probability that reader picks A's answer.
             A rate -- the question count is nowhere in its definition.  This is
             the effect size, and it is reported with a 95% interval covering
             both posterior uncertainty in the fitted human-agreement curve and
             resampling of the questions.

From the 78 pairs the script reports two thresholds, each the largest observed
score gap |D_AB| that FAILS its test:

  x_majority   fails when P_confirm < the confirmation level (default 0.95).
               Drifts with N as ~1/sqrt(N); quote it with N stamped on it.
  x_W          fails when the 95% interval on W_AB still contains 0.5.
               Declines with N only to a floor set by curve-posterior width.

The human-agreement curve comes from analyze_human_eval.py's hierarchical fit:

  logit w = beta_x*x + beta_xm*x*(m - 0.5) + u + a + gamma*side
  x = |logit p_A - logit p_B|,  m = (p_A + p_B)/2,  u ~ N(0, sigma_u),
  a ~ N(0, sigma_a), side ~ +-1.

Run analyze_human_eval.py --save-posterior first to produce the .npz this reads.

Per-question p_fit is RECOMPUTED under the 0.8 calibration from the persisted
Delta draws rather than read from the scored files: five candidates carry 319
stale 0.7-tagged per-question p_fit values (see 0.7_to_0.8_pipeline.py's header).
--stored-pfit restores the old behavior for diffing against earlier output.

Usage:
  cd modelasjudge/humeval_bt
  ~/Dropbox/python/py310hf/bin/python3 pair_confirmation.py \
      --posterior round1results/posterior_flat.npz --confirm-level 0.90 0.95 0.99
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np
from scipy.special import expit, logit
from scipy.stats import binomtest

SCRIPT_DIR = Path(__file__).resolve().parent
MODELASJUDGE_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(MODELASJUDGE_DIR))
sys.path.insert(0, str(SCRIPT_DIR))

from sample_pairs import DEFAULT_SCORED_DIR, DEFAULT_SCORED_GLOB  # noqa: E402
from substantive import artifacts as sub_artifacts  # noqa: E402
from bt import artifacts as bt_artifacts  # noqa: E402
from bt.calibrate import calibration_coefficients  # noqa: E402

DEFAULT_SUBSET = SCRIPT_DIR / "round1results" / "generation_subset_qnums.txt"
DEFAULT_OUT_DIR = SCRIPT_DIR / "round1results" / "pair_confirmation"
DEFAULT_LEDGER = MODELASJUDGE_DIR / "results" / "chronologic_scores.csv"
BT_TAG_08 = "anthropic_claude-sonnet-5__0.8__j-medium__pm-rationales"
EPS = 1e-6
NEAR_TIE = 0.01   # |p_fit gap| below which a question's winner is draw-subsample noise
N_MC_NUISANCE = 4000   # draws used to marginalize u, a, side into q_i


# ---------------------------------------------------------------------------
# 1. Candidates and per-question p_fit
# ---------------------------------------------------------------------------

def load_candidate_pfit(scored_dir: Path, scored_glob: str, use_stored: bool,
                        bt_tag: str) -> tuple[dict, list[str]]:
    """{label: {qnum: p_fit}} plus provenance lines.

    Auto-verdict questions (p_fit pinned to exactly 0.0 or 1.0) are excluded,
    matching analyze_human_eval.py's `0 < p < 1` filter, and counted per
    candidate so the drop is visible rather than silent.
    """
    files = sorted(scored_dir.glob(scored_glob))
    if not files:
        raise SystemExit(f"No scored_answers files matched {scored_glob!r} in {scored_dir}")

    calib = None
    if not use_stored:
        calib_path = bt_artifacts.calibration_path(bt_tag)
        if not calib_path.exists():
            raise SystemExit(f"Calibration artifact not found: {calib_path}")
        calib = json.loads(calib_path.read_text(encoding="utf-8"))
        intercept, slope = calibration_coefficients(calib)

    out: dict[str, dict] = {}
    lines = ["candidate_label | effort | n_pfit | n_auto_dropped | source"]
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        label = data.get("candidate_label") or f.stem
        effort = data.get("candidate_reasoning_effort") or "none"
        context_fit = data.get("context_fit", {})

        stored, n_auto = {}, 0
        for qnum, entry in context_fit.items():
            p = (entry.get("bt") or {}).get("p_fit")
            if p is None:
                continue
            if not (0.0 < float(p) < 1.0):
                n_auto += 1
                continue
            stored[qnum] = float(p)

        if use_stored:
            out[label] = stored
            lines.append(f"{label} | {effort} | {len(stored)} | {n_auto} | stored (may be 0.7-tagged)")
            continue

        # Recompute from the 0.8 Delta draws.
        dpath = sub_artifacts.delta_draws_path(bt_tag, label, effort)
        if not dpath.exists():
            raise SystemExit(f"Delta draws not found for {label!r} (effort {effort}): {dpath}")
        arrays, _meta = sub_artifacts.load_npz(dpath)
        recomputed = {}
        for qnum in stored:
            key = f"delta__{qnum}"
            if key not in arrays:
                continue
            draws = np.asarray(arrays[key], dtype=float)
            if not np.isfinite(draws).all():
                # all-NaN sentinel row: an auto-verdict question
                n_auto += 1
                continue
            recomputed[qnum] = float(expit(intercept + slope * draws).mean())
        out[label] = recomputed
        lines.append(f"{label} | {effort} | {len(recomputed)} | {n_auto} | recomputed at 0.8 from {dpath.name}")

    return out, lines


def load_ledger_scores(path: Path) -> dict[str, float]:
    """{label: grp_congen_score} from the 0.8 / direct_binary_v1 ledger rows.

    This is the number a reader looks up to compare two models, and it is NOT
    the mean of the per-question p_fit values this analysis differences.  Two
    reasons, both worth stating wherever the two are shown together:

      Jensen   the ledger computes expit(mean cal * mean Delta)
               (substantive/estimator.py:73) while p_fit is the mean of the
               sigmoid.  The gap is widest for models near the ends of the
               scale, where the sigmoid curves most.
      subset   the ledger scores all 273 group questions; this analysis drops
               auto-verdict questions whose p_fit is pinned to exactly 0 or 1,
               which is most of the difference for weak models.
    """
    import csv
    scores: dict[str, float] = {}
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("benchmark_version") != "0.8":
                continue
            if row.get("scoring_version") != "direct_binary_v1":
                continue
            if not row.get("grp_congen_score"):
                continue
            label = row["candidate_label"]
            if label in scores:
                raise SystemExit(
                    f"Duplicate 0.8/direct_binary_v1 ledger row for {label!r} in {path}")
            scores[label] = float(row["grp_congen_score"])
    if not scores:
        raise SystemExit(f"No 0.8 / direct_binary_v1 rows with grp_congen_score in {path}")
    return scores


def read_subset(path: Path | None) -> set[str] | None:
    if path is None:
        return None
    raw = Path(path).read_text(encoding="utf-8").replace(",", " ").split()
    return {s.strip() for s in raw if s.strip()}


# ---------------------------------------------------------------------------
# 2. The human-agreement curve
# ---------------------------------------------------------------------------

def nuisance_averaged_q(x: np.ndarray, m: np.ndarray, sign: np.ndarray,
                        bx: float, bxm: float, g: float, su: float, sa: float,
                        n_mc: int, rng: np.random.Generator) -> np.ndarray:
    """P(a reader picks A's answer) per question, for ONE posterior draw.

    The nuisance terms u, a and side are marginalized out here rather than
    carried as a single draw into the caller.  For the Bernoulli vote either
    would do -- Bernoulli(expit(eta)) with one nuisance draw is marginally
    identical to Bernoulli(q).  For the W_AB percentiles it matters: with
    sigma_u ~ 1.14 a single-draw w carries large per-question variance, which
    would widen the reported interval with pure Monte Carlo noise and inflate
    x_W.  Mirrors predict_q_signed() in analyze_human_eval.py.
    """
    u = rng.normal(0.0, su, size=n_mc)
    a = rng.normal(0.0, sa, size=n_mc)
    side = rng.choice([-1.0, 1.0], size=n_mc)
    mu = bx * x + bxm * x * (m - 0.5)
    q = expit(mu[:, None] + u[None, :] + a[None, :] + g * side[None, :]).mean(axis=1)
    return np.where(sign > 0, q, 1.0 - q)


# ---------------------------------------------------------------------------
# 3. One model pair
# ---------------------------------------------------------------------------

def compare_pair(pa: np.ndarray, pb: np.ndarray, post: dict, replications: int,
                 bootstrap_questions: bool, n_mc: int, d_ledger: float | None,
                 rng: np.random.Generator) -> dict:
    n = len(pa)
    pa_c = np.clip(pa, EPS, 1 - EPS)
    pb_c = np.clip(pb, EPS, 1 - EPS)
    x = np.abs(logit(pa_c) - logit(pb_c))
    m = (pa + pb) / 2.0
    d = pa - pb
    sign = np.sign(d)
    sign[sign == 0] = 1.0   # exact ties: q lands at 0.5 either way, so the
                            # orientation is arbitrary but must be consistent

    # Reference direction: the observed, full-subset leaderboard verdict.
    # Held fixed across replications -- recomputing it per replicate would ask a
    # different and circular question.
    D_AB = float(d.mean())
    # Anchored to the LEDGER gap when available: the claim being tested is that
    # readers endorse the leaderboard verdict, and grp_congen_score is the
    # leaderboard.  D_AB (this subset's mean p_fit gap) is kept as a diagnostic;
    # the two can only disagree in sign on near-tie pairs, which fail every test
    # anyway, but the disagreement is flagged rather than absorbed.
    D_ref = D_AB if d_ledger is None else d_ledger
    S = 1.0 if D_ref >= 0 else -1.0

    n_post = len(post["beta_x"])
    idx = rng.integers(0, n_post, size=replications)

    confirms = np.empty(replications, dtype=bool)
    w_means = np.empty(replications)
    q_accum = np.zeros(n)

    for r in range(replications):
        p = idx[r]
        q = nuisance_averaged_q(x, m, sign,
                                post["beta_x"][p], post["beta_xm"][p],
                                post["gamma"][p], post["sigma_u"][p],
                                post["sigma_a"][p], n_mc, rng)
        q_accum += q
        if bootstrap_questions:
            take = rng.integers(0, n, size=n)
            q_r = q[take]
        else:
            q_r = q
        w_means[r] = q_r.mean()
        votes_A = int((rng.random(n) < q_r).sum())
        margin = votes_A - n / 2.0
        confirms[r] = (margin > 0) if S > 0 else (margin < 0)

    q_bar = q_accum / replications
    wins_a = int((d > 0).sum())
    wins_b = int((d < 0).sum())
    ties = int((d == 0).sum())
    # Questions whose gap is inside the noise floor of the persisted Delta
    # draws.  bt_context_scoring.py thins to 1000 float32 draws per question
    # before saving, which costs ~0.003 of p_fit per model; a pair with many
    # questions below that has a win count driven by the draw subsample rather
    # than by the models.  See "Win counts are unstable for near-tied pairs".
    near = int((np.abs(d) < NEAR_TIE).sum())
    binom_p = (binomtest(wins_a, wins_a + wins_b, 0.5).pvalue
               if (wins_a + wins_b) > 0 else float("nan"))

    return {
        "n_questions": n,
        "D_AB": D_AB,
        "D_AB_ledger": float("nan") if d_ledger is None else float(d_ledger),
        "sign_disagree": int(d_ledger is not None and np.sign(D_AB) != np.sign(d_ledger)),
        "n_wins_A": wins_a, "n_wins_B": wins_b, "n_ties": ties,
        "n_near_ties": near,
        "wins_binom_p": float(binom_p),
        "W_AB": float(q_bar.mean()),
        "W_lo": float(np.quantile(w_means, 0.025)),
        "W_hi": float(np.quantile(w_means, 0.975)),
        "P_confirm": float(confirms.mean()),
        # diagnostics used by the verification steps in the plan
        "q_on_A_wins": float(q_bar[d > 0].mean()) if wins_a else float("nan"),
        "q_on_B_wins": float(q_bar[d < 0].mean()) if wins_b else float("nan"),
    }


# ---------------------------------------------------------------------------
# 4. Thresholds
# ---------------------------------------------------------------------------

def x_majority(rows: list[dict], level: float, axis: str = "D_AB") -> tuple[float | None, int]:
    """Largest gap on `axis` among pairs whose P_confirm falls short of `level`."""
    failing = [abs(r[axis]) for r in rows
               if r["P_confirm"] < level and not np.isnan(r[axis])]
    return (max(failing) if failing else None), len(failing)


def x_w(rows: list[dict], axis: str = "D_AB") -> tuple[float | None, int]:
    """Largest gap on `axis` among pairs whose 95% W_AB interval contains 0.5."""
    failing = [abs(r[axis]) for r in rows
               if r["W_lo"] <= 0.5 <= r["W_hi"] and not np.isnan(r[axis])]
    return (max(failing) if failing else None), len(failing)


# ---------------------------------------------------------------------------
# 5. Main
# ---------------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--posterior", required=True,
                   help="npz written by analyze_human_eval.py --save-posterior")
    p.add_argument("--question-subset", default=str(DEFAULT_SUBSET),
                   help="File of benchmark question_numbers; 'none' for all questions.")
    p.add_argument("--replications", type=int, default=1000)
    p.add_argument("--confirm-level", type=float, nargs="+", default=[0.95])
    p.add_argument("--n-questions", type=int, default=None,
                   help="Resample to this many questions per replication instead "
                        "of the subset size (N-sensitivity check). Implies bootstrap.")
    p.add_argument("--no-bootstrap-questions", action="store_true",
                   help="Hold the question set fixed, reproducing "
                        "analyze_human_eval.py's model_pair_comparisons().")
    p.add_argument("--stored-pfit", action="store_true",
                   help="Read p_fit from the scored JSON instead of recomputing "
                        "it under the 0.8 calibration.")
    p.add_argument("--scored-dir", default=str(DEFAULT_SCORED_DIR))
    p.add_argument("--scored-glob", default=DEFAULT_SCORED_GLOB)
    p.add_argument("--bt-tag", default=BT_TAG_08)
    p.add_argument("--n-mc", type=int, default=N_MC_NUISANCE)
    p.add_argument("--ledger", default=str(DEFAULT_LEDGER),
                   help="chronologic_scores.csv, for grp_congen_score gaps; "
                        "'none' to use this subset's mean p_fit gap instead.")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--seed", type=int, default=20260901)
    args = p.parse_args()

    rng = np.random.default_rng(args.seed)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    post = dict(np.load(args.posterior))
    missing = {"beta_x", "beta_xm", "gamma", "sigma_u", "sigma_a"} - set(post)
    if missing:
        raise SystemExit(f"Posterior npz is missing {sorted(missing)}")
    print(f"Loaded {len(post['beta_x'])} posterior draws from {args.posterior}")

    subset_path = None if args.question_subset.lower() == "none" else Path(args.question_subset)
    qsubset = read_subset(subset_path)
    if qsubset:
        print(f"Question subset: {len(qsubset)} question_number(s) from {subset_path}")

    ledger = None
    if args.ledger.lower() != "none":
        ledger = load_ledger_scores(Path(args.ledger))
        print(f"Ledger: grp_congen_score for {len(ledger)} candidates from {args.ledger}")

    cands, prov = load_candidate_pfit(Path(args.scored_dir), args.scored_glob,
                                      args.stored_pfit, args.bt_tag)
    print("\n".join(prov))
    print(f"{len(cands)} candidates loaded")

    bootstrap = not args.no_bootstrap_questions
    if args.n_questions and not bootstrap:
        raise SystemExit("--n-questions requires bootstrapping; drop --no-bootstrap-questions")

    rows = []
    for la, lb in itertools.combinations(sorted(cands), 2):
        qnums = set(cands[la]) & set(cands[lb])
        if qsubset is not None:
            qnums &= qsubset
        qnums = sorted(qnums, key=int)
        if not qnums:
            continue
        pa = np.array([cands[la][q] for q in qnums])
        pb = np.array([cands[lb][q] for q in qnums])
        if args.n_questions:
            take = rng.integers(0, len(qnums), size=args.n_questions)
            pa, pb = pa[take], pb[take]
        d_led = None
        if ledger is not None:
            if la not in ledger or lb not in ledger:
                raise SystemExit(f"No 0.8 ledger row for {la!r} or {lb!r}; "
                                 f"pass --ledger none to skip the ledger axis")
            d_led = ledger[la] - ledger[lb]
        res = compare_pair(pa, pb, post, args.replications, bootstrap,
                           args.n_mc, d_led, rng)
        res["candidate_A"], res["candidate_B"] = la, lb
        rows.append(res)
        print(f"  {la} vs {lb}: n={res['n_questions']} D={res['D_AB']:+.4f} "
              f"W={res['W_AB']:.4f} [{res['W_lo']:.3f},{res['W_hi']:.3f}] "
              f"P={res['P_confirm']:.3f} wins {res['n_wins_A']}-{res['n_wins_B']}")

    sort_axis = "D_AB_ledger" if ledger is not None else "D_AB"
    rows.sort(key=lambda r: abs(r[sort_axis]), reverse=True)

    cols = ["candidate_A", "candidate_B", "n_questions", "D_AB", "D_AB_ledger",
            "sign_disagree", "n_wins_A",
            "n_wins_B", "n_ties", "n_near_ties", "wins_binom_p", "W_AB", "W_lo", "W_hi",
            "P_confirm", "q_on_A_wins", "q_on_B_wins"]
    csv_path = out_dir / "pair_confirmation.csv"
    with open(csv_path, "w", encoding="utf-8") as fh:
        fh.write(",".join(cols) + "\n")
        for r in rows:
            fh.write(",".join(
                f"{r[c]:.4f}" if isinstance(r[c], float) else str(r[c])
                for c in cols) + "\n")
    print(f"\nWrote {csv_path}")

    # ---- report -----------------------------------------------------------
    n_eff = args.n_questions or (rows[0]["n_questions"] if rows else 0)
    L = []
    L.append("# Pair-level discriminative power, constrained_generation channel\n")
    L.append(f"- {len(rows)} model pairs, ~{n_eff} questions each")
    L.append(f"- {args.replications} replications; questions "
             f"{'resampled with replacement' if bootstrap else 'held fixed'}")
    L.append(f"- p_fit {'read from scored JSON (may be 0.7-tagged)' if args.stored_pfit else 'recomputed under the 0.8 calibration'}")
    L.append(f"- seed {args.seed}\n")

    L.append("## Thresholds\n")
    L.append("Each is the largest observed score gap that FAILS its test; every "
             "pair above it passes. Reported on two axes, because they are not "
             "the same number -- see *Two score axes* below.\n")
    axes = [("D_AB_ledger", "ledger `grp_congen_score` gap"),
            ("D_AB", "subset mean p_fit gap")] if ledger is not None else \
           [("D_AB", "subset mean p_fit gap")]
    L.append("| threshold | test | " + " | ".join(lbl for _, lbl in axes) + " | pairs failing |")
    L.append("|--|--|" + "--:|" * (len(axes) + 1))
    for lev in args.confirm_level:
        vals = []
        for ax, _ in axes:
            xm, nm = x_majority(rows, lev, ax)
            vals.append("n/a" if xm is None else f"{xm:.4f}")
        L.append(f"| `x_majority` @ {lev:.2f} | P_confirm < {lev:.2f} | "
                 + " | ".join(vals) + f" | {nm} |")
    vals = []
    for ax, _ in axes:
        xwv, nw = x_w(rows, ax)
        vals.append("n/a" if xwv is None else f"{xwv:.4f}")
    L.append("| `x_W` | 95% interval on W_AB contains 0.5 | "
             + " | ".join(vals) + f" | {nw} |")
    L.append("")
    L.append(f"**Both thresholds shrink as N grows, but only one of them should.**\n")
    L.append(f"`x_majority` asks whether a *majority* of N simulated readers "
             f"favour the higher-scoring model. That criterion changes meaning "
             f"with N: P_confirm goes to 1 for any W_AB != 0.5 given enough "
             f"questions, so the threshold goes to 0 even though nothing about "
             f"the models or the instrument has changed. Its N-dependence is an "
             f"artifact of the criterion, and it must be quoted with N = {n_eff} "
             f"stamped on it.\n")
    L.append(f"`x_W` asks whether the *effect size* W_AB is distinguishable from "
             f"chance. W_AB is a rate -- a per-question, per-reader probability "
             f"-- and does not move with N; only the interval around it narrows, "
             f"which is ordinary estimation precision. A bigger benchmark really "
             f"does pin W_AB down better, so this shrinkage is legitimate rather "
             f"than an artifact. Measured: 0.128 at N=100, 0.103 at N=273, 0.103 "
             f"at N=546, 0.021 at N=1092, and 0.001 conditioning on these "
             f"questions as the whole population (--no-bootstrap-questions).\n")
    L.append(f"At the benchmark's actual size the two criteria nearly coincide, "
             f"which is the practically useful finding: the choice between them "
             f"barely matters at N = {n_eff}.\n")

    if ledger is not None:
        L.append("### Two score axes\n")
        L.append("`D_AB_ledger` is the difference in `grp_congen_score` from "
                 "`results/chronologic_scores.csv` -- the number a reader looks "
                 "up. `D_AB` is the mean per-question `p_fit` gap over the "
                 "questions this analysis actually used. **They differ, for two "
                 "reasons, and the paper's threshold should be quoted on the "
                 "ledger axis** because that is the scale readers compare "
                 "models on:\n")
        L.append("- **Jensen.** The ledger computes `expit(mean cal * mean Delta)` "
                 "(`substantive/estimator.py:73`); `p_fit` is the mean of the "
                 "sigmoid. Widest for models near the ends of the scale.")
        L.append("- **Question set.** The ledger scores all 273 group questions; "
                 "this analysis drops auto-verdict questions whose `p_fit` is "
                 "pinned to exactly 0 or 1. That is most of the difference for "
                 "weak models (e.g. qwen25-7b: 0.175 here vs 0.132 in the ledger).\n")
        L.append("Per-question gaps feeding the human-agreement curve are "
                 "unaffected -- the curve was fitted against `p_fit` gaps and is "
                 "still consumed on that scale. Only the reporting axis changes.\n")
        nd = sum(r["sign_disagree"] for r in rows)
        L.append(f"Direction of \"confirmation\" is anchored to the **ledger** gap. "
                 f"The two axes disagree in sign on **{nd}** of {len(rows)} pairs"
                 + (".\n" if nd == 0 else
                    " (near-ties, which fail every test regardless).\n"))

    for lev in args.confirm_level:
        failing = sorted([r for r in rows if r["P_confirm"] < lev],
                         key=lambda r: abs(r[sort_axis]), reverse=True)
        L.append(f"## Pairs not confirmed at {lev:.2f} ({len(failing)} of {len(rows)})\n")
        L.append("| A | B | n | D ledger | D subset | wins A-B | W_AB | 95% CI | P_confirm |")
        L.append("|--|--|--:|--:|--:|--:|--:|--|--:|")
        for r in failing:
            L.append(f"| {r['candidate_A']} | {r['candidate_B']} | {r['n_questions']} | "
                     f"{r['D_AB_ledger']:+.4f} | {r['D_AB']:+.4f} | "
                     f"{r['n_wins_A']}-{r['n_wins_B']} | "
                     f"{r['W_AB']:.3f} | [{r['W_lo']:.3f}, {r['W_hi']:.3f}] | "
                     f"{r['P_confirm']:.3f} |")
        L.append("")

    L.append("## Win counts are unstable for near-tied pairs\n")
    L.append(f"`bt_context_scoring.py` thins each question's Delta draws to 1000 "
             f"float32 values before persisting them, which costs roughly 0.003 "
             f"of `p_fit` per model. A question whose gap is smaller than that "
             f"has a winner determined by the draw subsample, not by the models. "
             f"`n_near_ties` counts questions with |gap| < {NEAR_TIE}.\n")
    L.append("**Do not quote a head-to-head win count for a pair with a large "
             "`n_near_ties` share.** Measured case: qwen25-7b-local vs "
             "talkie-1930-13b-base reads 124-146 from the stored `p_fit` values "
             "and 158-109 from the persisted draws at the *same* calibration -- "
             "the whole swing is the draw subsample, not the 0.7-to-0.8 change, "
             "which moves exactly one question. `W_AB` and both thresholds are "
             "far more stable, because they weight each question by gap size and "
             "near-ties contribute almost nothing.\n")
    worst = sorted(rows, key=lambda r: -r["n_near_ties"])[:8]
    L.append("| A | B | n | n_near_ties | share | wins A-B |")
    L.append("|--|--|--:|--:|--:|--:|")
    for r in worst:
        L.append(f"| {r['candidate_A']} | {r['candidate_B']} | {r['n_questions']} | "
                 f"{r['n_near_ties']} | {r['n_near_ties']/r['n_questions']:.0%} | "
                 f"{r['n_wins_A']}-{r['n_wins_B']} |")
    L.append("")

    L.append("## Pairs where the win count and W_AB point opposite ways\n")
    L.append("Winning more questions and winning on score are different "
             "quantities, and this channel scores. A divergence is worth "
             "knowing about, not a contradiction: W_AB weights each question by "
             "how visible its gap is to a reader, so a pile of narrow wins can "
             "lose to a smaller pile of wide ones.\n")
    div = [r for r in rows
           if (r["n_wins_A"] - r["n_wins_B"]) * (r["W_AB"] - 0.5) < 0]
    if not div:
        L.append("_None._\n")
    else:
        L.append("| A | B | n | D ledger | wins A-B | near-ties | binom p | W_AB | q on A's wins | q on B's wins |")
        L.append("|--|--|--:|--:|--:|--:|--:|--:|--:|--:|")
        for r in sorted(div, key=lambda r: abs(r[sort_axis])):
            L.append(f"| {r['candidate_A']} | {r['candidate_B']} | {r['n_questions']} | "
                     f"{r['D_AB_ledger']:+.4f} | {r['n_wins_A']}-{r['n_wins_B']} | "
                     f"{r['n_near_ties']} | "
                     f"{r['wins_binom_p']:.3f} | {r['W_AB']:.3f} | "
                     f"{r['q_on_A_wins']:.3f} | {r['q_on_B_wins']:.3f} |")
        L.append("")

    L.append("## Provenance\n")
    L.extend("    " + line for line in prov)
    L.append("")

    md_path = out_dir / "pair_confirmation.md"
    md_path.write_text("\n".join(L), encoding="utf-8")
    print(f"Wrote {md_path}")

    print("\n=== thresholds ===")
    print(f"  {'':22s} {'ledger axis':>12s} {'subset axis':>12s}  pairs failing")
    for lev in args.confirm_level:
        xl, nm = x_majority(rows, lev, "D_AB_ledger") if ledger is not None else (None, 0)
        xs, nm = x_majority(rows, lev, "D_AB")
        print(f"  x_majority @ {lev:.2f}     {('n/a' if xl is None else f'{xl:.4f}'):>12s} "
              f"{xs:>12.4f}  {nm}")
    xl, nw = x_w(rows, "D_AB_ledger") if ledger is not None else (None, 0)
    xs, nw = x_w(rows, "D_AB")
    print(f"  x_W                  {('n/a' if xl is None else f'{xl:.4f}'):>12s} "
          f"{xs:>12.4f}  {nw}")


if __name__ == "__main__":
    main()

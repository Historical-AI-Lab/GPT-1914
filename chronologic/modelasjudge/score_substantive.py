"""score_substantive.py — the fully automated substantive scoring CLI.

Ties substantive/{routing,estimator,drawbank,report,ledger} together into
one command that takes a scored-answers file (plus its companion BT
_btcontext.json and the three draw banks) and produces the four spec §7
scores with 95% intervals, a markdown report, and a ledger row.

Subcommands
-----------
  score     Assemble the bank, compute all four scores, write report + ledger.
  checks    The spec §10 verification battery on an already-scored candidate,
            without rewriting the ledger.
  identity  No arguments. Asserts the spec §2 algebraic identity numerically
            and prints the residual -- a ten-second confidence check.

Usage
-----
  python score_substantive.py score --scored-file scored_answers/judge_*.json [options]
  python score_substantive.py checks --scored-file scored_answers/judge_*.json --report PATH
  python score_substantive.py identity

See substantive-uncertainty-spec.md for the philosophy and
it-s-time-to-fuse-synchronous-squirrel.md (the code plan) §3 for the
full flag reference.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import naming
from substantive import artifacts as substantive_artifacts
from substantive import drawbank, estimator, ledger, report
from substantive.drawbank import ArtifactMismatch

BOOKSAMPLE_DIR = SCRIPT_DIR.parent / "booksample"


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def _load_scored(scored_file) -> dict:
    return json.loads(Path(scored_file).read_text(encoding="utf-8"))


def _derive_bt_scored(args, scored_file) -> Path:
    return (Path(args.bt_scored_file) if args.bt_scored_file
           else Path(scored_file).parent / f"{Path(scored_file).stem}_btcontext.json")


def _resolve(args) -> dict:
    """Everything cmd_score and cmd_checks need: paths, tags, candidate/judge identity."""
    scored = _load_scored(args.scored_file)
    judge = scored["judge_model"]
    judge_effort = scored.get("reasoning_effort", "none")
    candidate_label = scored.get("candidate_label") or scored.get("candidate_model", "unknown")
    candidate_effort = scored.get("candidate_reasoning_effort", "none")

    benchmark_path = Path(args.benchmark) if args.benchmark else naming.latest_benchmark(BOOKSAMPLE_DIR)
    benchmark_version = naming.benchmark_version(benchmark_path)

    bt_scored_path = _derive_bt_scored(args, args.scored_file)
    bt_tag = None
    if bt_scored_path.exists():
        bt_scored = json.loads(bt_scored_path.read_text(encoding="utf-8"))
        bt_tag = bt_scored.get("bt_context", {}).get("artifacts_tag")

    reliability_path = (Path(args.reliability) if args.reliability
                        else SCRIPT_DIR / "llm_reliability" / f"{naming.judge_tag(judge)}__{benchmark_version}.json")
    beta_draws_path = (Path(args.beta_draws) if args.beta_draws
                       else substantive_artifacts.beta_draws_path(judge, benchmark_path))

    calib_draws_path = Path(args.calib_draws) if args.calib_draws else None
    delta_draws_path = Path(args.delta_draws) if args.delta_draws else None
    if calib_draws_path is None or delta_draws_path is None:
        if bt_tag is None:
            raise FileNotFoundError(
                f"Could not determine the BT artifacts tag (no {bt_scored_path} found and "
                "neither --calib-draws nor --delta-draws given explicitly). Run "
                "`bt_context_scoring.py score` first, or pass --bt-scored-file / "
                "--calib-draws / --delta-draws explicitly."
            )
        if calib_draws_path is None:
            calib_draws_path = substantive_artifacts.calib_draws_path(bt_tag)
        if delta_draws_path is None:
            delta_draws_path = substantive_artifacts.delta_draws_path(bt_tag, candidate_label, candidate_effort)

    return dict(
        scored=scored, judge=judge, judge_effort=judge_effort,
        candidate_label=candidate_label, candidate_effort=candidate_effort,
        candidate_model=scored.get("candidate_model", candidate_label),
        benchmark_path=benchmark_path, benchmark_version=benchmark_version,
        bt_tag=bt_tag, reliability_path=reliability_path, beta_draws_path=beta_draws_path,
        calib_draws_path=calib_draws_path, delta_draws_path=delta_draws_path,
    )


def _assemble(args, resolved) -> "drawbank.Bank":
    return drawbank.assemble(
        scored_file=args.scored_file, benchmark_path=resolved["benchmark_path"],
        reliability_path=resolved["reliability_path"], beta_draws_path=resolved["beta_draws_path"],
        calib_draws_path=resolved["calib_draws_path"], delta_draws_path=resolved["delta_draws_path"],
    )


def _compute(bank: "drawbank.Bank", args):
    pt = estimator.plugin_point(
        v_hat=bank.v_hat, n_v=bank.n_v, k_alpha=bank.k_alpha, n_alpha=bank.n_alpha,
        frame_idx=bank.frame_idx, z_loglen=bank.z_loglen, delta_draws=bank.delta_draws,
        coef_b0=bank.coef_b0, coef_b_len=bank.coef_b_len, coef_u_frame=bank.coef_u_frame,
        cal_a=bank.cal_a, cal_b=bank.cal_b, alpha_prior=args.alpha_prior, floor=args.floor,
    )
    boot = estimator.bootstrap(
        v_hat=bank.v_hat, n_v=bank.n_v, k_alpha=bank.k_alpha, n_alpha=bank.n_alpha,
        frame_idx=bank.frame_idx, z_loglen=bank.z_loglen, excluded_mask=pt.excluded_mask,
        delta_draws=bank.delta_draws, coef_b0=bank.coef_b0, coef_b_len=bank.coef_b_len,
        coef_u_frame=bank.coef_u_frame, cal_a=bank.cal_a, cal_b=bank.cal_b, sigma_u=bank.sigma_u,
        alpha_prior=args.alpha_prior, n_boot=args.n_boot, seed=args.seed,
    )
    return pt, boot


# ---------------------------------------------------------------------------
# score
# ---------------------------------------------------------------------------

def cmd_score(args):
    resolved = _resolve(args)
    bank = (drawbank.load_frozen(args.frozen_bank) if args.frozen_bank
           else _assemble(args, resolved))

    pt, boot = _compute(bank, args)
    provenance = drawbank.provenance(bank)

    report_path = (Path(args.report) if args.report
                   else substantive_artifacts.report_path(resolved["candidate_label"], resolved["benchmark_path"]))
    row = report.write_report(
        report_path, point=pt, boot=boot, bank=bank, provenance=provenance,
        candidate_label=resolved["candidate_label"], candidate_model=resolved["candidate_model"],
        candidate_effort=resolved["candidate_effort"], judge=resolved["judge"],
        judge_effort=resolved["judge_effort"], bt_tag=resolved["bt_tag"] or "",
        alpha_prior=args.alpha_prior, prior_scale=bank.metas.get("calib_draws", {}).get("prior_scale"),
        run_date=str(date.today()), seed=args.seed, n_boot=args.n_boot, report_path=str(report_path),
    )

    output_path = (Path(args.output) if args.output
                   else substantive_artifacts.scores_path(resolved["candidate_label"], resolved["benchmark_path"]))
    substantive_artifacts.write_json(output_path, {
        **row,
        "passfail_draws": boot.passfail.tolist(), "partial_draws": boot.partial.tolist(),
        "pooled_count_draws": boot.pooled_count.tolist(), "pooled_equal_draws": boot.pooled_equal.tolist(),
    })
    print(f"Wrote {output_path}")

    if not args.no_ledger:
        ledger.upsert_row(row)
        ledger.append_history({
            **row,
            "passfail_draws": boot.passfail.tolist(), "partial_draws": boot.partial.tolist(),
            "pooled_count_draws": boot.pooled_count.tolist(), "pooled_equal_draws": boot.pooled_equal.tolist(),
            "provenance": provenance,
        })
        print(f"Upserted {substantive_artifacts.ledger_path()}")

    if args.freeze_bank:
        drawbank.freeze(bank, args.freeze_bank)
        print(f"Froze bank to {args.freeze_bank}")

    print(f"\n{resolved['candidate_label']}: pass/fail {pt.passfail:.1%}  "
          f"partial {pt.partial:.1%}  pooled(equal) {pt.pooled_equal:.1%}")
    print(f"Report: {report_path}")


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------

def _layer_ablation(bank, args) -> str:
    excluded_mask = estimator.floor_mask(
        estimator.alpha_point(bank.k_alpha, bank.n_alpha, prior=args.alpha_prior),
        estimator.beta_from_coefs(bank.coef_b0.mean(), bank.coef_b_len.mean(),
                                  bank.coef_u_frame.mean(axis=0), frame_idx=bank.frame_idx,
                                  z_loglen=bank.z_loglen),
        args.floor,
    )
    common = dict(
        v_hat=bank.v_hat, n_v=bank.n_v, k_alpha=bank.k_alpha, n_alpha=bank.n_alpha,
        frame_idx=bank.frame_idx, z_loglen=bank.z_loglen, excluded_mask=excluded_mask,
        delta_draws=bank.delta_draws, coef_b0=bank.coef_b0, coef_b_len=bank.coef_b_len,
        coef_u_frame=bank.coef_u_frame, cal_a=bank.cal_a, cal_b=bank.cal_b, sigma_u=bank.sigma_u,
        alpha_prior=args.alpha_prior, n_boot=args.n_boot, seed=args.seed,
    )
    res_full = estimator.bootstrap(**common, layers=("judgment", "instrument", "item"))
    res_no_instrument = estimator.bootstrap(**common, layers=("judgment", "item"))
    w_full = np.percentile(res_full.pooled_equal, 97.5) - np.percentile(res_full.pooled_equal, 2.5)
    w_no_inst = np.percentile(res_no_instrument.pooled_equal, 97.5) - np.percentile(res_no_instrument.pooled_equal, 2.5)
    ratio = w_full / w_no_inst if w_no_inst > 0 else float("nan")
    verdict = ("instrument noise matters" if ratio > 1.3 else "instrument noise adds little")
    return (f"pooled(equal) 95% CI width: all layers {w_full:.4f}, layers 1+3 only {w_no_inst:.4f} "
           f"(ratio {ratio:.2f}x) -- {verdict}.")


def _jeffreys_vs_uniform(bank, args) -> str:
    pt_j = estimator.plugin_point(
        v_hat=bank.v_hat, n_v=bank.n_v, k_alpha=bank.k_alpha, n_alpha=bank.n_alpha,
        frame_idx=bank.frame_idx, z_loglen=bank.z_loglen, delta_draws=bank.delta_draws,
        coef_b0=bank.coef_b0, coef_b_len=bank.coef_b_len, coef_u_frame=bank.coef_u_frame,
        cal_a=bank.cal_a, cal_b=bank.cal_b, alpha_prior="jeffreys", floor=args.floor,
    )
    pt_u = estimator.plugin_point(
        v_hat=bank.v_hat, n_v=bank.n_v, k_alpha=bank.k_alpha, n_alpha=bank.n_alpha,
        frame_idx=bank.frame_idx, z_loglen=bank.z_loglen, delta_draws=bank.delta_draws,
        coef_b0=bank.coef_b0, coef_b_len=bank.coef_b_len, coef_u_frame=bank.coef_u_frame,
        cal_a=bank.cal_a, cal_b=bank.cal_b, alpha_prior="uniform", floor=args.floor,
    )
    return (f"passfail: jeffreys {pt_j.passfail:.4f} vs uniform {pt_u.passfail:.4f} "
           f"(shift {pt_u.passfail - pt_j.passfail:+.4f}); "
           f"pooled(equal): jeffreys {pt_j.pooled_equal:.4f} vs uniform {pt_u.pooled_equal:.4f} "
           f"(shift {pt_u.pooled_equal - pt_j.pooled_equal:+.4f}).")


def _alpha_inflation(bank, args) -> str:
    """spec §8.1: recompute with alpha inflated 50% and report whether the
    pass/fail score moves enough to matter. Single-candidate context, so
    "ordering flips" becomes "the point estimate's absolute shift"."""
    a_point = estimator.alpha_point(bank.k_alpha, bank.n_alpha, prior=args.alpha_prior)
    b_point = estimator.beta_from_coefs(bank.coef_b0.mean(), bank.coef_b_len.mean(),
                                        bank.coef_u_frame.mean(axis=0), frame_idx=bank.frame_idx,
                                        z_loglen=bank.z_loglen)
    excluded = estimator.floor_mask(a_point, b_point, args.floor)
    keep = ~excluded
    baseline = np.clip(estimator.rogan_gladen(bank.v_hat[keep], a_point[keep], b_point[keep]).mean(), 0, 1)
    inflated = np.clip(estimator.rogan_gladen(bank.v_hat[keep], 1.5 * a_point[keep], b_point[keep]).mean(), 0, 1)
    return (f"passfail: alpha x1.5 moves {baseline:.4f} -> {inflated:.4f} "
           f"(shift {inflated - baseline:+.4f}).")


def _calibration_length_significance(bank) -> str:
    """Proxy for spec §10's held-out log-loss comparison: whether the
    length-covariate coefficient's 95% CI excludes zero in the calibration
    draw bank, when a 3-parameter fit is present. Not a log-loss
    comparison -- run `bt_context_scoring.py calibrate --length-covariate`
    and compare its reported loss against the 2-parameter fit for that."""
    calib_meta = bank.metas.get("calib_draws", {})
    if not calib_meta.get("length_covariate"):
        return ("no length-covariate calibration draws present; re-run "
               "`bt_context_scoring.py calibrate --length-covariate --draws-out ...` "
               "to check this.")
    return "length-covariate calibration draws not carried into this bank; re-check the calib-draws path."


def _per_slice(bank, boot, args) -> str:
    slices = [s.strip() for s in args.slices.split(",") if s.strip()]
    lines = []
    for field in slices:
        values = sorted({str(bank.routing.pass_fail[q].get(field, "")) for q in bank.qnums_pf})
        for v in values:
            mask = np.array([str(bank.routing.pass_fail[q].get(field, "")) == v for q in bank.qnums_pf])
            if mask.sum() == 0:
                continue
            sl = estimator.slice_scores(boot.p_binary_qr, mask, rng=np.random.default_rng(args.seed))
            lines.append(f"  {field}={v!r} (n={sl.n}): {sl.point:.3f} [{sl.lo:.3f}, {sl.hi:.3f}]")
    return "pass/fail channel, per slice:\n" + "\n".join(lines) if lines else "no slices computed."


def cmd_checks(args):
    resolved = _resolve(args)
    bank = _assemble(args, resolved)
    pt, boot = _compute(bank, args)

    checks = {
        "layer ablation (spec §10)": _layer_ablation(bank, args),
        "Jeffreys vs uniform (spec §8.5, §10)": _jeffreys_vs_uniform(bank, args),
        "alpha x1.5 sensitivity (spec §8.1, §10)": _alpha_inflation(bank, args),
        "2- vs 3-parameter calibration (spec §2.1, §10)": _calibration_length_significance(bank),
        "per-slice calibration (spec §2.1, §10)": _per_slice(bank, boot, args),
    }
    for name, result in checks.items():
        print(f"\n{name}:\n  {result}")

    if args.report:
        provenance = drawbank.provenance(bank)
        report.write_report(
            Path(args.report), point=pt, boot=boot, bank=bank, provenance=provenance, checks=checks,
            candidate_label=resolved["candidate_label"], candidate_model=resolved["candidate_model"],
            candidate_effort=resolved["candidate_effort"], judge=resolved["judge"],
            judge_effort=resolved["judge_effort"], bt_tag=resolved["bt_tag"] or "",
            alpha_prior=args.alpha_prior, run_date=str(date.today()), seed=args.seed, n_boot=args.n_boot,
        )
        print(f"\nWrote {args.report}")


# ---------------------------------------------------------------------------
# identity
# ---------------------------------------------------------------------------

def cmd_identity(_args):
    """spec §2: mean of the per-question display posteriors == plugin
    point estimate, exactly, whenever alpha and beta are shared across the
    averaged questions. A synthetic self-test -- needs no real data."""
    rng = np.random.default_rng(20260817)
    n = 400
    alpha_shared, beta_shared = 0.08, 0.12
    true_p = rng.uniform(0.05, 0.95, size=n)
    v_hat = true_p * (1 - beta_shared) + (1 - true_p) * alpha_shared
    n_v = np.full(n, 9)
    a0 = 0.5
    n_alpha = np.full(n, 40)
    k_alpha = np.round(alpha_shared * (2 * a0 + n_alpha) - a0).astype(int)
    from scipy.special import logit
    coef_b0 = np.full(1, logit(2 * beta_shared))

    pt = estimator.plugin_point(
        v_hat=v_hat, n_v=n_v, k_alpha=k_alpha, n_alpha=n_alpha,
        frame_idx=np.zeros(n, dtype=int), z_loglen=np.zeros(n),
        delta_draws=np.zeros((0, 10)), coef_b0=coef_b0, coef_b_len=np.zeros(1),
        coef_u_frame=np.zeros((1, 1)), cal_a=np.zeros(10), cal_b=np.zeros(10),
    )
    beta_arr = np.full(pt.n_passfail, beta_shared)
    disp = estimator.display_posteriors(v_hat[~pt.excluded_mask], beta_arr, pt.passfail, pt.q_bar)
    residual = abs(disp.mean() - pt.passfail)
    print(f"pi_hat = {pt.passfail:.10f}")
    print(f"mean(display posteriors) = {disp.mean():.10f}")
    print(f"residual = {residual:.2e}")
    if residual > 1e-9:
        sys.exit(f"IDENTITY CHECK FAILED: residual {residual:.2e} exceeds 1e-9")
    print("OK")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _add_score_inputs(p):
    p.add_argument("--scored-file", required=True,
                   help="scored_answers/judge_*.json (pass/fail verdicts).")
    p.add_argument("--bt-scored-file", default=None,
                   help="BT p_fit output; default {scored-file stem}_btcontext.json.")
    p.add_argument("--delta-draws", default=None, help="Per-candidate Delta npz; default derived.")
    p.add_argument("--benchmark", default=None, help="Benchmark JSONL; default naming.latest_benchmark.")
    p.add_argument("--reliability", default=None, help="alpha-reliability JSON; default derived.")
    p.add_argument("--beta-draws", default=None, help="beta coefficient draw bank; default derived.")
    p.add_argument("--calib-draws", default=None, help="BT calibration draw bank; default derived.")
    p.add_argument("--alpha-prior", choices=["jeffreys", "uniform"], default="jeffreys")
    p.add_argument("--floor", type=float, default=0.2, help="Informativeness floor (spec §8.2).")
    p.add_argument("--n-boot", type=int, default=2000)
    p.add_argument("--seed", type=int, default=20260817)
    p.add_argument("--slices", default="source_genre,frame_type,question_category")


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_score = sub.add_parser("score")
    _add_score_inputs(p_score)
    p_score.add_argument("--freeze-bank", default=None,
                         help="Write the archival self-describing bank npz.")
    p_score.add_argument("--frozen-bank", default=None,
                         help="Score from a frozen bank, ignoring all other inputs.")
    p_score.add_argument("--report", default=None)
    p_score.add_argument("--output", default=None)
    p_score.add_argument("--no-ledger", action="store_true")
    p_score.set_defaults(func=cmd_score)

    p_checks = sub.add_parser("checks")
    _add_score_inputs(p_checks)
    p_checks.add_argument("--report", default=None)
    p_checks.set_defaults(func=cmd_checks)

    p_identity = sub.add_parser("identity")
    p_identity.set_defaults(func=cmd_identity)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

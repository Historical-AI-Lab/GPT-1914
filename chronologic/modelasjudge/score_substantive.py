"""score_substantive.py — the fully automated substantive scoring CLI.

Ties substantive/{routing,estimator,drawbank,report,ledger} together into
one command that takes a scored-answers file (plus its companion BT
_btcontext.json and the two BT draw banks) and produces the four scores
with 95% intervals, a markdown report, and a ledger row.

The pass/fail (binary) channel needs no alpha/beta artifacts: it is the
arithmetic mean of the observed judge verdicts, direct from the
scored-answers file. Judge false-pass/false-fail rates are validation
evidence about the instrument, reported separately by
judge_validation_report.py -- never a scoring dependency here.

Subcommands
-----------
  score     Assemble the bank, compute all four scores, write report + ledger.
  checks    The verification battery on an already-scored candidate,
            without rewriting the ledger.
  identity  No arguments. Asserts the partition identity numerically and
            prints the residual -- a ten-second confidence check.

Usage
-----
  python score_substantive.py score --scored-file scored_answers/judge_*.json [options]
  python score_substantive.py checks --scored-file scored_answers/judge_*.json --report PATH
  python score_substantive.py identity

See direct-binary-scoring-spec.md for the philosophy and
plan-direct-binary-scoring.md §4 for the full flag reference.
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
from substantive import drawbank, estimator, groups as group_defs, ledger, report

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
        bt_tag=bt_tag, calib_draws_path=calib_draws_path, delta_draws_path=delta_draws_path,
    )


def _assemble(args, resolved) -> "drawbank.Bank":
    return drawbank.assemble(
        scored_file=args.scored_file, benchmark_path=resolved["benchmark_path"],
        calib_draws_path=resolved["calib_draws_path"], delta_draws_path=resolved["delta_draws_path"],
        benchmark_version=resolved["benchmark_version"],
    )


def _compute(bank: "drawbank.Bank", args):
    pt = estimator.plugin_point(
        v_hat=bank.v_hat, delta_draws=bank.delta_draws, cal_a=bank.cal_a, cal_b=bank.cal_b,
        auto_pf=bank.auto_pf, auto_pc=bank.auto_pc,
    )
    boot = estimator.bootstrap(
        v_hat=bank.v_hat, delta_draws=bank.delta_draws, cal_a=bank.cal_a, cal_b=bank.cal_b,
        n_boot=args.n_boot, seed=args.seed, auto_pf=bank.auto_pf, auto_pc=bank.auto_pc,
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
    group_results = _group_breakdown(bank, pt, boot, args)

    report_path = (Path(args.report) if args.report
                   else substantive_artifacts.report_path(resolved["candidate_label"], resolved["benchmark_path"]))
    row = report.write_report(
        report_path, point=pt, boot=boot, bank=bank, provenance=provenance, groups=group_results,
        candidate_label=resolved["candidate_label"], candidate_model=resolved["candidate_model"],
        candidate_effort=resolved["candidate_effort"], judge=resolved["judge"],
        judge_effort=resolved["judge_effort"], bt_tag=resolved["bt_tag"] or "",
        benchmark_version=resolved["benchmark_version"],
        prior_scale=bank.metas.get("calib_draws", {}).get("prior_scale"),
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
    print("  " + "  ".join(
        f"{group_defs.GROUP_LABELS[g]} {group_results[g].point:.1%}" for g in group_defs.GROUPS
    ))
    print(f"Report: {report_path}")


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------

def _layer_ablation(bank, args) -> str:
    """BT-only diagnostic: the binary channel has no judgment/instrument
    layer left to ablate (it is conditioned on the observed v_q), so this
    toggle only measures the BT calibration draw's contribution to
    pooled(equal)'s interval width."""
    common = dict(
        v_hat=bank.v_hat, delta_draws=bank.delta_draws, cal_a=bank.cal_a, cal_b=bank.cal_b,
        auto_pf=bank.auto_pf, auto_pc=bank.auto_pc, n_boot=args.n_boot, seed=args.seed,
    )
    res_full = estimator.bootstrap(**common, layers=("judgment", "instrument", "item"))
    res_no_instrument = estimator.bootstrap(**common, layers=("judgment", "item"))
    w_full = np.percentile(res_full.pooled_equal, 97.5) - np.percentile(res_full.pooled_equal, 2.5)
    w_no_inst = np.percentile(res_no_instrument.pooled_equal, 97.5) - np.percentile(res_no_instrument.pooled_equal, 2.5)
    ratio = w_full / w_no_inst if w_no_inst > 0 else float("nan")
    verdict = ("BT instrument noise matters" if ratio > 1.3 else "BT instrument noise adds little")
    return (f"[BT-only] pooled(equal) 95% CI width: all layers {w_full:.4f}, "
           f"layers 1+3 only {w_no_inst:.4f} (ratio {ratio:.2f}x) -- {verdict}. "
           "The binary channel does not respond to this toggle (item resampling only).")


def _binary_identity(bank, pt) -> str:
    """binary_score == mean(v_q): the whole point of dropping Rogan-Gladen."""
    n = bank.v_hat.size
    residual = abs(pt.passfail - float(bank.v_hat.mean())) if n else float("nan")
    return f"|passfail - mean(v_q)| = {residual:.2e} (n={n})"


def _calibration_length_significance(bank) -> str:
    """Proxy for a held-out log-loss comparison: whether the length-covariate
    coefficient's 95% CI excludes zero in the calibration draw bank, when a
    3-parameter fit is present. Not a log-loss comparison -- run
    `bt_context_scoring.py calibrate --length-covariate` and compare its
    reported loss against the 2-parameter fit for that."""
    calib_meta = bank.metas.get("calib_draws", {})
    if not calib_meta.get("length_covariate"):
        return ("no length-covariate calibration draws present; re-run "
               "`bt_context_scoring.py calibrate --length-covariate --draws-out ...` "
               "to check this.")
    return "length-covariate calibration draws not carried into this bank; re-check the calib-draws path."


def _per_slice(bank, pt, boot, args) -> str:
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


def _group_breakdown(bank, pt, boot, args) -> dict:
    """Reasoning-type breakdown (substantive/groups.py): count-weighted
    score per group, combining both channels. Raises UnmappedReasoningType
    (via group_defs.group_of) if a routed question's reasoning_type isn't
    in the map -- fail loud rather than silently drop it from every group.
    """
    group_pf = [group_defs.group_of(bank.routing.pass_fail[q], qnum=q) for q in bank.qnums_pf]
    group_pc = [group_defs.group_of(bank.routing.partial[q], qnum=q) for q in bank.qnums_pc]

    rng = np.random.default_rng(args.seed)
    result = {}
    for g in group_defs.GROUPS:
        mask_pf = np.array([gg == g for gg in group_pf], dtype=bool)
        mask_pc = np.array([gg == g for gg in group_pc], dtype=bool)
        result[g] = estimator.group_scores(
            pt.p_binary, pt.p_partial, boot.p_binary_qr, boot.p_partial_qr,
            mask_pf, mask_pc, rng=rng,
        )
    return result


def _format_group_breakdown(group_results) -> str:
    lines = [f"  {group_defs.GROUP_LABELS[g]}: {r.point:.3f} [{r.lo:.3f}, {r.hi:.3f}] "
            f"(n={r.n}, pf={r.n_pf}, pc={r.n_pc})"
            for g, r in group_results.items()]
    return "\n".join(lines)


def cmd_checks(args):
    resolved = _resolve(args)
    bank = _assemble(args, resolved)
    pt, boot = _compute(bank, args)
    group_results = _group_breakdown(bank, pt, boot, args)

    checks = {
        "binary identity": _binary_identity(bank, pt),
        "layer ablation": _layer_ablation(bank, args),
        "2- vs 3-parameter calibration": _calibration_length_significance(bank),
        "per-slice calibration": _per_slice(bank, pt, boot, args),
        "reasoning-type breakdown": _format_group_breakdown(group_results),
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
            benchmark_version=resolved["benchmark_version"],
            run_date=str(date.today()), seed=args.seed, n_boot=args.n_boot,
        )
        print(f"\nWrote {args.report}")


# ---------------------------------------------------------------------------
# identity
# ---------------------------------------------------------------------------

def cmd_identity(_args):
    """No real data needed: (1) binary == mean(v_q) exactly, since the
    binary score is defined as that mean; (2) the partition identity
    S = sum(n_g * S_g) / sum(n_g) holds over an arbitrary complete group
    split of both channels, where S is the count-weighted pooled score and
    each S_g is estimator.group_scores' count-weighted score for that group."""
    rng = np.random.default_rng(20260817)
    n_pf, n_pc, n_groups = 400, 150, 3

    v_hat = rng.uniform(0.0, 1.0, size=n_pf)
    delta_draws = rng.normal(0.0, 1.0, size=(n_pc, 500))
    cal_a = np.full(50, 0.1)
    cal_b = np.full(50, 1.0)

    pt = estimator.plugin_point(v_hat=v_hat, delta_draws=delta_draws, cal_a=cal_a, cal_b=cal_b)

    residual_binary = abs(pt.passfail - float(v_hat.mean()))

    group_pf = rng.integers(0, n_groups, size=n_pf)
    group_pc = rng.integers(0, n_groups, size=n_pc)
    total_n = n_pf + n_pc
    weighted_sum = 0.0
    for g in range(n_groups):
        pf_mask = group_pf == g
        pc_mask = group_pc == g
        n_g = int(pf_mask.sum() + pc_mask.sum())
        if n_g == 0:
            continue
        s_g = (pt.p_binary[pf_mask].sum() + pt.p_partial[pc_mask].sum()) / n_g
        weighted_sum += n_g * s_g
    partition_score = weighted_sum / total_n
    residual_partition = abs(partition_score - pt.pooled_count)

    print(f"binary passfail        = {pt.passfail:.10f}")
    print(f"mean(v_q)               = {v_hat.mean():.10f}")
    print(f"residual (binary == mean(v_q))         = {residual_binary:.2e}")
    print(f"pooled_count             = {pt.pooled_count:.10f}")
    print(f"sum(n_g*S_g)/sum(n_g)    = {partition_score:.10f}")
    print(f"residual (partition identity)          = {residual_partition:.2e}")

    if residual_binary > 1e-12 or residual_partition > 1e-12:
        sys.exit(f"IDENTITY CHECK FAILED: residual_binary={residual_binary:.2e} "
                 f"residual_partition={residual_partition:.2e}")
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
    p.add_argument("--calib-draws", default=None, help="BT calibration draw bank; default derived.")
    p.add_argument("--benchmark", default=None, help="Benchmark JSONL; default naming.latest_benchmark.")
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

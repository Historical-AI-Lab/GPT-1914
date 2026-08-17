"""substantive/report.py — the markdown report (spec §7).

Renders already-computed numbers; no statistics happen here. House style
follows report_bt_inversions.py: build a list of markdown fragments, join
once, write. write_report also returns the flat dict of ledger-column
values it rendered, so score_substantive.py can hand that same dict to
ledger.upsert_row -- the report and the ledger row are then guaranteed to
carry identical numbers, which is what tests/test_substantive_report.py
checks (every ledger number must appear, formatted, in the report text).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np


def _ci(replicates):
    lo, hi = np.percentile(replicates, [2.5, 97.5])
    return float(lo), float(hi)


def write_report(path, *, point, boot, bank, provenance, checks=None,
                 candidate_label="", candidate_model="", candidate_effort="",
                 judge="", judge_effort="", bt_tag="", alpha_prior="jeffreys",
                 prior_scale=None, run_date="", seed=None, n_boot=None,
                 report_path="") -> dict:
    """point: estimator.PlugPoint. boot: estimator.BootstrapResult.
    bank: drawbank.Bank. provenance: drawbank.provenance(bank).
    checks: optional dict from score_substantive.py's `checks` subcommand,
    {check_name: human-readable result string}.

    Returns the flat ledger-row dict (spec §7's four scores + diagnostics).
    """
    pf_lo, pf_hi = _ci(boot.passfail)
    pc_lo, pc_hi = _ci(boot.partial)
    pcount_lo, pcount_hi = _ci(boot.pooled_count)
    pequal_lo, pequal_hi = _ci(boot.pooled_equal)

    clip_rate = float(np.mean((boot.pooled_equal <= 0.0) | (boot.pooled_equal >= 1.0)))
    near_floor_frac = float(point.n_excluded_floor / max(len(bank.v_hat), 1))
    mean_alpha = float(np.mean(bank.k_alpha / np.maximum(bank.n_alpha, 1))) if bank.n_alpha.size else float("nan")

    row = {
        "run_date": run_date, "benchmark_version": bank.metas.get("beta_draws", {}).get("benchmark_version", ""),
        "routing_basis": bank.routing.basis,
        "candidate_label": candidate_label, "candidate_model": candidate_model,
        "candidate_effort": candidate_effort, "judge": judge, "judge_effort": judge_effort,
        "bt_tag": bt_tag, "alpha_prior": alpha_prior, "prior_scale": prior_scale,
        "n_passfail": point.n_passfail, "n_partial": point.n_partial,
        "n_excluded_floor": point.n_excluded_floor,
        "passfail": point.passfail, "passfail_lo": pf_lo, "passfail_hi": pf_hi,
        "partial": point.partial, "partial_lo": pc_lo, "partial_hi": pc_hi,
        "pooled_count": point.pooled_count, "pooled_count_lo": pcount_lo, "pooled_count_hi": pcount_hi,
        "pooled_equal": point.pooled_equal, "pooled_equal_lo": pequal_lo, "pooled_equal_hi": pequal_hi,
        "clip_rate": clip_rate, "near_floor_frac": near_floor_frac,
        "sigma_u": bank.sigma_u, "mean_alpha": mean_alpha,
        "n_boot": n_boot, "seed": seed, "report_path": report_path,
    }

    L = []
    L.append(f"# Substantive score: {candidate_label}\n")
    L.append(f"\nJudge `{judge}` (effort `{judge_effort}`) · benchmark `{row['benchmark_version']}` "
             f"· run {run_date}\n")
    L.append(f"\nRouting basis: `{bank.routing.basis}` -- {point.n_passfail} pass/fail questions, "
             f"{point.n_partial} partial-credit questions, {point.n_excluded_floor} excluded "
             f"below the informativeness floor.\n")

    L.append("\n## Scores\n")
    L.append("\nAll intervals are 95% percentile (spec §7).\n")
    L.append("\n| score | point | 95% CI |\n|---|---:|---|\n")
    L.append(f"| pass/fail ({point.n_passfail} qs) | {point.passfail:.1%} | "
             f"[{pf_lo:.1%}, {pf_hi:.1%}] |\n")
    L.append(f"| partial-credit ({point.n_partial} qs) | {point.partial:.1%} | "
             f"[{pc_lo:.1%}, {pc_hi:.1%}] |\n")
    L.append(f"| pooled, count-weighted | {point.pooled_count:.1%} | "
             f"[{pcount_lo:.1%}, {pcount_hi:.1%}] |\n")
    L.append(f"| **pooled, equal-weight (headline)** | **{point.pooled_equal:.1%}** | "
             f"[{pequal_lo:.1%}, {pequal_hi:.1%}] |\n")

    L.append("\n## Diagnostics (spec §8.6 -- reported, not folded into intervals)\n")
    L.append(f"\n- sigma_u (beta residual scale): {bank.sigma_u:.4f}\n")
    L.append(f"- clip rate (replicates landing exactly at 0 or 1): {clip_rate:.2%}\n")
    L.append(f"- n excluded below informativeness floor: {point.n_excluded_floor} "
             f"({near_floor_frac:.1%} of pass/fail questions)\n")
    if not np.isnan(mean_alpha):
        L.append(f"- mean alpha (pass/fail channel, {alpha_prior} prior): {mean_alpha:.4f}\n")

    if checks:
        L.append("\n## Verification checks (spec §10)\n")
        for name, result in checks.items():
            L.append(f"\n**{name}**: {result}\n")

    L.append("\n## Provenance\n")
    for role, entry in provenance.items():
        L.append(f"\n- `{role}`: produced by `{entry.get('produced_by')}` "
                 f"at {entry.get('produced_at')} (git `{entry.get('git_head')}`)\n")

    Path(path).write_text("".join(L), encoding="utf-8")
    return row

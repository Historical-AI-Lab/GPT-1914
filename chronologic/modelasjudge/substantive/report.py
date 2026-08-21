"""substantive/report.py — the markdown report.

Renders already-computed numbers; no statistics happen here. House style
follows report_bt_inversions.py: build a list of markdown fragments, join
once, write. write_report also returns the flat dict of ledger-column
values it rendered, so score_substantive.py can hand that same dict to
ledger.upsert_row -- the report and the ledger row are then guaranteed to
carry identical numbers, which is what tests/test_substantive_report.py
checks (every ledger number must appear, formatted, in the report text).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

MODELASJUDGE_DIR = Path(__file__).resolve().parent.parent
if str(MODELASJUDGE_DIR) not in sys.path:
    sys.path.insert(0, str(MODELASJUDGE_DIR))

from naming import judge_tag  # noqa: E402
from substantive import groups as group_defs


def _ci(replicates):
    lo, hi = np.percentile(replicates, [2.5, 97.5])
    return float(lo), float(hi)


def write_report(path, *, point, boot, bank, provenance, checks=None, groups=None,
                 candidate_label="", candidate_model="", candidate_effort="",
                 judge="", judge_effort="", bt_tag="", benchmark_version="",
                 prior_scale=None, run_date="", seed=None, n_boot=None,
                 report_path="") -> dict:
    """point: estimator.PlugPoint. boot: estimator.BootstrapResult.
    bank: drawbank.Bank. provenance: drawbank.provenance(bank).
    checks: optional dict from score_substantive.py's `checks` subcommand,
    {check_name: human-readable result string}.
    groups: optional dict {group_name: estimator.GroupResult} from
    score_substantive.py's `_group_breakdown` (substantive/groups.py's
    reasoning-type breakdown). When given, adds a "Scores by reasoning
    type" section and 5 ledger columns per group.

    Returns the flat ledger-row dict (the four scores + diagnostics).
    """
    pf_lo, pf_hi = _ci(boot.passfail)
    pc_lo, pc_hi = _ci(boot.partial)
    pcount_lo, pcount_hi = _ci(boot.pooled_count)
    pequal_lo, pequal_hi = _ci(boot.pooled_equal)

    n_binary_pass = int(np.count_nonzero(point.p_binary == 1.0))
    n_binary_fail = int(np.count_nonzero(point.p_binary == 0.0))
    n_binary_split = point.n_passfail - n_binary_pass - n_binary_fail

    row = {
        "run_date": run_date, "benchmark_version": benchmark_version,
        "routing_basis": bank.routing.basis,
        "candidate_label": candidate_label, "candidate_model": candidate_model,
        "candidate_effort": candidate_effort, "judge": judge, "judge_effort": judge_effort,
        "bt_tag": bt_tag, "prior_scale": prior_scale,
        "scoring_version": "direct_binary_v1",
        "n_passfail": point.n_passfail, "n_partial": point.n_partial,
        "n_binary_pass": n_binary_pass, "n_binary_fail": n_binary_fail,
        "n_binary_split": n_binary_split,
        # How much of the headline came from certainties rather than judgments:
        # a score that is largely verbatim recall should be visible as such.
        "n_auto_passfail": int(np.count_nonzero(~np.isnan(bank.auto_pf))),
        "n_auto_partial": int(np.count_nonzero(~np.isnan(bank.auto_pc))),
        "passfail": point.passfail, "passfail_lo": pf_lo, "passfail_hi": pf_hi,
        "partial": point.partial, "partial_lo": pc_lo, "partial_hi": pc_hi,
        "pooled_count": point.pooled_count, "pooled_count_lo": pcount_lo, "pooled_count_hi": pcount_hi,
        "pooled_equal": point.pooled_equal, "pooled_equal_lo": pequal_lo, "pooled_equal_hi": pequal_hi,
        "n_boot": n_boot, "seed": seed, "report_path": report_path,
    }

    if groups:
        for g, gr in groups.items():
            prefix = group_defs.LEDGER_PREFIX[g]
            row[f"{prefix}_score"] = gr.point
            row[f"{prefix}_lo"] = gr.lo
            row[f"{prefix}_hi"] = gr.hi
            row[f"{prefix}_n_pf"] = gr.n_pf
            row[f"{prefix}_n_pc"] = gr.n_pc

    L = []
    L.append(f"# Substantive score: {candidate_label}\n")
    L.append(f"\nJudge `{judge}` (effort `{judge_effort}`) · benchmark `{benchmark_version}` "
             f"· run {run_date} · scoring `direct_binary_v1`\n")
    L.append(f"\nRouting basis: `{bank.routing.basis}` -- {point.n_passfail} pass/fail questions, "
             f"{point.n_partial} partial-credit questions.\n")

    L.append("\n## Scores\n")
    L.append("\nAll intervals are 95% percentile. The pass/fail score is the arithmetic mean of "
             "the observed judge verdicts -- no correction, no clipping.\n")
    L.append("\n| score | point | 95% CI |\n|---|---:|---|\n")
    L.append(f"| pass/fail ({point.n_passfail} qs) | {point.passfail:.1%} | "
             f"[{pf_lo:.1%}, {pf_hi:.1%}] |\n")
    L.append(f"| partial-credit ({point.n_partial} qs) | {point.partial:.1%} | "
             f"[{pc_lo:.1%}, {pc_hi:.1%}] |\n")
    L.append(f"| pooled, count-weighted | {point.pooled_count:.1%} | "
             f"[{pcount_lo:.1%}, {pcount_hi:.1%}] |\n")
    L.append(f"| **pooled, equal-weight (headline)** | **{point.pooled_equal:.1%}** | "
             f"[{pequal_lo:.1%}, {pequal_hi:.1%}] |\n")

    if groups:
        L.append("\n## Scores by reasoning type\n")
        L.append("\nCount-weighted over both channels within each group. The count-weighted "
                 "partition reconstructs the aggregate pooled(count) exactly; it does not "
                 "reconstruct pooled(equal), which weights the two channels equally rather "
                 "than by count -- this is a breakdown, not a decomposition of the headline.\n")
        L.append("\n| reasoning type | score | 95% CI | n (pass/fail + partial) |\n|---|---:|---|---|\n")
        for g in group_defs.GROUPS:
            gr = groups.get(g)
            if gr is None:
                continue
            label = group_defs.GROUP_LABELS[g]
            L.append(f"| {label} | {gr.point:.1%} | [{gr.lo:.1%}, {gr.hi:.1%}] | "
                     f"{gr.n} ({gr.n_pf} + {gr.n_pc}) |\n")

    L.append("\n## Diagnostics\n")
    L.append(f"\n- pass/fail verdicts: {n_binary_pass} pass (v=1), {n_binary_fail} fail (v=0), "
             f"{n_binary_split} fractional (0<v<1)\n")
    L.append(f"- automatic verdicts (verbatim ground-truth or probability-0 distractor match, "
             f"no judge call): {row['n_auto_passfail']} pass/fail, {row['n_auto_partial']} partial-credit\n")
    L.append("\nJudge error rates characterize the evaluator and are not used to adjust model "
             "scores. See "
             f"`results/judge_validation_{judge_tag(judge)}__{benchmark_version}.md` "
             "for the judge's false-pass (alpha) and false-fail (beta) rates.\n")

    if checks:
        L.append("\n## Verification checks\n")
        for name, result in checks.items():
            L.append(f"\n**{name}**: {result}\n")

    L.append("\n## Provenance\n")
    for role, entry in provenance.items():
        L.append(f"\n- `{role}`: produced by `{entry.get('produced_by')}` "
                 f"at {entry.get('produced_at')} (git `{entry.get('git_head')}`)\n")

    # Create the results directory the way ledger.py already does: the report is
    # the last thing written after the whole estimate has been computed, so a
    # missing directory here throws away a completed run.
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(L), encoding="utf-8")
    return row

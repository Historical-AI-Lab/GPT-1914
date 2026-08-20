"""substantive/ledger.py — CSV upsert + append-only history (spec §6, plan §6).

Two files under modelasjudge/results/:

  chronologic_scores.csv   one row per evaluation, UPSERTED on
                            (benchmark_version, candidate_label,
                            candidate_effort, judge, judge_effort, bt_tag)
                            -- a re-run after a bug fix must replace the
                            wrong row, not leave a reader to guess which
                            is current. run_date/seed/n_boot are not in
                            the key.
  score_history.jsonl      append-only audit trail: every ledger column
                            plus full provenance, replicate percentile
                            arrays, ablation results, sensitivity scenarios.

Read-modify-write via .tmp + replace (bt/artifacts.py's convention);
unknown pre-existing columns preserved; new columns back-filled empty on
old rows; rows sorted by key on every write so git diffs stay readable.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from . import artifacts

KEY_COLUMNS = ["benchmark_version", "candidate_label", "candidate_effort",
              "judge", "judge_effort", "bt_tag"]

COLUMNS = [
    "run_date", "benchmark_version", "routing_basis", "candidate_label", "candidate_model",
    "candidate_effort", "judge", "judge_effort", "bt_tag", "alpha_prior", "prior_scale",
    "prompt_mode", "n_passfail", "n_partial", "n_excluded_floor",
    "passfail", "passfail_lo", "passfail_hi", "partial", "partial_lo", "partial_hi",
    "pooled_count", "pooled_count_lo", "pooled_count_hi",
    "pooled_equal", "pooled_equal_lo", "pooled_equal_hi",
    "grp_cloze_score", "grp_cloze_lo", "grp_cloze_hi", "grp_cloze_n_pf", "grp_cloze_n_pc",
    "grp_congen_score", "grp_congen_lo", "grp_congen_hi", "grp_congen_n_pf", "grp_congen_n_pc",
    "grp_knowinf_score", "grp_knowinf_lo", "grp_knowinf_hi", "grp_knowinf_n_pf", "grp_knowinf_n_pc",
    "clip_rate", "near_floor_frac", "sigma_u", "mean_alpha", "mean_beta", "mean_informativeness",
    "style_cohort_id", "style_T_E2", "style_T_drift", "style_T_KS", "style_T_disp", "style_p_fused",
    "n_boot", "seed", "inputs_sha", "report_path", "notes",
]


def _key(row: dict) -> tuple:
    return tuple(str(row.get(c, "")) for c in KEY_COLUMNS)


def _read_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def upsert_row(row: dict, *, path=None) -> None:
    """Insert `row`, or replace whichever existing row shares its KEY_COLUMNS."""
    path = Path(path) if path else artifacts.ledger_path()
    existing = _read_rows(path)

    all_columns = list(dict.fromkeys(
        COLUMNS + [c for r in existing for c in r] + list(row)
    ))

    rows_by_key = {_key(r): r for r in existing}
    rows_by_key[_key(row)] = row

    out_rows = [{c: r.get(c, "") for c in all_columns} for r in rows_by_key.values()]
    out_rows.sort(key=lambda r: tuple(str(r.get(c, "")) for c in KEY_COLUMNS))

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_columns)
        writer.writeheader()
        writer.writerows(out_rows)
    tmp.replace(path)


def append_history(record: dict, *, path=None) -> None:
    path = Path(path) if path else artifacts.history_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

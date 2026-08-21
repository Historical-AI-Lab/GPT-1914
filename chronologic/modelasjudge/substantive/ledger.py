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
    "candidate_effort", "judge", "judge_effort", "bt_tag", "scoring_version", "prior_scale",
    "prompt_mode", "n_passfail", "n_partial",
    "n_binary_pass", "n_binary_fail", "n_binary_split",
    "passfail", "passfail_lo", "passfail_hi", "partial", "partial_lo", "partial_hi",
    "pooled_count", "pooled_count_lo", "pooled_count_hi",
    "pooled_equal", "pooled_equal_lo", "pooled_equal_hi",
    "grp_cloze_score", "grp_cloze_lo", "grp_cloze_hi", "grp_cloze_n_pf", "grp_cloze_n_pc",
    "grp_congen_score", "grp_congen_lo", "grp_congen_hi", "grp_congen_n_pf", "grp_congen_n_pc",
    "grp_knowinf_score", "grp_knowinf_lo", "grp_knowinf_hi", "grp_knowinf_n_pf", "grp_knowinf_n_pc",
    # Style columns (stylejudge/score_style.py -> merge_style_row.py). NOTE:
    # `style_cohort_id` keeps its original name but now holds a per-CANDIDATE
    # style run id -- the cohort-wide batch it was named for is retired.
    "style_cohort_id",
    "style_period_fidelity", "style_period_fidelity_lo", "style_period_fidelity_hi",
    "style_authenticity_fidelity", "style_authenticity_fidelity_lo", "style_authenticity_fidelity_hi",
    "style_w1", "style_w1_null_mean", "style_drift_years", "style_dispersion_mae",
    "style_T_drift", "style_T_disp", "style_T_E2",
    "style_T_KS",   # Spec B §16 compatibility diagnostic, not a headline
    "n_boot", "seed", "inputs_sha", "report_path", "notes",
]

# Dropped from COLUMNS but may still linger as a header on old CSVs written
# before this rename -- upsert_row/merge_columns's shared _write must filter
# it explicitly, since upsert_row's own all_columns is rebuilt from
# COLUMNS + headers-seen-on-disk + row, which would otherwise resurrect it
# as an empty column forever.
RETIRED_COLUMNS = {
    "style_p_fused",
    # Rogan-Gladen era (direct-binary-scoring-spec.md): the correction, its
    # informativeness floor, and its diagnostics are gone -- alpha/beta are
    # judge-validation quantities now (substantive/judge_validation.py) and
    # never touch a candidate score, so they are never written as a ledger
    # column again. mean_beta / mean_informativeness were already-dead
    # headers nothing wrote even before this change.
    "alpha_prior", "n_excluded_floor", "clip_rate", "near_floor_frac",
    "sigma_u", "mean_alpha", "mean_beta", "mean_informativeness",
}

# upsert_row carries these column PREFIXES forward from the row being
# replaced whenever the new `row` doesn't supply them -- without this,
# re-running stage 11 (score_substantive, which writes no style_* keys)
# would silently blank every style column on every re-score, since they're
# written by a different stage in a different process.
PRESERVE_PREFIXES = ("style_",)


def _key(row: dict) -> tuple:
    return tuple(str(row.get(c, "")) for c in KEY_COLUMNS)


def _read_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write(path: Path, rows_by_key: dict, all_columns: list[str]) -> None:
    """Shared write half of upsert_row/merge_columns: filter RETIRED_COLUMNS,
    sort by key, atomic .tmp + replace."""
    columns = [c for c in all_columns if c not in RETIRED_COLUMNS]
    out_rows = [{c: r.get(c, "") for c in columns} for r in rows_by_key.values()]
    out_rows.sort(key=lambda r: tuple(str(r.get(c, "")) for c in KEY_COLUMNS))

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(out_rows)
    tmp.replace(path)


def upsert_row(row: dict, *, path=None, preserve=PRESERVE_PREFIXES) -> None:
    """Insert `row`, or replace whichever existing row shares its KEY_COLUMNS.

    Columns matching a `preserve` prefix that `row` does not itself supply
    are carried forward from the row being replaced (see PRESERVE_PREFIXES).
    """
    path = Path(path) if path else artifacts.ledger_path()
    existing = _read_rows(path)

    all_columns = list(dict.fromkeys(
        COLUMNS + [c for r in existing for c in r] + list(row)
    ))

    rows_by_key = {_key(r): r for r in existing}
    key = _key(row)
    old_row = rows_by_key.get(key)
    if old_row is not None and preserve:
        merged = dict(row)
        for c, v in old_row.items():
            if c.startswith(preserve) and c not in row:
                merged[c] = v
        row = merged
    rows_by_key[key] = row

    _write(path, rows_by_key, all_columns)


def merge_columns(key: dict, updates: dict, *, path=None, create_missing: bool = False) -> bool:
    """Merge `updates` into the one row matching all six KEY_COLUMNS in
    `key`, leaving every other column (including ones not in COLUMNS)
    untouched. Values in `key` are compared as strings, exactly as `_key`
    builds them from a row.

    Returns False and writes nothing when no row matches, unless
    `create_missing` (which inserts a new row built from `key` + `updates`).
    Raises ValueError if `key` is incomplete, or if `updates` touches a key
    column (that would be an upsert, not a merge).
    """
    missing_key_cols = [c for c in KEY_COLUMNS if c not in key]
    if missing_key_cols:
        raise ValueError(f"key is missing required columns: {missing_key_cols}")
    bad = [c for c in updates if c in KEY_COLUMNS]
    if bad:
        raise ValueError(f"updates must not touch key columns: {bad}")

    path = Path(path) if path else artifacts.ledger_path()
    existing = _read_rows(path)
    all_columns = list(dict.fromkeys(COLUMNS + [c for r in existing for c in r] + list(updates)))

    rows_by_key = {_key(r): r for r in existing}
    target_key = tuple(str(key[c]) for c in KEY_COLUMNS)

    if target_key not in rows_by_key:
        if not create_missing:
            return False
        new_row = {c: str(key[c]) for c in KEY_COLUMNS}
        new_row.update(updates)
        rows_by_key[target_key] = new_row
    else:
        rows_by_key[target_key].update(updates)

    _write(path, rows_by_key, all_columns)
    return True


def append_history(record: dict, *, path=None) -> None:
    path = Path(path) if path else artifacts.history_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

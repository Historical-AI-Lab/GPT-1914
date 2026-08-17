"""substantive/artifacts.py — tags, paths, and atomic npz/json IO.

Three draw banks, three different scopes (spec §5, plan §4), so this is
three path families rather than one monolith:

  beta coefficient draws + sigma_u   per binary judge x benchmark version
  calibration (a, b) draws           per BT instrument (bt.artifacts.bt_tag)
  Delta draws                        per candidate x BT instrument

alpha draws are deliberately not persisted here (spec §5): closed-form
from (k, n) at estimation time, so freezing a prior choice into a file
never happens by accident.

npz format follows bt/fit.py's save_anchor_fits/load_anchor_fits template:
a JSON-string "meta" array alongside named float arrays, atomic .tmp +
replace, allow_pickle=False on load.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

MODELASJUDGE_DIR = Path(__file__).resolve().parent.parent
if str(MODELASJUDGE_DIR) not in sys.path:
    sys.path.insert(0, str(MODELASJUDGE_DIR))

from naming import benchmark_version, candidate_tag, judge_tag, sanitize  # noqa: E402

SCHEMA_VERSION = 1

BETA_RELIABILITY_DIR = MODELASJUDGE_DIR / "beta_reliability"
BT_ARTIFACTS_DIR = MODELASJUDGE_DIR / "bt_artifacts"
SUBSTANTIVE_ARTIFACTS_DIR = MODELASJUDGE_DIR / "substantive_artifacts"
RESULTS_DIR = MODELASJUDGE_DIR / "results"


def substantive_tag(judge: str, benchmark_path, judge_effort: str) -> str:
    """Tag for artifacts scoped to a binary judge x benchmark version x effort."""
    return f"{judge_tag(judge)}__{benchmark_version(benchmark_path)}__j-{judge_effort}"


def beta_draws_path(judge: str, benchmark_path) -> Path:
    return BETA_RELIABILITY_DIR / f"beta_draws_{judge_tag(judge)}__{benchmark_version(benchmark_path)}.npz"


def calib_draws_path(bt_tag: str) -> Path:
    return BT_ARTIFACTS_DIR / f"bt_calib_draws_{bt_tag}.npz"


def delta_draws_path(bt_tag: str, candidate_label: str, candidate_effort: str) -> Path:
    return (SUBSTANTIVE_ARTIFACTS_DIR
           / f"delta_{bt_tag}__{candidate_tag(candidate_label)}__c-{candidate_effort}.npz")


def bank_path(kind: str, **kwargs) -> Path:
    """Dispatch to the path helper for one of "beta", "calib", "delta"."""
    if kind == "beta":
        return beta_draws_path(kwargs["judge"], kwargs["benchmark_path"])
    if kind == "calib":
        return calib_draws_path(kwargs["bt_tag"])
    if kind == "delta":
        return delta_draws_path(kwargs["bt_tag"], kwargs["candidate_label"], kwargs["candidate_effort"])
    raise ValueError(f"unknown bank kind {kind!r}")


def report_path(candidate_label: str, benchmark_path, *, checks: bool = False) -> Path:
    stem = "checks" if checks else "report"
    return RESULTS_DIR / f"{stem}_{sanitize(candidate_label)}__{benchmark_version(benchmark_path)}.md"


def scores_path(candidate_label: str, benchmark_path) -> Path:
    return RESULTS_DIR / f"scores_{sanitize(candidate_label)}__{benchmark_version(benchmark_path)}.json"


def ledger_path() -> Path:
    return RESULTS_DIR / "chronologic_scores.csv"


def history_path() -> Path:
    return RESULTS_DIR / "score_history.jsonl"


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

def git_head() -> str:
    """Short git commit hash of HEAD, or "unknown" outside a repo / on error."""
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=MODELASJUDGE_DIR,
                             capture_output=True, text=True, timeout=5, check=True)
        return out.stdout.strip()
    except Exception:
        return "unknown"


def sha256_of(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def source_artifact_entry(role: str, path) -> dict:
    path = Path(path)
    return {role: {"path": str(path), "sha256": sha256_of(path) if path.exists() else None}}


def base_meta(*, produced_by: str, **extra) -> dict:
    """The provenance fields every draw bank's meta dict shares."""
    meta = {
        "schema_version": SCHEMA_VERSION,
        "produced_by": produced_by,
        "produced_at": datetime.now(timezone.utc).isoformat(),
        "git_head": git_head(),
    }
    meta.update(extra)
    return meta


# ---------------------------------------------------------------------------
# Atomic npz IO (bt/fit.py's save_anchor_fits template, generalized)
# ---------------------------------------------------------------------------

def save_npz(path, arrays: dict, meta: dict) -> None:
    payload = {"meta": np.array(json.dumps(meta))}
    for key, arr in arrays.items():
        payload[key] = np.asarray(arr)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.npz")
    np.savez(tmp, **payload)
    tmp.replace(path)


def load_npz(path) -> tuple[dict, dict]:
    data = np.load(path, allow_pickle=False)
    meta = json.loads(str(data["meta"]))
    arrays = {k: data[k] for k in data.files if k != "meta"}
    return arrays, meta


def write_json(path, obj: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1), encoding="utf-8")
    tmp.replace(path)


def read_json(path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))

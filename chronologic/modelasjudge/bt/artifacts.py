"""bt/artifacts.py — filenames and I/O for bt_context_scoring artifacts.

Everything lives under modelasjudge/bt_artifacts/, named with a tag that
records judge model, benchmark version, and judge reasoning effort (per
the spec: artifacts are specific to a judge model / benchmark file
combination).  Reuses naming.sanitize / naming.judge_tag so tags stay
consistent with the rest of the pipeline's filenames.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

MODELASJUDGE_DIR = Path(__file__).resolve().parent.parent
if str(MODELASJUDGE_DIR) not in sys.path:
    sys.path.insert(0, str(MODELASJUDGE_DIR))

from naming import benchmark_version, judge_tag  # noqa: E402
from bt.prompts import DEFAULT_PROMPT_MODE, PROMPT_MODES  # noqa: F401,E402

ARTIFACT_DIR = MODELASJUDGE_DIR / "bt_artifacts"


# "exemplars" ran before the mode existed, so its artifacts carry no suffix.
# That is a naming fact, not a statement about which mode to prefer -- the
# preferred mode is prompts.DEFAULT_PROMPT_MODE, currently "rationales".
UNSUFFIXED_PROMPT_MODE = "exemplars"


def bt_tag(judge: str, benchmark_path, judge_effort: str,
           prompt_mode: str = DEFAULT_PROMPT_MODE,
           prior_dist: str = "normal") -> str:
    """Artifact tag for a judge / benchmark / effort / prompt-mode combination.

    The suffix is omitted for UNSUFFIXED_PROMPT_MODE ("exemplars") so that
    artifacts written before the mode existed keep their names; every other
    mode, including the preferred one, is suffixed and coexists with them.
    """
    tag = f"{judge_tag(judge)}__{benchmark_version(benchmark_path)}__j-{judge_effort}"
    if prompt_mode != UNSUFFIXED_PROMPT_MODE:
        tag += f"__pm-{prompt_mode}"
    if prior_dist != "normal":
        tag += f"__pd-{prior_dist}"
    return tag


def anchors_path(tag: str, *, loo: bool = False) -> Path:
    name = f"bt_anchors_loo_{tag}.npz" if loo else f"bt_anchors_{tag}.npz"
    return ARTIFACT_DIR / name


def judgments_path(tag: str) -> Path:
    return ARTIFACT_DIR / f"bt_judgments_{tag}.jsonl"


def loo_path(tag: str) -> Path:
    return ARTIFACT_DIR / f"bt_loo_{tag}.json"


def calibration_path(tag: str) -> Path:
    return ARTIFACT_DIR / f"bt_calibration_{tag}.json"


def results_path(tag: str) -> Path:
    return ARTIFACT_DIR / f"bt_results_{tag}.json"


def recovery_path(mode: str, seed: int) -> Path:
    return ARTIFACT_DIR / f"bt_recovery_{mode}_{seed}.json"


def cache_dir() -> Path:
    return ARTIFACT_DIR / "cache"


def ensure_dirs() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def append_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    if not Path(path).exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_json(path: Path, obj: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1), encoding="utf-8")
    tmp.replace(path)


def read_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))

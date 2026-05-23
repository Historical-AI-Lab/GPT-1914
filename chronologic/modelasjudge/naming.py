"""naming.py — Shared filename helpers for the model-as-judge pipeline.

Every script that reads or writes scored_answers/ or generated_answers/ should
import these helpers so that {candidate}__{version} suffixes are identical across
free_generation, judge_scoring, discriminative_scoring, and score_calculation.
"""

import re
from pathlib import Path


def sanitize(s: str) -> str:
    """Replace characters that are unsafe in filenames with underscores."""
    return re.sub(r"[^a-zA-Z0-9_\-.]", "_", s)


def candidate_tag(model_id: str) -> str:
    """Filesystem-safe tag for a candidate model."""
    return sanitize(model_id)


def judge_tag(model_id: str) -> str:
    """Filesystem-safe tag for a judge model."""
    return sanitize(model_id)


def benchmark_version(benchmark_path) -> str:
    """Extract version string from a benchmark filename.

    E.g. 'chronologic_en_0.2.jsonl' → '0.2'.
    Returns 'unknown' if no version pattern found.
    """
    name = Path(benchmark_path).stem
    m = re.search(r"(\d+\.\d+)", name)
    return m.group(1) if m else "unknown"

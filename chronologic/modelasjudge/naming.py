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
    """Extract version string from a benchmark or free-gen filename.

    Takes the LAST X.Y decimal in the stem so that model names containing
    decimals (Qwen2.5, gpt-4.1) do not shadow the benchmark version token.

    Examples:
      'chronologic_en_0.4.jsonl'                        → '0.4'
      'free_gen_Qwen_Qwen2.5-7B-Instruct_ft_0.4.json'  → '0.4'
      'free_gen_gpt-4.1-2025-04-14__0.4.json'          → '0.4'
    Returns 'unknown' if no version pattern found.
    """
    name = Path(benchmark_path).stem
    matches = re.findall(r"\d+\.\d+", name)
    return matches[-1] if matches else "unknown"


def latest_benchmark(booksample_dir) -> Path:
    """Return the path to the highest-versioned chronologic_en_X.Y.jsonl.

    Raises FileNotFoundError if no matching file is found.
    """
    booksample_dir = Path(booksample_dir)
    candidates = list(booksample_dir.glob("chronologic_en_*.jsonl"))
    if not candidates:
        raise FileNotFoundError(f"No chronologic_en_*.jsonl found in {booksample_dir}")

    def _ver(p: Path):
        m = re.search(r"chronologic_en_(\d+)\.(\d+)\.jsonl", p.name)
        return (int(m.group(1)), int(m.group(2))) if m else (-1, -1)

    return max(candidates, key=_ver)


def scored_answers_filename(
    judge: str,
    candidate_label: str,
    version: str,
    candidate_effort: str = "none",
    judge_effort: str = "none",
) -> str:
    """Canonical filename for a scored-answers output file.

    Format:
      judge_{judge}__{candidate_label}__{version}__c-{ceff}__j-{jeff}.json

    Both effort tokens are always written so runs at different effort levels
    never collide.
    """
    j = judge_tag(judge)
    c = sanitize(candidate_label)
    return f"judge_{j}__{c}__{version}__c-{candidate_effort}__j-{judge_effort}.json"

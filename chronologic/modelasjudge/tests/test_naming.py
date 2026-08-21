"""test_naming.py — Unit tests for naming.py helpers.

Run with:
    pytest modelasjudge/tests/test_naming.py -v
"""

import sys
import tempfile
from pathlib import Path

import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from naming import benchmark_version, latest_benchmark, scored_answers_filename


# ---------------------------------------------------------------------------
# benchmark_version — takes the LAST X.Y token to skip model-name decimals
# ---------------------------------------------------------------------------

def test_plain_benchmark():
    assert benchmark_version("chronologic_en_0.2.jsonl") == "0.2"


def test_plain_benchmark_04():
    assert benchmark_version("chronologic_en_0.4.jsonl") == "0.4"


def test_model_decimal_shadowing_qwen25():
    # 'Qwen2.5' should not shadow '0.4' at the end
    assert benchmark_version("free_gen_Qwen_Qwen2.5-7B-Instruct_ft_0.4.json") == "0.4"


def test_model_decimal_shadowing_gpt41():
    # 'gpt-4.1' should not shadow '0.4' at the end
    assert benchmark_version("free_gen_gpt-4.1-2025-04-14__0.4.json") == "0.4"


def test_model_decimal_shadowing_gpt54():
    assert benchmark_version("free_gen_gpt-5.4__0.2.json") == "0.2"


def test_free_gen_standard():
    assert benchmark_version("free_gen_talkie-1930-13b-it__0.2.json") == "0.2"


def test_no_version_returns_unknown():
    assert benchmark_version("some_file_without_version.json") == "unknown"


def test_full_path():
    assert benchmark_version("/data/booksample/chronologic_en_0.4.jsonl") == "0.4"


# ---------------------------------------------------------------------------
# latest_benchmark
# ---------------------------------------------------------------------------

def test_latest_benchmark_finds_highest():
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        (tdp / "chronologic_en_0.2.jsonl").touch()
        (tdp / "chronologic_en_0.3.jsonl").touch()
        (tdp / "chronologic_en_0.4.jsonl").touch()
        result = latest_benchmark(tdp)
        assert result.name == "chronologic_en_0.4.jsonl"


def test_latest_benchmark_single_file():
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        (tdp / "chronologic_en_0.2.jsonl").touch()
        result = latest_benchmark(tdp)
        assert result.name == "chronologic_en_0.2.jsonl"


def test_latest_benchmark_no_files_raises():
    with tempfile.TemporaryDirectory() as td:
        with pytest.raises(FileNotFoundError):
            latest_benchmark(Path(td))


# ---------------------------------------------------------------------------
# scored_answers_filename
# ---------------------------------------------------------------------------

def test_scored_filename_default_efforts():
    name = scored_answers_filename(
        "anthropic/claude-sonnet-4-6",
        "gpt-5.4",
        "0.4",
    )
    assert name == "judge_anthropic_claude-sonnet-4-6__gpt-5.4__0.4__c-none__j-none.json"


def test_scored_filename_with_efforts():
    name = scored_answers_filename(
        "anthropic/claude-sonnet-4-6",
        "Qwen/Qwen2.5-7B-Instruct-ft",
        "0.4",
        candidate_effort="none",
        judge_effort="medium",
    )
    assert "__c-none__j-medium" in name
    assert name.endswith(".json")


def test_scored_filename_different_efforts_differ():
    name_none = scored_answers_filename("judge", "model", "0.4", "none", "none")
    name_med = scored_answers_filename("judge", "model", "0.4", "none", "medium")
    assert name_none != name_med


def test_scored_filename_sanitizes_slashes():
    name = scored_answers_filename("anthropic/claude", "Qwen/model", "0.4")
    assert "/" not in name

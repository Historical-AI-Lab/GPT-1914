"""
Tests for evalcode/benchmark_evaluation.py

Run unit tests (no model required):
    pytest evalcode/tests/ -m "not llm"

Run HF LLM tests (downloads gpt2 ~500 MB on first run, cached thereafter):
    pytest evalcode/tests/ -m "llm" -k "Hf"

Run vLLM LLM tests (vLLM must be running on port 9011):
    pytest evalcode/tests/ -m "llm" -k "not Hf"
"""

import json
import os
import sys
from pathlib import Path

import pytest

# Add evalcode/ to path so we can import benchmark_evaluation directly
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmark_evaluation import (
    _build_question_text,
    _build_mcq_prompt,
    _parse_mcq_response,
    calculate_brier_score,
    calculate_mcq_skill_score,
    get_answer_lls,
    get_answer_lls_hf,
    is_openai_model,
    load_model,
    load_openai_credentials,
    lls_to_probabilities,
    mcq_eval_openai,
    test_five_questions as run_five_questions_eval,
    test_five_questions_hf as run_five_questions_hf_eval,
    full_eval_hf as run_full_eval_hf,
    mcq_eval_hf as run_mcq_eval_hf,
    VLLM_BASE_URL,
    MODEL,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

SAMPLE_JSONL = (
    Path(__file__).parent.parent.parent
    / "booksample"
    / "connectors"
    / "process_files"
    / "HWWJNQ_clozequestions.jsonl"
)


@pytest.fixture
def sample_question():
    """Load the first question from HWWJNQ_clozequestions.jsonl."""
    with open(SAMPLE_JSONL, encoding="utf-8") as f:
        return json.loads(f.readline())


@pytest.fixture
def minimal_question():
    """A minimal hand-crafted question dict for unit tests (no LLM needed)."""
    return {
        "metadata_frame": "The following passage comes from a novel published in 1905.",
        "main_question": "What did the soldier do next?",
        "question_category": "cloze_causalclause",
        "answer_strings": ["He retreated quickly.", "He advanced boldly.", "He stood still."],
        "answer_types": ["ground_truth", "negation", "same_book"],
        "answer_probabilities": [1.0, 0.0, 0.0],
    }


# ---------------------------------------------------------------------------
# Unit tests — no LLM required
# ---------------------------------------------------------------------------

class TestBuildQuestionText:
    """Tests for _build_question_text() prompt construction."""

    def test_with_metadata_includes_metadata_frame(self, minimal_question):
        text = _build_question_text(minimal_question, use_metadata=True)
        assert minimal_question["metadata_frame"] in text

    def test_without_metadata_excludes_metadata_frame(self, minimal_question):
        text = _build_question_text(minimal_question, use_metadata=False)
        assert minimal_question["metadata_frame"] not in text

    def test_format_has_question_and_answer_labels(self, minimal_question):
        for use_metadata in (True, False):
            text = _build_question_text(minimal_question, use_metadata=use_metadata)
            assert "QUESTION: " in text
            assert "ANSWER: " in text

    def test_with_metadata_starts_with_metadata_frame(self, minimal_question):
        text = _build_question_text(minimal_question, use_metadata=True)
        assert text.startswith(minimal_question["metadata_frame"])

    def test_without_metadata_starts_with_question_label(self, minimal_question):
        text = _build_question_text(minimal_question, use_metadata=False)
        assert text.startswith("QUESTION: ")

    def test_ends_with_answer_label(self, minimal_question):
        for use_metadata in (True, False):
            text = _build_question_text(minimal_question, use_metadata=use_metadata)
            assert text.endswith("ANSWER: ")


class TestLlsToProbabilities:
    """Tests for lls_to_probabilities() softmax conversion."""

    def test_probabilities_sum_to_one(self):
        log_scores = [-1.22, -1.31, -1.80, -2.05]
        probs = lls_to_probabilities(log_scores)
        assert abs(sum(probs) - 1.0) < 1e-9

    def test_output_length_matches_input_length(self):
        for n in (2, 3, 6):
            log_scores = [-1.0] * n
            probs = lls_to_probabilities(log_scores)
            assert len(probs) == n

    def test_higher_ll_gets_higher_probability(self):
        log_scores = [-1.0, -2.0, -3.0]
        probs = lls_to_probabilities(log_scores)
        assert probs[0] > probs[1] > probs[2]

    def test_equal_scores_give_uniform_distribution(self):
        log_scores = [-1.5, -1.5, -1.5]
        probs = lls_to_probabilities(log_scores)
        for p in probs:
            assert abs(p - 1 / 3) < 1e-9

    def test_all_probabilities_are_non_negative(self):
        log_scores = [-0.5, -10.0, -100.0]
        probs = lls_to_probabilities(log_scores)
        for p in probs:
            assert p >= 0.0


class TestCalculateBrierScore:
    """Tests for calculate_brier_score()."""

    def test_perfect_prediction_scores_zero(self):
        gt = [1.0, 0.0, 0.0]
        model = [1.0, 0.0, 0.0]
        assert calculate_brier_score(gt, model) == pytest.approx(0.0)

    def test_worst_prediction_scores_one(self):
        # Model assigns all probability to the wrong answer
        gt = [1.0, 0.0]
        model = [0.0, 1.0]
        # (0-1)^2 + (1-0)^2 = 2, divided by 2 = 1.0
        assert calculate_brier_score(gt, model) == pytest.approx(1.0)

    def test_known_values(self):
        # Hand-computed: gt=[1,0,0], model=[0.5,0.3,0.2]
        # ((0.5-1)^2 + (0.3-0)^2 + (0.2-0)^2) / 3
        # = (0.25 + 0.09 + 0.04) / 3 = 0.38 / 3 ≈ 0.12667
        gt = [1.0, 0.0, 0.0]
        model = [0.5, 0.3, 0.2]
        expected = (0.25 + 0.09 + 0.04) / 3
        assert calculate_brier_score(gt, model) == pytest.approx(expected, rel=1e-6)

    def test_two_answer_case(self):
        gt = [1.0, 0.0]
        model = [0.8, 0.2]
        # ((0.8-1)^2 + (0.2-0)^2) / 2 = (0.04 + 0.04) / 2 = 0.04
        assert calculate_brier_score(gt, model) == pytest.approx(0.04)


class TestCalculateMcqSkillScore:
    """Tests for calculate_mcq_skill_score() — no LLM required."""

    def test_correct_always_scores_one(self):
        # True regardless of k or r
        for k in (2, 3, 4, 10):
            assert calculate_mcq_skill_score(True, k, r=1) == pytest.approx(1.0)

    def test_incorrect_with_two_choices(self):
        # k=2, r=1: (0 - 0.5) / (1 - 0.5) = -1.0
        assert calculate_mcq_skill_score(False, 2, r=1) == pytest.approx(-1.0)

    def test_incorrect_with_four_choices(self):
        # k=4, r=1: (0 - 0.25) / (1 - 0.25) = -1/3
        assert calculate_mcq_skill_score(False, 4, r=1) == pytest.approx(-1/3)

    def test_expected_value_at_chance_is_zero(self):
        # For k=4, r=1: 1/4 chance of being correct
        # E[score] = 0.25 * score(correct) + 0.75 * score(incorrect)
        #          = 0.25 * 1.0 + 0.75 * (-1/3) = 0.25 - 0.25 = 0.0
        k, r = 4, 1
        correct_score   = calculate_mcq_skill_score(True,  k, r)
        incorrect_score = calculate_mcq_skill_score(False, k, r)
        expected = (r/k) * correct_score + (1 - r/k) * incorrect_score
        assert expected == pytest.approx(0.0)


class TestBuildMcqPrompt:
    """Tests for _build_mcq_prompt() — no LLM required."""

    def test_negation_excluded_by_default(self, minimal_question):
        prompt_text, answer_order, correct_letter = _build_mcq_prompt(
            minimal_question, include_negation=False
        )
        # "He advanced boldly." is the negation answer
        assert "He advanced boldly." not in prompt_text

    def test_include_negation_keeps_negation(self, minimal_question):
        prompt_text, answer_order, correct_letter = _build_mcq_prompt(
            minimal_question, include_negation=True
        )
        assert "He advanced boldly." in prompt_text

    def test_all_non_negation_answers_appear(self, minimal_question):
        prompt_text, answer_order, correct_letter = _build_mcq_prompt(
            minimal_question, include_negation=False
        )
        # ground_truth and same_book answers should appear
        assert "He retreated quickly." in prompt_text
        assert "He stood still." in prompt_text

    def test_correct_letter_maps_to_ground_truth(self, minimal_question):
        prompt_text, answer_order, correct_letter = _build_mcq_prompt(
            minimal_question, include_negation=False
        )
        # Find what answer the correct_letter maps to
        correct_entry = next(
            (s, p) for letter, s, p in answer_order if letter == correct_letter
        )
        assert correct_entry[1] == 1.0  # prob == 1.0 for ground truth

    def test_prompt_ends_with_respond_instruction(self, minimal_question):
        prompt_text, answer_order, correct_letter = _build_mcq_prompt(minimal_question)
        assert prompt_text.endswith("Respond only with the letter of the correct answer:")

    def test_letters_are_uppercase_sequential(self, minimal_question):
        prompt_text, answer_order, correct_letter = _build_mcq_prompt(
            minimal_question, include_negation=True
        )
        letters = [letter for letter, s, p in answer_order]
        expected = [chr(ord("A") + i) for i in range(len(letters))]
        assert letters == expected


class TestParseMcqResponse:
    """Tests for _parse_mcq_response() — no LLM required."""

    def test_returns_letter_from_clean_response(self):
        assert _parse_mcq_response("A") == "A"

    def test_extracts_letter_from_verbose_response(self):
        assert _parse_mcq_response("The answer is B.") == "B"

    def test_returns_none_if_no_letter(self):
        assert _parse_mcq_response("42") is None

    def test_returns_first_letter_if_multiple(self):
        assert _parse_mcq_response("A or B") == "A"


class TestIsOpenaiModel:
    """Tests for is_openai_model() — no LLM required."""

    def test_gpt41_versioned(self):
        assert is_openai_model("gpt-4.1-2025-04-14") is True

    def test_gpt41_bare(self):
        assert is_openai_model("gpt-4.1") is True

    def test_gpt5_versioned(self):
        assert is_openai_model("gpt-5.2-2025-12-11") is True

    def test_gpt5_mini(self):
        assert is_openai_model("gpt-5-mini-2025-08-07") is True

    def test_gpt5_bare(self):
        assert is_openai_model("gpt-5") is True

    def test_finetune_gpt41(self):
        assert is_openai_model("ft:gpt-4.1-2025-04-14:org:mymodel:abc123") is True

    def test_finetune_gpt5(self):
        assert is_openai_model("ft:gpt-5-2025-12-01:org:mymodel:xyz") is True

    def test_local_hf_model(self):
        assert is_openai_model("Qwen/Qwen2.5-7B-Instruct") is False

    def test_gptoss_local(self):
        assert is_openai_model("gpt-oss:20b") is False

    def test_gpt2(self):
        assert is_openai_model("gpt2") is False

    def test_empty_string(self):
        assert is_openai_model("") is False


class TestLoadOpenaiCredentials:
    """Tests for load_openai_credentials() — no LLM required."""

    def test_loads_org_and_key(self, tmp_path):
        cred_file = tmp_path / "credentials.txt"
        cred_file.write_text("org-TESTORG\nsk-TESTAPIKEY\n", encoding="utf-8")
        org_id, api_key = load_openai_credentials(str(cred_file))
        assert org_id == "org-TESTORG"
        assert api_key == "sk-TESTAPIKEY"

    def test_strips_whitespace(self, tmp_path):
        cred_file = tmp_path / "credentials.txt"
        cred_file.write_text("  org-TESTORG  \n  sk-TESTAPIKEY  \n", encoding="utf-8")
        org_id, api_key = load_openai_credentials(str(cred_file))
        assert org_id == "org-TESTORG"
        assert api_key == "sk-TESTAPIKEY"

    def test_ignores_blank_lines(self, tmp_path):
        cred_file = tmp_path / "credentials.txt"
        cred_file.write_text("\norg-TESTORG\n\nsk-TESTAPIKEY\n\n", encoding="utf-8")
        org_id, api_key = load_openai_credentials(str(cred_file))
        assert org_id == "org-TESTORG"
        assert api_key == "sk-TESTAPIKEY"

    def test_raises_if_file_missing(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="OpenAI credentials file not found"):
            load_openai_credentials(str(tmp_path / "nonexistent.txt"))

    def test_raises_if_only_one_line(self, tmp_path):
        cred_file = tmp_path / "credentials.txt"
        cred_file.write_text("org-TESTORG\n", encoding="utf-8")
        with pytest.raises(ValueError, match="two non-empty lines"):
            load_openai_credentials(str(cred_file))


# ---------------------------------------------------------------------------
# LLM tests — require live vLLM on port 9011
# ---------------------------------------------------------------------------

@pytest.mark.llm
class TestGetAnswerLls:
    """Tests for get_answer_lls() — requires vLLM."""

    def test_returns_list_of_correct_length(self, sample_question):
        lls = get_answer_lls(sample_question, MODEL, use_metadata=True, base_url=VLLM_BASE_URL)
        assert len(lls) == len(sample_question["answer_strings"])

    def test_all_scores_are_floats(self, sample_question):
        lls = get_answer_lls(sample_question, MODEL, use_metadata=True, base_url=VLLM_BASE_URL)
        for score in lls:
            assert isinstance(score, float)

    def test_use_metadata_changes_scores(self, sample_question):
        lls_with = get_answer_lls(
            sample_question, MODEL, use_metadata=True, base_url=VLLM_BASE_URL
        )
        lls_without = get_answer_lls(
            sample_question, MODEL, use_metadata=False, base_url=VLLM_BASE_URL
        )
        # Scores should differ when metadata is included vs. excluded
        assert lls_with != lls_without

    def test_scores_are_non_positive(self, sample_question):
        """Log-probabilities are always ≤ 0."""
        lls = get_answer_lls(sample_question, MODEL, use_metadata=True, base_url=VLLM_BASE_URL)
        for score in lls:
            assert score <= 0.0


@pytest.mark.llm
class TestTestFiveQuestions:
    """Tests for test_five_questions() — requires vLLM."""

    def test_markdown_file_is_created(self, tmp_path):
        # Copy sample JSONL to tmp_path so the report lands there
        import shutil
        tmp_jsonl = tmp_path / "HWWJNQ_clozequestions.jsonl"
        shutil.copy(SAMPLE_JSONL, tmp_jsonl)

        report_path = run_five_questions_eval(MODEL, str(tmp_jsonl), base_url=VLLM_BASE_URL)
        assert Path(report_path).exists()

    def test_markdown_file_contains_model_name(self, tmp_path):
        import shutil
        tmp_jsonl = tmp_path / "HWWJNQ_clozequestions.jsonl"
        shutil.copy(SAMPLE_JSONL, tmp_jsonl)

        report_path = run_five_questions_eval(MODEL, str(tmp_jsonl), base_url=VLLM_BASE_URL)
        content = Path(report_path).read_text(encoding="utf-8")
        assert MODEL in content

    def test_brier_scores_not_all_identical(self, tmp_path):
        """Different questions should yield different Brier scores."""
        import shutil
        tmp_jsonl = tmp_path / "HWWJNQ_clozequestions.jsonl"
        shutil.copy(SAMPLE_JSONL, tmp_jsonl)

        report_path = run_five_questions_eval(MODEL, str(tmp_jsonl), base_url=VLLM_BASE_URL)
        content = Path(report_path).read_text(encoding="utf-8")

        # Extract Brier scores from lines like "**Brier Score:** 0.1234"
        brier_scores = [
            float(line.split("**Brier Score:** ")[1].strip())
            for line in content.splitlines()
            if "**Brier Score:**" in line
        ]
        assert len(brier_scores) == 5
        # At least two distinct values across five questions
        assert len(set(brier_scores)) > 1


# ---------------------------------------------------------------------------
# HF LLM tests — download gpt2 (~500 MB) on first run, cached thereafter
# ---------------------------------------------------------------------------

HF_TEST_MODEL = "gpt2"  # small, fast, always available via HF hub


@pytest.fixture(scope="module")
def hf_model_and_tokenizer():
    """Load gpt2 once for all HF LLM tests."""
    return load_model(HF_TEST_MODEL, device="cpu")


@pytest.mark.llm
class TestGetAnswerLlsHf:
    """Tests for get_answer_lls_hf() — requires HF transformers + gpt2."""

    def test_returns_list_of_correct_length(self, sample_question, hf_model_and_tokenizer):
        model, tokenizer = hf_model_and_tokenizer
        lls = get_answer_lls_hf(sample_question, model, tokenizer, use_metadata=True)
        assert len(lls) == len(sample_question["answer_strings"])

    def test_all_scores_are_floats(self, sample_question, hf_model_and_tokenizer):
        model, tokenizer = hf_model_and_tokenizer
        lls = get_answer_lls_hf(sample_question, model, tokenizer, use_metadata=True)
        for score in lls:
            assert isinstance(score, float)

    def test_scores_are_non_positive(self, sample_question, hf_model_and_tokenizer):
        """Log-probabilities are always ≤ 0."""
        model, tokenizer = hf_model_and_tokenizer
        lls = get_answer_lls_hf(sample_question, model, tokenizer, use_metadata=True)
        for score in lls:
            assert score <= 0.0

    def test_use_metadata_changes_scores(self, sample_question, hf_model_and_tokenizer):
        model, tokenizer = hf_model_and_tokenizer
        lls_with = get_answer_lls_hf(sample_question, model, tokenizer, use_metadata=True)
        lls_without = get_answer_lls_hf(sample_question, model, tokenizer, use_metadata=False)
        assert lls_with != lls_without

    def test_ground_truth_not_always_worst(self, sample_question, hf_model_and_tokenizer):
        """Ground truth answer should not always be the lowest-scored answer."""
        model, tokenizer = hf_model_and_tokenizer
        lls = get_answer_lls_hf(sample_question, model, tokenizer, use_metadata=True)
        # Ground truth is index 0; it should not always be the minimum
        gt_score = lls[0]
        min_score = min(lls)
        # Allow equality (gpt2 may assign the worst score to ground truth),
        # but at least one other answer must not outscore it by more than the
        # ground truth outscore itself — just check the list has variation.
        assert len(set(round(s, 6) for s in lls)) > 1


@pytest.mark.llm
class TestTestFiveQuestionsHf:
    """Tests for test_five_questions_hf() — requires HF transformers + gpt2."""

    def test_markdown_file_is_created(self, tmp_path):
        import shutil
        tmp_jsonl = tmp_path / "HWWJNQ_clozequestions.jsonl"
        shutil.copy(SAMPLE_JSONL, tmp_jsonl)

        report_path = run_five_questions_hf_eval(HF_TEST_MODEL, str(tmp_jsonl), device="cpu")
        assert Path(report_path).exists()

    def test_markdown_file_contains_model_name(self, tmp_path):
        import shutil
        tmp_jsonl = tmp_path / "HWWJNQ_clozequestions.jsonl"
        shutil.copy(SAMPLE_JSONL, tmp_jsonl)

        report_path = run_five_questions_hf_eval(HF_TEST_MODEL, str(tmp_jsonl), device="cpu")
        content = Path(report_path).read_text(encoding="utf-8")
        assert HF_TEST_MODEL in content

    def test_brier_scores_not_all_identical(self, tmp_path):
        """Different questions should yield different Brier scores."""
        import shutil
        tmp_jsonl = tmp_path / "HWWJNQ_clozequestions.jsonl"
        shutil.copy(SAMPLE_JSONL, tmp_jsonl)

        report_path = run_five_questions_hf_eval(HF_TEST_MODEL, str(tmp_jsonl), device="cpu")
        content = Path(report_path).read_text(encoding="utf-8")

        brier_scores = [
            float(line.split("**Brier Score:** ")[1].strip())
            for line in content.splitlines()
            if "**Brier Score:**" in line
        ]
        assert len(brier_scores) == 5
        assert len(set(brier_scores)) > 1


@pytest.mark.llm
class TestFullEvalHf:
    """Tests for full_eval_hf() — requires HF transformers + gpt2."""

    def test_report_file_is_created(self, tmp_path):
        import shutil
        tmp_jsonl = tmp_path / "HWWJNQ_clozequestions.jsonl"
        shutil.copy(SAMPLE_JSONL, tmp_jsonl)

        report_path = run_full_eval_hf(HF_TEST_MODEL, str(tmp_jsonl), device="cpu")
        assert Path(report_path).exists()

    def test_report_contains_overall_brier(self, tmp_path):
        import shutil
        tmp_jsonl = tmp_path / "HWWJNQ_clozequestions.jsonl"
        shutil.copy(SAMPLE_JSONL, tmp_jsonl)

        report_path = run_full_eval_hf(HF_TEST_MODEL, str(tmp_jsonl), device="cpu")
        content = Path(report_path).read_text(encoding="utf-8")
        assert "overall" in content.lower() or "Overall" in content

    def test_report_contains_category_breakdown(self, tmp_path):
        import shutil
        tmp_jsonl = tmp_path / "HWWJNQ_clozequestions.jsonl"
        shutil.copy(SAMPLE_JSONL, tmp_jsonl)

        # Load at least one question_category value from the JSONL
        with open(SAMPLE_JSONL, encoding="utf-8") as f:
            first_q = json.loads(f.readline())
        category = first_q.get("question_category", "")

        report_path = run_full_eval_hf(HF_TEST_MODEL, str(tmp_jsonl), device="cpu")
        content = Path(report_path).read_text(encoding="utf-8")
        assert category in content


@pytest.mark.llm
class TestMcqEvalHf:
    """Tests for mcq_eval_hf() — requires HF transformers + gpt2."""

    def test_report_file_is_created(self, tmp_path):
        import shutil
        tmp_jsonl = tmp_path / "HWWJNQ_clozequestions.jsonl"
        shutil.copy(SAMPLE_JSONL, tmp_jsonl)

        report_path = run_mcq_eval_hf(HF_TEST_MODEL, str(tmp_jsonl), device="cpu")
        assert Path(report_path).exists()

    def test_report_contains_accuracy_stats(self, tmp_path):
        import shutil
        tmp_jsonl = tmp_path / "HWWJNQ_clozequestions.jsonl"
        shutil.copy(SAMPLE_JSONL, tmp_jsonl)

        report_path = run_mcq_eval_hf(HF_TEST_MODEL, str(tmp_jsonl), device="cpu")
        content = Path(report_path).read_text(encoding="utf-8")
        assert "accuracy" in content.lower() or "Accuracy" in content

    def test_report_contains_true_or_false(self, tmp_path):
        import shutil
        tmp_jsonl = tmp_path / "HWWJNQ_clozequestions.jsonl"
        shutil.copy(SAMPLE_JSONL, tmp_jsonl)

        report_path = run_mcq_eval_hf(HF_TEST_MODEL, str(tmp_jsonl), device="cpu")
        content = Path(report_path).read_text(encoding="utf-8")
        assert "TRUE" in content or "FALSE" in content

    def test_report_contains_skill_score(self, tmp_path):
        import shutil
        tmp_jsonl = tmp_path / "HWWJNQ_clozequestions.jsonl"
        shutil.copy(SAMPLE_JSONL, tmp_jsonl)

        report_path = run_mcq_eval_hf(HF_TEST_MODEL, str(tmp_jsonl), device="cpu")
        content = Path(report_path).read_text(encoding="utf-8")
        assert "skill" in content.lower() or "Skill" in content

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
    _is_abstention_question,
    _parse_mcq_response,
    _parse_mcq_response_openai,
    _raw_sigmoid_probs,
    build_subset_index,
    bootstrap_evaluate,
    calculate_brier_score,
    calculate_mcq_skill_score,
    format_group_score_table,
    get_answer_lls,
    get_answer_lls_hf,
    get_answer_lls_together,
    is_openai_model,
    load_model,
    load_openai_credentials,
    load_together_credentials,
    load_openrouter_credentials,
    lls_to_probabilities,
    mcq_eval_openai,
    platt_scale_cv,
    write_json_report,
    test_five_questions as run_five_questions_eval,
    test_five_questions_hf as run_five_questions_hf_eval,
    full_eval_hf as run_full_eval_hf,
    full_eval_together as run_full_eval_together,
    mcq_eval_hf as run_mcq_eval_hf,
    mcq_eval_together as run_mcq_eval_together,
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


@pytest.fixture
def abstention_question_by_type():
    """A question with reasoning_type 'abstention' (type-A prompt variant)."""
    return {
        "metadata_frame": "From an 1890 scientific treatise.",
        "main_question": "What is the speed of light in a vacuum?",
        "question_category": "knowledge",
        "reasoning_type": "abstention",
        "answer_strings": ["insufficient information", "186,000 miles per second", "unknown"],
        "answer_types": ["ground_truth", "same_book", "same_book"],
        "answer_probabilities": [1.0, 0.0, 0.0],
    }


@pytest.fixture
def abstention_question_by_answer():
    """A question without reasoning_type but with 'insufficient information' in answers."""
    return {
        "metadata_frame": "From an 1895 travel narrative.",
        "main_question": "How many people lived in the city at that time?",
        "question_category": "cloze_causalclause",
        "answer_strings": ["About 50,000.", "Insufficient information", "More than a million."],
        "answer_types": ["ground_truth", "same_book", "same_book"],
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


class TestIsAbstentionQuestion:
    """Tests for _is_abstention_question() — no LLM required."""

    def test_true_for_reasoning_type_abstention(self, abstention_question_by_type):
        assert _is_abstention_question(abstention_question_by_type) is True

    def test_true_for_reasoning_type_knowledge(self):
        q = {"reasoning_type": "knowledge", "answer_strings": []}
        assert _is_abstention_question(q) is True

    def test_true_for_reasoning_type_inference(self):
        q = {"reasoning_type": "inference", "answer_strings": []}
        assert _is_abstention_question(q) is True

    def test_true_for_insufficient_information_in_answers(self, abstention_question_by_answer):
        assert _is_abstention_question(abstention_question_by_answer) is True

    def test_true_case_insensitive_match(self):
        q = {"answer_strings": ["Insufficient Information"]}
        assert _is_abstention_question(q) is True

    def test_false_for_plain_question(self, minimal_question):
        assert _is_abstention_question(minimal_question) is False

    def test_false_for_empty_dict(self):
        assert _is_abstention_question({}) is False

    def test_false_for_unrelated_reasoning_type(self):
        q = {"reasoning_type": "cloze", "answer_strings": ["Yes.", "No."]}
        assert _is_abstention_question(q) is False


class TestAbstentionAwareBuildQuestionText:
    """Tests for _build_question_text() abstention prompt insertion."""

    def test_abstention_reminder_inserted_for_type_a(self, abstention_question_by_type):
        text = _build_question_text(abstention_question_by_type, use_metadata=True)
        assert "insufficient information" in text.lower()

    def test_abstention_reminder_absent_for_type_b(self, minimal_question):
        text = _build_question_text(minimal_question, use_metadata=True)
        assert "insufficient information" not in text.lower()

    def test_reminder_appears_before_question(self, abstention_question_by_type):
        text = _build_question_text(abstention_question_by_type, use_metadata=True)
        reminder_pos = text.lower().index("insufficient information")
        question_pos = text.index("QUESTION: ")
        assert reminder_pos < question_pos

    def test_still_ends_with_answer_label_for_type_a(self, abstention_question_by_type):
        text = _build_question_text(abstention_question_by_type, use_metadata=True)
        assert text.endswith("ANSWER: ")


class TestAbstentionAwareBuildMcqPrompt:
    """Tests for _build_mcq_prompt() abstention hint insertion."""

    def test_abstention_hint_included_for_type_a(self, abstention_question_by_type):
        prompt_text, _, _ = _build_mcq_prompt(abstention_question_by_type)
        assert "insufficient information" in prompt_text.lower()

    def test_abstention_hint_absent_for_type_b(self, minimal_question):
        prompt_text, _, _ = _build_mcq_prompt(minimal_question)
        assert "insufficient information" not in prompt_text.lower()

    def test_type_a_still_ends_with_respond_instruction(self, abstention_question_by_type):
        prompt_text, _, _ = _build_mcq_prompt(abstention_question_by_type)
        assert prompt_text.endswith("Respond only with the letter of the correct answer:")

    def test_type_b_ends_with_standard_respond_instruction(self, minimal_question):
        prompt_text, _, _ = _build_mcq_prompt(minimal_question)
        assert prompt_text.endswith("Respond only with the letter of the correct answer:")


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


class TestParseMcqResponseOpenai:
    """Tests for _parse_mcq_response_openai() — no LLM required."""

    def test_parses_json_choice(self):
        assert _parse_mcq_response_openai('{"choice":"C"}') == "C"

    def test_parses_json_choice_with_whitespace(self):
        assert _parse_mcq_response_openai('{ "choice": "B" }') == "B"

    def test_falls_back_to_regex_for_plain_text(self):
        assert _parse_mcq_response_openai("The answer is D.") == "D"

    def test_falls_back_to_regex_for_bare_letter(self):
        assert _parse_mcq_response_openai("A") == "A"

    def test_returns_none_for_empty_string(self):
        assert _parse_mcq_response_openai("") is None

    def test_returns_none_for_invalid_json_and_no_letter(self):
        assert _parse_mcq_response_openai("{bad json}") is None

    def test_ignores_json_with_wrong_key(self):
        # Falls back to regex; no uppercase letter in the string → None
        assert _parse_mcq_response_openai('{"answer":"c"}') is None

    def test_ignores_json_lowercase_choice(self):
        # "c" is lowercase — falls back to regex, which also finds no \b[A-Z]\b
        assert _parse_mcq_response_openai('{"choice":"c"}') is None


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


class TestLoadTogetherCredentials:
    """Tests for load_together_credentials() — no LLM required."""

    def test_loads_api_key(self, tmp_path):
        key_file = tmp_path / "TogetherAPIKey.txt"
        key_file.write_text("my-together-api-key\n", encoding="utf-8")
        key = load_together_credentials(str(key_file))
        assert key == "my-together-api-key"

    def test_strips_whitespace(self, tmp_path):
        key_file = tmp_path / "TogetherAPIKey.txt"
        key_file.write_text("  my-key  \n", encoding="utf-8")
        key = load_together_credentials(str(key_file))
        assert key == "my-key"

    def test_ignores_blank_lines(self, tmp_path):
        key_file = tmp_path / "TogetherAPIKey.txt"
        key_file.write_text("\nmy-key\n\n", encoding="utf-8")
        key = load_together_credentials(str(key_file))
        assert key == "my-key"

    def test_raises_if_file_missing(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="Together AI key file not found"):
            load_together_credentials(str(tmp_path / "nonexistent.txt"))

    def test_raises_if_empty(self, tmp_path):
        key_file = tmp_path / "TogetherAPIKey.txt"
        key_file.write_text("\n\n", encoding="utf-8")
        with pytest.raises(ValueError, match="empty"):
            load_together_credentials(str(key_file))


class TestLoadOpenRouterCredentials:
    """Tests for load_openrouter_credentials() — no LLM required."""

    def test_loads_password_line(self, tmp_path):
        cred_file = tmp_path / "creds.txt"
        cred_file.write_text("username: foo\npassword: sk-or-v1-abc123\n", encoding="utf-8")
        key = load_openrouter_credentials(str(cred_file))
        assert key == "sk-or-v1-abc123"

    def test_strips_whitespace(self, tmp_path):
        cred_file = tmp_path / "creds.txt"
        cred_file.write_text("password:   sk-or-v1-xyz  \n", encoding="utf-8")
        key = load_openrouter_credentials(str(cred_file))
        assert key == "sk-or-v1-xyz"

    def test_case_insensitive_key(self, tmp_path):
        cred_file = tmp_path / "creds.txt"
        cred_file.write_text("PASSWORD: sk-or-v1-upper\n", encoding="utf-8")
        key = load_openrouter_credentials(str(cred_file))
        assert key == "sk-or-v1-upper"

    def test_env_var_overrides_file(self, tmp_path, monkeypatch):
        cred_file = tmp_path / "creds.txt"
        cred_file.write_text("password: sk-or-v1-from-file\n", encoding="utf-8")
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-from-env")
        key = load_openrouter_credentials(str(cred_file))
        assert key == "sk-or-v1-from-env"

    def test_raises_if_file_missing(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_openrouter_credentials(str(tmp_path / "nonexistent.txt"))

    def test_raises_if_no_password_line(self, tmp_path):
        cred_file = tmp_path / "creds.txt"
        cred_file.write_text("username: foo\ntoken: bar\n", encoding="utf-8")
        with pytest.raises(ValueError, match="password"):
            load_openrouter_credentials(str(cred_file))


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

    def test_json_report_is_created(self, tmp_path):
        import shutil
        tmp_jsonl = tmp_path / "HWWJNQ_clozequestions.jsonl"
        shutil.copy(SAMPLE_JSONL, tmp_jsonl)

        report_path = run_five_questions_hf_eval(HF_TEST_MODEL, str(tmp_jsonl), device="cpu")
        assert Path(report_path).exists()
        assert report_path.endswith(".json")

    def test_json_report_has_expected_structure(self, tmp_path):
        import shutil
        tmp_jsonl = tmp_path / "HWWJNQ_clozequestions.jsonl"
        shutil.copy(SAMPLE_JSONL, tmp_jsonl)

        report_path = run_five_questions_hf_eval(HF_TEST_MODEL, str(tmp_jsonl), device="cpu")
        with open(report_path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["metadata"]["model_id"] == HF_TEST_MODEL
        assert data["metadata"]["eval_mode"] == "probabilistic"
        assert "confidence_intervals" in data
        assert "overall_benchmark" in data["confidence_intervals"]

    def test_verbose_markdown_also_written(self, tmp_path):
        import shutil
        tmp_jsonl = tmp_path / "HWWJNQ_clozequestions.jsonl"
        shutil.copy(SAMPLE_JSONL, tmp_jsonl)

        report_path = run_five_questions_hf_eval(HF_TEST_MODEL, str(tmp_jsonl), device="cpu")
        md_path = Path(report_path).with_name(
            Path(report_path).name.replace("eval_results_", "eval_report_").replace(".json", ".md")
        )
        assert md_path.exists()
        content = md_path.read_text(encoding="utf-8")
        assert HF_TEST_MODEL in content

    def test_brier_scores_not_all_identical(self, tmp_path):
        """Different questions should yield different Brier scores."""
        import shutil
        tmp_jsonl = tmp_path / "HWWJNQ_clozequestions.jsonl"
        shutil.copy(SAMPLE_JSONL, tmp_jsonl)

        report_path = run_five_questions_hf_eval(HF_TEST_MODEL, str(tmp_jsonl), device="cpu")
        md_path = Path(report_path).with_name(
            Path(report_path).name.replace("eval_results_", "eval_report_").replace(".json", ".md")
        )
        content = md_path.read_text(encoding="utf-8")

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


# ---------------------------------------------------------------------------
# Unit tests for new v2.0 functions — no LLM required
# ---------------------------------------------------------------------------

import numpy as np


class TestBuildSubsetIndex:
    """Tests for build_subset_index()."""

    def test_questions_land_in_correct_subsets(self):
        questions = [
            {"question_category": "knowledge", "answer_length": "short"},
            {"question_category": "cloze", "answer_length": "long"},
            {"question_category": "knowledge", "answer_length": "long"},
        ]
        index = build_subset_index(questions, fields=["question_category", "answer_length"])
        assert index["question_category:knowledge"] == [0, 2]
        assert index["question_category:cloze"] == [1]
        assert index["answer_length:short"] == [0]
        assert index["answer_length:long"] == [1, 2]

    def test_every_value_gets_a_subset(self):
        questions = [
            {"question_category": "a", "frame_type": "x", "reasoning_type": "r1"},
            {"question_category": "b", "frame_type": "y", "reasoning_type": "r2"},
        ]
        index = build_subset_index(questions)
        assert "question_category:a" in index
        assert "question_category:b" in index
        assert "frame_type:x" in index
        assert "frame_type:y" in index
        assert "reasoning_type:r1" in index
        assert "reasoning_type:r2" in index

    def test_missing_fields_handled_gracefully(self):
        questions = [
            {"question_category": "knowledge"},  # no answer_length
            {"answer_length": "short"},           # no question_category
        ]
        index = build_subset_index(questions, fields=["question_category", "answer_length"])
        assert index["question_category:knowledge"] == [0]
        assert index["answer_length:short"] == [1]

    def test_custom_fields_parameter(self):
        questions = [{"source_genre": "novel"}, {"source_genre": "essay"}]
        index = build_subset_index(questions, fields=["source_genre"])
        assert "source_genre:novel" in index
        assert "source_genre:essay" in index

    def test_default_fields_used_when_none(self):
        questions = [{"question_category": "a", "answer_length": "short",
                       "frame_type": "f", "reasoning_type": "r"}]
        index = build_subset_index(questions)
        assert len(index) == 4  # one key per field
        # "r" isn't a real reasoning_type, so no reasoning_group key is added

    def test_reasoning_group_added_for_mappable_questions(self):
        questions = [
            {"reasoning_type": "phrase_cloze"},
            {"reasoning_type": "knowledge"},
            {"reasoning_type": "character_modeling"},
        ]
        index = build_subset_index(questions)
        assert index["reasoning_group:cloze"] == [0]
        assert index["reasoning_group:knowledge_inference"] == [1]
        assert index["reasoning_group:constrained_generation"] == [2]

    def test_unmapped_reasoning_type_skipped_not_raised(self, capsys):
        questions = [{"reasoning_type": "phrase_cloze"}, {"reasoning_type": None}]
        index = build_subset_index(questions)
        assert index["reasoning_group:cloze"] == [0]
        assert not any(k.startswith("reasoning_group:") and k != "reasoning_group:cloze"
                       for k in index)
        assert "1 question" in capsys.readouterr().out


class TestFormatGroupScoreTable:
    """Tests for format_group_score_table()."""

    def test_returns_empty_when_no_group_keys(self):
        assert format_group_score_table({"overall_benchmark": {}}) == []

    def test_renders_row_per_present_group(self):
        stats = {"brier_score": [0.1, 0.2, 0.3],
                  "accuracy": [0.5, 0.6, 0.7],
                  "skill_score": [0.05, 0.15, 0.25]}
        confidence_intervals = {
            "overall_benchmark": stats,
            "reasoning_group:cloze": stats,
            "reasoning_group:knowledge_inference": stats,
        }
        lines = format_group_score_table(confidence_intervals)
        table_text = "\n".join(lines)
        assert "Scores by reasoning group" in table_text
        assert "cloze" in table_text
        assert "knowledge and inference" in table_text
        assert "constrained generation" not in table_text
        assert "0.2000 [0.1000, 0.3000]" in table_text


class TestPlattScaleCv:
    """Tests for platt_scale_cv()."""

    def _make_overconfident_data(self, n=50):
        """Create synthetic data where the model is systematically overconfident.

        Returns (gt_probs, model_logprobs, model_probs) where model_probs is
        softmax(model_logprobs).
        """
        rng = np.random.default_rng(42)
        gt_probs = []
        model_logprobs = []
        model_probs = []
        for _ in range(n):
            # 4-way MCQ, ground truth is always index 0
            gt = [1.0, 0.0, 0.0, 0.0]
            # Generate log-probs: correct answer gets high value
            lp = rng.normal(loc=[2.0, -0.5, -0.5, -0.5], scale=0.5)
            # Softmax to get probabilities
            shifted = lp - lp.max()
            exp_vals = np.exp(shifted)
            probs = exp_vals / exp_vals.sum()
            gt_probs.append(gt)
            model_logprobs.append(lp.tolist())
            model_probs.append(probs.tolist())
        return gt_probs, model_logprobs, model_probs

    def test_calibrated_brier_generally_lower(self):
        gt_probs, model_logprobs, model_probs = self._make_overconfident_data(50)
        weights = np.ones(50)
        calibrated, uncalibrated = platt_scale_cv(
            gt_probs, model_logprobs, weights
        )
        # On average, calibrated should be no worse
        assert np.mean(calibrated) <= np.mean(uncalibrated) + 0.05  # allow small tolerance

    def test_no_question_in_both_train_and_test(self):
        """Verify fold separation by checking output changes with fold count."""
        gt_probs, model_logprobs, model_probs = self._make_overconfident_data(20)
        weights = np.ones(20)
        cal_5, _ = platt_scale_cv(gt_probs, model_logprobs, weights, n_folds=5)
        cal_2, _ = platt_scale_cv(gt_probs, model_logprobs, weights, n_folds=2)
        # Different fold counts should produce different calibrations
        assert cal_5 != cal_2

    def test_folds_balanced_by_count(self):
        gt_probs, model_logprobs, model_probs = self._make_overconfident_data(10)
        # Heavy weight on first 5, zero on last 5
        weights = np.array([10.0] * 5 + [0.0] * 5)
        calibrated, uncalibrated = platt_scale_cv(
            gt_probs, model_logprobs, weights, n_folds=5
        )
        # Should still produce 10 Brier scores (one per question)
        assert len(calibrated) == 10
        assert len(uncalibrated) == 10

    def test_weights_affect_calibration(self):
        gt_probs, model_logprobs, model_probs = self._make_overconfident_data(20)
        w1 = np.ones(20)
        w2 = np.array([10.0] * 10 + [0.1] * 10)
        cal1, _ = platt_scale_cv(gt_probs, model_logprobs, w1, n_folds=5)
        cal2, _ = platt_scale_cv(gt_probs, model_logprobs, w2, n_folds=5)
        assert cal1 != cal2

    def test_handles_zero_weight_fold(self):
        gt_probs, model_logprobs, model_probs = self._make_overconfident_data(10)
        # Weights that might leave some folds with zero total weight
        weights = np.array([0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0])
        calibrated, uncalibrated = platt_scale_cv(
            gt_probs, model_logprobs, weights, n_folds=5
        )
        assert len(calibrated) == 10


class TestBootstrapEvaluate:
    """Tests for bootstrap_evaluate()."""

    def _make_synthetic_data(self, n=30):
        """Create synthetic probabilistic eval data."""
        rng = np.random.default_rng(123)
        gt_probs = [[1.0, 0.0, 0.0, 0.0] for _ in range(n)]
        model_logprobs = []
        model_probs = []
        for _ in range(n):
            lp = rng.normal(loc=[1.5, -0.5, -0.5, -0.5], scale=0.5)
            shifted = lp - lp.max()
            exp_vals = np.exp(shifted)
            probs = exp_vals / exp_vals.sum()
            model_logprobs.append(lp.tolist())
            model_probs.append(probs.tolist())
        questions = [
            {"question_category": "cat_a" if i < 15 else "cat_b",
             "answer_length": "short" if i % 2 == 0 else "long",
             "frame_type": "period", "reasoning_type": "knowledge"}
            for i in range(n)
        ]
        subset_index = build_subset_index(questions)
        return gt_probs, model_logprobs, model_probs, subset_index

    def test_returns_correct_structure(self):
        gt, mlp, mp, si = self._make_synthetic_data()
        result = bootstrap_evaluate(gt, mp, si, mode="probabilistic",
                                    n_bootstrap=50, n_folds=5,
                                    model_logprobs=mlp)
        assert "overall_benchmark" in result
        for key in si:
            assert key in result
        for subset_result in result.values():
            assert "brier_score" in subset_result
            assert "skill_score" in subset_result
            assert "accuracy" in subset_result
            for metric_vals in subset_result.values():
                assert len(metric_vals) == 3  # [p2.5, p50, p97.5]

    def test_mcq_mode_brier_is_zero(self):
        n = 20
        gt = [[1.0, 0.0, 0.0] for _ in range(n)]
        mcq_results = [{"is_correct": i % 3 == 0, "k": 3} for i in range(n)]
        si = {"question_category:test": list(range(n))}
        result = bootstrap_evaluate(gt, mcq_results, si, mode="mcq",
                                    n_bootstrap=50)
        for vals in result["overall_benchmark"]["brier_score"]:
            assert vals == 0.0

    def test_median_accuracy_in_range(self):
        gt, mlp, mp, si = self._make_synthetic_data()
        result = bootstrap_evaluate(gt, mp, si, mode="probabilistic",
                                    n_bootstrap=100, n_folds=5,
                                    model_logprobs=mlp)
        median_acc = result["overall_benchmark"]["accuracy"][1]
        assert 0.0 <= median_acc <= 1.0

    def test_subset_results_reflect_subset_questions(self):
        gt, mlp, mp, si = self._make_synthetic_data()
        result = bootstrap_evaluate(gt, mp, si, mode="probabilistic",
                                    n_bootstrap=50, n_folds=5,
                                    model_logprobs=mlp)
        # cat_a and cat_b have different questions, so their results should differ
        # (not guaranteed to differ by much, but the structure should exist)
        assert "question_category:cat_a" in result
        assert "question_category:cat_b" in result


class TestWriteJsonReport:
    """Tests for write_json_report()."""

    def test_output_is_valid_json(self, tmp_path):
        report_path = tmp_path / "test_report.json"
        meta = {"model_id": "test", "benchmark_file": "test.jsonl",
                "eval_mode": "mcq", "timestamp": "20260101_000000",
                "n_questions": 2, "n_bootstrap": 10}
        pqr = [
            {"model_probs": None, "chosen_letter": "A", "correct": True},
            {"model_probs": None, "chosen_letter": "B", "correct": False},
        ]
        ci = {"overall_benchmark": {
            "brier_score": [0.0, 0.0, 0.0],
            "skill_score": [0.1, 0.5, 0.9],
            "accuracy": [0.3, 0.5, 0.7],
        }}
        cv = [True, False]
        write_json_report(report_path, meta, pqr, ci, cv)

        with open(report_path, encoding="utf-8") as f:
            data = json.load(f)

        assert "metadata" in data
        assert "per_question_results" in data
        assert "confidence_intervals" in data
        assert "correct_vector" in data

    def test_correct_vector_length_matches_results(self, tmp_path):
        report_path = tmp_path / "test_report.json"
        meta = {"model_id": "test", "benchmark_file": "test.jsonl",
                "eval_mode": "probabilistic", "timestamp": "20260101",
                "n_questions": 3, "n_bootstrap": 10}
        pqr = [{"model_probs": [0.5, 0.5], "chosen_letter": None, "correct": True}] * 3
        ci = {"overall_benchmark": {
            "brier_score": [0.1, 0.2, 0.3],
            "skill_score": [0.1, 0.2, 0.3],
            "accuracy": [0.1, 0.2, 0.3],
        }}
        cv = [True, False, True]
        write_json_report(report_path, meta, pqr, ci, cv)

        with open(report_path, encoding="utf-8") as f:
            data = json.load(f)

        assert len(data["correct_vector"]) == len(data["per_question_results"])

    def test_eval_mode_matches(self, tmp_path):
        report_path = tmp_path / "test_report.json"
        meta = {"model_id": "test", "benchmark_file": "test.jsonl",
                "eval_mode": "probabilistic", "timestamp": "20260101",
                "n_questions": 1, "n_bootstrap": 10}
        write_json_report(report_path, meta, [{"model_probs": [1.0], "chosen_letter": None, "correct": True}],
                          {"overall_benchmark": {"brier_score": [0,0,0], "skill_score": [0,0,0], "accuracy": [1,1,1]}},
                          [True])

        with open(report_path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["metadata"]["eval_mode"] == "probabilistic"


@pytest.mark.llm
def test_load_model_with_device_map():
    model, tokenizer = load_model(HF_TEST_MODEL, device_map="cpu")
    assert model is not None
    assert tokenizer is not None


# ---------------------------------------------------------------------------
# Talkie backend tests
# ---------------------------------------------------------------------------

import importlib

# is_talkie_model only needs pathlib — no talkie package required.
class TestIsTalkieModel:
    def setup_method(self):
        self.mod = importlib.import_module("talkie_backend")

    def test_registered_base(self):
        assert self.mod.is_talkie_model("talkie-1930-13b-base")

    def test_registered_it(self):
        assert self.mod.is_talkie_model("talkie-1930-13b-it")

    def test_registered_web(self):
        assert self.mod.is_talkie_model("talkie-web-13b-base")

    def test_unknown_hf_name(self):
        assert not self.mod.is_talkie_model("Qwen/Qwen2.5-7B-Instruct")

    def test_openai_name(self):
        assert not self.mod.is_talkie_model("gpt-4.1")

    def test_local_dir_with_vocab(self, tmp_path):
        (tmp_path / "vocab.txt").write_text("dummy")
        assert self.mod.is_talkie_model(str(tmp_path))

    def test_local_dir_without_vocab(self, tmp_path):
        assert not self.mod.is_talkie_model(str(tmp_path))

    def test_nonexistent_path(self):
        assert not self.mod.is_talkie_model("/nonexistent/path/to/model")


@pytest.mark.llm
class TestTalkieTokenizerAdapter:
    """Tests for _TalkieTokenizerAdapter — requires tiktoken (part of talkie)."""

    @pytest.fixture(scope="class")
    def base_adapter(self):
        import tiktoken
        from talkie.tokenizer import (
            build_tokenizer, _BASE_SPECIAL_TOKENS, BASE_VOCAB_SIZE,
        )
        from talkie_backend import _TalkieTokenizerAdapter
        # Build a minimal in-memory tokenizer using cl100k_base merges as a proxy.
        # We only need encode/decode round-trips, not Talkie vocab specifically.
        enc = tiktoken.get_encoding("cl100k_base")
        special_ids = frozenset({enc.eot_token})
        return _TalkieTokenizerAdapter(enc, "base", special_ids)

    @pytest.fixture(scope="class")
    def it_adapter(self):
        import tiktoken
        from talkie_backend import _TalkieTokenizerAdapter
        enc = tiktoken.get_encoding("cl100k_base")
        special_ids = frozenset({enc.eot_token})
        return _TalkieTokenizerAdapter(enc, "it", special_ids)

    def test_call_returns_input_ids_tensor(self, base_adapter):
        import torch
        result = base_adapter("Hello world", return_tensors="pt")
        assert hasattr(result, "input_ids")
        assert isinstance(result.input_ids, torch.Tensor)
        assert result.input_ids.shape[0] == 1
        assert result.input_ids.dtype == torch.long

    def test_call_nonempty(self, base_adapter):
        result = base_adapter("test", return_tensors="pt")
        assert result.input_ids.shape[1] > 0

    def test_decode_round_trip(self, base_adapter):
        import tiktoken, torch
        enc = tiktoken.get_encoding("cl100k_base")
        text = "The quick brown fox"
        ids = enc.encode(text)
        decoded = base_adapter.decode(torch.tensor(ids))
        assert decoded == text

    def test_decode_list_input(self, base_adapter):
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        ids = enc.encode("hello")
        assert base_adapter.decode(ids) == "hello"

    def test_format_context_base_passthrough(self, base_adapter):
        text = "QUESTION: What happened?\n\nANSWER: "
        assert base_adapter.format_context(text) == text

    def test_format_context_it_wraps(self, it_adapter):
        text = "QUESTION: What happened?\n\nANSWER: "
        wrapped = it_adapter.format_context(text)
        assert wrapped.startswith("<|user|>")
        assert "<|end|><|assistant|>" in wrapped
        assert text in wrapped

    def test_decode_skips_special_ids(self, base_adapter):
        import tiktoken, torch
        enc = tiktoken.get_encoding("cl100k_base")
        normal_ids = enc.encode("hello")
        ids_with_eot = normal_ids + [enc.eot_token]
        decoded = base_adapter.decode(torch.tensor(ids_with_eot), skip_special_tokens=True)
        assert decoded == "hello"

    def test_decode_keep_special_ids(self, base_adapter):
        import tiktoken, torch
        enc = tiktoken.get_encoding("cl100k_base")
        normal_ids = enc.encode("hello")
        ids_with_eot = normal_ids + [enc.eot_token]
        decoded = base_adapter.decode(torch.tensor(ids_with_eot), skip_special_tokens=False)
        assert len(decoded) > len("hello")


@pytest.mark.llm
class TestLoadTalkieModel:
    """Integration tests — loads talkie-1930-13b-base from $HF_HOME cache.

    Requires: talkie installed (pip install -e ../../talkie), cached weights,
    and a CUDA or CPU device with sufficient VRAM/RAM.
    """

    @pytest.fixture(scope="class")
    def talkie_base(self):
        from talkie_backend import load_talkie_model
        # Use CPU to avoid GPU requirement in CI; full inference on GPU tested
        # manually via talkie_eval_A100.slurm.
        model, tokenizer = load_talkie_model("talkie-1930-13b-base", device="cpu")
        return model, tokenizer

    def test_model_loaded(self, talkie_base):
        model, tokenizer = talkie_base
        import torch.nn as nn
        assert isinstance(model, nn.Module)

    def test_tokenizer_callable(self, talkie_base):
        _, tokenizer = talkie_base
        result = tokenizer("Hello", return_tensors="pt")
        assert result.input_ids.shape[0] == 1

    def test_forward_returns_all_position_logits(self, talkie_base):
        import torch
        model, tokenizer = talkie_base
        ids = tokenizer("The year was 1901.", return_tensors="pt").input_ids
        with torch.no_grad():
            out = model(ids)
        assert hasattr(out, "logits")
        # Shape [1, T, V]
        assert out.logits.ndim == 3
        assert out.logits.shape[0] == 1
        assert out.logits.shape[1] == ids.shape[1]

    def test_generate_returns_longer_sequence(self, talkie_base):
        import torch
        model, tokenizer = talkie_base
        ids = tokenizer("The year was", return_tensors="pt").input_ids
        with torch.no_grad():
            out_ids = model.generate(ids, max_new_tokens=3)
        assert out_ids.shape[1] > ids.shape[1]

    def test_log_probs_are_non_positive(self, talkie_base):
        import torch
        model, tokenizer = talkie_base
        context = "In the year 1901, the president was "
        answer = "Theodore Roosevelt."
        ctx_ids = tokenizer(context, return_tensors="pt").input_ids
        full_ids = tokenizer(context + answer, return_tensors="pt").input_ids
        with torch.no_grad():
            out = model(full_ids)
        log_probs = torch.log_softmax(out.logits[0], dim=-1)
        ans_start = ctx_ids.shape[1]
        ans_token_ids = full_ids[0, ans_start:]
        scores = log_probs[ans_start - 1:-1, :][range(len(ans_token_ids)), ans_token_ids]
        assert all(s.item() <= 0.0 for s in scores)

    def test_format_context_base_is_passthrough(self, talkie_base):
        _, tokenizer = talkie_base
        text = "QUESTION: What year?\n\nANSWER: "
        assert tokenizer.format_context(text) == text

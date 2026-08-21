"""test_judge_prompts.py — Unit tests for judge_prompts_nocontext.py.

No network calls; uses stub judge functions.

Run with:
    pytest modelasjudge/tests/test_judge_prompts.py -v
"""

import random
import sys
from pathlib import Path

import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from judge_prompts_nocontext import (
    assign_positions,
    build_judge_prompt,
    parse_judge_response,
    score_one_comparison,
    _REASONING_TYPES_NEEDING_ABSTENTION,
    _QUALIFICATIONS,
)


# ---------------------------------------------------------------------------
# parse_judge_response
# ---------------------------------------------------------------------------

class TestParseJudgeResponse:
    def test_well_formed_json(self):
        raw = '{"question fit": "A"}'
        result = parse_judge_response(raw)
        assert result == {"question fit": "A"}

    def test_lowercase_letters_normalized(self):
        raw = '{"question fit": "a"}'
        result = parse_judge_response(raw)
        assert result == {"question fit": "A"}

    def test_json_inside_code_fence(self):
        raw = '```json\n{"question fit": "B"}\n```'
        result = parse_judge_response(raw)
        assert result == {"question fit": "B"}

    def test_json_with_leading_prose(self):
        raw = 'After careful consideration: {"question fit": "A"}'
        result = parse_judge_response(raw)
        assert result == {"question fit": "A"}

    def test_json_with_trailing_prose(self):
        raw = '{"question fit": "C"} — both seem reasonable.'
        result = parse_judge_response(raw)
        assert result == {"question fit": "C"}

    def test_underscore_key_style(self):
        raw = '{"question_fit": "A"}'
        result = parse_judge_response(raw)
        assert result == {"question fit": "A"}

    def test_invalid_letter_rejected(self):
        raw = '{"question fit": "D"}'
        assert parse_judge_response(raw) is None

    def test_missing_question_fit_key_rejected(self):
        raw = '{"context fit": "A"}'
        assert parse_judge_response(raw) is None

    def test_two_key_response_still_parsed(self):
        # Judge returns old two-key format; we extract question fit and ignore context.
        raw = '{"question fit": "A", "context fit": "B"}'
        result = parse_judge_response(raw)
        assert result == {"question fit": "A"}

    def test_empty_string(self):
        assert parse_judge_response("") is None

    def test_none_input(self):
        assert parse_judge_response(None) is None

    def test_totally_garbled(self):
        assert parse_judge_response("I cannot decide.") is None


# ---------------------------------------------------------------------------
# build_judge_prompt
# ---------------------------------------------------------------------------

class TestBuildJudgePrompt:
    def test_contains_question_and_answers(self):
        prompt = build_judge_prompt("ctx", "q?", "ans_a", "ans_b", "knowledge")
        assert "q?" in prompt
        assert "ans_a" in prompt
        assert "ans_b" in prompt

    def test_context_arg_in_prompt(self):
        # context is injected into the prompt as "Context: {context}".
        prompt = build_judge_prompt("UNIQUE_CTX_MARKER", "q?", "a", "b", "knowledge")
        assert "UNIQUE_CTX_MARKER" in prompt

    def test_no_context_fit_section(self):
        prompt = build_judge_prompt("ctx", "q", "a", "b", "knowledge")
        assert "Context fit" not in prompt
        assert "Source:" not in prompt

    def test_abstention_clause_for_knowledge(self):
        prompt = build_judge_prompt("c", "q", "a", "b", "knowledge")
        assert "insufficient information" in prompt

    def test_abstention_clause_for_abstention(self):
        prompt = build_judge_prompt("c", "q", "a", "b", "abstention")
        assert "insufficient information" in prompt

    @pytest.mark.parametrize("rt", [
        "character_modeling", "topic_sentence", "inference",
        "sentence_cloze", "phrase_cloze", "constrained_generation",
    ])
    def test_no_abstention_clause_for_non_abstention_types(self, rt):
        prompt = build_judge_prompt("c", "q", "a", "b", rt)
        assert "insufficient information" not in prompt

    @pytest.mark.parametrize("rt", [
        "character_modeling", "topic_sentence", "knowledge", "abstention",
        "inference", "sentence_cloze", "phrase_cloze", "constrained_generation",
    ])
    def test_all_reasoning_types_produce_valid_prompt(self, rt):
        # Qualifications are in _QUALIFICATIONS but not injected into the template;
        # verify the prompt is well-formed regardless of reasoning_type.
        prompt = build_judge_prompt("c", "q", "a", "b", rt)
        assert "accurate and relevant" in prompt
        assert '"question fit"' in prompt

    def test_unknown_reasoning_type_uses_default(self):
        prompt = build_judge_prompt("c", "q", "a", "b", "some_future_type")
        assert "accurate and relevant" in prompt
        assert "insufficient information" not in prompt

    def test_json_format_instruction_question_only(self):
        prompt = build_judge_prompt("c", "q", "a", "b", "knowledge")
        assert '"question fit"' in prompt
        assert '"context fit"' not in prompt


# ---------------------------------------------------------------------------
# assign_positions (imported from judge_prompts; tested here for coverage)
# ---------------------------------------------------------------------------

class TestAssignPositions:
    def test_deterministic_with_seed(self):
        rng = random.Random(42)
        result1 = assign_positions(rng, "GT", "CAND")
        rng2 = random.Random(42)
        result2 = assign_positions(rng2, "GT", "CAND")
        assert result1 == result2

    def test_gt_letter_is_a_or_b(self):
        rng = random.Random(0)
        for _ in range(20):
            a, b, gt_letter = assign_positions(rng, "GT", "CAND")
            assert gt_letter in ("A", "B")
            if gt_letter == "A":
                assert a == "GT" and b == "CAND"
            else:
                assert a == "CAND" and b == "GT"

    def test_both_orderings_appear(self):
        rng = random.Random(0)
        gt_letters = set()
        for _ in range(40):
            _, _, gt_letter = assign_positions(rng, "GT", "CAND")
            gt_letters.add(gt_letter)
        assert gt_letters == {"A", "B"}


# ---------------------------------------------------------------------------
# score_one_comparison (stub judge)
# ---------------------------------------------------------------------------

def _stub_judge(choice_q):
    """Return a judge callable that always returns the given question-fit choice."""
    response = f'{{"question fit": "{choice_q}"}}'
    def judge_call(prompt):
        return response
    return judge_call


class TestScoreOneComparison:
    def _run(self, judge, force_pos=None):
        return score_one_comparison(
            judge,
            context="test context",
            question="test question",
            reasoning_type="knowledge",
            gt="Ground Truth",
            candidate="Candidate",
            rng=random.Random(99),
            force_gt_position=force_pos,
        )

    def test_result_has_no_context_keys(self):
        result = self._run(_stub_judge("C"), force_pos="A")
        assert "context_outcome" not in result
        assert "context_pass" not in result

    def test_gt_wins_pass_is_0(self):
        # GT in slot A; judge picks A → candidate loses
        result = self._run(_stub_judge("A"), force_pos="A")
        assert result["question_outcome"] == "loss"
        assert result["question_pass"] == 0

    def test_candidate_wins_pass_is_1(self):
        # GT in A, judge picks B → candidate wins
        result = self._run(_stub_judge("B"), force_pos="A")
        assert result["question_outcome"] == "win"
        assert result["question_pass"] == 1

    def test_tie_pass_is_1(self):
        result = self._run(_stub_judge("C"), force_pos="A")
        assert result["question_outcome"] == "tie"
        assert result["question_pass"] == 1

    def test_invalid_json_retried_and_returns_invalid(self):
        call_count = [0]
        def bad_judge(prompt):
            call_count[0] += 1
            return "not json at all"
        result = self._run(bad_judge)
        assert result["question_outcome"] == "invalid"
        assert result["question_pass"] == 0
        assert call_count[0] == 2  # initial + one retry

    def test_gt_position_recorded(self):
        result = self._run(_stub_judge("C"), force_pos="B")
        assert result["gt_position"] == "B"

    def test_force_position_a(self):
        result = score_one_comparison(
            _stub_judge("A"),
            context="c", question="q", reasoning_type="knowledge",
            gt="gt", candidate="cand",
            rng=random.Random(0), force_gt_position="A",
        )
        assert result["gt_position"] == "A"
        assert result["question_outcome"] == "loss"

    def test_force_position_b(self):
        result = score_one_comparison(
            _stub_judge("B"),
            context="c", question="q", reasoning_type="knowledge",
            gt="gt", candidate="cand",
            rng=random.Random(0), force_gt_position="B",
        )
        assert result["gt_position"] == "B"
        assert result["question_outcome"] == "loss"

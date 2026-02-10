"""
Tests for distractor_generator helpers: format_length_spec, get_term_spec,
and ANACHRONISTIC_PROMPT formatting.

No LLM calls — these test prompt assembly logic only.
"""

import re
import pytest
import sys
from pathlib import Path

# Add parent directory to path so we can import batchconnectors modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from distractor_generator_wcats import (
    format_length_spec,
    get_term_spec,
    ANACHRONISTIC_PROMPT,
    CONNECTOR_TERMS,
)


class TestFormatLengthSpec:
    """Tests for format_length_spec()."""

    def test_clause_short(self):
        result = format_length_spec(5, is_clause=True)
        assert result == "clause of roughly 4 words"

    def test_clause_medium(self):
        result = format_length_spec(12, is_clause=True)
        assert result == "clause of roughly 12 words"

    def test_sentence_long(self):
        # 21 / 2 = 10.5, round(10.5) = 10 (banker's rounding), 10 * 2 = 20
        result = format_length_spec(21, is_clause=False)
        assert result == "sentence of roughly 20 words"

    def test_odd_rounds_to_even(self):
        # 7 -> round(3.5)*2 = 8
        assert "8 words" in format_length_spec(7, is_clause=True)
        # 13 -> round(6.5)*2 = 14  (Python rounds half to even: round(6.5)=6)
        assert "12 words" in format_length_spec(13, is_clause=True)
        # 15 -> round(7.5)*2 = 16  (round(7.5)=8)
        assert "16 words" in format_length_spec(15, is_clause=True)

    def test_minimum_floor(self):
        result = format_length_spec(1, is_clause=True)
        assert "roughly 2 words" in result

    def test_zero_gets_floor(self):
        result = format_length_spec(0, is_clause=False)
        assert "roughly 2 words" in result

    def test_contains_roughly(self):
        for n in [3, 8, 14, 25]:
            for is_clause in [True, False]:
                result = format_length_spec(n, is_clause)
                assert "roughly" in result


class TestGetTermSpec:
    """Tests for get_term_spec()."""

    def test_each_category_has_all_triggers(self):
        expected_triggers = {
            'causalsentence': ['justification', 'rationale', 'purpose', 'cause', 'because'],
            'causalclause': ['because', 'since', 'as', 'in order to', 'for', 'seeing that',
                             'owing to', 'inasmuch', 'forasmuch'],
            'effectsentence': ['so', 'hence', 'thus', 'therefore', 'thence', 'accordingly',
                               'consequence', 'result', 'effect', 'consequently',
                               'it follows that'],
            'effectclause': ['so', 'then'],
            'contrastsentence': ['but', 'yet', 'however', 'nevertheless'],
            'contrastclause': ['but', 'however', 'nevertheless'],
            'conditionalclause': ['if', 'provided that', 'insofar as', 'unless'],
            'concessiveclause': ['although', 'though', 'even though', 'even if', 'albeit', 'while'],
        }
        for cat, triggers in expected_triggers.items():
            spec = get_term_spec(cat)
            for trigger in triggers:
                assert trigger in spec, (
                    f"Category {cat!r}: expected {trigger!r} in {spec!r}"
                )

    def test_last_term_preceded_by_or(self):
        for cat in CONNECTOR_TERMS:
            spec = get_term_spec(cat)
            # The pattern should be "..., or <last_term>"
            assert ", or " in spec, (
                f"Category {cat!r}: expected ', or ' in {spec!r}"
            )

    def test_none_category(self):
        result = get_term_spec(None)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_unknown_category(self):
        result = get_term_spec("nonexistent_category")
        assert isinstance(result, str)
        assert len(result) > 0
        # Should be the generic fallback
        assert result == "a connecting word or phrase"


class TestAnachronisticPromptFormatting:
    """Tests that format the ANACHRONISTIC_PROMPT template — no LLM calls."""

    def test_clause_prompt_format(self):
        length_spec = format_length_spec(10, is_clause=True)
        term_spec = get_term_spec('causalclause')
        question_text = "Some metadata\n\nSome passage\n\nWrite a clause:"

        result = ANACHRONISTIC_PROMPT.format(
            length_spec=length_spec,
            term_spec=term_spec,
            question_text=question_text
        )

        assert "clause of roughly 10 words" in result
        assert "because" in result

    def test_sentence_prompt_format(self):
        length_spec = format_length_spec(15, is_clause=False)
        term_spec = get_term_spec('effectsentence')
        question_text = "Some metadata\n\nSome passage\n\nWrite a sentence:"

        result = ANACHRONISTIC_PROMPT.format(
            length_spec=length_spec,
            term_spec=term_spec,
            question_text=question_text
        )

        assert "sentence of roughly" in result
        assert "therefore" in result

    def test_all_categories_produce_valid_prompts(self):
        for cat in CONNECTOR_TERMS:
            is_clause = 'clause' in cat
            length_spec = format_length_spec(10, is_clause)
            term_spec = get_term_spec(cat)
            question_text = "metadata\n\npassage\n\nprompt"

            result = ANACHRONISTIC_PROMPT.format(
                length_spec=length_spec,
                term_spec=term_spec,
                question_text=question_text
            )

            # No unfilled placeholders
            assert '{' not in result, f"Unfilled placeholder in prompt for {cat!r}"
            assert '}' not in result, f"Unfilled placeholder in prompt for {cat!r}"
            assert len(result) > 0

    def test_metadataless_omits_prefix(self):
        metadata_prefix = "This novel by Jane Austen was published in 1813."
        passage = "Some passage text here."
        prompt = "Write a clause:"

        # With metadata
        question_with = f"{metadata_prefix}\n\n{passage}\n\n{prompt}"
        # Without metadata
        question_without = f"{passage}\n\n{prompt}"

        length_spec = format_length_spec(8, is_clause=True)
        term_spec = get_term_spec('causalclause')

        result_with = ANACHRONISTIC_PROMPT.format(
            length_spec=length_spec, term_spec=term_spec,
            question_text=question_with
        )
        result_without = ANACHRONISTIC_PROMPT.format(
            length_spec=length_spec, term_spec=term_spec,
            question_text=question_without
        )

        assert metadata_prefix in result_with
        assert metadata_prefix not in result_without

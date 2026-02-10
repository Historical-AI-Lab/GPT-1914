"""
Tests for output format: approved output matches connectors format,
no batch fields in output, answer list consistency, JSON serializability.
"""

import json
import pytest
import sys
from pathlib import Path

# Add parent and connectors directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
CONNECTORS_DIR = str(Path(__file__).parent.parent.parent / "connectors")
if CONNECTORS_DIR not in sys.path:
    sys.path.insert(0, CONNECTORS_DIR)

from make_cloze_questions import (
    format_question_output,
    build_metadata_prefix,
)

from approve_batched_questions import (
    apply_metadata_to_question,
    BATCH_FIELDS,
)


# Required fields in final output (matching connectors format)
REQUIRED_FIELDS = [
    'metadata_frame',
    'main_question',
    'source_title',
    'source_author',
    'source_date',
    'author_nationality',
    'source_genre',
    'author_birth',
    'author_profession',
    'source_htid',
    'question_category',
    'question_process',
    'answer_types',
    'answer_strings',
    'answer_probabilities',
    'passage',
]


@pytest.fixture
def batch_question():
    """A batch question dict with all fields including batch-specific ones."""
    return {
        "metadata_frame": "The following passage comes from Test Book, a novel published in 1900 by Test Author, a British writer.",
        "main_question": "passage text\n\nWrite a sentence appropriate for this book...",
        "source_title": "Test Book",
        "source_author": "Test Author",
        "source_date": 1900,
        "author_nationality": "British",
        "source_genre": "novel",
        "author_birth": 1860,
        "author_profession": "writer",
        "source_htid": "hvd.test123",
        "question_category": "cloze_contrastsentence",
        "question_process": "automatic",
        "answer_types": ["ground_truth", "negation", "same_book", "same_book",
                         "anachronistic_mistral-small:24b", "anachronistic_gpt-oss:20b"],
        "answer_strings": [
            "But the king refused to listen.",
            "And the king agreed to listen.",
            "Yet the people remained silent.",
            "However the guards departed.",
            "But the president vetoed the bill.",
            "But the committee rejected the proposal.",
        ],
        "answer_probabilities": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "passage": "The council voted. But the king refused to listen. The advisor wept.",
        # Batch fields
        "is_clause": False,
        "mask_string": "[masked sentence revising an implied expectation]",
        "full_sentence": "But the king refused to listen.",
        "target_idx": 42,
        "masked_passage": "The council voted. [masked sentence revising an implied expectation] The advisor wept.",
        "ground_truth": "But the king refused to listen.",
    }


@pytest.fixture
def confirmed_metadata():
    """Confirmed metadata dict (post key-mapping fix)."""
    return {
        'source_title': 'The Kingdom',
        'source_author': 'Royal Author',
        'source_date': 1895,
        'source_htid': 'hvd.test123',
        'author_nationality': 'British',
        'genre': 'historical novel',
        'author_birth': 1850,
        'author_profession': 'historian',
    }


class TestApprovedOutputMatchesConnectorsFormat:
    """Tests that approved output has same fields as connectors output."""

    def test_all_required_fields_present(self, batch_question, confirmed_metadata):
        """Approved output should contain all required fields."""
        prefix = build_metadata_prefix(confirmed_metadata)
        result = apply_metadata_to_question(batch_question, confirmed_metadata, prefix)

        for field in REQUIRED_FIELDS:
            assert field in result, f"Missing required field: {field}"

    def test_no_extra_unknown_fields(self, batch_question, confirmed_metadata):
        """Approved output should not contain unknown fields."""
        prefix = build_metadata_prefix(confirmed_metadata)
        result = apply_metadata_to_question(batch_question, confirmed_metadata, prefix)

        known_fields = set(REQUIRED_FIELDS)
        for key in result:
            assert key in known_fields, f"Unexpected field in output: {key}"


class TestNoBatchFieldsInOutput:
    """Tests that batch-specific fields are stripped."""

    def test_no_batch_fields_after_apply(self, batch_question, confirmed_metadata):
        """Batch fields should be removed after apply_metadata_to_question."""
        prefix = build_metadata_prefix(confirmed_metadata)
        result = apply_metadata_to_question(batch_question, confirmed_metadata, prefix)

        for field in BATCH_FIELDS:
            assert field not in result, f"Batch field '{field}' should not be in output"

    def test_batch_fields_defined(self):
        """BATCH_FIELDS should include all expected batch-specific fields."""
        expected = {'is_clause', 'mask_string', 'full_sentence', 'target_idx',
                    'masked_passage', 'ground_truth'}
        assert BATCH_FIELDS == expected


class TestAnswerListConsistency:
    """Tests for answer list consistency."""

    def test_answer_lists_same_length(self, batch_question, confirmed_metadata):
        """answer_strings, answer_types, and answer_probabilities should match length."""
        prefix = build_metadata_prefix(confirmed_metadata)
        result = apply_metadata_to_question(batch_question, confirmed_metadata, prefix)

        assert len(result['answer_strings']) == len(result['answer_types'])
        assert len(result['answer_strings']) == len(result['answer_probabilities'])

    def test_ground_truth_first(self, batch_question, confirmed_metadata):
        """Ground truth should be first with type 'ground_truth' and prob 1.0."""
        prefix = build_metadata_prefix(confirmed_metadata)
        result = apply_metadata_to_question(batch_question, confirmed_metadata, prefix)

        assert result['answer_types'][0] == 'ground_truth'
        assert result['answer_probabilities'][0] == 1.0

    def test_distractor_probabilities_zero(self, batch_question, confirmed_metadata):
        """All distractor probabilities should be 0.0."""
        prefix = build_metadata_prefix(confirmed_metadata)
        result = apply_metadata_to_question(batch_question, confirmed_metadata, prefix)

        for prob in result['answer_probabilities'][1:]:
            assert prob == 0.0


class TestJSONSerializability:
    """Tests for JSON serialization."""

    def test_output_is_json_serializable(self, batch_question, confirmed_metadata):
        """Approved output should be JSON serializable."""
        prefix = build_metadata_prefix(confirmed_metadata)
        result = apply_metadata_to_question(batch_question, confirmed_metadata, prefix)

        json_str = json.dumps(result, ensure_ascii=False)
        assert len(json_str) > 0

        # Should round-trip cleanly
        parsed = json.loads(json_str)
        assert parsed['source_title'] == confirmed_metadata['source_title']

    def test_batch_question_is_json_serializable(self, batch_question):
        """Batch question (pre-approval) should also be JSON serializable."""
        json_str = json.dumps(batch_question, ensure_ascii=False)
        assert len(json_str) > 0

        parsed = json.loads(json_str)
        assert parsed['ground_truth'] == batch_question['ground_truth']


class TestQuestionCategoryFormat:
    """Tests for question_category field."""

    def test_category_starts_with_cloze(self, batch_question, confirmed_metadata):
        """question_category should start with 'cloze_'."""
        prefix = build_metadata_prefix(confirmed_metadata)
        result = apply_metadata_to_question(batch_question, confirmed_metadata, prefix)

        assert result['question_category'].startswith('cloze_')

    def test_question_process_is_automatic(self, batch_question, confirmed_metadata):
        """question_process should remain 'automatic'."""
        prefix = build_metadata_prefix(confirmed_metadata)
        result = apply_metadata_to_question(batch_question, confirmed_metadata, prefix)

        assert result['question_process'] == 'automatic'


class TestFormatQuestionOutputDirect:
    """Tests using format_question_output directly for comparison."""

    def test_direct_format_matches_batch_format(self):
        """Output from format_question_output should have same fields as batch output."""
        passage_data = {
            'passage': 'Text with [masked sentence revising an implied expectation]',
            'ground_truth': 'But the wind changed.',
            'mask_string': '[masked sentence revising an implied expectation]',
            'is_clause': False,
            'category': 'contrastsentence',
            'target_idx': 10,
            'full_sentence': 'But the wind changed.',
            'full_passage': 'Text with But the wind changed.',
        }

        metadata = {
            'source_title': 'Test',
            'source_author': 'Author',
            'source_date': 1900,
            'source_htid': 'hvd.test',
            'author_nationality': 'British',
            'genre': 'novel',
            'author_birth': 1850,
            'author_profession': 'writer',
        }

        prefix = build_metadata_prefix(metadata)

        direct_result = format_question_output(
            passage_data, metadata, prefix,
            ['gt', 'd1'], ['ground_truth', 'negation'], [1.0, 0.0]
        )

        direct_fields = set(direct_result.keys())
        required = set(REQUIRED_FIELDS)

        # Direct output should have all required fields
        for field in required:
            assert field in direct_fields, f"Direct format missing: {field}"

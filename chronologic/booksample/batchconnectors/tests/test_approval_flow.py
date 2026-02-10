"""
Tests for approval flow functions: find_potential_question_files(),
group_by_category(), batch field stripping, metadata application.
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

from approve_batched_questions import (
    find_potential_question_files,
    load_potential_questions,
    group_by_category,
    apply_metadata_to_question,
    BATCH_FIELDS,
)


@pytest.fixture
def sample_question():
    """A sample question dict with batch fields."""
    return {
        "metadata_frame": "The following passage comes from Test Book...",
        "main_question": "passage text\n\nWrite a clause...",
        "source_title": "Test Book",
        "source_author": "Test Author",
        "source_date": 1900,
        "author_nationality": "British",
        "source_genre": "novel",
        "author_birth": 1860,
        "author_profession": "",
        "source_htid": "hvd.test123",
        "question_category": "cloze_causalclause",
        "question_process": "automatic",
        "answer_types": ["ground_truth", "negation", "same_book"],
        "answer_strings": ["because he was tired", "because he was energetic", "because the sun set"],
        "answer_probabilities": [1.0, 0.0, 0.0],
        "passage": "He went home because he was tired. The day was done.",
        # Batch fields
        "is_clause": True,
        "mask_string": "[masked clause describing a cause or reason]",
        "full_sentence": "He went home because he was tired.",
        "target_idx": 42,
        "masked_passage": "He went home [masked clause describing a cause or reason]. The day was done.",
        "ground_truth": "because he was tired",
    }


@pytest.fixture
def sample_metadata():
    """Confirmed metadata dict (with 'genre' key as expected by build_metadata_prefix)."""
    return {
        'source_title': 'Confirmed Title',
        'source_author': 'Confirmed Author',
        'source_date': 1905,
        'source_htid': 'hvd.test123',
        'author_nationality': 'American',
        'genre': 'historical novel',
        'author_birth': 1855,
        'author_profession': 'novelist',
    }


class TestFindPotentialQuestionFiles:
    """Tests for finding unprocessed potential question files."""

    def test_finds_potential_files(self, tmp_path):
        """Should find _potentialquestions.jsonl files."""
        (tmp_path / "HN1IMP_potentialquestions.jsonl").write_text('{"test": 1}\n')
        (tmp_path / "HW2BQ6_potentialquestions.jsonl").write_text('{"test": 2}\n')

        result = find_potential_question_files(str(tmp_path))
        barcodes = [b for b, _ in result]

        assert "HN1IMP" in barcodes
        assert "HW2BQ6" in barcodes

    def test_excludes_already_approved(self, tmp_path):
        """Should exclude barcodes that already have _clozequestions.jsonl."""
        (tmp_path / "HN1IMP_potentialquestions.jsonl").write_text('{"test": 1}\n')
        (tmp_path / "HN1IMP_clozequestions.jsonl").write_text('{"approved": 1}\n')
        (tmp_path / "HW2BQ6_potentialquestions.jsonl").write_text('{"test": 2}\n')

        result = find_potential_question_files(str(tmp_path))
        barcodes = [b for b, _ in result]

        assert "HN1IMP" not in barcodes
        assert "HW2BQ6" in barcodes

    def test_empty_directory(self, tmp_path):
        """Should return empty list for directory with no potential files."""
        result = find_potential_question_files(str(tmp_path))
        assert result == []

    def test_nonexistent_directory(self):
        """Should return empty list for nonexistent directory."""
        result = find_potential_question_files("/nonexistent/path")
        assert result == []


class TestLoadPotentialQuestions:
    """Tests for loading JSONL files."""

    def test_loads_jsonl(self, tmp_path):
        """Should load questions from JSONL file."""
        filepath = tmp_path / "test.jsonl"
        lines = [
            json.dumps({"question": "q1", "answer": "a1"}),
            json.dumps({"question": "q2", "answer": "a2"}),
        ]
        filepath.write_text('\n'.join(lines) + '\n')

        result = load_potential_questions(filepath)
        assert len(result) == 2
        assert result[0]['question'] == 'q1'

    def test_skips_blank_lines(self, tmp_path):
        """Should skip blank lines in JSONL."""
        filepath = tmp_path / "test.jsonl"
        filepath.write_text('{"a": 1}\n\n{"b": 2}\n\n')

        result = load_potential_questions(filepath)
        assert len(result) == 2


class TestGroupByCategory:
    """Tests for grouping questions by category."""

    def test_groups_by_category(self):
        """Should group questions by question_category field."""
        questions = [
            {"question_category": "cloze_causalclause", "id": 1},
            {"question_category": "cloze_causalclause", "id": 2},
            {"question_category": "cloze_contrastsentence", "id": 3},
        ]

        groups = group_by_category(questions)

        assert len(groups) == 2
        assert len(groups["cloze_causalclause"]) == 2
        assert len(groups["cloze_contrastsentence"]) == 1

    def test_single_category(self):
        """Should handle all questions in one category."""
        questions = [
            {"question_category": "cloze_causalclause", "id": i}
            for i in range(5)
        ]

        groups = group_by_category(questions)
        assert len(groups) == 1
        assert len(groups["cloze_causalclause"]) == 5

    def test_empty_list(self):
        """Should return empty dict for empty list."""
        groups = group_by_category([])
        assert groups == {}


class TestApplyMetadataToQuestion:
    """Tests for applying confirmed metadata and stripping batch fields."""

    def test_strips_batch_fields(self, sample_question, sample_metadata):
        """Should remove all batch-specific fields from output."""
        from make_cloze_questions import build_metadata_prefix
        prefix = build_metadata_prefix(sample_metadata)

        result = apply_metadata_to_question(sample_question, sample_metadata, prefix)

        for field in BATCH_FIELDS:
            assert field not in result, f"Batch field '{field}' should be stripped"

    def test_replaces_provisional_metadata(self, sample_question, sample_metadata):
        """Should replace provisional metadata with confirmed values."""
        from make_cloze_questions import build_metadata_prefix
        prefix = build_metadata_prefix(sample_metadata)

        result = apply_metadata_to_question(sample_question, sample_metadata, prefix)

        assert result['source_title'] == 'Confirmed Title'
        assert result['source_author'] == 'Confirmed Author'
        assert result['source_date'] == 1905
        assert result['author_nationality'] == 'American'
        assert result['source_genre'] == 'historical novel'
        assert result['author_birth'] == 1855
        assert result['author_profession'] == 'novelist'

    def test_rebuilds_metadata_frame(self, sample_question, sample_metadata):
        """Should rebuild metadata_frame with confirmed values."""
        from make_cloze_questions import build_metadata_prefix
        prefix = build_metadata_prefix(sample_metadata)

        result = apply_metadata_to_question(sample_question, sample_metadata, prefix)

        assert result['metadata_frame'] == prefix
        assert 'Confirmed Title' in result['metadata_frame']

    def test_rebuilds_main_question(self, sample_question, sample_metadata):
        """Should rebuild main_question with masked passage and prompt."""
        from make_cloze_questions import build_metadata_prefix
        prefix = build_metadata_prefix(sample_metadata)

        result = apply_metadata_to_question(sample_question, sample_metadata, prefix)

        assert 'Write a clause' in result['main_question']
        assert 'appropriate for this book' in result['main_question']

    def test_preserves_answer_lists(self, sample_question, sample_metadata):
        """Should preserve answer_strings, answer_types, answer_probabilities."""
        from make_cloze_questions import build_metadata_prefix
        prefix = build_metadata_prefix(sample_metadata)

        result = apply_metadata_to_question(sample_question, sample_metadata, prefix)

        assert result['answer_strings'] == sample_question['answer_strings']
        assert result['answer_types'] == sample_question['answer_types']
        assert result['answer_probabilities'] == sample_question['answer_probabilities']

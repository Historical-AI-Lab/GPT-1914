"""
Tests for metadata key mapping between elicit_metadata() output and
format_question_output() input, provisional field replacement, and
"passage comes from" wording in prefix.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

# Add parent and connectors directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
CONNECTORS_DIR = str(Path(__file__).parent.parent.parent / "connectors")
if CONNECTORS_DIR not in sys.path:
    sys.path.insert(0, CONNECTORS_DIR)

from make_cloze_questions import (
    format_question_output,
    build_metadata_prefix,
    _is_anonymous_author,
)

from batched_cloze_questions import build_provisional_metadata


@pytest.fixture
def elicited_metadata():
    """Simulated output from elicit_metadata()."""
    return {
        'source_htid': 'hvd.hn1imp',
        'source_title': 'The House of Mirth',
        'source_author': 'Edith Wharton',
        'source_date': 1905,
        'author_nationality': 'American',
        'source_genre': 'novel',  # Note: elicit_metadata uses source_genre
        'author_birth': 1862,
        'author_profession': 'novelist',
    }


@pytest.fixture
def sample_passage_data():
    """Sample passage data for testing."""
    return {
        'passage': 'The room was crowded. [masked sentence describing a cause or reason] She left.',
        'ground_truth': 'Because the air was thick and suffocating.',
        'mask_string': '[masked sentence describing a cause or reason]',
        'is_clause': False,
        'category': 'causalsentence',
        'target_idx': 5,
        'full_sentence': 'Because the air was thick and suffocating.',
        'full_passage': 'The room was crowded. Because the air was thick and suffocating. She left.',
    }


class TestKeyMapping:
    """Tests for key mapping between elicit_metadata and format_question_output."""

    def test_elicit_uses_source_genre(self, elicited_metadata):
        """elicit_metadata() returns 'source_genre', not 'genre'."""
        assert 'source_genre' in elicited_metadata
        assert 'genre' not in elicited_metadata

    def test_format_expects_genre(self, sample_passage_data):
        """format_question_output() expects 'genre' key in metadata."""
        metadata = {
            'source_title': 'Test',
            'source_author': 'Author',
            'source_date': 1900,
            'source_htid': 'hvd.test',
            'author_nationality': 'British',
            'genre': 'novel',  # This is what format_question_output expects
            'author_birth': 1850,
            'author_profession': 'writer',
        }

        result = format_question_output(
            sample_passage_data, metadata, "prefix",
            ['gt'], ['ground_truth'], [1.0]
        )

        assert result['source_genre'] == 'novel'

    def test_key_mapping_fix(self, elicited_metadata, sample_passage_data):
        """After mapping source_genre -> genre, format_question_output should work."""
        # Apply the fix described in the plan
        metadata = dict(elicited_metadata)
        metadata['genre'] = metadata.pop('source_genre', 'novel')

        prefix = build_metadata_prefix(metadata)

        result = format_question_output(
            sample_passage_data, metadata, prefix,
            ['gt'], ['ground_truth'], [1.0]
        )

        assert result['source_genre'] == 'novel'
        assert result['source_title'] == 'The House of Mirth'

    def test_build_metadata_prefix_uses_genre_key(self):
        """build_metadata_prefix() should use 'genre' key."""
        metadata = {
            'source_title': 'Test Book',
            'source_author': 'Test Author',
            'source_date': 1900,
            'author_nationality': 'British',
            'genre': 'novel',
            'author_profession': 'writer',
        }

        prefix = build_metadata_prefix(metadata)
        assert 'a novel' in prefix


class TestProvisionalFieldReplacement:
    """Tests that provisional metadata gets replaced with confirmed values."""

    def test_provisional_defaults(self):
        """Provisional metadata should use sensible defaults."""
        metadata = build_provisional_metadata('HN1IMP', {})

        assert metadata['genre'] == 'novel'
        assert metadata['author_profession'] == ''

    def test_confirmed_replaces_provisional(self, sample_passage_data):
        """Confirmed metadata should override provisional values."""
        provisional = build_provisional_metadata('HN1IMP', {})
        assert provisional['genre'] == 'novel'
        assert provisional['author_profession'] == ''

        # Simulate confirmed metadata (after elicit + key mapping)
        confirmed = {
            'source_title': 'Confirmed Title',
            'source_author': 'Confirmed Author',
            'source_date': 1905,
            'source_htid': 'hvd.hn1imp',
            'author_nationality': 'American',
            'genre': 'historical novel',  # Changed from default
            'author_birth': 1855,
            'author_profession': 'historian',  # Changed from default
        }

        prefix = build_metadata_prefix(confirmed)
        result = format_question_output(
            sample_passage_data, confirmed, prefix,
            ['gt'], ['ground_truth'], [1.0]
        )

        assert result['source_genre'] == 'historical novel'
        assert result['author_profession'] == 'historian'


class TestPassageComesFromWording:
    """Tests for 'passage comes from' wording in metadata prefix."""

    def test_prefix_contains_passage_comes_from(self):
        """Metadata prefix should contain 'passage comes from'."""
        metadata = {
            'source_title': 'Test Book',
            'source_author': 'Test Author',
            'source_date': 1900,
            'author_nationality': 'British',
            'genre': 'novel',
            'author_profession': 'writer',
        }

        prefix = build_metadata_prefix(metadata)
        assert 'passage comes from' in prefix

    def test_anonymous_prefix_contains_passage_comes_from(self):
        """Anonymous author prefix should also contain 'passage comes from'."""
        metadata = {
            'source_title': 'Test Book',
            'source_author': 'Anonymous',
            'source_date': 1900,
            'author_nationality': '',
            'genre': 'encyclopedia',
            'author_profession': '',
        }

        prefix = build_metadata_prefix(metadata)
        assert 'passage comes from' in prefix

    def test_prefix_includes_title_and_date(self):
        """Prefix should include book title and publication date."""
        metadata = {
            'source_title': 'My Great Novel',
            'source_author': 'Jane Smith',
            'source_date': 1897,
            'author_nationality': 'American',
            'genre': 'novel',
            'author_profession': 'novelist',
        }

        prefix = build_metadata_prefix(metadata)
        assert 'My Great Novel' in prefix
        assert '1897' in prefix

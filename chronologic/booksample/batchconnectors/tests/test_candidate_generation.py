"""
Tests for generate_candidates_for_category() and build_provisional_metadata().
"""

import pytest
import sys
from pathlib import Path

# Add parent and connectors directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
CONNECTORS_DIR = str(Path(__file__).parent.parent.parent / "connectors")
if CONNECTORS_DIR not in sys.path:
    sys.path.insert(0, CONNECTORS_DIR)

from batched_cloze_questions import (
    generate_candidates_for_category,
    build_provisional_metadata,
)


def _make_tagged(n_sentences=50, category='causalclause', n_tagged=10):
    """
    Create a fake tagged sentence list for testing.

    Places tagged entries at regular intervals with enough preceding
    context to satisfy MIN_PRECEDING_WORDS.
    """
    tagged = []
    tagged_count = 0
    # Space tagged entries out so build_passage has enough preceding words
    interval = max(1, n_sentences // (n_tagged + 1))

    for i in range(n_sentences):
        entry = {
            'sentence': f"This is sentence number {i} with enough words to satisfy the minimum word count requirement for passage building.",
            'index': i,
        }
        # Tag every interval-th sentence after enough preceding context
        if i >= 5 and tagged_count < n_tagged and (i % interval == 0):
            entry[category] = ('because', 3)  # connector, word_pos
            tagged_count += 1
        tagged.append(entry)

    return tagged


class TestGenerateCandidatesForCategory:
    """Tests for generating candidate passages."""

    def test_generates_up_to_max(self):
        """Should generate up to max_candidates candidates."""
        tagged = _make_tagged(n_sentences=100, n_tagged=20)
        candidates = generate_candidates_for_category(
            tagged, 'causalclause', max_candidates=10
        )
        assert len(candidates) <= 10
        assert len(candidates) > 0

    def test_handles_fewer_than_max(self):
        """Should return fewer than max if not enough tagged sentences."""
        tagged = _make_tagged(n_sentences=30, n_tagged=3)
        candidates = generate_candidates_for_category(
            tagged, 'causalclause', max_candidates=15
        )
        assert len(candidates) <= 3

    def test_skips_invalid_passages(self):
        """Should skip sentences where build_passage returns None (too close to start)."""
        tagged = []
        for i in range(5):
            entry = {
                'sentence': 'Short.',
                'index': i,
                'causalclause': ('because', 0),
            }
            tagged.append(entry)

        # All sentences are at the start, so build_passage should fail
        candidates = generate_candidates_for_category(
            tagged, 'causalclause', max_candidates=5
        )
        assert len(candidates) == 0

    def test_no_duplicate_indices(self):
        """Should not return duplicate target indices."""
        tagged = _make_tagged(n_sentences=100, n_tagged=20)
        candidates = generate_candidates_for_category(
            tagged, 'causalclause', max_candidates=15
        )
        indices = [c['target_idx'] for c in candidates]
        assert len(indices) == len(set(indices))

    def test_returns_passage_data_dicts(self):
        """Each candidate should be a dict with expected keys."""
        tagged = _make_tagged(n_sentences=100, n_tagged=10)
        candidates = generate_candidates_for_category(
            tagged, 'causalclause', max_candidates=5
        )
        for c in candidates:
            assert 'passage' in c
            assert 'ground_truth' in c
            assert 'mask_string' in c
            assert 'is_clause' in c
            assert 'category' in c
            assert 'target_idx' in c

    def test_empty_category(self):
        """Should return empty list when no sentences have the category."""
        tagged = _make_tagged(n_sentences=50, category='causalclause', n_tagged=10)
        candidates = generate_candidates_for_category(
            tagged, 'contrastsentence', max_candidates=5
        )
        assert len(candidates) == 0


class TestBuildProvisionalMetadata:
    """Tests for building provisional metadata from CSV."""

    def test_csv_field_mapping(self):
        """Should map CSV fields to metadata dict."""
        csv_data = {
            'title_src': 'The house of mirth.',
            'author_src': 'Wharton, Edith',
            'firstpub': '1905',
            'authnationality': 'American',
            'authordates': '1862-1937',
        }

        result = build_provisional_metadata('HN1IMP', csv_data)

        assert result['source_title'] == 'The House of Mirth'
        assert result['source_author'] == 'Edith Wharton'
        assert result['source_date'] == 1905
        assert result['author_nationality'] == 'American'
        assert result['author_birth'] == 1862
        assert result['source_htid'] == 'hvd.hn1imp'

    def test_default_values(self):
        """Should use defaults when CSV data is missing."""
        result = build_provisional_metadata('HN1IMP', {})

        assert result['genre'] == 'novel'
        assert result['author_profession'] == ''
        assert result['source_title'] == 'HN1IMP'  # Falls back to barcode
        assert result['source_author'] == 'Anonymous'

    def test_anonymous_author_handling(self):
        """Should clear author-related fields for anonymous authors."""
        csv_data = {
            'title_src': 'Some Book',
            'author_src': '',  # No author
            'firstpub': '1900',
            'authnationality': 'British',
            'authordates': '1850-1920',
        }

        result = build_provisional_metadata('HN1IMP', csv_data)

        assert result['source_author'] == 'Anonymous'
        assert result['author_nationality'] == ''
        assert result['author_birth'] == 0
        assert result['author_profession'] == ''

    def test_date_fallback(self):
        """Should fall back to date1_src when firstpub is missing."""
        csv_data = {
            'title_src': 'Some Book',
            'author_src': 'Smith, John',
            'date1_src': '1895',
        }

        result = build_provisional_metadata('HN1IMP', csv_data)
        assert result['source_date'] == 1895

    def test_invalid_date(self):
        """Should handle invalid date gracefully."""
        csv_data = {
            'title_src': 'Some Book',
            'author_src': 'Smith, John',
            'firstpub': 'unknown',
        }

        result = build_provisional_metadata('HN1IMP', csv_data)
        assert result['source_date'] == 0

    def test_htid_format(self):
        """Should format htid as hvd.barcode_lowercase."""
        result = build_provisional_metadata('HW2BQ6', {})
        assert result['source_htid'] == 'hvd.hw2bq6'

    def test_numeric_barcode(self):
        """Should handle numeric barcodes."""
        result = build_provisional_metadata('32044106370034', {})
        assert result['source_htid'] == 'hvd.32044106370034'

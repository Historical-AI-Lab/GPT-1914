"""
Tests for read_barcode_file() in batched_cloze_questions.py.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from batched_cloze_questions import read_barcode_file


@pytest.fixture
def tmp_barcode_file(tmp_path):
    """Helper to create a temporary barcode file."""
    def _make(content):
        p = tmp_path / "barcodes.txt"
        p.write_text(content)
        return str(p)
    return _make


class TestReadBarcodeFile:
    """Tests for reading barcode files."""

    def test_simple_list(self, tmp_barcode_file):
        """Should read a simple list of barcodes."""
        path = tmp_barcode_file("HN1IMP\nHN1NUJ\nHW2BQ6\n")
        result = read_barcode_file(path)
        assert result == ["HN1IMP", "HN1NUJ", "HW2BQ6"]

    def test_whitespace_stripping(self, tmp_barcode_file):
        """Should strip leading/trailing whitespace."""
        path = tmp_barcode_file("  HN1IMP  \n  HN1NUJ\t\n")
        result = read_barcode_file(path)
        assert result == ["HN1IMP", "HN1NUJ"]

    def test_blank_line_skipping(self, tmp_barcode_file):
        """Should skip blank lines."""
        path = tmp_barcode_file("HN1IMP\n\n\nHN1NUJ\n\n")
        result = read_barcode_file(path)
        assert result == ["HN1IMP", "HN1NUJ"]

    def test_comment_skipping(self, tmp_barcode_file):
        """Should skip lines starting with #."""
        path = tmp_barcode_file("# This is a comment\nHN1IMP\n# Another comment\nHN1NUJ\n")
        result = read_barcode_file(path)
        assert result == ["HN1IMP", "HN1NUJ"]

    def test_uppercase_conversion(self, tmp_barcode_file):
        """Should convert all barcodes to uppercase."""
        path = tmp_barcode_file("hn1imp\nHn1nuj\nhw2bq6\n")
        result = read_barcode_file(path)
        assert result == ["HN1IMP", "HN1NUJ", "HW2BQ6"]

    def test_missing_file_error(self):
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            read_barcode_file("/nonexistent/path/barcodes.txt")

    def test_empty_file(self, tmp_barcode_file):
        """Should return empty list for empty file."""
        path = tmp_barcode_file("")
        result = read_barcode_file(path)
        assert result == []

    def test_only_comments_and_blanks(self, tmp_barcode_file):
        """Should return empty list for file with only comments and blanks."""
        path = tmp_barcode_file("# comment\n\n# another\n\n")
        result = read_barcode_file(path)
        assert result == []

    def test_numeric_barcodes(self, tmp_barcode_file):
        """Should handle numeric barcodes correctly."""
        path = tmp_barcode_file("32044106370034\n32044082646845\n")
        result = read_barcode_file(path)
        assert result == ["32044106370034", "32044082646845"]

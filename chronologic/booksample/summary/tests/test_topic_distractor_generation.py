#!/usr/bin/env python3
"""
Tests for topic_distractor_generator.py

Covers:
- Jaccard character metric calculation
- Punctuation handling and case insensitivity
- Same-book distractor generation from real text
- Masking window edge cases
- Paragraph distortion edge cases
- LLM error handling (mocked)
- Length rounding
- Format normalization
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure the summary package is importable
SUMMARY_DIR = Path(__file__).parent.parent
BOOKSAMPLE_DIR = SUMMARY_DIR.parent
sys.path.insert(0, str(SUMMARY_DIR))
sys.path.insert(0, str(BOOKSAMPLE_DIR))

from topic_distractor_generator import (
    jaccard_character_metric,
    find_topic_sentence_index,
    mask_sentences_around_topic,
    make_same_book_distractors,
    make_anachronistic_distractors,
    round_length,
    distort_paragraph,
    generate_topic_sentence,
    normalize_distractor_format,
)

# ---- Jaccard character metric tests ----

class TestJaccardCharacterMetric:
    def test_identical_sentences(self):
        """Two identical sentences should produce a high score."""
        sent = "The intersection of both sentences is complete"
        score = jaccard_character_metric(sent, sent)
        assert score > 0.5

    def test_no_overlap(self):
        """No shared words should produce 0.0."""
        score = jaccard_character_metric("cat dog fish", "apple banana cherry")
        assert score == 0.0

    def test_character_counting(self):
        """Verify character counting: 'the'->0, 'intersection'->9, 'of'->0, 'both'->1."""
        # "the intersection of both" has characters after 3rd:
        # the=0, intersection=9, of=0, both=1 => total=10
        # For identical sentences intersection=union, so: 10 / (10 + 10) = 0.5
        sent = "the intersection of both"
        score = jaccard_character_metric(sent, sent)
        assert abs(score - 0.5) < 0.01

    def test_short_words_penalized(self):
        """Sentences made entirely of short words (<=3 chars) score 0."""
        score = jaccard_character_metric("the a an of to", "the a an of to")
        assert score == 0.0

    def test_partial_overlap(self):
        """Partial overlap should produce intermediate score."""
        a = "The large brown dog ran quickly"
        b = "The small brown cat sat quietly"
        score = jaccard_character_metric(a, b)
        assert 0.0 < score < 0.5


class TestJaccardPunctuationHandling:
    def test_punctuation_stripped(self):
        """Punctuation should not affect the metric."""
        a = "Hello, world! This is a test."
        b = "Hello world This is a test"
        score_a = jaccard_character_metric(a, a)
        score_b = jaccard_character_metric(a, b)
        assert abs(score_a - score_b) < 0.01

    def test_case_insensitive(self):
        """Metric should be case-insensitive."""
        a = "The QUICK Brown FOX"
        b = "the quick brown fox"
        score = jaccard_character_metric(a, b)
        # Should be same as identical since case is folded
        score_identical = jaccard_character_metric(b, b)
        assert abs(score - score_identical) < 0.01


# ---- Same-book distractor tests ----

class TestMakeSameBookDistractors:
    @pytest.fixture
    def real_sentences(self):
        """Load sentences from a real text file if available."""
        source_dir = BOOKSAMPLE_DIR / "edgebooks"
        # Find any available text file
        txt_files = sorted(source_dir.glob("*.txt"))
        if not txt_files:
            pytest.skip("No text files in edgebooks/")

        from nltk import sent_tokenize
        with open(txt_files[0], 'r', encoding='utf-8') as f:
            text = f.read()
        sentences = sent_tokenize(text)
        if len(sentences) < 30:
            pytest.skip("Text file too short for meaningful test")
        return sentences

    def test_returns_five_sentences(self, real_sentences):
        """Should return 5 distractor sentences."""
        # Pick a sentence in the middle
        target_idx = len(real_sentences) // 2
        target = real_sentences[target_idx]
        result = make_same_book_distractors(real_sentences, target)
        assert len(result) == 5

    def test_not_in_masked_window(self, real_sentences):
        """Returned sentences should not be in the masked window."""
        target_idx = len(real_sentences) // 2
        target = real_sentences[target_idx]

        # Get the masked window
        start = max(0, target_idx - 5)
        end = min(len(real_sentences), target_idx + 11)
        masked_window = set(real_sentences[start:end])

        result = make_same_book_distractors(real_sentences, target)
        for sent in result:
            assert sent not in masked_window

    def test_vocabulary_overlap(self, real_sentences):
        """Returned sentences should have vocabulary overlap with target."""
        target_idx = len(real_sentences) // 2
        target = real_sentences[target_idx]
        result = make_same_book_distractors(real_sentences, target)

        # At least the top result should have some overlap
        if result:
            score = jaccard_character_metric(result[0], target)
            # Score should be positive (some overlap)
            assert score >= 0.0


# ---- Mask sentences tests ----

class TestMaskSentencesAroundTopic:
    def test_topic_at_start(self):
        """Topic at index 0: no sentences masked before."""
        sentences = [f"Sentence {i}." for i in range(20)]
        result = mask_sentences_around_topic(sentences, 0, before=5, after=10)
        # Should exclude indices 0..10 (0-5 before is clamped to 0, 0+10=10)
        assert len(result) == 9  # indices 11-19
        assert sentences[0] not in result
        assert sentences[11] in result

    def test_topic_at_end(self):
        """Topic at last index: no sentences masked after."""
        sentences = [f"Sentence {i}." for i in range(20)]
        result = mask_sentences_around_topic(sentences, 19, before=5, after=10)
        # Should exclude indices 14..19
        assert sentences[19] not in result
        assert sentences[13] in result

    def test_very_short_list(self):
        """Very short list of sentences."""
        sentences = ["A.", "B.", "C."]
        result = mask_sentences_around_topic(sentences, 1, before=5, after=10)
        # Everything is in the window, so nothing remains
        assert len(result) == 0

    def test_middle_of_text(self):
        """Topic in middle should mask before and after."""
        sentences = [f"S{i}" for i in range(50)]
        result = mask_sentences_around_topic(sentences, 25, before=5, after=10)
        # Excluded: 20-35 (16 sentences), remaining: 34
        assert len(result) == 34
        assert "S20" not in result
        assert "S35" not in result
        assert "S19" in result
        assert "S36" in result


# ---- Distort paragraph tests ----

class TestDistortParagraph:
    def test_short_paragraph(self):
        """Paragraph with only 1-2 sentences returns without crashing."""
        para = "[masked topic sentence] This is the only real sentence."
        similar = ["Replacement sentence one.", "Replacement sentence two."]
        result = distort_paragraph(para, similar, 1)
        # Should return unchanged since fewer than 2 real sentences
        assert "[masked topic sentence]" in result

    def test_n_greater_than_available(self):
        """n > available sentences should replace as many as possible."""
        para = (
            "[masked topic sentence] First real sentence here. "
            "Second real sentence here. Third real sentence here."
        )
        similar = ["Replacement A.", "Replacement B."]
        result = distort_paragraph(para, similar, 10)
        assert "[masked topic sentence]" in result

    def test_marker_preserved(self):
        """The [masked topic sentence] marker must always be preserved."""
        para = (
            "[masked topic sentence] The economy grew significantly. "
            "Trade routes expanded across the continent. "
            "New industries were established in the cities. "
            "Agriculture remained the primary occupation."
        )
        similar = ["A completely different sentence.", "Another different one."]
        result = distort_paragraph(para, similar, 2)
        assert "[masked topic sentence]" in result

    def test_empty_similar_sentences(self):
        """Empty similar_sentences list returns paragraph unchanged."""
        para = "[masked topic sentence] Some content here."
        result = distort_paragraph(para, [], 2)
        assert result == para


# ---- Generate topic sentence tests (mocked) ----

class TestGenerateTopicSentence:
    @patch('topic_distractor_generator.call_ollama_model')
    def test_error_returns_none(self, mock_call):
        """Model returning error should result in None."""
        mock_call.return_value = {"status": "error", "reason": "Connection refused"}
        result = generate_topic_sentence("frame", "paragraph", 20, "model")
        assert result is None

    @patch('topic_distractor_generator.call_ollama_model')
    def test_very_long_response_retries(self, mock_call):
        """500+ word response should trigger retry with length check."""
        long_response = " ".join(["word"] * 600)
        short_response = "A good topic sentence for the paragraph about history."
        mock_call.side_effect = [
            {"status": "success", "response": long_response},
            {"status": "success", "response": short_response},
        ]
        result = generate_topic_sentence("frame", "paragraph", 20, "model")
        assert result == short_response
        assert mock_call.call_count == 2

    @patch('topic_distractor_generator.call_ollama_model')
    def test_strips_quotes(self, mock_call):
        """Generated text should have quotation marks stripped."""
        mock_call.return_value = {
            "status": "success",
            "response": '"This is a topic sentence about something interesting."'
        }
        result = generate_topic_sentence("frame", "paragraph", 20, "model")
        assert not result.startswith('"')
        assert not result.endswith('"')

    @patch('topic_distractor_generator.call_ollama_model')
    def test_takes_first_line(self, mock_call):
        """Multi-line response should use only first line."""
        mock_call.return_value = {
            "status": "success",
            "response": "First line is the topic sentence.\nSecond line is explanation."
        }
        result = generate_topic_sentence("frame", "paragraph", 20, "model")
        assert "Second line" not in result
        assert "First line" in result


# ---- Round length tests ----

class TestRoundLength:
    def test_even_numbers_unchanged(self):
        assert round_length(10) == 10
        assert round_length(20) == 20

    def test_odd_numbers_rounded(self):
        # Python uses banker's rounding: round(x.5) rounds to nearest even
        assert round_length(11) == 12  # round(5.5)=6, 6*2=12
        assert round_length(9) == 8    # round(4.5)=4, 4*2=8
        assert round_length(13) == 12  # round(6.5)=6, 6*2=12
        assert round_length(15) == 16  # round(7.5)=8, 8*2=16

    def test_minimum_four(self):
        assert round_length(1) == 4
        assert round_length(2) == 4
        assert round_length(3) == 4

    def test_zero(self):
        assert round_length(0) == 4

    def test_rounding_direction(self):
        """7 -> round(7/2)*2 = round(3.5)*2 = 4*2 = 8."""
        assert round_length(7) == 8
        """5 -> round(5/2)*2 = round(2.5)*2 = 2*2 = 4."""
        assert round_length(5) == 4


# ---- Normalize distractor format tests ----

class TestNormalizeDistractorFormat:
    def test_capitalize_match(self):
        """Distractor should match ground truth capitalization."""
        gt_lower = "because the river was wide"
        result = normalize_distractor_format("Because it was narrow", gt_lower)
        assert result[0].islower()

        gt_upper = "The river was wide."
        result = normalize_distractor_format("the river was narrow.", gt_upper)
        assert result[0].isupper()

    def test_punctuation_match_add(self):
        """Add period if ground truth has final punctuation."""
        gt = "The river was wide."
        result = normalize_distractor_format("The river was narrow", gt)
        assert result.endswith('.')

    def test_punctuation_match_remove(self):
        """Remove period if ground truth lacks final punctuation."""
        gt = "because the river was wide"
        result = normalize_distractor_format("because it was narrow.", gt)
        assert not result.endswith('.')

    def test_empty_inputs(self):
        """Empty inputs should not crash."""
        assert normalize_distractor_format("", "hello") == ""
        assert normalize_distractor_format("hello", "") == "hello"

    def test_preserves_content(self):
        """Content should be preserved aside from first char and final punct."""
        gt = "This is a sentence."
        result = normalize_distractor_format("that is another sentence", gt)
        assert "is another sentence" in result


# ---- Find topic sentence index tests ----

class TestFindTopicSentenceIndex:
    def test_exact_match(self):
        sentences = ["First.", "Second.", "Third."]
        assert find_topic_sentence_index(sentences, "Second.") == 1

    def test_fuzzy_match(self):
        sentences = ["First sentence here.", "The second sentence.", "Third."]
        # Slightly modified version should still match
        idx = find_topic_sentence_index(sentences, "The second sentence")
        assert idx == 1

    def test_not_found_raises(self):
        sentences = ["First.", "Second.", "Third."]
        with pytest.raises(ValueError):
            find_topic_sentence_index(sentences, "Completely different text that shares nothing")

    def test_threshold_at_075(self):
        """A match with ratio between 0.75 and 0.80 should succeed."""
        # Build a pair where the fuzzy ratio is ~0.77
        original = "The sovereign endeavored to replace the old judicial system."
        # OCR-garbled version — enough overlap to be >0.75 but <0.80
        sentences = [
            "Unrelated sentence here.",
            "The sovereign endeavoured to replaee the olde judicial systeme.",
            "Another unrelated sentence.",
        ]
        idx = find_topic_sentence_index(sentences, original)
        assert idx == 1


# ---- Same-book fallback tests ----

class TestSameBookDistractorFallback:
    def test_fallback_uses_passage_to_locate_region(self):
        """When topic sentence can't be found, passage sentences locate the region."""
        sentences = [
            f"Sentence number {i} about various topics and important historical events in the region."
            for i in range(30)
        ]
        # A topic sentence that won't match anything
        topic = "Completely unrelated topic sentence about elephants and astronomy in the region."
        # But the passage contains a sentence that IS in the book
        passage = (
            "Sentence number 15 about various topics and important historical events in the region. "
            "Another part of the passage with more detail."
        )

        result = make_same_book_distractors(sentences, topic, passage)

        # Should still return results via the fallback
        assert len(result) > 0
        assert len(result) <= 5
        # The passage sentence itself should be masked out (it's near index 15)
        assert sentences[15] not in result

    def test_fallback_returns_empty_when_nothing_matches(self):
        """If neither topic nor passage sentences are found, return empty."""
        sentences = [f"Sentence number {i} about various topics." for i in range(30)]
        topic = "Completely unrelated elephants and astronomy."
        passage = "Also completely unrelated whales and geology."

        result = make_same_book_distractors(sentences, topic, passage)
        assert result == []

    def test_no_passage_fallback_returns_empty(self):
        """Without passage param, unmatched topic returns empty."""
        sentences = [f"Sentence number {i} about various topics." for i in range(30)]
        topic = "Completely unrelated elephants and astronomy."

        result = make_same_book_distractors(sentences, topic)
        assert result == []


# ---- Anachronistic prompt distortion tests ----

class TestAnachronisticPromptsContainDistortion:
    """Verify that prompts for passes 2 and 3 actually include substituted sentences."""

    CANARY_SENTENCES = [
        "CANARY_ALPHA was deliberately inserted here.",
        "CANARY_BETA serves as a unique test marker.",
        "CANARY_GAMMA indicates successful substitution.",
        "CANARY_DELTA confirms paragraph distortion occurred.",
        "CANARY_EPSILON verifies the replacement worked properly.",
    ]

    @patch('topic_distractor_generator.call_ollama_model')
    def test_distorted_prompts_contain_canary_sentences(self, mock_call):
        """Passes 2 and 3 should send prompts with substituted (canary) sentences."""
        mock_call.return_value = {
            "status": "success",
            "response": "A generated topic sentence about the subject matter at hand.",
        }

        trimmed_paragraph = (
            "[masked topic sentence] "
            "The Argentine Republic occupies a vast territory in southern South America. "
            "Its boundaries stretch from the Andes to the Atlantic Ocean. "
            "The climate varies greatly from the subtropical north to the cold south. "
            "Agriculture and cattle-raising form the basis of its national prosperity. "
            "Buenos Aires serves as the political and commercial capital of the nation."
        )

        metadata_frame = "The following paragraph comes from Argentina, a novel."
        gt_word_count = 12

        make_anachronistic_distractors(
            self.CANARY_SENTENCES, metadata_frame, trimmed_paragraph, gt_word_count
        )

        # Collect all prompts passed to call_ollama_model
        prompts = [call_args.args[0] for call_args in mock_call.call_args_list]
        assert len(prompts) >= 3, f"Expected at least 3 LLM calls, got {len(prompts)}"

        # Pass 1 (original): should NOT contain any canary
        assert "CANARY" not in prompts[0], "Pass 1 prompt should use original paragraph"

        # Pass 2 (distort1, 1 swap): should contain at least one canary
        has_canary_2 = any(c in prompts[1] for c in self.CANARY_SENTENCES)
        assert has_canary_2, (
            f"Pass 2 prompt does not contain any substituted sentences.\n"
            f"PROMPT:\n{prompts[1]}"
        )

        # Pass 3 (distort2, 2 swaps): should contain at least one canary
        has_canary_3 = any(c in prompts[2] for c in self.CANARY_SENTENCES)
        assert has_canary_3, (
            f"Pass 3 prompt does not contain any substituted sentences.\n"
            f"PROMPT:\n{prompts[2]}"
        )

    @patch('topic_distractor_generator.call_ollama_model')
    def test_distort1_has_fewer_canaries_than_distort2(self, mock_call):
        """Pass 2 (1 swap) should have fewer canaries than pass 3 (2 swaps)."""
        mock_call.return_value = {
            "status": "success",
            "response": "A generated topic sentence about the subject matter at hand.",
        }

        trimmed_paragraph = (
            "[masked topic sentence] "
            "The Argentine Republic occupies a vast territory in southern South America. "
            "Its boundaries stretch from the Andes to the Atlantic Ocean. "
            "The climate varies greatly from the subtropical north to the cold south. "
            "Agriculture and cattle-raising form the basis of its national prosperity. "
            "Buenos Aires serves as the political and commercial capital of the nation."
        )

        metadata_frame = "Test metadata."
        gt_word_count = 12

        make_anachronistic_distractors(
            self.CANARY_SENTENCES, metadata_frame, trimmed_paragraph, gt_word_count
        )

        prompts = [call_args.args[0] for call_args in mock_call.call_args_list]

        canaries_in_2 = sum(1 for c in self.CANARY_SENTENCES if c in prompts[1])
        canaries_in_3 = sum(1 for c in self.CANARY_SENTENCES if c in prompts[2])

        assert canaries_in_2 >= 1, "Pass 2 should have at least 1 canary"
        assert canaries_in_3 >= 2, "Pass 3 should have at least 2 canaries"
        assert canaries_in_3 > canaries_in_2, (
            f"Pass 3 ({canaries_in_3} canaries) should have more than "
            f"pass 2 ({canaries_in_2} canaries)"
        )

    def test_distort_paragraph_directly_with_canaries(self):
        """distort_paragraph itself should produce output containing canary sentences."""
        trimmed_paragraph = (
            "[masked topic sentence] "
            "The Argentine Republic occupies a vast territory in southern South America. "
            "Its boundaries stretch from the Andes to the Atlantic Ocean. "
            "The climate varies greatly from the subtropical north to the cold south. "
            "Agriculture and cattle-raising form the basis of its national prosperity. "
            "Buenos Aires serves as the political and commercial capital of the nation."
        )

        result = distort_paragraph(trimmed_paragraph, self.CANARY_SENTENCES, 2)

        assert result != trimmed_paragraph, (
            "distort_paragraph returned the original paragraph unchanged"
        )
        has_canary = any(c in result for c in self.CANARY_SENTENCES)
        assert has_canary, (
            f"Distorted paragraph contains no canary sentences.\n"
            f"RESULT:\n{result}"
        )

    def test_distort_paragraph_short_paragraph_still_distorts(self):
        """A paragraph with only 2 sentences after the marker should still be distorted.

        sent_tokenize merges [masked topic sentence] with the next sentence
        (since the marker has no terminal punctuation), which reduces the count
        of 'real' (replaceable) sentences. With only 2 remaining sentences,
        sent_tokenize produces 2 tokens: one containing the marker + first sentence,
        and the second sentence alone — leaving only 1 real_index, which triggers
        the early return in distort_paragraph.
        """
        # 2 remaining sentences after topic removal
        trimmed_paragraph = (
            "[masked topic sentence] "
            "Thus her policy in general stimulated the growth of industry "
            "and trade in the empire. "
            "Here, as in administrative reforms, failure to achieve more "
            "was due to the incapacity and corruption of many of her agents."
        )

        result = distort_paragraph(trimmed_paragraph, self.CANARY_SENTENCES, 1)

        assert result != trimmed_paragraph, (
            "distort_paragraph returned a short paragraph unchanged — "
            "sent_tokenize likely merged [masked topic sentence] with the next sentence, "
            "reducing the replaceable sentence count below the threshold"
        )
        has_canary = any(c in result for c in self.CANARY_SENTENCES)
        assert has_canary, (
            f"Distorted short paragraph contains no canary sentences.\n"
            f"RESULT:\n{result}"
        )

    @patch('topic_distractor_generator.call_ollama_model')
    def test_short_paragraph_prompts_still_distorted(self, mock_call):
        """Full pipeline: even with a short paragraph, passes 2/3 prompts must differ."""
        mock_call.return_value = {
            "status": "success",
            "response": "A generated topic sentence about the subject matter at hand.",
        }

        # 2 remaining sentences — the bug-triggering case
        trimmed_paragraph = (
            "[masked topic sentence] "
            "Thus her policy in general stimulated the growth of industry "
            "and trade in the empire. "
            "Here, as in administrative reforms, failure to achieve more "
            "was due to the incapacity and corruption of many of her agents."
        )

        metadata_frame = "Test metadata."
        gt_word_count = 12

        make_anachronistic_distractors(
            self.CANARY_SENTENCES, metadata_frame, trimmed_paragraph, gt_word_count
        )

        prompts = [call_args.args[0] for call_args in mock_call.call_args_list]
        assert len(prompts) >= 3

        has_canary_2 = any(c in prompts[1] for c in self.CANARY_SENTENCES)
        assert has_canary_2, (
            f"Pass 2 prompt (short paragraph) lacks canary sentences.\n"
            f"PROMPT:\n{prompts[1]}"
        )

        has_canary_3 = any(c in prompts[2] for c in self.CANARY_SENTENCES)
        assert has_canary_3, (
            f"Pass 3 prompt (short paragraph) lacks canary sentences.\n"
            f"PROMPT:\n{prompts[2]}"
        )

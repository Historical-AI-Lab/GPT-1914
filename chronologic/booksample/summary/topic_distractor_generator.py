#!/usr/bin/env python3
"""
Topic Distractor Generator Module

Generates distractors for topic-sentence benchmark questions.
Supports three distractor types:
- same_book: Jaccard-ranked sentences from same text
- anachronistic: LLM-generated topic sentences (stylistically dissonant),
  produced via OpenRouter using the shared modelasjudge client
- manual: User-supplied distractors

This module is independent of distractor_generator_wcats.py by design.

Usage:
    from topic_distractor_generator import (
        make_same_book_distractors,
        make_anachronistic_distractors,
        jaccard_character_metric,
    )
"""

import difflib
import json
import random
import re
import string
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from nltk import sent_tokenize
except ImportError:
    import nltk
    nltk.download('punkt', quiet=True)
    from nltk import sent_tokenize

# Reuse the OpenRouter client shared by the modelasjudge pipeline
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "modelasjudge"))
from openrouter_client import make_openrouter_client, call_openrouter_chat

# Constants
PRIMARY_MODEL = "qwen/qwen3-30b-a3b-instruct-2507"
SECONDARY_MODEL = "google/gemma-4-31b-it"

# The placeholder left where the topic sentence was removed. Shared with
# topic_question_writer.py, which imports it — the two must agree exactly.
MASK_MARKER = "[masked introductory sentence]"

ANACHRONISTIC_PROMPT = """{metadata_frame}

{trimmed_paragraph}

Write an introductory sentence of roughly {rounded_length} words that would make a suitable introduction for this whole paragraph. Return only the introductory sentence, without quotation marks:"""


def model_slug(model_id: str) -> str:
    """
    Strip the OpenRouter provider prefix for use in answer_type strings.

    "qwen/qwen3-30b-a3b-instruct-2507" -> "qwen3-30b-a3b-instruct-2507"
    """
    return model_id.split('/')[-1]


_CLIENT = None


def get_client():
    """Return a cached OpenRouter client, creating it on first use."""
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = make_openrouter_client()
    return _CLIENT


def call_openrouter_model(prompt: str, model: str = PRIMARY_MODEL,
                          max_tokens: int = 400) -> Dict[str, Any]:
    """
    Generate text via OpenRouter.

    Wraps call_openrouter_chat, which raises after exhausting its own retries,
    in the status-dict contract the rest of this module expects.

    Returns dict with 'status' and either 'response' or 'reason'.
    """
    try:
        text = call_openrouter_chat(
            get_client(), model, prompt, max_tokens=max_tokens
        )
        return {"status": "success", "response": (text or "").strip()}
    except Exception as e:
        return {"status": "error", "reason": f"{type(e).__name__}: {str(e)}"}


def jaccard_character_metric(sentence_a: str, sentence_b: str) -> float:
    """
    Compute a character-weighted Jaccard metric between two sentences.

    Lowercase both, strip punctuation, compute word-level intersection and union.
    For each word, count characters after the 3rd (e.g., "the"->0, "intersection"->9).
    Returns intersection_chars / (union_chars + 10).

    The +10 penalizes very short sentences.
    """
    translator = str.maketrans('', '', string.punctuation)

    words_a = set(sentence_a.lower().translate(translator).split())
    words_b = set(sentence_b.lower().translate(translator).split())

    intersection = words_a & words_b
    union = words_a | words_b

    def char_count(word_set):
        return sum(max(0, len(w) - 3) for w in word_set)

    intersection_chars = char_count(intersection)
    union_chars = char_count(union)

    return intersection_chars / (union_chars + 10)


def find_topic_sentence_index(sentences: List[str], topic_sentence: str) -> int:
    """
    Find the index of topic_sentence in the sentence list.

    Tries exact match first, then fuzzy match (ratio > 0.75).
    Raises ValueError if not found.
    """
    # Exact match
    for i, sent in enumerate(sentences):
        if sent.strip() == topic_sentence.strip():
            return i

    # Fuzzy match
    best_ratio = 0.0
    best_idx = -1
    for i, sent in enumerate(sentences):
        ratio = difflib.SequenceMatcher(None, sent.strip(), topic_sentence.strip()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_idx = i

    if best_ratio > 0.75:
        return best_idx

    raise ValueError(
        f"Could not find topic sentence in text (best fuzzy ratio: {best_ratio:.2f})"
    )


def mask_sentences_around_topic(sentences: List[str], topic_index: int,
                                before: int = 5, after: int = 10) -> List[str]:
    """
    Return all sentences NOT in the window [topic_index - before, topic_index + after].

    Handles edge cases where topic_index is near start or end.
    """
    start = max(0, topic_index - before)
    end = min(len(sentences), topic_index + after + 1)

    return [s for i, s in enumerate(sentences) if i < start or i >= end]


def make_same_book_distractors(sentences: List[str],
                                topic_sentence: str,
                                passage: str = "") -> List[str]:
    """
    Find same-book distractor sentences ranked by Jaccard character metric.

    Finds topic sentence index, masks nearby sentences, ranks remaining
    by jaccard_character_metric against topic_sentence.

    If the topic sentence can't be located, falls back to locating any
    sentence from the passage to determine the region, then masks around
    that index so passage sentences are excluded from candidates.

    Returns top 5 ranked sentences.
    """
    try:
        topic_index = find_topic_sentence_index(sentences, topic_sentence)
    except ValueError:
        # Fallback: use other passage sentences to find the region
        topic_index = None
        if passage:
            passage_sents = sent_tokenize(passage)
            for ps in passage_sents:
                try:
                    topic_index = find_topic_sentence_index(sentences, ps)
                    print(f"  Fallback: located passage region via another sentence.")
                    break
                except ValueError:
                    continue

        if topic_index is None:
            print("  Warning: Could not locate passage region in text at all.")
            return []

    candidates = mask_sentences_around_topic(sentences, topic_index)

    if not candidates:
        return []

    # Exclude short sentences: must be at least 10 words or 75% of
    # topic sentence length, whichever threshold is larger.
    topic_word_count = len(topic_sentence.split())
    min_words = max(10, int(topic_word_count * 0.75))
    candidates = [c for c in candidates if len(c.split()) >= min_words]

    if not candidates:
        return []

    scored = [
        (jaccard_character_metric(candidate, topic_sentence), candidate)
        for candidate in candidates
    ]
    scored.sort(key=lambda x: x[0], reverse=True)

    return [sent for _, sent in scored[:5]]


def round_length(word_count: int) -> int:
    """
    Round word count to nearest even number, minimum 4.
    """
    rounded = round(word_count / 2) * 2
    return max(rounded, 4)


def distort_paragraph(trimmed_paragraph: str, similar_sentences: List[str],
                      n: int) -> str:
    """
    Distort a paragraph by replacing n random sentences with similar ones.

    Separates the mask marker before tokenizing so that
    sent_tokenize doesn't merge it with the following sentence. Randomly
    replaces n real sentences with choices from similar_sentences, then
    reconstructs the paragraph with the marker in its original position.

    Edge case: paragraphs with 0-1 real sentences return unchanged.
    """
    if not similar_sentences:
        return trimmed_paragraph

    marker = MASK_MARKER

    # Split the marker out before tokenizing to prevent sent_tokenize
    # from merging it with the next sentence (the marker has no terminal
    # punctuation, so sent_tokenize treats "marker + next sentence" as one unit).
    if marker in trimmed_paragraph:
        before_marker, after_marker = trimmed_paragraph.split(marker, 1)
        before_sents = sent_tokenize(before_marker.strip()) if before_marker.strip() else []
        after_sents = sent_tokenize(after_marker.strip()) if after_marker.strip() else []

        # Rebuild with marker as its own element
        all_sentences = before_sents + [marker] + after_sents
        marker_index = len(before_sents)
    else:
        all_sentences = sent_tokenize(trimmed_paragraph)
        marker_index = None

    # Find replaceable sentence indices (everything except the marker)
    real_indices = [i for i in range(len(all_sentences)) if i != marker_index]

    # If fewer than 2 real sentences, return unchanged
    if len(real_indices) < 2:
        return trimmed_paragraph

    # How many can we actually replace
    replacements = min(n, len(real_indices))

    # Pick random indices to replace
    replace_indices = random.sample(real_indices, replacements)

    # Build the result — each replacement gets a distinct sentence
    result = list(all_sentences)
    if replacements <= len(similar_sentences):
        chosen = random.sample(similar_sentences, replacements)
    else:
        chosen = list(similar_sentences)
        random.shuffle(chosen)
    for idx, replacement in zip(replace_indices, chosen):
        result[idx] = replacement

    return ' '.join(result)


def generate_topic_sentence(metadata_frame: str, trimmed_paragraph: str,
                            rounded_length: int, model: str) -> Optional[str]:
    """
    Generate a topic sentence using an LLM.

    Calls call_openrouter_model with ANACHRONISTIC_PROMPT.
    Strips quotation marks, takes first line if multi-line.
    Length validation: accept if > 5 words AND < 3x ground truth length;
    otherwise retry once.

    Returns generated text or None on failure.
    """
    prompt = ANACHRONISTIC_PROMPT.format(
        metadata_frame=metadata_frame,
        trimmed_paragraph=trimmed_paragraph,
        rounded_length=rounded_length
    )

    print(f"\n  --- PROMPT sent to {model} ---")
    print(prompt)
    print("  --- END PROMPT ---\n")

    for attempt in range(2):
        result = call_openrouter_model(prompt, model=model)

        if result['status'] != 'success':
            if attempt < 1:
                print(f"  Topic sentence generation failed ({result['reason']}), retrying...")
                continue
            return None

        response = result['response'].strip()

        # Strip quotation marks
        response = response.strip('"\'')

        # Take first line if multi-line
        if '\n' in response:
            response = response.split('\n')[0].strip()

        # Length validation
        word_count = len(response.split())
        # rounded_length is our proxy for ground truth length
        if word_count > 5 and word_count < 3 * rounded_length:
            return response

        if attempt < 1:
            print(f"  Response length ({word_count} words) outside bounds "
                  f"(need >5, <{3 * rounded_length}), retrying...")

    # Return whatever we got on last attempt
    if result['status'] == 'success':
        response = result['response'].strip().strip('"\'')
        if '\n' in response:
            response = response.split('\n')[0].strip()
        if response:
            return response

    return None


def normalize_distractor_format(distractor: str, ground_truth: str) -> str:
    """
    Match capitalization (first letter) and final punctuation to ground truth.
    """
    if not distractor or not ground_truth:
        return distractor

    result = distractor.strip()

    # Handle capitalization
    gt_starts_lower = ground_truth[0].islower()
    if gt_starts_lower and result and result[0].isupper():
        result = result[0].lower() + result[1:]
    elif not gt_starts_lower and result and result[0].islower():
        result = result[0].upper() + result[1:]

    # Handle final punctuation
    final_punct = '.!?'
    gt_has_final_punct = (ground_truth.rstrip()[-1] in final_punct
                          if ground_truth.rstrip() else False)

    if gt_has_final_punct:
        if result and result[-1] not in final_punct:
            result = result.rstrip(',;:') + '.'
    else:
        while result and result[-1] in final_punct:
            result = result[:-1]

    return result


def make_anachronistic_distractors(
    similar_sentences: List[str],
    metadata_frame: str,
    trimmed_paragraph: str,
    gt_word_count: int,
    primary_model: str = PRIMARY_MODEL,
    secondary_model: str = SECONDARY_MODEL
) -> Tuple[List[str], List[str]]:
    """
    Generate anachronistic distractors for a topic sentence question.

    Generates 3 distractors:
    1. Primary model on original trimmed_paragraph
    2. Secondary model on distorted paragraph (1 sentence swapped)
    3. Primary model on distorted paragraph (2 sentences swapped)

    Passes 2 and 3 are skipped when similar_sentences is empty: distortion
    would be a no-op, so all three prompts would be identical.

    Answer types carry the bare model slug, without the provider prefix.

    Returns (distractor_strings, distractor_types) for whatever was
    successfully generated (may be fewer than 3).
    """
    rounded = round_length(gt_word_count)
    primary_slug = model_slug(primary_model)
    secondary_slug = model_slug(secondary_model)
    distractor_strings = []
    distractor_types = []

    # 1. Primary model on original trimmed paragraph
    print(f"  Generating anachronistic distractor 1/3 ({primary_slug}, original)...")
    result1 = generate_topic_sentence(metadata_frame, trimmed_paragraph,
                                       rounded, primary_model)
    if result1:
        result1 = normalize_distractor_format(result1, "")  # capitalize first letter
        distractor_strings.append(result1)
        distractor_types.append(f"anachronistic_{primary_slug}")

    # Without same-book sentences there is nothing to swap in, so the distorted
    # passes would send prompts identical to pass 1.
    if not similar_sentences:
        print("  No same-book sentences available; skipping the two distorted passes.")
        return distractor_strings, distractor_types

    # 2. Secondary model on distorted paragraph (1 swap)
    print(f"  Generating anachronistic distractor 2/3 ({secondary_slug}, distort1)...")
    distorted1 = distort_paragraph(trimmed_paragraph, similar_sentences, 1)
    result2 = generate_topic_sentence(metadata_frame, distorted1,
                                       rounded, secondary_model)
    if result2:
        result2 = normalize_distractor_format(result2, "")
        distractor_strings.append(result2)
        distractor_types.append(f"anachronistic_distort1_{secondary_slug}")

    # 3. Primary model on distorted paragraph (2 swaps)
    print(f"  Generating anachronistic distractor 3/3 ({primary_slug}, distort2)...")
    distorted2 = distort_paragraph(trimmed_paragraph, similar_sentences, 2)
    result3 = generate_topic_sentence(metadata_frame, distorted2,
                                       rounded, primary_model)
    if result3:
        result3 = normalize_distractor_format(result3, "")
        distractor_strings.append(result3)
        distractor_types.append(f"anachronistic_distort2_{primary_slug}")

    return distractor_strings, distractor_types

#!/usr/bin/env python3
"""
Cloze Question Generator

Generates cloze-style benchmark questions from historical texts by:
1. Detecting logical connectors (cause, effect, contrast, conditional, concessive)
2. Masking sentences or clauses containing these connectors
3. Creating multiple-choice questions with distractors

Usage:
    python make_cloze_questions.py INPUT_TEXT [OPTIONS]

    Options:
        --metadata FILE          Path to JSON metadata file for this book
        --primary-metadata FILE  Path to primary_metadata.csv for defaults
                                 (default: ../primary_metadata.csv)
        --resume FILE            Resume from tagged sentences file
        --output FILE            Output JSONL file (default: process_files/{barcode}_clozequestions.jsonl)
        --verbose-bert           Print BERT ranking details
        --debug                  Enable debug output
"""

import argparse
import csv
import json
import os
import random
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import requests

try:
    from nltk import sent_tokenize
except ImportError:
    import nltk
    nltk.download('punkt', quiet=True)
    from nltk import sent_tokenize

# Import distractor generator
from distractor_generator import generate_distractors, call_ollama_model

# Constants
OLLAMA_URL = "http://localhost:11434/api/generate"
DISAMBIGUATION_MODEL = "mistral-small:24b"
MIN_SENTENCES_REQUIRED = 10
MIN_CATEGORY_EXAMPLES = 3
MIN_PRECEDING_WORDS = 40
INCLUDE_FOLLOWING_PROB = 0.75
CAP_WHERE_VERIFICATION_STOPS = 100  # Stop LLM verification once category has this many verified

# Default distractor types for cloze questions
DEFAULT_DISTRACTOR_TYPES = [
    "negation",
    "same_book",
    "same_book",
    "anachronistic_mistral-small:24b",
    "anachronistic_gpt-oss:20b"
]

# Metadata template (different from character questions)
METADATA_FRAME_TEMPLATE = """The following passage comes from {title}, {a_an_genre} {genre} published in {year} by {author}, {a_an_nat} {nationality} {profession}."""
METADATA_FRAME_NOAUTHOR = """The following passage comes from {title}, {a_an_genre} {genre} published in {year}."""
# Tag descriptions for mask strings
TAG_DESCRIPTIONS = {
    'causalsentence': '[masked sentence describing a cause or reason]',
    'causalclause': '[masked clause describing a cause or reason]',
    'effectsentence': '[masked sentence describing an inference or effect]',
    'effectclause': '[masked clause describing an inference or effect]',
    'contrastsentence': '[masked sentence revising an implied expectation]',
    'contrastclause': '[masked clause revising an implied expectation]',
    'conditionalclause': '[masked clause describing a condition or proviso]',
    'concessiveclause': '[masked clause acknowledging a countervailing fact]'
}

# Connector patterns from connector_list.md
CONNECTOR_PATTERNS = {
    # CAUSE/REASON
    'causalsentence': {
        'first_word': [],
        'first_five_words': ['justification', 'rationale', 'purpose', 'cause', 'because'],
        'prev_sentence_why': True
    },
    'causalclause': {
        'after_punct': ['because', 'since', 'as', 'in order that', 'in order to',
                        'for', 'seeing that', 'owing to', 'inasmuch', 'forasmuch']
    },
    # EFFECT/INFERENCE
    'effectsentence': {
        'first_word': ['so', 'hence'],
        'first_five_words': ['thus', 'therefore', 'thence', 'accordingly',
                             'consequence', 'result', 'effect', 'consequently',
                             'it follows that']
    },
    'effectclause': {
        'after_punct': ['so'],
        'if_then_rule': True
    },
    # CONTRAST
    'contrastsentence': {
        'first_word': ['but', 'yet'],
        'first_five_words': ['however', 'nevertheless']
    },
    'contrastclause': {
        'after_punct': ['but', 'however', 'nevertheless']
    },
    # CONDITIONAL
    'conditionalclause': {
        'after_comma': ['if', 'provided that', 'insofar as', 'unless']
    },
    # CONCESSIVE
    'concessiveclause': {
        'after_comma': ['although', 'though', 'even though', 'even if', 'albeit', 'while']
    }
}

# Ambiguous connectors requiring LLM disambiguation
AMBIGUOUS_CONNECTORS = {
    'since': 'causalclause',
    'as': 'causalclause',
    'then': 'effectclause',
    'while': 'concessiveclause'
}


def a_or_an(word: str) -> str:
    """
    Return 'a' or 'an' based on whether word starts with a vowel sound.

    Args:
        word: The word that will follow the article

    Returns:
        'a' or 'an'
    """
    if not word:
        return 'a'

    # Check first letter (simple heuristic)
    first_letter = word[0].lower()

    # Words starting with vowels typically use 'an'
    # Exception: words starting with 'u' that sound like 'you' (e.g., 'university')
    # Exception: words starting with silent 'h' use 'an' (e.g., 'hour', 'honest')
    vowels = 'aeiou'

    if first_letter in vowels:
        # Special case: 'u' words that sound like 'you'
        u_exceptions = ['university', 'united', 'unique', 'uniform', 'universal',
                        'usage', 'useful', 'usual', 'utensil', 'utility']
        if first_letter == 'u' and any(word.lower().startswith(exc) for exc in u_exceptions):
            return 'a'
        return 'an'

    # Special case: silent 'h' words
    silent_h = ['honest', 'honor', 'honour', 'hour', 'heir']
    if first_letter == 'h' and any(word.lower().startswith(h) for h in silent_h):
        return 'an'

    return 'a'


# Default path for primary metadata CSV (in parent directory)
DEFAULT_PRIMARY_METADATA = Path(__file__).parent.parent / "primary_metadata.csv"

# Central directory for JSON metadata files (shared across pipelines)
CENTRAL_METADATA_DIR = Path(__file__).parent.parent / "json_metadata"


def load_primary_metadata_csv(filepath: Path) -> Dict[str, Dict]:
    """
    Load primary_metadata.csv into a dict keyed by barcode.

    Args:
        filepath: Path to the CSV file

    Returns:
        Dict mapping barcode (e.g., "hvd.hn1imp") to row dict
    """
    metadata = {}

    if not filepath.exists():
        print(f"Warning: Primary metadata CSV not found: {filepath}")
        return metadata

    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            barcode = row.get('barcode_src', '').strip()
            if barcode:
                metadata[barcode] = row

    return metadata


def barcode_to_csv_key(barcode: str) -> str:
    """
    Convert filename barcode to CSV lookup key.

    Filename: 32044106370034 or HN1IMP (uppercase for alphabetic)
    CSV key: hvd.32044106370034 or hvd.hn1imp (with hvd. prefix, lowercase)
    """
    return f"hvd.{barcode.lower()}"


def clean_title(title: str) -> str:
    """
    Clean up book title from CSV metadata.

    - Trim final punctuation (., :, ;, etc.)
    - Capitalize words longer than 3 letters (title case for significant words)

    Examples:
        "The house of mirth." -> "The House of Mirth"
        "a tale of two cities:" -> "A Tale of Two Cities"
    """
    if not title:
        return title

    # Trim trailing punctuation
    result = title.rstrip('.,;:!?')

    # Capitalize words longer than 3 letters
    words = result.split()
    capitalized = []
    for i, word in enumerate(words):
        # Always capitalize first word, or words > 3 letters
        if i == 0 or len(word) > 3:
            capitalized.append(word.capitalize())
        else:
            capitalized.append(word.lower())

    return ' '.join(capitalized)


def reformat_author_name(author: str) -> str:
    """
    Convert author name from "Lastname, First Middle" to "First Middle Lastname".

    Examples:
        "Besant, Annie" -> "Annie Besant"
        "Twain, Mark" -> "Mark Twain"
        "Already Correct" -> "Already Correct"
    """
    if not author or ',' not in author:
        return author

    parts = author.split(',', 1)
    if len(parts) == 2:
        lastname = parts[0].strip()
        firstnames = parts[1].strip()
        return f"{firstnames} {lastname}"

    return author


def load_or_create_metadata(text_path: str, metadata_path: Optional[str] = None,
                            csv_metadata: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Load metadata from file or prompt user interactively.

    Args:
        text_path: Path to the input text file (used to derive barcode)
        metadata_path: Optional path to existing metadata JSON file
        csv_metadata: Optional dict from primary_metadata.csv for this barcode

    Returns:
        Dict with metadata fields
    """
    # Try to load existing metadata
    if metadata_path and os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # Check for required fields (including new author_profession)
            required = ['source_title', 'source_author', 'source_date', 'source_htid',
                        'author_nationality', 'genre', 'author_birth', 'author_profession']

            missing = [f for f in required if f not in metadata]
            if missing:
                print(f"Metadata file missing fields: {missing}")
                print("Please provide missing information:")
                for field in missing:
                    value = input(f"  {field}: ").strip()
                    if field in ['source_date', 'author_birth']:
                        metadata[field] = int(value) if value else 0
                    else:
                        metadata[field] = value

                # Save updated metadata
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)

            return metadata

        except json.JSONDecodeError as e:
            print(f"Error reading metadata file: {e}")
            print("Prompting for metadata interactively...")

    # Derive barcode from text path
    barcode = Path(text_path).stem.upper()
    csv_metadata = csv_metadata or {}

    # Extract defaults from CSV metadata
    default_title = clean_title(csv_metadata.get('title_src', ''))
    default_author = reformat_author_name(csv_metadata.get('author_src', ''))
    default_date = csv_metadata.get('firstpub') or csv_metadata.get('date1_src', '')
    default_htid = barcode_to_csv_key(barcode)
    default_nationality = csv_metadata.get('authnationality', '')

    # Parse author birth year from authordates if available (format: "1829-1900")
    author_dates = csv_metadata.get('authordates', '')
    default_birth = ''
    if author_dates and '-' in author_dates:
        default_birth = author_dates.split('-')[0].strip()

    # Display CSV defaults if available
    if csv_metadata:
        print("\nBook information from primary_metadata.csv:")
        print(f"  Title: {default_title}")
        print(f"  Author: {default_author}")
        print(f"  Date: {default_date}")
        print(f"  Nationality: {default_nationality}")
        print(f"  Author dates: {author_dates}")

    # Prompt user for metadata with defaults
    print("\nProvide book metadata (press Enter to accept default in brackets):")
    metadata = {}

    title_prompt = f"  Title [{default_title}]: " if default_title else "  Title: "
    title_input = input(title_prompt).strip()
    metadata['source_title'] = title_input if title_input else default_title

    author_prompt = f"  Author [{default_author or 'Anonymous'}]: " if default_author else "  Author (First Last format, or press Enter for Anonymous): "
    author_input = input(author_prompt).strip()
    metadata['source_author'] = author_input if author_input else (default_author or "Anonymous")

    date_prompt = f"  Publication year [{default_date}]: " if default_date else "  Publication year: "
    date_input = input(date_prompt).strip()
    date_val = date_input if date_input else default_date
    metadata['source_date'] = int(date_val) if date_val else 0

    htid_prompt = f"  HathiTrust ID [{default_htid}]: "
    htid_input = input(htid_prompt).strip()
    metadata['source_htid'] = htid_input if htid_input else default_htid

    genre_prompt = "  Genre [novel]: "
    genre_input = input(genre_prompt).strip()
    metadata['genre'] = genre_input if genre_input else "novel"

    # Only prompt for author details if not anonymous
    if _is_anonymous_author(metadata['source_author']):
        metadata['author_nationality'] = ""
        metadata['author_birth'] = 0
        metadata['author_profession'] = ""
        print("  (Skipping author details for anonymous/unknown author)")
    else:
        nat_prompt = f"  Author nationality [{default_nationality}]: " if default_nationality else "  Author nationality: "
        nat_input = input(nat_prompt).strip()
        metadata['author_nationality'] = nat_input if nat_input else default_nationality

        birth_prompt = f"  Author birth year [{default_birth}]: " if default_birth else "  Author birth year: "
        birth_input = input(birth_prompt).strip()
        birth_val = birth_input if birth_input else default_birth
        metadata['author_birth'] = int(birth_val) if birth_val else 0

        prof_prompt = "  Author profession (e.g., novelist, historian, theosophist): "
        metadata['author_profession'] = input(prof_prompt).strip()

    # Save metadata if path provided
    if metadata_path:
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"Metadata saved to: {metadata_path}")

    return metadata


def _is_anonymous_author(author: str) -> bool:
    """Check if author field indicates anonymous/unknown authorship."""
    if not author:
        return True
    author_lower = author.strip().lower()
    return author_lower in ('', 'anonymous', 'unknown', 'various', 'n/a')


def build_metadata_prefix(metadata: Dict[str, Any]) -> str:
    """
    Build metadata prefix string from metadata dict.

    Uses METADATA_FRAME_NOAUTHOR if author is missing or anonymous.

    Args:
        metadata: Dict with source_title, source_author, etc.

    Returns:
        Formatted metadata prefix string
    """
    author = metadata.get('source_author', '')

    if _is_anonymous_author(author):
        return METADATA_FRAME_NOAUTHOR.format(
            title=metadata['source_title'],
            a_an_genre=a_or_an(metadata['genre']),
            genre=metadata['genre'],
            year=metadata['source_date']
        )
    else:
        return METADATA_FRAME_TEMPLATE.format(
            title=metadata['source_title'],
            a_an_genre=a_or_an(metadata['genre']),
            genre=metadata['genre'],
            year=metadata['source_date'],
            author=metadata['source_author'],
            a_an_nat=a_or_an(metadata['author_nationality']),
            nationality=metadata['author_nationality'],
            profession=metadata['author_profession']
        )


def _is_why_question(sentence: str) -> bool:
    """Check if sentence is a 'why' question."""
    words = sentence.strip().lower().split()
    return words and words[0] == 'why' and sentence.strip().endswith('?')


def _check_sentence_start(words: List[str], category: str, rules: Dict) -> Optional[Tuple[str, int]]:
    """
    Check for connectors at sentence start.

    Args:
        words: List of words (lowercase, punctuation stripped)
        category: The connector category being checked
        rules: The rules for this category

    Returns:
        Tuple of (connector, word_position) or None
    """
    if not words:
        return None

    # First word check
    first_word_connectors = rules.get('first_word', [])
    if words[0] in first_word_connectors:
        return (words[0], 0)

    # First five words check
    first_five_connectors = rules.get('first_five_words', [])
    for connector in first_five_connectors:
        connector_words = connector.split()
        if len(connector_words) == 1:
            # Single word connector
            for i, word in enumerate(words[:5]):
                if word == connector:
                    return (connector, i)
        else:
            # Multi-word connector
            for i in range(min(5, len(words))):
                phrase = ' '.join(words[i:i+len(connector_words)])
                if phrase == connector:
                    return (connector, i)

    return None


def _check_clause_start(sentence: str, category: str, rules: Dict) -> Optional[Tuple[str, int]]:
    """
    Check for connectors after comma or semicolon.

    Args:
        sentence: The full sentence text
        category: The connector category being checked
        rules: The rules for this category

    Returns:
        Tuple of (connector, word_position) or None
    """
    # Get connectors to check
    connectors = []
    if 'after_punct' in rules:
        connectors.extend(rules['after_punct'])
    if 'after_comma' in rules:
        connectors.extend(rules['after_comma'])

    if not connectors:
        return None

    for connector in connectors:
        # Pattern: comma or semicolon, optional space, then connector word
        pattern = r'[,;]\s*(' + re.escape(connector) + r')\b'
        match = re.search(pattern, sentence, re.IGNORECASE)

        if match:
            # Calculate word position
            char_pos = match.start(1)
            # Count words before this position
            word_pos = len(sentence[:char_pos].split())
            return (connector.lower(), word_pos)

    return None


def _check_if_then_rule(sentence: str, words: List[str]) -> Optional[Tuple[str, int]]:
    """
    Check for if...then pattern indicating effect clause.

    Args:
        sentence: The full sentence text
        words: List of words (lowercase, punctuation stripped)

    Returns:
        Tuple of ('then', word_position) or None
    """
    # Check if sentence starts with "if"
    if not words or words[0] != 'if':
        return None

    # Look for "then" after a comma
    pattern = r',\s*(then)\b'
    match = re.search(pattern, sentence, re.IGNORECASE)

    if match:
        char_pos = match.start(1)
        word_pos = len(sentence[:char_pos].split())
        return ('then', word_pos)

    return None


def parse_connector_patterns(sentence: str, prev_sentence: str = "") -> Dict[str, Tuple[str, int]]:
    """
    Parse a sentence for connector patterns.

    Args:
        sentence: The sentence to analyze
        prev_sentence: The previous sentence (for why? rule)

    Returns:
        Dict mapping category names to (connector, word_position) tuples
        e.g., {'contrastsentence': ('but', 0), 'conditionalclause': ('if', 21)}
    """
    tags = {}

    # Prepare words list (lowercase, punctuation stripped)
    words = sentence.split()
    words_clean = [w.lower().rstrip(',.;:!?"\')') for w in words]

    # Check each category
    for category, rules in CONNECTOR_PATTERNS.items():
        # Sentence-starting patterns
        if 'sentence' in category:
            result = _check_sentence_start(words_clean, category, rules)
            if result:
                tags[category] = result
                continue

        # Clause-starting patterns
        if 'clause' in category:
            result = _check_clause_start(sentence, category, rules)
            if result:
                tags[category] = result
                continue

        # Special: if...then rule for effect clause
        if category == 'effectclause' and rules.get('if_then_rule'):
            result = _check_if_then_rule(sentence, words_clean)
            if result:
                tags[category] = result

    # Special: why? previous sentence rule for causal sentence
    if prev_sentence and _is_why_question(prev_sentence):
        if 'causalsentence' not in tags:
            tags['causalsentence'] = (words_clean[0] if words_clean else '', 0)

    return tags


# Disambiguation prompts
DISAMBIGUATION_PROMPT = """Read the following sentence and determine whether the word "{connector}" is being used to express:
A) A cause or reason (WHY something happened) 
B) A temporal relationship (WHEN something happened) or similarity of manner (HOW something was done)

Sentence: {sentence}

Context (previous sentence): {context}

Respond with only "A" or "B" followed by a one-sentence explanation."""

CAUSAL_VERIFICATION_PROMPT = """Read the following two sentences. Does the second sentence express a CAUSE, REASON, or EXPLANATION for something mentioned or implied in the first sentence?

Previous sentence: {prev}
Current sentence: {current}

Respond "YES" if the current sentence explains why something happens or provides a reason.
Respond "NO" if it does not express causation or explanation.
Then provide a one-sentence explanation."""


def disambiguate_temporal_vs_logical(sentence: str, connector: str,
                                     prev_sentence: str = "",
                                     debug: bool = False) -> bool:
    """
    Use LLM to disambiguate temporal vs logical usage of connector.

    Args:
        sentence: The sentence containing the connector
        connector: The ambiguous connector word
        prev_sentence: Previous sentence for context
        debug: Print debug information

    Returns:
        True if logical (keep tag), False if temporal (remove tag)
    """
    prompt = DISAMBIGUATION_PROMPT.format(
        connector=connector,
        sentence=sentence,
        context=prev_sentence or "(none)"
    )

    result = call_ollama_model(prompt, model=DISAMBIGUATION_MODEL, temperature=0.1, debug=debug)

    if result['status'] != 'success':
        print(f"  Warning: Disambiguation failed ({result['reason']}), keeping tag")
        return True  # Conservative default

    response = result['response'].strip().upper()
    return response.startswith('A')  # A = logical/causal


def verify_causal_sentence(sentence: str, prev_sentence: str,
                           debug: bool = False) -> bool:
    """
    Verify that a flagged causal sentence actually expresses causation.

    Args:
        sentence: The sentence flagged as causal
        prev_sentence: The previous sentence for context
        debug: Print debug information

    Returns:
        True if actually causal, False otherwise
    """
    if not prev_sentence:
        return True  # Can't verify without context

    prompt = CAUSAL_VERIFICATION_PROMPT.format(
        prev=prev_sentence,
        current=sentence
    )

    result = call_ollama_model(prompt, model=DISAMBIGUATION_MODEL, temperature=0.1, debug=debug)

    if result['status'] != 'success':
        print(f"  Warning: Causal verification failed ({result['reason']}), keeping tag")
        return True

    return result['response'].strip().upper().startswith('YES')


def tokenize_and_tag_sentences(text: str, debug: bool = False) -> List[Dict]:
    """
    Tokenize text and tag sentences with connector patterns.

    Args:
        text: The full text to process
        debug: Print debug information

    Returns:
        List of dicts with 'sentence' and connector tags
    """
    sentences = sent_tokenize(text)
    tagged = []

    print(f"Tokenized {len(sentences)} sentences")
    print("Parsing connector patterns...")

    for i, sentence in enumerate(sentences):
        prev_sentence = sentences[i-1] if i > 0 else ""
        tags = parse_connector_patterns(sentence, prev_sentence)

        entry = {'sentence': sentence, 'index': i}
        entry.update(tags)
        tagged.append(entry)

        if debug and tags:
            print(f"  [{i}] {list(tags.keys())}: {sentence[:60]}...")

    # Count tags
    tag_counts = {}
    for entry in tagged:
        for key in entry:
            if key not in ['sentence', 'index']:
                tag_counts[key] = tag_counts.get(key, 0) + 1

    print(f"Initial tag counts: {tag_counts}")
    return tagged


def disambiguate_tagged_sentences(tagged: List[Dict], debug: bool = False) -> List[Dict]:
    """
    Use LLM to disambiguate ambiguous connector usages.

    Once a category reaches CAP_WHERE_VERIFICATION_STOPS verified examples,
    ambiguous connectors in that category are skipped (tag removed) without
    LLM verification to save time. Non-ambiguous connectors still pass through.

    Args:
        tagged: List of tagged sentence dicts
        debug: Print debug information

    Returns:
        Updated list with false positives removed
    """
    print("\nDisambiguating ambiguous connectors...")
    print(f"  (Will stop verifying each category after {CAP_WHERE_VERIFICATION_STOPS} verified examples)")

    removed_count = 0
    skipped_count = 0

    # Track verified counts per category
    verified_counts: Dict[str, int] = {}

    for i, entry in enumerate(tagged):
        sentence = entry['sentence']
        prev_sentence = tagged[i-1]['sentence'] if i > 0 else ""

        # Check each ambiguous connector
        for connector, category in AMBIGUOUS_CONNECTORS.items():
            if category in entry:
                conn, pos = entry[category]
                if conn == connector:
                    # Check if we've already verified enough for this category
                    if verified_counts.get(category, 0) >= CAP_WHERE_VERIFICATION_STOPS:
                        # Skip LLM call, just remove the ambiguous tag
                        del entry[category]
                        skipped_count += 1
                        if skipped_count <= 5 or skipped_count % 50 == 0:
                            print(f"  Skipping '{connector}' in sentence {i} ({category} has {verified_counts[category]} verified)")
                        continue

                    print(f"  Checking '{connector}' in sentence {i}...")
                    is_logical = disambiguate_temporal_vs_logical(
                        sentence, connector, prev_sentence, debug
                    )
                    if not is_logical:
                        print(f"    -> Temporal usage, removing {category} tag")
                        del entry[category]
                        removed_count += 1
                    else:
                        print(f"    -> Logical usage, keeping tag")
                        verified_counts[category] = verified_counts.get(category, 0) + 1

        # Verify causal sentences
        if 'causalsentence' in entry:
            # Check if we've already verified enough
            if verified_counts.get('causalsentence', 0) >= CAP_WHERE_VERIFICATION_STOPS:
                # causalsentence verification is for all, not just ambiguous, so we keep the tag
                # but skip the LLM verification
                verified_counts['causalsentence'] = verified_counts.get('causalsentence', 0) + 1
            else:
                print(f"  Verifying causal sentence {i}...")
                is_causal = verify_causal_sentence(sentence, prev_sentence, debug)
                if not is_causal:
                    print(f"    -> Not actually causal, removing tag")
                    del entry['causalsentence']
                    removed_count += 1
                else:
                    print(f"    -> Confirmed causal")
                    verified_counts['causalsentence'] = verified_counts.get('causalsentence', 0) + 1

    print(f"Removed {removed_count} false positive tags")
    print(f"Skipped {skipped_count} ambiguous tags (category cap reached)")
    print(f"Verified counts: {verified_counts}")

    # Recount tags
    tag_counts = {}
    for entry in tagged:
        for key in entry:
            if key not in ['sentence', 'index']:
                tag_counts[key] = tag_counts.get(key, 0) + 1

    print(f"Final tag counts: {tag_counts}")
    return tagged


def save_tagged_sentences(tagged: List[Dict], filepath: str) -> None:
    """Save tagged sentences to JSONL file for resumability."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for entry in tagged:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    print(f"Saved tagged sentences to: {filepath}")


def load_tagged_sentences(filepath: str) -> List[Dict]:
    """Load tagged sentences from JSONL file."""
    tagged = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                tagged.append(json.loads(line))
    print(f"Loaded {len(tagged)} tagged sentences from: {filepath}")
    return tagged


def build_category_index(tagged: List[Dict]) -> Dict[str, List[int]]:
    """
    Build index mapping categories to sentence indices.

    Args:
        tagged: List of tagged sentence dicts

    Returns:
        Dict mapping category names to lists of sentence indices
    """
    index = {}

    for entry in tagged:
        for key in entry:
            if key not in ['sentence', 'index']:
                if key not in index:
                    index[key] = []
                index[key].append(entry['index'])

    return index


# Categories where clause extraction should stop at internal punctuation
# rather than extending to end of sentence
CLAUSE_STOPS_AT_PUNCTUATION = {'conditionalclause'}


def extract_clause_to_punctuation(sentence: str, word_pos: int) -> str:
    """
    Extract clause from word position to the next punctuation mark.

    This is used for clause types (like conditionalclause) where the clause
    should not extend to the end of the sentence, but only to the next
    comma, semicolon, or other punctuation.

    Example:
        sentence: "Game wardens are rarely able to prosecute; if the evidence has been consumed, there will be no grounds."
        word_pos: 8 (position of "if")
        result: "if the evidence has been consumed"

    Args:
        sentence: The full sentence text
        word_pos: Starting word position for the clause

    Returns:
        The extracted clause (without trailing punctuation)
    """
    words = sentence.split()

    # Build clause word by word, stopping at punctuation
    clause_words = []
    for i in range(word_pos, len(words)):
        word = words[i]
        # Check if word ends with clause-ending punctuation
        if word.rstrip('.,;:!?') != word:
            # Word has trailing punctuation - include the word but strip punctuation
            clause_words.append(word.rstrip('.,;:!?'))
            break
        else:
            clause_words.append(word)

    return ' '.join(clause_words)


def extract_ground_truth(sentence: str, tag_info: Tuple[str, int], is_clause: bool,
                         category: str = '') -> str:
    """
    Extract ground truth answer from sentence.

    Args:
        sentence: The full sentence text
        tag_info: Tuple of (connector, word_position)
        is_clause: Whether to extract clause (vs full sentence)
        category: The connector category (used to determine extraction method)

    Returns:
        The ground truth string
    """
    if not is_clause:
        return sentence.strip()

    connector, word_pos = tag_info

    # For certain categories, stop at punctuation rather than sentence end
    if category in CLAUSE_STOPS_AT_PUNCTUATION:
        return extract_clause_to_punctuation(sentence, word_pos)

    # Default: extract from word position to end
    words = sentence.split()
    clause = ' '.join(words[word_pos:])

    # Remove trailing punctuation that belongs to parent sentence
    clause = clause.rstrip('.,;:!?')

    return clause


def build_passage(tagged: List[Dict], target_idx: int, category: str) -> Optional[Dict]:
    """
    Build a passage with masked sentence/clause.

    Args:
        tagged: List of tagged sentence dicts
        target_idx: Index of the target sentence
        category: The connector category

    Returns:
        Dict with passage, ground_truth, mask_string, etc. or None if invalid
    """
    is_clause = 'clause' in category

    # Get tag info
    entry = tagged[target_idx]
    if category not in entry:
        return None

    tag_info = entry[category]

    # Normalize sentence text: replace newlines with spaces, collapse double spaces
    def normalize_text(text: str) -> str:
        result = text.replace('\n', ' ')
        while '  ' in result:
            result = result.replace('  ', ' ')
        return result

    target_sentence = normalize_text(entry['sentence'])

    # Extract ground truth
    ground_truth = extract_ground_truth(target_sentence, tag_info, is_clause, category)

    # Collect preceding sentences until >= MIN_PRECEDING_WORDS
    preceding = []
    word_count = 0
    idx = target_idx - 1

    while idx >= 0 and word_count < MIN_PRECEDING_WORDS:
        sent = normalize_text(tagged[idx]['sentence'])
        preceding.insert(0, sent)
        word_count += len(sent.split())
        idx -= 1

    if word_count < MIN_PRECEDING_WORDS:
        return None  # Too close to start of text

    # Determine if including following sentence
    include_following = random.random() < INCLUDE_FOLLOWING_PROB
    following = []

    if include_following and target_idx + 1 < len(tagged):
        following.append(normalize_text(tagged[target_idx + 1]['sentence']))

    # Create mask string
    mask_string = TAG_DESCRIPTIONS[category]

    # Build masked version of target
    if is_clause:
        # Mask just the clause portion
        masked_sentence = target_sentence.replace(ground_truth, mask_string)
    else:
        # Mask entire sentence
        masked_sentence = mask_string

    # Assemble masked passage (for the question)
    passage_parts = preceding + [masked_sentence] + following
    passage = ' '.join(passage_parts)

    # Assemble full unmasked passage (for the "passage" field in output)
    full_passage_parts = preceding + [target_sentence] + following
    full_passage = ' '.join(full_passage_parts)

    return {
        'passage': passage,
        'ground_truth': ground_truth,
        'mask_string': mask_string,
        'is_clause': is_clause,
        'category': category,
        'target_idx': target_idx,
        'full_sentence': target_sentence,
        'full_passage': full_passage
    }


def get_distractor_candidates(tagged: List[Dict], category: str,
                              exclude_idx: int, ground_truth: str) -> List[str]:
    """
    Get candidate sentences/clauses from the same category for same_book distractors.

    Args:
        tagged: List of tagged sentence dicts
        category: The connector category
        exclude_idx: Index to exclude (the ground truth sentence)
        ground_truth: The ground truth text to exclude (avoids duplicates)

    Returns:
        List of unique candidate strings (excluding ground truth)
    """
    is_clause = 'clause' in category
    candidates = []
    seen_text: Set[str] = set()

    # Normalize ground truth for comparison
    gt_normalized = ground_truth.strip().lower()
    seen_text.add(gt_normalized)

    for entry in tagged:
        if entry['index'] == exclude_idx:
            continue
        if category in entry:
            candidate = extract_ground_truth(entry['sentence'], entry[category], is_clause, category)
            # Normalize for deduplication
            candidate_normalized = candidate.strip().lower()

            if candidate_normalized not in seen_text:
                seen_text.add(candidate_normalized)
                candidates.append(candidate)

    return candidates


def present_question_for_approval(passage_data: Dict, metadata_prefix: str) -> str:
    """
    Present a question to the user for approval.

    Args:
        passage_data: Dict with passage, ground_truth, etc.
        metadata_prefix: The metadata frame string

    Returns:
        "accept", "reject", or "stop"
    """
    print("\n" + "=" * 70)
    print("PROPOSED QUESTION")
    print("=" * 70)
    print()
    print(f"metadata prefix: \"{metadata_prefix}\"")
    print()
    print(f"passage: \"{passage_data['passage']}\"")
    print()

    answer_type = "clause" if passage_data['is_clause'] else "sentence"
    prompt = f"Write a {answer_type} appropriate for this book that could stand in the position marked by {passage_data['mask_string']}:"
    print(f"prompt: \"{prompt}\"")
    print()
    print(f"ground truth answer: \"{passage_data['ground_truth']}\"")
    print()
    print(f"Category: {passage_data['category']}")
    print("=" * 70)

    while True:
        response = input("\nAccept this question? (y/n/p=show full sentence/stop): ").strip().lower()

        if response in ['y', 'yes']:
            return "accept"
        elif response in ['n', 'no', '']:
            return "reject"
        elif response == 'p':
            print(f"\nFull sentence: {passage_data['full_sentence']}")
        elif response == 'stop':
            return "stop"
        else:
            print("Please enter 'y', 'n', 'p', or 'stop'")


def present_distractors_for_approval(distractors: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    Present distractors for individual approval.

    Args:
        distractors: List of (text, type) tuples

    Returns:
        List of approved (text, type) tuples
    """
    approved = []

    print("\n" + "-" * 50)
    print("DISTRACTOR REVIEW")
    print("-" * 50)

    for i, (text, dtype) in enumerate(distractors):
        print(f"\nDistractor {i+1} ({dtype}):")
        print(f"  \"{text}\"")

        while True:
            response = input("  Accept (a), reject (r), or manual replacement (m)? ").strip().lower()

            if response in ['a', 'accept']:
                approved.append((text, dtype))
                break
            elif response in ['r', 'reject']:
                break
            elif response in ['m', 'manual']:
                manual_text = input("  Enter replacement: ").strip()
                if manual_text:
                    approved.append((manual_text, f"manual_{dtype}"))
                break
            else:
                print("  Please enter 'a', 'r', or 'm'")

    return approved


def save_question(question_data: Dict, output_path: str) -> None:
    """
    Save a question to the output JSONL file.

    Args:
        question_data: The question dict
        output_path: Path to output file
    """
    with open(output_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(question_data, ensure_ascii=False) + '\n')


def format_question_output(passage_data: Dict, metadata: Dict,
                           metadata_prefix: str,
                           answer_strings: List[str],
                           answer_types: List[str],
                           answer_probabilities: List[float]) -> Dict:
    """
    Format the final question output.

    Args:
        passage_data: Dict with passage, ground_truth, etc.
        metadata: The metadata dict
        metadata_prefix: The formatted metadata prefix
        answer_strings: List of answer strings
        answer_types: List of answer type labels
        answer_probabilities: List of probabilities

    Returns:
        Formatted question dict for JSONL output
    """
    answer_type = "clause" if passage_data['is_clause'] else "sentence"
    prompt = f"Write a {answer_type} appropriate for this book that could stand in the position marked by {passage_data['mask_string']}:"

    return {
        "metadata_frame": metadata_prefix,
        "main_question": f"{passage_data['passage']}\n\n{prompt}",
        "source_title": metadata['source_title'],
        "source_author": metadata['source_author'],
        "source_date": metadata['source_date'],
        "author_nationality": metadata['author_nationality'],
        "source_genre": metadata['genre'],
        "author_birth": metadata['author_birth'],
        "author_profession": metadata['author_profession'],
        "source_htid": metadata['source_htid'],
        "question_category": f"cloze_{passage_data['category']}",
        "question_process": "automatic",
        "answer_types": answer_types,
        "answer_strings": answer_strings,
        "answer_probabilities": answer_probabilities,
        "passage": passage_data['full_passage']
    }


def process_questions(tagged: List[Dict], metadata: Dict, output_path: str,
                      verbose_bert: bool = False, debug: bool = False) -> None:
    """
    Main question generation loop.

    Args:
        tagged: List of tagged sentence dicts
        metadata: Metadata dict
        output_path: Path to output JSONL file
        verbose_bert: Print BERT ranking details
        debug: Enable debug output
    """
    # Build metadata prefix
    metadata_prefix = build_metadata_prefix(metadata)

    # Build category index
    category_index = build_category_index(tagged)

    # Find viable categories (>= 3 examples)
    viable_categories = {cat: indices for cat, indices in category_index.items()
                         if len(indices) >= MIN_CATEGORY_EXAMPLES}

    if not viable_categories:
        print("\nError: No categories have >= 3 examples. Cannot generate questions.")
        return

    print(f"\nViable categories: {list(viable_categories.keys())}")

    # Track which sentences have been used
    used_indices: Set[int] = set()

    # Track accepted questions per category
    accepted_per_category: Dict[str, int] = {cat: 0 for cat in viable_categories}

    questions_generated = 0
    questions_accepted = 0

    print("\n" + "=" * 70)
    print("Starting question generation...")
    print("=" * 70)

    # Continue until we have one accepted question per category or exhaust options
    while any(accepted_per_category[cat] == 0 for cat in viable_categories):
        # Pick a category that doesn't have an accepted question yet
        remaining_cats = [cat for cat in viable_categories
                         if accepted_per_category[cat] == 0]

        if not remaining_cats:
            break

        category = random.choice(remaining_cats)

        # Get unused indices for this category
        available = [idx for idx in viable_categories[category]
                     if idx not in used_indices]

        if not available:
            print(f"\nNo more available sentences in {category}")
            # Remove from viable to avoid infinite loop
            del viable_categories[category]
            continue

        # Select random sentence
        target_idx = random.choice(available)

        # Build passage
        passage_data = build_passage(tagged, target_idx, category)

        if passage_data is None:
            print(f"\n  Could not build passage for sentence {target_idx} (too close to text boundary)")
            used_indices.add(target_idx)
            continue

        questions_generated += 1

        # Present for approval
        try:
            decision = present_question_for_approval(passage_data, metadata_prefix)
        except KeyboardInterrupt:
            print("\n\nStopped by user (Ctrl+C).")
            break

        if decision == "stop":
            print("\nStopped by user.")
            break

        if decision == "reject":
            used_indices.add(target_idx)
            print("Question rejected.")
            continue

        # Question accepted - generate distractors
        print("\nGenerating distractors...")

        # Get same_book candidates (excluding ground truth and duplicates)
        candidates = get_distractor_candidates(tagged, category, target_idx, passage_data['ground_truth'])

        # Build prompt for distractor generation
        answer_type = "clause" if passage_data['is_clause'] else "sentence"
        prompt = f"Write a {answer_type} appropriate for this book that could stand in the position marked by {passage_data['mask_string']}:"

        answer_strings, answer_types, answer_probabilities = generate_distractors(
            metadata_prefix=metadata_prefix,
            passage=passage_data['passage'],
            prompt=prompt,
            ground_truth=passage_data['ground_truth'],
            distractor_candidates=candidates,
            mask_string=passage_data['mask_string'],
            distractor_types=DEFAULT_DISTRACTOR_TYPES,
            is_clause=passage_data['is_clause'],
            verbose_bert=verbose_bert,
            debug=debug
        )

        # Present distractors (excluding ground truth which is first)
        distractors_for_review = list(zip(answer_strings[1:], answer_types[1:]))
        approved_distractors = present_distractors_for_approval(distractors_for_review)

        if not approved_distractors:
            print("No distractors approved. Question not saved.")
            used_indices.add(target_idx)
            continue

        # Rebuild answer lists with approved distractors
        final_strings = [passage_data['ground_truth']]
        final_types = ["ground_truth"]
        final_probs = [1.0]

        for text, dtype in approved_distractors:
            final_strings.append(text)
            final_types.append(dtype)
            final_probs.append(0.0)

        # Format and save
        question_output = format_question_output(
            passage_data, metadata, metadata_prefix,
            final_strings, final_types, final_probs
        )

        save_question(question_output, output_path)

        used_indices.add(target_idx)
        accepted_per_category[category] += 1
        questions_accepted += 1

        print(f"\nQuestion accepted and saved. ({questions_accepted} total)")
        print(f"Progress: {accepted_per_category}")

    # Final summary
    print(f"\n{'=' * 70}")
    print("Summary")
    print(f"{'=' * 70}")
    print(f"Questions generated: {questions_generated}")
    print(f"Questions accepted: {questions_accepted}")
    print(f"Accepted per category: {accepted_per_category}")
    print(f"Output file: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate cloze-style benchmark questions from historical texts"
    )

    parser.add_argument("input_file",
                        help="Path to input text file")
    parser.add_argument("--metadata",
                        help="Path to JSON metadata file for this book")
    parser.add_argument("--primary-metadata",
                        help=f"Path to primary_metadata.csv for defaults (default: {DEFAULT_PRIMARY_METADATA})")
    parser.add_argument("--resume",
                        help="Resume from tagged sentences file")
    parser.add_argument("--output",
                        help="Output JSONL file (default: process_files/{barcode}_clozequestions.jsonl)")
    parser.add_argument("--verbose-bert", action="store_true",
                        help="Print BERT ranking details")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug output")

    args = parser.parse_args()

    # Derive paths
    input_path = Path(args.input_file)
    barcode = input_path.stem.upper()

    script_dir = Path(__file__).parent
    process_dir = script_dir / "process_files"
    process_dir.mkdir(exist_ok=True)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = process_dir / f"{barcode}_clozequestions.jsonl"

    if args.metadata:
        metadata_path = Path(args.metadata)
    else:
        # Use central metadata directory (shared across pipelines)
        CENTRAL_METADATA_DIR.mkdir(exist_ok=True)
        metadata_path = CENTRAL_METADATA_DIR / f"{barcode}_metadata.json"

    tagged_path = process_dir / f"{barcode}_tagged.jsonl"

    # Load primary metadata CSV for defaults
    primary_csv_path = Path(args.primary_metadata) if args.primary_metadata else DEFAULT_PRIMARY_METADATA
    print(f"Loading primary metadata from: {primary_csv_path}")
    primary_metadata = load_primary_metadata_csv(primary_csv_path)
    print(f"  Loaded {len(primary_metadata)} entries")

    # Look up this barcode in CSV
    csv_key = barcode_to_csv_key(barcode)
    csv_metadata = primary_metadata.get(csv_key, {})
    if csv_metadata:
        print(f"  Found entry for {csv_key}")
    else:
        print(f"  No entry found for {csv_key}")

    print("\n" + "=" * 70)
    print("Cloze Question Generator")
    print("=" * 70)
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print(f"Metadata: {metadata_path}")

    # Load or create metadata
    print("\nLoading metadata...")
    metadata = load_or_create_metadata(str(input_path), str(metadata_path), csv_metadata)
    print(f"  Title: {metadata['source_title']}")
    if _is_anonymous_author(metadata.get('source_author', '')):
        print(f"  Author: Anonymous")
    else:
        print(f"  Author: {metadata['source_author']} ({metadata.get('author_profession', 'writer')})")
    print(f"  Date: {metadata['source_date']}")

    # Load or create tagged sentences
    if args.resume and Path(args.resume).exists():
        tagged = load_tagged_sentences(args.resume)
    elif tagged_path.exists():
        print(f"\nFound existing tagged file: {tagged_path}")
        use_existing = input("Use existing tagged sentences? (y/n) [y]: ").strip().lower()
        if use_existing in ['y', 'yes', '']:
            tagged = load_tagged_sentences(str(tagged_path))
        else:
            # Read and process text
            print(f"\nReading text from: {input_path}")
            with open(input_path, 'r', encoding='utf-8') as f:
                text = f.read()

            tagged = tokenize_and_tag_sentences(text, args.debug)
            tagged = disambiguate_tagged_sentences(tagged, args.debug)
            save_tagged_sentences(tagged, str(tagged_path))
    else:
        # Read and process text
        print(f"\nReading text from: {input_path}")
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()

        tagged = tokenize_and_tag_sentences(text, args.debug)
        tagged = disambiguate_tagged_sentences(tagged, args.debug)
        save_tagged_sentences(tagged, str(tagged_path))

    # Check viability
    if len(tagged) < MIN_SENTENCES_REQUIRED:
        print(f"\nError: Text too short ({len(tagged)} sentences, need {MIN_SENTENCES_REQUIRED})")
        sys.exit(1)

    # Process questions
    process_questions(tagged, metadata, str(output_path),
                      args.verbose_bert, args.debug)


if __name__ == "__main__":
    main()

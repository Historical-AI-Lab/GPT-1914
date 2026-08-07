#!/usr/bin/env python3
"""
Cloze Question Generator

Generates cloze-style benchmark questions from historical texts by:
1. Detecting logical connectors (cause, effect, contrast) at the start of a sentence
2. Masking the whole sentence containing the connector
3. Creating multiple-choice questions with distractors

The answer to a cloze question is always a complete sentence. Distractors are
generated through OpenRouter (Qwen and Gemma); no local model server is needed.

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

try:
    from nltk import sent_tokenize
except ImportError:
    import nltk
    nltk.download('punkt', quiet=True)
    from nltk import sent_tokenize

# Import distractor generator
from distractor_generator import (
    generate_distractors,
    call_openrouter_model,
    PRIMARY_MODEL,
    SECONDARY_MODEL,
)

# Constants
VERIFICATION_MODEL = PRIMARY_MODEL
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
    f"anachronistic_{PRIMARY_MODEL}",
    f"anachronistic_{SECONDARY_MODEL}"
]

# Metadata template (different from character questions)
METADATA_FRAME_TEMPLATE = """The following passage comes from {title}, {a_an_genre} {genre} published in {year} by {author}, {a_an_nat} {nationality} {profession}."""
METADATA_FRAME_NOAUTHOR = """The following passage comes from {title}, {a_an_genre} {genre} published in {year}."""
# Tag descriptions for mask strings.
#
# Only sentence-level categories are generated: the answer to a cloze question
# is always a complete sentence. Clause-level categories (causalclause,
# effectclause, contrastclause, conditionalclause, concessiveclause) were
# retired; questions of those kinds already in the benchmark are unaffected.
TAG_DESCRIPTIONS = {
    'causalsentence': '[masked sentence describing a cause or reason]',
    'effectsentence': '[masked sentence describing an inference or effect]',
    'contrastsentence': '[masked sentence revising an implied expectation]'
}

# Connector patterns from connector_list.md
CONNECTOR_PATTERNS = {
    # CAUSE/REASON
    'causalsentence': {
        'first_word': [],
        'first_five_words': ['justification', 'rationale', 'purpose', 'cause', 'because'],
        'prev_sentence_why': True
    },
    # EFFECT/INFERENCE
    'effectsentence': {
        'first_word': ['so', 'hence'],
        'first_five_words': ['thus', 'therefore', 'thence', 'accordingly',
                             'consequence', 'result', 'effect', 'consequently',
                             'it follows that']
    },
    # CONTRAST
    'contrastsentence': {
        'first_word': ['but', 'yet'],
        'first_five_words': ['however', 'nevertheless']
    }
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
                metadata[barcode_to_csv_key(barcode)] = row

    return metadata


def barcode_to_csv_key(barcode: str) -> str:
    """
    Convert filename barcode to CSV lookup key.

    Filename: 32044106370034 or HN1IMP (uppercase for alphabetic)
    CSV key: hvd.32044106370034 or hvd.hn1imp (with hvd. prefix, lowercase)
    """
    if barcode.lower().startswith('hvd.'):
        return barcode.lower()
    return f"hvd.{barcode.lower()}"


def parse_year(year_str: Any) -> Optional[int]:
    """
    Parse a year string to int, tolerating float-formatted CSV values
    like "1841.0" (pandas writes int columns with NaNs as floats).

    Returns None for blank or unparseable input.
    """
    year_str = str(year_str or '').strip()
    if not year_str:
        return None
    try:
        return int(float(year_str))
    except ValueError:
        return None


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
                        metadata[field] = parse_year(value) or 0
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
    # Normalize to a bare year: the CSV can carry float-formatted values ("1854.0")
    default_year = parse_year(csv_metadata.get('firstpub') or csv_metadata.get('date1_src', ''))
    default_date = str(default_year) if default_year is not None else ''
    default_htid = barcode_to_csv_key(barcode)
    default_nationality = csv_metadata.get('authnationality', '')

    # Parse author birth year from authordates if available (format: "1829-1900")
    author_dates = csv_metadata.get('authordates', '')
    default_birth = ''
    if author_dates and '-' in author_dates:
        birth_year = parse_year(author_dates.split('-')[0])
        default_birth = str(birth_year) if birth_year is not None else ''

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
    metadata['source_date'] = parse_year(date_val) or 0

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
        metadata['author_birth'] = parse_year(birth_val) or 0

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


def parse_connector_patterns(sentence: str, prev_sentence: str = "") -> Dict[str, Tuple[str, int]]:
    """
    Parse a sentence for connector patterns.

    Args:
        sentence: The sentence to analyze
        prev_sentence: The previous sentence (for why? rule)

    Returns:
        Dict mapping category names to (connector, word_position) tuples
        e.g., {'contrastsentence': ('but', 0), 'effectsentence': ('thus', 2)}
    """
    tags = {}

    # Prepare words list (lowercase, punctuation stripped)
    words = sentence.split()
    words_clean = [w.lower().rstrip(',.;:!?"\')') for w in words]

    # Check each category. All surviving categories are sentence-initial.
    for category, rules in CONNECTOR_PATTERNS.items():
        result = _check_sentence_start(words_clean, category, rules)
        if result:
            tags[category] = result

    # Special: why? previous sentence rule for causal sentence
    if prev_sentence and _is_why_question(prev_sentence):
        if 'causalsentence' not in tags:
            tags['causalsentence'] = (words_clean[0] if words_clean else '', 0)

    return tags


CAUSAL_VERIFICATION_PROMPT = """Read the following two sentences. Does the second sentence express a CAUSE, REASON, or EXPLANATION for something mentioned or implied in the first sentence?

Previous sentence: {prev}
Current sentence: {current}

Respond "YES" if the current sentence explains why something happens or provides a reason.
Respond "NO" if it does not express causation or explanation.
Then provide a one-sentence explanation."""


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

    result = call_openrouter_model(prompt, model=VERIFICATION_MODEL, debug=debug)

    if result['status'] != 'success':
        print(f"  Warning: Causal verification failed ({result['reason']}), keeping tag")
        return True

    return result['response'].strip().upper().startswith('YES')


def clean_ocr_text(text: str) -> str:
    """
    Light OCR repair for early-print scans, applied before sentence tokenization.

    The edgebooks texts are mostly reflowed already, so the dominant artifact is
    not hyphenation but short ALL-CAPS running heads and bare page numbers
    dropped into the middle of paragraphs, which both split real sentences and
    inject junk "sentences". Measured across the 92-volume corpus: running heads
    and page numbers occur 3-65 per 10,000 words; hyphenated line-break splits
    only 1-5 per 10,000 words.

    This is deliberately shallow. It will occasionally drop a legitimate short
    ALL-CAPS line (a shouted line of dialogue, a line of small-caps verse) and
    will occasionally merge a genuine hyphenated compound broken across lines.
    Both are far rarer than the artifacts being removed, and the interactive
    edit_passage step remains available as a backstop.

    Args:
        text: Raw text as read from the volume file

    Returns:
        Cleaned text, with paragraph breaks (blank lines) preserved
    """
    # Rejoin words split by a hyphen at a line ending
    text = re.sub(r'(\w)-[ \t]*\n[ \t]*(\w)', r'\1\2', text)

    kept_lines = []
    for line in text.split('\n'):
        stripped = line.strip()
        if stripped:
            # Bare page or section number (arabic or roman)
            if re.fullmatch(r'[\dIVXLC.,\-—\[\]() ]{1,12}', stripped):
                continue
            # Short ALL-CAPS line: a running head or chapter heading
            if (len(stripped) < 45 and stripped == stripped.upper()
                    and re.search(r'[A-Z]{3}', stripped)):
                continue
        kept_lines.append(line)
    text = '\n'.join(kept_lines)

    # Drop spaces the OCR inserted before punctuation
    text = re.sub(r'[ \t]+([,;:.!?])', r'\1', text)
    # Reflow paragraph interiors: a lone newline is a line wrap, not a break
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

    return re.sub(r'[ \t]{2,}', ' ', text)


def tokenize_and_tag_sentences(text: str, debug: bool = False) -> List[Dict]:
    """
    Tokenize text and tag sentences with connector patterns.

    Args:
        text: The full text to process
        debug: Print debug information

    Returns:
        List of dicts with 'sentence' and connector tags
    """
    text = clean_ocr_text(text)
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
    Use an LLM to verify that sentences tagged 'causalsentence' really are causal.

    Once the category reaches CAP_WHERE_VERIFICATION_STOPS verified examples,
    remaining tags are kept without an LLM call to save time.

    (This function formerly also disambiguated temporal vs. logical uses of
    'since', 'as', 'then' and 'while'. Those connectors only ever produced
    clause-level tags, so that pass went away with the clause categories.)

    Args:
        tagged: List of tagged sentence dicts
        debug: Print debug information

    Returns:
        Updated list with false positives removed
    """
    print("\nVerifying causal sentences...")
    print(f"  (Will stop verifying after {CAP_WHERE_VERIFICATION_STOPS} verified examples)")

    removed_count = 0

    # Track verified counts per category
    verified_counts: Dict[str, int] = {}

    for i, entry in enumerate(tagged):
        sentence = entry['sentence']
        prev_sentence = tagged[i-1]['sentence'] if i > 0 else ""

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

    Only live categories are indexed. A *_tagged.jsonl file saved before the
    clause categories were retired still carries keys like 'causalclause';
    ignoring them here keeps those files reusable via --resume instead of
    failing later on a TAG_DESCRIPTIONS lookup.

    Args:
        tagged: List of tagged sentence dicts

    Returns:
        Dict mapping category names to lists of sentence indices
    """
    index = {}

    for entry in tagged:
        for key in entry:
            if key in TAG_DESCRIPTIONS:
                if key not in index:
                    index[key] = []
                index[key].append(entry['index'])

    return index


def extract_ground_truth(sentence: str, tag_info: Tuple[str, int],
                         is_clause: bool = False, category: str = '') -> str:
    """
    Extract ground truth answer from sentence.

    Every surviving category is sentence-level, so the ground truth is always
    the whole sentence.

    Args:
        sentence: The full sentence text
        tag_info: Tuple of (connector, word_position); unused, kept for callers
        is_clause: Vestigial, always False
        category: The connector category; unused

    Returns:
        The ground truth string
    """
    return sentence.strip()


def build_passage(tagged: List[Dict], target_idx: int, category: str) -> Optional[Dict]:
    """
    Build a passage with the target sentence masked.

    Args:
        tagged: List of tagged sentence dicts
        target_idx: Index of the target sentence
        category: The connector category

    Returns:
        Dict with passage, ground_truth, mask_string, etc. or None if invalid
    """
    # Vestigial: all categories are sentence-level now. The field is retained
    # because approve_batched_questions.py and older batch files still read it.
    is_clause = False

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
    ground_truth = extract_ground_truth(target_sentence, tag_info)

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

    # Mask the entire target sentence
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
    Get candidate sentences from the same category for same_book distractors.

    Args:
        tagged: List of tagged sentence dicts
        category: The connector category
        exclude_idx: Index to exclude (the ground truth sentence)
        ground_truth: The ground truth text to exclude (avoids duplicates)

    Returns:
        List of unique candidate strings (excluding ground truth)
    """
    candidates = []
    seen_text: Set[str] = set()

    # Normalize ground truth for comparison
    gt_normalized = ground_truth.strip().lower()
    seen_text.add(gt_normalized)

    for entry in tagged:
        if entry['index'] == exclude_idx:
            continue
        if category in entry:
            candidate = extract_ground_truth(entry['sentence'], entry[category], False, category)
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

    prompt = f"Write a sentence appropriate for this book that could stand in the position marked by {passage_data['mask_string']}:"
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


def edit_passage(passage_data: Dict) -> Dict:
    """
    Optionally edit the passage to fix noise like running page headers.

    Offers two modes:
    - Delete: remove a substring (e.g., an intruding running header)
    - Edit: enter a fully revised passage (multi-line, terminated by ===)

    Loops to allow multiple edits. Applies changes to passage, full_passage,
    full_sentence, and ground_truth as appropriate.

    Args:
        passage_data: Dict with passage, full_passage, ground_truth, mask_string, etc.

    Returns:
        Updated passage_data dict (modified in place)
    """
    while True:
        response = input("\nEdit passage? (y or enter for no): ").strip().lower()

        if response in ['', 'n', 'no']:
            return passage_data

        if response not in ['y', 'yes']:
            continue

        print("  (d) Delete a string from the passage")
        print("  (e) Enter edited passage (end with a line containing only ===)")

        mode = input("  Choice: ").strip().lower()

        if mode == 'd':
            to_delete = input("  String to delete: ")
            if to_delete:
                for key in ['passage', 'full_passage', 'full_sentence', 'ground_truth']:
                    passage_data[key] = passage_data[key].replace(to_delete, '')
                    # Clean up double spaces left by deletion
                    while '  ' in passage_data[key]:
                        passage_data[key] = passage_data[key].replace('  ', ' ')
                    passage_data[key] = passage_data[key].strip()
                print(f"\n  Updated passage: \"{passage_data['passage']}\"")

        elif mode == 'e':
            print("  Enter the edited passage (end with a line containing only ===):")
            lines = []
            while True:
                line = input()
                if line.strip() == '===':
                    break
                lines.append(line)
            new_passage = ' '.join(lines)
            while '  ' in new_passage:
                new_passage = new_passage.replace('  ', ' ')
            new_passage = new_passage.strip()

            passage_data['passage'] = new_passage
            # Reconstruct full_passage by replacing mask with ground truth
            passage_data['full_passage'] = new_passage.replace(
                passage_data['mask_string'], passage_data['ground_truth']
            )
            print(f"\n  Updated passage: \"{passage_data['passage']}\"")

        else:
            print("  Please enter 'd' or 'e'")
            continue

        # Loop back to allow further edits


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
    prompt = f"Write a sentence appropriate for this book that could stand in the position marked by {passage_data['mask_string']}:"

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

        # Offer chance to edit the passage before generating distractors
        passage_data = edit_passage(passage_data)

        # Question accepted - generate distractors
        print("\nGenerating distractors...")

        # Get same_book candidates (excluding ground truth and duplicates)
        candidates = get_distractor_candidates(tagged, category, target_idx, passage_data['ground_truth'])

        # Build prompt for distractor generation
        prompt = f"Write a sentence appropriate for this book that could stand in the position marked by {passage_data['mask_string']}:"

        answer_strings, answer_types, answer_probabilities = generate_distractors(
            metadata_prefix=metadata_prefix,
            passage=passage_data['passage'],
            prompt=prompt,
            ground_truth=passage_data['ground_truth'],
            distractor_candidates=candidates,
            mask_string=passage_data['mask_string'],
            distractor_types=DEFAULT_DISTRACTOR_TYPES,
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

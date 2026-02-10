#!/usr/bin/env python3
"""
Batch Cloze Question Generator

Non-interactive batch processing of books for cloze question generation.
Runs tagging, passage building, and distractor generation without user
interaction, saving potential questions for later approval.

Usage:
    python batched_cloze_questions.py BARCODE_FILE [OPTIONS]

    Options:
        --primary-metadata FILE      Path to primary_metadata.csv
                                     (default: ../primary_metadata.csv)
        --text-dir DIR               Directory containing text files
                                     (default: ../IDI_sample_1875-25)
        --candidates-per-category N  Max candidate passages per category (default: 15)
        --verbose-bert               Print BERT ranking details
        --debug                      Enable debug output
"""

import argparse
import json
import os
import random
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add connectors directory to path for imports
CONNECTORS_DIR = str(Path(__file__).parent.parent / "connectors")
if CONNECTORS_DIR not in sys.path:
    sys.path.insert(0, CONNECTORS_DIR)

from make_cloze_questions import (
    tokenize_and_tag_sentences,
    disambiguate_tagged_sentences,
    save_tagged_sentences,
    load_tagged_sentences,
    build_category_index,
    build_passage,
    get_distractor_candidates,
    load_primary_metadata_csv,
    barcode_to_csv_key,
    clean_title,
    reformat_author_name,
    build_metadata_prefix,
    _is_anonymous_author,
    format_question_output,
    TAG_DESCRIPTIONS,
    MIN_CATEGORY_EXAMPLES,
    MIN_SENTENCES_REQUIRED,
    DEFAULT_DISTRACTOR_TYPES,
)

from distractor_generator import generate_distractors

# Default paths
DEFAULT_PRIMARY_METADATA = Path(__file__).parent.parent / "primary_metadata.csv"
DEFAULT_TEXT_DIR = Path(__file__).parent.parent / "IDI_sample_1875-25"
DEFAULT_CANDIDATES_PER_CATEGORY = 15


def read_barcode_file(filepath: str) -> List[str]:
    """
    Read barcode file, one barcode per line.

    Strips whitespace, skips blank lines and # comments, uppercases all.

    Args:
        filepath: Path to barcode file

    Returns:
        List of uppercase barcode strings

    Raises:
        FileNotFoundError: If file does not exist
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Barcode file not found: {filepath}")

    barcodes = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            barcodes.append(line.upper())

    return barcodes


def build_provisional_metadata(barcode: str, csv_metadata: Dict) -> Dict:
    """
    Build metadata dict from CSV without user interaction.

    Uses clean_title(), reformat_author_name(), barcode_to_csv_key().
    Defaults: genre="novel", profession="".

    Args:
        barcode: The book barcode (e.g., "HN1IMP")
        csv_metadata: Dict of CSV row data for this barcode, or empty dict

    Returns:
        Metadata dict with standard fields
    """
    htid = barcode_to_csv_key(barcode)

    title = clean_title(csv_metadata.get('title_src', ''))
    author = reformat_author_name(csv_metadata.get('author_src', ''))
    date_str = csv_metadata.get('firstpub') or csv_metadata.get('date1_src', '')
    nationality = csv_metadata.get('authnationality', '')

    # Parse birth year
    author_dates = csv_metadata.get('authordates', '')
    birth = 0
    if author_dates and '-' in author_dates:
        try:
            birth = int(author_dates.split('-')[0].strip())
        except ValueError:
            birth = 0

    # Parse date
    try:
        date_val = int(date_str) if date_str else 0
    except ValueError:
        date_val = 0

    metadata = {
        'source_title': title or barcode,
        'source_author': author or 'Anonymous',
        'source_date': date_val,
        'source_htid': htid,
        'author_nationality': nationality,
        'genre': 'novel',
        'author_birth': birth,
        'author_profession': '',
    }

    # Clear author-related fields if anonymous
    if _is_anonymous_author(metadata['source_author']):
        metadata['author_nationality'] = ''
        metadata['author_birth'] = 0
        metadata['author_profession'] = ''

    return metadata


def generate_candidates_for_category(tagged: List[Dict], category: str,
                                     max_candidates: int = 15) -> List[Dict]:
    """
    Randomly sample sentence indices for a category and build passages.

    Args:
        tagged: List of tagged sentence dicts
        category: The connector category (e.g., 'causalclause')
        max_candidates: Maximum number of candidate passages to return

    Returns:
        List of up to max_candidates valid passage_data dicts
    """
    # Get all indices for this category
    indices = [entry['index'] for entry in tagged if category in entry
               and entry.get(category) is not None]

    # Shuffle for random sampling
    random.shuffle(indices)

    candidates = []
    for idx in indices:
        if len(candidates) >= max_candidates:
            break

        passage_data = build_passage(tagged, idx, category)
        if passage_data is not None:
            candidates.append(passage_data)

    return candidates


def generate_distractors_for_candidate(passage_data: Dict, tagged: List[Dict],
                                       metadata: Dict, metadata_prefix: str,
                                       verbose_bert: bool = False,
                                       debug: bool = False) -> Dict:
    """
    Generate distractors for one candidate passage.

    Calls generate_distractors() and format_question_output(), then merges
    in extra batch fields for later approval.

    Args:
        passage_data: Dict from build_passage()
        tagged: List of tagged sentence dicts
        metadata: Metadata dict
        metadata_prefix: Formatted metadata prefix string
        verbose_bert: Print BERT ranking details
        debug: Enable debug output

    Returns:
        Formatted question dict with extra batch fields
    """
    category = passage_data['category']
    target_idx = passage_data['target_idx']

    # Get same_book distractor candidates
    candidates = get_distractor_candidates(
        tagged, category, target_idx, passage_data['ground_truth']
    )

    # Build prompt
    answer_type = "clause" if passage_data['is_clause'] else "sentence"
    prompt = (f"Write a {answer_type} appropriate for this book that could "
              f"stand in the position marked by {passage_data['mask_string']}:")

    # Generate distractors
    answer_strings, answer_types, answer_probabilities = generate_distractors(
        metadata_prefix=metadata_prefix,
        passage=passage_data['passage'],
        prompt=prompt,
        ground_truth=passage_data['ground_truth'],
        distractor_candidates=candidates,
        mask_string=passage_data['mask_string'],
        distractor_types=DEFAULT_DISTRACTOR_TYPES,
        is_clause=passage_data['is_clause'],
        category=passage_data['category'],
        verbose_bert=verbose_bert,
        debug=debug
    )

    # Format using standard output format
    question_output = format_question_output(
        passage_data, metadata, metadata_prefix,
        answer_strings, answer_types, answer_probabilities
    )

    # Merge in extra batch fields for later approval
    question_output['is_clause'] = passage_data['is_clause']
    question_output['mask_string'] = passage_data['mask_string']
    question_output['full_sentence'] = passage_data['full_sentence']
    question_output['target_idx'] = passage_data['target_idx']
    question_output['masked_passage'] = passage_data['passage']
    question_output['ground_truth'] = passage_data['ground_truth']

    return question_output


def process_single_book(barcode: str, text_dir: Path, process_dir: Path,
                        csv_metadata: Dict,
                        candidates_per_category: int = 15,
                        verbose_bert: bool = False,
                        debug: bool = False) -> bool:
    """
    Full batch pipeline for one book.

    Args:
        barcode: Book barcode (e.g., "HN1IMP")
        text_dir: Directory containing text files
        process_dir: Directory for output files
        csv_metadata: Dict of CSV row data for this barcode
        candidates_per_category: Max candidates per category
        verbose_bert: Print BERT ranking details
        debug: Enable debug output

    Returns:
        True if processing succeeded, False otherwise
    """
    try:
        print(f"\n{'=' * 60}")
        print(f"Processing: {barcode}")
        print(f"{'=' * 60}")

        # Find text file
        text_path = text_dir / f"{barcode}.txt"
        if not text_path.exists():
            # Try lowercase
            text_path = text_dir / f"{barcode.lower()}.txt"
        if not text_path.exists():
            print(f"  Error: Text file not found for {barcode}")
            return False

        # Load or generate tagged sentences
        tagged_path = process_dir / f"{barcode}_tagged.jsonl"
        if tagged_path.exists():
            print(f"  Loading existing tagged sentences: {tagged_path}")
            tagged = load_tagged_sentences(str(tagged_path))
        else:
            print(f"  Reading text from: {text_path}")
            with open(text_path, 'r', encoding='utf-8') as f:
                text = f.read()

            tagged = tokenize_and_tag_sentences(text, debug)
            tagged = disambiguate_tagged_sentences(tagged, debug)
            save_tagged_sentences(tagged, str(tagged_path))

        # Check viability
        if len(tagged) < MIN_SENTENCES_REQUIRED:
            print(f"  Error: Text too short ({len(tagged)} sentences, "
                  f"need {MIN_SENTENCES_REQUIRED})")
            return False

        # Build provisional metadata
        metadata = build_provisional_metadata(barcode, csv_metadata)
        metadata_prefix = build_metadata_prefix(metadata)

        print(f"  Title: {metadata['source_title']}")
        print(f"  Author: {metadata['source_author']}")
        print(f"  Date: {metadata['source_date']}")

        # Build category index
        category_index = build_category_index(tagged)
        viable_categories = {cat: indices for cat, indices in category_index.items()
                             if len(indices) >= MIN_CATEGORY_EXAMPLES}

        if not viable_categories:
            print(f"  Error: No categories have >= {MIN_CATEGORY_EXAMPLES} examples")
            return False

        print(f"  Viable categories: {list(viable_categories.keys())}")

        # Generate candidates for each category
        output_path = process_dir / f"{barcode}_potentialquestions.jsonl"
        total_questions = 0

        with open(output_path, 'w', encoding='utf-8') as f:
            for category in viable_categories:
                print(f"  Generating candidates for {category}...")
                candidates = generate_candidates_for_category(
                    tagged, category, candidates_per_category
                )

                print(f"    Built {len(candidates)} candidate passages")

                for passage_data in candidates:
                    try:
                        question = generate_distractors_for_candidate(
                            passage_data, tagged, metadata, metadata_prefix,
                            verbose_bert, debug
                        )
                        f.write(json.dumps(question, ensure_ascii=False) + '\n')
                        total_questions += 1
                    except Exception as e:
                        print(f"    Warning: Failed to generate distractors "
                              f"for idx {passage_data['target_idx']}: {e}")
                        if debug:
                            traceback.print_exc()

        print(f"  Saved {total_questions} potential questions to: {output_path}")
        return True

    except Exception as e:
        print(f"  Error processing {barcode}: {e}")
        if debug:
            traceback.print_exc()
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch cloze question generator for multiple books"
    )

    parser.add_argument("barcode_file",
                        help="File with one barcode per line")
    parser.add_argument("--primary-metadata",
                        help=f"Path to primary_metadata.csv "
                             f"(default: {DEFAULT_PRIMARY_METADATA})")
    parser.add_argument("--text-dir",
                        help=f"Directory containing text files "
                             f"(default: {DEFAULT_TEXT_DIR})")
    parser.add_argument("--candidates-per-category", type=int,
                        default=DEFAULT_CANDIDATES_PER_CATEGORY,
                        help="Max candidate passages per category (default: 15)")
    parser.add_argument("--verbose-bert", action="store_true",
                        help="Print BERT ranking details")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug output")

    args = parser.parse_args()

    # Read barcodes
    barcodes = read_barcode_file(args.barcode_file)
    print(f"Loaded {len(barcodes)} barcodes from {args.barcode_file}")

    # Load primary metadata
    csv_path = Path(args.primary_metadata) if args.primary_metadata else DEFAULT_PRIMARY_METADATA
    print(f"Loading primary metadata from: {csv_path}")
    primary_metadata = load_primary_metadata_csv(csv_path)
    print(f"  Loaded {len(primary_metadata)} entries")

    # Set up directories
    text_dir = Path(args.text_dir) if args.text_dir else DEFAULT_TEXT_DIR
    process_dir = Path(__file__).parent / "process_files"
    process_dir.mkdir(exist_ok=True)

    # Process each book
    succeeded = 0
    failed = 0
    skipped = 0

    for barcode in barcodes:
        # Skip if output already exists
        output_path = process_dir / f"{barcode}_potentialquestions.jsonl"
        if output_path.exists():
            print(f"\nSkipping {barcode}: {output_path.name} already exists")
            skipped += 1
            continue

        # Look up CSV metadata
        csv_key = barcode_to_csv_key(barcode)
        csv_entry = primary_metadata.get(csv_key, {})

        success = process_single_book(
            barcode, text_dir, process_dir, csv_entry,
            args.candidates_per_category, args.verbose_bert, args.debug
        )

        if success:
            succeeded += 1
        else:
            failed += 1

    # Summary
    print(f"\n{'=' * 60}")
    print("BATCH PROCESSING SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total barcodes: {len(barcodes)}")
    print(f"Succeeded: {succeeded}")
    print(f"Failed: {failed}")
    print(f"Skipped (already existed): {skipped}")


if __name__ == "__main__":
    main()

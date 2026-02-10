#!/usr/bin/env python3
"""
Approve Batched Questions

Interactive approval of batch-generated cloze questions.
Loads *_potentialquestions.jsonl files, lets the user review and approve
candidates, and saves approved questions to *_clozequestions.jsonl.

Usage:
    python approve_batched_questions.py [OPTIONS]

    Options:
        --process-dir DIR          Directory with potential question files
                                   (default: process_files/)
        --primary-metadata FILE    Path to primary_metadata.csv
                                   (default: ../primary_metadata.csv)
        --barcode BARCODE          Process only this barcode
        --debug                    Enable debug output
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add connectors directory to path for imports
CONNECTORS_DIR = str(Path(__file__).parent.parent / "connectors")
if CONNECTORS_DIR not in sys.path:
    sys.path.insert(0, CONNECTORS_DIR)

from make_cloze_questions import (
    present_question_for_approval,
    edit_passage,
    present_distractors_for_approval,
    format_question_output,
    save_question,
    build_metadata_prefix,
    _is_anonymous_author,
    TAG_DESCRIPTIONS,
)

from metadata_elicitation import elicit_metadata

# Extra batch fields that get stripped from final output
BATCH_FIELDS = {'is_clause', 'mask_string', 'full_sentence', 'target_idx',
                'masked_passage', 'ground_truth'}


def find_potential_question_files(process_dir: str) -> List[Tuple[str, Path]]:
    """
    Find *_potentialquestions.jsonl files, excluding barcodes that already
    have *_clozequestions.jsonl.

    Args:
        process_dir: Directory to search

    Returns:
        List of (barcode, filepath) tuples
    """
    pdir = Path(process_dir)
    if not pdir.exists():
        return []

    # Find all potential question files
    potential_files = sorted(pdir.glob("*_potentialquestions.jsonl"))

    # Find existing approved files
    approved_barcodes = set()
    for f in pdir.glob("*_clozequestions.jsonl"):
        barcode = f.name.replace("_clozequestions.jsonl", "")
        approved_barcodes.add(barcode)

    results = []
    for f in potential_files:
        barcode = f.name.replace("_potentialquestions.jsonl", "")
        if barcode not in approved_barcodes:
            results.append((barcode, f))

    return results


def load_potential_questions(filepath: Path) -> List[Dict]:
    """
    Read potential questions from a JSONL file.

    Args:
        filepath: Path to the JSONL file

    Returns:
        List of question dicts
    """
    questions = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                questions.append(json.loads(line))
    return questions


def group_by_category(questions: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group questions by their question_category field.

    Args:
        questions: List of question dicts

    Returns:
        Dict mapping category names to lists of question dicts
    """
    groups: Dict[str, List[Dict]] = {}
    for q in questions:
        cat = q.get('question_category', 'unknown')
        if cat not in groups:
            groups[cat] = []
        groups[cat].append(q)
    return groups


def present_batch_question_for_approval(question: Dict,
                                        metadata_prefix: str) -> str:
    """
    Reconstruct passage_data from batch fields and delegate to
    present_question_for_approval().

    Args:
        question: Question dict with batch fields
        metadata_prefix: Metadata frame string

    Returns:
        "accept", "reject", or "stop"
    """
    passage_data = {
        'passage': question['masked_passage'],
        'ground_truth': question['ground_truth'],
        'mask_string': question['mask_string'],
        'is_clause': question['is_clause'],
        'category': question['question_category'].replace('cloze_', ''),
        'target_idx': question['target_idx'],
        'full_sentence': question['full_sentence'],
        'full_passage': question['passage'],
    }

    return present_question_for_approval(passage_data, metadata_prefix)


def edit_batch_passage(question: Dict) -> Dict:
    """
    Reconstruct passage_data, call edit_passage(), map edits back.

    Args:
        question: Question dict with batch fields

    Returns:
        Updated question dict
    """
    passage_data = {
        'passage': question['masked_passage'],
        'ground_truth': question['ground_truth'],
        'mask_string': question['mask_string'],
        'is_clause': question['is_clause'],
        'category': question['question_category'].replace('cloze_', ''),
        'target_idx': question['target_idx'],
        'full_sentence': question['full_sentence'],
        'full_passage': question['passage'],
    }

    edited = edit_passage(passage_data)

    # Map edits back to question dict
    question['masked_passage'] = edited['passage']
    question['ground_truth'] = edited['ground_truth']
    question['passage'] = edited['full_passage']
    question['full_sentence'] = edited['full_sentence']

    return question


def review_batch_distractors(question: Dict) -> Optional[Dict]:
    """
    Extract distractors from answer lists, present for approval,
    rebuild answer lists with approved ones.

    Args:
        question: Question dict with answer_strings, answer_types, etc.

    Returns:
        Updated question dict with approved distractors, or None if
        no distractors were approved
    """
    answer_strings = question['answer_strings']
    answer_types = question['answer_types']

    # Extract distractors (skip ground truth at index 0)
    distractors = list(zip(answer_strings[1:], answer_types[1:]))

    approved = present_distractors_for_approval(distractors)

    if not approved:
        return None

    # Rebuild answer lists
    question['answer_strings'] = [question['ground_truth']]
    question['answer_types'] = ['ground_truth']
    question['answer_probabilities'] = [1.0]

    for text, dtype in approved:
        question['answer_strings'].append(text)
        question['answer_types'].append(dtype)
        question['answer_probabilities'].append(0.0)

    return question


def apply_metadata_to_question(question: Dict, metadata: Dict,
                               metadata_prefix: str) -> Dict:
    """
    Replace provisional metadata with confirmed values, rebuild
    metadata_frame and main_question, strip batch fields.

    Args:
        question: Question dict with batch fields
        metadata: Confirmed metadata dict (with 'genre' key)
        metadata_prefix: Confirmed metadata prefix string

    Returns:
        Cleaned question dict ready for output
    """
    # Update metadata fields
    question['metadata_frame'] = metadata_prefix
    question['source_title'] = metadata['source_title']
    question['source_author'] = metadata['source_author']
    question['source_date'] = metadata['source_date']
    question['author_nationality'] = metadata.get('author_nationality', '')
    question['source_genre'] = metadata['genre']
    question['author_birth'] = metadata.get('author_birth', 0)
    question['author_profession'] = metadata.get('author_profession', '')
    question['source_htid'] = metadata['source_htid']

    # Rebuild main_question with confirmed metadata
    answer_type = "clause" if question.get('is_clause', False) else "sentence"
    mask_string = question.get('mask_string', '')
    masked_passage = question.get('masked_passage', '')
    prompt = (f"Write a {answer_type} appropriate for this book that could "
              f"stand in the position marked by {mask_string}:")
    question['main_question'] = f"{masked_passage}\n\n{prompt}"

    # Strip batch fields
    for field in BATCH_FIELDS:
        question.pop(field, None)

    return question


def process_single_file(barcode: str, questions: List[Dict],
                        output_path: Path,
                        primary_metadata_path: str,
                        debug: bool = False) -> int:
    """
    Full interactive approval for one book's potential questions.

    Args:
        barcode: Book barcode
        questions: List of potential question dicts
        output_path: Path for approved output JSONL
        primary_metadata_path: Path to primary_metadata.csv
        debug: Enable debug output

    Returns:
        Number of questions approved
    """
    print(f"\n{'=' * 70}")
    print(f"REVIEWING: {barcode}")
    print(f"{'=' * 70}")
    print(f"  {len(questions)} potential questions loaded")

    # Elicit/confirm metadata
    htid = questions[0].get('source_htid', f'hvd.{barcode.lower()}') if questions else f'hvd.{barcode.lower()}'
    metadata = elicit_metadata(
        metadata_file=primary_metadata_path,
        source_htid=htid
    )

    # Fix key mapping: elicit_metadata returns source_genre,
    # but format_question_output and build_metadata_prefix expect genre
    metadata['genre'] = metadata.pop('source_genre', 'novel')

    # Build confirmed metadata prefix
    metadata_prefix = build_metadata_prefix(metadata)

    # Group by category
    groups = group_by_category(questions)
    print(f"\n  Categories: {list(groups.keys())}")

    approved_count = 0

    for category, cat_questions in groups.items():
        print(f"\n  --- Category: {category} ({len(cat_questions)} candidates) ---")

        approved_this_category = False

        for i, question in enumerate(cat_questions):
            if approved_this_category:
                break

            print(f"\n  Candidate {i + 1}/{len(cat_questions)} for {category}")

            try:
                decision = present_batch_question_for_approval(
                    question, metadata_prefix
                )
            except KeyboardInterrupt:
                print("\n\nStopped by user (Ctrl+C).")
                return approved_count

            if decision == "stop":
                print("\nStopped by user.")
                return approved_count

            if decision == "reject":
                print("  Rejected.")
                continue

            # Accepted - offer passage edit
            question = edit_batch_passage(question)

            # Review distractors
            result = review_batch_distractors(question)
            if result is None:
                print("  No distractors approved. Skipping this candidate.")
                continue

            question = result

            # Apply confirmed metadata and strip batch fields
            question = apply_metadata_to_question(
                question, metadata, metadata_prefix
            )

            # Save
            save_question(question, str(output_path))
            approved_count += 1
            approved_this_category = True

            print(f"\n  Question approved and saved. ({approved_count} total)")

    print(f"\n  Approved {approved_count} questions for {barcode}")
    return approved_count


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Interactive approval of batch-generated cloze questions"
    )

    parser.add_argument("--process-dir",
                        default="process_files",
                        help="Directory with potential question files "
                             "(default: process_files)")
    parser.add_argument("--primary-metadata",
                        help="Path to primary_metadata.csv "
                             "(default: ../primary_metadata.csv)")
    parser.add_argument("--barcode",
                        help="Process only this barcode")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug output")

    args = parser.parse_args()

    # Resolve process dir relative to script
    script_dir = Path(__file__).parent
    process_dir = Path(args.process_dir)
    if not process_dir.is_absolute():
        process_dir = script_dir / process_dir

    primary_metadata = args.primary_metadata or str(
        Path(__file__).parent.parent / "primary_metadata.csv"
    )

    if args.barcode:
        # Process single barcode
        barcode = args.barcode.upper()
        filepath = process_dir / f"{barcode}_potentialquestions.jsonl"

        if not filepath.exists():
            print(f"Error: File not found: {filepath}")
            sys.exit(1)

        questions = load_potential_questions(filepath)
        output_path = process_dir / f"{barcode}_clozequestions.jsonl"

        process_single_file(barcode, questions, output_path,
                           primary_metadata, args.debug)
    else:
        # Find all unprocessed files
        files = find_potential_question_files(str(process_dir))

        if not files:
            print("No unprocessed potential question files found.")
            print(f"  Searched: {process_dir}")
            sys.exit(0)

        print(f"Found {len(files)} books to review:")
        for barcode, filepath in files:
            print(f"  {barcode}: {filepath.name}")

        for barcode, filepath in files:
            questions = load_potential_questions(filepath)
            output_path = process_dir / f"{barcode}_clozequestions.jsonl"

            process_single_file(barcode, questions, output_path,
                               primary_metadata, args.debug)

            # Ask to continue
            try:
                response = input("\nContinue to next book? (y/n) [y]: ").strip().lower()
                if response in ['n', 'no']:
                    print("Stopping.")
                    break
            except KeyboardInterrupt:
                print("\nStopping.")
                break

    print("\nDone.")


if __name__ == "__main__":
    main()

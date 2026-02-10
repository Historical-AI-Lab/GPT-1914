#!/usr/bin/env python3
"""
Approve Batched Questions

Interactive approval of batch-generated cloze questions.
Loads a single *_potentialquestions.jsonl file, lets the user review and
approve candidates, and saves approved questions to *_clozequestions.jsonl.

Usage:
    python approve_batched_questions.py INPUT_FILE [OPTIONS]

    Arguments:
        INPUT_FILE                 Path to a *_potentialquestions.jsonl file

    Options:
        --primary-metadata FILE    Path to primary_metadata.csv
                                   (default: ../primary_metadata.csv)
        --debug                    Enable debug output
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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


def final_review(question: Dict, metadata_prefix: str) -> bool:
    """
    Show the complete question with all answers for final approval
    before writing to file.

    Args:
        question: Question dict after distractor approval
        metadata_prefix: Metadata frame string

    Returns:
        True if user confirms, False to reject
    """
    answer_type = "clause" if question.get('is_clause', False) else "sentence"
    mask_string = question.get('mask_string', '')
    masked_passage = question.get('masked_passage', '')
    prompt = (f"Write a {answer_type} appropriate for this book that could "
              f"stand in the position marked by {mask_string}:")

    print("\n" + "=" * 70)
    print("FINAL REVIEW")
    print("=" * 70)
    print()
    print(f"  {metadata_prefix}")
    print()
    print(f"  {masked_passage}")
    print()
    print(f"  {prompt}")
    print()
    print("-" * 40)

    for text, dtype in zip(question['answer_strings'],
                           question['answer_types']):
        marker = " *" if dtype == "ground_truth" else "  "
        print(f"{marker} [{dtype:20s}]  {text}")

    print("-" * 40)
    print("  (* = correct answer)")
    print()

    while True:
        response = input("Save this question? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no', '']:
            return False
        else:
            print("Please enter 'y' or 'n'")


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

            # Final review before saving
            if not final_review(question, metadata_prefix):
                print("  Rejected at final review.")
                continue

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

    parser.add_argument("input_file",
                        help="Path to a *_potentialquestions.jsonl file")
    parser.add_argument("--primary-metadata",
                        help="Path to primary_metadata.csv "
                             "(default: ../primary_metadata.csv)")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug output")

    args = parser.parse_args()

    filepath = Path(args.input_file)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    # Extract barcode from filename (e.g. "HXDN6E_potentialquestions.jsonl" -> "HXDN6E")
    barcode = filepath.name.replace("_potentialquestions.jsonl", "")
    output_path = filepath.parent / f"{barcode}_clozequestions.jsonl"

    primary_metadata = args.primary_metadata or str(
        Path(__file__).parent.parent / "primary_metadata.csv"
    )

    questions = load_potential_questions(filepath)
    process_single_file(barcode, questions, output_path,
                       primary_metadata, args.debug)

    print("\nDone.")


if __name__ == "__main__":
    main()

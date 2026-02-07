#!/usr/bin/env python3
"""
Augment Existing Questions

Utility script to add period_words_in_main_question and manual_comment fields
to existing questions in manual/process_files/.

Reads all JSONL files from process_files/, prompts user for the two new fields
for each question, and writes augmented questions to augmented_files/.

Usage:
    python augment_existing_questions.py
"""

import json
from pathlib import Path
from typing import List, Dict

from manual_question_writer import prompt_for_period_words, prompt_for_manual_comment


def get_ground_truth_answer(question: Dict) -> str:
    """
    Extract the ground truth answer from a question record.

    Args:
        question: The question dict

    Returns:
        The ground truth answer string, or "N/A" if not found
    """
    answer_strings = question.get('answer_strings', [])
    answer_types = question.get('answer_types', [])

    for ans, atype in zip(answer_strings, answer_types):
        if atype == 'ground_truth':
            return ans

    # Fallback: return first answer if no ground_truth type found
    if answer_strings:
        return answer_strings[0]

    return "N/A"


def process_file(input_path: Path, output_path: Path) -> int:
    """
    Process a single JSONL file, prompting for new fields for each question.

    Args:
        input_path: Path to input JSONL file
        output_path: Path to output JSONL file

    Returns:
        Number of questions processed
    """
    questions: List[Dict] = []

    # Read all questions from input file
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))

    if not questions:
        print(f"  No questions found in {input_path.name}")
        return 0

    print(f"\n{'=' * 60}")
    print(f"FILE: {input_path.name}")
    print(f"Questions to process: {len(questions)}")
    print('=' * 60)

    augmented_questions: List[Dict] = []

    for i, question in enumerate(questions, 1):
        print(f"\n--- Question {i} of {len(questions)} ---")
        print(f"Source title: {question.get('source_title', 'Unknown')}")
        print(f"Main question: {question.get('main_question', 'N/A')}")
        print(f"Ground truth: {get_ground_truth_answer(question)}")

        # Check if already has these fields
        if 'period_words_in_main_question' in question:
            print(f"  [Already has period_words_in_main_question: {question['period_words_in_main_question']}]")
        if 'manual_comment' in question:
            print(f"  [Already has manual_comment: {question['manual_comment']!r}]")

        # Prompt for new fields
        main_question = question.get('main_question', '')
        period_words = prompt_for_period_words(main_question)
        manual_comment = prompt_for_manual_comment()

        # Add new fields to question
        question['period_words_in_main_question'] = period_words
        question['manual_comment'] = manual_comment

        augmented_questions.append(question)

    # Write augmented questions to output file
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for question in augmented_questions:
            f.write(json.dumps(question, ensure_ascii=False) + '\n')

    print(f"\n  Saved {len(augmented_questions)} questions to {output_path}")
    return len(augmented_questions)


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    process_dir = script_dir / "process_files"
    augmented_dir = script_dir / "augmented_files"

    if not process_dir.exists():
        print(f"Error: {process_dir} does not exist")
        return

    # Find all JSONL files in process_files
    jsonl_files = sorted(process_dir.glob("*.jsonl"))

    if not jsonl_files:
        print(f"No JSONL files found in {process_dir}")
        return

    print("\n" + "=" * 60)
    print("AUGMENT EXISTING QUESTIONS")
    print("=" * 60)
    print(f"Input directory: {process_dir}")
    print(f"Output directory: {augmented_dir}")
    print(f"Files to process: {len(jsonl_files)}")
    print("=" * 60)
    print("\nType Ctrl+C to stop at any time.")

    total_processed = 0

    try:
        for jsonl_file in jsonl_files:
            output_path = augmented_dir / jsonl_file.name
            count = process_file(jsonl_file, output_path)
            total_processed += count

            # Ask if user wants to continue to next file
            if jsonl_file != jsonl_files[-1]:
                cont = input("\nContinue to next file? (enter for yes, 'q' to quit): ").strip().lower()
                if cont in ['q', 'quit', 'exit']:
                    print("\nStopping early.")
                    break

    except KeyboardInterrupt:
        print("\n\nInterrupted. Progress saved to augmented_files/.")

    print(f"\n{'=' * 60}")
    print(f"Total questions processed: {total_processed}")
    print(f"Output saved to: {augmented_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()

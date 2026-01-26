#!/usr/bin/env python3
"""
Manual Question Writer

Interactive CLI for creating manual benchmark questions and writing
them to JSONL files in manual/process_files/.

Usage:
    python manual_question_writer.py [--metadata PATH]

    Options:
        --metadata PATH    Path to primary_metadata.csv (default: ../primary_metadata.csv)
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from metadata_elicitation import (
    elicit_metadata,
    build_metadata_frame,
    a_or_an
)


# Special htids that have fixed categories
SPECIAL_HTIDS = {'attribution', 'handcrafted', 'refusal'}

# Question category options
CATEGORY_OPTIONS = ['attribution', 'handcrafted', 'refusal', 'textbook']


def get_output_path(source_htid: str) -> Path:
    """
    Get the output file path for a given htid.

    Args:
        source_htid: The source htid

    Returns:
        Path to the output JSONL file
    """
    script_dir = Path(__file__).parent
    process_dir = script_dir / "process_files"
    process_dir.mkdir(exist_ok=True)

    # Normalize htid for filename
    htid_clean = source_htid.replace('.', '_').replace('/', '_')
    return process_dir / f"{htid_clean}_manualquestions.jsonl"


def save_question(question_data: Dict, output_path: Path) -> None:
    """
    Append a question to the output JSONL file.

    Args:
        question_data: The question dict
        output_path: Path to output file
    """
    with open(output_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(question_data, ensure_ascii=False) + '\n')
    print(f"  Question saved to: {output_path}")


def prompt_for_frame(metadata: Dict) -> str:
    """
    Prompt user to approve, blank, or manually supply metadata frame.

    Args:
        metadata: The metadata dict

    Returns:
        The metadata frame string (may be empty)
    """
    default_frame = build_metadata_frame(metadata)

    print("\nDefault metadata frame:")
    print(f'  "{default_frame}"')
    print()

    while True:
        choice = input("(a)pprove this frame, (b)lank frame, or (m)anually supply frame: ").strip().lower()

        if choice in ['a', 'approve', '']:
            return default_frame
        elif choice in ['b', 'blank']:
            return ""
        elif choice in ['m', 'manual']:
            manual_frame = input("Enter frame: ").strip()
            return manual_frame
        else:
            print("  Please enter 'a', 'b', or 'm'")


def prompt_for_question() -> str:
    """
    Prompt user for the main question text.

    Returns:
        The question text (required, cannot be blank)
    """
    while True:
        question = input("\nEnter main question: ").strip()
        if question:
            return question
        print("  Question cannot be blank")


def prompt_for_category(source_htid: str, current_category: str = "textbook") -> str:
    """
    Prompt user for question category.

    For special htids (attribution, handcrafted, refusal), the category
    matches the htid.

    Args:
        source_htid: The source htid
        current_category: Current/default category

    Returns:
        The selected category
    """
    # Special htids have fixed categories
    if source_htid in SPECIAL_HTIDS:
        return source_htid

    print(f"\nQuestion category: {current_category}")
    choice = input("(a)pprove this category or (c)hange it? (enter for approve): ").strip().lower()

    if choice in ['a', 'approve', '']:
        return current_category
    elif choice in ['c', 'change']:
        print("\nCategory options:")
        for i, cat in enumerate(CATEGORY_OPTIONS, 1):
            print(f"  {i}. {cat}")

        while True:
            cat_choice = input("Select category (1-4): ").strip()
            try:
                idx = int(cat_choice) - 1
                if 0 <= idx < len(CATEGORY_OPTIONS):
                    return CATEGORY_OPTIONS[idx]
            except ValueError:
                pass
            print("  Please enter a number 1-4")
    else:
        return current_category


def prompt_for_answers() -> Tuple[List[str], List[str], List[float]]:
    """
    Collect answers interactively.

    First answer is always ground_truth with probability 1.0.
    Subsequent answers can be ground_truth, manual, or anachronistic_manual.

    Returns:
        Tuple of (answer_strings, answer_types, answer_probabilities)
    """
    answer_strings = []
    answer_types = []
    answer_probabilities = []

    print("\n--- Answers ---")

    # First answer (required, ground_truth)
    while True:
        first_answer = input("Answer 1 (ground_truth): ").strip()
        if first_answer:
            answer_strings.append(first_answer)
            answer_types.append("ground_truth")
            answer_probabilities.append(1.0)
            break
        print("  First answer is required")

    # Second answer (required)
    while True:
        second_answer = input("Answer 2: ").strip()
        if second_answer:
            answer_strings.append(second_answer)

            # Prompt for type
            answer_type, prob = prompt_for_answer_type_and_prob()
            answer_types.append(answer_type)
            answer_probabilities.append(prob)
            break
        print("  Second answer is required (minimum 2 answers)")

    # Additional answers (optional)
    answer_num = 3
    while True:
        add_more = input(f"\nAdd another answer? (n or enter for yes): ").strip().lower()
        if add_more in ['n', 'no']:
            break

        answer = input(f"Answer {answer_num}: ").strip()
        if not answer:
            # Empty answer means done
            break

        answer_strings.append(answer)
        answer_type, prob = prompt_for_answer_type_and_prob()
        answer_types.append(answer_type)
        answer_probabilities.append(prob)
        answer_num += 1

    return answer_strings, answer_types, answer_probabilities


def prompt_for_answer_type_and_prob() -> Tuple[str, float]:
    """
    Prompt for answer type and probability.

    Returns:
        Tuple of (answer_type, probability)
    """
    while True:
        type_choice = input("  Type - (g)round_truth, (m)anual, (a)nachronistic_manual: ").strip().lower()

        if type_choice in ['g', 'ground_truth']:
            # ground_truth always has probability 1.0
            return "ground_truth", 1.0
        elif type_choice in ['m', 'manual']:
            prob = prompt_for_probability()
            return "manual", prob
        elif type_choice in ['a', 'anachronistic_manual', 'anachronistic']:
            prob = prompt_for_probability()
            return "anachronistic_manual", prob
        else:
            print("  Please enter 'g', 'm', or 'a'")


def prompt_for_probability() -> float:
    """
    Prompt for answer probability (default 0.0).

    Returns:
        The probability as a float
    """
    prob_str = input("  Probability [0.0]: ").strip()
    if not prob_str:
        return 0.0

    try:
        prob = float(prob_str)
        if 0.0 <= prob <= 1.0:
            return prob
        print("  Probability must be between 0.0 and 1.0, using 0.0")
        return 0.0
    except ValueError:
        print("  Invalid number, using 0.0")
        return 0.0


def create_question(metadata: Dict) -> Dict:
    """
    Run the interactive question creation dialogue.

    Args:
        metadata: The metadata dict for this source

    Returns:
        Complete question record dict
    """
    print("\n" + "=" * 60)
    print("CREATE NEW QUESTION")
    print("=" * 60)
    print(f"Source: {metadata['source_htid']}")
    print(f"Title: {metadata.get('source_title', 'Unknown')}")
    print("=" * 60)

    # A. Metadata frame
    metadata_frame = prompt_for_frame(metadata)

    # B. Main question
    main_question = prompt_for_question()

    # C. Question category
    question_category = prompt_for_category(metadata['source_htid'])

    # D. Answers
    answer_strings, answer_types, answer_probabilities = prompt_for_answers()

    # Build output record
    record = {
        "metadata_frame": metadata_frame,
        "main_question": main_question,
        "answer_strings": answer_strings,
        "answer_types": answer_types,
        "answer_probabilities": answer_probabilities,
        "question_category": question_category,
        "question_process": "manual",
        "source_title": metadata.get('source_title', ''),
        "source_author": metadata.get('source_author', ''),
        "source_date": metadata.get('source_date'),
        "author_nationality": metadata.get('author_nationality', ''),
        "source_genre": metadata.get('source_genre', ''),
        "author_birth": metadata.get('author_birth'),
        "author_profession": metadata.get('author_profession', ''),
        "source_htid": metadata['source_htid']
    }

    return record


def confirm_htid(current_htid: str, metadata_file: str) -> Tuple[str, Optional[Dict]]:
    """
    Confirm or change the current htid.

    Args:
        current_htid: The current htid
        metadata_file: Path to primary_metadata.csv

    Returns:
        Tuple of (htid, metadata_dict or None if needs elicitation)
    """
    print(f"\nSource htid is: {current_htid}")
    choice = input("New id, [a] for attribution, [h] for handcrafted, or enter to confirm: ").strip()

    if not choice:
        # Confirm current
        return current_htid, None

    if choice.lower() == 'a':
        return 'attribution', None

    if choice.lower() == 'h':
        return 'handcrafted', None

    # New htid provided
    return choice, None


def main_loop(metadata_file: str) -> None:
    """
    Main interactive loop for question creation.

    Args:
        metadata_file: Path to primary_metadata.csv
    """
    current_htid = ""
    current_metadata: Optional[Dict] = None

    print("\n" + "=" * 60)
    print("MANUAL QUESTION WRITER")
    print("=" * 60)
    print("Type 'quit' or 'exit' to stop.")
    print("=" * 60)

    while True:
        try:
            # Step 1: Check source_htid
            if not current_htid:
                htid_input = input("\nEnter source_htid (or 'quit'): ").strip()
                if htid_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break
                if not htid_input:
                    continue
                current_htid = htid_input

            # Step 2: Check metadata
            needs_elicitation = False
            if current_metadata is None:
                needs_elicitation = True
            elif not current_metadata.get('source_date'):
                needs_elicitation = True

            # Step 3: Special htid handling
            if current_htid in SPECIAL_HTIDS:
                new_meta = input("Provide new metadata? (y or enter for no): ").strip().lower()
                if new_meta in ['y', 'yes']:
                    needs_elicitation = True

            # Step 4: Confirm htid
            new_htid, _ = confirm_htid(current_htid, metadata_file)

            if new_htid != current_htid:
                current_htid = new_htid
                current_metadata = None
                needs_elicitation = True

            # Elicit metadata if needed
            if needs_elicitation:
                if current_htid in SPECIAL_HTIDS:
                    # For special htids, create minimal metadata
                    print(f"\nCreating metadata for special htid: {current_htid}")
                    current_metadata = {
                        'source_htid': current_htid,
                        'source_title': '',
                        'source_author': '',
                        'source_date': None,
                        'author_nationality': '',
                        'source_genre': '',
                        'author_birth': None,
                        'author_profession': ''
                    }

                    # Optionally prompt for some fields
                    use_defaults = input("Use blank metadata? (enter for yes, 'n' to fill in): ").strip().lower()
                    if use_defaults in ['n', 'no']:
                        current_metadata = elicit_metadata(
                            metadata_file=metadata_file,
                            source_htid=current_htid
                        )
                else:
                    current_metadata = elicit_metadata(
                        metadata_file=metadata_file,
                        source_htid=current_htid
                    )

            # Step 5: Create question
            question = create_question(current_metadata)

            # Preview
            print("\n" + "-" * 40)
            print("QUESTION PREVIEW")
            print("-" * 40)
            print(json.dumps(question, indent=2, ensure_ascii=False))
            print("-" * 40)

            save_choice = input("\nSave this question? (enter for yes, 'n' to discard): ").strip().lower()
            if save_choice not in ['n', 'no']:
                # Step 6: Write to file
                output_path = get_output_path(current_htid)
                save_question(question, output_path)

            # Step 7: Loop back
            continue_choice = input("\nCreate another question? (enter for yes, 'quit' to exit): ").strip().lower()
            if continue_choice in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break

        except KeyboardInterrupt:
            print("\n\nInterrupted. Exiting...")
            break
        except EOFError:
            print("\n\nEnd of input. Exiting...")
            break


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Interactive CLI for creating manual benchmark questions"
    )

    parser.add_argument("--metadata",
                        default="../primary_metadata.csv",
                        help="Path to primary_metadata.csv (default: ../primary_metadata.csv)")

    args = parser.parse_args()

    main_loop(args.metadata)


if __name__ == "__main__":
    main()

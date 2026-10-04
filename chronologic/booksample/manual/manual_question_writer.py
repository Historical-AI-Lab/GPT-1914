#!/usr/bin/env python3
"""
Manual Question Writer

Interactive CLI for creating manual benchmark questions and writing
them to JSONL files in manual/process_files/.

Parallax questions are the ones open to judgment about fit with the
target historical context: they carry a "reject_reasons" array parallel
to the answers, and "context_judged": 1. Every other category is written
with "context_judged": 0 and no "reject_reasons".

Usage:
    python manual_question_writer.py [--metadata PATH]

    Options:
        --metadata PATH    Path to primary_metadata.csv (default: ../primary_metadata.csv)
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from manual_metadata_framing import (
    elicit_metadata,
    build_metadata_frame,
    a_or_an
)


# Special htids that have fixed categories
SPECIAL_HTIDS = {'attribution', 'handcrafted', 'refusal'}

# Question category options
CATEGORY_OPTIONS = ['attribution', 'handcrafted', 'refusal', 'textbook', 'parallax']


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

    # Normalize htid for filename:
    # Strip 'hvd.' prefix if present and uppercase alphabetic characters
    htid_clean = source_htid
    if htid_clean.lower().startswith('hvd.'):
        htid_clean = htid_clean[4:]  # Remove 'hvd.' prefix
    htid_clean = htid_clean.upper()
    htid_clean = htid_clean.replace('.', '_').replace('/', '_')
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


def prompt_for_frame(metadata: Dict, current_frame: Optional[str] = None) -> str:
    """
    Prompt user to approve, blank, or manually supply metadata frame.

    If current_frame is provided (a previously edited frame), it is shown
    as the default instead of the frame derived from metadata.

    Args:
        metadata: The metadata dict
        current_frame: A previously entered frame to use as the default, or None

    Returns:
        The metadata frame string (may be empty)
    """
    if current_frame is not None:
        default_frame = current_frame
    else:
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


def prompt_for_category(source_htid: str, current_category: str = "parallax") -> str:
    """
    Prompt user for question category.

    For special htids (attribution, handcrafted, refusal), the category
    matches the htid. Otherwise, the numbered category options are shown
    directly; pressing enter selects current_category as a default.

    Args:
        source_htid: The source htid
        current_category: Category selected by a bare enter (default)

    Returns:
        The selected category
    """
    # Special htids have fixed categories
    if source_htid in SPECIAL_HTIDS:
        return source_htid

    print("\nCategory options:")
    default_idx = CATEGORY_OPTIONS.index(current_category) + 1 if current_category in CATEGORY_OPTIONS else None
    for i, cat in enumerate(CATEGORY_OPTIONS, 1):
        marker = " (default)" if i == default_idx else ""
        print(f"  {i}. {cat}{marker}")
    print(f"  {len(CATEGORY_OPTIONS) + 1}. [enter manually]")

    while True:
        prompt_label = f"Select category (1-{len(CATEGORY_OPTIONS) + 1})"
        if default_idx is not None:
            prompt_label += f" [{default_idx}={current_category}]"
        cat_choice = input(f"{prompt_label}: ").strip()

        if cat_choice == '' and default_idx is not None:
            return current_category

        try:
            idx = int(cat_choice) - 1
            if 0 <= idx < len(CATEGORY_OPTIONS):
                return CATEGORY_OPTIONS[idx]
            elif idx == len(CATEGORY_OPTIONS):
                # Manual entry option
                manual_cat = input("Enter category: ").strip()
                if manual_cat:
                    return manual_cat
                print("  Category cannot be blank")
                continue
        except ValueError:
            pass
        print(f"  Please enter a number 1-{len(CATEGORY_OPTIONS) + 1}")


def prompt_for_answers(collect_reasons: bool) -> Tuple[List[str], List[str], List[float], Optional[List[str]]]:
    """
    Collect answers interactively.

    First answer is always ground_truth with probability 1.0.
    Subsequent answers can be ground_truth, manual, or anachronistic_manual.

    Rejection rationales are only meaningful for parallax questions, where
    fit with the target context is what's being judged. When collect_reasons
    is False the user is never asked for one and None is returned in place
    of the array.

    Args:
        collect_reasons: Whether to require a reject_reason per distractor

    Returns:
        Tuple of (answer_strings, answer_types, answer_probabilities,
        reject_reasons or None)
    """
    answer_strings = []
    answer_types = []
    answer_probabilities = []
    reject_reasons = [] if collect_reasons else None

    print("\n--- Answers ---")

    # First answer (required, ground_truth)
    while True:
        first_answer = input("Answer 1 (ground_truth): ").strip()
        if first_answer:
            answer_strings.append(first_answer)
            answer_types.append("ground_truth")
            answer_probabilities.append(1.0)
            if collect_reasons:
                reject_reasons.append("")
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
            if collect_reasons:
                reject_reasons.append(
                    "" if answer_type == "ground_truth" else prompt_for_reject_reason()
                )
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
        if collect_reasons:
            reject_reasons.append(
                "" if answer_type == "ground_truth" else prompt_for_reject_reason()
            )
        answer_num += 1

    return answer_strings, answer_types, answer_probabilities, reject_reasons


def prompt_for_reject_reason() -> str:
    """
    Prompt user for the reason a non-ground_truth answer should be rejected.

    Required, non-blank: the ideal phrasing begins with a verb, completing
    "Reason for rejection is that the answer ...".

    Returns:
        The reason string (non-blank)
    """
    while True:
        reason = input("Reason for rejection is that the answer ...: ").strip()
        if reason:
            return reason
        print("  Reason cannot be blank")


def prompt_for_period_words(main_question: str) -> int:
    """
    Prompt user for count of words from the original source in the question.

    Args:
        main_question: The main question text

    Returns:
        Integer count of period words
    """
    word_count = len(main_question.split())

    while True:
        choice = input("\nWords from original source: [a]ll, [n]one, or integer: ").strip().lower()

        if choice in ['n', 'none']:
            return 0
        elif choice in ['a', 'all']:
            return word_count
        else:
            try:
                value = int(choice)
                if value < 0:
                    print("  Value cannot be negative")
                elif value > word_count:
                    print(f"  Value cannot exceed word count ({word_count})")
                else:
                    return value
            except ValueError:
                print("  Please enter 'a', 'n', or an integer")


def prompt_for_manual_comment() -> str:
    """
    Prompt user for an optional comment on rationale.

    Returns:
        The comment string (may be empty)
    """
    return input("Comment on rationale (enter to leave blank): ").strip()


def prompt_for_answer_type_and_prob() -> Tuple[str, float]:
    """
    Prompt for answer type and probability.

    Returns:
        Tuple of (answer_type, probability)
    """
    while True:
        type_choice = input("  Type - (g)round_truth, (m)anual, (s)ame_book, (a)nachronistic_manual, (k)eyboard entry: ").strip().lower()

        if type_choice in ['g', 'ground_truth']:
            # ground_truth always has probability 1.0
            return "ground_truth", 1.0
        elif type_choice in ['m', 'manual']:
            prob = prompt_for_probability()
            return "manual", prob
        elif type_choice in ['s', 'same_book', 'manual_same_book']:
            prob = prompt_for_probability()
            return "manual_same_book", prob
        elif type_choice in ['a', 'anachronistic_manual', 'anachronistic']:
            prob = prompt_for_probability()
            return "anachronistic_manual", prob
        elif type_choice in ['k', 'keyboard']:
            custom_type = input("  Enter distractor type: ").strip()
            if custom_type:
                prob = prompt_for_probability()
                return custom_type, prob
            print("  Type cannot be blank")
        else:
            print("  Please enter 'g', 'm', 's', 'a', or 'k'")


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


def create_question(metadata: Dict, current_frame: Optional[str] = None) -> Tuple[Dict, str]:
    """
    Run the interactive question creation dialogue.

    Args:
        metadata: The metadata dict for this source
        current_frame: A previously entered frame to use as the default, or None

    Returns:
        Tuple of (complete question record dict, the frame that was used)
    """
    print("\n" + "=" * 60)
    print("CREATE NEW QUESTION")
    print("=" * 60)
    print(f"Source: {metadata['source_htid']}")
    print(f"Title: {metadata.get('source_title', 'Unknown')}")
    print("=" * 60)

    # A. Metadata frame
    metadata_frame = prompt_for_frame(metadata, current_frame)

    # B. Main question
    main_question = prompt_for_question()

    # C. Question category
    question_category = prompt_for_category(metadata['source_htid'])

    # Only parallax questions are judged on fit with the target context,
    # so only they collect rejection rationales.
    is_parallax = question_category == "parallax"

    # D. Period words in main question
    period_words = prompt_for_period_words(main_question)

    # E. Manual comment
    manual_comment = prompt_for_manual_comment()

    # F. Answers
    answer_strings, answer_types, answer_probabilities, reject_reasons = prompt_for_answers(
        collect_reasons=is_parallax
    )

    # Build output record
    record = {
        "metadata_frame": metadata_frame,
        "main_question": main_question,
        "answer_strings": answer_strings,
        "answer_types": answer_types,
        "answer_probabilities": answer_probabilities,
        "reject_reasons": reject_reasons,
        "context_judged": 1 if is_parallax else 0,
        "question_category": question_category,
        "period_words_in_main_question": period_words,
        "manual_comment": manual_comment,
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

    if reject_reasons is None:
        del record["reject_reasons"]

    return record, metadata_frame


def confirm_htid(current_htid: str, metadata_file: str) -> Tuple[str, Optional[Dict]]:
    """
    Confirm or change the current htid.

    Args:
        current_htid: The current htid
        metadata_file: Path to primary_metadata.csv

    Returns:
        Tuple of (htid, metadata_dict or None if needs elicitation)
    """
    print(f"\nCurrent id is: {current_htid}")
    choice = input("New id, [a]ttribution, [h]andcrafted, or enter to confirm current id: ").strip()

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
    current_frame: Optional[str] = None

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
                current_frame = None
                needs_elicitation = True

            # Elicit metadata if needed
            if needs_elicitation:
                current_frame = None
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
            question, current_frame = create_question(current_metadata, current_frame)

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

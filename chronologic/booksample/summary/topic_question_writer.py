#!/usr/bin/env python3
"""
Topic Question Writer

Interactive script that turns potential topic-sentence questions into finished
benchmark questions with distractors.

Reads {barcode}_potentialquestions.jsonl from process_files/,
produces {barcode}_topicquestions.jsonl in the same directory.

Usage:
    python summary/topic_question_writer.py --file BARCODE
    python summary/topic_question_writer.py  # process all unfinished
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from nltk import sent_tokenize
except ImportError:
    import nltk
    nltk.download('punkt', quiet=True)
    from nltk import sent_tokenize

# Path setup
SCRIPT_DIR = Path(__file__).parent
BOOKSAMPLE_DIR = SCRIPT_DIR.parent
SOURCE_DIR = BOOKSAMPLE_DIR / "IDI_sample_1875-25"
PROCESS_FILES_DIR = SCRIPT_DIR / "process_files"

# Add batchconnectors to path for imports
sys.path.insert(0, str(BOOKSAMPLE_DIR / "batchconnectors"))
from metadata_elicitation import elicit_metadata, a_or_an

# Import distractor functions
from topic_distractor_generator import (
    make_same_book_distractors,
    make_anachronistic_distractors,
    normalize_distractor_format,
    round_length,
)

METADATA_FRAME_TEMPLATE = (
    "The following paragraph comes from {title}, {article} {genre} "
    "written by {author} and published in {date}. The topic sentence, which gives a preview of the paragraph's central theme, has been masked."
)

QUESTION_SUFFIX = (
    "Write a topic sentence that would provide a suitable introduction "
    "for this paragraph. Return only the topic sentence, without quotation marks:"
)


def build_topic_metadata_frame(metadata: dict) -> str:
    """Build the metadata frame string from metadata dict.

    Uses a shorter template when the author is blank or anonymous.
    """
    genre = metadata.get('source_genre', 'book')
    article = a_or_an(genre)
    author = metadata.get('source_author', '')

    if not author or author.strip().lower() in ('anonymous', 'unknown', 'various', 'n/a'):
        return (
            f"The following paragraph comes from {metadata['source_title']}, "
            f"{article} {genre} published in {metadata['source_date']}. "
            f"The topic sentence, which gives a preview of the paragraph's central theme, has been masked."
        )

    return METADATA_FRAME_TEMPLATE.format(
        title=metadata['source_title'],
        article=article,
        genre=genre,
        author=author,
        date=metadata['source_date'],
    )


def create_trimmed_paragraph(passage: str, synopsis: str) -> str:
    """
    Replace the synopsis in passage with [masked topic sentence].

    Uses exact string replacement; falls back to fuzzy match if needed.
    """
    marker = "[masked topic sentence]"

    # Try exact replacement
    if synopsis in passage:
        return passage.replace(synopsis, marker, 1)

    # Try with stripped whitespace variants
    stripped_synopsis = ' '.join(synopsis.split())
    stripped_passage = ' '.join(passage.split())
    if stripped_synopsis in stripped_passage:
        return stripped_passage.replace(stripped_synopsis, marker, 1)

    # Fuzzy fallback: find best matching substring
    import difflib
    # Try to find the synopsis somewhere in the passage
    best_ratio = 0.0
    best_start = 0
    best_end = len(passage)
    synopsis_len = len(synopsis)

    # Slide a window across the passage
    for start in range(len(passage) - synopsis_len // 2):
        for end_offset in range(-20, 21):
            end = start + synopsis_len + end_offset
            if end > len(passage) or end <= start:
                continue
            candidate = passage[start:end]
            ratio = difflib.SequenceMatcher(None, candidate, synopsis).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_start = start
                best_end = end

    if best_ratio > 0.7:
        return passage[:best_start] + marker + passage[best_end:]

    # Last resort: prepend marker
    print(f"  Warning: Could not locate synopsis in passage (best ratio: {best_ratio:.2f})")
    return marker + " " + passage


def present_passage_for_approval(trimmed_paragraph: str, synopsis: str) -> str | None:
    """
    Display trimmed paragraph and synopsis to user for approval.

    User can:
      - Accept (enter/y)
      - Reject (n) -> returns None
      - Edit (d) -> prompted for a string to delete from the paragraph,
        then re-presented. Useful for removing running headers or junk.

    Returns the (possibly edited) trimmed_paragraph, or None if rejected.
    """
    while True:
        print("\n" + "=" * 70)
        print("PASSAGE (with masked topic sentence):")
        print("-" * 70)
        print(trimmed_paragraph)
        print("-" * 70)
        print(f"TOPIC SENTENCE: {synopsis}")
        print("=" * 70)

        response = input(
            "Accept (enter/y), skip (n), or delete junk text (d)? "
        ).strip().lower()

        if response in ('', 'y', 'yes'):
            return trimmed_paragraph
        elif response in ('n', 'no'):
            return None
        elif response in ('d', 'delete'):
            to_delete = input("  String to delete: ")
            if to_delete and to_delete in trimmed_paragraph:
                trimmed_paragraph = trimmed_paragraph.replace(to_delete, '')
                # Clean up any double spaces left behind
                while '  ' in trimmed_paragraph:
                    trimmed_paragraph = trimmed_paragraph.replace('  ', ' ')
                trimmed_paragraph = trimmed_paragraph.strip()
                print("  Deleted. Showing updated passage...")
            elif to_delete:
                print("  String not found in passage. Try again.")
            # Loop back to re-display
        else:
            print("  Unrecognized option. Try again.")


def present_distractor_for_approval(distractor: str, dtype: str) -> tuple:
    """
    Display a distractor for user approval.

    Returns (distractor_string_or_None, final_type).
    User can accept, edit, or reject.
    """
    print(f"\n  DISTRACTOR [{dtype}]:")
    print(f"  {distractor}")

    response = input("  Accept (enter/y), edit (e), or reject (n)? ").strip().lower()

    if response in ('', 'y', 'yes'):
        return distractor, dtype
    elif response in ('e', 'edit'):
        edited = input("  Enter replacement: ").strip()
        if edited:
            return edited, f"manual_{dtype}"
        return distractor, dtype
    else:
        return None, dtype


def present_final_question(question_record: dict) -> bool:
    """
    Display complete question record for final approval.

    Returns True if approved, False if rejected.
    """
    print("\n" + "=" * 70)
    print("FINAL QUESTION RECORD:")
    print("-" * 70)
    print(f"Metadata: {question_record['metadata_frame']}")
    print(f"Category: {question_record['question_category']}")
    print(f"Period words: {question_record['period_words_in_main_question']}")
    print("-" * 70)

    for i, (atype, astr) in enumerate(
        zip(question_record['answer_types'], question_record['answer_strings'])
    ):
        label = "GROUND TRUTH" if i == 0 else f"DISTRACTOR {i}"
        print(f"  {label} [{atype}]: {astr[:100]}{'...' if len(astr) > 100 else ''}")

    print("=" * 70)

    response = input("Approve this question? (enter/y = yes, n = reject): ").strip().lower()
    return response in ('', 'y', 'yes')


def process_file(barcode: str, metadata: dict, sentences: list):
    """
    Process a single potentialquestions file into topicquestions.

    Reads {barcode}_potentialquestions.jsonl, interactively generates
    distractors, writes {barcode}_topicquestions.jsonl.
    """
    input_path = PROCESS_FILES_DIR / f"{barcode}_potentialquestions.jsonl"
    output_path = PROCESS_FILES_DIR / f"{barcode}_topicquestions.jsonl"

    # Read potential questions
    potential_questions = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                potential_questions.append(json.loads(line))

    if not potential_questions:
        print(f"No potential questions found in {input_path}")
        return

    # Check for existing output and offer to resume
    existing_count = 0
    if output_path.exists():
        with open(output_path, 'r', encoding='utf-8') as f:
            existing_count = sum(1 for line in f if line.strip())
        if existing_count > 0:
            response = input(
                f"\nFound {existing_count} existing questions in {output_path.name}. "
                f"Resume from line {existing_count + 1}? (enter/y = yes, n = restart): "
            ).strip().lower()
            if response in ('n', 'no'):
                existing_count = 0
                # Truncate the file
                open(output_path, 'w').close()

    # Build metadata frame
    metadata_frame = build_topic_metadata_frame(metadata)
    print(f"\nMetadata frame: {metadata_frame}")

    # Process each potential question
    for i, pq in enumerate(potential_questions):
        if i < existing_count:
            print(f"\nSkipping question {i + 1}/{len(potential_questions)} (already processed)")
            continue

        print(f"\n{'#' * 70}")
        print(f"Question {i + 1}/{len(potential_questions)}")

        passage = pq['passage']
        synopsis = pq['synopsis']

        # Create trimmed paragraph
        trimmed_paragraph = create_trimmed_paragraph(passage, synopsis)

        # Present for approval (may return edited paragraph or None)
        trimmed_paragraph = present_passage_for_approval(trimmed_paragraph, synopsis)
        if trimmed_paragraph is None:
            print("  Skipped.")
            continue

        # Generate same_book distractors
        print("\n  Generating same-book distractors...")
        similar_sentences = make_same_book_distractors(sentences, synopsis, passage)

        # Present top 2 same_book distractors for approval
        approved_same_book = []
        approved_same_book_types = []
        for j, sent in enumerate(similar_sentences[:2]):
            distractor, dtype = present_distractor_for_approval(sent, "same_book")
            if distractor is not None:
                approved_same_book.append(distractor)
                approved_same_book_types.append(dtype)

        # Generate anachronistic distractors
        gt_word_count = len(synopsis.split())
        anach_strings, anach_types = make_anachronistic_distractors(
            similar_sentences, metadata_frame, trimmed_paragraph, gt_word_count
        )

        # Normalize anachronistic distractors to match ground truth format
        anach_strings = [
            normalize_distractor_format(s, synopsis) for s in anach_strings
        ]

        # Present anachronistic distractors for approval
        approved_anach = []
        approved_anach_types = []
        for astr, atype in zip(anach_strings, anach_types):
            distractor, dtype = present_distractor_for_approval(astr, atype)
            if distractor is not None:
                approved_anach.append(distractor)
                approved_anach_types.append(dtype)

        # Prompt for manual distractor
        print("\n  Manual distractor (press enter to skip):")
        manual = input("  > ").strip()
        manual_strings = []
        manual_types = []
        if manual:
            manual_strings.append(manual)
            manual_types.append("manual")

        # Assemble answer lists
        answer_strings = [synopsis] + approved_same_book + approved_anach + manual_strings
        answer_types = (
            ["ground_truth"] + approved_same_book_types
            + approved_anach_types + manual_types
        )
        answer_probabilities = [1.0] + [0.0] * (len(answer_strings) - 1)

        # Build main_question
        main_question = trimmed_paragraph + "\n" + QUESTION_SUFFIX

        # Calculate period_words
        period_words = len(trimmed_paragraph.split())

        # Assemble the full question record
        question_record = {
            "metadata_frame": metadata_frame,
            "main_question": main_question,
            "source_title": metadata['source_title'],
            "source_author": metadata['source_author'],
            "source_date": metadata['source_date'],
            "author_nationality": metadata.get('author_nationality', ''),
            "source_genre": metadata.get('source_genre', ''),
            "author_birth": metadata.get('author_birth'),
            "author_profession": metadata.get('author_profession', ''),
            "source_htid": metadata['source_htid'],
            "question_category": "topic_sentence",
            "question_process": "automatic",
            "answer_types": answer_types,
            "answer_strings": answer_strings,
            "answer_probabilities": answer_probabilities,
            "period_words_in_main_question": period_words,
            "passage": passage,
        }

        # Present final question for approval
        if not present_final_question(question_record):
            print("  Question rejected.")
            continue

        # Write to output file (progressive, one line at a time)
        with open(output_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(question_record, ensure_ascii=False) + '\n')

        print(f"  Written to {output_path.name}")

    print(f"\nDone processing {barcode}.")


def main():
    parser = argparse.ArgumentParser(
        description="Generate topic-sentence benchmark questions with distractors."
    )
    parser.add_argument(
        '--file', type=str, default=None,
        help='Barcode of specific file to process (e.g., 32044106370034)'
    )
    args = parser.parse_args()

    if args.file:
        barcodes = [args.file]
    else:
        # Find all unfinished potentialquestions files
        barcodes = []
        for pq_path in sorted(PROCESS_FILES_DIR.glob('*_potentialquestions.jsonl')):
            barcode = pq_path.name.replace('_potentialquestions.jsonl', '')
            tq_path = PROCESS_FILES_DIR / f"{barcode}_topicquestions.jsonl"

            # Count lines in each
            pq_count = sum(1 for line in open(pq_path) if line.strip())
            tq_count = 0
            if tq_path.exists():
                tq_count = sum(1 for line in open(tq_path) if line.strip())

            if pq_count > tq_count:
                barcodes.append(barcode)

        if not barcodes:
            print("No unfinished files found.")
            return

        print(f"Found {len(barcodes)} files with unprocessed questions:")
        for b in barcodes:
            print(f"  {b}")

    for barcode in barcodes:
        # Check that potentialquestions file exists
        pq_path = PROCESS_FILES_DIR / f"{barcode}_potentialquestions.jsonl"
        if not pq_path.exists():
            print(f"Error: {pq_path} not found")
            continue

        # Load the source text file and tokenize into sentences
        source_path = SOURCE_DIR / f"{barcode}.txt"
        if not source_path.exists():
            print(f"Error: Source text not found: {source_path}")
            continue

        print(f"\nLoading source text from {source_path.name}...")
        with open(source_path, 'r', encoding='utf-8') as f:
            text = f.read()
        sentences = sent_tokenize(text)
        print(f"  {len(sentences)} sentences tokenized.")

        # Elicit metadata
        print(f"\nEliciting metadata for {barcode}...")
        metadata = elicit_metadata(source_htid=barcode)

        # Process the file
        process_file(barcode, metadata, sentences)


if __name__ == "__main__":
    main()

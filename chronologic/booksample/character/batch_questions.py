#!/usr/bin/env python3
"""
batch_questions.py - Stage 2: Interactive Question Generation

For each book with extraction complete but no questions:
1. Display book info from primary_metadata.csv
2. Prompt for metadata (nationality, genre, author birth year) if not already saved
3. Run form_character_questions.py interactively
4. Ask whether to continue to next book

Usage:
    python batch_questions.py

The script saves progress via metadata files and can be resumed at any time.
"""

import argparse
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

# Paths relative to this script
SCRIPT_DIR = Path(__file__).parent
BOOKSAMPLE_DIR = SCRIPT_DIR.parent
PROCESS_FILES_DIR = SCRIPT_DIR / "process_files"
FICTION_LIST = SCRIPT_DIR / "fiction_to_process.txt"
METADATA_CSV = BOOKSAMPLE_DIR / "primary_metadata.csv"
DICTIONARY_FILE = BOOKSAMPLE_DIR / "MainDictionary.txt"

# Scripts to run
QUESTIONS_SCRIPT = SCRIPT_DIR / "form_character_questions.py"


def load_barcodes(filepath: Path) -> list[str]:
    """
    Load barcodes from fiction_to_process.txt.

    Skips empty lines and lines starting with #.
    """
    barcodes = []

    if not filepath.exists():
        print(f"Error: {filepath} not found", file=sys.stderr)
        sys.exit(1)

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                barcodes.append(line)

    return barcodes


def load_primary_metadata(filepath: Path) -> dict[str, dict]:
    """
    Load primary_metadata.csv into a dict keyed by barcode_src.

    Returns dict mapping barcode (e.g., "hvd.hn1imp") to row dict.
    """
    metadata = {}

    if not filepath.exists():
        print(f"Warning: {filepath} not found", file=sys.stderr)
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


def reformat_author_name(author: str) -> str:
    """
    Convert author name from "Lastname, First Middle" to "First Middle Lastname".

    If there's a comma after the first word, moves that word to the end.
    E.g., "Smith, John Edward" -> "John Edward Smith"
    """
    if ',' not in author:
        return author
    parts = author.split(',', 1)
    if len(parts) == 2:
        lastname = parts[0].strip()
        rest = parts[1].strip()
        if rest:
            return f"{rest} {lastname}"
    return author


def get_output_paths(barcode: str) -> dict[str, Path]:
    """
    Get output file paths for a barcode.

    Uses uppercase barcode for consistency with existing files.
    """
    stem = barcode.upper()
    return {
        'characters': PROCESS_FILES_DIR / f"{stem}_characters.jsonl",
        'dialogue': PROCESS_FILES_DIR / f"{stem}_dialogue.jsonl",
        'metadata': PROCESS_FILES_DIR / f"{stem}_metadata.json",
        'questions': PROCESS_FILES_DIR / f"{stem}_questions.jsonl",
    }


def is_extraction_complete(barcode: str) -> bool:
    """Check if dialogue extraction is complete for a barcode."""
    paths = get_output_paths(barcode)
    return paths['dialogue'].exists()


def is_questions_complete(barcode: str) -> bool:
    """Check if question generation is complete for a barcode."""
    paths = get_output_paths(barcode)
    return paths['questions'].exists()


def load_book_metadata(barcode: str) -> dict | None:
    """Load saved metadata for a book if it exists."""
    paths = get_output_paths(barcode)
    if paths['metadata'].exists():
        with open(paths['metadata'], 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_book_metadata(barcode: str, metadata: dict) -> None:
    """Save metadata for a book."""
    paths = get_output_paths(barcode)
    with open(paths['metadata'], 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def display_book_info(barcode: str, csv_metadata: dict) -> None:
    """Display book information from CSV metadata."""
    print(f"\n{'='*60}")
    print(f"Book: {barcode}")
    print(f"{'='*60}")

    title = csv_metadata.get('title_src', 'Unknown')
    author = reformat_author_name(csv_metadata.get('author_src', 'Unknown'))
    date = csv_metadata.get('date1_src', 'Unknown')
    firstpub = csv_metadata.get('firstpub', date)
    author_dates = csv_metadata.get('authordates', '')
    nationality = csv_metadata.get('authnationality', '')
    genre_field = csv_metadata.get('number in genre', '')

    print(f"  Title: {title}")
    print(f"  Author: {author}")
    print(f"  Publication date: {date}")
    print(f"  First published: {firstpub}")
    print(f"  Author dates: {author_dates}")
    print(f"  Nationality: {nationality}")
    print(f"  Genre field: {genre_field}")


def prompt_for_metadata(barcode: str, csv_metadata: dict) -> dict:
    """
    Prompt user for required metadata fields.

    Pre-fills from CSV where possible.
    """
    print("\nPlease provide metadata for question generation:")

    # Pre-fill from CSV
    title = csv_metadata.get('title_src', '')
    author = reformat_author_name(csv_metadata.get('author_src', ''))
    date_str = csv_metadata.get('firstpub') or csv_metadata.get('date1_src', '')
    nationality_hint = csv_metadata.get('authnationality', '')
    author_dates = csv_metadata.get('authordates', '')

    # Parse author birth year from authordates if available (format: "1829-1900")
    birth_year_hint = ''
    if author_dates and '-' in author_dates:
        birth_year_hint = author_dates.split('-')[0].strip()

    # Get source_htid (the CSV barcode)
    source_htid = barcode_to_csv_key(barcode)

    # Prompt for each field
    print(f"\n  Title [from CSV]: {title}")
    title_input = input(f"  Confirm or edit title [{title}]: ").strip()
    if title_input:
        title = title_input

    print(f"\n  Author [from CSV]: {author}")
    author_input = input(f"  Confirm or edit author [{author}]: ").strip()
    if author_input:
        author = author_input

    while True:
        date_input = input(f"  Publication year [{date_str}]: ").strip()
        if not date_input:
            date_input = date_str
        try:
            pub_year = int(date_input)
            break
        except ValueError:
            print("  Please enter a valid year")

    nationality_input = input(f"  Author nationality [{nationality_hint}]: ").strip()
    if not nationality_input:
        nationality_input = nationality_hint
    if not nationality_input:
        nationality_input = input("  Author nationality (required): ").strip()

    genre_input = input("  Genre [novel]: ").strip()
    if not genre_input:
        genre_input = "novel"

    while True:
        birth_input = input(f"  Author birth year [{birth_year_hint}]: ").strip()
        if not birth_input:
            birth_input = birth_year_hint
        if not birth_input:
            birth_input = input("  Author birth year (required): ").strip()
        try:
            birth_year = int(birth_input)
            break
        except ValueError:
            print("  Please enter a valid year")

    metadata = {
        'source_title': title,
        'source_author': author,
        'source_date': pub_year,
        'source_htid': source_htid,
        'author_nationality': nationality_input,
        'genre': genre_input,
        'author_birth': birth_year
    }

    return metadata


def run_question_generation(barcode: str, use_qwen: bool = False,
                            use_mistral: bool = False) -> bool:
    """
    Run form_character_questions.py for a barcode.

    Args:
        barcode: Book barcode
        use_qwen: If True, use qwen2.5:7b-instruct for anachronistic distractors
        use_mistral: If True, use mistral-small:24b for anachronistic distractors

    Returns True on success/normal completion, False on error.
    """
    paths = get_output_paths(barcode)

    cmd = [
        sys.executable,
        str(QUESTIONS_SCRIPT),
        str(paths['characters']),
        str(paths['dialogue']),
        str(paths['questions']),
        '--metadata', str(paths['metadata']),
        '--dictionary', str(DICTIONARY_FILE)
    ]

    if use_qwen:
        cmd.append('--qwen')
    elif use_mistral:
        cmd.append('--mistral')

    print(f"\nRunning question generation...")
    print(f"Command: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, check=False)
        # Return code 0 or keyboard interrupt inside the script is normal
        return True
    except KeyboardInterrupt:
        print("\n  Question generation interrupted")
        return True  # Not an error, user can resume
    except Exception as e:
        print(f"  Error: {e}")
        return False


def process_book(barcode: str, csv_metadata_all: dict, use_qwen: bool = False,
                 use_mistral: bool = False) -> str:
    """
    Process a single book for question generation.

    Args:
        barcode: Book barcode
        csv_metadata_all: Dictionary of all CSV metadata
        use_qwen: If True, use qwen2.5:7b-instruct for anachronistic distractors
        use_mistral: If True, use mistral-small:24b for anachronistic distractors

    Returns: "continue", "skip", or "quit"
    """
    # Get CSV metadata for this book
    csv_key = barcode_to_csv_key(barcode)
    csv_metadata = csv_metadata_all.get(csv_key, {})

    if not csv_metadata:
        print(f"\nWarning: No CSV metadata found for {barcode} (key: {csv_key})")
        response = input("Continue anyway? (y/n) [n]: ").strip().lower()
        if response not in ['y', 'yes']:
            return "skip"
        csv_metadata = {}

    # Display book info
    display_book_info(barcode, csv_metadata)

    # Check/create metadata file
    book_metadata = load_book_metadata(barcode)

    if book_metadata is None:
        print("\nNo metadata file found. Creating one...")
        book_metadata = prompt_for_metadata(barcode, csv_metadata)
        save_book_metadata(barcode, book_metadata)
        print(f"\nMetadata saved to: {get_output_paths(barcode)['metadata']}")
    else:
        print(f"\nUsing existing metadata from: {get_output_paths(barcode)['metadata']}")
        print(f"  Title: {book_metadata.get('source_title')}")
        print(f"  Author: {book_metadata.get('source_author')}")
        print(f"  Date: {book_metadata.get('source_date')}")
        print(f"  Nationality: {book_metadata.get('author_nationality')}")
        print(f"  Genre: {book_metadata.get('genre')}")
        print(f"  Birth year: {book_metadata.get('author_birth')}")

        edit = input("\nEdit metadata? (y/n) [n]: ").strip().lower()
        if edit in ['y', 'yes']:
            book_metadata = prompt_for_metadata(barcode, csv_metadata)
            save_book_metadata(barcode, book_metadata)

    # Confirm before running
    proceed = input("\nProceed with question generation? (y/n) [y]: ").strip().lower()
    if proceed in ['n', 'no']:
        return "skip"

    # Run question generation
    success = run_question_generation(barcode, use_qwen, use_mistral)

    if not success:
        print(f"\nQuestion generation failed for {barcode}")

    # Ask what to do next
    print(f"\n{'='*60}")
    while True:
        response = input("Continue to next book? (y/n/q) [y]: ").strip().lower()
        if response in ['', 'y', 'yes']:
            return "continue"
        elif response in ['n', 'no']:
            return "quit"
        elif response in ['q', 'quit']:
            return "quit"
        else:
            print("  Enter y (continue) or n/q (quit)")


def main():
    parser = argparse.ArgumentParser(
        description="Batch process books for question generation"
    )
    parser.add_argument("--qwen", action="store_true",
                       help="Use qwen2.5:7b-instruct instead of gpt-oss:20b for anachronistic distractors")
    parser.add_argument("--mistral", action="store_true",
                       help="Use mistral-small:24b instead of gpt-oss:20b for anachronistic distractors")
    args = parser.parse_args()

    # Check for conflicting model options
    if args.qwen and args.mistral:
        print("Error: Cannot specify both --qwen and --mistral")
        sys.exit(1)

    print("="*60)
    print("Stage 2: Interactive Question Generation")
    if args.qwen:
        print("Using qwen2.5:7b-instruct for anachronistic distractors")
    elif args.mistral:
        print("Using mistral-small:24b for anachronistic distractors")
    else:
        print("Using gpt-oss:20b for anachronistic distractors")
    print("="*60)

    # Load barcodes
    print(f"\nLoading barcodes from: {FICTION_LIST}")
    barcodes = load_barcodes(FICTION_LIST)

    if not barcodes:
        print("No barcodes found in fiction_to_process.txt")
        sys.exit(0)

    print(f"Found {len(barcodes)} barcodes")

    # Load CSV metadata
    print(f"Loading metadata from: {METADATA_CSV}")
    csv_metadata = load_primary_metadata(METADATA_CSV)
    print(f"Loaded {len(csv_metadata)} entries")

    # Check status of each book
    ready = []
    complete = []
    incomplete = []

    for barcode in barcodes:
        if is_questions_complete(barcode):
            complete.append(barcode)
        elif is_extraction_complete(barcode):
            ready.append(barcode)
        else:
            incomplete.append(barcode)

    print(f"\nStatus:")
    print(f"  Questions complete: {len(complete)}")
    print(f"  Ready for questions: {len(ready)}")
    print(f"  Extraction incomplete: {len(incomplete)}")

    if incomplete:
        print(f"\n  Books needing extraction first:")
        for b in incomplete[:5]:
            print(f"    - {b}")
        if len(incomplete) > 5:
            print(f"    ... and {len(incomplete) - 5} more")

    if not ready:
        print("\nNo books ready for question generation.")
        print("Run batch_extract.py first to extract characters and dialogue.")
        sys.exit(0)

    print(f"\nWill process {len(ready)} books:")
    for b in ready:
        print(f"  - {b}")

    input("\nPress Enter to begin (or Ctrl+C to abort)...")

    # Process each ready book
    processed = 0
    skipped = 0

    try:
        for barcode in ready:
            result = process_book(barcode, csv_metadata, args.qwen, args.mistral)

            if result == "quit":
                print("\nQuitting...")
                break
            elif result == "skip":
                skipped += 1
            else:  # continue
                processed += 1

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")

    # Summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    print(f"  Processed: {processed}")
    print(f"  Skipped: {skipped}")
    print(f"  Previously complete: {len(complete)}")


if __name__ == "__main__":
    main()

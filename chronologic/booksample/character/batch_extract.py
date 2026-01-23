#!/usr/bin/env python3
"""
batch_extract.py - Stage 1: Automated Character Extraction

Runs extract_character_descriptions.py and extract_character_dialogue.py
on each book listed in fiction_to_process.txt.

Usage:
    python batch_extract.py [--dry-run] [--force] [--max-books N]

Options:
    --dry-run     Show what would be processed without running
    --force       Re-process even if outputs exist
    --max-books N Process at most N books
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Paths relative to this script
SCRIPT_DIR = Path(__file__).parent
BOOKSAMPLE_DIR = SCRIPT_DIR.parent
SOURCE_DIR = BOOKSAMPLE_DIR / "IDI_sample_1875-25"
PROCESS_FILES_DIR = SCRIPT_DIR / "process_files"
FICTION_LIST = SCRIPT_DIR / "fiction_to_process.txt"

# Scripts to run
DESCRIPTIONS_SCRIPT = SCRIPT_DIR / "extract_character_descriptions.py"
DIALOGUE_SCRIPT = SCRIPT_DIR / "extract_character_dialogue.py"


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


def get_source_file(barcode: str) -> Path | None:
    """
    Find the source text file for a barcode.

    Tries both the exact barcode and uppercase version.
    """
    # Try exact match first
    path = SOURCE_DIR / f"{barcode}.txt"
    if path.exists():
        return path

    # Try uppercase
    path = SOURCE_DIR / f"{barcode.upper()}.txt"
    if path.exists():
        return path

    return None


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


def run_descriptions_extraction(barcode: str, source_file: Path, dry_run: bool = False,
                                 use_mistral: bool = False) -> bool:
    """
    Run extract_character_descriptions.py for a barcode.

    Args:
        barcode: Book barcode
        source_file: Path to source text file
        dry_run: If True, only print command without running
        use_mistral: If True, use mistral-small:24b instead of gpt-oss:20b

    Returns True on success, False on failure.
    """
    paths = get_output_paths(barcode)
    output_file = paths['characters']

    cmd = [
        sys.executable,
        str(DESCRIPTIONS_SCRIPT),
        str(source_file),
        str(output_file)
    ]

    if use_mistral:
        cmd.append('--mistral')

    if dry_run:
        print(f"  Would run: {' '.join(cmd)}")
        return True

    print(f"  Running character descriptions extraction...")
    print(f"  Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            print(f"  Error: descriptions extraction failed with code {result.returncode}")
            return False
        return True
    except KeyboardInterrupt:
        print("\n  Interrupted by user")
        raise
    except Exception as e:
        print(f"  Error: {e}")
        return False


def run_dialogue_extraction(barcode: str, source_file: Path, dry_run: bool = False,
                            use_mistral: bool = False) -> bool:
    """
    Run extract_character_dialogue.py for a barcode.

    Args:
        barcode: Book barcode
        source_file: Path to source text file
        dry_run: If True, only print command without running
        use_mistral: If True, use mistral-small:24b instead of gpt-oss:20b

    Returns True on success, False on failure.
    """
    paths = get_output_paths(barcode)
    characters_file = paths['characters']
    output_file = paths['dialogue']

    if not dry_run and not characters_file.exists():
        print(f"  Error: characters file not found: {characters_file}")
        return False

    cmd = [
        sys.executable,
        str(DIALOGUE_SCRIPT),
        str(characters_file),
        str(source_file),
        str(output_file)
    ]

    if use_mistral:
        cmd.append('--mistral')

    if dry_run:
        print(f"  Would run: {' '.join(cmd)}")
        return True

    print(f"  Running dialogue extraction...")
    print(f"  Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            print(f"  Error: dialogue extraction failed with code {result.returncode}")
            return False
        return True
    except KeyboardInterrupt:
        print("\n  Interrupted by user")
        raise
    except Exception as e:
        print(f"  Error: {e}")
        return False


def process_book(barcode: str, force: bool = False, dry_run: bool = False,
                 use_mistral: bool = False) -> bool:
    """
    Process a single book through both extraction stages.

    Args:
        barcode: Book barcode
        force: If True, re-process even if outputs exist
        dry_run: If True, only print commands without running
        use_mistral: If True, use mistral-small:24b instead of gpt-oss:20b

    Returns True if processing completed (or was skipped), False on error.
    """
    print(f"\n{'='*60}")
    print(f"Processing: {barcode}")
    print(f"{'='*60}")

    # Check if already complete
    if not force and is_extraction_complete(barcode):
        print(f"  Skipping: extraction already complete")
        return True

    # Find source file
    source_file = get_source_file(barcode)
    if source_file is None:
        print(f"  Error: source file not found for {barcode}")
        print(f"  Looked in: {SOURCE_DIR}")
        return False

    print(f"  Source: {source_file}")

    # Ensure process_files directory exists
    if not dry_run:
        PROCESS_FILES_DIR.mkdir(exist_ok=True)

    # Check if we need to run descriptions extraction
    paths = get_output_paths(barcode)
    if force or not paths['characters'].exists():
        success = run_descriptions_extraction(barcode, source_file, dry_run, use_mistral)
        if not success:
            return False
    else:
        print(f"  Skipping descriptions: {paths['characters']} exists")

    # Run dialogue extraction
    success = run_dialogue_extraction(barcode, source_file, dry_run, use_mistral)
    if not success:
        return False

    print(f"  Extraction complete for {barcode}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Stage 1: Automated character extraction for all books in fiction_to_process.txt"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be processed without running'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Re-process even if outputs exist'
    )
    parser.add_argument(
        '--max-books',
        type=int,
        default=None,
        help='Process at most N books'
    )
    parser.add_argument(
        '--mistral',
        action='store_true',
        help='Use mistral-small:24b instead of gpt-oss:20b'
    )

    args = parser.parse_args()

    # Print model info
    if args.mistral:
        print("Using model: mistral-small:24b")
    else:
        print("Using model: gpt-oss:20b")

    # Load barcodes
    print(f"Loading barcodes from: {FICTION_LIST}")
    barcodes = load_barcodes(FICTION_LIST)

    if not barcodes:
        print("No barcodes found in fiction_to_process.txt")
        sys.exit(0)

    print(f"Found {len(barcodes)} barcodes to process")

    # Limit if requested
    if args.max_books is not None:
        barcodes = barcodes[:args.max_books]
        print(f"Limited to first {args.max_books} books")

    if args.dry_run:
        print("\n*** DRY RUN - no changes will be made ***\n")

    # Process each book
    processed = 0
    skipped = 0
    failed = 0

    try:
        for barcode in barcodes:
            if not args.force and is_extraction_complete(barcode):
                print(f"\nSkipping {barcode}: extraction already complete")
                skipped += 1
                continue

            success = process_book(barcode, force=args.force, dry_run=args.dry_run,
                                   use_mistral=args.mistral)
            if success:
                processed += 1
            else:
                failed += 1

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")

    # Summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    print(f"  Processed: {processed}")
    print(f"  Skipped (already complete): {skipped}")
    print(f"  Failed: {failed}")
    print(f"  Total: {len(barcodes)}")


if __name__ == "__main__":
    main()

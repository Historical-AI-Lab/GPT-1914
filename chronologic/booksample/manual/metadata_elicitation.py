#!/usr/bin/env python3
"""
Metadata Elicitation Module

Collect and validate metadata for a source, using defaults from:
1. Existing JSON metadata file in json_metadata/ (highest priority)
2. CSV defaults from primary_metadata.csv (fallback)

Elicited metadata is saved to json_metadata/{barcode}_metadata.json.

Usage:
    from metadata_elicitation import elicit_metadata

    metadata = elicit_metadata(metadata_file="../primary_metadata.csv", source_htid="")
"""

import csv
import json
import re
from pathlib import Path
from typing import Dict, Optional

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
                metadata[barcode] = row

    return metadata


def barcode_to_csv_key(barcode: str) -> str:
    """
    Convert filename barcode to CSV lookup key.

    Filename: 32044106370034 or HN1IMP (uppercase for alphabetic)
    CSV key: hvd.32044106370034 or hvd.hn1imp (with hvd. prefix, lowercase)
    """
    # If already has hvd. prefix, normalize case
    if barcode.lower().startswith('hvd.'):
        return barcode.lower()
    return f"hvd.{barcode.lower()}"


def htid_to_barcode(htid: str) -> str:
    """
    Extract barcode from htid for use in filenames.

    htid: hvd.hn1nuj or HN1NUJ or hvd.32044106370034
    Returns: HN1NUJ or 32044106370034 (uppercase for alphabetic)
    """
    # Remove hvd. prefix if present
    if htid.lower().startswith('hvd.'):
        barcode = htid[4:]
    else:
        barcode = htid
    return barcode.upper()


def get_json_metadata_path(htid: str) -> Path:
    """
    Get the path to the JSON metadata file for an htid.

    Args:
        htid: The source htid (e.g., "hvd.hn1nuj" or "HN1NUJ")

    Returns:
        Path to json_metadata/{BARCODE}_metadata.json
    """
    barcode = htid_to_barcode(htid)
    return CENTRAL_METADATA_DIR / f"{barcode}_metadata.json"


def load_json_metadata(htid: str) -> Optional[Dict]:
    """
    Load existing JSON metadata for an htid if it exists.

    Args:
        htid: The source htid

    Returns:
        Metadata dict if file exists, None otherwise
    """
    json_path = get_json_metadata_path(htid)
    if json_path.exists():
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load {json_path}: {e}")
    return None


def save_json_metadata(htid: str, metadata: Dict) -> Path:
    """
    Save metadata to central JSON metadata directory.

    Args:
        htid: The source htid
        metadata: The metadata dict to save

    Returns:
        Path to the saved file
    """
    CENTRAL_METADATA_DIR.mkdir(exist_ok=True)
    json_path = get_json_metadata_path(htid)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    return json_path


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


def normalize_nationality(nationality: str) -> str:
    """
    Normalize nationality abbreviations to full adjective form.

    Examples:
        "US" -> "American"
        "UK" -> "British"
        "UK (England)" -> "British"
        "UK (Irish writer, pub London)" -> "Irish"
    """
    if not nationality:
        return nationality

    nat_lower = nationality.lower().strip()

    # Check for Irish in parenthetical
    if 'irish' in nat_lower:
        return "Irish"

    # Check for US
    if nat_lower == 'us' or nat_lower.startswith('us '):
        return "American"

    # Check for UK
    if nat_lower == 'uk' or nat_lower.startswith('uk ') or nat_lower.startswith('uk('):
        return "British"

    # Return original if no normalization needed
    return nationality


def parse_birth_year(authordates: str) -> Optional[int]:
    """
    Parse author birth year from authordates field.

    The field format is typically "YYYY-" or "YYYY-YYYY".

    Examples:
        "1855-" -> 1855
        "1829-1900" -> 1829
        "1881 - , 1886 -" -> 1881
        "" -> None
    """
    if not authordates:
        return None

    # Find first 4-digit number (should be birth year)
    match = re.search(r'\b(\d{4})\b', authordates)
    if match:
        return int(match.group(1))

    return None


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

    first_letter = word[0].lower()
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


def build_metadata_frame(metadata: Dict) -> str:
    """
    Build metadata frame string from metadata dict.

    Uses a simpler template if author is missing or anonymous.

    Args:
        metadata: Dict with source_title, source_author, etc.

    Returns:
        Formatted metadata frame string
    """
    author = metadata.get('source_author', '')

    # Check for anonymous/missing author
    if not author or author.strip().lower() in ('', 'anonymous', 'unknown', 'various', 'n/a'):
        return (
            f"The following questions is based on {metadata['source_title']}, "
            f"{a_or_an(metadata.get('source_genre', 'book'))} {metadata.get('source_genre', 'book')} "
            f"published in {metadata['source_date']}."
        )
    else:
        nationality = metadata.get('author_nationality', '')
        profession = metadata.get('author_profession', 'writer')

        return (
            f"The following question is drawn from {metadata['source_title']}, "
            f"{a_or_an(metadata.get('source_genre', 'book'))} {metadata.get('source_genre', 'book')} "
            f"published in {metadata['source_date']} by {metadata['source_author']}, "
            f"{a_or_an(nationality)} {nationality} {profession}."
        )


def prompt_with_default(prompt_text: str, default: str = "") -> str:
    """
    Prompt user for input with a default value shown in brackets.

    Args:
        prompt_text: The field name or prompt
        default: Default value to show

    Returns:
        User input or default if empty
    """
    if default:
        display = f"{prompt_text} [{default}]: "
    else:
        display = f"{prompt_text}: "

    user_input = input(display).strip()
    return user_input if user_input else default


def elicit_metadata(metadata_file: str = "../primary_metadata.csv",
                    source_htid: str = "",
                    save_to_json: bool = True) -> Dict:
    """
    Collect and validate metadata for a source.

    Priority for defaults:
    1. Existing JSON metadata file in json_metadata/ (highest priority)
    2. CSV defaults from primary_metadata.csv (fallback)

    If save_to_json is True (default), saves the result to json_metadata/.

    Args:
        metadata_file: Path to primary_metadata.csv
        source_htid: Initial htid (will prompt if blank)
        save_to_json: Whether to save elicited metadata to json_metadata/

    Returns:
        Dict with keys:
        - source_htid, source_title, source_author, source_date
        - author_nationality, source_genre, author_birth, author_profession
    """
    # Determine the correct path to CSV
    script_dir = Path(__file__).parent
    csv_path = Path(metadata_file)
    if not csv_path.is_absolute():
        csv_path = script_dir / metadata_file

    # Load CSV metadata
    csv_data = load_primary_metadata_csv(csv_path)
    print(f"Loaded {len(csv_data)} entries from metadata CSV")

    # Step 1: Get source_htid if blank
    if not source_htid:
        source_htid = input("Enter source_htid: ").strip()

    # Step 2: Check for existing JSON metadata (highest priority)
    existing_json = load_json_metadata(source_htid)
    if existing_json:
        json_path = get_json_metadata_path(source_htid)
        print(f"Found existing metadata in: {json_path}")
        print("\nExisting metadata:")
        for key, value in existing_json.items():
            print(f"  {key}: {value}")

        use_existing = input("\nUse this metadata? (enter for yes, 'e' to edit): ").strip().lower()
        if use_existing not in ['e', 'edit']:
            return existing_json

        # User wants to edit - use existing values as defaults
        default_title = existing_json.get('source_title', '')
        default_author = existing_json.get('source_author', '')
        default_date = existing_json.get('source_date', '')
        default_nationality = existing_json.get('author_nationality', '')
        default_genre = existing_json.get('source_genre', 'novel')
        default_birth = existing_json.get('author_birth')
        default_profession = existing_json.get('author_profession', '')
        print("\nEditing existing metadata...")
    else:
        # Step 3: Lookup htid in CSV for defaults
        csv_key = barcode_to_csv_key(source_htid)
        row = csv_data.get(csv_key, {})

        if row:
            print(f"Found CSV entry for {csv_key}")
        else:
            print(f"No CSV entry found for {csv_key}")

        # Extract and normalize defaults from CSV
        default_title = clean_title(row.get('title_src', ''))
        default_author = reformat_author_name(row.get('author_src', ''))
        default_date = row.get('firstpub') or row.get('date1_src', '')
        default_nationality = normalize_nationality(row.get('authnationality', ''))
        default_genre = 'novel'  # Default fallback

        # Parse author birth year from authordates
        author_dates = row.get('authordates', '')
        default_birth = parse_birth_year(author_dates)

        # Check if profession column exists
        default_profession = row.get('author_profession', '')

        # Display CSV defaults if available
        if row:
            print("\nDefaults from primary_metadata.csv:")
            print(f"  Title: {default_title}")
            print(f"  Author: {default_author}")
            print(f"  Date: {default_date}")
            print(f"  Nationality: {default_nationality}")
            if author_dates:
                print(f"  Author dates: {author_dates} (birth: {default_birth})")

    # Step 4: Prompt for each field with defaults
    print("\nProvide metadata (press Enter to accept default in brackets):")

    metadata = {}
    metadata['source_htid'] = source_htid

    # Title
    metadata['source_title'] = prompt_with_default("Title", default_title)

    # Author
    metadata['source_author'] = prompt_with_default("Author", default_author)

    # Date (required)
    while True:
        date_str = prompt_with_default("Publication year", str(default_date) if default_date else "")
        if date_str:
            try:
                metadata['source_date'] = int(date_str)
                break
            except ValueError:
                print("  Please enter a valid year (integer)")
        else:
            print("  Publication year is required")

    # Nationality
    metadata['author_nationality'] = prompt_with_default("Author nationality", default_nationality)

    # Genre
    metadata['source_genre'] = prompt_with_default("Genre", default_genre)

    # Author birth year
    birth_str = prompt_with_default("Author birth year",
                                     str(default_birth) if default_birth else "")
    if birth_str:
        try:
            metadata['author_birth'] = int(birth_str)
        except ValueError:
            metadata['author_birth'] = None
    else:
        metadata['author_birth'] = None

    # Author profession
    metadata['author_profession'] = prompt_with_default("Author profession", default_profession)

    # Validate required fields
    if not metadata['source_htid']:
        raise ValueError("source_htid is required")

    print("\nMetadata collected:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")

    # Step 5: Save to JSON
    if save_to_json:
        json_path = save_json_metadata(source_htid, metadata)
        print(f"\nMetadata saved to: {json_path}")

    return metadata


if __name__ == "__main__":
    # Test the module
    import sys

    htid = sys.argv[1] if len(sys.argv) > 1 else ""
    metadata = elicit_metadata(source_htid=htid)
    print("\nFinal metadata dict:")
    print(metadata)

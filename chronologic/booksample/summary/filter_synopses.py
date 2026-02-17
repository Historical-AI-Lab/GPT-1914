#!/usr/bin/env python3
"""
filter_synopses.py

Sends candidate synopsis passages (from find_synopses.py) to a fine-tuned
GPT-4.1-mini model for more stringent filtering.

Reads *_synopses.jsonl files from process_files/, sends "y" entries to the
model, and writes accepted passages to {barcode}_potentialquestions.jsonl.

Requires credentials.txt in the summary/ directory (not committed to git):
    Line 1: OpenAI organization ID
    Line 2: OpenAI API key

Usage:
    python summary/filter_synopses.py [--credentials summary/credentials.txt] [--dry-run]
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse

try:
    import openai
except ImportError:
    print("Error: openai package not installed. Run: pip install openai")
    raise

# --- Path configuration ---
SCRIPT_DIR = Path(__file__).parent
PROCESS_FILES_DIR = SCRIPT_DIR / "process_files"
FILTERED_FILES_LOG = SCRIPT_DIR / "filtered_files.txt"
DEFAULT_CREDENTIALS = SCRIPT_DIR / "credentials.txt"

# --- Model configuration ---
FINETUNED_MODEL = "ft:gpt-4.1-mini-2025-04-14:tedunderwood::CbB93x2c"

# --- System prompt (verbatim from fine-tuning data) ---
SYSTEM_PROMPT = """You are sorting paragraphs into two groups: those that contain a sentence that previews or summarizes the whole paragraph, and those that lack single-sentence synopsis.

Most paragraphs do not contain a synopsis sentence, and if one does not already exist you should not create one. For instance, consider the following paragraph:

This may clearly be seen by taking a very small quantity of such a substance as chlorate of potash. If a crystal of this is examined under a magnifying glass till its crystalline form and structure are familiar, and it is then placed in a test-tube and gently heated, cleavage will at once be evident. With a little crackling, the chlorate splits itself into many crystals along its chief lines of cleavage (called the cleavage planes), every one of which crystals showing under the microscope the identical form and characteristics of the larger crystal from which it came.

No single sentence there adequately summarizes the whole. If you determine that the paragraph does not contain a good synopsis, respond ONLY with the following JSON object:

{"synopsis_present": "n", "synopsis": ""}

If there is a synopsis, you will answer ONLY with a valid JSON object in exactly this format:

{"synopsis_present": "y", "synopsis": <single verbatim sentence from the text>}

For instance, given the following paragraph:

First, I went to the wrong classroom for math. I was sitting in the class, surrounded by people taking notes and paying attention to how to do equations, which would have been okay if I was supposed to be in an algebra class. In reality, I was supposed to be in geometry, and when I discovered my error, I had already missed the first twenty minutes of a one-hour class. When I got to the correct class, all twenty-five students turned and looked at me as the teacher said, "You're late." That would have been bad enough, but in my next class my history teacher spoke so fast I could not follow most of what they said. The only thing I did hear was that we were having a quiz tomorrow over today\u2019s lecture. My day seemed to be going better during botany class, that is, until we visited the lab. I had a sneezing fit because of one of the plants in the lab and had to leave the room. When I finally finished my classes for the day, I discovered I had locked my keys in the car and had to wait for my brother to bring another set. My first day of college was a disaster.

The correct response would be:

{"synopsis_present": "y", "synopsis": "My first day of college was a disaster."}"""


def load_credentials(credentials_path: Path) -> "openai.OpenAI":
    """Load OpenAI credentials and return a client."""
    if not credentials_path.exists():
        raise FileNotFoundError(
            f"Credentials file not found: {credentials_path}\n"
            f"Expected format:\n  Line 1: OpenAI organization ID\n"
            f"  Line 2: OpenAI API key")

    with open(credentials_path, encoding='utf-8') as f:
        lines = f.readlines()

    if len(lines) < 2:
        raise ValueError(
            f"Credentials file must have at least 2 lines "
            f"(organization, api_key)")

    organization = lines[0].strip()
    api_key = lines[1].strip()
    return openai.OpenAI(organization=organization, api_key=api_key)


def get_model_prediction(client: "openai.OpenAI", passage: str,
                          model: str = FINETUNED_MODEL,
                          max_retries: int = 3) -> Optional[str]:
    """Send a passage to the model and return the response content."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": passage}
    ]

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"    Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise
    return None


def parse_json_response(response_text: str) -> Optional[Dict[str, Any]]:
    """Parse JSON response and extract synopsis fields."""
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start != -1 and end > start:
            try:
                return json.loads(response_text[start:end])
            except json.JSONDecodeError:
                pass
    return None


def get_synopses_files() -> List[Path]:
    """Get all *_synopses.jsonl files in process_files/, sorted."""
    if not PROCESS_FILES_DIR.exists():
        return []
    return sorted(PROCESS_FILES_DIR.glob("*_synopses.jsonl"))


def get_filtered_barcodes() -> set:
    """Get barcodes that already have _potentialquestions.jsonl files."""
    if not PROCESS_FILES_DIR.exists():
        return set()
    barcodes = set()
    for f in PROCESS_FILES_DIR.glob("*_potentialquestions.jsonl"):
        barcode = f.name.replace("_potentialquestions.jsonl", "")
        barcodes.add(barcode)
    return barcodes


def get_logged_files() -> set:
    """Get filenames logged in filtered_files.txt."""
    if not FILTERED_FILES_LOG.exists():
        return set()
    with open(FILTERED_FILES_LOG, encoding='utf-8') as f:
        return {line.strip() for line in f if line.strip()}


def get_unfiltered_files() -> List[Path]:
    """Get synopses files that haven't been filtered yet."""
    all_synopses = get_synopses_files()
    filtered_barcodes = get_filtered_barcodes()

    unfiltered = []
    for f in all_synopses:
        barcode = f.name.replace("_synopses.jsonl", "")
        if barcode not in filtered_barcodes:
            unfiltered.append(f)

    print(f"Synopses files: {len(all_synopses)}, "
          f"Already filtered: {len(filtered_barcodes)}, "
          f"Remaining: {len(unfiltered)}")
    return unfiltered


def load_synopses_file(filepath: Path) -> List[Dict]:
    """Load a JSONL synopses file."""
    records = []
    with open(filepath, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def filter_single_file(client: "openai.OpenAI", synopses_path: Path,
                        model: str = FINETUNED_MODEL) -> List[Dict]:
    """Filter a synopses file through the fine-tuned model.

    Returns list of accepted entries (passages the model also marks "y").
    """
    barcode = synopses_path.name.replace("_synopses.jsonl", "")
    records = load_synopses_file(synopses_path)

    # Only send candidates that Qwen marked as "y"
    candidates = [r for r in records if r.get("synopsis_present") == "y"]

    if not candidates:
        print(f"  No candidates to filter")
        return []

    print(f"  {len(candidates)} candidates from {len(records)} paragraphs")
    accepted = []

    for i, record in enumerate(candidates):
        passage = record["passage"]
        print(f"    Filtering {i+1}/{len(candidates)}...", end="")

        try:
            response_text = get_model_prediction(client, passage, model)
            if response_text is None:
                print(" no response")
                continue

            parsed = parse_json_response(response_text)
            if parsed is None:
                print(" parse error")
                continue

            if parsed.get("synopsis_present", "").lower() == "y":
                accepted_record = {
                    "filename": barcode,
                    "passage": passage,
                    "synopsis": parsed.get("synopsis", "")
                }
                accepted.append(accepted_record)
                print(" accepted")
            else:
                print(" rejected")

        except Exception as e:
            print(f" error: {e}")
            raise

    return accepted


def write_potentialquestions(barcode: str, results: List[Dict]) -> None:
    """Write accepted results to {barcode}_potentialquestions.jsonl."""
    output_path = PROCESS_FILES_DIR / f"{barcode}_potentialquestions.jsonl"
    with open(output_path, 'w', encoding='utf-8') as f:
        for record in results:
            f.write(json.dumps(record) + '\n')


def mark_file_filtered(synopses_filename: str) -> None:
    """Append a filename to filtered_files.txt."""
    with open(FILTERED_FILES_LOG, 'a', encoding='utf-8') as f:
        f.write(synopses_filename + '\n')


def main():
    parser = argparse.ArgumentParser(
        description="Filter synopsis candidates using fine-tuned GPT-4.1-mini")
    parser.add_argument("--credentials", type=Path,
                        default=DEFAULT_CREDENTIALS,
                        help=f"Path to credentials file (default: {DEFAULT_CREDENTIALS})")
    parser.add_argument("--model", type=str, default=FINETUNED_MODEL,
                        help=f"Fine-tuned model ID (default: {FINETUNED_MODEL})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be filtered without running")
    args = parser.parse_args()

    # Get unfiltered files
    unfiltered = get_unfiltered_files()

    if not unfiltered:
        print("All synopses files have been filtered!")
        return

    print(f"\nWill filter {len(unfiltered)} files:")
    for f in unfiltered:
        print(f"  {f.name}")

    if args.dry_run:
        return

    # Load credentials and create client
    client = load_credentials(args.credentials)
    total_accepted = 0

    try:
        for i, synopses_path in enumerate(unfiltered):
            barcode = synopses_path.name.replace("_synopses.jsonl", "")
            print(f"\n--- File {i+1}/{len(unfiltered)}: {synopses_path.name} ---")

            accepted = filter_single_file(client, synopses_path, args.model)
            write_potentialquestions(barcode, accepted)
            mark_file_filtered(synopses_path.name)

            total_accepted += len(accepted)
            print(f"  Accepted: {len(accepted)}")

    except KeyboardInterrupt:
        print("\n\nInterrupted. Progress saved for completed files.")

    # Summary
    filtered_barcodes = get_filtered_barcodes()
    total_synopses = len(get_synopses_files())
    print(f"\n=== Summary ===")
    print(f"Filtered so far: {len(filtered_barcodes)}/{total_synopses}")
    print(f"Accepted this run: {total_accepted}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
find_synopses.py

Identifies paragraphs containing synopsis sentences using Qwen via Ollama.

Processes text files from IDI_sample_1875-25/ in alphabetical order,
20 at a time. Progress is tracked by the presence of output files in
process_files/. Each invocation picks up where the last left off.

Usage:
    python summary/find_synopses.py [--batch-size 20] [--num-paragraphs 10] [--dry-run]
"""

import json
import requests
import random
from pathlib import Path
from typing import List, Dict, Any
import argparse

# --- Path configuration ---
SCRIPT_DIR = Path(__file__).parent
BOOKSAMPLE_DIR = SCRIPT_DIR.parent
SOURCE_DIR = BOOKSAMPLE_DIR / "IDI_sample_1875-25"
PROCESS_FILES_DIR = SCRIPT_DIR / "process_files"

# --- Model configuration ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b-instruct"


def extract_paragraphs_from_file(file_path: Path, min_words: int = 80,
                                  max_words: int = 1000,
                                  num_paragraphs: int = 10) -> List[str]:
    """
    Extract paragraphs from a text file, filter by word count,
    and randomly select a subset.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Split by double newlines first, fall back to single if too few
    paragraphs = text.split('\n\n')
    if len(paragraphs) < 10:
        paragraphs = text.split('\n')

    filtered_paragraphs = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if 'Gutenberg' in para or 'ebook' in para or '1.F' in para:
            continue
        word_count = len(para.split())
        if min_words <= word_count <= max_words:
            filtered_paragraphs.append(para)

    num_to_select = min(num_paragraphs, len(filtered_paragraphs))
    if num_to_select > 0:
        return random.sample(filtered_paragraphs, num_to_select)
    else:
        return []


def call_ollama(prompt: str, model: str = MODEL) -> Dict[str, Any]:
    """Call Ollama API with the given prompt."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "top_p": 0.9
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print(f"  Request timed out after 5 minutes")
        return {"response": "ERROR"}
    except requests.exceptions.RequestException as e:
        print(f"  Error calling Ollama: {e}")
        return {"response": "ERROR"}


def create_summary_prompt(passage: str) -> str:
    """Create prompt for synopsis detection."""
    escaped_passage = passage.replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')

    prompt = f"""You are sorting paragraphs into two groups: those that contain a sentence that previews or summarizes the whole paragraph, and those that lack single-sentence synopsis.

Most paragraphs do not contain a synopsis sentence, and if one does not already exist you should not create one. For instance, consider the following paragraph:

This may clearly be seen by taking a very small quantity of such a substance as chlorate of potash. If a crystal of this is examined under a magnifying glass till its crystalline form and structure are familiar, and it is then placed in a test-tube and gently heated, cleavage will at once be evident. With a little crackling, the chlorate splits itself into many crystals along its chief lines of cleavage (called the cleavage planes), every one of which crystals showing under the microscope the identical form and characteristics of the larger crystal from which it came.

No single sentence there adequately summarizes the whole. If you determine that the paragraph does not contain a good synopsis, respond ONLY with the following JSON object:

{{"synopsis_present": "n", "synopsis": ""}}

If there is a synopsis, you will answer ONLY with a valid JSON object in exactly this format:

{{"synopsis_present": "y", "synopsis": <single verbatim sentence from the text>}}

For instance, given the following paragraph:

First, I went to the wrong classroom for math. I was sitting in the class, surrounded by people taking notes and paying attention to how to do equations, which would have been okay if I was supposed to be in an algebra class. In reality, I was supposed to be in geometry, and when I discovered my error, I had already missed the first twenty minutes of a one-hour class. When I got to the correct class, all twenty-five students turned and looked at me as the teacher said, "You're late." That would have been bad enough, but in my next class my history teacher spoke so fast I could not follow most of what they said. The only thing I did hear was that we were having a quiz tomorrow over today's lecture. My day seemed to be going better during botany class, that is, until we visited the lab. I had a sneezing fit because of one of the plants in the lab and had to leave the room. When I finally finished my classes for the day, I discovered I had locked my keys in the car and had to wait for my brother to bring another set. My first day of college was a disaster.

The correct response would be:

{{"synopsis_present": "y", "synopsis": "My first day of college was a disaster."}}

Passage to analyze: {escaped_passage}
JSON response:"""

    return prompt


def clean_and_parse_json(response_text: str) -> Dict[str, Any]:
    """Attempt to clean and parse JSON response, with fallbacks."""
    start_idx = response_text.find('{')
    if start_idx == -1:
        raise ValueError("No JSON object found in response")

    end_idx = response_text.rfind('}')
    if end_idx == -1:
        raise ValueError("No complete JSON object found in response")

    json_str = response_text[start_idx:end_idx + 1]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        json_str = json_str.replace('\n', ' ').replace('\r', ' ')
        json_str = json_str.replace('\\"', '"').replace('""', '"')
        return json.loads(json_str)


def get_all_input_files() -> List[Path]:
    """Get all .txt files from the source directory, sorted alphabetically."""
    return sorted(SOURCE_DIR.glob("*.txt"), key=lambda p: p.name)


def get_processed_stems() -> set:
    """Get stems of files already processed (have _synopses.jsonl in process_files/)."""
    if not PROCESS_FILES_DIR.exists():
        return set()
    stems = set()
    for f in PROCESS_FILES_DIR.glob("*_synopses.jsonl"):
        stem = f.name.replace("_synopses.jsonl", "")
        stems.add(stem)
    return stems


def get_unprocessed_files(batch_size: int) -> List[Path]:
    """Get the next batch of unprocessed files."""
    all_files = get_all_input_files()
    processed = get_processed_stems()
    unprocessed = [f for f in all_files if f.stem not in processed]
    print(f"Total: {len(all_files)}, Processed: {len(processed)}, "
          f"Remaining: {len(unprocessed)}")
    return unprocessed[:batch_size]


def process_single_file(file_path: Path, num_paragraphs: int,
                         min_words: int, max_words: int,
                         model: str = MODEL) -> None:
    """Extract paragraphs from a file and analyze each for synopses."""
    barcode = file_path.stem
    output_file = PROCESS_FILES_DIR / f"{barcode}_synopses.jsonl"
    tmp_file = PROCESS_FILES_DIR / f"{barcode}_synopses.jsonl.tmp"

    print(f"\nProcessing {file_path.name}...")

    # Extract paragraphs
    try:
        paragraphs = extract_paragraphs_from_file(
            file_path, min_words, max_words, num_paragraphs)
    except Exception as e:
        print(f"  Error reading file: {e}")
        with open(tmp_file, 'w', encoding='utf-8') as f:
            record = {"filename": barcode, "passage": "",
                       "synopsis_present": "error", "synopsis": "",
                       "error": f"file read error: {e}"}
            f.write(json.dumps(record) + '\n')
        tmp_file.rename(output_file)
        return

    if not paragraphs:
        print(f"  No qualifying paragraphs found")
        with open(tmp_file, 'w', encoding='utf-8') as f:
            record = {"filename": barcode, "passage": "",
                       "synopsis_present": "empty", "synopsis": "",
                       "error": "no qualifying paragraphs"}
            f.write(json.dumps(record) + '\n')
        tmp_file.rename(output_file)
        return

    print(f"  Extracted {len(paragraphs)} paragraphs")
    synopsis_count = 0

    with open(tmp_file, 'w', encoding='utf-8') as f:
        for i, passage in enumerate(paragraphs):
            print(f"  Analyzing paragraph {i+1}/{len(paragraphs)}...", end="")

            prompt = create_summary_prompt(passage)
            response = call_ollama(prompt, model=model)

            if response.get("response") == "ERROR":
                result = {"filename": barcode, "passage": passage,
                          "synopsis_present": "error", "synopsis": "",
                          "error": "API call failed"}
                print(" error")
            else:
                try:
                    llm_output = clean_and_parse_json(response["response"])
                    result = {
                        "filename": barcode,
                        "passage": passage,
                        "synopsis_present": llm_output.get(
                            "synopsis_present", "idk").lower(),
                        "synopsis": llm_output.get("synopsis", "")
                    }
                    if result["synopsis_present"] == "y":
                        synopsis_count += 1
                        print(" y")
                    else:
                        print(" n")
                except (json.JSONDecodeError, ValueError):
                    result = {"filename": barcode, "passage": passage,
                              "synopsis_present": "error", "synopsis": "",
                              "error": "decode error"}
                    print(" parse error")

            f.write(json.dumps(result) + '\n')

    # Atomically mark as complete
    tmp_file.rename(output_file)
    print(f"  Done: {synopsis_count} synopses found in {len(paragraphs)} paragraphs")


def main():
    parser = argparse.ArgumentParser(
        description="Find synopsis sentences in text files using Qwen via Ollama")
    parser.add_argument("--batch-size", type=int, default=20,
                        help="Number of files to process per invocation (default: 20)")
    parser.add_argument("--num-paragraphs", type=int, default=10,
                        help="Paragraphs to sample per file (default: 10)")
    parser.add_argument("--min-words", type=int, default=80,
                        help="Minimum paragraph word count (default: 80)")
    parser.add_argument("--max-words", type=int, default=1000,
                        help="Maximum paragraph word count (default: 1000)")
    parser.add_argument("--model", type=str, default=MODEL,
                        help=f"Ollama model to use (default: {MODEL})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be processed without running")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    # Ensure process_files directory exists
    PROCESS_FILES_DIR.mkdir(exist_ok=True)

    # Get next batch
    to_process = get_unprocessed_files(args.batch_size)

    if not to_process:
        print("All files have been processed!")
        return

    print(f"\nWill process {len(to_process)} files:")
    for f in to_process:
        print(f"  {f.name}")

    if args.dry_run:
        return

    # Process batch
    try:
        for i, file_path in enumerate(to_process):
            print(f"\n--- File {i+1}/{len(to_process)} ---")
            process_single_file(file_path, args.num_paragraphs,
                                args.min_words, args.max_words,
                                model=args.model)
    except KeyboardInterrupt:
        print("\n\nInterrupted. Progress saved for completed files.")
        # Clean up any .tmp file from the current file
        for tmp in PROCESS_FILES_DIR.glob("*.tmp"):
            print(f"  Removing incomplete: {tmp.name}")
            tmp.unlink()

    # Summary
    processed = get_processed_stems()
    total = len(get_all_input_files())
    print(f"\n=== Summary ===")
    print(f"Processed so far: {len(processed)}/{total}")
    print(f"Remaining: {total - len(processed)}")


if __name__ == "__main__":
    main()

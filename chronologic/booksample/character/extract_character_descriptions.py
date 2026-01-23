"""
extract_character_descriptions.py

Extracts character descriptions from novels using a local LLM (gpt-oss:20b via Ollama).

This script:
1. Reads a novel text file (HathiTrust format)
2. Skips the first N lines (default 25) to avoid title page/TOC
3. Chunks text at sentence boundaries (~700 words per chunk)
4. Sends each chunk to the LLM to identify explicit character descriptions
5. Aggregates descriptions by character (merging name variants)
6. Outputs a .jsonl file with one line per character

Output format:
{"character_names": ["Elsie", "Elsie Mitchell"], "descriptions": [(3, "description text..."), (12, "more text...")]}
"""

import json
import os
import sys
import argparse
import requests
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

# Download nltk data if needed
import nltk
try:
    from nltk import sent_tokenize
except LookupError:
    nltk.download('punkt', quiet=True)
    from nltk import sent_tokenize

# Constants
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gpt-oss:20b"
TEMPERATURE = 0.3
NUM_PREDICT = 1250
TIMEOUT = 120
MAX_WORDS_PER_CHUNK = 700
DEFAULT_SKIP_LINES = 25

DESCRIPTION_EXTRACTING_PROMPT = """You are filtering text from a novel to find moments when named characters are explicitly described.

If you find a good example of explicit description, return only the character and extracted description, in json format.

For example, given this passage:
"Across the table sat a silent child with strange, ice-blue eyes. Later in the day, Frank learned that her name was Elsie—Elsie Mitchell."
{{"character_name": "Elsie Mitchell", "description": "A silent child with strange, ice-blue eyes."}}

If there is no good example of explicit description, return an empty json object like this:
{{}}

Be choosy. Most passages of fiction don't contain explicit character description. 

For instance, passage:
"The wedding took place at the next Nachtmaal, Gideon managing, by means of some pretext, to avoid being present. The priest who officiated was a corpulent conservative man. Soon afterwards old Tyardt cut off a portion of the farm and handed it over to his married son, who thereupon built a homestead and began farming on his own account."
reply:
{{}}

The passage implies things about Gideon and Tyardt but does not explicitly describe them. The priest is described explicitly, but he is not a named character. So nothing is returned.

passage:{passage}
reply:
"""


def read_novel_text(file_path: str, skip_lines: int = DEFAULT_SKIP_LINES) -> str:
    """
    Read novel text file, skipping first N lines to avoid headers/TOC.

    Args:
        file_path: Path to input text file
        skip_lines: Number of lines to skip at start (default 25)

    Returns:
        Text content as string with skipped lines removed

    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If file encoding is invalid
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Skip first N lines, join remainder
    remaining_text = ''.join(lines[skip_lines:])
    return remaining_text


def chunk_text_at_sentences(text: str, max_words: int = MAX_WORDS_PER_CHUNK) -> List[str]:
    """
    Divide text into chunks at sentence boundaries, up to max_words per chunk.

    Uses nltk.sent_tokenize for sentence splitting. Ensures chunks don't exceed
    max_words unless a single sentence is longer (in which case include it anyway
    to avoid losing content).

    Args:
        text: Input text to chunk
        max_words: Maximum words per chunk (default 700)

    Returns:
        List of text chunks
    """
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_word_count = 0

    for sentence in sentences:
        word_count = len(sentence.split())

        # Add sentence if room OR if chunk is empty (prevents skipping long sentences)
        if current_word_count + word_count <= max_words or current_word_count == 0:
            current_chunk.append(sentence)
            current_word_count += word_count
        else:
            # Finalize current chunk, start new one
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_word_count = word_count

    # Don't forget final chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def call_ollama_model(
    prompt: str,
    model: str = MODEL,
    temperature: float = TEMPERATURE,
    num_predict: int = NUM_PREDICT,
    timeout: int = TIMEOUT,
    debug: bool = False
) -> Dict[str, Any]:
    """
    Make a request to the Ollama API and handle common error cases.

    This function handles all HTTP-level and connection-level errors, returning
    a standardized dict with either the model's response text or error information.

    Args:
        prompt: The complete prompt to send to the model
        model: Model identifier (default: MODEL constant)
        temperature: Sampling temperature (0.0-1.0)
        num_predict: Maximum tokens to generate
        timeout: Request timeout in seconds
        debug: If True, print diagnostic information

    Returns:
        dict with one of these structures:
        - {"status": "success", "response": str} on success
        - {"status": "error", "reason": str} on any error

    This function is designed to be reused for different prompting tasks.
    Response parsing should be done by task-specific functions.
    """

    if debug:
        print(f"\n{'='*60}")
        print(f"PROMPT LENGTH: {len(prompt)} chars")
        print(f"PROMPT PREVIEW:\n{prompt[:500]}...")
        print(f"{'='*60}")

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": num_predict,
                }
            },
            timeout=timeout
        )

        if debug:
            print(f"HTTP STATUS: {response.status_code}")
            print(f"RAW RESPONSE: {response.text[:1000]}")

        # HTTP error handling
        if response.status_code != 200:
            return {
                "status": "error",
                "reason": f"HTTP {response.status_code}: {response.text[:200]}"
            }

        # Parse JSON response
        resp_json = response.json()

        if debug:
            print(f"RESPONSE KEYS: {resp_json.keys()}")
            for k, v in resp_json.items():
                print(f"  {k}: {str(v)[:100]}")

        # Check for Ollama-specific errors
        if "error" in resp_json:
            return {"status": "error", "reason": f"Ollama error: {resp_json['error']}"}

        # Extract response text
        result_text = resp_json.get("response", "").strip()

        # Check for empty response
        if not result_text:
            return {"status": "error", "reason": "Empty response from model"}

        return {"status": "success", "response": result_text}

    except requests.exceptions.ConnectionError:
        return {"status": "error", "reason": "Connection refused - is ollama running?"}
    except requests.exceptions.Timeout:
        return {"status": "error", "reason": "Request timed out"}
    except json.JSONDecodeError as e:
        return {"status": "error", "reason": f"Invalid JSON response: {e}"}
    except Exception as e:
        return {"status": "error", "reason": f"{type(e).__name__}: {e}"}


def parse_character_description(response_text: str, debug: bool = False) -> Dict[str, Any]:
    """
    Parse LLM response to extract character description JSON.

    Handles various response formats:
    1. Clean JSON: {"character_name": "...", "description": "..."}
    2. Empty JSON: {} or {{}}
    3. JSON with surrounding text: "Here's what I found: {...}"
    4. Malformed JSON with escaped braces: {{...}}

    Args:
        response_text: Raw LLM response
        debug: Print parsing diagnostics

    Returns:
        {"status": "success", "character_name": str, "description": str} or
        {"status": "empty"} or
        {"status": "error", "reason": str}
    """

    # Clean up double-brace artifacts from prompt examples
    cleaned = response_text.replace('{{', '{').replace('}}', '}')

    # Find JSON-like structures
    json_pattern = r'\{[^{}]*\}'
    matches = re.findall(json_pattern, cleaned)

    if not matches:
        if debug:
            print(f"No JSON structure found in: {response_text[:100]}")
        return {"status": "error", "reason": f"No JSON found in response: {response_text[:100]}"}

    # Try parsing each match
    for match in matches:
        try:
            parsed = json.loads(match)

            # Empty object case
            if not parsed or len(parsed) == 0:
                return {"status": "empty"}

            # Valid character description
            if "character_name" in parsed and "description" in parsed:
                return {
                    "status": "success",
                    "character_name": parsed["character_name"],
                    "description": parsed["description"]
                }

            # Unexpected keys but valid JSON
            if debug:
                print(f"Valid JSON but unexpected keys: {list(parsed.keys())}")

        except json.JSONDecodeError:
            continue

    # All parsing attempts failed
    return {"status": "error", "reason": f"Could not parse JSON from: {response_text[:100]}"}


def extract_character_description(passage: str, chunk_index: int, model: str = MODEL,
                                   debug: bool = False) -> Dict[str, Any]:
    """
    Extract character description from a passage using LLM.

    Args:
        passage: Text passage to analyze
        chunk_index: Index of this chunk (for tracking)
        model: Model to use for extraction
        debug: Print debug info

    Returns:
        {"status": "success", "chunk_index": int, "character_name": str, "description": str} or
        {"status": "empty", "chunk_index": int} or
        {"status": "error", "chunk_index": int, "reason": str}
    """

    # Format prompt
    prompt = DESCRIPTION_EXTRACTING_PROMPT.format(passage=passage)

    # Call LLM
    result = call_ollama_model(prompt, model=model, debug=debug)

    if result["status"] == "error":
        return {
            "status": "error",
            "chunk_index": chunk_index,
            "reason": result["reason"]
        }

    # Parse response
    parsed = parse_character_description(result["response"], debug=debug)

    # Add chunk index to result
    parsed["chunk_index"] = chunk_index
    return parsed


def merge_character_names(name_groups: List[List[str]]) -> List[List[str]]:
    """
    Merge character name groups using case-insensitive substring matching.

    Algorithm:
    1. Sort name groups by shortest name in each group (ascending)
    2. For each group, check if any name is substring of any name in later groups
    3. If match found, merge groups
    4. Repeat until no more merges possible

    Example:
        Input: [["Elsie Mitchell"], ["Elsie"], ["Miss Elsie"]]
        Output: [["Elsie", "Elsie Mitchell", "Miss Elsie"]]

    Args:
        name_groups: List of character name lists

    Returns:
        Merged list of character name lists
    """

    if not name_groups:
        return []

    # Sort by length of shortest name in group
    sorted_groups = sorted(name_groups, key=lambda g: min(len(n) for n in g))

    merged = True
    while merged:
        merged = False
        new_groups = []
        skip_indices = set()

        for i, group_i in enumerate(sorted_groups):
            if i in skip_indices:
                continue

            # Check if this group should merge with any later group
            merged_with_later = False

            for j in range(i + 1, len(sorted_groups)):
                if j in skip_indices:
                    continue

                group_j = sorted_groups[j]

                # Check if any name in group_i is substring of any name in group_j
                # (case-insensitive)
                should_merge = False
                for name_i in group_i:
                    for name_j in group_j:
                        if name_i.lower() in name_j.lower() or name_j.lower() in name_i.lower():
                            should_merge = True
                            break
                    if should_merge:
                        break

                if should_merge:
                    # Merge groups
                    combined = list(set(group_i + group_j))  # Remove duplicates
                    new_groups.append(combined)
                    skip_indices.add(j)
                    merged_with_later = True
                    merged = True
                    break

            if not merged_with_later:
                new_groups.append(group_i)

        sorted_groups = new_groups
        # Re-sort after merging
        sorted_groups = sorted(sorted_groups, key=lambda g: min(len(n) for n in g))

    return sorted_groups


def aggregate_character_descriptions(
    raw_descriptions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Aggregate character descriptions by character, merging variant names.

    Args:
        raw_descriptions: List of dicts with "character_name", "description", "chunk_index"

    Returns:
        List of dicts with:
        {
            "character_names": List[str],
            "descriptions": List[Tuple[int, str]]  # (chunk_index, description)
        }
    """

    if not raw_descriptions:
        return []

    # Group by exact character name first
    exact_groups: Dict[str, List[Tuple[int, str]]] = {}

    for desc in raw_descriptions:
        name = desc["character_name"]
        chunk_idx = desc["chunk_index"]
        description = desc["description"]

        if name not in exact_groups:
            exact_groups[name] = []
        exact_groups[name].append((chunk_idx, description))

    # Create name groups (each starts as single-name list)
    name_groups = [[name] for name in exact_groups.keys()]

    # Merge related names
    merged_groups = merge_character_names(name_groups)

    # Build final aggregated results
    results = []
    for name_group in merged_groups:
        # Collect all descriptions for any name in this group
        all_descriptions = []
        for name in name_group:
            if name in exact_groups:
                all_descriptions.extend(exact_groups[name])

        # Sort descriptions by chunk index
        all_descriptions.sort(key=lambda x: x[0])

        results.append({
            "character_names": sorted(name_group),  # Sort for consistency
            "descriptions": all_descriptions
        })

    # Sort results by first appearance (earliest chunk_index)
    results.sort(key=lambda x: x["descriptions"][0][0] if x["descriptions"] else float('inf'))

    return results


def process_novel(
    input_path: str,
    output_path: str,
    skip_lines: int = DEFAULT_SKIP_LINES,
    start_chunk: int = 0,
    max_chunks: Optional[int] = None,
    model: str = MODEL,
    debug: bool = False
) -> List[Dict[str, Any]]:
    """
    Process a novel to extract character descriptions.

    Args:
        input_path: Path to input .txt file
        output_path: Path to output .jsonl file
        skip_lines: Lines to skip at file start
        start_chunk: Resume from this chunk (0-indexed)
        max_chunks: Process only this many chunks (None for all)
        model: Model to use for extraction
        debug: Print debug info

    Returns:
        List of aggregated character descriptions
    """

    print(f"Reading novel from: {input_path}")
    print(f"Skipping first {skip_lines} lines")

    # Read and chunk text
    text = read_novel_text(input_path, skip_lines=skip_lines)

    if not text.strip():
        print("Warning: Input file is empty after skipping header lines", file=sys.stderr)
        # Continue with empty chunks, will produce empty output

    chunks = chunk_text_at_sentences(text, max_words=MAX_WORDS_PER_CHUNK)

    print(f"Created {len(chunks)} chunks (~{MAX_WORDS_PER_CHUNK} words each)")

    # Limit chunks if specified
    if max_chunks is not None:
        chunks = chunks[:max_chunks]
        print(f"Limited to first {max_chunks} chunks for testing")

    # Resume logic
    raw_descriptions = []
    if start_chunk > 0:
        print(f"Resuming from chunk {start_chunk}...")

    # Process chunks
    print(f"\nProcessing chunks {start_chunk} to {len(chunks)-1}...\n")

    for i in range(start_chunk, len(chunks)):
        chunk = chunks[i]
        chunk_preview = chunk[:60].replace('\n', ' ')
        print(f"[{i+1}/{len(chunks)}] {chunk_preview}...", end=" ")

        # Debug only on first chunk
        show_debug = debug and i == start_chunk

        # Extract description
        result = extract_character_description(chunk, chunk_index=i, model=model, debug=show_debug)

        if result["status"] == "success":
            char_name = result["character_name"]
            desc_preview = result["description"][:50].replace('\n', ' ')
            print(f"✓ {char_name}: {desc_preview}...")
            raw_descriptions.append(result)

        elif result["status"] == "empty":
            print("○ (no description)")

        else:  # error
            error_msg = result.get("reason", "Unknown error")[:50]
            print(f"✗ {error_msg}")

    # Aggregate descriptions by character
    print("\nAggregating descriptions by character...")
    aggregated = aggregate_character_descriptions(raw_descriptions)

    # Create output directory if needed
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created output directory: {output_dir}")

    # Write output
    print(f"Writing {len(aggregated)} characters to {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        for char_entry in aggregated:
            f.write(json.dumps(char_entry, ensure_ascii=False) + '\n')

    # Print summary
    print(f"\n=== Summary ===")
    print(f"Chunks processed: {len(chunks) - start_chunk}")
    print(f"Descriptions found: {len(raw_descriptions)}")
    print(f"Unique characters: {len(aggregated)}")
    print(f"Output: {output_path}")

    return aggregated


def main():
    """Main execution function with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Extract character descriptions from novels using LLM (gpt-oss:20b via Ollama)"
    )

    parser.add_argument(
        "input_file",
        type=str,
        help="Path to input .txt file (HathiTrust format)"
    )

    parser.add_argument(
        "output_file",
        type=str,
        help="Path to output .jsonl file"
    )

    parser.add_argument(
        "--start-chunk",
        type=int,
        default=0,
        help="Resume from chunk N (0-indexed, default: 0)"
    )

    parser.add_argument(
        "--max-chunks",
        type=int,
        default=None,
        help="Process only N chunks for testing (default: all)"
    )

    parser.add_argument(
        "--skip-lines",
        type=int,
        default=DEFAULT_SKIP_LINES,
        help=f"Lines to skip at file start (default: {DEFAULT_SKIP_LINES})"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print debug info for first chunk"
    )

    parser.add_argument(
        "--mistral",
        action="store_true",
        help="Use mistral-small:24b instead of gpt-oss:20b"
    )

    args = parser.parse_args()

    # Validate input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)

    # Determine model
    if args.mistral:
        model = "mistral-small:24b"
    else:
        model = MODEL
    print(f"Using model: {model}")

    # Process the novel
    try:
        process_novel(
            input_path=args.input_file,
            output_path=args.output_file,
            skip_lines=args.skip_lines,
            start_chunk=args.start_chunk,
            max_chunks=args.max_chunks,
            model=model,
            debug=args.debug
        )
    except UnicodeDecodeError as e:
        print(f"Error: File encoding problem: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Partial results may have been written.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

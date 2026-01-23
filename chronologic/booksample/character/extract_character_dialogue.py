"""
extract_character_dialogue.py

Extracts character dialogue from novels using a local LLM (gpt-oss:20b via Ollama).

This is the second script in the character modeling pipeline, using character names
identified by extract_character_descriptions.py.

This script:
1. Loads character names from JSONL file (output of extract_character_descriptions.py)
2. Reads novel text file (HathiTrust format)
3. Skips first N lines (default 25) to avoid title page/TOC
4. Chunks text at sentence boundaries (~700 words per chunk)
5. Sends each chunk + character list to LLM to identify substantial dialogue
6. Aggregates dialogue passages by character (matching against name variants)
7. Outputs a .jsonl file with one line per character

Output format:
{"character_names": ["Elsie", "Miss Elsie"], "character_dialogue": [{"chunk": 8, "character": "Elsie", "dialogue": "...", "summary": "..."}]}
"""

import json
import os
import sys
import argparse
import requests
from typing import Dict, Any, List, Optional

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
NUM_PREDICT = 1500  # Higher than description task (1000) to avoid truncation
TIMEOUT = 120
MAX_WORDS_PER_CHUNK = 700
DEFAULT_SKIP_LINES = 25

DIALOGUE_EXTRACTION_PROMPT = """You are identifying fictional passages that contain substantial dialogue from one of a group of characters. If dialogue from one of those characters is found, you extract it (for that character only), and return json with three parts: the character name, a single passage of dialogue from the character, and a one-sentence summary of the whole scene.

For instance,
character_list: [["Elsie", "Miss Elsie"], ["Stephanus"]]
passage: "When Stephanus returned home after the encounter with Gideon he found the blind child waiting for him under a large mulberry tree. Here Elsie would sit for hours when her father was away.

'Hello, my child,' he said.

'Father, why are you so late tonight?' Elsie asked, 'and where 66 BLIND ELSIE is your horse?' 

'Late,' he repeated, musingly- 'yes, it is late.'

The child's intuitive sense prevented her from questioning further. 'Come with me, father.'"

reply:
{{"character": "Elsie", "dialogue": "Father, why are you so late tonight? And where is your horse?", "summary": "Stephanus returns home and finds Elsie, who questions him."}}

Note that interruptions in Elsie's dialogue ('Elsie asked' and an all-caps page header) have been silently removed. Note also that only a single passage of dialogue from a single character is provided; the transcription stops when Elsie stops speaking. 

Finally, notice that the summary sentence covers the whole scene in a general way and does not focus on Elsie's dialogue.

If there is no dialogue, or there is dialogue but not from any of the character names mentioned, return an empty json object:
{{}}

character_list: {characters}
passage: {passage}
reply:
"""


# ============================================================================
# COPIED FUNCTIONS from extract_character_descriptions.py
# ============================================================================

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


# ============================================================================
# NEW FUNCTIONS for dialogue extraction
# ============================================================================

def load_character_names(character_file: str) -> List[List[str]]:
    """
    Load character names from JSONL file and format for LLM prompt.

    Args:
        character_file: Path to .jsonl file from extract_character_descriptions.py

    Returns:
        List of character name lists, e.g. [["Elsie", "Miss Elsie"], ["Stephanus"]]

    Raises:
        FileNotFoundError: If character file doesn't exist
        json.JSONDecodeError: If JSONL is malformed
    """
    character_groups = []

    with open(character_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:  # Skip empty lines
                continue

            char_data = json.loads(line)

            # Extract character_names list
            if "character_names" in char_data:
                names = char_data["character_names"]
                if names:  # Only add non-empty lists
                    character_groups.append(names)

    return character_groups


def parse_dialogue_response(response_text: str, debug: bool = False) -> Dict[str, Any]:
    """
    Parse LLM response to extract dialogue JSON.

    Handles various response formats:
    1. Clean JSON: {"character": "...", "dialogue": "...", "summary": "..."}
    2. Empty JSON: {} or {{}}
    3. JSON with surrounding text
    4. Malformed JSON with escaped braces

    Uses start/end brace extraction (more robust than regex for multi-field responses).

    Args:
        response_text: Raw LLM response
        debug: Print parsing diagnostics

    Returns:
        {"status": "success", "character": str, "dialogue": str, "summary": str} or
        {"status": "empty"} or
        {"status": "error", "reason": str}
    """

    # Clean up double-brace artifacts
    cleaned = response_text.replace('{{', '{').replace('}}', '}')

    # Use robust extraction (pattern from make_training_data_motive.py)
    start_idx = cleaned.find('{')
    end_idx = cleaned.rfind('}')

    if start_idx == -1 or end_idx == -1:
        if debug:
            print(f"No JSON structure found in: {response_text[:100]}")
        return {"status": "error", "reason": f"No JSON found: {response_text[:100]}"}

    json_str = cleaned[start_idx:end_idx + 1]

    try:
        parsed = json.loads(json_str)

        # Empty object case
        if not parsed or len(parsed) == 0:
            return {"status": "empty"}

        # Valid dialogue extraction (all 3 fields required)
        if "character" in parsed and "dialogue" in parsed and "summary" in parsed:
            return {
                "status": "success",
                "character": parsed["character"],
                "dialogue": parsed["dialogue"],
                "summary": parsed["summary"]
            }

        # Partial response (missing fields)
        if debug:
            print(f"Incomplete JSON - keys found: {list(parsed.keys())}")
        return {"status": "error", "reason": f"Missing required fields: {list(parsed.keys())}"}

    except json.JSONDecodeError as e:
        # Try cleanup
        try:
            json_str = json_str.replace('\n', ' ').replace('\r', ' ')
            parsed = json.loads(json_str)

            if not parsed:
                return {"status": "empty"}

            if "character" in parsed and "dialogue" in parsed and "summary" in parsed:
                return {
                    "status": "success",
                    "character": parsed["character"],
                    "dialogue": parsed["dialogue"],
                    "summary": parsed["summary"]
                }
            else:
                return {"status": "error", "reason": "Missing required fields after cleanup"}

        except json.JSONDecodeError:
            if debug:
                print(f"JSON parse error: {e}")
            return {"status": "error", "reason": f"JSON parse failed: {response_text[:100]}"}


def extract_dialogue_from_chunk(
    passage: str,
    characters: List[List[str]],
    chunk_index: int,
    model: str = MODEL,
    debug: bool = False
) -> Dict[str, Any]:
    """
    Extract dialogue from a single chunk for one character.

    Args:
        passage: Text chunk to analyze
        characters: Character name groups [["Elsie", "Miss Elsie"], ["Stephanus"]]
        chunk_index: Index of this chunk (for tracking)
        model: Model to use for extraction
        debug: Print debug info

    Returns:
        {"status": "success", "chunk_index": int, "character": str,
         "dialogue": str, "summary": str, "passage": str} or
        {"status": "empty", "chunk_index": int} or
        {"status": "error", "chunk_index": int, "reason": str}
    """

    # Format prompt
    prompt = DIALOGUE_EXTRACTION_PROMPT.format(
        characters=json.dumps(characters),  # Converts to JSON string
        passage=passage
    )

    # Call LLM with num_predict=1500 (higher than description task)
    result = call_ollama_model(
        prompt,
        model=model,
        num_predict=NUM_PREDICT,
        debug=debug
    )

    if result["status"] == "error":
        return {
            "status": "error",
            "chunk_index": chunk_index,
            "reason": result["reason"]
        }

    # Parse response
    parsed = parse_dialogue_response(result["response"], debug=debug)

    # Add chunk index and original passage
    parsed["chunk_index"] = chunk_index
    parsed["passage"] = passage
    return parsed


def aggregate_dialogue_by_character(
    raw_dialogue: List[Dict[str, Any]],
    character_groups: List[List[str]]
) -> List[Dict[str, Any]]:
    """
    Aggregate dialogue passages by character.

    Unlike description aggregation, we DON'T need to merge character names
    (already done in first script). Instead, we match extracted dialogue
    against known character groups.

    Args:
        raw_dialogue: List of dicts with "character", "dialogue", "summary", "chunk_index", "passage"
        character_groups: Original character name groups from JSONL

    Returns:
        List of dicts:
        {
            "character_names": List[str],  # Original name group
            "character_dialogue": [
                {"chunk": int, "character": str, "dialogue": str, "summary": str, "passage": str},
                ...
            ]
        }
    """

    if not raw_dialogue:
        return []

    # Create mapping: character name (any variant) -> canonical group
    name_to_group = {}
    for group in character_groups:
        for name in group:
            name_to_group[name.lower()] = group

    # Group dialogue by canonical character group
    dialogue_by_group = {}

    for dialogue_entry in raw_dialogue:
        extracted_name = dialogue_entry["character"]
        chunk_idx = dialogue_entry["chunk_index"]

        # Find matching character group (case-insensitive)
        matched_group = None
        for name_variant, group in name_to_group.items():
            if extracted_name.lower() == name_variant or \
               extracted_name.lower() in name_variant or \
               name_variant in extracted_name.lower():
                matched_group = tuple(sorted(group))  # Use as dict key
                break

        # If no match found, create singleton group (edge case)
        if matched_group is None:
            matched_group = (extracted_name,)

        # Add to group
        if matched_group not in dialogue_by_group:
            dialogue_by_group[matched_group] = []

        dialogue_by_group[matched_group].append({
            "chunk": chunk_idx,
            "character": extracted_name,
            "dialogue": dialogue_entry["dialogue"],
            "summary": dialogue_entry["summary"],
            "passage": dialogue_entry["passage"]
        })

    # Build final results
    results = []
    for group_tuple, dialogues in dialogue_by_group.items():
        # Sort dialogues by chunk index (preserves narrative order)
        dialogues.sort(key=lambda x: x["chunk"])

        results.append({
            "character_names": list(group_tuple),
            "character_dialogue": dialogues
        })

    # Sort results by first appearance
    results.sort(key=lambda x: x["character_dialogue"][0]["chunk"] if x["character_dialogue"] else float('inf'))

    return results


def process_novel_dialogue(
    character_file: str,
    text_file: str,
    output_file: str,
    skip_lines: int = DEFAULT_SKIP_LINES,
    start_chunk: int = 0,
    max_chunks: Optional[int] = None,
    model: str = MODEL,
    debug: bool = False
) -> List[Dict[str, Any]]:
    """
    Process a novel to extract character dialogue.

    Args:
        character_file: Path to character .jsonl file
        text_file: Path to novel .txt file
        output_file: Path to output .jsonl file
        skip_lines: Lines to skip at file start
        start_chunk: Resume from this chunk (0-indexed)
        max_chunks: Process only this many chunks (None for all)
        model: Model to use for extraction
        debug: Print debug info

    Returns:
        List of aggregated dialogue by character
    """

    # Validate files exist
    if not os.path.exists(character_file):
        raise FileNotFoundError(f"Character file not found: {character_file}")

    if not os.path.exists(text_file):
        raise FileNotFoundError(f"Text file not found: {text_file}")

    # Load characters
    print(f"Loading characters from: {character_file}")
    try:
        character_groups = load_character_names(character_file)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSONL in character file: {e}")

    if not character_groups:
        print("Warning: No characters found in character file", file=sys.stderr)
        # Continue with empty list - will produce empty output

    print(f"Loaded {len(character_groups)} character groups")

    # Read and chunk text
    print(f"Reading novel from: {text_file}")
    print(f"Skipping first {skip_lines} lines")

    text = read_novel_text(text_file, skip_lines=skip_lines)

    if not text.strip():
        print("Warning: Input file is empty after skipping header lines", file=sys.stderr)

    chunks = chunk_text_at_sentences(text, max_words=MAX_WORDS_PER_CHUNK)
    print(f"Created {len(chunks)} chunks (~{MAX_WORDS_PER_CHUNK} words each)")

    # Limit chunks if specified
    if max_chunks is not None:
        chunks = chunks[:max_chunks]
        print(f"Limited to first {max_chunks} chunks for testing")

    # Resume logic
    raw_dialogue = []
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

        # Extract dialogue
        result = extract_dialogue_from_chunk(
            chunk,
            characters=character_groups,
            chunk_index=i,
            model=model,
            debug=show_debug
        )

        if result["status"] == "success":
            char = result["character"]
            dialogue_preview = result["dialogue"][:40].replace('\n', ' ')
            print(f"✓ {char}: {dialogue_preview}...")
            raw_dialogue.append(result)

        elif result["status"] == "empty":
            print("○ (no dialogue)")

        else:  # error
            error_msg = result.get("reason", "Unknown error")[:50]
            print(f"✗ {error_msg}")

    # Aggregate dialogue by character
    print("\nAggregating dialogue by character...")
    aggregated = aggregate_dialogue_by_character(raw_dialogue, character_groups)

    # Create output directory if needed
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created output directory: {output_dir}")

    # Write output
    print(f"Writing {len(aggregated)} characters to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        for char_entry in aggregated:
            f.write(json.dumps(char_entry, ensure_ascii=False) + '\n')

    # Print summary
    print(f"\n=== Summary ===")
    print(f"Chunks processed: {len(chunks) - start_chunk}")
    print(f"Dialogue passages found: {len(raw_dialogue)}")
    print(f"Characters with dialogue: {len(aggregated)}")
    print(f"Output: {output_file}")

    return aggregated


def main():
    """Main execution function with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Extract character dialogue from novels using LLM (gpt-oss:20b via Ollama)"
    )

    parser.add_argument(
        "character_file",
        type=str,
        help="Path to character .jsonl file (from extract_character_descriptions.py)"
    )

    parser.add_argument(
        "text_file",
        type=str,
        help="Path to novel .txt file (HathiTrust format)"
    )

    parser.add_argument(
        "output_file",
        type=str,
        help="Path to output .jsonl file for dialogue"
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

    # Determine model
    if args.mistral:
        model = "mistral-small:24b"
    else:
        model = MODEL
    print(f"Using model: {model}")

    # Process the novel
    try:
        process_novel_dialogue(
            character_file=args.character_file,
            text_file=args.text_file,
            output_file=args.output_file,
            skip_lines=args.skip_lines,
            start_chunk=args.start_chunk,
            max_chunks=args.max_chunks,
            model=model,
            debug=args.debug
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
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

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
import re
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple, Optional

# Download nltk data if needed
import nltk
try:
    from nltk import sent_tokenize
except LookupError:
    nltk.download('punkt', quiet=True)
    from nltk import sent_tokenize

# Reuse the OpenRouter client shared by the modelasjudge and summary pipelines
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "modelasjudge"))
from openrouter_client import make_openrouter_client, call_openrouter_chat

# Constants
OPENROUTER_MODEL = "google/gemini-3.5-flash-lite"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gpt-oss:20b"
MODEL = OPENROUTER_MODEL  # default backend is OpenRouter
TEMPERATURE = 0.3  # Ollama path only; call_openrouter_chat sends no temperature
REASONING_EFFORT = "low"  # Gemini Flash endpoints reject effort="none"
NUM_PREDICT = 1500  # Higher than description task (1000) to avoid truncation
TIMEOUT = 120
MAX_WORDS_PER_CHUNK = 700
DEFAULT_SKIP_LINES = 25

# Structured-output schema. Under strict:true every declared property is required,
# so "nothing found" can no longer be signalled by an empty object -- hence "found".
DIALOGUE_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "character_dialogue",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "found": {"type": "boolean"},
                "character": {"type": "string"},
                "dialogue": {"type": "string"},
                "summary": {"type": "string"},
            },
            "required": ["found", "character", "dialogue", "summary"],
            "additionalProperties": False,
        },
    },
}

DIALOGUE_EXTRACTION_PROMPT = """You are identifying fictional passages that contain substantial dialogue from one of a group of characters. If dialogue from one of those characters is found, you extract it (for that character only), and return json with three parts: the character name, a single passage of dialogue from the character, and a one-sentence summary of the whole scene.

For instance,
character_list: [["Elsie", "Miss Elsie"], ["Stephanus"]]
passage: "When Stephanus returned home after the encounter with Gideon he found the blind child waiting for him under a large mulberry tree. Here Elsie would sit for hours when her father was away.

'Hello, my child,' he said.

'Father, why are you so late tonight?' Elsie asked, 'and where 66 BLIND ELSIE is your horse?' 

'Late,' he repeated, musingly- 'yes, it is late.'

The child's intuitive sense prevented her from questioning further. 'Come with me, father.'"

reply:
{{"found": true, "character": "Elsie", "dialogue": "Father, why are you so late tonight? And where is your horse?", "summary": "Stephanus returns home and finds Elsie, who questions him."}}

Note that interruptions in Elsie's dialogue ('Elsie asked' and an all-caps page header) have been silently removed. Note also that only a single passage of dialogue from a single character is provided; the transcription stops when Elsie stops speaking. 

Finally, notice that the summary sentence covers the whole scene in a general way and does not focus on Elsie's dialogue.

If there is no dialogue, or there is dialogue but not from any of the character names mentioned, set "found" to false and leave the other fields empty:
{{"found": false, "character": "", "dialogue": "", "summary": ""}}

character_list: {characters}
passage: {passage}
reply:
"""


# ============================================================================
# COPIED FUNCTIONS from extract_character_descriptions.py
# ============================================================================

def clean_ocr_text(text: str) -> str:
    """
    Light OCR repair for early-print scans, applied before sentence tokenization.

    Copied verbatim from connectors/make_cloze_questions.py:540 (commit 98e6eab).
    Keep the three copies in sync; connectors/tests/test_passage_building.py::TestCleanOcrText
    is the canonical test.

    The edgebooks texts are mostly reflowed already, so the dominant artifact is
    not hyphenation but short ALL-CAPS running heads and bare page numbers
    dropped into the middle of paragraphs, which both split real sentences and
    inject junk "sentences". Measured across the 92-volume corpus: running heads
    and page numbers occur 3-65 per 10,000 words; hyphenated line-break splits
    only 1-5 per 10,000 words.

    This is deliberately shallow. It will occasionally drop a legitimate short
    ALL-CAPS line (a shouted line of dialogue, a line of small-caps verse) and
    will occasionally merge a genuine hyphenated compound broken across lines.
    Both are far rarer than the artifacts being removed, and the interactive
    edit_passage step remains available as a backstop.

    Args:
        text: Raw text as read from the volume file

    Returns:
        Cleaned text, with paragraph breaks (blank lines) preserved
    """
    # Rejoin words split by a hyphen at a line ending
    text = re.sub(r'(\w)-[ \t]*\n[ \t]*(\w)', r'\1\2', text)

    kept_lines = []
    for line in text.split('\n'):
        stripped = line.strip()
        if stripped:
            # Bare page or section number (arabic or roman)
            if re.fullmatch(r'[\dIVXLC.,\-—\[\]() ]{1,12}', stripped):
                continue
            # Short ALL-CAPS line: a running head or chapter heading
            if (len(stripped) < 45 and stripped == stripped.upper()
                    and re.search(r'[A-Z]{3}', stripped)):
                continue
        kept_lines.append(line)
    text = '\n'.join(kept_lines)

    # Drop spaces the OCR inserted before punctuation
    text = re.sub(r'[ \t]+([,;:.!?])', r'\1', text)
    # Reflow paragraph interiors: a lone newline is a line wrap, not a break
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

    return re.sub(r'[ \t]{2,}', ' ', text)


def read_novel_text(file_path: str, skip_lines: int = DEFAULT_SKIP_LINES) -> str:
    """
    Read novel text file, skipping first N lines to avoid headers/TOC.

    Args:
        file_path: Path to input text file
        skip_lines: Number of lines to skip at start (default 25)

    Returns:
        Cleaned text: skipped lines removed, then clean_ocr_text applied to strip
        running heads and page numbers and repair hyphenated line breaks

    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If file encoding is invalid
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Skip first N lines, join remainder
    remaining_text = ''.join(lines[skip_lines:])
    return clean_ocr_text(remaining_text)


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
    model: str = OLLAMA_MODEL,
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


# ============================================================================
# BACKEND DISPATCH — keep byte-identical with extract_character_descriptions.py
# ============================================================================

_CLIENT = None


def get_client():
    """Return a cached OpenRouter client, creating it on first use."""
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = make_openrouter_client()
    return _CLIENT


def call_openrouter_model(prompt: str, model: str, max_tokens: int,
                          response_format: Optional[Dict[str, Any]] = None,
                          debug: bool = False) -> Dict[str, Any]:
    """
    Generate text via OpenRouter, in the status-dict contract this module expects.

    Wraps call_openrouter_chat, which raises after exhausting its own retries.

    Uses REASONING_EFFORT rather than the client's "none" default: Gemini Flash
    endpoints reject reasoning.effort="none" outright with "Reasoning is mandatory
    for this endpoint". Measured reasoning_tokens at "low" is 0 for
    gemini-3.5-flash-lite, so this costs nothing extra.
    """
    try:
        text = call_openrouter_chat(
            get_client(), model, prompt, max_tokens=max_tokens,
            response_format=response_format, debug=debug,
            reasoning_effort=REASONING_EFFORT
        )
        return {"status": "success", "response": (text or "").strip()}
    except Exception as e:
        return {"status": "error", "reason": f"{type(e).__name__}: {str(e)}"}


def call_extraction_model(prompt: str, model: str, use_ollama: bool,
                          response_format: Optional[Dict[str, Any]],
                          num_predict: int, debug: bool = False) -> Dict[str, Any]:
    """
    Route one extraction call to Ollama or OpenRouter.

    Args:
        prompt: The prompt to send
        model: Model identifier for whichever backend is selected
        use_ollama: Send to local Ollama instead of OpenRouter
        response_format: Structured-output spec, or None. Always None on the
            Ollama path and whenever --no-schema is set
        num_predict: Output token cap
        debug: Print debug information

    Returns:
        Dict with 'status' and either 'response' or 'reason'
    """
    if use_ollama:
        return call_ollama_model(prompt, model=model, num_predict=num_predict, debug=debug)
    return call_openrouter_model(prompt, model=model, max_tokens=num_predict,
                                 response_format=response_format, debug=debug)


def _dialogue_from_found(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """
    Interpret a structured-output response carrying an explicit "found" flag.

    Under strict:true a response can validate while carrying blank strings, so
    treat any blank required field as "empty" rather than emitting an entry with
    no speaker or no dialogue.
    """
    if not parsed.get("found"):
        return {"status": "empty"}

    character = (parsed.get("character") or "").strip()
    dialogue = (parsed.get("dialogue") or "").strip()
    summary = (parsed.get("summary") or "").strip()

    if not character or not dialogue:
        return {"status": "empty"}

    return {
        "status": "success",
        "character": character,
        "dialogue": dialogue,
        "summary": summary
    }


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

        # Structured-output form: "found" gates the result
        if "found" in parsed:
            return _dialogue_from_found(parsed)

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

            if "found" in parsed:
                return _dialogue_from_found(parsed)

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
    use_ollama: bool = False,
    use_schema: bool = True,
    debug: bool = False
) -> Dict[str, Any]:
    """
    Extract dialogue from a single chunk for one character.

    Args:
        passage: Text chunk to analyze
        characters: Character name groups [["Elsie", "Miss Elsie"], ["Stephanus"]]
        chunk_index: Index of this chunk (for tracking)
        model: Model to use for extraction
        use_ollama: Route to local Ollama instead of OpenRouter
        use_schema: Constrain the response with DIALOGUE_SCHEMA (OpenRouter only)
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

    # Call LLM with num_predict=1500 (higher than description task).
    # Ollama has no structured-output support, so it never gets a schema.
    response_format = DIALOGUE_SCHEMA if (use_schema and not use_ollama) else None
    result = call_extraction_model(
        prompt,
        model=model,
        use_ollama=use_ollama,
        response_format=response_format,
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


# ============================================================================
# PROGRESS SIDECAR — keep byte-identical with extract_character_descriptions.py
# ============================================================================

def progress_path(output_path: str) -> str:
    """
    Sidecar path for an output file: X_characters.jsonl -> X_characters.progress.jsonl.

    Derived rather than passed on the CLI, so resuming needs no extra flag.
    """
    base, ext = os.path.splitext(output_path)
    return f"{base}.progress{ext or '.jsonl'}"


def append_progress(path: str, record: Dict[str, Any]) -> None:
    """
    Append one record to the progress sidecar.

    Opened and closed per record so an abrupt kill loses at most one chunk.
    """
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')


def load_progress(path: str) -> Tuple[Optional[Dict[str, Any]], Set[int], List[Dict[str, Any]]]:
    """
    Read a progress sidecar written by an earlier run.

    Chunks recorded as "success" or "empty" count as done. Chunks recorded only
    as "error" are deliberately left out, so a run interrupted by a stretch of
    Ollama failures retries them instead of treating them as settled.

    Args:
        path: Path to the .progress.jsonl sidecar

    Returns:
        (header, done_indices, successes) - successes sorted by chunk_index.
        Returns (None, empty, empty) when no sidecar exists.
    """
    header: Optional[Dict[str, Any]] = None
    done: Set[int] = set()
    successes: List[Dict[str, Any]] = []

    if not os.path.exists(path):
        return header, done, successes

    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                # Truncated final line from a hard kill; ignore it
                continue

            if record.get("record") == "header":
                header = record
                continue

            index = record.get("chunk_index")
            if index is None:
                continue
            if record.get("status") in ("success", "empty"):
                done.add(index)
            if record.get("status") == "success":
                successes.append(record)

    successes.sort(key=lambda r: r["chunk_index"])
    return header, done, successes


def check_progress_header(header: Optional[Dict[str, Any]],
                          expected: Dict[str, Any], path: str) -> None:
    """
    Refuse to resume when the chunking has changed since the sidecar was written.

    Chunk indices only mean something relative to a fixed chunking, which depends
    on skip_lines, the source text and clean_ocr_text. If any of those moved, the
    stored indices point at different text and resuming would silently mix two
    different books' worth of chunk numbering.

    Args:
        header: Header record from load_progress, or None
        expected: Field values this run computed; compared key by key
        path: Sidecar path, for the error message

    Exits with status 1 on any mismatch.
    """
    if header is None:
        return

    for key, want in expected.items():
        got = header.get(key)
        if got != want:
            print(f"\nError: {path}", file=sys.stderr)
            print(f"  was written with {key}={got!r}, but this run has {key}={want!r}.",
                  file=sys.stderr)
            print("  Chunk numbering would not match, so resuming is unsafe.",
                  file=sys.stderr)
            print("  Re-run with --restart to discard that progress and start over.",
                  file=sys.stderr)
            sys.exit(1)


def process_novel_dialogue(
    character_file: str,
    text_file: str,
    output_file: str,
    skip_lines: int = DEFAULT_SKIP_LINES,
    start_chunk: int = 0,
    max_chunks: Optional[int] = None,
    model: str = MODEL,
    debug: bool = False,
    restart: bool = False,
    use_ollama: bool = False,
    use_schema: bool = True
) -> List[Dict[str, Any]]:
    """
    Process a novel to extract character dialogue.

    Args:
        character_file: Path to character .jsonl file
        text_file: Path to novel .txt file
        output_file: Path to output .jsonl file
        skip_lines: Lines to skip at file start
        start_chunk: Resume from this chunk (0-indexed)
        max_chunks: Stop after chunk N, i.e. process chunks 0..N-1 (None for all)
        model: Model to use for extraction
        debug: Print debug info
        restart: Discard any saved progress and extract from scratch
        use_ollama: Route to local Ollama instead of OpenRouter
        use_schema: Constrain responses with DIALOGUE_SCHEMA (OpenRouter only)

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

    # Total before any ceiling: this defines chunk numbering and completeness
    total_chunks = len(chunks)
    print(f"Created {total_chunks} chunks (~{MAX_WORDS_PER_CHUNK} words each)")

    # Limit chunks if specified
    if max_chunks is not None:
        chunks = chunks[:max_chunks]
        print(f"Ceiling: stopping after chunk {len(chunks) - 1}")

    # Create output directory if needed (the sidecar lands here too)
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created output directory: {output_dir}")

    # Resume logic
    prog_path = progress_path(output_file)
    if restart and os.path.exists(prog_path):
        os.remove(prog_path)
        print(f"--restart: discarded previous progress ({prog_path})")

    header, done, raw_dialogue = load_progress(prog_path)
    check_progress_header(
        header,
        {"skip_lines": skip_lines, "n_chunks": total_chunks,
         "n_character_groups": len(character_groups)},
        prog_path
    )
    # Model is recorded but deliberately kept out of the hard check above: swapping
    # models doesn't shift chunk boundaries, so the data stays valid - just mixed.
    if header is not None and header.get("model") not in (None, model):
        print(f"Warning: progress file was written with model={header['model']}, "
              f"this run uses {model}.")
        print("  Chunks already done keep their original model's output.")

    if header is None:
        append_progress(prog_path, {
            "record": "header",
            "source": text_file,
            "character_file": character_file,
            "skip_lines": skip_lines,
            "n_chunks": total_chunks,
            "n_character_groups": len(character_groups),
            "model": model
        })

    # Drop anything above the current ceiling, so lowering it on a later run
    # doesn't pull out-of-range chunks back into the aggregation
    raw_dialogue = [r for r in raw_dialogue if r["chunk_index"] < len(chunks)]

    already_done = len(done & set(range(len(chunks))))
    if already_done:
        print(f"Resuming: {already_done} of {len(chunks)} chunks already done")

    # Process chunks
    print(f"\nProcessing chunks {start_chunk} to {len(chunks)-1}...\n")

    interrupted = False
    first_processed = True
    try:
        for i in range(start_chunk, len(chunks)):
            if i in done:
                continue

            chunk = chunks[i]
            chunk_preview = chunk[:60].replace('\n', ' ')
            print(f"[{i+1}/{len(chunks)}] {chunk_preview}...", end=" ")

            # Debug only on the first chunk actually processed this run
            show_debug = debug and first_processed
            first_processed = False

            # Extract dialogue
            result = extract_dialogue_from_chunk(
                chunk,
                characters=character_groups,
                chunk_index=i,
                model=model,
                use_ollama=use_ollama,
                use_schema=use_schema,
                debug=show_debug
            )

            # Record before reacting, so a crash here still leaves a trace
            append_progress(prog_path, result)
            if result["status"] in ("success", "empty"):
                done.add(i)

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

    except KeyboardInterrupt:
        interrupted = True
        print("\n\nInterrupted. Aggregating the chunks processed so far...")

    # Keep chronological order even when a retried error chunk was filled in late
    raw_dialogue.sort(key=lambda r: r["chunk_index"])

    # Aggregate dialogue by character
    print("\nAggregating dialogue by character...")
    aggregated = aggregate_dialogue_by_character(raw_dialogue, character_groups)

    # Write output
    print(f"Writing {len(aggregated)} characters to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        for char_entry in aggregated:
            f.write(json.dumps(char_entry, ensure_ascii=False) + '\n')

    # The sidecar goes away only once every chunk in the book is accounted for.
    # Coverage, not "the loop ended": --start-chunk can reach the end with early
    # chunks never attempted, and the batch drivers rely on this file to tell
    # a partial extraction from a finished one.
    complete = set(range(total_chunks)) <= done
    if complete:
        os.remove(prog_path)
        print(f"All {total_chunks} chunks done; removed progress file")
    else:
        remaining = total_chunks - len(done & set(range(total_chunks)))
        print(f"Progress saved: {remaining} of {total_chunks} chunks still to do")
        print(f"  Re-run the same command to continue ({prog_path})")

    # Print summary
    print(f"\n=== Summary ===")
    print(f"Chunks done: {len(done & set(range(total_chunks)))}/{total_chunks}")
    print(f"Dialogue passages found: {len(raw_dialogue)}")
    print(f"Characters with dialogue: {len(aggregated)}")
    print(f"Output: {output_file}")
    if interrupted:
        print("Status: INTERRUPTED (output above covers completed chunks only)")

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
        help="Stop after chunk N: processes chunks 0 to N-1 (default: all)"
    )

    parser.add_argument(
        "--restart",
        action="store_true",
        help="Discard saved progress and extract from scratch"
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
        "--model",
        default=None,
        help=f"Model identifier (default: {OPENROUTER_MODEL}, or {OLLAMA_MODEL} with --ollama)"
    )

    parser.add_argument(
        "--ollama",
        action="store_true",
        help="Use local Ollama instead of OpenRouter (replaces the old --mistral)"
    )

    parser.add_argument(
        "--no-schema",
        action="store_true",
        help="Don't constrain the response with a JSON schema (OpenRouter only)"
    )

    args = parser.parse_args()

    # Determine backend and model
    model = args.model or (OLLAMA_MODEL if args.ollama else OPENROUTER_MODEL)
    backend = "Ollama" if args.ollama else "OpenRouter"
    use_schema = not args.no_schema and not args.ollama
    print(f"Using model: {model} via {backend}"
          f"{' with structured output' if use_schema else ''}")

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
            debug=args.debug,
            restart=args.restart,
            use_ollama=args.ollama,
            use_schema=use_schema
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
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

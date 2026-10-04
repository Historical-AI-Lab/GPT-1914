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
NUM_PREDICT = 1250
TIMEOUT = 120
MAX_WORDS_PER_CHUNK = 700

# Structured-output schema. Under strict:true every declared property is required,
# so "nothing found" can no longer be signalled by an empty object -- hence "found".
DESCRIPTION_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "character_description",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "found": {"type": "boolean"},
                "character_name": {"type": "string"},
                "description": {"type": "string"},
            },
            "required": ["found", "character_name", "description"],
            "additionalProperties": False,
        },
    },
}
DEFAULT_SKIP_LINES = 25

DESCRIPTION_EXTRACTING_PROMPT = """You are filtering text from a novel to find moments when named characters are explicitly described.

If you find a good example of explicit description, set "found" to true and return the character and extracted description, in json format.

For example, given this passage:
"Across the table sat a silent child with strange, ice-blue eyes. Later in the day, Frank learned that her name was Elsie—Elsie Mitchell."
{{"found": true, "character_name": "Elsie Mitchell", "description": "A silent child with strange, ice-blue eyes."}}

If there is no good example of explicit description, set "found" to false and leave the other fields empty:
{{"found": false, "character_name": "", "description": ""}}

Be choosy. Most passages of fiction don't contain explicit character description. 

For instance, passage:
"The wedding took place at the next Nachtmaal, Gideon managing, by means of some pretext, to avoid being present. The priest who officiated was a corpulent conservative man. Soon afterwards old Tyardt cut off a portion of the farm and handed it over to his married son, who thereupon built a homestead and began farming on his own account."
reply:
{{"found": false, "character_name": "", "description": ""}}

The passage implies things about Gideon and Tyardt but does not explicitly describe them. The priest is described explicitly, but he is not a named character. So nothing is returned.

passage:{passage}
reply:
"""


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
# BACKEND DISPATCH — keep byte-identical with extract_character_dialogue.py
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

            # Structured-output form: "found" gates the result. Under strict:true
            # a blank name/description is still valid JSON, so treat it as empty
            # rather than emitting a nameless character.
            if "found" in parsed:
                if not parsed["found"]:
                    return {"status": "empty"}
                name = (parsed.get("character_name") or "").strip()
                description = (parsed.get("description") or "").strip()
                if not name or not description:
                    return {"status": "empty"}
                return {
                    "status": "success",
                    "character_name": name,
                    "description": description
                }

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
                                   use_ollama: bool = False, use_schema: bool = True,
                                   debug: bool = False) -> Dict[str, Any]:
    """
    Extract character description from a passage using LLM.

    Args:
        passage: Text passage to analyze
        chunk_index: Index of this chunk (for tracking)
        model: Model to use for extraction
        use_ollama: Route to local Ollama instead of OpenRouter
        use_schema: Constrain the response with DESCRIPTION_SCHEMA (OpenRouter only)
        debug: Print debug info

    Returns:
        {"status": "success", "chunk_index": int, "character_name": str, "description": str} or
        {"status": "empty", "chunk_index": int} or
        {"status": "error", "chunk_index": int, "reason": str}
    """

    # Format prompt
    prompt = DESCRIPTION_EXTRACTING_PROMPT.format(passage=passage)

    # Call LLM. Ollama has no structured-output support, so it never gets a schema.
    response_format = DESCRIPTION_SCHEMA if (use_schema and not use_ollama) else None
    result = call_extraction_model(prompt, model=model, use_ollama=use_ollama,
                                   response_format=response_format,
                                   num_predict=NUM_PREDICT, debug=debug)

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


# ============================================================================
# PROGRESS SIDECAR — keep byte-identical with extract_character_dialogue.py
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


def process_novel(
    input_path: str,
    output_path: str,
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
    Process a novel to extract character descriptions.

    Args:
        input_path: Path to input .txt file
        output_path: Path to output .jsonl file
        skip_lines: Lines to skip at file start
        start_chunk: Resume from this chunk (0-indexed)
        max_chunks: Stop after chunk N, i.e. process chunks 0..N-1 (None for all)
        model: Model to use for extraction
        debug: Print debug info
        restart: Discard any saved progress and extract from scratch
        use_ollama: Route to local Ollama instead of OpenRouter
        use_schema: Constrain responses with DESCRIPTION_SCHEMA (OpenRouter only)

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

    # Total before any ceiling: this defines chunk numbering and completeness
    total_chunks = len(chunks)
    print(f"Created {total_chunks} chunks (~{MAX_WORDS_PER_CHUNK} words each)")

    # Limit chunks if specified
    if max_chunks is not None:
        chunks = chunks[:max_chunks]
        print(f"Ceiling: stopping after chunk {len(chunks) - 1}")

    # Create output directory if needed (the sidecar lands here too)
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created output directory: {output_dir}")

    # Resume logic
    prog_path = progress_path(output_path)
    if restart and os.path.exists(prog_path):
        os.remove(prog_path)
        print(f"--restart: discarded previous progress ({prog_path})")

    header, done, raw_descriptions = load_progress(prog_path)
    check_progress_header(
        header,
        {"skip_lines": skip_lines, "n_chunks": total_chunks},
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
            "source": input_path,
            "skip_lines": skip_lines,
            "n_chunks": total_chunks,
            "model": model
        })

    # Drop anything above the current ceiling, so lowering it on a later run
    # doesn't pull out-of-range chunks back into the aggregation
    raw_descriptions = [r for r in raw_descriptions if r["chunk_index"] < len(chunks)]

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

            # Extract description
            result = extract_character_description(
                chunk, chunk_index=i, model=model, use_ollama=use_ollama,
                use_schema=use_schema, debug=show_debug
            )

            # Record before reacting, so a crash here still leaves a trace
            append_progress(prog_path, result)
            if result["status"] in ("success", "empty"):
                done.add(i)

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

    except KeyboardInterrupt:
        interrupted = True
        print("\n\nInterrupted. Aggregating the chunks processed so far...")

    # Keep chronological order even when a retried error chunk was filled in late
    raw_descriptions.sort(key=lambda r: r["chunk_index"])

    # Aggregate descriptions by character
    print("\nAggregating descriptions by character...")
    aggregated = aggregate_character_descriptions(raw_descriptions)

    # Write output
    print(f"Writing {len(aggregated)} characters to {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
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
    print(f"Descriptions found: {len(raw_descriptions)}")
    print(f"Unique characters: {len(aggregated)}")
    print(f"Output: {output_path}")
    if interrupted:
        print("Status: INTERRUPTED (output above covers completed chunks only)")

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

    # Validate input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)

    # Determine backend and model
    model = args.model or (OLLAMA_MODEL if args.ollama else OPENROUTER_MODEL)
    backend = "Ollama" if args.ollama else "OpenRouter"
    use_schema = not args.no_schema and not args.ollama
    print(f"Using model: {model} via {backend}"
          f"{' with structured output' if use_schema else ''}")

    # Process the novel
    try:
        process_novel(
            input_path=args.input_file,
            output_path=args.output_file,
            skip_lines=args.skip_lines,
            start_chunk=args.start_chunk,
            max_chunks=args.max_chunks,
            model=model,
            debug=args.debug,
            restart=args.restart,
            use_ollama=args.ollama,
            use_schema=use_schema
        )
    except UnicodeDecodeError as e:
        print(f"Error: File encoding problem: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

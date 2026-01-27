"""
RoundTripChecker.py

Validates questions by performing round-trip answer checking.
This script:
1. Reads questions.jsonl (output from KnowledgeQuestionWriter.py)
2. Filters for questions that passed quality criteria
3. For each question, asks the model to answer it given the passage
4. Compares the model's answer to the expected answer span
5. Records whether the round-trip succeeded or failed

This validates that questions are answerable and produce the expected answer.
"""

import json
import os
import requests
from typing import Dict, Any
from difflib import SequenceMatcher

# ==============================================================================
# CONFIGURATION
# ==============================================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gpt-oss:20b"

ANSWER_PROMPT = """Read the passage and answer the question with a brief phrase taken directly from the text. Do not add explanations, context, or phrases like "the answer is" - respond only with the relevant span from the passage.

Passage: {passage}

Question: {question}

"""

# ==============================================================================
# REUSABLE MODEL INTERACTION (copied from KnowledgeQuestionWriter.py)
# ==============================================================================

def call_ollama_model(
    prompt: str,
    model: str = MODEL,
    temperature: float = 0.3,
    num_predict: int = 900,
    timeout: int = 120,
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


# ==============================================================================
# ANSWER EXTRACTION AND MATCHING
# ==============================================================================

def extract_answer(passage: str, question: str, debug: bool = False) -> Dict[str, Any]:
    """
    Ask the model to answer a question given a passage.

    Args:
        passage: The source passage containing the answer
        question: The question to answer
        debug: If True, print diagnostic information

    Returns:
        dict with one of these structures:
        - {"status": "success", "answer": str} on success
        - {"status": "error", "reason": str} on API errors
    """

    # Construct the prompt
    prompt = ANSWER_PROMPT.format(passage=passage, question=question)

    if debug:
        print(f"PASSAGE LENGTH: {len(passage)} chars")
        print(f"QUESTION: {question}")

    # Call the model with general error handling
    result = call_ollama_model(prompt, debug=debug)

    # If the API call failed, return the error
    if result["status"] == "error":
        return result

    # For answer extraction, we just return the raw response text
    return {"status": "success", "answer": result["response"]}


def check_answer_match(extracted: str, expected: str) -> Dict[str, Any]:
    """
    Compare the extracted answer to the expected answer span.

    Uses two matching criteria:
    1. Fuzzy match ratio > 0.9 (using SequenceMatcher)
    2. Expected is contained in extracted AND length ratio (extracted/expected) < 1.8

    Either condition passing means the answer is accepted.

    Args:
        extracted: The answer extracted by the model
        expected: The expected answer span

    Returns:
        dict with:
        - {"match": bool, "match_type": str, "fuzzy_ratio": float,
           "length_ratio": float, "extracted": str, "expected": str}
    """

    # Normalize whitespace for both
    extracted_norm = " ".join(extracted.split())
    expected_norm = " ".join(expected.split())

    # Calculate fuzzy match ratio (case-insensitive)
    fuzzy_ratio = SequenceMatcher(
        None,
        extracted_norm.lower(),
        expected_norm.lower()
    ).ratio()

    # Calculate length ratio
    expected_len = len(expected_norm)
    extracted_len = len(extracted_norm)
    length_ratio = extracted_len / expected_len if expected_len > 0 else float('inf')

    # Check if expected is contained in extracted (case-insensitive)
    expected_in_extracted = expected_norm.lower() in extracted_norm.lower()

    # Condition 1: Fuzzy match ratio > 0.9
    if fuzzy_ratio > 0.9:
        return {
            "match": True,
            "match_type": "fuzzy_high",
            "fuzzy_ratio": fuzzy_ratio,
            "length_ratio": length_ratio,
            "extracted": extracted,
            "expected": expected
        }

    # Condition 2: Expected in extracted AND length ratio < 1.8
    if expected_in_extracted and length_ratio < 1.8:
        return {
            "match": True,
            "match_type": "contained_compact",
            "fuzzy_ratio": fuzzy_ratio,
            "length_ratio": length_ratio,
            "extracted": extracted,
            "expected": expected
        }

    # No match
    return {
        "match": False,
        "match_type": "no_match",
        "fuzzy_ratio": fuzzy_ratio,
        "length_ratio": length_ratio,
        "extracted": extracted,
        "expected": expected
    }


# ==============================================================================
# ROUND-TRIP VALIDATION
# ==============================================================================

def validate_question(question_data: dict, debug: bool = False) -> Dict[str, Any]:
    """
    Perform round-trip validation on a single question.

    Args:
        question_data: Dict containing 'passage', 'question', 'answer_span'
        debug: If True, print diagnostic information

    Returns:
        dict with validation results including:
        - extract_status: 'success' or 'error'
        - extracted_answer: the model's answer (if successful)
        - match: bool indicating if answer matched expected
        - match_type: 'fuzzy_high', 'contained_compact', or 'no_match'
        - fuzzy_ratio: similarity ratio from SequenceMatcher (0.0-1.0)
        - length_ratio: ratio of extracted length to expected length
        - error_reason: reason for failure (if error occurred)
    """

    passage = question_data['passage']
    question = question_data['question']
    expected_answer = question_data['answer_span']

    # Extract answer from the model
    result = extract_answer(passage, question, debug=debug)

    if result["status"] == "error":
        return {
            "extract_status": "error",
            "error_reason": result["reason"],
            "match": False
        }

    extracted_answer = result["answer"]

    # Check if the extracted answer matches the expected answer
    match_result = check_answer_match(extracted_answer, expected_answer)

    return {
        "extract_status": "success",
        "extracted_answer": extracted_answer,
        "match": match_result["match"],
        "match_type": match_result["match_type"],
        "fuzzy_ratio": match_result["fuzzy_ratio"],
        "length_ratio": match_result["length_ratio"]
    }


# ==============================================================================
# MAIN PROCESSING
# ==============================================================================

def process_questions(input_path: str, output_path: str, debug: bool = False):
    """
    Process questions from questions.jsonl and validate with round-trip checking.

    Reads questions.jsonl, filters for passed questions, and validates each by:
    1. Asking the model to answer the question given the passage
    2. Comparing the extracted answer to the expected answer span
    3. Recording match results

    Args:
        input_path: Path to questions.jsonl (output from KnowledgeQuestionWriter.py)
        output_path: Path to write validation results
        debug: If True, print diagnostic information for first question

    Returns:
        List of validation results
    """

    results = []
    passed_questions = []

    # Read all questions and filter for passed ones
    print("Loading questions...")
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            q = json.loads(line)
            # Only process questions that passed all filters
            if q.get('status') == 'success' and q.get('filter_status') == 'pass':
                passed_questions.append(q)

    print(f"Found {len(passed_questions)} questions that passed filtering\n")

    # Validate each passed question
    for i, question_data in enumerate(passed_questions):
        question_preview = question_data['question'][:60]
        answer_span = question_data['answer_span']

        print(f"[{i+1}/{len(passed_questions)}] {question_preview}...", end=" ")

        # Only show debug info for first question
        show_debug = debug and i == 0

        # Perform round-trip validation
        validation = validate_question(question_data, debug=show_debug)

        # Add original question data to the result
        result = {**question_data, **validation}

        # Print result
        if validation.get('extract_status') == 'error':
            print(f"✗ ERROR: {validation.get('error_reason', 'Unknown')[:40]}")
        elif validation['match']:
            match_type = validation['match_type']
            extracted = validation['extracted_answer'][:40]
            fuzzy = validation.get('fuzzy_ratio', 0)
            length = validation.get('length_ratio', 0)
            print(f"✓ {match_type} (f:{fuzzy:.2f}, l:{length:.2f}): '{extracted}...' ≈ '{answer_span}'")
        else:
            extracted = validation.get('extracted_answer', '')[:40]
            fuzzy = validation.get('fuzzy_ratio', 0)
            length = validation.get('length_ratio', 0)
            print(f"✗ MISMATCH (f:{fuzzy:.2f}, l:{length:.2f}): '{extracted}...' ≠ '{answer_span}'")

        results.append(result)

        # Write results progressively
        with open(output_path, 'w', encoding='utf-8') as f:
            for r in results:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')

    # Print summary statistics
    total = len(results)
    errors = sum(1 for r in results if r.get('extract_status') == 'error')
    matches = sum(1 for r in results if r.get('match') is True)
    mismatches = total - errors - matches

    match_types = {}
    for r in results:
        if r.get('match'):
            mtype = r.get('match_type', 'unknown')
            match_types[mtype] = match_types.get(mtype, 0) + 1

    print(f"\n=== Summary ===")
    print(f"Total validated: {total}")
    print(f"Matches: {matches} ({matches/total*100:.1f}%)")
    for mtype, count in sorted(match_types.items()):
        print(f"  - {mtype}: {count}")
    print(f"Mismatches: {mismatches} ({mismatches/total*100:.1f}%)")
    print(f"Errors: {errors}")
    print(f"Output written to: {output_path}")

    return results


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    """
    Validate questions through round-trip answer checking.
    """

    print("Working directory:", os.getcwd())

    # Change to the directory of this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Process all passed questions
    results = process_questions(
        input_path="cyclopedia2questions.jsonl",
        output_path="validated_cyclopedia2questions.jsonl",
        debug=True  # Show debug info for first question
    )

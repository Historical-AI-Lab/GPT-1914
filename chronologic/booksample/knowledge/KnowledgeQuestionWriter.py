"""
KnowledgeQuestionWriter.py

Generates knowledge benchmark questions from encyclopedia passages using a local LLM.
This script:
1. Reads passages with identified entity spans
2. Generates questions that would elicit those specific spans as answers
3. Filters out ambiguous or context-dependent questions

The code is structured to allow reusable model interaction and error handling for
subsequent filtering stages (pass/fail validation and round-trip answer checking).
"""

import json, os, sys
import argparse
import requests
from typing import Optional, Dict, Any, Callable, List

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gpt-oss:20b"

SYSTEM_PROMPT = """You are a question writer for a historical knowledge benchmark. Given a passage from a 19th century encyclopedia and an answer span, generate a question that would elicit that answer.

A good question:
- Can be answered with ONLY the answer span (not a longer or shorter phrase)
- Has exactly one correct answer given the passage
- Does not use pronouns or vague references that require the passage to resolve
- Fully spells out any names or places (no abbreviations like "P.")
- Does not refer to the passage, e.g., "What place is mentioned in the definition of..."  
- Does not state the answer in the question itself

If no unambiguous question is possible (e.g., the answer is too generic, appears multiple times with different meanings, or lacks sufficient context), respond with SKIP and a brief reason.

Respond in exactly this format:
QUESTION: [your question]
or
SKIP: [reason]"""

FEW_SHOT_EXAMPLES = """
---
Passage: PHILIPPSBURG: town of Baden, on the right bank of the Rhine; anciently one of the most important fortresses on the Rhine. The fortifications were destroyed 1800.
Answer span: 1800
Entity type: DATE

QUESTION: In what year were the fortifications of Philippsburg destroyed?
---
Passage: PHILLIPS, JOHN, LL.D.: 1719, Dec. 6-1795, Apr. 21; b. Andover, Mass.: philanthropist. He graduated at Harvard College 1735.
Answer span: Harvard College
Entity type: ORG

QUESTION: From which institution did the philanthropist John Phillips graduate in 1735?
---
Passage: PEDRO II. (Dom PEDRO DE ALCANTARA), ex-Emperor of Brazil: born Rio Janeiro, 1825, Dec. 2 (reigned 1841-89); died 1891, Dec. 5; son of Pedro I.
Answer span: Rio Janeiro
Entity type: GPE

QUESTION: In what city was Emperor Pedro II of Brazil born?
---
Passage: The Amazon river was made free to all nations 1867. Journeys were made by P. to Europe 1871-2.
Answer span: 1867
Entity type: DATE

SKIP: Multiple dates in passage; "the Amazon river was made free" lacks enough context for someone without the passage to know this refers to Brazil's navigation policy.
---
Passage: He was a man of noble presence and character, highly cultivated, interested especially in science.
Answer span: science
Entity type: MISC

SKIP: Answer is too generic and the passage uses only pronouns, making an unambiguous question impossible.
---"""

FILTER_PROMPT = """You are a quality filter for a historical knowledge benchmark. Evaluate whether the following question meets quality standards.

Question: {question}
Expected answer: {answer}

Evaluate against these criteria:
1. WORLD_KNOWLEDGE: Requires knowledge of the 19c world (history, geography, people, events), not just dictionary definitions of words.
2. REAL_ENTITIES: Can be answered through knowledge of real entities, not by consulting a specific text (reject questions like "What is the definition of X in the encyclopedia?" or "What does the entry for Y say?").
3. CLEAR_REFERENCES: Does not contain opaque abbreviations or pronouns with unclear referents.
4. NO_ANSWER_LEAK: The answer does not appear verbatim in the question.
5. GRAMMATICAL: The question is grammatically well-formed and understandable.
6. UNAMBIGUOUS: The question has a single, specific expected answer (not multiple plausible answers).

Respond in this format:
PASS: [brief note on why it's good]
or
FAIL: [which criterion failed]: [explanation]

---
Question: In what year were the fortifications of Philippsburg destroyed?
Expected answer: 1800

PASS: Clear historical question about a specific event with unambiguous answer.
---
Question: What is a pencil?
Expected answer: thin strip of plumbago

FAIL: WORLD_KNOWLEDGE: This is a dictionary definition question, not a test of historical knowledge.
---
Question: What does the entry for Pedaliacae reference?
Expected answer: Bignoniaceae

FAIL: REAL_ENTITIES: This asks about consulting a specific encyclopedia entry, not general knowledge.
---
Question: When did he arrive in Portugal?
Expected answer: Dec. 7

FAIL: CLEAR_REFERENCES: "he" has no referent outside the source passage.
---
Question: In what year was the 1800 fortress destroyed?
Expected answer: 1800

FAIL: NO_ANSWER_LEAK: The answer "1800" appears in the question.
---
Question: {question}
Expected answer: {answer}

"""

# ==============================================================================
# REUSABLE MODEL INTERACTION AND ERROR HANDLING
# ==============================================================================

def call_ollama_model(
    prompt: str,
    model: str = MODEL,
    temperature: float = 0.3,
    num_predict: int = 1000,
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


def parse_question_response(response_text: str) -> Dict[str, Any]:
    """
    Parse a question generation response into structured format.

    This function handles the question-specific response format where the model
    responds with either:
    - "QUESTION: <text>" for successful question generation
    - "SKIP: <reason>" when no good question can be formed

    Args:
        response_text: Raw text response from the model

    Returns:
        dict with one of these structures:
        - {"status": "success", "question": str} for valid questions
        - {"status": "skip", "reason": str} when model skips
        - {"status": "error", "reason": str} for unexpected formats
    """

    if response_text.startswith("QUESTION:"):
        question = response_text[9:].strip()
        return {"status": "success", "question": question}
    elif response_text.startswith("SKIP:"):
        reason = response_text[5:].strip()
        return {"status": "skip", "reason": reason}
    else:
        return {"status": "error", "reason": f"Unexpected format: {response_text[:100]}"}


def parse_filter_response(response_text: str) -> Dict[str, Any]:
    """
    Parse a question filter response into structured format.

    The filter evaluates questions against quality criteria and responds with:
    - "PASS: <reason>" if the question meets all criteria
    - "FAIL: <criterion>: <explanation>" if it fails any criterion

    Args:
        response_text: Raw text response from the model

    Returns:
        dict with one of these structures:
        - {"status": "pass", "reason": str} for questions that pass
        - {"status": "fail", "criterion": str, "reason": str} for questions that fail
        - {"status": "error", "reason": str} for unexpected formats
    """

    if response_text.startswith("PASS:"):
        reason = response_text[5:].strip()
        return {"status": "pass", "reason": reason}
    elif response_text.startswith("FAIL:"):
        # Parse FAIL: [criterion]: [explanation]
        fail_content = response_text[5:].strip()
        # Try to split on first colon to separate criterion from explanation
        if ":" in fail_content:
            criterion, explanation = fail_content.split(":", 1)
            return {
                "status": "fail",
                "criterion": criterion.strip(),
                "reason": explanation.strip()
            }
        else:
            # If no colon found, just use the whole thing as reason
            return {
                "status": "fail",
                "criterion": "UNKNOWN",
                "reason": fail_content
            }
    else:
        return {"status": "error", "reason": f"Unexpected format: {response_text[:100]}"}


# ==============================================================================
# QUESTION FILTERING
# ==============================================================================

def filter_question(question: str, answer_span: str, debug: bool = False) -> Dict[str, Any]:
    """
    Evaluate a generated question against quality criteria.

    Uses the FILTER_PROMPT to check if a question:
    - Tests world knowledge (not dictionary definitions)
    - Can be answered through real entity knowledge (not text-specific)
    - Has clear references (no opaque pronouns/abbreviations)
    - Doesn't leak the answer in the question text
    - Is grammatically well-formed
    - Has an unambiguous expected answer

    Args:
        question: The generated question to evaluate
        answer_span: The expected answer
        debug: If True, print diagnostic information

    Returns:
        dict with one of these structures:
        - {"status": "pass", "reason": str} if question meets criteria
        - {"status": "fail", "criterion": str, "reason": str} if it fails
        - {"status": "error", "reason": str} on API/parsing errors
    """

    # Fill in the FILTER_PROMPT template
    prompt = FILTER_PROMPT.format(question=question, answer=answer_span)

    if debug:
        print(f"FILTER PROMPT LENGTH: {len(prompt)} chars")

    # Call the model with general error handling
    result = call_ollama_model(prompt, debug=debug)

    # If the API call failed, return the error
    if result["status"] == "error":
        return result

    # Parse the filter-specific response format
    return parse_filter_response(result["response"])


# ==============================================================================
# QUESTION GENERATION
# ==============================================================================

def generate_question(passage: str, answer_span: str, entity_type: str, debug: bool = False) -> Dict[str, Any]:
    """
    Generate a knowledge question for a given answer span in a passage.

    This function constructs a prompt with few-shot examples and system instructions,
    calls the LLM, and parses the response. The model is instructed to either generate
    a clear, unambiguous question or skip if no good question is possible.

    Args:
        passage: Encyclopedia passage containing the answer span
        answer_span: The specific text that should be the answer
        entity_type: Named entity type (DATE, GPE, ORG, PERSON, etc.)
        debug: If True, print diagnostic information

    Returns:
        dict with one of these structures:
        - {"status": "success", "question": str}
        - {"status": "skip", "reason": str}
        - {"status": "error", "reason": str}
    """

    # Construct the prompt with system instructions and few-shot examples
    prompt = f"""{SYSTEM_PROMPT}

{FEW_SHOT_EXAMPLES}
---
Passage: {passage}
Answer span: {answer_span}
Entity type: {entity_type}

"""

    if debug:
        print(f"PASSAGE LENGTH: {len(passage)} chars")

    # Call the model with general error handling
    result = call_ollama_model(prompt, debug=debug)

    # If the API call failed, return the error
    if result["status"] == "error":
        return result

    # Parse the question-specific response format
    return parse_question_response(result["response"])

def process_chunks(
    input_path: str,
    output_path: str,
    max_entities_per_chunk: int = 20,
    start_line: int = 1
):
    """
    Process encyclopedia chunks and generate questions for identified entities.

    Reads a JSONL file where each line contains a chunk with:
    - 'text': passage text
    - 'entities': list of (span, label) tuples
    - 'start_line', 'end_line': source line numbers

    For each entity in each chunk:
    1. Deduplicate entity spans
    2. Filter out short spans and numeric types (CARDINAL, ORDINAL)
    3. Generate a knowledge question
    4. Filter the question against quality criteria
    5. Write results progressively to output file

    Each result dict contains:
    - status: 'success', 'skip', or 'error' (from question generation)
    - question: the generated question (if status='success')
    - filter_status: 'pass', 'fail', or 'error' (if question was generated)
    - filter_criterion: which criterion failed (if filter_status='fail')
    - filter_reason: explanation of pass/fail/error

    Args:
        input_path: Path to input JSONL file with chunks and entities
        output_path: Path to write output JSONL file with questions
        max_entities_per_chunk: Maximum entities to process per chunk (for cost control)
        start_line: Line number to start processing from (1-indexed, for restart capability)

    Returns:
        List of all result dicts (each with status, question/reason, and metadata)
    """

    results = []

    # If restarting, load existing results from output file
    if start_line > 1 and os.path.exists(output_path):
        print(f"Restarting from line {start_line}, loading existing results...")
        with open(output_path, 'r', encoding='utf-8') as f:
            for line in f:
                results.append(json.loads(line))
        print(f"Loaded {len(results)} existing results")

    with open(input_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            # Skip lines before start_line
            if line_num < start_line:
                continue

            chunk = json.loads(line)
            passage = chunk['text']
            entities = chunk['entities']

            # Display JSONL line number clearly for restart purposes
            print(f"\n=== Processing JSONL line {line_num} ===")
            if 'start_line' in chunk and 'end_line' in chunk:
                print(f"    Source lines {chunk['start_line']}-{chunk['end_line']}")
            print(f"    {len(entities)} entities found")

            # Deduplicate entities (same span might appear multiple times)
            seen = set()
            unique_entities = []
            for span, label in entities:
                if span not in seen:
                    seen.add(span)
                    unique_entities.append((span, label))

            # Filter out short/noisy entities
            # CARDINAL and ORDINAL types tend to be numbers without sufficient context
            filtered = [
                (span, label) for span, label in unique_entities
                if len(span) >= 3 and label not in ('CARDINAL', 'ORDINAL')
            ]

            # Limit per chunk to control processing time and API costs
            filtered = filtered[:max_entities_per_chunk]

            # Generate question for each entity
            for span, label in filtered:
                print(f"  → {label}: {span[:50]}...", end=" ")

                result = generate_question(passage, span, label)

                # Add metadata to the result
                result.update({
                    "passage": passage,
                    "answer_span": span,
                    "entity_type": label,
                    "chunk_start": chunk['start_line'],
                    "chunk_end": chunk['end_line'],
                })

                # If question was successfully generated, filter it for quality
                if result['status'] == 'success':
                    filter_result = filter_question(result['question'], span)
                    result['filter_status'] = filter_result['status']

                    if filter_result['status'] == 'pass':
                        result['filter_reason'] = filter_result.get('reason', '')
                    elif filter_result['status'] == 'fail':
                        result['filter_criterion'] = filter_result.get('criterion', 'UNKNOWN')
                        result['filter_reason'] = filter_result.get('reason', '')
                    elif filter_result['status'] == 'error':
                        result['filter_reason'] = filter_result.get('reason', '')

                # Print status indicator
                if result['status'] == 'success':
                    question_preview = result['question'][:60]
                    filter_status = result.get('filter_status', 'unknown')

                    if filter_status == 'pass':
                        print(f"✓ {question_preview}...")
                    elif filter_status == 'fail':
                        criterion = result.get('filter_criterion', 'UNKNOWN')
                        reason = result.get('filter_reason', '')[:40]
                        print(f"✗ FAIL ({criterion}): {question_preview}... | {reason}")
                    else:
                        # Filter error - still show the question but indicate filter failed
                        print(f"⚠ {question_preview}... (filter error)")
                elif result['status'] == 'skip':
                    print(f"⊘ {result['reason'][:40]}...")
                else:
                    print(f"✗ {result.get('reason', 'Unknown error')[:50]}")

                results.append(result)

            # Write results progressively (after each chunk)
            with open(output_path, 'w', encoding='utf-8') as f:
                for r in results:
                    f.write(json.dumps(r, ensure_ascii=False) + '\n')

            # Print summary statistics
            successes = sum(1 for r in results if r['status'] == 'success')
            skips = sum(1 for r in results if r['status'] == 'skip')
            errors = sum(1 for r in results if r['status'] == 'error')

            # Filter statistics (only for successfully generated questions)
            passed = sum(1 for r in results
                        if r['status'] == 'success' and r.get('filter_status') == 'pass')
            failed = sum(1 for r in results
                        if r['status'] == 'success' and r.get('filter_status') == 'fail')
            filter_errors = sum(1 for r in results
                               if r['status'] == 'success' and r.get('filter_status') == 'error')

            print(f"\n=== Summary ===")
            print(f"Questions generated: {successes}")
            print(f"  - Passed filter: {passed}")
            print(f"  - Failed filter: {failed}")
            print(f"  - Filter errors: {filter_errors}")
            print(f"Skipped: {skips}")
            print(f"Errors: {errors}")
            print(f"Output written to: {output_path}")

    return results


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    """
    Generate knowledge questions from encyclopedia chunks with entity spans.

    Usage:
        python KnowledgeQuestionWriter.py <input_file> <output_file> [options]
    """

    parser = argparse.ArgumentParser(
        description="Generate knowledge benchmark questions from encyclopedia passages with entity spans."
    )

    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the input JSONL file with chunks and entities"
    )

    parser.add_argument(
        "output_file",
        type=str,
        help="Path to the output JSONL file for generated questions"
    )

    parser.add_argument(
        "--max-entities",
        type=int,
        default=20,
        help="Maximum entities to process per chunk (default: 20)"
    )

    parser.add_argument(
        "--start-line",
        type=int,
        default=1,
        help="JSONL line number to start processing from (1-indexed, for restart capability)"
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Run a single test with debug output before processing"
    )

    args = parser.parse_args()

    # Validate input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)

    print("Working directory:", os.getcwd())

    # Optional test mode
    if args.test:
        print("\n=== Running test generation with debug output ===")
        with open(args.input_file, 'r', encoding='utf-8') as f:
            test_chunk = json.loads(f.readline())

        if test_chunk.get('entities'):
            result = generate_question(
                test_chunk['text'],
                test_chunk['entities'][0][0],  # first entity span
                test_chunk['entities'][0][1],  # first entity type
                debug=True
            )
            print("\nTest result:", result)
        else:
            print("No entities found in first chunk for testing")

    # Process all chunks
    print(f"\n=== Processing chunks from {args.input_file} ===")
    if args.start_line > 1:
        print(f"Starting from JSONL line {args.start_line}")

    results = process_chunks(
        input_path=args.input_file,
        output_path=args.output_file,
        max_entities_per_chunk=args.max_entities,
        start_line=args.start_line
    )
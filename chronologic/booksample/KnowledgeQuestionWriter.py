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

import json, os
import requests
from typing import Optional, Dict, Any, Callable

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
    num_predict: int = 750,
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

def process_chunks(input_path: str, output_path: str, max_entities_per_chunk: int = 20):
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
    4. Write results progressively to output file

    Args:
        input_path: Path to input JSONL file with chunks and entities
        output_path: Path to write output JSONL file with questions
        max_entities_per_chunk: Maximum entities to process per chunk (for cost control)

    Returns:
        List of all result dicts (each with status, question/reason, and metadata)
    """

    results = []

    with open(input_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            chunk = json.loads(line)
            passage = chunk['text']
            entities = chunk['entities']

            print(f"\n=== Chunk {line_num + 1} (lines {chunk['start_line']}-{chunk['end_line']}) ===")
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

                # Print status indicator
                if result['status'] == 'success':
                    print(f"✓ {result['question'][:60]}...")
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

            print(f"\n=== Summary ===")
            print(f"Questions generated: {successes}")
            print(f"Skipped: {skips}")
            print(f"Errors: {errors}")
            print(f"Output written to: {output_path}")

    return results


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    """
    Test the question generation pipeline:
    1. Run a single test with debug output
    2. Process all chunks in encyclopedia.jsonl
    3. Write questions to questions.jsonl
    """

    print("Working directory:", os.getcwd())

    # Change to the directory of this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Test with first entity from first chunk (with debug output)
    print("\n=== Running test generation with debug output ===")
    test_chunk = json.loads(open("encyclopedia.jsonl").readline())
    result = generate_question(
        test_chunk['text'],
        test_chunk['entities'][0][0],  # first entity span
        test_chunk['entities'][0][1],  # first entity type
        debug=True
    )
    print("\nTest result:", result)

    # Process all chunks
    print("\n=== Processing all chunks ===")
    results = process_chunks(
        input_path="encyclopedia.jsonl",
        output_path="questions.jsonl",
        max_entities_per_chunk=20
    )
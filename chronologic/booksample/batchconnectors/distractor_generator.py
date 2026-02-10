#!/usr/bin/env python3
"""
Distractor Generator Module

Generates distractors for cloze-style benchmark questions.
Supports three distractor types:
- negation: LLM reverses meaning of ground truth
- same_book: BERT NSP-ranked candidates from same text
- anachronistic: LLM generates without historical context

Usage:
    from distractor_generator import generate_distractors

    answer_strings, answer_types, answer_probabilities = generate_distractors(
        metadata_prefix="...",
        passage="...",
        prompt="...",
        ground_truth="...",
        distractor_candidates=[...],
        mask_string="[masked sentence...]",
        distractor_types=["negation", "same_book", "anachronistic_gpt-oss:20b"],
        is_clause=False
    )
"""

import json
import math
import random
import re
import requests
import time
from typing import Any, Dict, List, Optional, Tuple

# Try to import BERT dependencies
try:
    import torch
    from transformers import BertTokenizer, BertForNextSentencePrediction
    BERT_AVAILABLE = True
except ImportError:
    BERT_AVAILABLE = False
    print("Warning: transformers/torch not available. BERT ranking will fall back to random selection.")

try:
    from nltk import sent_tokenize
except ImportError:
    import nltk
    nltk.download('punkt', quiet=True)
    from nltk import sent_tokenize

# Constants
OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "gpt-oss:20b"
BERT_MODEL_NAME = "bert-base-uncased"
TEMPERATURE = 0.7
NUM_PREDICT = 1200
TIMEOUT = 120
MAX_RETRIES = 2

# BERT model cache
_bert_cache: Dict[str, Any] = {}

# Prompts for negation
NEGATION_SENTENCE_PROMPT = """You are transforming sentences by reversing one aspect of their meaning. In doing this you try to change as little as possible and produce idiomatic prose. Don't simply add 'not' if it's possible to reverse the meaning more idiomatically by substituting a different word. 

Reverse only one aspect of the sentence; don't reverse everything. Respond only with the negated sentence; do not add any framing language or explanation.

For instance:

original sentence: As a result, the judge condemned him and sentenced him to die that day.

negation: As a result, the judge exonerated him and released him that day.

original sentence: But for our present purpose, we may focus on the inherent unity of each self, even though this be hidden by its varied forms.

negation: But for our present purpose, we may focus on the inherent unity of each self, even though this be displayed by its varied forms.

original sentence: {ground_truth}
negation:"""

NEGATION_CLAUSE_PROMPT = """You are transforming clauses by reversing one aspect of their meaning. In doing this you try to change as little as possible, but also strive to produce idiomatic prose. Don't simply add 'not' if it's possible to reverse the meaning more idiomatically by substituting different words. Also, don't reverse everything and produce a double negative; reversing one aspect is enough. Respond only with the negated clause; do not add any framing language or explanation.

original clause: because its sides are so steep that a stone will slide down

negation: because its sides slope so gently that a stone will slide down

original clause: provided that the funds are sufficient to cover costs

negation: provided that the funds fail to cover costs

original clause: {ground_truth}
negation:"""

CONNECTOR_TERMS = {
    'causalsentence': 'justification, rationale, purpose, cause, or because',
    'causalclause': 'because, since, as, in order to, for, seeing that, owing to, inasmuch, or forasmuch',
    'effectsentence': 'so, hence, thus, therefore, thence, accordingly, consequence, result, effect, consequently, or it follows that',
    'effectclause': 'so, or then',
    'contrastsentence': 'but, yet, however, or nevertheless',
    'contrastclause': 'but, however, or nevertheless',
    'conditionalclause': 'if, provided that, insofar as, or unless',
    'concessiveclause': 'although, though, even though, even if, albeit, or while',
}

ANACHRONISTIC_PROMPT = """Answer the following question with a {length_spec} that uses a term such as {term_spec}:

{question_text}

Write only the answer, without quotation marks:"""


def format_length_spec(gt_words: int, is_clause: bool) -> str:
    """
    Build a length specification string for the anachronistic prompt.

    Rounds gt_words to the nearest even number (floor of 2) and returns
    a string like "clause of roughly 12 words" or "sentence of roughly 20 words".

    Args:
        gt_words: Word count of the ground truth
        is_clause: Whether the ground truth is a clause (vs full sentence)

    Returns:
        Length specification string
    """
    rounded = round(gt_words / 2) * 2
    rounded = max(rounded, 2)
    unit = "clause" if is_clause else "sentence"
    return f"{unit} of roughly {rounded} words"


def get_term_spec(category: Optional[str]) -> str:
    """
    Look up connector term specification for a category.

    Args:
        category: Connector category key (e.g. 'causalclause'), or None

    Returns:
        Term spec string listing appropriate connector vocabulary,
        or a generic fallback if category is unknown/None
    """
    if category and category in CONNECTOR_TERMS:
        return CONNECTOR_TERMS[category]
    return "a connecting word or phrase"


def call_ollama_model(prompt: str, model: str = DEFAULT_MODEL,
                      temperature: float = TEMPERATURE,
                      num_predict: int = NUM_PREDICT,
                      timeout: int = TIMEOUT,
                      debug: bool = False) -> Dict[str, Any]:
    """
    Call Ollama API to generate text.

    Args:
        prompt: The prompt to send to the model
        model: Model name (default: gpt-oss:20b)
        temperature: Temperature parameter (default: 0.7)
        num_predict: Maximum tokens to generate (default: 500)
        timeout: Request timeout in seconds (default: 120)
        debug: Print debug information

    Returns:
        Dict with 'status' and either 'response' or 'reason'
    """
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": num_predict
            }
        }

        if debug:
            print(f"\n[DEBUG] Calling Ollama API with model: {model}")
            print(f"[DEBUG] Prompt length: {len(prompt)} characters")

        response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        response.raise_for_status()

        result = response.json()
        generated_text = result.get("response", "").strip()

        # Handle thinking models that put content in "thinking" field
        if not generated_text and "thinking" in result:
            thinking_text = result.get("thinking", "").strip()
            if thinking_text:
                # Try to extract the actual response from thinking
                generated_text = thinking_text

        if debug:
            print(f"[DEBUG] Response length: {len(generated_text)} characters")
            print(f"[DEBUG] Response: {generated_text[:200]}...")

        return {"status": "success", "response": generated_text}

    except requests.exceptions.ConnectionError:
        return {"status": "error", "reason": "Connection refused - is Ollama running?"}
    except requests.exceptions.Timeout:
        return {"status": "error", "reason": f"Request timeout after {timeout}s"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "reason": f"Request failed: {str(e)}"}
    except json.JSONDecodeError:
        return {"status": "error", "reason": "Invalid JSON response from Ollama"}
    except Exception as e:
        return {"status": "error", "reason": f"Unexpected error: {str(e)}"}


def _load_bert_model() -> Tuple[Optional[Any], Optional[Any]]:
    """
    Load BERT model and tokenizer with caching.

    Returns:
        Tuple of (model, tokenizer) or (None, None) if loading fails
    """
    if not BERT_AVAILABLE:
        return None, None

    if 'failed' in _bert_cache:
        return None, None

    if 'model' in _bert_cache:
        return _bert_cache['model'], _bert_cache['tokenizer']

    try:
        print("Loading BERT model for distractor ranking (this may take a moment)...")
        start = time.time()

        _bert_cache['tokenizer'] = BertTokenizer.from_pretrained(BERT_MODEL_NAME)
        _bert_cache['model'] = BertForNextSentencePrediction.from_pretrained(BERT_MODEL_NAME)
        _bert_cache['model'].eval()

        elapsed = time.time() - start
        print(f"BERT loaded in {elapsed:.1f}s")

        return _bert_cache['model'], _bert_cache['tokenizer']

    except Exception as e:
        print(f"Warning: Could not load BERT model: {e}")
        print("Falling back to random distractor selection for same_book type")
        _bert_cache['failed'] = True
        return None, None


def get_nsp_probability(tokenizer, model, sent_a: str, sent_b: str) -> float:
    """
    Get BERT's Next Sentence Prediction probability.

    Args:
        tokenizer: BERT tokenizer
        model: BERT NSP model
        sent_a: First sentence
        sent_b: Second sentence

    Returns:
        Probability that sent_b follows sent_a (0.0 to 1.0)
    """
    try:
        encoding = tokenizer(
            sent_a, sent_b,
            return_tensors='pt',
            truncation=True,
            max_length=512,
            padding=True
        )

        with torch.no_grad():
            outputs = model(**encoding)
            # outputs.logits shape: [1, 2] where [0] = IsNext, [1] = NotNext
            probs = torch.softmax(outputs.logits, dim=1)
            is_next_prob = probs[0, 0].item()

        return is_next_prob

    except Exception as e:
        print(f"Warning: NSP calculation failed: {e}")
        return 0.5  # Return neutral probability on error


def rank_candidates_by_nsp(passage: str, mask_string: str,
                           candidates: List[str], n: int,
                           verbose: bool = False) -> List[str]:
    """
    Rank candidate distractors by BERT NSP probability.

    For each candidate:
    1. Substitute into passage (replacing mask_string)
    2. Extract sentences: prev_sent, substituted_sent, next_sent
    3. Calculate log P(prev -> sub) + log P(sub -> next)
    4. Return top n candidates

    Args:
        passage: Passage text with mask_string placeholder
        mask_string: The placeholder to replace (e.g., "[masked sentence...]")
        candidates: List of candidate strings to rank
        n: Number of top candidates to return
        verbose: Print all candidates with scores for inspection

    Returns:
        List of top n candidates sorted by NSP probability
    """
    model, tokenizer = _load_bert_model()

    if model is None:
        # Fallback to random selection
        shuffled = list(candidates)
        random.shuffle(shuffled)
        return shuffled[:n]

    scored_candidates = []

    for candidate in candidates:
        # Substitute candidate into passage
        filled_passage = passage.replace(mask_string, candidate)

        # Split into sentences
        sentences = sent_tokenize(filled_passage)

        # Find which sentence contains the substitution
        sub_idx = None
        for i, sent in enumerate(sentences):
            if candidate in sent or candidate.rstrip('.,;:!?') in sent:
                sub_idx = i
                break

        if sub_idx is None:
            # Couldn't locate substitution, skip
            continue

        # Calculate log probabilities (use log to avoid underflow)
        log_prob = 0.0

        if sub_idx > 0:
            prev_prob = get_nsp_probability(
                tokenizer, model,
                sentences[sub_idx - 1],
                sentences[sub_idx]
            )
            # Add small epsilon to avoid log(0)
            log_prob += math.log(prev_prob + 1e-10)

        if sub_idx < len(sentences) - 1:
            next_prob = get_nsp_probability(
                tokenizer, model,
                sentences[sub_idx],
                sentences[sub_idx + 1]
            )
            log_prob += math.log(next_prob + 1e-10)

        scored_candidates.append((log_prob, candidate))

    # Sort by log probability (descending)
    scored_candidates.sort(key=lambda x: x[0], reverse=True)

    if verbose:
        print("\n[BERT RANKING] All candidates sorted by NSP probability:")
        for i, (score, cand) in enumerate(scored_candidates):
            print(f"  {i+1}. (log_prob={score:.4f}) {cand[:80]}...")
        print()

    return [cand for _, cand in scored_candidates[:n]]


def generate_negation(ground_truth: str, is_clause: bool,
                      model: str = "mistral-small:24b",
                      debug: bool = False) -> Optional[str]:
    """
    Generate negation distractor using LLM.

    Args:
        ground_truth: The original sentence/clause to negate
        is_clause: Whether this is a clause (vs full sentence)
        model: Model to use for generation
        debug: Print debug information

    Returns:
        Negated string or None if generation fails
    """
    if is_clause:
        prompt = NEGATION_CLAUSE_PROMPT.format(ground_truth=ground_truth)
    else:
        prompt = NEGATION_SENTENCE_PROMPT.format(ground_truth=ground_truth)

    for attempt in range(MAX_RETRIES + 1):
        result = call_ollama_model(prompt, model=model, temperature=0.5, debug=debug)

        if result['status'] != 'success':
            if attempt < MAX_RETRIES:
                print(f"  Negation generation failed ({result['reason']}), retrying...")
                time.sleep(1)
                continue
            return None

        negation = result['response'].strip()

        # Clean up the response
        # Take only the first line (model often adds explanation after)
        if '\n' in negation:
            negation = negation.split('\n')[0].strip()

        # Remove any prefix like "negation:" if present
        negation = re.sub(r'^negation:\s*', '', negation, flags=re.IGNORECASE)
        # Remove quotation marks
        negation = negation.strip('"\'')

        # If it still has explanation text after period (for sentences), try to extract just the sentence
        if not is_clause and '. ' in negation:
            # Check if there's explanatory text after the first sentence
            parts = negation.split('. ', 1)
            # If second part starts with lowercase or parenthesis, it's likely explanation
            if len(parts) > 1 and (parts[1][0].islower() or parts[1][0] == '('):
                negation = parts[0] + '.'

        # Normalize formatting to match ground truth
        negation = normalize_distractor_format(negation, ground_truth)

        # Basic validation: should be different from original
        if negation and negation.lower() != ground_truth.lower():
            return negation

        if attempt < MAX_RETRIES:
            print("  Negation too similar to original, retrying...")

    return None


def parse_distractor_type(type_string: str) -> Dict[str, Any]:
    """
    Parse a distractor type string into components.

    Examples:
        "negation" -> {"type": "negation", "model": None, "metadataless": False}
        "same_book" -> {"type": "same_book", "model": None, "metadataless": False}
        "anachronistic_gpt-oss:20b" -> {"type": "anachronistic", "model": "gpt-oss:20b", "metadataless": False}
        "anachronistic_metadataless_mistral-small:24b" -> {"type": "anachronistic", "model": "mistral-small:24b", "metadataless": True}

    Args:
        type_string: The distractor type specification

    Returns:
        Dict with parsed components
    """
    if type_string == "negation":
        return {"type": "negation", "model": None, "metadataless": False}

    if type_string == "same_book":
        return {"type": "same_book", "model": None, "metadataless": False}

    if type_string.startswith("anachronistic_"):
        remainder = type_string[len("anachronistic_"):]

        if remainder.startswith("metadataless_"):
            model = remainder[len("metadataless_"):]
            return {"type": "anachronistic", "model": model, "metadataless": True}
        else:
            return {"type": "anachronistic", "model": remainder, "metadataless": False}

    # Unknown type, return as-is
    return {"type": type_string, "model": None, "metadataless": False}


def normalize_distractor_format(distractor: str, ground_truth: str) -> str:
    """
    Normalize distractor formatting to match ground truth capitalization and punctuation.

    - If ground truth starts lowercase, make distractor start lowercase
    - If ground truth starts uppercase, make distractor start uppercase
    - If ground truth ends with sentence punctuation (.!?), ensure distractor does too
    - If ground truth lacks final punctuation, remove it from distractor

    Args:
        distractor: The generated distractor text
        ground_truth: The ground truth to match formatting against

    Returns:
        Distractor with normalized formatting
    """
    if not distractor or not ground_truth:
        return distractor

    result = distractor.strip()

    # Handle capitalization
    gt_starts_lower = ground_truth[0].islower()
    if gt_starts_lower and result and result[0].isupper():
        # Ground truth starts lowercase, distractor starts uppercase -> lowercase it
        result = result[0].lower() + result[1:]
    elif not gt_starts_lower and result and result[0].islower():
        # Ground truth starts uppercase, distractor starts lowercase -> uppercase it
        result = result[0].upper() + result[1:]

    # Handle final punctuation
    final_punct = '.!?'
    gt_has_final_punct = ground_truth.rstrip()[-1] in final_punct if ground_truth.rstrip() else False

    if gt_has_final_punct:
        # Ground truth has final punctuation - ensure distractor does too
        if result and result[-1] not in final_punct:
            # Add period if missing
            result = result.rstrip(',;:') + '.'
    else:
        # Ground truth lacks final punctuation - remove from distractor
        while result and result[-1] in final_punct:
            result = result[:-1]

    return result


def generate_anachronistic(metadata_prefix: str, passage: str, prompt: str,
                           ground_truth: str, model: str,
                           metadataless: bool = False,
                           is_clause: bool = False, category: Optional[str] = None,
                           debug: bool = False) -> Optional[str]:
    """
    Generate anachronistic distractor using LLM.

    Args:
        metadata_prefix: Metadata frame describing the book
        passage: The passage with mask
        prompt: The question prompt
        ground_truth: The correct answer (for length comparison)
        model: Model to use for generation
        metadataless: If True, omit metadata_prefix from the prompt
        is_clause: Whether the ground truth is a clause (vs full sentence)
        category: Connector category (e.g. 'causalclause') for term guidance
        debug: Print debug information

    Returns:
        Generated distractor or None if generation fails
    """
    gt_words = len(ground_truth.split())

    # Build question text
    if metadataless:
        question_text = f"{passage}\n\n{prompt}"
    else:
        question_text = f"{metadata_prefix}\n\n{passage}\n\n{prompt}"

    # Compute specs upfront — same on every attempt
    length_spec = format_length_spec(gt_words, is_clause)
    term_spec = get_term_spec(category)

    for attempt in range(2):
        full_prompt = ANACHRONISTIC_PROMPT.format(
            length_spec=length_spec,
            term_spec=term_spec,
            question_text=question_text
        )

        result = call_ollama_model(full_prompt, model=model, debug=debug)

        if result['status'] != 'success':
            if attempt < 1:
                print(f"  Anachronistic generation failed ({result['reason']}), retrying...")
                time.sleep(1)
                continue
            return None

        response = result['response'].strip()

        # Clean up response
        response = response.strip('"\'')

        # Normalize formatting to match ground truth
        response = normalize_distractor_format(response, ground_truth)

        # Check length
        resp_words = len(response.split())

        if resp_words >= gt_words * 0.5 and resp_words <= gt_words * 2:
            return response

        # Length check failed, retry once with same spec
        if attempt < 1:
            print(f"  Response length ({resp_words} words) outside bounds, retrying...")

    # Return whatever we got even if length is off, but still normalize formatting
    fallback = result.get('response', '').strip().strip('"\'')
    if fallback:
        return normalize_distractor_format(fallback, ground_truth)
    return None


def assign_metadataless_variant(distractor_types: List[str]) -> List[str]:
    """
    Randomly assign exactly one anachronistic distractor to be metadataless.

    Args:
        distractor_types: List of distractor type specifications

    Returns:
        Modified list with one anachronistic type changed to metadataless
    """
    # Find indices of anachronistic types that aren't already metadataless
    anachronistic_indices = [
        i for i, dt in enumerate(distractor_types)
        if dt.startswith('anachronistic_') and 'metadataless' not in dt
    ]

    if anachronistic_indices:
        chosen_idx = random.choice(anachronistic_indices)
        original = distractor_types[chosen_idx]
        # Insert 'metadataless_' after 'anachronistic_'
        parts = original.split('_', 1)
        distractor_types[chosen_idx] = f"{parts[0]}_metadataless_{parts[1]}"

    return distractor_types


def generate_distractors(
    metadata_prefix: str,
    passage: str,
    prompt: str,
    ground_truth: str,
    distractor_candidates: List[str],
    mask_string: str,
    distractor_types: List[str],
    is_clause: bool,
    category: Optional[str] = None,
    verbose_bert: bool = False,
    debug: bool = False
) -> Tuple[List[str], List[str], List[float]]:
    """
    Generate distractors for a cloze question.

    Args:
        metadata_prefix: Metadata frame describing the book
        passage: The passage with mask_string placeholder
        prompt: The question prompt
        ground_truth: The correct answer
        distractor_candidates: List of candidates for same_book type
        mask_string: The placeholder string in passage (e.g., "[masked sentence...]")
        distractor_types: List of distractor types to generate
        is_clause: Whether ground truth is a clause (vs full sentence)
        category: Connector category (e.g. 'causalclause') for term guidance
        verbose_bert: Print BERT ranking details
        debug: Print debug information

    Returns:
        Tuple of (answer_strings, answer_types, answer_probabilities)
        - answer_strings: [ground_truth, distractor1, distractor2, ...]
        - answer_types: ["ground_truth", type1, type2, ...]
        - answer_probabilities: [1.0, 0.0, 0.0, ...]
    """
    # Start with ground truth
    answer_strings = [ground_truth]
    answer_types = ["ground_truth"]
    answer_probabilities = [1.0]

    # Assign metadataless variant to one anachronistic distractor
    distractor_types = assign_metadataless_variant(list(distractor_types))

    # Track how many same_book distractors we need
    same_book_count = sum(1 for dt in distractor_types if dt == "same_book")
    same_book_distractors = []

    # If we need same_book distractors, generate them all at once
    if same_book_count > 0 and distractor_candidates:
        # Safety: filter out ground truth and duplicates from candidates
        gt_normalized = ground_truth.strip().lower()
        seen = {gt_normalized}
        filtered_candidates = []
        for c in distractor_candidates:
            c_normalized = c.strip().lower()
            if c_normalized not in seen:
                seen.add(c_normalized)
                filtered_candidates.append(c)

        if len(filtered_candidates) < len(distractor_candidates):
            removed = len(distractor_candidates) - len(filtered_candidates)
            print(f"  Filtered {removed} duplicate/ground-truth candidates")

        same_book_distractors = rank_candidates_by_nsp(
            passage, mask_string, filtered_candidates,
            n=same_book_count, verbose=verbose_bert
        )

    same_book_idx = 0

    # Generate each distractor
    for dtype in distractor_types:
        parsed = parse_distractor_type(dtype)

        if parsed['type'] == 'negation':
            distractor = generate_negation(ground_truth, is_clause, debug=debug)
            if distractor:
                answer_strings.append(distractor)
                answer_types.append("negation")
                answer_probabilities.append(0.0)
            else:
                print(f"  Warning: Failed to generate negation distractor")

        elif parsed['type'] == 'same_book':
            if same_book_idx < len(same_book_distractors):
                distractor = same_book_distractors[same_book_idx]
                same_book_idx += 1
                answer_strings.append(distractor)
                answer_types.append("same_book")
                answer_probabilities.append(0.0)
            else:
                print(f"  Warning: Not enough same_book candidates available")

        elif parsed['type'] == 'anachronistic':
            distractor = generate_anachronistic(
                metadata_prefix, passage, prompt, ground_truth,
                model=parsed['model'],
                metadataless=parsed['metadataless'],
                is_clause=is_clause,
                category=category,
                debug=debug
            )
            if distractor:
                answer_strings.append(distractor)
                # Include model info in type, and metadataless if applicable
                if parsed['metadataless']:
                    answer_types.append(f"anachronistic_metadataless_{parsed['model']}")
                else:
                    answer_types.append(f"anachronistic_{parsed['model']}")
                answer_probabilities.append(0.0)
            else:
                print(f"  Warning: Failed to generate anachronistic distractor ({parsed['model']})")

        else:
            print(f"  Warning: Unknown distractor type: {dtype}")

    return answer_strings, answer_types, answer_probabilities


# For testing
if __name__ == "__main__":
    # Simple test
    print("Testing distractor_generator module...")

    # Test parse_distractor_type
    test_cases = [
        "negation",
        "same_book",
        "anachronistic_gpt-oss:20b",
        "anachronistic_metadataless_mistral-small:24b"
    ]

    print("\nParsing distractor types:")
    for tc in test_cases:
        result = parse_distractor_type(tc)
        print(f"  {tc} -> {result}")

    # Test assign_metadataless_variant
    print("\nTesting metadataless assignment:")
    types = ["negation", "same_book", "same_book",
             "anachronistic_mistral-small:24b", "anachronistic_gpt-oss:20b"]
    modified = assign_metadataless_variant(list(types))
    print(f"  Original: {types}")
    print(f"  Modified: {modified}")

    print("\nModule tests complete.")

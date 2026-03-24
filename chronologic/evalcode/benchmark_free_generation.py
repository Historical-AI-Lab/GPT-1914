"""
Free-generation evaluation of benchmark questions.

Poses questions to language models and collects open-ended text answers, rather
than scoring fixed answer options as benchmark_evaluation.py does. The answers
are written to a JSON file for evaluation by a separate scoring script.

Supported backends:
  HuggingFace transformers (local models, Apple Silicon / CUDA / CPU)
  OpenAI Responses API (GPT-4.1, GPT-5, fine-tuned variants)

Usage:
  # Print formatted prompts before running (recommended first step):
  python benchmark_free_generation.py path.jsonl --show-prompts

  # Print length-spec samples:
  python benchmark_free_generation.py path.jsonl --inspect

  # Run on OpenAI model:
  python benchmark_free_generation.py gpt-4.1-2025-04-14 path.jsonl

  # Run on local HF model (5 questions for testing):
  python benchmark_free_generation.py Qwen/Qwen2.5-7B-Instruct path.jsonl -n 5

Requires (HF path):     pip install torch transformers
Requires (OpenAI path): pip install openai  +  evalcode/credentials.txt
"""

import json
import math
import random
import re
import datetime
import statistics
from pathlib import Path
from types import SimpleNamespace

# ---------------------------------------------------------------------------
# Imports from benchmark_evaluation (shared infrastructure)
# ---------------------------------------------------------------------------

from benchmark_evaluation import (
    load_model,
    is_openai_model,
    load_openai_credentials,
    _call_responses_with_retry,
    _generate_hf,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_A = (
    "You will be asked to answer a question in a way that fits the beliefs and "
    "expository style of a specific historical context. If the context described "
    "would not contain enough information to answer the question, respond simply "
    "'insufficient information.' Otherwise, answer in {length_spec}."
)

SYSTEM_PROMPT_B = (
    "Answer the question in a way that fits the beliefs and expository style of "
    "the historical context described. As a rough guideline, answer in {length_spec}."
)

_PROMPT_A_REASONING_TYPES = {"knowledge", "abstention", "inference"}


def _select_system_prompt(reasoning_type, answer_strings):
    if reasoning_type in _PROMPT_A_REASONING_TYPES:
        return SYSTEM_PROMPT_A
    for a in answer_strings:
        if isinstance(a, str):
            low = a.lower()
            if "insufficient information" in low or "i don't know" in low:
                return SYSTEM_PROMPT_A
    return SYSTEM_PROMPT_B


# ---------------------------------------------------------------------------
# Length-spec helpers
# ---------------------------------------------------------------------------

def extract_features(cleaned_answers):
    """Compute length and form features from a list of cleaned answer strings.

    Args:
        cleaned_answers: list of stripped answer strings.

    Returns:
        SimpleNamespace with fields:
            word_counts         — list[int], words per answer
            sentence_counts     — list[int], sentences per answer
            median_word_count   — float
            median_sentence_count — float
            proportion_sentence_like — float, fraction that look like sentences
            newline_count       — int, total newlines across all answers
    """
    word_counts = []
    sentence_counts = []
    sentence_like_count = 0
    total_newlines = 0

    for ans in cleaned_answers:
        words = ans.split()
        word_counts.append(len(words))

        # Split on sentence-ending punctuation
        parts = [p.strip() for p in re.split(r'[.!?]+', ans) if p.strip()]
        sentence_counts.append(max(1, len(parts)))

        # "Sentence-like": ends with terminal punctuation or has >= 8 words
        if re.search(r'[.!?]\s*$', ans) or len(words) >= 8:
            sentence_like_count += 1

        total_newlines += ans.count('\n')

    n = len(cleaned_answers)
    median_wc = statistics.median(word_counts) if word_counts else 0
    median_sc = statistics.median(sentence_counts) if sentence_counts else 1
    prop_sentence = sentence_like_count / n if n > 0 else 0.0

    return SimpleNamespace(
        word_counts=word_counts,
        sentence_counts=sentence_counts,
        median_word_count=median_wc,
        median_sentence_count=median_sc,
        proportion_sentence_like=prop_sentence,
        newline_count=total_newlines,
    )


def clamp_and_round(value, form, direction='nearest'):
    """Round value to a natural step size and clamp to a form minimum.

    Args:
        value:     raw numeric value (may be fractional).
        form:      one of 'verse', 'short_phrase', 'single_sentence',
                   'multi_sentence', 'phrase_or_sentence'.
        direction: 'floor' rounds down (for lower bounds),
                   'ceil'  rounds up   (for upper bounds),
                   'nearest' rounds to closest step (default).

    Returns:
        int: rounded, clamped value >= the form's minimum.
    """
    config = {
        'verse':              (1,  1),
        'short_phrase':       (1,  1),
        'single_sentence':    (10, 10),
        'multi_sentence':     (10, 10),
        'phrase_or_sentence': (3,  5),
    }
    minimum, step = config.get(form, (3, 5))
    if step <= 1:
        return int(max(minimum, round(value)))
    if direction == 'floor':
        return int(max(minimum, math.floor(value / step) * step))
    if direction == 'ceil':
        return int(max(minimum, math.ceil(value / step) * step))
    return int(max(minimum, round(value / step) * step))


def verbal_sentence_range(median_sent_count):
    """Convert a median sentence count to a verbal description.

    Args:
        median_sent_count: float.

    Returns:
        str: e.g. "one to two sentences".
    """
    if median_sent_count <= 1.5:
        return "one to two sentences"
    elif median_sent_count <= 2.5:
        return "two to three sentences"
    elif median_sent_count <= 4.0:
        return "three to five sentences"
    else:
        return "a short paragraph"


def make_length_spec(answer_strings, question_category):
    """Derive a verbal length guideline and max-token ceiling from sample answers.

    Does not pass the answer options to the model; they only guide the length hint.

    Args:
        answer_strings:    list of candidate answer strings (index 0 = ground truth).
        question_category: question category string (e.g. 'poetry', 'cloze_causal').

    Returns:
        tuple: (upper, length_spec_string)
            upper             — int; caller should set max_new_tokens = upper * 2
            length_spec_string — str; inserted into SYSTEM_PROMPT
    """
    if not answer_strings:
        return 50, "about 20\u201350 words"

    cleaned = [s.strip() for s in answer_strings if s.strip()]
    if not cleaned:
        return 50, "about 20\u201350 words"

    features = extract_features(cleaned)

    # --- Form detection ---
    if features.newline_count > 0 and 'poet' in (question_category or '').lower():
        form = 'verse'
    elif (features.median_word_count <= 6
          and features.proportion_sentence_like < 0.5):
        form = 'short_phrase'
    elif features.proportion_sentence_like >= 0.6:
        if features.median_sentence_count <= 1.5:
            form = 'single_sentence'
        else:
            form = 'multi_sentence'
    else:
        form = 'phrase_or_sentence'

    # --- Length summary ---
    counts = sorted(features.word_counts)
    if len(counts) >= 2:
        q1 = statistics.median(counts[:len(counts)//2])
        q3 = statistics.median(counts[(len(counts)+1)//2:])
    else:
        q1 = q3 = counts[0] if counts else 20

    lower = clamp_and_round(q1, form, direction='floor')
    upper = clamp_and_round(q3, form, direction='ceil')

    # If actual data starts below a lower bound of 10, pull the lower bound down
    # to reflect where the answers actually begin: clamp to 5 if min >= 5,
    # otherwise use the actual minimum directly.
    actual_min = counts[0]
    if lower == 10 and actual_min < 10:
        lower = 5 if actual_min >= 5 else actual_min

    # Ensure lower < upper
    if lower >= upper:
        lower = max(1, upper - (10 if upper >= 20 else 5 if upper >= 5 else 1))

    # --- Sentence vs phrase labeling ---
    # If no sample answer starts with a capital letter, call it a "phrase".
    none_capitalized = not any(s[0].isupper() for s in cleaned if s)
    unit = 'phrase' if none_capitalized else 'sentence'

    # --- Verbalization ---
    if form == 'verse':
        return 75, "lines of verse, as specified in the question"

    if form == 'short_phrase':
        if upper <= 3:
            return upper, "a few words"
        else:
            return upper, f"a short phrase of about {lower}\u2013{upper} words"

    if form == 'single_sentence':
        return upper, f"one {unit} of about {lower}\u2013{upper} words"

    if form == 'multi_sentence':
        sent_range = verbal_sentence_range(features.median_sentence_count)
        if unit == 'phrase':
            sent_range = sent_range.replace('sentences', 'phrases').replace('sentence', 'phrase')
        return upper, f"{sent_range}, about {lower}\u2013{upper} words total"

    # phrase_or_sentence fallback
    return upper, f"about {lower}\u2013{upper} words"


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

def build_prompts(question):
    """Build system and user prompts for a free-generation question.

    Args:
        question: dict with keys 'metadata_frame', 'main_question',
                  'answer_strings', 'question_category'.

    Returns:
        tuple: (system_str, user_str, max_tokens)
            system_str — system prompt with length_spec filled in
            user_str   — CONTEXT / QUESTION / ANSWER: block
            max_tokens — int; hard ceiling = upper * 2
    """
    upper, length_spec = make_length_spec(
        question.get('answer_strings', []),
        question.get('question_category', ''),
    )
    template = _select_system_prompt(
        question.get('reasoning_type', ''),
        question.get('answer_strings', []),
    )
    system_str = template.format(length_spec=length_spec)
    user_str = (
        "CONTEXT: " + question.get('metadata_frame', '')
        + "\nQUESTION: " + question.get('main_question', '')
        + "\nANSWER: "
    )
    return system_str, user_str, max(16, upper * 2), length_spec


# ---------------------------------------------------------------------------
# Generation functions
# ---------------------------------------------------------------------------

def generate_answer_openai(question, model_id, client, reasoning_effort="none"):
    """Generate a free-text answer via the OpenAI Responses API.

    Args:
        question:         benchmark question dict.
        model_id:         OpenAI model identifier string.
        client:           openai.OpenAI instance.
        reasoning_effort: one of "none", "minimal", "low", "medium", "high".

    Returns:
        tuple: (answer_str, length_spec_str)
    """
    system_str, user_str, max_tokens, length_spec = build_prompts(question)
    # For reasoning models, max_output_tokens covers thinking + answer combined.
    # Use 25000 whenever reasoning is active so thinking tokens don't crowd out
    # the answer; the length_spec in the system prompt still constrains length.
    effective_max_tokens = max_tokens if reasoning_effort == "none" else 25000
    response = _call_responses_with_retry(
        client, model_id, user_str, system_str,
        max_output_tokens=effective_max_tokens,
        reasoning_effort=reasoning_effort,
        text_format=None,
    )
    return (response.output_text or "").strip(), length_spec


def generate_answer_hf(question, model, tokenizer):
    """Generate a free-text answer using a HuggingFace causal LM.

    Prepends the system prompt to the user prompt since HF causal LMs have no
    separate system prompt channel.

    Args:
        question:  benchmark question dict.
        model:     loaded HF AutoModelForCausalLM in eval mode.
        tokenizer: matching AutoTokenizer.

    Returns:
        tuple: (answer_str, length_spec_str)
    """
    system_str, user_str, max_tokens, length_spec = build_prompts(question)
    full_prompt = system_str + "\n" + user_str
    answer = _generate_hf(full_prompt, model, tokenizer, max_new_tokens=max_tokens)
    return answer.strip(), length_spec


# ---------------------------------------------------------------------------
# Output normalization
# ---------------------------------------------------------------------------

def normalize_answer(answer, answer_strings):
    """Normalize a model reply to match the formatting conventions of sample answers.

    Currently: if none of the sample answers end with terminal punctuation,
    silently strips any trailing punctuation from the model's reply.
    Capitalization is left untouched (proper nouns may appear first).

    Args:
        answer:         the model's raw reply string.
        answer_strings: list of sample answer strings from the benchmark question.

    Returns:
        str: normalized answer.
    """
    cleaned = [s.strip() for s in answer_strings if s.strip()]
    if cleaned and not any(re.search(r'[.!?]\s*$', s) for s in cleaned):
        answer = re.sub(r'[.!?]+\s*$', '', answer).rstrip()
    return answer


# ---------------------------------------------------------------------------
# Inspection utilities
# ---------------------------------------------------------------------------

def inspect_length_specs(path_to_jsonl, n=20):
    """Print length-spec samples for human inspection.

    Args:
        path_to_jsonl: path to benchmark JSONL file.
        n:             number of questions to sample.
    """
    questions = _load_questions(path_to_jsonl)
    sample = random.sample(questions, min(n, len(questions)))

    print(f"\n{'='*70}")
    print(f"LENGTH SPEC INSPECTION  ({len(sample)} questions from {path_to_jsonl})")
    print('='*70)

    for i, q in enumerate(sample, 1):
        upper, spec = make_length_spec(
            q.get('answer_strings', []),
            q.get('question_category', ''),
        )
        print(f"\n--- Question {i} (category: {q.get('question_category', '?')}) ---")
        print("Answer strings:")
        for ans in q.get('answer_strings', []):
            print(f"  {ans!r}")
        print(f"→ length_spec: {spec!r}  (upper={upper}, max_tokens={upper*2})")

    print(f"\n{'='*70}\n")


def show_sample_prompts(path_to_jsonl, n=5):
    """Print full formatted prompts for human inspection before running.

    Shows exactly what the model will receive: the system prompt and the
    user-facing CONTEXT / QUESTION / ANSWER block.

    Args:
        path_to_jsonl: path to benchmark JSONL file.
        n:             number of questions to sample.
    """
    questions = _load_questions(path_to_jsonl)
    sample = random.sample(questions, min(n, len(questions)))

    print(f"\n{'='*70}")
    print(f"PROMPT PREVIEW  ({len(sample)} questions from {path_to_jsonl})")
    print('='*70)

    for i, q in enumerate(sample, 1):
        system_str, user_str, max_tokens, length_spec = build_prompts(q)
        print(f"\n{'─'*70}")
        print(f"Question {i}  |  category: {q.get('question_category', '?')}  |  max_tokens: {max_tokens}")
        print(f"{'─'*70}")
        print("[SYSTEM PROMPT]")
        print(system_str)
        print()
        print("[USER PROMPT]")
        print(user_str)
        print()
        print(f"[GROUND TRUTH]  {q.get('answer_strings', ['?'])[0]!r}")

    print(f"\n{'='*70}\n")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_questions(path_to_jsonl):
    """Load all questions from a JSONL file.

    Args:
        path_to_jsonl: str or Path.

    Returns:
        list of question dicts.
    """
    questions = []
    with open(path_to_jsonl, encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if line:
                questions.append(json.loads(line))
    return questions


def _sanitize_model_id(model_id):
    """Convert a model ID to a filesystem-safe string."""
    return re.sub(r'[^a-zA-Z0-9_\-.]', '_', model_id)


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def run_free_generation(
    model_id,
    path_to_jsonl,
    output_path=None,
    credentials_path=None,
    reasoning_effort="none",
    quantize=None,
    lora_adapter=None,
    trust_remote_code=False,
    num_questions=None,
):
    """Generate free-text answers for benchmark questions and write a JSON report.

    Detects HuggingFace vs OpenAI backend from model_id.  Resumes automatically
    if the output file already exists (skips already-answered question_numbers).
    Writes the output JSON after every answer so a crash loses at most one answer.

    Args:
        model_id:          HF model path/ID or OpenAI model ID.
        path_to_jsonl:     path to benchmark JSONL file.
        output_path:       output JSON path; auto-named if None.
        credentials_path:  path to OpenAI credentials file; None = default.
        reasoning_effort:  OpenAI Responses API reasoning effort.
        quantize:          'int4' or 'int8' for HF torchao quantization; None = off.
        lora_adapter:      path to LoRA adapter; None = off.
        trust_remote_code: passed to HF from_pretrained.
        num_questions:     cap on questions to process (for testing).

    Returns:
        str: absolute path to the written JSON output file.
    """
    questions = _load_questions(path_to_jsonl)
    if num_questions is not None:
        questions = questions[:num_questions]

    # Auto-name output file
    if output_path is None:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_model = _sanitize_model_id(model_id)
        output_path = Path(path_to_jsonl).parent / f"free_gen_{safe_model}_{timestamp}.json"
    output_path = Path(output_path)

    # Load existing results for resume
    if output_path.exists():
        with open(output_path, encoding='utf-8') as fh:
            existing = json.load(fh)
        already_answered = set(existing.get('answers', {}).keys())
        answers = existing.get('answers', {})
        print(f"Resuming: {len(already_answered)} questions already answered.")
    else:
        already_answered = set()
        answers = {}

    output_data = {"model": model_id, "answers": answers}

    # Set up backend
    use_openai = is_openai_model(model_id)

    if use_openai:
        org_id, api_key = load_openai_credentials(credentials_path)
        from openai import OpenAI
        client = OpenAI(organization=org_id, api_key=api_key)
        hf_model = hf_tokenizer = None
    else:
        print(f"Loading model: {model_id}")
        hf_model, hf_tokenizer = load_model(
            model_id,
            trust_remote_code=trust_remote_code,
            quantize=quantize,
            lora_adapter=lora_adapter,
        )
        client = None

    # Generate answers
    total = len(questions)
    for idx, q in enumerate(questions):
        qnum = str(q.get('question_number', idx))
        if qnum in already_answered:
            continue

        print(f"  [{idx + 1}/{total}] question_number={qnum}", end=' ', flush=True)

        if use_openai:
            answer, length_spec = generate_answer_openai(
                q, model_id, client, reasoning_effort=reasoning_effort
            )
        else:
            answer, length_spec = generate_answer_hf(q, hf_model, hf_tokenizer)

        answer = normalize_answer(answer, q.get('answer_strings', []))
        print(f"→ {answer[:60]!r}{'...' if len(answer) > 60 else ''}")

        answers[qnum] = {
            "metadata_frame": q.get('metadata_frame', ''),
            "main_question": q.get('main_question', ''),
            "ground_truth": q.get('answer_strings', [''])[0],
            "reasoning_type": q.get('reasoning_type', ''),
            "length_spec": length_spec,
            "answer": answer,
        }

        # Write after every answer (crash-safe)
        with open(output_path, 'w', encoding='utf-8') as fh:
            json.dump(output_data, fh, indent=2, ensure_ascii=False)

    print(f"\nDone. Results written to: {output_path.resolve()}")
    return str(output_path.resolve())


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Free-generation evaluation of benchmark questions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        'model_id', nargs='?',
        help="HF model path/ID or OpenAI model ID. Omit with --inspect/--show-prompts.",
    )
    parser.add_argument(
        'path_to_jsonl',
        help="Path to benchmark JSONL question file.",
    )
    parser.add_argument(
        '--inspect', action='store_true',
        help="Print length-spec samples for 20 random questions and exit.",
    )
    parser.add_argument(
        '--show-prompts', action='store_true',
        help="Print full formatted prompts for 5 random questions and exit.",
    )
    parser.add_argument(
        '--output', metavar='PATH',
        help="Override output JSON file path.",
    )
    parser.add_argument(
        '--credentials', metavar='PATH',
        help="Path to OpenAI credentials file (default: evalcode/credentials.txt).",
    )
    parser.add_argument(
        '--reasoning-effort',
        choices=['none', 'minimal', 'low', 'medium', 'high'],
        default='none',
        help="OpenAI Responses API reasoning effort (default: none).",
    )
    parser.add_argument(
        '--quantize', choices=['int4', 'int8'],
        help="HF model quantization via torchao.",
    )
    parser.add_argument(
        '--lora-adapter', metavar='PATH',
        help="Path to LoRA adapter checkpoint (HF only).",
    )
    parser.add_argument(
        '--trust-remote-code', action='store_true',
        help="Pass trust_remote_code=True to HF from_pretrained.",
    )
    parser.add_argument(
        '-n', '--num-questions', type=int, metavar='N',
        help="Process only the first N questions (useful for testing).",
    )

    args = parser.parse_args()

    if args.inspect:
        inspect_length_specs(args.path_to_jsonl)
        return

    if args.show_prompts:
        show_sample_prompts(args.path_to_jsonl)
        return

    if not args.model_id:
        parser.error("model_id is required unless --inspect or --show-prompts is set.")

    run_free_generation(
        model_id=args.model_id,
        path_to_jsonl=args.path_to_jsonl,
        output_path=args.output,
        credentials_path=args.credentials,
        reasoning_effort=args.reasoning_effort,
        quantize=args.quantize,
        lora_adapter=args.lora_adapter,
        trust_remote_code=args.trust_remote_code,
        num_questions=args.num_questions,
    )


if __name__ == '__main__':
    main()

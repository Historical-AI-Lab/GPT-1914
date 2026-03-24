"""
Binary evaluation of free-generation answers.

Takes a JSON file of free-generated answers (from benchmark_free_generation.py)
and asks an LLM to choose between the ground-truth answer and the generated answer
for each question. The proportion of questions where ground truth is selected
measures how distinguishable the generations are from ground truth.

Supported backends:
  OpenAI Responses API (GPT-4.1, GPT-5, fine-tuned variants)
  HuggingFace transformers (local models, Apple Silicon / CUDA / CPU)

Usage:
  # Inspect sample prompts before running:
  python benchmark_binary_eval.py --show-prompts free_gen_output.json

  # Run with an OpenAI evaluator:
  python benchmark_binary_eval.py gpt-4.1-2025-04-14 free_gen_output.json

  # Run with a local HF evaluator (5 questions for testing):
  python benchmark_binary_eval.py Qwen/Qwen2.5-7B-Instruct free_gen_output.json -n 5

Requires (OpenAI path): pip install openai  +  evalcode/credentials.txt
Requires (HF path):     pip install torch transformers
"""

import difflib
import json
import random
import re
import datetime
from pathlib import Path

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

SYSTEM_PROMPT = (
    "You will be provided a historical context, a question, and two answers to "
    "the question. Decide which answer to the question is a better fit for the "
    "beliefs and writing style of the context, and then reply with only a single "
    "letter, A or B."
)

ABSTENTION_PHRASES = {"insufficient information", "i don't know", "abstain", "n/a"}

ABSTENTION_TRIAGE_MODEL = "Qwen/Qwen2.5-7B-Instruct"

# JSON schema for OpenAI structured output: constrains response to {"choice": "A"|"B"}.
# Mirrors the pattern used in benchmark_evaluation.py and eliminates unparseable responses.
BINARY_CHOICE_SCHEMA = {
    "type": "json_schema",
    "name": "binary_choice",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "choice": {"type": "string", "enum": ["A", "B"]},
        },
        "required": ["choice"],
        "additionalProperties": False,
    },
}

# Few-shot prompt for LLM-based abstention triage.  Used when reasoning_type
# is "abstention" but neither answer matches ABSTENTION_PHRASES exactly.
ABSTENTION_TRIAGE_PROMPT = """\
You are deciding whether two answers to a historical question both amount to \
refusing or declining to answer, or whether at least one gives substantive information.

Refusing to answer includes expressions like: "no longer exists", \
"not a meaningful question", "unanswerable", "insufficient information", \
"I don't know", "cannot be determined", "this question doesn't apply", \
and similar variants.

Substantive answers include actual names, dates, facts, descriptions, or any \
attempt to provide real information about the topic.

Respond with exactly BOTH_ABSTAIN if both answers refuse or decline, \
or ONE_SUBSTANTIVE if at least one answer provides real information.

A: "No longer exists"
B: "This is not a meaningful question."
→ BOTH_ABSTAIN

A: "insufficient information"
B: "The Republic of Transvaal was dissolved in 1902 after the Second Boer War."
→ ONE_SUBSTANTIVE

A: "I cannot determine this from the given context."
B: "unanswerable in context"
→ BOTH_ABSTAIN

A: "Paul Kruger"
B: "That question cannot be answered."
→ ONE_SUBSTANTIVE

A: "It no longer exists as of 1902"
B: "I don't know"
→ BOTH_ABSTAIN

A: "The question is anachronistic; the Transvaal ceased to exist in 1902."
B: "Unanswerable — this asks about a republic that no longer exists."
→ BOTH_ABSTAIN

A: {answer_a}
B: {answer_b}
→"""


# ---------------------------------------------------------------------------
# Triage
# ---------------------------------------------------------------------------

def triage(answer, ground_truth, reasoning_type):
    """Return "indistinguishable" if evaluation can be skipped, else None.

    Args:
        answer:         free-generated answer string.
        ground_truth:   ground-truth answer string.
        reasoning_type: reasoning_type field from the question.

    Returns:
        str "indistinguishable" or None.
    """
    ans_low = answer.strip().lower()
    gt_low = ground_truth.strip().lower()

    # (a) exact match (case-insensitive)
    if ans_low == gt_low:
        return "indistinguishable"

    # (b) abstention matches abstention reasoning type
    if ans_low in ABSTENTION_PHRASES and reasoning_type == "abstention":
        return "indistinguishable"

    # (c) high sequence similarity for longer strings
    if len(answer) > 19 and len(ground_truth) > 19:
        ratio = difflib.SequenceMatcher(None, ans_low, gt_low).ratio()
        if ratio > 0.94:
            return "indistinguishable"

    return None


def triage_abstention_llm(answer_a, answer_b, model, tokenizer):
    """Use an LLM to check if both answers are effectively abstentions.

    Called when reasoning_type == "abstention" and the exact-phrase check did
    not fire.  Handles paraphrased abstentions such as "No longer exists" vs
    "This is not a meaningful question."

    Args:
        answer_a: first answer string (typically the ground truth).
        answer_b: second answer string (the free-generated answer).
        model:    loaded HF AutoModelForCausalLM in eval mode.
        tokenizer: matching AutoTokenizer.

    Returns:
        str "indistinguishable" if both answers abstain, else None.
    """
    prompt = ABSTENTION_TRIAGE_PROMPT.format(answer_a=answer_a, answer_b=answer_b)
    response = _generate_hf(prompt, model, tokenizer, max_new_tokens=8)
    if "BOTH" in response.upper():
        return "indistinguishable"
    return None


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

def build_binary_prompt(question_data):
    """Build the system prompt, user prompt, and record which letter is ground truth.

    Randomly assigns ground truth to A or B.

    Args:
        question_data: dict with keys 'metadata_frame', 'main_question',
                       'ground_truth', 'answer'.

    Returns:
        tuple: (system_str, user_str, ground_truth_letter)
            system_str         — the system prompt string.
            user_str           — the user prompt string.
            ground_truth_letter — 'A' or 'B'; which letter maps to ground truth.
    """
    ground_truth = question_data["ground_truth"]
    generation = question_data["answer"]

    if random.random() < 0.5:
        option_a, option_b = ground_truth, generation
        ground_truth_letter = "A"
    else:
        option_a, option_b = generation, ground_truth
        ground_truth_letter = "B"

    user_str = (
        "CONTEXT: " + question_data.get("metadata_frame", "")
        + "\nQUESTION: " + question_data.get("main_question", "")
        + "\nA: " + option_a
        + "\nB: " + option_b
        + "\nANSWER: "
    )

    return SYSTEM_PROMPT, user_str, ground_truth_letter


def _parse_letter(response_text):
    """Extract 'A' or 'B' from a model response.

    Args:
        response_text: string output from the model.

    Returns:
        str 'A' or 'B', or None if neither found.
    """
    match = re.search(r'\b([AB])\b', response_text.strip())
    return match.group(1) if match else None


# ---------------------------------------------------------------------------
# Backend evaluation
# ---------------------------------------------------------------------------

def evaluate_openai(question_data, model_id, client, reasoning_effort="none"):
    """Evaluate one question via the OpenAI Responses API.

    Args:
        question_data:    dict from the free-generation JSON (one answer entry).
        model_id:         OpenAI model identifier string.
        client:           openai.OpenAI instance.
        reasoning_effort: one of "none", "minimal", "low", "medium", "high".

    Returns:
        str: "ground truth", "generation", or "unparseable".
    """
    system_str, user_str, ground_truth_letter = build_binary_prompt(question_data)
    # max_output_tokens covers reasoning tokens + output tokens combined.
    # Some models (e.g. gpt-5.x) emit implicit reasoning tokens even when
    # reasoning_effort="none", so 16 is too small and causes empty output_text.
    # Use 256 for the no-reasoning path (generous for the JSON payload alone)
    # and 25000 for any reasoning effort — matching the MCQ evaluator — since
    # medium/high reasoning on gpt-5.x can consume thousands of tokens before
    # emitting output.
    max_tokens = 256 if reasoning_effort == "none" else 25000
    response = _call_responses_with_retry(
        client, model_id, user_str, system_str,
        max_output_tokens=max_tokens,
        reasoning_effort=reasoning_effort,
        text_format=BINARY_CHOICE_SCHEMA,
    )
    raw = response.output_text or ""
    letter = _parse_letter(raw)
    if letter is None:
        print(f"[unparseable output_text={raw!r}]", end=" ")
        return "unparseable"
    return "ground truth" if letter == ground_truth_letter else "generation"


def evaluate_hf(question_data, model, tokenizer):
    """Evaluate one question using a HuggingFace causal LM.

    Args:
        question_data: dict from the free-generation JSON (one answer entry).
        model:         loaded HF AutoModelForCausalLM in eval mode.
        tokenizer:     matching AutoTokenizer.

    Returns:
        str: "ground truth", "generation", or "unparseable".
    """
    system_str, user_str, ground_truth_letter = build_binary_prompt(question_data)
    full_prompt = system_str + "\n" + user_str
    response = _generate_hf(full_prompt, model, tokenizer, max_new_tokens=10)
    letter = _parse_letter(response)
    if letter is None:
        return "unparseable"
    return "ground truth" if letter == ground_truth_letter else "generation"


# ---------------------------------------------------------------------------
# Inspection utilities
# ---------------------------------------------------------------------------

def show_sample_prompts(input_json_path, n=5, triage_model=None, triage_tokenizer=None):
    """Print sample binary prompts for inspection before running.

    Args:
        input_json_path: path to free-generation JSON file.
        n:               number of questions to sample.
        triage_model:    optional loaded HF model for LLM-based abstention triage.
        triage_tokenizer: matching tokenizer for triage_model.
    """
    with open(input_json_path, encoding="utf-8") as fh:
        data = json.load(fh)

    answers = data.get("answers", {})
    items = list(answers.items())
    sample = random.sample(items, min(n, len(items)))

    print(f"\n{'='*70}")
    print(f"BINARY EVAL PROMPT PREVIEW  ({len(sample)} questions from {input_json_path})")
    print(f"{'='*70}")

    for i, (qnum, qdata) in enumerate(sample, 1):
        reasoning_type = qdata.get("reasoning_type", "")
        triaged = triage(
            qdata.get("answer", ""),
            qdata.get("ground_truth", ""),
            reasoning_type,
        )
        if triaged is None and reasoning_type == "abstention":
            if triage_model is not None:
                triaged = triage_abstention_llm(
                    qdata.get("ground_truth", ""),
                    qdata.get("answer", ""),
                    triage_model,
                    triage_tokenizer,
                )
                triage_note = triaged or "no — will be posed (LLM triage: not both abstentions)"
            else:
                triage_note = "no — abstention, triage model not loaded"
        else:
            triage_note = triaged or "no — will be posed"
        print(f"\n{'─'*70}")
        print(f"Question {qnum}  |  triaged: {triage_note}")
        print(f"{'─'*70}")
        if triaged:
            print(f"[GROUND TRUTH]  {qdata.get('ground_truth', '')!r}")
            print(f"[GENERATION]    {qdata.get('answer', '')!r}")
            print(f"→ result: {triaged}")
        else:
            system_str, user_str, gt_letter = build_binary_prompt(qdata)
            print("[SYSTEM PROMPT]")
            print(system_str)
            print()
            print("[USER PROMPT]")
            print(user_str)
            print(f"[GROUND TRUTH LETTER: {gt_letter}]")

    print(f"\n{'='*70}\n")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _sanitize_model_id(model_id):
    """Convert a model ID to a filesystem-safe string."""
    return re.sub(r'[^a-zA-Z0-9_\-.]', '_', model_id)


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def run_binary_eval(
    evaluator_model_id,
    input_json_path,
    output_path=None,
    credentials_path=None,
    reasoning_effort="none",
    quantize=None,
    trust_remote_code=False,
    num_questions=None,
):
    """Run binary evaluation and write a JSON report.

    Resumes automatically if the output file already exists (skips
    already-evaluated question keys). Writes after every question so a crash
    loses at most one result.

    Args:
        evaluator_model_id: HF model path/ID or OpenAI model ID used for evaluation.
        input_json_path:    path to free-generation JSON output.
        output_path:        output JSON path; auto-named if None.
        credentials_path:   path to OpenAI credentials file; None = default.
        reasoning_effort:   OpenAI Responses API reasoning effort.
        quantize:           'int4' or 'int8' for HF torchao quantization; None = off.
        trust_remote_code:  passed to HF from_pretrained.
        num_questions:      cap on questions to evaluate (for testing).

    Returns:
        str: absolute path to the written JSON output file.
    """
    with open(input_json_path, encoding="utf-8") as fh:
        input_data = json.load(fh)

    generation_model = input_data.get("model", "unknown")
    all_answers = input_data.get("answers", {})

    items = list(all_answers.items())
    if num_questions is not None:
        items = items[:num_questions]

    # Auto-name output file
    if output_path is None:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_eval = _sanitize_model_id(evaluator_model_id)
        safe_gen = _sanitize_model_id(generation_model)
        output_path = (
            Path(input_json_path).parent
            / f"binary_eval_{safe_eval}_on_{safe_gen}_{timestamp}.json"
        )
    output_path = Path(output_path)

    # Load existing results for resume
    if output_path.exists():
        with open(output_path, encoding="utf-8") as fh:
            existing = json.load(fh)
        already_done = set(existing.get("answers", {}).keys())
        result_answers = existing.get("answers", {})
        print(f"Resuming: {len(already_done)} questions already evaluated.")
    else:
        already_done = set()
        result_answers = {}

    output_data = {
        "model": evaluator_model_id,
        "generation_model": generation_model,
        "answers": result_answers,
    }

    # Set up backend
    use_openai = is_openai_model(evaluator_model_id)

    if use_openai:
        org_id, api_key = load_openai_credentials(credentials_path)
        from openai import OpenAI
        client = OpenAI(organization=org_id, api_key=api_key)
        hf_model = hf_tokenizer = None
    else:
        print(f"Loading evaluator model: {evaluator_model_id}")
        hf_model, hf_tokenizer = load_model(
            evaluator_model_id,
            trust_remote_code=trust_remote_code,
            quantize=quantize,
        )
        client = None

    # Load abstention triage model (Qwen-2.5-7B) if any pending questions have
    # reasoning_type == "abstention".  Reuses the evaluator model when it is
    # already Qwen-2.5-7B-Instruct to avoid loading a second copy.
    pending_abstentions = any(
        qdata.get("reasoning_type") == "abstention"
        for qnum, qdata in items
        if qnum not in already_done
    )
    triage_model = triage_tokenizer = None
    if pending_abstentions:
        if not use_openai and evaluator_model_id == ABSTENTION_TRIAGE_MODEL:
            print("Reusing evaluator model for abstention triage.")
            triage_model, triage_tokenizer = hf_model, hf_tokenizer
        else:
            print(f"Loading abstention triage model: {ABSTENTION_TRIAGE_MODEL}")
            triage_model, triage_tokenizer = load_model(ABSTENTION_TRIAGE_MODEL)

    total = len(items)
    for idx, (qnum, qdata) in enumerate(items):
        if qnum in already_done:
            continue

        print(f"  [{idx + 1}/{total}] question={qnum}", end=" ", flush=True)

        ground_truth = qdata.get("ground_truth", "")
        generation = qdata.get("answer", "")
        reasoning_type = qdata.get("reasoning_type", "")

        triaged = triage(generation, ground_truth, reasoning_type)
        if triaged is None and reasoning_type == "abstention" and triage_model is not None:
            triaged = triage_abstention_llm(
                ground_truth, generation, triage_model, triage_tokenizer
            )

        if triaged:
            selected = triaged
            print(f"→ {selected} (triaged)")
        else:
            if use_openai:
                selected = evaluate_openai(
                    qdata, evaluator_model_id, client,
                    reasoning_effort=reasoning_effort,
                )
            else:
                selected = evaluate_hf(qdata, hf_model, hf_tokenizer)
            print(f"→ {selected}")

        result_answers[qnum] = {
            "ground_truth": ground_truth,
            "generation": generation,
            "selected": selected,
        }

        # Write after every answer (crash-safe)
        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(output_data, fh, indent=2, ensure_ascii=False)

    # Summary
    total_done = len(result_answers)
    n_gt = sum(1 for v in result_answers.values() if v["selected"] == "ground truth")
    n_indist = sum(1 for v in result_answers.values() if v["selected"] == "indistinguishable")
    n_gen = sum(1 for v in result_answers.values() if v["selected"] == "generation")
    n_unparse = sum(1 for v in result_answers.values() if v["selected"] == "unparseable")

    print(f"\nDone. {total_done} questions evaluated.")
    print(f"  indistinguishable: {n_indist}")
    print(f"  ground truth:      {n_gt}")
    print(f"  generation:        {n_gen}")
    if n_unparse:
        print(f"  unparseable:       {n_unparse}")
    print(f"\nResults written to: {output_path.resolve()}")

    return str(output_path.resolve())


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Binary evaluation of free-generation answers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "evaluator_model_id", nargs="?",
        help="HF model path/ID or OpenAI model ID to use as evaluator. "
             "Omit with --show-prompts.",
    )
    parser.add_argument(
        "input_json",
        help="Path to free-generation JSON output (from benchmark_free_generation.py).",
    )
    parser.add_argument(
        "--show-prompts", action="store_true",
        help="Print sample binary prompts for 5 random questions and exit.",
    )
    parser.add_argument(
        "--output", metavar="PATH",
        help="Override output JSON file path.",
    )
    parser.add_argument(
        "--credentials", metavar="PATH",
        help="Path to OpenAI credentials file (default: evalcode/credentials.txt).",
    )
    parser.add_argument(
        "--reasoning-effort",
        choices=["none", "minimal", "low", "medium", "high"],
        default="none",
        help="OpenAI Responses API reasoning effort (default: none).",
    )
    parser.add_argument(
        "--quantize", choices=["int4", "int8"],
        help="HF model quantization via torchao.",
    )
    parser.add_argument(
        "--trust-remote-code", action="store_true",
        help="Pass trust_remote_code=True to HF from_pretrained.",
    )
    parser.add_argument(
        "-n", "--num-questions", type=int, metavar="N",
        help="Evaluate only the first N questions (useful for testing).",
    )

    args = parser.parse_args()

    if args.show_prompts:
        with open(args.input_json, encoding="utf-8") as fh:
            _preview_data = json.load(fh)
        has_abstentions = any(
            v.get("reasoning_type") == "abstention"
            for v in _preview_data.get("answers", {}).values()
        )
        triage_model = triage_tokenizer = None
        if has_abstentions:
            print(f"Loading abstention triage model: {ABSTENTION_TRIAGE_MODEL}")
            triage_model, triage_tokenizer = load_model(ABSTENTION_TRIAGE_MODEL)
        show_sample_prompts(args.input_json, triage_model=triage_model,
                            triage_tokenizer=triage_tokenizer)
        return

    if not args.evaluator_model_id:
        parser.error("evaluator_model_id is required unless --show-prompts is set.")

    run_binary_eval(
        evaluator_model_id=args.evaluator_model_id,
        input_json_path=args.input_json,
        output_path=args.output,
        credentials_path=args.credentials,
        reasoning_effort=args.reasoning_effort,
        quantize=args.quantize,
        trust_remote_code=args.trust_remote_code,
        num_questions=args.num_questions,
    )


if __name__ == "__main__":
    main()

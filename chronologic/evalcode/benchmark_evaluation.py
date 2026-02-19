"""
Benchmark evaluation of benchmark questions via log-likelihood scoring and MCQ.

Primary path: HuggingFace AutoModelForCausalLM (works on Apple Silicon, CUDA, CPU).
  - Five-question sampling mode (default)
  - Full eval mode (--full-eval): scores every question, reports mean Brier score
  - MCQ mode (--mcq): presents lettered multiple-choice prompts, scores top-1 accuracy
Legacy path:  vLLM's OpenAI-compatible endpoint with echo=True (requires a running
              vLLM server; unavailable on Apple Silicon MPS).

Requires (HF path):  pip install torch transformers
Requires (vLLM path): pip install openai  +  a running vLLM server
"""

import json
import math
import random
import re
import datetime
from pathlib import Path

# HF path (primary)
HF_DEFAULT_DEVICE = None  # None → auto-detect at runtime

# vLLM path (legacy)
VLLM_BASE_URL = "http://localhost:9011/v1"
MODEL = "gpt-oss:20b"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_question_text(question, use_metadata=True):
    """Compose the prompt prefix for a question.

    Args:
        question: dict with keys 'metadata_frame' and 'main_question'.
        use_metadata: if True, prepend the metadata_frame.

    Returns:
        str ending with 'ANSWER: ' ready for answer concatenation.
    """
    if use_metadata:
        return (
            question["metadata_frame"]
            + "\nQUESTION: "
            + question["main_question"]
            + "\nANSWER: "
        )
    else:
        return "QUESTION: " + question["main_question"] + "\nANSWER: "


def _build_mcq_prompt(question, use_metadata=True, include_negation=False):
    """Build a multiple-choice prompt for a question.

    Args:
        question:         dict conforming to the benchmark question format.
        use_metadata:     if True, prepend metadata_frame to the prompt.
        include_negation: if False (default), drop entries whose answer_type
                          is 'negation'.

    Returns:
        tuple: (prompt_text, answer_order, correct_letter)
            prompt_text:   the full MCQ prompt string.
            answer_order:  list of (letter, answer_str, prob) tuples in the
                           order they appear in the prompt.
            correct_letter: the letter that corresponds to the ground-truth
                            answer (the entry with answer_probability == 1.0).
    """
    entries = list(zip(
        question["answer_strings"],
        question["answer_types"],
        question["answer_probabilities"],
    ))

    if not include_negation:
        entries = [(s, t, p) for s, t, p in entries if t != "negation"]

    random.shuffle(entries)

    letters = [chr(ord("A") + i) for i in range(len(entries))]
    answer_order = [(letter, s, p) for letter, (s, t, p) in zip(letters, entries)]

    correct_letter = None
    for letter, s, p in answer_order:
        if p == 1.0:
            correct_letter = letter
            break

    lines = []
    if use_metadata:
        lines.append(question.get("metadata_frame", ""))
    lines.append(f"QUESTION: {question['main_question']}")
    for letter, s, p in answer_order:
        lines.append(f"{letter}) {s}")
    lines.append("Respond only with the letter of the correct answer:")

    prompt_text = "\n".join(lines)
    return prompt_text, answer_order, correct_letter


def _parse_mcq_response(response_text):
    """Extract the first uppercase letter from a model response.

    Args:
        response_text: string output from the model.

    Returns:
        str: the first uppercase letter found, or None if none found.
    """
    match = re.search(r"\b[A-Z]\b", response_text)
    return match.group(0) if match else None


def _generate_hf(prompt, model, tokenizer, max_new_tokens=10):
    """Generate text from a prompt using a HuggingFace causal LM (greedy).

    Args:
        prompt:         the input prompt string.
        model:          a loaded HF AutoModelForCausalLM in eval mode.
        tokenizer:      the matching AutoTokenizer.
        max_new_tokens: maximum number of new tokens to generate.

    Returns:
        str: the newly generated text (prompt tokens excluded).
    """
    import torch

    inputs = tokenizer(prompt, return_tensors="pt")
    device = next(model.parameters()).device
    input_ids = inputs.input_ids.to(device)
    prompt_len = input_ids.shape[1]

    with torch.no_grad():
        output_ids = model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,
            do_sample=False,
        )

    new_ids = output_ids[0, prompt_len:]
    return tokenizer.decode(new_ids, skip_special_tokens=True)


def _score_answer_ll(context_text, answer_text, model_name, base_url):
    """Return the average log-probability per token for answer_text given context_text.

    Uses vLLM's echo=True mode: one API call returns logprobs for the entire
    (context + answer) sequence. Tokens at or after len(context_text) are
    treated as answer tokens; their logprobs are averaged.

    Args:
        context_text: the prompt prefix (question text ending with 'ANSWER: ').
        answer_text:  the candidate answer string.
        model_name:   model identifier passed to vLLM.
        base_url:     vLLM OpenAI-compatible endpoint URL.

    Returns:
        float: average log-prob per answer token, or 0.0 if no answer tokens.

    Raises:
        ConnectionError: if the vLLM endpoint cannot be reached.
        ImportError: if the 'openai' package is not installed.
    """
    if not answer_text:
        return 0.0

    try:
        from openai import OpenAI
    except ImportError as e:
        raise ImportError(
            "The 'openai' package is required for log-likelihood scoring. "
            "Install it with: pip install openai"
        ) from e

    try:
        client = OpenAI(base_url=base_url, api_key="EMPTY")
        response = client.completions.create(
            model=model_name,
            prompt=context_text + answer_text,
            max_tokens=1,   # generate 1 token to satisfy the API
            echo=True,      # return logprobs for the full prompt too
            logprobs=1,
        )
    except Exception as e:
        # Distinguish connection errors from other API errors
        err_str = str(e).lower()
        if any(word in err_str for word in ("connection", "refused", "unreachable", "timeout")):
            raise ConnectionError(
                f"Cannot reach vLLM endpoint at {base_url}. "
                f"Is vLLM running? Original error: {e}"
            ) from e
        raise

    token_logprobs = response.choices[0].logprobs.token_logprobs
    text_offsets = response.choices[0].logprobs.text_offset

    context_len = len(context_text)

    # Find the index of the first token that begins at or after context_text ends
    answer_start_idx = None
    for i, offset in enumerate(text_offsets):
        if offset >= context_len:
            answer_start_idx = i
            break

    if answer_start_idx is None:
        return 0.0

    # Exclude the 1 token the API generated (last entry in token_logprobs)
    answer_logprobs = token_logprobs[answer_start_idx:-1]

    if not answer_logprobs:
        return 0.0

    # The first token's logprob can be None in some API implementations
    valid = [lp for lp in answer_logprobs if lp is not None]

    if not valid:
        return 0.0

    return sum(valid) / len(valid)


def _score_answer_ll_hf(context_text, answer_text, model, tokenizer):
    """Return the average log-probability per token for answer_text given context_text.

    Uses a pre-loaded HuggingFace causal LM. Tokenizes context+answer together
    to avoid re-tokenization boundary artefacts, then uses the causal LM shift
    to read off answer-token log-probs from the forward pass.

    Args:
        context_text: the prompt prefix (question text ending with 'ANSWER: ').
        answer_text:  the candidate answer string.
        model:        a loaded HF AutoModelForCausalLM in eval mode.
        tokenizer:    the matching AutoTokenizer.

    Returns:
        float: average log-prob per answer token, or 0.0 if answer is empty or
               has zero tokens beyond the context.
    """
    if not answer_text:
        return 0.0

    import torch

    full_ids    = tokenizer(context_text + answer_text, return_tensors="pt").input_ids
    context_ids = tokenizer(context_text,               return_tensors="pt").input_ids
    answer_start = context_ids.shape[1]

    if answer_start >= full_ids.shape[1]:
        return 0.0

    device = next(model.parameters()).device
    full_ids = full_ids.to(device)

    with torch.no_grad():
        logits = model(full_ids).logits          # [1, seq_len, vocab]

    log_probs = torch.log_softmax(logits[0], dim=-1)  # [seq_len, vocab]
    answer_token_ids = full_ids[0, answer_start:]            # [n]
    answer_logprobs  = log_probs[answer_start - 1:-1, :]     # [n, vocab]
    scores = answer_logprobs[range(len(answer_token_ids)), answer_token_ids]
    return scores.mean().item()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_model(model_id, device=None, trust_remote_code=False):
    """Load a HuggingFace causal LM and tokenizer.

    Auto-detects device: mps (Apple Silicon) → cuda → cpu.
    Returns (model, tokenizer); model is in eval mode on the target device.

    Args:
        model_id:           HF model ID or local path.
        device:             device string ('mps', 'cuda', 'cpu') or None for auto.
        trust_remote_code:  passed through to HF from_pretrained calls.

    Returns:
        tuple: (model, tokenizer)
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if device is None:
        if torch.backends.mps.is_available():
            device = "mps"
        elif torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"

    tokenizer = AutoTokenizer.from_pretrained(
        model_id, trust_remote_code=trust_remote_code
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        trust_remote_code=trust_remote_code,
        torch_dtype=torch.float16 if device != "cpu" else torch.float32,
    ).to(device)
    model.eval()
    return model, tokenizer


def get_answer_lls(question, model_name, use_metadata=True, base_url=VLLM_BASE_URL):
    """Return average log-probability per token for each candidate answer (vLLM path).

    Args:
        question:     dict conforming to the benchmark question format.
        model_name:   model identifier string (e.g. 'gpt-oss:20b').
        use_metadata: if True, include metadata_frame in the prompt.
        base_url:     vLLM OpenAI-compatible endpoint URL.

    Returns:
        list[float]: one score per entry in question['answer_strings'],
                     in the same order.
    """
    full_question_text = _build_question_text(question, use_metadata)
    return [
        _score_answer_ll(full_question_text, answer, model_name, base_url)
        for answer in question["answer_strings"]
    ]


def get_answer_lls_hf(question, model, tokenizer, use_metadata=True):
    """Return average log-probability per token for each candidate answer (HF path).

    Args:
        question:     dict conforming to the benchmark question format.
        model:        a loaded HF AutoModelForCausalLM in eval mode.
        tokenizer:    the matching AutoTokenizer.
        use_metadata: if True, include metadata_frame in the prompt.

    Returns:
        list[float]: one score per entry in question['answer_strings'],
                     in the same order.
    """
    full_question_text = _build_question_text(question, use_metadata)
    return [
        _score_answer_ll_hf(full_question_text, answer, model, tokenizer)
        for answer in question["answer_strings"]
    ]


def lls_to_probabilities(log_scores):
    """Convert log-likelihood scores to a probability distribution via softmax.

    Uses the numerically stable form: subtract max before exponentiating.

    Args:
        log_scores: list of floats (average log-probs per token).

    Returns:
        list[float]: probabilities summing to 1.0, same length as log_scores.
    """
    max_score = max(log_scores)
    exp_scores = [math.exp(s - max_score) for s in log_scores]
    total = sum(exp_scores)
    return [e / total for e in exp_scores]


def calculate_brier_score(ground_truth_probs, model_probs):
    """Compute the Brier score between ground-truth and model probability distributions.

    Brier score = (1/N) * sum((p_model_i - p_gt_i) ** 2)

    A perfect model scores 0.0; a worst-case model scores 1.0 for binary
    ground truth distributions.

    Args:
        ground_truth_probs: list of floats (ground truth distribution).
        model_probs:        list of floats (model's distribution), same length.

    Returns:
        float: Brier score.
    """
    n = len(ground_truth_probs)
    return sum(
        (mp - gtp) ** 2
        for mp, gtp in zip(model_probs, ground_truth_probs)
    ) / n


def calculate_mcq_skill_score(is_correct, k, r=1):
    """Compute a chance-adjusted skill score for a single MCQ question.

    score = (observed – chance) / (1 – chance)

    where observed = 1 if correct else 0, chance = r / k.

    Expected value at chance = 0.0; perfect = 1.0; worse-than-chance = negative.
    Returns 1.0 for the degenerate case where chance == 1.0 (all options correct).

    Args:
        is_correct: bool — whether the model chose the right answer.
        k:          int  — total number of answer options presented.
        r:          int  — number of correct answers (default 1).

    Returns:
        float: skill score.
    """
    observed = 1.0 if is_correct else 0.0
    chance = r / k
    if chance == 1.0:          # degenerate: only correct answers exist
        return 1.0
    return (observed - chance) / (1.0 - chance)


def test_five_questions(model_name, path_to_jsonl, base_url=VLLM_BASE_URL):
    """Run probabilistic evaluation on 5 randomly sampled questions and write a markdown report.

    For each selected question the function calls get_answer_lls(),
    lls_to_probabilities(), and calculate_brier_score(), then writes a
    human-readable markdown report next to the JSONL file.

    Args:
        model_name:    model identifier string (e.g. 'gpt-oss:20b').
        path_to_jsonl: path to a JSONL file of benchmark questions.
        base_url:      vLLM OpenAI-compatible endpoint URL.

    Returns:
        str: absolute path to the written markdown report.
    """
    path = Path(path_to_jsonl)

    questions = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))

    selected = random.sample(questions, min(5, len(questions)))

    # Build a filesystem-safe model name for the report filename
    model_safe = model_name.replace(":", "_").replace("/", "_")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = path.parent / f"eval_report_{model_safe}_{timestamp}.md"

    lines = [f"# {model_name}\n"]

    for i, question in enumerate(selected, 1):
        lines.append(f"## Question {i}\n")
        lines.append(f"**Metadata:** {question.get('metadata_frame', '')}\n")
        lines.append(f"**Question:** {question.get('main_question', '')}\n")
        lines.append(f"**Category:** {question.get('question_category', '')}\n")

        lls = get_answer_lls(question, model_name, use_metadata=True, base_url=base_url)
        model_probs = lls_to_probabilities(lls)
        gt_probs = question["answer_probabilities"]
        brier = calculate_brier_score(gt_probs, model_probs)

        lines.append("| Answer | Type | Ground Truth Prob | Model Prob |")
        lines.append("|--------|------|-------------------|------------|")

        for ans, atype, gtp, mp in zip(
            question["answer_strings"],
            question["answer_types"],
            gt_probs,
            model_probs,
        ):
            lines.append(f"| {ans} | {atype} | {gtp:.3f} | {mp:.3f} |")

        lines.append(f"\n**Brier Score:** {brier:.4f}\n")

    report_text = "\n".join(lines)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    return str(report_path)


def test_five_questions_hf(model_id, path_to_jsonl, device=None, trust_remote_code=False):
    """Run probabilistic evaluation on 5 randomly sampled questions and write a markdown report.

    Uses the HuggingFace path. Loads the model once, then scores each question.

    Args:
        model_id:           HF model ID or local path.
        path_to_jsonl:      path to a JSONL file of benchmark questions.
        device:             device string ('mps', 'cuda', 'cpu') or None for auto.
        trust_remote_code:  passed through to HF from_pretrained calls.

    Returns:
        str: absolute path to the written markdown report.
    """
    path = Path(path_to_jsonl)

    questions = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))

    selected = random.sample(questions, min(5, len(questions)))

    model, tokenizer = load_model(model_id, device=device, trust_remote_code=trust_remote_code)

    # Build a filesystem-safe model name for the report filename
    model_safe = model_id.replace(":", "_").replace("/", "_")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = path.parent / f"eval_report_{model_safe}_{timestamp}.md"

    lines = [f"# {model_id}\n"]

    for i, question in enumerate(selected, 1):
        lines.append(f"## Question {i}\n")
        lines.append(f"**Metadata:** {question.get('metadata_frame', '')}\n")
        lines.append(f"**Question:** {question.get('main_question', '')}\n")
        lines.append(f"**Category:** {question.get('question_category', '')}\n")

        lls = get_answer_lls_hf(question, model, tokenizer, use_metadata=True)
        model_probs = lls_to_probabilities(lls)
        gt_probs = question["answer_probabilities"]
        brier = calculate_brier_score(gt_probs, model_probs)

        lines.append("| Answer | Type | Ground Truth Prob | Model Prob |")
        lines.append("|--------|------|-------------------|------------|")

        for ans, atype, gtp, mp in zip(
            question["answer_strings"],
            question["answer_types"],
            gt_probs,
            model_probs,
        ):
            lines.append(f"| {ans} | {atype} | {gtp:.3f} | {mp:.3f} |")

        lines.append(f"\n**Brier Score:** {brier:.4f}\n")

    report_text = "\n".join(lines)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    return str(report_path)


def full_eval_hf(model_id, path_to_jsonl, device=None, trust_remote_code=False):
    """Score every question in a JSONL and write a full markdown report.

    For each question: get_answer_lls_hf() → lls_to_probabilities() →
    calculate_brier_score(). Reports mean Brier score overall and broken down
    by question_category. Prints overall score to stdout.

    Args:
        model_id:           HF model ID or local path.
        path_to_jsonl:      path to a JSONL file of benchmark questions.
        device:             device string ('mps', 'cuda', 'cpu') or None for auto.
        trust_remote_code:  passed through to HF from_pretrained calls.

    Returns:
        str: absolute path to the written markdown report.
    """
    path = Path(path_to_jsonl)

    questions = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))

    model, tokenizer = load_model(model_id, device=device, trust_remote_code=trust_remote_code)

    model_safe = model_id.replace(":", "_").replace("/", "_")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = path.parent / f"eval_report_full_{model_safe}_{timestamp}.md"

    all_brier_scores = []
    category_scores = {}  # category → list of brier scores
    per_question_blocks = []

    for i, question in enumerate(questions, 1):
        lls = get_answer_lls_hf(question, model, tokenizer, use_metadata=True)
        model_probs = lls_to_probabilities(lls)
        gt_probs = question["answer_probabilities"]
        brier = calculate_brier_score(gt_probs, model_probs)

        all_brier_scores.append(brier)
        category = question.get("question_category", "unknown")
        category_scores.setdefault(category, []).append(brier)

        block = []
        block.append(f"## Question {i}\n")
        block.append(f"**Metadata:** {question.get('metadata_frame', '')}\n")
        block.append(f"**Question:** {question.get('main_question', '')}\n")
        block.append(f"**Category:** {category}\n")
        block.append("| Answer | Type | Ground Truth Prob | Model Prob |")
        block.append("|--------|------|-------------------|------------|")
        for ans, atype, gtp, mp in zip(
            question["answer_strings"],
            question["answer_types"],
            gt_probs,
            model_probs,
        ):
            block.append(f"| {ans} | {atype} | {gtp:.3f} | {mp:.3f} |")
        block.append(f"\n**Brier Score:** {brier:.4f}\n")
        per_question_blocks.append("\n".join(block))

    overall_mean = sum(all_brier_scores) / len(all_brier_scores) if all_brier_scores else 0.0
    by_category = {cat: sum(scores) / len(scores) for cat, scores in category_scores.items()}

    # Build summary table
    summary_lines = [
        f"# Full Eval — {model_id}\n",
        "## Summary\n",
        "| Metric | Mean Brier Score |",
        "|--------|-----------------|",
        f"| **Overall** | {overall_mean:.4f} |",
    ]
    for cat, mean_brier in sorted(by_category.items()):
        summary_lines.append(f"| {cat} | {mean_brier:.4f} |")
    summary_lines.append("")

    report_text = "\n".join(summary_lines) + "\n" + "\n\n".join(per_question_blocks)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"Overall Brier score: {overall_mean:.4f}")
    return str(report_path)


def mcq_eval_hf(model_id, path_to_jsonl, device=None, trust_remote_code=False,
                include_negation=False):
    """Evaluate a model on multiple-choice questions and write a markdown report.

    For each question: build a lettered MCQ prompt, generate a response, parse
    the chosen letter, check against the correct letter. Reports top-1 accuracy
    overall and by question_category. Prints overall accuracy to stdout.

    Args:
        model_id:           HF model ID or local path.
        path_to_jsonl:      path to a JSONL file of benchmark questions.
        device:             device string ('mps', 'cuda', 'cpu') or None for auto.
        trust_remote_code:  passed through to HF from_pretrained calls.
        include_negation:   if True, include negation-type answers as distractors.

    Returns:
        str: absolute path to the written markdown report.
    """
    path = Path(path_to_jsonl)

    questions = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))

    model, tokenizer = load_model(model_id, device=device, trust_remote_code=trust_remote_code)

    model_safe = model_id.replace(":", "_").replace("/", "_")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = path.parent / f"eval_report_mcq_{model_safe}_{timestamp}.md"

    correct_total = 0
    category_results = {}  # category → [correct_count, total_count]
    all_skill_scores = []
    category_skill = {}   # category → list of per-question skill scores
    per_question_blocks = []

    for i, question in enumerate(questions, 1):
        prompt_text, answer_order, correct_letter = _build_mcq_prompt(
            question, use_metadata=True, include_negation=include_negation
        )
        response_text = _generate_hf(prompt_text, model, tokenizer, max_new_tokens=10)
        chosen_letter = _parse_mcq_response(response_text)

        is_correct = chosen_letter == correct_letter
        if is_correct:
            correct_total += 1

        category = question.get("question_category", "unknown")
        if category not in category_results:
            category_results[category] = [0, 0]
        if is_correct:
            category_results[category][0] += 1
        category_results[category][1] += 1

        k = len(answer_order)
        r = sum(1 for _, _, p in answer_order if p == 1.0)
        skill = calculate_mcq_skill_score(is_correct, k, r)
        all_skill_scores.append(skill)
        category_skill.setdefault(category, []).append(skill)

        result_str = "TRUE" if is_correct else "FALSE"

        block = []
        block.append(f"## Question {i}\n")
        block.append(f"**Metadata:** {question.get('metadata_frame', '')}\n")
        block.append(f"**Question:** {question.get('main_question', '')}\n")
        block.append(f"**Category:** {category}\n")
        block.append("**Choices:**")
        for letter, ans_str, prob in answer_order:
            markers = []
            if letter == chosen_letter:
                markers.append("←")
            if prob == 1.0:
                markers.append("(ground truth)")
            marker_str = " ".join(markers)
            block.append(f"- {letter}) {ans_str} {marker_str}".strip())
        block.append(f"\n**Model response:** `{response_text.strip()}`")
        block.append(f"**Chosen:** {chosen_letter}  **Correct:** {correct_letter}  **Result:** {result_str}")
        block.append(f"**Skill Score:** {skill:.4f}\n")
        per_question_blocks.append("\n".join(block))

    total = len(questions)
    overall_accuracy = correct_total / total if total > 0 else 0.0
    by_category = {
        cat: counts[0] / counts[1] if counts[1] > 0 else 0.0
        for cat, counts in category_results.items()
    }
    overall_mean_skill = sum(all_skill_scores) / len(all_skill_scores) if all_skill_scores else 0.0
    by_category_skill = {cat: sum(s) / len(s) for cat, s in category_skill.items()}

    summary_lines = [
        f"# MCQ Eval — {model_id}\n",
        "## Summary\n",
        "| Metric | Accuracy | Skill Score |",
        "|--------|----------|-------------|",
        f"| **Overall** | {overall_accuracy:.1%} | {overall_mean_skill:.4f} |",
    ]
    for cat in sorted(by_category.keys()):
        acc = by_category[cat]
        skill_avg = by_category_skill.get(cat, 0.0)
        summary_lines.append(f"| {cat} | {acc:.1%} | {skill_avg:.4f} |")
    summary_lines.append("")

    report_text = "\n".join(summary_lines) + "\n" + "\n\n".join(per_question_blocks)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"Overall MCQ accuracy: {overall_accuracy:.1%}")
    print(f"Overall MCQ skill score: {overall_mean_skill:.4f}")
    return str(report_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Evaluate a model on benchmark questions (Brier score or MCQ accuracy)."
    )
    parser.add_argument("model_id",      help="HF model ID or local path (HF mode); "
                                              "vLLM model name (--vllm mode)")
    parser.add_argument("path_to_jsonl", help="Path to benchmark questions JSONL")
    parser.add_argument("--vllm",        action="store_true",
                        help="Use legacy vLLM endpoint instead of HuggingFace")
    parser.add_argument("--device",      default=None,
                        help="Device override: mps | cuda | cpu (HF mode only)")
    parser.add_argument("--trust-remote-code", action="store_true",
                        help="Pass trust_remote_code=True to HF (HF mode only)")

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--full-eval", action="store_true",
                            help="Score every question; report mean Brier score (HF mode only)")
    mode_group.add_argument("--mcq",       action="store_true",
                            help="Present MCQ prompts; report top-1 accuracy (HF mode only)")

    parser.add_argument("--include-negation", action="store_true",
                        help="Include negation-type answers in MCQ distractors (--mcq only)")

    args = parser.parse_args()

    if args.vllm:
        report = test_five_questions(args.model_id, args.path_to_jsonl)
    elif args.full_eval:
        report = full_eval_hf(
            args.model_id, args.path_to_jsonl,
            device=args.device,
            trust_remote_code=args.trust_remote_code,
        )
    elif args.mcq:
        report = mcq_eval_hf(
            args.model_id, args.path_to_jsonl,
            device=args.device,
            trust_remote_code=args.trust_remote_code,
            include_negation=args.include_negation,
        )
    else:
        report = test_five_questions_hf(
            args.model_id, args.path_to_jsonl,
            device=args.device,
            trust_remote_code=args.trust_remote_code,
        )
    print(f"Report written to: {report}")

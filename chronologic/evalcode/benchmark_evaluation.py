"""
Benchmark evaluation of benchmark questions via log-likelihood scoring and MCQ.

Primary path: HuggingFace AutoModelForCausalLM (works on Apple Silicon, CUDA, CPU).
  - Five-question sampling mode (default)
  - Full eval mode (--full-eval): scores every question, reports mean Brier score
  - MCQ mode (--mcq): presents lettered multiple-choice prompts, scores top-1 accuracy
Together AI path: Together's OpenAI-compatible API for probabilistic and MCQ eval.
  - Select with --api together
  - Probabilistic eval (--full-eval): uses completions endpoint with echo=True
  - MCQ eval (--mcq): uses chat completions endpoint
  - API key loaded from evalcode/TogetherAPIKey.txt (or --together-key)
OpenAI API path: Responses API for GPT-4.1, GPT-5, and fine-tuned variants.
  - MCQ mode only (--mcq): auto-detected when model name matches a known OpenAI pattern
  - Credentials loaded from evalcode/credentials.txt (org ID line 1, API key line 2)
  - Retry logic with exponential backoff for rate-limit errors
  - Reasoning effort controllable via --reasoning-effort (none/minimal/low/medium/high)
  - JSON schema structured output on by default; disable with --no-json-schema
Legacy path:  vLLM's OpenAI-compatible endpoint with echo=True (requires a running
              vLLM server; unavailable on Apple Silicon MPS).

Requires (HF path):      pip install torch transformers
Requires (vLLM path):    pip install openai  +  a running vLLM server
Requires (Together path): pip install openai  +  evalcode/TogetherAPIKey.txt
Requires (OpenAI path):  pip install openai  +  evalcode/credentials.txt
"""

import json
import math
import random
import re
import datetime
from pathlib import Path

import numpy as np

# HF path (primary)
HF_DEFAULT_DEVICE = None  # None → auto-detect at runtime

# vLLM path (legacy)
VLLM_BASE_URL = "http://localhost:9011/v1"
MODEL = "gpt-oss:20b"

# Together AI path
TOGETHER_BASE_URL = "https://api.together.xyz/v1"

# OpenAI API path
# Model ID prefixes that indicate an OpenAI-hosted model (including fine-tunes).
# is_openai_model() uses startswith() against this tuple.
OPENAI_MODEL_PREFIXES = (
    "gpt-4.1-",
    "gpt-4.1",   # exact match covered by startswith too
    "gpt-5.",
    "gpt-5-",
    "gpt-5",     # covers "gpt-5" exactly and any gpt-5* without a separator
    "ft:gpt-4.1-",
    "ft:gpt-4.1",
    "ft:gpt-5.",
    "ft:gpt-5-",
    "ft:gpt-5",
)


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
    device = _input_device(model)
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


def _score_answer_ll(context_text, answer_text, model_name, base_url, api_key="EMPTY"):
    """Return the average log-probability per token for answer_text given context_text.

    Uses echo=True mode on an OpenAI-compatible completions endpoint: one API
    call returns logprobs for the entire (context + answer) sequence. Tokens at
    or after len(context_text) are treated as answer tokens; their logprobs are
    averaged.

    Works with vLLM (api_key="EMPTY") and Together AI (real api_key,
    base_url=TOGETHER_BASE_URL).

    Args:
        context_text: the prompt prefix (question text ending with 'ANSWER: ').
        answer_text:  the candidate answer string.
        model_name:   model identifier.
        base_url:     OpenAI-compatible endpoint URL.
        api_key:      API key string (default 'EMPTY' for local vLLM).

    Returns:
        float: average log-prob per answer token, or 0.0 if no answer tokens.

    Raises:
        ConnectionError: if the endpoint cannot be reached.
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
        client = OpenAI(base_url=base_url, api_key=api_key)
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

    device = _input_device(model)
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

def _input_device(model):
    """Return the device where input tensors should be placed.

    For device_map='auto' models, this is the device of the first parameter
    (embedding layer). For single-device models, same result.
    """
    return next(model.parameters()).device


def load_model(model_id, device=None, device_map=None, trust_remote_code=False, quantize=None, lora_adapter=None):
    """Load a HuggingFace causal LM and tokenizer.

    Auto-detects device: mps (Apple Silicon) → cuda → cpu.
    Returns (model, tokenizer); model is in eval mode on the target device.

    Args:
        model_id:           HF model ID or local path.
        device:             device string ('mps', 'cuda', 'cpu') or None for auto.
                            Mutually exclusive with device_map.
        device_map:         HF Accelerate device_map (e.g. 'auto') for multi-GPU
                            inference; None to use single-device mode (default).
                            Mutually exclusive with quantize.
        trust_remote_code:  passed through to HF from_pretrained calls.
        quantize:           'int4' or 'int8' to use torchao quantization (works on
                            MPS and CUDA); None for full-precision float16 (default).
                            Requires: pip install torchao
        lora_adapter:       path to a LoRA/QLoRA adapter checkpoint to attach to the
                            base model after loading; None to skip (default).
                            Requires: pip install peft

    Returns:
        tuple: (model, tokenizer)
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if device_map is not None and quantize is not None:
        raise ValueError(
            "--device-map and --quantize are mutually exclusive: "
            "torchao quantize-then-move does not work with sharded models."
        )

    if device_map is None:
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

    # Workaround for transformers 5.3.0: Mistral-Small-3.1 uses Mistral3Config but
    # is registered only under AutoModelForImageTextToText (it's a VLM). Register
    # Mistral3ForConditionalGeneration with AutoModelForCausalLM so text-only
    # log-likelihood scoring works normally.
    try:
        from transformers.models.mistral3 import (
            Mistral3Config, Mistral3ForConditionalGeneration
        )
        AutoModelForCausalLM.register(Mistral3Config, Mistral3ForConditionalGeneration)
    except (ImportError, AttributeError):
        pass

    if device_map is not None:
        # Multi-GPU / Accelerate path: let HF shard the model across devices.
        # Do NOT call .to(device) — Accelerate handles placement via dispatch hooks.
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            trust_remote_code=trust_remote_code,
            torch_dtype=torch.bfloat16,
            device_map=device_map,
        )
    elif quantize is not None:
        # Use torchao directly — bypasses transformers' TorchAoConfig wrapper,
        # which has a fragile dependency on torchao's internal API names.
        from torchao.quantization import quantize_
        if quantize == "int4":
            from torchao.quantization import Int4WeightOnlyConfig
            quant_config = Int4WeightOnlyConfig()
        elif quantize == "int8":
            from torchao.quantization import Int8WeightOnlyConfig
            quant_config = Int8WeightOnlyConfig()
        else:
            raise ValueError(f"--quantize must be 'int4' or 'int8', got '{quantize}'")
        # Load on CPU first: MPS cannot allocate the full bfloat16 model as a
        # single contiguous buffer. Quantize in-place on CPU (~12GB result),
        # then move the small quantized model to the target device.
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            trust_remote_code=trust_remote_code,
            dtype=torch.bfloat16,
            device_map="cpu",
        )
        quantize_(model, quant_config)
        model = model.to(device)
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            trust_remote_code=trust_remote_code,
            dtype=torch.float16 if device != "cpu" else torch.float32,
        ).to(device)

    model.eval()

    if lora_adapter is not None:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, lora_adapter)
        model.eval()

    return model, tokenizer


def get_answer_lls(question, model_name, use_metadata=True, base_url=VLLM_BASE_URL,
                   api_key="EMPTY"):
    """Return average log-probability per token for each candidate answer.

    Uses an OpenAI-compatible completions endpoint with echo=True. Works with
    vLLM (default) and Together AI (pass base_url=TOGETHER_BASE_URL and a real
    api_key).

    Args:
        question:     dict conforming to the benchmark question format.
        model_name:   model identifier string (e.g. 'gpt-oss:20b').
        use_metadata: if True, include metadata_frame in the prompt.
        base_url:     OpenAI-compatible endpoint URL.
        api_key:      API key string (default 'EMPTY' for local vLLM).

    Returns:
        list[float]: one score per entry in question['answer_strings'],
                     in the same order.
    """
    full_question_text = _build_question_text(question, use_metadata)
    return [
        _score_answer_ll(full_question_text, answer, model_name, base_url, api_key)
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


# ---------------------------------------------------------------------------
# Subset indexing, Platt scaling, and bootstrap evaluation
# ---------------------------------------------------------------------------

DEFAULT_SUBSET_FIELDS = [
    "question_category", "answer_length", "frame_type", "reasoning_type",
]


def build_subset_index(questions, fields=None):
    """Build a dictionary mapping 'field:value' keys to lists of question indices.

    Args:
        questions: list of question dicts.
        fields:    list of field names to index (default: DEFAULT_SUBSET_FIELDS).

    Returns:
        dict: e.g. {"question_category:cloze_causalclause": [0, 3, 7], ...}
    """
    if fields is None:
        fields = DEFAULT_SUBSET_FIELDS

    index = {}
    for i, q in enumerate(questions):
        for field in fields:
            if field not in q:
                continue
            key = f"{field}:{q[field]}"
            index.setdefault(key, []).append(i)
    return index


def _fit_platt_params(x, y, w):
    """Fit 2-parameter Platt scaling: p = sigmoid(a*x + b).

    Uses scipy.optimize.minimize to find (a, b) that minimise weighted
    negative log-likelihood.

    Args:
        x: 1-d array of per-option log-probabilities (unbounded).
        y: 1-d array of ground-truth probabilities (1.0 = correct, 0.0 = incorrect,
           intermediate values allowed).
        w: 1-d array of sample weights (bootstrap counts).

    Returns:
        tuple: (a, b) — the fitted affine parameters.
    """
    from scipy.optimize import minimize

    # Clip to avoid log(0)
    eps = 1e-12

    def neg_log_likelihood(params):
        a, b = params
        logits = a * x + b
        # Numerically stable sigmoid
        p = 1.0 / (1.0 + np.exp(-np.clip(logits, -500, 500)))
        p = np.clip(p, eps, 1.0 - eps)
        ll = w * (y * np.log(p) + (1.0 - y) * np.log(1.0 - p))
        return -ll.sum()

    result = minimize(neg_log_likelihood, x0=[1.0, 0.0], method="Nelder-Mead")
    return result.x[0], result.x[1]


def _raw_sigmoid_probs(logprobs):
    """Convert log-probs to option-level probabilities via sigmoid.

    This is the uncalibrated baseline: equivalent to Platt with a=1, b=0.

    Args:
        logprobs: list or array of per-option log-probabilities.

    Returns:
        list[float]: independent probabilities (may not sum to 1).
    """
    arr = np.array(logprobs, dtype=float)
    return (1.0 / (1.0 + np.exp(-np.clip(arr, -500, 500)))).tolist()


def _apply_platt(logprobs, a, b):
    """Apply Platt calibration: p_i = sigmoid(a * x_i + b) for each option.

    Each option is treated as an independent binary event, matching the
    benchmark's semantics (multiple correct answers and fractional ground
    truth are allowed).

    Args:
        logprobs: list or array of per-option log-probabilities.
        a, b:     Platt affine parameters.

    Returns:
        list[float]: calibrated probabilities (independent, may not sum to 1).
    """
    arr = np.array(logprobs, dtype=float)
    logits = a * arr + b
    return (1.0 / (1.0 + np.exp(-np.clip(logits, -500, 500)))).tolist()


def platt_scale_cv(gt_probs_list, model_logprobs_list, weights, n_folds=5):
    """Cross-validated Platt scaling with option-level sigmoid calibration.

    Both uncalibrated and calibrated Brier scores use sigmoid probabilities,
    ensuring they're in the same probability space. Uncalibrated = sigmoid(x),
    calibrated = sigmoid(a*x + b).

    Args:
        gt_probs_list:       list of ground-truth probability vectors.
        model_logprobs_list: list of per-option log-probability vectors.
        weights:             list/array of per-question weights (e.g. bootstrap counts).
        n_folds:             number of CV folds.

    Returns:
        tuple: (calibrated_brier, uncalibrated_brier) — both lists of floats,
               one per question.
    """
    n = len(gt_probs_list)
    weights = np.array(weights, dtype=float)

    # Assign folds: deterministic round-robin on indices
    fold_ids = np.array([i % n_folds for i in range(n)])

    # Pre-compute per-question uncalibrated Brier scores via sigmoid
    uncalibrated_brier = [
        calculate_brier_score(gt, _raw_sigmoid_probs(lp))
        for gt, lp in zip(gt_probs_list, model_logprobs_list)
    ]

    calibrated_brier = [0.0] * n

    for fold in range(n_folds):
        test_mask = fold_ids == fold
        train_mask = ~test_mask

        # Build training data: for each training question, each answer option
        # contributes a (log-prob, ground_truth_label) pair weighted by the
        # question's bootstrap weight.
        train_x = []
        train_y = []
        train_w = []
        for idx in np.where(train_mask)[0]:
            qw = weights[idx]
            for lp_val, gt_val in zip(model_logprobs_list[idx], gt_probs_list[idx]):
                train_x.append(lp_val)
                train_y.append(gt_val)
                train_w.append(qw)

        train_x = np.array(train_x)
        train_y = np.array(train_y)
        train_w = np.array(train_w)

        # Need positive-weight samples with both 0 and 1 labels to fit
        effective_w = train_w.sum()
        has_both = (train_y[train_w > 0].min() < 0.5 and
                    train_y[train_w > 0].max() > 0.5) if effective_w > 0 else False
        if effective_w < 1e-12 or train_mask.sum() < 2 or not has_both:
            # Can't calibrate; fall back to uncalibrated
            for i in np.where(test_mask)[0]:
                calibrated_brier[i] = uncalibrated_brier[i]
            continue

        a, b = _fit_platt_params(train_x, train_y, train_w)

        for i in np.where(test_mask)[0]:
            cal_probs = _apply_platt(model_logprobs_list[i], a, b)
            calibrated_brier[i] = calculate_brier_score(
                gt_probs_list[i], cal_probs
            )

    return calibrated_brier, uncalibrated_brier


def bootstrap_evaluate(gt_probs_list, model_results, subset_index,
                       mode, n_bootstrap=1000, n_folds=5,
                       model_logprobs=None, model_logodds=None):
    """Bootstrap confidence intervals for Brier, skill, and accuracy scores.

    Args:
        gt_probs_list:  list of ground-truth probability vectors.
        model_results:  if mode == "probabilistic", list of model probability vectors;
                        if mode == "mcq", list of dicts {"is_correct": bool, "k": int}.
        subset_index:   dict from build_subset_index().
        mode:           "probabilistic" or "mcq".
        n_bootstrap:    number of bootstrap iterations.
        n_folds:        CV folds for Platt scaling (probabilistic mode only).
        model_logprobs: list of per-option log-probability vectors (probabilistic mode).
                        Required when mode == "probabilistic".
        model_logodds:  deprecated alias for model_logprobs (backward compat).

    Returns:
        dict: {"overall_benchmark": {"brier_score": [p2.5, p50, p97.5], ...}, ...}
    """
    # Backward compat: accept model_logodds as alias for model_logprobs
    if model_logprobs is None and model_logodds is not None:
        model_logprobs = model_logodds

    n = len(gt_probs_list)
    rng = np.random.default_rng()

    # Pre-compute per-question correctness and k values
    if mode == "probabilistic":
        per_q_correct = np.array([
            (np.argmax(mp) == np.argmax(gt))
            for mp, gt in zip(model_results, gt_probs_list)
        ], dtype=float)
        per_q_k = np.array([len(gt) for gt in gt_probs_list])
    else:  # mcq
        per_q_correct = np.array(
            [r["is_correct"] for r in model_results], dtype=float
        )
        per_q_k = np.array([r["k"] for r in model_results])

    # Per-question skill scores (static, don't depend on weights)
    per_q_skill = np.array([
        calculate_mcq_skill_score(bool(c), int(k))
        for c, k in zip(per_q_correct, per_q_k)
    ])

    # All subsets we need to report on (including overall)
    all_subsets = {"overall_benchmark": np.arange(n)}
    for key, indices in subset_index.items():
        all_subsets[key] = np.array(indices)

    # Collectors: subset → list of (brier, skill, accuracy) per bootstrap iteration
    collectors = {key: {"brier": [], "skill": [], "accuracy": []}
                  for key in all_subsets}

    for _ in range(n_bootstrap):
        # Draw bootstrap sample → weight vector
        counts = np.bincount(rng.integers(0, n, size=n), minlength=n)
        weights = counts.astype(float)

        # Get per-question Brier scores for this bootstrap
        if mode == "probabilistic":
            per_q_brier, _ = platt_scale_cv(
                gt_probs_list, model_logprobs, weights,
                n_folds=n_folds
            )
            per_q_brier = np.array(per_q_brier)
        else:
            per_q_brier = np.zeros(n)

        # Compute weighted means for each subset
        for key, indices in all_subsets.items():
            w = weights[indices]
            w_sum = w.sum()
            if w_sum < 1e-12:
                collectors[key]["brier"].append(0.0)
                collectors[key]["skill"].append(0.0)
                collectors[key]["accuracy"].append(0.0)
                continue

            collectors[key]["brier"].append(
                (w * per_q_brier[indices]).sum() / w_sum
            )
            collectors[key]["skill"].append(
                (w * per_q_skill[indices]).sum() / w_sum
            )
            collectors[key]["accuracy"].append(
                (w * per_q_correct[indices]).sum() / w_sum
            )

    # Compute percentiles
    result = {}
    for key in all_subsets:
        result[key] = {}
        for metric in ("brier_score", "skill_score", "accuracy"):
            short = metric.replace("_score", "").replace("brier_score", "brier")
            # Map metric names to collector keys
            ckey = {"brier_score": "brier", "skill_score": "skill",
                    "accuracy": "accuracy"}[metric]
            vals = np.array(collectors[key][ckey])
            p2_5, p50, p97_5 = np.percentile(vals, [2.5, 50, 97.5])
            result[key][metric] = [float(p2_5), float(p50), float(p97_5)]

    return result


def write_json_report(report_path, metadata, per_question_results,
                      confidence_intervals, correct_vector):
    """Write the machine-readable JSON evaluation report.

    Args:
        report_path:          Path (or str) for the output file.
        metadata:             dict with model_id, benchmark_file, eval_mode, etc.
        per_question_results: list of dicts (model_probs, chosen_letter, correct).
        confidence_intervals: dict from bootstrap_evaluate().
        correct_vector:       list of bools.
    """
    report = {
        "metadata": metadata,
        "per_question_results": per_question_results,
        "confidence_intervals": confidence_intervals,
        "correct_vector": correct_vector,
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


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


def test_five_questions_hf(model_id, path_to_jsonl, device=None,
                           trust_remote_code=False, verbose_report=True,
                           n_bootstrap=1000, quantize=None, lora_adapter=None,
                           device_map=None):
    """Run probabilistic evaluation on 5 randomly sampled questions.

    Uses the HuggingFace path. Loads the model once, then scores each question.
    Runs bootstrap evaluation with cross-validated Platt scaling, writes a JSON
    report, and (by default) a verbose per-question markdown report.

    Args:
        model_id:           HF model ID or local path.
        path_to_jsonl:      path to a JSONL file of benchmark questions.
        device:             device string ('mps', 'cuda', 'cpu') or None for auto.
        trust_remote_code:  passed through to HF from_pretrained calls.
        verbose_report:     if True (default), also write a per-question markdown report.
        n_bootstrap:        number of bootstrap iterations for confidence intervals.

    Returns:
        str: absolute path to the written JSON report.
    """
    path = Path(path_to_jsonl)

    questions = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))

    selected = random.sample(questions, min(5, len(questions)))

    model, tokenizer = load_model(model_id, device=device, device_map=device_map,
                                  trust_remote_code=trust_remote_code,
                                  quantize=quantize, lora_adapter=lora_adapter)

    model_safe = model_id.replace(":", "_").replace("/", "_")
    if lora_adapter is not None:
        model_safe += "_" + Path(lora_adapter).name
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_report_path = path.parent / f"eval_results_{model_safe}_{timestamp}.json"
    md_report_path = path.parent / f"eval_report_{model_safe}_{timestamp}.md"

    total = len(selected)
    all_brier_scores = []
    all_model_probs = []
    all_model_logprobs = []
    all_gt_probs = []
    category_scores = {}
    scoring_fail_total = 0
    category_scoring_fail = {}
    per_question_blocks = []

    for i, question in enumerate(selected, 1):
        lls = get_answer_lls_hf(question, model, tokenizer, use_metadata=True)
        all_model_logprobs.append(lls)

        scoring_failed = all(ll == 0.0 for ll in lls)
        category = question.get("question_category", "unknown")
        if scoring_failed:
            scoring_fail_total += 1
            print(f"  WARNING: all log-likelihoods are 0.0 for question {i} "
                  f"(category: {category}) — scoring may have failed "
                  f"(empty answer tokens?)")
        model_probs = lls_to_probabilities(lls)
        gt_probs = question["answer_probabilities"]
        brier = calculate_brier_score(gt_probs, model_probs)

        all_brier_scores.append(brier)
        all_model_probs.append(model_probs)
        all_gt_probs.append(gt_probs)
        category_scores.setdefault(category, []).append(brier)
        if scoring_failed:
            category_scoring_fail[category] = category_scoring_fail.get(category, 0) + 1

        fail_note = "  ⚠ SCORING FAILURE (all LLs = 0.0)" if scoring_failed else ""
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
        block.append(f"\n**Brier Score:** {brier:.4f}{fail_note}\n")
        per_question_blocks.append("\n".join(block))

    overall_mean = sum(all_brier_scores) / len(all_brier_scores) if all_brier_scores else 0.0
    scoring_fail_rate = scoring_fail_total / total if total > 0 else 0.0

    correct_vector = [
        bool(np.argmax(mp) == np.argmax(gt))
        for mp, gt in zip(all_model_probs, all_gt_probs)
    ]
    per_question_results = [
        {"model_probs": mp, "chosen_letter": None, "correct": c}
        for mp, c in zip(all_model_probs, correct_vector)
    ]

    subset_index = build_subset_index(selected)
    confidence_intervals = bootstrap_evaluate(
        all_gt_probs, all_model_probs, subset_index,
        mode="probabilistic", n_bootstrap=n_bootstrap,
        model_logprobs=all_model_logprobs,
    )

    meta = {
        "model_id": model_id,
        "benchmark_file": str(path),
        "eval_mode": "probabilistic",
        "timestamp": timestamp,
        "n_questions": total,
        "n_bootstrap": n_bootstrap,
    }
    write_json_report(json_report_path, meta, per_question_results,
                      confidence_intervals, correct_vector)

    if verbose_report:
        by_category = {cat: sum(scores) / len(scores)
                       for cat, scores in category_scores.items()}
        summary_lines = [
            f"# Five-Question Smoke Test — {model_id}\n",
            "## Summary\n",
            f"**Scoring failure rate:** {scoring_fail_rate:.1%} "
            f"({scoring_fail_total} of {total} questions had all-zero log-likelihoods)\n",
            "| Metric | Mean Brier Score | Scoring Failures |",
            "|--------|-----------------|-----------------|",
            f"| **Overall** | {overall_mean:.4f} | {scoring_fail_total} / {total} |",
        ]
        for cat, mean_brier in sorted(by_category.items()):
            cat_total = len(category_scores[cat])
            cat_fails = category_scoring_fail.get(cat, 0)
            summary_lines.append(f"| {cat} | {mean_brier:.4f} | {cat_fails} / {cat_total} |")
        summary_lines.append("")

        report_text = "\n".join(summary_lines) + "\n" + "\n\n".join(per_question_blocks)
        with open(md_report_path, "w", encoding="utf-8") as f:
            f.write(report_text)

    print(f"Overall Brier score: {overall_mean:.4f}")
    print(f"Scoring failure rate: {scoring_fail_rate:.1%} "
          f"({scoring_fail_total} of {total} questions had all-zero log-likelihoods)")
    print(f"JSON report: {json_report_path}")
    return str(json_report_path)


def full_eval_hf(model_id, path_to_jsonl, device=None, trust_remote_code=False,
                 verbose_report=False, n_bootstrap=1000, quantize=None, lora_adapter=None,
                 device_map=None):
    """Score every question in a JSONL; write JSON report and optional markdown.

    For each question: get_answer_lls_hf() → lls_to_probabilities() →
    calculate_brier_score(). Runs bootstrap evaluation with cross-validated
    Platt scaling for confidence intervals. Always writes a JSON report;
    writes a verbose markdown report only if verbose_report is True.

    Scoring failures — questions where every log-likelihood score is 0.0
    (the sentinel returned by _score_answer_ll_hf when tokenisation produces
    no answer tokens) — are counted, warned about during the run, flagged in
    the per-question report blocks, and summarised in the report header and
    final stdout output.

    Args:
        model_id:           HF model ID or local path.
        path_to_jsonl:      path to a JSONL file of benchmark questions.
        device:             device string ('mps', 'cuda', 'cpu') or None for auto.
        trust_remote_code:  passed through to HF from_pretrained calls.
        verbose_report:     if True, also write the detailed markdown report.
        n_bootstrap:        number of bootstrap iterations for confidence intervals.

    Returns:
        str: absolute path to the written JSON report.
    """
    path = Path(path_to_jsonl)

    questions = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))

    model, tokenizer = load_model(model_id, device=device, device_map=device_map,
                                  trust_remote_code=trust_remote_code,
                                  quantize=quantize, lora_adapter=lora_adapter)

    model_safe = model_id.replace(":", "_").replace("/", "_")
    if lora_adapter is not None:
        model_safe += "_" + Path(lora_adapter).name
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_report_path = path.parent / f"eval_results_full_{model_safe}_{timestamp}.json"
    md_report_path = path.parent / f"eval_report_full_{model_safe}_{timestamp}.md"

    total = len(questions)
    try:
        from tqdm import tqdm
        question_iter = tqdm(enumerate(questions, 1), total=total, desc=model_id)
        _tqdm_active = True
    except ImportError:
        question_iter = enumerate(questions, 1)
        _tqdm_active = False

    all_brier_scores = []
    all_model_probs = []       # collected for bootstrap
    all_model_logprobs = []     # collected for Platt scaling in log-odds space
    all_gt_probs = []           # collected for bootstrap
    category_scores = {}    # category → list of brier scores
    scoring_fail_total = 0
    category_scoring_fail = {}  # category → count of scoring failures
    per_question_blocks = []

    for i, question in question_iter:
        if not _tqdm_active and i % 50 == 0:
            print(f"  Processed {i} of {total} questions...")

        lls = get_answer_lls_hf(question, model, tokenizer, use_metadata=True)
        all_model_logprobs.append(lls)

        scoring_failed = all(ll == 0.0 for ll in lls)
        category = question.get("question_category", "unknown")
        if scoring_failed:
            scoring_fail_total += 1
            print(f"  WARNING: all log-likelihoods are 0.0 for question {i} "
                  f"(category: {category}) — scoring may have failed "
                  f"(empty answer tokens?)")
        model_probs = lls_to_probabilities(lls)
        gt_probs = question["answer_probabilities"]
        brier = calculate_brier_score(gt_probs, model_probs)

        all_brier_scores.append(brier)
        all_model_probs.append(model_probs)
        all_gt_probs.append(gt_probs)
        category_scores.setdefault(category, []).append(brier)
        if scoring_failed:
            category_scoring_fail[category] = category_scoring_fail.get(category, 0) + 1

        fail_note = "  ⚠ SCORING FAILURE (all LLs = 0.0)" if scoring_failed else ""
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
        block.append(f"\n**Brier Score:** {brier:.4f}{fail_note}\n")
        per_question_blocks.append("\n".join(block))

    overall_mean = sum(all_brier_scores) / len(all_brier_scores) if all_brier_scores else 0.0
    scoring_fail_rate = scoring_fail_total / total if total > 0 else 0.0

    # Build correct_vector and per_question_results for JSON
    correct_vector = [
        bool(np.argmax(mp) == np.argmax(gt))
        for mp, gt in zip(all_model_probs, all_gt_probs)
    ]
    per_question_results = [
        {"model_probs": mp, "chosen_letter": None, "correct": c}
        for mp, c in zip(all_model_probs, correct_vector)
    ]

    # Bootstrap evaluation
    subset_index = build_subset_index(questions)
    confidence_intervals = bootstrap_evaluate(
        all_gt_probs, all_model_probs, subset_index,
        mode="probabilistic", n_bootstrap=n_bootstrap,
        model_logprobs=all_model_logprobs,
    )

    # Always write JSON report
    meta = {
        "model_id": model_id,
        "benchmark_file": str(path),
        "eval_mode": "probabilistic",
        "timestamp": timestamp,
        "n_questions": total,
        "n_bootstrap": n_bootstrap,
    }
    write_json_report(json_report_path, meta, per_question_results,
                      confidence_intervals, correct_vector)

    # Optionally write verbose markdown
    if verbose_report:
        by_category = {cat: sum(scores) / len(scores)
                       for cat, scores in category_scores.items()}
        summary_lines = [
            f"# Full Eval — {model_id}\n",
            "## Summary\n",
            f"**Scoring failure rate:** {scoring_fail_rate:.1%} "
            f"({scoring_fail_total} of {total} questions had all-zero log-likelihoods)\n",
            "| Metric | Mean Brier Score | Scoring Failures |",
            "|--------|-----------------|-----------------|",
            f"| **Overall** | {overall_mean:.4f} | {scoring_fail_total} / {total} |",
        ]
        for cat, mean_brier in sorted(by_category.items()):
            cat_total = len(category_scores[cat])
            cat_fails = category_scoring_fail.get(cat, 0)
            summary_lines.append(f"| {cat} | {mean_brier:.4f} | {cat_fails} / {cat_total} |")
        summary_lines.append("")

        report_text = "\n".join(summary_lines) + "\n" + "\n\n".join(per_question_blocks)
        with open(md_report_path, "w", encoding="utf-8") as f:
            f.write(report_text)

    print(f"Overall Brier score: {overall_mean:.4f}")
    print(f"Scoring failure rate: {scoring_fail_rate:.1%} "
          f"({scoring_fail_total} of {total} questions had all-zero log-likelihoods)")
    print(f"JSON report: {json_report_path}")
    return str(json_report_path)


def mcq_eval_hf(model_id, path_to_jsonl, device=None, trust_remote_code=False,
                include_negation=False, verbose_report=False, n_bootstrap=1000,
                quantize=None, lora_adapter=None, device_map=None):
    """Evaluate a model on multiple-choice questions; write JSON and optional markdown.

    For each question: build a lettered MCQ prompt, generate a response, parse
    the chosen letter, check against the correct letter. Runs bootstrap
    evaluation for confidence intervals. Always writes a JSON report; writes
    a verbose markdown report only if verbose_report is True.

    Args:
        model_id:           HF model ID or local path.
        path_to_jsonl:      path to a JSONL file of benchmark questions.
        device:             device string ('mps', 'cuda', 'cpu') or None for auto.
        trust_remote_code:  passed through to HF from_pretrained calls.
        include_negation:   if True, include negation-type answers as distractors.
        verbose_report:     if True, also write the detailed markdown report.
        n_bootstrap:        number of bootstrap iterations for confidence intervals.

    Returns:
        str: absolute path to the written JSON report.
    """
    path = Path(path_to_jsonl)

    questions = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))

    model, tokenizer = load_model(model_id, device=device, device_map=device_map,
                                  trust_remote_code=trust_remote_code,
                                  quantize=quantize, lora_adapter=lora_adapter)

    model_safe = model_id.replace(":", "_").replace("/", "_")
    if lora_adapter is not None:
        model_safe += "_" + Path(lora_adapter).name
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_report_path = path.parent / f"eval_results_mcq_{model_safe}_{timestamp}.json"
    md_report_path = path.parent / f"eval_report_mcq_{model_safe}_{timestamp}.md"

    total = len(questions)
    try:
        from tqdm import tqdm
        question_iter = tqdm(enumerate(questions, 1), total=total, desc=model_id)
        _tqdm_active = True
    except ImportError:
        question_iter = enumerate(questions, 1)
        _tqdm_active = False

    correct_total = 0
    no_response_total = 0
    category_results = {}    # category → [correct_count, total_count]
    category_no_response = {}  # category → no-response count
    all_skill_scores = []
    category_skill = {}      # category → list of per-question skill scores
    per_question_blocks = []
    all_mcq_results = []     # collected for bootstrap

    for i, question in question_iter:
        if not _tqdm_active and i % 50 == 0:
            print(f"  Processed {i} of {total} questions...")

        prompt_text, answer_order, correct_letter = _build_mcq_prompt(
            question, use_metadata=True, include_negation=include_negation
        )
        response_text = _generate_hf(prompt_text, model, tokenizer, max_new_tokens=10)
        chosen_letter = _parse_mcq_response(response_text)

        if chosen_letter is None:
            no_response_total += 1
            category = question.get("question_category", "unknown")
            print(f"  WARNING: no parseable letter in response for question {i} "
                  f"(category: {category}) — "
                  f"raw response: {repr(response_text)}")

        is_correct = chosen_letter == correct_letter
        if is_correct:
            correct_total += 1

        category = question.get("question_category", "unknown")
        if category not in category_results:
            category_results[category] = [0, 0]
        if is_correct:
            category_results[category][0] += 1
        category_results[category][1] += 1
        if chosen_letter is None:
            category_no_response[category] = category_no_response.get(category, 0) + 1

        k = len(answer_order)
        r = sum(1 for _, _, p in answer_order if p == 1.0)
        skill = calculate_mcq_skill_score(is_correct, k, r)
        all_skill_scores.append(skill)
        category_skill.setdefault(category, []).append(skill)
        all_mcq_results.append({"is_correct": is_correct, "k": k})

        result_str = "TRUE" if is_correct else "FALSE"
        no_resp_str = "  ⚠ NO RESPONSE" if chosen_letter is None else ""

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
        block.append(
            f"**Chosen:** {chosen_letter}  **Correct:** {correct_letter}  "
            f"**Result:** {result_str}{no_resp_str}"
        )
        block.append(f"**Skill Score:** {skill:.4f}\n")
        per_question_blocks.append("\n".join(block))

    overall_accuracy = correct_total / total if total > 0 else 0.0
    no_response_rate = no_response_total / total if total > 0 else 0.0
    overall_mean_skill = sum(all_skill_scores) / len(all_skill_scores) if all_skill_scores else 0.0

    # Build correct_vector and per_question_results for JSON
    correct_vector = [r["is_correct"] for r in all_mcq_results]
    per_question_results = [
        {"model_probs": None, "chosen_letter": None, "correct": r["is_correct"]}
        for r in all_mcq_results
    ]

    # Bootstrap evaluation
    gt_probs_list = [q["answer_probabilities"] for q in questions]
    subset_index = build_subset_index(questions)
    confidence_intervals = bootstrap_evaluate(
        gt_probs_list, all_mcq_results, subset_index,
        mode="mcq", n_bootstrap=n_bootstrap,
    )

    # Always write JSON report
    meta = {
        "model_id": model_id,
        "benchmark_file": str(path),
        "eval_mode": "mcq",
        "timestamp": timestamp,
        "n_questions": total,
        "n_bootstrap": n_bootstrap,
    }
    write_json_report(json_report_path, meta, per_question_results,
                      confidence_intervals, correct_vector)

    # Optionally write verbose markdown
    if verbose_report:
        by_category = {
            cat: counts[0] / counts[1] if counts[1] > 0 else 0.0
            for cat, counts in category_results.items()
        }
        by_category_skill = {cat: sum(s) / len(s) for cat, s in category_skill.items()}

        summary_lines = [
            f"# MCQ Eval — {model_id}\n",
            "## Summary\n",
            f"**No-response rate:** {no_response_rate:.1%} "
            f"({no_response_total} of {total} questions returned no parseable letter)\n",
            "| Metric | Accuracy | Skill Score | No Response |",
            "|--------|----------|-------------|-------------|",
            f"| **Overall** | {overall_accuracy:.1%} | {overall_mean_skill:.4f} "
            f"| {no_response_total} / {total} |",
        ]
        for cat in sorted(by_category.keys()):
            acc = by_category[cat]
            skill_avg = by_category_skill.get(cat, 0.0)
            cat_total = category_results[cat][1]
            cat_no_resp = category_no_response.get(cat, 0)
            summary_lines.append(
                f"| {cat} | {acc:.1%} | {skill_avg:.4f} | {cat_no_resp} / {cat_total} |"
            )
        summary_lines.append("")

        report_text = "\n".join(summary_lines) + "\n" + "\n\n".join(per_question_blocks)
        with open(md_report_path, "w", encoding="utf-8") as f:
            f.write(report_text)

    print(f"Overall MCQ accuracy: {overall_accuracy:.1%}")
    print(f"Overall MCQ skill score: {overall_mean_skill:.4f}")
    print(f"No-response rate: {no_response_rate:.1%} "
          f"({no_response_total} of {total} questions returned no parseable letter)")
    print(f"JSON report: {json_report_path}")
    return str(json_report_path)


# ---------------------------------------------------------------------------
# Together AI path
# ---------------------------------------------------------------------------

def load_together_credentials(cred_path=None):
    """Load the Together AI API key from a single-line text file.

    Args:
        cred_path: path to API key file, or None to use the default
                   (evalcode/TogetherAPIKey.txt, resolved relative to this
                   script so it works regardless of the working directory).

    Returns:
        str: the API key, stripped of whitespace.

    Raises:
        FileNotFoundError: if the key file does not exist.
        ValueError: if the file is empty.
    """
    if cred_path is None:
        cred_path = Path(__file__).parent / "TogetherAPIKey.txt"
    else:
        cred_path = Path(cred_path)

    if not cred_path.exists():
        raise FileNotFoundError(
            f"Together AI key file not found: {cred_path}\n"
            "Create it with the API key as a single line."
        )

    lines = [ln.strip() for ln in cred_path.read_text(encoding="utf-8").splitlines()
             if ln.strip()]
    if not lines:
        raise ValueError("Together AI key file is empty.")

    return lines[0]


def _together_completions_raw(prompt, model_name, api_key, max_tokens=1,
                               echo=True, logprobs=1):
    """POST to Together's /completions endpoint and return the raw JSON dict.

    Uses `requests` directly to bypass OpenAI SDK schema parsing, which
    silently drops Together-specific fields like `token_logprobs` (Together's
    flat list) because they don't match OpenAI's chat logprobs schema.

    Args:
        prompt:     the full prompt string (context + answer, or context alone).
        model_name: Together AI model identifier.
        api_key:    Together AI API key string.
        max_tokens: number of tokens to generate (default 1).
        echo:       if True, include prompt tokens in the logprobs response.
        logprobs:   number of top logprobs to return per token.

    Returns:
        dict: the parsed JSON response from Together's API.

    Raises:
        RuntimeError: if the HTTP request fails.
        ImportError:  if the `requests` package is not installed.
    """
    try:
        import requests as _requests
    except ImportError as e:
        raise ImportError(
            "The 'requests' package is required for Together AI evaluation. "
            "Install it with: pip install requests"
        ) from e

    resp = _requests.post(
        f"{TOGETHER_BASE_URL}/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model_name,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "echo": echo,
            "logprobs": logprobs,
        },
        timeout=120,
    )
    if not resp.ok:
        raise RuntimeError(
            f"Together API error {resp.status_code}: {resp.text[:400]}"
        )
    return resp.json()


def _extract_token_logprobs_from_raw(raw_json, first_call=False):
    """Extract token_logprobs from a raw Together completions JSON response.

    Together's completions response has logprobs at:
        choices[0].logprobs.token_logprobs   (flat list of floats)

    Prints a one-time diagnostic if the expected structure is missing.

    Args:
        raw_json:   dict returned by _together_completions_raw().
        first_call: if True and extraction fails, print the response structure.

    Returns:
        list[float] or None
    """
    try:
        tlp = raw_json["choices"][0]["logprobs"]["token_logprobs"]
        if isinstance(tlp, list):
            return tlp
    except (KeyError, TypeError, IndexError):
        pass
    if first_call:
        choices = raw_json.get("choices", [{}])
        lp = choices[0].get("logprobs") if choices else None
        print(f"  DEBUG: unexpected logprobs structure from Together API: "
              f"choices[0].logprobs = {lp!r}")
    return None


def get_answer_lls_together(question, model_name, api_key, use_metadata=True):
    """Return average log-probability per token for each candidate answer (Together path).

    Uses Together's /completions endpoint with echo=True and logprobs=1 via
    raw HTTP (requests), bypassing the OpenAI SDK which silently drops
    Together-specific fields. Together does not return text_offset, so the
    context/answer boundary is found by counting tokens in one preliminary
    context-only call.

    Total API calls per question: 1 (context token count) + N (answers).

    Args:
        question:     dict conforming to the benchmark question format.
        model_name:   Together AI model identifier
                      (e.g. 'meta-llama/Llama-3.3-70B-Instruct-Turbo').
        api_key:      Together AI API key string.
        use_metadata: if True, include metadata_frame in the prompt.

    Returns:
        list[float]: one score per entry in question['answer_strings'],
                     in the same order.
    """
    context_text = _build_question_text(question, use_metadata)

    # One preliminary call to count context tokens.
    # echo=True + max_tokens=1 → token_logprobs contains context tokens + 1
    # generated token.  Subtract 1 to get the number of context tokens.
    ctx_raw = _together_completions_raw(context_text, model_name, api_key)
    ctx_logprobs = _extract_token_logprobs_from_raw(ctx_raw, first_call=True)
    if ctx_logprobs is None:
        return [0.0] * len(question["answer_strings"])

    context_token_count = len(ctx_logprobs) - 1  # exclude the 1 generated token
    if context_token_count <= 0:
        print(f"  DEBUG: context_token_count={context_token_count} "
              f"(token_logprobs length={len(ctx_logprobs)}). "
              f"Together may not be returning prompt logprobs for this model.")
        return [0.0] * len(question["answer_strings"])

    results = []
    for answer in question["answer_strings"]:
        if not answer:
            results.append(0.0)
            continue

        ans_raw = _together_completions_raw(
            context_text + answer, model_name, api_key
        )
        tlp = _extract_token_logprobs_from_raw(ans_raw)
        if tlp is None:
            results.append(0.0)
            continue

        # Answer tokens are between the context and the 1 generated token
        answer_logprobs = tlp[context_token_count:-1]
        valid = [lp for lp in answer_logprobs if lp is not None]
        results.append(sum(valid) / len(valid) if valid else 0.0)

    return results


def _generate_together(prompt, model_id, api_key, max_tokens=10):
    """Generate text from a prompt via Together AI chat completions.

    Args:
        prompt:     the input prompt string (MCQ format).
        model_id:   Together AI model identifier.
        api_key:    Together AI API key string.
        max_tokens: maximum tokens to generate.

    Returns:
        str: the generated text.

    Raises:
        ImportError: if the 'openai' package is not installed.
    """
    try:
        from openai import OpenAI
    except ImportError as e:
        raise ImportError(
            "The 'openai' package is required for Together AI evaluation. "
            "Install it with: pip install openai"
        ) from e

    client = OpenAI(base_url=TOGETHER_BASE_URL, api_key=api_key)
    response = client.chat.completions.create(
        model=model_id,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0,
    )
    return response.choices[0].message.content or ""


def full_eval_together(model_id, path_to_jsonl, api_key_path=None,
                       verbose_report=False, n_bootstrap=1000):
    """Score every question via the Together AI API; write JSON and optional markdown.

    Uses Together AI's OpenAI-compatible completions endpoint with echo=True
    for log-likelihood scoring. Runs bootstrap evaluation with cross-validated
    Platt scaling for confidence intervals.

    Args:
        model_id:       Together AI model identifier
                        (e.g. 'meta-llama/Llama-3.3-70B-Instruct-Turbo').
        path_to_jsonl:  path to a JSONL file of benchmark questions.
        api_key_path:   path to API key file; None uses evalcode/TogetherAPIKey.txt.
        verbose_report: if True, also write the detailed markdown report.
        n_bootstrap:    number of bootstrap iterations for confidence intervals.

    Returns:
        str: absolute path to the written JSON report.
    """
    path = Path(path_to_jsonl)
    api_key = load_together_credentials(api_key_path)

    questions = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))

    model_safe = model_id.replace(":", "_").replace("/", "_")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_report_path = path.parent / f"eval_results_full_{model_safe}_{timestamp}.json"
    md_report_path = path.parent / f"eval_report_full_{model_safe}_{timestamp}.md"

    total = len(questions)
    try:
        from tqdm import tqdm
        question_iter = tqdm(enumerate(questions, 1), total=total, desc=model_id)
        _tqdm_active = True
    except ImportError:
        question_iter = enumerate(questions, 1)
        _tqdm_active = False

    all_brier_scores = []
    all_model_probs = []
    all_model_logprobs = []
    all_gt_probs = []
    category_scores = {}
    scoring_fail_total = 0
    category_scoring_fail = {}
    per_question_blocks = []

    for i, question in question_iter:
        if not _tqdm_active and i % 50 == 0:
            print(f"  Processed {i} of {total} questions...")

        lls = get_answer_lls_together(question, model_id, api_key, use_metadata=True)
        all_model_logprobs.append(lls)

        scoring_failed = all(ll == 0.0 for ll in lls)
        category = question.get("question_category", "unknown")
        if scoring_failed:
            scoring_fail_total += 1
            print(f"  WARNING: all log-likelihoods are 0.0 for question {i} "
                  f"(category: {category}) — scoring may have failed "
                  f"(empty answer tokens?)")
            if i == 1:
                raise RuntimeError(
                    "\nTogether AI is not returning prompt log-probabilities for model "
                    f"'{model_id}'.\n"
                    "This means the /completions endpoint's echo=True feature is not "
                    "working on Together's live service for this model — a known gap "
                    "between their documentation and live behavior.\n\n"
                    "Options:\n"
                    "  1. Use MCQ evaluation instead:  --api together --mcq\n"
                    "  2. Try a Together base (non-instruct) model on /completions.\n"
                    "  3. Report the bug to Together support and await a fix.\n"
                )
        model_probs = lls_to_probabilities(lls)
        gt_probs = question["answer_probabilities"]
        brier = calculate_brier_score(gt_probs, model_probs)

        all_brier_scores.append(brier)
        all_model_probs.append(model_probs)
        all_gt_probs.append(gt_probs)
        category_scores.setdefault(category, []).append(brier)
        if scoring_failed:
            category_scoring_fail[category] = category_scoring_fail.get(category, 0) + 1

        fail_note = "  ⚠ SCORING FAILURE (all LLs = 0.0)" if scoring_failed else ""
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
        block.append(f"\n**Brier Score:** {brier:.4f}{fail_note}\n")
        per_question_blocks.append("\n".join(block))

    overall_mean = sum(all_brier_scores) / len(all_brier_scores) if all_brier_scores else 0.0
    scoring_fail_rate = scoring_fail_total / total if total > 0 else 0.0

    correct_vector = [
        bool(np.argmax(mp) == np.argmax(gt))
        for mp, gt in zip(all_model_probs, all_gt_probs)
    ]
    per_question_results = [
        {"model_probs": mp, "chosen_letter": None, "correct": c}
        for mp, c in zip(all_model_probs, correct_vector)
    ]

    subset_index = build_subset_index(questions)
    confidence_intervals = bootstrap_evaluate(
        all_gt_probs, all_model_probs, subset_index,
        mode="probabilistic", n_bootstrap=n_bootstrap,
        model_logprobs=all_model_logprobs,
    )

    meta = {
        "model_id": model_id,
        "benchmark_file": str(path),
        "eval_mode": "probabilistic",
        "api": "together",
        "timestamp": timestamp,
        "n_questions": total,
        "n_bootstrap": n_bootstrap,
    }
    write_json_report(json_report_path, meta, per_question_results,
                      confidence_intervals, correct_vector)

    if verbose_report:
        by_category = {cat: sum(scores) / len(scores)
                       for cat, scores in category_scores.items()}
        summary_lines = [
            f"# Full Eval — {model_id}\n",
            "## Summary\n",
            f"**Scoring failure rate:** {scoring_fail_rate:.1%} "
            f"({scoring_fail_total} of {total} questions had all-zero log-likelihoods)\n",
            "| Metric | Mean Brier Score | Scoring Failures |",
            "|--------|-----------------|-----------------|",
            f"| **Overall** | {overall_mean:.4f} | {scoring_fail_total} / {total} |",
        ]
        for cat, mean_brier in sorted(by_category.items()):
            cat_total = len(category_scores[cat])
            cat_fails = category_scoring_fail.get(cat, 0)
            summary_lines.append(f"| {cat} | {mean_brier:.4f} | {cat_fails} / {cat_total} |")
        summary_lines.append("")

        report_text = "\n".join(summary_lines) + "\n" + "\n\n".join(per_question_blocks)
        with open(md_report_path, "w", encoding="utf-8") as f:
            f.write(report_text)

    print(f"Overall Brier score: {overall_mean:.4f}")
    print(f"Scoring failure rate: {scoring_fail_rate:.1%} "
          f"({scoring_fail_total} of {total} questions had all-zero log-likelihoods)")
    print(f"JSON report: {json_report_path}")
    return str(json_report_path)


def mcq_eval_together(model_id, path_to_jsonl, api_key_path=None,
                      include_negation=False, verbose_report=False, n_bootstrap=1000):
    """Evaluate a Together AI model on multiple-choice questions.

    Uses Together AI's chat completions endpoint for generation. Runs bootstrap
    evaluation for confidence intervals. Always writes a JSON report; writes a
    verbose markdown report only if verbose_report is True.

    Args:
        model_id:          Together AI model identifier.
        path_to_jsonl:     path to a JSONL file of benchmark questions.
        api_key_path:      path to API key file; None uses evalcode/TogetherAPIKey.txt.
        include_negation:  if True, include negation-type answers as distractors.
        verbose_report:    if True, also write the detailed markdown report.
        n_bootstrap:       number of bootstrap iterations for confidence intervals.

    Returns:
        str: absolute path to the written JSON report.
    """
    path = Path(path_to_jsonl)
    api_key = load_together_credentials(api_key_path)

    questions = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))

    model_safe = model_id.replace(":", "_").replace("/", "_")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_report_path = path.parent / f"eval_results_mcq_{model_safe}_{timestamp}.json"
    md_report_path = path.parent / f"eval_report_mcq_{model_safe}_{timestamp}.md"

    total = len(questions)
    try:
        from tqdm import tqdm
        question_iter = tqdm(enumerate(questions, 1), total=total, desc=model_id)
        _tqdm_active = True
    except ImportError:
        question_iter = enumerate(questions, 1)
        _tqdm_active = False

    correct_total = 0
    no_response_total = 0
    category_results = {}
    category_no_response = {}
    all_skill_scores = []
    category_skill = {}
    per_question_blocks = []
    all_mcq_results = []

    for i, question in question_iter:
        if not _tqdm_active and i % 50 == 0:
            print(f"  Processed {i} of {total} questions...")

        prompt_text, answer_order, correct_letter = _build_mcq_prompt(
            question, use_metadata=True, include_negation=include_negation
        )
        response_text = _generate_together(prompt_text, model_id, api_key)
        chosen_letter = _parse_mcq_response(response_text)

        if chosen_letter is None:
            no_response_total += 1
            category = question.get("question_category", "unknown")
            print(f"  WARNING: no parseable letter in response for question {i} "
                  f"(category: {category}) — "
                  f"raw response: {repr(response_text)}")

        is_correct = chosen_letter == correct_letter
        if is_correct:
            correct_total += 1

        category = question.get("question_category", "unknown")
        if category not in category_results:
            category_results[category] = [0, 0]
        if is_correct:
            category_results[category][0] += 1
        category_results[category][1] += 1
        if chosen_letter is None:
            category_no_response[category] = category_no_response.get(category, 0) + 1

        k = len(answer_order)
        r = sum(1 for _, _, p in answer_order if p == 1.0)
        skill = calculate_mcq_skill_score(is_correct, k, r)
        all_skill_scores.append(skill)
        category_skill.setdefault(category, []).append(skill)
        all_mcq_results.append({"is_correct": is_correct, "k": k})

        result_str = "TRUE" if is_correct else "FALSE"
        no_resp_str = "  ⚠ NO RESPONSE" if chosen_letter is None else ""

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
        block.append(
            f"**Chosen:** {chosen_letter}  **Correct:** {correct_letter}  "
            f"**Result:** {result_str}{no_resp_str}"
        )
        block.append(f"**Skill Score:** {skill:.4f}\n")
        per_question_blocks.append("\n".join(block))

    overall_accuracy = correct_total / total if total > 0 else 0.0
    no_response_rate = no_response_total / total if total > 0 else 0.0
    overall_mean_skill = sum(all_skill_scores) / len(all_skill_scores) if all_skill_scores else 0.0

    correct_vector = [r["is_correct"] for r in all_mcq_results]
    per_question_results = [
        {"model_probs": None, "chosen_letter": None, "correct": r["is_correct"]}
        for r in all_mcq_results
    ]

    gt_probs_list = [q["answer_probabilities"] for q in questions]
    subset_index = build_subset_index(questions)
    confidence_intervals = bootstrap_evaluate(
        gt_probs_list, all_mcq_results, subset_index,
        mode="mcq", n_bootstrap=n_bootstrap,
    )

    meta = {
        "model_id": model_id,
        "benchmark_file": str(path),
        "eval_mode": "mcq",
        "api": "together",
        "timestamp": timestamp,
        "n_questions": total,
        "n_bootstrap": n_bootstrap,
    }
    write_json_report(json_report_path, meta, per_question_results,
                      confidence_intervals, correct_vector)

    if verbose_report:
        by_category = {
            cat: counts[0] / counts[1] if counts[1] > 0 else 0.0
            for cat, counts in category_results.items()
        }
        by_category_skill = {cat: sum(s) / len(s) for cat, s in category_skill.items()}

        summary_lines = [
            f"# MCQ Eval — {model_id}\n",
            "## Summary\n",
            f"**No-response rate:** {no_response_rate:.1%} "
            f"({no_response_total} of {total} questions returned no parseable letter)\n",
            "| Metric | Accuracy | Skill Score | No Response |",
            "|--------|----------|-------------|-------------|",
            f"| **Overall** | {overall_accuracy:.1%} | {overall_mean_skill:.4f} "
            f"| {no_response_total} / {total} |",
        ]
        for cat in sorted(by_category.keys()):
            acc = by_category[cat]
            skill_avg = by_category_skill.get(cat, 0.0)
            cat_total = category_results[cat][1]
            cat_no_resp = category_no_response.get(cat, 0)
            summary_lines.append(
                f"| {cat} | {acc:.1%} | {skill_avg:.4f} | {cat_no_resp} / {cat_total} |"
            )
        summary_lines.append("")

        report_text = "\n".join(summary_lines) + "\n" + "\n\n".join(per_question_blocks)
        with open(md_report_path, "w", encoding="utf-8") as f:
            f.write(report_text)

    print(f"Overall MCQ accuracy: {overall_accuracy:.1%}")
    print(f"Overall MCQ skill score: {overall_mean_skill:.4f}")
    print(f"No-response rate: {no_response_rate:.1%} "
          f"({no_response_total} of {total} questions returned no parseable letter)")
    print(f"JSON report: {json_report_path}")
    return str(json_report_path)


# ---------------------------------------------------------------------------
# OpenAI API path
# ---------------------------------------------------------------------------

def load_openai_credentials(cred_path=None):
    """Load OpenAI credentials from a two-line text file.

    The file must contain exactly two non-empty lines:
        Line 1 — organisation ID  (e.g. org-xxxxxxxxxxxxxxxx)
        Line 2 — API key          (e.g. sk-xxxxxxxxxxxxxxxx)

    Args:
        cred_path: path to credentials file, or None to use the default
                   (evalcode/credentials.txt, resolved relative to this
                   script so it works regardless of the working directory).

    Returns:
        tuple: (org_id, api_key) — both strings, stripped of whitespace.

    Raises:
        FileNotFoundError: if the credentials file does not exist.
        ValueError: if the file does not contain two non-empty lines.
    """
    if cred_path is None:
        cred_path = Path(__file__).parent / "credentials.txt"
    else:
        cred_path = Path(cred_path)

    if not cred_path.exists():
        raise FileNotFoundError(
            f"OpenAI credentials file not found: {cred_path}\n"
            "Create it with the organisation ID on line 1 and the API key on line 2."
        )

    lines = [ln.strip() for ln in cred_path.read_text(encoding="utf-8").splitlines()
             if ln.strip()]
    if len(lines) < 2:
        raise ValueError(
            f"credentials.txt must contain two non-empty lines "
            f"(org ID then API key); found {len(lines)} line(s)."
        )

    return lines[0], lines[1]


def is_openai_model(model_id):
    """Return True if model_id looks like an OpenAI-hosted model.

    Matches against OPENAI_MODEL_PREFIXES using str.startswith(), which
    covers exact names (e.g. 'gpt-4.1') and versioned variants
    (e.g. 'gpt-4.1-2025-04-14') as well as fine-tuned IDs
    (e.g. 'ft:gpt-4.1-2025-04-14:org:name:id').

    Args:
        model_id: model identifier string.

    Returns:
        bool
    """
    return model_id.startswith(OPENAI_MODEL_PREFIXES)


def _call_responses_with_retry(client, model_id, input_text, instructions,
                                max_output_tokens=25000, reasoning_effort="medium",
                                text_format=None, max_retries=3):
    """Call client.responses.create() with exponential-backoff retries.

    Retries specifically on openai.RateLimitError (HTTP 429).  Other
    exceptions propagate immediately.

    Args:
        client:            an openai.OpenAI instance.
        model_id:          model identifier string.
        input_text:        the user input string.
        instructions:      the system instructions string.
        max_output_tokens: maximum tokens to generate (includes reasoning tokens).
        reasoning_effort:  one of "none", "minimal", "low", "medium", "high".
        text_format:       optional dict passed as text={"format": text_format}
                           (e.g. a JSON schema for structured outputs).
        max_retries:       number of retry attempts after the first failure.

    Returns:
        openai.types.responses.Response: the API response object.

    Raises:
        openai.RateLimitError: if all retries are exhausted.
        Any other openai exception: propagated immediately.
    """
    import time

    try:
        from openai import RateLimitError
    except ImportError as exc:
        raise ImportError(
            "The 'openai' package is required for OpenAI API evaluation. "
            "Install it with: pip install openai"
        ) from exc

    kwargs = dict(
        model=model_id,
        input=input_text,
        instructions=instructions,
        max_output_tokens=max_output_tokens,
        store=False,
    )
    if reasoning_effort != "none":
        kwargs["reasoning"] = {"effort": reasoning_effort}
    if text_format is not None:
        kwargs["text"] = {"format": text_format}

    last_exc = None
    for attempt in range(max_retries + 1):
        try:
            return client.responses.create(**kwargs)
        except RateLimitError as exc:
            last_exc = exc
            if attempt < max_retries:
                wait = 2 ** attempt
                print(f"  Rate limit hit; retrying in {wait}s "
                      f"(attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait)
            else:
                raise RateLimitError(
                    f"OpenAI rate limit exceeded after {max_retries} retries."
                ) from last_exc


def _parse_mcq_response_openai(response_text):
    """Parse a model response that may be JSON (structured output) or plain text.

    Tries to decode the response as a JSON object with a "choice" key first
    (the format returned by structured-output requests).  Falls back to the
    plain-text regex parser _parse_mcq_response() if JSON decoding fails or
    the expected key is absent.

    Args:
        response_text: string returned by the model.

    Returns:
        str or None: a single uppercase letter, or None if no letter was found.
    """
    try:
        data = json.loads(response_text)
        if isinstance(data, dict) and "choice" in data:
            val = data["choice"]
            if isinstance(val, str) and len(val) == 1 and val.isupper():
                return val
    except (json.JSONDecodeError, TypeError, ValueError):
        pass
    return _parse_mcq_response(response_text)


def _generate_openai(prompt, model_id, client, valid_letters=None,
                     max_output_tokens=25000, reasoning_effort="medium",
                     use_json_schema=True):
    """Generate a Responses API completion for an MCQ prompt.

    Sends the prompt as input with a concise instructions string.  Reasoning
    is controlled via the reasoning_effort parameter rather than being
    suppressed in the instructions.

    When use_json_schema=True (default), uses a JSON schema structured output
    (Responses API format) to guarantee a valid letter regardless of how much
    reasoning the model performs.

    When use_json_schema=False, relies on the instructions alone to produce a
    short answer; max_output_tokens should still be generous to leave room for
    reasoning tokens.

    Args:
        prompt:             the full MCQ prompt string (from _build_mcq_prompt).
        model_id:           OpenAI model identifier string.
        client:             an openai.OpenAI instance.
        valid_letters:      list of uppercase letter strings that are valid
                            answers for this question (e.g. ['A','B','C','D']).
                            Used to build the structured-output enum when
                            use_json_schema=True.  If None, no schema is applied.
        max_output_tokens:  maximum tokens to generate (includes reasoning tokens).
        reasoning_effort:   one of "none", "minimal", "low", "medium", "high".
        use_json_schema:    if True, apply JSON schema constraint (default True).

    Returns:
        str: the model's raw response text (JSON string when structured outputs
             are active, e.g. '{"choice":"C"}'; plain text otherwise).
    """
    instructions = "Choose the best answer. Respond with only the letter of the correct answer."

    text_format = None
    if use_json_schema and valid_letters:
        text_format = {
            "type": "json_schema",
            "name": "mcq_answer",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "choice": {"type": "string", "enum": list(valid_letters)},
                },
                "required": ["choice"],
                "additionalProperties": False,
            },
        }

    response = _call_responses_with_retry(
        client, model_id, prompt, instructions,
        max_output_tokens=max_output_tokens,
        reasoning_effort=reasoning_effort,
        text_format=text_format,
    )
    return response.output_text or ""


def mcq_eval_openai(model_id, path_to_jsonl, credentials_path=None,
                    include_negation=False, trace=False,
                    verbose_report=False, n_bootstrap=1000,
                    reasoning_effort="medium", use_json_schema=True):
    """Evaluate an OpenAI-hosted model on multiple-choice questions.

    Uses the Responses API.  For each question the function builds a
    lettered MCQ prompt, sends it to the model, parses the chosen letter, and
    checks it against the correct answer.  Runs bootstrap evaluation for
    confidence intervals. Always writes a JSON report; writes a verbose
    markdown report only if verbose_report is True.

    Args:
        model_id:          OpenAI model identifier (e.g. 'gpt-4.1-2025-04-14').
        path_to_jsonl:     path to a JSONL file of benchmark questions.
        credentials_path:  path to credentials file; None uses the default
                           evalcode/credentials.txt.
        include_negation:  if True, include negation-type answers as distractors.
        trace:             if True, sample 5 random questions and print the full
                           prompt, raw API response, parsed letter, and correct
                           letter to stdout for each — useful for debugging
                           response-parsing failures.
        verbose_report:    if True, also write the detailed markdown report.
        n_bootstrap:       number of bootstrap iterations for confidence intervals.
        reasoning_effort:  reasoning effort for the Responses API; one of
                           "none", "minimal", "low", "medium", "high".
        use_json_schema:   if True (default), apply JSON schema structured
                           output to guarantee a valid letter response.

    Returns:
        str: absolute path to the written JSON report.

    Raises:
        FileNotFoundError: if credentials file is missing.
        ImportError: if the 'openai' package is not installed.
    """
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ImportError(
            "The 'openai' package is required for OpenAI API evaluation. "
            "Install it with: pip install openai"
        ) from exc

    org_id, api_key = load_openai_credentials(credentials_path)
    client = OpenAI(api_key=api_key, organization=org_id)

    path = Path(path_to_jsonl)
    questions = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))

    if trace:
        questions = random.sample(questions, min(5, len(questions)))

    model_safe = model_id.replace(":", "_").replace("/", "_")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_report_path = path.parent / f"eval_results_mcq_{model_safe}_{timestamp}.json"
    md_report_path = path.parent / f"eval_report_mcq_{model_safe}_{timestamp}.md"

    total = len(questions)
    try:
        from tqdm import tqdm
        question_iter = tqdm(enumerate(questions, 1), total=total, desc=model_id)
        _tqdm_active = True
    except ImportError:
        question_iter = enumerate(questions, 1)
        _tqdm_active = False

    correct_total = 0
    no_response_total = 0
    category_results = {}    # category → [correct_count, total_count]
    category_no_response = {}  # category → no-response count
    all_skill_scores = []
    category_skill = {}      # category → list of per-question skill scores
    per_question_blocks = []
    all_mcq_results = []     # collected for bootstrap

    for i, question in question_iter:
        if not _tqdm_active and not trace and i % 50 == 0:
            print(f"  Processed {i} of {total} questions...")

        prompt_text, answer_order, correct_letter = _build_mcq_prompt(
            question, use_metadata=True, include_negation=include_negation
        )
        valid_letters = [letter for letter, _, _ in answer_order]
        response_text = _generate_openai(
            prompt_text, model_id, client, valid_letters=valid_letters,
            reasoning_effort=reasoning_effort, use_json_schema=use_json_schema,
        )
        chosen_letter = _parse_mcq_response_openai(response_text)

        if chosen_letter is None:
            no_response_total += 1
            print(f"  WARNING: no parseable letter in response for question {i} "
                  f"(category: {question.get('question_category', 'unknown')}) — "
                  f"raw response: {repr(response_text)}")

        if trace:
            sep = "=" * 72
            print(f"\n{sep}")
            print(f"QUESTION {i}  (category: {question.get('question_category', '')})")
            print(sep)
            print("── PROMPT ──────────────────────────────────────────────────────────")
            print(prompt_text)
            print("── RAW RESPONSE ────────────────────────────────────────────────────")
            print(repr(response_text))
            print("── PARSE RESULT ────────────────────────────────────────────────────")
            print(f"  chosen_letter : {chosen_letter!r}")
            print(f"  correct_letter: {correct_letter!r}")
            print(f"  correct       : {chosen_letter == correct_letter}")
            print(sep)

        is_correct = chosen_letter == correct_letter
        if is_correct:
            correct_total += 1

        category = question.get("question_category", "unknown")
        if category not in category_results:
            category_results[category] = [0, 0]
        if is_correct:
            category_results[category][0] += 1
        category_results[category][1] += 1
        if chosen_letter is None:
            category_no_response[category] = category_no_response.get(category, 0) + 1

        k = len(answer_order)
        r = sum(1 for _, _, p in answer_order if p == 1.0)
        skill = calculate_mcq_skill_score(is_correct, k, r)
        all_skill_scores.append(skill)
        category_skill.setdefault(category, []).append(skill)
        all_mcq_results.append({"is_correct": is_correct, "k": k})

        result_str = "TRUE" if is_correct else "FALSE"
        no_resp_str = "  ⚠ NO RESPONSE" if chosen_letter is None else ""

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
        block.append(
            f"**Chosen:** {chosen_letter}  **Correct:** {correct_letter}  "
            f"**Result:** {result_str}{no_resp_str}"
        )
        block.append(f"**Skill Score:** {skill:.4f}\n")
        per_question_blocks.append("\n".join(block))

    overall_accuracy = correct_total / total if total > 0 else 0.0
    no_response_rate = no_response_total / total if total > 0 else 0.0
    overall_mean_skill = (
        sum(all_skill_scores) / len(all_skill_scores) if all_skill_scores else 0.0
    )

    # Build correct_vector and per_question_results for JSON
    correct_vector = [r["is_correct"] for r in all_mcq_results]
    per_question_results = [
        {"model_probs": None, "chosen_letter": None, "correct": r["is_correct"]}
        for r in all_mcq_results
    ]

    # Bootstrap evaluation
    gt_probs_list = [q["answer_probabilities"] for q in questions]
    subset_index = build_subset_index(questions)
    confidence_intervals = bootstrap_evaluate(
        gt_probs_list, all_mcq_results, subset_index,
        mode="mcq", n_bootstrap=n_bootstrap,
    )

    # Always write JSON report
    meta = {
        "model_id": model_id,
        "benchmark_file": str(path),
        "eval_mode": "mcq",
        "timestamp": timestamp,
        "n_questions": total,
        "n_bootstrap": n_bootstrap,
    }
    write_json_report(json_report_path, meta, per_question_results,
                      confidence_intervals, correct_vector)

    # Optionally write verbose markdown
    if verbose_report:
        by_category = {
            cat: counts[0] / counts[1] if counts[1] > 0 else 0.0
            for cat, counts in category_results.items()
        }
        by_category_skill = {cat: sum(s) / len(s) for cat, s in category_skill.items()}

        summary_lines = [
            f"# MCQ Eval — {model_id}\n",
            "## Summary\n",
            f"**No-response rate:** {no_response_rate:.1%} "
            f"({no_response_total} of {total} questions returned no parseable letter)\n",
            "| Metric | Accuracy | Skill Score | No Response |",
            "|--------|----------|-------------|-------------|",
            f"| **Overall** | {overall_accuracy:.1%} | {overall_mean_skill:.4f} "
            f"| {no_response_total} / {total} |",
        ]
        for cat in sorted(by_category.keys()):
            acc = by_category[cat]
            skill_avg = by_category_skill.get(cat, 0.0)
            cat_total = category_results[cat][1]
            cat_no_resp = category_no_response.get(cat, 0)
            summary_lines.append(
                f"| {cat} | {acc:.1%} | {skill_avg:.4f} | {cat_no_resp} / {cat_total} |"
            )
        summary_lines.append("")

        report_text = "\n".join(summary_lines) + "\n" + "\n\n".join(per_question_blocks)
        with open(md_report_path, "w", encoding="utf-8") as f:
            f.write(report_text)

    print(f"Overall MCQ accuracy: {overall_accuracy:.1%}")
    print(f"Overall MCQ skill score: {overall_mean_skill:.4f}")
    print(f"No-response rate: {no_response_rate:.1%} "
          f"({no_response_total} of {total} questions returned no parseable letter)")
    print(f"JSON report: {json_report_path}")
    return str(json_report_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Evaluate a model on benchmark questions (Brier score or MCQ accuracy).\n\n"
            "Together AI: use --api together for probabilistic (--full-eval) or MCQ.\n"
            "OpenAI models (gpt-4.1-*, gpt-5*, ft:gpt-4.1-*, ft:gpt-5*) are detected\n"
            "automatically when --mcq is set and routed to the Responses API.\n"
            "Credentials are read from evalcode/credentials.txt (or --credentials)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("model_id",      help="HF model ID or local path (HF mode); "
                                              "Together AI model name (--api together); "
                                              "OpenAI model name (OpenAI mode); "
                                              "vLLM model name (--vllm mode)")
    parser.add_argument("path_to_jsonl", help="Path to benchmark questions JSONL")
    parser.add_argument("--api",         default=None, choices=["together"],
                        help="API backend: 'together' routes to Together AI's API "
                             "for probabilistic (--full-eval) or MCQ (--mcq) eval")
    parser.add_argument("--together-key", default=None, metavar="PATH",
                        help="Path to Together AI API key file "
                             "(default: evalcode/TogetherAPIKey.txt)")
    parser.add_argument("--vllm",        action="store_true",
                        help="Use legacy vLLM endpoint instead of HuggingFace")
    parser.add_argument("--device",      default=None,
                        help="Device override: mps | cuda | cpu (HF mode only)")
    parser.add_argument("--device-map",  default=None,
                        help="HF Accelerate device_map (e.g. 'auto') for multi-GPU "
                             "inference. Mutually exclusive with --device.")
    parser.add_argument("--quantize",    default=None, choices=["int4", "int8"],
                        help="Quantize model weights via torchao (HF mode only). "
                             "int4 (~4GB for 7B, ~12GB for 24B) works on MPS and CUDA. "
                             "Requires: pip install torchao")
    parser.add_argument("--trust-remote-code", action="store_true",
                        help="Pass trust_remote_code=True to HF (HF mode only)")
    parser.add_argument("--lora-adapter", default=None, metavar="PATH",
                        help="Path to a LoRA/QLoRA adapter checkpoint to attach "
                             "to the base model (requires: pip install peft)")
    parser.add_argument("--credentials", default=None, metavar="PATH",
                        help="Path to OpenAI credentials file "
                             "(default: evalcode/credentials.txt)")

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--full-eval", action="store_true",
                            help="Score every question; report mean Brier score (HF mode only)")
    mode_group.add_argument("--mcq",       action="store_true",
                            help="Present MCQ prompts; report top-1 accuracy. "
                                 "Auto-routes to OpenAI API for GPT-4.1/5 model IDs.")

    parser.add_argument("--include-negation", action="store_true",
                        help="Include negation-type answers in MCQ distractors (--mcq only)")
    parser.add_argument("--trace", action="store_true",
                        help="Sample 5 questions, print full prompt + raw response to stdout "
                             "(OpenAI --mcq only; useful for debugging parse failures)")
    parser.add_argument("--verbose-report", action="store_true",
                        help="Also write a detailed per-question markdown report "
                             "(--full-eval and --mcq modes)")
    parser.add_argument("--n-bootstrap", type=int, default=1000,
                        help="Number of bootstrap iterations for confidence intervals "
                             "(default: 1000)")
    parser.add_argument("--reasoning-effort", default="none",
                        choices=["none", "minimal", "low", "medium", "high"],
                        help="Reasoning effort for OpenAI models via Responses API "
                             "(default: medium)")
    parser.add_argument("--no-json-schema", action="store_true",
                        help="Skip JSON schema constraint; rely on instructions for "
                             "output format (OpenAI --mcq only)")

    args = parser.parse_args()

    if args.device is not None and args.device_map is not None:
        parser.error("--device and --device-map are mutually exclusive")

    if args.api == "together":
        if args.full_eval:
            report = full_eval_together(
                args.model_id, args.path_to_jsonl,
                api_key_path=args.together_key,
                verbose_report=args.verbose_report,
                n_bootstrap=args.n_bootstrap,
            )
        elif args.mcq:
            report = mcq_eval_together(
                args.model_id, args.path_to_jsonl,
                api_key_path=args.together_key,
                include_negation=args.include_negation,
                verbose_report=args.verbose_report,
                n_bootstrap=args.n_bootstrap,
            )
        else:
            parser.error("--api together requires --full-eval or --mcq")
    elif args.vllm:
        report = test_five_questions(args.model_id, args.path_to_jsonl)
    elif args.full_eval:
        if is_openai_model(args.model_id):
            parser.error(
                f"'{args.model_id}' is an OpenAI API model. "
                "Log-likelihood scoring (--full-eval) is not supported for the Responses "
                "API. Use --mcq instead."
            )
        report = full_eval_hf(
            args.model_id, args.path_to_jsonl,
            device=args.device,
            device_map=args.device_map,
            trust_remote_code=args.trust_remote_code,
            verbose_report=args.verbose_report,
            n_bootstrap=args.n_bootstrap,
            quantize=args.quantize,
            lora_adapter=args.lora_adapter,
        )
    elif args.mcq:
        if is_openai_model(args.model_id):
            report = mcq_eval_openai(
                args.model_id, args.path_to_jsonl,
                credentials_path=args.credentials,
                include_negation=args.include_negation,
                trace=args.trace,
                verbose_report=args.verbose_report,
                n_bootstrap=args.n_bootstrap,
                reasoning_effort=args.reasoning_effort,
                use_json_schema=not args.no_json_schema,
            )
        else:
            report = mcq_eval_hf(
                args.model_id, args.path_to_jsonl,
                device=args.device,
                device_map=args.device_map,
                trust_remote_code=args.trust_remote_code,
                include_negation=args.include_negation,
                verbose_report=args.verbose_report,
                n_bootstrap=args.n_bootstrap,
                quantize=args.quantize,
                lora_adapter=args.lora_adapter,
            )
    else:
        report = test_five_questions_hf(
            args.model_id, args.path_to_jsonl,
            device=args.device,
            device_map=args.device_map,
            trust_remote_code=args.trust_remote_code,
            n_bootstrap=args.n_bootstrap,
            quantize=args.quantize,
            lora_adapter=args.lora_adapter,
        )
    print(f"Report written to: {report}")

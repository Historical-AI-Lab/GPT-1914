# benchmark_evaluation.py — CLI Reference

```
python benchmark_evaluation.py MODEL_ID PATH_TO_JSONL [options]
```

## Positional arguments

| Argument | Description |
|----------|-------------|
| `model_id` | HF model ID or local path (HF mode); Together AI model name (`--api together`); OpenAI model name (auto-detected with `--mcq`); vLLM model name (`--vllm`) |
| `path_to_jsonl` | Path to benchmark questions JSONL file |

---

## Evaluation modes

If none of these flags is given, the script runs a **five-question smoke test** (HF path only): samples 5 questions at random and writes a JSON + markdown report.

| Flag | Description |
|------|-------------|
| `--full-eval` | Score every question in the JSONL via log-likelihood (Brier score). HF and Together AI paths only. Not supported for OpenAI models. |
| `--mcq` | Present each question as a lettered multiple-choice prompt and score top-1 accuracy. Supported on all paths. OpenAI models are auto-detected and routed to the Responses API. |

`--full-eval` and `--mcq` are mutually exclusive.

---

## Backend / API selection

| Flag | Default | Description |
|------|---------|-------------|
| `--api together` | — | Route to Together AI's OpenAI-compatible API. Requires `evalcode/TogetherAPIKey.txt`. Use with `--full-eval` or `--mcq`. |
| `--vllm` | — | Use the legacy vLLM endpoint (OpenAI-compatible, requires a running vLLM server on port 9011). Runs the five-question smoke test only. |
| `--together-key PATH` | `evalcode/TogetherAPIKey.txt` | Path to Together AI API key file. |
| `--credentials PATH` | `evalcode/credentials.txt` | Path to OpenAI credentials file (line 1: org ID, line 2: API key). |

If neither `--api together` nor `--vllm` is set, and the model ID does not match an OpenAI pattern, the **HuggingFace path** is used (default).

OpenAI model IDs are auto-detected by prefix (`gpt-4.1`, `gpt-5`, `ft:gpt-4.1-`, `ft:gpt-5-`). When detected with `--mcq`, the Responses API is used automatically — no extra flag needed.

---

## Device / hardware (HF path only)

| Flag | Default | Description |
|------|---------|-------------|
| `--device mps\|cuda\|cpu` | auto-detect | Pin the model to a specific device. Auto-detect order: MPS → CUDA → CPU. Mutually exclusive with `--device-map`. |
| `--device-map auto` | — | Use HuggingFace Accelerate to shard the model across multiple GPUs. Pass `auto` to let Accelerate decide placement. Mutually exclusive with `--device` and `--quantize`. |
| `--quantize int4\|int8` | — | Quantize weights with torchao before inference. `int4` ≈ 4 GB for 7B / 12 GB for 24B. Works on MPS and CUDA. Requires `pip install torchao`. Mutually exclusive with `--device-map`. |
| `--trust-remote-code` | off | Pass `trust_remote_code=True` to HuggingFace `from_pretrained`. |
| `--lora-adapter PATH` | — | Attach a LoRA/QLoRA adapter checkpoint to the base model after loading. Requires `pip install peft`. |

---

## Output control

| Flag | Default | Description |
|------|---------|-------------|
| `--output-dir DIR` | same directory as input JSONL | Directory where JSON and markdown report files are written. Created automatically if it does not exist. |
| `--verbose-report` | off | Also write a detailed per-question markdown report alongside the JSON report (`--full-eval` and `--mcq` modes). |
| `--n-bootstrap N` | 1000 | Number of bootstrap iterations for confidence intervals on Brier score, skill score, and accuracy. |

---

## MCQ-specific options

| Flag | Default | Description |
|------|---------|-------------|
| `--include-negation` | off | Include negation-type distractor answers in the MCQ choices. |
| `--trace` | off | Sample 5 questions, print the full prompt and raw model response to stdout. OpenAI `--mcq` only; useful for debugging parse failures. |
| `--reasoning-effort none\|minimal\|low\|medium\|high` | `none` | Reasoning effort budget for OpenAI models via the Responses API. |
| `--no-json-schema` | off | Disable JSON schema structured output for OpenAI models; fall back to instruction-based formatting. |

---

## Output files

All report files are written to the input JSONL's directory by default, or to `--output-dir` if specified. Filenames include the model name (with `:` and `/` replaced by `_`) and a `YYYYMMDD_HHMMSS` timestamp.

| Mode | JSON report | Markdown report (with `--verbose-report`) |
|------|-------------|------------------------------------------|
| Five-question smoke test (HF) | `eval_results_{model}_{ts}.json` | `eval_report_{model}_{ts}.md` (always written) |
| `--full-eval` | `eval_results_full_{model}_{ts}.json` | `eval_report_full_{model}_{ts}.md` |
| `--mcq` | `eval_results_mcq_{model}_{ts}.json` | `eval_report_mcq_{model}_{ts}.md` |

---

## Examples

```bash
# Five-question smoke test on gpt2 (CPU, no GPU needed)
python benchmark_evaluation.py gpt2 booksample/first100.jsonl

# Full probabilistic eval, Qwen 7B on a single GPU
python benchmark_evaluation.py Qwen/Qwen2.5-7B-Instruct \
    booksample/chronologic_en_0.1.jsonl \
    --full-eval --verbose-report \
    --output-dir prob_results

# Full probabilistic eval, Qwen 32B across two A100s
python benchmark_evaluation.py Qwen/Qwen2.5-32B-Instruct \
    booksample/chronologic_en_0.1.jsonl \
    --device-map auto \
    --full-eval --verbose-report \
    --output-dir prob_results

# MCQ eval, Qwen 7B with int4 quantization on MPS
python benchmark_evaluation.py Qwen/Qwen2.5-7B-Instruct \
    booksample/chronologic_en_0.1.jsonl \
    --mcq --quantize int4 \
    --output-dir mcq_results

# MCQ eval, fine-tuned Qwen with a LoRA adapter
python benchmark_evaluation.py Qwen/Qwen2.5-7B-Instruct \
    booksample/chronologic_en_0.1.jsonl \
    --mcq --lora-adapter ../qwentuning/checkpoints/run1/checkpoint-3500 \
    --output-dir mcq_results

# Full eval via Together AI
python benchmark_evaluation.py mistralai/Mistral-Small-3.1-24B-Instruct-2503 \
    booksample/chronologic_en_0.1.jsonl \
    --api together --full-eval --verbose-report \
    --output-dir prob_results

# MCQ eval, OpenAI GPT-4.1 (auto-detected, uses Responses API)
python benchmark_evaluation.py gpt-4.1-2025-04-14 \
    booksample/chronologic_en_0.1.jsonl \
    --mcq --verbose-report \
    --output-dir mcq_results

# MCQ eval, OpenAI with higher reasoning effort
python benchmark_evaluation.py gpt-5.4 \
    booksample/chronologic_en_0.1.jsonl \
    --mcq --reasoning-effort medium \
    --output-dir mcq_results
```

# evalcode

This directory contains `benchmark_evaluation.py`, the primary script for testing language models against the ChronoLogic benchmark. The script accepts a JSONL file of benchmark questions and a HuggingFace model identifier, loads the model locally via `transformers`, and writes a per-question markdown report alongside the JSONL file. A summary line is also printed to stdout. The default device is auto-detected (MPS on Apple Silicon, then CUDA, then CPU), making the script usable without a GPU server. A legacy path using a running vLLM endpoint is available via `--vllm` but is no longer the primary route.

## Probabilistic evaluation (Brier score)

The probabilistic path scores every candidate answer by measuring how well the model predicts its tokens in context. For each answer option the script constructs the full prompt — optionally prepending the question's `metadata_frame`, then `QUESTION: <text>\nANSWER:` — and concatenates the candidate answer string. It runs a forward pass through the model and extracts the log-probability of each answer token given all preceding tokens, averaging these to produce a single score per answer (average log-probability per token, the quantity inside the exponent of perplexity). Those raw log-scores are then converted to a proper probability distribution via softmax, so the model's uncertainty is spread across all options rather than evaluated in isolation. The **Brier score** for a question is the mean squared error between the ground-truth probability vector (1.0 for the correct answer(s), 0.0 for distractors) and the model's softmax distribution, averaged over all options so that questions with more answer choices are not penalized. A perfect model scores 0.0; a model that puts all probability on the wrong answer scores 1.0. The full-eval report includes per-question Brier scores and a summary table of mean Brier score overall and broken down by `question_category`.

## MCQ evaluation (accuracy and skill score)

The MCQ path presents each question as a lettered multiple-choice prompt and asks the model to generate the letter of the correct answer. Answer options (excluding `negation`-type answers by default) are shuffled randomly and labeled A, B, C, …; the prompt ends with `Respond only with the letter of the correct answer:`. The model generates up to 10 tokens and the first uppercase letter in the output is taken as its choice. The report records top-1 **accuracy** — the fraction of questions where the chosen letter matches the ground-truth answer — both overall and by category. Because questions vary in the number of options (and therefore in the chance baseline), the report also computes a chance-adjusted **skill score** per question: `(observed − chance) / (1 − chance)`, where `observed` is 1 if correct and 0 otherwise, and `chance = r / k` (r correct options out of k total shown). This rescales performance so that 1.0 is perfect, 0.0 is what a random guesser would achieve in expectation, and negative values indicate below-chance performance. Per-question skill scores are averaged to produce overall and per-category means, reported alongside accuracy in the summary table.

## Command-line usage

```
python evalcode/benchmark_evaluation.py <model_id> <path_to_jsonl> [options]
```

| Flag | Effect |
|------|--------|
| *(no flag)* | Score 5 randomly sampled questions; write a Brier-score report |
| `--full-eval` | Score every question; write a full Brier-score report with category breakdown |
| `--mcq` | Present MCQ prompts; write an accuracy + skill-score report with category breakdown |
| `--include-negation` | Include `negation`-type answers as MCQ distractors (excluded by default) |
| `--device cpu\|cuda\|mps` | Override the auto-detected device |
| `--trust-remote-code` | Pass `trust_remote_code=True` to HuggingFace `from_pretrained` calls |
| `--vllm` | Use the legacy vLLM endpoint instead of HuggingFace (requires a server on port 9011; scores 5 questions only) |

**Examples:**

```bash
# Quick sanity check — 5 questions, Brier score
python evalcode/benchmark_evaluation.py Qwen/Qwen2.5-7B-Instruct booksample/all_benchmark_questions.jsonl

# Full probabilistic evaluation
python evalcode/benchmark_evaluation.py Qwen/Qwen2.5-7B-Instruct booksample/all_benchmark_questions.jsonl --full-eval

# MCQ evaluation (accuracy + skill score)
python evalcode/benchmark_evaluation.py Qwen/Qwen2.5-7B-Instruct booksample/all_benchmark_questions.jsonl --mcq

# Force CPU; include negation distractors
python evalcode/benchmark_evaluation.py gpt2 booksample/all_benchmark_questions.jsonl --mcq --device cpu --include-negation
```

Reports are written to the same directory as the input JSONL, named `eval_report_<model>_<timestamp>.md` (probabilistic) or `eval_report_mcq_<model>_<timestamp>.md` (MCQ).

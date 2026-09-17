# evalcode - directly evaluating models against ground truths and distractors

This directory contains `benchmark_evaluation.py`, the primary script for directly testing language models against the Chronologic benchmark. The script accepts a JSONL file of benchmark questions and a HuggingFace model identifier, loads the model locally via `transformers`, and writes a per-question markdown report alongside the JSONL file. A summary line is also printed to stdout. The default device is auto-detected (MPS on Apple Silicon, then CUDA, then CPU), making the script usable without a GPU server. A legacy path using a running vLLM endpoint is available via `--vllm` but is no longer the primary route.

## Probabilistic evaluation

The probabilistic path scores every candidate answer by measuring how well the model predicts its tokens in context. For each answer option the script constructs the full prompt — prepending the question's `metadata_frame`, then `QUESTION: <text>\nANSWER:` — and concatenates the candidate answer string. It runs a forward pass through the model and extracts the log-probability of each answer token given all preceding tokens, averaging these to produce a single score per answer (average log-probability per token, the quantity inside the exponent of perplexity). Those raw log-scores are then converted to a proper probability distribution via softmax, so the model's uncertainty is spread across all options rather than evaluated in isolation. The **Brier score** for a question is the mean squared error between the ground-truth probability vector (1.0 for the correct answer(s), 0.0 for most distractors) and the model's softmax distribution, averaged over all options so that questions with more answer choices are not penalized. A perfect model scores 0.0; a model that puts all probability on the wrong answer scores 1.0. The full-eval report includes per-question Brier scores and a summary table of mean Brier score overall and broken down by `question_category`.

## MCQ evaluation 

Multiple-choice scores are not reported in our paper. But we document this scoring pathway, since it is used as a component in the memorization and self-rejection tests.

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
python evalcode/benchmark_evaluation.py Qwen/Qwen2.5-7B-Instruct booksample/chronologic_en_1.0.jsonl

# Full probabilistic evaluation
python evalcode/benchmark_evaluation.py Qwen/Qwen2.5-7B-Instruct booksample/chronologic_en_1.0.jsonl --full-eval

# MCQ evaluation (accuracy + skill score)
python evalcode/benchmark_evaluation.py Qwen/Qwen2.5-7B-Instruct booksample/chronologic_en_1.0.jsonl --mcq

# Force CPU; include negation distractors
python evalcode/benchmark_evaluation.py gpt2 booksample/chronologic_en_1.0.jsonl --mcq --device cpu --include-negation
```

Reports are written to the same directory as the input JSONL, named `eval_report_<model>_<timestamp>.md` (probabilistic) or `eval_report_mcq_<model>_<timestamp>.md` (MCQ).

## Hosted models

`--api together|openrouter|openai` routes the same evaluation through a hosted endpoint
instead of loading weights locally. Keys are read from `evalcode/credentials.txt`
(OpenAI), `evalcode/TogetherAPIKey.txt`, or `bertclassify/OpenRouterCredentials.txt`;
override with `--credentials`, `--together-key`, `--openrouter-key`. Reasoning models take
`--reasoning-effort {none,minimal,low,medium,high,max}`.

For large open-weight models, `--quantize int4|int8` and `--device-map` make a 72B model
fit where it otherwise would not.

## The leaderboard

`make_leaderboard_table.py` turns a directory of `eval_results_full_*.json` into the
leaderboard in three formats — CSV, Markdown and LaTeX. The published version, covering the
seven models in the paper's Table 1, is in [`../results/likelihood/`](../results/likelihood).

Working output lives in `prob_08/` (probabilistic) and the `mcq_*/` directories. Note that
`eval_results_full_*.json` records every scored answer option verbatim, so those files
carry the benchmark's answers and are deliberately not committed.

## The self-rejection experiment

`self_rejection_test.py` asks whether a model can recognize its own wrong answers. Taking
the questions a model got wrong in a completed free-generation run, it rebuilds each as a
two-choice MCQ — ground truth against the model's own failed answer — and re-administers it
to the same model.

The result bears on why this benchmark does not use multiple choice as its primary format:
every reasoning model tested rejected its own wrong answers at 71–84% accuracy, far above
chance. Recognizing an apt historical answer is substantially easier than producing one, so
an MCQ score would overstate the ability the benchmark is trying to measure.

It reuses existing artifacts only — `modelasjudge/generated_answers/`,
`modelasjudge/scored_answers/`, and the benchmark — and shells out to
`benchmark_evaluation.py --mcq` to administer the retest, so it is cheap to re-run for any
candidate that already has a scored generative run. Per-candidate output is in
`self_rejection/<candidate>/`, with the cross-model summary in `self_rejection/analysis/`
and `self_rejection_ledger.csv`.

## Other scripts here

| Script | Does |
|---|---|
| `benchmark_free_generation.py` | Collects free-generated answers only; the scoring lives in `../modelasjudge/` |
| `make_benchmark_diff.py`, `integrate_diff_results.py` | Build and fold in a diff of two benchmark versions, so an updated version can be scored without re-running unchanged questions |
| `plot_*.py` | Figures, including `plot_self_rejection_scatter.py` for the paper's self-rejection figure |
| `talkie_backend.py` | Adapter for the Talkie-1930 models, which are not HuggingFace-hosted |
| `*.slurm` | Cluster jobs for the larger open-weight evaluations |

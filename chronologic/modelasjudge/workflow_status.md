# model-as-judge workflow: status and remaining steps

This document is the map for the multi-stage scoring pipeline. Each section
lists the script, its status, canonical input/output paths, and open work items.

---

## Module inventory

The pipeline separates **shared library modules** (no `__main__`, imported by
multiple stage scripts) from **stage scripts** (each runs as a CLI tool).

### Shared library modules

| Module | Role | Imported by |
|---|---|---|
| `naming.py` | Filesystem-safe tag helpers (`candidate_tag`, `judge_tag`, `benchmark_version`, `sanitize`). Every script that reads or writes `generated_answers/` or `scored_answers/` imports this so filenames are consistent. | `free_generation`, `judge_scoring`, `judge_reliability`, `discriminative_scoring`, `human_scoring`, `score_calculation`, `bootstrap_confidence`, `bayes_correction`, `free_gen_adapter` |
| `judge_prompts.py` | Pure prompt-building module: `build_judge_prompt`, `parse_judge_response`, `assign_positions`, `score_one_comparison`. No network calls or file I/O. Centralises prompt strings and scoring logic so they're never duplicated. | `judge_scoring`, `judge_reliability`, `inspect_judge_prompts` |
| `openrouter_client.py` | OpenRouter API wrapper: `is_openrouter_model`, `load_openrouter_api_key`, `make_openrouter_client`, `call_openrouter_chat`. Also used for direct Anthropic and OpenAI calls via the OpenRouter unified endpoint. | `free_generation`, `judge_scoring`, `judge_reliability` |

### External dependencies (outside this directory)

Two modules from other parts of the repo are imported directly:

- **`../bertclassify/filter_balance_clean.py`** — `normalize_text` used by
  `discriminative_scoring.py` to normalise text before DeBERTa inference.
- **`../evalcode/benchmark_evaluation.py`** — benchmark-loading utilities used
  by `free_generation.py`.

Both must be on `sys.path` (or the scripts run from `modelasjudge/` with the
repo root also on the path) for the imports to resolve.

### Stage scripts (one per pipeline stage)

`free_generation`, `judge_reliability`, `judge_scoring`, `discriminative_scoring`,
`human_scoring`, `score_calculation`, `bootstrap_confidence`, `bayes_correction`.

Calibration sub-pipeline (run once per benchmark version, not per candidate model):
`build_benchmark_data`, `build_anachronic_pairs`, `build_ground_truth_pairs`,
`run_deberta_pairs`, `train_logistic`, `compute_per_question_reliability`.

---

## Relationship between Stage 5 scripts

For the most part, `bayes_correction.py` should be understood as a substitute for the largely deprecated `bootstrap_confidence.py`. The bootstrap part of `bootstrap_confidence.py` is valid, but it also does other things that are iffy and should not be relied upon. Probably would be a good idea to move its functions over to the current script (`bayes_correction.py`) entirely.

But at present, `bayes_correction.py` imports three data-loading helpers from
`bootstrap_confidence` (`SCORED_DIR`, `compute_raw_observed`, `load_inputs`) to
avoid duplicating I/O logic, but otherwise runs an independent PyMC hierarchical
model. The README describes the Bayesian approach as the preferred method for the
paper; bootstrap CIs are retained as a fast cross-check that requires no PyMC
installation.

---

## File-naming conventions

All per-candidate output files share the suffix `{candidate}__{version}` so they
can be auto-paired by `score_calculation.py`. The `{candidate}` tag is produced by
`naming.candidate_tag(model_id)` — characters outside `[a-zA-Z0-9_\-.]` become
underscores. All scripts that touch `generated_answers/` or `scored_answers/`
import from `naming.py`.

| Stage                       | Directory          | Filename pattern                                     |
|-----------------------------|--------------------|------------------------------------------------------|
| Free generation             | `generated_answers/` | `free_gen_{candidate}__{version}.json`             |
| LLM judge (raw)             | `scored_answers/`  | `judge_{judge}__{candidate}__{version}.json`         |
| LLM judge (post-human)      | `scored_answers/`  | `judge_{judge}__{candidate}__{version}_human.json`   |
| Discriminative judge        | `scored_answers/`  | `discrim_{deberta_tag}__{candidate}__{version}.json` |
| Final aggregated scores     | `scored_answers/`  | `final_{candidate}__{version}.json`                  |
| Cumulative human log        | `modelasjudge/`    | `human_judgments.jsonl`                              |

The `{deberta_tag}` is read from the `"tag"` field of
`calibration/logistic_calibrator.pkl` (set at training time via `--tag`).

---

## Stage 1 — Free generation

**Script:** `free_generation.py`  
**Status:** ✓ exists; multi-GT and reasoning_effort fields added  
**Input:** benchmark JSONL (e.g. `../booksample/chronologic_en_0.2.jsonl`), model ID  
**Output:** `generated_answers/free_gen_{candidate}__{version}.json`

Output schema:
```json
{
  "model": "Qwen/Qwen2.5-7B-Instruct",
  "reasoning_effort": "none",
  "answers": {
    "<qnum>": {
      "metadata_frame": "...",
      "main_question": "...",
      "ground_truths": ["answer1", "answer2"],
      "reasoning_type": "inference",
      "length_spec": "...",
      "answer": "..."
    }, ...
  }
}
```

Open items: none.

---

## Stage 2a — LLM-judge reliability (prerequisite, runs once per judge)

**Script:** `judge_reliability.py`  
**Status:** ✓ exists and complete  
**Input:** benchmark JSONL, judge model ID  
**Output:** `llm_reliability/{judge}__{version}.json`

Output schema (per question):
```json
{
  "question_r": 0.91, "question_weight": 0.68,
  "context_r":  0.88, "context_weight":  0.58,
  ...
}
```

Must be run *before* `judge_scoring.py` for any new judge model.
Existing files: `anthropic_claude-sonnet-4-6__0.2.json`, `openai_gpt-4o-mini__0.2.json`.

---

## Stage 2b — Discriminative-judge reliability (prerequisite, runs once)

**Scripts:** (pipeline)
1. `build_anachronic_pairs.py` — build GT vs. anachronic distractor pairs
2. `run_deberta_pairs.py` — score pairs with DeBERTa
3. `train_logistic.py --tag TAG` — fit logistic calibrator; embed tag in output
4. `compute_per_question_reliability.py` — compute per-question r_q, w_q

**Status:** ✓ all scripts exist; calibration files present in `calibration/`  
**Output:** `calibration/logistic_calibrator.pkl` (with `"tag"` field),
            `calibration/per_question_reliability_chronologic-0.2.jsonl`

Open items:
- Existing calibrator pickles and JSONs do not yet have a `"tag"` field. Before
  running `discriminative_scoring.py`, either re-run `train_logistic.py --tag TAG`
  or manually add `"tag": "<your-tag>"` to `calibration/logistic_calibrator.json`
  and re-pickle (or pass `--output` with an explicit tag to `discriminative_scoring.py`).

---

## Stage 3a — LLM judge scoring

**Script:** `judge_scoring.py`  
**Status:** ✓ exists; multi-GT, reliability join, needs_human added  
**Input:** free_gen JSON, judge model ID  
**Output:** `scored_answers/judge_{judge}__{candidate}__{version}.json`

Output schema summary:
```json
{
  "judge_model": "...", "candidate_model": "...",
  "candidate_reasoning_effort": "...",
  "question_fit": {
    "<qnum>": {
      "judge": "...", "r_q": 0.91,
      "judgments": ["GT", "tie"], "scores": [0, 1],
      "gt_positions": ["B", "A"], "gt_indices": [0, 0]
    }
  },
  "context_fit": { ... same shape ... },
  "needs_human": [{"qnum": "...", "aspects": ["question_fit"]}, ...]
}
```

`gt_indices` identifies which entry in `ground_truths` was used in each comparison —
necessary for bootstrap because comparisons against different GTs are independent
but repeated comparisons against the same GT are not.

If `needs_human` is empty, proceed directly to stage 4 (score_calculation).
If non-empty, pass to stage 3c (human_scoring) first.

---

## Stage 3b — Discriminative judge scoring

**Script:** `discriminative_scoring.py`  
**Status:** ✓ exists (newly written)  
**Input:** free_gen JSON, calibrator pickle, per-question reliability JSONL, DeBERTa model  
**Output:** `scored_answers/discrim_{deberta_tag}__{candidate}__{version}.json`

Output schema summary:
```json
{
  "judge_kind": "discriminative", "judge_tag": "...",
  "candidate_model": "...", "candidate_reasoning_effort": "...",
  "style": {
    "<qnum>": {
      "judge": "...", "r_q": 0.78, "w_q": 0.31,
      "gt_indices": [0], "deltas": [0.32],
      "p_anachronic": [0.61], "continuous_scores": [0.39],
      "continuous": 0.39
    }
  },
  "below_threshold": ["0123", ...]
}
```

No binarization in this file — `score_calculation.py` applies the 0.5 threshold.
Questions in `below_threshold` (r_q ≤ 0.70) get NA for style in score_calculation.

---

## Stage 3c — Human scoring (when needed)

**Script:** `human_scoring.py`  
**Status:** ✓ exists  
**Input:** `judge_{judge}__{candidate}__{version}.json` (which has a non-empty `needs_human`)  
**Output:** `judge_{judge}__{candidate}__{version}_human.json`

Spec (from `model_as_judge_overview.md` §Thresholding):
- Asks the human for a `human_reliability` value once at startup.
- For each question in `needs_human`, prints the metadata_frame, question, ground
  truth(s), and the aspects needing judgment.
- Before each aspect prompt, shows up to 5 precedents from `human_judgments.jsonl`.
- Records each judgment (0/1) and reason.
- Appends every judgment to `human_judgments.jsonl` (cumulative cross-model log).
- Produces the `_human` variant: replaces the LLM judge's name/score/r_q with
  `"human"`, the human score, and the provided `human_reliability` for affected questions.

Key schema note: the human judge provides a single 0 or 1 per question per aspect
(not a list of judgments), so the `_human` variant collapses the per-comparison
lists to a single-element list `[human_score]` for questions that were re-judged.

---

## Stage 4 — Score calculation

**Script:** `score_calculation.py`  
**Status:** ✓ exists  
**Input:** `judge_{judge}__{candidate}__{version}[_human].json` +
           `discrim_{deberta_tag}__{candidate}__{version}.json`  
**Output:** `scored_answers/final_{candidate}__{version}.json`

Spec (from `model_as_judge_overview.md` §Calculating weighted scores):
- Accept `--candidate` and `--version` flags (or a single `{candidate}__{version}` tag)
  and auto-locate the judge and discrim files by globbing `scored_answers/`.
- For each aspect (question_fit, context_fit, style):
  - Weighted mean of scores, weight = max(2 * r_q - 1, 0)² per question.
  - Style NAs (`below_threshold` qnums) are excluded from the mean.
- Overall binary accuracy: a question passes iff all three aspect scores ≥ 0.5.
  Style NA counts as a pass.
- Print provisional overall accuracy.
- The `final_` file should record per-question pass/fail for each aspect plus the
  three weighted aspect means and the overall binary accuracy.

---

## Stage 5 — Bootstrap confidence intervals

**Script:** `bootstrap_confidence.py`  
**Status:** ✓ exists  
**Input:** `judge_{judge}__{candidate}__{version}[_human].json` +
           `discrim_{deberta_tag}__{candidate}__{version}.json`  
**Output:** `scored_answers/bootstrap_{candidate}__{version}.json`

For each of N bootstrap iterations: resamples questions with replacement, draws
latent verdict posteriors from the Bayesian update given observed judge verdicts
and per-question reliability `r_q`.  Reports bias-corrected point estimates and
percentile CIs for the three aspect scores (linear and quadratic weighting) and
overall binary accuracy.

Key design points:
- Per-aspect scores use continuous posteriors (no Bernoulli sampling) → narrower CIs.
- Binary accuracy uses discrete Bernoulli draws per aspect + AND-aggregation → bias-
  corrected for the multiplicative compression that AND introduces over noisy gates.
- Within each question, comparisons against the same `gt_index` are collapsed into one
  block (agree = one observation; split = no observation) to avoid double-counting
  correlated evidence.
- `--include-r-uncertainty` samples `r_q` from a Beta posterior each iteration; requires
  `(k, n)` counts in the reliability files (already present in all current files).

```bash
# Quick smoke test (2000 iterations)
python bootstrap_confidence.py --candidate gpt-5.4 --version 0.2 --n-iterations 2000

# Full run (10000 iterations) with r uncertainty
python bootstrap_confidence.py --candidate gpt-5.4 --version 0.2 --include-r-uncertainty
```

---

## Quick-start commands (run from `modelasjudge/`)

### One-time prerequisites: LLM-judge reliability (once per judge model)

```bash
python judge_reliability.py --judge anthropic/claude-opus-4-7
# Output: llm_reliability/anthropic_claude-opus-4-7__0.2.json
```

### One-time prerequisites: discriminative calibration (once per benchmark version)

This sub-pipeline is documented in detail in `discriminative_calibration.md`.
Run the steps in order:

```bash
# 1. Extract per-question benchmark data (reasoning types, answer lengths, distractors)
python build_benchmark_data.py
# Output: calibration/benchmark_data_for_discrim_calibration.jsonl

# 2. Build GT-vs-anachronic pairs and GT-vs-GT pairs
python build_anachronic_pairs.py
python build_ground_truth_pairs.py
# Output: calibration/anachronic_pairs.jsonl, calibration/ground_truth_pairs.jsonl

# 3. Score both pair sets with DeBERTa
python run_deberta_pairs.py calibration/anachronic_pairs.jsonl \
    calibration/anachronic_pairs_scored.jsonl
python run_deberta_pairs.py calibration/ground_truth_pairs.jsonl \
    calibration/ground_truth_pairs_scored.jsonl

# 4. Train the logistic calibrator (--tag embeds a label in the pickle)
python train_logistic.py --tag deberta-baseline-2026-04
# Output: calibration/logistic_calibrator.pkl (with "tag" field),
#         calibration/logistic_calibrator.json

# 5. Compute per-question reliability (stratified by reasoning_type × length_decile)
python compute_per_question_reliability.py
# Output: calibration/per_question_reliability_chronologic-0.2.jsonl
```

### Per candidate model

```bash
# 1. Generate free answers
python free_generation.py gpt-4.1-2025-04-14 ../booksample/chronologic_en_0.2.jsonl
# Output: generated_answers/free_gen_gpt-4.1-2025-04-14__0.2.json

# 2a. LLM judge scoring
python judge_scoring.py generated_answers/free_gen_gpt-4.1-2025-04-14__0.2.json \
    --judge anthropic/claude-opus-4-7
# Output: scored_answers/judge_anthropic_claude-opus-4-7__gpt-4.1-2025-04-14__0.2.json

# 2b. Discriminative judge scoring
python discriminative_scoring.py generated_answers/free_gen_gpt-4.1-2025-04-14__0.2.json
# Output: scored_answers/discrim_<tag>__gpt-4.1-2025-04-14__0.2.json

# 3. (Only if needs_human is non-empty in the judge output) Human scoring
python human_scoring.py \
    scored_answers/judge_anthropic_claude-opus-4-7__gpt-4.1-2025-04-14__0.2.json
# Output: scored_answers/judge_anthropic_claude-opus-4-7__gpt-4.1-2025-04-14__0.2_human.json

# 4. Aggregated binary scores
python score_calculation.py --candidate gpt-4.1-2025-04-14 --version 0.2
# Output: scored_answers/final_gpt-4.1-2025-04-14__0.2.json

# 5a. Bootstrap confidence intervals (fast, no PyMC required)
python bootstrap_confidence.py --candidate gpt-4.1-2025-04-14 --version 0.2
# Output: scored_answers/bootstrap_gpt-4.1-2025-04-14__0.2.json

# 5b. Hierarchical Bayesian correction (preferred for paper; requires PyMC)
python bayes_correction.py --candidate gpt-4.1-2025-04-14 --version 0.2
# Output: scored_answers/bayes_gpt-4.1-2025-04-14__0.2.json
```

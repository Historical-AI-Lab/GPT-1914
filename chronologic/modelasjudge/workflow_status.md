# model-as-judge workflow: status and remaining steps

This document is the map for the multi-stage scoring pipeline. Each section
lists the script, its status, canonical input/output paths, and open work items.

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

```bash
# Prerequisites: judge reliability (once per judge)
python judge_reliability.py --judge anthropic/claude-opus-4-7

# Prerequisites: discriminative calibration (once)
python train_logistic.py --tag deberta-baseline-2026-04

# Per model being evaluated:

# 1. Generate answers
python free_generation.py gpt-4.1-2025-04-14 ../booksample/chronologic_en_0.2.jsonl

# 2a. LLM judge
python judge_scoring.py generated_answers/free_gen_gpt-4.1-2025-04-14__0.2.json \
    --judge anthropic/claude-opus-4-7

# 2b. Discriminative judge
python discriminative_scoring.py generated_answers/free_gen_gpt-4.1-2025-04-14__0.2.json

# 3. (If needs_human non-empty) Human scoring
python human_scoring.py \
    scored_answers/judge_anthropic_claude-opus-4-7__gpt-4.1-2025-04-14__0.2.json

# 4. Final scores
python score_calculation.py --candidate gpt-4.1-2025-04-14 --version 0.2
```

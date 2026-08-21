# Plan (follow-up): Combined alpha+beta reliability gate (0.7) + Bayesian context rework

> **Superseded.** This document predates the current two-path framing. ChronoLogic
> no longer claims a divide between a "question fit" construct and a "context fit"
> construct; it has a binary **pass/fail path** (`judge_scoring_nocontext.py`,
> instruction following + factual accuracy) and a continuous **partial-credit path**
> (`bt_context_scoring.py`) whose criteria are a superset of those. The final scoring
> stage is `score_substantive.py`. Kept as a record of the reasoning at the time.
> See `substantive-uncertainty-spec.md` and `estimator_and_calibration_explained.md`.

## Status

Spec only — **not yet implemented.** Saved to pause and execute later. Both design
decisions below are locked (confirmed with user); the three open questions in B3 still
need answers before Part B is built.

## Context

The just-completed "nocontext" refactor made the LLM judge score **question fit only**;
context fit moved to human judgment for `book_context` questions. Two loose ends remain:

1. **Routing gate is alpha-only.** `judge_scoring_nocontext.py` decides which questions
   need human re-judging of *question fit* using **alpha reliability only**
   (`question_r`, the type-I correct/total fraction) at threshold `<= 0.65`. It ignores
   beta (type-II, tie-blindness). A judge can have good alpha but poor beta on a question
   and still skip human review. **Decision (user): gate on `mean(alpha, beta)` at `0.7`
   for all modes.**

2. **Bayesian scripts read fields that no longer exist.** `bootstrap_confidence.py` and
   `bayes_correction.py` build a per-question Beta(k, n) posterior for context fit from
   `context_correct` / `context_total` in the LLM reliability file. After the nocontext
   change those LLM context counts are gone — context is now a **human binary (0/1)** with
   a **fixed `human_reliability`**, present only for `book_context` questions (NA → pass
   elsewhere). These two scripts currently break / silently zero-out context, and the
   hierarchical model in `bayes_correction.py` still couples context to the LLM reliability
   latent `theta_qc`.

This plan specs both. Part A is the smaller, higher-priority change; Part B is the larger
rework deferred from the nocontext plan.

---

## Data sources (confirmed during exploration)

- **Alpha**, per question — `llm_reliability/{judge}__{version}.json` → `per_question[qnum]`
  has `question_correct`, `question_total`, `question_r = correct/total ∈ [0,1]`
  (higher = better). Loaded today by `judge_scoring_nocontext.py:_load_reliability`.
- **Beta**, per length-stratum — `beta_reliability/{judge}__{version}.json` has
  `length_threshold_chars` (e.g. 33) and, under both `overall` and
  `by_length_bin.{short,long}`, a `question_fit` tally with `two_beta = k_nontie/n_tie_trials`
  (raw tie-recognition failure rate) and `beta = two_beta/2`. **Beta is not per-question** —
  the finest granularity is the short/long length bin, split at `length_threshold_chars`.

---

## Part A — Combined reliability gate in `judge_scoring_nocontext.py`

### A1. Define the combined reliability

For each question:
- `r_alpha` = `question_r` from the alpha file (as today).
- `r_beta` = `1 - beta` of the question's **length bin**, where `beta = two_beta/2` is the
  project's halved type-II rate: take the GT string length (`answer_strings[0]` from the
  benchmark JSONL), compare to `length_threshold_chars` (`<= threshold` → `short`, else
  `long`), read that bin's `question_fit.beta`. Fall back to `overall.beta` if the bin is
  empty.
- `r_combined = (r_alpha + r_beta) / 2`.

**Decision (user):** use the **halved** rate (`r_beta = 1 - beta`), not `1 - two_beta`.
Rationale: of the way beta trials are formed, the model gets **two chances to err** per tie
pair, so the raw `two_beta` failure rate is not parallel to alpha's single-shot correct/total.
Halving (`beta`) corrects for that double-exposure, making `r_beta` comparable to `r_alpha`
in the average.

### A2. Threshold

- Replace `_QUESTION_FIT_THRESHOLD = 0.65` with `0.7`.
- "All modes" = the single combined gate uses 0.7. This also matches the discriminative
  style NA threshold (0.70) already in `score_calculation.py`, so the two reliability gates
  in the pipeline become numerically consistent.

### A3. Wiring

- **Load the beta file.** Add `_load_beta_reliability(path)` and a `--beta-reliability`
  override; auto-locate `beta_reliability/{judge}__{version}.json` (mirror the existing
  alpha `_load_reliability` / `reliability_source` pattern). Record the path in
  `output_data["beta_reliability_source"]`.
- **GT length map.** `judge_scoring_nocontext.py` already loads the benchmark JSONL for
  frame types (`_load_benchmark_frame_types`); extend it (or add a sibling) to also return
  `{qnum: len(answer_strings[0])}` so length-bin assignment needs no second pass.
- **Store all three reliabilities per question.** In `run_panel`, where the entry currently
  gets `r_q`, also compute and store `r_alpha`, `r_beta`, `r_combined`. Set the canonical
  `r_q = r_combined` so that **both routing and downstream weighting/posterior reflect the
  combined reliability** (downstream `score_calculation.py` and `bootstrap_confidence.py`
  read `question_fit[qnum].r_q`). Keep the existing `identity_match → 0.999` override on top
  of the combined value.
  - **Decision (user): combined everywhere.** `r_q = r_combined` drives both routing and
    downstream weighting/posterior. This shifts weighted means relative to the alpha-only
    baseline by design — beta-blindness should lower trust in the verdict everywhere, not
    only at the gate.
- **`_rebuild_needs_human`.** Gate question_fit on `r_combined` (via `r_q`):
  `if qf.get("r_q") is None or qf["r_q"] <= q_thresh: aspects.append("question_fit")`.
  Context-fit routing (book_context membership) is unchanged.
- **Resume logic.** Preserve the new per-question fields and `beta_reliability_source` when
  resuming an existing scoring file.

### A4. Schema delta (`judge_scoring_nocontext.py` output)

```json
"thresholds": {"question_fit": 0.7},
"reliability_source": "llm_reliability/...",
"beta_reliability_source": "beta_reliability/...",
"question_fit": {
  "<qnum>": {
    "r_q": 0.74,           // = r_combined (canonical, used downstream)
    "r_alpha": 0.81,
    "r_beta": 0.67,
    "judge": "...", "judgments": [...], "scores": [...], ...
  }
}
```

---

## Part B — Bayesian rework for human context (`bootstrap_confidence.py`, `bayes_correction.py`)

Context is no longer an LLM Beta(k, n) posterior. It is a **human binary 0/1** with a
**fixed reliability** `r = human_reliability`, stored in the judge file as
`context_fit[qnum] = {judge:"human", r_q:human_reliability, scores:[0|1...], gt_indices:[None]}`,
present only for `book_context` questions. Non-book_context: `context_fit[qnum]` absent → NA →
counts as a pass (already handled in `score_calculation.py`).

### B1. `bootstrap_confidence.py`

- **`_build_beta_counts` (≈ lines 130–145).** Remove the `context_fit` Beta entry
  (`context_correct`/`context_total` no longer exist). Question-fit Beta counts stay
  (`question_correct`/`question_total` — still produced by alpha; note these are alpha-only
  counts, *not* the combined `r_q`, so the `--include-r-uncertainty` sampler keeps using
  alpha's k/n while the point estimate uses combined `r_q`; flag this asymmetry for the user).
- **Context posterior.** Context uses the existing `posterior_z_llm(aspect_record, r_q)`
  machinery unchanged — feed `r_q = context_fit[qnum].r_q` (the human constant) and the human
  `scores`. No Beta sampling for context under `--include-r-uncertainty` (human reliability is
  a fixed input, not an estimated count). Absent context_fit → skip the aspect (NA/pass), as
  `score_calculation.py` already does.
- **`r_cf_obs` (≈ line 371).** Already reads `context_fit[qnum].r_q`; now that value is the
  human constant — no code change beyond tolerating absent entries (default to NA/skip rather
  than `0.0`).

### B2. `bayes_correction.py`

- **Aspect loop (≈ lines 170–201).** Stop reading `context_correct`/`context_total`. Context
  is observed human binary with fixed reliability.
- **Decouple context from the LLM reliability latent.** The model couples question and context
  via `theta_qc ~ N(0,1)` and a shared `beta[aspect]` (≈ lines 78, 302–308) on the assumption
  both are LLM-judged. Context is now human with fixed reliability, so it must **not** draw from
  the LLM reliability hierarchy. Options:
  1. **(Recommended)** Drop context from the `theta_qc`/`beta` LLM-reliability block entirely;
     fold the human context binary into overall accuracy via fixed-reliability `posterior_z`,
     exactly like `bootstrap_confidence.py`. Simplest, and matches the "context is not an LLM
     measurement" reality.
  2. Keep context in the model but pin its reliability to the human constant (a `Data`/`Deterministic`
     node) instead of a sampled latent. More faithful to a joint posterior but more invasive.
- **Coverage.** Restrict context contributions to `book_context` qnums (read
  `judge_data["book_context_qnums"]`); others NA.
- **Reporting maps (≈ lines 418–419, 447–448, 578–579).** Keep `context_fit` rows; they now
  summarize human context over book_context only. Document the coverage change.

### B3. Open design questions for Part B (resolve before implementing B)

1. r-uncertainty for human context: treat `human_reliability` as a fixed scalar (recommended,
   no Beta node) vs. give it a weak Beta prior.
2. Whether the bootstrap question-fit Beta sampler should keep using **alpha** k/n while the
   point estimate uses **combined** `r_q` (the only counts available are alpha's), or whether
   combined reliability should suppress r-uncertainty sampling for question-fit too.
3. Whether `bayes_correction.py` should keep a question-only LLM reliability hierarchy
   (`theta_q`) now that context has left it.

---

## Files to change

- `judge_scoring_nocontext.py` — Part A (gate, beta loader, GT-length map, schema). **Primary.**
- `bootstrap_confidence.py` — Part B1 (drop context Beta counts; fixed-reliability context).
- `bayes_correction.py` — Part B2 (decouple context from LLM latent; book_context coverage).
- `tests/test_judge_scoring.py` — extend `TestRebuildNeedsHuman` + reliability tests for the
  combined gate at 0.7 and the new `r_alpha`/`r_beta`/`r_combined` fields; add a stubbed beta
  file fixture.
- `tests/test_bootstrap_confidence.py`, `tests/test_bayes_correction.py` — update context
  expectations to human-binary + fixed reliability, book_context-only (these are the
  previously-noted failing/deferred tests).
- `score_calculation.py`, `judge_agreement_report.py` — no logic change expected (already
  tolerate absent context); re-verify after Part B.

---

## Verification

Run from `modelasjudge/` (project convention).

1. **Unit tests (no network):**
   ```bash
   pytest tests/test_judge_scoring.py tests/test_bootstrap_confidence.py \
          tests/test_bayes_correction.py -v
   ```
   Expect: combined gate at 0.7 routes a question whose `mean(alpha, beta) <= 0.7` to human
   even when alpha alone is > 0.7; per-question entries carry `r_alpha`/`r_beta`/`r_combined`;
   context handled as human-binary + fixed reliability, book_context-only.

2. **Scoring smoke (few real calls) — confirm beta join + gate:**
   ```bash
   python judge_scoring_nocontext.py generated_answers/free_gen_gpt-4.1__0.2.json \
       --judge openai/gpt-4o-mini --limit 8
   # inspect: question_fit entries have r_alpha/r_beta/r_combined; beta_reliability_source set;
   # needs_human reflects the 0.7 combined gate
   ```
   (Requires `llm_reliability/` and `beta_reliability/` files for the judge+version; if missing,
   run the alpha/beta reliability scripts first or point `--beta-reliability` at a stub.)

3. **End-to-end Bayesian path:**
   ```bash
   python human_scoring.py scored_answers/judge_*__gpt-4.1__0.2.json --reliability 0.9
   python bootstrap_confidence.py --candidate gpt-4.1 --version 0.2
   python bayes_correction.py    --candidate gpt-4.1 --version 0.2
   ```
   Expect: no `KeyError` on `context_correct`/`context_total`; context contributions appear
   only for book_context questions; overall accuracy stable vs. `score_calculation.py`.

---

## Implementation order

1. Part A in `judge_scoring_nocontext.py` (beta loader → GT-length map → combined `r_q` →
   threshold 0.7 → `_rebuild_needs_human`), then its tests. Ship/validate independently.
2. Resolve the B3 design questions with the user.
3. Part B1 (`bootstrap_confidence.py`), then B2 (`bayes_correction.py`), then their tests.
4. Re-run `score_calculation.py` + `judge_agreement_report.py` to confirm no regressions.

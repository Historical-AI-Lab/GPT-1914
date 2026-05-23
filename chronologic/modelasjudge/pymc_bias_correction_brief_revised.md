# Hierarchical Bias-Correction for ChronoLogic Binary Accuracy

## Purpose

This document specifies a Bayesian hierarchical model for estimating the true binary accuracy of a model evaluated on the ChronoLogic benchmark, correcting for multiplicative bias introduced by noisy judge aggregation. The intended implementation is in PyMC. This is a self-contained brief: it should give a fresh LLM (or a fresh-eyed reader) everything needed to design and write the model without external context.

## Background: ChronoLogic and the existing pipeline

ChronoLogic is a benchmark that evaluates whether language models can authentically represent historical perspectives from the 1875–1924 period. For each question, a candidate model generates a free-form answer, which is then scored on three aspects:

- **Question fit**: whether the answer is substantively correct.
- **Context fit**: whether the answer fits the specified historical context (a metadata frame indicating source author, year, genre, etc.).
- **Style fit**: whether the answer's prose style is appropriate to the period.

Question fit and context fit are judged by an LLM that compares the candidate's answer against the ground truth(s) in a forced-choice prompt. Each comparison produces a binary verdict: 1 if the model's answer was judged at least as good as ground truth, 0 otherwise. Style fit is judged by a fine-tuned DeBERTa classifier whose logistic output gives a continuous score in [0, 1] representing P(this answer is period-authentic).

Each judge has a per-question reliability `r_q ∈ [0.5, 1.0]`, estimated empirically on a calibration set against known distractors. The LLM judge has high reliability on most questions (~0.95 for both aspects). The style judge has moderate reliability that varies by stratum (defined by reasoning_type × length decile); typical ~0.75 on average.

The existing pipeline computes:

1. **Per-aspect scores**: weighted means of observed scores per aspect, with weights `w_q = max(2·r_q − 1, 0)^k` for k = 1 (linear) or k = 2 (quadratic).

2. **Overall binary accuracy**: fraction of questions where all three aspect scores exceed 0.5 (with style NAs counting as automatic passes).

Questions with `r_q ≤ 0.65` on the LLM aspects are punted to a human judge with a known (and typically higher) reliability. Style questions with `r_q ≤ 0.70` are flagged NA and excluded from the per-aspect style score.

## The problem

The binary accuracy score has a known multiplicative bias. Under a binary symmetric channel with reliability `r_a` per aspect:

```
observed_pass_rate_per_aspect = π_a · (2·r_a − 1) + (1 − r_a)
```

where π_a is the true pass rate. When three noisy aspects are ANDed per question, the multiplicative compression toward the noise floor (0.5)³ = 0.125 is substantial — especially for strong models near the accuracy ceiling. A model with true per-aspect performance of 0.9 across three aspects with `r = (0.95, 0.95, 0.78)` will produce an expected raw binary score about 10 percentage points below the truth.

The frequentist per-aspect correction is closed-form:

```
π̂_a = (observed_a − (1 − r̄_a)) / (2·r̄_a − 1)
```

But naively multiplying disattenuated per-aspect estimates assumes aspect-independence, which empirically fails. In ChronoLogic, the dependence is not uniform across all three aspects: question fit and context fit are empirically correlated, while style fit is close to independent of both. A typical pattern is that raw question/context performance is jointly high or low, while style varies on a separate axis. The hierarchical model below captures this block structure explicitly, rather than either multiplying independent marginals or forcing all three aspects onto one shared dimension.

A previous attempt to correct for bias used Bayesian posterior averaging in a bootstrap: per question, sample `z ~ Bernoulli(P(z=1 | obs))`, average over questions. This turned out to be the wrong tool — it computes `E[P(z|obs)] = π·(2r−1)² + 2r(1−r)`, which is shrunk *toward* 0.5 rather than disattenuated *away* from it. The result was that per-aspect "corrected" values regressed to 0.5 (helpful only for style, which was below 0.5), and binary accuracy stayed essentially unchanged because the asymmetric shrinkage effects on passing vs. failing questions nearly canceled. The hierarchical model below avoids this trap by estimating latent population proportions directly rather than averaging per-question posteriors.

## Data structures (input format)

For each question `q ∈ {1, ..., N}`, available data:

- `qnum`: question identifier
- `reasoning_type`: categorical (knowledge, inference, character_modeling, ...)
- `length_decile`: integer 1–10, decile of mean answer length
- `style_na`: boolean — whether style is NA for this question

For each (question, aspect) pair where aspect ∈ {question_fit, context_fit, style}:

- `r_q`: per-question reliability (float in [0.5, 1.0]). For style this is stratified by `reasoning_type × length_decile` rather than per-question, so many questions share the same `r_q`.
- `observations`: a list of observation records. Each record has:
  - `verdict`: integer in {0, 1} for question/context, or float in [0, 1] for style.
  - `gt_index`: integer identifying which ground truth was used in this comparison.
  - `ordering`: 'A' or 'B' (which side ground truth was on in the prompt). Optional.

For style, the `verdict` is the continuous output `1 − p_anachronic` from the logistic model — i.e., the probability that the answer is period-authentic.

For questions with multiple ground truths (typical when the benchmark records more than one acceptable answer), the observation list will contain entries with different `gt_index` values. Repeated `gt_index` values within an aspect indicate paired observations (both orderings of the same GT versus candidate answer). These paired observations are correlated — they share the same answer pair and the same judge — and should be collapsed before being treated as independent evidence (see "Preprocessing" below).

Human-judged questions look identical to LLM-judged questions from the model's perspective; the only difference is the recorded `r_q` (typically `human_reliability`, a fixed value used for all human-judged questions in this run, derived from inter-annotator agreement on a sample).

Optionally, if reliability uncertainty is desired:

- `calibration_k[q, aspect]`: integer, correct judgments on calibration data.
- `calibration_n[q, aspect]`: integer, total judgments.

These let the model put `Beta(1 + k, 1 + n − k)` posteriors on each `r` rather than treating it as known.

## Preprocessing

Before feeding the model, collapse paired observations within each `gt_index` block:

- If both orderings agree (both 0 or both 1), treat as a single observation with that verdict.
- If they disagree, treat as a single observation with verdict ambiguous — best handled by dropping the pair (the two orderings cancel, providing information about judge order-bias on this item rather than about the latent verdict).

For style with continuous verdicts: average the continuous scores within each `gt_index` block before binarization (Option A) or before continuous likelihood (Option B). Across `gt_index` values within a question, treat the resulting observations as independent.

## The model

The proposed model is a block-structured multivariate-IRT-style latent ability model. Each question has two latent abilities: `θ_qc,q ∈ ℝ`, which governs substantive adequacy on question fit and context fit, and `θ_s,q ∈ ℝ`, which governs style fit. Aspects differ in their intercepts (`α_a`, the baseline difficulty of aspect a) and slopes (`β_a`, how strongly aspect-a passes depend on the relevant latent ability). The shared `θ_qc,q` induces correlation between question fit and context fit within questions: an answer that fails to address the question often also fails to fit the historical context. Style fit is modeled on a separate latent dimension, because empirical results suggest that period-authentic prose style is close to independent of substantive/contextual adequacy.

Generative process:

```
θ_qc,q ~ Normal(0, 1)                       # substantive/contextual ability per question
θ_s,q  ~ Normal(0, 1)                       # style ability per question, independent by default
α_a ~ Normal(0, 2)                          # aspect intercept, three values
β_a ~ HalfNormal(2)                         # aspect loading, three values, positive

p_{q,question} = σ(α_question + β_question · θ_qc,q)
p_{q,context}  = σ(α_context  + β_context  · θ_qc,q)
p_{q,style}    = σ(α_style    + β_style    · θ_s,q)
```

This structure is deliberately weaker than a single shared-ability model. It preserves the empirically important dependence between question fit and context fit, while avoiding the assumption that style rises and falls with them.

For each observation `v_{q,a,j}` of question q, aspect a, judgment j (with reliability `r_{q,a,j}`):

```
P(v = 1 | p_{q,a}, r) = p_{q,a} · r + (1 − p_{q,a}) · (1 − r)   # marginalized over z
v_{q,a,j} ~ Bernoulli( P(v = 1 | p_{q,a}, r) )
```

The marginalization over the latent discrete verdict z gives a continuous likelihood that NUTS can sample efficiently. This is the key technical move that lets the model run.

For style, the observation is the binarized continuous score (Option A, simpler) or the continuous score itself (Option B, preserves magnitude). See implementation notes below.

The quantity of interest, **binary accuracy**, is:

```
binary_accuracy = (1/N) · Σ_q [ p_{q, question} · p_{q, context} · effective_style_p_q ]

where effective_style_p_q = 1 if style_na[q] else p_{q, style}
```

Per-aspect accuracies:

```
accuracy_question = (1/N) · Σ_q p_{q, question}
accuracy_context  = (1/N) · Σ_q p_{q, context}
accuracy_style    = (1/N_non_na) · Σ_{q: not NA} p_{q, style}
```

These are continuous functions of latent parameters; their posteriors fall out of the trace.

## PyMC skeleton

```python
import pymc as pm
import pytensor.tensor as pt
import numpy as np

# --- Data preparation (assume done) ---
# After preprocessing, you have flat 1D arrays:
#   obs_question_idx[i]:  question index for observation i (0..N-1)
#   obs_aspect_idx[i]:    0 / 1 / 2 for question_fit / context_fit / style
#   obs_verdict[i]:       0 or 1 (after collapsing paired orderings)
#   obs_r[i]:             reliability for this observation
#
# Plus per-question style_na: shape (N,), boolean.

N = n_questions

with pm.Model() as model:
    # Hyperpriors
    alpha = pm.Normal('alpha', mu=0, sigma=2, shape=3)         # aspect intercepts
    beta = pm.HalfNormal('beta', sigma=2, shape=3)             # aspect loadings (positive)

    # Block-structured latent abilities.
    # theta_qc governs question_fit and context_fit.
    # theta_s governs style_fit and is independent by default.
    theta_qc = pm.Normal('theta_qc', mu=0, sigma=1, shape=N)
    theta_s = pm.Normal('theta_s', mu=0, sigma=1, shape=N)

    # Per-(question, aspect) pass probability, shape (N, 3)
    logit_question = alpha[0] + beta[0] * theta_qc
    logit_context  = alpha[1] + beta[1] * theta_qc
    logit_style    = alpha[2] + beta[2] * theta_s

    p_pass = pm.Deterministic(
        'p_pass',
        pt.stack([
            pm.math.sigmoid(logit_question),
            pm.math.sigmoid(logit_context),
            pm.math.sigmoid(logit_style),
        ], axis=1)
    )

    # Observation likelihood: marginalize z
    # P(v=1) = p_pass · r + (1 − p_pass) · (1 − r)
    obs_p_pass = p_pass[obs_question_idx, obs_aspect_idx]
    obs_likelihood = obs_p_pass * obs_r + (1 - obs_p_pass) * (1 - obs_r)
    pm.Bernoulli('obs', p=obs_likelihood, observed=obs_verdict)

    # Quantities of interest
    style_effective = pt.where(style_na, 1.0, p_pass[:, 2])
    pm.Deterministic(
        'binary_accuracy',
        pm.math.mean(p_pass[:, 0] * p_pass[:, 1] * style_effective)
    )
    pm.Deterministic('accuracy_question', pm.math.mean(p_pass[:, 0]))
    pm.Deterministic('accuracy_context',  pm.math.mean(p_pass[:, 1]))
    pm.Deterministic(
        'accuracy_style',
        pm.math.sum(p_pass[:, 2] * (1 - style_na)) / pm.math.sum(1 - style_na)
    )

    trace = pm.sample(2000, tune=1000, target_accept=0.9, chains=4)
```

For N of a few hundred questions and a few thousand total observations, this should sample in a few minutes on CPU. If you see divergences, raise `target_accept` to 0.95 and/or reparameterize `theta_qc` and `theta_s` non-centered.

## Refinements (optional)

### Style as continuous (Option B)

Replace the Bernoulli likelihood for style observations with a Normal in logit space:

```python
# For style observations only
s_clipped = np.clip(style_continuous_verdicts, 1e-3, 1 - 1e-3)
logit_s = np.log(s_clipped / (1 - s_clipped))

# Precision scales with reliability
# (heuristic; assumes r > 0.5)
sigma_style = 1.0 / (2 * obs_r_style - 1)

logit_p_style = pt.log(p_pass[style_obs_qidx, 2] / (1 - p_pass[style_obs_qidx, 2]))
pm.Normal('style_obs', mu=logit_p_style, sigma=sigma_style, observed=logit_s)
```

This preserves the magnitude of the logistic output and recovers the perfect-calibration limit as `r → 1`. The `1/(2r−1)` scaling for `sigma` is a heuristic; a more principled version would fit a calibration model from human-judged data.

If you do this, omit style from the Bernoulli observation block and use only the Normal likelihood above. The style entry in `p_pass[:, 2]` and the deterministic quantities of interest are unchanged.

### Reliability uncertainty

If calibration counts are available, put Beta posteriors on r rather than fixing it:

```python
# alpha_r, beta_r are shape (n_unique_r,)
# obs_r_idx[i] maps each observation to its r posterior index
r_samples = pm.Beta('r', alpha=alpha_r, beta=beta_r, shape=n_unique_r)
obs_r = r_samples[obs_r_idx]   # use this in the likelihood instead of fixed obs_r
```

This propagates reliability-estimation uncertainty into the posterior. For ChronoLogic's typical reliability sample sizes (n = 8–16 per question for LLM judges, larger for stratified style), this is a meaningful but secondary effect. Turn it on if you want to be thorough; leave it off for speed.

### Estimating residual style correlation

The default model assumes that the style dimension is independent of the substantive/contextual dimension. If you want the data to estimate whether style has some residual correlation with question/context performance, replace the two independent Normal priors with a two-dimensional latent ability:

```python
# Cholesky-parameterized correlation matrix for two latent dimensions:
# dimension 0 = question/context, dimension 1 = style
chol, corr, sigmas = pm.LKJCholeskyCov(
    'chol', n=2, eta=2.0, sd_dist=pm.HalfNormal.dist(1.0)
)
theta = pm.MvNormal('theta', mu=np.zeros(2), chol=chol, shape=(N, 2))

theta_qc = theta[:, 0]
theta_s = theta[:, 1]

logit_question = alpha[0] + beta[0] * theta_qc
logit_context  = alpha[1] + beta[1] * theta_qc
logit_style    = alpha[2] + beta[2] * theta_s

p_pass = pm.Deterministic(
    'p_pass',
    pt.stack([
        pm.math.sigmoid(logit_question),
        pm.math.sigmoid(logit_context),
        pm.math.sigmoid(logit_style),
    ], axis=1)
)
```

This is slightly more flexible but requires more data to identify the correlation between style and the question/context dimension. For most ChronoLogic-scale runs, the independent two-factor model is the safer default if prior analyses already show that style is nearly independent.

### Question-set bootstrap

The hierarchical model's posterior gives uncertainty about binary accuracy *on the observed N questions*. If you also want to characterize variance from a hypothetical larger question population (rare in benchmark reporting), bootstrap-resample questions and refit. Most reporting contexts treat the benchmark as fixed and don't need this.

## Output

Write `scored_answers/bayes_{candidate}__{version}.json`:

```json
{
  "candidate": "...",
  "version": "...",
  "n_iterations": 8000,
  "raw_observed": {
    "question_fit_linear": 0.821,    "question_fit_quadratic": 0.813,
    "context_fit_linear":  0.679,    "context_fit_quadratic":  0.673,
    "style_linear":        0.395,    "style_quadratic":        0.394,
    "binary_accuracy":     0.476
  },
  "bias_corrected": {
    "question_fit": {"mean": 0.857, "ci_lower": 0.832, "ci_upper": 0.881},
    "context_fit":  {"mean": 0.715, "ci_lower": 0.681, "ci_upper": 0.748},
    "style":        {"mean": 0.378, "ci_lower": 0.342, "ci_upper": 0.412},
    "binary_accuracy": {"mean": 0.583, "ci_lower": 0.521, "ci_upper": 0.642}
  },
  "estimated_bias": {
    "binary_accuracy": 0.107
  },
  "diagnostics": {
    "n_divergent": 0,
    "min_ess": 1247,
    "max_rhat": 1.003
  }
}
```

Print a human-readable summary alongside.

## Coexistence with the bootstrap pipeline

The hierarchical model and the bootstrap script `bootstrap_confidence.py` serve different purposes:

- **Bootstrap (`bootstrap_confidence.py`)**: captures question-sampling variance around the raw observed scores. Treats judges as known-noise observation tools. Useful when you want to report a CI around what the pipeline produces.
- **Hierarchical Bayesian (this document)**: estimates bias-corrected latent population proportions. Treats questions as fixed but explicitly models judge noise and the empirically observed aspect-correlation structure. Useful when you want to report what the model's accuracy *actually is* under the noise model.

For a paper, report both. The bootstrap CI tells the reader how the pipeline's output would fluctuate; the Bayesian posterior tells them the model's estimated true performance. Disagreement between them is informative — large gaps indicate that judge noise is doing significant work.

## Sanity checks

- **Synthetic recovery.** Generate data from the model with known `α`, `β`, `θ_qc`, and `θ_s`, then fit. Posterior means should recover the truth within CIs.
- **High-reliability limit.** With `r ≈ 1` for all observations, posterior on per-aspect accuracy should closely match raw observed; posterior on binary should closely match the block-structured joint estimate, preserving question/context correlation without forcing style to correlate with them.
- **Low-reliability limit.** With all `r = 0.5`, observations carry no information; posteriors should reflect the priors on `θ_qc` and `θ_s`, giving binary accuracy posterior around its prior-predictive mean (≈ 0.125 if priors center logits at 0).
- **Bias direction.** For a strong model (most observations = 1) with imperfect r, the posterior mean for binary accuracy should be *higher* than raw. For a weak model the gap should be smaller.
- **Posterior correlations.** Within posterior samples, question-fit and context-fit accuracies should be positively correlated. Style accuracy should not be forced to correlate strongly with them unless the optional residual-correlation model is used and the data support it.
- **Posterior predictive.** Simulate observations from the fitted model; the simulated raw binary should match the actual raw binary. If it doesn't, the model is misspecified.
- **MCMC diagnostics.** Standard checks: no divergences after tuning, R̂ < 1.01, ESS > 400 for all reported quantities. If the chain struggles, try non-centered parameterization of the latent abilities and tighter priors on α, β.

## What this model does not address

- Aspect-independent systematic biases — e.g., a judge that prefers verbose answers, or that confuses style with content. The model assumes per-judgment noise is Bernoulli with rate (1 − r_q) around the latent verdict, symmetric across z = 0 and z = 1.
- Calibration of the style logistic. Under Option B, the heuristic `σ_style = 1/(2r−1)` is a stand-in for a real calibration model. If miscalibration is suspected (e.g., the logistic always outputs values bunched in 0.3–0.7 regardless of truth), fit a calibration model from human-judged subsets.
- Selection bias in the benchmark. The model treats the N questions as fixed; posterior conclusions generalize only to this benchmark.
- Question-level dependencies beyond the block-structured latent abilities (e.g., topical clustering, repeated source authors). For most ChronoLogic uses this is fine; if not, add a higher-level grouping.

These limitations are worth flagging in any paper that reports the bias-corrected numbers, but they don't undermine the central correction for multiplicative aggregation bias, which is what the model is designed to fix.

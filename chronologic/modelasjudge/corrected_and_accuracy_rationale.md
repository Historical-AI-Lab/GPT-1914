# ChronoLogic Accuracy Estimation: Rationale and Method

This document records the design of `montecarlo_accuracy.py`: what it does, why, and what
earlier approaches failed at. It is self-contained for a reader who did not participate in
the design conversations.

---

## The goal

ChronoLogic's benchmark score has two layers.

**Per-aspect pass rates** — what fraction of questions did a candidate model pass on
question fit, context fit, and style, respectively. These are simple observed proportions;
the main challenge is honest uncertainty quantification given that each judge (an LLM for
question/context fit, a fine-tuned DeBERTa discriminator for style) has known per-question
reliability.

**Binary AND-accuracy** — the fraction of questions on which the model *simultaneously*
passed all applicable aspects. This is the headline benchmark number. It is harder to
estimate because the hard conjunction of three noisy verdicts is itself a noisy estimator
of the latent true AND-fraction.

The key design principle is:

> **Judge reliability is used primarily to model uncertainty in the observed verdicts, not
> to redefine the benchmark score.**

For per-aspect scores the raw observed pass rate is retained as the point estimate — it is
the right quantity. Reliability enters to widen the confidence interval. For binary
AND-accuracy, reliability additionally matters because the conjunction of noisy verdicts
creates a structural measurement problem that shifts the point estimate.

---

## What failed: `bootstrap_confidence.py`

The first attempt drew a per-question Bernoulli verdict from the Bayesian posterior and
ANDed three draws. For a binary-symmetric channel with reliability `r`:

```
P(z=1 | obs=1, r) = r             # flat prior
P(z=1 | obs=0, r) = 1 − r
```

The posterior-average binary accuracy is `mean_q( r_q · r_c · r_s )` when all three aspects
pass — which for reliabilities near 0.9 gives roughly 0.73, far below raw AND (≈0.45). This
is not attenuation correction; it is **shrinkage toward 0.5** applied to every verdict
independently, which deflates the AND estimate severely.

---

## What failed: `bayes_correction.py` — product approach

A hierarchical IRT model estimated latent per-question probabilities `p_q, p_c, p_s` and
computed `mean_q( p_q · p_c · p_s )`. This has the right form as an estimand but
**deflates** because a product of sub-1 probabilities is always less than any individual
factor — a confidently-passing question with `p ≈ 0.95` on all three aspects contributes
0.857, not 1.0. Cross-aspect correlation was also ignored. Observed result: raw 0.454 →
corrected 0.378 (−0.075), a large nonsensical downward correction.

---

## What failed: `bayes_correction.py` — threshold-AND approach

To fix product deflation, latent probabilities were thresholded at 0.5 before ANDing.
This produced the opposite problem: raw 0.454 → corrected 0.531 (+0.077). The cause:
**hierarchical prior shrinkage on style**. The DeBERTa likelihood is logit-Normal with
variance `σ² = 1/(2r_s − 1)²`. At `r_s ≈ 0.75`, `σ ≈ 2` — a very diffuse likelihood —
so each question's latent style score is dominated by the shared `N(0,1)` population prior.
A question with observed style score 0.40 (a raw failure) gets posterior pulled back to
≈0.53, crossing the threshold and becoming a "corrected pass." Prior shrinkage was
**promoting raw failures**, the opposite of the intended correction.

Root cause: a hierarchical model that borrows strength across questions is wrong when the
goal is to count per-question AND-passes. Each question's individual true score matters,
not its position relative to a population mean.

---

## The current approach: per-verdict reliability model

### Conceptual frame

The current method does not try to estimate a latent population pass rate by inverting an
attenuation channel (that is the classical MOM / disattenuation approach). Instead it
treats each observed verdict as a **fallible piece of evidence about one individual
question**:

- An observed pass means the judge said "pass." If the judge is reliable with probability
  `r`, this pass is a true pass with probability `r` and a false positive with probability
  `1 − r`. So the per-question posterior probability of a true pass is `r`.
- An observed fail means the judge said "fail." By symmetry, the posterior probability of
  a true pass is `1 − r`.
- A split (tied orderings cancel out, no informative verdict) gives posterior 0.5.

This is not attenuation correction; it is **epistemic discounting**: we do not take observed
verdicts as certainties; we weight them by the reliability of the instrument.

### Question fit and context fit

For each question, `_collapse_verdicts()` reduces the raw scored list to a single collapsed
verdict in {0, 0, 0.5, 1}:

- Within each `gt_index` block, average the scores.
- If the block average is exactly 0.5 (paired orderings split), drop it — no information.
- Otherwise binarise (> 0.5 → 1, < 0.5 → 0) and take the mean of surviving block verdicts.
- If no blocks survive, return 0.5.

The per-question pass probability is then:

```
π_q = r_q     if obs_q > 0.5   (observed pass → posterior = reliability)
π_q = 1 − r_q if obs_q < 0.5   (observed fail → posterior = 1 − reliability)
π_q = 0.5     if obs_q = 0.5   (uninformative tie)
```

where `r_q` is the per-question judge reliability stored in the scored file (default 0.75).
Context fit is handled identically; context-NA questions auto-pass (`π_c = 1.0`).

### Style

The DeBERTa discriminator produces a continuous score per question. The score is thresholded
at 0.5 to produce a binary verdict, and the per-verdict reliability model is then applied:

```
mean_score = mean(continuous_scores)
π_s = r_s     if mean_score > 0.5
π_s = 1 − r_s if mean_score < 0.5
π_s = 0.5     if mean_score = 0.5
```

Style-NA questions (discriminator reliability below threshold) auto-pass (`π_s = 1.0`).

### Point estimates

Per-aspect point estimates are the mean per-question posteriors over the relevant question
subset:

```
question_fit  = mean_q( π_q )
context_fit   = mean over context-scored questions ( π_c )
style         = mean over non-style-NA questions ( π_s )
```

Binary AND-accuracy:

```
binary_accuracy = mean_q( π_q × π_c × π_s )
```

with `π_c = 1.0` for context-NA questions and `π_s = 1.0` for style-NA questions.

### Confidence interval: two-level Bernoulli bootstrap

For each of `n_iterations` bootstrap draws:

1. **Resample questions** with replacement (question-sampling variability).
2. For each resampled question, **draw Bernoulli** pass/fail from π per aspect, then AND:
   ```
   z_q ~ Bernoulli(π_q),   z_c ~ Bernoulli(π_c),   z_s ~ Bernoulli(π_s)
   pass = z_q AND z_c AND z_s
   ```
3. Record `mean(pass)` for the iteration.

The Bernoulli draw samples from our epistemic uncertainty about which side of the 0.5
threshold each question's true score falls on. Questions near the threshold (π ≈ 0.5)
contribute most of the CI width; confident passes/fails contribute negligible variance.

Per-aspect CIs use question resampling only (continuous means, no Bernoulli).

---

## The floor-ceiling problem and range-normalized reporting

### Why the per-verdict model creates a floor and a ceiling

Under per-verdict reliability, the achievable range of the adjusted per-aspect score is not
[0, 1]. An observed fail maps to `1 − r`, not 0. An observed pass maps to `r`, not 1. So:

```
max possible adjusted score for one aspect = mean(r)     [all questions pass]
min possible adjusted score for one aspect = mean(1 − r) [all questions fail]
```

This means a model that saturates the benchmark on some aspect — every question passes —
cannot achieve an adjusted per-aspect score above `mean(r) < 1`. A critic could read an
adjusted style score of 0.75 as "the model only got 75% on style" when the truth is "the
model passed every style question, but the DeBERTa classifier is only 75% reliable, so we
cannot confirm 100% with certainty."

For binary AND-accuracy, the floor and ceiling compound across aspects:

```
ceiling_q = r_q  × (r_c  if context-scored else 1.0) × (r_s  if style-scored else 1.0)
floor_q   = (1-r_q) × ((1-r_c) if context-scored else 1.0) × ((1-r_s) if style-scored else 1.0)

ceiling_AND = mean_q( ceiling_q )
floor_AND   = mean_q( floor_q   )
```

### Range normalization

To make the distinction between "model performance" and "measurement limits" explicit, the
script reports a range-normalized score alongside the adjusted score:

```
norm(x) = clip( (x − floor) / (ceiling − floor),  0, 1 )
```

This answers: *how close did the model come to the best score this measurement instrument
could resolve?* CI endpoints are linearly transformed by the same map (monotonic, so
endpoint order is preserved). The denominator — floor and ceiling — is reported explicitly.

Note: for a single binary aspect with constant `r`, range normalization recovers the raw
observed pass rate. Aggregated across many questions with varying reliabilities, it stays
close to raw. This is intentional and confirms the design principle.

### Empirical sanity check

For the fine-tuned GPT-4.1 model on benchmark v0.4 (ft:gpt-4.1-2025-04-14:…DNkT25IC):

```
metric          raw     adjusted   range         % of range   95% CI
question_fit    .567      .564    (0.04, 0.96)     .570      [.533, .607]
context_fit     .545      .536    (0.10, 0.90)     .545      [.446, .646]
style           .767      .681    (0.15, 0.85)     .761      [.720, .801]
binary_accuracy .454      .417    (0.01, 0.86)     .480      [.437, .523]
```

The three per-aspect range-normalized scores (.570, .545, .761) are nearly identical to
their raw values (.567, .545, .767). The correction mostly lives in the interval width, not
the point estimate. This is the expected result: for individual aspects, the raw observed
pass rate is the natural estimator; reliability enters to model CI width, not to shift the
center.

For binary AND-accuracy the picture is different. The raw observed score (.454) is the
threshold-AND count. The adjusted score (.417) is lower because every observed triple-pass
is now treated as a fallible conjunction of three uncertain verdicts. The range-normalized
score (.480) is slightly *above* raw: on the reliability-limited latent scale, the model
sits slightly closer to the ceiling than the raw count suggests, because some observed
AND-failures are plausibly false negatives. The CI [.437, .523] appropriately reflects both
question-sampling uncertainty and per-question verdict uncertainty propagated through the
AND gate.

---

## Reporting conventions

The script produces two stdout tables and writes all quantities to a JSON file.

**Table 1 — Per-aspect and binary accuracy (raw and adjusted):**

```
metric                    raw  corrected  95% CI
binary_accuracy         0.454      0.417  [0.381, 0.454]
question_fit            0.567      0.564  [0.530, 0.598]
context_fit             0.545      0.536  [0.457, 0.617]
style                   0.767      0.681  [0.652, 0.709]
```

**Table 2 — Range-normalized (% of possible score given judge reliability):**

```
metric                    min      max  corrected  % of range  95% CI
binary_accuracy         0.011    0.858      0.417       0.480  [0.437, 0.523]
question_fit            0.040    0.960      0.564       0.570  [0.533, 0.607]
context_fit             0.100    0.900      0.536       0.545  [0.446, 0.646]
style                   0.153    0.847      0.681       0.761  [0.720, 0.801]
```

**How to read the results:**

For per-aspect scores (question_fit, context_fit, style), the **raw observed pass rate will be nearly identical to the range-normalized value.** The slight changes that occur in the range-normalized value are the result, in effect, of weighting questions for the judges' variable per-question reliability. This is probably desirable, but we might decide to report raw observed pass rate for simplicity. The CI (range-normalized) reflects judge reliability as well as resampling to reflect a larger hypothetical question population.

For binary AND-accuracy, **the range-normalized score** is definitely the recommended headline number.
It places the model's performance on the scale the measurement instrument can actually
resolve, and also reflects a correction for multiplicative bias. The raw observed AND-count and the posterior expected AND-count are both reported for completeness and interpretability, but neither is the main number.

**Precedent:**

The per-aspect rescaling is, identically, the Rogan–Gladen estimator (1978, American Journal of Epidemiology, "Estimating prevalence from the results of a screening test"). See also
https://arxiv.org/abs/2601.05420
https://arxiv.org/html/2511.21140v3

---

## JSON output structure

The output JSON (`scored_answers/mcacc_{ctag}__{version}.json`) contains three top-level
result blocks:

```json
"raw":              { "binary_accuracy": ..., "question_fit": ..., ... },
"corrected":        { "binary_accuracy": { "point": ..., "ci_lower": ..., "ci_upper": ...,
                                           "bootstrap_mean": ... }, ... },
"range_normalized": { "binary_accuracy": { "min": ..., "max": ..., "norm_point": ...,
                                           "norm_ci_lower": ..., "norm_ci_upper": ... }, ... }
```

`raw` — simple observed values (threshold-AND for binary_accuracy; mean verdicts for aspects).

`corrected` — per-verdict reliability model applied; two-level Bernoulli bootstrap CI.

`range_normalized` — corrected values linearly rescaled into [0, 1] relative to the
floor/ceiling achievable under the per-question reliabilities. CI endpoints are rescaled by
the same linear map.

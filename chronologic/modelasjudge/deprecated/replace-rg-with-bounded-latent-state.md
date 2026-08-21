# Specification: Bounded Latent-State Estimator for the Binary Substantive Channel

[This was never implemented and is now deprecated. It was more complex than necessary and had weird consequences because the global pi prior could outweigh individual verdicts.]

## 0. Purpose

Replace the Rogan–Gladen pass/fail estimator with a bounded latent-state model.

The replacement must preserve the useful parts of the existing architecture:

* separate false-pass and false-fail behavior of the judge;
* question-specific calibration where available;
* shared uncertainty in calibration models;
* separate judgment, instrument, and item-sampling uncertainty;
* automatic verdicts as certainties;
* exact decomposition of aggregate scores into question subsets.

It must remove the principal pathology of Rogan–Gladen in the present benchmark: individual questions must never contribute negative or greater-than-one "pseudo-accuracy." Consequently, a subset with positive accuracy cannot be contained in a superset reported at zero because other questions supplied negative mass.

The estimator is a latent-state measurement model, not an algebraic inversion.

---

## 1. Change the common substantive quantity from `p_q` to `s_q`

The pipeline should use the following general quantity:

> **`s_q` — the model's expected substantive credit on question q, on a bounded 0–1 scale where larger values mean closer to full substantive adequacy.**

Every reported substantive score is an arithmetic mean of `s_q` over the relevant questions.

This slightly revises the previous claim that every channel estimates "the probability that the answer is as good as ground truth." That wording is literally correct for the new binary model, but too strong for the anchored Bradley–Terry channel, whose mapping is partly a declared reporting convention.

For the two channels:

* **binary:** `s_q = P(z_q = 1 | judge evidence, calibration)`, a literal posterior probability;
* **partial credit:** `s_q = g(Δ_q)`, or its posterior expectation over Δ and calibration draws, where `g` is the anchored monotone calibration map.

Thus both are **bounded expected-credit scores**, but only the binary score requires a binary latent state.

Automatic verdicts remain exact:

* verbatim ground-truth match: `s_q = 1`;
* applicable probability-0 distractor match: `s_q = 0`.

---

## 2. Latent state for the binary channel

For every genuinely judged binary question q, define

[
z_q \in {0,1}
]

where

[
z_q = 1
]

means that the candidate answer is substantively acceptable — i.e. as good as the ground truth for the criteria measured by this channel.

The benchmark does not observe `z_q`. It observes judge verdicts.

Let

* `k_q` = number of pass verdicts received by the candidate;
* `n_q` = number of judge trials;
* `α_q = P(pass | z_q = 0)`, the judge's false-pass probability;
* `β_q = P(fail | z_q = 1)`, the judge's false-fail probability.

Then

[
k_q \mid z_q=1 \sim \operatorname{Binomial}(n_q,1-\beta_q)
]

and

[
k_q \mid z_q=0 \sim \operatorname{Binomial}(n_q,\alpha_q).
]

This is the same substantive measurement model that motivated Rogan–Gladen, but rather than algebraically solving for an unconstrained mixture weight, it performs inference about the bounded latent state.

---

## 3. Model-level prevalence parameter

Introduce one model-level parameter for the binary channel:

[
\pi=P(z_q=1).
]

`π` represents the model's underlying prevalence of acceptable answers across the binary questions in this benchmark.

This is **not a judge parameter**. It belongs to the candidate model being evaluated.

The same `π` must be used for all binary questions of that candidate. In particular:

> **Never re-estimate π separately for reasoning types, genres, frame types, or other reported slices.**

Slices are summaries of already-estimated question scores, not new estimation problems.

This requirement is what guarantees coherent nesting and decomposition.

---

## 4. Per-question likelihood

For each genuinely judged question calculate

[
L_{1q}
======

# P(k_q\mid z_q=1)

\operatorname{BinomPMF}(k_q;n_q,1-\beta_q)
]

and

[
L_{0q}
======

# P(k_q\mid z_q=0)

\operatorname{BinomPMF}(k_q;n_q,\alpha_q).
]

These calculations should be performed in log space for numerical stability.

For a given `π`, the marginal likelihood of the observed verdicts is

[
P(k_q\mid \pi)
==============

\pi L_{1q}+(1-\pi)L_{0q}.
]

The likelihood for the binary benchmark is the product over questions.

Automatic verdicts are observations of `z_q` itself rather than judge evidence. An auto-pass therefore contributes a known `z_q=1`; an auto-fail contributes a known `z_q=0`.

---

## 5. Estimate π by empirical Bayes

Estimate `π` from the complete binary channel for the candidate being scored.

With fixed `α_q` and `β_q`, maximize

[
\ell(\pi)
=========

\sum_q
\log\left[
\pi L_{1q}+(1-\pi)L_{0q}
\right]
]

plus the contributions of automatic verdicts.

Equivalently, use the EM fixed point.

Given a current `π`, calculate

[
r_q
===

# P(z_q=1\mid k_q)

\frac{\pi L_{1q}}
{\pi L_{1q}+(1-\pi)L_{0q}}.
]

Then update

[
\pi
\leftarrow
\frac{
N_{\text{auto-pass}}+\sum_q r_q
}{
N_{\text{binary}}
}.
]

Iterate until convergence.

For an interior maximum, this gives the useful self-consistency identity

[
\hat\pi
=======

\frac{
N_{\text{auto-pass}}+\sum_q r_q
}{
N_{\text{binary}}
}.
]

Thus the binary-channel score is simultaneously the estimated prevalence of acceptable answers and the mean expected credit of its questions.

### Boundary behavior

The implementation must explicitly detect an optimum at `π=0` or `π=1`.

Do not silently impose an arbitrary epsilon merely to avoid a boundary estimate.

If boundary estimates occur materially in production, add a predeclared weak regularization or a one-dimensional Bayesian sensitivity analysis rather than an undocumented numerical floor.

---

## 6. The per-question substantive score

After estimating `π`, define

[
s_q=r_q
=======

\frac{\hat\pi L_{1q}}
{\hat\pi L_{1q}+(1-\hat\pi)L_{0q}}.
]

For automatic verdicts,

[
s_q=1
]

or

[
s_q=0.
]

Every binary `s_q` therefore lies in `[0,1]`.

There is no clipping step.

The binary-channel point estimate is

[
S_{\text{binary}}
=================

\frac{1}{N}
\sum_q s_q.
]

Any reasoning-type or other subgroup is scored by exactly the same rule:

[
S_G
===

\frac{1}{|G|}
\sum_{q\in G}s_q.
]

No parameter is refitted for the subgroup.

---

## 7. Required aggregation invariant

Because every question has one fixed bounded `s_q`, any partition of the benchmark must obey ordinary arithmetic decomposition.

For disjoint groups (G_1,\ldots,G_m),

[
S
=

\frac{\sum_j |G_j|S_{G_j}}
{\sum_j |G_j|}.
]

This must hold to floating-point precision.

Among other things, this guarantees that if a subset A of a superset U scores 0.136, then

[
S_U
\ge
\frac{|A|}{|U|},0.136.
]

There can be no negative contribution from the complement.

This is a required unit test, not merely a desirable property.

---

## 8. Relationship to α and β

The interpretation of `α` and `β` does not change.

They remain properties of the measurement instrument:

[
\alpha_q=P(pass\mid bad)
]

and

[
\beta_q=P(fail\mid good).
]

The difference is entirely downstream.

Rogan–Gladen asks:

> What unconstrained prevalence would algebraically reproduce the observed pass rate?

The latent-state estimator asks:

> Given this judge's sensitivity and specificity, how much evidence do these verdicts provide that this particular answer is genuinely acceptable?

The latter produces a posterior probability rather than a signed correction term.

### Useful limiting cases

The implementation should satisfy these checks.

**Perfect judge**

If

[
\alpha_q=\beta_q=0,
]

then any observed pass implies `s_q=1` and any observed fail implies `s_q=0`.

**Uninformative judge**

If

[
1-\beta_q=\alpha_q,
]

then

[
L_{1q}=L_{0q}
]

for every possible verdict, and therefore

[
s_q=\pi.
]

The verdict supplies no evidence. The estimator does not explode.

**Increasing evidence**

Provided

[
1-\beta_q>\alpha_q,
]

`s_q` must increase monotonically as the number of observed passes `k_q` increases.

**Many repeated judgments**

As `n_q` grows, strongly consistent verdicts should drive `s_q` toward 0 or 1 whenever the judge is informative.

---

## 9. Treatment of low-informativeness questions

The Rogan–Gladen informativeness floor existed primarily because

[
1-\alpha-\beta
]

appeared in a denominator and could make the estimator numerically explosive.

That problem disappears.

A nearly uninformative judge naturally gives

[
s_q\approx\pi.
]

Therefore the existing informativeness floor should no longer be required as a mathematical stabilization device.

Recommended production policy:

* retain `1 − α_q − β_q` as a diagnostic;
* report the number of questions with very low judge informativeness;
* do not automatically exclude them solely because the latent-state estimator would be unstable — it is not;
* continue to flag or exclude cases where the judge appears genuinely anti-informative or where calibration is otherwise invalid.

A benchmark dominated by uninformative questions should produce wide uncertainty and a diagnostic warning, not artificial numerical explosions.

---

## 10. Point estimates for α and β

For the plug-in point estimate, retain the existing sources of calibration:

### α

Use the posterior mean of the question-specific false-pass probability estimated from known-bad calibration trials.

The existing Jeffreys-prior treatment may remain unless a separate sensitivity analysis changes that decision.

### β

Use the posterior-mean prediction from the existing shared β regression, including its established frame/length structure.

No change to how α or β is learned is required by this estimator.

The change is from **inverse correction** to **latent-state inference**.

---

## 11. Uncertainty propagation

The existing three-layer vocabulary should be retained, but the binary judgment layer changes meaning.

### Layer 1 — question-level measurement uncertainty

For a binary question, uncertainty about the candidate answer is represented directly by the posterior distribution

[
z_q\mid k_q,\alpha_q,\beta_q,\pi
\sim
\operatorname{Bernoulli}(s_q).
]

A Monte Carlo replicate may therefore draw

[
z_q^{(r)}\sim\operatorname{Bernoulli}(s_q^{(r)}).
]

This is the natural binary-channel analogue of drawing one `Δ_q` from the BT question's posterior.

Do **not** both resample the observed candidate verdicts and then also draw `z_q` from its posterior unless a separate repeated-measurement estimand is explicitly desired. The observed `k_q` is the evidence being conditioned on; posterior uncertainty about `z_q` is the uncertainty remaining after seeing it.

Question-specific uncertainty in measured `α_q`, and any independent per-question β residual already present in the model, may continue to be drawn at this layer because those uncertainties are local to a question rather than shared globally.

Automatic verdicts have zero Layer-1 uncertainty.

### Layer 2 — shared instrument uncertainty

Draw the shared parameters governing the measurement instrument once per replicate and apply that draw to all relevant questions.

Binary channel:

* one shared β-regression coefficient draw per replicate;
* any other calibration parameters learned globally.

Partial-credit channel:

* one shared calibration-slope draw per replicate;
* the anchored intercept remains fixed and therefore contributes no uncertainty.

This uncertainty does not average away merely because more benchmark questions are added.

### Layer 3 — item-sampling uncertainty

Resample benchmark questions with replacement according to the existing benchmark sampling design.

Whenever item resampling changes the binary collection used for a replicate, `π` should be re-estimated from that replicate's complete resampled binary channel before binary `s_q` values are calculated.

Do not estimate a separate `π` within a reported reasoning group. If group scores are required for the replicate, calculate them from questions scored using the replicate-wide binary `π`.

---

## 12. One full uncertainty replicate

For each replicate:

1. Draw the shared β-regression coefficients if instrument uncertainty is enabled.
2. Draw question-specific α values from their calibration posteriors.
3. Draw any established question-specific β residuals.
4. Draw the partial-credit calibration slope if that channel is included; keep its anchored intercept fixed.
5. Perform item resampling if enabled, preserving the benchmark's declared channel stratification.
6. Using the complete resampled binary channel, estimate that replicate's `π`.
7. For every sampled binary question:

   * calculate `L1_q` and `L0_q`;
   * calculate bounded posterior `s_q`;
   * if judgment uncertainty is enabled, draw `z_q ~ Bernoulli(s_q)`; otherwise use `s_q`.
8. For every sampled BT question, use the existing posterior Δ draw and anchored calibration machinery.
9. Calculate channel, pooled, and group means.
10. Record them without clipping.

All reported replicate scores must already lie in `[0,1]` because all their constituent question scores do.

---

## 13. Automatic verdicts

Automatic verdicts continue to bypass the judge entirely.

They enter both point estimates and uncertainty replicates as fixed substantive credit:

* auto-pass = 1;
* auto-fail = 0.

They should also participate in estimation of the model-level binary prevalence `π`, since they are direct observations of the latent state.

They have:

* zero judgment variance;
* zero instrument variance;
* ordinary item-sampling variance.

---

## 14. Transport assumptions remain

This estimator fixes a mathematical and interpretive problem; it does not solve calibration transport.

The same substantive warning remains:

* `α_q` is learned from benchmark distractors but applied to model-generated bad answers;
* `β_q` is learned from known-good comparison material but applied to model-generated good answers.

If judge behavior differs between calibration answers and deployed model answers, the posterior `s_q` values will be biased.

This is exactly parallel to the BT channel's calibration-transport problem: the anchored curve is fitted from benchmark answer material and then applied to generated candidates.

Retain the existing sensitivity analyses for such distribution shift.

---

## 15. Relationship to the partial-credit channel

The previous specification said:

> α/β and (a,b) are the same kind of object.

Replace that with the more precise statement:

> **Both channels treat the judge as a fallible measurement instrument whose output must be calibrated before it is interpreted as substantive credit. They share an uncertainty architecture, but they use different measurement models.**

### Binary channel

The binary channel is **generative**.

It explicitly models

[
P(\text{judge evidence}\mid\text{latent substantive state})
]

through `α` and `β`, then applies Bayes' rule to infer

[
E[z_q\mid\text{evidence}].
]

Its output has a literal probability interpretation.

### Partial-credit channel

The BT channel is **comparative and calibrated**.

Pairwise judgments first produce a posterior over relative quality `Δ_q`. A monotone calibration map then converts `Δ_q` to bounded substantive credit.

Its slope represents how strongly differences on the judge-derived latent axis should translate into differences on the reporting scale.

Its intercept is not currently an estimated prevalence parameter: it is deliberately anchored so that `Δ=0`, ground-truth parity, maps to 0.90.

Therefore `(α,β)` and `(a,b)` should not be described as mathematically equivalent parameter pairs.

What is shared is the larger structure:

|                               | Binary                                               | Partial credit                       |                            |
| ----------------------------- | ---------------------------------------------------- | ------------------------------------ | -------------------------- |
| latent substantive object     | `z_q ∈ {0,1}`                                        | comparative quality `Δ_q`            |                            |
| raw evidence                  | pass/fail judge trials                               | pairwise comparisons                 |                            |
| instrument calibration        | `α_q`, `β_q`                                         | calibration slope and anchored scale |                            |
| item-level uncertainty        | posterior uncertainty in `z_q`                       | posterior uncertainty in `Δ_q`       |                            |
| shared instrument uncertainty | β regression and other shared calibration parameters | calibration slope                    |                            |
| bounded output                | `E[z_q                                               | evidence]`                           | anchored calibrated credit |
| downstream operation          | arithmetic mean                                      | arithmetic mean                      |                            |

This is the common language to use in the paper.

---

## 16. The role of π versus the BT intercept

There is a useful analogy here, but it must be stated carefully.

The binary `π` and the BT intercept both determine how raw judge evidence is located on a bounded reporting scale.

But they have different epistemic status.

### Binary π

`π` is an empirical property of the candidate model on the binary benchmark.

It answers:

> Before considering this question's noisy verdicts, how frequently does this candidate appear to produce acceptable answers across the binary benchmark?

It is estimated anew for each candidate.

### BT intercept

The BT intercept is a declared reporting anchor.

It answers:

> What score do we choose to assign to an answer located exactly at ground-truth parity on the BT quality axis?

It is held fixed across candidates.

Thus the binary channel uses **empirical-Bayes shrinkage toward the candidate's estimated prevalence**, while the BT channel uses **anchoring to a fixed semantic reference point**.

These are not the same operation. But both prevent the reporting scale from being determined accidentally by nuisance features of the calibration sample.

That is the deeper philosophical parallel.

The free BT intercept was contaminated by the ratio of ground truths to distractors in the calibration set. Pinning it removed a nuisance prevalence term from the reporting scale.

Rogan–Gladen had the opposite problem on the binary side: it eliminated the latent prevalence entirely and treated inversion residuals as if they were question-level scores. Reintroducing `π` as an explicit latent prevalence allows Bayes' rule to distinguish a calibration property of the judge from an empirical property of the candidate.

In both cases the repair consists of identifying which quantity belongs to the **instrument**, which belongs to the **candidate**, and which belongs merely to the **reporting convention**.

---

## 17. Recommended paper language

A concise description suitable for the methods section is:

> We treated both substantive judges as noisy measurement instruments and converted their outputs to bounded expected-credit scores before aggregation. For binary questions, we used a latent-state measurement model: question-specific false-pass and false-fail rates define the likelihood of the observed judge verdicts under acceptable and unacceptable answers, and an empirical-Bayes estimate of the candidate's overall prevalence of acceptable answers supplies the prior. The resulting question score is the posterior probability that the answer is acceptable. For partial-credit questions, pairwise comparisons yield a posterior over relative answer quality, which is mapped to the same 0–1 reporting scale by an anchored calibration function. The two channels therefore share a calibration-and-uncertainty architecture without assuming identical statistical models.

For uncertainty:

> In both channels we distinguished question-level measurement uncertainty from uncertainty in calibration parameters shared across questions, and from uncertainty due to the benchmark's finite sample of items. Question-level uncertainty averages down with additional questions; shared instrument uncertainty does not.

---

## 18. Verification requirements

Before replacing the production estimator, verify all of the following.

### Mathematical tests

* Every binary question score lies in `[0,1]`.
* No aggregate clipping is required.
* Any partition of the binary questions reconstructs the binary total exactly by count weighting.
* Any partition spanning both channels reconstructs the count-weighted pooled total exactly.
* A positive subset cannot be contained in a zero-scoring superset unless the subset itself is zero.
* With a perfect judge, scores reduce to the observed binary outcomes.
* With an uninformative judge, a verdict leaves the question at the model-level prior.
* More pass evidence monotonically increases the posterior whenever the judge is informative.
* Automatic passes and fails remain exactly 1 and 0 under every uncertainty replicate.

### Empirical comparisons

For several weak, medium, and strong models, report side by side:

* raw judge pass rate;
* old Rogan–Gladen score;
* new latent-state binary score;
* distribution of per-question `s_q`;
* reasoning-group scores;
* pooled substantive score.

Pay particular attention to models for which Rogan–Gladen currently clips to zero.

### Uncertainty checks

Report interval widths under:

* judgment only;
* judgment + instrument;
* judgment + item;
* all three layers.

The instrument layer should remain visible rather than being allowed to average away.

### Calibration checks

Among held-out known-good and known-bad answers, verify that posterior scores are correspondingly high and low and inspect calibration by score bin.

Repeat existing α-inflation and α-prior sensitivity checks.

---

## 19. One BT consistency check prompted by this framework

If the common downstream quantity is described as **expected calibrated credit**, the BT point estimator should use the expectation of the calibrated draw,

[
E[\sigma(a+b\Delta_q)],
]

rather than

[
\sigma(a+bE[\Delta_q]),
]

because the sigmoid is nonlinear.

This is independent of the binary rewrite, but the new shared language makes the distinction conceptually important and it should be checked against the production implementation.

---

## 20. Summary of the change

Old binary pipeline:

[
\text{verdict rate}
\rightarrow
\frac{v-\alpha}{1-\alpha-\beta}
\rightarrow
\text{possibly negative pseudo-score}
\rightarrow
\text{aggregate}
\rightarrow
\text{clip}.
]

New binary pipeline:

[
\text{judge evidence}
+
(\alpha,\beta)
+
\text{model prevalence }\pi
\rightarrow
P(z_q=1\mid\text{evidence})
\rightarrow
s_q\in[0,1]
\rightarrow
\text{arithmetic mean}.
]

The new estimator gives up Rogan–Gladen's finite-sample unbiasedness in exchange for properties that matter more for this benchmark: bounded interpretation, coherent subgroup decomposition, explicit treatment of latent uncertainty, and a common expected-credit language with the partial-credit channel.

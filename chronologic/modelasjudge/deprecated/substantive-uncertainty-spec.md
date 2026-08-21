# Uncertainty in the Substantive Score

> **Superseded.** The binary (pass/fail) channel this spec describes no longer runs
> through Rogan-Gladen: `direct-binary-scoring-spec.md` retires the correction, and the
> binary score is the arithmetic mean of the observed judge verdicts. alpha and beta are
> judge-validation quantities now (`substantive/judge_validation.py`,
> `judge_validation_report.py`), never applied to a candidate score. The BT
> (partial-credit) channel this spec describes is unchanged. Kept as a record of the
> reasoning at the time. See `direct-binary-scoring-spec.md` and
> `estimator_and_calibration_explained.md`.

*A philosophical spec for the fully automated ChronoLogic scoring pipeline.*

Approved 2026-08-17. This document deliberately contains **no code design** — that is the second-stage plan. What it fixes is the *vocabulary and the reasoning*: one quantity, three named layers of uncertainty, one mechanism. It is the companion to `new-spec-integrating-bt.md`, which states the goal; this one settles how uncertainty is talked about.

---

## Context

`modelasjudge/new-spec-integrating-bt.md` asks for a fully automated workflow that fuses three subsystems built separately over the last month:

- the **binary pass/fail judge** (`judge_scoring_nocontext.py`, with per-question reliability in `llm_reliability/` and `beta_reliability/`),
- the **Bradley-Terry partial-credit judge** (`bt/`, driven by `bt_context_scoring.py`),
- the **new style judge** (`stylejudge/typicality.py`).

Routing is already decided: ChronoLogic 0.7 carries a `partial_credit` field, and **310 of its 864 questions have `partial_credit == 1`** (they go to Bradley-Terry; the other 554 go to the binary judge). The style judge already reports its own uncertainty and stays separate from substantive scoring.

The two channels are not two constructs. The binary judge scores instruction following and factual accuracy; the Bradley-Terry judge scores a **superset** — those criteria plus fit to the historical context — on a continuous scale. Which channel a question uses is an editorial property of the question, not a claim about which criteria apply to it. (The stored keys `question_fit` / `context_fit` predate this framing and are kept only because artifacts on disk carry them.)

### Amendment, 2026-08-19: the anchored p_fit scale

`bt/calibrate.py` fits `p_fit = σ(a + b·Δ)` where `Δ = θ_candidate − mean(θ_ground_truths)`, so **Δ = 0 means "exactly as good as the ground truths" by construction**. The intercept is therefore the score a perfect answer receives, and left free it is not identified by anything about answer quality: it absorbs `log(good:bad odds)` of the calibration set, which is a benchmark design choice. Between ChronoLogic 0.1 and 0.7 the held-out-GT Δ distributions were nearly identical, yet `a` moved −1.341, of which −1.040 is exactly the label-mix log-odds shift (60:148 → 38:336). Ground-truth parity scored 0.669 on one version and 0.345 on the other for no reason connected to the judge.

Two changes fix that, and both are now the production default:

- **The intercept is pinned** at `logit(0.90)`, so ground-truth parity scores 0.90 exactly, as a declared convention with **zero estimation error**. `cal_a` is consequently a constant column in the calibration draw bank; the instrument layer of §3's decomposition carries only the slope's uncertainty on this channel. That narrowing is intended, not an artifact.
- **Ground truths and non-ground-truths are weighted to equal total influence**, so a question's distractor count cannot move the curve.

Neither changes any ranking — both are monotone re-scalings of the same Δ, and AUC is unaffected. `pin_p` and `class_balance` are stamped into the calibration artifact, the calibration draw bank, and the Δ draw bank, and appear in `drawbank.COMPATIBILITY_KEYS`, so scores produced under different designs fail loudly rather than pooling. `--no-pin --no-class-balance` reproduces the previous fit. Full derivation and the empirical decomposition: `estimator_and_calibration_explained.md` §6–7.

### Amendment, 2026-08-19: automatic verdicts bypass both corrections

A candidate answer verbatim identical (lowercased, punctuation-stripped) to one of the question's own answer options does not need a judge, and neither channel calls one. Ground-truth matches score 1.0; probability-0 distractor matches score 0.0 — on the binary channel only for penalty classes `question` and `both`, since that channel does not measure period fidelity, and on the partial-credit channel for every probability-0 match. Rules: `substantive/verdicts.py`.

These are **certainties, not noisy readings**, so they enter the estimator as overrides rather than as observations, carried by `Bank.auto_pf` / `Bank.auto_pc` (NaN where a question was genuinely judged):

- On the binary channel the override replaces the Rogan–Gladen result. This also repairs a real defect: §2's inversion applied to a `v_hat` of 1.0 returns `(1−α)/(1−α−β) > 1`, an out-of-range per-question contribution the pipeline previously emitted for every ground-truth match.
- On the partial-credit channel it replaces `σ(a + b·Δ)`, and the question's Δ draws are written as NaN rather than zero — Δ = 0 would mean "exactly ground-truth level", which is false for an auto-fail and would be read silently by any consumer that ignored the override.
- Both are **exempt from the §8.2 informativeness floor**, which measures the judge.
- The override is applied to the per-question replicate arrays before item resampling, so §6's slice and group breakdowns agree with the headline they decompose. Judgment-layer variance for an overridden question is consequently zero, which is correct; item-layer variance is retained.

Artifacts written before this existed carry neither array, load as all-NaN, and reproduce their previous numbers exactly. `n_auto_passfail` and `n_auto_partial` are reported in the ledger so a headline that is substantially verbatim recall is visible as such.

What is missing is a coherent account of uncertainty on the substantive side. And the gap is larger than it looks, because of one thing I found while exploring.

### The finding that forces the issue

The current final stage (`montecarlo_accuracy.py`) discounts each verdict by judge reliability (`π_q = r_q` if pass, `1 − r_q` if fail) and then rescales by the per-question floor and ceiling. For a **single** aspect that round trip is algebraically self-cancelling, and the existing outputs confirm it numerically — comparing `raw.question_fit` to `range_normalized.question_fit.norm_point` (`question_fit` here being the stored key for the pass/fail channel, not a distinct construct) in `modelasjudge/scored_answers/mcacc_*__0.4.json`:

| model | raw judge pass rate | after discount + range-normalize |
|---|---|---|
| Qwen2.5-72B-Instruct | 0.4108 | 0.4078 |
| Qwen2.5-7B-Instruct-ft | 0.1046 | 0.0999 |
| deepseek-r1-distill-llama-70b | 0.6482 | 0.6425 |
| ft:gpt-4.1 | 0.5892 | 0.5867 |

The correction returns the raw number to within 0.006. It only ever did real work because three aspects were multiplied together and the product needed un-compressing — deepseek's `binary_accuracy` does move, 0.2851 → 0.3829.

The new design abandons the multiplicative three-aspect model. So the existing correction machinery would silently become a no-op. **We cannot carry it forward; we need a real estimator.** That is what this document specifies.

---

## 1. One quantity: `p_q`

> **`p_q` — the probability that the model's answer to question *q* is substantively as good as the ground-truth answer.**

Every question in the benchmark gets a `p_q`, whichever channel judged it. Every score we report is an average of `p_q` values. Every interval we report describes uncertainty about such an average.

That is the whole framework. The two channels differ only in how they estimate `p_q`, and the rest of the pipeline cannot tell them apart.

Two things this deliberately excludes. `p_q` says nothing about **style** — that is measured separately and is not multiplied in. And `p_q` is a probability about *this question*, not a difficulty-weighted merit score; a hard question and an easy question both contribute one `p_q` to the mean.

---

## 2. The unifying insight: both channels are the same machine

The two channels look very different — one is a yes/no verdict, the other a Bayesian round-robin. But they have identical structure. Each takes a **raw, biased judge signal** and maps it to a probability using a **two-parameter calibration fitted on an external set of answers whose true labels we know**.

| | pass/fail channel | partial-credit channel |
|---|---|---|
| raw judge signal | win / loss / tie verdict against ground truth | Δ = θ_candidate − mean θ_ground-truth, from a round robin |
| labelled validation set | GT-vs-distractor trials (→ α) and GT-vs-GT trials (→ β) | leave-one-out held-out answers, labels 1 / fraction / 0 |
| calibration map | 2-parameter step: (v − α)/(1 − α − β) | 2-parameter logistic: σ(a + b·Δ) |
| output | `p_q` | `p_q` |

Say it in one sentence: **α/β and (a, b) are the same kind of object — the calibration of a fallible instrument against known answers.** The pass/fail channel's calibration happens to have only two possible inputs, so it collapses to a pair of error rates. The BT channel's has a continuous input, so it is a curve.

This also answers a question that otherwise looks like an embarrassing asymmetry: *why does the BT channel have no judge-error term?* Because it does not need a separate one for the noise part. Judge mistakes in pairwise comparisons pull Δ toward zero; the slope `b`, being fitted on labelled data, comes out correspondingly steeper and undoes the shrinkage. **For symmetric judge noise, the calibration curve already is an attenuation correction.** The binary channel has no continuous signal to attenuate, so its judge error has to be written down explicitly as α and β.

### 2.1 Where the analogy breaks — and why the break is also shared

The parallel is real but it is not an identity, and the difference is worth stating precisely because it determines what we are allowed to claim.

**α/β is generative; (a, b) is discriminative.** α and β parametrize P(verdict | true state) and Rogan-Gladen *inverts* them. Because they are properties of the judge, they transport to new answers as long as the judge behaves the same way. (a, b) is a recalibration of P(good | signal) fitted directly on labels. A discriminative fit absorbs *any* error structure — including asymmetric and idiosyncratic error — but only error structure that is **the same in calibration and in deployment**. It transports nothing under distribution shift.

**Two things therefore survive calibration uncorrected in the BT channel:**

1. **The measured length bias.** The BT judge prefers the longer answer 61.8% of the time. That is not attenuation — it is an additive shift in θ correlated with a covariate, and AB/BA balancing does not cancel it. Model-generated answers are systematically more verbose than the benchmark's own distractors, so the bias level baked into (a, b) is not the bias level at deployment. Expect `p_q` inflated for verbose candidates, and note that no global two-parameter curve can fix it. **Remedy to evaluate in the code plan: add answer length as a covariate to the calibration, i.e. fit σ(a + b·Δ + c·z_len).** This is a small, well-posed change and it is the single highest-value fix available on the BT side.
2. **Heterogeneous attenuation.** Judge reliability varies by question — the pass/fail channel's own β regression says so, with frame type and answer length as predictors. One global slope corrects the *average* shrinkage, leaving noisy-question scores under-corrected and clean-question scores over-corrected. Aggregate calibration can look healthy while per-slice scores are miscalibrated, and the miscalibration correlates with exactly the metadata we intend to slice on.

**And the break points the same way on both sides.** α is measured on *benchmark distractors* and applied to *model answers*, so the pass/fail channel has the identical transport failure (§8.1). The two channels are alike in their correction *and* alike in their weakness. That symmetry is not a defect of the framing — it is the reason a single vocabulary is the right one.

### Consequence: the estimator for the pass/fail channel

[This is all deprecated now -- edit Ted Underwood 8/21/26]

Because α and β are a calibration map, we apply them as one. Let `v_q` be the judge's collapsed verdict for question *q* (a fraction in [0, 1] after averaging orderings and ground-truth indices — see §8.8). Then:

```
p_q  =  (v_q − α_q) / (1 − α_q − β_q)
```

That is Rogan-Gladen, and it is one line of algebra: the observed pass rate mixes true passes the judge got right with true failures it wrongly passed, so invert the mixture. A perfect judge (α = β = 0) leaves `v_q` untouched. It replaces both the discount step and range-normalization, because unlike them it does not cancel — it moves the numbers:

```
deepseek-r1-70b     0.648  →  0.701
ft:gpt-4.1          0.589  →  0.632
Qwen2.5-7B-ft       0.105  →  0.061
```

Two honesty notes. Individual `p_q` values can fall slightly outside [0, 1]; that is legitimate and the excursions cancel in the mean, so **we clip the average, never the per-question value** (§8.3). And with α, β shared across questions this transform is monotone in the raw rate, so it **cannot reorder a leaderboard** — it changes spacing, not ranking. Per-question α_q makes small reorderings possible but they will be small. The point is calibration, not rank rescue.

### The per-question view, for display

Reviewers will want to see per-question probabilities, and values like −0.03 are not showable. There is an exact way to get them. Take the channel score π̂ = mean of `p_q`, use it as the prior, and compute each question's posterior:

```
verdict passed:  π̂(1 − β_q) / q̄            verdict failed:  π̂ β_q / (1 − q̄)
```

These are genuine probabilities in [0, 1], and **they average back to exactly π̂** when α and β are shared — an algebraic identity, not an approximation. So this is not a second, competing number; it is the same score viewed per question. (The current pipeline's discount rule is this formula with the prior pinned at 0.5, which is precisely why it shrinks everything toward the middle and then needs range-normalization to undo the shrinkage.)

---

## 3. Three layers of uncertainty

One vocabulary for all three subsystems. Every source of uncertainty in the pipeline is exactly one of these, and the layer determines *how it is resampled*.

**Layer 1 — judgment noise.** How sure are we of *this question's* score, given the judging we actually did? Independent across questions, so it **averages away** at roughly 1/√n.

**Layer 2 — instrument noise.** Uncertainty in parameters estimated once and applied to every question. Perfectly correlated across questions, so it **does not average away** — it is a floor on precision no amount of extra questions will lower. This is the layer people forget, and forgetting it is why naively-computed benchmark intervals are too narrow.

**Layer 3 — item-sampling noise.** The 864 questions are one sample from a notional population of questions we could have written. Resampling them shrinks as 1/√n.

Here is where every subsystem's existing machinery sits:

| | pass/fail channel | partial-credit channel | style judge |
|---|---|---|---|
| **judgment** | α_q ~ Beta(1 + k_q, 1 + n_q − k_q) from that question's measured trials; binomial noise in v_q; a per-question β residual (§4) | one draw from that question's stored Δ posterior (2000 draws) | *none* — the detectors are deterministic given the answer |
| **instrument** | one draw of the β-regression coefficients, applied to all questions | one draw of the calibration (a, b), applied to all questions | one resample of the reference corpus, clustered by volume |
| **item sampling** | resample the 554 binary questions | resample the 310 BT questions | resample `question_number`s |

The bottom-right column is the payoff for the "shared language" request: **the style judge's existing two-way bootstrap is already exactly layers 2 and 3 under different names.** Nothing in `stylejudge/` has to change. We just describe it in the same words, and the report reads as one argument instead of three.

---

## 4. A correction: β is instrument-level, not per-question

Fable's advice (in `new-spec-integrating-bt.md`) says α_q and β_q are both per-question parameters, drawn independently inside the question loop. That is right for α and **wrong for β**, and the difference matters.

α *is* genuinely measured per question: `judge_alpha_reliability_nocontext.py` runs 6–16 real trials per question and preserves the raw counts (`question_correct`, `question_total`), exactly so they can seed a Beta posterior.

β is not. Only ~100 GT-vs-GT pairs were ever tested, at 2 trials each. `fit_beta_regression_nocontext.py` then post-stratifies to all questions through **one shared regression**, `logit(p) = b0 + u_frame + b_len·z_loglen`. Most questions on disk carry `n_trials: null` — their β is a model prediction, not a measurement. Drawing those predictions independently per question would treat one small shared fit as if it were hundreds of independent measurements, and would **understate the interval**.

Correct handling, and it produces a pleasing symmetry:

> **Each channel has per-question measurement noise plus exactly one shared instrument.**
> Binary: measured α_q + the shared β regression. BT: per-question Δ posterior + the shared calibration curve.

**Getting the β coefficient draws cheaply.** The default should be to **save the coefficient posterior draws from the β regression that already exists** — `fit_beta_regression_nocontext.py` is a PyMC model, so the draws are free; we currently throw them away and keep only moment-matched per-question marginals. That is not a new Bayesian layer, it is reusing an accepted one. The fallback, if those draws prove unavailable, is a ridge-penalized cluster-bootstrap refit over the ~100 calibration questions — **not** 1000 PyMC refits (hours of compute for no gain) and **not** draws from an asymptotic covariance matrix, since with 2 trials per question and rare failures both the covariance and the separation behaviour are untrustworthy. Either way, no new hierarchy: the existing PyMC fits (BT anchors, the β regression) stay as they are and we only resample on top.

**One amendment to the "coefficients only" rule.** Resampling coefficients alone treats the regression as *exact given the draw* — but true β_q scatters around its predicted value, because R² < 1. The complete scheme is a shared coefficient draw **plus an independent per-question residual term**. For the pooled score this makes little difference (residuals average out over 554 questions), but for **per-question and per-slice intervals it matters**, and we do intend to slice by genre, frame type, and question category. Include the residual; note in the report that it is inert at the aggregate level.

**And a bias warning that no amount of resampling will surface.** ~200 total Bernoulli trials estimating a multi-parameter logistic is thin, and if β depends on anything beyond frame type and answer length — near certain — every question carries a systematic prediction error that the bootstrap cannot see. Worse, β is defined on *verbatim ground-truth-vs-ground-truth* pairs, whereas at deployment we apply it to a differently-phrased but equally good model answer, which plausibly fails more often. So predicted β is likely **biased low**, which biases `p_q` low. This runs opposite to the α transport bias in §8.1, and the two will not cancel by design. Both belong in the limitations section of any write-up, not in the interval.

---

## 5. One mechanism: a draw bank

Everything above becomes a **draw bank** — a small set of arrays computed once, cached on disk, and thereafter only indexed:

| array | shape | how it is produced |
|---|---|---|
| Δ draws, BT questions | (310, ~1000) | already exist in memory; must be persisted (§9) |
| calibration (a, b) | (1000, 2) | **new** — cluster-bootstrap the calibration set by question |
| β regression coefficients | (1000, k) | **new** — cluster-bootstrap the GT-pair fit |
| α_q Beta draws | (554, 1000) | closed form from the stored (k_q, n_q), Jeffreys prior Beta(0.5 + k_q, 0.5 + n_q − k_q) by default, uniform Beta(1 + k_q, 1 + n_q − k_q) as the sensitivity arm (§8.5); instant |
| β residual scale | scalar | **new** — the residual spread of the β regression (§4) |
| verdicts v_q and their trial counts | (554,) each | already produced by the binary judge; counts are needed to resample v_q |

A replicate is then array indexing, not inference. Two thousand replicates over 864 questions runs in well under a second, and — the point that decided the design — **no new complex model has to be fitted or defended.** The two genuinely new uncertainty sources are both obtained by resampling data we already have.

---

## 6. One replicate, step by step

1. Draw one shared calibration pair (a, b) — index into the cached array.
2. Draw one shared set of β-regression coefficients — index into the cached array.
3. Resample the 310 BT questions with replacement, and the 554 binary questions with replacement, **separately**. (That separation *is* the stratification: it holds each replicate's channel mix at the true proportion instead of letting composition noise inflate the interval.)
4. For each sampled BT question: pick one index into its own Δ draws, apply σ(a + b·Δ). Indices are drawn **independently per question** — verified: `bt/fit.py` fits a separate per-question model with θ zero-sum *within* a question, so draw *i* means nothing in common across questions. (This resolves the open check Fable flagged.)

5. For each sampled binary question: draw α_q from its Beta posterior; compute β_q from this replicate's coefficients **plus that question's own residual draw**; resample v_q to reflect its own binomial noise over the few orderings judged; then apply (v_q − α_q)/(1 − α_q − β_q). **No clipping here.** [**This is deprecated** -- TU 8/21/26]

6. Record four numbers for this replicate: the binary-channel mean, the BT-channel mean, the count-weighted pooled mean over all sampled questions, and the equal-weight average of the two channel means. Clip each to [0, 1] at this point.

Repeat 2000 times; report the 2.5th and 97.5th percentiles.

The **point estimate is computed separately** as the plug-in value — posterior-mean (a, b), posterior-mean β coefficients, posterior-mean α_q, mean of each question's Δ draws, no resampling. The bootstrap mean will be close but is the wrong thing to quote.

Note the asymmetry that justifies the whole design: step 4's per-question draws partly average away across questions; steps 1–2's shared draws do not. That is why they are drawn at different levels.

---

## 7. What gets reported

**Substantive** — all four, all with 95% percentile intervals:

- pass/fail accuracy (554 questions)
- partial-credit score (310 questions)
- pooled substantive, count-weighted — i.e. the plain mean of `p_q` over all 864
- pooled substantive, equal-weight channel average ← *the expected headline number*

All four come out of the same bootstrap, so they are mutually consistent and no extra machinery is needed to keep all of them in the data.

**Scores by reasoning type.** In addition to the channel breakdown above, the substantive score is also broken out by what kind of reasoning a question demands (`substantive/groups.py`), keyed on the benchmark's `reasoning_type` field:

- **cloze** — a passage is given and the model fills in a blank (`phrase_cloze`, `sentence_cloze`, `topic_sentence`)
- **constrained generation** — the model is given specs and produces a passage (`constrained_generation`, `character_modeling`)
- **knowledge and inference** — answered with a fact or a term, including abstention (`knowledge`, `inference`, `abstention`/`refusal`)

Each group spans both scoring channels unevenly (on 0.7: cloze is mostly pass/fail, constrained generation is mostly partial-credit, knowledge/inference is almost entirely pass/fail), so each group's score is the **count-weighted** mean of `p_q` over every question in the group, both channels — the same combination rule as the pooled count-weighted score above, applied within the group rather than across all questions. Consequently the three group scores do **not** average back to the equal-weight headline; this is a breakdown, not a decomposition, and the report says so next to the table. Questions excluded below the informativeness floor (§8.2) drop out of their group's count along with the headline's.

**Style** — unchanged from `stylejudge/f1_reports/model_report.md`: T_E2, T_drift, T_KS, T_disp, and the fused (p_KS, p_E2) statistic.

**Conventions.** 95% intervals everywhere, including the BT path's per-question intervals, which move from central 90% to 95%. This is a reporting change only — the underlying draws are untouched — and it means every number in the final report has the same meaning.

**No multiplicative combination of style and substance.** Per the spec, that decision is deferred; the report presents substantive and stylistic strength side by side as different kinds of achievement.

---

## 8. Assumptions and guards

**8.1 The transport assumption — the one real threat, and it hits both channels.** Both calibrations are fitted on the **benchmark's own answer inventory** (ground truths, distractors, held-out options) and then applied to model outputs. Bad model answers are fluent, on-topic, and long; with a length-biased judge their true pass rate is almost certainly higher than the distractors' was, so **α is underestimated and `p_q` inflated**. A strong model's wrong answers are wrong in subtler ways still, so α plausibly varies by model — which would mean no clean constant to divide out. This is not fixable by better statistics; it must be stated and bounded. Guards: **recompute the leaderboard with α inflated 50% and report whether any ordering flips**; and where feasible, draw future judge-validation answers from the same spread of models being evaluated rather than from the benchmark's distractors. If nothing moves under α inflation, we can say so in print and stop worrying.

**8.1b Rogan-Gladen assumes a binary latent state; model answers are graded.** The correction supposes each answer is exactly "good" or "bad." A partially-correct model answer fits neither, and under that misspecified two-point mixture `p_q` is a mixture weight rather than a clean "probability the answer is as good as the ground truth." This is a genuine limit on how the pass/fail number may be described — and it is precisely the defect the partial-credit channel exists to remedy, which is a good reason to be generous about which questions get `partial_credit == 1` in future benchmark versions. State it; do not paper over it.

**8.2 The informativeness floor — the automated replacement for the human in the loop.** If 1 − α_q − β_q falls below ~0.2, the judge is near-coin-flip on that question and the correction explodes rather than corrects. Such questions are **excluded, with the count reported** — never silently clipped or quietly downweighted. This is what replaces HITL routing. Encouragingly, the routing field already does most of this work: of the 18 questions with α-reliability ≤ 0.65 that appear in both 0.4 and 0.7, **17 already carry `partial_credit == 1`**. The floor is a backstop for the residue, not a load-bearing filter.

**8.3 Clip aggregates, never per-question corrections.** Rogan-Gladen is linear in the verdict, so per-question excursions outside [0, 1] cancel in the mean. Clipping them individually biases the aggregate inward. Clip once, at the replicate mean.

**8.4 Correct, don't also downweight.** The old `w_q = (2r − 1)²` inverse-variance weights are retired. Correcting *and* weighting by the same reliability double-counts it and makes the score depend on judge quality in a way no reader can interpret. Low-reliability questions are either corrected or excluded (§8.2), not weighted.

**8.5 The uniform prior on α is not a neutral choice — default to Jeffreys.** Beta(1 + k, 1 + n − k) with n_q = 6 and k = 0 has posterior mean 0.125 against an MLE of 0 — and it pushes the *same* direction on every clean question, hundreds of times over, systematically inflating corrected scores. **82.3% of pass/fail questions have a perfect judge** (k = n), so on the modal question the prior alone supplies all of α: mean α across the pass/fail set runs 0.033 under the MLE, 0.084 under Jeffreys `Beta(0.5 + k, 0.5 + n − k)`, and 0.125 under the uniform prior. Jeffreys is the default; report the uniform result as the sensitivity arm, not the other way around. While there, spend one line on the **α–β correlation**: both sit in the same denominator, so in principle they should be drawn jointly, but the effect on interval width is second-order. A sensitivity check is enough — do not restructure the draw bank for it.

**8.6 Diagnostics that are not uncertainty.** Report but do not fold into intervals: the BT judge's measured length preference (`p_longer = 0.618` on the pilot — see §2.1, where it is a *bias in the point estimate*, not noise), the BT model-fit checks `ppc_pair_check` and `three_cycle_check` (currently written but never called in production), the clip rate from §8.3, and the fraction of replicates near the informativeness floor.

**8.7 Effective sample size of the BT calibration set.** 239 records over 40 questions is a cluster sample: options within a question share one BT fit and the judge's idiosyncrasies on that material, so the **effective n is nearer 40 than 239.** Clustered bootstrapping (§9, item 3) gets the interval right, but the underlying message is that this set is small and should be enlarged as the 310-question production run generates more leave-one-out records.

**8.8 One definitional choice to settle in the code plan.** `v_q` should be the *collapsed fraction* rather than re-thresholded to 0/1, since α_q and β_q were measured as per-trial rates and Rogan-Gladen is linear — so the fraction loses less information at no cost in coherence.

**8.9 No silent fallbacks.** `bt_context_scoring.py` currently substitutes `tau_mean` for `p_fit` under the same key name when no calibration file is found. In the new pipeline a missing calibration artifact must be a hard error; uncalibrated τ is not on the `p_q` scale and must never enter a pooled score.

**8.10 Calibration and deployment must be mechanically identical.** The leave-one-out items that fit (a, b) must go through the *same* cut-inference procedure, the same reference policy, and a comparable number of pairwise comparisons as a deployed candidate — otherwise the attenuation levels differ and the curve corrects the wrong amount. The pilot looks consistent on this (LOO records show `n_comparisons` ∈ {8, 10, 12, 14}, matching candidates), but it should be asserted in code rather than assumed, and re-checked when anchors are refit for the 310-question production run.

---

## 9. Artifacts that must be in position first

None of this can run until these exist. Listing them here so the code plan can schedule them:

1. **α measured for 79 questions.** 173 of 0.7's questions are absent from the 0.4 reliability file; 79 of those are `partial_credit == 0` and so need fresh alpha trials. (The other 94 route to BT.)
2. **β regression coefficient draws** — saved from the existing PyMC fit if possible, else a ridge-penalized cluster bootstrap (§4). Also needed: the residual scale.
3. **Calibration (a, b) draws** — cluster-bootstrap of the calibration set **by question**, not by record: it is 239 records over only 40 pilot questions, so the clustering matters and the resulting instrument uncertainty will not be negligible.
4. **Persisted Δ draws.** Currently discarded (`bt_context_scoring.py:349` binds the calibrated draws and drops them). Cheap to recover — anchor posteriors are on disk and judge calls are cached — but the pipeline needs them stored.
5. **Anchor fits for the 310 `partial_credit == 1` questions**, replacing the 40-question pilot.
6. **Adjusted metadata frames** inherited from 0.4 by question number, per the spec.

---

## 10. Verification

The philosophical claims in this document are checkable, and should be checked before the code plan is finalized:

- **The self-cancelling result** (§Context) — reproduce the table from `modelasjudge/scored_answers/mcacc_*__0.4.json`. *Already done; numbers above.*
- **The exact identity** (§2) — with shared α, β, confirm numerically that the mean of the per-question display posteriors equals π̂ to floating-point precision.
- **Per-question independence of Δ draws** (§6 step 4) — confirm from the anchor archive that θ arrays are per-question with question-local item ids. *Already done: 40 separate `theta__{q}` arrays, widths varying with each question's option count.*
- **Instrument noise is material** — report the interval width with layers 1+3 only versus all three layers. If layer 2 adds nothing, §4 was a lot of care for no gain and we should say so; if it adds a lot, the calibration set needs enlarging before publication.
- **The α-inflation sensitivity check** (§8.1) — run it and report whether any ordering flips.
- **The α prior-sensitivity check** (§8.5) — recompute every score under Beta(1 + k, 1 + n − k) versus Jeffreys and report the shift. This is cheap and it touches hundreds of questions in one direction, so it should not be skipped.
- **Does length as a calibration covariate change anything?** (§2.1) — fit σ(a + b·Δ + c·z_len) alongside the current curve and compare held-out log-loss. If `c` is significant, the two-parameter curve is transporting the judge's length bias into the scores and the three-parameter version should replace it.
- **Per-slice calibration** (§2.1) — check whether `p_q` is calibrated within frame type and answer-length band, not just in aggregate. Heterogeneous attenuation would show up here and nowhere else, and it would compromise exactly the sliced comparisons the benchmark exists to support.

---

## 11. Deferred to the code plan

Not decided here: file formats and artifact naming; draw-count thinning; where the pipeline runner lives; the schema of the results spreadsheet (model slug × reasoning level × benchmark version × date); whether style and substance are ever combined into a single figure of merit.

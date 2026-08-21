# How the final score is actually computed

*Written to be read straight through, not skimmed. Describes the pipeline as it
stands after the 2026-08-19 calibration and auto-verdict changes; §6 explains why
the scale changed.*

---

## 0. Which code is live

Three modules have, at different times, been "the final scoring stage." Two are dead:

| Module | Status |
|---|---|
| `score_calculation.py` | **DEPRECATED** (its own docstring, line 2). Superseded by `montecarlo_accuracy.py`. Kept because tests and comments reference it. |
| `montecarlo_accuracy.py` | **DEPRECATED** (its own docstring, line 3). Superseded by `score_substantive.py`. Its three-aspect multiplicative correction "is now a near no-op." |
| `score_substantive.py` → `substantive/estimator.py` | **Live.** Stage 11 of `run_pipeline.py`. |

This matters for one specific reason. Both dead modules binarize scores at a 0.5
threshold (`score_calculation.py:123-125`, `montecarlo_accuracy.py:93-109`), which would
interact badly with where the partial-credit scale puts ground truth. No live code path
does this. **The live estimator never thresholds anything** — it consumes continuous
quantities all the way to the headline number. Any argument about the scoring scale that
rests on the 0.5 threshold is an argument about deprecated code.

---

## 1. The one quantity

Everything in `substantive/estimator.py` exists to estimate one thing, per question:

> **p_q — the probability that the candidate's answer to question *q* is substantively
> as good as the ground truth.**

The benchmark score is the mean of p_q over questions. That is the whole idea. The
complexity below is entirely about the fact that we cannot observe p_q directly — we
observe a noisy judge, and we have to invert the noise.

Questions reach p_q by one of two routes, depending on how `substantive/routing.py`
routed them:

- the **binary channel** (pass/fail path), and
- the **partial-credit channel** (the Bradley-Terry path).

The two routes are completely different machinery, and they are supposed to arrive at
the same quantity. §6 and §7 are about a way they had drifted apart, and what was done
about it.

---

## 2. The binary channel: inverting judge noise

### What we observe

For a pass/fail question, the judge is asked to compare the candidate answer against
each ground truth, and each comparison yields pass or fail. `drawbank.py:175-177` reads
those and computes

- `v_hat` — the observed **pass rate** for that question (mean of the 0/1 scores), and
- `n_v` — how many comparisons produced it.

If the judge were perfect, `v_hat` *would be* p_q and we would stop here. It isn't.

### The two error rates

The judge makes two kinds of mistake, and they are estimated by completely separate
machinery:

**α (alpha) — the false-pass rate.** The probability the judge passes an answer that is
*not* actually as good as the ground truth. This is measured directly, by
`judge_alpha_reliability_nocontext.py`: for each question it stages duels between the
ground truth and each of the question's own distractors — answers we *know* are bad —
in both A/B orderings, and counts how often the judge wrongly lets the distractor tie
or win. So α is a per-question property estimated from *benchmark items*, and it
carries a Beta posterior with a Jeffreys prior (`estimator.py:76-90`).

Worth pausing on: **α has nothing to do with the candidate model.** It is a property of
(this judge, this question). The same α applies whichever model you are scoring.

**β (beta) — the false-fail rate.** The probability the judge fails an answer that *is*
as good as the ground truth. This one cannot be measured the same way — we have no
supply of known-good-but-not-ground-truth answers — so it is *modelled*, by
`fit_beta_regression_nocontext.py`, as a regression on question features:

```
beta_q = expit(b0 + u_frame[frame_type_of_q] + b_len * z_loglen_q) / 2
```

(`estimator.py:93-118`). The `/2` is structural: it bounds β to (0, 0.5) by
construction, because a judge that fails good answers more than half the time is not a
judge. `u_frame` is a per-frame-type offset (world_context / book_context /
passage_context); `z_loglen` is the standardized log length of the ground truth.

### Rogan–Gladen: the inversion

[References to Rogan-Gladen throughout this document are deprecated.]

Given a true p_q, the pass rate we *expect* to observe is

```
v = p·(1 − β)  +  (1 − p)·α
     ^^^^^^^^^     ^^^^^^^^^
     good answers  bad answers
     correctly     wrongly
     passed        passed
```

Solve for p and you get the Rogan–Gladen estimator (`estimator.py:26-35`):

```
p_q = (v_q − α_q) / (1 − α_q − β_q)
```

**A worked example.** Suppose a question has α = 0.15 (the judge lets 15% of known-bad
distractors through) and β = 0.10. The denominator, `1 − α − β = 0.75`, is what the code
calls **informativeness** (`:38-40`) — how far this judge is from a coin flip on this
question.

- Observed `v_hat = 1.0` (candidate passed every comparison) → p_q = (1 − 0.15)/0.75 = **1.133**
- Observed `v_hat = 0.5` → p_q = (0.5 − 0.15)/0.75 = **0.467**
- Observed `v_hat = 0.0` → p_q = (0 − 0.15)/0.75 = **−0.200**

Yes, those go outside [0, 1]. That is deliberate and correct: `rogan_gladen` never
clips, and the docstring at `:29-30` explains why — individual excursions are
legitimate and cancel in the mean. Only the *aggregate* is clipped (`:160-164`). If you
clipped per question you would bias the mean upward at the bottom and downward at the top.

**This is exactly where automatic verdicts matter.** A verbatim string match is not a
judge output. It has no α and no β. The pipeline used to feed its `v_hat = 1.0` through
Rogan–Gladen anyway and emit 1.133 — wrong in a way nothing downstream could detect.
Such questions now carry an override that replaces the corrected value with the verdict
itself (§8).

### The floor

`floor_mask` (`:43-45`) drops questions where informativeness < 0.2 — where the judge is
so close to a coin flip that dividing by `1 − α − β` would amplify noise catastrophically.
Note it **excludes** rather than clips. An automatic-verdict question consulted no judge
at all, so excluding it on grounds of judge quality would make no sense — those are
exempt from the floor (§8).

---

## 3. The partial-credit channel: a different world

Nothing above applies here. No α, no β, no Rogan–Gladen.

### Step 1 — Bradley–Terry, per question

For each partial-credit question, `bt/fit.py` fits a Bradley–Terry model over that
question's **own answer options**: its ground truths and its distractors. Every pair is
judged in both orderings; the model turns win counts into a latent quality score θ per
option, on a logit scale:

```
P(item i beats item j) = sigma(theta_i − theta_j)
```

θ is only meaningful up to differences — the fit is constrained sum-to-zero
(`fit.py:105`). This is the **anchor fit**: it places the question's known answers on a
quality scale, using only judge comparisons among items whose quality we already know.

### Step 2 — locate the candidate on that scale

`bt/tau.py::score_candidate` compares the candidate against the anchors and infers its
θ, holding the anchor draws frozen. Then (`tau.py:123`):

```
Delta = theta_candidate − mean(theta of all ground truths)
```

**This definition is the source of everything confusing in §7, so it is worth stating
plainly: Δ = 0 *means* "exactly as good as the ground truths."** Δ > 0 means better,
Δ < 0 means worse. Δ is in logit units and is capped at ±8 by the inference grid
(`tau.py:59, 88`).

### Step 3 — calibration: turn Δ into a probability

Δ is on an arbitrary logit scale. To get a probability we need a curve, and
`bt/calibrate.py` fits one:

```
p_fit = sigma(a + b·Delta)
```

Where do the training labels come from? From **leave-one-out** (`cmd_loo`): each answer
option in turn is held out, the anchor model is refit without it, and it is re-scored as
if it were a candidate. Then (`bt_context_scoring.py:620-633`):

- a held-out **ground truth** gets label **1.0**
- a plain **distractor** gets label **0.0**
- a **partial-credit** distractor (benchmark probability strictly between 0 and 1) gets
  that fractional value as a *soft* label

So the curve is fit to answer: *given a Δ this large, how likely is this to be a
good answer?* Current fitted coefficients on the 0.7 benchmark: **a = −0.6395,
b = 0.5986**.

`apply_calibration` (`calibrate.py:99-108`) applies it across the posterior draws and
returns the **mean of the sigmoid**, `E[σ(a + bΔ)]`, not the sigmoid of the mean.

---

## 4. Where the headline number is assembled

`substantive/estimator.py::plugin_point` (`:140-170`) computes the number you quote:

```python
p_binary  = rogan_gladen(v_hat, alpha, beta)[keep]          # binary channel
p_partial = expit(cal_a.mean() + cal_b.mean() * delta_draws.mean(axis=1))

passfail     = clip(p_binary.mean(), 0, 1)
partial      = clip(p_partial.mean(), 0, 1)
pooled_count = clip((p_binary.sum() + p_partial.sum()) / (n_pf + n_pc), 0, 1)
pooled_equal = clip((passfail + partial) / 2, 0, 1)
```

Two observations that are easy to miss and that the plan depends on:

1. **The estimator does not read `p_fit`.** It reads the persisted **Δ draws** and
   recomputes the sigmoid itself. So writing `p_fit = 1.0` into a scored file changes
   what you see in that file and changes *nothing* about the headline number. That is
   the entire reason Part 5 of the plan exists.
2. **`pooled_count` averages `p_binary` and `p_partial` together as if they were the
   same quantity.** Hold that thought for §7.

---

## 5. The bootstrap: three layers of uncertainty

`bootstrap` (`:189-290`) produces the confidence interval by resampling three distinct
things per replicate. The layer names are literal strings you can switch off, which
makes them individually attributable:

**Layer 1 — "judgment."** The noise in *this* measurement. On the binary channel: draw
α from its Beta posterior, redraw `v_hat` from a Binomial with `n_v` trials, draw the
β residual. On the BT channel: pick a random index into that question's Δ draws
(`:258-261`). This is "if we ran the judge again, what would we see?"

**Layer 2 — "instrument."** The uncertainty in the *calibration and regression
coefficients themselves*. One shared draw index per replicate (`:226-230`) — shared
because if the calibration curve is wrong, it is wrong for every question at once. This
correlation is why a coefficient's uncertainty does not average away across questions.

**Layer 3 — "item."** Resampling *which questions are in the benchmark*, with
replacement (`:265-273`). This is the "would a different 300 questions have given the
same answer?" component.

Only after all three does it take means (`:275-279`). The clip happens on the replicate
mean, never per question (`:282-285`).

One consequence worth stating for the auto-verdict work: forcing a verbatim match to
exactly 1.0 removes its layer-1 variance, which is *correct* — there is no measurement
noise in a string comparison — while layer 3 still resamples over it, so its
contribution to "would a different question set change the answer?" is retained.

---

## 6. Why the old scale was odd

Combine §3's two facts:

- Δ = 0 means "exactly as good as ground truth," and
- p_fit = σ(a + b·Δ)

and you get: **a ground-truth-quality answer scores σ(a).** When `a` was fitted freely
it came out at −0.6395 on ChronoLogic 0.7, so σ(a) = **0.345**. Empirically, held-out
real ground truths under LOO had median p_fit **0.328** (n = 38), which matches.

So the old scale said: *a perfect answer is a 0.33.* That was not a coding error — the
curve was correctly fit to its training data — but it made the number uninterpretable on
its face, and, worse, unstable for a reason that had nothing to do with answer quality.

### Where the intercept comes from — the crucial diagnosis

The obvious guess is that the judge got harsher between benchmark versions. Mostly it
didn't. Here is the actual training data both curves were fit to:

![BT calibration training data](figures/bt_calibration_scatter.png)

*(`figures/bt_calibration_scatter.png`. x = Δ; y = the calibration label, jittered
±0.035 so overlapping points are visible. Grey dashed = the superseded free-intercept
fit; black = the anchored fit adopted in §7, refit on each panel's own data.)*

Read the green points first. **The ground-truth clouds are nearly identical between the
two panels** — same location, same spread, straddling Δ = 0 as they should:

| | 0.1 benchmark | 0.7 benchmark |
|---|---|---|
| intercept `a` | +0.7015 | −0.6395 |
| slope `b` | 0.7024 | 0.5986 |
| **held-out-GT Δ: q25 / median / q75** | **−1.33 / −0.15 / +1.12** | **−1.34 / −0.13 / +1.22** |
| distractor Δ: median | −5.01 | −4.46 |
| distractors with Δ > −1 | 3.4% | 8.6% |
| AUC (GT vs distractor) | 0.939 | 0.908 |
| label mix | 60 GT / 148 distractor / 31 partial | 38 GT / 336 distractor / 31 partial |
| good:bad label log-odds | −0.858 | −1.899 |
| resulting GT p_fit median | 0.645 | 0.328 |

The intercept moved **−1.341**. Decomposing it:

- **−1.040 (78%) is exactly the shift in the label mix's log-odds** — going from 60:148
  to 38:336 good:bad training examples. This is the standard case-control result: fit a
  logistic model on a sample whose class balance you chose yourself, and the **slope is
  consistently estimated while the intercept absorbs the log of the sampling odds**. The
  number of distractors per question is a *benchmark design choice*, not a fact about
  answer quality.
- **−0.301 (22%) is residual**, and it is not nothing. The purple cloud in the right
  panel is visibly denser near Δ = 0: distractors in 0.7 are genuinely a bit harder
  (median Δ −5.01 → −4.46, share above −1 more than doubling, AUC down 3 points). That
  is real signal about separability, entangled with the slope drop (0.70 → 0.60) and the
  ridge penalty.

The headline conclusion survives the caveat: **`σ(a + bΔ)` is not a transportable
"probability this answer is as good as ground truth."** It is "probability of the
positive class given Δ, under whatever good:bad ratio happened to be in the calibration
set." Write more distractors for the same questions, and every model's score drops
without any model getting worse.

One thing the plot makes plain that the numbers alone don't: **the curve does not pass
through the ground-truth cloud.** In the right panel the fitted sigmoid crosses Δ = 0 at
0.345 while the green points sit at 1.0. That is not a fitting failure — with 336
distractors versus 38 ground truths, pulling the curve up through the green cloud would
cost far more on the purple points than it saves. The curve is doing exactly what it was
asked to do; the question is whether that is the thing we want to report.

---

## 7. The fix that was adopted: pin the anchor, balance the classes

**This is now what the code does** (`bt/calibrate.py`, since 2026-08-19). Two changes,
both aimed at the diagnosis in §6.

**1. Pin the intercept.** Fix `a := logit(0.90)` and solve for the slope only — a GLM
offset. Ground-truth parity becomes a *declared constant* rather than an estimate, and
the prevalence term is gone by construction rather than by subtraction.

**2. Balance the classes.** Ground truths and non-ground-truths (distractors plus
partial-credit answers) each get half of a fixed weight pool, so 336 distractors cannot
outvote 38 ground truths. On 0.7 that is 5.329 per ground truth against 0.552 per
non-ground-truth — a 9.66× ratio.

Fitted on 0.7: **a = 2.1972 (pinned), b = 0.9516**, against the old free fit's
a = −0.6395, b = 0.5986.

### What it does to actual numbers

| Δ (candidate minus GT, logit units) | old: σ(−0.6395 + 0.5986Δ) | **now: σ(2.1972 + 0.9516Δ)** |
|---:|---:|---:|
| −4.0 | 0.046 | 0.167 |
| −3.0 (much worse than GT) | 0.081 | 0.341 |
| −2.0 | 0.137 | 0.573 |
| −1.0 | 0.225 | 0.777 |
| **−0.13 (median held-out GT)** | **0.328** | **0.888** |
| **0.0 (exactly GT-level)** | **0.345** | **0.900** |
| +1.0 (better than GT) | 0.490 | 0.959 |
| +2.0 | 0.636 | 0.984 |
| +3.0 | 0.761 | 0.994 |

Read the two bolded rows. That is the point: **ground-truth parity is 0.90, exactly, by
construction and with zero variance.** The number is readable without consulting a
calibration artifact, and it no longer moves when someone writes more distractors.

Class balance is also a clean *experimental* confirmation of §6's diagnosis. Rebalancing
alone (leaving the intercept free) moves the label log-odds by +1.979 and the fitted
intercept by +2.176, while the slope barely budges, 0.60 → 0.76. Reweighting acts almost
entirely on the intercept, exactly as case-control theory predicts — this is measured
directly, not inferred from a cross-version comparison.

And the strongest evidence that this fixes the right thing: **the anchored fit lands in
nearly the same place on both benchmark versions.** Refit per version, the free
intercepts are +0.70 and −0.64 (GT parity 0.669 vs 0.345), while the anchored fits are
a = +2.1972 both, b = 0.9123 and 0.9516. What was a wild swing becomes a 4% difference
in slope — which is the residual real change in judge separability from §6, and nothing
else. Both curves are drawn in the figure above.

### Why 0.90 and not 1.0

1.0 is unreachable by a sigmoid at finite Δ, and anchoring judged ground truths at the
very top would saturate the instrument. Real candidates cluster *at* ground-truth level
(median candidate p_fit under the old curve was 0.316 against a GT median of 0.328), so
putting GT at the ceiling would collapse roughly half the benchmark into an atom at 1.0
and destroy discrimination exactly where the data lives.

0.90 leaves headroom above ground truth without spending the useful range on it, and
reserves 1.0 for **automatic verdicts** — a candidate answer verbatim identical to a
ground truth, where there is nothing to estimate. The guarantee is therefore:

> Ground-truth parity = 0.90, a known fixed constant. Verbatim ground truth = exactly
> 1.0. Everything else falls between, monotonically.

### What it costs, stated plainly

Under the anchored scale 22.3% of probability-0 distractors score above 0.5, 12.8% above
0.7, and 4.2% above 0.90. That last figure looks alarming next to the old curve's
"0.3% above 0.90" — but the comparison is meaningless, because the two curves put
ground truth in different places. Compare each against *its own* ground-truth parity
point and they are identical:

| | anchor p(Δ=0) | distractors above the anchor |
|---|---:|---:|
| old free fit | 0.345 | 4.2% |
| **anchored** | **0.900** | **4.2%** |

Both report the same invariant: **4.2% of probability-0 distractors have Δ > 0** — the
BT judge genuinely ranks them above the average ground truth. AUC is 0.908 either way.
Anchoring does not create that tail; it makes it legible. The old curve concealed it by
pushing ground truths down to 0.328 alongside it.

That 4.2% is the instrument's honest resolution limit. (Breaking the tail down by
distractor class is informative: of the 75 that clear 0.5, 58 are `context`-class —
anachronistic answers — at 27.5% of that class, against 13.9% of `question`-class ones.
`anachronistic_gpt-5.4` alone contributes 15. Modern frontier models write anachronistic
text this judge cannot reliably catch. That is a judge-quality finding, equally true
under either calibration, and it argues about the rubric rather than the curve.)

### What it does not fix

- **The slope still moves.** `b` went 0.70 → 0.60 across benchmark versions. Pinning is
  immune to class balance, not to this. That drift is a real change in how sharply the
  judge separates good from bad and arguably *should* move the scale — but name it
  rather than let it pass silently.
- **Held-out ground truths sit at Δ ≈ −0.13, not 0**, a small leave-one-out asymmetry:
  when you hold out a ground truth, Δ is measured against the *remaining* ones, and the
  held-out one tends to score marginally below them. So judged ground-truth-quality
  answers land at 0.888 rather than exactly 0.900.
- **Pinning discards the 22% residual along with the 78% artifact.** The −0.301 of §6
  that reflects genuinely harder distractors in 0.7 goes too. The defence is that
  separability still registers through the slope, which is the parameter that actually
  measures discrimination, and that there is no principled way to split an intercept
  into "artifact" and "signal" after the fact. It is a judgment call, not a free lunch.

### The alternative that was rejected

`pilot_record/bt_pilot_findings.md:453-462` proposed, under "agreed direction, not yet
built": `benchmark score = p_fit / median p_fit(held-out ground truth)`, so ground truth
lands at 1.0. Three reasons it was not adopted:

1. **It divides one prevalence-contaminated number by another.** §6's problem is additive
   on the *logit* scale; division on the probability scale cancels it only at the median
   itself, so the same candidate Δ still gets different scores across benchmark versions.
2. **The normalizer is very noisy and does not improve.** The bootstrap 95% CI on the
   median of the 38 held-out GT `p_fit` values is **[0.23, 0.46]** around 0.328 — ±35%
   relative, perfectly correlated across all questions, and dependent on the number of
   held-out ground truths rather than the number of questions. Choosing the mean instead
   of the median moves it 12% on its own.
3. **Clipping at 1.0 lands in the middle of the data** — the saturation problem above.

Pinning has none of these: no normalizer to estimate, so no normalizer CI; no ratio; no
clipping; no atom at 1.0.

### Three things worth being clear about

**It changes no rankings.** σ(a + bΔ) with any fixed `a` is a monotone transform of the
same Δ. Every model's questions are ordered identically and every model's rank against
every other is identical. This changed what the number *means*, not who wins.

**It does change the headline number**, because `pooled_count` (§4) averages the two
channels. The BT channel's mean rises substantially, so any pooled figure from before
2026-08-19 is on a different scale and is not comparable.

**It is not a correction for judge error.** The Rogan–Gladen inversion on the binary
channel *is* such a correction. Anchoring is a change of reporting scale — it removes an
artifact of how the calibration set was assembled. Those are different kinds of
operation and the docs should not blur them.


## 8. How automatic verdicts reach the headline number

Two conditions skip the judge entirely (`substantive/verdicts.py`): a candidate answer
verbatim identical — lowercased, punctuation-stripped — to a ground truth is an
automatic pass, and one identical to a probability-0 distractor is an automatic fail.
On the pass/fail path the fail applies only to distractor types whose penalty class is
`question` or `both`; `anachronistic_*` types are exempt there, because that path does
not measure period fidelity. The partial-credit path fails every probability-0 match.

Getting that into the score takes more than writing it into the scored file. As §4 said,
the estimator recomputes probabilities from Δ draws and from `v_hat`; it never reads the
`p_fit` written into a scored file. So a short-circuit is represented where the estimator
actually looks:

- **BT channel** — an `auto__{qnum}` scalar in the Δ-draws npz, applied as
  `np.where(np.isnan(auto_pc), p_partial, auto_pc)`, bypassing the calibration curve.
- **Binary channel** — an `auto_pf` array derived from the `auto_verdict` field in the
  scored file, applied the same way, bypassing Rogan–Gladen. This also repairs the
  existing 1.133-style out-of-range contribution described in §2.

Both default to NaN, so every artifact written before this existed reproduces its old
numbers exactly.

Two consequences worth stating. An overridden question contributes **zero
judgment-layer variance** to the bootstrap, which is correct — a string comparison is not
a noisy measurement — while item resampling still resamples over it, so between-question
composition variance is retained. And automatic verdicts are **exempt from the
informativeness floor** (§2), which measures the judge.

Note how §7 makes the 1.0 legible. Under the old free-intercept curve an auto-pass sat
about 3× above where judged ground truths landed (1.0 against 0.328). On the anchored
scale it sits just above them (1.0 against 0.900) — which reads as what it is: the same
quality level, known with certainty rather than estimated.

# modelasjudge — substantive scoring of free-generated answers

When a model answers a Chronologic question in its own words, something has to decide
whether the answer is apt. That is harder than it sounds: the answer need not match ground
truth, only fall within the range of what a writer in the specified context might
plausibly have said.

This directory holds code that makes these substantive judgments. Style is scored separately, in
[`../stylejudge/`](../stylejudge).

## The idea

Earlier work found that human readers can reliably tell authentic period prose from an
imitation when shown the two side by side, but not when rating a passage in isolation. The
scoring here is built on that asymmetry: every judgment is a **choice between two
answers**, never a rating of one.

Questions divide into two channels by how much aptness is a matter of degree. The
`partial_credit` field in the benchmark records which channel a question belongs to.

**Pass/fail — 520 questions.** The candidate answer is compared once against an unlabelled
ground truth. If the judge finds it better than or equal to ground truth, it passes. Used where a question either a) has one definite answer, as in many knowledge questions or b) the substantive bar is not terribly high, as with many cloze questions. (If a cloze question fits the passage rhetorically, it passes substantively; the more stringent test will often be stylistic.) Both Type I and Type II error rates average below 5%.

**Bradley-Terry partial credit — 346 questions.** Where aptness is a matter of degree —
could a Quaker periodical really have said this about Indian policy in the 1860s? — one
comparison is too blunt. Instead every pair of that question's reference answers, ground
truths and distractors alike, is compared, and a Bradley-Terry model infers a latent
strength θ for each, the way a series of matches yields Elo ratings. The candidate is then
placed on that scale.

Strong distractors are necessary for this strategy to be effective. Because they span a range from clearly wrong to nearly
right, they supply the middle of the scale, which is where discrimination actually happens.

## Turning θ into a score

Inferring latent strengths places answers on an ordinal scale, but doesn't yet tell us which answers are acceptable, or how close they are to acceptable. To convert θ into a benchmark score, we need to measure the penumbra of acceptable variation. We do this using the 86 questions that have **two** ground truths. Hold one out, score it as though it were a candidate, and fit

```
p_fit = σ(a + b·Δ)      where Δ = θ_candidate − mean(θ_ground_truths)
```

The intercept is pinned so that a Δ of 0 — exactly as good as the average ground truth —
scores **0.90**. Ground truths and non-ground-truths carry equal total weight in the fit; the rationale for that choice is that the numerical superiority of distractors is a feature of question design, not real information about the sharpness of the boundary between acceptable and unacceptable answers.

What this scale looks like in practice:

| | p_fit |
|---|---|
| ground-truth parity (Δ = 0), by construction | 0.900 |
| held-out real ground truths, median | 0.888 |
| held-out real ground truths, 25th percentile | 0.716 |
| probability-0 distractors, median | 0.114 |
| probability-0 distractors scoring above 0.90 | 4.2% |

That last row is not calibration error, and it does not shrink if the scale is re-anchored:
it is the share of distractors the judge genuinely ranks above the average ground truth,
and it represents the instrument's resolution limit. The benchmark's job is separating
slightly-better from slightly-worse answers *below* ground truth, and the pinned scale
gives that region most of the range. Compression above 0.90 is the accepted cost.

## Running it

`run_pipeline.py` orchestrates thirteen stages as separate subprocesses — separate because
each long-running script installs its own SIGINT handler and resumes from its own output
file, neither of which survives being imported into a single process.

```bash
python run_pipeline.py --candidate openai/gpt-5.4 --candidate-label gpt-5.4 \
    --candidate-effort medium --benchmark ../booksample/chronologic_en_1.0.jsonl --dry-run
```

**Always dry-run first.** It prints the stage table with an estimated judge-call count per
stage, which is the only warning before the run starts spending money. Drop `--dry-run` to
execute. Every stage has a content-based skip predicate, so re-issuing the same command
after an interruption resumes rather than restarts.

The stages fall into three groups:

| # | Stage | Scope |
|---|---|---|
| 0–7 | `distractor_sorter`, `seed_reliability`, `alpha_reliability`, `beta_regression`, `anchor_fit`, `loo`, `validate`, `calibrate` | **Instrument** — shared by every candidate. Already computed and committed; these should all report `skip`. |
| 8–11 | `free_generation`, `judge_scoring`, `bt_score`, `score_substantive` | **Candidate** — the per-model work. |
| 12 | `style_score` | Hands off to `../stylejudge/`. |

If a stage in 0–7 wants to *run*, stop and find out why: those are the expensive ones, and
the committed artifacts should satisfy all of them. The usual cause is a benchmark filename
whose version tag doesn't match the artifacts — see below.

Useful flags: `--only STAGE` and `--stop-after STAGE` to run part of the pipeline,
`--force STAGE` to recompute something deliberately, `--no-style` to skip stage 12,
`--judge` and `--bt-judge` to change judges.

## Artifact layout

Filenames encode a tag built from the judge, the benchmark version, the judge effort and
the prompt mode — `bt.artifacts.bt_tag()` assembles it, and **the benchmark version comes
from the benchmark's filename**: `naming.benchmark_version()` takes the last `X.Y` in the
stem. Rename the benchmark file and the pipeline will look for differently-named artifacts.

| Directory | Holds |
|---|---|
| `llm_reliability/` | Per-question judge reliability, measured on known-answer pairs |
| `beta_reliability/` | Posterior draws for binary-judge reliability |
| `bt_artifacts/` | The frozen anchor fit, the pairwise judgments behind it, the LOO set, the calibration draws |
| `bt_artifacts/cache/` | Content-addressed judge-call cache. Not committed: large, and regenerable |
| `substantive_artifacts/` | Per-candidate Δ posterior draws |
| `results/` | Working output — per-model reports and scores, and the append-only ledger |
| `bt/` | The Bradley-Terry implementation: design, collection, fit, calibration, validation |
| `substantive/` | Score assembly: routing, draw banks, the estimator, the ledger, reports |

Artifacts carry provenance in a `meta` blob — what produced them, when, the git HEAD, and
SHA-256 of their inputs. Draw banks refuse to mix incompatible calibrations: `pin_p` and
`class_balance` travel with both the calibration draws and the Δ draws.

Recalibrating is free. `bt_context_scoring.py calibrate` refits from the stored LOO
artifact and makes no judge calls; only `calibrate` ever needs re-running, never
`anchor_fit`, `loo` or `validate`, which are the expensive stages. Anything scored against
a previous curve must then be re-scored.

## Validation

`humeval_bt/` holds the human validation: six readers ranked pairs of answers, and their
agreement with the model's ordering is what licenses reading a score difference as a
preference difference. The headline is that a 0.1 gap between two models corresponds to
roughly a 10% difference in human preference.

`erroranalysis/` breaks down which classes of distractor defeat which models, conditional
on the class being present in a question.

## One wrinkle worth knowing

Five candidates — gpt-5.4, gpt-5.6, gpt-5.6-high, openai/gpt-4.1 and talkie-1930-13b-base —
generated their answers against a release candidate of the benchmark and were re-judged
under the final rubrics. In their `_btcontext.json` files, 319 of 346
`context_fit[qnum]["bt"]` entries still carry the earlier tag and an earlier-calibrated
`p_fit`, because only the 27 reclassified questions were re-scored.

**The scores are correct.** The anchor fits for those 319 questions are bit-identical
across the two tags, and `substantive/estimator.py` never reads that `p_fit` — it
recomputes the sigmoid from the merged Δ draws under the ledger row's tag. The stale value
is a display artifact worth at most 0.023 of p_fit per question if read directly. Trust the
ledger and the report; don't read per-question `p_fit` out of those five files.

## Further reading

- [`../results/README.md`](../results/README.md) — published scores, and which file backs which table row
- [`../DATA.md`](../DATA.md) — the `partial_credit` and `reject_reasons` fields this pipeline routes on
- [`../stylejudge/README.md`](../stylejudge/README.md) — the other scoring axis

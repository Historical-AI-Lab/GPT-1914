# stylejudge — stylistic evaluation

The style judge scores whether a benchmark answer reads like genuine prose of the period
its question targets. It is two frozen DeBERTa instruments (a date predictor and an
authenticity detector) plus a conformal layer that ranks each answer against
date- and length-matched authentic passages.

This file is an index. Nothing here is a source of truth; everything points at one.

## Start here

| You want | Read |
|---|---|
| To run it — what to call, in what order | `StyleJudgeGuide.md` |
| Prose for a paper: the instruments, their accuracy, and the calibration layer | `calibration_appendix.md` |
| The original design argument, before any of it was built | `new-style-judge-spec.md` |
| What was actually built, decision by decision, with every measured number | `NOTES.md` (18 dated sections, Phase A → E4) |

`NOTES.md` is the execution record and outranks every plan document where they disagree.
The phase plans (`phase-a-plan.md` … `phase-e4-plan.md`, `phase-*-runbook.md`) are
forward-looking design records: useful for *why*, unreliable for *what happened*.

## Measured results

| Report | What it covers |
|---|---|
| `evaluations/e3_deberta_evaluation.md` | Date judge, held-out test split, by decade |
| `evaluations/e3_benchmarkbooks.md` | Date judge vs. its lexical predecessor on the reserved benchmark volumes |
| `evaluations/e3_lexical_evaluation.md` | The lexical re-baseline: same pool, same splits, like-for-like |
| `evaluations/e2_authenticity_evaluation.md` | Authenticity detector: test split and the frozen cross-generator holdout, with breakdowns by elicitation modality, generator family, decade, and length |
| `f1_reports/verify_report.md` | Reference-corpus validity check (lexical, both channels). Also the argument for length-conditioning and for exactly 6 length bins. |
| `f1_reports/verify_e3.md` | The same check on the sentences-only reference used by the date channel |
| `e1_stat_diagnostic_report.md` | The pre-registered test that killed the predictive-dispersion hypothesis (rule set in advance in `confirm-null-diagnosis.md`) |

`evaluations/` holds copies; the originals are written by the training code into
`~/workdata/chronologic-dating-corpus/passages/{e1,e2,e3,e3_v2}/`. Regenerate there,
then re-copy — do not edit the copies.

Corpus construction reports: `decade_census_report.md` (what was on disk),
`corpus_roster_report.md` (what was selected, and under which quotas),
`corpus_roster_dated_report.md` (date-reliability exclusions and corrections),
`length_distribution_report.md` (the answer-length distribution everything is sampled
to match), `normalization_census_{before,after}.md` (the Phase C acceptance test).

## Rationale that lives outside this directory

| Topic | Where |
|---|---|
| Why W1 replaced KS as the headline; why empirical p-values were dropped | `../modelasjudge/spec-to-wire-in-style-judge.md` §1, §2, §16 |
| Why W₀/μ₀ are held fixed inside the bootstrap; the per-answer shrinkage correction | `../modelasjudge/plan-wire-in-style-judge.md` lines 42–172 |
| Empirical validation of that fixed-W₀ approximation | `../modelasjudge/substantive_scoring_runbook.md` lines 329–357 |
| Why HMP rather than the Cauchy combination test; what "double-conformal" means | `f1_reports/model_report.md` line 15 — **pre-E4, see below** |

## Four things that will mislead you

1. **`f1_reports/` is Phase F1 output, not F1 scores.** No F1 metric is reported there.
2. **`f1_reports/model_report.md` is pre-E4 (2026-08-17).** It describes the retired
   lexical date channel and the retired T_KS headline; W1 and Period Fidelity appear
   nowhere in it. Its fusion rationale is still the only copy anywhere — take that and
   nothing else from it.
3. **"E1/E2" means two different things.** In specs, plans and reports they are
   *channels* (E1 = date / Period Fidelity, E2 = authenticity). In provenance lines and
   ledger column suffixes, `e1` and `e3` are the *date models* behind the E1 channel
   (`e1` = lexical, `e3` = DeBERTa). An `__e3` report still labels its section "E1 (date)
   diagnostics." `_e3` is not a third channel.
4. **`../bertclassify/`'s markdown documents a different, retired model** — the
   March-2025 binary classifier (deberta-v3-base, 128 tokens, BCE). Only
   `train_date_deberta.py` and `train_date_deberta_A100.slurm` there belong to this
   project.

## A lost document

`typicality.py` and `calibration_corpus.py` cite `phase-f-plan.md` by section number
("rev.2 §4/§5/§6") throughout; `diagnose_e1_stats.py` cites
`in-stylejudge-we-are-frolicking-treehouse.md`. **Neither file exists** anywhere in this
repository or in workdata. Those citations are dead. The surviving substitutes are
`typicality.py`'s own module docstring (~90 lines, effectively a summary of that plan),
`f1_reports/verify_report.md`, and the `modelasjudge` spec/plan pair above. Module
docstrings generally are the best-maintained documentation in this directory — read
`typicality.py`, `score_style.py`, and `calibration_corpus.py` before assuming something
is undocumented.

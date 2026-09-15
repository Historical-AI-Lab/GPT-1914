# Results

Scores for every model reported in the paper, on Chronologic-EN-1.0.

This is a frozen snapshot, not pipeline output. The scoring code writes to
`modelasjudge/results/` and `evalcode/prob_08/`; those are working directories
whose contents change as runs accumulate. The files here are the versions the
paper reports, with machine-specific paths removed.

```
results/
  likelihood/     leaderboard_1.0.{csv,md,tex}    <- paper Table 1
  freegen/
    free_gen_results_1.0.csv                      <- paper Table 2
    chronologic_scores_1.0.csv                    <- the full scoring ledger
    scores/scores_<model>__1.0.json               <- per-model detail, 15 files
```

## A note on version numbering

Five models — GPT-4.1, GPT-5.4, GPT-5.6, GPT-5.6-high and Talkie-1930-13B-base —
generated their answers against a release candidate of the benchmark. Its 866
questions are identical to 1.0; what differed was the judging rubric for 27 of
them, plus one added distractor. Those answers were then re-judged under the
final rubrics.

Every score in this directory is therefore a 1.0 score, and the whole set is
directly comparable. Some intermediate filenames elsewhere in the repository
still carry the candidate's `0.8` tag; that is a naming artifact, not a
difference in what was measured.

## Which file is which paper row

Two mappings are not guessable from the filenames.

**`gpt-41-ft2` is the paper's "GPT-4.1 finetune" row**, not `gpt-41-ft`. The
latter is an earlier fine-tune, superseded; its scores are kept here for
completeness but appear in no table. Likewise `scores_gpt-5.6__1.0.json` is the
medium-effort run, while the paper's "GPT-5.6" row is the high-effort
`gpt-5.6-high`. That is why there are 15 score files for 13 table rows.

**The paper's style columns come from the `_e3` variants.** The ledger carries
two date channels: `style_period_fidelity_e3` and `style_drift_years_e3` are
the DeBERTa instrument the paper uses. The unsuffixed columns belonged to an
earlier lexical date predictor and have been dropped from the copy here.

| Paper Table 2 row | `candidate_label` | effort |
|---|---|---|
| Talkie 1930 13B base | `talkie-1930-13b-base` | — |
| Talkie 1930 13B it | `talkie-1930-13b-it` | — |
| Qwen2.5 7B | `qwen25-7b-local` | — |
| Qwen2.5 72B it | `/projects/bdfx/models/Qwen2.5-72B-Instruct` | — |
| Gemini 3.7 flash | `google/gemini-3.7-flash` | high |
| Kimi K3 | `moonshotai/kimi-k3` | max |
| GPT-4o 2024-08-06 | `gpt-4o-2024-08-06` | — |
| GPT-4.1 | `openai/gpt-4.1` | — |
| GPT-4.1 finetune | `gpt-41-ft2` | — |
| GPT-5.4 | `gpt-5.4` | medium |
| GPT-5.4 wrong contexts | `gpt-5.4-wrongframe` | medium |
| GPT-5.6 | `gpt-5.6-high` | high |
| GPT-6-Astra | `gpt-6-astra_high` | high |

## Reading the ledger

`chronologic_scores_1.0.csv` has one row per scored model and 65 columns. The
ones that carry the reported numbers:

| Column | Meaning |
|---|---|
| `grp_cloze_score`, `grp_congen_score`, `grp_knowinf_score` | substantive score by question group, 0–1 |
| `grp_*_lo`, `grp_*_hi` | 95% bootstrap interval for each |
| `style_period_fidelity_e3` | date fidelity, 0–100 |
| `style_drift_years_e3` | signed mean error in years |
| `style_authenticity_fidelity` | human-authenticity score, 0–100 |
| `passfail`, `partial`, `pooled_count` | the two scoring channels and their pooled result |
| `n_passfail`, `n_partial` | questions routed to each channel (520 / 346) |

The three `grp_*_score` columns are fractions; the paper reports them as
percentages. Style scores are already on 0–100.

## What is not here

**Model generations and per-question judge verdicts.** These contain the
questions and their ground-truth answers inline, and the full answer set is
distributed under controlled access. They are available with the benchmark
itself, at
[huggingface.co/datasets/chronologic/Chronologic-EN-1.0](https://huggingface.co/datasets/chronologic/Chronologic-EN-1.0).

**Per-model likelihood JSONs.** `eval_results_full_*.json` records the score of
every answer option, so it likewise carries the answer set. Only the aggregate
leaderboard is published here.

## Reproducing

`free_gen_results_1.0.csv` is derived from the ledger: the three `grp_*_score`
columns scaled to percentages, plus the three style columns as-is. Table 1 comes
from `leaderboard_1.0.csv` unchanged.

To rescore a model yourself you need the frozen instruments — judge reliability,
Bradley-Terry anchors, and the calibration draws — which are committed under
`modelasjudge/`, and the benchmark from the link above. See the repository
README for the command lines.

# gpt41tuning — fine-tuning GPT-4.1 on period text

Produces the **GPT-4.1 finetune** row in the paper's free-generation table. The question it
answers is whether tuning a strong modern model on pre-1930 prose buys historical fidelity,
and if so, at what cost.

It appears to buy a great deal of style and cost some substance. The fine-tune reaches the
benchmark's highest human-authenticity score and near-perfect date
fidelity, while several of its substantive scores fall below the untuned model's. Note that the human-authenticity score might not really mean that this model sounds "more human": it might mean primarily that it sounds *unlike* other models, which could be a consequence of idiosyncratic tuning artefacts.

## Two versions

`v2/` is the one in the paper. The original run is at this directory's top level, and is
kept because it is referenced by earlier scoring artifacts.

Be careful which you compare against: in `../results/`, `scores_gpt-41-ft2__1.0.json` is
the paper's row and `scores_gpt-41-ft__1.0.json` is the superseded first run. See
[`../results/README.md`](../results/README.md).

## Pipeline

```bash
python gpt_41_tuning_data_prep.py       # v1 training data
python v2/export_text.py                # v2: extract passages from source volumes
python v2/elicit_metadata.py            # v2: attach period/genre metadata to each
```

Training itself runs through OpenAI's fine-tuning API — see `RunGPT41FineTuning.ipynb` for
the v1 run, and `v2/finetune_run_v2.json` for the v2 job record.

| File | Contents |
|---|---|
| `gpt41trainingdata.jsonl` | v1 training set |
| `v2/gpt41trainingdata_v2.jsonl`, `v2/gpt41validationdata_v2.jsonl` | v2 sets |
| `v2/corpus_audit_v2.md` | What went into the v2 corpus, and what was excluded |
| `gpt_41_tuning_data_prep.md` | Notes on the v1 data preparation |
| `OpenAIFineTuneGuide.md` | Vendor documentation, kept for reference |

## Scoring the result

A fine-tuned model is scored exactly like any other hosted model — the job id goes in as
the candidate:

```bash
python ../modelasjudge/run_pipeline.py \
    --candidate ft:gpt-4.1-2025-04-14:tedunderwood:chrono-v2:... \
    --candidate-label gpt-41-ft2 \
    --benchmark ../booksample/chronologic_en_1.0.jsonl --dry-run
```

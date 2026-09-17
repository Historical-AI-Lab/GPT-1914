# gpt41tuning — fine-tuning GPT-4.1 on period text

Produces the **GPT-4.1 finetune** row in the paper's free-generation table. The question it
answers is whether tuning a strong modern model on pre-1930 prose buys historical fidelity,
and if so, at what cost.

It appears to buy a great deal of style and cost some substance. The fine-tune reaches the
benchmark's highest human-authenticity score and near-perfect date fidelity, while several
of its substantive scores fall below the untuned model's. Note that the human-authenticity
score might not really mean that this model sounds "more human": it might mean primarily
that it sounds *unlike* other models, which could be a consequence of idiosyncratic tuning
artefacts.

## Training data

`gpt41_training_sample.jsonl` holds ten instances, drawn at random from the 340 used to
train the model in the paper. Each is an OpenAI chat-format record with three messages: a
system message setting the task, a user message giving `CONTEXT:` and `QUESTION:`, and an
assistant message with a period-appropriate answer drawn from the source.

The ten span sources from 1833 to 1923, and they show how varied the task is. Answers run
from four characters to eight hundred — an arithmetic result, a refusal
("insufficient information") where the stated context could not have known the answer, and
several multi-sentence passages continuing a work in its own style. The system prompt is
not fixed: it is written per record to describe that record's task.

The full training set is not published here. It was built from the same corpus the benchmark
draws on, but from different passages: **no benchmark question or ground-truth answer
appears in the training data**, which is what makes the fine-tune's scores meaningful rather
than a memorization result.

## Two fine-tunes, and which is which

Two models were trained. Only the second is in the paper, but both were scored, so both
appear in the results — and the labels are easy to confuse:

| Label | OpenAI job | Status |
|---|---|---|
| `gpt-41-ft2` | `ft:gpt-4.1-2025-04-14:tedunderwood:chrono-v2:ENKb6PVp:ckpt-step-340` | **The paper's "GPT-4.1 finetune" row** |
| `gpt-41-ft` | `ft:gpt-4.1-2025-04-14:tedunderwood::DNkT25IC` | An earlier run, superseded |

Both have rows in `../results/freegen/chronologic_scores_1.0.csv` and score files in
`../results/freegen/scores/`. If you are comparing against the published numbers, use
`scores_gpt-41-ft2__1.0.json`. See [`../results/README.md`](../results/README.md).

## Scoring the result

A fine-tuned model is scored exactly like any other hosted model — the job id goes in as the
candidate:

```bash
python ../modelasjudge/run_pipeline.py \
    --candidate ft:gpt-4.1-2025-04-14:tedunderwood:chrono-v2:ENKb6PVp:ckpt-step-340 \
    --candidate-label gpt-41-ft2 \
    --benchmark ../booksample/chronologic_en_1.0.jsonl --dry-run
```

Training itself ran through OpenAI's fine-tuning API. The data-preparation scripts and the
run notebooks are not published: they are specific to one vendor's API at one moment, and
the sample above is enough to show the shape of what the model saw.

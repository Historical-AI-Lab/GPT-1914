# bertclassify - training the style instruments

Two DeBERTa-v3-large models judge whether a generated answer *reads* like prose of the
period a question targets. This directory trains them. The scoring layer that turns their
raw output into 0–100 numbers lives in [`../stylejudge/`](../stylejudge).

| Instrument | Head | Asks |
|---|---|---|
| **Authenticity detector** | single-output regression | Is this authentic period prose, or an LLM imitation of it? |
| **Date predictor** | 36-way ordinal softmax over date bins | When was this written? |

Both are published, and download automatically when the style judge needs them:

- [`chronologic/chronologic-authenticity-deberta`](https://huggingface.co/chronologic/chronologic-authenticity-deberta)
- [`chronologic/chronologic-date-deberta`](https://huggingface.co/chronologic/chronologic-date-deberta)

You only need this directory to retrain them, or to run one directly over your own text.

## Why a trained judge

Neither a human reader nor a modern LLM is reliable at rating period style in isolation.
The authenticity detector is trained on a task that has a ground truth by construction:
given a real passage from a period book and an LLM's continuation of that same passage,
the two differ in exactly the way we care about. That makes the label free, and the
resulting classifier measures something the judge LLM cannot.

## Training data

`bert_data_prep.py` builds the pairs. For each book in the corpus sample it extracts
sentences with NLTK, trims the first and last 10% to avoid front and back matter, samples
100 chunks of at least 100 words, and asks a local model to continue each chunk in the same
genre and style. Authentic chunks land in `authentic/{barcode}.txt`, continuations in
`imitation/{barcode}_{model}.txt` — 167 files a side, roughly 22,800 lines each.

`filter_balance_clean.py` turns that into a training set:

- **Filtering** (training only, never at inference) drops lines under 5 words, LaTeX and
  formula-like content, index/TOC/bibliography patterns, URLs and markup. If more than 30%
  of a barcode's lines are dropped, the barcode is removed from **both** sides, so
  filtering cannot itself become a signal.
- **Normalization** (everywhere, including inference) straightens quotes, folds dashes to
  hyphens, collapses exotic whitespace.
- **Length balancing** to 5,000 examples a side across five bins — short, clause, medium,
  long, multi — because otherwise length alone separates the classes. Round-robin sampling
  by barcode stops any one book dominating.
- **Splitting** stratified by barcode, so no book appears on both sides of the
  train/validation split.

That length balancing matters more than it looks. An imitation is not distinguishable from
authentic prose by any single surface feature, but it is distinguishable by length
distribution if you let it be — and a classifier that learns length has learned nothing
about period style.

## Running

```bash
# Score a file with the authenticity detector
python run_deberta.py input.tsv --model-dir model_output/e2_v1/

# Train
sbatch train_deberta_A100.slurm          # authenticity
sbatch train_date_deberta_A100.slurm     # date predictor
```

`run_deberta.py` takes a TSV with a `text\tlabel` header, or plain text one item per line;
with labels it prints metrics, without them it writes predictions only. The SLURM scripts
target a single A100 and are the form the released models were trained in;
`smoke_test_A100.slurm` is a short job for checking the environment before committing to a
full run.

## Layout

| Path | Contents |
|---|---|
| `bert_data_prep.py`, `filter_balance_clean.py` | The data pipeline above |
| `train_deberta.py`, `train_date_deberta.py` | Training entry points |
| `*.slurm` | Cluster jobs for each training variant |
| `run_deberta.py` | Inference over a file |
| `free_gen_eval.py`, `free_gen_triage.py` | Scoring free-generated answers, and routing the ones too short or too factual for style to be informative |
| `score_pairs.py`, `bin_counter.py` | Pair scoring and date-bin census |
| `authentic/`, `imitation/` | Training pairs, 167 files each |
| `model_output/`, `large_tok196/`, `baseline/` | Trained checkpoints. Not committed — see the HuggingFace links above |
| `scores/` | Saved scores for a couple of early free-generation runs |

`model_output/e2_v1/` is the released authenticity detector. `baseline/` and
`large_tok196/` are earlier variants, kept because some scoring artifacts in
`../modelasjudge/scored_answers/` reference them; neither is on the current path.

The date predictor trains against a separate corpus of dated passages rather than the pair
data here. Point `CHRONOLOGIC_DATA` at that corpus — see
[`../stylejudge/README.md`](../stylejudge/README.md).

## Credentials

`bert_data_prep.py` calls a hosted model to generate continuations, and reads
`OpenRouterCredentials.txt` in this directory (`password: sk-or-v1-...`), or
`$OPENROUTER_API_KEY`. The file is in `.gitignore`.

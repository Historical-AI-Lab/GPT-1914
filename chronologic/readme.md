Chronologic-EN-1.0
==================

Ted Underwood, Ziliang Qiu, Sarah Griebel, Laura K. Nelson, Teddy Roland, Wenyi Shang, Matthew Wilkens

Chronologic-EN-1.0 is a benchmark that measures language models' ability to respond like
English-language writers located in specified social and historical contexts between 1831
and 1930.

For the paper, see URL.

The benchmark contains 866 questions drawn from 187 sources, listed in
[`booksample/primary_metadata.csv`](booksample/primary_metadata.csv). Every question comes
with a **metadata frame** naming a context — a date, a nationality, often a genre and an
author's background — and ground-truth answers are taken from period texts rather than
written by us.

**This repository does not contain the questions.** To reduce the risk of benchmark
contamination we publish a representative sample rather than the complete answer set. A
100-question sample is in
[`booksample/chronologic_en_1.0_sample.jsonl`](booksample/chronologic_en_1.0_sample.jsonl),
drawn by [`booksample/make_public_sample.py`](booksample/make_public_sample.py) and
including every question reproduced in the paper. The complete benchmark is available
under controlled access at
[huggingface.co/datasets/chronologic/Chronologic-EN-1.0](https://huggingface.co/datasets/chronologic/Chronologic-EN-1.0),
subject to an agreement not to redistribute it or use it for model training.

Installing
----------

Developed under Python 3.12.

```bash
git clone https://github.com/Historical-AI-Lab/Chronologic-EN
cd Chronologic-EN
python -m venv .venv && .venv/bin/pip install -r requirements.txt
```

`requirements.txt` describes the environment the published results were produced in. Two things
are deliberately not in it: `talkie`, the inference package for the Talkie-1930 models,
which is distributed separately — do not `pip install talkie`, which is an unrelated
project — and a CUDA build of PyTorch, if you intend to score open-weight models locally.

Scoring against a hosted model needs credentials. Create whichever you use:

```
bertclassify/OpenRouterCredentials.txt      password: sk-or-v1-...
evalcode/credentials.txt                    an OpenAI key
evalcode/TogetherAPIKey.txt                 a Together key
```

All three are in `.gitignore`.

Running the benchmark
---------------------

Once you retrieve the full benchmark file from the gated HF repo, a model can be scored two ways. They measure
different things and are not interchangeable: likelihood scoring asks whether a model
*prefers* an apt answer; free generation asks whether it can *produce* one.

### Likelihood scoring

Scores every candidate answer by the mean per-token log-probability the model assigns it,
then softmaxes across the options. Reports Brier score, top-1 accuracy, and a
chance-adjusted skill score. Needs an open-weight model whose token probabilities you can
read.

*Artifacts required:* the benchmark JSONL and a model. Nothing else — this path uses no
judges and no calibration.

```bash
python evalcode/benchmark_evaluation.py Qwen/Qwen2.5-7B-Instruct \
    booksample/chronologic_en_1.0.jsonl --full-eval
```

Add `--mcq` for the multiple-choice framing, `--device cpu|cuda|mps` to override
detection, `--quantize int4` to fit a large model on one GPU, or
`--api together|openrouter|openai` to score a hosted model. A report lands beside the
input JSONL. Published results for the seven models in the paper's Table 1 are in
[`results/likelihood/`](results/likelihood).

To exercise the path without the full benchmark, run it against the public sample:

```bash
python evalcode/benchmark_evaluation.py gpt2 \
    booksample/chronologic_en_1.0_sample.jsonl --mcq --device cpu
```

### Free generation

Asks the model to answer in its own words, then scores the answer on two independent axes.
**Substance** is judged by an LLM making comparisons against ground truth: a
single comparison for the 520 questions where judgment can be treated as a yes/no question, and Bradley-Terry partial
credit against multiple references for the 346 where aptness is a matter of degree.
**Style** is judged by two fine-tuned DeBERTa models, one predicting date of composition,
one distinguishing authentic period prose from LLM imitation.

*Artifacts required:* the benchmark JSONL; an OpenRouter key for the judge; the frozen
instruments committed under `modelasjudge/` — judge reliability (`llm_reliability/`), the
Bradley-Terry anchor fit and calibration draws (`bt_artifacts/`), and the beta-reliability
draws (`beta_reliability/`); and the two DeBERTa judges, which download automatically from
[chronologic-authenticity-deberta](https://huggingface.co/chronologic/chronologic-authenticity-deberta)
and [chronologic-date-deberta](https://huggingface.co/chronologic/chronologic-date-deberta)
on first use. The style judge also needs the reference corpus of scored period passages
that its percentiles are taken against; point `CHRONOLOGIC_DATA` at it.

```bash
python modelasjudge/run_pipeline.py \
    --candidate openai/gpt-5.4 --candidate-label gpt-5.4 \
    --candidate-effort medium \
    --benchmark booksample/chronologic_en_1.0.jsonl
```

Thirteen stages run in dependency order, each skipping if its output already exists, so an
interrupted run resumes by re-issuing the same command. **Use `--dry-run` first**: it
prints the stage table with an estimated judge-call count, which is the only warning you
get before spending money.

Results append to `modelasjudge/results/chronologic_scores.csv`. Published scores for all
thirteen models in the paper's Table 2 are in [`results/`](results), together with the
mapping from table row to file.

Repository guide
----------------

| Directory | Contents |
|---|---|
| [`results/`](results) | Published scores for every model in the paper, and which file backs which table row |
| [`booksample/`](booksample) | Source metadata, the public sample, and the seven pipelines that generated the questions |
| [`evalcode/`](evalcode) | Likelihood scoring, the leaderboard, and the self-rejection experiment |
| [`modelasjudge/`](modelasjudge) | Free-generation scoring: judges, Bradley-Terry calibration, human validation, error analysis |
| [`stylejudge/`](stylejudge) | The style instruments and the conformal layer that turns their raw output into 0–100 scores |
| [`bertclassify/`](bertclassify) | Training and inference for the two DeBERTa style judges |
| [`memorize/`](memorize) | The contamination test: proper-noun cloze over sixteen corpus books |
| [`gpt41tuning/`](gpt41tuning), [`qwentuning/`](qwentuning) | Fine-tuning for the two tuned models in the results tables |
| [`article/`](article) | The paper |

Question format
---------------

Each line of the benchmark JSONL is one question. Every field is documented in
[`DATA.md`](DATA.md); the essentials:

| Field | Meaning |
|---|---|
| `main_question` | what the model is asked |
| `metadata_frame` | the context it should answer from |
| `answer_strings` | ground truth first, then distractors |
| `answer_probabilities` | graded admissibility — 1.0 for ground truth, 0.0 for a plain distractor, intermediate where editors judged one partly defensible |
| `reasoning_type` | one of eight task types |
| `partial_credit` | 1 if scored by Bradley-Terry, 0 if pass/fail |

Tests
-----

```bash
pytest -m "not llm and not slow"
```

Citation
--------

```bibtex
@misc{chronologic2026,
  title  = {Chronologic-EN: Measuring the Ability to Represent the Past},
  author = {Underwood, Ted and Qiu, Ziliang and Griebel, Sarah and
            Nelson, Laura K. and Roland, Teddy and Shang, Wenyi and
            Wilkens, Matthew},
  year   = {2026}
}
```

License
-------

MIT, see [LICENSE](LICENSE). The benchmark data is distributed separately under its own
terms; see the HuggingFace dataset card.

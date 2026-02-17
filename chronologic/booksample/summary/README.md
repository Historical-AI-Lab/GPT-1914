summary
=======

This module finds paragraphs that contain their own summary sentence (a topic sentence or concluding synopsis). The extracted passage + synopsis pairs can later be used to frame summarization questions with ground-truth answers guaranteed to be in period style.

## Pipeline overview

```
IDI_sample_1875-25/*.txt
        |
        v
  find_synopses.py          Uses Qwen (local, via Ollama) to identify
        |                   candidate paragraphs containing a synopsis sentence.
        |                   Fast but noisy: produces false positives.
        v
  process_files/
    {barcode}_synopses.jsonl
        |
        v
  filter_synopses.py        Sends candidates to a fine-tuned GPT-4.1-mini
        |                   model for more stringent filtering.
        v
  process_files/
    {barcode}_potentialquestions.jsonl
```

Both scripts are incremental: they check what has already been processed and pick up where they left off.

## Prerequisites

- **Ollama** running locally (`ollama serve`) with `qwen2.5:7b-instruct` pulled
- **OpenAI credentials** in `summary/credentials.txt` (not committed to git):
  ```
  Line 1: OpenAI organization ID
  Line 2: OpenAI API key
  ```
- Python packages: `requests`, `openai`

## Usage

### Stage 1: Find candidates with Qwen

```bash
python summary/find_synopses.py
```

Each invocation processes the next 20 text files (alphabetically) from `IDI_sample_1875-25/`. For each file it extracts 10 random paragraphs (80-1000 words), sends them to Qwen, and writes results to `process_files/{barcode}_synopses.jsonl`.

Run it 5 times to cover all 99 files.

Options:

| Flag | Default | Description |
|------|---------|-------------|
| `--batch-size N` | 20 | Number of files to process per invocation |
| `--num-paragraphs N` | 10 | Paragraphs to sample per file |
| `--min-words N` | 80 | Minimum paragraph word count |
| `--max-words N` | 1000 | Maximum paragraph word count |
| `--model MODEL` | `qwen2.5:7b-instruct` | Ollama model to use |
| `--seed N` | (none) | Random seed for reproducible paragraph sampling |
| `--dry-run` | | List files that would be processed, then exit |

### Stage 2: Filter with fine-tuned GPT-4.1-mini

```bash
python summary/filter_synopses.py
```

Reads all `*_synopses.jsonl` files in `process_files/`, skips any that already have a matching `*_potentialquestions.jsonl`, and sends the Qwen "y" candidates to the fine-tuned model. Accepted passages are written to `process_files/{barcode}_potentialquestions.jsonl`.

Options:

| Flag | Default | Description |
|------|---------|-------------|
| `--credentials PATH` | `summary/credentials.txt` | Path to OpenAI credentials file |
| `--model MODEL` | `ft:gpt-4.1-mini-2025-04-14:tedunderwood::CbB93x2c` | Fine-tuned model ID |
| `--dry-run` | | List files that would be filtered, then exit |

## Progress tracking

- **Stage 1** tracks progress by the presence of `{barcode}_synopses.jsonl` files in `process_files/`. A `.tmp` suffix is used during processing, so interrupted files are automatically retried.
- **Stage 2** tracks progress by the presence of `{barcode}_potentialquestions.jsonl` files. A log of completed files is also kept in `filtered_files.txt`.

## Output format

Each line in `*_synopses.jsonl`:
```json
{"filename": "32044004506143", "passage": "...", "synopsis_present": "y", "synopsis": "..."}
```

Each line in `*_potentialquestions.jsonl`:
```json
{"filename": "32044004506143", "passage": "...", "synopsis": "The identified sentence."}
```

## Background

Early attempts to get a single local model to reliably identify synopsis sentences (see `oldsummary/`) showed that a two-stage approach works better: a quick, cheap local model to cast a wide net, followed by a more capable fine-tuned model to sift the results. The fine-tuned model (`ft:gpt-4.1-mini-2025-04-14:tedunderwood::CbB93x2c`) was trained on ~773 examples combining Qwen outputs, Gemini-generated synopses, and manual annotations from multiple human coders.

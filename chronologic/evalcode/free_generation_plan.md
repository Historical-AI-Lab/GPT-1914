# Plan: `benchmark_free_generation.py`

A script that asks models for free-text answers to benchmark questions. Separate from
`benchmark_evaluation.py` (which scores fixed answer options); this script generates
open-ended responses that a future evaluation script will score.

## Shared infrastructure

Imports from `benchmark_evaluation` rather than copying:

```python
from benchmark_evaluation import (
    load_model,
    is_openai_model,
    load_openai_credentials,
    _call_responses_with_retry,
    _generate_hf,
    OPENAI_MODEL_PREFIXES,
)
```

## System prompt

```python
SYSTEM_PROMPT = (
    "You will be asked to answer a question in a way that fits the beliefs and "
    "expository style of a specific historical context. If the context described "
    "would not contain enough information to answer the question, respond simply "
    "'insufficient information.' Otherwise, answer directly, in {length_spec}."
)
```

## Functions

### `extract_features(cleaned_answers)` → SimpleNamespace

Takes a list of stripped answer strings. Returns:
- `word_counts` — list of ints, one per answer
- `sentence_counts` — list of ints (sentences per answer, split on `[.!?]+`)
- `median_word_count` — float
- `median_sentence_count` — float
- `proportion_sentence_like` — fraction that end in `.!?` or have ≥ 8 words
- `newline_count` — total newlines across all answers

### `clamp_and_round(value, form)` → int

Rounds to a natural round number and clamps to a form-appropriate minimum:

| form | minimum | step |
|------|---------|------|
| `short_phrase` | 1 | 1 |
| `single_sentence` | 5 | 5 |
| `multi_sentence` | 10 | 5 |
| `phrase_or_sentence` | 3 | 5 |
| `verse` | 1 | 1 |

### `verbal_sentence_range(median_sent_count)` → str

| median | returns |
|--------|---------|
| ≤ 1.5 | `"one to two sentences"` |
| ≤ 2.5 | `"two to three sentences"` |
| ≤ 4.0 | `"three to five sentences"` |
| > 4.0 | `"a short paragraph"` |

### `make_length_spec(answer_strings, question_category)` → (int, str)

Implements the pseudocode from `free_generation_spec.md`. Returns `(upper, length_spec_string)`.

- `upper` → caller sets `max_new_tokens = upper * 2`
- `length_spec_string` → inserted into SYSTEM_PROMPT

Edge cases:
- Empty `answer_strings` → `(50, "about 20–50 words")`
- Verse: upper = max(4, computed upper)

### `build_prompts(question)` → (system_str, user_str, max_tokens)

```
system_str = SYSTEM_PROMPT.format(length_spec=length_spec)
user_str   = "CONTEXT: " + question["metadata_frame"]
           + "\nQUESTION: " + question["main_question"]
           + "\nANSWER: "
max_tokens = upper * 2
```

### `generate_answer_openai(question, model_id, client, reasoning_effort="none")` → str

Calls `_call_responses_with_retry` with system/user prompts, no JSON schema.
Returns `response.output_text.strip()`.

### `generate_answer_hf(question, model, tokenizer)` → str

Builds HF prompt as `system_str + "\n" + user_str` (no separate system channel).
Calls `_generate_hf(prompt, model, tokenizer, max_new_tokens=max_tokens)`.

### `inspect_length_specs(path_to_jsonl, n=20)`

Prints n randomly sampled questions showing answer_strings and resulting length specs.
Triggered by `--inspect` CLI flag.

### `show_sample_prompts(path_to_jsonl, n=5)`

Prints n randomly sampled questions showing the full formatted system prompt and user
prompt as they would be sent to the model. Triggered by `--show-prompts` CLI flag.
Lets the user verify formatting before running a full eval.

### `run_free_generation(model_id, path_to_jsonl, ...)` → str (output path)

Main orchestrator.

| param | default | notes |
|-------|---------|-------|
| `model_id` | required | HF path or OpenAI model ID |
| `path_to_jsonl` | required | benchmark question file |
| `output_path` | None | auto-named if None |
| `credentials_path` | None | OpenAI only |
| `reasoning_effort` | `"none"` | OpenAI only |
| `quantize` | None | HF only, `"int4"` / `"int8"` |
| `lora_adapter` | None | HF only |
| `trust_remote_code` | False | HF only |
| `num_questions` | None | limit for testing |

Logic:
1. Load questions from JSONL
2. Auto-name output: `free_gen_{model_sanitized}_{timestamp}.json`
3. If output file already exists, load it and skip already-answered question_numbers
4. Detect HF vs OpenAI via `is_openai_model(model_id)`
5. Loop over questions, generate answers, build result records
6. Write full output JSON after each answer (crash-safe)
7. Return output path

### Output JSON structure

```json
{
  "model": "gpt-4.1-2025-04-14",
  "answers": {
    "1042": {
      "metadata_frame": "...",
      "main_question": "...",
      "ground_truth": "...",
      "length_spec": "...",
      "answer": "..."
    }
  }
}
```

Keys are string question_numbers (from the `question_number` field of each question).

## CLI

```
python benchmark_free_generation.py [model_id] path_to_jsonl [options]

positional:
  model_id          HF model path or OpenAI model ID (omit with --inspect/--show-prompts)
  path_to_jsonl     benchmark question file

flags:
  --inspect         print length spec samples for 20 random questions and exit
  --show-prompts    print full formatted prompts for 5 random questions and exit
  --output PATH     override output file path
  --credentials PATH
  --reasoning-effort {none,minimal,low,medium,high}  (default: none)
  --quantize {int4,int8}
  --lora-adapter PATH
  --trust-remote-code
  -n / --num-questions N   limit to first N questions (for testing)
```

## What is NOT in this script

- Scoring / evaluation — separate future script
- Brier scores, skill scores, bootstrap CIs — those live in benchmark_evaluation.py
- vLLM path — not in spec; add later if needed

---

## CLI Reference

All commands are run from the `evalcode/` directory (or adjust paths accordingly).

### Inspection commands (no model needed)

```bash
# Show length-spec derivations for 20 random questions
python benchmark_free_generation.py --inspect ../booksample/all_benchmark_questions.jsonl

# Show full formatted prompts (system + user) for 5 random questions
python benchmark_free_generation.py --show-prompts ../booksample/all_benchmark_questions.jsonl

# Inspect a specific sub-corpus (e.g. poetry + knowledge only)
python benchmark_free_generation.py --inspect ../booksample/knowpoechar.jsonl
```

### OpenAI backend

```bash
# Run GPT-4.1 on the full benchmark
python benchmark_free_generation.py gpt-4.1-2025-04-14 ../booksample/all_benchmark_questions.jsonl

# Smoke-test with 5 questions (recommended before full run)
python benchmark_free_generation.py gpt-4.1-2025-04-14 ../booksample/all_benchmark_questions.jsonl -n 5

# Use a custom credentials file
python benchmark_free_generation.py gpt-4.1-2025-04-14 ../booksample/all_benchmark_questions.jsonl \
    --credentials credentials.txt

# Enable reasoning (o-series / extended thinking models)
python benchmark_free_generation.py o3-mini-2025-01-31 ../booksample/all_benchmark_questions.jsonl \
    --reasoning-effort medium

# Override output path
python benchmark_free_generation.py gpt-4.1-2025-04-14 ../booksample/all_benchmark_questions.jsonl \
    --output results/gpt41_run1.json
```

### HuggingFace backend

```bash
# Smoke-test local model (5 questions)
python benchmark_free_generation.py Qwen/Qwen2.5-7B-Instruct ../booksample/all_benchmark_questions.jsonl -n 5

# Full run with int4 quantization (saves VRAM on large models)
python benchmark_free_generation.py Qwen/Qwen2.5-7B-Instruct ../booksample/all_benchmark_questions.jsonl \
    --quantize int4

# Fine-tuned model with LoRA adapter
python benchmark_free_generation.py Qwen/Qwen2.5-7B-Instruct ../booksample/all_benchmark_questions.jsonl \
    --lora-adapter ../qwentuning/smoke_checkpoints/checkpoint-500

# Model requiring trust_remote_code (e.g. some community models)
python benchmark_free_generation.py some-org/some-model ../booksample/all_benchmark_questions.jsonl \
    --trust-remote-code
```

### Resume an interrupted run

```bash
# Re-run the same command — the script auto-detects the existing output file and skips
# already-answered question_numbers.  You must pass --output to point at the existing file:
python benchmark_free_generation.py gpt-4.1-2025-04-14 ../booksample/all_benchmark_questions.jsonl \
    --output free_gen_gpt-4.1-2025-04-14_20260318_143000.json
```

### All flags

| Flag | Default | Notes |
|------|---------|-------|
| `model_id` | required (positional) | HF path or OpenAI model ID; omit with `--inspect`/`--show-prompts` |
| `path_to_jsonl` | required (positional) | benchmark question file |
| `--inspect` | off | print length-spec samples for 20 random questions, then exit |
| `--show-prompts` | off | print full formatted prompts for 5 random questions, then exit |
| `--output PATH` | auto-named | override output JSON path |
| `--credentials PATH` | `evalcode/credentials.txt` | OpenAI credentials (org id + api key) |
| `--reasoning-effort` | `none` | OpenAI Responses API: `none`, `minimal`, `low`, `medium`, `high` |
| `--quantize` | off | HF only: `int4` or `int8` via torchao |
| `--lora-adapter PATH` | off | HF only: path to LoRA adapter checkpoint |
| `--trust-remote-code` | off | HF only: passed to `from_pretrained` |
| `-n` / `--num-questions N` | all | process only the first N questions |

---

## Validation Workflow

Use this sequence before any full benchmark run.

### Step 1 — Inspect length specs

```bash
cd evalcode
python benchmark_free_generation.py --inspect ../booksample/first100.jsonl
```

Expected output: 20 blocks like:

```
--- Question 3 (category: cloze_causal) ---
Answer strings:
  'because the water was rising'
  'the water was not rising'
  'because the fire had spread'
→ length_spec: 'a short phrase of about 3–8 words'  (upper=8, max_tokens=16)
```

Things to check:
- Short cloze answers → `short_phrase` form
- Multi-sentence knowledge answers → `multi_sentence` form
- Poetry answers with newlines → `verse` form
- `upper` values look proportionate (not 1 or 500)

### Step 2 — Preview formatted prompts

```bash
python benchmark_free_generation.py --show-prompts ../booksample/first100.jsonl
```

Expected output: 5 blocks showing `[SYSTEM PROMPT]`, `[USER PROMPT]`, and `[GROUND TRUTH]`.

Things to check:
- `CONTEXT:` line contains the metadata frame (period, genre, nationality, etc.)
- `QUESTION:` line is the actual question text
- `ANSWER:` appears at the end with nothing after it (the model completes from here)
- The length spec in the system prompt matches what `--inspect` showed for the same question category
- No stray newlines, escaped characters, or truncated metadata frames

### Step 3 — Smoke-test with 5 questions (OpenAI)

```bash
python benchmark_free_generation.py gpt-4.1-2025-04-14 ../booksample/first100.jsonl -n 5
```

Expected console output:

```
  [1/5] question_number=42 → 'The locomotive arrived at Paddington Station at hal...'
  [2/5] question_number=43 → 'because the steam pressure was insufficient'
  ...
Done. Results written to: /path/to/evalcode/free_gen_gpt-4.1-2025-04-14_20260318_143201.json
```

Things to check in the output JSON:
- All 5 question_numbers are present as keys in `answers`
- Each answer dict has `metadata_frame`, `main_question`, `ground_truth`, `length_spec`, `answer`
- `answer` is non-empty and not `"insufficient information"` for typical factual questions
- `length_spec` matches what `--inspect` would show for that category

### Step 4 — Smoke-test with 5 questions (HF)

```bash
python benchmark_free_generation.py Qwen/Qwen2.5-7B-Instruct ../booksample/first100.jsonl -n 5
```

Same checks as Step 3. Additionally verify:
- Model loads without CUDA/MPS errors
- Answers are in the target language (English)
- Answers do not include the prompt text (the model is not just echoing input)

### Step 5 — Check question_number field coverage

If you see `question_number=0` for every question, the source JSONL is missing `question_number`
fields and resume logic will not work correctly. Verify:

```bash
python -c "
import json
with open('../booksample/all_benchmark_questions.jsonl') as f:
    rows = [json.loads(l) for l in f if l.strip()]
missing = sum(1 for r in rows if 'question_number' not in r)
print(f'{missing}/{len(rows)} rows missing question_number')
"
```

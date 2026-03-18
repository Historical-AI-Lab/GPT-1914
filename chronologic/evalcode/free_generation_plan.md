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

# Plan: `benchmark_binary_eval.py`

## Context

The free-generation pipeline (`benchmark_free_generation.py`) produces a JSON file of model-generated answers. The next step is a **binary evaluation** script that presents an LLM with the ground-truth answer and the generated answer (in randomized order) and asks it to pick the better fit for the historical context. This measures how distinguishable free-generated answers are from ground truth.

Spec: `evalcode/binary_eval_spec.md`

## New file

`evalcode/benchmark_binary_eval.py`

## Design

### Input

A JSON file produced by `benchmark_free_generation.py` with structure:
```json
{
  "model": "...",
  "answers": {
    "42": {
      "metadata_frame": "...",
      "main_question": "...",
      "ground_truth": "...",
      "reasoning_type": "...",
      "length_spec": "...",
      "answer": "..."
    }
  }
}
```

### Triage (skip evaluation when answer ≈ ground truth)

Before posing each question to the evaluator LLM, check:

1. `answer.lower() == ground_truth.lower()` → "indistinguishable"
2. `answer.lower()` in `{"insufficient information", "i don't know", "abstain", "n/a"}` AND `reasoning_type == "abstention"` → "indistinguishable"
3. Both strings > 19 chars AND `difflib.SequenceMatcher(None, answer, ground_truth).ratio() > 0.94` → "indistinguishable"

### Evaluation prompt

```
SYSTEM: "You will be provided a historical context, a question, and two answers
to the question. Decide which answer to the question is a better fit for the
context, and then reply with only a single letter, A or B."

USER: "CONTEXT: {metadata_frame}\nQUESTION: {main_question}\nA: {option_a}\nB: {option_b}\nANSWER: "
```

- Randomly assigns ground truth to A or B for each question.
- Parses response for "A" or "B", maps back to "ground truth" or "generation".

### Backends

Reuses from `benchmark_evaluation.py`:
- `is_openai_model()` — detect OpenAI vs HF
- `load_openai_credentials()` — read creds
- `_call_responses_with_retry()` — OpenAI Responses API with retries, reasoning_effort, temperature
- `load_model()` — HF model loading
- `_generate_hf()` — HF text generation

For OpenAI: uses `_call_responses_with_retry` with `max_output_tokens=10` (only "A" or "B" needed). No JSON schema — just parse the letter.

For HF: prefixes system prompt + newline to user prompt, calls `_generate_hf` with `max_new_tokens=10`.

### Output

JSON file:
```json
{
  "model": "<evaluator_model_id>",
  "generation_model": "<model from input file>",
  "answers": {
    "42": {
      "ground_truth": "the correct answer",
      "generation": "what the model generated",
      "selected": "indistinguishable" | "ground truth" | "generation" | "unparseable"
    }
  }
}
```

### Crash-safety & resume

Same pattern as `benchmark_free_generation.py`:
- Writes JSON after every answer
- On startup, loads existing output file and skips already-evaluated question keys

### Key functions

1. `triage(answer, ground_truth, reasoning_type)` → `"indistinguishable"` or `None`
2. `build_binary_prompt(question_data)` → `(system_str, user_str, ground_truth_letter)`
3. `_parse_letter(response_text)` → `'A'`, `'B'`, or `None`
4. `evaluate_openai(question_data, model_id, client, reasoning_effort)` → `"ground truth"` | `"generation"` | `"unparseable"`
5. `evaluate_hf(question_data, model, tokenizer)` → same
6. `show_sample_prompts(input_json_path, n)` — inspection mode
7. `run_binary_eval(...)` — main orchestrator
8. `main()` — CLI via argparse

---

## CLI Reference

All commands are run from the `evalcode/` directory (or adjust paths accordingly).

### Positional arguments

| Argument | Notes |
|----------|-------|
| `evaluator_model_id` | HF model path or OpenAI model ID used as the judge. Omit with `--show-prompts`. |
| `input_json` | Path to free-generation JSON output from `benchmark_free_generation.py`. |

### Inspection commands (no model needed)

```bash
# Preview binary eval prompts for 5 random questions from the free-gen output
python benchmark_binary_eval.py --show-prompts ../booksample/free_gen_gpt-4.1-2025-04-14_20260318_085046.json
```

### OpenAI backend

```bash
# Smoke-test: evaluate 5 questions (recommended before full run)
python benchmark_binary_eval.py gpt-4.1-2025-04-14 \
    ../booksample/free_gen_gpt-4.1-2025-04-14_20260318_085046.json \
    -n 5

# Full run: use GPT-4.1 as evaluator
python benchmark_binary_eval.py gpt-4.1-2025-04-14 \
    ../booksample/free_gen_gpt-4.1-2025-04-14_20260318_085046.json

# Use a different evaluator (e.g. GPT-5 or a fine-tuned variant)
python benchmark_binary_eval.py gpt-5-2025-xx-xx \
    ../booksample/free_gen_gpt-4.1-2025-04-14_20260318_085046.json

# Custom credentials file
python benchmark_binary_eval.py gpt-4.1-2025-04-14 \
    ../booksample/free_gen_gpt-4.1-2025-04-14_20260318_085046.json \
    --credentials credentials.txt

# Enable reasoning for o-series models
python benchmark_binary_eval.py o3-mini-2025-01-31 \
    ../booksample/free_gen_gpt-4.1-2025-04-14_20260318_085046.json \
    --reasoning-effort low

# Override output path
python benchmark_binary_eval.py gpt-4.1-2025-04-14 \
    ../booksample/free_gen_gpt-4.1-2025-04-14_20260318_085046.json \
    --output binary_eval_pilot.json
```

### HuggingFace backend

```bash
# Smoke-test local model (5 questions)
python benchmark_binary_eval.py Qwen/Qwen2.5-7B-Instruct \
    ../booksample/free_gen_gpt-4.1-2025-04-14_20260318_085046.json \
    -n 5

# Full run with int4 quantization
python benchmark_binary_eval.py Qwen/Qwen2.5-7B-Instruct \
    ../booksample/free_gen_gpt-4.1-2025-04-14_20260318_085046.json \
    --quantize int4

# Model requiring trust_remote_code
python benchmark_binary_eval.py some-org/some-model \
    ../booksample/free_gen_gpt-4.1-2025-04-14_20260318_085046.json \
    --trust-remote-code
```

### Resume an interrupted run

```bash
# Re-run with --output pointing at the existing file; already-evaluated questions are skipped
python benchmark_binary_eval.py gpt-4.1-2025-04-14 \
    ../booksample/free_gen_gpt-4.1-2025-04-14_20260318_085046.json \
    --output binary_eval_gpt-4.1-2025-04-14_on_gpt-4.1-2025-04-14_20260318_XXXXXX.json
```

### All flags

| Flag | Default | Notes |
|------|---------|-------|
| `evaluator_model_id` | required (positional) | HF path or OpenAI model ID; omit with `--show-prompts` |
| `input_json` | required (positional) | free-generation JSON file |
| `--show-prompts` | off | print binary prompts for 5 random questions, then exit |
| `--output PATH` | auto-named | override output JSON path |
| `--credentials PATH` | `evalcode/credentials.txt` | OpenAI credentials (org id + api key) |
| `--reasoning-effort` | `none` | OpenAI Responses API: `none`, `minimal`, `low`, `medium`, `high` |
| `--quantize` | off | HF only: `int4` or `int8` via torchao |
| `--trust-remote-code` | off | HF only: passed to `from_pretrained` |
| `-n` / `--num-questions N` | all | process only the first N questions |

---

## Validation Workflow

Use this sequence before any full benchmark run.

### Step 1 — Inspect sample prompts

```bash
cd evalcode
python benchmark_binary_eval.py --show-prompts \
    ../booksample/free_gen_gpt-4.1-2025-04-14_20260318_085046.json
```

Expected output: 5 blocks, each showing either:

**Triaged question** (no LLM call will be made):
```
────────────────────────────────────────────────────────────────────────
Question 42  |  triaged: no — will be posed
[GROUND TRUTH]  'because the water was rising'
[GENERATION]    'because the water was rising'
→ result: indistinguishable
```

**Or a question that will be posed:**
```
────────────────────────────────────────────────────────────────────────
Question 288  |  triaged: no — will be posed
[SYSTEM PROMPT]
You will be provided a historical context, a question, and two answers to
the question. Decide which answer to the question is a better fit for the
context, and then reply with only a single letter, A or B.

[USER PROMPT]
CONTEXT: The following passage comes from Thucydides Mythistoricus...
QUESTION: ...
A: because his persons are still so near to the symbolic...
B: because he inherits from older ritual forms...
ANSWER:
[GROUND TRUTH LETTER: A]
```

Things to check:
- `CONTEXT:` line is the `metadata_frame` (title, date, author, nationality)
- `QUESTION:` is the actual question text (may be long for cloze questions — that is expected)
- `A:` and `B:` are the two answers in random order
- `ANSWER:` appears at the end with nothing after it
- `[GROUND TRUTH LETTER: A]` confirms which option is correct (not shown to the model)
- Triaged questions correctly show identical or near-identical answer pairs

### Step 2 — Check triage behavior on a real run

```bash
python benchmark_binary_eval.py gpt-4.1-2025-04-14 \
    ../booksample/free_gen_gpt-4.1-2025-04-14_20260318_085046.json \
    -n 20
```

Expected console output:
```
  [1/20] question=288 → generation (triaged: no)
  [2/20] question=483 → ground truth
  [3/20] question=242 → indistinguishable (triaged)
  ...
Done. 20 questions evaluated.
  indistinguishable: 3
  ground truth:      11
  generation:        6
Results written to: /path/to/evalcode/binary_eval_gpt-4.1-2025-04-14_on_gpt-4.1-2025-04-14_20260318_XXXXXX.json
```

Things to check:
- `(triaged)` annotations appear for exact/near-exact matches — these should not go to the API
- `indistinguishable` count in the summary matches the number of `(triaged)` lines
- No `unparseable` results (would indicate the evaluator is returning something other than A/B)
- Results are plausible: GPT-4.1 self-evaluation may favor "ground truth" more often than chance

### Step 3 — Verify output JSON structure

```bash
python -c "
import json
with open('../booksample/binary_eval_gpt-4.1-2025-04-14_on_gpt-4.1-2025-04-14_XXXXXX.json') as f:
    d = json.load(f)
print('evaluator model:', d['model'])
print('generation model:', d['generation_model'])
print('question count:', len(d['answers']))
sample_key = next(iter(d['answers']))
print('sample entry:', json.dumps(d['answers'][sample_key], indent=2))
"
```

Expected:
```json
{
  "ground_truth": "because his persons are still so near to the symbolic...",
  "generation": "because he inherits from older ritual forms...",
  "selected": "ground truth"
}
```

Things to check:
- `model` and `generation_model` are present and correct
- Every entry has exactly `ground_truth`, `generation`, `selected`
- `selected` is always one of: `"indistinguishable"`, `"ground truth"`, `"generation"`, `"unparseable"`
- No entry is missing or has `null` values

### Step 4 — Tally results manually

```bash
python -c "
import json
from collections import Counter
with open('../booksample/binary_eval_gpt-4.1-2025-04-14_on_gpt-4.1-2025-04-14_XXXXXX.json') as f:
    d = json.load(f)
counts = Counter(v['selected'] for v in d['answers'].values())
total = len(d['answers'])
print(f'Total questions: {total}')
for label, n in sorted(counts.items()):
    print(f'  {label}: {n} ({100*n/total:.1f}%)')
"
```

Interpretation guide:
- `indistinguishable` — model answered essentially identically to ground truth (best outcome)
- `ground truth` — evaluator preferred ground truth over generation (generation fell short)
- `generation` — evaluator preferred generation over ground truth (interesting; not necessarily bad — generated answer may be more coherent or more contextually apt)
- `unparseable` — evaluator did not return A or B; check for API errors or model instability

A rough baseline expectation for a capable but unevaluated model: ~20–40% indistinguishable + ground-truth-selected, ~50–70% ground-truth-selected, <5% unparseable. Exact rates will vary by question category.

### Step 5 — Test resume logic

Run with `-n 5` twice, pointing at the same output file the second time:

```bash
# First run
python benchmark_binary_eval.py gpt-4.1-2025-04-14 \
    ../booksample/free_gen_gpt-4.1-2025-04-14_20260318_085046.json \
    -n 5 --output binary_eval_resume_test.json

# Second run (should print "Resuming: 5 questions already evaluated." and do nothing)
python benchmark_binary_eval.py gpt-4.1-2025-04-14 \
    ../booksample/free_gen_gpt-4.1-2025-04-14_20260318_085046.json \
    -n 5 --output binary_eval_resume_test.json
```

Expected second-run output:
```
Resuming: 5 questions already evaluated.
  [1/5] question=... (skipped)
  ...
Done. 5 questions evaluated.
```

The output file should be byte-for-byte identical after the second run (no new API calls, no reordering).

### Step 6 — Check for unparseable responses

If unparseable results appear:

```bash
python -c "
import json
with open('../booksample/binary_eval_XXXX.json') as f:
    d = json.load(f)
bad = {k: v for k, v in d['answers'].items() if v['selected'] == 'unparseable'}
print(f'{len(bad)} unparseable results')
for k, v in list(bad.items())[:3]:
    print(f'  Q{k}: gt={v[\"ground_truth\"]!r:.40}  gen={v[\"generation\"]!r:.40}')
"
```

If unparseable rate is > 2%, investigate:
- Is the evaluator model returning long explanations before the letter?
- Is the API timing out (check `_call_responses_with_retry` logs)?
- Try `--reasoning-effort minimal` to suppress chain-of-thought that might bury the letter

---

## Interpreting Results

The binary eval metric measures **evaluator preference for ground truth** as a fraction of all evaluated questions (excluding indistinguishable). A complementary way to express the score:

```
distinguishable_rate = (ground_truth_count + generation_count) / total
ground_truth_preference = ground_truth_count / (ground_truth_count + generation_count)
```

- `distinguishable_rate` close to 0 → model generates near-identical answers to ground truth (strong performance)
- `ground_truth_preference` > 0.5 → evaluator prefers human answers when it can tell them apart (expected)
- `ground_truth_preference` near 0.5 → model generates answers that are as plausible as ground truth (strong performance on fluency/contextual fit)

These two metrics together give a richer picture than either alone.

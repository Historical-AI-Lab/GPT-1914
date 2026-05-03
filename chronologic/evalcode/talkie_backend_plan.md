# Plan: Add Talkie backend to `benchmark_evaluation.py`

## Context

ChronoLogic evaluates LMs on 1875–1924 historical reasoning. The existing
`benchmark_evaluation.py` (~2,900 lines) supports HF transformers, Together,
OpenRouter, OpenAI, and (legacy) vLLM via per-backend driver functions.

We now need to evaluate **Talkie** (a 13B custom decoder-only LM trained by
Radford/Levine/Duvenaud, specifically the `talkie-1930-13b-base` and
`talkie-1930-13b-it` checkpoints already cached in `$HF_HOME` on Delta) under
both `--full-eval` (per-token log-likelihood scoring of answer continuations,
yielding Brier + Platt-scaled probabilities) and `--mcq` (greedy generation +
letter parsing) modes. Goal: produce results directly comparable to existing
Qwen runs without forking the eval pipeline.

Talkie is **not** a HuggingFace model. It has no `transformers` dependency,
uses a `tiktoken` tokenizer with a custom regex pretokenizer, and its
`forward()` method (`talkie/src/talkie/model.py:184`) returns logits **only at
the last position** — `[B, V]`, not `[B, T, V]` — because it was designed for
sampling, not scoring. It also has no `model.generate()`; generation runs
through a custom `_stream_raw` loop (`generate.py:289`) that calls
`model.sample_batch()` once per token. The IT variant has 4 extra special
tokens (`<|end|>`, `<|user|>`, `<|assistant|>`, `<|system|>`, vocab size 65540
vs. 65536) and expects a chat-template prompt; the base variant takes raw
text.

The cleanest integration is a **thin adapter** in a new module that wraps
Talkie behind the same minimal interface the existing HF-mode helpers
(`_score_answer_ll_hf`, `_generate_hf`, `_input_device`) already require:

- `next(model.parameters()).device` works (Talkie is an `nn.Module` ✓)
- `model(input_ids).logits` returns `[B, T, V]` ← needs a 5-line patch
- `model.generate(input_ids, max_new_tokens=..., do_sample=False)` ← needs a wrapper
- `tokenizer(text, return_tensors="pt").input_ids` and
  `tokenizer.decode(ids, skip_special_tokens=True)` ← needs a tiktoken adapter

With those four contracts honored, `_score_answer_ll_hf` and `_generate_hf`
drive Talkie unchanged and we inherit Brier scoring, Platt calibration,
bootstrap CIs, abstention handling, MCQ skill score, and report writing for
free. No driver-function duplication.

## Design choices specific to Talkie (and likely failure modes)

### 1. Why patch `forward` to return all-position logits
The shipped `forward` ends with `F.linear(x[:, -1, :], ...)` which collapses
the time axis. For log-likelihood scoring we need logits at every position so
we can (after a left-shift by one) read off the conditional probability of
each answer token given its prefix. The patch is mechanical: drop the
`[:, -1, :]` slice. Single forward pass per (context+answer) pair, same cost
as one generation step.

**Failure mode:** `cos`/`sin` rotary buffers are precomputed for `max_seq_len=2048`
(`model.py:165`). Inputs longer than 2048 tokens will silently index into a
slice of length 2048 and produce wrong values — Python won't raise. We add an
explicit length check in the adapter and raise. ChronoLogic prompts include
long metadata frames, so this is a real risk to monitor.

### 2. Why wrap `generate` instead of using Talkie's `Talkie.generate`
The high-level `Talkie.generate` returns sampled text under
`temperature=0.7, top_p`, etc. Our MCQ path calls
`model.generate(input_ids, max_new_tokens=10, do_sample=False)` — greedy. We
need a small wrapper that does greedy argmax in a loop (no Gumbel noise, no
top-k/top-p) and returns token ids. ~15 lines: call our patched all-position
`forward`, take the last position, `argmax`, append, loop.

**Failure mode:** No KV cache. Each new token recomputes the full prefix.
Fine for `max_new_tokens=10` MCQ; would matter only for long generations.

### 3. Why the chat template is conditional on variant
Talkie-IT was instruction-tuned + DPO'd against a chat template
(`<|user|>{prompt}<|end|><|assistant|>`, see `chat.py:17`). Feeding it the raw
`ANSWER:`-style prompt will degrade behavior — the model expects a
`<|assistant|>` marker before its turn. Talkie-base has no such expectation
and uses raw text. The adapter detects style from `Talkie.spec.style` (`base`
or `it`); style is set in the model registry (`config.py:21`). The score
boundary stays the same: tokenize `context+answer` together; the context for
IT is `format_prompt(question_text)`, which already ends with `<|assistant|>`.

**Failure mode:** If the IT-formatted context ends right at a special-token
boundary, tokenizing `context + " A"` may merge the leading space with the
`<|assistant|>` token. We tokenize both separately *and* together and compare
prefix ids; if they diverge, log a warning and fall back to summing log-probs
starting at the last common-prefix position. (Same defensive trick
`_score_answer_ll_hf` implicitly relies on by tokenizing `context+answer` once
and using `context_ids.shape[1]` as the boundary.)

### 4. Why a tiktoken→HF tokenizer shim
`_score_answer_ll_hf` calls
`tokenizer(context_text, return_tensors="pt").input_ids`. tiktoken's API is
`tok.encode(text)` returning a `list[int]`. The shim is a tiny class that
exposes `__call__(text, return_tensors="pt")` returning an object with
`.input_ids` (a `torch.LongTensor [1, n]`), and
`.decode(ids, skip_special_tokens=True)` mapping back through
`tok.decode(ids.tolist())` with optional special-token stripping. ~30 lines.

**Failure mode:** `skip_special_tokens` semantics differ. tiktoken doesn't
have a built-in concept; we filter the IT extra-special ids
(`<|end|>`, `<|user|>`, `<|assistant|>`, `<|system|>`, plus `<|endoftext|>`)
by id before decoding.

### 5. Why pip-install rather than vendor
`pip install -e ../../talkie` into the existing `qlora-env` on Delta. Cleaner
than vendoring, and we'll get upstream fixes (notably any `forward` API
expansion if the Talkie authors ever add all-position logits). The eval-side
adapter is short enough that drift risk is low.

### 6. Resolving the model id (HF cache vs. local fine-tune dir)
Two accepted forms for the positional `model_id`:

- **Registered HF name** — one of `talkie-1930-13b-base`, `talkie-1930-13b-it`,
  `talkie-web-13b-base`. The adapter calls Talkie's `get_model_files(name)`
  (`config.py`), which resolves through `huggingface_hub`'s cache to local
  paths. Since `$HF_HOME` is already populated on Delta, no network is
  needed.
- **Local directory path** — any directory containing both `vocab.txt` and
  exactly one `*.ckpt` / `*.pt` weights file. Style (`base` vs `it`) is read
  from a small `talkie_style.txt` file in the directory (one word: `base` or
  `it`). **This is the path for your own fine-tunes:** when you fine-tune
  Talkie's architecture on a new dataset and dump the weights somewhere
  outside the HF cache, point the eval CLI at that directory and it loads
  via `load_checkpoint(path, device, target_vocab_size=...)` directly without
  going through `huggingface_hub`. Vocab size is chosen automatically
  (`IT_VOCAB_SIZE=65540` if style=`it`, else `BASE_VOCAB_SIZE=65536`).

  Expected layout for a fine-tune directory:
  ```
  /projects/bdfx/models/my-talkie-ft-v1/
    ├── vocab.txt              # copy from upstream Talkie repo
    ├── talkie_style.txt       # contains the literal word "base" or "it"
    └── final.ckpt             # or any single *.ckpt / *.pt file
  ```
  If you start from `talkie-1930-13b-it` you'll keep `style=it` (vocab 65540
  with chat tokens). If you fine-tune on raw period text starting from
  `talkie-1930-13b-base`, keep `style=base` (vocab 65536, no chat tokens).
  If your fine-tune *adds* new special tokens beyond the IT set, you'll need
  to extend `target_vocab_size` accordingly (revisit then).

Detection rule: if `model_id` exists as a directory on disk → local path
mode; else → registered-name mode (raise a clear error if neither matches).

## Files to be modified

1. **`evalcode/talkie_backend.py`** *(new)*
   - `is_talkie_model(model_id) -> bool` — True for the three registered
     names or any directory containing `vocab.txt`.
   - `_resolve_talkie_paths(model_id) -> (ckpt_path, vocab_path, style)` —
     handles both registered-name and local-dir branches.
   - `class _TalkieTokenizerAdapter` — wraps a tiktoken `Encoding`, exposing
     `__call__(text, return_tensors="pt")` and
     `decode(ids, skip_special_tokens=True)`. Also exposes
     `format_context(text)` (no-op for base, chat-wrap for IT).
   - `class _TalkieModelAdapter(nn.Module)` — owns the `TalkieModel`,
     overrides `forward(input_ids)` to return an object with `.logits`
     `[B, T, V]` (all positions), and provides
     `generate(input_ids, max_new_tokens, do_sample=False)` doing greedy
     argmax in a Python loop. Enforces 2048-token max with explicit raise.
   - `load_talkie_model(model_id, device=None, device_map=None) -> (model, tokenizer)`
     — orchestrates resolve → `build_tokenizer(vocab_path, style)` →
     `load_checkpoint(ckpt_path, device, target_vocab_size=...)` → wrap.
     Raises `NotImplementedError` if `device_map` is passed (Talkie doesn't
     support multi-GPU dispatch; 13B fits on one 40GB A100 in bf16).

2. **`evalcode/benchmark_evaluation.py`** *(modified)*
   - Inside `load_model` (line 376), insert near the top:
     ```python
     from talkie_backend import is_talkie_model, load_talkie_model
     if is_talkie_model(model_id):
         return load_talkie_model(model_id, device=device, device_map=device_map)
     ```
   - In `_score_answer_ll_hf` (line 321) and `_generate_hf` (line 206),
     route `context_text` through `tokenizer.format_context(context_text)`
     if the tokenizer exposes that hook (duck-typed, no isinstance branch).
     Trivial helper added at top of the file.
   - **Reused functions, no rewrites:** `_build_question_text` (line 117),
     `_build_mcq_prompt` (line 137), `_score_answer_ll_hf` (line 321),
     `_generate_hf` (line 206), `lls_to_probabilities` (line 529),
     `calculate_brier_score` (line 546), `bootstrap_evaluate` (line 765),
     `write_json_report` (line 871), `full_eval_hf` (line 1112),
     `mcq_eval_hf` (line 1285).

3. **`evalcode/talkie_eval_A100.slurm`** *(new)* — copy of
   `qwen25_eval_A100.slurm`, single GPU, with launch lines:
   ```
   python -u benchmark_evaluation.py \
       talkie-1930-13b-it \
       ../booksample/chronologic_en_0.1.jsonl \
       --full-eval \
       --verbose-report \
       --output-dir prob_results
   ```
   Plus a parallel `--mcq` variant writing to `mcq_results/`. Add
   `pip install -e ../../talkie` once after venv activation (idempotent).
   Set `export HF_HOME=/projects/bdfx/hf_cache` if not already in env.

4. **`evalcode/tests/test_benchmark_evaluation.py`** *(extended)*
   - Pure-unit: `TestIsTalkieModel`, `TestTalkieTokenizerAdapter`
     (encode/decode round-trip on simple ASCII).
   - `@pytest.mark.llm`: `TestLoadTalkieModel` loads
     `talkie-1930-13b-base` from cache, runs a 1-token generation and a
     1-token log-prob check.

## CLI

No new flags required. Existing CLI works:

```bash
# Talkie-base, full-eval (probabilistic Brier + Platt)
python benchmark_evaluation.py talkie-1930-13b-base \
    ../booksample/chronologic_en_0.1.jsonl \
    --full-eval --verbose-report --output-dir prob_results

# Talkie-IT, MCQ
python benchmark_evaluation.py talkie-1930-13b-it \
    ../booksample/chronologic_en_0.1.jsonl \
    --mcq --verbose-report --output-dir mcq_results

# Future: your own fine-tune in a directory
python benchmark_evaluation.py /projects/bdfx/models/my-talkie-ft-v1 \
    ../booksample/chronologic_en_0.1.jsonl --full-eval
```

`--device-map`, `--quantize`, `--lora-adapter`, `--trust-remote-code` are not
applicable to Talkie and will raise a clear error if combined with a Talkie
model id.

## Verification (run from `evalcode/` on Delta A100)

1. `pytest tests/ -m "not llm" -k Talkie` — pure-unit tests pass.
2. `pytest tests/ -m "llm" -k Talkie` — model loads, single forward +
   generate works.
3. **Smoke test (5-question default mode):**
   ```bash
   python benchmark_evaluation.py talkie-1930-13b-base \
       ../booksample/chronologic_en_0.1.jsonl
   ```
   Expect 5 questions printed with parsed answers. Failure here means the
   adapter or chat template is broken before any scoring math runs.
4. **Sanity-check log-likelihoods:** run `--full-eval` on a 50-question
   slice; confirm `lls_to_probabilities` outputs sum to 1 per row and
   ground-truth probability is on average above uniform (`1/k`). If GT is at
   or below uniform, the chat-template wrap or the `forward` patch is wrong.
5. **Compare base vs IT:** both should run; IT typically gives sharper
   distributions (lower entropy on confident questions).
6. **Reference comparison:** Brier scores should land in the same ballpark
   as Qwen2.5-7B (already in `prob_results/`). Wildly different magnitudes
   (>2× or <0.5×) suggest a tokenization-boundary or shift-by-one bug in the
   patched `forward`.
7. **Length guard:** craft a 2,100-token prompt and confirm the adapter
   raises rather than silently truncating.

## Out of scope

- Multi-GPU `device_map` support for Talkie (13B fits on one 40GB A100 in
  bf16; revisit if larger fine-tunes appear).
- KV-cache acceleration for `generate` (only matters if `max_new_tokens` >>
  10 — not the case for MCQ).
- Quantization (`--quantize int4|int8`); torchao integration for Talkie's
  custom layers would be a separate project.

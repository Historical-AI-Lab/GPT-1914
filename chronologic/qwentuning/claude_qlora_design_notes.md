# QLoRA Design Notes

## Now I have a complete picture. Here's what exists and what needs to be written:

**Already done:**
- `SFT_dataprep.py` — complete data preparation pipeline
- `sample_train.jsonl` — sample training data (~783KB, so already populated)
- `Qwen2.5-7B-Instruct/` — model weights already downloaded locally

**Needs to be written:**
1. `train_qlora.py` — main training script (auto-adapts CUDA 4-bit QLoRA vs MPS float16)
2. `smoke_test.sh` — one-command local smoke test
3. `qwen_qlora.slurm` — Delta HPC job (updated for RH9: CUDA 12.8, no mpirun, `srun`)

**Key design decisions:**
- **Quantization**: 4-bit bitsandbytes on CUDA only. MPS doesn't support it, so the smoke test uses float16 with standard LoRA — same code path, different precision.
- **Mixed data schemas**: Pre-process all examples to `{"text": "..."}` before building the Dataset (see `normalize_examples()` in `train_qlora.py`). See Bug #2 below for why the original `formatting_func` approach was abandoned.
- **Smoke test**: `--smoke` flag uses `sample_train.jsonl` (already exists), 90/10 split, `max_steps=100`, `batch_size=1`. Also runs a generation check at the end.
- **Delta slurm**: Single A100 (40GB is plenty for 4-bit 7B + LoRA). New RH9 module `cudatoolkit/25.3_12.8`, use `python train_qlora.py` directly (no mpirun, no MPI needed for single-GPU).

---

## Plan

### What was already done
- **`SFT_dataprep.py`** — complete; generates `sample_train.jsonl` (one book, `--test`) or `data/train.jsonl` + `data/val.jsonl` (full corpus)
- **`Qwen2.5-7B-Instruct/`** — model weights already on disk

### What was just written

**`train_qlora.py`** — the core training script
- Detects device and branches automatically:
  - **CUDA**: loads in 4-bit (`nf4` + double-quant), calls `prepare_model_for_kbit_training`, trains with `bf16=True`
  - **MPS**: loads in float16, moves to MPS, trains without quantisation (LoRA still active)
- `formatting_func` unifies both data schemas before tokenisation — `{"text": ...}` and `{"messages": ...}` both work
- `--smoke` flag: uses `sample_train.jsonl`, 100 examples, 100 steps, `max_seq_len=2048`, ends with a generation check
- All hyperparameters are CLI flags so they can be overridden from the slurm script

**`smoke_test.sh`** — one command to run locally:
```bash
bash smoke_test.sh
```
It generates `sample_train.jsonl` if missing (via `SFT_dataprep.py --test --no-type2`), then runs the smoke training. Watch for loss decrease over 100 steps and a coherent generation at the end.

**`qwen_qlora.slurm`** — updated for Delta RH9:
- Module: `cudatoolkit/25.3_12.8` (not the old 11.8)
- Uses `python train_qlora.py` directly (no mpirun — single GPU, and RH9 doesn't have mpirun anyway)
- 1× A100 40GB, 12-hour wall time, 8 CPUs for data loading
- PyTorch install uses `--index-url .../cu128` to match CUDA 12.8

### Execution order
1. `bash smoke_test.sh` — local smoke test on MPS
2. Once passing, run `python SFT_dataprep.py` to build the full training set
3. Transfer to Delta, create venv (see comment in slurm file), then `sbatch qwen_qlora.slurm`

### One caveat
The account name in the slurm script is `bdfx-delta-gpu` (copied from the old script). Verify this is still your active allocation on Delta before submitting.

---

## Bugs encountered during smoke testing

### Bug #1 — Model weights in Dropbox were cloud-only stubs (135 bytes each)

The `Qwen2.5-7B-Instruct/` directory was cloned into Dropbox purely as documentation (config files, tokenizer, README). The four `.safetensors` shards (~4 GB each) were Dropbox online-only placeholders and caused a `SafetensorError: header too large` on load.

**Fix**: The real weights were already in the HuggingFace cache at `~/.cache/huggingface/hub/models--Qwen--Qwen2.5-7B-Instruct/snapshots/a09a35458c702b33eeacc393d103063234e8bc28`. Updated `LOCAL_MODEL` in `train_qlora.py` to point there. Going forward, any machine running this code needs either the HF cache populated or a local path passed via `--model_path`.

### Bug #2 — TRL 0.29 `formatting_func` + mixed schemas causes `AttributeError`

The original design passed a `formatting_func` to `SFTTrainer` to convert Schema B `{"messages": [...]}` examples to text at training time. TRL 0.29 applies `formatting_func` and then immediately runs an `add_eos` step that checks `example["text"]`. For Schema B rows, `example["text"]` doesn't exist yet (it would have been set by the formatter), so this produced:

```
AttributeError: 'NoneType' object has no attribute 'endswith'
```

**Fix**: Moved schema normalisation earlier, into a `normalize_examples()` function called right after the tokenizer loads. All examples are converted to `{"text": "..."}` — with the Qwen chat template applied to Schema B — before the Dataset is constructed. `formatting_func` was removed from `SFTTrainer` entirely.

### Bug #3 — TRL 0.29 renamed `SFTConfig` parameter `max_seq_length` → `max_length`

Straightforward API change. Fixed by renaming the parameter in the `SFTConfig(...)` call.

### Bug #5 — MPS crashes during evaluation: `MPSGaph does not support tensor dims larger than INT_MAX`

Training ran successfully for 50 steps (mean token accuracy improved from 0.46 to 0.53), then crashed at the first evaluation step. TRL's `entropy_from_logits` applies `F.log_softmax` over the full logits tensor `[batch, seq_len, vocab_size]`. With Qwen's vocabulary of ~152K tokens, the product of those dimensions exceeds MPS's INT_MAX limit for tensor dimension sizes.

This is MPS-specific — CUDA does not have this constraint.

**Fix**: Set `eval_strategy="no"` when `device == "mps"`. Evaluation is not needed for smoke-test purposes; training loss and mean token accuracy logged every 10 steps are sufficient to confirm the pipeline is working. On CUDA (Delta), `eval_strategy="steps"` remains active.

### Bug #4 — `warmup_ratio` deprecated in TRL 0.29

`warmup_ratio` raises a deprecation warning and will be removed in v5.2. Replaced with `warmup_steps=50` (appropriate for a 100-step smoke run; scale up proportionally for full training).

---

## Should `SFT_dataprep.py` output normalised text instead of mixed schemas?

The question arises: since `normalize_examples()` in the training script has to apply the Qwen chat template to Schema B data anyway, should we just do that in `SFT_dataprep.py` and write everything out as `{"text": "..."}` from the start?

**Recommendation: keep the mixed schema output from `SFT_dataprep.py`.**

Rationale: the `messages` format is model-agnostic. The chat template is model-specific. Applying it in the training script is the right separation of concerns — if you later fine-tune a different base model (different chat template), you can reuse the same JSONL data files without re-running the expensive dataprep step. The normalisation in the training script is cheap (pure Python, runs in seconds before training starts).

If it ever becomes necessary to inspect pre-tokenised training examples directly (e.g. for debugging or data auditing), you can always run `normalize_examples()` standalone on the JSONL files.

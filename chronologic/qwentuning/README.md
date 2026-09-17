# qwentuning — QLoRA fine-tuning of Qwen2.5-7B on period text

Produces the **Qwen 7B ft (ckpt-3500)** row in the paper's likelihood table. It is the
cheap counterpart to the GPT-4.1 fine-tune: an open-weight model, tuned on period prose locally with QLoRA
rather than through a vendor API, which makes it the one tuned model that can also be
scored by likelihood.

The result gives clear evidence that period training helps. Untuned,
Qwen2.5-7B sits near the bottom of the likelihood table with 8.6% cloze accuracy; tuned on
period text it reaches 36.2% and third place overall, ahead of models ten times its size.

## Running

```bash
bash smoke_test.sh                  # short run to check the environment first
sbatch qwen_qlora.slurm             # full training
```

`train_qlora.py` is the entry point both use. `SFT_dataprep.py` builds the training file;
`sample_train.jsonl` is a small excerpt for checking the format.

Training used 4-bit quantization with LoRA adapters, which is what lets a 7B model tune on
a single GPU. The released checkpoint is step 3500 — the label `ckpt-3500` in the results
tables refers to it.

| File | Contents |
|---|---|
| `train_qlora.py` | Training entry point |
| `SFT_dataprep.py` | Builds the instruction-tuning file from period text |
| `qwen_qlora.slurm`, `gpt2_774M_A100x8.slurm` | Cluster jobs |
| `smoke_test.sh` | Short sanity run |
| `RUNBOOK.md` | Operating notes for the cluster |
| `DATAPREP.md`, `DATAPREP_REVISION.md`, `DATA.md` | Data-preparation decisions |
| `claude_qlora_design_notes.md`, `qlora_learning_notes.md` | Design and background reading |
| `data/`, `smoke_checkpoints/`, `qlora-env/` | Training data, checkpoints, virtualenv. Not committed |

The remaining `.md` files (`LORA.md`, `PEFT.md`, `Bitsandbytes.md`, `AccelerateCLI.md` and
similar) are vendor documentation saved during development, not project docs.

## Scoring the result

A local checkpoint is scored by path, with the adapter applied:

```bash
python ../evalcode/benchmark_evaluation.py Qwen/Qwen2.5-7B-Instruct \
    ../booksample/chronologic_en_1.0.jsonl --full-eval \
    --lora-adapter /path/to/checkpoint-3500
```

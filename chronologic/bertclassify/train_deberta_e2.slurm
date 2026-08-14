#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --partition=gpuA100x4
#SBATCH --account=bdfx-delta-gpu
#SBATCH --time=08:00:00
#SBATCH --job-name=deberta-e2
#SBATCH --error=deberta-e2-%j.err
#SBATCH --output=deberta-e2-%j.out
#SBATCH --gpus-per-node=1
#SBATCH --gpu-bind=closest
#SBATCH --mem=40g
#SBATCH --constraint="scratch"

# ---------------------------------------------------------------------------
# Phase E2 authenticity detector, per stylejudge/phase-e2-plan.md.
#
# Copied from train_deberta_A100.slurm (same deberta-env, same module load) —
# changes from that baseline run:
#   - --model-name microsoft/deberta-v3-large (spec: "last time we used
#     DeBERTa-lg"). Verified real precedent, not just the spec's recollection:
#     bertclassify/large_tok196/ is an actual fine-tuned deberta-v3-large
#     checkpoint (config.json: hidden_size 1024, 24 layers — matches -large,
#     not -base's 768/12) from a prior (undocumented, no surviving slurm/log)
#     training run for the modelasjudge/ discriminative judge. It was trained
#     at --max-length 196 for that task's shorter texts; this run uses 256,
#     independently justified by the token-length census below, since E2's
#     matched export has a longer tail (D3's 4-6-sentence rows).
#   - --max-length 256, not 128 — the matched export's p99 word count runs
#     well past 128 sub-word tokens; the token-length census in
#     phase-e2-runbook.md §2 measured p99 = 203 tokens on this exact data with
#     the deberta-v3 tokenizer, confirming 256 covers it with headroom.
#   - HF_HOME / HF_HUB_OFFLINE=1 added (missing from the -base template, which
#     got away without it because deberta-v3-base was presumably already
#     cached from an earlier interactive session). Delta compute nodes have no
#     outbound network (reference_delta_hpc memory note, confirmed against the
#     three working Talkie slurm scripts, which all set this). Unlike -base,
#     deberta-v3-large is NOT known to be cached under this HF_HOME yet —
#     pre-download it and its tokenizer from a LOGIN node before submitting:
#         module load cudatoolkit/25.3_12.8; source deberta-env/bin/activate
#         export HF_HOME=/work/nvme/bdfx/.cache/huggingface
#         python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; \
#             AutoTokenizer.from_pretrained('microsoft/deberta-v3-large'); \
#             AutoModelForSequenceClassification.from_pretrained('microsoft/deberta-v3-large', num_labels=1)"
#     Without this the job will hang or fail trying to reach huggingface.co
#     from a network-less compute node.
#
# --train-file / --val-file point at stylejudge/authenticity_detector.py
# `prepare`'s output, not this directory's train.tsv/val.tsv — absolute paths,
# since train_deberta.py resolves relative paths against its own SCRIPT_DIR
# (bertclassify/), not the submit directory.
#
# Host memory: 40g is UNTOUCHED from the -base template and is NOT verified
# by precedent for -large — no slurm script or log for the large_tok196 run
# survives, so there is no confirmed number for it. Reasoning for leaving it
# at 40g anyway: the 40g->128g Talkie lesson (NOTES.md §16) was specifically
# about a 13B model whose checkpoint alone is ~26 GB; deberta-v3-large's
# checkpoint is 1.74 GB (the actual file size of large_tok196/model.safetensors),
# two orders of magnitude smaller, and the failure mode that note describes
# (OOM at checkpoint load, host RAM not GPU) is not plausible at this scale.
# Reported effectively as ~400M-parameter-scale in reference_delta_hpc memory
# notes ("DeBERTa is ~400M... Copying --mem=40g... gets the job OOM-killed" —
# that OOM is Talkie's, not DeBERTa's; DeBERTa itself is the example of what
# fits fine at 40g). If this run OOMs anyway, it is far more likely to be GPU
# VRAM at batch-size 32 / max-length 256 than host RAM — the fix there is
# --batch-size 16 with --effective-batch-size 32 (grad accum 2), not --mem.
#
# Walltime bumped 4h -> 8h against the A100 baseline: ~46,600 train rows on
# deberta-v3-large at max-length 256 is a larger job on every axis than the
# -base/128-token runs this template was tuned for, and there is no timing
# precedent for -large specifically. Revise once an actual run reports what
# it needed (phase-e2-runbook.md records that once known).
#
# CRITICAL: --adam-epsilon 1e-6 is not optional. The local smoke test
# (phase-e2-runbook.md §3) reproduced train_deberta.py silently producing NaN
# parameters after the *first* optimizer step at PyTorch's AdamW default of
# eps=1e-8, for this exact DeBERTa-v2 architecture — independent of
# --max-length, --learning-rate, and device; isolated to Adam's own update
# math (SGD does not reproduce it). The run still "completes" and saves a
# checkpoint; only the metrics (stuck at exactly chance) give it away. Fixed
# in train_deberta.py itself (new --adam-epsilon flag, default changed
# 1e-8 -> 1e-6, HuggingFace's own documented value for DeBERTa), passed
# explicitly below anyway so this job doesn't silently depend on that default
# surviving a future edit. **Make sure Delta's copy of train_deberta.py has
# this fix** (sync/pull it) before submitting — the fix lives in the script,
# not in this slurm file, so an out-of-date copy on Delta will reproduce the
# exact same NaN run this precedent check exists to prevent.
# ---------------------------------------------------------------------------

echo "Job starting on $(hostname)"
date

module reset
module load cudatoolkit/25.3_12.8
module list

export HF_HOME=/work/nvme/bdfx/.cache/huggingface
export HF_HUB_OFFLINE=1

source deberta-env/bin/activate

SCRIPT_DIR="$SLURM_SUBMIT_DIR"
cd "$SCRIPT_DIR"

E2_DIR="$SCRIPT_DIR"

python -u train_deberta.py \
    --model-name microsoft/deberta-v3-large \
    --train-file "$E2_DIR/train.tsv" \
    --val-file "$E2_DIR/val.tsv" \
    --epochs 3 \
    --batch-size 32 \
    --effective-batch-size 32 \
    --learning-rate 2e-5 \
    --weight-decay 0.01 \
    --adam-epsilon 1e-6 \
    --warmup-ratio 0.1 \
    --max-length 256 \
    --device cuda \
    --run-name e2_v1

echo "Job completed"
date

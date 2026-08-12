#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --partition=gpuA100x4
#SBATCH --account=bdfx-delta-gpu
#SBATCH --time=08:00:00
#SBATCH --job-name=talkie-negatives
#SBATCH --error=talkie-negatives-%j.err
#SBATCH --output=talkie-negatives-%j.out
#SBATCH --gpus-per-node=1
#SBATCH --gpu-bind=closest
#SBATCH --mem=40g
#SBATCH --constraint="scratch"

# ---------------------------------------------------------------------------
# Phase D2 §4.3 — 2,000 negatives from talkie-1930-13b-base.
#
# talkie-eval-env setup (one-time, run interactively before submitting):
#
#   module reset
#   module load cudatoolkit/25.3_12.8
#   python -m venv talkie-eval-env
#   source talkie-eval-env/bin/activate
#   pip install torch --index-url https://download.pytorch.org/whl/cu128
#   pip install huggingface_hub tiktoken nltk
#   pip install -e /path/to/talkie          # the talkie package
#   python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
#
# Upload before submitting:
#   talkie_input.jsonl   (built locally by `generate_talkie_negatives.py stage`)
#   generate_talkie_negatives.py, negative_qc.py, normalize.py,
#   passage_filters.py, measure_length_distribution.py, sample_passages.py,
#   length_distribution.json
#
# The model needs >=28 GB VRAM in bf16, so one A100 is the minimum. The first
# run downloads a ~26 GB checkpoint into HF_HOME -- do that in an interactive
# job rather than burning batch time on it.
#
# Recommended sequence:
#   1. interactive 20-row check, eyeballed for repetition loops and verbatim
#      reproduction of the source (the base-model failure modes)
#   2. this batch job for the remaining 2,000
# ---------------------------------------------------------------------------

echo "Job starting on $(hostname)"
date
nvidia-smi

module reset
module load cudatoolkit/25.3_12.8
module list

export HF_HOME=/work/nvme/bdfx/.cache/huggingface

SCRIPT_DIR="$SLURM_SUBMIT_DIR"
cd "$SCRIPT_DIR"

source "$SLURM_SUBMIT_DIR/talkie-eval-env/bin/activate"

python generate_talkie_negatives.py run \
    --input talkie_input.jsonl \
    --model talkie-1930-13b-base \
    --temperature 0.9 \
    --top-p 0.95 \
    --max-new-tokens 160 \
    --device cuda \
    --out talkie_negatives.jsonl

echo "Job completed"
date

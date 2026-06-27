#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --partition=gpuA100x4
#SBATCH --account=bdfx-delta-gpu
#SBATCH --time=08:00:00
#SBATCH --job-name=talkie-eval
#SBATCH --error=talkie-eval-%j.err
#SBATCH --output=talkie-eval-%j.out
#SBATCH --gpus-per-node=1
#SBATCH --gpu-bind=closest
#SBATCH --mem=128g
#SBATCH --constraint="scratch"

echo "Job starting on $(hostname)"
date

module reset
module load cudatoolkit/25.3_12.8
module list

source "$SLURM_SUBMIT_DIR/talkie-eval-env/bin/activate"

export HF_HOME=/work/nvme/bdfx/.cache/huggingface
export HF_HUB_OFFLINE=1

SCRIPT_DIR="$SLURM_SUBMIT_DIR"
cd "$SCRIPT_DIR"

# --- full-eval (probabilistic Brier + Platt scaling) ---
# Run both base and IT variants; results land in prob_results/.

python -u benchmark_evaluation.py \
    talkie-1930-13b-base \
    ../booksample/chronologic_en_0.4.jsonl \
    --full-eval \
    --verbose-report \
    --output-dir prob_04

python -u benchmark_evaluation.py \
    talkie-1930-13b-it \
    ../booksample/chronologic_en_0.4.jsonl \
    --full-eval \
    --verbose-report \
    --output-dir prob_04

echo "full-eval done"
date

# --- MCQ eval ---
# Uncomment to run MCQ instead of (or in addition to) full-eval.
# Results land in mcq_results/.

# python -u benchmark_evaluation.py \
#     talkie-1930-13b-base \
#     ../booksample/chronologic_en_0.2.jsonl \
#     --mcq \
#     --verbose-report \
#     --output-dir mcq_results
#
# python -u benchmark_evaluation.py \
#     talkie-1930-13b-it \
#     ../booksample/chronologic_en_0.2.jsonl \
#     --mcq \
#     --verbose-report \
#     --output-dir mcq_results

# --- Fine-tune eval (future use) ---
# To evaluate your own fine-tuned model stored under /projects/bdfx/models/:
#
#   python -u benchmark_evaluation.py \
#       /projects/bdfx/models/my-talkie-ft-v1 \
#       ../booksample/chronologic_en_0.2.jsonl \
#       --full-eval \
#       --verbose-report \
#       --output-dir prob_results
#
# The directory must contain:
#   vocab.txt          (copy from upstream talkie-lm HF repo)
#   talkie_style.txt   (one word: 'base' or 'it')
#   final.ckpt         (or any single *.ckpt / *.pt weights file)

echo "Job completed"
date

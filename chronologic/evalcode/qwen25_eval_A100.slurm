#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --partition=gpuA100x4
#SBATCH --account=bdfx-delta-gpu
#SBATCH --time=08:00:00
#SBATCH --job-name=qwen25-eval
#SBATCH --error=qwen25-eval-%j.err
#SBATCH --output=qwen25-eval-%j.out
#SBATCH --gpus-per-node=1
#SBATCH --gpu-bind=closest
#SBATCH --mem=64g
#SBATCH --constraint="scratch"

echo "Job starting on $(hostname)"
date

module reset
module load cudatoolkit/25.3_12.8
module list

# Activate the Python environment that has torch + transformers
# (same qlora-env used for Qwen training; adjust path if different)

source ../qwentuning/qlora-env/bin/activate

SCRIPT_DIR="$SLURM_SUBMIT_DIR"
cd "$SCRIPT_DIR"

python benchmark_evaluation.py \
    Qwen/Qwen2.5-7B-Instruct \
    ../booksample/chronologic_en_0.1.jsonl \
    --full-eval \
    --verbose-report

echo "Job completed"
date

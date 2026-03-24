#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --partition=gpuA100x4
#SBATCH --account=bdfx-delta-gpu
#SBATCH --time=08:00:00
#SBATCH --job-name=qwen25-72b-eval
#SBATCH --error=qwen25-72b-eval-%j.err
#SBATCH --output=qwen25-72b-eval-%j.out
#SBATCH --gpus-per-node=4
#SBATCH --mem=128g
#SBATCH --constraint="scratch"

echo "Job starting on $(hostname)"
date

module reset
module load cudatoolkit/25.3_12.8
module list

source ../qwentuning/qlora-env/bin/activate

SCRIPT_DIR="$SLURM_SUBMIT_DIR"
cd "$SCRIPT_DIR"

python -u benchmark_evaluation.py \
    /projects/bdfx/models/Qwen2.5-72B-Instruct \
    ../booksample/chronologic_en_0.1.jsonl \
    --device-map auto \
    --full-eval \
    --verbose-report \
    --output-dir prob_results

echo "Job completed"
date

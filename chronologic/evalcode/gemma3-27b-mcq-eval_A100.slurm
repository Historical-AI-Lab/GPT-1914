#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --partition=gpuA100x4
#SBATCH --account=bdfx-delta-gpu
#SBATCH --time=08:00:00
#SBATCH --job-name=gemma3-27b-mcq
#SBATCH --error=gemma3-27b-mcq-%j.err
#SBATCH --output=gemma3-27b-mcq-%j.out
#SBATCH --gpus-per-node=2
#SBATCH --mem=64g
#SBATCH --constraint="scratch"

echo "Job starting on $(hostname)"
date

module reset
module load cudatoolkit/25.3_12.8
module list

source ../qwentuning/qlora-env/bin/activate

export HF_HOME=/work/nvme/bdfx/.cache/huggingface
export HF_HUB_OFFLINE=1

SCRIPT_DIR="$SLURM_SUBMIT_DIR"
cd "$SCRIPT_DIR"

python -u benchmark_evaluation.py \
    /projects/bdfx/models/gemma-3-27b-pt \
    ../booksample/chronologic_en_0.2.jsonl \
    --device-map auto \
    --mcq \
    --verbose-report \
    --output-dir mcq_02

echo "Job completed"
date

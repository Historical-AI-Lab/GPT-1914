#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --partition=gpuA100x4
#SBATCH --account=bdfx-delta-gpu
#SBATCH --time=08:00:00
#SBATCH --job-name=qwen25-qlora-freegen
#SBATCH --error=qwen25-qlora-freegen-%j.err
#SBATCH --output=qwen25-qlora-freegen-%j.out
#SBATCH --gpus-per-node=1
#SBATCH --gpu-bind=closest
#SBATCH --mem=64g
#SBATCH --constraint="scratch"

echo "Job starting on $(hostname)"
date

module reset
module load cudatoolkit/25.3_12.8
module list

source "$SLURM_SUBMIT_DIR/../qwentuning/qlora-env/bin/activate"

pip install -q peft

export HF_HOME=/work/nvme/bdfx/.cache/huggingface
export HF_HUB_OFFLINE=1

SCRIPT_DIR="$SLURM_SUBMIT_DIR"
cd "$SCRIPT_DIR"

python -u free_generation.py \
    Qwen/Qwen2.5-7B-Instruct \
    ../booksample/chronologic_en_0.4.jsonl \
    --lora-adapter ../qwentuning/checkpoints/run1/checkpoint-3500

echo "Job completed"
date

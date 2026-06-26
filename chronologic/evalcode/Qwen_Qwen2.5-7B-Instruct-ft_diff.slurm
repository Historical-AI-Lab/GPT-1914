#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --partition=gpuA100x4
#SBATCH --account=bdfx-delta-gpu
#SBATCH --time=02:00:00
#SBATCH --job-name=Qwen_Qwen2.5-7B-Instruct-ft-diff
#SBATCH --error=Qwen_Qwen2.5-7B-Instruct-ft-diff-%j.err
#SBATCH --output=Qwen_Qwen2.5-7B-Instruct-ft-diff-%j.out
#SBATCH --gpus-per-node=1
#SBATCH --mem=64g
#SBATCH --constraint="scratch"

echo "Job starting on $(hostname)"
date

module reset
module load cudatoolkit/25.3_12.8
module list

source ../qwentuning/qlora-env/bin/activate
pip install -q peft

SCRIPT_DIR="$SLURM_SUBMIT_DIR"
cd "$SCRIPT_DIR"

export HF_HOME=/work/nvme/bdfx/.cache/huggingface
export TRANSFORMERS_CACHE=/work/nvme/bdfx/.cache/huggingface/hub
export HF_HUB_OFFLINE=1

python -u benchmark_evaluation.py \
    Qwen/Qwen2.5-7B-Instruct \
    diff_0.2_to_0.4/chronologic_diff_0.2_to_0.4.jsonl \
    --lora-adapter ../qwentuning/checkpoints/run1/checkpoint-3500 \
    --full-eval \
    --output-dir prob_04_diff_ft

echo "Job completed"
date

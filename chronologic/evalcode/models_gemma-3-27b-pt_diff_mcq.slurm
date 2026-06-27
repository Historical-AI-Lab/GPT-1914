#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --partition=gpuA100x4
#SBATCH --account=bdfx-delta-gpu
#SBATCH --time=02:00:00
#SBATCH --job-name=_projects_bdfx_models_gemma-3--diff
#SBATCH --error=_projects_bdfx_models_gemma-3--diff-%j.err
#SBATCH --output=_projects_bdfx_models_gemma-3--diff-%j.out
#SBATCH --gpus-per-node=2
#SBATCH --mem=64g
#SBATCH --constraint="scratch"

echo "Job starting on $(hostname)"
date

module reset
module load cudatoolkit/25.3_12.8
module list

source ../qwentuning/qlora-env/bin/activate

SCRIPT_DIR="$SLURM_SUBMIT_DIR"
cd "$SCRIPT_DIR"

export HF_HOME=/work/nvme/bdfx/.cache/huggingface
export TRANSFORMERS_CACHE=/work/nvme/bdfx/.cache/huggingface/hub
export HF_HUB_OFFLINE=1

python -u benchmark_evaluation.py \
    /projects/bdfx/models/gemma-3-27b-pt \
    diff_0.2_to_0.4/chronologic_diff_0.2_to_0.4.jsonl \
    --device-map auto \
    --mcq \
    --output-dir mcq_04_diff

echo "Job completed"
date

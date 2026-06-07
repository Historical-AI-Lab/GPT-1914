#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --partition=gpuA100x4
#SBATCH --account=bdfx-delta-gpu
#SBATCH --time=08:00:00
#SBATCH --job-name=talkie-freegen
#SBATCH --error=talkie-freegen-%j.err
#SBATCH --output=talkie-freegen-%j.out
#SBATCH --gpus-per-node=1
#SBATCH --gpu-bind=closest
#SBATCH --mem=128g
#SBATCH --constraint="scratch"

echo "Job starting on $(hostname)"
date

module reset
module load cudatoolkit/25.3_12.8
module list

# talkie-eval-env lives in evalcode/; reference it relative to this script's dir
source "$SLURM_SUBMIT_DIR/../evalcode/talkie-eval-env/bin/activate"

export HF_HOME=/work/nvme/bdfx/.cache/huggingface
export HF_HUB_OFFLINE=1

SCRIPT_DIR="$SLURM_SUBMIT_DIR"
cd "$SCRIPT_DIR"

# --- Free-generation eval ---
# Run both base and IT variants; results land in generated_answers/.

python -u free_generation.py \
    talkie-1930-13b-base \
    ../booksample/chronologic_en_0.4.jsonl

python -u free_generation.py \
    talkie-1930-13b-it \
    ../booksample/chronologic_en_0.4.jsonl

echo "Job completed"
date

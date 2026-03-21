#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --partition=gpuA100x4
#SBATCH --account=bdfx-delta-gpu
#SBATCH --time=04:00:00
#SBATCH --job-name=deberta-train
#SBATCH --error=deberta-train-%j.err
#SBATCH --output=deberta-train-%j.out
#SBATCH --gpus-per-node=1
#SBATCH --gpu-bind=closest
#SBATCH --mem=40g
#SBATCH --constraint="scratch"

# ---------------------------------------------------------------------------
# deberta-env setup (one-time, run interactively before submitting):
#
#   module reset
#   module load cudatoolkit/25.3_12.8
#   python -m venv ../bertclassify/deberta-env
#   source ../bertclassify/deberta-env/bin/activate
#   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
#   pip install transformers sentencepiece scikit-learn matplotlib numpy
# ---------------------------------------------------------------------------

echo "Job starting on $(hostname)"
date

module reset
module load cudatoolkit/25.3_12.8
module list

source deberta-env/bin/activate

SCRIPT_DIR="$SLURM_SUBMIT_DIR"
cd "$SCRIPT_DIR"

python train_deberta.py \
    --epochs 3 \
    --batch-size 32 \
    --effective-batch-size 32 \
    --learning-rate 2e-5 \
    --weight-decay 0.01 \
    --warmup-ratio 0.1 \
    --max-length 128 \
    --device cuda \
    --run-name baseline

echo "Job completed"
date

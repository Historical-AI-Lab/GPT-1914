#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --partition=gpuA100x4
#SBATCH --account=bdfx-delta-gpu
#SBATCH --time=08:00:00
#SBATCH --job-name=deberta-smoke
#SBATCH --error=deberta-smoke-%j.err
#SBATCH --output=deberta-smoke-%j.out
#SBATCH --gpus-per-node=1
#SBATCH --gpu-bind=closest
#SBATCH --mem=40g
#SBATCH --constraint="scratch"

echo "Job starting on $(hostname)"
date

module reset
module load cudatoolkit/25.3_12.8

source deberta-env/bin/activate

SCRIPT_DIR="$SLURM_SUBMIT_DIR"
cd "$SCRIPT_DIR"

python -u train_deberta.py \
    --epochs 1 \
    --batch-size 32 \
    --effective-batch-size 32 \
    --learning-rate 2e-5 \
    --weight-decay 0.01 \
    --warmup-ratio 0.1 \
    --max-length 128 \
    --device cuda \
    --run-name smoke_test

echo "Job completed"
date

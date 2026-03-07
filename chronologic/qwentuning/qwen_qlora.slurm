#!/bin/bash
# qwen_qlora.slurm
#
# QLoRA fine-tuning of Qwen2.5-7B-Instruct on Delta HPC (NCSA).
# Runs on a single A100 40GB GPU — plenty of headroom for 4-bit 7B + LoRA.
#
# Submit:
#   sbatch qwen_qlora.slurm
#
# Monitor:
#   squeue --me
#   tail -f qwen_qlora_<jobid>.out
#
# Environment setup (run once on a login node before submitting):
#   module load cudatoolkit/25.3_12.8
#   python -m venv qlora-env
#   source qlora-env/bin/activate
#   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
#   pip install transformers datasets peft trl bitsandbytes accelerate
#   pip install nltk tiktoken requests
#   python SFT_dataprep.py   # generates data/train.jsonl + data/val.jsonl

#SBATCH --job-name=qwen-qlora
#SBATCH --output=qwen_qlora_%j.out
#SBATCH --error=qwen_qlora_%j.err
#SBATCH --partition=gpuA100x4
#SBATCH --account=bdfx-delta-gpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --gpus-per-node=1
#SBATCH --mem=64g
#SBATCH --time=12:00:00

echo "Job started on $(hostname) at $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "GPUs: $CUDA_VISIBLE_DEVICES"

# ---- Environment -------------------------------------------------------------

module load cudatoolkit/25.3_12.8

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

source qlora-env/bin/activate

# Sanity check
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); \
           print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'none')"

# ---- Training ----------------------------------------------------------------
#
# Adjust --num_epochs and --max_steps to taste.
# With ~80M tokens at 4096 seq len, one epoch ≈ 20k steps.
# For a first proof-of-concept run, 3000–5000 steps is reasonable.

python train_qlora.py \
    --train_data   "$SCRIPT_DIR/data/train.jsonl"  \
    --val_data     "$SCRIPT_DIR/data/val.jsonl"    \
    --output_dir   "$SCRIPT_DIR/checkpoints"       \
    --model_path   "$SCRIPT_DIR/Qwen2.5-7B-Instruct" \
    --max_seq_length  4096 \
    --batch_size      2    \
    --grad_accum      8    \
    --learning_rate   2e-4 \
    --num_epochs      1    \
    --save_steps      500  \
    --lora_r          16   \
    --lora_alpha      32   \
    --lora_dropout    0.05

echo ""
echo "Job completed at $(date)"

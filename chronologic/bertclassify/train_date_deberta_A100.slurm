#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --partition=gpuA100x4
#SBATCH --account=bdfx-delta-gpu
#SBATCH --time=08:00:00
#SBATCH --job-name=deberta-e3
#SBATCH --error=deberta-e3-%j.err
#SBATCH --output=deberta-e3-%j.out
#SBATCH --gpus-per-node=1
#SBATCH --gpu-bind=closest
#SBATCH --mem=40g
#SBATCH --constraint="scratch"

# ---------------------------------------------------------------------------
# Phase E3 DeBERTa date predictor, per stylejudge/phase-e3-plan.md Step 5.
#
# Cloned from train_deberta_e2.slurm (same deberta-env, module load, account,
# partition, HF_HOME, --mem). Differences from that E2 run:
#   - runs train_date_deberta.py, not train_deberta.py: a 36-class softmax
#     date-regression head with soft-target cross-entropy, not the E2 binary
#     BCE classifier. Same training-loop shape, same --adam-epsilon fix.
#   - --train-file / --val-file are JSONL (text + date), produced by
#     stylejudge/date_predictor_deberta.py `prepare`, NOT the E2 TSVs.
#   - --best-metric crps (lower is better) drives --save-strategy best.
#   - --batch-size 16 --effective-batch-size 32 (grad accum 2): the E2 header's
#     documented OOM fallback for deberta-v3-large at max-length 256. Bump to
#     32/32 if VRAM allows and you want the exact E2 optimizer trajectory.
#
#   BEFORE SUBMITTING, from the Mac, copy the prepared data to the Delta path
#   this script reads ($E3_DIR below). `date_predictor_deberta.py prepare`
#   writes them locally; they are not in the repo:
#       scp ~/workdata/chronologic-dating-corpus/passages/e3/{train,val}.jsonl \
#           delta:~/workdata/chronologic-dating-corpus/passages/e3/
#   and sync this script + train_date_deberta.py + stylejudge/date_predictor.py.
#
#   deberta-v3-large + its tokenizer should already be cached under this
#   HF_HOME from the E2 run. If not, pre-download from a LOGIN node first:
#       module load cudatoolkit/25.3_12.8; source deberta-env/bin/activate
#       export HF_HOME=/work/nvme/bdfx/.cache/huggingface
#       python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; \
#           AutoTokenizer.from_pretrained('microsoft/deberta-v3-large'); \
#           AutoModelForSequenceClassification.from_pretrained('microsoft/deberta-v3-large', num_labels=36)"
#   Delta compute nodes have no outbound network (reference_delta_hpc).
#
# CRITICAL: --adam-epsilon 1e-6 is not optional. At torch's 1e-8 default this
# DeBERTa-v2 architecture silently produces NaN parameters after the first
# optimizer step and still saves a checkpoint (metrics stuck at chance).
# The fix lives in train_date_deberta.py's default AND is passed explicitly
# below. Make sure Delta's copy of train_date_deberta.py AND
# stylejudge/date_predictor.py (imported for the bin grid / soft labels /
# CRPS) are synced before submitting.
#
# After the run: the checkpoint lands in
# bertclassify/model_output/e3_v1/. Sync it to
# $HOME/workdata/chronologic-dating-corpus/passages/e3/deberta_model/ (the path
# stylejudge/date_predictor_deberta.py `evaluate --run-dir` expects) before
# evaluating. Revise --time once a real run reports what it needed.
# ---------------------------------------------------------------------------

echo "Job starting on $(hostname)"
date

module reset
module load cudatoolkit/25.3_12.8
module list

export HF_HOME=/work/nvme/bdfx/.cache/huggingface
export HF_HUB_OFFLINE=1

source deberta-env/bin/activate

SCRIPT_DIR="$SLURM_SUBMIT_DIR"
cd "$SCRIPT_DIR"

E3_DIR="$HOME/workdata/chronologic-dating-corpus/passages/e3"

python -u train_date_deberta.py \
    --model-name microsoft/deberta-v3-large \
    --train-file "$E3_DIR/train.jsonl" \
    --val-file "$E3_DIR/val.jsonl" \
    --sigma 15 \
    --epochs 3 \
    --batch-size 16 \
    --effective-batch-size 32 \
    --learning-rate 2e-5 \
    --weight-decay 0.01 \
    --adam-epsilon 1e-6 \
    --warmup-ratio 0.1 \
    --max-length 256 \
    --best-metric crps \
    --save-strategy best \
    --device cuda \
    --run-name e3_v1

echo "Job completed"
date

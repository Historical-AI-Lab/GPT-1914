#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --partition=gpuA100x4
#SBATCH --account=bdfx-delta-gpu
#SBATCH --time=01:00:00
#SBATCH --job-name=gemma4-31b-eval
#SBATCH --error=gemma4-31b-eval-%j.err
#SBATCH --output=gemma4-31b-eval-%j.out
#SBATCH --gpus-per-node=2
#SBATCH --gpu-bind=closest
#SBATCH --mem=128g
#SBATCH --constraint="scratch"

# Likelihood (--full-eval) scoring of Gemma 4 31B *base* on ChronoLogic-en-0.8.
#
# Submit from chronologic/evalcode/:   sbatch gemma4_31b_eval_A100x2.slurm
#
# ---------------------------------------------------------------------------
# AS WRITTEN THIS IS A SMOKE TEST: the first $SMOKE_N questions only, written
# to prob_08_smoke/ so it can't leak into the prob_08/ leaderboard.
#
# Check the smoke run:
#   - the .err file has no load errors, no "Some weights ... not initialized"
#     warning (that would mean the wrong model class loaded), and no OOM;
#   - the eval_results_full_*.json in prob_08_smoke/ has finite log-likelihoods
#     (no NaN/inf) and an accuracy that isn't at chance;
#   - the elapsed time between the two `date` lines below, scaled by
#     866 / $SMOKE_N, tells you how much --time the real run needs.
#
# TO MAKE IT REAL, if the smoke test passes:
#   1. Set SMOKE=0 below.
#   2. Raise --time above (Qwen-72B on 4 GPUs was given 08:00:00; budget from
#      the smoke-test timing, with a generous margin).
#   3. Optionally rename --job-name / --error / --output to drop "eval" -> "full".
# The real run writes to prob_08/, where make_leaderboard_table.py picks it up.
# Add a display name for "_projects_bdfx_models_gemma-4-31B" to the dict in
# make_leaderboard_table.py (see make_leaderboard_docs.md).
# ---------------------------------------------------------------------------
#
# Notes:
#   - --device-map auto is required even though the model would fit on fewer
#     GPUs: in benchmark_evaluation.py's load_model(), only the device_map path
#     loads in bfloat16; the single-device path uses float16, which Gemma
#     models overflow in.
#   - ~62 GB of bf16 weights across 2x A100 40GB leaves ~18 GB for
#     activations. If the smoke test OOMs on GPU, go to --gpus-per-node=4.
#   - Gemma 4 needs a recent transformers. The preflight check below fails
#     fast if the active env can't import it.
#
# ENV SETUP (once, on a login node, from evalcode/):
#   module avail python                # pick a Python >= 3.10 module
#   module load <that python module>
#   python -m venv gemma4-env
#   source gemma4-env/bin/activate
#   pip install --upgrade pip
#   pip install torch transformers accelerate numpy scipy tqdm httpx openai requests
#   python -c "import transformers.models.gemma4, torch; print(transformers.__version__, torch.__version__)"

SMOKE=1
SMOKE_N=40

MODEL_DIR=/projects/bdfx/models/gemma-4-31B
BENCHMARK=../booksample/chronologic_en_0.8.jsonl
ENV_ACTIVATE=gemma4-env/bin/activate   # see setup note above

echo "Job starting on $(hostname)"
date

module reset
# Unversioned: Delta's OS upgrade removed cudatoolkit/25.3_12.8. pip torch
# wheels bundle their own CUDA runtime, so this is mostly for nvidia-smi.
module load cudatoolkit
module list

source "$ENV_ACTIVATE"

export HF_HOME=/work/nvme/bdfx/.cache/huggingface
export HF_HUB_OFFLINE=1

SCRIPT_DIR="$SLURM_SUBMIT_DIR"
cd "$SCRIPT_DIR"

# --- preflight: fail in seconds, not after a 60 GB load ---
python - <<'EOF' || { echo "Preflight failed; see above."; exit 1; }
import sys, transformers
print("python", sys.version.split()[0], "| transformers", transformers.__version__)
import transformers.models.gemma4  # ImportError here => transformers too old for Gemma 4
import torch, accelerate, scipy.optimize  # scipy is imported lazily for Platt scaling at the very end
import benchmark_evaluation           # pulls in modelasjudge/ helpers and their deps
print("torch", torch.__version__, "| CUDA available:", torch.cuda.is_available())
EOF
if [ ! -f "$MODEL_DIR/config.json" ]; then
    echo "No config.json in $MODEL_DIR -- download the model on a login node first."
    exit 1
fi
nvidia-smi --query-gpu=name,memory.total --format=csv

if [ "$SMOKE" -eq 1 ]; then
    mkdir -p prob_08_smoke
    QUESTIONS=prob_08_smoke/chronologic_en_0.8_first${SMOKE_N}.jsonl
    head -n "$SMOKE_N" "$BENCHMARK" > "$QUESTIONS"
    OUTDIR=prob_08_smoke
    EXTRA_ARGS="--n-bootstrap 100"
else
    QUESTIONS=$BENCHMARK
    OUTDIR=prob_08
    EXTRA_ARGS=""
fi
echo "Scoring $(wc -l < "$QUESTIONS") questions -> $OUTDIR/"

date
python -u benchmark_evaluation.py \
    "$MODEL_DIR" \
    "$QUESTIONS" \
    --device-map auto \
    --full-eval \
    --verbose-report \
    --output-dir "$OUTDIR" \
    $EXTRA_ARGS
date

echo "Job completed"

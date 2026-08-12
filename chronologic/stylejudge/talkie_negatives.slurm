#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --partition=gpuA100x4
#SBATCH --account=bdfx-delta-gpu
#SBATCH --time=08:00:00
#SBATCH --job-name=talkie-negatives
#SBATCH --error=talkie-negatives-%j.err
#SBATCH --output=talkie-negatives-%j.out
#SBATCH --gpus-per-node=1
#SBATCH --gpu-bind=closest
#SBATCH --mem=128g          # 13B bf16: peaks ~2x the 26 GB checkpoint while loading.
                            # 40g (the DeBERTa template's value) gets OOM-killed at load.
#SBATCH --constraint="scratch"

# ---------------------------------------------------------------------------
# Phase D2 §4.3 — 2,000 negatives from talkie-1930-13b-base.
#
# The venv is the pre-existing `talkie-eval-env`, which lives in **evalcode/**,
# a sibling of stylejudge -- NOT in the submit directory. Override with
# TALKIE_VENV=/path/to/env if it has moved. It was built for Talkie eval, so it
# should already carry torch and the talkie package; the preflight below checks
# for the extras this pipeline adds (nltk in particular). If any are missing:
#
#   source ../evalcode/talkie-eval-env/bin/activate
#   pip install nltk huggingface_hub tiktoken
#   python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
#
# Talkie needs Python >=3.11; if a fresh env is ever required, build it with
# `module load cray-python/3.11.7` (qlora-env's 3.9 is too old).
#
# Upload before submitting, into the submit directory:
#   talkie_input.jsonl    (built locally by `generate_talkie_negatives.py stage`)
#   MainDictionary.txt    (the lexicon; ~/Dropbox path does not exist on Delta)
#
# From the repo (all tracked, so a clone/pull suffices):
#   stylejudge/{generate_talkie_negatives,negative_qc,normalize,
#               passage_filters,measure_length_distribution,sample_passages}.py
#   bertclassify/{bin_counter,filter_balance_clean}.py   <- imported via
#               passage_filters; must sit one level up, at ../bertclassify/
#
# The model needs >=28 GB VRAM in bf16, so one A100 is the minimum. The first
# run downloads a ~26 GB checkpoint into HF_HOME -- do that in an interactive
# job rather than burning batch time on it.
#
# Recommended sequence:
#   1. interactive 20-row check, eyeballed for repetition loops and verbatim
#      reproduction of the source (the base-model failure modes)
#   2. this batch job for the remaining 2,000
# ---------------------------------------------------------------------------

echo "Job starting on $(hostname)"
date
nvidia-smi

module reset
module load cudatoolkit/25.3_12.8
module list

export HF_HOME=/work/nvme/bdfx/.cache/huggingface
# The other Talkie jobs on this cluster run offline; the checkpoint is
# already cached, and this turns a silent 26 GB download attempt on a
# network-less compute node into an immediate, legible failure.
export HF_HUB_OFFLINE=1

SCRIPT_DIR="$SLURM_SUBMIT_DIR"
cd "$SCRIPT_DIR"

TALKIE_VENV="${TALKIE_VENV:-$SLURM_SUBMIT_DIR/../evalcode/talkie-eval-env}"
if [ ! -f "$TALKIE_VENV/bin/activate" ]; then
    echo "ERROR: no venv at $TALKIE_VENV" >&2
    echo "       set TALKIE_VENV=/path/to/env and resubmit" >&2
    exit 1
fi
source "$TALKIE_VENV/bin/activate"
echo "venv: $TALKIE_VENV  ($(python --version 2>&1))"

# Preflight: fail in seconds on a missing import rather than after the model
# has been loaded, and check the two inputs that are not in the repo.
python - <<'PREFLIGHT' || exit 1
# `import importlib` alone does NOT bind the `util` submodule -- it must be
# imported by name. Without this the preflight itself dies with
# "module 'importlib' has no attribute 'util'".
import importlib.util
import os
import sys

REQUIRED = ("torch", "nltk", "talkie", "huggingface_hub", "tiktoken")
present, missing = [], []
for name in REQUIRED:
    try:
        found = importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        found = False
    (present if found else missing).append(name)
print("packages present:", ", ".join(present) or "(none)")
if missing:
    sys.exit(f"ERROR: missing packages in this venv: {', '.join(missing)}\n"
             f"       pip install them into $TALKIE_VENV on a login node")

import nltk
for resource in ("tokenizers/punkt", "tokenizers/punkt_tab"):
    try:
        nltk.data.find(resource)
    except LookupError:
        sys.exit(f"ERROR: nltk {resource} missing and compute nodes have no "
                 f"network; run nltk.download() for it on a login node")

# Talkie has no local checkpoint directory: get_model_files() pulls from the
# Hub into HF_HOME. If it is not already cached, this job will try to download
# ~26 GB inside batch time. With HF_HUB_OFFLINE=1 that is not even possible, so
# an uncached checkpoint is a hard error here rather than a warning -- better to
# fail in two seconds than to burn a GPU allocation discovering it.
try:
    from huggingface_hub import try_to_load_from_cache
    from talkie.config import MODELS
    spec = MODELS["talkie-1930-13b-base"]
    hit = try_to_load_from_cache(repo_id=spec.repo_id,
                                 filename=spec.checkpoint_filename)
    if isinstance(hit, str):
        print(f"checkpoint cached: {hit}")
    else:
        sys.exit("ERROR: talkie-1930-13b-base is not cached in HF_HOME "
                 f"({os.environ.get('HF_HOME', '<unset>')}) and HF_HUB_OFFLINE=1.\n"
                 "       Pre-fetch on a login node:\n"
                 "         python -c \"from talkie.download import "
                 "download_model; download_model('talkie-1930-13b-base')\"")
except Exception as exc:                                       # noqa: BLE001
    print(f"note: could not check the checkpoint cache ({exc})", file=sys.stderr)
print("preflight ok")
PREFLIGHT

for f in talkie_input.jsonl MainDictionary.txt ../bertclassify/bin_counter.py; do
    [ -e "$f" ] || { echo "ERROR: missing required input: $f" >&2; exit 1; }
done

python -u generate_talkie_negatives.py run \
    --input talkie_input.jsonl \
    --model talkie-1930-13b-base \
    --temperature 0.9 \
    --top-p 0.95 \
    --max-new-tokens 160 \
    --device cuda \
    --lexicon "$SLURM_SUBMIT_DIR/MainDictionary.txt" \
    --out talkie_negatives.jsonl

echo "Job completed"
date

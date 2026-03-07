#!/usr/bin/env bash
# smoke_test.sh
#
# Run a quick local smoke test of the QLoRA pipeline on Apple Silicon (MPS).
# Uses sample_train.jsonl (100 examples), trains for 100 steps, then runs
# a generation check. No bitsandbytes quantisation — float16 via MPS.
#
# Prerequisites (run once):
#   python -m venv qlora-env
#   source qlora-env/bin/activate
#   pip install torch transformers datasets peft trl bitsandbytes accelerate
#   pip install nltk tiktoken requests    # for SFT_dataprep.py
#
# Usage:
#   bash smoke_test.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment if present
if [ -f "qlora-env/bin/activate" ]; then
    echo "Activating qlora-env..."
    source qlora-env/bin/activate
else
    echo "Warning: qlora-env not found. Using current Python environment."
fi

# --- Step 1: generate sample_train.jsonl if it is missing or empty ----------

SAMPLE="$SCRIPT_DIR/sample_train.jsonl"

if [ ! -s "$SAMPLE" ]; then
    echo ""
    echo "=== Generating sample_train.jsonl (one book, --test mode) ==="
    python SFT_dataprep.py --test --no-type2
    echo "Done."
else
    echo "sample_train.jsonl already exists ($(wc -l < "$SAMPLE") lines). Skipping data prep."
fi

# --- Step 2: run smoke training ---------------------------------------------

echo ""
echo "=== Running smoke training (100 examples, 100 steps, MPS) ==="

python train_qlora.py \
    --smoke \
    --output_dir "$SCRIPT_DIR/smoke_checkpoints" \
    --max_seq_length 2048

echo ""
echo "=== Smoke test complete ==="
echo "Adapter saved to: $SCRIPT_DIR/smoke_checkpoints/final_adapter"
echo ""
echo "To load and inspect the adapter:"
echo "  from peft import PeftModel"
echo "  from transformers import AutoModelForCausalLM"
echo "  model = AutoModelForCausalLM.from_pretrained('Qwen2.5-7B-Instruct')"
echo "  model = PeftModel.from_pretrained(model, 'smoke_checkpoints/final_adapter')"

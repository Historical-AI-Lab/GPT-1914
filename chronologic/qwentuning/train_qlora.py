#!/usr/bin/env python3
"""
train_qlora.py

QLoRA fine-tuning of Qwen2.5-7B-Instruct on mixed historical text +
instruction data.

Usage
-----
  # Smoke test (local Apple Silicon, uses sample_train.jsonl):
  python train_qlora.py --smoke

  # Full training (single GPU, reads data/train.jsonl + data/val.jsonl):
  python train_qlora.py

  # Full training, explicit paths:
  python train_qlora.py --train_data /path/to/train.jsonl \
                        --val_data   /path/to/val.jsonl   \
                        --output_dir /path/to/checkpoints

Device behaviour
----------------
  CUDA  : 4-bit QLoRA (bitsandbytes nf4 + double quantisation)
  MPS   : float16, standard LoRA (bitsandbytes not supported on MPS)
  CPU   : float32, standard LoRA (slow, only for debugging)

Prerequisites
-------------
  pip install torch transformers datasets peft trl bitsandbytes accelerate
"""

import argparse
import json
import sys
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR  = Path(__file__).parent
LOCAL_MODEL = (
    Path.home() / ".cache/huggingface/hub/models--Qwen--Qwen2.5-7B-Instruct"
    / "snapshots/a09a35458c702b33eeacc393d103063234e8bc28"
)

# ---------------------------------------------------------------------------
# Device detection
# ---------------------------------------------------------------------------

def detect_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"

# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def load_jsonl(path: Path) -> list:
    examples = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                examples.append(json.loads(line))
    return examples


def normalize_examples(examples: list, tokenizer) -> list:
    """
    Convert all examples to {"text": "..."} before building the Dataset.

    Handles both training schemas:
      Schema A  {"text": "..."}
      Schema B  {"messages": [{"role": "user", ...}, {"role": "assistant", ...}]}

    Pre-processing here (rather than via formatting_func) avoids a TRL 0.29
    bug where add_eos checks example["text"] before formatting_func has run,
    causing AttributeError on Schema B rows that have no "text" key.
    """
    result = []
    for ex in examples:
        if "text" in ex:
            result.append({"text": ex["text"]})
        elif "messages" in ex:
            text = tokenizer.apply_chat_template(
                ex["messages"],
                tokenize=False,
                add_generation_prompt=False,
            )
            result.append({"text": text})
    return result

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="QLoRA fine-tuning for Qwen2.5-7B-Instruct."
    )
    parser.add_argument(
        "--model_path", default=str(LOCAL_MODEL),
        help="Local directory or HF hub id for the base model",
    )
    parser.add_argument("--train_data",  default=str(SCRIPT_DIR / "data" / "train.jsonl"))
    parser.add_argument("--val_data",    default=str(SCRIPT_DIR / "data" / "val.jsonl"))
    parser.add_argument("--output_dir",  default=str(SCRIPT_DIR / "checkpoints"))

    # Training hyperparameters (defaults match RUNBOOK.md recommendations)
    parser.add_argument("--max_seq_length",  type=int,   default=4096,
                        help="Maps to SFTConfig max_length")
    parser.add_argument("--batch_size",      type=int,   default=2)
    parser.add_argument("--grad_accum",      type=int,   default=8)
    parser.add_argument("--learning_rate",   type=float, default=2e-4)
    parser.add_argument("--num_epochs",      type=float, default=1.0)
    parser.add_argument("--max_steps",       type=int,   default=-1,
                        help="If > 0, overrides num_epochs")
    parser.add_argument("--save_steps",      type=int,   default=500)

    # LoRA hyperparameters
    parser.add_argument("--lora_r",       type=int,   default=16)
    parser.add_argument("--lora_alpha",   type=int,   default=32)
    parser.add_argument("--lora_dropout", type=float, default=0.05)

    # Smoke test flag
    parser.add_argument(
        "--smoke", action="store_true",
        help=(
            "Quick smoke test: first 100 examples from sample_train.jsonl, "
            "max_steps=100, batch_size=1. Runs a generation check at the end."
        ),
    )
    args = parser.parse_args()

    device = detect_device()
    print(f"Device : {device}")
    print(f"Model  : {args.model_path}")

    # ---- Data ----------------------------------------------------------------

    if args.smoke:
        sample_path = SCRIPT_DIR / "sample_train.jsonl"
        if not sample_path.exists():
            sys.exit(
                f"ERROR: {sample_path} not found.\n"
                "Run: python SFT_dataprep.py --test"
            )
        all_ex = load_jsonl(sample_path)[:100]
        train_examples = all_ex[:90]
        val_examples   = all_ex[90:]
        print(f"Smoke  : {len(train_examples)} train / {len(val_examples)} val examples")
    else:
        train_path = Path(args.train_data)
        val_path   = Path(args.val_data)
        if not train_path.exists():
            sys.exit(f"ERROR: {train_path} not found.\nRun: python SFT_dataprep.py")
        train_examples = load_jsonl(train_path)
        val_examples   = load_jsonl(val_path)
        print(f"Data   : {len(train_examples)} train / {len(val_examples)} val examples")

    # ---- Tokenizer -----------------------------------------------------------
    # Load tokenizer first so normalize_examples can apply the chat template.

    tokenizer = AutoTokenizer.from_pretrained(args.model_path)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"  # required for causal LM training

    train_examples = normalize_examples(train_examples, tokenizer)
    val_examples   = normalize_examples(val_examples,   tokenizer)
    train_ds = Dataset.from_list(train_examples)
    val_ds   = Dataset.from_list(val_examples)

    # ---- Model ---------------------------------------------------------------

    if device == "cuda":
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
        model = AutoModelForCausalLM.from_pretrained(
            args.model_path,
            quantization_config=bnb_config,
            device_map="auto",
        )
        model = prepare_model_for_kbit_training(model)

    elif device == "mps":
        # bitsandbytes does not support MPS; load in float16 (~14 GB, fine on 64 GB M3 Max)
        model = AutoModelForCausalLM.from_pretrained(
            args.model_path,
            dtype=torch.float16,
        )
        model = model.to("mps")

    else:  # cpu
        model = AutoModelForCausalLM.from_pretrained(
            args.model_path,
            torch_dtype=torch.float32,
        )

    # ---- LoRA config ---------------------------------------------------------

    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        bias="none",
        task_type="CAUSAL_LM",
    )

    # ---- Training config overrides for smoke test ----------------------------

    if args.smoke:
        max_steps  = 100
        batch_size = 1
        grad_accum = 4
        save_steps = 50
        eval_steps = 50
        num_epochs = 1   # ignored because max_steps is set
    else:
        max_steps  = args.max_steps
        batch_size = args.batch_size
        grad_accum = args.grad_accum
        save_steps = args.save_steps
        eval_steps = args.save_steps
        num_epochs = args.num_epochs

    # ---- SFTConfig -----------------------------------------------------------

    sft_config = SFTConfig(
        output_dir=args.output_dir,
        max_length=args.max_seq_length,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=grad_accum,
        learning_rate=args.learning_rate,
        num_train_epochs=num_epochs,
        max_steps=max_steps,
        save_steps=save_steps,
        # MPS: entropy_from_logits overflows INT_MAX on large vocab (152K tokens).
        # Skip eval on MPS; training loss is sufficient for smoke-test purposes.
        eval_strategy="no" if device == "mps" else "steps",
        eval_steps=eval_steps,
        logging_steps=10,
        bf16=(device == "cuda"),
        fp16=False,
        packing=False,   # disabled: formatting_func handles mixed schemas
        report_to="none",
        warmup_steps=50,
        lr_scheduler_type="cosine",
    )

    # ---- Trainer -------------------------------------------------------------

    trainer = SFTTrainer(
        model=model,
        args=sft_config,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        processing_class=tokenizer,
        peft_config=lora_config,
    )

    # ---- Train ---------------------------------------------------------------

    print("\nStarting training...")
    train_result = trainer.train()
    print(f"\nTraining complete. Steps: {train_result.global_step}  "
          f"Loss: {train_result.training_loss:.4f}")

    # ---- Save adapter --------------------------------------------------------

    adapter_path = Path(args.output_dir) / "final_adapter"
    trainer.save_model(str(adapter_path))
    print(f"Adapter saved to {adapter_path}")

    # ---- Generation check (smoke only) ---------------------------------------

    if args.smoke:
        print("\n--- Generation check (should produce a coherent answer) ---")
        model.eval()
        prompt = [{"role": "user", "content": "What is the capital of England?"}]
        text   = tokenizer.apply_chat_template(
            prompt, tokenize=False, add_generation_prompt=True
        )
        inputs = tokenizer(text, return_tensors="pt").to(device)
        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=60, do_sample=False)
        print(tokenizer.decode(out[0], skip_special_tokens=True))
        print("\nSmoke test passed.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
train_deberta.py

Fine-tune DeBERTa-v3-base for authentic (0) vs. LLM-generated (1) binary classification.

Reads train.tsv / val.tsv produced by filter_balance_clean.py and trains with a manual
PyTorch loop so per-epoch metrics are trivially available for learning-curve inspection.

Usage:
    python bertclassify/train_deberta.py [options]

Options:
    --learning-rate FLOAT       AdamW learning rate (default: 2e-5)
    --weight-decay FLOAT        AdamW weight decay (default: 0.01)
    --epochs INT                Training epochs (default: 3)
    --batch-size INT            Micro-batch size per forward pass (default: 32)
    --effective-batch-size INT  Logical batch size; grad accum = effective // micro (default: 32)
    --warmup-ratio FLOAT        Fraction of total steps used for LR warm-up (default: 0.1)
    --max-length INT            Token sequence length for truncation/padding (default: 128)
    --device STR                mps | cuda | cpu  (default: auto)
    --output-dir PATH           Parent directory for run output (default: model_output)
    --run-name STR              Sub-directory name; timestamp used if omitted
    --seed INT                  Random seed (default: 42)

Examples:
    # Smoke test
    python bertclassify/train_deberta.py --epochs 1 --batch-size 8 --effective-batch-size 8 --run-name smoke_test

    # Stage 1 baseline
    python bertclassify/train_deberta.py --epochs 3 --run-name baseline

    # Hyperparameter search
    python bertclassify/train_deberta.py --epochs 4 --learning-rate 1e-5 --weight-decay 0.05 \\
        --effective-batch-size 64 --batch-size 16 --warmup-ratio 0.05 --max-length 96 --run-name search_1
"""

import argparse
import random
import sys
from datetime import datetime
from pathlib import Path

try:
    import sentencepiece  # noqa: F401
except ImportError:
    print(
        "ERROR: 'sentencepiece' is required for the DeBERTa-v3 tokenizer.\n"
        "Install it with:  pip install sentencepiece",
        file=sys.stderr,
    )
    sys.exit(1)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    get_linear_schedule_with_warmup,
)
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).parent
MODEL_NAME = "microsoft/deberta-v3-base"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Fine-tune DeBERTa-v3-base for authentic vs. imitation classification.",
    )
    parser.add_argument("--learning-rate", type=float, default=2e-5, dest="learning_rate",
                        help="AdamW learning rate (default: 2e-5)")
    parser.add_argument("--weight-decay", type=float, default=0.01, dest="weight_decay",
                        help="AdamW weight decay (default: 0.01)")
    parser.add_argument("--epochs", type=int, default=3,
                        help="Number of training epochs (default: 3)")
    parser.add_argument("--batch-size", type=int, default=32, dest="batch_size",
                        help="Micro-batch size per forward pass (default: 32)")
    parser.add_argument("--effective-batch-size", type=int, default=32,
                        dest="effective_batch_size",
                        help="Logical batch size; grad accum = effective // micro (default: 32)")
    parser.add_argument("--warmup-ratio", type=float, default=0.1, dest="warmup_ratio",
                        help="Fraction of total steps for LR warmup (default: 0.1)")
    parser.add_argument("--max-length", type=int, default=128, dest="max_length",
                        help="Token sequence length for truncation/padding (default: 128)")
    parser.add_argument("--device", default="auto",
                        help="mps | cuda | cpu | auto (default: auto)")
    parser.add_argument("--output-dir", default="model_output", dest="output_dir",
                        help="Parent directory for run output (default: model_output)")
    parser.add_argument("--run-name", default=None, dest="run_name",
                        help="Sub-directory name; timestamp used if omitted")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default: 42)")
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Device selection
# ---------------------------------------------------------------------------

def select_device(device_arg):
    if device_arg == "auto":
        if torch.cuda.is_available():
            device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            device = torch.device("mps")
        else:
            device = torch.device("cpu")
    else:
        device = torch.device(device_arg)

    print(f"Device: {device}", end="")
    if device.type == "mps":
        print("  (MPS — fp16 autocast disabled, tensors moved to CPU before numpy)")
    elif device.type == "cuda":
        print(f"  (CUDA — mixed precision enabled; {torch.cuda.get_device_name(0)})")
    else:
        print()
    return device


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

class TextDataset(Dataset):
    """Read a TSV (text\\tlabel), tokenize all texts in __init__."""

    def __init__(self, tsv_path, tokenizer, max_length):
        texts, labels = [], []
        with open(tsv_path, encoding="utf-8") as f:
            header = f.readline()  # skip header
            for line in f:
                line = line.rstrip("\n")
                if not line:
                    continue
                parts = line.split("\t")
                if len(parts) < 2:
                    continue
                texts.append(parts[0])
                labels.append(int(parts[1]))

        print(f"  {tsv_path.name}: {len(texts):,} rows "
              f"({sum(1 for l in labels if l == 0):,} authentic, "
              f"{sum(1 for l in labels if l == 1):,} imitation)")

        encoding = tokenizer(
            texts,
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
        self.input_ids = encoding["input_ids"]
        self.attention_mask = encoding["attention_mask"]
        self.token_type_ids = encoding.get("token_type_ids")
        self.labels = torch.tensor(labels, dtype=torch.float32)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {
            "input_ids": self.input_ids[idx],
            "attention_mask": self.attention_mask[idx],
            "labels": self.labels[idx],
        }
        if self.token_type_ids is not None:
            item["token_type_ids"] = self.token_type_ids[idx]
        return item


# ---------------------------------------------------------------------------
# Training / evaluation
# ---------------------------------------------------------------------------

def _no_decay_params(model):
    """Return (decay_params, no_decay_params) for AdamW weight-decay exclusion."""
    no_decay = {"bias", "LayerNorm.weight", "LayerNorm.bias"}
    decay_p, no_decay_p = [], []
    for name, param in model.named_parameters():
        if not param.requires_grad:
            continue
        if any(nd in name for nd in no_decay):
            no_decay_p.append(param)
        else:
            decay_p.append(param)
    return decay_p, no_decay_p


def train_one_epoch(model, loader, optimizer, scheduler, device,
                    grad_accum_steps, use_amp, scaler, loss_fn):
    model.train()
    total_loss = 0.0
    optimizer.zero_grad()
    step = 0

    for i, batch in enumerate(loader):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)
        token_type_ids = batch.get("token_type_ids")
        if token_type_ids is not None:
            token_type_ids = token_type_ids.to(device)

        kwargs = dict(input_ids=input_ids, attention_mask=attention_mask)
        if token_type_ids is not None:
            kwargs["token_type_ids"] = token_type_ids

        if use_amp:
            with torch.amp.autocast("cuda"):
                logits = model(**kwargs).logits.squeeze(-1)
                loss = loss_fn(logits, labels) / grad_accum_steps
            scaler.scale(loss).backward()
        else:
            logits = model(**kwargs).logits.squeeze(-1)
            loss = loss_fn(logits, labels) / grad_accum_steps
            loss.backward()

        total_loss += loss.item() * grad_accum_steps

        if (i + 1) % grad_accum_steps == 0:
            if use_amp:
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                scaler.step(optimizer)
                scaler.update()
            else:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
            scheduler.step()
            optimizer.zero_grad()
            step += 1

    # Handle leftover micro-batches at end of epoch
    remaining = len(loader) % grad_accum_steps
    if remaining != 0:
        if use_amp:
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()
        else:
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
        scheduler.step()
        optimizer.zero_grad()

    return total_loss / len(loader)


def evaluate(model, loader, device, loss_fn):
    model.eval()
    all_logits, all_labels = [], []
    total_loss = 0.0

    with torch.no_grad():
        for batch in loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            token_type_ids = batch.get("token_type_ids")
            if token_type_ids is not None:
                token_type_ids = token_type_ids.to(device)

            kwargs = dict(input_ids=input_ids, attention_mask=attention_mask)
            if token_type_ids is not None:
                kwargs["token_type_ids"] = token_type_ids

            logits = model(**kwargs).logits.squeeze(-1)
            loss = loss_fn(logits, labels)
            total_loss += loss.item()

            # Move to CPU before numpy (required for MPS)
            all_logits.append(logits.cpu().float())
            all_labels.append(labels.cpu().float())

    all_logits = torch.cat(all_logits).numpy()
    all_labels = torch.cat(all_labels).numpy().astype(int)

    nan_count = int(np.isnan(all_logits).sum())
    if nan_count:
        print(f"\n  WARNING: {nan_count}/{len(all_logits)} NaN logits (MPS numerical issue); "
              "replacing with 0.0 (prob=0.5). Consider --device cpu if this persists.")
        all_logits = np.nan_to_num(all_logits, nan=0.0)

    probs = 1.0 / (1.0 + np.exp(-all_logits))  # sigmoid
    preds = (probs >= 0.5).astype(int)

    acc = accuracy_score(all_labels, preds)
    f1 = f1_score(all_labels, preds, zero_division=0)
    auroc = roc_auc_score(all_labels, probs) if len(np.unique(all_labels)) > 1 else float("nan")
    avg_loss = total_loss / len(loader)

    return {"loss": avg_loss, "accuracy": acc, "f1": f1, "auroc": auroc}


# ---------------------------------------------------------------------------
# Learning curve
# ---------------------------------------------------------------------------

def plot_learning_curve(train_losses, val_metrics, run_dir):
    epochs = list(range(1, len(train_losses) + 1))

    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Loss", color="steelblue")
    ax1.plot(epochs, train_losses, "o-", color="steelblue", label="Train loss")
    val_losses = [m["loss"] for m in val_metrics]
    ax1.plot(epochs, val_losses, "s--", color="cornflowerblue", label="Val loss")
    ax1.tick_params(axis="y", labelcolor="steelblue")

    ax2 = ax1.twinx()
    ax2.set_ylabel("Val metric", color="darkorange")
    accs = [m["accuracy"] for m in val_metrics]
    f1s = [m["f1"] for m in val_metrics]
    aurocs = [m["auroc"] for m in val_metrics]
    ax2.plot(epochs, accs, "^-", color="darkorange", label="Val accuracy")
    ax2.plot(epochs, f1s, "v-", color="tomato", label="Val F1")
    ax2.plot(epochs, aurocs, "D-", color="green", label="Val AUROC")
    ax2.tick_params(axis="y", labelcolor="darkorange")
    ax2.set_ylim(0, 1)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower left", fontsize=9)

    plt.title("DeBERTa fine-tuning learning curve")
    plt.tight_layout()
    out_path = run_dir / "learning_curve.png"
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Learning curve saved → {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv=None):
    args = parse_args(argv)

    # Seed
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    # Run directory
    run_name = args.run_name or datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = SCRIPT_DIR / args.output_dir / run_name
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Run output: {output_dir}")

    # Device
    device = select_device(args.device)
    use_amp = device.type == "cuda"
    scaler = torch.amp.GradScaler("cuda") if use_amp else None

    # Gradient accumulation
    grad_accum_steps = args.effective_batch_size // args.batch_size
    if args.effective_batch_size % args.batch_size != 0:
        print(
            f"WARNING: effective_batch_size ({args.effective_batch_size}) is not evenly "
            f"divisible by batch_size ({args.batch_size}). "
            f"Using grad_accum_steps={grad_accum_steps} (truncated)."
        )
    print(f"Grad accum steps: {grad_accum_steps} "
          f"(micro={args.batch_size}, effective={grad_accum_steps * args.batch_size})")

    # Tokenizer + datasets
    print(f"\nLoading tokenizer: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    train_tsv = SCRIPT_DIR / "train.tsv"
    val_tsv = SCRIPT_DIR / "val.tsv"
    for p in (train_tsv, val_tsv):
        if not p.exists():
            print(f"ERROR: {p} not found. Run filter_balance_clean.py first.", file=sys.stderr)
            sys.exit(1)

    print("\nTokenizing datasets ...")
    train_dataset = TextDataset(train_tsv, tokenizer, args.max_length)
    val_dataset = TextDataset(val_tsv, tokenizer, args.max_length)

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size * 2, shuffle=False)

    # Model
    print(f"\nLoading model: {MODEL_NAME}")
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=1)
    model = model.to(device)

    # Optimizer (exclude bias + LayerNorm from weight decay)
    decay_p, no_decay_p = _no_decay_params(model)
    optimizer = torch.optim.AdamW(
        [
            {"params": decay_p, "weight_decay": args.weight_decay},
            {"params": no_decay_p, "weight_decay": 0.0},
        ],
        lr=args.learning_rate,
    )

    # Scheduler
    total_steps = (len(train_loader) // grad_accum_steps) * args.epochs
    warmup_steps = int(total_steps * args.warmup_ratio)
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps
    )
    print(f"Scheduler: linear warmup {warmup_steps} / {total_steps} steps")

    loss_fn = nn.BCEWithLogitsLoss()

    # Training loop
    train_losses = []
    val_metrics_list = []

    print(f"\n{'Epoch':>5}  {'Train loss':>10}  {'Val loss':>9}  "
          f"{'Val acc':>8}  {'Val F1':>7}  {'Val AUROC':>9}")
    print("-" * 60)

    for epoch in range(1, args.epochs + 1):
        train_loss = train_one_epoch(
            model, train_loader, optimizer, scheduler, device,
            grad_accum_steps, use_amp, scaler, loss_fn,
        )
        val_m = evaluate(model, val_loader, device, loss_fn)

        train_losses.append(train_loss)
        val_metrics_list.append(val_m)

        print(
            f"{epoch:>5}  {train_loss:>10.4f}  {val_m['loss']:>9.4f}  "
            f"{val_m['accuracy']:>8.4f}  {val_m['f1']:>7.4f}  {val_m['auroc']:>9.4f}"
        )

    # Save model + tokenizer
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"\nModel saved → {output_dir}")

    # Learning curve
    if args.epochs > 1:
        plot_learning_curve(train_losses, val_metrics_list, output_dir)
    else:
        print("(Learning curve skipped — only 1 epoch)")


if __name__ == "__main__":
    main()

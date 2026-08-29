#!/usr/bin/env python3
"""
train_date_deberta.py

Fine-tune DeBERTa-v3-large as a *binned date regressor*: a 36-way softmax head
(1680-2040, 10-year bins) trained against Gaussian soft targets, exactly the
objective `stylejudge/date_predictor.py`'s lexical E1 head uses, so the two are
directly comparable. Phase E3 — see `stylejudge/phase-e3-plan.md` Step 5.

A sibling of `train_deberta.py`, not an edit of it: that script is a binary
`num_labels=1` BCE classifier that Phase E2 depends on unchanged. This one keeps
its proven training-loop shape (manual PyTorch loop, grad accumulation, linear
warmup, AdamW with bias/LayerNorm weight-decay exclusion, `--adam-epsilon 1e-6`
to dodge the DeBERTa-v2 NaN bug) and swaps in the 36-class head and the
soft-target cross-entropy loss.

Input is JSONL with `text` and `date` fields (a 36-vector soft label does not
fit the two-column TSV contract, and the labels are cheap to build in the
loader). The bin grid, soft-label construction, CRPS and coverage all come from
`stylejudge/date_predictor.py` — never re-implemented here.

Usage:
    python bertclassify/train_date_deberta.py --train-file train.jsonl --val-file val.jsonl

Run-dir contents: HuggingFace `config.json` (with the bin grid + sigma stored on
`model.config` so `evaluate`/`score` never have to be told them again),
`model.safetensors` + tokenizer, `metrics.json` (per-epoch train loss / val CRPS
/ coverage), `learning_curve.png`.
"""

import argparse
import json
import random
import sys
from datetime import datetime
from pathlib import Path

try:
    import sentencepiece  # noqa: F401
except ImportError:
    print("ERROR: 'sentencepiece' is required for the DeBERTa-v3 tokenizer.\n"
          "Install it with:  pip install sentencepiece", file=sys.stderr)
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

SCRIPT_DIR = Path(__file__).resolve().parent
STYLEJUDGE_DIR = SCRIPT_DIR.parent / "stylejudge"
sys.path.insert(0, str(STYLEJUDGE_DIR))

from date_predictor import (                                        # noqa: E402
    build_bin_grid,
    date_to_bin,
    soft_label,
    crps_binned,
    coverage,
)

MODEL_NAME = "microsoft/deberta-v3-large"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Fine-tune DeBERTa-v3-large as a binned-date softmax regressor.")
    p.add_argument("--model-name", default=MODEL_NAME, dest="model_name")
    p.add_argument("--train-file", required=True, dest="train_file",
                   help="JSONL with `text` + `date` fields")
    p.add_argument("--val-file", required=True, dest="val_file",
                   help="JSONL with `text` + `date` fields")
    p.add_argument("--sigma", type=float, default=15.0,
                   help="Gaussian soft-label width in years (default: 15, E1's selected value)")
    p.add_argument("--grid-lo", type=int, default=1680, dest="grid_lo")
    p.add_argument("--grid-hi", type=int, default=2040, dest="grid_hi")
    p.add_argument("--bin-width", type=int, default=10, dest="bin_width")
    p.add_argument("--epochs", type=int, default=3)
    p.add_argument("--batch-size", type=int, default=16, dest="batch_size",
                   help="Micro-batch per forward pass (default: 16)")
    p.add_argument("--effective-batch-size", type=int, default=32,
                   dest="effective_batch_size",
                   help="Logical batch size; grad accum = effective // micro (default: 32)")
    p.add_argument("--learning-rate", type=float, default=2e-5, dest="learning_rate")
    p.add_argument("--weight-decay", type=float, default=0.01, dest="weight_decay")
    p.add_argument("--adam-epsilon", type=float, default=1e-6, dest="adam_epsilon",
                   help="AdamW eps (default: 1e-6, NOT torch's 1e-8 — the smaller value "
                        "silently produces NaN parameters after the first optimizer step "
                        "for this DeBERTa-v2 architecture; see train_deberta.py's flag help "
                        "and bertclassify/train_deberta_e2.slurm's header. Do not lower.")
    p.add_argument("--warmup-ratio", type=float, default=0.1, dest="warmup_ratio")
    p.add_argument("--max-length", type=int, default=256, dest="max_length")
    p.add_argument("--device", default="auto", help="mps | cuda | cpu | auto (default: auto)")
    p.add_argument("--output-dir", default="model_output", dest="output_dir")
    p.add_argument("--run-name", default=None, dest="run_name",
                   help="Sub-directory name; timestamp used if omitted")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--save-strategy", choices=["best", "last"], default="best",
                   dest="save_strategy")
    p.add_argument("--best-metric", choices=["crps", "coverage50", "loss"], default="crps",
                   dest="best_metric",
                   help="Val metric --save-strategy best selects on (default: crps)")
    return p.parse_args(argv)


# ---------------------------------------------------------------------------
# Device
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
    print(f"Device: {device}")
    return device


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

class DateJsonlDataset(Dataset):
    """Read a JSONL (`text`, `date`), tokenize + build 36-vec soft labels in __init__."""

    def __init__(self, jsonl_path, tokenizer, max_length, sigma, midpoints):
        texts, dates = [], []
        with open(jsonl_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if "text" not in row or row.get("date") in (None, ""):
                    continue
                texts.append(row["text"])
                dates.append(float(row["date"]))

        print(f"  {Path(jsonl_path).name}: {len(texts):,} rows "
              f"(dates {min(dates):.0f}-{max(dates):.0f})")

        enc = tokenizer(texts, padding="max_length", truncation=True,
                        max_length=max_length, return_tensors="pt")
        self.input_ids = enc["input_ids"]
        self.attention_mask = enc["attention_mask"]
        self.token_type_ids = enc.get("token_type_ids")
        self.soft = torch.tensor(
            np.stack([soft_label(d, sigma, midpoints) for d in dates]),
            dtype=torch.float32)
        self.dates = np.asarray(dates, dtype=float)

    def __len__(self):
        return len(self.dates)

    def __getitem__(self, idx):
        item = {
            "input_ids": self.input_ids[idx],
            "attention_mask": self.attention_mask[idx],
            "soft": self.soft[idx],
        }
        if self.token_type_ids is not None:
            item["token_type_ids"] = self.token_type_ids[idx]
        return item


# ---------------------------------------------------------------------------
# Loss / train / eval
# ---------------------------------------------------------------------------

def soft_ce(logits, y_soft):
    """-(y_soft * log_softmax(logits)).sum(-1).mean() — E1's fit_lexical_model objective."""
    return -(y_soft * torch.log_softmax(logits, dim=-1)).sum(dim=-1).mean()


def _no_decay_params(model):
    no_decay = {"bias", "LayerNorm.weight", "LayerNorm.bias"}
    decay_p, no_decay_p = [], []
    for name, param in model.named_parameters():
        if not param.requires_grad:
            continue
        (no_decay_p if any(nd in name for nd in no_decay) else decay_p).append(param)
    return decay_p, no_decay_p


def _forward_kwargs(batch, device):
    kwargs = dict(input_ids=batch["input_ids"].to(device),
                  attention_mask=batch["attention_mask"].to(device))
    if "token_type_ids" in batch:
        kwargs["token_type_ids"] = batch["token_type_ids"].to(device)
    return kwargs


def train_one_epoch(model, loader, optimizer, scheduler, device, grad_accum_steps,
                    use_amp, scaler):
    model.train()
    total_loss = 0.0
    optimizer.zero_grad()
    for i, batch in enumerate(loader):
        y_soft = batch["soft"].to(device)
        kwargs = _forward_kwargs(batch, device)
        if use_amp:
            with torch.amp.autocast("cuda"):
                logits = model(**kwargs).logits
                loss = soft_ce(logits, y_soft) / grad_accum_steps
            scaler.scale(loss).backward()
        else:
            logits = model(**kwargs).logits
            loss = soft_ce(logits, y_soft) / grad_accum_steps
            loss.backward()
        total_loss += loss.item() * grad_accum_steps

        if (i + 1) % grad_accum_steps == 0 or (i + 1) == len(loader):
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


@torch.no_grad()
def evaluate(model, loader, device, edges, midpoints, val_dates):
    model.eval()
    all_probs = []
    total_loss = 0.0
    for batch in loader:
        y_soft = batch["soft"].to(device)
        kwargs = _forward_kwargs(batch, device)
        logits = model(**kwargs).logits
        total_loss += soft_ce(logits, y_soft).item()
        probs = torch.softmax(logits, dim=-1).cpu().float()
        probs = torch.nan_to_num(probs, nan=0.0)
        all_probs.append(probs.numpy())
    probs = np.concatenate(all_probs, axis=0)
    true_bins = [date_to_bin(d, edges) for d in val_dates]
    crps = float(np.mean([crps_binned(p, tb) for p, tb in zip(probs, true_bins)]))
    cov50 = coverage(probs, true_bins, 0.5)
    cov90 = coverage(probs, true_bins, 0.9)
    means = probs @ np.asarray(midpoints, dtype=float)
    mae = float(np.mean(np.abs(means - np.asarray(val_dates, dtype=float))))
    return {"loss": total_loss / len(loader), "crps": crps, "coverage50": cov50,
            "coverage90": cov90, "mae": mae}


# ---------------------------------------------------------------------------
# Learning curve
# ---------------------------------------------------------------------------

def plot_learning_curve(train_losses, val_metrics, run_dir):
    epochs = list(range(1, len(train_losses) + 1))
    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Loss / CRPS", color="steelblue")
    ax1.plot(epochs, train_losses, "o-", color="steelblue", label="Train loss")
    ax1.plot(epochs, [m["loss"] for m in val_metrics], "s--", color="cornflowerblue",
             label="Val loss")
    ax1.plot(epochs, [m["crps"] for m in val_metrics], "D-", color="firebrick",
             label="Val CRPS (yrs)")
    ax1.tick_params(axis="y", labelcolor="steelblue")

    ax2 = ax1.twinx()
    ax2.set_ylabel("Coverage", color="darkorange")
    ax2.plot(epochs, [m["coverage50"] for m in val_metrics], "^-", color="darkorange",
             label="Val coverage@50")
    ax2.plot(epochs, [m["coverage90"] for m in val_metrics], "v-", color="green",
             label="Val coverage@90")
    ax2.set_ylim(0, 1)
    ax2.tick_params(axis="y", labelcolor="darkorange")

    l1, lab1 = ax1.get_legend_handles_labels()
    l2, lab2 = ax2.get_legend_handles_labels()
    ax1.legend(l1 + l2, lab1 + lab2, loc="upper right", fontsize=9)
    plt.title("DeBERTa date-regressor learning curve")
    plt.tight_layout()
    out_path = run_dir / "learning_curve.png"
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Learning curve saved -> {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv=None):
    args = parse_args(argv)
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    run_name = args.run_name or datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = SCRIPT_DIR / args.output_dir / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"Run output: {run_dir}")

    device = select_device(args.device)
    use_amp = device.type == "cuda"
    scaler = torch.amp.GradScaler("cuda") if use_amp else None

    grad_accum_steps = max(1, args.effective_batch_size // args.batch_size)
    print(f"Grad accum steps: {grad_accum_steps} "
          f"(micro={args.batch_size}, effective={grad_accum_steps * args.batch_size})")

    edges, midpoints = build_bin_grid(args.grid_lo, args.grid_hi, args.bin_width)
    n_bins = len(midpoints)
    print(f"Bin grid: {n_bins} bins, {args.grid_lo}-{args.grid_hi} step {args.bin_width}, "
          f"sigma={args.sigma}")

    print(f"\nLoading tokenizer: {args.model_name}")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)

    for f in (args.train_file, args.val_file):
        if not Path(f).exists():
            print(f"ERROR: {f} not found.", file=sys.stderr)
            sys.exit(1)

    print("\nTokenizing datasets ...")
    train_ds = DateJsonlDataset(Path(args.train_file), tokenizer, args.max_length,
                                args.sigma, midpoints)
    val_ds = DateJsonlDataset(Path(args.val_file), tokenizer, args.max_length,
                              args.sigma, midpoints)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size * 2, shuffle=False)

    print(f"\nLoading model: {args.model_name}")
    model = AutoModelForSequenceClassification.from_pretrained(
        args.model_name, num_labels=n_bins)
    model = model.to(device)

    decay_p, no_decay_p = _no_decay_params(model)
    optimizer = torch.optim.AdamW(
        [{"params": decay_p, "weight_decay": args.weight_decay},
         {"params": no_decay_p, "weight_decay": 0.0}],
        lr=args.learning_rate, eps=args.adam_epsilon)

    total_steps = (len(train_loader) // grad_accum_steps) * args.epochs
    warmup_steps = int(total_steps * args.warmup_ratio)
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=warmup_steps, num_training_steps=max(total_steps, 1))
    print(f"Scheduler: linear warmup {warmup_steps} / {total_steps} steps")

    # All three --best-metric options are lower-is-better: raw CRPS, raw val
    # loss, or |coverage@50 - 0.5| (calibration error, not coverage itself).
    best_score = float("inf")
    best_epoch = None

    def selection_score(vm):
        if args.best_metric == "coverage50":
            return abs(vm["coverage50"] - 0.5)
        return vm[args.best_metric]

    train_losses, val_metrics_list = [], []
    print(f"\n{'Epoch':>5}  {'Train loss':>10}  {'Val loss':>9}  {'Val CRPS':>9}  "
          f"{'Val MAE':>8}  {'cov@50':>7}  {'cov@90':>7}")
    print("-" * 68)

    for epoch in range(1, args.epochs + 1):
        train_loss = train_one_epoch(model, train_loader, optimizer, scheduler, device,
                                     grad_accum_steps, use_amp, scaler)
        vm = evaluate(model, val_loader, device, edges, midpoints, val_ds.dates)
        train_losses.append(train_loss)
        val_metrics_list.append(vm)
        print(f"{epoch:>5}  {train_loss:>10.4f}  {vm['loss']:>9.4f}  {vm['crps']:>9.3f}  "
              f"{vm['mae']:>8.2f}  {vm['coverage50']:>7.3f}  {vm['coverage90']:>7.3f}")

        if args.save_strategy == "best":
            score = selection_score(vm)
            if score == score and score < best_score:
                best_score = score
                best_epoch = epoch
                model.config.date_grid_lo = args.grid_lo
                model.config.date_grid_hi = args.grid_hi
                model.config.date_bin_width = args.bin_width
                model.config.date_sigma = args.sigma
                model.save_pretrained(run_dir)
                tokenizer.save_pretrained(run_dir)
                print(f"       -> new best {args.best_metric}={score:.4f}, checkpoint saved")

    if args.save_strategy == "last" or best_epoch is None:
        model.config.date_grid_lo = args.grid_lo
        model.config.date_grid_hi = args.grid_hi
        model.config.date_bin_width = args.bin_width
        model.config.date_sigma = args.sigma
        model.save_pretrained(run_dir)
        tokenizer.save_pretrained(run_dir)
        kept = f"last (epoch {args.epochs})"
    else:
        kept = f"epoch {best_epoch} ({args.best_metric}={best_score:.4f})"
    print(f"\nModel saved -> {run_dir}  [kept: {kept}]")

    with open(run_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump({
            "save_strategy": args.save_strategy,
            "best_metric": args.best_metric,
            "kept": kept,
            "sigma": args.sigma,
            "grid": {"lo": args.grid_lo, "hi": args.grid_hi, "bin_width": args.bin_width,
                     "n_bins": n_bins},
            "per_epoch": [{"epoch": i + 1, "train_loss": tl, **vm}
                          for i, (tl, vm) in enumerate(zip(train_losses, val_metrics_list))],
        }, f, indent=2)

    if args.epochs > 1:
        plot_learning_curve(train_losses, val_metrics_list, run_dir)
    else:
        print("(Learning curve skipped — only 1 epoch)")


if __name__ == "__main__":
    main()

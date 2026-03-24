#!/usr/bin/env python3
"""run_deberta.py

Run inference with a fine-tuned DeBERTa-v3-base classifier.

Classifies texts as authentic (0) or imitation (1). Applies normalize_text()
from filter_balance_clean.py to match the training pipeline exactly.

Usage:
    python bertclassify/run_deberta.py INPUT_FILE [options]

Positional:
    INPUT_FILE              TSV (text\\tlabel header) or plain text (one per line)

Options:
    --model-dir PATH        Saved model directory (default: model_output/baseline/)
    --output PATH           Output TSV path (default: {input_stem}_predictions.tsv)
    --batch-size INT        Inference batch size (default: 64)
    --max-length INT        Token sequence length (default: 128)
    --threshold FLOAT       Classification threshold (default: 0.5)
    --device STR            mps | cuda | cpu | auto (default: auto)

Examples:
    # Labeled input — prints metrics + writes predictions
    python bertclassify/run_deberta.py bertclassify/val.tsv \\
        --model-dir bertclassify/model_output/baseline/

    # Custom output path
    python bertclassify/run_deberta.py bertclassify/val.tsv \\
        --model-dir bertclassify/model_output/search_1/ \\
        --output search1_preds.tsv

    # Unlabeled plain text — predictions only, no metrics
    python bertclassify/run_deberta.py some_texts.txt \\
        --model-dir bertclassify/model_output/baseline/
"""

import argparse
import sys
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

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from filter_balance_clean import normalize_text


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Run DeBERTa-v3-base inference for authentic vs. imitation classification.",
    )
    parser.add_argument("input_file", metavar="INPUT_FILE",
                        help="TSV (text\\tlabel header) or plain text (one per line)")
    parser.add_argument("--model-dir", default="model_output/baseline/", dest="model_dir",
                        help="Saved model directory (default: model_output/baseline/)")
    parser.add_argument("--output", default=None,
                        help="Output TSV path (default: {input_stem}_predictions.tsv)")
    parser.add_argument("--batch-size", type=int, default=64, dest="batch_size",
                        help="Inference batch size (default: 64)")
    parser.add_argument("--max-length", type=int, default=128, dest="max_length",
                        help="Token sequence length (default: 128)")
    parser.add_argument("--threshold", type=float, default=0.5,
                        help="Classification threshold (default: 0.5)")
    parser.add_argument("--device", default="auto",
                        help="mps | cuda | cpu | auto (default: auto)")
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
        print(f"  (CUDA — {torch.cuda.get_device_name(0)})")
    else:
        print()
    return device


# ---------------------------------------------------------------------------
# Input loading
# ---------------------------------------------------------------------------

def load_input(input_path: Path) -> tuple[list[str], list[int] | None]:
    """Read input file; return (texts, labels).

    If first line is 'text\\tlabel', parse as labeled TSV and return integer labels.
    Otherwise treat as plain text (one text per line) and return None for labels.
    normalize_text() is applied to every text.
    """
    with open(input_path, encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]

    if not lines:
        return [], None

    # Detect labeled TSV by header
    if lines[0].strip() == "text\tlabel":
        texts, labels = [], []
        for line in lines[1:]:
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            texts.append(normalize_text(parts[0]))
            labels.append(int(parts[1]))
        print(f"Labeled TSV: {len(texts):,} rows "
              f"({sum(1 for l in labels if l == 0):,} authentic, "
              f"{sum(1 for l in labels if l == 1):,} imitation)")
        return texts, labels
    else:
        texts = [normalize_text(line) for line in lines if line.strip()]
        print(f"Plain text: {len(texts):,} lines")
        return texts, None


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------

def run_inference(
    texts: list[str],
    model,
    tokenizer,
    device: torch.device,
    batch_size: int,
    max_length: int,
) -> np.ndarray:
    """Run batched forward passes; return sigmoid probabilities as numpy array."""
    model.eval()
    all_probs = []
    nan_total = 0

    with torch.no_grad():
        for start in range(0, len(texts), batch_size):
            batch_texts = texts[start:start + batch_size]
            encoding = tokenizer(
                batch_texts,
                padding="max_length",
                truncation=True,
                max_length=max_length,
                return_tensors="pt",
            )
            input_ids = encoding["input_ids"].to(device)
            attention_mask = encoding["attention_mask"].to(device)
            kwargs = dict(input_ids=input_ids, attention_mask=attention_mask)
            if "token_type_ids" in encoding:
                kwargs["token_type_ids"] = encoding["token_type_ids"].to(device)

            logits = model(**kwargs).logits.squeeze(-1)
            # Move to CPU before numpy (required for MPS)
            logits_np = logits.cpu().float().numpy()

            nan_count = int(np.isnan(logits_np).sum())
            if nan_count:
                nan_total += nan_count
                logits_np = np.nan_to_num(logits_np, nan=0.0)

            probs = 1.0 / (1.0 + np.exp(-logits_np))
            all_probs.append(probs)

    if nan_total:
        print(f"\nWARNING: {nan_total}/{len(texts)} NaN logits (MPS numerical issue); "
              "replaced with 0.0 (prob=0.5). Consider --device cpu if this persists.")

    return np.concatenate(all_probs)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def write_output(output_path: Path, texts: list[str], probs: np.ndarray, threshold: float) -> None:
    """Write predictions TSV with columns: text, prediction, probability."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("text\tprediction\tprobability\n")
        for text, prob in zip(texts, probs):
            pred = 1 if prob > threshold else 0
            clean = text.replace("\t", " ").replace("\n", " ")
            f.write(f"{clean}\t{pred}\t{prob:.6f}\n")
    print(f"Predictions written → {output_path}")


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def print_metrics(labels: list[int], probs: np.ndarray, threshold: float) -> None:
    """Print accuracy, F1, AUROC, and per-class breakdown to stdout."""
    labels_np = np.array(labels, dtype=int)
    preds = (probs > threshold).astype(int)

    acc = accuracy_score(labels_np, preds)
    f1 = f1_score(labels_np, preds, zero_division=0)
    auroc = (
        roc_auc_score(labels_np, probs)
        if len(np.unique(labels_np)) > 1
        else float("nan")
    )

    # Per-class breakdown
    auth_mask = labels_np == 0
    imit_mask = labels_np == 1
    auth_correct = int((preds[auth_mask] == 0).sum())
    imit_correct = int((preds[imit_mask] == 1).sum())
    auth_total = int(auth_mask.sum())
    imit_total = int(imit_mask.sum())

    print(f"\nAccuracy: {acc:.4f}")
    print(f"F1:       {f1:.4f}")
    print(f"AUROC:    {auroc:.4f}")
    print(f"Authentic: {auth_correct} / {auth_total} correct")
    print(f"Imitation: {imit_correct} / {imit_total} correct")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv=None):
    args = parse_args(argv)

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Resolve model dir relative to script dir if not absolute
    model_dir = Path(args.model_dir)
    if not model_dir.is_absolute():
        model_dir = SCRIPT_DIR / model_dir
    if not model_dir.exists():
        print(f"ERROR: model directory not found: {model_dir}", file=sys.stderr)
        sys.exit(1)

    # Output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_predictions.tsv"

    # Device
    device = select_device(args.device)

    # Load input
    texts, labels = load_input(input_path)
    if not texts:
        print("ERROR: no texts found in input file.", file=sys.stderr)
        sys.exit(1)

    # Load model + tokenizer
    print(f"\nLoading model from {model_dir} ...")
    tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
    model = AutoModelForSequenceClassification.from_pretrained(str(model_dir))
    model = model.to(device)
    print(f"Model loaded ({sum(p.numel() for p in model.parameters()):,} parameters)")

    # Inference
    print(f"\nRunning inference (batch_size={args.batch_size}, max_length={args.max_length}) ...")
    probs = run_inference(texts, model, tokenizer, device, args.batch_size, args.max_length)

    # Output
    write_output(output_path, texts, probs, args.threshold)

    # Metrics (labeled input only)
    if labels is not None:
        print_metrics(labels, probs, args.threshold)


if __name__ == "__main__":
    main()

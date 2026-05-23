#!/usr/bin/env python3
"""run_deberta_pairs.py

Run DeBERTa inference on paired passages and emit log-odds (logits) for each.

For each pair, text_a is treated as the reference (e.g. ground truth) and
text_b as the candidate (e.g. anachronistic distractor).
delta = logit_b - logit_a (positive means b is more "imitation-like").

Input JSONL must contain at least: pair_id, text_a, text_b
All other fields are passed through unchanged.

Output JSONL: input fields + logit_a, logit_b, delta

Usage:
    python modelasjudge/run_deberta_pairs.py PAIRS_JSONL OUT_JSONL \\
        [--model-dir ../bertclassify/baseline] \\
        [--batch-size 64] [--max-length 256] [--device auto]

Options:
    --model-dir PATH    Saved DeBERTa model directory (default: ../bertclassify/baseline)
    --batch-size INT    Flat-batch size across both texts (default: 64)
    --max-length INT    Tokenizer max length (default: 256)
    --device STR        mps | cuda | cpu | auto (default: auto)
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import sentencepiece  # noqa: F401
except ImportError:
    print("ERROR: 'sentencepiece' required.  pip install sentencepiece", file=sys.stderr)
    sys.exit(1)

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

SCRIPT_DIR = Path(__file__).parent
BERTCLASSIFY_DIR = SCRIPT_DIR.parent / "bertclassify"
sys.path.insert(0, str(BERTCLASSIFY_DIR))
from filter_balance_clean import normalize_text


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="DeBERTa log-odds for paired passages")
    p.add_argument("pairs_jsonl", metavar="PAIRS_JSONL")
    p.add_argument("out_jsonl", metavar="OUT_JSONL")
    p.add_argument("--model-dir", default=str(BERTCLASSIFY_DIR / "baseline"), dest="model_dir")
    p.add_argument("--batch-size", type=int, default=64, dest="batch_size")
    p.add_argument("--max-length", type=int, default=256, dest="max_length")
    p.add_argument("--device", default="auto")
    return p.parse_args(argv)


def select_device(device_arg: str) -> torch.device:
    if device_arg == "auto":
        if torch.cuda.is_available():
            return torch.device("cuda")
        if torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")
    return torch.device(device_arg)


def load_deberta(model_dir, device: torch.device):
    """Load DeBERTa tokenizer and model from *model_dir*, move to *device*.

    Returns:
        (tokenizer, model) both ready for inference.
    """
    model_dir = Path(model_dir)
    tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
    model = AutoModelForSequenceClassification.from_pretrained(str(model_dir)).to(device)
    return tokenizer, model


def batch_logits(
    texts: list[str],
    model,
    tokenizer,
    device: torch.device,
    batch_size: int,
    max_length: int,
) -> np.ndarray:
    """Return raw logits (shape [N]) for a list of texts."""
    model.eval()
    all_logits = []
    with torch.no_grad():
        for start in range(0, len(texts), batch_size):
            chunk = texts[start : start + batch_size]
            enc = tokenizer(
                chunk,
                padding="max_length",
                truncation=True,
                max_length=max_length,
                return_tensors="pt",
            )
            kwargs = {
                "input_ids": enc["input_ids"].to(device),
                "attention_mask": enc["attention_mask"].to(device),
            }
            if "token_type_ids" in enc:
                kwargs["token_type_ids"] = enc["token_type_ids"].to(device)
            logits = model(**kwargs).logits.squeeze(-1).cpu().float().numpy()
            logits = np.nan_to_num(logits, nan=0.0)
            all_logits.append(logits)
    return np.concatenate(all_logits)


def score_pairs(
    texts_a: list[str],
    texts_b: list[str],
    model,
    tokenizer,
    device: torch.device,
    batch_size: int = 64,
    max_length: int = 256,
) -> list[float]:
    """Compute delta = logit_b - logit_a for each (text_a, text_b) pair.

    Normalizes text via normalize_text before scoring.

    Args:
        texts_a:    reference texts (e.g. ground truth).
        texts_b:    candidate texts (e.g. model answer or distractor).
        model:      loaded AutoModelForSequenceClassification.
        tokenizer:  matching tokenizer.
        device:     torch device.
        batch_size: flat batch size across interleaved a/b texts.
        max_length: tokenizer max length.

    Returns:
        list of float deltas, one per pair.
    """
    assert len(texts_a) == len(texts_b), "texts_a and texts_b must have equal length"
    flat = []
    for a, b in zip(texts_a, texts_b):
        flat.append(normalize_text(a))
        flat.append(normalize_text(b))
    flat_logits = batch_logits(flat, model, tokenizer, device, batch_size, max_length)
    return [float(flat_logits[2 * i + 1]) - float(flat_logits[2 * i]) for i in range(len(texts_a))]


def main(argv=None):
    args = parse_args(argv)

    pairs_path = Path(args.pairs_jsonl)
    if not pairs_path.exists():
        print(f"ERROR: {pairs_path} not found", file=sys.stderr)
        sys.exit(1)

    model_dir = Path(args.model_dir)
    if not model_dir.exists():
        print(f"ERROR: model dir not found: {model_dir}", file=sys.stderr)
        sys.exit(1)

    records = []
    with open(pairs_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    print(f"Loaded {len(records):,} pairs from {pairs_path}")

    device = select_device(args.device)
    print(f"Device: {device}")

    print(f"Loading model from {model_dir} …")
    tokenizer, model = load_deberta(model_dir, device)

    texts_a = [normalize_text(r["text_a"]) for r in records]
    texts_b = [normalize_text(r["text_b"]) for r in records]
    print(f"Running inference on {2 * len(records):,} texts (batch_size={args.batch_size}) …")
    deltas = score_pairs(texts_a, texts_b, model, tokenizer, device, args.batch_size, args.max_length)

    out_path = Path(args.out_jsonl)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        for i, rec in enumerate(records):
            out = dict(rec)
            out["delta"] = deltas[i]
            f.write(json.dumps(out) + "\n")

    print(f"Written {len(records):,} scored pairs → {out_path}")
    deltas_arr = np.array(deltas)
    print(f"delta  mean={deltas_arr.mean():.4f}  std={deltas_arr.std():.4f}  "
          f"min={deltas_arr.min():.4f}  max={deltas_arr.max():.4f}")


if __name__ == "__main__":
    main()

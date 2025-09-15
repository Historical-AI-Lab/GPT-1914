#!/usr/bin/env python3

# ByT5 OCR Correction Fine-Tuning Script

# by Ted Underwood, Claude Opus 4.1, and GPT-5
# Sep 13, 2025

# This script fine-tunes a ByT5 model for OCR text correction using a dataset of noisy and clean text pairs.
# It includes data loading, model training, evaluation, and testing functionalities.

import os
import json
import torch
from torch.utils.data import Dataset
from transformers import (
    T5ForConditionalGeneration,
    AutoTokenizer,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
    DataCollatorForSeq2Seq,
    EarlyStoppingCallback
)
from datasets import Dataset as HFDataset
import numpy as np
from tqdm import tqdm
import logging
from pathlib import Path
import random
import Levenshtein
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

# ---------- Logging ----------
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- Dataset ----------
class OCRDataset(Dataset):
    """Custom dataset for OCR correction pairs"""

    def __init__(self, data_dir, tokenizer, max_length=1024, sample_rate=1.0):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.examples = []

        json_files = list(Path(data_dir).glob("*.json"))
        logger.info(f"Found {len(json_files)} .json files")

        for json_file in tqdm(json_files, desc="Loading data files"):
            with open(json_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        if 'noisy_text' in data and 'clean_text' in data:
                            if random.random() < sample_rate:
                                self.examples.append({
                                    'input_text': data['noisy_text'],
                                    'target_text': data['clean_text']
                                })
                    except json.JSONDecodeError:
                        logger.warning(f"Skipping invalid JSON line in {json_file}")
                        continue

        logger.info(f"Loaded {len(self.examples)} examples")

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        example = self.examples[idx]

        # Tokenize input/target; pad to fixed 1024 for stable compute
        input_encoding = self.tokenizer(
            example['input_text'],
            truncation=True,
            max_length=self.max_length,
            padding='max_length',
            return_tensors='pt'
        )
        target_encoding = self.tokenizer(
            example['target_text'],
            truncation=True,
            max_length=self.max_length,
            padding='max_length',
            return_tensors='pt'
        )

        labels = target_encoding['input_ids'].squeeze(0)
        labels[labels == self.tokenizer.pad_token_id] = -100

        return {
            'input_ids': input_encoding['input_ids'].squeeze(0),
            'attention_mask': input_encoding['attention_mask'].squeeze(0),
            'labels': labels
        }

# ---------- Metrics (CER/BLEU) ----------
def compute_metrics_factory(tokenizer):
    def compute_metrics(eval_preds):
        predictions, labels = eval_preds
        # Seq2SeqTrainer returns logits or generated ids depending on predict_with_generate
        if isinstance(predictions, tuple):
            predictions = predictions[0]
        decoded_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)

        labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
        decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

        total_distance = 0
        total_distance_no_newlines = 0
        total_chars = 0

        for pred, label in zip(decoded_preds, decoded_labels):
            total_distance += Levenshtein.distance(label, pred)
            label_norm = ' '.join(label.split())
            pred_norm = ' '.join(pred.split())
            total_distance_no_newlines += Levenshtein.distance(label_norm, pred_norm)
            total_chars += len(label)

        cer = total_distance / total_chars if total_chars > 0 else 0.0
        cer_no_newlines = total_distance_no_newlines / total_chars if total_chars > 0 else 0.0

        smoothing = SmoothingFunction().method1
        bleu_scores = []
        for pred, label in zip(decoded_preds, decoded_labels):
            ptok, ltok = pred.split(), label.split()
            if ptok and ltok:
                bleu_scores.append(
                    sentence_bleu([ltok], ptok, smoothing_function=smoothing, weights=(0.5, 0.5))
                )
        avg_bleu = float(np.mean(bleu_scores)) if bleu_scores else 0.0

        return {'cer': cer, 'cer_no_newlines': cer_no_newlines, 'accuracy': 1 - cer, 'bleu': avg_bleu}
    return compute_metrics

# ---------- Quick test ----------
def test_ocr_correction(trainer, tokenizer, device):
    test_samples = [
        "Thls is a test wlth some OCR errors.",
        "The quiek brown f0x jumps over the lazy d0g.",
        "Machlne learnlng is very lnteresting!",
        "This is a paragraph that has been\nbroken into multiple lines but\nshould be joined together.",
        "This is the first paragraph.\n\nThis is the second paragraph that\nhas been split but should stay\nas a separate paragraph."
    ]
    model = trainer.model
    model.eval()

    for sample in test_samples:
        inputs = tokenizer(sample, return_tensors="pt", max_length=1024, truncation=True, padding='max_length')
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=1024, num_beams=4, early_stopping=True)
        corrected = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"\nOriginal: {repr(sample)}")
        print(f"Corrected: {repr(corrected)}")

def main():
    import nltk
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)

    # ---------- Config ----------
    config = {
        'model_name': 'yelpfeast/byt5-base-english-ocr-correction',
        'data_dir': './data',
        'output_dir': './ocr_correction_model',
        'max_length': 1024,                    # fixed instance length
        'target_effective_batch': 32,          # sequences per optimizer step
        'adamw_lr': 2e-4,                      # safer for ByT5 at 1024 tokens
        'num_epochs': 2,
        'warmup_steps': 1000,
        'save_steps': 1000,
        'eval_steps': 500,
        'logging_steps': 100,
        'use_cer': False,                      # default to eval loss; set True to use CER
        'use_adafactor': False,                # set True if you want Adafactor for T5 family
        'sample_rate': 0.05,
        'validation_split': 0.05,
        'seed': 42
    }

    # ---------- Seeds ----------
    random.seed(config['seed'])
    np.random.seed(config['seed'])
    torch.manual_seed(config['seed'])

    # ---------- Device / dtype ----------
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"Using device: {device}")
    total_mem_gb = None
    if torch.cuda.is_available():
        props = torch.cuda.get_device_properties(0)
        logger.info(f"GPU: {props.name}")
        total_mem_gb = props.total_memory / (1024 ** 3)
        logger.info(f"GPU Memory: {total_mem_gb:.1f} GB")
        torch.backends.cuda.matmul.allow_tf32 = True

    # ---------- Tokenizer/Model ----------
    logger.info(f"Loading model and tokenizer from {config['model_name']}")
    tokenizer = AutoTokenizer.from_pretrained(config['model_name'])
    tokenizer.model_max_length = config['max_length']
    model = T5ForConditionalGeneration.from_pretrained(config['model_name'])

    # enable grad checkpointing to fit 1024 tokens comfortably
    model.gradient_checkpointing_enable()

    # ---------- Data ----------
    logger.info("Loading dataset...")
    full_dataset = OCRDataset(
        config['data_dir'],
        tokenizer,
        max_length=config['max_length'],
        sample_rate=config['sample_rate']
    )

    if len(full_dataset) == 0:
        raise RuntimeError("No training examples found. Check data_dir and JSONL format.")

    val_size = max(1, int(len(full_dataset) * config['validation_split']))
    train_size = len(full_dataset) - val_size
    if train_size <= 0:
        raise RuntimeError("Validation split too large for dataset size.")

    train_dataset, val_dataset = torch.utils.data.random_split(
        full_dataset,
        [train_size, val_size],
        generator=torch.Generator().manual_seed(config['seed'])
    )
    logger.info(f"Train size: {len(train_dataset)}, Validation size: {len(val_dataset)}")

    # Convert to HF datasets (store as lists to avoid type quirks)
    def dataset_to_dict(ds):
        out = {'input_ids': [], 'attention_mask': [], 'labels': []}
        for i in tqdm(range(len(ds)), desc="Converting dataset"):
            item = ds[i]
            out['input_ids'].append(item['input_ids'].tolist())
            out['attention_mask'].append(item['attention_mask'].tolist())
            out['labels'].append(item['labels'].tolist())
        return out

    train_hf_dataset = HFDataset.from_dict(dataset_to_dict(train_dataset))
    val_hf_dataset = HFDataset.from_dict(dataset_to_dict(val_dataset))

    # ---------- Collator ----------
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        padding=True,
        max_length=config['max_length']
    )

    # ---------- Batch size heuristics ----------
    # conservative defaults; you can override explicitly if you like
    if total_mem_gb is None:
        per_device_bs = 2
    elif total_mem_gb >= 75:
        per_device_bs = 8
    elif total_mem_gb >= 45:
        per_device_bs = 4
    elif total_mem_gb >= 24:
        per_device_bs = 2
    else:
        per_device_bs = 1

    # aim for effective batch ~= target_effective_batch
    grad_accum = max(1, config['target_effective_batch'] // per_device_bs)

    # ---------- Precision ----------
    bf16_ok = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
    fp16_ok = torch.cuda.is_available()
    use_bf16 = bf16_ok
    use_fp16 = (not use_bf16) and fp16_ok

    # ---------- Optimizer choice ----------
    adafactor_flag = config['use_adafactor']
    optim_arg = "adamw_torch" if not adafactor_flag else "adamw_torch"  # ignored when adafactor=True

    # ---------- Training args ----------
    eval_strategy = "steps"
    metric_for_best = "eval_loss"
    greater_is_better = False
    predict_with_generate = False
    gen_kwargs = {}

    compute_metrics = None
    if config['use_cer']:
        compute_metrics = compute_metrics_factory(tokenizer)
        predict_with_generate = True
        metric_for_best = "eval_cer"   # Trainer prefixes "eval_"
        gen_kwargs = dict(generation_max_length=config['max_length'], generation_num_beams=1)

    training_args = Seq2SeqTrainingArguments(
        output_dir=config['output_dir'],
        num_train_epochs=config['num_epochs'],
        per_device_train_batch_size=per_device_bs,
        per_device_eval_batch_size=per_device_bs,
        gradient_accumulation_steps=grad_accum,
        warmup_steps=config['warmup_steps'],
        learning_rate=config['adamw_lr'],
        logging_steps=config['logging_steps'],
        save_steps=config['save_steps'],
        eval_steps=config['eval_steps'],
        evaluation_strategy=eval_strategy,
        save_strategy="steps",
        save_total_limit=3,
        load_best_model_at_end=True,
        metric_for_best_model=metric_for_best,
        greater_is_better=greater_is_better,
        predict_with_generate=predict_with_generate,
        report_to="none",
        push_to_hub=False,
        dataloader_num_workers=8,
        remove_unused_columns=False,
        optim=optim_arg,
        adafactor=adafactor_flag,
        tf32=True,
        dataloader_pin_memory=True,
        group_by_length=False,
        gradient_checkpointing=True,
        fp16=use_fp16,
        bf16=use_bf16,
        **gen_kwargs
    )

    # ---------- Trainer ----------
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_hf_dataset,
        eval_dataset=val_hf_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
    )

    # ---------- Train ----------
    logger.info(
        f"Starting training with per_device_bs={per_device_bs}, grad_accum={grad_accum}, "
        f"effective_batch≈{per_device_bs*grad_accum}, "
        f"{'bf16' if use_bf16 else ('fp16' if use_fp16 else 'fp32')}"
    )
    trainer.train()

    # ---------- Save ----------
    final_dir = f"{config['output_dir']}/final"
    logger.info(f"Saving final model to {final_dir}")
    trainer.save_model(final_dir)
    tokenizer.save_pretrained(final_dir)
    logger.info("Training completed!")

    # ---------- Quick test ----------
    test_ocr_correction(trainer, tokenizer, trainer.args.device)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3

# ByT5 OCR Correction Fine-Tuning Script

# by Ted Underwood, Claude Opus 4.1, and GPT-5
# Sep 13, 2025

# This script fine-tunes a ByT5 model for OCR text correction using a dataset of noisy and clean text pairs.
# It includes data loading, model training, evaluation, and testing functionalities.

import os
import json
from xml.parsers.expat import model
import torch
import transformers  # Added missing import
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
import sacrebleu

# ---------- Logging ----------
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Transformers {transformers.__version__} | Torch {torch.__version__}")

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

# ---------- CER Calculation ----------
def calculate_cer_metrics(predictions, references):
    """Calculate CER metrics between predictions and references"""
    total_dist = total_dist_norm = total_chars = 0
    for pred, ref in zip(predictions, references):
        total_dist += Levenshtein.distance(ref, pred)
        total_dist_norm += Levenshtein.distance(' '.join(ref.split()), ' '.join(pred.split()))
        total_chars += len(ref)
    
    cer = (total_dist / total_chars) if total_chars else 0.0
    cer_no_newlines = (total_dist_norm / total_chars) if total_chars else 0.0
    accuracy = 1 - cer
    
    return {
        "cer": cer, 
        "cer_no_newlines": cer_no_newlines, 
        "accuracy": accuracy,
        "total_chars": total_chars,
        "total_examples": len(predictions)
    }

# ---------- Metrics (CER/BLEU) ----------
def compute_metrics_factory(tokenizer):
    def compute_metrics(eval_preds):
        preds, labels = eval_preds
        if isinstance(preds, tuple): preds = preds[0]
        decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
        labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
        decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

        return calculate_cer_metrics(decoded_preds, decoded_labels)
    return compute_metrics

def evaluate_on_test_set(model, tokenizer, noisy_texts, clean_texts, device, batch_size=8, debug_samples=3):
    """Evaluate model on test set and return metrics"""
    model.eval()
    predictions = []
    
    logger.info(f"Evaluating on {len(noisy_texts)} test examples...")
    
    # Process in batches to avoid memory issues
    for i in tqdm(range(0, len(noisy_texts), batch_size), desc="Generating predictions"):
        batch_noisy = noisy_texts[i:i + batch_size]
        
        # Tokenize batch
        inputs = tokenizer(
            batch_noisy, 
            return_tensors="pt", 
            max_length=1024, 
            truncation=True, 
            padding='max_length'
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate predictions
        with torch.no_grad():
            outputs = model.generate(
                **inputs, 
                max_new_tokens=1024, 
                num_beams=4, 
                early_stopping=False,  # Changed to False
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        
        # Decode predictions
        batch_preds = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        predictions.extend(batch_preds)
        
        # Debug: Show first few examples
        if i == 0 and debug_samples > 0:
            logger.info("=== DEBUG: First few predictions ===")
            for j in range(min(debug_samples, len(batch_noisy))):
                logger.info(f"Example {j+1}:")
                logger.info(f"  Input length: {len(batch_noisy[j])}, Expected length: {len(clean_texts[j])}, Output length: {len(batch_preds[j])}")
                logger.info(f"  Input (first 200 chars): {repr(batch_noisy[j][:200])}")
                logger.info(f"  Expected (first 200 chars): {repr(clean_texts[j][:200])}")
                logger.info(f"  Model output (FULL): {repr(batch_preds[j])}")

                # Calculate CER for this single example
                single_cer = Levenshtein.distance(clean_texts[j], batch_preds[j]) / len(clean_texts[j])
                logger.info(f"  Single example CER: {single_cer:.4f}")
                logger.info(f"  Edit distance: {Levenshtein.distance(clean_texts[j], batch_preds[j])}")
                logger.info("-" * 40)
    
    # Calculate metrics
    metrics = calculate_cer_metrics(predictions, clean_texts)
    
    logger.info(f"Test Results:")
    logger.info(f"  CER: {metrics['cer']:.4f}")
    logger.info(f"  CER (no newlines): {metrics['cer_no_newlines']:.4f}")
    logger.info(f"  Accuracy: {metrics['accuracy']:.4f}")
    
    return metrics, predictions

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
            outputs = model.generate(**inputs, max_new_tokens=1024, num_beams=4, early_stopping=False)
        corrected = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"\nOriginal: {repr(sample)}")
        print(f"Corrected: {repr(corrected)}")

def main():

    # ---------- Config ----------
    config = {
        # 'model_name': 'yelpfeast/byt5-base-english-ocr-correction',
        'model_name': 'google/byt5-base',
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
    
    # Required to avoid the warning when using gradient checkpointing
    model.config.use_cache = False

    # enable grad checkpointing to fit 1024 tokens comfortably
    model.gradient_checkpointing_enable()

    cleanevaltexts = []
    noisyevaltexts = []
    cer = []
    cer_no_newlines = []

    # ---------- Load final test dataset --------- #
    with open('ocrevaldata.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            cleanevaltexts.append(data['clean'])
            noisyevaltexts.append(data['dirty'])
            cer.append(data['cer'])
            cer_no_newlines.append(data['cer_no_newlines'])

    logger.info(f"Loaded {len(cleanevaltexts)} evaluation examples from ocrevaldata.jsonl")
    logger.info(f"  Average CER: {sum(cer)/len(cer):.4f}, Max CER: {max(cer):.4f}")
    logger.info(f"  Average CER (no newlines): {sum(cer_no_newlines)/len(cer_no_newlines):.4f}, Max CER (no newlines): {max(cer_no_newlines):.4f}")

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
        padding=False  # already padded to max_length in dataset
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
        gen_kwargs = dict(generation_max_new_tokens=config['max_length'], generation_num_beams=1)

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
        eval_strategy=eval_strategy,
        save_strategy="steps",
        save_total_limit=3,
        load_best_model_at_end=True,
        metric_for_best_model=metric_for_best,
        greater_is_better=greater_is_better,
        predict_with_generate=predict_with_generate,
        report_to="none",
        push_to_hub=False,
        dataloader_num_workers=4,
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
        processing_class=tokenizer,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
    )

    # ---------- Evaluate initial model ----------
    logger.info("=" * 50)
    logger.info("Evaluating INITIAL model on test set...")
    initial_metrics, initial_predictions = evaluate_on_test_set(
        model, tokenizer, noisyevaltexts, cleanevaltexts, device, batch_size=per_device_bs
    )

    logger.info(f'Initial CER: {initial_metrics["cer"]:.4f}, CER (no newlines): {initial_metrics["cer_no_newlines"]:.4f}')

    # ---------- Train ----------
    logger.info(
        f"Starting training with per_device_bs={per_device_bs}, grad_accum={grad_accum}, "
        f"effective_batch≈{per_device_bs*grad_accum}, "
        f"{'bf16' if use_bf16 else ('fp16' if use_fp16 else 'fp32')}"
    )
    trainer.train()

    # ---------- Evaluate fine-tuned model ----------
    logger.info("=" * 50)
    logger.info("Evaluating FINE-TUNED model on test set...")
    final_metrics, final_predictions = evaluate_on_test_set(
        trainer.model, tokenizer, noisyevaltexts, cleanevaltexts, trainer.args.device, batch_size=per_device_bs
    )
    
    # Compare results
    logger.info("=" * 50)
    logger.info("COMPARISON:")
    logger.info(f"Initial CER: {initial_metrics['cer']:.4f} -> Final CER: {final_metrics['cer']:.4f}")
    logger.info(f"CER improvement: {initial_metrics['cer'] - final_metrics['cer']:.4f}")
    logger.info(f"Initial CER (no newlines): {initial_metrics['cer_no_newlines']:.4f} -> Final CER (no newlines): {final_metrics['cer_no_newlines']:.4f}")
    logger.info(f"CER (no newlines) improvement: {initial_metrics['cer_no_newlines'] - final_metrics['cer_no_newlines']:.4f}") 

    # ---------- Save ----------
    final_dir = f"{config['output_dir']}/final"
    logger.info(f"Saving final model to {final_dir}")
    trainer.save_model(final_dir)
    tokenizer.save_pretrained(final_dir)
    
    # Save evaluation results
    eval_results = {
        'initial_metrics': initial_metrics,
        'final_metrics': final_metrics,
        'improvement': {
            'cer_reduction': initial_metrics['cer'] - final_metrics['cer'],
            'accuracy_gain': final_metrics['accuracy'] - initial_metrics['accuracy']
        }
    }
    
    results_path = f"{config['output_dir']}/evaluation_results.json"
    with open(results_path, 'w') as f:
        json.dump(eval_results, f, indent=2)
    logger.info(f"Evaluation results saved to {results_path}")
    logger.info("Training completed!")

    # ---------- Quick test not needed ----------
    # test_ocr_correction(trainer, tokenizer, trainer.args.device)

if __name__ == "__main__":
    main()
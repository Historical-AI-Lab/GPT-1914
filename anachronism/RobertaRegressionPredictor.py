# Roberta Regression Prediction Script

import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from tqdm import tqdm
import logging
import argparse
import os
from datetime import datetime
from torch import nn
from transformers import RobertaTokenizer, RobertaModel, RobertaPreTrainedModel

class RobertaForRegression(RobertaPreTrainedModel):
    """RoBERTa model with a regression head."""
    def __init__(self, config):
        super().__init__(config)
        self.roberta = RobertaModel(config)
        self.regression = nn.Sequential(
            nn.Linear(config.hidden_size, config.hidden_size),
            nn.GELU(),
            nn.Dropout(config.hidden_dropout_prob),
            nn.Linear(config.hidden_size, 1)
        )
        self.init_weights()

    def forward(self, input_ids=None, attention_mask=None, labels=None):
        outputs = self.roberta(input_ids=input_ids, attention_mask=attention_mask)
        sequence_output = outputs[0]
        pooled_output = sequence_output[:, 0, :]  # Use [CLS] token state
        logits = self.regression(pooled_output)

        loss = None
        if labels is not None:
            loss_fct = nn.MSELoss()
            loss = loss_fct(logits.view(-1), labels.view(-1))

        return {'loss': loss, 'logits': logits} if loss is not None else {'logits': logits}

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Apply fine-tuned RoBERTa model for year prediction')
    parser.add_argument('--model', '-m', type=str, required=True,
                       help='Path to the fine-tuned model checkpoint')
    parser.add_argument('--data', '-d', type=str, required=True,
                       help='Path to the input data file (TSV format)')
    parser.add_argument('--output', '-o', type=str, required=True,
                       help='Path to save predictions TSV file')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size for prediction')
    return parser.parse_args()

def setup_logging():
    """Setup basic logging to console."""
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    return logging.getLogger(__name__)

class TextRegressionDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]

        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'label': torch.tensor(label, dtype=torch.float32)
        }

def get_device():
    """Determine the best available device."""
    if torch.cuda.is_available():
        return torch.device('cuda')
    elif torch.backends.mps.is_available() and torch.backends.mps.is_built():
        return torch.device('mps')
    else:
        return torch.device('cpu')

def make_predictions(model, dataloader, device):
    """Make predictions using the model."""
    model.eval()
    predictions = []
    true_labels = []
    
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Making predictions"):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label']

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask
            )

            preds = outputs['logits'].view(-1)
            predictions.extend(preds.cpu().numpy())
            true_labels.extend(labels.cpu().numpy())

    return predictions, true_labels

def calculate_metrics(predictions, true_labels):
    """Calculate regression metrics."""
    predictions = np.array(predictions)
    true_labels = np.array(true_labels)
    
    mse = np.mean((predictions - true_labels) ** 2)
    mae = np.mean(np.abs(predictions - true_labels))
    rmse = np.sqrt(mse)
    
    return {
        'mse': mse,
        'rmse': rmse,
        'mae': mae
    }

def main():
    # Parse arguments and setup logging
    args = parse_args()
    logger = setup_logging()
    
    # Setup device
    DEVICE = get_device()
    logger.info(f"Using device: {DEVICE}")
    if DEVICE.type == 'cuda':
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
    elif DEVICE.type == 'mps':
        logger.info("Using Apple Silicon GPU")
    
    # Load the data
    logger.info(f"Loading data from {args.data}")
    df = pd.read_csv(args.data, sep='\t')
    
    # Initialize tokenizer and model
    logger.info("Loading model and tokenizer")
    tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
    model = RobertaForRegression.from_pretrained('roberta-base')
    
    # Load the fine-tuned model weights
    checkpoint = torch.load(args.model, map_location=DEVICE)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(DEVICE)
    
    # Create dataset and dataloader
    dataset = TextRegressionDataset(
        df['text'].values,
        df['label'].values,
        tokenizer
    )
    
    dataloader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        num_workers=4 if DEVICE.type in ['cuda', 'mps'] else 0,
        pin_memory=True if DEVICE.type in ['cuda', 'mps'] else False
    )
    
    # Make predictions
    logger.info("Making predictions")
    predictions, true_labels = make_predictions(model, dataloader, DEVICE)
    
    # Calculate metrics
    metrics = calculate_metrics(predictions, true_labels)
    logger.info(f"MSE: {metrics['mse']:.4f}")
    logger.info(f"RMSE: {metrics['rmse']:.4f}")
    logger.info(f"MAE: {metrics['mae']:.4f}")
    
    # Add predictions to dataframe and save
    df['prediction'] = predictions
    logger.info(f"Saving predictions to {args.output}")
    df.to_csv(args.output, sep='\t', index=False)
    
    logger.info("Done!")

if __name__ == "__main__":
    main()
# FineTune RoBERTa for Publication Year Prediction

# code by Claude sonnet

import torch
from torch.utils.data import Dataset, DataLoader, random_split
from transformers import RobertaTokenizer, RobertaPreTrainedModel, RobertaModel
from transformers import AdamW, get_linear_schedule_with_warmup
import pandas as pd
import numpy as np
from tqdm import tqdm
import logging
import time
import platform
import argparse
import os
from datetime import datetime
from torch import nn

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
    parser = argparse.ArgumentParser(description='Fine-tune RoBERTa for year prediction')
    parser.add_argument('--data', '-d', type=str, default='data.tsv',
                       help='Path to the input data file (TSV format)')
    parser.add_argument('--log-dir', type=str, default='logs',
                       help='Directory for log files')
    parser.add_argument('--output-dir', type=str, default='models',
                       help='Directory for saving model checkpoints')
    return parser.parse_args()

def setup_logging(log_dir):
    """Setup logging to both file and console."""
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'training_{timestamp}.log')
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Setup file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    logging.info(f"Logging to: {log_file}")
    return logging.getLogger(__name__)

class TextRegressionDataset(Dataset):
    def __init__(self, texts, years, tokenizer, max_length=128):
        self.texts = texts
        self.years = years
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        year = self.years[idx]

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
            'label': torch.tensor(year, dtype=torch.float32)  # Use float for regression
        }

def get_device():
    """Determine the best available device."""
    if torch.cuda.is_available():
        return torch.device('cuda')
    elif torch.backends.mps.is_available() and torch.backends.mps.is_built():
        return torch.device('mps')
    else:
        return torch.device('cpu')

def load_data(file_path):
    """Load data from tab-separated file."""
    df = pd.read_csv(file_path, sep='\t')
    return df['text'].values, df['label'].values.astype(float)  # Convert years to float

def train_epoch(model, dataloader, optimizer, scheduler, device):
    """Train for one epoch."""
    model.train()
    total_loss = 0
    num_batches = len(dataloader)

    for batch in tqdm(dataloader, desc="Training"):
        optimizer.zero_grad()
        
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['label'].to(device)

        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )

        loss = outputs['loss']
        total_loss += loss.item()

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()

    return total_loss / num_batches

def evaluate(model, dataloader, device):
    """Evaluate model on given dataloader."""
    model.eval()
    total_mse = 0
    total_mae = 0
    num_samples = 0

    predictions = []
    true_values = []

    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating"):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask
            )

            logits = outputs['logits'].view(-1)
            predictions.extend(logits.cpu().numpy())
            true_values.extend(labels.cpu().numpy())

    predictions = np.array(predictions)
    true_values = np.array(true_values)
    
    mse = np.mean((predictions - true_values) ** 2)
    mae = np.mean(np.abs(predictions - true_values))
    rmse = np.sqrt(mse)

    return {
        'mse': mse,
        'rmse': rmse,
        'mae': mae
    }

def main():
    # Parse command line arguments
    args = parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_dir)
    
    # Setup directories
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Get the appropriate device
    DEVICE = get_device()
    logger.info(f"Using device: {DEVICE}")
    if DEVICE.type == 'cuda':
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
    elif DEVICE.type == 'mps':
        logger.info("Using Apple Silicon GPU")
    
    # Configuration
    MAX_LENGTH = 128
    BATCH_SIZE = 32
    EPOCHS = 20
    LEARNING_RATE = 2e-5
    WARMUP_STEPS = 0
    PATIENCE = 3  # Number of epochs to wait before early stopping
    
    # Load and prepare data
    logger.info("Loading data...")
    texts, years = load_data(args.data)
    
    # Initialize tokenizer and model
    tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
    model = RobertaForRegression.from_pretrained('roberta-base')
    model = model.to(DEVICE)

    # Create dataset
    dataset = TextRegressionDataset(texts, years, tokenizer, MAX_LENGTH)
    
    # Split dataset
    train_size = 21000
    test_size = len(dataset) - train_size
    train_dataset, test_dataset = random_split(
        dataset, 
        [train_size, test_size],
        generator=torch.Generator().manual_seed(42)
    )

    # Create dataloaders
    train_dataloader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=4 if DEVICE.type in ['cuda', 'mps'] else 0,
        pin_memory=True if DEVICE.type in ['cuda', 'mps'] else False
    )
    test_dataloader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        num_workers=4 if DEVICE.type in ['cuda', 'mps'] else 0,
        pin_memory=True if DEVICE.type in ['cuda', 'mps'] else False
    )

    # Prepare optimizer and scheduler
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)
    total_steps = len(train_dataloader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=WARMUP_STEPS,
        num_training_steps=total_steps
    )

    # Training loop
    logger.info("Starting training...")
    best_rmse = float('inf')
    no_improvement = 0
    training_start_time = time.time()
    
    for epoch in range(EPOCHS):
        epoch_start_time = time.time()
        logger.info(f"Epoch {epoch + 1}/{EPOCHS}")
        
        # Train
        avg_loss = train_epoch(model, train_dataloader, optimizer, scheduler, DEVICE)
        logger.info(f"Average training loss: {avg_loss:.4f}")
        
        # Evaluate
        metrics = evaluate(model, test_dataloader, DEVICE)
        epoch_time = time.time() - epoch_start_time
        logger.info(f"Test MSE: {metrics['mse']:.4f}")
        logger.info(f"Test RMSE: {metrics['rmse']:.4f}")
        logger.info(f"Test MAE: {metrics['mae']:.4f}")
        logger.info(f"Epoch completed in {epoch_time:.2f} seconds")
        
        # Early stopping check based on RMSE
        if metrics['rmse'] < best_rmse - 0.1:  # 0.1 year improvement threshold
            best_rmse = metrics['rmse']
            no_improvement = 0
            # Save best model
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'metrics': metrics,
            }, os.path.join(args.output_dir, 'best_model.pt'))
            logger.info(f"Saved new best model with RMSE: {best_rmse:.4f}")
        else:
            no_improvement += 1
            
        if no_improvement >= PATIENCE:
            logger.info(f"Early stopping triggered after epoch {epoch + 1}")
            break
    
    total_time = time.time() - training_start_time
    logger.info(f"Training completed in {total_time:.2f} seconds")
    logger.info(f"Best test RMSE: {best_rmse:.4f}")

if __name__ == "__main__":
    main()
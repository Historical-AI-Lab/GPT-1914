#!/usr/bin/env python3
"""
header_inference.py
Module for applying trained RoBERTa model to new pages for header/footer removal.

Usage:
    import header_inference
    
    # Load model once
    header_inference.load_model("./header_model")
    
    # Run inference on new pages
    filtered_pages = header_inference.run_inference(pages, batch_size=16)
"""

import json
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
from transformers import RobertaTokenizerFast, RobertaModel, RobertaConfig
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from tqdm import tqdm
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global storage for loaded model and tokenizer
_model = None
_tokenizer = None
_device = None
_model_config = None


class RobertaWithMetadataTags(nn.Module):
    """
    RoBERTa model with learnable metadata tag embeddings.
    Tag embeddings are added to token embeddings before processing.
    """
    
    def __init__(self, model_name: str = "roberta-base", num_labels: int = 2, 
                 tag_embedding_dim: int = 32, dropout: float = 0.1, metadata_std: float = 0.08):
        super().__init__()
        
        self.config = RobertaConfig.from_pretrained(model_name)
        self.roberta = RobertaModel.from_pretrained(model_name)
        self.hidden_size = self.config.hidden_size
        
        # Define our metadata tags
        self.tag_names = ["short_line", "early_caps_num", "late_caps_num", "repeated_line", "drop", "uppercase",  
                          "first10", "first05", "last15", "header", "footnote", "capitalized", "nonalphabetic"]
        self.num_tags = len(self.tag_names)
        
        # Create tag embeddings (32-dim) and projection to hidden size
        self.tag_embeddings = nn.Embedding(self.num_tags, tag_embedding_dim)
        self.tag_projection = nn.Linear(tag_embedding_dim, self.hidden_size)
        
        # Classification head
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(self.hidden_size, num_labels)
        
        # Initialize tag embeddings with configurable magnitude
        with torch.no_grad():
            self.tag_embeddings.weight.normal_(mean=0.0, std=metadata_std)
            nn.init.xavier_uniform_(self.tag_projection.weight)
            self.tag_projection.bias.zero_()
    
    def create_tag_tensor(self, metadata_tags_batch: List[List[List[str]]], batch_size: int, seq_len: int, device):
        """
        Convert metadata tags to tensor for embedding lookup.
        """
        # Create binary tensor for tag presence
        tag_tensor = torch.zeros(batch_size, seq_len, self.num_tags, device=device)
        
        for batch_idx, sequence in enumerate(metadata_tags_batch):
            # Ensure we don't exceed the actual sequence length
            actual_seq_len = min(len(sequence), seq_len)
            for seq_idx in range(actual_seq_len):
                tags = sequence[seq_idx] if seq_idx < len(sequence) else []
                for tag in tags:
                    if tag in self.tag_names:
                        tag_idx = self.tag_names.index(tag)
                        tag_tensor[batch_idx, seq_idx, tag_idx] = 1.0
        
        return tag_tensor
    
    def forward(self, input_ids, attention_mask, metadata_tags_batch, labels=None, class_weights=None):
        """
        Forward pass with metadata tag embeddings added to token embeddings.
        """
        batch_size, seq_len = input_ids.shape
        device = input_ids.device
        
        # Get token embeddings from RoBERTa embedding layer
        token_embeddings = self.roberta.embeddings.word_embeddings(input_ids)
        
        # Create tag embeddings
        tag_binary = self.create_tag_tensor(metadata_tags_batch, batch_size, seq_len, device)
        
        # Get tag embeddings and project to hidden size
        tag_embeds = self.tag_embeddings.weight  # [num_tags, tag_embedding_dim]
        tag_embeds_projected = self.tag_projection(tag_embeds)  # [num_tags, hidden_size]
        
        # Apply tags: sum over active tags for each position
        tag_contributions = torch.matmul(tag_binary, tag_embeds_projected)  # [B, S, hidden_size]
        
        # Add tag embeddings to token embeddings
        enhanced_embeddings = token_embeddings + tag_contributions
        
        # Continue with RoBERTa processing
        position_embeddings = self.roberta.embeddings.position_embeddings(
            torch.arange(seq_len, device=device).expand(batch_size, -1)
        )
        token_type_embeddings = self.roberta.embeddings.token_type_embeddings(
            torch.zeros_like(input_ids)
        )
        
        # Complete embedding
        embeddings = enhanced_embeddings + position_embeddings + token_type_embeddings
        embeddings = self.roberta.embeddings.LayerNorm(embeddings)
        embeddings = self.roberta.embeddings.dropout(embeddings)
        
        # Pass through encoder
        extended_attention_mask = self.roberta.get_extended_attention_mask(attention_mask, input_ids.shape)
        encoder_outputs = self.roberta.encoder(embeddings, attention_mask=extended_attention_mask)
        sequence_output = encoder_outputs.last_hidden_state
        
        # Classification
        sequence_output = self.dropout(sequence_output)
        logits = self.classifier(sequence_output)
        
        loss = None
        if labels is not None:
            # Use class weights if provided
            if class_weights is not None:
                loss_fct = nn.CrossEntropyLoss(weight=class_weights)
            else:
                loss_fct = nn.CrossEntropyLoss()
            # Flatten for loss calculation
            active_loss = attention_mask.view(-1) == 1
            active_logits = logits.view(-1, 2)[active_loss]
            active_labels = labels.view(-1)[active_loss]
            loss = loss_fct(active_logits, active_labels)
        
        return {"loss": loss, "logits": logits}


class InferenceDataset(Dataset):
    """Dataset for inference with metadata tags and alignment tracking"""
    
    def __init__(self, sequences: List[Dict], tokenizer, max_length: int = 512, alignment_maps: List[List[Dict]] = None):
        self.sequences = sequences
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.alignment_maps = alignment_maps or [None] * len(sequences)
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        sequence = self.sequences[idx]
        alignment_map = self.alignment_maps[idx]
        
        # Make copies to avoid modifying the original sequence data
        tokens = sequence['tokens'].copy()
        metadata_tags = sequence['metadata_tags'].copy()
        if alignment_map:
            alignment_map = alignment_map.copy()
        
        # Convert to token IDs
        token_ids = [self.tokenizer.convert_tokens_to_ids(token) for token in tokens]
        
        # Truncate to max_length if needed
        if len(token_ids) > self.max_length:
            token_ids = token_ids[:self.max_length]
            metadata_tags = metadata_tags[:self.max_length]
            if alignment_map:
                alignment_map = alignment_map[:self.max_length]
        
        # Pad sequences
        padding_length = self.max_length - len(token_ids)
        token_ids.extend([self.tokenizer.pad_token_id] * padding_length)
        metadata_tags.extend([[] for _ in range(padding_length)])
        if alignment_map:
            alignment_map.extend([None] * padding_length)
        
        # Create attention mask
        attention_mask = [1 if token_id != self.tokenizer.pad_token_id else 0 
                         for token_id in token_ids]
        
        result = {
            'input_ids': torch.tensor(token_ids, dtype=torch.long),
            'attention_mask': torch.tensor(attention_mask, dtype=torch.long),
            'metadata_tags': metadata_tags
        }
        
        # Include alignment map if available
        if alignment_map:
            result['alignment_map'] = alignment_map
            
        return result


def custom_collate_fn(batch):
    """Custom collate function to handle metadata_tags and alignment_maps"""
    input_ids = torch.stack([item['input_ids'] for item in batch])
    attention_mask = torch.stack([item['attention_mask'] for item in batch])
    
    # Keep metadata_tags as a list of lists (can't be tensorized)
    metadata_tags = [item['metadata_tags'] for item in batch]
    
    result = {
        'input_ids': input_ids,
        'attention_mask': attention_mask,
        'metadata_tags': metadata_tags
    }
    
    # Include alignment maps if available
    if 'alignment_map' in batch[0]:
        alignment_maps = [item['alignment_map'] for item in batch]
        result['alignment_maps'] = alignment_maps
    
    return result


def create_sequences_with_book_boundaries(pages: List[Dict], max_seq_length: int = 512):
    """
    Create sequences from pages, respecting book boundaries.
    No sequence will span multiple books.
    """
    # Group pages by book
    books = defaultdict(list)
    for page in pages:
        books[page['source_file']].append(page)
    
    # Sort pages within each book
    for source_file in books:
        books[source_file].sort(key=lambda x: x['page_number'])
    
    all_sequences = []
    all_alignment_maps = []
    
    # Process each book separately
    for source_file, book_pages in books.items():
        book_tokens = []
        book_metadata = []
        book_alignment = []
        
        # Concatenate all data from this book
        for page in book_pages:
            page_tokens = page['tokens']
            page_metadata = page['metadata_tags']
            
            # Validate page data consistency
            if len(page_tokens) != len(page_metadata):
                logger.error(f"Page {page['page_number']} in {page['source_file']} has mismatched lengths")
                continue
            
            # Add all tokens from this page
            book_tokens.extend(page_tokens)
            book_metadata.extend(page_metadata)
            
            # Track alignment
            for token_idx in range(len(page_tokens)):
                book_alignment.append({
                    'source_file': page['source_file'],
                    'page_number': page['page_number'],
                    'token_index': token_idx,
                    'original_token': page_tokens[token_idx]
                })
        
        # Create sequences for this book
        start_idx = 0
        while start_idx < len(book_tokens):
            end_idx = min(start_idx + max_seq_length, len(book_tokens))
            
            sequence = {
                'tokens': book_tokens[start_idx:end_idx],
                'metadata_tags': book_metadata[start_idx:end_idx]
            }
            
            all_sequences.append(sequence)
            
            alignment_chunk = book_alignment[start_idx:end_idx]
            all_alignment_maps.append(alignment_chunk)
            
            start_idx = end_idx
    
    return all_sequences, all_alignment_maps


def reconstruct_filtered_pages(alignments_with_predictions, original_pages):
    """
    Reconstruct pages with only KEEP tokens retained.
    """
    # Group alignments by (source_file, page_number)
    page_alignments = defaultdict(list)
    for alignment in alignments_with_predictions:
        key = (alignment['source_file'], alignment['page_number'])
        page_alignments[key].append(alignment)
    
    # Sort alignments within each page by token_index
    for key in page_alignments:
        page_alignments[key].sort(key=lambda x: x['token_index'])
    
    # Create a mapping of original pages for easy lookup
    original_page_map = {}
    for page in original_pages:
        key = (page['source_file'], page['page_number'])
        original_page_map[key] = page
    
    filtered_pages = []
    
    for key, page_alignment_list in page_alignments.items():
        source_file, page_number = key
        
        if key not in original_page_map:
            logger.warning(f"Could not find original page for {source_file}, page {page_number}")
            continue
            
        original_page = original_page_map[key]
        
        # Collect only KEEP tokens
        keep_tokens = []
        
        for alignment in page_alignment_list:
            if alignment['predicted_label'] == 'KEEP':
                token_idx = alignment['token_index']
                if 0 <= token_idx < len(original_page['tokens']):
                    keep_tokens.append(original_page['tokens'][token_idx])
        
        # Create filtered page
        filtered_page = {
            'source_file': source_file,
            'page_number': page_number,
            'tokens': keep_tokens
        }
        
        filtered_pages.append(filtered_page)
    
    # Sort pages by source_file and page_number
    filtered_pages.sort(key=lambda x: (x['source_file'], x['page_number']))
    
    return filtered_pages


def load_model(model_dir: str):
    """
    Load the trained model and tokenizer from a directory.
    This should be called once after importing the module.
    
    Args:
        model_dir: Directory containing pytorch_model.bin, tokenizer files, and training_config.json
    """
    global _model, _tokenizer, _device, _model_config
    
    # Set device
    if torch.backends.mps.is_available():
        _device = torch.device("mps")
        logger.info("Using MPS (Apple Silicon)")
    elif torch.cuda.is_available():
        _device = torch.device("cuda")
        logger.info("Using CUDA")
    else:
        _device = torch.device("cpu")
        logger.info("Using CPU")
    
    # Load configuration
    config_path = f"{model_dir}/training_config.json"
    with open(config_path, 'r') as f:
        _model_config = json.load(f)
    
    # Load tokenizer
    logger.info(f"Loading tokenizer from {model_dir}")
    _tokenizer = RobertaTokenizerFast.from_pretrained(model_dir)
    
    # Initialize model
    logger.info(f"Loading model from {model_dir}")
    model_name = _model_config.get('model_name', 'roberta-base')
    hyperparams = _model_config.get('hyperparameters', {})
    
    _model = RobertaWithMetadataTags(
        model_name=model_name,
        metadata_std=hyperparams.get('metadata_std', 0.08),
        dropout=hyperparams.get('dropout', 0.1)
    )
    
    # Load model weights
    model_path = f"{model_dir}/pytorch_model.bin"
    state_dict = torch.load(model_path, map_location=_device)
    _model.load_state_dict(state_dict)
    _model.to(_device)
    _model.eval()
    
    logger.info("Model loaded successfully")


def run_inference(pages: List[Dict], batch_size: int = 16) -> List[Dict]:
    """
    Run inference on a list of pages and return filtered pages with only KEEP tokens.
    
    Args:
        pages: List of page dictionaries with 'source_file', 'page_number', 'tokens', 'metadata_tags'
        batch_size: Batch size for inference
        
    Returns:
        List of filtered page dictionaries with only KEEP tokens
    """
    global _model, _tokenizer, _device, _model_config
    
    if _model is None or _tokenizer is None:
        raise RuntimeError("Model not loaded. Please call load_model() first.")
    
    logger.info(f"Running inference on {len(pages)} pages")
    
    # Get max sequence length from config
    max_seq_length = _model_config.get('max_seq_length', 512)
    
    # Create sequences respecting book boundaries
    sequences, alignment_maps = create_sequences_with_book_boundaries(pages, max_seq_length)
    logger.info(f"Created {len(sequences)} sequences for inference")
    
    # Create dataset and dataloader
    dataset = InferenceDataset(sequences, _tokenizer, max_seq_length, alignment_maps)
    dataloader = DataLoader(
        dataset, 
        batch_size=batch_size, 
        shuffle=False, 
        collate_fn=custom_collate_fn
    )
    
    # Run inference
    all_alignments_with_predictions = []
    
    _model.eval()
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Running inference"):
            input_ids = batch['input_ids'].to(_device)
            attention_mask = batch['attention_mask'].to(_device)
            metadata_tags = batch['metadata_tags']
            alignment_maps = batch['alignment_maps']
            
            # Get model predictions
            outputs = _model(input_ids, attention_mask, metadata_tags)
            logits = outputs["logits"]
            predictions = torch.argmax(logits, dim=-1)
            
            # Process each item in the batch
            batch_size_actual = input_ids.shape[0]
            for batch_idx in range(batch_size_actual):
                item_attention_mask = attention_mask[batch_idx]
                item_predictions = predictions[batch_idx]
                alignment_map = alignment_maps[batch_idx]
                
                # Collect predictions with alignment info
                for pos_idx in range(len(item_attention_mask)):
                    if item_attention_mask[pos_idx] == 1 and alignment_map[pos_idx] is not None:
                        alignment_info = alignment_map[pos_idx].copy()
                        alignment_info['predicted_label'] = 'KEEP' if item_predictions[pos_idx].cpu().item() == 0 else 'DROP'
                        all_alignments_with_predictions.append(alignment_info)
    
    # Reconstruct filtered pages
    filtered_pages = reconstruct_filtered_pages(all_alignments_with_predictions, pages)
    
    logger.info(f"Inference complete. Processed {len(filtered_pages)} pages")
    
    return filtered_pages


# Example usage in docstring
"""
Example usage:
    
    # Import the module
    import roberta_inference
    
    # Load the model once
    roberta_inference.load_model("./roberta_model")
    
    # Prepare your pages data
    pages = [
        {
            'source_file': 'book1.pdf',
            'page_number': 1,
            'tokens': ['This', 'is', 'a', 'header', '.', 'Main', 'content', 'here', '.'],
            'metadata_tags': [[], [], [], ['header'], [], [], [], [], []]
        },
        # ... more pages
    ]
    
    # Run inference
    filtered_pages = roberta_inference.run_inference(pages, batch_size=16)
    
    # Each filtered page will have only KEEP tokens:
    # {
    #     'source_file': 'book1.pdf',
    #     'page_number': 1,
    #     'tokens': ['Main', 'content', 'here', '.']
    # }
"""
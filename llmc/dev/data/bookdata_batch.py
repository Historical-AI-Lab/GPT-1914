import os, sys
import argparse
import multiprocessing as mp
from pathlib import Path
import psutil
import gc
import logging
from dataclasses import dataclass
from typing import List, Optional

import pandas as pd
import numpy as np
import tiktoken
from tqdm import tqdm
from transformers import AutoTokenizer

from data_common import write_datafile

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocumentMetadata:
    path: str
    size_bytes: int
    
def get_document_paths(input_dir: str, holdout_docs: set, file_pattern: str = "*") -> List[DocumentMetadata]:
    """Returns list of documents with their metadata"""
    paths = Path(input_dir).glob(f"**/{file_pattern}")

    # Filter out holdout documents by filename:
    # specifically, we find the filename part of the path
    # and remove ".trim.tsv" from the end, then check if
    # the resulting filename is in the holdout set.

    paths = [p for p in paths if os.path.basename(p).replace(".trim.tsv", "") not in holdout_docs]

    return [
        DocumentMetadata(
            path=str(p),
            size_bytes=p.stat().st_size
        )
        for p in paths
    ]

def estimate_batch_size(doc_sizes: List[int], available_memory: int, 
                       safety_factor: float = 0.5) -> int:
    """
    Estimate how many documents we can process in parallel given memory constraints.
    
    Args:
        doc_sizes: List of document sizes in bytes
        available_memory: Available memory in bytes
        safety_factor: Fraction of available memory to actually use (0.0 to 1.0)
    """
    if not doc_sizes:
        return 1
        
    # Estimate memory multiplication factor from text to tokens
    # (includes both raw text and tokenized arrays)
    mem_factor = 6  # Conservative estimate: 2-3x for tokenization + buffer
    
    # Calculate median document size
    median_size = np.median(doc_sizes)
    estimated_max_memory_per_doc = median_size * mem_factor
    
    # Calculate batch size
    safe_memory = available_memory * safety_factor
    batch_size = max(1, int(safe_memory / estimated_max_memory_per_doc))
    
    return batch_size

def only_final_newline(s):
    """Checks for a final newline, replaces all newlines with spaces,
    and adds a final newline if one was present."""
    if s.endswith("\n"):
        return s.replace("\n", " ").replace("  ", " ") + "\n"
    else:
        return s.replace("\n", " ").replace("  ", " ") + " "

def read_and_tokenize_document(args):
    """Reads and tokenizes a single document"""
    path, model_desc = args

    try:
        # Read document
        
        text_df = pd.read_csv(path, sep='\t')
        # we construct the text by concatenating the strings in the
        # 'sentence' column, with two rules: We remove any '\n'
        # characters within the sentence, but allow an '\n' at the end
        # if one is present. If not present, we add a space at the end.

        text = "".join(text_df['sentence'].apply(only_final_newline))

        # Tokenize based on model type
        if model_desc == "gpt-2":
            enc = tiktoken.get_encoding("gpt2")
            encode = lambda s: enc.encode_ordinary(s)
            eot = enc._special_tokens['<|endoftext|>']
            tokens = [eot]
            tokens.extend(encode(text))
            tokens_np = np.array(tokens, dtype=np.uint16)
        else:  # llama-3
            tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3.1-8B")
            encode = lambda s: tokenizer.encode(s, add_special_tokens=False)
            eot = tokenizer.encode('')[0]
            tokens = [eot]
            tokens.extend(encode(text))
            tokens_np = np.array(tokens, dtype=np.uint32)
            
        # Force garbage collection after processing large document
        del text
        print(path, flush = True)
        gc.collect()
        
        return tokens_np
        
    except Exception as e:
        logger.error(f"Error processing {path}: {str(e)}")
        return None

def calculate_safe_memory_settings(total_memory: int, num_cores: int, 
                                 reserve_memory: float = 0.2) -> tuple[int, float]:
    """
    Calculate safe memory fraction and resulting batch size based on core count.
    
    Args:
        total_memory: Total available system memory in bytes
        num_cores: Number of CPU cores to use
        reserve_memory: Fraction of memory to reserve for system (0.0 to 1.0)
    
    Returns:
        tuple of (num_cores_to_use, memory_fraction_per_core)
    """
    # Reserve some memory for the system and other processes
    available_memory = total_memory * (1 - reserve_memory)
    
    # Calculate safe memory fraction per core
    safe_fraction_per_core = 1.0 / num_cores
    
    # If this would use too much memory, reduce core count
    if (safe_fraction_per_core * num_cores * total_memory) > available_memory:
        adjusted_cores = max(1, int(available_memory / (total_memory * safe_fraction_per_core)))
        safe_fraction_per_core = 1.0 / adjusted_cores
        return adjusted_cores, safe_fraction_per_core
    
    return num_cores, safe_fraction_per_core

def process_documents(input_dir: str, output_dir: str, holdout_docs: set,
                     batch_file: str,
                     model_desc: str = "gpt-2",
                     shard_size: int = 10**8,
                     requested_cores: Optional[int] = None,
                     file_pattern: str = "*") -> None:
    """
    Process documents with memory-aware batching and core-aware memory management
    """
    # Setup
    os.makedirs(output_dir, exist_ok=True)
    
    # Get document information
    # in the batch version of this script, we read the list of filenames from a file
    # and then use that to get the document paths by concatenating the input_dir
    with open(batch_file, 'r') as f:
        filenames = f.readlines()
    filenames = [x.strip() for x in filenames]
    print(len(filenames), 'files in batch file', flush=True)
    newfilenames = []
    for filename in filenames:
        if filename in holdout_docs or filename.replace('.trim.tsv', '') in holdout_docs:
            print('Held out:', filename, flush=True)
            continue
        else:
            newfilenames.append(filename)
    print(len(newfilenames), 'files to process', flush=True)
    filenames = newfilenames
    docs = [os.path.join(input_dir, x) for x in filenames]
    total_docs = len(docs)
    logger.info(f"Found {total_docs} documents to process")
    
    # Calculate safe processing settings
    available_memory = psutil.virtual_memory().available
    max_cores = os.cpu_count() - 1  # Leave one core for system
    # num_cores = min(requested_cores or max_cores, max_cores)
    
    # num_cores_to_use, memory_fraction = calculate_safe_memory_settings(
        # available_memory, num_cores
    # )

    num_cores_to_use = requested_cores
    memory_fraction = 0.8 / num_cores_to_use
    
    # Calculate batch size based on available memory per core
    # doc_sizes = [doc.size_bytes for doc in docs]
    # batch_size = estimate_batch_size(
        # doc_sizes, 
        # available_memory * memory_fraction,
        # safety_factor=0.8  # Additional safety margin within each core's allocation
    # )

    batch_size = 1
    
    logger.info(f"Using {num_cores_to_use} cores with {batch_size} documents per batch")
    logger.info(f"Memory fraction per core: {memory_fraction:.3f}")
    
    # Setup for tokenization
    token_dtype = np.uint16 if model_desc == "gpt-2" else np.uint32

    # Explicitly calculate, and log, the core count
    num_cores = os.cpu_count() - 2     # Leave two cores for system
    
    # Process documents in batches
    nprocs = min(num_cores, num_cores_to_use)
    logger.info(f"Using {nprocs} cores for processing")
    shard_index = 0
    all_tokens_np = np.empty((shard_size,), dtype=token_dtype)
    token_count = 0
    progress_bar = None
    
    # Process in batches
    with mp.Pool(nprocs) as pool:
        for i in range(0, len(docs), batch_size):
            batch_docs = docs[i:i + batch_size]
            
            # Create args for each document (path and model_desc)
            batch_args = [(doc, model_desc) for doc in batch_docs]
            
            # Process batch
            for tokens in pool.imap(read_and_tokenize_document, batch_args):
                if tokens is None:
                    continue
                    
                # Handle shard management
                if token_count + len(tokens) < shard_size:
                    # Append tokens to current shard
                    all_tokens_np[token_count:token_count+len(tokens)] = tokens
                    token_count += len(tokens)
                    if progress_bar is None:
                        progress_bar = tqdm(total=shard_size, unit="tokens", 
                                         desc=f"Shard {shard_index}")
                    progress_bar.update(len(tokens))
                    sys.stderr.flush()
                else:
                    # Write current shard and start a new one
                    split = "val" if shard_index == 0 else "train"
                    filename = os.path.join(
                        output_dir, 
                        f"documents_{split}_{shard_index:06d}.bin"
                    )
                    
                    # Split document between shards if needed
                    remainder = shard_size - token_count
                    if progress_bar:
                        progress_bar.update(remainder)
                    all_tokens_np[token_count:token_count+remainder] = tokens[:remainder]
                    write_datafile(filename, all_tokens_np.tolist(), model_desc)
                    
                    shard_index += 1
                    progress_bar = None
                    
                    # Start new shard with remainder
                    all_tokens_np[0:len(tokens)-remainder] = tokens[remainder:]
                    token_count = len(tokens)-remainder
                
                # Force garbage collection after processing each document
                del tokens
                gc.collect()
            
            # Additional garbage collection after each batch
            gc.collect()
    
    # Write final shard if there are remaining tokens
    if token_count != 0:
        split = "val" if shard_index == 0 else "train"
        filename = os.path.join(output_dir, 
                              f"documents_{split}_{shard_index:06d}.bin")
        write_datafile(filename, (all_tokens_np[:token_count]).tolist(), model_desc)
    
    # Close progress bar if needed
    if progress_bar:
        progress_bar.close()
    
    logger.info("Processing complete")
    print("Processing complete")

def clean_pairtree(htid):
    period = htid.find('.')
    prefix = htid[0:period]
    postfix = htid[(period+1): ]
    if ':' in postfix:
        postfix = postfix.replace(':','+')
        postfix = postfix.replace('/','=')
    if '.' in postfix:
        postfix = postfix.replace('.',',')
    cleanname = prefix + "." + postfix
    return cleanname

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Document tokenization for large files")
    parser.add_argument("-i", "--input_dir", type=str, help="Directory containing input documents")
    parser.add_argument("-o", "--output_dir", type=str, help="Directory for output shards")
    parser.add_argument("-m", "--model_desc", type=str, default="gpt-2",
                       help="Model descriptor, gpt-2|llama-3")
    parser.add_argument("-s", "--shard_size", type=int, default=10**8,
                       help="Size of each data shard in tokens")
    parser.add_argument("-c", "--cores", type=int, default=None,
                       help="Number of CPU cores to use (default: all but one)")
    parser.add_argument("-p", "--file_pattern", type=str, default="*",
                       help="File pattern to match (e.g., '*.txt')")
    parser.add_argument("-b", "--batch", type = str, help="Path to list of filenames")
    args = parser.parse_args()

    holdout = pd.read_csv('../../../metadata/HeldOutRecords1905-14.tsv', sep = '\t')
    holdout_docs = set([clean_pairtree(x) for x in holdout['HTid']])
    print('Holdout:', holdout_docs, flush = True)

    process_documents(
        args.input_dir, 
        args.output_dir, 
        holdout_docs,
        args.batch,
        args.model_desc, 
        args.shard_size,
        args.cores,
        args.file_pattern
    )
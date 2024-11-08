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

def process_documents(input_dir: str, output_dir: str, 
                     model_desc: str = "gpt-2",
                     shard_size: int = 10**8,
                     requested_cores: Optional[int] = None,
                     file_pattern: str = "*"):
    """
    Process documents with memory-aware batching and core-aware memory management
    """
    # Setup
    os.makedirs(output_dir, exist_ok=True)
    
    # Get document information
    docs = get_document_paths(input_dir, file_pattern)
    total_docs = len(docs)
    logger.info(f"Found {total_docs} documents to process")
    
    # Calculate safe processing settings
    available_memory = psutil.virtual_memory().available
    max_cores = os.cpu_count() - 1  # Leave one core for system
    num_cores = min(requested_cores or max_cores, max_cores)
    
    num_cores_to_use, memory_fraction = calculate_safe_memory_settings(
        available_memory, num_cores
    )
    
    if num_cores_to_use < num_cores:
        logger.warning(
            f"Reduced core count from {num_cores} to {num_cores_to_use} "
            "to ensure safe memory usage"
        )
    
    # Calculate batch size based on available memory per core
    doc_sizes = [doc.size_bytes for doc in docs]
    batch_size = estimate_batch_size(
        doc_sizes, 
        available_memory * memory_fraction,
        safety_factor=0.8  # Additional safety margin within each core's allocation
    )
    
    logger.info(f"Using {num_cores_to_use} cores with {batch_size} documents per batch")
    logger.info(f"Memory fraction per core: {memory_fraction:.3f}")
    
    # Rest of the processing logic remains the same as before...
    # [previous implementation continues here]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Document tokenization for large files")
    parser.add_argument("input_dir", type=str, help="Directory containing input documents")
    parser.add_argument("output_dir", type=str, help="Directory for output shards")
    parser.add_argument("-m", "--model_desc", type=str, default="gpt-2",
                       help="Model descriptor, gpt-2|llama-3")
    parser.add_argument("-s", "--shard_size", type=int, default=10**8,
                       help="Size of each data shard in tokens")
    parser.add_argument("-c", "--cores", type=int, default=None,
                       help="Number of CPU cores to use (default: all but one)")
    parser.add_argument("-p", "--file_pattern", type=str, default="*",
                       help="File pattern to match (e.g., '*.txt')")
    args = parser.parse_args()

    process_documents(
        args.input_dir, 
        args.output_dir, 
        args.model_desc, 
        args.shard_size,
        args.cores,
        args.file_pattern
    )

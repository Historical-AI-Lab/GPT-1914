import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os, random
import pandas as pd
from torch.nn.parallel import DistributedDataParallel as DDP
import torch.distributed as dist
import torch.multiprocessing as mp

def setup(rank, world_size):
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '12355'
    dist.init_process_group("nccl", rank=rank, world_size=world_size)

def cleanup():
    dist.destroy_process_group()

def load_model(rank):
    model_path = "hf774M140k"
    
    print(f"GPU {rank} loading model and tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    
    device = f'cuda:{rank}'
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float16,
        device_map=device,
        low_cpu_mem_usage=True
    ).to(device)
    model.eval()
    
    return model, tokenizer

def generate_text(prompt, model, tokenizer, params):
    tokens = tokenizer.encode(prompt, return_tensors="pt")
    attention_mask = torch.ones_like(tokens)
    
    tokens = tokens.to(model.device)
    attention_mask = attention_mask.to(model.device)
    
    output = model.generate(
        tokens,
        attention_mask=attention_mask,
        max_new_tokens=params['max_tokens'],
        temperature=params['temperature'],
        repetition_penalty=params['repetition_penalty'],
        top_p=params['top_p'],
        do_sample=True,
        min_length=tokens.shape[1] + 132,
        pad_token_id=tokenizer.eos_token_id
    )
    
    generated_text = tokenizer.batch_decode(output)[0]
    return generated_text

def process_chunk(rank, world_size):
    # Initialize process group
    setup(rank, world_size)
    
    # Load model on this GPU
    model, tokenizer = load_model(rank)
    
    # Read data
    prompts = pd.read_csv('edwardian_segments.tsv', sep='\t')
    prompts = prompts[prompts['use_as_prompt'] == 1].reset_index(drop=True)
    
    # Split data among GPUs
    chunk_size = len(prompts) // world_size
    start_idx = rank * chunk_size
    end_idx = start_idx + chunk_size if rank != world_size - 1 else len(prompts)
    
    chunk_prompts = prompts.iloc[start_idx:end_idx]
    
    params = {
        'max_tokens': 200,
        'temperature': 0.6,
        'repetition_penalty': 1.3,
        'top_p': 0.7
    }
    
    continuations = []
    ctr = 0
    for idx, row in chunk_prompts.iterrows():
        ctr += 1
        try:
            params['temperature'] = round(random.uniform(0.5, 0.7), 3)
            generated_text = generate_text(row['segment'], model, tokenizer, params)
            continuations.append(generated_text)
            
        except Exception as e:
            print(f"GPU {rank}: Error at prompt {idx}: {str(e)}", flush=True)
            continuations.append("")
    
        if idx % 50 == 0:
            print(f"GPU {rank}: Completed {ctr} prompts", flush=True)
    
    # Save final results for this GPU
    chunk_prompts['continuation'] = continuations
    chunk_prompts.to_csv(f'done_so_far_gpu{rank}.tsv', sep='\t', index=False)
    
    cleanup()

def main():
    world_size = torch.cuda.device_count()  # Number of GPUs
    print(f"Using {world_size} GPUs")
    
    # Spawn processes for each GPU
    mp.spawn(
        process_chunk,
        args=(world_size,),
        nprocs=world_size,
        join=True
    )
    
    # Combine results from all GPUs
    all_results = []
    for rank in range(world_size):
        results = pd.read_csv(f'done_so_far_gpu{rank}.tsv', sep='\t')
        all_results.append(results)
    
    final_results = pd.concat(all_results).sort_index()
    final_results.to_csv('final_results.tsv', sep='\t', index=False)

if __name__ == "__main__":
    main()
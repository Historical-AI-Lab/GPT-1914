# GenerateGPT1914Completions.py

# Loads a model trained on books from the past, and
# generates text based on prompts drawn from held-out books.
# This version uses the MPS backend for faster generation.

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os, random
import pandas as pd

# Set tokenizer parallelism explicitly to avoid warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def load_model():
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    model_path = "../llmc/hf774M140k"
    
    print("Loading model and tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16,
        device_map=device
    )
    model.eval()
    
    return model, tokenizer, device

def generate_text(prompt, model, tokenizer, device, params):
    tokens = tokenizer.encode(prompt, return_tensors="pt")
    attention_mask = torch.ones_like(tokens)
    
    tokens = tokens.to(device)
    attention_mask = attention_mask.to(device)

    input_length = tokens.shape[1]
    # print(f"Input length in tokens: {input_length}")
    # print(f"Requested new tokens: {params['max_tokens']}")
    # print(f"Total tokens that would be needed: {input_length + params['max_tokens']}")
    
    output = model.generate(
        tokens,
        attention_mask=attention_mask,
        max_new_tokens=params['max_tokens'],
        temperature=params['temperature'],
        repetition_penalty=params['repetition_penalty'],
        top_p=params['top_p'],
        min_length=input_length + 132,
        do_sample=True,  # Enable sampling
        pad_token_id=tokenizer.eos_token_id
    )
    
    generated_text = tokenizer.batch_decode(output)[0]
    return generated_text

def main():
    print("Initializing model...")
    model, tokenizer, device = load_model()
    
    # Get initial parameters
    params = {
            'max_tokens': 200,
            'temperature': 0.6,
            'repetition_penalty': 1.3,
            'top_p': 0.7
        }    
    
    prompts = pd.read_csv('edwardian_segments.tsv', sep='\t')
    prompts = prompts[prompts['use_as_prompt'] == 1]

    prompts = prompts.reset_index(drop=True)  # we set drop to True to avoid the old index being added as a column

    continuations = []

    print('Starting generation...')
    
    for i, row in prompts.iterrows():
        prompt = row['segment']
        params['temperature'] = temperature = round(random.uniform(0.5, 0.7), 3)

        try:
            generated_text = generate_text(prompt, model, tokenizer, device, params)
            generated_text = generated_text[len(prompt):]
            continuations.append(generated_text)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            continuations.append("")

        if i % 40 == 2:
            print(f"Prompt: {prompt}")
            print()
            print(f"Completed {i + 1} of {len(prompts)}")
            print(f'and have generated {len(continuations)} continuations')
            print()
            print(f"Continuation: {generated_text}")
            print()
            done_so_far = prompts.iloc[:i+1].copy()
            done_so_far['continuation'] = continuations
            done_so_far.to_csv('done_so_far.tsv', sep='\t', index=False)

if __name__ == "__main__":
    main()
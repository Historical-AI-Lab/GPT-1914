# time_travel2.py
# Loads a model trained on books from the past, and
# generates text based on user input prompts.
# This version uses the MPS backend for faster generation.

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os

# Set tokenizer parallelism explicitly to avoid warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def load_model():
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    model_path = "../../hf774M140k"
    
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
    
    output = model.generate(
        tokens,
        attention_mask=attention_mask,
        max_new_tokens=params['max_tokens'],
        temperature=params['temperature'],
        repetition_penalty=params['repetition_penalty'],
        top_p=params['top_p'],
        do_sample=True,  # Enable sampling
        pad_token_id=tokenizer.eos_token_id
    )
    
    generated_text = tokenizer.batch_decode(output)[0]
    return generated_text

def get_params(params):
    print("\nGeneration Parameters:")
    print("-" * 20)
    
    if len(params) < 2:
        # Initialize with defaults
        params = {
            'max_tokens': 128,
            'temperature': 0.6,
            'repetition_penalty': 1.2,
            'top_p': 0.7
        }
        
    print(f"Current settings:")
    print(f"1. Max tokens: {params['max_tokens']}")
    print(f"2. Temperature: {params['temperature']}")
    print(f"3. Repetition penalty: {params['repetition_penalty']}")
    print(f"4. Top-p: {params['top_p']}")
    print("\nEnter parameter number to change, or 'r' to return to prompting")
    
    while True:
        choice = input("> ").strip().lower()
        
        if choice == 'r':
            return params
            
        try:
            choice = int(choice)
            if choice not in [1, 2, 3, 4]:
                print("Invalid choice. Please enter 1-4 or 'r'")
                continue
                
            if choice == 1:
                value = int(input("Enter new max tokens (10-512): "))
                if 10 <= value <= 512:
                    params['max_tokens'] = value
            elif choice == 2:
                value = float(input("Enter new temperature (0.1-2.0): "))
                if 0.1 <= value <= 2.0:
                    params['temperature'] = value
            elif choice == 3:
                value = float(input("Enter new repetition penalty (1.0-2.0): "))
                if 1.0 <= value <= 2.0:
                    params['repetition_penalty'] = value
            elif choice == 4:
                value = float(input("Enter new top-p (0.1-1.0): "))
                if 0.1 <= value <= 1.0:
                    params['top_p'] = value
                    
            print("\nUpdated settings:")
            print(f"1. Max tokens: {params['max_tokens']}")
            print(f"2. Temperature: {params['temperature']}")
            print(f"3. Repetition penalty: {params['repetition_penalty']}")
            print(f"4. Top-p: {params['top_p']}")
            print("\nEnter parameter number to change, or 'r' to return to prompting")
            
        except ValueError:
            print("Invalid input. Please enter a number or 'r'")

def main():
    print("Initializing model...")
    model, tokenizer, device = load_model()
    
    # Get initial parameters
    dummyparams = {}    
    params = get_params(dummyparams)    
    
    print("\nModel ready! Commands:")
    print("- Enter your prompt to generate text")
    print("- Type 'params' to adjust generation parameters")
    print("- Type 'stop' to exit")
    print("-" * 50)
    
    while True:
        prompt = input("\nEnter prompt: ").strip()
        
        if prompt.lower() == 'stop':
            print("Goodbye!")
            break
            
        if prompt.lower() == 'params':
            params = get_params(params)
            continue
            
        if not prompt:
            print("Please enter a valid prompt!")
            continue
            
        try:
            generated_text = generate_text(prompt, model, tokenizer, device, params)
            print("\nGenerated text:")
            print("-" * 30)
            print(generated_text)
            print("-" * 30)
        except Exception as e:
            print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
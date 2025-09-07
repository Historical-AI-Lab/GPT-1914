#!/usr/bin/env python3
"""
make_training_data_motive.py

Co-written by Ted Underwood and Claude Sonnet

Version 1.1 — now with improved JSON parsing and error handling,
also allows limiting number of chunks processed for testing

Two-stage pipeline for detecting character motives in text:
1. Chunk text into manageable pieces
2. Use LLM to identify character motives
"""

import json
import nltk
import tiktoken
import requests
import sys
from pathlib import Path
from typing import List, Dict, Any
import argparse

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def count_tokens(text: str) -> int:
    """Approximate token count using tiktoken (GPT tokenizer as proxy)"""
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except:
        # Fallback to rough word-based estimate
        return len(text.split()) * 1.3

def chunk_text(text: str, max_tokens: int = 768) -> List[str]:
    """
    Break text into sentences and group into chunks under token limit.
    Uses clean sentence boundaries.
    """
    # Split into sentences
    sentences = nltk.sent_tokenize(text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # Check if adding this sentence would exceed limit
        test_chunk = current_chunk + " " + sentence if current_chunk else sentence
        
        if count_tokens(test_chunk) <= max_tokens:
            current_chunk = test_chunk
        else:
            # Current chunk is full, start new one
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    # Don't forget the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def stage1_create_chunks(input_file: str) -> str:
    """
    Stage 1: Read text file and create chunks
    Returns the output filename
    """
    input_path = Path(input_file)
    
    # Read the input file
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Create chunks
    chunks = chunk_text(text)
    
    # Prepare output filename
    output_file = input_path.stem + "-chunks.json"
    
    # Save chunks with metadata
    chunk_data = {
        "source_file": input_file,
        "total_chunks": len(chunks),
        "chunks": [{"id": i, "text": chunk} for i, chunk in enumerate(chunks)]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunk_data, f, indent=2)
    
    print(f"Created {len(chunks)} chunks from {input_file}")
    print(f"Saved to {output_file}")
    return output_file

def call_ollama(prompt: str, model: str = "gpt-oss:20b") -> Dict[str, Any]:
    """
    Call ollama API with the given prompt
    """
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,  # Lower temperature for more consistent output
            "top_p": 0.9
        }
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling ollama: {e}")
        return {"response": "ERROR"}

def create_motive_prompt(passage: str) -> str:
    """
    Create prompt for motive relationship detection
    """
    # Escape quotes in the passage to prevent JSON issues
    escaped_passage = passage.replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')
    
    prompt = f"""You are sifting text to find passages that draw very clear connections between motives and behavior. A connection is only present if:

1. A specific motive or emotion is explicitly attributed to a chararacter in the text. It has to be explicitly described, not just implied. 
2. The character's resulting behavior (speech or action) is described in a different part of the text, separate from the motive. It should clearly result from the motive.
3. The passage describing motive is not just an incident that causes the character's action, but directly describes the character's internal state.

Analyze this passage to decide whether all three of those descriptions unambiguously apply to it. \
If you are not certain that the motive-behavior connection is clear enough, answer ONLY with a JSON object in exactly this format:

{{"motive_yn": "n", "character": "", "motive": "", "behavior": ""}}

If you are certain that all three things unambiguously apply to this passage -- a psychological motive is explicitly provided for an action distinct from the motive -- answer with ONLY a valid JSON object in exactly this format:

{{"motive_yn": "y", "character": "character's name or other designation e.g. 'butler'", "motive": "verbatim motive drawn from the passage", "behavior": "paraphrased description of resulting behavior"}}

Passage to analyze: {escaped_passage}

JSON response:"""
    
    return prompt

def clean_and_parse_json(response_text: str) -> Dict[str, Any]:
    """
    Attempt to clean and parse JSON response, with fallbacks
    """
    # Remove any text before the first {
    start_idx = response_text.find('{')
    if start_idx == -1:
        raise ValueError("No JSON object found in response")
    
    # Remove any text after the last }
    end_idx = response_text.rfind('}')
    if end_idx == -1:
        raise ValueError("No complete JSON object found in response")
    
    json_str = response_text[start_idx:end_idx + 1]
    
    # Try to parse
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Try some basic cleaning
        json_str = json_str.replace('\n', ' ').replace('\r', ' ')
        # Fix common issues with quotes
        json_str = json_str.replace('\\"', '"').replace('""', '"')
        return json.loads(json_str)

def stage2_analyze_motivation(chunks_file: str, max_chunks: int) -> str:
    """
    Stage 2: Analyze chunks for motive relationships
    Returns the output filename
    """
    # Load chunks
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunk_data = json.load(f)
    
    results = []
    total_chunks = len(chunk_data["chunks"])
    if max_chunks:
        total_chunks = min(total_chunks, max_chunks)
    else:
        max_chunks = total_chunks
        
    print(f"Analyzing {total_chunks} chunks for motive relationships...")
    
    for i, chunk_info in enumerate(chunk_data["chunks"][0: max_chunks] if max_chunks else chunk_data["chunks"]):
        chunk_id = chunk_info["id"]
        passage = chunk_info["text"]
        
        print(f"Processing chunk {i+1}/{total_chunks} (ID: {chunk_id})")
        
        # Create prompt
        prompt = create_motive_prompt(passage)
        
        # Call ollama
        response = call_ollama(prompt)
        
        if response.get("response") == "ERROR":
            result = {
                "chunk_id": chunk_id,
                "passage": passage,
                "motive_yn": "error",
                "character:": "",
                "motive": "",
                "behavior": "",
                "error": "API call failed"
            }
        else:
            try:
                # Parse the JSON response with cleaning
                llm_output = clean_and_parse_json(response["response"])
                result = {
                    "chunk_id": chunk_id,
                    "passage": passage,
                    "motive_yn": llm_output.get("motive_yn", "n").lower(),
                    "motive": llm_output.get("motive", ""),
                    "character": llm_output.get("character", ""),
                    "behavior": llm_output.get("behavior", ""),
                }
                # Validate motive_yn field
                if result["motive_yn"] not in ["y", "n"]:
                    result["motive_yn"] = "n"
                    
            except (json.JSONDecodeError, ValueError) as e:
                # Try a fallback approach - look for key indicators in raw text
                raw_response = response.get("response", "").lower()
                fallback_motive = "y" if any(indicator in raw_response for indicator in [
                    '"motive_yn": "y"', '"motive_yn":"y"', 'motive relationship present', 'explicit motive'
                ]) else "n"
                
                result = {
                    "chunk_id": chunk_id,
                    "passage": passage,
                    "motive_yn": fallback_motive,
                    "character": "",
                    "motive": "",
                    "behavior": "",
                    "error": f"JSON parse error, used fallback: {e}",
                    "raw_response": response.get("response", "")[:500]  # First 500 chars
                }
        
        results.append(result)
    
    # Save results
    chunks_path = Path(chunks_file)
    output_file = chunks_path.stem.replace("-chunks", "") + "-motive-analysis.json"
    
    output_data = {
        "source_chunks_file": chunks_file,
        # "model_used": "qwen2.5:7b-instruct",
        "model_used": "gpt-oss:20b",
        "total_chunks": len(results),
        "motive_chunks": len([r for r in results if r["motive_yn"] == "y"]),
        "results": results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    motive_count = len([r for r in results if r["motive_yn"] == "y"])
    print(f"\nAnalysis complete!")
    print(f"Found {motive_count} chunks with motive relationships out of {len(results)} total chunks")
    print(f"Results saved to {output_file}")
    
    return output_file

def main():
    parser = argparse.ArgumentParser(description="Detect motives in text")
    parser.add_argument("command", choices=["chunk", "analyze", "full"], 
                       help="Stage to run: chunk, analyze, or full pipeline")
    parser.add_argument("input_file", help="Input file (text for chunk/full, chunks.json for analyze)")

    # add an optional argument for how many chunks to process (for testing)
    parser.add_argument("--max_chunks", type=int, default=None, 
                        help="Maximum number of chunks to process (for testing)")
    
    args = parser.parse_args()

    max_chunks = args.max_chunks
    
    if args.command == "chunk":
        stage1_create_chunks(args.input_file)
    
    elif args.command == "analyze":
        if not args.input_file.endswith("-chunks.json"):
            print("Warning: analyze command expects a -chunks.json file")
        stage2_analyze_motivation(args.input_file, max_chunks)
    
    elif args.command == "full":
        print("Running full pipeline...")
        chunks_file = stage1_create_chunks(args.input_file)
        stage2_analyze_motivation(chunks_file, max_chunks)

if __name__ == "__main__":
    main()
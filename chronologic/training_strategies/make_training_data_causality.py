#!/usr/bin/env python3
"""
Two-stage pipeline for detecting causal relationships in text:
1. Chunk text into manageable pieces
2. Use LLM to identify causal relationships
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

def call_ollama(prompt: str, model: str = "qwen2.5:7b-instruct") -> Dict[str, Any]:
    """
    Call ollama API with the given prompt
    """
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json"  # Request JSON output
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling ollama: {e}")
        return {"response": "ERROR"}

def create_causal_prompt(passage: str) -> str:
    """
    Create prompt for causal relationship detection
    """
    prompt = f"""You are analyzing text for explicit causal relationships. A causal relationship is present when:
1. Both a cause and an effect are clearly described
2. The causal connection between them is explicitly stated (not just implied)
3. The causality is thematized - it's a key part of what the passage is communicating

Analyze this passage and return a JSON response with these fields:
- "passage": the original passage
- "causal_yn": "y" if explicit causal relationship present, "n" if not
- "cause": the text describing the cause (empty string if causal_yn is "n")
- "effect": the text describing the effect (empty string if causal_yn is "n")

Passage to analyze:
{passage}

Return only valid JSON:"""
    
    return prompt

def stage2_analyze_causality(chunks_file: str) -> str:
    """
    Stage 2: Analyze chunks for causal relationships
    Returns the output filename
    """
    # Load chunks
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunk_data = json.load(f)
    
    results = []
    total_chunks = len(chunk_data["chunks"])
    
    print(f"Analyzing {total_chunks} chunks for causal relationships...")
    
    for i, chunk_info in enumerate(chunk_data["chunks"]):
        chunk_id = chunk_info["id"]
        passage = chunk_info["text"]
        
        print(f"Processing chunk {i+1}/{total_chunks} (ID: {chunk_id})")
        
        # Create prompt
        prompt = create_causal_prompt(passage)
        
        # Call ollama
        response = call_ollama(prompt)
        
        if response.get("response") == "ERROR":
            result = {
                "chunk_id": chunk_id,
                "passage": passage,
                "causal_yn": "error",
                "cause": "",
                "effect": "",
                "error": "API call failed"
            }
        else:
            try:
                # Parse the JSON response
                llm_output = json.loads(response["response"])
                result = {
                    "chunk_id": chunk_id,
                    "passage": passage,
                    "causal_yn": llm_output.get("causal_yn", "n"),
                    "cause": llm_output.get("cause", ""),
                    "effect": llm_output.get("effect", ""),
                }
            except json.JSONDecodeError as e:
                result = {
                    "chunk_id": chunk_id,
                    "passage": passage,
                    "causal_yn": "error",
                    "cause": "",
                    "effect": "",
                    "error": f"JSON parse error: {e}",
                    "raw_response": response.get("response", "")
                }
        
        results.append(result)
    
    # Save results
    chunks_path = Path(chunks_file)
    output_file = chunks_path.stem.replace("-chunks", "") + "-causal-analysis.json"
    
    output_data = {
        "source_chunks_file": chunks_file,
        "model_used": "qwen2.5:7b-instruct",
        "total_chunks": len(results),
        "causal_chunks": len([r for r in results if r["causal_yn"] == "y"]),
        "results": results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    causal_count = len([r for r in results if r["causal_yn"] == "y"])
    print(f"\nAnalysis complete!")
    print(f"Found {causal_count} chunks with causal relationships out of {len(results)} total chunks")
    print(f"Results saved to {output_file}")
    
    return output_file

def main():
    parser = argparse.ArgumentParser(description="Detect causal relationships in text")
    parser.add_argument("command", choices=["chunk", "analyze", "full"], 
                       help="Stage to run: chunk, analyze, or full pipeline")
    parser.add_argument("input_file", help="Input file (text for chunk/full, chunks.json for analyze)")
    
    args = parser.parse_args()
    
    if args.command == "chunk":
        stage1_create_chunks(args.input_file)
    
    elif args.command == "analyze":
        if not args.input_file.endswith("-chunks.json"):
            print("Warning: analyze command expects a -chunks.json file")
        stage2_analyze_causality(args.input_file)
    
    elif args.command == "full":
        print("Running full pipeline...")
        chunks_file = stage1_create_chunks(args.input_file)
        stage2_analyze_causality(chunks_file)

if __name__ == "__main__":
    main()
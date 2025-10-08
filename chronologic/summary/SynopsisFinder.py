#!/usr/bin/env python3
"""
SynopsisFinder.py

Co-written by Ted Underwood and Claude Sonnet

Version 2.0 — Directory processing with paragraph extraction

Two-stage pipeline for detecting summary sentences in text:
1. Extract paragraphs from multiple files (10 random paragraphs of 80+ words per file)
2. Use LLM to identify summary sentences
"""

import json
import requests
import random
from pathlib import Path
from typing import List, Dict, Any
import argparse


def extract_paragraphs_from_file(file_path: Path, min_words: int = 80, num_paragraphs: int = 10) -> List[str]:
    """
    Extract paragraphs from a text file, filter by word count, and randomly select a subset.
    
    Args:
        file_path: Path to the text file
        min_words: Minimum word count for a paragraph to be included
        num_paragraphs: Number of paragraphs to randomly select
    
    Returns:
        List of selected paragraphs
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Split by double newlines (common paragraph separator) or single newlines
    # Try double newlines first, fall back to single if needed
    paragraphs = text.split('\n\n')
    if len(paragraphs) < 5:  # If we got too few, try single newlines
        paragraphs = text.split('\n')
    
    # Filter paragraphs by word count
    filtered_paragraphs = []
    for para in paragraphs:
        para = para.strip()
        if para:  # Not empty
            word_count = len(para.split())
            if word_count >= min_words:
                filtered_paragraphs.append(para)
    
    # Randomly select num_paragraphs (or all if fewer available)
    num_to_select = min(num_paragraphs, len(filtered_paragraphs))
    if num_to_select > 0:
        selected = random.sample(filtered_paragraphs, num_to_select)
        return selected
    else:
        return []


def stage1_extract_paragraphs(input_dir: str, min_words: int = 80, num_paragraphs: int = 10) -> str:
    """
    Stage 1: Read all .txt files from directory and extract paragraphs
    Returns the output filename
    """
    input_path = Path(input_dir)
    
    if not input_path.is_dir():
        raise ValueError(f"{input_dir} is not a directory")
    
    # Find all .txt files
    txt_files = list(input_path.glob("*.txt"))
    
    if not txt_files:
        raise ValueError(f"No .txt files found in {input_dir}")
    
    print(f"Found {len(txt_files)} .txt files in {input_dir}")
    
    # Process each file
    all_paragraphs = {}
    total_paragraphs = 0
    
    for txt_file in txt_files:
        print(f"Processing {txt_file.name}...")
        paragraphs = extract_paragraphs_from_file(txt_file, min_words, num_paragraphs)
        
        if paragraphs:
            all_paragraphs[txt_file.name] = paragraphs
            total_paragraphs += len(paragraphs)
            print(f"  Selected {len(paragraphs)} paragraphs")
        else:
            print(f"  No paragraphs met the criteria")
    
    # Prepare output filename
    output_file = "paragraphs-extracted.json"
    
    # Save paragraphs with metadata
    paragraph_data = {
        "source_directory": str(input_dir),
        "min_words": min_words,
        "paragraphs_per_file": num_paragraphs,
        "total_files": len(all_paragraphs),
        "total_paragraphs": total_paragraphs,
        "files": all_paragraphs
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(paragraph_data, f, indent=2)
    
    print(f"\nExtracted {total_paragraphs} total paragraphs from {len(all_paragraphs)} files")
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
        "options": {
            "temperature": 0.1,
            "top_p": 0.9
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print(f"Request timed out after 5 minutes")
        return {"response": "ERROR"}
    except requests.exceptions.RequestException as e:
        print(f"Error calling ollama: {e}")
        return {"response": "ERROR"}


def create_summary_prompt(passage: str) -> str:
    """
    Create prompt for summary generation
    """
    escaped_passage = passage.replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')
    
    prompt = f"""You are sorting paragraphs into two groups: those that contain a sentence that previews or summarizes the whole paragraph, and those that lack single-sentence synopsis.

Most paragraphs do not contain a synopsis sentence, and if one does not already exist you should not create one. For instance, consider the following paragraph:

This may clearly be seen by taking a very small quantity of such a substance as chlorate of potash. If a crystal of this is examined under a magnifying glass till its crystalline form and structure are familiar, and it is then placed in a test-tube and gently heated, cleavage will at once be evident. With a little crackling, the chlorate splits itself into many crystals along its chief lines of cleavage (called the cleavage planes), every one of which crystals showing under the microscope the identical form and characteristics of the larger crystal from which it came.

No single sentence there adequately summarizes the whole. If you determine that the paragraph does not contain a good synopsis, respond ONLY with the following JSON object:

{{"synopsis_present": "n", "synopsis": ""}}

If there is a synopsis, you will answer ONLY with a valid JSON object in exactly this format:

{{"synopsis_present": "y", "synopsis": <single verbatim sentence from the text>}}

For instance, given the following paragraph:

First, I went to the wrong classroom for math. I was sitting in the class, surrounded by people taking notes and paying attention to how to do equations, which would have been okay if I was supposed to be in an algebra class. In reality, I was supposed to be in geometry, and when I discovered my error, I had already missed the first twenty minutes of a one-hour class. When I got to the correct class, all twenty-five students turned and looked at me as the teacher said, "You're late." That would have been bad enough, but in my next class my history teacher spoke so fast I could not follow most of what they said. The only thing I did hear was that we were having a quiz tomorrow over today’s lecture. My day seemed to be going better during botany class, that is, until we visited the lab. I had a sneezing fit because of one of the plants in the lab and had to leave the room. When I finally finished my classes for the day, I discovered I had locked my keys in the car and had to wait for my brother to bring another set. My first day of college was a disaster. 

The correct response would be:

{{"synopsis_present": "y", "synopsis": "My first day of college was a disaster."}}

Passage to analyze: {escaped_passage}
JSON response:"""
    
    return prompt


def clean_and_parse_json(response_text: str) -> Dict[str, Any]:
    """
    Attempt to clean and parse JSON response, with fallbacks
    """
    start_idx = response_text.find('{')
    if start_idx == -1:
        raise ValueError("No JSON object found in response")
    
    end_idx = response_text.rfind('}')
    if end_idx == -1:
        raise ValueError("No complete JSON object found in response")
    
    json_str = response_text[start_idx:end_idx + 1]
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        json_str = json_str.replace('\n', ' ').replace('\r', ' ')
        json_str = json_str.replace('\\"', '"').replace('""', '"')
        return json.loads(json_str)


def stage2_analyze_summary(paragraphs_file: str, max_paragraphs: int = None) -> str:
    """
    Stage 2: Analyze paragraphs for summaries using LLM
    Returns the output filename
    """
    with open(paragraphs_file, 'r', encoding='utf-8') as f:
        paragraph_data = json.load(f)
    
    results = []
    
    # Flatten the paragraph structure for processing
    all_items = []
    for filename, paragraphs in paragraph_data["files"].items():
        for para_idx, paragraph in enumerate(paragraphs):
            all_items.append({
                "filename": filename,
                "paragraph_index": para_idx,
                "text": paragraph
            })
    
    total_paragraphs = len(all_items)
    if max_paragraphs:
        total_paragraphs = min(total_paragraphs, max_paragraphs)
        all_items = all_items[:max_paragraphs]

    print(f"Analyzing {total_paragraphs} paragraphs for synopses...")

    for i, item in enumerate(all_items):
        filename = item["filename"]
        para_idx = item["paragraph_index"]
        passage = item["text"]
        
        print(f"Processing {i+1}/{total_paragraphs} ({filename}, para {para_idx})")
        
        prompt = create_summary_prompt(passage)
        response = call_ollama(prompt)
        
        if response.get("response") == "ERROR":
            result = {
                "filename": filename,
                "passage": passage,
                "synopsis_present": "error",
                "synopsis": "",
                "error": "API call failed"
            }
        else:
            try:
                llm_output = clean_and_parse_json(response["response"])
                result = {
                    "filename": filename,
                    "passage": passage,
                    "synopsis_present": llm_output.get("synopsis_present", "idk").lower(),
                    "synopsis": llm_output.get("synopsis", "")
                }
                    
            except (json.JSONDecodeError, ValueError) as e:
                raw_response = response.get("response", "").lower()
                fallback_synopsis = "error"
                
                result = {
                    "filename": filename,
                    "passage": passage,
                    "synopsis_present": fallback_synopsis,
                    "synopsis": "",
                    "error": "decode error",
                }
        
        results.append(result)
    
    output_file = "synopses.json"
    
    output_data = {
        "model_used": "qwen2.5:7b-instruct",
        "total_paragraphs": len(results),
        "synopsis_paragraphs": len([r for r in results if r["synopsis_present"] == "y"]),
        "results": results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)

    synopsis_count = len([r for r in results if r["synopsis_present"] == "y"])
    print(f"\nAnalysis complete!")
    print(f"Found {synopsis_count} paragraphs with synopses out of {len(results)} total paragraphs")
    print(f"Results saved to {output_file}")
    
    return output_file


def main():
    parser = argparse.ArgumentParser(description="Detect synopses in text from directory of files")
    parser.add_argument("command", choices=["extract", "analyze", "full"], 
                       help="Stage to run: extract, analyze, or full pipeline")
    parser.add_argument("input", help="Input directory (for extract/full) or paragraphs.json file (for analyze)")
    parser.add_argument("--min_words", type=int, default=80,
                       help="Minimum word count for paragraphs (default: 80)")
    parser.add_argument("--num_paragraphs", type=int, default=10,
                       help="Number of paragraphs to select per file (default: 10)")
    parser.add_argument("--max_paragraphs", type=int, default=None,
                       help="Maximum number of paragraphs to process in analysis (for testing)")
    
    args = parser.parse_args()
    
    if args.command == "extract":
        stage1_extract_paragraphs(args.input, args.min_words, args.num_paragraphs)
    
    elif args.command == "analyze":
        if not args.input.endswith(".json"):
            print("Warning: analyze command expects a .json file")
        stage2_analyze_summary(args.input, args.max_paragraphs)
    
    elif args.command == "full":
        print("Running full pipeline...")
        paragraphs_file = stage1_extract_paragraphs(args.input, args.min_words, args.num_paragraphs)
        stage2_analyze_summary(paragraphs_file, args.max_paragraphs)


if __name__ == "__main__":
    main()
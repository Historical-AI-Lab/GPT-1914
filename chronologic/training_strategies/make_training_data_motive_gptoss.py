"""
Use OpenAI API (vLLM backend) to run make_training_data_motive

Modifications:
- Replaced vLLM direct loading with OpenAI API calls
- Works with vLLM OpenAI-compatible API server
"""

import json
import nltk
import tiktoken
import sys
from pathlib import Path
from typing import List, Dict, Any
import argparse
from openai import OpenAI

# Configure your vLLM API endpoint
BASE_URL = "http://localhost:9011/v1"  # Update this to your server address
API_KEY = "EMPTY"  # vLLM doesn't require a real API key
MODEL_NAME = "/work/hdd/bdfx/zqiu1/models/gpt-oss-20b"  # This should match your deployed model

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)

def count_tokens(text: str) -> int:
    """Approximate token count using tiktoken (GPT tokenizer as proxy)"""
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except:
        return len(text.split()) * 1.3


def chunk_text(text: str, max_tokens: int = 768) -> List[str]:
    """Break text into sentences and group into chunks under token limit."""
    sentences = nltk.sent_tokenize(text)
    chunks, current_chunk = [], ""

    for sentence in sentences:
        test_chunk = current_chunk + " " + sentence if current_chunk else sentence
        if count_tokens(test_chunk) <= max_tokens:
            current_chunk = test_chunk
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


def stage1_create_chunks(input_file: str) -> str:
    input_path = Path(input_file)
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    chunks = chunk_text(text)
    output_file = input_path.stem + "-chunks.json"
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


def call_openai_api(prompt: str) -> Dict[str, Any]:
    """Call OpenAI-compatible API (vLLM backend)"""
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            top_p=0.9,
            max_tokens=16384,
        )
        response_text = completion.choices[0].message.content
        return {"response": response_text}
    except Exception as e:
        print(f"API call error: {e}")
        return {"response": "", "error": str(e)}


def create_motive_prompt(passage: str) -> str:
    escaped_passage = passage.replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')
    prompt = f"""
You are analyzing text to detect passages that show a clear link between a character's motive (internal state) and their behavior (speech or action).  

A passage is valid **only if ALL three rules are met**: 

1. **Explicit motive:** The text must clearly state a character's motive or emotion. It cannot be implied; it must be directly described.  

2. **Separate behavior:** The text must also describe the character's behavior (speech or action) in a different sentence or part of the passage. The behavior must clearly result from the motive.  

3. **Internal state:** The motive must be the character's inner state, not just an external event that triggers their behavior.  

## Task
- If the passage **fails any rule**, respond ONLY with this JSON template (leave values empty):  

{{"motive_yn": "n", "character": "", "motive": "", "behavior": "", "difficulty": "", "motive_passage": "", "behavior_passage": ""}}

- If the passage **meets all three rules**, respond ONLY with this JSON format:

{{"motive_yn": "y",
"character": <character's name or role>,
"motive": <paraphrased motive>,
"behavior": <paraphrased behavior>,
"difficulty": <very easy | easy | moderate | difficult | very difficult>,
"motive_passage": <exact sentence(s) with the motive>,
"behavior_passage": <exact sentence(s) with the behavior>}}

## Passage to analyze
{escaped_passage}

## Example
Input passage:
Mrs. Pembroke's airs had always set Eleanor's temper on edge; she could not abide the clipped tones and artificial laughter that seemed to lurk behind every civil phrase.\n\nYet when she saw the younger girl's color fade as Mrs. Pembroke turned the conversation toward the poor girl's circumstances, Eleanor's irritation softened into a fierce protectiveness.\n\nShe stepped forward with a bright laugh, laid her hand upon the girl's arm, and, smiling with genuine cordiality, said, \"Nonsense — come, sit by me; you shall have none of these idle remarks.\" The company murmured, surprised; Harold, observing Eleanor's change of manner, rose to pour the tea with an ignoble air of relief.

Output JSON:
{{
"motive_yn": "y",
"character": "Eleanor",
"motive": "annoyance at Mrs. Pembroke's affectations that turns into protective sympathy when she sees the younger girl's distress",
"behavior": "she steps forward, laughs lightly, lays her hand on the girl's arm and invites her to sit by her, dismissing the other's remarks",
"difficulty": "easy",
"motive_passage": "Yet when she saw the younger girl's color fade as Mrs. Pembroke turned the conversation toward the poor girl's circumstances, Eleanor's irritation softened into a fierce protectiveness.",
"behavior_passage": "She stepped forward with a bright laugh, laid her hand upon the girl's arm, and, smiling with genuine cordiality, said, \"Nonsense — come, sit by me; you shall have none of these idle remarks.\""
}}"""
    return prompt


def clean_and_parse_json(response_text: str) -> Dict[str, Any]:
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


def stage2_analyze_motivation(chunks_file: str, max_chunks: int) -> str:
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunk_data = json.load(f)

    results = []
    total_chunks = len(chunk_data["chunks"])
    if max_chunks:
        total_chunks = min(total_chunks, max_chunks)
    else:
        max_chunks = total_chunks

    print(f"Analyzing {total_chunks} chunks for motive relationships...")

    for i, chunk_info in enumerate(chunk_data["chunks"][0:max_chunks]):
        chunk_id = chunk_info["id"]
        passage = chunk_info["text"]
        print(f"Processing chunk {i+1}/{total_chunks} (ID: {chunk_id})")

        prompt = create_motive_prompt(passage)
        response = call_openai_api(prompt)

        if "error" in response:
            print(f"  Error on chunk {chunk_id}: {response['error']}")
            result = {
                "chunk_id": chunk_id,
                "passage": passage,
                "motive_yn": "n",
                "character": "",
                "motive": "",
                "behavior": "",
                "difficulty": "",
                "motive_passage": "",
                "behavior_passage": "",
                "error": response["error"]
            }
            results.append(result)
            continue

        try:
            llm_output = clean_and_parse_json(response["response"])
            result = {
                "chunk_id": chunk_id,
                "passage": passage,
                "motive_yn": llm_output.get("motive_yn", "n").lower(),
                "motive": llm_output.get("motive", ""),
                "character": llm_output.get("character", ""),
                "behavior": llm_output.get("behavior", ""),
                "difficulty": llm_output.get("difficulty", ""),
                "motive_passage": llm_output.get("motive_passage", ""),
                "behavior_passage": llm_output.get("behavior_passage", "")
            }
            if result["motive_yn"] not in ["y", "n"]:
                result["motive_yn"] = "n"
        except (json.JSONDecodeError, ValueError) as e:
            raw_response = response.get("response", "").lower()
            fallback_motive = "y" if '"motive_yn": "y"' in raw_response else "n"
            result = {
                "chunk_id": chunk_id,
                "passage": passage,
                "motive_yn": fallback_motive,
                "character": "",
                "motive": "",
                "behavior": "",
                "difficulty": "",
                "motive_passage": "",
                "behavior_passage": "",
                "error": f"JSON parse error, used fallback: {e}",
                "raw_response": response.get("response", "")[:500]
            }
        results.append(result)

    chunks_path = Path(chunks_file)
    output_file = "/work/hdd/bdfx/zqiu1/response/evaldata-motive-analysis-gptoss.json" # Please edit the output path
    output_data = {
        "source_chunks_file": chunks_file,
        "model_used": MODEL_NAME,
        "api_endpoint": BASE_URL,
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
    global BASE_URL, MODEL_NAME, client
    
    parser = argparse.ArgumentParser(description="Detect motives in text using OpenAI API (vLLM backend)")
    parser.add_argument("command", choices=["chunk", "analyze", "full"], 
    help="Stage to run: chunk, analyze, or full pipeline")
    parser.add_argument("input_file", help="Input file (text for chunk/full, chunks.json for analyze)")
    parser.add_argument("--max_chunks", type=int, default=None, help="Maximum number of chunks to process")
    parser.add_argument("--api_url", type=str, default=BASE_URL, help="API base URL")
    parser.add_argument("--model", type=str, default=MODEL_NAME, help="Model name")
    args = parser.parse_args()

    # Update global settings if provided
    if args.api_url != BASE_URL:
        BASE_URL = args.api_url
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    if args.model != MODEL_NAME:
        MODEL_NAME = args.model

    print(f"Using API endpoint: {BASE_URL}")
    print(f"Using model: {MODEL_NAME}")

    # Ensure nltk data is available
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print("Downloading nltk punkt tokenizer...")
        nltk.download('punkt')

    if args.command == "chunk":
        stage1_create_chunks(args.input_file)
    elif args.command == "analyze":
        if not args.input_file.endswith("-chunks.json"):
            print("Warning: analyze command expects a -chunks.json file")
        stage2_analyze_motivation(args.input_file, args.max_chunks)
    elif args.command == "full":
        print("Running full pipeline...")
        chunks_file = stage1_create_chunks(args.input_file)
        stage2_analyze_motivation(chunks_file, args.max_chunks)


if __name__ == "__main__":
    main()
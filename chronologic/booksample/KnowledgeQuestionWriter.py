import json, os 
import requests
from typing import Optional

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gpt-oss:20b"

SYSTEM_PROMPT = """You are a question writer for a historical knowledge benchmark. Given a passage from a 19th century encyclopedia and an answer span, generate a question that would elicit that answer.

A good question:
- Can be answered with ONLY the answer span (not a longer or shorter phrase)
- Has exactly one correct answer given the passage
- Does not use pronouns or vague references that require the passage to resolve
- Fully spells out any names or places (no abbreviations like "P.")
- Does not refer to the passage, e.g., "What place is mentioned in the definition of..."  
- Does not state the answer in the question itself

If no unambiguous question is possible (e.g., the answer is too generic, appears multiple times with different meanings, or lacks sufficient context), respond with SKIP and a brief reason.

Respond in exactly this format:
QUESTION: [your question]
or
SKIP: [reason]"""

FEW_SHOT_EXAMPLES = """
---
Passage: PHILIPPSBURG: town of Baden, on the right bank of the Rhine; anciently one of the most important fortresses on the Rhine. The fortifications were destroyed 1800.
Answer span: 1800
Entity type: DATE

QUESTION: In what year were the fortifications of Philippsburg destroyed?
---
Passage: PHILLIPS, JOHN, LL.D.: 1719, Dec. 6-1795, Apr. 21; b. Andover, Mass.: philanthropist. He graduated at Harvard College 1735.
Answer span: Harvard College
Entity type: ORG

QUESTION: From which institution did the philanthropist John Phillips graduate in 1735?
---
Passage: PEDRO II. (Dom PEDRO DE ALCANTARA), ex-Emperor of Brazil: born Rio Janeiro, 1825, Dec. 2 (reigned 1841-89); died 1891, Dec. 5; son of Pedro I.
Answer span: Rio Janeiro
Entity type: GPE

QUESTION: In what city was Emperor Pedro II of Brazil born?
---
Passage: The Amazon river was made free to all nations 1867. Journeys were made by P. to Europe 1871-2.
Answer span: 1867
Entity type: DATE

SKIP: Multiple dates in passage; "the Amazon river was made free" lacks enough context for someone without the passage to know this refers to Brazil's navigation policy.
---
Passage: He was a man of noble presence and character, highly cultivated, interested especially in science.
Answer span: science
Entity type: MISC

SKIP: Answer is too generic and the passage uses only pronouns, making an unambiguous question impossible.
---"""


def generate_question(passage: str, answer_span: str, entity_type: str, debug: bool = False) -> dict:
    """
    Call ollama to generate a question for the given answer span.
    """
    
    prompt = f"""{SYSTEM_PROMPT}

{FEW_SHOT_EXAMPLES}
---
Passage: {passage}
Answer span: {answer_span}
Entity type: {entity_type}

"""
    
    if debug:
        print(f"\n{'='*60}")
        print(f"PROMPT LENGTH: {len(prompt)} chars")
        print(f"PASSAGE LENGTH: {len(passage)} chars")
        print(f"PROMPT PREVIEW:\n{prompt[:500]}...")
        print(f"{'='*60}")
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 750,
                }
            },
            timeout=120  # Increase timeout for long prompts
        )
        
        if debug:
            print(f"HTTP STATUS: {response.status_code}")
            print(f"RAW RESPONSE: {response.text[:1000]}")
        
        if response.status_code != 200:
            return {
                "status": "error", 
                "reason": f"HTTP {response.status_code}: {response.text[:200]}"
            }
        
        resp_json = response.json()
        
        if debug:
            print(f"RESPONSE KEYS: {resp_json.keys()}")
            for k, v in resp_json.items():
                print(f"  {k}: {str(v)[:100]}")
        
        if "error" in resp_json:
            return {"status": "error", "reason": f"Ollama error: {resp_json['error']}"}
        
        result_text = resp_json.get("response", "").strip()
        
        if not result_text:
            return {"status": "error", "reason": "Empty response from model"}
        
        # Parse response
        if result_text.startswith("QUESTION:"):
            question = result_text[9:].strip()
            return {"status": "success", "question": question}
        elif result_text.startswith("SKIP:"):
            reason = result_text[5:].strip()
            return {"status": "skip", "reason": reason}
        else:
            return {"status": "error", "reason": f"Unexpected format: {result_text[:100]}"}
            
    except requests.exceptions.ConnectionError:
        return {"status": "error", "reason": "Connection refused - is ollama running?"}
    except requests.exceptions.Timeout:
        return {"status": "error", "reason": "Request timed out"}
    except json.JSONDecodeError as e:
        return {"status": "error", "reason": f"Invalid JSON response: {e}"}
    except Exception as e:
        return {"status": "error", "reason": f"{type(e).__name__}: {e}"}

def process_chunks(input_path: str, output_path: str, max_entities_per_chunk: int = 20):
    """
    Process chunks from jsonl file, generate questions for each entity.
    """
    
    results = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            chunk = json.loads(line)
            passage = chunk['text']
            entities = chunk['entities']
            
            print(f"\n=== Chunk {line_num + 1} (lines {chunk['start_line']}-{chunk['end_line']}) ===")
            print(f"    {len(entities)} entities found")
            
            # Dedupe entities (same span might appear multiple times)
            seen = set()
            unique_entities = []
            for span, label in entities:
                if span not in seen:
                    seen.add(span)
                    unique_entities.append((span, label))
            
            # Optional: filter short/noisy entities here
            filtered = [
                (span, label) for span, label in unique_entities
                if len(span) >= 3 and label not in ('CARDINAL', 'ORDINAL')
            ]
            
            # Limit per chunk to control costs/time
            filtered = filtered[:max_entities_per_chunk]
            
            for span, label in filtered:
                print(f"  → {label}: {span[:50]}...", end=" ")
                
                result = generate_question(passage, span, label)
                result.update({
                    "passage": passage,
                    "answer_span": span,
                    "entity_type": label,
                    "chunk_start": chunk['start_line'],
                    "chunk_end": chunk['end_line'],
                })
                
                if result['status'] == 'success':
                    print(f"✓ {result['question'][:60]}...")
                elif result['status'] == 'skip':
                    print(f"⊘ {result['reason'][:40]}...")
                else:
                    print(f"✗ {result.get('reason', 'Unknown error')[:50]}")
                
                results.append(result)
    
            # Write results
            with open(output_path, 'w', encoding='utf-8') as f:
                for r in results:
                    f.write(json.dumps(r, ensure_ascii=False) + '\n')
            
            # Summary
            successes = sum(1 for r in results if r['status'] == 'success')
            skips = sum(1 for r in results if r['status'] == 'skip')
            errors = sum(1 for r in results if r['status'] == 'error')
            
            print(f"\n=== Summary ===")
            print(f"Questions generated: {successes}")
            print(f"Skipped: {skips}")
            print(f"Errors: {errors}")
            print(f"Output written to: {output_path}")
    
    return results


if __name__ == "__main__":
    # print the working directory

    print("Working directory:", os.getcwd())

    # change to the directory of this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    test_chunk = json.loads(open("encyclopedia.jsonl").readline())
    result = generate_question(
        test_chunk['text'], 
        test_chunk['entities'][0][0],  # first entity span
        test_chunk['entities'][0][1],  # first entity type
        debug=True
    )
    print(result)
    
    results = process_chunks(
        input_path="encyclopedia.jsonl",
        output_path="questions.jsonl",
        max_entities_per_chunk=20
    )
# Character Question Formation Script - Specification

## Overview
`form_character_questions.py` generates benchmark questions by combining character descriptions and dialogue passages from the previous two scripts. The script presents questions interactively for user approval.

## Purpose
This is the third script in the character modeling pipeline. It pairs character descriptions with dialogue passages to create multiple-choice questions with ground truth answers and distractors (both from the same book and anachronistic from contemporary LLMs).

## Processing Pipeline

1. Load character descriptions and dialogue from JSONL files
2. Load or prompt for book metadata
3. Pair descriptions with dialogue to create Character objects
4. Loop: randomly select character and unused dialogue
5. Generate question (50% with summary, 50% without)
6. Select distractors from same book
7. Generate anachronistic distractor via gpt-oss:20b
8. Present question for interactive user approval
9. Write approved questions to JSONL output file

## Command-Line Interface

```bash
python character/form_character_questions.py DESCRIPTIONS_FILE DIALOGUE_FILE OUTPUT_FILE [OPTIONS]

Required:
  DESCRIPTIONS_FILE       Path to character descriptions .jsonl file
  DIALOGUE_FILE           Path to character dialogue .jsonl file
  OUTPUT_FILE             Path to output questions .jsonl file

Optional:
  --metadata FILE         Path to JSON file with book metadata
  --dictionary FILE       Path to word frequency dictionary (default: ../MainDictionary.txt)
  --start-from N          Resume from question N (default: 0)
  --debug                 Print debug information
```

## Input Formats

### Character Descriptions JSONL (from script 1)
```json
{"character_names": ["Elsie", "Miss Elsie"], "descriptions": [[3, "Elsie took after her mother..."], [12, "Elsie was a silent child..."]]}
```

### Character Dialogue JSONL (from script 2)
```json
{"character_names": ["Elsie", "Miss Elsie"], "character_dialogue": [{"chunk": 8, "character": "Elsie", "dialogue": "Father, why are you so late?", "summary": "Stephanus returns home and finds Elsie", "passage": "When Stephanus returned home..."}]}
```

### Metadata JSON (optional)
```json
{
  "source_title": "A Vendetta of the Desert",
  "source_author": "W. C. Scully",
  "source_date": 1898,
  "source_htid": "hvd.32044082646845",
  "author_nationality": "South African",
  "genre": "novel",
  "author_birth": 1855
}
```

If not provided, prompt user interactively for each field.

## Output Format

**JSONL file** (one question per line):

```json
{
  "metadata_frame": "This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.",
  "main_question": "The character in question here is Elsie, who is described this way in the book:\n\"Elsie took after her mother; she was of fair complexion.\", \"Elsie was a silent child.\"\n\nAt one moment in the book, Stephanus returns home and finds Elsie. Write a short passage of dialogue (1-3 sentences) that Elsie might speak in this situation:",
  "source_title": "A Vendetta of the Desert",
  "source_author": "W. C. Scully",
  "source_date": 1898,
  "author_nationality": "South African",
  "source_genre": "novel",
  "author_birth": 1855,
  "source_htid": "hvd.32044082646845",
  "question_category": "character_modeling_with_summary",
  "question_process": "automatic",
  "answer_types": ["ground_truth", "same_character", "same_book", "anachronistic_gpt-oss:20b"],
  "answer_strings": ["Father, why are you so late tonight?", "I heard the horses neighing.", "Late, yes it is late.", "Hey Dad, what's up? Running behind schedule?"],
  "answer_probabilities": [1.0, 0.0, 0.0, 0.0],
  "passage": "When Stephanus returned home after the encounter with Gideon he found the blind child waiting for him under a large mulberry tree..."
}
```

## Core Data Structures

### Character Class
```python
class Character:
    """
    Represents a character with paired descriptions and dialogue.

    Attributes:
        names: List[str] - All name variants
        longest_name: str - Longest name for display
        descriptions: List[Tuple[int, str]] - (chunk_index, description_text)
        dialogue_passages: List[Dict] - Dialogue entries with chunk, dialogue, summary, passage
        used_dialogue_indices: Set[int] - Indices of dialogue passages already used
    """
```

## Core Functions

### 1. Metadata and Dictionary Handling

**`load_metadata(metadata_file: Optional[str]) -> Dict[str, Any]`**
- If file provided, load JSON
- Otherwise, prompt user interactively for required fields
- Validate all fields present and correct types
- Return metadata dict

**`build_metadata_frame(metadata: Dict) -> str`**
- Format: "This question asks you to provide dialogue for a character in a book. The book in this case is a {genre} published in {source_date} by {source_author}, a {author_nationality} writer born in {author_birth}."

**`load_common_words_set(dictionary_file: str, max_words: int = 10000) -> Set[str]`**
- Load MainDictionary.txt (first ~10,000 words)
- Convert to lowercase set for fast lookup
- Used to determine if first word of summary should be lowercased
- Gracefully handle missing file

**`preprocess_summary(summary: str, common_words: Set[str]) -> str`**
- Extract first word from summary
- If found in common_words set: lowercase the first word
- If NOT found (likely proper noun): keep original capitalization
- Return preprocessed summary

### 2. Character Loading and Pairing

**`load_characters(descriptions_file: str, dialogue_file: str) -> List[Character]`**
- Load both JSONL files
- Match descriptions with dialogue by character_names (any name overlap)
- Create Character objects for matches
- Warn about unmatched descriptions or dialogue

### 3. Description Building

**`build_character_description(descriptions: List[Tuple[int, str]], max_words: int = 150) -> Optional[str]`**

Algorithm:
1. For each description chunk (in chunk order):
   - Split into sentences using nltk.sent_tokenize
   - Track current word count
   - Add complete sentences until next would exceed max_words
   - Enclose each chunk's text in quotes
   - Separate chunks with commas
2. Check final length: 10-150 words
3. Return description string or None if constraints not met

Example output:
```
"Elsie took after her mother; she was of fair complexion.", "Elsie was a silent child and possessed a calm and happy nature."
```

### 4. Question Generation

**`generate_question(character: Character, dialogue_index: int, metadata_frame: str, use_summary: bool, common_words: Set[str]) -> Dict`**

Creates question dict with:
- metadata_frame
- character_portion (CHARACTER_PORTION template)
- question_text (NO_SUMMARY or WITH_SUMMARY template)
- ground_truth (dialogue truncated to 3 sentences)
- dialogue_chunk_index (for distractor selection)
- passage (original passage from dialogue entry)

Note: When use_summary=True, the summary is preprocessed to potentially lowercase the first word.

### 5. Distractor Selection

**`select_distractors(characters: List[Character], question_char: Character, dialogue_idx: int, use_summary: bool) -> Tuple[Optional[str], Optional[str]]`**

Returns: (same_character_distractor, other_character_distractor)

**If NO_SUMMARY (use_summary=False):**
- Both distractors from different characters
- Select based on chunk proximity to ground truth

**If WITH_SUMMARY (use_summary=True):**
- First distractor: Different dialogue from same character (if available)
- Second distractor: Dialogue from different character
- Prefer chunks close to ground truth chunk number

**`truncate_to_sentences(text: str, max_sentences: int) -> str`**
- Split into sentences using nltk.sent_tokenize
- Return first N sentences joined
- Strip quotation marks from result

### 6. Anachronistic Distractor Generation

**`generate_anachronistic_distractor(question_text: str, max_attempts: int = 2) -> Optional[str]`**

Prompt template:
```python
ANACHRONISTIC_PROMPT = """Answer the following question with a short passage of dialogue (1-3 sentences):

{question_text}

Write only the dialogue, without quotation marks:"""
```

Algorithm:
1. Send full question to gpt-oss:20b (num_predict=1500)
2. Parse response, truncate to 3 sentences
3. Strip quotation marks
4. Present to user for approval (y/n)
5. If rejected and attempts < max_attempts, retry
6. Return distractor string or None if all attempts failed

### 7. Interactive Approval Interface

**`present_question_for_approval(question_dict: Dict, distractors: List[str], question_num: int) -> str`**

Display format:
```
========================================
QUESTION #N

[metadata_frame]

[character_portion]

[question_text]

Ground Truth:
  [ground_truth_answer]

Distractors:
  1. [same_character or other_book]
  2. [other_book]
  3. [anachronistic]

========================================
Accept (y/n)? [Enter = n]
Commands: y (accept), n/Enter (reject), p (show passage), stop (exit)
```

Commands:
- `y`: Accept question, write to output, continue
- `n` or Enter: Reject question, mark dialogue as used, continue
- `p`: Display the original passage from the novel
- `stop`: Exit the program

Returns: "accept", "reject", or "stop"

### 8. Question Output Format

**`format_question(question_dict: Dict, metadata: Dict, distractors: List[str], use_summary: bool) -> Dict`**

Determines answer_types based on use_summary and available distractors:
- WITH_SUMMARY + same_character available: ["ground_truth", "same_character", "same_book", "anachronistic_gpt-oss:20b"]
- WITH_SUMMARY + no same_character: ["ground_truth", "same_book", "same_book", "anachronistic_gpt-oss:20b"]
- NO_SUMMARY: ["ground_truth", "same_book", "same_book", "anachronistic_gpt-oss:20b"]

### 9. Main Processing Loop

**`process_questions(characters: List[Character], metadata: Dict, output_file: str, common_words: Set[str], start_from: int = 0) -> None`**

Main question generation loop:
1. Build metadata frame once
2. Filter characters with unused dialogue
3. Randomly select character and unused dialogue
4. Random choice: with or without summary (50/50)
5. Generate question (with summary preprocessing if needed)
6. Select distractors from book
7. Generate anachronistic distractor
8. Present for approval
9. Mark dialogue as used regardless of acceptance
10. If accepted, format and write to output file
11. Continue until no characters have unused dialogue

## Constants

```python
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gpt-oss:20b"
TEMPERATURE = 0.7  # Higher for creative dialogue generation
NUM_PREDICT = 1500
TIMEOUT = 120
MAX_DESCRIPTION_WORDS = 150
MIN_DESCRIPTION_WORDS = 10

METADATA_FRAME = """This question asks you to provide dialogue for a character in a book. The book in this case is a {genre} published in {source_date} by {source_author}, a {author_nationality} writer born in {author_birth}."""

CHARACTER_PORTION = """The character in question here is {longest_character_name}, who is described this way in the book:
{character_description}
"""

NO_SUMMARY = """
Write a short passage of dialogue (1-3 sentences) that we might expect from {longest_character_name}:"""

WITH_SUMMARY = """
At one moment in the book, {summary}. Write a short passage of dialogue (1-3 sentences) that {longest_character_name} might speak in this situation:"""
```

## Error Handling

| Error Type | Handling |
|------------|----------|
| Descriptions file not found | Exit with error message |
| Dialogue file not found | Exit with error message |
| Metadata file not found | Prompt user interactively for metadata |
| Invalid JSON in input files | Exit with error message |
| No matching characters found | Exit with error message |
| Character description too short/long | Skip character, print warning |
| Insufficient distractors | Skip dialogue, mark as used, continue |
| Ollama connection refused | Print error, retry once, then skip question |
| Keyboard interrupt | Save progress, exit gracefully |

## Edge Cases

- **Character with only 1 dialogue (WITH_SUMMARY)**: Use two same_book distractors instead of same_character + same_book
- **Tied chunk distances**: Random selection among tied options
- **Description building edge cases**:
  - Single description < 10 words: Skip character
  - All descriptions together < 10 words: Skip character
  - First description > 150 words: Truncate at sentence boundary
- **Summary capitalization**: Use dictionary lookup to determine if first word should be lowercased
- **Empty dialogue after truncation**: Skip and retry with different selection

## Dependencies

```python
import json
import os
import sys
import argparse
import requests
import random
from typing import Dict, Any, List, Optional, Tuple, Set
import nltk
from nltk import sent_tokenize
```

## Testing Strategy

**Phase 1: Data loading test**
```bash
python character/form_character_questions.py \
    character/test_characters.jsonl \
    character/test_dialogue.jsonl \
    character/test_questions.jsonl \
    --metadata character/test_metadata.json \
    --debug
```

**Phase 2: Interactive approval test**
```bash
python character/form_character_questions.py \
    character/32044082646845_characters.jsonl \
    character/32044082646845_dialogue.jsonl \
    character/32044082646845_questions.jsonl \
    --metadata character/32044082646845_metadata.json
```

**Phase 3: Resume capability test**
```bash
python character/form_character_questions.py \
    character/32044082646845_characters.jsonl \
    character/32044082646845_dialogue.jsonl \
    character/32044082646845_questions.jsonl \
    --start-from 5
```

## Implementation Notes

- Script should be **self-contained** - copy call_ollama_model() and other needed utilities
- Progressive output writing: append to file after each accepted question
- Random selection with proper seeding for reproducibility
- Clear user feedback at each step
- Graceful handling of Ctrl+C - save state and allow resume
- Description building: Use actual quote characters for clarity
- **Summary preprocessing**: Use MainDictionary.txt to determine if first word should be lowercased
  - Load dictionary into set at startup (first ~10k words)
  - If first word (lowercased) is in set → lowercase it in summary
  - If not in set → likely proper noun, keep original capitalization
  - Dictionary path configurable via --dictionary argument
  - Gracefully handle missing dictionary file

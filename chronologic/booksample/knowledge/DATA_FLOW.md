# Knowledge Question Pipeline - Data Flow

This document describes the pipeline for generating historical knowledge benchmark questions from encyclopedia texts.

## Pipeline Overview

```
Raw Text → AnswerSpanExtractor → KnowledgeQuestionWriter → RoundTripChecker → AnswerAcceptor → ManualDistractors → convert_knowledge_format
```

## Production Scripts (Current)

| Stage | Script | Input | Output |
|-------|--------|-------|--------|
| 1. Extract spans | `AnswerSpanExtractor.py` | `encyclopedia2.jsonl` | `cyclopedia2questions.jsonl` |
| 2. Generate questions | `KnowledgeQuestionWriter.py` | `cyclopedia2questions.jsonl` | same file (enriched) |
| 3. Validate | `RoundTripChecker.py` | `cyclopedia2questions.jsonl` | `validated_cyclopedia2questions.jsonl` |
| 4. Accept | `AnswerAcceptor.py` | validated JSONL | `knowledge_questions.jsonl` |
| 5. Add distractors | `ManualDistractors.ipynb` | `knowledge_questions.jsonl` | `knowledge_questions_with_distractors.jsonl` |
| 6. Format conversion | `convert_knowledge_format.py` | with_distractors JSONL | `HN5BS8_knowledgequestions.jsonl` |

## Script Descriptions

### Stage 1: AnswerSpanExtractor.py
Divides text into ~200-word chunks at sentence boundaries. Uses Ollama LLM to extract significant spans (PERSON, DATE, LOCATION, TECHNICAL_TERM, etc.).

```bash
python AnswerSpanExtractor.py input.txt output.jsonl [--max-chunks N] [--debug]
```

### Stage 2: KnowledgeQuestionWriter.py
Generates questions for each extracted span. Applies 6-criterion quality filter:
- WORLD_KNOWLEDGE, REAL_ENTITIES, CLEAR_REFERENCES, NO_ANSWER_LEAK, GRAMMATICAL, UNAMBIGUOUS

```bash
python KnowledgeQuestionWriter.py chunks.jsonl questions.jsonl [--max-entities 20] [--start-line 1]
```

### Stage 3: RoundTripChecker.py
Validates questions by asking the model to answer them and comparing to expected spans using fuzzy matching (ratio > 0.9 or contained with length_ratio < 1.8).

**Note:** Has hardcoded input/output filenames (`cyclopedia2questions.jsonl` → `validated_cyclopedia2questions.jsonl`).

### Stage 4: AnswerAcceptor.py
Interactive CLI for manual review. Commands: `a`(accept), `r`(reject), `p`(show passage), `answer STRING`, `question STRING`, `b`(break).

```bash
python AnswerAcceptor.py input.jsonl output.jsonl
```

### Stage 5: ManualDistractors.ipynb (Notebook only)
Interactive notebook for adding 3 manual distractors per question.

### Stage 6: convert_knowledge_format.py
Transforms fields for unified benchmark format:
- `question` → `main_question`
- `source` → `source_title`
- Adds author metadata fields

## Notebook vs Script Versions

| File | Status | Notes |
|------|--------|-------|
| `AnswerAcceptor.ipynb` | **Superseded** | Use `AnswerAcceptor.py` (CLI version) |
| `AnswerSpanExtractor_HN5BS8.ipynb` | **Superseded** | Dataset-specific variant (Jan 5) |
| `AnswerSpanExtractor_Generalized.ipynb` | **Development** | Newer generalized version (Jan 27) |
| `ManualDistractors.ipynb` | **Production** | No .py equivalent; interactive by design |
| `CreateIndividualMetadataFiles.ipynb` | **Production** | Post-processing; outputs to `process_files/` |

## Data Files

### Active Pipeline
| File | Lines | Purpose |
|------|-------|---------|
| `encyclopedia2.jsonl` | 800 | Raw encyclopedia input |
| `cyclopedia2questions.jsonl` | 1,219 | Main working file (stages 1-3) |
| `validated_cyclopedia2questions.jsonl` | 693 | Validated questions |
| `knowledge_questions.jsonl` | 55 | Accepted questions |
| `knowledge_questions_with_distractors.jsonl` | 55 | Final with distractors |

### Legacy/Deprecated
| File | Notes |
|------|-------|
| `encyclopedia.jsonl` | Smaller test dataset (25 lines) |
| `questions.jsonl` | Legacy output |
| `oldquestions.jsonl` | Duplicate of questions.jsonl |
| `validated_questions.jsonl` | Legacy validation output |

## Model Configuration

All scripts use local Ollama with `gpt-oss:20b`:
```python
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gpt-oss:20b"
```

---
*Last updated: January 2025*

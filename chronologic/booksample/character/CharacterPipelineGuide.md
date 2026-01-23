# Character Question Pipeline: User Guide

This guide explains how to generate character-modeling benchmark questions from fiction. The process extracts character descriptions and dialogue from novels, then creates multiple-choice questions that test whether a language model can produce dialogue appropriate to a specific character.

## What You'll Need

### Software requirements
- **Python 3.10+** with packages: `nltk`, `requests`
- **Ollama** running locally with the `gpt-oss:20b` model loaded
- Realistically, this assumes you're running on a machine that can handle gpt-oss:20b, which might take 64GB, or at least mistral-small:24b. Quantized, that requires 12GB of GPU VRAM. Which probably means Apple Silicon with 16GB, or a non-Apple machine with a 4080 or 4090 GPU. Might work on Colab Pro. If that's not available, we need to rewrite this to run in some other context.

To check if Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

If not running, start it with `ollama serve` in a separate terminal, then pull the model:
```bash
ollama pull gpt-oss:20b
```

### Input files
- **Source texts**: Plain text files of novels (one per book), placed in the `IDI_sample_1875-25/` directory
- **Metadata CSV**: `primary_metadata.csv` containing book and author information
- **Book list**: `fiction_to_process.txt` listing which books to process

## Overview of the Two Stages

The pipeline has two stages with different levels of automation:

| Stage | Script | Mode | What it does |
|-------|--------|------|--------------|
| 1 | `batch_extract.py` | Fully automated | Reads each novel and extracts character descriptions and dialogue |
| 2 | `batch_questions.py` | Interactive | Generates questions with human review of each one |

Stage 1 can run unattended for hours. Stage 2 requires you to approve each question, so plan to be present.

---

## Preparing Your Book List

Edit `fiction_to_process.txt` to list the books you want to process. Each line should contain a barcode (the filename stem without `.txt`):

```
HNNWY1
HXDI7Y
32044082646845
```

Lines starting with `#` are ignored, so you can add comments:

```
# Irish fiction
HNNWY1
HNPEIJ

# American historical fiction
HXDI7Y
```

### How barcodes map to files

The barcode in your list maps to files in two ways:

| What | Format | Example |
|------|--------|---------|
| Source text file | `IDI_sample_1875-25/{BARCODE}.txt` | `IDI_sample_1875-25/HNNWY1.txt` |
| CSV metadata lookup | `hvd.{barcode}` (lowercase) | `hvd.hnnwy1` |

The scripts handle this conversion automatically.

---

## Stage 1: Extracting Characters and Dialogue

### Running the extraction

```bash
cd character
python batch_extract.py
```

This processes each book in your list, running two extraction passes:

1. **Character descriptions**: Scans the novel for passages where named characters are explicitly described
2. **Character dialogue**: Finds substantial dialogue spoken by those characters

### What you'll see

For each book, the script prints progress as it processes ~700-word chunks:

```
[42/187] "I must go to him at once," said Eleanor...  ✓ Eleanor: a young woman of perhaps...
[43/187] The morning light streamed through the...   ○ (no description)
[44/187] Connection refused - is ollama running?     ✗ Connection refused
```

- `✓` = Found a character description or dialogue
- `○` = No relevant content in this chunk (most chunks)
- `✗` = Error (usually Ollama connection issues)

### Output files

For each book, Stage 1 creates two files in `process_files/`:

| File | Contents |
|------|----------|
| `{BARCODE}_characters.jsonl` | Character names and their descriptions |
| `{BARCODE}_dialogue.jsonl` | Dialogue passages with scene summaries |

### Command-line options

| Option | Effect |
|--------|--------|
| `--dry-run` | Show what would be processed without running |
| `--force` | Re-process books even if output files exist |
| `--max-books N` | Process only the first N books |

### Resuming after interruption

If you stop the script (Ctrl+C) or it crashes, just run it again. Books with completed `_dialogue.jsonl` files are automatically skipped.

### Time expectations

Each book takes roughly 30-90 minutes depending on length. A 400-page novel might have ~250 chunks, each requiring an LLM call.

---

## Stage 2: Generating Questions

### Running question generation

```bash
python batch_questions.py
```

This is interactive—you'll review and approve each question.

### The workflow for each book

1. **Book info display**: Shows title, author, publication date from the CSV

2. **Metadata entry** (first time only): You'll be prompted for:
   - Author nationality (e.g., "British", "American")
   - Genre (default: "novel")
   - Author birth year

   This is saved to `{BARCODE}_metadata.json` and reused if you resume later.

3. **Question generation loop**: For each question, you'll see:
   - The question prompt (metadata frame + character description + question)
   - The ground truth answer (actual dialogue from the book)
   - Two distractor answers from other characters in the same book

   You can:
   - `y` = Accept this question
   - `n` = Reject and try another
   - `p` = View the original passage for context
   - `stop` = Stop processing this book

4. **Anachronistic distractor**: If you accept a question, the script generates a third distractor using the LLM (dialogue that sounds modern/anachronistic). You approve or reject this too.

5. **Continue prompt**: After each book, choose whether to continue to the next one.

### What makes a good question?

When reviewing questions, consider:

- **Is the character description informative?** It should give enough context that someone familiar with the book's era could imagine the character.
- **Is the ground truth dialogue distinctive?** Generic dialogue ("Yes, I understand") makes for weak questions.
- **Are the distractors plausible?** They should be wrong but not obviously wrong.

### Output files

Approved questions are appended to `{BARCODE}_questions.jsonl`. Each question includes:

- The full question text
- Four answer options (ground truth + 3 distractors)
- Metadata (title, author, date, genre, etc.)
- The original passage for reference

### Resuming

The script tracks which dialogue passages have been used. If you stop and restart, it picks up where you left off, selecting from unused dialogue.

---

## Parameters You Can Adjust

### In the extraction scripts

These constants appear at the top of `extract_character_descriptions.py` and `extract_character_dialogue.py`:

| Parameter | Default | Effect |
|-----------|---------|--------|
| `MODEL` | `"gpt-oss:20b"` | Which Ollama model to use |
| `TEMPERATURE` | `0.3` | Lower = more deterministic responses |
| `MAX_WORDS_PER_CHUNK` | `700` | Chunk size for processing |
| `DEFAULT_SKIP_LINES` | `25` | Lines to skip at start of file (headers, title pages) |

### In the question formation script

In `form_character_questions.py`:

| Parameter | Default | Effect |
|-----------|---------|--------|
| `TEMPERATURE` | `0.7` | Higher for more creative anachronistic distractors |
| `MAX_DESCRIPTION_WORDS` | `150` | Maximum words in character description |
| `MIN_DESCRIPTION_WORDS` | `10` | Skip characters with very short descriptions |
| `MIN_DIALOGUE_WORDS` | `10` | Skip very brief dialogue passages |

### Adjusting skip lines per book

If a particular book has an unusually long front matter, you can run the extraction scripts directly with a custom skip value:

```bash
python extract_character_descriptions.py ../IDI_sample_1875-25/MYBOOK.txt process_files/MYBOOK_characters.jsonl --skip-lines 50
```

---

## Troubleshooting

### "Connection refused - is ollama running?"

Ollama isn't running or isn't responding. In a separate terminal:
```bash
ollama serve
```

### Extraction finds very few characters

Some possibilities:
- The novel may have few explicit character descriptions (common in some styles)
- The `--skip-lines` value may be cutting into the actual text
- OCR quality may be poor (check the source file)

### Questions seem low quality

You can always reject questions with `n`. The script will try another character/dialogue combination. If a book consistently produces poor questions, it may not be suitable for this benchmark.

### "No characters found with both descriptions and dialogue"

The two extraction passes found different characters, or one pass found nothing. Check the `_characters.jsonl` and `_dialogue.jsonl` files to see what was extracted.

---

## File Reference

```
character/
├── fiction_to_process.txt          # Your list of books to process
├── batch_extract.py                # Stage 1: automated extraction
├── batch_questions.py              # Stage 2: interactive questions
├── extract_character_descriptions.py  # (called by batch_extract)
├── extract_character_dialogue.py      # (called by batch_extract)
├── form_character_questions.py        # (called by batch_questions)
└── process_files/                  # All outputs go here
    ├── HNNWY1_characters.jsonl
    ├── HNNWY1_dialogue.jsonl
    ├── HNNWY1_metadata.json
    └── HNNWY1_questions.jsonl
```

The `primary_metadata.csv` and source texts live in the parent `booksample/` directory.

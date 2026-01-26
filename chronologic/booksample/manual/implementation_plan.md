# Implementation Plan: Manual Question Writer Scripts

## Overview

Create two scripts for manually creating question files in `manual/process_files/`:

1. **metadata_elicitation.py** - Reusable module for collecting book/source metadata
2. **manual_question_writer.py** - Interactive CLI for creating manual questions

## File Structure

```
manual/
├── metadata_elicitation.py      # New script
├── manual_question_writer.py    # New script
├── process_files/               # Output directory (create if needed)
│   └── {htid}_manualquestions.jsonl
└── implementation_plan.md       # This file
```

---

## Script 1: metadata_elicitation.py

### Purpose
Collect and validate metadata for a source, optionally using CSV defaults.

### Interface

```python
def elicit_metadata(metadata_file: str = "../primary_metadata.csv",
                    source_htid: str = "") -> dict:
    """
    Returns dict with keys:
    - source_htid, source_title, source_author, source_date
    - author_nationality, source_genre, author_birth, author_profession
    """
```

### Implementation Details

**1. CSV Loading** (model on `connectors/make_cloze_questions.py:169-202`)
- Load CSV, key by `barcode_src` column
- Lookup: `hvd.{htid.lower()}` for numeric barcodes, direct match for alpha

**2. Normalizations to Apply**

| Field | Normalization |
|-------|---------------|
| title | Trim trailing punctuation (.,;:!?), capitalize words >3 letters |
| author | Convert "Last, First" → "First Last" |
| author_nationality | "US" → "American", "UK" → "British" |
| author_birth | Parse first number from authordates (e.g., "1855-" → 1855) |

**3. Dialogue Flow**
```
1. If source_htid blank → prompt: "Enter source_htid:"
2. Lookup htid in CSV for defaults
3. For each field, display default in brackets, accept Enter to confirm:
   "Title [default_value]: "
4. Validate: source_htid and source_date cannot be blank
5. Return complete metadata dict
```

**4. Fields to Collect**
- `source_htid` (required)
- `source_title`
- `source_author`
- `source_date` (required, integer)
- `author_nationality`
- `source_genre`
- `author_birth` (integer or blank)
- `author_profession` (check if column exists in CSV)

---

## Script 2: manual_question_writer.py

### Purpose
Interactive loop for creating manual questions, writing to JSONL files.

### Command Line

```bash
python manual_question_writer.py [--metadata PATH]
```

Default metadata file: `../primary_metadata.csv`

### Main Loop Structure

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Check source_htid                                        │
│    - Empty? → Prompt user for htid                          │
│    - Non-empty? → Continue                                  │
├─────────────────────────────────────────────────────────────┤
│ 2. Check metadata (test: source_date not blank)             │
│    - No metadata? → Call metadata_elicitation.py            │
│    - Has metadata? → Show current htid, prompt for change   │
├─────────────────────────────────────────────────────────────┤
│ 3. Special htid handling ("attribution"/"handcrafted"/      │
│    "refusal")                                               │
│    - Always ask: "Provide new metadata? (y or enter for no)"│
├─────────────────────────────────────────────────────────────┤
│ 4. Confirm htid:                                            │
│    "Source htid is {htid}. New id or [a, h] or enter to     │
│     confirm:"                                               │
│    - "a" → htid = "attribution"                             │
│    - "h" → htid = "handcrafted" (but not all "h*" strings!) │
│    - New value → call metadata_elicitation                  │
│    - Enter → keep current                                   │
├─────────────────────────────────────────────────────────────┤
│ 5. Create question (see below)                              │
├─────────────────────────────────────────────────────────────┤
│ 6. Write to {htid}_manualquestions.jsonl                    │
│ 7. Return to step 1                                         │
└─────────────────────────────────────────────────────────────┘
```

### Question Creation Dialogue

**A. Metadata Frame**

Build default frame using template from `connectors/make_cloze_questions.py:63-65`:
```
The following passage comes from {title}, {a_an_genre} {genre} published
in {year} by {author}, {a_an_nat} {nationality} {profession}.
```
(Use simpler template without author if author is blank/anonymous)

Prompt:
```
"(a)pprove this frame, (b)lank frame, or (m)anually supply frame:"
```

**B. Main Question**
- Required, cannot be blank
- Prompt: `"Enter main question:"`

**C. Question Category**

If htid is "attribution"/"handcrafted"/"refusal" → category = htid (skip dialogue)

Otherwise:
```
"(a)pprove this category or (c)hange it? (enter for approve):"
```
If change, show menu:
```
1. attribution
2. handcrafted
3. refusal
4. textbook
```

**D. Answers (collected one at a time)**

```
For each answer:
  1. Prompt for answer string (required, "" means done after answer 2+)
  2. Prompt for answer type:
     - First answer: always "ground_truth" (automatic)
     - Subsequent: (g)round_truth, (m)anual, (a)nachronistic_manual
  3. Prompt for probability:
     - ground_truth: always 1.0 (automatic)
     - others: default 0.0, user can override with float

After answer 2+: "Add another answer? (n or enter for yes):"
```

**E. Output Record**

```json
{
  "metadata_frame": "...",
  "main_question": "...",
  "answer_strings": ["...", "..."],
  "answer_types": ["ground_truth", "manual"],
  "answer_probabilities": [1.0, 0.0],
  "question_category": "textbook",
  "question_process": "manual",
  "source_title": "...",
  "source_author": "...",
  "source_date": 1911,
  "author_nationality": "American",
  "source_genre": "...",
  "author_birth": 1858,
  "author_profession": "...",
  "source_htid": "hvd.32044106370034"
}
```

Note: No "passage" field for manual questions.

---

## Helper Functions to Implement

### From make_cloze_questions.py (copy/adapt)

| Function | Purpose |
|----------|---------|
| `clean_title(title)` | Trim punctuation, capitalize |
| `reformat_author_name(author)` | "Last, First" → "First Last" |
| `a_or_an(word)` | Grammar helper for articles |
| `barcode_to_csv_key(barcode)` | Convert to `hvd.{lower}` format |

### New Functions

| Function | Purpose |
|----------|---------|
| `normalize_nationality(nat)` | "US" → "American", "UK" → "British" |
| `parse_birth_year(authordates)` | "1855-" → 1855 |
| `build_metadata_frame(metadata)` | Generate default frame from template |

---

## Output Location

Files written to: `manual/process_files/{source_htid}_manualquestions.jsonl`

Special htids always write to their respective files:
- `attribution_manualquestions.jsonl`
- `handcrafted_manualquestions.jsonl`
- `refusal_manualquestions.jsonl`

---

## Verification

1. **Unit test metadata_elicitation.py:**
   - Test with known barcode from primary_metadata.csv
   - Verify normalizations (US→American, author name flip, birth year parse)
   - Test with unknown barcode (no defaults)

2. **Integration test manual_question_writer.py:**
   - Create question with real barcode
   - Create question with "handcrafted" htid
   - Verify JSONL output format matches character/process_files examples
   - Test minimum 2 answers requirement
   - Test answer type/probability rules

3. **Manual walkthrough:**
   - Run full dialogue creating 2-3 questions
   - Inspect output files for correct JSON structure

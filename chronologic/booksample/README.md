ChronoLogic_EN_1875-1924 pipeline
=================================

This directory holds metadata and code for the initial (1875-1924) section of the ChronoLogic English-language benchmark.

The documentation below explores corpus development, reviews the general strategy of the benchmark, and briefly describes the function of subdirectories. (Consult documentation in the subdirectories for more detail.) It also outlines the structure of the JSON objects that represent questions in the benchmark.

corpus
-------

The currently active metadata for the benchmark is in ```primary_metadata.csv```. This shows not only the original library metadata for each volume, but information about genre, author nationality, author profession, etc that the pipeline elicited from me through dialogue each time a new book was selected. Benchmarks for other national contexts might need a column ```linguistic_register,``` with potential values such as 文言文, 白话文, or 早期白话, or 文白夹杂.

If you're interested in the process of corpus development, see ```metadata_history.csv```, which includes all 400 files I initially sampled, and reveals something about the process I used. I started by approving everything and then leapt forward as needed in order to cover sparse parts of the timeline, or get nationalities/genres/author demographics that seemed underrepresented. Also you'll notice some volumes were added manually at the end, mainly in order to get reference/encyclopedias at three points in the timeline (early/middle/late).

how metadata updates
--------------------

When a volume is processed, the user may be queried for missing fields like author_profession, and a json metadata file for that volume is produced in ```json_metadata/```.

The script ```metadata_updater.py``` draws values both from metadata_history and from these enriched metadata files. It also checks the ```process_files/``` directories in each of the subfolders to see if there are {barcode}...questions.jsonl files associated with a volume. If so, it updates the columns that report number of questions created for that volume.

a general note on metadata and "coverage"
-----------------------------------------

There are a lot of different ways to envision historical coverage. Are we trying to represent the actual population of the US in 1890? Should we rebalance our corpus to get 50/50 gender representation? What about geography and dialect?

It would be easy to reach paralysis. The strategy that allows this project to go forward without endlessly debating different normative rationales is to record metadata like genre, profession, nationality, and gender for each volume, and then associate it directly with questions based on that volume. So if we want to know whether a model is biased toward the UK or US, or men, or women, we can ask how well it performs on those questions.

This means that it's not necessary to have an absolutely balanced corpus. Generally, we want to attempt to get a range of volumes that is roughly representative of things published in English 1875-1924. (We concede in advance that we're representing writing, and not the actual English-speaking population.) But the *balance* of the corpus matters less than simply having some modest representation of books by Britons, or women, or conduct books that can tell us if a model is underperforming there.

Many debatable aspects of question-formation have been handled in a similar way. What types of questions are most valuable? How much should we hand-craft them? How should we handle "wrong answers" that are, rationally, possible answers to a question, but expressed in anachronistic terms? All of these variables are recorded in metadata attached to each question (or answer), and the variables can be used to slice our benchmark from different angles, or even give "wrong answers," provisionally, different *degrees of wrongness*.

We will report a top-line number. But the real interest of this benchmark will be our ability to particularize performance by source genre, question type, date, and degree of importance attributed to period style. Perhaps also linguistic register? Uncertainty about the "correctly representative" balance of genres should not daunt or delay us.

overview of question types
--------------------------

So far, I've written code that creates questions in four subdirectories:

1. character/
2. connectors/
3. knowledge/
4. manual/

These are each a separate software pipeline, but there can be multiple question categories in each directory. For instance, the questions in ```connectors``` can have question_category "cloze_concessiveclause" or "cloze_effectsentence," among a total of seven types of rhetorical connection associated with different logical moves. 

In ```manual,``` we have "textbook" questions that were actually formulated in period textbooks of arithmetic &c, "refusal" questions where the model should say it cannot answer, "attribution" questions where the model is asked to identify period, genre, or author, and a generic category of "handcrafted" questions we can thoughtfully design with a variety of explicit aims. This will include handcrafted knowledge questions, multi-hop reasoning questions, and poetry generation tasks.

The ```character``` and ```knowledge``` directories are more unified. ```character``` is based on works of fiction, and asks the model to invent dialogue appropriate to a character, genre, and dramatic situation provided. ```knowledge``` is based on reference works, especially encyclopedias, and asks the model for knowledge not provided in the question.

In all cases except for "refusal," "attribution," and some "handcrafted," the right answer is drawn from a period text. But the importance of style varies greatly. In "knowledge" questions the right answer is typically a named entity, and wrong answers are different named entities; expression is not a major factor. The same is largely true of "textbook" questions. 

On the other hand, style can play a large role in ```character/``` and ```connectors/.``` Here answers are typically a clause, a full sentence, or even several sentences. Also, these questions have "anachronistic distractors" produced by a contemporary language model's effort to answer the question. If these distractors are counted, and probability is set to zero, anachronistic style will be strongly penalized. However, this is adjustable. Probability of these answers can vary smoothly from 0 to 1 if we want to examine a curve. Alternatively, we could use a model trained to measure divergence from 1875-1924 style in order to assign each "wrong answer" a degree of stylistic wrongness.

Answer types in ```connectors/``` have names like "cloze_effectsentence." But they are not really pure cloze questions. In answering these questions, the model is instructed to fill in a blank labeled e.g. "[masked clause describing an inference or effect]" or "[masked sentence revising an implied expectation]". The model can thus benefit both from verbal context and from abstract logical reasoning. Finally, these questions--like most questions in the benchmark--come with "metadata frames" that provide the author's profession and the book's title and date, details which can also inform inference.

In a sense, whenever a question is asked with a metadata frame, the model is being invited to do a kind of multi-hop reasoning. How valuable is this guidance? We don't know *a priori,* and the answer might vary from one model to another. However, the metadata frame is provided separately from the main question, and can be regenerated differently using the metadata fields in the question, so it will possible to suppress or provide particular kinds of metadata and ask how much they help.

guide to specific fields in the json question format
----------------------------------------------------

The documentation below was written by Claude Code after an inspection of existing *questions.jsonl files.

All questions across the benchmark share a common JSON structure, though some fields are optional depending on the pipeline. Each question is stored as a single JSON object per line in JSONL files.

### Core fields (present in all questions)

| Field | Type | Description |
|-------|------|-------------|
| `metadata_frame` | string | Contextual preamble describing the source (title, date, author, genre). Can be regenerated from metadata fields if needed. May be blank for some manual questions. |
| `main_question` | string | The question or prompt presented to the model. |
| `answer_strings` | list[string] | Parallel array of possible answers. First element is always the ground truth. |
| `answer_types` | list[string] | Parallel array labeling each answer's type (see below). |
| `answer_probabilities` | list[float] | Parallel array of probabilities. Ground truth is 1.0; distractors default to 0.0 but can be adjusted. |
| `question_category` | string | Categorizes the question type (see below). |
| `question_process` | string | Either `"automatic"` (pipeline-generated) or `"manual"` (hand-crafted). |

### Source metadata fields

| Field | Type | Description |
|-------|------|-------------|
| `source_htid` | string | HathiTrust identifier (e.g., `"hvd.hnnwy1"`) or special value (`"attribution"`, `"handcrafted"`, `"refusal"`). |
| `source_title` | string | Book title. |
| `source_author` | string | Author name in "First Last" format. |
| `source_date` | int | Publication year. |
| `source_genre` | string | Genre label (e.g., `"novel"`, `"encyclopedia"`, `"work of history and social description"`). |
| `author_nationality` | string | Author's nationality as an adjective (e.g., `"American"`, `"British"`, `"Irish"`). |
| `author_birth` | int or null | Author's birth year, if known. |
| `author_profession` | string | Author's profession (e.g., `"novelist"`, `"historian"`, `"physician"`). |

### Optional fields

| Field | Type | Description |
|-------|------|-------------|
| `passage` | string | The relevant passage from the source text. Present in most automatic questions; absent in some manual questions where no specific passage applies. |

### question_category values

**From `character/` pipeline:**
- `character_modeling_with_summary` — asks the model to generate dialogue appropriate to a character, given character descriptions and a dramatic situation.

**From `connectors/` pipeline (cloze-style questions):**
- `cloze_causalsentence` — masked sentence expressing cause/reason
- `cloze_causalclause` — masked clause expressing cause/reason
- `cloze_effectsentence` — masked sentence expressing inference/effect
- `cloze_effectclause` — masked clause expressing inference/effect
- `cloze_contrastsentence` — masked sentence revising an implied expectation
- `cloze_contrastclause` — masked clause revising an implied expectation
- `cloze_conditionalclause` — masked clause describing a condition or proviso
- `cloze_concessiveclause` — masked clause acknowledging a countervailing fact

**From `manual/` pipeline:**
- `textbook` — questions drawn from period textbooks (arithmetic problems, grammar exercises, etc.)
- `attribution` — questions asking the model to identify period, genre, or author
- `refusal` — questions where the model should recognize it cannot answer (testing appropriate epistemic humility)
- `handcrafted` — general category for carefully designed questions with explicit aims (multi-hop reasoning, poetry generation, etc.)

**From `knowledge/` pipeline:**
- Knowledge questions test factual recall from encyclopedias and reference works. These may have categories added in later development.

### answer_types values

**Ground truth:**
- `ground_truth` — the correct answer drawn directly from the period text. Always probability 1.0.

**Same-source distractors (period-appropriate alternatives):**
- `same_character` — dialogue from the same character in a different scene (character/ pipeline)
- `same_book` — clause or sentence from elsewhere in the same book (connectors/ and character/ pipelines)
- `negation` — semantically inverted version of the ground truth (connectors/ pipeline)

**Anachronistic distractors (generated by contemporary models):**
- `anachronistic_gpt-oss:20b` — generated by the gpt-oss:20b model (fine-tuned on period text)
- `anachronistic_mistral-small:24b` — generated by mistral-small:24b
- `anachronistic_metadataless_gpt-oss:20b` — generated by gpt-oss:20b without metadata context
- Additional model names may appear as `anachronistic_{model_name}`

**Manual distractors:**
- `manual` — distractor entered by a human annotator
- `anachronistic_manual` — anachronistic distractor entered by a human annotator
- `manual_{original_type}` — a human replacement for an automatically-generated distractor

### answer_probabilities

The probability array allows flexible scoring:
- Ground truth answers have probability `1.0`
- Distractors default to `0.0` but can be adjusted to represent degrees of acceptability
- Setting an anachronistic distractor to a small positive value (e.g., 0.2) would give it partial credit, penalizing anachronism less severely
- The benchmark can be sliced by treating different probability thresholds as "correct enough"

### Example question (from connectors/)

```json
{
  "metadata_frame": "The following passage comes from Argentina, a work of history...",
  "main_question": "...Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition or proviso]:",
  "source_title": "Argentina",
  "source_author": "W. A. Hirst",
  "source_date": 1910,
  "author_nationality": "American",
  "source_genre": "work of history and social description",
  "author_birth": 1870,
  "author_profession": "writer",
  "source_htid": "hvd.hwwjnq",
  "question_category": "cloze_conditionalclause",
  "question_process": "automatic",
  "answer_types": ["ground_truth", "negation", "same_book", "same_book", "anachronistic_mistral-small:24b", "anachronistic_metadataless_gpt-oss:20b"],
  "answer_strings": ["provided that punishment does not take the form of...", "provided that punishment involves...", "unless they can count beforehand...", "if the right of collecting debts...", "unless such misconduct involves...", "provided that the state has failed..."],
  "answer_probabilities": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
  "passage": "Further, Mr. Hay, in his reply to Dr. Drago, said..."
}
```


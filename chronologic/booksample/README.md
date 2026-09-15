booksample: the directory where sources were stored and questions developed
===========================================================================

This directory holds metadata and code for the initial (1875-1924) section of the ChronoLogic English-language benchmark.

The documentation below explores corpus development, reviews the general strategy of the benchmark, and briefly describes the function of subdirectories. (Consult documentation in the subdirectories for more detail.) It also outlines the structure of the JSON objects that represent questions in the benchmark.

general strategy
-----------------

The approach we’ve taken tries to balance two conflicting observations.

1. Contemporary expertise is not a sufficient foundation for historical benchmarks. People who have spent decades studying nineteenth-century Britain still cannot reliably express themselves like a member of parliament in 1820 or a Methodist clergyman in 1885. Mode of expression matters; it’s a big part of what we’re aiming to achieve. *So the ground truth for at least some of our questions must be drawn from period texts.*
2. On the other hand, benchmarks are only necessary because the distribution of user input to a language model diverges from the distribution of the training corpus. If the two were the same, after all, we could just evaluate the model with perplexity on held-out texts. But users are different from training data in lots of ways. Benchmarks have to test a model’s ability to handle those differences. In the case of a historical language model, one key difference is that users are living in the 21st century! *Strict historical purity is thus basically the wrong goal: we want some questions to incorporate 21c concepts and 21c language, in order to test the model’s ability to translate between contexts.*

We can resolve this tension by designing multiple types of questions, and keeping track of the sources for both our questions and our answers. Ground truth answers will usually be drawn from period documents, but questions often include a mix of 21c language and period prose. We will track that mix. Distractors (wrong answers) are produced in a variety of ways to test different failure modes.

corpus
-------

The currently active metadata for the benchmark is in ```primary_metadata.csv```. This shows not only the original library metadata for each volume, but information about genre, author nationality, author profession, etc that the pipeline elicited from me through dialogue each time a new book was selected. Benchmarks for other national contexts might need a column ```linguistic_register,``` with potential values such as 文言文, 白话文, or 早期白话, or 文白夹杂.

```metadata_history.csv``` is a document used to create ```primary_metadata.csv```, now mostly obsolete, but it does have some columns not present in the other file.

The corpus includes 187 sources linked to questions. This doesn't fully account for all the questions in the benchmark, because there are also a few questions where the source is diffuse. For instance, when an abstention question is asking for knowledge that *would not have been* available at the time, there is no actual period source for the question, although the metadata frame may posit a hypothetical one ("provide knowledge that would have been available in a British encyclopedia from 1875").

a general note on metadata and "coverage"
-----------------------------------------

There are a lot of different ways to envision historical coverage. Our goal was to get a diverse sample of English-language texts published between 1831 and 1930. 

It is definitely not a population sample of English speakers between those dates; the vast majority of people were not published writers. Nor does it aim to be a population sample of texts published in the period. (We don't even have a complete census of texts published in the period.)

Instead, the hope was simply to cover a wide enough range of genres and topics that the broad outlines of English-language publication would be dimly visible. A small sample like this will never be *sufficient* for coverage of history. But the goal of a benchmark is rather to establish a *necessary* test. A model that can answer these questions may still have important gaps. But one that cannot answer them definitely does.

overview of question types
--------------------------

Questions are produced by seven pipelines, each in its own subdirectory:

1. character/
2. connectors/ and batchconnectors/
3. knowledge/
4. manual/
5. poetry/
6. summary/

These are each a separate software pipeline, but there can be multiple question categories in each directory. For instance, the questions in ```connectors``` can have question_category "cloze_concessiveclause" or "cloze_effectsentence," among a total of seven types of rhetorical connection associated with different logical moves. ```batchconnectors``` is the batch wrapper around the same cloze pipeline, separating LLM processing from interactive approval; both write the same ```*_clozequestions.jsonl```.

In ```manual,``` we have "textbook" questions that were actually formulated in period textbooks of arithmetic &c, "refusal" questions where the model should say it cannot answer, "attribution" questions where the model is asked to identify period, genre, or author, and ```parallax``` questions that contrast different perspectives.

The ```character``` and ```knowledge``` directories are more unified. ```character``` is based on works of fiction, and asks the model to invent dialogue appropriate to a character, genre, and dramatic situation provided. ```knowledge``` is based on reference works, especially encyclopedias, and asks the model for knowledge not provided in the question.

The ```poetry``` directory is a branch of ```manual``` that allows easier entry of questions and answers that contain linebreaks. Categories here include "poetry_generation"", where the answer is a poem, but also "poetic_form", which asks for knowledge of meter and stanza form. "Attribution" questions here may ask for biographical or historical knowledge about famous texts we know were reprinted and discussed in our period.

The ```summary``` directory reframes summarization as infill: it finds paragraphs that contain their own topic sentence, masks it, and asks for a replacement. That yields a ground truth written in the period rather than by us.

In all cases except for "refusal," "attribution," and some "handcrafted," the right answer is drawn from a period text. But the importance of style varies greatly. In "knowledge" questions the right answer is typically a named entity, and wrong answers are different named entities; expression is not a major factor. The same is largely true of "textbook" questions. 

On the other hand, style can play a large role in ```character/``` and ```connectors/.``` 

guide to specific fields in the json question format
----------------------------------------------------

The documentation below was written by Claude Opus 5 to explain why the format produced by scripts in this directory will not align precisely with the final benchmark. It gets into the weeds a bit.

**There are two formats.** This section documents the
**pipeline format** — what the seven question-writing pipelines emit into their
`process_files/` directories. `QuestionCategorizer.py` then assembles those files into the
**released benchmark format**, which is documented in [`../DATA.md`](../DATA.md).

If you are writing code against the benchmark, use `../DATA.md`. Use this section if you
are working on a question pipeline.

Assembly into the benchmark drops two fields and adds eight:

| | Field | Why |
|---|---|---|
| **dropped** | `passage` | Folded into `main_question`; the released file has no separate passage field |
| | `context_judged` | Superseded by `partial_credit`, which records the same routing decision |
| **added** | `question_number` | Stable identifier, assigned at assembly |
| | `reasoning_type` | The eight-way grouping the paper reports (see the mapping below) |
| | `frame_type` | `world_context`, `book_context` or `passage_context` |
| | `partial_credit` | 1 if Bradley-Terry scored, 0 if pass/fail |
| | `answer_length` | `short_answer`, `phrase` or `sentence_plus`, derived from answer lengths |
| | `reject_reasons` | Per-option rubric for the BT judge, on partial-credit questions |
| | `substantive_metadata_frame` | A trimmed frame for substantive judging, where the full frame would give the answer away |
| | `added_answers` | Provenance for distractors added after the first pass |

### Core fields (present in all pipeline output)

| Field | Type | Description |
|-------|------|-------------|
| `metadata_frame` | string | Contextual preamble describing the source (title, date, author, genre). Can be regenerated from metadata fields if needed. May be blank for some manual questions. |
| `main_question` | string | The question or prompt presented to the model. |
| `answer_strings` | list[string] | Parallel array of possible answers. First element is always a ground truth. |
| `answer_types` | list[string] | Parallel array labeling each answer's provenance (see below). |
| `answer_probabilities` | list[float] | Parallel array of admissibility scores (see below). |
| `question_category` | string | Fine-grained question type (see below). |
| `question_process` | string | `"automatic"` (pipeline-generated), `"manual"` (hand-crafted), or `"poetry"` (entered through the poetry writer, which tolerates linebreaks). |

### Source metadata fields

| Field | Type | Description |
|-------|------|-------------|
| `source_htid` | string | HathiTrust identifier (e.g., `"hvd.hnnwy1"`), a newspaper or periodical slug (e.g. `"hvd.exeterandplymouthgazette"`, `"1875-07-15_p4_sn85026421"`), or a special value naming a diffuse source. Three such values survive into the released file: `"knowledge"`, `"attribution"`, `"refusal"` — these are the questions the corpus note above describes as having no single period source. |
| `source_title` | string | Book title. |
| `source_author` | string | Author name in "First Last" format. `"Anonymous"` where unknown. |
| `source_date` | int | Publication year. |
| `source_genre` | string | Genre label (e.g., `"novel"`, `"encyclopedia"`, `"work of history and social description"`). |
| `author_nationality` | string | Author's nationality as an adjective (e.g., `"American"`, `"British"`, `"Irish"`). |
| `author_birth` | int or null | Author's birth year; null where unknown. |
| `author_profession` | string | Author's profession (e.g., `"novelist"`, `"historian"`, `"physician"`). May be empty. |

### Optional fields

| Field | Type | Description |
|-------|------|-------------|
| `passage` | string | The relevant passage from the source text. Present in most automatic questions; absent where no specific passage applies. **Not carried into the released file** — it is folded into `main_question`. |
| `context_judged` | int | Whether the question needs context-sensitive judging. **Superseded** by `partial_credit` in the released file. |
| `period_words_in_main_question` | int | Count of words in the main question drawn verbatim from the original source text. 0 means entirely paraphrased; equal to word count means entirely quoted. |
| `manual_comment` | string | Comment explaining the question's design or any notable considerations. |

### question_category values

Eighteen categories appear in the released benchmark. Grouped by the pipeline that emits
them:

**`character/`** — `character_modeling_with_summary`: generate dialogue appropriate to a character, given descriptions and a dramatic situation.

**`connectors/` and `batchconnectors/`** — cloze questions, named for the logical relation the masked span carries. Sentence-level: `cloze_causalsentence`, `cloze_effectsentence`, `cloze_contrastsentence`. Clause-level: `cloze_causalclause`, `cloze_effectclause`, `cloze_contrastclause`, `cloze_conditionalclause`, `cloze_concessiveclause`.

**`knowledge/`** — `knowledge`: factual recall from encyclopedias and reference works.

**`manual/`** — `textbook` (problems posed in period textbooks), `refusal` (the model should recognize it cannot answer), `parallax` (contrasting perspectives on one question), `constrained_generation` (write to a subject and a form), `inference`.

**`poetry/`** — `poetry_generation` (the answer is a poem), `poetic_form` (knowledge of meter and stanza form).

**`summary/`** — `topic_sentence`.

### How question_category maps to reasoning_type

The released file carries a coarser `reasoning_type`, and this is the grouping the paper's
tables report. The mapping is **not** one-to-one: several categories split across
reasoning types, because the same pipeline can produce questions that test different
abilities. `textbook` is the clearest case — a period arithmetic problem is inference, but
a period definition is knowledge.

| `reasoning_type` | N | from `question_category` |
|---|---:|---|
| `sentence_cloze` | 160 | cloze_effectsentence (63), cloze_contrastsentence (63), cloze_causalsentence (34) |
| `constrained_generation` | 158 | parallax (98), constrained_generation (30), poetry_generation (18), textbook (11), refusal (1) |
| `phrase_cloze` | 155 | cloze_causalclause (36), cloze_contrastclause (32), cloze_concessiveclause (30), cloze_conditionalclause (30), cloze_effectclause (27) |
| `character_modeling` | 115 | character_modeling_with_summary (115) |
| `knowledge` | 94 | knowledge (91), textbook (3) |
| `inference` | 78 | textbook (32), inference (24), knowledge (13), poetic_form (9) |
| `abstention` | 62 | refusal (62) |
| `topic_sentence` | 44 | topic_sentence (44) |

Where the split is not mechanical it was made by hand; see `apply_handcrafted_recategorization.py`.

### answer_types values

The suffix on a type is not always a model name — it can be a **year**. Two whole families
are period-displaced rather than model-generated, and they test a different failure mode:
a passage that is authentic prose but from the wrong moment.

Across the released file's 4,743 answer options, the families break down as:

| Family | N | % | What it is |
|---|---:|---:|---|
| `anachronistic_<model>` | 1042 | 22.0 | Generated by the named model, given the metadata frame |
| `ground_truth` | 952 | 20.1 | Drawn from the period text |
| `manual` | 807 | 17.0 | Written by an editor |
| `same_book` | 782 | 16.5 | Passage from elsewhere in the same source |
| `anachronistic_manual` | 283 | 6.0 | An anachronism written by an editor |
| `anachronistic_metadataless_<model>` | 279 | 5.9 | Generated *without* the frame, so it reads as generically modern |
| `negation` | 212 | 4.5 | Semantically inverted ground truth |
| `same_character` | 110 | 2.3 | Dialogue by the same character in a different scene |
| `other_book_<year>` | 87 | 1.8 | Authentic prose from a *different* book of that year (1875–1995) |
| `manual_negation` | 80 | 1.7 | Editor-written inversion |
| `anachronistic_<year>` | 63 | 1.3 | Authentic prose from the wrong period (1647–2025) |
| `manual_anachronistic_<model>` | 46 | 1.0 | Editor's replacement for a model-generated anachronism |

Notes on the families that are easy to misread:

- **`ground_truth` is not one per question.** 86 questions carry two, which is what makes
  the Bradley-Terry calibration possible: hold one out, score it as a candidate.
- **`same_book` is not wrong about the context**, only about the question. A judge that
  accepts it is making a different error from one that accepts an anachronism, which is why
  judge reliability is measured separately by distractor type.
- **`anachronistic_<year>` and `other_book_<year>`** carry a date, not a model. These are
  real passages placed in the wrong period — the hardest distractors stylistically, since
  nothing about the prose itself is synthetic.
- **Model slugs are recorded verbatim**, including `distort1_` / `distort2_` prefixes for
  deliberately degraded variants. Because the slug names the generator, it is always
  visible when a model would be scored against its own output.

Model names appearing in the file include `gpt-oss:20b`, `mistral-small:24b`,
`qwen3-30b-a3b-instruct-2507`, `gemma-4-31b-it`, `claude-opus-5`, `gpt-5.4` and
`talkie-1930-13b-it`, along with non-model sources `wikipedia`, `google` and `older`.

### answer_probabilities

A graded admissibility score, not a binary flag.

- `1.0` marks a ground truth.
- `0.0` marks a plain distractor.
- **Intermediate values are used**, not merely available: the released file contains 0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.75, 0.8, 0.9 and 0.95. 0.5 is the commonest, marking a distractor that editors judged partly defensible in the given context.

This is what lets the benchmark be sliced by how severely a given failure mode should be penalized, and it is read directly by the Bradley-Terry calibration, which treats probability-0 distractors as the negative class.

### Example question (pipeline format, from connectors/)

Note the `passage` field, which the released file does not have.

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

For the same question as it appears in the released benchmark — with `question_number`,
`reasoning_type`, `frame_type` and `partial_credit`, and without `passage` — see
[`../DATA.md`](../DATA.md), or look it up in the public sample.

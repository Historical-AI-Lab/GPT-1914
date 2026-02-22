poetry
======

Code that allows the user to create questions that are individually designed. These scripts are closely based on the ones in manual/, but adapted to permit answers that have multiple linebreaks, with initial spaces -- as appropriate for poetry.

Question categories will include

1. "poetry_generation" tasks where the model is given a poetic form and subject, and asked to produce a couplet or stanza-length passage of verse; these always have a barcode as source_htid
2. "poetic_form" tasks where the model is given a stanza and asked to identify the meter, rhyme scheme, or form; these also have a barcode as source_htid
3. "attribution" questions where the model is asked to identify period, genre, or author of a famous passage; here the source_htid is "attribution"

## Scripts

- `poetry_question_writer.py` - Interactive CLI for creating new poetry questions
- `metadata_elicitation.py` - Helper module for gathering source metadata

## Question Fields

Each question record in the JSONL output contains:

| Field | Type | Description |
|-------|------|-------------|
| `metadata_frame` | string | Contextual frame for the question (e.g., "In an 1892 novel by Arthur Conan Doyle...") |
| `main_question` | string | The question text |
| `answer_strings` | list[string] | Possible answers |
| `answer_types` | list[string] | Type for each answer: `ground_truth`, `manual`, or `anachronistic_manual` |
| `answer_probabilities` | list[float] | Probability for each answer (ground_truth is always 1.0) |
| `question_category` | string | One of: `attribution`, `handcrafted`, `refusal`, `textbook` |
| `period_words_in_main_question` | int | Count of words in the main question drawn verbatim from the original source text. 0 means the question is entirely paraphrased; equal to word count means entirely quoted. |
| `manual_comment` | string | Optional comment explaining the rationale for this question's design or any notable considerations. |
| `question_process` | string | Always `manual` for questions created by these scripts |
| `source_title` | string | Title of source text |
| `source_author` | string | Author of source text |
| `source_date` | int/null | Publication year |
| `author_nationality` | string | Author's nationality |
| `source_genre` | string | Genre of source text |
| `author_birth` | int/null | Author's birth year |
| `author_profession` | string | Author's profession |
| `source_htid` | string | HathiTrust ID or special category identifier |
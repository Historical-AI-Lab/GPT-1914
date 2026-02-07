manual
======

Code that allows the user to create questions that are individually designed rather than produced by a well-established automatic pipeline.

These may include

1. "textbook" questions that were actually formulated in period textbooks of arithmetic &c, 
2. "refusal" questions where the model should say it cannot answer,
3. "attribution" questions where the model is asked to identify period, genre, or author, 
4. and a generic category of "handcrafted" questions we can thoughtfully design with a variety of explicit aims. This will include handcrafted knowledge questions, multi-hop reasoning questions, and poetry generation tasks.

## Scripts

- `manual_question_writer.py` - Interactive CLI for creating new manual questions
- `augment_existing_questions.py` - Utility to add new fields to existing questions in `process_files/`, writing output to `augmented_files/`
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
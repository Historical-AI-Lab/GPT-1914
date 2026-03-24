Question Categorizer Goals
==========================

The questions for this benchmark are currently contained in individual .jsonl files in the process_files subdirectories of 

batchconnectors/
connectors/
characters/
knowledge/
manual/
poetry/, and
summary/

We need to aggregate them, and simultaneously normalize some fields that have become irregular. A glance at the question_category_census.txt and answer_type_census.txt will reveal a long tail of different question categories and answer types. 

Some of the terms used for answer_types have changed; e.g. the answer_type 'manual_distractor', used in the knowledge/ subfolder, should be normalized to simple 'manual'. I also started out creating distractors of the form 'anachronistic_barcode,' but realized eventually this was too specific, and should really be 'other_book_yyyy', where yyyy is the first publication date for the book with (barcode).

Question categories are even trickier, because I've realized that the old 'question categories' were really, mostly about the source material. The field 'question_category' therefore needs to be supplemented by a couple of new fields that characterize the context invoked in the metadata frame (frame_type), the typical answer_length, and the kind of reasoning required by the question (reasoning_type)

Allowable frame_types are 'world_context', 'book_context', and 'passage_context'.
Allowable answer_lengths are 'short_answer', 'phrase', and 'sentence_plus'.
Allowable reasoning_types are 

1. knowledge (which will include attribution as well as most, but not all, questions currently characterized as 'knowledge')
2. refusal
3. inference (which will include some questions from handcrafted, textbook, and knowledge)
4. character_modeling (both with and without summary)
5. constrained_generation (which includes parallax and poetry_generation)
6. topic_sentence
7. phrase_cloze
8. sentence_cloze

We normalize answer types to one of the following:

1. ground_truth
2. same_book
3. manual
4. negation
5. anachronistic_gpt-oss:20b
6. anachronistic_metadataless_mistral-small:24b
7. anachronistic_mistral-small:24b
8. anachronistic_metadataless_gpt-oss:20b
9. same_character
10. manual_same_book
11. manual_negation
12. anachronistic_gpt-5.2
13. anachronistic_wikipedia
14. anachronistic_sonnet-4.6
15. anachronistic_distort1_gpt-oss:20b	18
16. anachronistic_distort2_mistral-small:24b
17. manual_anachronistic_mistral-small:24b
18. anachronistic_older
19. anachronistic_qwen2.5:7b-instruct
20. manual_anachronistic_gpt-oss:20b
21. manual_anachronistic_metadataless_mistral-small:24
22. anachronistic_yyyy where yyyy is an integer between 1600 and 2025
23. other_book_yyyy where yyyy is an integer between 1875 and 1924
23. anachronistic_google
24. manual_anachronistic_distort2_mistral-small:24b
25. manual_anachronistic_distort2_mistral-small:24b
26. anachronistic_manual

Anything not in that list needs to go through a process where

a) we check if it fits a pattern like 'anachronistic_{barcode}, and if so try to look it up in primary metadata to get a firstpub year so we can make it anachronistic_yyyy or other_book_yyyy

b) if that fails we request manual intervention

Some question_categories need to be folded together automatically. E.g., 'poetic_form' is going to be automatically folded into 'inference'. 

But questions in a few categories require manual inspection so they can be reassigned. For instance, the 'textbook' and 'handcrafted' categories involve a wide range of reasoning types. The user will have to inspect each question to assign a type.

Fortunately the frame_type can be inferred direction from the reasoning_type.

1. knowledge => world_context
2. refusal => world_context
3. inference => world_context
4. character_modeling => book_context
5. constrained_generation => book_context
6. topic_sentence => book_context
7. phrase_cloze => passage_context
8. sentence_cloze => passage_context

However, in some cases the metadata_frame itself may need adjustment. E.g., all the questions in the knowledge/ subfolder need a new frame, which fits the general template for world_context frames.

In QuestionCategorizer.ipynb, I've started to write some of the utility functions needed for a workflow that normalizes questions and writes them to a new aggregated file, titled simply chronologic_en_1875.jsonl. 

I also started to write a cell that would step through the whole process for the knowledge/ subfolder, which is unusually complicated, since knowledge questions always require manual inspection to assign a 'reasoning_type.' (Some might be reassigned to reasoning_type 'inference'.)

But I realized that Jupyter notebooks are not ideal for a process that requires a lot of user interaction.

Can you rewrite that code as a .py script, and also refactor it as needed? You'll need to flesh out one [TODO].

In doing this keep in mind that I have so far only sketched the process for the knowledge/ subfolder.

Some of the other subfolders will be pretty simple. For instance, in poetry, all the questions with question_type 'poetic_form' will go to reasoning_type 'inference', while all with 'poetry_generation' will go to reasoning_type 'constrained_generation.'

Character, connectors, and batchconnectors are also relatively simple.

But the process for 'manual' will be complex. Many different question_categories are represented in that folder, including the 'textbook,' 'knowledge,' and 'handcrafted' categories, which require manual inspection in order to assign a 'reasoning_type'.

In these ambiguous categories, it's also a good idea to give the user an opportunity to manually enter a new metadata_frame if the existing one is inappropriate. That's not needed for 'knowledge' questions actually in the 'knowledge/' subfolder ('knowledge/process_files/HN5BS8_knowledgequestions.jsonl') because those all come from the same source, and will all get the same frame ("The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.") But the 'textbook,' 'knowledge,' and 'handcrafted' categories in the 'manual' folder are diverse, and some may need a new frame.

Build the script so it accepts subfolder (e.g. connectors or manual) as a command-line argument, and uses that argument to select a master function defining a workflow appropriate to the subfolder. Many of the utility functions, e.g. retrieve_date() or display_question_info(), can be reused in all of the workflows.



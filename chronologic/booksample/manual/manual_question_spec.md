specification for manual_question_writer.py
===========================================

This script allows the user to manually create question files analogous to the ones saved in the character/process_files/ and connectors/process_files/ directories. They will be saved in the analogous local (manual/process_files/) directory.

When the user invokes manual_question_writer.py, they can optionally specify a metadata file after the command line option --metadata. Otherwise this will be, by default, ../primary_metadata.csv.

The control flow in manual_question_writer.py is essentially a loop of this structure:

1. Do we already have a source_htid?
2. If not — if it's the initial empty string — ask the user for a source_htid.
3. If we do have a non-empty source_htid, do we have metadata for it? A reliable way to test this is to ask whether source_date is not blank. All the metadata fields other than source_date are allowed to be empty.
4. If not, elicit metadata, using a script described below.
5. If we do have an id with metadata, ask the user:
"Source htid is {source_htid}. New id or [a, h] or enter to confirm:"
(here "a" triggers htid "attribution" and "h" triggers "handcrafted", but note that not all strings beginning "h" are "h"!)
6. A new id (different from previous) triggers the metadata_elicitation script.
7. If source_htid is "attribution", "handcrafted", or "refusal", we should always query:
"Provide new metadata? (y or enter for no):"
If yes, run metadata_elicitation script

Once ID and metadata are confirmed, the script can dialogue with the user to get all the fields needed for a "question." When the question is complete it writes a .json object with question fields, metadata fields, and one automatic field as a new line to {source_htid}_manualquestions.jsonl, creating that file if it does not yet exist.

Then return to the top of the loop.

You should probably create a separate script for the metadata-elicitation dialogue, because it can be reused more easily elsewhere if packaged as a separate file. Call it metadata_elicitation.py. Loosely model the dialogue on the one in connectors/make_cloze_questions.py. Here are examples of the variables that this script needs to confirm and returned:

{"source_title": "Some American Medical Botanists", 
"source_author": "Howard A. Kelly", 
"source_date": 1911, 
"author_nationality": "American", 
"source_genre": "work of biography", 
"author_birth": 1858, 
"author_profession": "naturalist and physician", 
"source_htid": "hvd.32044106370034"}

Write metadata_elicitation.py so that a metadata file path and source_htid can be passed from outside or left blank. In other workflows the source_htid will often be specified from outside, but manual_question_writer.py will pass metadata_elicitation.py an empty string. In that case, the process begins by asking the user for a source_htid. If the source_htid can be matched to a barcode_src in the metadata file, then default values for title, author, source_date, author_birth, and author_nationality can be inferred from the metadata, using processes modeled in make_cloze_questions.py. Note the normalizations to title and author applied there.

One additional normalization should be written that doesn't yet exist in the model from connections/. For author_nationality, "US" should automatically normalize to "American" and "UK" should normalize to "British."

Also note that there is currently no author_profession column in primary_metadata.csv, but you should expect one to be created in the future. Check if that column exists and, if it does, draw a default value for author_profession from it.

All variables need to be confirmed by the user. Hitting return confirms them.

It is acceptable to have blank values for all variables except for "source_htid" and "source_date".

In some cases the source_htid will not match a barcode_src. This is because our manual process will sometimes be used to create questions that don't align to a book in metadata. In particular, users may specify source_htid as "attribution", "handcrafted", or "refusal". These special values of source_htid will create questions that always get written to attribution_manualquestions.jsonl, handcrafted_manualquestions.jsonl, or refusal_manualquestions.jsonl. However, the metadata for questions may differ from one line of those files to the next (unlike files that have a barcode in the name). For this reason we'll always give the user an option to specify a new source_htid between each question in a dialogue. If one is specified, even if it matches the existing source_htid, we call metadata_elicitation.py again. But if the user hits enter, we keep the existing source_htid and the existing metadata.

Once metadata have been established, we can form questions. The fields that need to be elicited from the user include:

{"metadata_frame": "",
"main_question": "",
"answer_strings": [],
"answer_types": [],
"answer_probabilities": [],
"question_category": "",
"question_process": "manual"} # question_process is always manual in this script

We should form a default metadata frame using the template in connectors/make_cloze_questions.py. Ask the user
"(a)pprove this frame, (b)lank frame, or (m)anually supply frame:"
If m, query for a new frame.

The main question can never be blank and the user must supply a new one each time.

Question_category can never be blank. If source_htid is "attribution", "handcrafted", or "refusal", you can skip the dialogue, because question type will definitionally be the same as htid.

If source_htid is anything else, you should print the existing question_category, which becomes the default, and prompt:

"(a)pprove this category or (c)hange it? (enter for approve):"

Valid question categories are only

"attribution",
"handcrafted",
"refusal", and
"textbook"

so, if change is desired, it is possible to ask a menu question instead of requiring the user to type those out. Typically when source_htid is a barcode, most question_category will be "textbook", but this is not guaranteed.

The ultimate values of answer_strings, answer_types, and answer_probabilities will be lists. But we should not query the user for the whole lists at once! Instead, ask the user for answers one by one, and in each case append the string, type, and probability to the growing list.

There must be at least two answers for each question. After the second answer, you should begin to ask the user
"Add another answer? (n or enter for yes):"
(note the reversal of normal protocol there — we don't want accidental truncation of the answer sequence)

For each answer you need a string, answer_type, and probability. But there are rules that can help you abbreviate user interaction for the types and probabilities.

The string must be supplied by the user each time, alas. There is no default. If the user supplies a blank string, query again. If they respond only "n", infer that they decided not to continue and respond as if "add another answer" had received "n".

Answer type permits some abbreviation, because the only valid answer_types are
"ground_truth",
"manual", and
"anachronistic_manual".
And the type of the first answer will always be "ground_truth". There can be more than one ground_truth answer, however, so (g) should be included in the menu for subsequent answers.

Answer_probability is always 1.0 for "ground_truth" answers. Otherwise it should default to 0.0, but allow user to override by entering a float. (Enter accepts the default of zero.)

Once the user replies "n" and stops providing new answers, write the question to file, including all metadata fields and all manual fields. In questions.jsonl files elsewhere you may see a "passage" field, but there will be no "passage" field for manually entered questions.
Plan for make_cloze_questions.py
================================

The following markdown file contains specifications for a script to be called make_cloze_questions.py, which will transform a set of text files into cloze questions categorized for a benchmark.

The overall plan is:

0. Pair each text file with a metadata file, calling an external metadata-elicitation script if the metadata file doesn't yet exist. Convert the metadata into a prose "metadata prefix" that will be used for all questions, describing the book and author. I think you can find outlines for an external metadata-elicitation script in character/batch_questions.py.
1. Break the text file into sentences.
2a. Loop through sentences, using a set of verbal rules (in connector_list.md) to identify full sentences, or sentence-ending clauses, that begin with connectors in certain logical categories (cause/reason, effect/inference, contrast, concessive, conditional). Save these tags in a list of dictionaries that is the same length as the list of sentences. Format is {'categoryname': (connector, startwordposition)}. E.g., a sentence that was flagged as a contrast sentence with a conditional clause would be represented as {'contrastsentence': ('but', 0), 'conditionalclause': ('if', 21)}.
2b. Here is a full list of tags, with corresponding prose descriptions
causalsentence  [masked sentence describing a cause or reason]
causalclause  [masked clause describing a cause or reason]
effectsentence [masked sentence describing an inference or effect]
effectclause [masked sentence describing an inference or effect]
contrastsentence [masked sentence describing a tension or contrast]
contrastclause [masked clause describing a tension or contrast]
conditionalclause [masked clause describing a condition]
concessiveclause [masked clause conceding a limit or exception]
3a. Loop through the sentences and use a language model to double-check certain ambiguous cases. For instance, clauses beginning "since" could express a reason or could be temporal dependency. We need to ask mistral-small to read the sentence and resolve the ambiguity. Erase the "causalclause" tag from the appropriate tag-dictionary if it's inapplicable. Do the same thing for clauses beginning "as" and "then," which have similar indeterminacy between causal and temporal dependence, and "while," which is ambiguous between temporal and concessive. Also check all causal/reason sentences, appended to the previous sentence, to confirm a relation of causation or explanation is actually being expressed.
3b. Write results to disk, so we can resume here if needed, in this format: a sequential list of dictionaries where each dictionary has a key for "sentence" containing the text of the sentence, as well as the confirmed connection tags.
4. Create a master dictionary containing lists of sentence indices in each logical category. If we have > 3 sentences, or >3 clauses, in a category it's possible to form questions in that category.
5. Loop through the categories: causal sentences, causal clauses, inference sentences, etc. For each category where we have enough examples to form questions, randomly select examples, form questions, and query the user until we exhaust possibilities or get one user-accepted example in that category.
6. When an example has been randomly selected, retrieve the sentences preceding it, moving backwards until you have at least 40 words of preceding sentences (it's okay to go over). 60% of the time also retrieve a sentence following it. Reject sentences very near the start or end of the text where it is impossible to fulfill these conditions.
7. Present the passage and ground truth answer to the user like this:

metadata prefix: "The following passage comes from The Mystic Gate, a religious treatise published in 1901 by Annie Besant, a British theosophist."

passage: "The Self is one, however varying may be the forms of his manifestation, when working through and by means of the different kinds of matter. It is, of course, true that there is but One Self in the fullest sense of the words ; that as rays flame forth from the stm, the Selves that are the true Men are but rays of the Supreme Self, and that each Self may whisper : "I am He." [masked sentence describing a tension or contrast] Consciousness is a unit, and the divisions we make in it are either made for purposes of study, or are illusions, due to the limitation of our perceptive power by the organs through which it works in the lower worlds."

prompt: "Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:"

ground truth answer: "But for our present purpose, taking a single ray, we may assert also in its separation its own inherent unity, even though this be hidden by its forms."

Note that when the selected answer is a clause rather than a sentence, we need to use the startwordposition saved with the tag in order to create the ground truth answer and mask the right part of the sentence. Also, the prompt text should be edited in that case to say "clause" rather than "sentence."

Ask the user to confirm that this passage and answer provide a foundation for a good question.
8. If the user accepts the passage, generate distractors. This part of the workflow probably needs be broken out as a separate script; it might be reused by other processes. So I have described it separately. You will pass that script a list of "distractor_candidates" which is basically all the sentences or clauses in the current connector-class, other than the ground truth answer. You also need to pass the metadata prefix, passage, prompt, and ground truth answer. The script will return a list of answers (including the ground truth and all distractors), as well as a list of answer-probabilities and answer-categories. Finally, the distractor-generator needs a list of distractor-types that tells it what to generate. For this task, the list is [negation, same_book, same_book, anchronistic_mistral-small:24b, anachronistic_gpt-oss:20b].
9. Present the selected distractors to the user, collectively, and ask for confirmation on each one. Allow the user to write a manual distractor if desired.
10. If any distractors are approved, save this question to a file named "process_files/{BookBarcode}-clozequestions.jsonl". A question takes the form of a json line, with the metadata prefix, "question": passage + prompt, a list of answers including the ground truth answer and all distractors, a list of answer probabilities (1.0 for ground truth, 0 for distractors), and a list of answer categories. The tags from the metadata file should also be included; you can consult existing questions files under character/process_files/ to get a sense of the format. Finally, each question object has "question_process": "automatic" and "question_category," for instance, "cloze_effectclause" if the connector category for this question was "effectclause."

Script for distractor generation
--------------------------------

This script (distractor_generator.py) accepts a metadata prefix, passage, prompt, and ground truth answer, as well as a list of distractor candidates, and a "mask string" that tells it which string in the passage needs to be replaced, e.g. "[masked contrastive sentence]". It also accepts an answer_type flag that tells it whether the ground truth answer is a sentence or just a clause.

Finally, the script accepts a list of distractor types that instructs it how many distractors to create, of which kinds. The currently existing kinds are negation, same_book, and anachronistic, which is subdivided into anchronistic_mistral-small:24b, anachronistic_gpt-oss:20b, and anachronistic_qwen2.5:7b-instruct.

For instance, in serving the present task, this script will normally receive the list: [negation, same_book, same_book, anachronistic_mistral-small:24b, anachronistic_gpt-oss:20b]. Either "anachronistic_mistral-small:24b" or "anachronistic_gpt-oss:20b" will be replaced by a metadataless variant: "anachronistic_metadataless_mistral-small:24b" or "anachronistic_metadataless_gpt-oss:20b". There will always be one and only one metadataless variant but it could be either model.

Let's now outline the process used to create each of these distractors.

1. negation: pass the language model the ground truth answer with a prompt that tells it to transform it by negation.

NEGATION_SENTENCE_PROMPT =
"""
You are transforming sentences by reversing one aspect of their meaning. In doing this you try to change as little as possible, but also strive to produce idiomatic prose. This means that you will not simply add 'not' if it's possible to reverse the meaning more elegantly and idiomatically by substituting different words. For instance:

original sentence: As a result, the judge condemned him and sentenced him to die that day.

negation: As a result, the judge exonerated him and released him that day.

original sentence: But for our present purpose, we may assert also the inherent unity of each self, even though this be hidden by its forms.

negation: But for our present purpose, we may assert that also that the inherent unity of each self is hidden by its forms.

original sentence: {ground_truth_answer}
negation:
"""

NEGATION_CLAUSE_PROMPT =
"""
You are transforming clauses by reversing one aspect of their meaning. In doing this you try to change as little as possible, but also strive to produce idiomatic prose. This means that you will not simply add 'not' if it's possible to reverse the meaning more elegantly and idiomatically by substituting different words. For instance:

original clause: because its sides are so steep that a stone will slide down.

negation: because its sides slope so gently that stones never slide.

original clause: provided that the funds are sufficient to cover costs.

negation: provided that the funds fail to cover costs.

original clause: {ground_truth_answer}
negation:
"""

return the negation.

2. same_book: This category of distractor is created by selecting candidates from the list of distractor candidates and filtering them with BERT to produce the best fits for the blank in the original passage. The function accepts a list of distractor candidates, a passage, a mask string, a clause-or-sentence flag, and a ground truth answer. It also accepts an integer n that tells it how many distractors to return.

In other words, for each distractor candidate, we

a) substitute it for the "mask string" in the passage
b) divide sentences to get the sentence immediately preceding the sentence that had replacement, the sentence that had replacement, and the sentence following it (if one exists)
c) Use BERT next-sentence probability to measure the probabilities previous-sentence -> sentence-with-replacement and (if applicable) sentence-with-replacement -> next-sentence. If there are two probabilities, multiply them (being thoughtful to avoid numeric overflow for super-small quantities).
d) keep track of the probability for each candidate distractor as you go
e) return the n top candidates

3. anachronistic: This category of distractor is produced by passing a language model the question and asking it to generate a response. The function receives a distractor description, e.g, "anachronistic_metadataless_gpt-oss:20b", as well as the metadata prefix, passage, prompt, and ground truth answer.

Our first task is to parse the description to figure out whether this distractor is "metadataless." If not, we construct the question text by concatenating metadata prefix + passage + prompt. If it's metadataless, obviously, we omit the metadata prefix.

In parsing the description we will also have extracted the model descriptor at the end. Using that descriptor to select a model, we pass the question text and receive a response.

We do some quick checks on length. The response should not be less than 0.5 * the length of the ground truth answer and not greater than 2 * that length. If it fails the check, repeat the prompt while adding a word length specification like "(about 42 words)"" between the penultimate character and the ending colon.

If an appropriate-length response is received, return it. Or return None in case of failure. This needs to be caught at the top level.

4. top-level return

Once distractor_generator.py has created distractors, or Nones, to match all the distractors in the list of distractor types originally requested, the top-level script will return

answer_strings, answer_types, and answer_probabilities

These lists always start with the ground_truth answer, which has type ground_truth. Then the lists are generated to match the provided distractors, skipping Nones. The answer_types are provided by the original list of requests, e.g. "same_book"" or "negation,"" or "anachronistic_mistral-small:24b."" The probabilities are 1.0 for the ground truth and 0 for all the distractors.

Basic unit tests for this workflow
----------------------------------

Here I outline some things that could go wrong. We need some way of testing for these edge cases and failures. Consider writing unit tests for them.

0. Are metadata_prefixes being created appropriately? Create some samples, using existing metadata files in character/process_files, and ask user to inspect.
1. What happens if a very short text file is passed to make_cloze_questions.py and it can't find enough candidates in any connector category.
2a. Test that parsing for connector types is generating plausible output. Some of this can be tested automatically. For instance, generate a sample file with one example of each connector in connector_list.md, and pass it through to check that they are all caught and rules are followed appropriately — e.g. sentences get caught when a connector is in the first five words, whether it is capitalized or not, etc.
2b. Then test using real-world data, a text file from IDI_sample_1875-25/. Run it through and generate marked-up sentences until you have caught ~25 cases that fall into connector categories, and then let the human user read the file output to confirm that appropriate things are being caught and there aren't too many false positives.
3. Are ambiguous cases, e.g. of "since" and "as" being filtered appropriately? Construct a synthetic text to test this. Are cause/reasoning sentences being filtered appropriately. Construct synthetic examples to test this.
4. Are passages constructed appropriately? An automatic test can be written for this.
5. Are we always requesting one and only one metadataless anachronistic distractor?
6. In distractor generation, are negations appropriate? Generate a sample and allow user inspection.
7. In same_book distractor generation, is BERT-ranking of distractor candidates appropriately selecting the best candidates. This function should have an option to generate test output where it prints all candidates, in probability order, to file -- so we can see that the rejected candidates were really inferior.
8. In anachronistic distractor generation, is the "metadataless" flag actually changing the prompt submitted? (This can be tested automatically.) Do the parameters passed to models permit successful response, or are we getting a lot of model errors due to timeouts or answer overflows? Consider that gpt-oss is a thinking model and may be more verbose.
9. When we're requesting clauses, do the distractors look like clauses (no initial capital)? When we're requesting sentences, do they look like sentences?
10. Is the length check working for anachronistic distractors? If there's an initial failure, are length specifications being constructed appropriately?
11. When question output is written to file, do the tags align with tags illustrated in character/process_files/*.questions.jsonl? What tags are present in one set of question files but not the other?

Thanks!
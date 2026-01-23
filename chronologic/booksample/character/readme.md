character modeling
==================

The scripts in this directory will be used to develop questions that test whether a language model can model character in ways appropriate for period fiction, and understand the relation between genre, character, and dialogue.

The overall logic here is that we are going to ask questions where the 'right answer' would be an actual passage of dialogue taken from a novel, and the 'wrong answers' are lines that are inappropriate either because they don't fit the narrative context, or because they don't fit the character, or because they are written in an anachronistic, pastiche-y style. Or all three!

The model should assign highest probability to the right answer. The clues helping it do that are

1. A "metadata prefix," which tells it about the genre and the author.
2. Descriptions of the character speaking, extracted from across the whole span of the book.
3. Usually, a short description of the dramatic situation when the dialogue takes place.

So, while the right answer is an actual passage of dialogue extracted from the novel, this is *not a cloze-style question* that could be answered just using a base model's ability to extrapolate. There is no immediately surrounding context to extrapolate *from*! Instead, the question tests the model's ability to connect generalizations about genre, period, and character to the type of dialogue associated with those abstract concepts. It incidentally also tests ability to follow instructions.

I recommend checking out the CharacterPipelineGuide.md, which gives you an overview of the code structure here, and also contains instructions for running new batches of books through the pipeline. Short version: it's a three-stage process:

1. Organize your books as .txt files in a folder, and create a file called fiction_to_process.txt that points at their barcodes (the first part of the filename).
2. Run batch_extract.py, which can run unattended and will extract character descriptions and dialogue passages from the books.
3. Run batch_questions.py, which pairs descriptions with dialogue and forms questions. This requires user interaction.

Examples of the intermediate-stage files (dialogue and description) as well as the final "questions" file, are available in the subdirectory process_files.
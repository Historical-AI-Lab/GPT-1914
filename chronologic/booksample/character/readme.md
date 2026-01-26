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

Examples of the intermediate-stage files (dialogue and character descriptions) as well as the final "questions" file, are available in the subdirectory process_files. But here's a quick example:

{"metadata_frame": "This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, an Irish writer born in 1865." 

"main_question": "The character in question here is John Butler, who is described this way in the book:

"He was a big man, with a square, ruddy face; the mouth large and mobile, the chin weak and flabby. His eyes were bright and kindly, his nose large, his head crowned with a shock of brown hair", "Old John was asleep, chin on breast and his lips dribbling.", "Big John, hands in pockets, shoulders slouched, hat on the back of his head; goes shambling along, without care or purpose, just lounging about in the sunshine", "His face shone red as a coal. His eyes flared.", "John's face was solemn; one hand gripped his pipe stem, the other swung limply to and fro.", "Ould John, still clutching his pipe, had fallen asleep.", "John was a big, soft-handed, blethering Irishman, one who wanted work yet loathed it, spoke one thing and meant the other, said he was this and looked that."

"At one moment in the book, John passionately debates Ireland with Frank, Nan, and Ted while they listen. Write a short passage of dialogue (1-3 sentences) that John Butler might speak in this situation:", 

ground-truth answer: "Who would save Ireland, sir? Would England, sir? Would politicians, sir?" 

same-character distractor: "You'd be thinkin a power, Frank, o' the poetry o' Pope, I'm thinkin?"

same-book distractor: "Well, I'm for there too, if you don't mind taking me."

anachronistic-gpt-oss:20b distractor: "Listen, ye lads, Ireland's not a dream but a fight, a breath that must be kept in our throats! We must stand up, and make them hear the roar of the green! If we don't, the next generation will be born with no tongue to speak of the Emerald."

"source_title": "The Barrys", "source_author": "Shan F. Bullock", "source_date": 1899, "author_nationality": "Irish", "source_genre": "novel", "author_birth": 1865, "source_htid": "hvd.hnnwy1", "question_category": "character_modeling_with_summary", "question_process": "automatic"}
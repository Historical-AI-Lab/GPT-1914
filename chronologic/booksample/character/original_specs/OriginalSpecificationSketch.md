First script: description extraction
------------------------------------

Our strategy is to first iterate through a novel, dividing the text at sentences and chunking up to ~ 700 words, broken at sentence breaks. We will send each chunk to gpt-oss:20b. From each chunk, we will extract any moments when characters are explicitly described. We'll ask the model to return character names + descriptions in JSON format, aggregate the descriptions by character, and save them in a jsonl with one line per character.

Here is the proposed prompt
DESCRIPTION_EXTRACTING_PROMPT = """
You are filtering text from a novel to find moments when named characters are explicitly described. 

If you find a good example of explicit description, return only the character and extracted description, in json format like this:
{{"character_name": "Elsie Mitchell", "description": "Elsie was a silent child and possessed a calm and happy nature. Her eyes were very strange and in no way suggested blindness."}}

If there is no good example of explicit description, return an empty json object like this:
{{}}

Be choosy. Most passages of fiction don't contain explicit character description. For instance,

passage:
"The wedding took place at the next Nachtmaal, Gideon managing, by means of some pretext, to avoid being present. The priest who officiated was a corpulent conservative man. Soon afterwards old Tyardt cut off a portion of the farm and handed it over to his married son, who thereupon built a homestead and began farming on his own account."
reply:
{}

The passage implies things about Gideon and Tyardt but does not explicitly describe them. The priest is described explicitly, but he is not a named character. So nothing is returned.

passage:{passage}
reply:
"""


We will group the replies and write them out to a .jsonl file. For instance, after processing file 32044082646845.txt
we'll be able to write 32044082646845_characters.jsonl

where one line might be
{"character_names": ["Elsie Mitchell", "Elsie"],
"descriptions": [(3, "Elsie took after her mother; she was of fair complexion, with long locks of dead-gold hair which took a wonderful depth of colour in certain halflights."),
(12, "Elsie was a silent child and possessed a calm and happy nature. Her eyes were very strange and in no way suggested blindness.")]
}

The descriptions are stored as chunk_number, description tuples. Characters are grouped on the principle "if any charname in x contained in any charname in y, merge both lists." We work through candidates in increasing order of length.

Second script: dialogue extraction
----------------------------------

Once we have this character list we can make a second pass through the novel. This time we will pass the model the same sort of chunks -- broken at sentence boundaries, up to 700 words -- along with a list of character names and the following instruction

DIALOGUE_EXTRACTION_PROMPT = """
You are identifying fictional passages that contain substantial dialogue from one of a group of characters. If dialogue from one of those characters is found, you extract it, and return json with three parts: the character name, the dialogue extracted, and a one-sentence summary of the scene.

For instance,
character_list: [["Elsie", "Miss Elsie"], ["Stephanus"]]
passage: "When Stephanus returned home after the encounter with Gideon he found the blind child waiting for him under a large mulberry tree. This was her accustomed trysting-place; here Elsie would sit for hours when her father was away, waiting, with the pathetic patience of the blind, for his return.

She advanced to meet him, guided by the sound of his footsteps, and took his hand. 'Father, why are you so late tonight?' Elsie asked, 'And where 66 BLIND ELSIE is your horse?' 'Late,' he repeated, musingly- 'yes, it is late, but not too late.'

The child's intuitive sense prevented her from questioning further."

reply:
{{"character": "Elsie", "dialogue": "Father, why are you so late tonight? And where is your horse?", summary: "Stephanus returns home and finds Elsie, who asks why he is late."}}

Note that interruptions in the dialogue (speech tags and running page headers) have been silently removed. Note also that Elsie's dialogue was chosen and Stephanus was ignored: if multiple named characters are present, choose dialogue from one. Don't try to do all the characters.

If there is no dialogue, or there is dialogue but not from any of the character names mentioned, -- or if the dialogue is just a brief remark (five words or less), return an empty json object:
{{}}

character_list: {characters}
passage: {passage}
reply:
"""

After proceeding through the whole novel, we will write another jsonl file, with dialogue passages organized by character. Each line will contain all passages related to a single character, with format:
{"character_names": [], "character_dialogue": [{"chunk": 8,"character": "Elsie", "dialogue": "Father, why are you so late tonight? And where is your horse?", summary: "Stephanus returns home and finds Elsie, who asks why he is late."}, {another chunk, character, dialogue, and summary}]
}
# metadata_updater.py

# Constructs a new primary_metadata.csv file by, first, extracting
# barcodes from metadata_history.csv, then enriching with data from
# json_metadata/, and finally checking to see how many questions
# have been written for each book in the process_files/ subdirectories.

import pandas as pd
import os
import json
from collections import Counter

history = pd.read_csv('metadata_history.csv', encoding='latin-1')

# limit to rows where 'include_yn' is 'y'
history = history[history['include_yn'] == 'y']

# limit to columns 'barcode_src', 'title_src', 'author_src', 'firstpub', 'reason',
# 'pubplace', 'authgender', 'authnationality', 'authordates', 'pagecount', 'tokencount'
history = history[['barcode_src', 'title_src', 'author_src', 'firstpub', 'reason',
                   'pubplace', 'authgender', 'authnationality', 'authordates', 'author_profession',
                   'page_count_src', 'token_count_o200k_base_gen']]

# function to get metadata from json file
def get_json_metadata(htid):
    barcode = htid.replace('hvd.', '')
    json_path = os.path.join('json_metadata', f"{barcode}_metadata.json")
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='latin-1') as f:
            data = json.load(f)
            returndict = dict()

            if 'author_profession' in data:
                returndict['author_profession'] = data['author_profession']
            else:
                returndict['author_profession'] = None
            if 'genre' in data:
                returndict['genre'] = data['genre']
            else:
                returndict['genre'] = ''

            return returndict
    else:
        return {'author_profession': None, 'genre': ''}

# iterate through history and enrich with json metadata
# (json_metadata/ takes priority when present; otherwise fall back
# to the author_profession already recorded in metadata_history.csv)
author_professions = []
genres = []
for idx, row in history.iterrows():
    htid = row['barcode_src']
    json_metadata = get_json_metadata(htid)
    if json_metadata['author_profession']:
        author_professions.append(json_metadata['author_profession'])
    else:
        author_professions.append(row['author_profession'])
    genres.append(json_metadata['genre'])
history['author_profession'] = author_professions
history['genre'] = genres

directories_to_count = ['character', 'connectors', 'manual', 'poetry', 'summary']

# we iterate through each of those directories, list files in
# its process_files/ subdirectory, and then iterate through
# those files to count how many questions exist for each barcode.
# A file is a questions file if it ends with '_questions.jsonl',
# and the barcode those should be attributed to is 'hvd.' plus the part before
# the first underscore.
#
# In addition, we walk chronologic_en_0.7.jsonl -- the approved benchmark --
# and add its counts to the same totals. This is a literal sum: a question
# that started life in process_files/ and was later approved into the
# benchmark gets counted in both places. That double-counting is intentional
# (the totals track combined pipeline + benchmark volume), not a bug.
#
# Results are stored in a dictionary mapping barcodes to dicts,
# within which keys are reasoning_type values and values are counts.
def normalize_barcode(barcode: str) -> str:
    """Lowercase and strip hvd. prefix for consistent matching."""
    b = barcode.lower()
    if b.startswith("hvd."):
        b = b[4:]
    return b

REASONING_TYPES = {
    'knowledge', 'constrained_generation', 'inference', 'topic_sentence',
    'character_modeling', 'sentence_cloze', 'phrase_cloze', 'abstention',
}

# Fallback for manual/ question_categories that aren't already a reasoning_type
# and aren't covered by a directory-level rule below. Values are the empirical
# majority reasoning_type for that category in chronologic_en_0.6.jsonl.
CATEGORY_FALLBACK = {
    'parallax': 'constrained_generation',
    'handcrafted': 'constrained_generation',
    'textbook': 'inference',
    'refusal': 'abstention',
    'attribution': 'knowledge',
    'poetic_form': 'inference',
    'contrastclause': 'phrase_cloze',  # legacy typo category, predates cloze_ prefix
}

DIRECTORY_REASONING_TYPE = {
    'connectors': 'sentence_cloze',  # clause-level cloze categories are retired
    'poetry': 'constrained_generation',
    'summary': 'topic_sentence',
    'character': 'character_modeling',
}

def infer_reasoning_type(directory: str, question_category: str) -> str:
    """Infer a reasoning_type for a process_files record that lacks one."""
    if question_category in REASONING_TYPES:
        return question_category
    if directory in DIRECTORY_REASONING_TYPE:
        return DIRECTORY_REASONING_TYPE[directory]
    return CATEGORY_FALLBACK.get(question_category, 'unknown')

DECADE_START = 1831
DECADE_END = 1930

def decade_of(year) -> str:
    """Bucket a year into a decade label like '1831-1840', or a catch-all."""
    try:
        year = int(year)
    except (TypeError, ValueError):
        return 'outside_1831_1930'
    if DECADE_START <= year <= DECADE_END:
        start = DECADE_START + ((year - DECADE_START) // 10) * 10
        return f"{start}-{start + 9}"
    return 'outside_1831_1930'

question_counts = dict()
category_counter = Counter()
answer_type_counter = Counter()
decade_counter = Counter()
aggregation_file = open('all_benchmark_questions.jsonl', 'w')

def tally_record(record, barcode, reasoning_type):
    if barcode not in question_counts:
        question_counts[barcode] = dict()
    question_counts[barcode][reasoning_type] = question_counts[barcode].get(reasoning_type, 0) + 1
    if 'question_category' in record:
        category_counter[record['question_category']] += 1
    if 'answer_types' in record:
        for answer_type in record['answer_types']:
            answer_type_counter[answer_type] += 1
    if 'source_date' in record:
        decade_counter[decade_of(record['source_date'])] += 1

for directory in directories_to_count:
    process_files_path = os.path.join(directory, 'process_files')
    if os.path.exists(process_files_path):
        for filename in os.listdir(process_files_path):
            if filename.endswith('questions.jsonl') and not filename.endswith('potentialquestions.jsonl'):
                file_path = os.path.join(process_files_path, filename)
                with open(file_path, 'r', encoding='latin-1') as f:
                    lines = f.readlines()

                # Derive barcode from source_htid inside the file (ground truth),
                # falling back to the old filename-based approach if needed.
                barcode = None
                for line in lines:
                    stripped = line.strip()
                    if stripped:
                        try:
                            record = json.loads(stripped)
                            if 'source_htid' in record:
                                barcode = record['source_htid'].lower()
                                break
                        except json.JSONDecodeError:
                            pass
                if barcode is None:
                    barcode_part = filename.split('_')[0].lower()
                    barcode = f"hvd.{barcode_part}"

                barcode = normalize_barcode(barcode)
                for line in lines:
                    line = line.rstrip('\n')
                    if line:
                        aggregation_file.write(line + '\n')
                        try:
                            record = json.loads(line)
                            reasoning_type = infer_reasoning_type(
                                directory, record.get('question_category', '')
                            )
                            tally_record(record, barcode, reasoning_type)
                        except json.JSONDecodeError:
                            pass

# Second data source: the approved benchmark, which already carries reasoning_type.
with open('chronologic_en_0.7.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        if not line:
            continue
        aggregation_file.write(line + '\n')
        record = json.loads(line)
        barcode = normalize_barcode(record.get('source_htid', ''))
        reasoning_type = record.get('reasoning_type', 'unknown')
        tally_record(record, barcode, reasoning_type)

aggregation_file.close()

with open('question_category_census.txt', 'w', encoding='utf-8') as f:
    for value, count in category_counter.most_common():
        f.write(f"{value}\t{count}\n")

with open('answer_type_census.txt', 'w', encoding='utf-8') as f:
    for value, count in answer_type_counter.most_common():
        f.write(f"{value}\t{count}\n")

with open('decade_census.txt', 'w', encoding='utf-8') as f:
    for value, count in decade_counter.most_common():
        f.write(f"{value}\t{count}\n")
    f.write(f"total\t{sum(decade_counter.values())}\n")

# Now we add one column per reasoning_type for each barcode's question counts
reasoning_type_columns = sorted(REASONING_TYPES) + ['unknown']
added_columns = []
for reasoning_type in reasoning_type_columns:
    counts = []
    for idx, row in history.iterrows():
        barcode = normalize_barcode(row['barcode_src'])
        if barcode in question_counts and reasoning_type in question_counts[barcode]:
            counts.append(question_counts[barcode][reasoning_type])
        else:
            counts.append(0)
    history[f'{reasoning_type}_question_count'] = counts
    added_columns.append(f'{reasoning_type}_question_count')

# Add a column that totals the question counts in 
# columns we just added
history['total_question_count'] = history[added_columns].sum(axis=1)

# finally, write out the new primary_metadata.csv
history.to_csv('primary_metadata.csv', index=False)


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

directories_to_count = ['character', 'connectors', 'knowledge', 'manual', 'batchconnectors', 'summary', 'poetry']

# we iterate through each of those directories, list files in
# its process_files/ subdirectory, and then iterate through
# those files to count how many questions exist for each barcode
# (which is simply the line count of each file)
# A file is a questions file if it ends with '_questions.jsonl',
# and the barcode those should be attributed to is 'hvd.' plus the part before
# the first underscore.

# Results are stored in a dictionary mapping barcodes to dicts,
# within which keys are directory names and values are counts.
def normalize_barcode(barcode: str) -> str:
    """Lowercase and strip hvd. prefix for consistent matching."""
    b = barcode.lower()
    if b.startswith("hvd."):
        b = b[4:]
    return b

question_counts = dict()
category_counter = Counter()
answer_type_counter = Counter()
aggregation_file = open('all_benchmark_questions.jsonl', 'w')
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
                line_count = len(lines)
                if barcode not in question_counts:
                    question_counts[barcode] = dict()
                question_counts[barcode][directory] = line_count
                for line in lines:
                    line = line.rstrip('\n')
                    if line:
                        aggregation_file.write(line + '\n')
                        try:
                            record = json.loads(line)
                            if 'question_category' in record:
                                category_counter[record['question_category']] += 1
                            if 'answer_types' in record:
                                for answer_type in record['answer_types']:
                                    answer_type_counter[answer_type] += 1
                        except json.JSONDecodeError:
                            pass
aggregation_file.close()

with open('question_category_census.txt', 'w', encoding='utf-8') as f:
    for value, count in category_counter.most_common():
        f.write(f"{value}\t{count}\n")

with open('answer_type_census.txt', 'w', encoding='utf-8') as f:
    for value, count in answer_type_counter.most_common():
        f.write(f"{value}\t{count}\n")

# Now we add columns to history for each directory's question counts
added_columns = []
for directory in directories_to_count:
    counts = []
    for idx, row in history.iterrows():
        barcode = normalize_barcode(row['barcode_src'])
        if barcode in question_counts and directory in question_counts[barcode]:
            counts.append(question_counts[barcode][directory])
        else:
            counts.append(0)
    history[f'{directory}_question_count'] = counts
    added_columns.append(f'{directory}_question_count')

# Add a column that totals the question counts in 
# columns we just added
history['total_question_count'] = history[added_columns].sum(axis=1)

# finally, write out the new primary_metadata.csv
history.to_csv('primary_metadata.csv', index=False)


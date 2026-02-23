# metadata_updater.py

# Constructs a new primary_metadata.csv file by, first, extracting
# barcodes from metadata_history.csv, then enriching with data from
# json_metadata/, and finally checking to see how many questions
# have been written for each book in the process_files/ subdirectories.

import pandas as pd
import os
import json

history = pd.read_csv('metadata_history.csv')

# limit to rows where 'include_yn' is 'y'
history = history[history['include_yn'] == 'y']

# limit to columns 'barcode_src', 'title_src', 'author_src', 'firstpub', 'reason',
# 'pubplace', 'authgender', 'authnationality', 'authordates', 'pagecount', 'tokencount'
history = history[['barcode_src', 'title_src', 'author_src', 'firstpub', 'reason',
                   'pubplace', 'authgender', 'authnationality', 'authordates', 'page_count_src', 'token_count_o200k_base_gen']]

# function to get metadata from json file
def get_json_metadata(htid):
    barcode = htid.replace('hvd.', '')
    json_path = os.path.join('json_metadata', f"{barcode}_metadata.json")
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)
            returndict = dict()
            
            if 'author_profession' in data:
                returndict['author_profession'] = data['author_profession']
            else:
                returndict['author_profession'] = ''
            if 'genre' in data:
                returndict['genre'] = data['genre']
            else:
                returndict['genre'] = ''
            
            return returndict
    else:
        return {'author_profession': '', 'genre': ''}

# iterate through history and enrich with json metadata
author_professions = []
genres = []
for idx, row in history.iterrows():
    htid = row['barcode_src']
    json_metadata = get_json_metadata(htid)
    author_professions.append(json_metadata['author_profession'])
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
question_counts = dict()
aggregation_file = open('all_benchmark_questions.jsonl', 'w')
for directory in directories_to_count:
    process_files_path = os.path.join(directory, 'process_files')
    if os.path.exists(process_files_path):
        for filename in os.listdir(process_files_path):
            if filename.endswith('questions.jsonl') and not filename.endswith('potentialquestions.jsonl'):
                barcode_part = filename.split('_')[0]
                # lowercase the barcode part, since filenames are uppercased
                barcode_part = barcode_part.lower()
                barcode = f"hvd.{barcode_part}"
                file_path = os.path.join(process_files_path, filename)
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    line_count = len(lines)
                    if barcode not in question_counts:
                        question_counts[barcode] = dict()
                    question_counts[barcode][directory] = line_count
                    for line in lines:
                        line = line.rstrip('\n')
                        if line:
                            aggregation_file.write(line + '\n')
aggregation_file.close()

# Now we add columns to history for each directory's question counts
added_columns = []
for directory in directories_to_count:
    counts = []
    for idx, row in history.iterrows():
        barcode = row['barcode_src']
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


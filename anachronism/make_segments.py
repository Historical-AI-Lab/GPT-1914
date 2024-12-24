# make_segments.py
# reads text files, divides them into sentences, and
# selects roughly 200-word segments that start and end
# with complete sentences. The segments are saved to
# a dataframe, along with information about the source.

import pandas as pd
import os
import nltk # For sentence tokenization
from nltk.tokenize import sent_tokenize
import SonicScrewdriver as utils

input_dir = 'edwardian'
# print working directory
print(os.getcwd())
# change working directory to GPT-1914/anachronism
os.chdir('GPT-1914/anachronism')
 
input_files = [x for x in os.listdir(input_dir) if x.endswith('.txt')]

metadata = pd.read_csv('HeldOutRecords1905-14_nodupes.tsv', sep='\t')

def make_segments(afile):
    with open(afile, 'r') as f:
        text = f.read()
    
    text = text.replace('\n', ' ').replace('\r', ' ') # Remove newlines and carriage returns
    text = text.replace('\t', ' ').replace('<pb>', ' ') # Remove tabs and page breaks
    text = text.replace('  ', ' ') # Remove double spaces

    # Tokenize the text into sentences
    sentences = sent_tokenize(text)

    sentence_lengths = [len(s.split()) for s in sentences]

    # We skip the first 1/8 of the text, which may be front matter.
    # Then we select segments of roughly 120 words that start and end with complete sentences,
    # and skip roughly 120 words before starting the next segment.

    skipnumber = 3  # Skip the first three sentences of the text
    segments = []
    start = skipnumber
    use_segment = True

    while start < len(sentences) - 10:
        segment = ''
        segment_length = 0
        end = start
        while end < len(sentences):
            if segment_length + sentence_lengths[end] > 165:
                break
            segment += sentences[end] + ' '
            segment_length += sentence_lengths[end]
            end += 1

        if use_segment:
            segments.append(segment)
            use_segment = False
        else:
            use_segment = True
            # we skip this segment, as a way of skipping another 200 words
            # but we still need to increment the start pointer
        
        start = end + 1

    return segments

# Create a dataframe to hold the segments
df = pd.DataFrame(columns=['source', 'date', 'segment'])

for afile in input_files:
    tooshort = 0
    segments = make_segments(os.path.join(input_dir, afile))
    dirty_id = utils.dirty_pairtree(afile.replace('.trim.txt', ''))
    for segment in segments:
        seglen = len(segment.split())
        if seglen < 100:
            tooshort += 1
            continue
        date = metadata[metadata['HTid'] == dirty_id]['inferred_date'].values[0]
        df = pd.concat([df, pd.DataFrame([{'source': dirty_id, 'date': date, 'segment': segment}])], ignore_index=True)
    print(f"{afile}: {len(segments)} segments, {tooshort} too short, {date} date") 

df.to_csv('edwardian_segments.tsv', index=False, sep='\t')
print(df.shape)
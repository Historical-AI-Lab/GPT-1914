# Sentence splitter
# Usage: python3 sentence_splitter.py <input_folder> <output_folder>

# This script iterates through all the files in the input_folder;
# in each case it splits the text into sentences, and then calculates
# the number of tokens in each sentence. Two different tokenizers are
# used: the Roberta-base tokenizer and the GPT-2 tokenizer.

# The output is a tsv file with the original filename
# in the output_folder, where each line corresponds to a sentence,
# and has the following columns:
# #tokensRoberta #tokensGPT2 sentence

import os
import sys, time
import nltk
import torch
import argparse
import pandas as pd
from transformers import RobertaTokenizer, GPT2Tokenizer

# import spacy

nltk.download('punkt_tab')

# # Load the spaCy model (make sure to install it first with: python -m spacy download en_core_web_sm)
# nlp = spacy.load('en_core_web_sm')
# nlp = spacy.load('en_core_web_sm')
# nlp.max_length = 2100000 # Increase the maximum text length

def tabless(text):
    # Remove tabs from text
    return text.replace('\t', ' ').replace('  ', ' ')

def split_sentences(text):
    # Split text into sentences
    text = text.replace('<pb>', ' ')
    sentences = nltk.sent_tokenize(text)
    # doc = nlp(text)
    # sentences = [sent.text for sent in doc.sents]

    # Sentences greater than 350 words are split into smaller chunks
    # of fewer than 350 words each

    transformed_sentences = []
    for sentence in sentences:
        words = sentence.split()
        if len(words) > 350:
            num_chunks = (len(words) + 349) // 350  # Calculate the number of chunks needed
            chunk_size = (len(words) + num_chunks - 1) // num_chunks  # Calculate the size of each chunk
            for i in range(0, len(words), chunk_size):
                transformed_sentences.append(' '.join(words[i:i + chunk_size]))
        else:
            transformed_sentences.append(sentence)
    sentences = transformed_sentences

    return [tabless(sentence) for sentence in sentences]

def count_tokens(sentences, tokenizer):
    # Use batch tokenization for faster performance
    batch_tokens = tokenizer(sentences, add_special_tokens=False)
    num_tokens = [len(ids) for ids in batch_tokens['input_ids']]
    return num_tokens

def split_text_at_whitespace(text, max_length=2000000):
    """
    Splits a long text into smaller chunks at whitespace boundaries if the text exceeds max_length.

    Args:
        text (str): The input text to be split.
        max_length (int): The maximum length for each chunk.

    Returns:
        List[str]: A list of text chunks.
    """
    if len(text) <= max_length:
        # If the text is already within the limit, return it as a single chunk
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        # Determine the endpoint for the current chunk
        end = start + max_length

        if end >= len(text):
            # If the end exceeds the text length, just add the final chunk
            chunks.append(text[start:])
            break

        # Find the nearest whitespace before the end
        end = text.rfind(" ", start, end)
        if end == -1:
            # If no whitespace is found, use the max_length as the endpoint
            end = start + max_length

        # Add the chunk to the list
        chunks.append(text[start:end])

        # Move the start to the end of the current chunk
        start = end + 1  # Skip the space at the start of the next chunk

    return chunks

def main(input_folder, output_folder, time_limit):
    # Load tokenizers
    roberta_tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
    gpt2_tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Initialize timers for benchmarking
    total_spacy_time = 0.0
    total_tokenization_time = 0.0
    
    # If a file exists named output_folder.processed_files.txt,
    # read it and skip the files that have already been processed.

    # record the start time
    start_time = time.time()
    discrepancy_count = 0

    processed_files = set()
    processed_file = os.path.join(output_folder, 'processed_files.txt')
    if os.path.exists(processed_file):
        with open(processed_file, 'r') as f:
            for line in f:
                processed_files.add(line.strip())

    # Iterate through all files in the input folder
    for filename in os.listdir(input_folder):
        if filename in processed_files:
            print(f'{filename} has already been processed. Skipping...')
            continue
        
        # Check if the time limit has been reached
        elapsed_time = time.time() - start_time
        if elapsed_time > time_limit * 3600:
            print(f'Time limit of {time_limit} hours reached. Exiting...')
            break
        
        if filename.endswith('.txt'):
            print(f'Processing {filename}', flush = True)
            with open(os.path.join(input_folder, filename), 'r') as f:
                text = f.read()
                if len(text) > 2000000:
                    chunks = split_text_at_whitespace(text, max_length=2000000)
                    dfs = []
                    for i, chunk in enumerate(chunks):
                        spacy_start_time = time.time()
                        sentences = split_sentences(chunk)
                        spacy_end_time = time.time()
                        total_spacy_time += spacy_end_time - spacy_start_time

                        tokenization_start_time = time.time()
                        num_tokens_roberta = count_tokens(sentences, roberta_tokenizer)
                        num_tokens_gpt2 = count_tokens(sentences, gpt2_tokenizer)
                        tokenization_end_time = time.time()
                        total_tokenization_time += tokenization_end_time - tokenization_start_time
                        df = pd.DataFrame({'#tokensRoberta': num_tokens_roberta,
                                           '#tokensGPT2': num_tokens_gpt2,
                                           'sentence': sentences})
                        dfs.append(df)
                    df = pd.concat(dfs)
                else:
                    spacy_start_time = time.time()
                    sentences = split_sentences(text)
                    spacy_end_time = time.time()
                    total_spacy_time += spacy_end_time - spacy_start_time

                    tokenization_start_time = time.time()
                    num_tokens_roberta = count_tokens(sentences, roberta_tokenizer)
                    num_tokens_gpt2 = count_tokens(sentences, gpt2_tokenizer)
                    tokenization_end_time = time.time()
                    total_tokenization_time += tokenization_end_time - tokenization_start_time
                    df = pd.DataFrame({'#tokensRoberta': num_tokens_roberta,
                                   '#tokensGPT2': num_tokens_gpt2,
                                   'sentence': sentences})
                
                # We iterate through the rows of df checking if the number of tokens
                # is greater than 510 in either of the tokenizers. If it is, we split
                # the sentence into smaller chunks of fewer than 400 tokens each.
                # We do this by splitting the sentence at word boundaries
                # Since words are not tokens, we calculate the number of words (proportional
                # to total words) needed to produce chunks of fewer than 400 tokens.

                if max(df['#tokensRoberta'].max(), df['#tokensGPT2'].max()) > 510:
                    listofrows = []
                    for index, row in df.iterrows():
                        if row['#tokensRoberta'] > 510 or row['#tokensGPT2'] > 510:
                            maxtokens = max(row['#tokensRoberta'], row['#tokensGPT2'])
                            words = row['sentence'].split()
                            num_chunks = (maxtokens + 399) // 400
                            chunk_size = (len(words) + num_chunks - 1) // num_chunks

                            sentencepieces = []
                            for i in range(0, len(words), chunk_size):
                                sentencepiece = ' '.join(words[i:i + chunk_size])
                                sentencepieces.append(sentencepiece)
                            
                            for sentencepiece in sentencepieces:
                                roberta_tokens = count_tokens([sentencepiece], roberta_tokenizer)[0]
                                gpt2_tokens = count_tokens([sentencepiece], gpt2_tokenizer)[0]
                                listofrows.append(pd.Series({'#tokensRoberta': roberta_tokens,
                                                    '#tokensGPT2': gpt2_tokens,
                                                    'sentence': sentencepiece}))  
                        else:
                            listofrows.append(row)
                
                    df = pd.DataFrame(listofrows)
                
                if max(df['#tokensRoberta'].max(), df['#tokensGPT2'].max()) > 510:
                    print(f'Error: Sentence still greater than 510 tokens in {filename}.')
                
                # If there are any discrepancies in the number of tokens between the two tokenizers,
                # we print a warning message. This is expected behavior, but we want to know
                # how often it occurs.

                if (df['#tokensRoberta'] != df['#tokensGPT2']).any():
                    print(f'Number of tokens differ between tokenizers in {filename}.')
                    discrepancy_count += 1

                df.to_csv(os.path.join(output_folder, filename.replace('.txt', '.tsv')), sep='\t', index=False)
                with open(processed_file, 'a') as f:
                    f.write(filename + '\n')

    print(f'Total time spent in nltk: {total_spacy_time:.2f} seconds')
    print(f'Total time spent in tokenization: {total_tokenization_time:.2f} seconds')
    print(f'Total number of discrepancies: {discrepancy_count}')
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sentence splitter')
    parser.add_argument('-i', '--input_folder', default='input', help='Input folder (default: input)')
    parser.add_argument('-o', '--output_folder', default='output', help='Output folder (default: output)')
    parser.add_argument('-t', '--time_limit', type=int, default=24, help='Maximum wall time in hours (default: 24)')
    args = parser.parse_args()

    if args.input_folder == 'input':
        print('No input folder provided. Using default: input')
    if args.output_folder == 'output':
        print('No output folder provided. Using default: output')

    main(args.input_folder, args.output_folder, args.time_limit)


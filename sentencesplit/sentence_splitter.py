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
import sys
# import nltk
import torch
import argparse
import pandas as pd
from transformers import RobertaTokenizer, GPT2Tokenizer

import spacy

# Load the spaCy model (make sure to install it first with: python -m spacy download en_core_web_sm)
nlp = spacy.load('en_core_web_sm')
nlp = spacy.load('en_core_web_sm')
nlp.max_length = 2100000 # Increase the maximum text length

def tabless(text):
    # Remove tabs from text
    return text.replace('\t', ' ').replace('  ', ' ')

def split_sentences(text):
    # Split text into sentences
    text = text.replace('<pb>', ' ')
    # sentences = nltk.sent_tokenize(text)
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]

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

def main(input_folder, output_folder):
    # Load tokenizers
    roberta_tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
    gpt2_tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # If a file exists named output_folder.processed_files.txt,
    # read it and skip the files that have already been processed.

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

        if filename.endswith('.txt'):
            print(f'Processing {filename}')
            with open(os.path.join(input_folder, filename), 'r') as f:
                text = f.read()
                if len(text) > 2000000:
                    chunks = split_text_at_whitespace(text, max_length=2000000)
                    dfs = []
                    for i, chunk in enumerate(chunks):
                        sentences = split_sentences(chunk)
                        num_tokens_roberta = count_tokens(sentences, roberta_tokenizer)
                        num_tokens_gpt2 = count_tokens(sentences, gpt2_tokenizer)
                        df = pd.DataFrame({'#tokensRoberta': num_tokens_roberta,
                                           '#tokensGPT2': num_tokens_gpt2,
                                           'sentence': sentences})
                        dfs.append(df)
                    df = pd.concat(dfs)
                else:
                    sentences = split_sentences(text)
                    num_tokens_roberta = count_tokens(sentences, roberta_tokenizer)
                    num_tokens_gpt2 = count_tokens(sentences, gpt2_tokenizer)
                    df = pd.DataFrame({'#tokensRoberta': num_tokens_roberta,
                                   '#tokensGPT2': num_tokens_gpt2,
                                   'sentence': sentences})
                
                df.to_csv(os.path.join(output_folder, filename.replace('.txt', '.tsv')), sep='\t', index=False)
                with open(processed_file, 'a') as f:
                    f.write(filename + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sentence splitter')
    parser.add_argument('-i', '--input_folder', default='input', help='Input folder (default: input)')
    parser.add_argument('-o', '--output_folder', default='output', help='Output folder (default: output)')
    args = parser.parse_args()

    if args.input_folder == 'input':
        print('No input folder provided. Using default: input')
    if args.output_folder == 'output':
        print('No output folder provided. Using default: output')

    main(args.input_folder, args.output_folder)


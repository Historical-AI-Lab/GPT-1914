#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Master Process Script ProcessBooks.py
#
# This script takes a group of digitized books through all the stages of cleaning:
# 1. Trimming front and back matter
# 2. Removing headers and footers / page numbers
# 3. OCR post-processing

# It processes books in batches, allowing for efficient handling of large
# datasets. The whole group of books can be passed to the script via command 
# line arguments, either as a list of file paths, or as the path to a .jsonl file 
# containing the books.
#
# The script then iterates through the assigned books in batches defined by a
# parameter M that specifies the maximum memory size, in megabytes, to be
# processed at once.

import sys
import json
import os
from pathlib import Path
import argparse
import SonicScrewdriver as pairtreeutils
import TagTokens
import RemoveHeaders
import zipfile

import os

def read_zip_pages(zip_path, source_file):
    pages = []
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            for file_info in z.infolist():
                if file_info.filename.endswith('.txt'):
                    # Extract the page number from the filename
                    page_part = file_info.filename.split('/')[-1].split('.')[0]
                    # make sure the page number is numeric; accept only numeric characters
                    # starting with the last character and moving left until a non-numeric character is found
                    # or until the start of the string is reached
                    page_number = int(''.join(filter(str.isdigit, page_part[::-1]))[::-1])
                    with z.open(file_info) as f:
                        text = f.read().decode('utf-8')
                        pages.append({'text': text,
                                      'meta': {'source_file': source_file, 'page_number': page_number}})
    except zipfile.BadZipFile:
        print(f"Bad zip file: {zip_path}")
    
    # sort pages by page number
    pages.sort(key=lambda x: x['meta']['page_number'])

    # confirm that page numbers start at 1 and are consecutive
    if pages:
        problematic = False
        for i, page in enumerate(pages):
            page_number = page['meta']['page_number']
            if page_number != i + 1: 
                problematic = True
                page['meta']['page_number'] = i + 1  # adjust page number to be consecutive
        if problematic:
            print(f"Warning: Page numbers in {source_file} were not consecutive. Adjusted to be consecutive starting from 1.")
    else:
        print(f"No pages found in {source_file}. Please check the zip file.")
    
    # returns a list of dictionaries, each containing the text and metadata for each page
    # where metadata includes the source file and page number
    #  
    return pages

def get_jsonl_pages(line):
    row = json.loads(line)
    source_file = row['hathitrust_data_ext']['url'].split("/")[-1]  # Extract the file name from the URL
    pages = row['text_by_page_src']
    pagedicts = []
    for page_number, text in enumerate(pages):
        pagedicts.append({'text': text,
                        'meta': {'source_file': source_file, 'page_number': page_number}})
    return pagedicts

def get_batch_by_jsonl(jsonl_path, max_size_mb=100):
    batch = []
    current_size_mb = 0
    
    with open(jsonl_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue  
            line_size_mb = len(line.encode('utf-8')) / (1024 * 1024)

            pages = read_jsonl_pages(line)
            batch.extend(pages) 
            
            if current_size_mb + line_size_mb > max_size_mb and batch:
                yield batch
                batch = []
                current_size_mb = 0
            else:
                current_size_mb += line_size_mb
                
    if batch:
        yield batch

def get_batch_by_paths(book_paths, trigger_size_mb=100):
    '''Generates batches of book paths based on the total size in megabytes.
    Batches are not guaranteed to be less than trigger_size, but the first
    file that exceeds the trigger size will end this batch.

    We expect book_paths to be a list of file paths to zip files
    containing book pages, where each zip file contains text files named
    with page numbers (e.g., "page1.txt", "page2.txt", etc.). 

    Returns a list of page dictionaries, where each page is represented 
    as a dict with two keys: 'text': the text content of the page, 
    and 'meta': a dict containing the source file and page number.
    '''
    batch = []
    current_size_mb = 0
    
    for path in book_paths:
        file_size_mb = os.path.getsize(path) / (1024 * 1024)

        source_file = os.path.basename(path)
        pages = read_zip_pages(path, source_file)
        batch.extend(pages)
        
        if current_size_mb + file_size_mb > max_size_mb and batch:
            yield batch
            batch = []
            current_size_mb = 0
        else:
            current_size_mb += file_size_mb
            
    if batch:
        yield batch

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a group of digitized books.")
    # input type: either a list of book file paths or a .jsonl file containing book metadata
    # by default, it expects a list of book paths
    parser.add_argument("--input_type", type=str, choices=['paths', 'jsonl'], default='paths',
                        help="Specify the input type: 'paths' for a file of book paths or 'jsonl' for a .jsonl file containing books.")
    parser.add_argument("--input", type=str, help="File containing book file paths or a .jsonl file containing book metadata.")
    parser.add_argument("--batch_mb", type=int, default=100, help="Number of megabytes in each batch.")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the pre-trained model for inference.") 
    parser.add_argument("--output_folder", type=str, default="output", help="Folder to save the processed books.") 

    args = parser.parse_args()

    # Ensure the output folder exists
    os.makedirs(args.output_folder, exist_ok=True)

    # Ensure the model path is provided
    if not args.model_path:
        print("Please provide the path to the pre-trained model.")
        sys.exit(1)
    # Load the pre-trained model for inference
    InferHeaders.load_model(args.model_path)
    
    if args.input_type == 'paths':
        if not args.input:
            print("Please provide a file containing book paths.")
            sys.exit(1)
        
        with open(args.input, 'r', encoding='utf-8') as f:
            book_paths = [line.strip() for line in f if line.strip()]
        
        if not book_paths:
            print("No valid book paths found in the input file.")
            sys.exit(1)
        
        batches = get_batch_by_paths(book_paths, max_size_mb=args.batch_mb)

    elif args.input_type == 'jsonl':
        if not args.input:
            print("Please provide a .jsonl file containing book metadata.")
            sys.exit(1)
        
        if not os.path.exists(args.input):
            print(f"The file {args.input} does not exist.")
            sys.exit(1)
        
        batches = get_batch_by_jsonl(args.input, max_size_mb=args.batch_mb)
    
    # The main processing loop
    # Each batch will contain a list of page dictionaries, where each page is represented
    # as a dict with two keys: 'text': the text content of the page,
    # and 'meta': a dict containing the source file and page number. 

    # The output will be a set of text files, one for each book,
    # containing the cleaned text of the book, with headers and footers removed.

    batch_counter = 1
    for batch in batches:

        # TODO insert the front/back matter trimming here

        print(f"Processing batch {batch_counter} with {len(batch)} pages.")
        processed_pages = TagTokens.tokenize_books(batch)

        # processed_pages will have this structure:
        # processed_pages = [
        # {
        #     'source_file': 'book1.pdf',
        #     'page_number': 1,
        #     'tokens': ['This', 'is', 'a', 'header', '.', 'Main', 'content', 'here', '.'],
        #     'metadata_tags': [[], [], [], ['header'], [], [], [], [], []]
        # },
        # ... more pages]

        filtered_pages = RemoveHeaders.run_inference(pages, batch_size=16)

        # Each filtered page will have only KEEP tokens:
        # {
        #     'source_file': 'book1.pdf',
        #     'page_number': 1,
        #     'tokens': ['Main', 'content', 'here', '.']
        # }

        # TODO: Insert the OCR post-processing here.
        # We're going to use a ByT5 model, fine-tuned on documents
        # in domain.

        # Now we can write the filtered books to the output folder.
    
        dict_of_pages = set()
        for page in filtered_pages:
            source_file = page['meta']['source_file']
            if source_file not in dict_of_pages:
                dict_of_pages[source_file] = []
            dict_of_pages[source_file].append(page)
        
        for source_file, pages in dict_of_pages.items():
            if '/' in source_file or '.' in source_file:
                source_file = pairtreeutils.clean_pairtree(source_file)
            output_file = os.path.join(args.output_folder, f"{source_file}.txt")
            pages.sort(key=lambda x: x['page_number']) # sort defaults to ascending order
            with open(output_file, 'w', encoding='utf-8') as f:
                for page in pages:
                    f.write(page['text'] + '\n')

        batch_counter += 1
    print(f"Processing completed. Processed {batch_counter - 1} batches.") 
        



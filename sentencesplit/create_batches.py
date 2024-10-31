# Create file batches

import os
import math
import argparse

def convert_size(size):
    if (size == 0):
        return '0B'
    size_name = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p, 2)
    return '%s %s' % (s, size_name[i])

def main(input_folder, output_folder):
    processed_files = set()
    processed_file = os.path.join(output_folder, 'processed_files.txt')
    if os.path.exists(processed_file):
        with open(processed_file, 'r') as f:
            for line in f:
                processed_files.add(line.strip())

    input_files = set(os.listdir(input_folder))
    
    still_to_process = input_files - processed_files

    # Get list of files with their full paths
    files = [os.path.join(input_folder, f) for f in still_to_process if os.path.isfile(os.path.join(input_folder, f))]
    
    # Sort files by size in descending order
    files_sorted = sorted(files, key=os.path.getsize, reverse=True)

    # Create twenty batches of files

    batch_size = len(files_sorted) // 20
    batches = [files_sorted[i:i+batch_size] for i in range(0, len(files_sorted), batch_size)]

    for i, batch in enumerate(batches):
        batchfile = 'batch_' + str(i) + '.txt'
        with open(batchfile, 'w') as f:
            for file in batch:
                f.write(file + '\n')
        firstfilesize = os.path.getsize(batch[0])
        lastfilesize = os.path.getsize(batch[-1])

        # convert to human readable size
        firstfilesize = convert_size(firstfilesize)
        lastfilesize = convert_size(lastfilesize)

        print(f'Batch {i} has {len(batch)} files, first file size: {firstfilesize}, last file size: {lastfilesize}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create file batches')
    parser.add_argument('-i', '--input_folder', required=True, help='Input folder')
    parser.add_argument('-o', '--output_folder', required=True, help='Output folder')
    args = parser.parse_args()
    main(args.input_folder, args.output_folder)

# Batch creator
# 
# Reads in all the files in a directory and divides them (alphabetically)
# into batches of 70k each.

# Each batch list is saved as a separate file in the same directory.

import os
import sys
import re

directory = '/work/hdd/bdfx/sentences/outputprewar/'

# Get a list of all the files in the directory
# that end in 'trim.tsv'
files = os.listdir(directory)
files = [f for f in files if re.match(r'.*trim.tsv', f)]
files.sort()

# Create a list of lists to hold the batches
batches = []
batch = []
for file in files:
    if len(batch) > 70000:
        batches.append(batch)
        batch = []
    batch.append(file)
batches.append(batch)

# Save the batches to files
for i, batch in enumerate(batches):
    with open(directory + 'batch' + str(i) + '.txt', 'w') as f:
        for file in batch:
            f.write(file + '\n')
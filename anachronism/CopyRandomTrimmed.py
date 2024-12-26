# Whereas CopyTrimmed.py copies all the files in a held-out list,
# this script copies a random set of 120 files *excluding* the held-out list.

import os
import shutil, random

def clean_pairtree(htid):
    period = htid.find('.')
    prefix = htid[0:period]
    postfix = htid[(period+1): ]
    if ':' in postfix:
        postfix = postfix.replace(':','+')
        postfix = postfix.replace('/','=')
    if '.' in postfix:
        postfix = postfix.replace('.',',')
    cleanname = prefix + "." + postfix
    return cleanname

files_to_avoid = open('HeldOutHTidListNoDupes.txt', encoding = 'utf-8').readlines()
files_to_avoid = [clean_pairtree(x.strip()) + '.trim.txt' for x in files_to_avoid]

sourcefolder = '../train1/outputprewar/'
destination = 'trimmedfiles/'

files_to_copy = os.listdir(sourcefolder)
files_to_copy = [x for x in files_to_copy if x.endswith('.txt')]
print(len(files_to_copy), 'files available in source folder.')
files_to_copy = [x for x in files_to_copy if x not in files_to_avoid]
print(len(files_to_copy), 'files available after removing held-out list.')
files_to_copy = random.sample(files_to_copy, 120)

for filename in files_to_copy:
    source = sourcefolder + filename
    destination = 'trimmedfiles/' + filename
    shutil.copyfile(source, destination)


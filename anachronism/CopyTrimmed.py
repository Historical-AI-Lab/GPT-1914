# copy held-out files

import os
import shutil

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

files_to_copy = open('HeldOutHTidListNoDupes.txt', encoding = 'utf-8').readlines()

sourcefolder = '../train1/outputprewar/'
destination = 'trimmedfiles/'

for line in files_to_copy:
    filename = clean_pairtree(line.strip())
    source = sourcefolder + filename + '.trim.txt'
    destination = 'trimmedfiles/' + filename + '.trim.txt'
    shutil.copyfile(source, destination)


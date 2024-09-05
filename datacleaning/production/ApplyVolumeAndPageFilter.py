# ApplyVolumeAndPageFilter.py

# This production script rolls several functions that we've developed
# separately into a single script. Given a metadata file and a root
# folder where text files are stored, it will generate a matrix of
# features for each page in the text files. It will also generate
# a matrix of features for each volume, by averaging the features
# of pages in that volume.
#
# Then it applies two filters: first, a volume-level filter
# identifies volumes that are not in English or contain purely
# reference material. Those are marked for exclusion in the
# metadata file. 
# 
# Second, for each volume that remains, a page-level filter 
# identifies pages that are likely to be paratext. A new
# trimmed text file is created for each volume, with paratext
# pages removed. Running headers are also trimmed at this stage.

# The new files, with an extension of ".trim.txt", are saved in an
# output folder that is passed in as a command-line argument.

# import modules

import numpy as np
import pandas as pd

import os, math
from collections import Counter

import argparse, joblib, sklearn

import header

# We're going to use a list of common verbs, and a list of words that are
# likely to signal paratext. We'll also use a list of the 2000 most common
# words in English.

top2000lexicon = set()

# The features below were identified as likely to signal paratext by running Dunnings' log likelihood
# on about 400 volumes with pages manually tagged as paratext or text.

paratext_clues = {'v', 'c', 'iv', 'p', 'pp', 'contents', 'd', 'ib', 'illustrations', 'esq', 'cloth',
         'iii', 'vols', 'ii', 'ibid', 'edition', 's', 'vo', 'book', 'volume', 'page', 'shillings',
         'edited', 'chapter', 'author', 'price', 'illustrated', 'extra', 'dollars', 'cents', 'published',
         'library', 'rev', 'crown', 'j', 'v', 'w', 'index', 'vi', 'viii', 'ix', 'x', 'xi', 'xii'}

byofset = {'by', 'of'}
priceset = {'$', '£', '¢'}

# We're using a version of the Main Dictionary that has been cleaned of some
# abbreviations, foreign words, and word fragments ("de", "la", "com", etc). 

with open('CleanedMainDictionary.txt', encoding = 'utf-8') as file:   
    lines = file.readlines()

for i, line in enumerate(lines):
    word = line.split('\t')[0].strip()
    if word in paratext_clues or word in byofset or len(word) < 2:    # we don't allow paratext clues in the lexicon
        continue
    if len(top2000lexicon) < 2000: 
        top2000lexicon.add(word)
    else:
        break

with open('romannumerals.txt', encoding = 'utf-8') as file:
    romannumerals = set([x.strip() for x in file.readlines() if len(x.strip()) > 0])

# Verbs can be useful features, because they are more common in body text than
# in indexes and other list-like genres of paratext.

verbs = set()
with open('EnglishVerbs.txt', encoding = 'utf-8') as file:
    for line in file:
        verbs.add(line.strip())

def paginate_file(filepath):
    ''' This function takes a text file with <pb> tags and returns a list of pages.
    Each page is a list of lines. Each line is a string.
    '''
    with open(filepath, encoding = 'utf-8') as file:
        lines = file.readlines()
    
    pages = []
    current_page = []

    for line in lines:
        if line.startswith('<pb>'):
            pages.append(current_page)
            current_page = []
        else:
            current_page.append(line)
    
    pages.append(current_page)
    return pages

# We construct features in two passes, because many of the final features will be
# relative to volume averages, or to adjacent pages. The first pass calculates
# a set of features that are page-local. The second pass calculates features
# that are relative to the volume or to adjacent pages.

# Initial page-local features:

# pagenum: the (absolute) page number
# pagefrac: the page number divided by the total number of pages
# backnum: the number of pages from the end of the volume
# backfrac: the proportion of the volume that is behind this page
# nlines: the number of lines on the page
# nwords: the number of words on the page
# nalpha: the number of alphabetic characters on the page
# fracalpha: the proportion of alphabetic characters
# nnumeric: the number of numeric characters on the page
# fracnumeric: the proportion of numeric characters
# npunct: the number of punctuation characters on the page
# fracpunct: the proportion of punctuation characters
# nupper: the number of uppercase characters on the page
# fracupper: the proportion of uppercase characters
# nother: the number of characters on the page that are not in the above categories
# fracother: the proportion of characters that are not in the above categories
# meanlinelen: mean linelength (in characters)
# sdlinelen: the standard deviation of linelength (in characters)
# meanwordlength: the mean length of words
# startupper: the proportion of lines that start with an uppercase letter
# verbs: the proportion of words that are in our list of ~460 common verbs
# top2000words: the proportion of words that are in the top 2000 most common words
# paratextwords: the proportion of words that are in our list of paratext clues
# byofwords: the proportion of words that are "by" or "of"
# fracprice: the proportion of characters that are currency symbols

def page_features(page, pagenum, totalpgcount):
    ''' This function takes a list of lines and returns a dictionary of features.
    '''

    global verbs, top2000lexicon, paratext_clues

    pagefrac = pagenum / totalpgcount
    backnum = totalpgcount - pagenum
    backfrac = backnum / totalpgcount
    nlines = len(page)
    nwords = 0
    nalpha = 0
    nnumeric = 0
    npunct = 0
    nupper = 0
    nother = 0
    nprice = 0
    wordlengths = []
    linelengths = []
    startupper = 0
    verbwords = 0
    top2000words = 0
    paratextwords = 0
    byofwords = 0
    
    for line in page:
        nwords += len(line.split())
        linelengths.append(len(line))
        if len(line) == 0:
            pass
        else:
            if line[0].isupper():
                startupper += 1
            for word in line.split():
                wordlengths.append(len(word))
                # strip punctuation and convert to lowercase
                lowerword = ''.join([char.lower() for char in word if char.isalpha()])
                
                if lowerword in byofset:
                    byofwords += 1
                if lowerword in verbs:
                    verbwords += 1
                if lowerword in top2000lexicon:
                    top2000words += 1
                if lowerword in paratext_clues:
                    paratextwords += 1
                for char in word:
                    if char.isalpha():
                        nalpha += 1
                    elif char.isnumeric():
                        nnumeric += 1
                    elif char in '.,;:?!()-"“”\'\'':
                        npunct += 1
                    else:
                        nother += 1
                    
                    if char.isupper():
                        nupper += 1
                    if char in priceset:
                        nprice += 1
    
    meanlinelen = np.mean(linelengths) if len(linelengths) > 0 else 0
    sdlinelen = np.std(linelengths) if len(linelengths) > 1 else 0
    meanwordlength = np.mean(wordlengths) if len(wordlengths) > 0 else 0
    nchars = nalpha + nnumeric + npunct + nother + len(wordlengths) # counting words is counting spaces!
    if nchars > 0:
        fracalpha = nalpha / nchars
        fracnumeric = nnumeric / nchars
        fracpunct = npunct / nchars
        fracupper = nupper / nchars
        fracother = nother / nchars
        fracprice = nprice / nchars
    else:
        fracalpha = 1
        fracnumeric = 0
        fracpunct = 0
        fracupper = 0
        fracother = 0
        fracprice = 0
    startupper = startupper / nlines if nlines > 0 else 0
    verbwords = verbwords / nwords if nwords > 0 else 0
    top2000words = top2000words / nwords if nwords > 0 else 0
    paratextwords = paratextwords / nwords if nwords > 0 else 0
    byofwords = byofwords / nwords if nwords > 0 else 0

    pg_feature_dict = {'pagenum': pagenum, 'pagefrac': pagefrac, 'backnum': backnum, 'backfrac': backfrac,
            'nlines': nlines, 'nwords': nwords, 'nalpha': nalpha, 'fracalpha': fracalpha,
            'nnumeric': nnumeric, 'fracnumeric': fracnumeric, 'npunct': npunct, 'fracpunct': fracpunct,
            'nupper': nupper, 'fracupper': fracupper, 'nother': nother, 'fracother': fracother,
            'meanlinelen': meanlinelen, 'sdlinelen': sdlinelen, 'meanwordlength': meanwordlength,
            'startupper': startupper, 'verbs': verbwords, 'top2000words': top2000words, 'paratextwords': paratextwords,
            'byofwords': byofwords, 'fracprice': fracprice}
    return pg_feature_dict

# Now for each page we add the following relative features:

# nwordsminusmean: the number of words on this page minus the volume average
# wordlengthminusmean: the mean word length on this page minus the volume average
# top2000minusmean: the proportion of words on this page that are in the top 2000 minus the volume average
# nwordsminusprev: the number of words on this page minus the number of words on the previous page
# top2000minusprev: the proportion of words on this page that are in the top 2000 minus the proportion on the previous page

def safe_mean(values):
    # Calculate the mean, but return 0 if the list is empty
    return np.mean(values) if values else 0


def add_relative_features(pages, htid):
    '''
    This function accepts a list of dictionaries produced by the page_features function,
    and adds relative features to each dictionary.
    '''

    # We calculate means ignoring zeroes.

    volmeanwords = safe_mean([d['nwords'] for d in pages if d['nwords'] != 0])
    volmeanwordlength = safe_mean([d['meanwordlength'] for d in pages if d['meanwordlength'] != 0])
    volmeantop2000 = safe_mean([d['top2000words'] for d in pages if d['top2000words'] != 0])
    volmeansdlinelen = safe_mean([d['sdlinelen'] for d in pages if d['sdlinelen'] != 0])
    volmeanlinelen = safe_mean([d['meanlinelen'] for d in pages if d['meanlinelen'] != 0])

    for i, page in enumerate(pages):

        # For some features, zero is not an informative value. It tells us only that
        # there are no words on the page, and that's something we already know from
        # the nwords feature. So we replace zero with the volume average, which makes
        # differences in this variable more informative by eliminating the outlier
        # status of pages with no words.

        if page['meanwordlength'] == 0:
            page['meanwordlength'] = volmeanwordlength
        if page['sdlinelen'] == 0:
            page['sdlinelen'] = volmeansdlinelen
        if page['meanlinelen'] == 0:
            page['meanlinelen'] = volmeanlinelen
        if page['top2000words'] == 0:
            page['top2000words'] = volmeantop2000

        # Some features will vary across volumes, but we want to know how they vary
        # within a volume. So we subtract the volume average from the page value.
        # Note that this interacts with the change we made above, replacing zero
        # with the volume average. That's intentional. It means, once again, that pages
        # with no words will tend to have a neutral value for this feature. We already
        # know they have no words, and need to use this feature to make subtler
        # discriminations.

        page['nwordsminusmean'] = page['nwords'] - volmeanwords
        page['wordlengthminusmean'] = page['meanwordlength'] - volmeanwordlength
        page['linelenminusmean'] = page['meanlinelen'] - volmeanlinelen
        page['top2000minusmean'] = page['top2000words'] - volmeantop2000

        # Some features are potentially informative in themselves, but also
        # because a change signals a transition from one part of the volume to another.

        if i > 2:
            nwordsminusprev = page['nwords'] - np.mean([pages[i - 1]['nwords'], pages[i - 2]['nwords'], pages[i - 3]['nwords']])
            top2000minusprev = page['top2000words'] - np.mean([pages[i - 1]['top2000words'], pages[i - 2]['top2000words'], pages[i - 3]['top2000words']])
        elif i > 1:
            nwordsminusprev = page['nwords'] - np.mean([pages[i - 1]['nwords'], pages[i - 2]['nwords']])
            top2000minusprev = page['top2000words'] - np.mean([pages[i - 1]['top2000words'] , pages[i - 2]['top2000words']])
        elif i > 0:
            nwordsminusprev = page['nwords'] - pages[i - 1]['nwords']
            top2000minusprev = page['top2000words'] - pages[i - 1]['top2000words']
        else:
            nwordsminusprev = 0
            top2000minusprev = 0

        page['nwordsminusprev'] = nwordsminusprev
        page['top2000minusprev'] = top2000minusprev

        # We also calculate the absolute distance from the volume's center,
        # and quadratic versions of all positional features.

        page['centerdist'] = abs(page['pagefrac'] - 0.5)
        page['centerdist^2'] = page['centerdist'] ** 2
        page['pagefrac^2'] = page['pagefrac'] ** 2
        page['backfrac^2'] = page['backfrac'] ** 2
        page['htid'] = htid  # we need this to separate training and test sets by volume
    
    # # Check if the mean of relative features is zero
    # mean_wordlengthminusmean = np.mean([d['wordlengthminusmean'] for d in pages])
    # mean_linelenminusmean = np.mean([d['linelenminusmean'] for d in pages])
    # mean_top2000minusmean = np.mean([d['top2000minusmean'] for d in pages])
    # mean_nwordsminusmean = np.mean([d['nwordsminusmean'] for d in pages])

    # print("Mean of wordlengthminusmean:", mean_wordlengthminusmean)
    # print("Mean of linelenminusmean:", mean_linelenminusmean)
    # print("Mean of top2000minusmean:", mean_top2000minusmean)
    # print("Mean of nwordsminusmean:", mean_nwordsminusmean)
    
    return pages

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

def pairtreepath(htid,rootpath):
    ''' Given a HathiTrust volume id, returns a relative path to that
    volume. While the postfix is part of the path, it's also useful to
    return it separately since it can be a folder/filename in its own
    right.'''

    period = htid.find('.')
    prefix = htid[0:period]
    postfix = htid[(period+1): ]
    if ':' in postfix:
        postfix = postfix.replace(':','+')
        postfix = postfix.replace('/','=')
    if '.' in postfix:
        postfix = postfix.replace('.',',')
    path = rootpath + prefix + '/pairtree_root/'

    if len(postfix) % 2 != 0:
        for i in range(0, len(postfix) - 2, 2):
            next_two = postfix[i: (i+2)]
            path = path + next_two + '/'
        path = path + postfix[-1] + '/'
    else:
        for i in range(0, len(postfix), 2):
            next_two = postfix[i: (i+2)]
            path = path + next_two + '/'

    return path, postfix

def labeled_volume(htid, textroot):
    '''
    This function takes a volume ID and a root directory for text files. It returns a 
    list of dictionaries, each representing a page, with features and a label.
    '''

    path, postfix = pairtreepath(htid, textroot)

    textpath = path + postfix + '/' + postfix + '.norm.txt'

    if not os.path.isfile(textpath):
        print(textpath, 'does not exist.')
        return []

    pages = paginate_file(textpath)

    totalpgcount = len(pages)

    for i in range(totalpgcount):
        page = page_features(pages[i], i, totalpgcount)
        pages[i] = page
    
    pages = add_relative_features(pages, htid)

    return pages, textpath

def apply_volume_filter(volumematrix, metadata, volume_model, scaler):

    usedfeatures = volumematrix.loc[ : , ['fracalpha', 'fracnumeric', 'verbs', 'top2000words', 'max_top2000words']]

    X = scaler.transform(usedfeatures)
    y = volume_model.predict_proba(X)

    filtered_out = ['exclude' if x > 0.8 else 'ok' for x in y[:, 1]]
    metadata['exclude'] = filtered_out

    return metadata

# Now we define a simple function that uses predicted probabilities
# for pages to infer a good start page, where paratext gives way to text,
# and a good end page, where text gives way to paratext.

# In reality, text and paratext can be interleaved throughout a volume,
# but the odds of making an error, and destroying continuity, are fairly
# high in the middle of a volume. By contrast, the mere fact of position
# at the beginning or end of a volume is a strong enough signal to support
# a reliable, conservative "trimming" approach.

# Our goal is to stop trimming when we hit a
# sequence of three pages that are all text. For this reason, we combine
# the probability of the current page with the average probability of the
# next two pages, and use that as a guide. The default parameters
# set below have been determined by trial and error.

def simple_probabilistic_cut(vol_df, threshold = 0.5, longlookweight = 0.1):
    ''' This function takes a dataframe representing a volume, and
    parameters that define a probability threshold, along with the weight
    to be assigned to a "look forward" at the next two pages. It returns
    
    '''

    inferred_labels = []
    text_probabilities = vol_df['probabilities'].tolist()
    text_lengths = vol_df['wordcount'].tolist()
    text_lengths = [1 for x in text_lengths] # we're treating all pages equally;
                                                #weighting them did not help
    firstcut = len(text_probabilities)
    for i in range(len(text_probabilities)):
        lookforward = i + 3
        if lookforward >= len(text_probabilities):
            lookforward = len(text_probabilities)
        # longlookforward = i + 5
        # if longlookforward >= len(text_probabilities):
        #     longlookforward = len(text_probabilities)
        # longavg = sum(text_probabilities[i:lookforward]) / len(text_probabilities[i:lookforward])
        longavg = sum([text_probabilities[j] * text_lengths[j] for j in range(i, lookforward)]) / sum(text_lengths[i:lookforward])
        shortavg = text_probabilities[i]
        textavg = (shortavg * (1 - longlookweight)) + (longavg * longlookweight)
        if textavg >= threshold:
            firstcut = i
            break

    lastcut = 0
    for i in range(len(text_probabilities), 0, -1):
        lookback = i - 3
        if lookback < 0:
            lookback = 0
        # longlookback = i - 5
        # if longlookback < 0:
        #     longlookback = 0
        longavg = sum([text_probabilities[j] * text_lengths[j] for j in range(lookback, i)]) / sum(text_lengths[lookback:i])
        shortavg = text_probabilities[i - 1]
        textavg = (shortavg * (1 - longlookweight)) + (longavg * longlookweight)
        if textavg >= threshold:
            lastcut = i
            break
    
    if firstcut < lastcut:
        inferred_labels = ['para'] * firstcut + ['text'] * (lastcut - firstcut) + ['para'] * (len(text_probabilities) - lastcut)
        assert len(inferred_labels) == len(text_probabilities)
    else:
        inferred_labels = ['para'] * len(text_probabilities)
    
    return inferred_labels

def main():

    global top2000lexicon, paratext_clues, byofset, priceset, verbs, romannumerals

    # The valid arguments are
    # -m --meta: the path to the metadata file
    # -f --folder: the path to the folder containing the text files
    # -o --output: the path to the output file

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--meta", help="the path to the metadata file")
    parser.add_argument("-f", "--folder", help="the path to the folder containing the text files")
    parser.add_argument("-o", "--output", help="the path to the output directory")

    args = parser.parse_args()

    if args.meta:
        meta_path = args.meta
    else:
        sys.exit("Please provide the path to the metadata file")
    
    if args.folder:
        input_dir = args.folder
        # if the input directory doesn't end in a slash we add one
        if input_dir[-1] != '/':
            input_dir = input_dir + '/'
        
    else:
        sys.exit("Please provide the path to the folder containing the text files")
    
    if args.output:
        output_dir = args.output
        # if the output directory doesn't end in a slash we add one
        if output_dir[-1] != '/':
            output_dir = output_dir + '/'

    else:
        sys.exit("Please provide the path to the output directory")
    
    page_model = joblib.load('page_RF_model4.pkl') # This is the page-level model that will be used to filter out paratext
    volume_model = joblib.load('logreg_for_volume_filter.pkl')
    scaler = joblib.load('scaler_for_volume_filter.pkl')

    ctr = 0
    alreadyhave = set()
    
    metadata = pd.read_csv(meta_path, sep = '\t', low_memory = False)

    htids = metadata['HTid'].tolist()
    
    allpages = []
    pathdictionary = dict()

    foundhtids = []

    for htid in htids:

        htid = clean_pairtree(htid)
        
        if htid in alreadyhave:
            continue
        else:
            alreadyhave.add(htid)

        try:
            pages, path_to_vol = labeled_volume(htid, input_dir)
            pathdictionary[htid] = path_to_vol
            if len(pages) < 1:
                print('No pages in', htid, flush=True)
                continue
        except:
            print('Error with', htid, flush=True)
            continue
        
        ctr += 1
        if ctr % 50 == 1:
            print(ctr, flush=True)

        allpages.extend(pages)
        foundhtids.append(clean_pairtree(htid))

    print('Total volumes:', ctr)
    print('Total pages:', len(allpages), flush=True)

    featurematrix = pd.DataFrame(allpages)

    # Now we have a featurematrix with a row for each page. We're going to
    # use it to create a volumematrix, with a row for each volume.

    volumematrix = featurematrix.groupby('htid').mean().reset_index()
    metadata['htid'] = metadata['HTid'].apply(clean_pairtree)
    metadata.set_index('htid', inplace = True)
    volumematrix.set_index('htid', inplace = True)
    volumematrix = volumematrix.merge(metadata[['title', 'inferred_date']], left_index=True, right_index=True, how='inner')
    print('Total volumes after metadata merge:', len(volumematrix))
    volumematrix.drop(['centerdist', 'backfrac', 'nwordsminusmean', 'wordlengthminusmean', 'linelenminusmean', 'top2000minusmean', 
                       'nwordsminusprev', 'centerdist^2', 'pagefrac^2', 'backfrac^2'], axis=1, inplace=True)
    
    featurematrix['n2000words'] = featurematrix['top2000words'] * featurematrix['nwords']
    groups = featurematrix.groupby('htid')
    top10percent2000 = []
    htidindex = []
    for htid, group in groups:
        numrows = len(group)
        if numrows < 1:
            thetop = 0
        else:
            numtoaverage = math.ceil(numrows / 10)
            thetop = np.mean(group.top2000words.sort_values(ascending=False)[0: numtoaverage])
        top10percent2000.append(thetop)
        htidindex.append(htid)
    htid_top10percent2000 = pd.Series(top10percent2000, index = htidindex)
    htid_std_top2000 = featurematrix.groupby('htid')['top2000words'].std()
    htid_sum_top2000 = featurematrix.groupby('htid')['n2000words'].sum()

    htid_features = pd.DataFrame({'max_top2000words': htid_top10percent2000, 'std_top2000words': htid_std_top2000, 'sum_top2000words': htid_sum_top2000})
    htid_features.index.name = 'htid'

    volumematrix = volumematrix.merge(htid_features[['max_top2000words', 'std_top2000words', 'sum_top2000words']], left_index=True, right_index=True, how='inner')

    # Now we have a featurematrix with a row for each page, and a volumematrix
    # with a row for each volume. Let's use the volumematrix to filter out
    # volumes that are not in English or contain purely reference material.

    # Before we can do that, we need to deal with the problem that some rows
    # in the metadata file don't have corresponding rows in the volumematrix,
    # because we couldn't find text files for them. We'll exclude those rows,
    # by only keeping rows where the index is in the 'foundhtids' list.
    # Note that we have transformed both the index, and the elements of the 'foundhtids'
    # list, to a standard form that eliminates pairtree encoding.

    metadata = metadata.loc[foundhtids, :]
    print('Metadata rows after filtering:', len(metadata))
    print('Volumematrix rows after filtering:', len(volumematrix))

    print('Applying volume filter...', flush=True)
    filtered_meta = apply_volume_filter(volumematrix, metadata, volume_model, scaler)

    # Now we're going to apply a page-level filter to each volume that remains.
    # We'll identify pages that are likely to be paratext, and remove them.

    ctr = 0
    trimming_metadata = dict()

    print('Trimming volumes...', flush=True)
    print(featurematrix.shape, flush=True)
    print(featurematrix.columns, flush=True)
    print(featurematrix.index, flush=True)
    for htid in filtered_meta.index:
        if filtered_meta.loc[htid, 'exclude'] == 'exclude':
            continue
        pages = featurematrix[featurematrix['htid'] == htid].drop(['htid', 'n2000words'], axis=1)
        print(htid, pages.shape, flush=True)
        probabilities = page_model.predict_proba(pages)

        # Create a dataframe with columns for pagenum, htid, and probability
        vol_df = pd.DataFrame({
            'pagenum': pages['pagenum'],
            'wordcount': pages['nwords'],
            'probabilities': probabilities[:, 1]  # Assuming the second column contains the probabilities for 'text'
        })

        vol_df = vol_df.sort_values(by='pagenum')
        vol_df = vol_df.reset_index(drop=True)
        vol_df['inferred_labels'] = simple_probabilistic_cut(vol_df, threshold = 0.5, longlookweight = 0.1)
    
        input_path = pathdictionary[htid]
        output_path = os.path.join(output_dir, htid + '.trim.txt')

        pages = []
        thispage = []
        with open(input_path, encoding = 'utf-8') as file:
            lines = file.readlines()
        for l in lines:
            if l.startswith('<pb>'):
                pages.append(thispage)
                thispage = []
            else:
                thispage.append(l)
        pages.append(thispage)

        trimmed_pages = []
        cut_wordcount = 0
        for i, row in vol_df.iterrows():
            if row['inferred_labels'] == 'text':
                trimmed_pages.append(pages[i])
            else:
                cut_wordcount += row['wordcount']
        
        total_words = sum(vol_df['wordcount'])
        if total_words > 0:
            pct_trim = cut_wordcount / total_words
        else:
            pct_trim = 0

        trimmed_pages, removed = header.remove_headers(trimmed_pages, romannumerals)

        header_words = sum([len(x.split()) for x in removed])
        if total_words > 0:
            pct_header = header_words / total_words
        else:
            pct_header = 0

        with open(output_path, mode = 'w', encoding = 'utf-8') as file:
            for p in trimmed_pages:
                for l in p:
                    file.write(l)
                file.write('<pb>\n')
        
        trimming_metadata[htid] = {'total_words': total_words, 'pct_trim': pct_trim, 'pct_header': pct_header,
                                    'remaining_words': total_words - (cut_wordcount + header_words)}
        
        ctr += 1
        if ctr % 100 == 0:
            print(ctr, flush=True)
    
    # Save the metadata about trimming to a file
    with open(os.path.join(output_dir, 'trimming_metadata.tsv'), mode = 'w', encoding = 'utf-8') as file:
        file.write('htid\ttotal_words\tpct_trim\tpct_header\tremaining_words\n')
        for htid, data in trimming_metadata.items():
            file.write(htid + '\t' + str(data['total_words']) + '\t' + str(data['pct_trim']) + '\t' + str(data['pct_header']) + '\t' + str(data['remaining_words']) + '\n')
        
    print('Done!')

if __name__ == '__main__':
    main()
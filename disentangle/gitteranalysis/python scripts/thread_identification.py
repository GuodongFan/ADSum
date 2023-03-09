import os
import json
import pandas as pd
import glob
import numpy as np
import matplotlib.pyplot as plt
import time
from nltk.tree import Tree
import nltk
import re
from pprint import pprint

import re, math
from collections import Counter

from nltk.collocations import *
import pandas as pd
from nltk.tokenize import word_tokenize

#nltk.download('genesis')

texts = pd.read_csv('./data/combined_cleaned_unlisted.csv')
print("data loaded ....")
texts = texts[['id', 'text', 'clean', 'sent', 'username', 'chatroom']]
texts['sent'] = pd.to_datetime(texts['sent'])
texts['mention'] = 0
texts['ngrams'] = 0
texts['involved'] = 0
texts['back_and_forth'] = 0 # add 2023
texts = texts.fillna("")

def unique(a):
    a = np.ascontiguousarray(a)
    unique_a = np.unique(a.view([('', a.dtype)]*a.shape[1]))
    return unique_a.view(a.dtype).reshape((unique_a.shape[0], a.shape[1]))

bigram_measures = nltk.collocations.BigramAssocMeasures()
finder = BigramCollocationFinder.from_words(word_tokenize(' '.join(texts['text'])))
listBigrams = finder.nbest(bigram_measures.pmi, 10000) 
sorted_listBigrams = np.array(listBigrams)
sorted_listBigrams.sort(axis=1)
unique_listBigrams = unique(sorted_listBigrams)

def identify_threads(texts):
    texts['discussionId'] = [[] for _ in range(len(texts))]
    index = 0
    thread_id = 0
    thread_found = True
    for i in range(len(texts)):
        j = i
        starter = texts.iloc[i,3]
        ngram_group = list("")
        ngram_group += texts.iloc[i,10].split(',')
        involvement_group =list("")
        involvement_group.append(texts.iloc[i,4])
        if thread_found == True:
            thread_id += 1
            thread_found = False
        cutoff = 4
        counter = i + cutoff
        pairs = {}
        coupling_effect = False
        while (j < counter) :
            if j == len(texts)-1:
                break
            j = j + 1
            last_matched = 0
            matching = ""
            mention = 0
            involved = 0
            existing = 0
            my_list = texts.iloc[j,5].split(',')
            if texts.iloc[j,4] in involvement_group: #involement group
                involved = 1
            elif any(met in texts.iloc[j,1] for met in involvement_group): #mention from involvement group
                mention = 1
            elif (ngram_group[0] != '' ) & (my_list[0] != ''): # matching Bi-grams
                matching = [s for s in ngram_group if any(xs in s for xs in my_list)]
            #back and forth user pattern
            pattern = texts.iloc[j-1,4]+","+texts.iloc[j,4]
            if pairs.get(pattern):
                pairs[pattern] = pairs.get(pattern) + 1
            else:
                pairs[pattern] = 1
            user = ""
            for key,value in pairs.items():
                if value >= 3:
                    users = key.split(",")
                    for u in users:
                        if not u in involvement_group:
                            user = u
                            involvement_group.append(u)
                            coupling_effect = True
            if coupling_effect:
                coupling_effect = False
                for k in range(j, i, -1): 
                    if texts.iloc[k,4] == user:
                        texts.iloc[k,11].append(thread_id)
                        texts.iloc[k,9] = 1
            if (mention == 1) | (involved == 1) | (len(matching) > 0):
                texts.iloc[j,6] = mention
                texts.iloc[j,7] = len(matching)
                texts.iloc[j,8] = involved

                #这是什么逻辑？ 有病吧 写的代码这么难读
                existing = any(i in texts.iloc[j,11] for i in texts.iloc[i,11])
                if (thread_id not in texts.iloc[j,11]) & (existing == 0):
                    texts.iloc[j,11].append(thread_id)
                    thread_found = True
                    last_matched = j
                if (thread_id not in texts.iloc[i,11]) & (existing == 0):
                    texts.iloc[i,11].append(thread_id)
                    last_matched = j
                if thread_found == True:
                    involvement_group.append(texts.iloc[j,4])
                    ngram_group += texts.iloc[j,10].split(',')
            if ((j == counter)) & (last_matched != 0):
                if (counter - last_matched <= 2) :
                    counter += 4
                    index+=1
    return texts
	
texts['bigrams'] = ""
for i in range(len(texts)):
    flag = False
    text = texts.iloc[i,2]
    keywords = ""
    if i % 100000 == 0:
        print(i," messages bigrams done ...")
    for bigram in unique_listBigrams:
        if bigram[0]+" "+bigram[1] in text or bigram[1]+" "+bigram[0] in text:
            if(keywords == ""):
                keywords = bigram[0]+" "+bigram[1] 
            else:
                keywords = keywords + ", " + bigram[0]+" "+bigram[1] 
    texts.iloc[i,10] =keywords
print("bigrams done ....")

identify_threads = identify_threads(texts)
identify_threads.to_csv("threads.csv")
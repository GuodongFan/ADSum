import os
import json
import pandas as pd
import glob
import numpy as np
import time
import nltk
from nltk.tree import Tree
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import re
from pprint import pprint
from spellchecker import SpellChecker
from nltk.stem import WordNetLemmatizer
import time
import requests
from symspellpy.symspellpy import SymSpell, Verbosity
from tqdm import tqdm
import multiprocessing as mp

from multiprocessing import Pool
from multiprocessing import Process, Manager


# =======================================================================================
# Removing non-English words
def RemoveNonEnglishWords(sent):
    word_full = set(nltk.corpus.words.words())
    english_words = " ".join(w for w in nltk.wordpunct_tokenize(sent) \
                             if w.lower() in word_full)
    return english_words


# =======================================================================================
# SpellingChecker
max_edit_distance_dictionary = 1
prefix_length = 3
# create object
sym_spell = SymSpell(max_edit_distance_dictionary)
# load dictionary
dictionary_path = os.path.join("frequency_dictionary_en_82_765.txt")
term_index = 0  # column of the term in the dictionary text file
count_index = 1  # column of the term frequency in the dictionary text file
if not sym_spell.load_dictionary(dictionary_path, term_index, count_index):
    print("Dictionary file not found")


def segmentation(input_term):
    result = sym_spell.word_segmentation(input_term)
    return result.corrected_string


def spellChecker(input_term):
    # maximum edit distance per dictionary precalculation

    # max edit distance per lookup (per single word, not per whole input string)
    max_edit_distance_lookup = 1
    time.sleep(0.995)
    suggestions = sym_spell.lookup_compound(input_term, max_edit_distance_lookup)
    # display suggestion term, edit distance, and term frequency
    return suggestions[0].term


# =======================================================================================
# stop words removal
def RemoveStopWords(text):
    words = word_tokenize(text)
    stopWords = set(stopwords.words('english'))
    more_stop_words = (
    "could", "can", "cant", "yeah", "spec", "quo", "quot", "might", "and", "hey", "ill", "you", "someone", "would",
    "also")
    for w in more_stop_words:
        stopWords.add(w)
    stopWords = [re.sub("\'", "", word) for word in stopWords]
    wordsFiltered = []
    for w in words:
        if w not in stopWords:
            wordsFiltered.append(w)
    removed = ' '.join(wordsFiltered)
    return removed


# =======================================================================================
# Lemmatizer
def lemmatizer(text):
    sentence_words = word_tokenize(text)
    wordnet_lemmatizer = WordNetLemmatizer()
    punctuations = "?:!.,;"
    word_list = []
    for word in sentence_words:
        if word in punctuations:
            sentence_words.remove(word)
    for word in sentence_words:
        word_list.append(wordnet_lemmatizer.lemmatize(word, pos="v"))
    str1 = ' '.join(word_list)
    return str1


# =======================================================================================

def Preprocess(texts, p_id):
    t0 = time.time()
    # Convert to list
    data = texts.text.values.tolist()
    # print("data: ", len(data))
    # Remove Emails
    data = [re.sub('\S*@\S*\s?', '', str(html)) for html in data]
    # Remove new line characters
    data = [re.sub('\s+', ' ', html) for html in data]
    # remove URLs
    data = [re.sub('(?:(?:https|http|ftp)://)?\\w[\w-]*(?:\.[\w-]+)+\S*', '', html) for html in data]
    # Remove distracting single quotes
    data = [re.sub("\'", "", html) for html in data]
    # remove html tags
    data = [re.sub('```[^```]+?```', '', html) for html in data]
    data = [re.sub('<[^<]+?>', '', html) for html in data]
    # Remove punctuation and special characters
    data = [re.sub('[(/`.!@#?%&{\[\]}*$:’‘—”;)_+=\"-]', "", html) for html in data]
    data = [re.sub(',', " ", html) for html in data]
    data = [re.sub("&39", "", html) for html in data]
    data = [re.sub('<span datalinktypemention datascreenname', "", html) for html in data]
    data = [''.join(filter(lambda x: not x.isdigit(), sentence)) for sentence in data]
    # removing all words with less than 3 characters
    data = [re.sub(r'\b\w{1,2}\b', '', html) for html in data]
    data = [re.sub(' +', ' ', html) for html in data]
    data = [re.sub("[^a-zA-Z ]+", "", d) for d in data]
    t1 = time.time()
    print(p_id, "Preprocessing done....", (t1 - t0) / 60)
    data = [RemoveStopWords(d) for d in data]
    t2 = time.time()
    print(p_id, "RemoveStopWords done....", (t2 - t1) / 60)
    data = [spellChecker(d) for d in data]
    t3 = time.time()
    print(p_id, "SpellChecker done....", (t3 - t2) / 60)
    data = [lemmatizer(d) for d in data]
    t4 = time.time()
    print(p_id, "Lemmatizer done....", (t4 - t3) / 60)
    t6 = time.time()
    data = [re.sub(r'\b\w{1,2}\b', '', d) for d in data]
    data = [re.sub(' +', ' ', d) for d in data]
    data = [RemoveStopWords(d) for d in data]
    print(p_id, "RemoveStopWords done....", (time.time() - t6) / 60)
    print(p_id, "total time : ", (time.time() - t0) / 60)
    texts['clean'] = data
    texts.to_csv('cleaned_18_50.csv', mode='a', header=False)

    return data


def main():
    sub_texts = pd.read_csv("./data/test.csv") #./data/full_data_sample.csv
    #sub_texts = sub_texts[1700001:5000000]
    sub_texts = sub_texts[['id', 'text']]
    print("Data length: ", len(sub_texts))

    t_ = time.time()
    Preprocess(sub_texts, 0)
    print("Total Time : ", (time.time() - t_) / 60)


if __name__ == "__main__":
    main()

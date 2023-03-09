import pandas as pd
import numpy as np

def main():
    texts = pd.read_csv("./data/test.csv")
    clean = pd.read_csv("./data/cleaned_18_50.csv")


    clean.columns = ('idd', 'id', 'text', 'clean')
    clean = clean.drop('idd', 1)
    clean = clean.drop('text', 1)

    clean['id'] = clean['id'].apply(int)
    texts['id'] = texts['id'].apply(int)
    clean = pd.merge(texts, clean, how='inner', on='id', left_on=None, right_on=None, left_index=False, right_index=False,
             sort=True, suffixes=('_x', '_y'), copy=True, indicator=False, validate=None)

    clean.to_csv('./data/combined_cleaned_unlisted.csv')

if __name__ == "__main__":
    main()
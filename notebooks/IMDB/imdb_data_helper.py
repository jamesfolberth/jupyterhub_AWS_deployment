import os
import numpy as np
import pandas as pd

COLUMNS=['tconst', 'primaryTitle', 'genres', 'startYear']
NROWS=None # all rows

def have_title_basics():
    return os.path.isfile('title_basics_clean.csv')

def download_title_basics():
    if not os.path.isfile('title.basics.tsv'):
        os.system('wget https://datasets.imdbws.com/title.basics.tsv.gz && gunzip title.basics.tsv.gz')
    
    title_basics = pd.read_csv('title.basics.tsv', nrows=NROWS, sep='\t', index_col='tconst', usecols=COLUMNS)
    clean_genres = ~title_basics['genres'].str.contains('Adult').astype(np.bool)
    title_basics_clean = title_basics.loc[clean_genres]
    del title_basics # try to release memory
    title_basics_clean.to_csv('title_basics_clean.csv')

def get_title_basics():
    return pd.read_csv('title_basics_clean.csv', index_col='tconst')

def have_title_ratings():
    return os.path.isfile('title.ratings.tsv')

def download_title_ratings():
    os.system('wget https://datasets.imdbws.com/title.ratings.tsv.gz && gunzip title.ratings.tsv.gz')

def get_title_ratings():
    return pd.read_csv('title.ratings.tsv', sep='\t', index_col='tconst')

if __name__ == '__main__':
    pass
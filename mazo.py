#!/usr/bin/env python3

"""
Mazo is "mallet" in Spanish.

Mazo is a simple inteface MALLET, built on top of polite.

The user puts a corpus file in the corpus directory and names in in a special way:

    <keyword>-corpus.csv

<keyword> is a keyword used to name everything else.

To run Mazo the user does this:

    mazo.py <keyword> <k>

wher <k> stands for the number of topics in the model.

"""

import sys, os, re
from polite.polite import Polite


mallet_bin = 'mallet' # NEEDS TO BE CHANGED WITH ENV

# Get keyword
try:
    keyword = sys.argv[1]
except IndexError:
    print("Please provide a keyword for your corpus.")
    sys.exit()

# Get number of topics
try:
    n_topics = sys.argv[2]
except IndexError:
    print("No value provided for number of topics. Using 10.")
    n_topics = 10

# See if a corpus file exists. If not, complain.
corpus_file = "corpus/{}-corpus.csv".format(keyword)
if not os.path.isfile(corpus_file):
    print("Corpus file {} not found.".format(corpus_file))
    sys.exit()

# See if corpus file has been imported
mallet_file = "corpus/{}-corpus.mallet".format(keyword)
if not os.path.isfile(mallet_file):
    print("MALLET file {} not found. Creating it now.".format(mallet_file))
    cmd = "{} import-file --input {} --output {} --keep-sequence true --remove-stopwords true"\
        .format(mallet_bin, corpus_file, mallet_file)
    os.system(cmd)

# if not os.path.isfile():
#     try:
#         os.mkdir(tables_dir)
#     except FileExistsError:
#         pass


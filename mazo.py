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
mallet_output_dir = './output'

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
    print("Done creating MALLET file.")

# Make sure output directory exists
if not os.path.isfile(mallet_output_dir):
    try:
        os.mkdir(mallet_output_dir)
    except FileExistsError:
        pass

if not os.path.isfile('{}/{}'.format(mallet_output_dir, keyword)):
    try:
        os.mkdir('{}/{}'.format(keyword))
    except FileExistsError:
        pass

# Run the topic model
print("Running topic model.")
# Eventually provide ways to override these defaults
trial_key = os.utime()
mallet_trial_dir = "{}/{}-{}".format(mallet_output_dir, keyword, trial_key)
params = {
    'num-topics': n_topics,
    'num-top-words': 10,
    'num-iterations': 1000,
    'optimize-interval': 100,
    'num-threads': 4,
    'num-top-docs': 5,
    'doc-topics-max': 10,
    'show-topics-interval': 100,
    'input': mallet_file,
    'output-topic-keys': '{}/topic-keys.txt'.format(mallet_trial_dir),
    'output-doc-topics': '{}/doc-topics.txt'.format(mallet_trial_dir),
    'word-topic-counts-file': '{}/word-topic-counts.txt'.format(mallet_trial_dir),
    'topic-word-weights-file': '{}/topic-word-weights.txt'.format(mallet_trial_dir),
    'xml-topic-report': '{}/topic-report.xml'.format(mallet_trial_dir),
    'xml-topic-phrase-report': '{}/topic-phrase-report.xml'.format(mallet_trial_dir),
    'diagnostics-file': '{}/diagnostics.xml'.format(mallet_trial_dir),
    'output-state': '{}/output-state.gz'.format(mallet_trial_dir)
}
cmds = []
for k, v in params.items():
    cmds.append("--{} {}".format(k, v))
train_cmd = "{} train-topics ".format(mallet_bin) + ' '.join(cmds)
print("Command to be executed.")
print(train_cmd)
os.system(train_cmd)
print("Done with training model.")

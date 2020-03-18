#! /usr/bin/env python3

import os

# Put in a config?
python = 'python3'
import_config_file = 'config-import-file.txt'
train_config_file = 'config-train-topics.txt'

cmds = [
    "mallet import-file --config {}".format(import_config_file),
    "mallet train-topics --config {}".format(train_config_file),
    "{} polite.py".format(python)
]
print("Importing corpus: {}".format(cmds[0]))
os.system(cmds[0])
print("Training model: {}".format(cmds[1]))
os.system(cmds[1])
print("Creating tables: {}".format(cmds[2]))
os.system(cmds[2])
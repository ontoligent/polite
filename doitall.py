#! /usr/bin/env python3

import os

# Put in a config
python = 'python3'
import_config_file = 'config-import-file.txt'
train_config_file = 'config-train-topics.txt'

print("Importing corpus")
os.system("mallet import-file --config {}".format(import_config_file))
print("Training model")
os.system("mallet train-topics --config {}".format(train_config_file))
print("Creating tables")
os.system("{} mallet2db.py".format(python))

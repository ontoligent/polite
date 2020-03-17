import sys, os, re
from polite.polite import Polite

default_config_file = './config-train-topics.txt'
default_tables_dir = './tables/'

try:
    train_config_file = sys.argv[1]
except IndexError as e:
    print("Using default config file.")
    train_config_file = default_config_file

try:
    tables_dir = sys.argv[2]
except IndexError as e:
    print("Using default tables dir.")
    tables_dir = default_tables_dir

if not re.match('/$', tables_dir):
    tables_dir + '/'

print("Using config file \"{}\" and tables dir \"{}\"."\
      .format(train_config_file, tables_dir))

p = Polite(train_config_file, tables_dir)
p.do_all()
print("Done.")
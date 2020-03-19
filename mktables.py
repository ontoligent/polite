import sys, os, re
from polite.polite import Polite

default_config_file = './config-train-topics.txt'
default_tables_dir = './tables/'

try:
    train_config_file = sys.argv[1]
except IndexError:
    print("Using default config file.")
    train_config_file = default_config_file

try:
    tables_dir = sys.argv[2]
except IndexError:
    print("Using default tables dir.")
    tables_dir = default_tables_dir

if not re.search(r'/$', tables_dir):
    tables_dir = tables_dir + '/'

print(tables_dir)

if not os.path.isfile(tables_dir):
    try:
        os.mkdir(tables_dir)
    except FileExistsError:
        pass

print("Using config file \"{}\" and tables dir \"{}\"."\
      .format(train_config_file, tables_dir))

p = Polite(train_config_file, tables_dir)
p.do_all()

print("Done.")
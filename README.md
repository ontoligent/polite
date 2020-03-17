# polite

Polite is a lite version of Polo.

# Instructions

1. Install MALLET.
  * Go [here](http://mallet.cs.umass.edu/download.php) to download MALLET. Follow the installation instructions.
2. Get a corpus file to model.
  * There is a sample one to start with, in the `/corpus` directory.
3. Create the config files. Samples are included; these can be used as templates to work with other corpora and to generate other models.
  * `config-import-file.txt`
  * `config-train-topics.txt`
4. Run MALLET to import corpus. You need to do this only once per corpus.
  * `mallet import-file --config config-import-file.txt`
5. Run MALLET to train topic model. Do this for as many models as you want to create, using a different config file for each. In each file, be sure to use different output directories. 
  * `mallet train-topics --config config-train-topics.txt`
6. Run `mallet2db.py` to create tables.
  * `python polite.py`
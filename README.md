# Polite

Polite is a lite version of <a href="https://github.com/ontoligent-design/polo2" target="_blank">Polo</a>. The main function Polite performs is to convert MALLET's topic model output data into tables that can be used a unified data model. 

# Instructions

1. Install MALLET.
  * Make sure Java is installed on your computer.
  * Go [here](http://mallet.cs.umass.edu/download.php) to download MALLET. Follow the installation instructions.
2. Get a corpus file to model.
  * See the MALLET website for instructions on the format of this file. Essentially, it's a CSV with two or three items per row: a document ID, an optional label, and the document itself. In other words, it roughly conforms to F1 form of text data. 
  * There is a sample corpus to start with, in the `/corpus` directory. You can add your own. 
3. Create the config files. Samples are included; these can be used as templates to work with other corpora and to generate other models.
  * `config-import-file.txt`
  * `config-train-topics.txt`
4. Create any new directories that are referenced in the config files, such as the output directory for the files MALLET generates.
4. Run MALLET to import the corpus, that is, to convert the CSV into a special file that MALLET wants to work with. You need to do this only once per corpus. For example, using the example config:
  * `mallet import-file --config config-import-file.txt`
5. Run MALLET to train topic model. Do this for as many models as you want to create, using a different config file for each. In each file, be sure to use different output directories. For example, using the example config: 
  * `mallet train-topics --config config-train-topics.txt`
6. Run `mktables.py` to create tables, with arguments for the configuration file and the output directory for the tables.
  * `python mktables.py <CONFIGFILE> <TABLEDIR>`

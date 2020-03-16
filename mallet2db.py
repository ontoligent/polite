import os
import time
import re
import pandas as pd
from itertools import combinations
from lxml import etree
from scipy import stats

class Mallet2Db():

    def __init__(self, config_file, tables_dir='./'):
        """Initialize MALLET with trial name""" 
        self.config_file = config_file
        self.tables_dir = tables_dir
        self.config = {}
        with open(self.config_file, 'r') as cfg:
            for line in cfg.readlines():
                if not re.match(r'^#', line):
                    a, b = line.split()
                    if re.match(r'^\d+$', b):
                        b = int(b)
                    elif re.match(r'TRUE', b):
                        b = True
                    elif re.match(r'FALSE', b):
                        b = False
                    self.config[a] = b

    def import_table_state(self):
        """Import the state file into docword table"""
        src_file = self.config['output-state']
        import gzip
        with gzip.open(src_file, 'rb') as f:
            docword = pd.DataFrame(
                [line.split() for line in f.readlines()[3:]],
                columns=['doc_id', 'src', 'word_pos', 'word_id', 'word_str', 'topic_id'])
            docword = docword[['doc_id', 'word_id', 'word_pos', 'topic_id']]
            docword = docword.astype('int')
            docword.set_index(['doc_id', 'word_id'], inplace=True)
            docword.to_csv(self.tables_dir + 'DOCWORD.csv')

    def import_table_topic(self):
        """Import data into topic table"""
        src_file = self.config['output-topic-keys']
        topic = pd.read_csv(src_file, sep='\t', header=None, index_col=False,
                            names=['topic_id', 'topic_alpha', 'topic_words'])
        topic.set_index('topic_id', inplace=True)
        topic['topic_alpha_zscore'] = stats.zscore(topic.topic_alpha)
        topic['topic_gloss'] = 'TBA'
        topic.to_csv(self.tables_dir + 'TOPIC.csv')

    def import_tables_topicword_and_word(self):
        """Import data into topicword and word tables"""
        src_file = self.config['word-topic-counts-file']
        WORD = []
        TOPICWORD = []
        with open(src_file, 'r') as src:
            for line in src.readlines():
                row = line.strip().split()
                (word_id, word_str) = row[0:2]
                WORD.append((int(word_id), word_str))
                for item in row[2:]:
                    (topic_id, word_count) = item.split(':')
                    TOPICWORD.append((int(word_id), int(topic_id), int(word_count)))
        word = pd.DataFrame(WORD, columns=['word_id', 'word_str'])
        topicword = pd.DataFrame(TOPICWORD, columns=['word_id', 'topic_id', 'word_count'])
        word.set_index('word_id', inplace=True)
        topicword.set_index(['word_id', 'topic_id'], inplace=True)
        word.to_csv(self.tables_dir + 'VOCAB.csv')
        topicword.to_csv(self.tables_dir + 'TOPICWORD.csv')

    def import_table_doctopic(self):
        """Import data into doctopic table"""
        src_file = self.config['output-doc-topics']
        doctopic = pd.read_csv(src_file, sep='\t', header=None)
        doc = pd.DataFrame(doctopic.iloc[:, 1])
        doc.columns = ['doc_tmp']
        doc['src_doc_id'] = doc.doc_tmp.apply(lambda x: int(x.split(',')[0]))
        doc['doc_label'] = doc.doc_tmp.apply(lambda x: x.split(',')[1])
        doc = doc[['src_doc_id', 'doc_label']]
        doc.index.name = 'doc_id' 
        doctopic.drop(1, axis = 1, inplace=True)
        doctopic.rename(columns={0:'doc_id'}, inplace=True)
        y = [col for col in doctopic.columns[1:]]
        doctopic_narrow = pd.lreshape(doctopic, {'topic_weight': y})
        doctopic_narrow['topic_id'] = [i for i in range(self.config['num-topics'])
                                        for doc_id in doctopic['doc_id']]
        doctopic_narrow = doctopic_narrow[['doc_id', 'topic_id', 'topic_weight']]
        doctopic_narrow.set_index(['doc_id', 'topic_id'], inplace=True)
        doctopic_narrow['topic_weight_zscore'] = stats.zscore(doctopic_narrow.topic_weight)
        dtm = doctopic_narrow.reset_index()\
            .set_index(['doc_id','topic_id'])['topic_weight'].unstack()
        dtm.to_csv(self.tables_dir + 'DOCTOPIC.csv')
        doc.to_csv(self.tables_dir + 'DOC.csv')
        doctopic_narrow.to_csv(self.tables_dir + 'DOCTOPIC_NARROW.csv')

    def import_table_topicphrase(self):
        """Import data into topicphrase table"""
        src_file = self.config['xml-topic-phrase-report']
        TOPICPHRASE = []
        tree = etree.parse(src_file)
        for topic in tree.xpath('/topics/topic'):
            topic_id = int(topic.xpath('@id')[0])
            for phrase in topic.xpath('phrase'):
                phrase_weight = float(phrase.xpath('@weight')[0])
                phrase_count = int(phrase.xpath('@count')[0])
                topic_phrase = phrase.xpath('text()')[0]
                TOPICPHRASE.append((topic_id, topic_phrase, phrase_weight, phrase_count))
        topicphrase = pd.DataFrame(TOPICPHRASE, columns=['topic_id', 'topic_phrase',
                                                         'phrase_weight', 'phrase_count'])
        topicphrase.set_index(['topic_id', 'topic_phrase'], inplace=True)
        topicphrase.to_csv(self.tables_dir + 'TOPICPHRASE.csv')

    def add_topic_glosses(self):
        """Add glosses to topic table"""
        topicphrase = pd.read_csv(self.tables_dir + 'TOPICPHRASE.csv',
                                  index_col=['topic_id','topic_phrase'])
        topic = pd.read_csv(self.tables_dir + 'TOPIC.csv', index_col='topic_id')
        topic['topic_gloss'] = topicphrase['phrase_weight'].unstack().idxmax(1)
        topic.to_csv(self.tables_dir + 'TOPIC.csv')

    def add_diagnostics(self):
        """Add diagnostics data to topics and topicword_diags tables"""
        src_file = self.config['diagnostics-file']
        TOPIC = []
        TOPICWORD = []
        tkeys = ['id', 'tokens', 'document_entropy', 'word-length', 'coherence',
                 'uniform_dist', 'corpus_dist',
                 'eff_num_words', 'token-doc-diff', 'rank_1_docs',
                 'allocation_ratio', 'allocation_count',
                 'exclusivity']
        tints = ['id', 'tokens']
        wkeys = ['rank', 'count', 'prob', 'cumulative', 'docs', 'word-length', 'coherence',
                 'uniform_dist', 'corpus_dist', 'token-doc-diff', 'exclusivity']
        wints = ['rank', 'count', 'docs', 'word-length']
        tree = etree.parse(src_file)
        for topic in tree.xpath('/model/topic'):
            tvals = []
            for key in tkeys:
                xpath = '@{}'.format(key)
                if key in tints:
                    tvals.append(int(float(topic.xpath(xpath)[0])))
                else:
                    tvals.append(float(topic.xpath(xpath)[0]))
            TOPIC.append(tvals)
            for word in topic.xpath('word'):
                wvals = []
                topic_id = tvals[0]  # Hopefully
                wvals.append(topic_id)
                word_str = word.xpath('text()')[0]
                wvals.append(word_str)
                for key in wkeys:
                    xpath = '@{}'.format(key)
                    if key in wints:
                        wvals.append(int(float(word.xpath(xpath)[0])))
                    else:
                        wvals.append(float(word.xpath(xpath)[0]))
                TOPICWORD.append(wvals)
        tkeys = ['topic_{}'.format(re.sub('-', '_', k)) for k in tkeys]
        wkeys = ['topic_id', 'word_str'] + wkeys
        wkeys = [re.sub('-', '_', k) for k in wkeys]
        topic_diags = pd.DataFrame(TOPIC, columns=tkeys)
        topic_diags.set_index('topic_id', inplace=True)
        topics = pd.read_csv(self.tables_dir + 'TOPIC.csv', index_col='topic_id')
        topics = pd.concat([topics, topic_diags], axis=1)
        topics.to_csv(self.tables_dir + 'TOPIC.csv')
        topicword_diags = pd.DataFrame(TOPICWORD, columns=wkeys)
        topicword_diags.set_index(['topic_id', 'word_str'], inplace=True)
        word = pd.read_csv(self.tables_dir + 'VOCAB.csv')
        word.set_index('word_str', inplace=True)
        topicword_diags = topicword_diags.join(word, how='inner')
        topicword_diags.reset_index(inplace=True)
        topicword_diags.set_index(['topic_id', 'word_id'], inplace=True)
        topicword_diags.to_csv(self.tables_dir + 'TOPICWORD_DIAGS.csv')


if __name__ == '__main__':

    import sys

    train_config_file = 'config-train-topics.txt'
    tables_dir = './tables/'
    if not os.path.exists(tables_dir):
        os.mkdir(tables_dir)

    m2d = Mallet2Db(train_config_file, tables_dirdir=tables_dir)
    m2d.import_table_state()
    m2d.import_table_topic()
    m2d.import_tables_topicword_and_word()
    m2d.import_table_doctopic()
    m2d.import_table_topicphrase()
    m2d.add_diagnostics()
    m2d.add_topic_glosses()
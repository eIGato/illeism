#!/urs/bin/env python

from argparse import ArgumentParser
import logging

from nltk import sent_tokenize, word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer
import psycopg2


logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

# This part-of-speech map does not include articles and particles
pos_map = {
    'CD': 'n',
    'EX': 'v',
    'JJ': 'a',
    'JJR': 'a',
    'JJS': 'a',
    'MD': 'v',
    'NN': 'n',
    'NNS': 'n',
    'NNP': 'n',
    'NNPS': 'n',
    'PRP': 'n',
    'PRP$': 'a',
    'RB': 'r',
    'RBR': 'r',
    'RBS': 'r',
    'UH': 'n',
    'VB': 'v',
    'VBD': 'v',
    'VBG': 'v',
    'VBN': 'v',
    'VBP': 'v',
    'VBZ': 'v',
    'WDT': 'a',
    'WP': 'n',
    'WP': 'a',
    'WRB': 'r',
}


class Word():
    _all = []

    def __init__(self, name, quantity=0):
        if name not in self._all:
            self._all.append(name)
        self.id = self._all.index(name)
        self.name = name
        self.quantity = quantity
        self.wiss = BagOfWords()  # Bag of words met in same sentences

    def __lt__(self, value):
        if self.quantity == value.quantity:
            return self.id < value.id
        return self.quantity > value.quantity

    def __str__(self):
        return '{:8s}: {}'.format(self.name, self.quantity)


class BagOfWords():
    def __init__(self):
        self._bow = {}
        self.keys = self._bow.keys
        self.values = self._bow.values

    def add(self, word, quantity=1, wiss=None):
        if word in self._bow:
            self._bow[word].quantity += quantity
        else:
            self._bow[word] = Word(word, quantity)
        if wiss:
            self._bow[word].wiss.merge(wiss, exclude=word)

    def merge(self, bag, exclude=None):
        for word in bag.values():
            if word.name != exclude:
                self.add(word.name, word.quantity, word.wiss)

    def sorted(self):
        return sorted(self.values())

    def in_same_sentence(self, username):
        wiss = self._bow[username].wiss.keys()
        bag = BagOfWords()
        for word in self.values():
            if word.name in wiss:
                bag.add(word.name, word.quantity)
        return bag


def read_users(db):
    if not db:
        return {line.strip(): hash(line) for line in open('user.example.txt').readlines()}
    cur = psycopg2.connect(db).cursor()
    cur.execute('SELECT name, id from user')
    rows = cur.fetchall()
    return dict(rows)


def main():
    parser = ArgumentParser()
    parser.add_argument('filename', help='path to textfile.txt (default: STDIN).', default='/dev/stdin')
    parser.add_argument('--db', help='datebase connection params.', default=None)
    args = parser.parse_args()
    users = read_users(args.db)

    text = open(args.filename).read()
    sentences = sent_tokenize(text)
    bag = BagOfWords()
    lemmatizer = WordNetLemmatizer()
    for sentence in sentences:
        bag_s = BagOfWords()
        words = word_tokenize(sentence)
        for word, tag in pos_tag(words):
            if word.isalnum() and tag in pos_map:
                bag_s.add(lemmatizer.lemmatize(word, pos=pos_map[tag]))
        for word in bag_s.values():
            if word.name in users:
                word.wiss.merge(bag_s, exclude=word.name)
        bag.merge(bag_s)

    owner = None
    owner_words = []
    bag_sorted = bag.sorted()
    for word in bag_sorted:
        if word.name in users:
            owner = {word.name: users[word.name]}
            owner_words = word.wiss.keys()
            break
    logger.info('File owner is {}'.format(owner))

    logger.info('\nTop 10 popular words:')
    for word in bag_sorted[:10]:
        logger.info(word)

    if not owner:
        return
    logger.info('\nTop 5 popular owner words:')
    i = 0
    for word in bag_sorted:
        if word.name in owner_words:
            i += 1
            logger.info(word)
        if i >= 5:
            break


if __name__ == '__main__':
    main()

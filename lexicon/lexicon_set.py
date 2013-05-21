__author__ = 'Jacky'

global_set = {}


def read_lexicon(filename):
    global global_set
    with open(filename, 'r') as dictionary:
        global_set = {word.strip() for word in dictionary.readlines()}
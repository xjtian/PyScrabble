__author__ = 'Jacky'

global_set = {}


def read_lexicon(filename):
    try:
        global global_set
        with open(filename, 'r') as dictionary:
            global_set = {word[:-1] for word in dictionary.readlines()}
    except IOError:
        pass
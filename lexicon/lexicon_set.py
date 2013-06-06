__author__ = 'Jacky'


def read_lexicon(filename):
    """
    Read a lexicon from a file into a native Python set. Returns the set.
    """
    with open(filename, 'r') as dictionary:
        lex_set = {word.strip() for word in dictionary.readlines()}

    return lex_set
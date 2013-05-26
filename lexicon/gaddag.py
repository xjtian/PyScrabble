__author__ = 'Jacky'

from lexicon.settings import WORDLIST_PATH, GADDAG_PICKLE_PATH
import cPickle as Pickle


class GaddagState(object):
    """
    A state (node) in a GADDAG. Each state contains a letter set (the set of
    letters which, if encountered next, make a word) and the arcs leading out
    of it and their corresponding letters.
    """

    def __init__(self):
        self.arcs = dict()
        self.letter_set = set()

    def add_arc(self, char):
        """
        Add an arc from the current state for char if no such arc exists.
        Returns the node this arc leads to.
        """
        if char in self.arcs:
            next_state = self.arcs[char]
        else:
            next_state = GaddagState()
            self.arcs[char] = next_state

        return next_state

    def add_final_arc(self, c1, c2):
        """
        Add an arc from the current state for c1 if no such arc exists and adds
        c2 to the letter set at that state. Returns the node this arc leads to.
        """
        if c1 in self.arcs:
            next_state = self.arcs[c1]
        else:
            next_state = GaddagState()
            self.arcs[c1] = next_state

        next_state.letter_set.add(c2)
        return next_state

    def force_arc(self, char, forced_state):
        """
        Add an arc from the current state for char to forced_state, raising an
        exception if an arc for char already exists going to any other state.
        """
        if char in self.arcs:
            if not self.arcs[char] == forced_state:
                raise Exception('Arc for forced character already exists.')

        self.arcs[char] = forced_state


class Gaddag(object):
    """
    A partially-minimized GADDAG structure to represent a lexicon as described
    in Steven Gordon's 1994 paper 'A Faster Scrabble Move Generation Algorithm'.
    """

    def __init__(self):
        self.root = GaddagState()

    def add_word(self, word):
        """
        Add a word to the GADDAG and partially minimize the resulting structure.
        """
        n = len(word)

        state = self.root   # create path for n...1
        for i in xrange(n - 1, 1, -1):
            state = state.add_arc(word[i])
        state.add_final_arc(word[1], word[0])

        state = self.root   # create path for n-1...1|n
        for i in xrange(n - 2, -1, -1):
            state = state.add_arc(word[i])
        state = state.add_final_arc('|', word[-1])

        # partially minimize the remaining paths
        for m in xrange(n - 3, -1, -1):
            forced_state = state
            state = self.root
            for i in xrange(m, -1, -1):
                state = state.add_arc(word[i])
            state = state.add_arc('|')
            state.force_arc(word[m + 1], forced_state)

    def is_word(self, word):
        """
        Determines if the given word is in the lexicon represented by the
        GADDAG. Returns True if the word exists, False otherwise.
        """
        cur_state = self.root
        for letter in word[:0:-1]:
            if not letter in cur_state.arcs:
                return False
            cur_state = cur_state.arcs[letter]

        return word[0] in cur_state.letter_set

    def cross_sets(self, word):
        """
        Returns the left and right cross-sets for the given string or word.

        Parameters:
            word:
                The word/string/subword to compute cross-sets for.

        Returns:
            (left, right):
                Tuple of two sets of letters where left is the left
                cross-set for the word and right is the right cross-set.
        """
        cur_state = self.root
        for letter in word[::-1]:
            if not letter in cur_state.arcs:
                return set(), set()
            cur_state = cur_state.arcs[letter]

        if '|' in cur_state.arcs:
            d_state = cur_state.arcs['|']
            return cur_state.letter_set, d_state.letter_set
        else:
            return cur_state.letter_set, set()

    def mid_set(self, prefix, suffix):
        """
        Returns the middle cross-set for the given prefix and suffix. In
        other words, the set of letters such that prefix-l-suffix is a word.

        Parameters:
            prefix:
                The prefix to compute the mid-set for.
            suffix:
                The accompanying suffix for the mid-set.

        Returns:
            The middle crossing-set for the prefix and suffix.
        """
        cur_state = self.root
        for letter in suffix[::-1]:
            if not letter in cur_state.arcs:
                return set()
            cur_state = cur_state.arcs[letter]

        letter_set = set()
        for k, v in cur_state.arcs.iteritems():
            for letter in prefix[:0:-1]:
                if not letter in v.arcs:
                    break
                v = v.arcs[letter]
            else:
                if prefix[0] in v.letter_set:
                    letter_set.add(k)

        return letter_set


gaddag = Gaddag()


def gaddag_from_file():
    """
    Create a GADDAG from a text file of a lexicon given by the WORDLIST_PATH
    setting. The text file should only have the words in the lexicon, one per
    line, with a blank line at the very end. The created GADDAG will be in the
    'gaddag' module variable.
    """
    global gaddag
    try:
        with open(WORDLIST_PATH, 'r') as f:
            for word in f.readlines():
                gaddag.add_word(word[:-1])  # Chop the newline
    except IOError:
        pass


def unpickle_gaddag():
    """
    Unpickle a GADDAG from the GADDAG_PICKLE_PATH setting. The unpickled
    GADDAG will be in the 'gaddag' module variable.
    """
    global gaddag
    try:
        with open(GADDAG_PICKLE_PATH, 'r') as f:
            gaddag = Pickle.load(f)
    except IOError:
        pass
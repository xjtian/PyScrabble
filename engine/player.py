__author__ = 'Jacky'

from collections import Counter


class Player(object):
    def __init__(self, name):
        self.name = name

        self.score = 0
        self.rack = []

    def valid_play(self, letters):
        """
        Returns the way the given letters to be played are played from the
        player's rack. If a blank is used, the corresponding letter is
        replaced with a lowercase one. If the play is not possible, an empty
        list is returned.

        Note that this method will put off using a blank until the last
        possible letter.
        """
        llist = list(letters)
        counter = dict(Counter(self.rack))

        for i, letter in enumerate(letters):
            if not counter.get(letter, 0) and not counter.get(' ', 0):
                return []
            elif not counter.get(letter, 0) and counter[' ']:   # Use a blank
                counter[' '] -= 1
                llist[i] = llist[i].lower()
            else:   # Letter exists on the rack
                counter[letter] -= 1

        return llist

    def use_letters(self, letters):
        for i, letter in enumerate(letters):
            if letter not in self.rack:
                self.rack.pop(self.rack.index(' '))
            else:
                self.rack.pop(self.rack.index(letter))

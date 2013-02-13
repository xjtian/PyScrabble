__author__ = 'Jacky'


class Player(object):
    def __init__(self, name):
        self.name = name

        self.score = 0
        self.rack = []

    def valid_play(self, letters):
        blank_count = self.rack.count(' ')
        llist = list(letters)

        for i, letter in enumerate(letters):
            if letter not in self.rack:
                if blank_count:
                    blank_count -= 1
                    llist[i] = llist[i].lower()     # Use a blank
                else:
                    return []

        return llist

    def use_letters(self, letters):
        for i, letter in enumerate(letters):
            if letter not in self.rack:
                self.rack.pop(self.rack.index(' '))
            else:
                self.rack.pop(self.rack.index(letter))

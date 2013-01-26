__author__ = 'Jacky'

default_board = [
    list('#..2...#...2..#'),
    list('.@...3...3...@.'),
    list('..@...2.2...@..'),
    list('2..@...2...@..2'),
    list('....@.....@....'),
    list('.3...3...3...3.'),
    list('..2...2.2...2..'),
    list('#..2...*...2..#'),
    list('..2...2.2...2..'),
    list('.3...3...3...3.'),
    list('....@.....@....'),
    list('2..@...2...@..2'),
    list('..@...2.2...@..'),
    list('.@...3...3...@.'),
    list('#..2...#...2..#')
]

word_multipliers = {'#': 3, '@': 2, '*': 2, '.': 1}
letter_multipliers = {'3': 3, '2': 2, '.': 1}

empty_locations = ['#', '@', '.', '3', '2', '*']

class BoardPosition(object):
    def __init__(self, letter, pos):
        self.pos = pos
        self.letter = letter
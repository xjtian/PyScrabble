__author__ = 'Jacky'

from engine.board import BoardPosition

class Move(object):
    def __init__(self):
        self.positions = []
        self.horizontal = True
        self.score = 0

        self.drawn = []

    def add_letter(self, letter, pos):
        self.positions.append(BoardPosition(letter, pos))

    def sort_letters(self):
        self.positions.sort(key=lambda bp: bp.pos[self.horizontal])
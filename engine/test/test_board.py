__author__ = 'Jacky'

import unittest
from engine.board import default_board, empty_locations


class TestBoard(unittest.TestCase):
    def test_board_dimensions(self):
        # Make sure the board is square
        self.assert_(all([len(row) == len(default_board[0]) for row in default_board]))

    def test_board_emptiness(self):
        # Make sure default board is totally empty
        for row in default_board:
            for letter in row:
                self.assertIn(letter, empty_locations)
__author__ = 'Jacky'

import unittest
from engine.board import *


class TestBoard(unittest.TestCase):
    def test_board_dimensions(self):
        # Make sure the board is square
        self.assert_(all([len(row) == len(default_board[0]) for row in default_board]))

    def test_board_emptiness(self):
        # Make sure default board is totally empty
        for row in default_board:
            for letter in row:
                self.assertIn(letter, empty_locations)


class TestPrefixSuffix(unittest.TestCase):
    def setUp(self):
        self.board = [
            list('.....'),
            list('.....'),
            list('.....'),
            list('.....'),
            list('.....')
        ]

    def test_get_prefix(self):
        # No prefix
        board = [
            list('..B..'),
            list('.....'),
            list('B.A.B'),
            list('.....'),
            list('..B..')
        ]

        self.assertEqual('', get_prefix(board, 2, 2, True))
        self.assertEqual('', get_prefix(board, 2, 2, False))

        # Simple prefix
        board = [
            list('.....'),
            list('...B.'),
            list('...B.'),
            list('.BBA.'),
            list('.....')
        ]

        self.assertEqual('BB', get_prefix(board, 3, 3, True))
        self.assertEqual('BB', get_prefix(board, 3, 3, False))

        # Prefix all the way to end of board and around
        board = [
            list('..B..'),
            list('..B..'),
            list('BBA.B'),
            list('.....'),
            list('..B..')
        ]

        self.assertEqual('BB', get_prefix(board, 2, 2, True))
        self.assertEqual('BB', get_prefix(board, 2, 2, False))

    def test_get_suffix(self):
        # No suffix
        board = [
            list('..B..'),
            list('.....'),
            list('B.A.B'),
            list('.....'),
            list('..B..')
        ]

        self.assertEqual('', get_suffix(board, 2, 2, True))
        self.assertEqual('', get_suffix(board, 2, 2, False))

        # Simple suffix
        board = [
            list('.....'),
            list('.ABB.'),
            list('.B...'),
            list('.B...'),
            list('.....')
        ]

        self.assertEqual('BB', get_suffix(board, 1, 1, True))
        self.assertEqual('BB', get_suffix(board, 1, 1, False))

        # Suffix all the way to end of board and around
        board = [
            list('..B..'),
            list('.....'),
            list('B.ABB'),
            list('..B..'),
            list('..B..')
        ]

        self.assertEqual('BB', get_suffix(board, 2, 2, True))
        self.assertEqual('BB', get_suffix(board, 2, 2, False))


class TestBoardPosition(unittest.TestCase):
    def test_equality(self):
        a = BoardPosition('A', (0, 1))
        b = BoardPosition('A', (0, 1))

        self.assert_(a == b)
        self.assert_(a == a)
        self.assert_(b == b)

        b = BoardPosition('B', (0, 0))

        self.assert_(not a == b)

    def test_hash(self):
        a = BoardPosition('A', (0, 1))
        b = BoardPosition('A', (0, 1))

        self.assert_(hash(a) == hash(b))

        b = BoardPosition('B', (0, 0))

        self.assert_(hash(a) != hash(b))

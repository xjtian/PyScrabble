__author__ = 'Jacky'

import unittest
from copy import deepcopy

from strategy.strategies import *
from engine.game import ScrabbleGame


class TestStrategyBase(unittest.TestCase):
    def setUp(self):
        self.game = ScrabbleGame(wordlist='./wordlists/empty_list.txt')
        self.board = [
            list('.....'),
            list('.....'),
            list('.....'),
            list('.....'),
            list('.....')
        ]

        self.game.board = deepcopy(self.board)
        self.strategy = StrategyBase(self.game)

    def test_find_anchors_empty(self):
        """
        Test case with only one letter on the whole board at a time.
        """
        # Regular test case with letter in the middle of the board
        self.game.board[2][2] = 'A'

        expected = {(1, 2), (3, 2), (2, 1), (2, 3)}
        self.assertEqual(expected, self.strategy.find_anchors())

        self.__reset_anchor_tests()
        # Letter on top edge so no upper tile exists
        self.game.board[0][2] = 'A'
        expected = {(0, 1), (0, 3), (1, 2)}
        self.assertEqual(expected, self.strategy.find_anchors())

        self.__reset_anchor_tests()
        # Letter on bottom edge so no lower tile exists
        self.game.board[4][2] = 'A'
        expected = {(3, 2), (4, 1), (4, 3)}
        self.assertEqual(expected, self.strategy.find_anchors())

        self.__reset_anchor_tests()
        # Letter on right edge so no right tile exists
        self.game.board[2][4] = 'A'
        expected = {(1, 4), (3, 4), (2, 3)}
        self.assertEqual(expected, self.strategy.find_anchors())

        self.__reset_anchor_tests()
        # Letter on left edge so no left tile exists
        self.game.board[2][0] = 'A'
        expected = {(1, 0), (3, 0), (2, 1)}
        self.assertEqual(expected, self.strategy.find_anchors())

    def test_find_anchors_occupied(self):
        """
        Test cases with tiles next to each other.
        """
        # Two tiles next to each other horizontally
        self.game.board[2][2] = 'A'
        self.game.board[2][3] = 'B'

        expected = {(2, 1), (1, 2), (1, 3), (2, 4), (3, 3), (3, 2)}
        self.assertEqual(expected, self.strategy.find_anchors())

        # Two tiles next to each other vertically
        self.__reset_anchor_tests()
        self.game.board[2][2] = 'A'
        self.game.board[1][2] = 'B'

        expected = {(0, 2), (1, 3), (2, 3), (3, 2), (2, 1), (1, 1)}
        self.assertEqual(expected, self.strategy.find_anchors())

        # 5 tiles arranged in a plus
        self.__reset_anchor_tests()
        self.game.board[2][2] = 'A'
        self.game.board[1][2] = 'B'
        self.game.board[3][2] = 'B'
        self.game.board[2][1] = 'C'
        self.game.board[2][3] = 'C'

        expected = {(1, 1), (0, 2), (1, 3), (2, 4), (3, 3), (4, 2), (3, 1), (2, 0)}
        self.assertEqual(expected, self.strategy.find_anchors())

    def test_find_anchors_realistic(self):
        """
        A slightly more realistic (game-like) test case.
        """
        self.game.board = [
            list('.....'),
            list('..B..'),
            list('ABCD.'),
            list('B.DEA'),
            list('C....')
        ]

        expected = {(1, 0), (1, 1), (0, 2), (1, 3), (2, 4), (3, 1), (4, 1), (4, 2), (4, 3), (4, 4)}
        self.assertEqual(expected, self.strategy.find_anchors())

    def __reset_anchor_tests(self):
        self.game.board = deepcopy(self.board)
        self.strategy.anchors = set()
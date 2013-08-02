__author__ = 'Jacky'

import unittest

from strategy.strategies import StaticScoreStrategy
from engine.game import ScrabbleGame
from engine.move import Move
from engine.board import BoardPosition


class StaticScoreTest(unittest.TestCase):
    def setUp(self):
        game = ScrabbleGame(wordlist='./wordlists/ABBA.txt', read_gaddag=True)
        self.strategy = StaticScoreStrategy(game)

    def test_constructor(self):
        self.assertEqual(-1, self.strategy.a_x)
        self.assertEqual(-1, self.strategy.a_y)

    def test_move_open(self):
        """
        Test cases for generating opening move.
        """
        self.strategy.a_x, self.strategy.a_y = (7, 7)
        rack = ['A', 'A']

        m = Move()
        moves = self.strategy.move_finder(0, m, rack, self.strategy.game.gaddag.root)

        m1 = Move()
        m1.positions = [BoardPosition('A', (7, 7)), BoardPosition('A', (7, 8))]

        m2 = Move()
        m2.positions = [BoardPosition('A', (7, 6)), BoardPosition('A', (7, 7))]

        expected = {m1, m2}
        self.assertEqual(expected, moves)

        m = Move()
        m.horizontal = False
        moves = self.strategy.move_finder(0, m, rack, self.strategy.game.gaddag.root)

        m1 = Move()
        m1.horizontal = False
        m1.positions = [BoardPosition('A', (7, 7)), BoardPosition('A', (8, 7))]

        m2 = Move()
        m2.horizontal = False
        m2.positions = [BoardPosition('A', (6, 7)), BoardPosition('A', (7, 7))]

        expected = {m1, m2}
        self.assertEqual(expected, moves)

        rack = ['B', 'A']

        m = Move()
        h_moves = self.strategy.move_finder(0, m, rack, self.strategy.game.gaddag.root)

        m = Move()
        m.horizontal = False
        v_moves = self.strategy.move_finder(0, m, rack, self.strategy.game.gaddag.root)

        words = ['AB', 'BA']
        h_expected = set()
        v_expected = set()
        for word in words:
            low_start = 7 - len(word) + 1
            for i in xrange(0, len(word)):
                m = Move()
                for j, letter in enumerate(word):
                    m.positions.append(BoardPosition(letter, (7, low_start + i + j)))
                h_expected.add(m)

                m = Move()
                m.horizontal = False
                for j, letter in enumerate(word):
                    m.positions.append(BoardPosition(letter, (low_start + i + j, 7)))
                v_expected.add(m)

        self.assertEqual(h_expected, h_moves)
        self.assertEqual(v_expected, v_moves)

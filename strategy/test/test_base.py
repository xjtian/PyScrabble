__author__ = 'Jacky'

import unittest
from copy import deepcopy

from strategy.strategies import StrategyBase
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

    def test_find_anchors(self):
        self.game.board = [
            list('A..A.'),
            list('.....'),
            list('AAAA.'),
            list('AA.AA'),
            list('.A.A.'),
            list('AAAAA')
        ]

        self.assertEqual([2], self.strategy.find_anchors(0, True))
        self.assertEqual([0], self.strategy.find_anchors(1, True))
        self.assertEqual([4], self.strategy.find_anchors(2, True))
        self.assertEqual([2], self.strategy.find_anchors(3, True))
        self.assertEqual([0, 2], self.strategy.find_anchors(4, True))
        self.assertEqual([], self.strategy.find_anchors(5, True))

        self.game.board = [
            list('A.AA.A'),
            list('..AAAA'),
            list('..A..A'),
            list('A.AAAA'),
            list('...A.A')
        ]

        self.assertEqual([2], self.strategy.find_anchors(0, False))
        self.assertEqual([0], self.strategy.find_anchors(1, False))
        self.assertEqual([4], self.strategy.find_anchors(2, False))
        self.assertEqual([2], self.strategy.find_anchors(3, False))
        self.assertEqual([0, 2], self.strategy.find_anchors(4, False))
        self.assertEqual([], self.strategy.find_anchors(5, False))

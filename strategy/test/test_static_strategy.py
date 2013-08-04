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

__author__ = 'Jacky'

import unittest

from strategy.strategies import StaticScoreStrategy, MoveAlias
from engine.game import ScrabbleGame


class StaticScoreTest(unittest.TestCase):
    def setUp(self):
        game = ScrabbleGame(wordlist='./wordlists/ABBA.txt', read_gaddag=True)
        self.strategy = StaticScoreStrategy(game)

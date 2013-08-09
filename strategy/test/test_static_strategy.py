__author__ = 'Jacky'

import unittest

from strategy.strategies import StaticScoreStrategy, MoveAlias
from engine.game import ScrabbleGame


class StaticScoreTest(unittest.TestCase):
    def setUp(self):
        game = ScrabbleGame(wordlist='./wordlists/ABBA.txt', read_gaddag=True)
        self.strategy = StaticScoreStrategy(game)

    def test_record_play(self):
        self.strategy.horizontal = True
        self.strategy.coord = 1
        self.strategy.moves = set()
        self.strategy.leftmost = 0

        self.strategy.record_play('hello')

        expected = set()
        expected.add(MoveAlias(word='hello', x=1, y=0, horizontal=True, score=0))
        self.assertEqual(expected, self.strategy.moves)

        self.strategy.leftmost = 5
        self.strategy.coord = 2
        self.strategy.record_play('goodbye')

        expected.add(MoveAlias(word='goodbye', x=2, y=5, horizontal=True, score=0))
        self.assertEqual(expected, self.strategy.moves)

        self.strategy.horizontal = False
        self.strategy.coord = 3
        self.strategy.moves = set()
        self.strategy.leftmost = -1

        self.strategy.record_play('abcd')

        expected = set()
        expected.add(MoveAlias(word='abcd', x=-1, y=3, horizontal=False, score=0))
        self.assertEqual(expected, self.strategy.moves)

        self.strategy.leftmost = 10
        self.strategy.coord = 0
        self.strategy.record_play('dcba')

        expected.add(MoveAlias(word='dcba', x=10, y=0, horizontal=False, score=0))
        self.assertEqual(expected, self.strategy.moves)

    def test_algorithm(self):
        # Try some empty rows (analogous to openings)
        self.strategy.row = ['.', '.']
        self.strategy.anchors = [0]
        self.strategy.moves = set()
        self.strategy.cross_sets = [None, None]
        self.strategy.leftmost = 0
        self.strategy.cur_anchor = 0
        self.strategy.coord = 0

        self.strategy.gen(0, '', ['A', 'B', 'A', 'B'], self.strategy.game.gaddag.root)

        expected_words = ['AA', 'BB', 'AB', 'BA']
        expected = set()
        for word in expected_words:
            expected.add(MoveAlias(word=word, x=0, y=0, horizontal=True, score=0))
        self.assertEqual(expected, self.strategy.moves)

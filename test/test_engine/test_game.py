__author__ = 'Jacky'

import unittest
from collections import Counter
from engine.game import ScrabbleGame

from engine.letters import default_bag

class TestScrabbleGame(unittest.TestCase):
    def setUp(self):
        self.game = ScrabbleGame()

    def test_add_player(self):
        self.assert_(self.game.add_player('Bob'))
        self.assertEqual('Bob', self.game.players[0].name)

        self.assert_(self.game.add_player('Bob2'))
        self.assert_(self.game.add_player('Bob3'))
        self.assert_(self.game.add_player('Bob4'))

        names = [player.name for player in self.game.players]
        self.assert_(all(name in names for name in ['Bob', 'Bob2', 'Bob3', 'Bob4']))

        self.assert_(not self.game.add_player('Bob5'))
        self.assertEqual(4, len(self.game.players))

    def test_start_game(self):
        self.game.add_player('Bob')
        self.game.add_player('Bob2')

        self.game.start_game()

        self.assertEqual(7, len(self.game.players[0].rack))
        self.assertEqual(7, len(self.game.players[1].rack))
        self.assertEqual(len(default_bag) - 14, len(self.game.bag))

        all_drawn = self.game.players[0].rack + self.game.players[1].rack
        check_bag = self.game.bag + all_drawn

        check_counter = Counter(check_bag)
        bag_counter = Counter(default_bag)

        for l in bag_counter.keys():
            self.assertEqual(bag_counter[l], check_counter[l])
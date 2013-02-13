__author__ = 'Jacky'

import unittest
from copy import deepcopy

from collections import Counter
from engine.game import ScrabbleGame
from engine import board

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

    def test_set_candidate(self):
        self.game.add_player('Bob')
        self.game.players[0].rack = ['H', 'E', 'L', 'L', 'O', ' ', ' ']

        hello = 'HELLO'

        self.assert_(self.game.set_candidate(hello, (0, 0), True))
        for i, bp in enumerate(self.game.candidate.positions):
            self.assertEqual(hello[i], bp.letter)
            self.assertEqual((0, i), bp.pos)

        self.game.candidate = None

        self.assert_(self.game.set_candidate(hello, (0, 0), False))
        for i, bp in enumerate(self.game.candidate.positions):
            self.assertEqual(hello[i], bp.letter)
            self.assertEqual((i, 0), bp.pos)

        # Didn't clear the candidate so this should return False
        self.assert_(not self.game.set_candidate(hello, (0, 0), True))

        self.game.candidate = None
        self.assert_(not self.game.set_candidate('ABCD', (0, 0), False))

        self.assert_(not self.game.set_candidate(hello, (-1, 0), True))
        self.assert_(not self.game.set_candidate(hello, (16, 0), False))

        self.assert_(not self.game.set_candidate(hello, (0, -1), True))
        self.assert_(not self.game.set_candidate(hello, (16, 0), False))

        self.assert_(not self.game.set_candidate(hello, (7, 13), True))
        self.assert_(not self.game.set_candidate(hello, (13, 7), False))

        self.assert_(not self.game.set_candidate('', (7, 7), True))

    def test_validate_candidate(self):
        self.game.add_player('Bob')
        self.game.players[0].rack = ['H', 'E', 'L', 'L', 'O', ' ', ' ']

        hello = 'HELLO'

        def clear_game():
            self.game.candidate = None
            self.game.board = deepcopy(board.default_board)

        # Try every way of putting 'HELLO' as the first move onto the board
        pos = (7, 7)
        for i, l in enumerate(hello):
            self.game.set_candidate(hello, (pos[0], pos[1] - i), True)
            self.assert_(self.game.validate_candidate())

            clear_game()

            self.game.set_candidate(hello, (pos[0] - i, pos[1]), False)
            self.assert_(self.game.validate_candidate())

            clear_game()

        # Make sure words are being scored correctly
        self.game.set_candidate(hello, (7, 3), True)
        self.game.validate_candidate()
        self.assertEqual(24, self.game.candidate.score)

        clear_game()

        self.game.set_candidate(hello, (7, 7), False)
        self.game.validate_candidate()
        self.assertEqual(18, self.game.candidate.score)
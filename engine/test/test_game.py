__author__ = 'Jacky'

import unittest
from copy import deepcopy

from collections import Counter

from engine.game import ScrabbleGame, MoveTypes
from engine import board
from engine.letters import default_bag
from lexicon import lexicon_set

from engine.test.scenario import parse_scenario


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

        # Try a move with the last letter on the edge
        self.game.candidate = None
        self.assert_(self.game.set_candidate('AB', (0, 13), True))

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
        def clear_game():
            self.game.candidate = None
            self.game.board = deepcopy(board.default_board)

        # Drop-in replacement for testing openings using scenario tester
        self.__scenario_tester('./engine/test/scenarios/opening.txt')
        clear_game()

        # Drop-in replacement for testing crosses using scenarios
        self.__scenario_tester('./engine/test/scenarios/crosses.txt')
        clear_game()

        # Testing parallel moves
        self.__scenario_tester('./engine/test/scenarios/parallel.txt')
        clear_game()

        # Testing specific scenarios that came up in playtesting
        self.__scenario_tester('./engine/test/scenarios/specific.txt', False)

    def test_remove_candidate(self):
        self.game.add_player('Bob')
        self.game.players[0].rack = ['H', 'E', 'L', 'L', 'O', ' ', ' ']

        self.game.set_candidate('HELLO', (7, 7), True)
        self.game.validate_candidate()

        self.game.remove_candidate()
        self.assertIsNone(self.game.candidate)
        self.assertEqual(self.game.board, board.default_board)
        self.assertEqual(0, self.game.players[0].score)

    def test_commit_candidate(self):
        self.game.add_player('Bob')
        self.game.players[0].rack = ['H', 'E', 'L', 'L', 'O', ' ', ' ']

        self.game.set_candidate('HELLO', (7, 7), True)
        self.game.validate_candidate()
        self.game.commit_candidate()

        self.assertIsNone(self.game.candidate)
        self.assertIsNotNone(self.game.history)

        self.assertEqual(MoveTypes.Placed, self.game.history.action)
        self.assertIsNone(self.game.history.previous)

        self.assertEqual(0, self.game.current_turn)
        self.assertEqual(18, self.game.players[0].score)

        self.assertEqual(7, len(self.game.players[0].rack))
        self.assertNotEqual(['H', 'E', 'L', 'L', 'O', ' ', ' '], self.game.players[0].rack)
        self.assertEqual(len(default_bag) - 5, len(self.game.bag))

    def test_pass_turn(self):
        self.game.add_player('Bob')
        self.game.players[0].rack = ['H', 'E', 'L', 'L', 'O', ' ', ' ']

        self.game.add_player('Jane')
        self.game.players[1].rack = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

        self.game.pass_turn()
        self.assertEqual(1, self.game.current_turn)
        self.assertEqual(0, self.game.players[0].score)
        self.assertEqual(0, self.game.players[1].score)
        self.assertEqual(['H', 'E', 'L', 'L', 'O', ' ', ' '], self.game.players[0].rack)
        self.assertEqual(['A', 'B', 'C', 'D', 'E', 'F', 'G'], self.game.players[1].rack)

        self.assertIsNotNone(self.game.history)
        self.assertEqual(MoveTypes.Pass, self.game.history.action)

    def test_exchange_tiles(self):
        self.game.add_player('Bob')
        self.game.players[0].rack = ['H', 'E', 'L', 'L', 'O', ' ', ' ']
        self.game.bag = ['A', 'B', 'C', 'D', 'E']

        hello = ['H', 'E', 'L', 'L', 'O']
        bag = ['A', 'B', 'C', 'D', 'E']

        self.assert_(self.game.exchange_tiles('HELLO'))
        self.assert_(all([letter in self.game.bag for letter in hello]))
        self.assert_(all([letter in self.game.players[0].rack for letter in bag]))

        self.assertEqual(5, len(self.game.bag))
        self.assertEqual(7, len(self.game.players[0].rack))

        self.assertIsNotNone(self.game.history)
        self.assertEqual(MoveTypes.Exchange, self.game.history.action)
        self.assert_(all([letter in self.game.history.move.drawn for letter in bag]))

        self.assert_(not self.game.exchange_tiles('ABCDE  '))     # Not enough stuff in bag
        self.assert_(all([letter in self.game.players[0].rack for letter in bag]))
        self.assert_(all([letter in self.game.bag for letter in hello]))

        self.assert_(not self.game.exchange_tiles('ABCDEQ'))    # Non-existent letter
        self.assert_(all([letter in self.game.players[0].rack for letter in bag]))
        self.assert_(all([letter in self.game.bag for letter in hello]))

        # Make sure that exchange works properly after a failed attempt
        self.assert_(self.game.exchange_tiles('AB'))

    def __scenario_tester(self, filename, wordlist=True):
        old_set = self.game.lexicon_set
        if wordlist:
            self.game.lexicon_set = lexicon_set.read_lexicon('./engine/test/wordlists/wordlist1.txt')

        for exp_results in parse_scenario(filename):
            self.game.candidate = None
            self.game.board = exp_results['board']

            if self.game.board == board.default_board:
                self.game.history = None
            else:
                self.game.history = object()

            self.game.candidate = exp_results['candidate']
            if exp_results['result']:
                self.assert_(self.game.validate_candidate())
                self.assertEquals(exp_results['score'], self.game.candidate.score)
            else:
                self.assert_(not self.game.validate_candidate())

        self.game.lexicon_set = old_set

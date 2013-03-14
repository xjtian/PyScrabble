__author__ = 'Jacky'

import unittest
from copy import deepcopy

from collections import Counter
from engine.game import ScrabbleGame, MoveTypes
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

        # With 'HELLO' placed vertically down from start square, try some crosses
        self.game.history = object()    # Just so game.history is not None

        self.game.candidate = None
        self.game.set_candidate('ELLO', (7, 8), True)
        self.assert_(self.game.validate_candidate())
        self.assertEqual(9, self.game.candidate.score)

        self.game.candidate = None
        self.game.set_candidate('HELO', (9, 5), True)
        self.assert_(self.game.validate_candidate())
        self.assertEqual(18, self.game.candidate.score)

        self.game.candidate = None
        self.game.set_candidate('HELL', (11, 3), True)
        self.assert_(self.game.validate_candidate())
        self.assertEqual(16, self.game.candidate.score)

        # Now try a parallel move
        clear_game()
        self.game.history = None

        self.game.set_candidate(hello, (7, 7), False)
        self.game.validate_candidate()

        self.game.history = object()
        self.game.candidate = None
        self.game.set_candidate('EL', (7, 8), False)    # Forms EL, HE, and EL
        self.assert_(self.game.validate_candidate())
        self.assertEqual(11, self.game.candidate.score)

        clear_game()
        self.game.history = None

        self.game.set_candidate('AB', (7, 7), True)
        self.assert_(self.game.validate_candidate())
        self.assertEqual(0, self.game.candidate.score)

        # Try a move with a tile on the edge
        clear_game()
        self.game.history = None

        self.game.set_candidate(hello, (3, 7), False)
        self.game.validate_candidate()

        self.game.history = object()
        self.game.candidate = None
        self.game.set_candidate('ELLO', (3, 8), True)
        self.game.validate_candidate()

        self.game.candidate = None
        self.game.set_candidate('LW', (2, 11), False)
        self.assert_(self.game.validate_candidate())

        self.game.candidate = None
        self.game.set_candidate('HAT', (4, 12), True)
        self.assert_(self.game.validate_candidate())

        # Try an invalid first move
        clear_game()
        self.game.history = None
        self.game.set_candidate(hello, (8, 8), True)
        self.assert_(not self.game.validate_candidate())

        # Try some invalid crosses now
        clear_game()
        self.game.set_candidate(hello, (7, 7), False)
        self.game.validate_candidate()

        self.game.history = object()
        self.game.candidate = None
        self.game.set_candidate(hello, (9, 9), True)     # No hook or cross
        self.assert_(not self.game.validate_candidate())

        clear_game()
        self.game.set_candidate(hello, (7, 7), False)
        self.game.validate_candidate()

        self.game.history = object()
        self.game.candidate = None
        self.game.set_candidate('HO', (7, 8), True)     # Not a word (HHO)
        self.assert_(not self.game.validate_candidate())

    def test_specific_cases(self):
        """
        Some tests for unexpected outcomes encountered when playing the game
        """
        def parse_situation(s):
            lines = situation.splitlines()
            return [line[line.index('|') + 2:].split(' ') for line in lines]

        # The problem with this case was that the prefix finder wrapped around because the first letter was on an edge.
        # 'HUMVEE' was added as a prefix to the attempted play 'RASING', which clearly made it invalid

        situation = """ 0| # . . 2 . . . J I L T 2 . . #
             1| . @ . . . Y . . . 3 O W . @ .
             2| . . @ . . O F . 2 . K I P . .
             3| 2 . . @ . D I F . D E N E . 2
             4| . . . . @ . Z A . I D . A . .
             5| . 3 . . . 3 . C . V . . R 3 .
             6| . . 2 . . . 2 a W A . . L . G
             7| # . . 2 . . . D O N . C . . R
             8| . . 2 . . . Y E N . . O 2 . I
             9| . 3 . . . 3 O . . 3 H E . U M
            10| . . . . P L U G . . A N . R E
            11| 2 . . Q I . . R . . B A . T 2
            12| . . @ . . . 2 I 2 H U M V E E
            13| . @ . . . 3 . O . 3 . O . X .
            14| # . . 2 . . . T o L E R A T E"""
        current_rack = list('RAASIGN')
        attempt = {'letters': 'RASING', 'pos': (12, 0), 'horiz': True}

        # Setup the game
        self.game.add_player('Player 1')
        self.game.add_player('Player 2')
        self.game.current_turn = 1
        self.game.players[1].rack = current_rack
        self.game.history = object()

        self.game.board = parse_situation(situation)    # Set the board
        # Set the candidate attempt to the improper failure
        self.assert_(self.game.set_candidate(attempt['letters'], attempt['pos'], attempt['horiz']))
        self.assert_(self.game.validate_candidate())

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

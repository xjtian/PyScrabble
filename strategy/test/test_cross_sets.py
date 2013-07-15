__author__ = 'Jacky'

import unittest

from lexicon.gaddag import gaddag_from_file
from strategy.cross_sets import *
from engine.board import BoardPosition

from strategy.test.scenario import parse_cross_set


class TestCrossSets(unittest.TestCase):
    def setUp(self):
        self.gaddag = gaddag_from_file('./wordlists/test_list1.txt')

    def test_cases(self):
        self.__scenario_tester('./strategy/test/scenarios/basic.txt')
        self.__scenario_tester('./strategy/test/scenarios/mids.txt')
        self.__scenario_tester('./strategy/test/scenarios/specific.txt')
        self.__scenario_tester('./strategy/test/scenarios/parallel_presuff.txt')

    def __scenario_tester(self, filename):
        for scenario in parse_cross_set(filename):
            board = scenario['board']

            # print 'Testing scenario in file %s' % filename
            # move_letters = ''.join([bp.letter for bp in scenario['candidate'].positions])
            # print 'Move candidate letters: %s' % move_letters

            vertical_crosses = [[None] * len(row) for row in board]
            horizontal_crosses = [[None] * len(row) for row in board]
            move = scenario['candidate']

            redo_crosses(move, horizontal_crosses, vertical_crosses, board, self.gaddag)

            for cross in scenario['crosses']:
                x, y = cross['x'], cross['y']
                if cross['horizontal']:
                    self.assertEqual(cross['letters'], horizontal_crosses[x][y])
                else:
                    self.assertEqual(cross['letters'], vertical_crosses[x][y])


class TestMidCross(unittest.TestCase):
    def setUp(self):
        self.gaddag = gaddag_from_file('./wordlists/test_list1.txt')

    def test_standard(self):
        """
        No prefix, no suffix, bare board.
        """
        board = [
            list('..B..'),
            list('.....'),
            list('C...C'),
            list('.....'),
            list('..B..')
        ]

        bp = BoardPosition('A', (2, 2))
        expected = (set('CDE'), set('CDE'))

        self.assertEqual(expected, mid_cross(bp, '', '', True, board, self.gaddag))

        expected = (set('BDE'), set('BDE'))
        self.assertEqual(expected, mid_cross(bp, '', '', False, board, self.gaddag))

        board = [
            list('.....'),
            list('.....'),
            list('.....'),
            list('.....'),
            list('.....')
        ]
        expected = (None, None)

        self.assertEqual(expected, mid_cross(bp, '', '', True, board, self.gaddag))
        self.assertEqual(expected, mid_cross(bp, '', '', False, board, self.gaddag))

    def test_prefix(self):
        """
        Test with prefix.
        """
        board = [
            list('.......'),
            list('....C..'),
            list('.......'),
            list('....B..'),
            list('.D.B..C'),
            list('.......'),
            list('....D..')
        ]

        bp = BoardPosition('A', (4, 4))
        expected = (set('DE'), set('CE'))

        self.assertEqual(expected, mid_cross(bp, 'B', '', True, board, self.gaddag))

        expected = (set('CE'), set('DE'))
        self.assertEqual(expected, mid_cross(bp, 'B', '', False, board, self.gaddag))

    def test_suffix(self):
        """
        Test with suffix.
        """
        board = [
            list('..D....'),
            list('.......'),
            list('C..B.D.'),
            list('..B....'),
            list('.......'),
            list('..C....'),
            list('.......')
        ]

        bp = BoardPosition('A', (2, 2))
        expected = (set('CE'), set('DE'))

        self.assertEqual(expected, mid_cross(bp, '', 'B', True, board, self.gaddag))

        expected = (set('DE'), set('CE'))
        self.assertEqual(expected, mid_cross(bp, '', 'B', False, board, self.gaddag))

    def test_prefix_suffix(self):
        """
        Test with prefix and suffix.
        """
        board = [
            list('....B....'),
            list('.........'),
            list('....D....'),
            list('.D.B.C.D.'),
            list('....E....'),
            list('.........'),
            list('....B....'),
        ]

        bp = BoardPosition('A', (3, 4))

        expected = (set('C'), set('C'))
        self.assertEqual(expected, mid_cross(bp, 'D', 'E', True, board, self.gaddag))

        expected = (set('E'), set('E'))
        self.assertEqual(expected, mid_cross(bp, 'B', 'C', False, board, self.gaddag))

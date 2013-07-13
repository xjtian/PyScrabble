__author__ = 'Jacky'

import unittest

from lexicon.gaddag import gaddag_from_file
from strategy.cross_sets import redo_crosses

from strategy.test.scenario import parse_cross_set


class TestCrossSets(unittest.TestCase):
    def setUp(self):
        self.gaddag = gaddag_from_file('./wordlists/test_list1.txt')

    def test_cases(self):
        self.__scenario_tester('./strategy/test/scenarios/basic.txt')
        self.__scenario_tester('./strategy/test/scenarios/mids.txt')
        self.__scenario_tester('./strategy/test/scenarios/specific.txt')

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

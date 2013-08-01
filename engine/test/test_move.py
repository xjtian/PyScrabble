__author__ = 'Jacky'

import unittest
from copy import deepcopy

from engine.move import Move
from engine.board import BoardPosition


class TestMove(unittest.TestCase):
    def test_constructor(self):
        m = Move()

        self.assertEqual(m.score, 0)
        self.assert_(not m.positions)
        self.assert_(not m.drawn)

    def test_add_letter(self):
        m = Move()
        m.add_letter('a', (0, 0))

        self.assertEqual(m.positions[0].letter, 'a')
        self.assertEqual(m.positions[0].pos, (0, 0))

        m.add_letter('b', (1, 1))

        self.assertEqual(m.positions[1].letter, 'b')
        self.assertEqual(m.positions[1].pos, (1, 1))

    def test_sort_letters(self):
        m = Move()
        m.add_letter('a', (0, 1))
        m.add_letter('b', (0, 0))

        m.sort_letters()

        self.assertEqual('b', m.positions[0].letter)
        self.assertEqual((0, 0), m.positions[0].pos)

        self.assertEqual('a', m.positions[1].letter)
        self.assertEqual((0, 1), m.positions[1].pos)

        m = Move()
        m.horizontal = False
        m.add_letter('a', (1, 0))
        m.add_letter('b', (0, 0))

        m.sort_letters()

        self.assertEqual('b', m.positions[0].letter)
        self.assertEqual((0, 0), m.positions[0].pos)

        self.assertEqual('a', m.positions[1].letter)
        self.assertEqual((1, 0), m.positions[1].pos)

    def test_deepcopy(self):
        m = Move()

        m.add_letter('A', (0, 1))
        m.add_letter('B', (0, 0))

        m.drawn = ['A', 'B', 'C']

        exp_pos = deepcopy(m.positions)
        exp_drawn = deepcopy(m.drawn)

        m2 = deepcopy(m)

        m.drawn[2] = 'D'
        m.positions[0] = ('D', (7, 7))

        self.assertEqual(exp_pos, m2.positions)
        self.assertEqual(exp_drawn, m2.drawn)

    def test_equality(self):
        a = Move()
        a.positions = ['A', {'a': [1, 2, 3]}]

        b = Move()
        b.positions = ['A', {'a': [1, 2, 3]}]

        self.assert_(a == b)

        b.horizontal = False
        self.assert_(not a == b)

        b.positions = ['A', {'b': [1, 2]}]
        self.assert_(not a == b)

        b.horizontal = True
        self.assert_(not a == b)

    def test_hash(self):
        a = Move()
        a.positions = ['A', 'B', 'C']

        b = Move()
        b.positions = ['A', 'B', 'C']

        self.assert_(hash(a) == hash(b))

        b.horizontal = False
        self.assert_(not hash(a) == hash(b))

        b.positions = ['A', 'B', 'D']
        self.assert_(not hash(a) == hash(b))

        b.horizontal = True
        self.assert_(not hash(a) == hash(b))

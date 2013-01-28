__author__ = 'Jacky'

import unittest
from engine.move import Move

class TestMove(unittest.TestCase):
    def test_constructor(self):
        m = Move()

        self.assertEquals(m.score, 0)
        self.assert_(not m.positions)
        self.assert_(not m.drawn)

    def test_add_letter(self):
        m = Move()
        m.add_letter('a', (0, 0))

        self.assertEquals(m.positions[0].letter, 'a')
        self.assertEquals(m.positions[0].pos, (0, 0))

        m.add_letter('b', (1, 1))

        self.assertEquals(m.positions[1].letter, 'b')
        self.assertEquals(m.positions[1].pos, (1, 1))

    def test_sort_letters(self):
        m = Move()
        m.add_letter('a', (0, 1))
        m.add_letter('b', (0, 0))

        m.sort_letters()

        self.assertEquals('b', m.positions[0].letter)
        self.assertEquals((0,0), m.positions[0].pos)

        self.assertEquals('a', m.positions[1].letter)
        self.assertEquals((0, 1), m.positions[1].pos)

        m = Move()
        m.horizontal = False
        m.add_letter('a', (1, 0))
        m.add_letter('b', (0, 0))

        m.sort_letters()

        self.assertEquals('b', m.positions[0].letter)
        self.assertEquals((0, 0), m.positions[0].pos)

        self.assertEquals('a', m.positions[1].letter)
        self.assertEquals((1, 0), m.positions[1].pos)
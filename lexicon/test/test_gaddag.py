__author__ = 'Jacky'

import unittest

from lexicon.gaddag import *


class TestGaddagState(unittest.TestCase):
    def setUp(self):
        self.state = GaddagState()

    def test_add_arc(self):
        new_state = self.state.add_arc('A')

        self.assertIn('A', self.state.arcs)
        self.assertEquals(new_state, self.state.arcs['A'])

    def test_add_final_arc(self):
        new_state = self.state.add_final_arc('A', 'B')

        self.assertIn('A', self.state.arcs)
        self.assertEquals(new_state, self.state.arcs['A'])

        self.assertIn('B', new_state.letter_set)

    def test_force_arc(self):
        force = GaddagState()

        self.state.force_arc('A', force)

        self.assertIn('A', self.state.arcs)
        self.assertEquals(force, self.state.arcs['A'])


class TestGaddag(unittest.TestCase):
    def setUp(self):
        self.word = 'ABCDEFG'
        self.gaddag = Gaddag()

    def test_add_word(self):
        self.gaddag.add_word(self.word)

        # Ensuring that every REV(x)|y path is in the GADDAG
        for i, letter in enumerate(self.word):
            rev_prefix = self.word[:i + 1][::-1]
            suffix = self.word[i + 1:]

            cur_state = self.gaddag.root

            if i == len(self.word) - 1:
                for letter in rev_prefix[:-1]:
                    self.assertIn(letter, cur_state.arcs)
                    cur_state = cur_state.arcs[letter]
                self.assertIn(rev_prefix[-1], cur_state.letter_set)
            else:
                for letter in rev_prefix:
                    self.assertIn(letter, cur_state.arcs)
                    cur_state = cur_state.arcs[letter]

                self.assertIn('|', cur_state.arcs)
                cur_state = cur_state.arcs['|']

            if len(suffix) == 1:
                self.assertIn(suffix[0], cur_state.letter_set)
            elif len(suffix) > 0:
                for letter in suffix[:-1]:
                    self.assertIn(letter, cur_state.arcs)
                    cur_state = cur_state.arcs[letter]
                self.assertIn(suffix[-1], cur_state.letter_set)

    def test_is_word(self):
        self.gaddag.add_word(self.word)

        self.assert_(self.gaddag.is_word(self.word))
        self.assert_(not self.gaddag.is_word(self.word[::-1]))

    def test_cross_sets(self):
        self.gaddag.add_word(self.word)

        subword = self.word[1:]
        left, right = self.gaddag.cross_sets(subword)
        self.assertEqual({self.word[0]}, left)
        self.assertEqual(set(), right)

        subword = self.word[:-1]
        left, right = self.gaddag.cross_sets(subword)
        self.assertEqual(set(), left)
        self.assertEqual({self.word[-1]}, right)

    def test_mid_set(self):
        self.gaddag.add_word(self.word)

        for i in xrange(1, len(self.word) - 1):
            s = self.gaddag.mid_set(self.word[0:i], self.word[i+1:])
            self.assertEqual({self.word[i]}, s)
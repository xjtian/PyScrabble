__author__ = 'Jacky'

import unittest
from engine.player import Player


class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.player = Player('player')

    def test_constructor(self):
        self.assertEqual('player', self.player.name)
        self.assertEqual(0, self.player.score)
        self.assert_(not self.player.rack)

    def test_valid_play(self):
        self.player.rack = list('DEADBEEF')

        l = self.player.valid_play('DEAD')
        for letter in 'DEAD':
            self.assertIn(letter, l)

        l = self.player.valid_play('DEADBEEF')
        for letter in 'DEADBEEF':
            self.assertIn(letter, l)

        l = self.player.valid_play('BLAH')
        self.assert_(not l)

        # With blanks now
        self.player.rack = list('HELLO WORLD')

        l = self.player.valid_play('HELLOS')
        for letter in 'HELLOs':
            self.assertIn(letter, l)

        # Make sure the blank isn't used unless absolutely necessary
        l = self.player.valid_play('HELLO')
        for letter in 'HELLO':
            self.assertIn(letter, l)

        # What if the blank is a second instance of an existing letter?
        l = self.player.valid_play('LLLL')
        self.assertEqual(1, l.count('l'))

    def test_use_letters(self):
        self.player.rack = list('DEADBEEF')

        self.player.use_letters('DEAD')
        self.assertEqual(list('BEEF'), self.player.rack)

        self.player.rack = list('HELLO WORLD')

        self.player.use_letters('JELLO')
        self.assertEqual(list('HWORLD'), self.player.rack)

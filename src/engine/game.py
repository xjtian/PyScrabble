__author__ = 'Jacky'

import copy
import random

from engine import letters, board, player, move
from lexicon import lexicon_set
from settings.lexicon import WORDLIST_PATH

class MoveTypes(object):
    Blank, Placed, Pass, Exchange = range(4)

class StateNode(object):
    def __init__(self, move):
        self.move = move
        self.previous = None

        self.action = MoveTypes.Blank

class ScrabbleGame(object):
    def __init__(self):
        self.board = copy.deepcopy(board.default_board)
        self.bag = copy.deepcopy(letters.default_bag)

        self.players = []
        self.current_turn = 0

        self.history = None
        self.candidate = move.Move()

    def add_player(self, name):
        if len(self.players) > 3:
            return False
        self.players.append(player.Player(name))
        return True

    def start_game(self):
        n = len(self.players)
        for i in xrange(0, 7*n):
            self.players[i % n].rack.append(self.bag.pop(random.randint(0, len(self.bag) - 1)))

        lexicon_set.read_lexicon(WORDLIST_PATH)

    def set_candidate(self, letters, pos, horizontal):
        from_rack = self.players[self.current_turn].valid_play(letters)
        if not from_rack:
            return False

        self.candidate.horizontal = horizontal
        for i, letter in enumerate(from_rack):
            if horizontal:
                self.candidate.add_letter(letter, (pos[0] + i, pos[1]))
            else:
                self.candidate.add_letter(letter, (pos[0], pos[1] + i))

        self.candidate.sort_letters()
        return True

    def validate_candidate(self):
        if not self.candidate.positions:
            return False

        if self.candidate.horizontal:
            if not all([b.pos[0] == self.candidate.positions[0].pos[0] for b in self.candidate.positions]):
                return False
        else:
            if not all([b.pos[1] == self.candidate.positions[0].pos[1] for b in self.candidate.positions]):
                return False

        word_multiplier = 1
        for bpos in self.candidate.positions:
            x, y = bpos.pos
            if self.board[x][y] not in board.empty_locations:
                return False

            word_multiplier *= board.word_multipliers.get(self.board[x][y], 1)
            letter_multiplier = board.letter_multipliers.get(self.board[x][y], 1)
            self.candidate.score += letters.letter_scores.get(bpos.letter, 0) * letter_multiplier

            self.board[x][y] = bpos.letter

        prefix = self.__get_prefix(self.candidate.positions[0].pos, self.candidate.horizontal)
        suffix = self.__get_suffix(self.candidate.positions[-1].pos, self.candidate.horizontal)

        for l in prefix:
            self.candidate.score += letters.letter_scores.get(l, 0)
        for l in suffix:
            self.candidate.score += letters.letter_scores.get(l, 0)
        self.candidate.score *= word_multiplier

        body = ''.join([bp.letter for bp in self.candidate.positions])
        word = '%s%s%s' % (prefix, body, suffix)

        if word.upper() not in lexicon_set.global_set:
            return False

        return self.__check_crosses()


    def remove_candidate(self):
        for bpos in self.candidate.positions:
            x, y = bpos.pos
            self.board[x][y] = board.default_board[x][y]

        #TODO: finish logic in here

    def commit_candidate(self):
        self.players[self.current_turn].use_letters(''.join([bp.letter for bp in self.candidate.positions]))

        newstate = StateNode(self.candidate)
        newstate.action = MoveTypes.Placed
        newstate.previous = self.history

        self.history = newstate

        #TODO: draw new tiles from bag and write that action to history as well

    def __get_prefix(self, pos, horizontal):
        """
        Returns the prefix the leads up to the given position.

        @param pos: Tuple of position on board to check for a prefix before.
        @param horizontal: Boolean value to set which direction to look in.
        @return: Prefix preceeding the given position on the board.
        """

        return ''.join(self.__pre_suff_helper(pos, horizontal, True))

    def __get_suffix(self, pos, horizontal):
        """
        Returns the suffix after the given position.

        @param pos: Tuple of position on board to check for a prefix before.
        @param horizontal: Boolean value to set which direction to look in.
        @return: Suffix after the given position on the board.
        """

        return ''.join(self.__pre_suff_helper(pos, horizontal, False))

    def __pre_suff_helper(self, pos, horizontal, pre):
        i = -1 if pre else 1
        sub = []
        x, y = pos

        l = self.board[x][y + i] if horizontal else self.board[x + i][y]
        while l not in board.empty_locations:
            sub.append(l)
            i += -1 if pre else 1
            l = self.board[x][y + i] if horizontal else self.board[x + i][y]

        if pre:
            sub.reverse()

        return sub

    def __check_crosses(self):
        """
        Check that all crosses created by the candidate move are valid. Calling this method will also update the score
        value of the candidate move.

        @return: True if the candidate move produces valid crosses, False otherwise.
        """
        if not self.history:    #First turn, no crosses possible
            return True

        for bpos in self.candidate.positions:
            x, y = bpos.pos
            prefix = self.__get_prefix(bpos.pos, not self.candidate.horizontal)
            suffix = self.__get_suffix(bpos.pos, not self.candidate.horizontal)

            cross = '%s%s%s' % (prefix, bpos.letter, suffix)
            if len(cross) > 1:
                if cross.upper() not in lexicon_set.global_set:
                    return False
                else:
                    subscore = 0
                    for l in prefix:
                        subscore += letters.letter_scores.get(l, 0)
                    for l in suffix:
                        subscore += letters.letter_scores.get(l, 0)

                    subscore += letters.letter_scores.get(bpos.letter, 0) * \
                                board.letter_multipliers.get(board.default_board[x][y], 1)
                    subscore *= board.word_multipliers.get(board.default_board[x][y], 1)

                    self.candidate.score += subscore

        return True
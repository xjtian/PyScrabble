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
        """
        Shortcut for setting the candidate move.

        @param letters: string or list of letters to play
        @param pos: x,y position of the first tile of the play
        @param horizontal: True if the play is horizontal, False otherwise
        @return: True if function succeeds, False otherwise.
        """
        from_rack = self.players[self.current_turn].valid_play(letters)
        if not from_rack:
            return False

        self.candidate.horizontal = horizontal
        x, y = pos
        j = 0
        for letter in from_rack:
            if horizontal:
                while self.board[x][y+j] not in board.empty_locations:
                    j += 1
                self.candidate.add_letter(letter, (x, y+j))
            else:
                while self.board[x+j][y] not in board.empty_locations:
                    j += 1
                self.candidate.add_letter(letter, (x+j, y))
            j += 1

        return True

    def validate_candidate(self):
        """
        Validate the candidate move and score it. May assign a score to an invalid move.

        @return: True if the move is valid, False if it is invalid.
        """
        if not self.candidate.positions:
            return False

        self.candidate.sort_letters()

        #Verify the candidate is all horizontal or all vertical
        if self.candidate.horizontal:
            if not all([b.pos[0] == self.candidate.positions[0].pos[0] for b in self.candidate.positions]):
                return False
        else:
            if not all([b.pos[1] == self.candidate.positions[0].pos[1] for b in self.candidate.positions]):
                return False

        hooked = not self.history   #If it's the first turn, no need to hook for valid moves
        if hooked:
            for bp in self.candidate.positions:
                if bp.pos == (7, 7):
                    break
        else:
            return False    #First turn but move doesn't cover middle square

        word_multiplier = 1
        lx, ly = self.candidate.positions[0].pos
        for bpos in self.candidate.positions:
            x, y = bpos.pos
            if self.board[x][y] not in board.empty_locations:
                return False

            #If tiles got skipped in letter placement, make sure they contain existing letters and add them to the score
            if self.candidate.horizontal and y - ly > 1:
                hooked = True
                for i in xrange(ly + 1, y):
                    existing = self.board[x][i]
                    if existing in board.empty_locations:
                        return False
                    self.candidate.score += letters.letter_scores.get(existing, 0)
            elif not self.candidate.horizontal and x - lx > 1:
                hooked = True
                for i in xrange(lx + 1, x):
                    existing = self.board[i][y]
                    if existing in board.empty_locations:
                        return False
                    self.candidate.score += letters.letter_scores.get(existing, 0)

            #Process multipliers for placed letter and add to score of candidate
            word_multiplier *= board.word_multipliers.get(self.board[x][y], 1)
            letter_multiplier = board.letter_multipliers.get(self.board[x][y], 1)
            self.candidate.score += letters.letter_scores.get(bpos.letter, 0) * letter_multiplier

            self.board[x][y] = bpos.letter
            lx, ly = x, y

        prefix = self.__get_prefix(self.candidate.positions[0].pos, self.candidate.horizontal)
        suffix = self.__get_suffix(self.candidate.positions[-1].pos, self.candidate.horizontal)

        hooked |= prefix or suffix  #Bridging also counts as hooking

        #Add prefix and suffix to candidate score, then multiply the whole thing by the word multiplier
        for l in prefix:
            self.candidate.score += letters.letter_scores.get(l, 0)
        for l in suffix:
            self.candidate.score += letters.letter_scores.get(l, 0)
        self.candidate.score *= word_multiplier

        x, y = self.candidate.positions[0].pos
        lx, ly = self.candidate.positions[-1].pos

        #Construct the word that makes up the play
        if self.candidate.horizontal:
            body = ''.join([self.board[x][y+i] for i in xrange(0, ly-y)])
        else:
            body = ''.join([self.board[x+i][y] for i in xrange(0, lx-x)])
        word = '%s%s%s' % (prefix, body, suffix)

        if word.upper() not in lexicon_set.global_set:
            return False

        return self.__check_crosses() and hooked

    def remove_candidate(self):
        """
        Remove the current candidate move.
        """
        for bpos in self.candidate.positions:
            x, y = bpos.pos
            self.board[x][y] = board.default_board[x][y]

        self.candidate = None

    def commit_candidate(self):
        """
        Commit the candidate move. This updates scores, draws new tiles for the player, ends the turn, and adds a new
        state to the game tree.
        """
        self.players[self.current_turn].use_letters(''.join([bp.letter for bp in self.candidate.positions]))
        self.candidate.drawn = [self.bag.pop(random.randint(0, len(self.bag) - 1))
                                for _ in xrange(0, len(self.candidate.positions))]
        for letter in self.candidate.drawn:
            self.players[self.current_turn].rack.append(letter)
        self.players[self.current_turn].score += self.candidate.score

        newstate = StateNode(self.candidate)
        newstate.action = MoveTypes.Placed
        newstate.previous = self.history

        self.history = newstate
        self.current_turn += 1
        self.current_turn %= len(self.players)

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

        crosses = False
        for bpos in self.candidate.positions:
            x, y = bpos.pos
            prefix = self.__get_prefix(bpos.pos, not self.candidate.horizontal)
            suffix = self.__get_suffix(bpos.pos, not self.candidate.horizontal)

            cross = '%s%s%s' % (prefix, bpos.letter, suffix)
            if len(cross) > 1:
                if cross.upper() not in lexicon_set.global_set:
                    return False
                else:
                    crosses = True
                    subscore = 0
                    for l in prefix:
                        subscore += letters.letter_scores.get(l, 0)
                    for l in suffix:
                        subscore += letters.letter_scores.get(l, 0)

                    subscore += letters.letter_scores.get(bpos.letter, 0) * \
                                board.letter_multipliers.get(board.default_board[x][y], 1)
                    subscore *= board.word_multipliers.get(board.default_board[x][y], 1)

                    self.candidate.score += subscore

        return crosses
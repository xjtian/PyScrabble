__author__ = 'Jacky'

import copy
import random

from engine import letters, board, player, move
from lexicon import lexicon_set
from lexicon.settings import WORDLIST_PATH


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
        self.candidate = None

        self.game_over = False
        self.game_started = False

        self.passes = 0

        lexicon_set.read_lexicon(WORDLIST_PATH)

    def current_player_info(self):
        """
        Returns information about the current player as a dictionary. Keys are
        'name', 'rack'
        """
        if not self.players:
            return dict()

        info = dict()
        raw_letters = ''.join(self.players[self.current_turn].rack)
        rack = ''
        for letter in raw_letters:
            rack += '%s%d ' % (letter if letter != ' ' else '_',
                               letters.letter_scores.get(letter, 0))

        info['name'] = self.players[self.current_turn].name
        info['rack'] = rack

        return info

    def get_scores(self):
        """
        Returns a dictionary with scores keyed by player name
        """
        return {player.name: player.score for player in self.players}

    def add_player(self, name):
        if self.game_started:
            return False

        if len(self.players) > 3:
            return False
        self.players.append(player.Player(name))
        return True

    def start_game(self):
        if self.game_started:
            return False

        n = len(self.players)
        for i in xrange(0, 7 * n):
            self.players[i % n].rack.append(
                self.bag.pop(random.randint(0, len(self.bag) - 1)))

        self.game_started = True
        return True

    def set_candidate(self, letters, pos, horizontal):
        """
        Shortcut for setting the candidate move. Specify the letters (in order)
        to play, the position of the first letter, and the direction of the
        move and this method will place the letters sequentially in the correct
        positions, accounting properly for any existing tiles on the board that
        have to be skipped.

        @param letters: string or list of letters to play.
        @param pos: x,y position of the first tile of the play.
        @param horizontal: True if the play is horizontal, False otherwise.
        @return: True if function succeeds, False if any letters aren't in
        player's rack, there's already a candidate, the move goes out of the
        board, or the game is over.
        """
        if self.game_over:
            return False

        from_rack = self.players[self.current_turn].valid_play(letters)
        b_height, b_width = len(self.board), len(self.board[0])

        # Candidate exists already or no letters are being played
        if self.candidate is not None or not letters:
            return False
            # Not a valid play given current rack
        if not from_rack:
            return False
            # First letter placed out of bounds
        if pos[0] < 0 or pos[0] >= b_height or pos[1] < 0 or pos[1] >= b_width:
            return False

        self.candidate = move.Move()
        self.candidate.horizontal = horizontal
        x, y = pos
        j = 0
        for i, letter in enumerate(from_rack):
            if horizontal:
                while self.board[x][y + j] not in board.empty_locations:
                    j += 1
                    if y + j >= b_width:
                        return False     # Move goes out of the board
                self.candidate.add_letter(letter, (x, y + j))
            else:
                while self.board[x + j][y] not in board.empty_locations:
                    j += 1
                    if x + j >= b_height:
                        return False    # Move goes out of the board
                self.candidate.add_letter(letter, (x + j, y))
            j += 1
            # Check bounds
            if (horizontal and y + j >= b_width) or (
                    not horizontal and x + j >= b_height):
                # Was the last letter placed before incrementing?
                return i == len(from_rack) - 1

        return True

    def validate_candidate(self):
        """
        Validate the candidate move and score it. May assign a partial score to
        an invalid move.

        @return: True if the move is valid, False if it is invalid.
        """
        if not self.candidate.positions or self.game_over:
            return False

        self.candidate.sort_letters()

        # Verify the candidate is all horizontal or all vertical
        if self.candidate.horizontal:
            if not all([b.pos[0] == self.candidate.positions[0].pos[0] for b in
                        self.candidate.positions]):
                return False
        else:
            if not all([b.pos[1] == self.candidate.positions[0].pos[1] for b in
                        self.candidate.positions]):
                return False

        # Make sure all letters are placed in-bounds
        for bp in self.candidate.positions:
            if any([bp.pos[0] < 0, bp.pos[0] > len(self.board),
                    bp.pos[1] < 0, bp.pos[1] > len(self.board[0])]):
                return False

        # If it's the first turn, no need to hook for valid moves
        hooked = not self.history
        if hooked:
            for bp in self.candidate.positions:
                if bp.pos == (7, 7):
                    break
            else:
                return False    # First turn but doesn't cover middle square

        word_multiplier = 1
        lx, ly = self.candidate.positions[0].pos
        for bpos in self.candidate.positions:
            x, y = bpos.pos
            # Position already occupied
            if self.board[x][y] not in board.empty_locations:
                return False

            # If tiles got skipped in letter placement, make sure they contain
            # letters and add them to the score
            if self.candidate.horizontal and y - ly > 1:
                hooked = True
                for i in xrange(ly + 1, y):
                    existing = self.board[x][i]
                    if existing in board.empty_locations:
                        return False

                    letter_score = letters.letter_scores.get(existing, 0)
                    self.candidate.score += letter_score
            elif not self.candidate.horizontal and x - lx > 1:
                hooked = True
                for i in xrange(lx + 1, x):
                    existing = self.board[i][y]
                    if existing in board.empty_locations:
                        return False

                    letter_score = letters.letter_scores.get(existing, 0)
                    self.candidate.score += letter_score

            # Process multipliers for placed letter and add to
            # score of candidate
            word_multiplier *= board.word_multipliers.get(self.board[x][y], 1)
            letter_multiplier = board.letter_multipliers.get(
                self.board[x][y], 1)

            letter_score = letters.letter_scores.get(bpos.letter, 0)
            self.candidate.score += letter_score * letter_multiplier

            self.board[x][y] = bpos.letter
            lx, ly = x, y

        prefix = self.__get_prefix(self.candidate.positions[0].pos,
                                   self.candidate.horizontal)
        suffix = self.__get_suffix(self.candidate.positions[-1].pos,
                                   self.candidate.horizontal)

        # Bridging also counts as hooking
        hooked |= bool(prefix) or bool(suffix)

        # Add prefix and suffix to candidate score, then multiply the whole
        # thing by the word multiplier
        for l in prefix:
            self.candidate.score += letters.letter_scores.get(l, 0)
        for l in suffix:
            self.candidate.score += letters.letter_scores.get(l, 0)
        self.candidate.score *= word_multiplier

        x, y = self.candidate.positions[0].pos
        lx, ly = self.candidate.positions[-1].pos

        # Construct the word that makes up the play
        if self.candidate.horizontal:
            body = ''.join(
                [self.board[x][y + i] for i in xrange(0, ly - y + 1)])
        else:
            body = ''.join(
                [self.board[x + i][y] for i in xrange(0, lx - x + 1)])
        word = '%s%s%s' % (prefix, body, suffix)

        # Not a valid play
        if word.upper() not in lexicon_set.global_set:
            return False

        # Bingo! - all 7 letters in rack used
        if len(self.candidate.positions) >= 7:
            self.candidate.score += 50

        cross = self.__check_crosses()
        if not cross:
            return hooked
        elif cross == -1:
            return False
        elif cross == 1:
            return True
        else:
            raise Exception('Invalid return %d from __check_crosses' % cross)

    def remove_candidate(self):
        """
        Remove the current candidate move.
        """
        if self.game_over:
            return False

        for bpos in self.candidate.positions:
            x, y = bpos.pos
            self.board[x][y] = board.default_board[x][y]

        self.candidate = None
        return True

    def commit_candidate(self):
        """
        Commit the candidate move. This updates scores, draws new tiles for
        the player, ends the turn, and adds a new state to the game tree.
        """
        if self.game_over:
            return False

        # Use the appropriate tiles from the rack
        self.players[self.current_turn].use_letters(
            ''.join([bp.letter for bp in self.candidate.positions]))
        if len(self.bag) >= len(self.candidate.positions):
            self.candidate.drawn = [
                self.bag.pop(random.randint(0, len(self.bag) - 1))
                for _ in xrange(0, len(self.candidate.positions))]
        else:   # Put the rest of the bag in the rack
            self.candidate.drawn = self.bag[:]
            self.bag = []

        for letter in self.candidate.drawn:
            self.players[self.current_turn].rack.append(letter)
        self.players[self.current_turn].score += self.candidate.score

        newstate = StateNode(self.candidate)
        newstate.action = MoveTypes.Placed

        if not len(self.players[self.current_turn].rack) and not len(self.bag):
            self.game_over = True

        self.__commit_state(newstate)
        self.passes = 0

        return True

    def pass_turn(self):
        """
        Pass the current player's turn. This ends the current turn with no
        move and commits to the game tree.

        @return: True if the current turn is passable, False otherwise
        (e.g. candidate on board)
        """
        if self.candidate is not None or self.game_over:
            return False

        newstate = StateNode(None)
        newstate.action = MoveTypes.Pass

        self.__commit_state(newstate)
        self.passes += 1
        if self.passes >= 6:
            self.game_over = True

        return True

    def exchange_tiles(self, letters):
        """
        Current player exchanges up to 7 letters with the bag. If there are
        not enough letters in the bag to exchange, this method will not do
        anything. Otherwise, the letters are exchanged and the move is
        committed to the game tree.

        @param letters: Letters to exchange
        @return: True if everything was valid, False if any errors were
        encountered.
        """
        if len(self.bag) < len(
                letters) or self.candidate is not None or self.game_over:
            return False

        self.candidate = move.Move()
        holder = []
        rack = self.players[self.current_turn].rack
        for letter in letters:
            try:
                holder.append(rack.pop(rack.index(letter)))
            except ValueError:
                rack += holder
                self.candidate = None
                return False

        self.candidate.drawn = [
            self.bag.pop(random.randint(0, len(self.bag) - 1)) for _ in
            xrange(0, len(letters))]
        rack += self.candidate.drawn
        self.bag += holder

        newstate = StateNode(self.candidate)
        newstate.action = MoveTypes.Exchange

        self.__commit_state(newstate)
        self.passes += 1
        if self.passes >= 6:
            self.game_over = True

        return True

    def __commit_state(self, state):
        state.previous = self.history

        self.history = state
        self.current_turn += 1
        self.current_turn %= len(self.players)

        self.candidate = None

    def __get_prefix(self, pos, horizontal):
        """
        Returns the prefix the leads up to the given position.

        @param pos: Tuple of position on board to check for a prefix before.
        @param horizontal: Boolean value to set which direction to look in.
        @return: Prefix preceding the given position on the board.
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

        # If the end/beginning of the word lies on an edge, no need
        # to check for suffix/prefix.
        if (y + i >= len(self.board[x]) or y + i < 0) if horizontal else \
            (x + i >= len(self.board) or x + i < 0):
            return sub

        l = self.board[x][y + i] if horizontal else self.board[x + i][y]
        while l not in board.empty_locations:
            sub.append(l)
            i += -1 if pre else 1
            if y + i >= len(self.board[x]) if horizontal else x + i >= len(
                    self.board):
                break
            l = self.board[x][y + i] if horizontal else self.board[x + i][y]

        if pre:
            sub.reverse()

        return sub

    def __check_crosses(self):
        """
        Check that all crosses created by the candidate move are valid. Calling
        this method will also update the score value of the candidate move.

        @return: 1 if crosses exist, 0 if no crosses, and -1 if
        invalid crosses exist
        """
        if not self.history:    # First turn, no crosses possible
            return 0

        crosses = 0
        for bpos in self.candidate.positions:
            x, y = bpos.pos
            prefix = self.__get_prefix(bpos.pos, not self.candidate.horizontal)
            suffix = self.__get_suffix(bpos.pos, not self.candidate.horizontal)

            cross = '%s%s%s' % (prefix, bpos.letter, suffix)
            if len(cross) > 1:
                if cross.upper() not in lexicon_set.global_set:
                    return -1

                crosses = 1
                subscore = 0

                for l in prefix:
                    subscore += letters.letter_scores.get(l, 0)
                for l in suffix:
                    subscore += letters.letter_scores.get(l, 0)

                letter_score = letters.letter_scores.get(bpos.letter, 0)
                letter_multiplier = board.letter_multipliers.get(
                    board.default_board[x][y], 1)

                subscore += letter_score * letter_multiplier

                subscore *= board.word_multipliers.get(
                    board.default_board[x][y], 1)

                self.candidate.score += subscore

        return crosses
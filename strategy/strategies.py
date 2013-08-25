__author__ = 'Jacky'

from copy import deepcopy
from collections import namedtuple

from engine.game import ScrabbleGame
from engine import board

from lexicon.gaddag import GaddagState


MoveAlias = namedtuple('MoveAlias', 'word, x, y, horizontal, score')


class StrategyBase(object):
    """
    Base class for strategies.
    """

    def __init__(self, game):
        """
        Create a new static scrabble strategy for a specific game.

        :param ScrabbleGame game: The ScrabbleGame for the strategy
        """
        self.game = game

    def find_anchors(self, coord, horizontal):
        """
        Compute anchor squares for a given row or column.

        :param int coord: Row or column number to compute.
        :param bool horizontal: True for a row, False for a column.

        :returns: Anchor squares on the given row/column as a list of
        integers as indexes of the anchors within the row/column.
        """
        if horizontal:
            line = ''.join(self.game.board[coord])
        else:
            line = ''.join([row[coord] for row in self.game.board])

        def next_occupied(j):
            j += 1
            while j < len(line):
                letter = line[j]
                if letter not in board.empty_locations:
                    return j
                j += 1

            return j

        def is_anchor(j):
            if line[j] not in board.empty_locations:
                return False

            # Look left/up, if possible
            if j > 0:
                if line[j - 1] not in board.empty_locations:
                    return True

            # Look right/down, if possible
            if j < len(line) - 1:
                if line[j + 1] not in board.empty_locations:
                    return True

            # Look up/left, if possible
            if horizontal and coord > 0:
                if self.game.board[coord - 1][j] not in board.empty_locations:
                    return True
            elif not horizontal and coord > 0:
                if self.game.board[j][coord - 1] not in board.empty_locations:
                    return True

            # Look down/right, if possible
            if horizontal and coord < len(self.game.board) - 1:
                if self.game.board[coord + 1][j] not in board.empty_locations:
                    return True
            elif not horizontal and coord < len(self.game.board[j]) - 1:
                if self.game.board[j][coord + 1] not in board.empty_locations:
                    return True

            return False

        anchors = []
        i = 0

        while i < len(line):
            if is_anchor(i):
                anchors.append(i)
                i = next_occupied(i)

            i += 1

        return anchors

    def generate_moves(self):
        """
        Generates all possible moves for the game at this turn.

        Yields:
            move:
                A valid Scrabble move for this turn. Will continue generating
                moves until all possibilities are exhausted.
        """
        pass


class StaticScoreStrategy(StrategyBase):
    """
    Strategy to maximize the score every turn, no lookahead.
    """
    def __init__(self, game):
        super(StaticScoreStrategy, self).__init__(game)

        # x, y coordinates of the anchor square for the move being generated
        self.cur_anchor = -1

        # Direction currently generating in
        self.horizontal = True
        self.coord = -1

        self.moves = set()
        self.row = []
        self.anchors = []
        self.cross_sets = []

    def generate_moves(self):
        def move_mapper(move):
            check = self.game.set_candidate(move.word, (move.x, move.y), move.horizontal)
            if not check:
                print move
                if move.horizontal:
                    print self.find_anchors(move.x, True)
                else:
                    print self.find_anchors(move.y, False)
                assert check    # sanity check

            check = self.game.validate_candidate()
            if not check:
                print move
                if move.horizontal:
                    print self.find_anchors(move.x, True)
                else:
                    print self.find_anchors(move.y, False)
                assert check    # sanity check

            score = self.game.candidate.score
            self.game.remove_candidate()

            return move._replace(score=score)

        self.moves = set()
        if self.game.history is None:
            # Special case for first move
            self.horizontal = True
            self.row = self.game.board[7]
            self.coord = 7

            self.anchors = [7]
            self.cross_sets = self.game.vertical_crosses[7]

            rack = self.game.players[self.game.current_turn].rack
            self.cur_anchor = 0

            self.gen(7, 0, '', rack, self.game.gaddag.root)

            self.horizontal = False
            self.row = [row[7] for row in self.game.board]
            self.cross_sets = [row[7] for row in self.game.horizontal_crosses]

            self.gen(7, 0, '', rack, self.game.gaddag.root)

            return map(move_mapper, self.moves)

        self.horizontal = True
        for i, row in enumerate(self.game.board):
            self.row = row
            self.coord = i

            self.anchors = self.find_anchors(i, True)
            self.cross_sets = self.game.vertical_crosses[i]

            rack = self.game.players[self.game.current_turn].rack

            for j, anchor in enumerate(self.anchors):
                self.cur_anchor = j

                self.gen(anchor, 0, '', rack, self.game.gaddag.root)

        self.horizontal = False
        columns = [[row[i] for row in self.game.board] for i in xrange(0, len(self.game.board[0]))]
        for i, col in enumerate(columns):
            self.row = col
            self.coord = i

            self.anchors = self.find_anchors(i, False)
            self.cross_sets = [row[i] for row in self.game.horizontal_crosses]

            rack = self.game.players[self.game.current_turn].rack

            for j, anchor in enumerate(self.anchors):
                self.cur_anchor = j

                self.gen(anchor, 0, '', rack, self.game.gaddag.root)

        return map(move_mapper, self.moves)

    def record_play(self, leftmost, word):
        """
        Record a move candidate.

        :param str word: The letters of the move to record.
        :param int coord: The leftmost coordinate of the move.
        """
        if self.horizontal:
            self.moves.add(MoveAlias(word=word, x=self.coord,
                                     y=leftmost, horizontal=self.horizontal, score=0))
        else:
            self.moves.add(MoveAlias(word=word, x=leftmost,
                                     y=self.coord, horizontal=self.horizontal, score=0))

    def gen(self, leftmost, pos, word, rack, state):
        """
        :param pos:
        :param word:
        :param rack:
        :param state:
        :type state: GaddagState
        """
        coord = self.anchors[self.cur_anchor] + pos
        cur_letter = self.row[coord]

        if cur_letter not in board.empty_locations:
            self.go_on(leftmost, pos, cur_letter, word, rack, state.arcs.get(cur_letter), state)
        elif len(rack) > 0:
            # Because of the way the algorithm is implemented, the letters
            # we can put on this square is just the intersection of the
            # orthogonal cross set and the rack. Outgoing arcs from the
            # GADDAG state don't matter
            valid_letters = set(rack)
            cross_set = self.cross_sets[coord]

            if cross_set is not None:
                valid_letters &= cross_set

            for letter in valid_letters:
                new_rack = deepcopy(rack)
                new_rack.remove(letter)

                self.go_on(leftmost, pos, letter, word, new_rack, state.arcs.get(letter), state)

            if ' ' in rack:
                # A blank tile can be any letter in the orthogonal cross set
                if cross_set is None:
                    cross_set = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

                for letter in cross_set:
                    new_rack = deepcopy(rack)
                    new_rack.remove(' ')
                    self.go_on(leftmost, pos, letter, word, new_rack, state.arcs.get(letter), state)

    def go_on(self, leftmost, pos, letter, word, rack, new_arc, old_arc):
        """
        :param pos:
        :param str letter:
        :param str word:
        :param list rack:
        :param new_arc:
        :param old_arc:

        :type new_arc: GaddagState or None
        :type old_arc: GaddagState
        """
        coord = self.anchors[self.cur_anchor] + pos
        if coord < 0:
            return

        if pos <= 0:
            if self.row[coord] in board.empty_locations:
                word = '%s%s' % (letter, word)

                if pos < 0 and coord < leftmost:
                    leftmost = coord

            left_unoccupied = coord - 1 < 0 or self.row[coord - 1] in board.empty_locations
            if letter in old_arc.letter_set and left_unoccupied:
                # TODO: remove redundancy with overruning previous anchor
                self.record_play(leftmost, word)

            if new_arc is not None:
                # Shift direction if possible
                coord = self.anchors[self.cur_anchor] + 1
                if '|' in new_arc.arcs and left_unoccupied and coord < len(self.row):
                    self.gen(leftmost, 1, word, rack, new_arc.arcs['|'])

                if coord > 0:
                    # Keep going left
                    self.gen(leftmost, pos - 1, word, rack, new_arc)
        else:
            # Moving right
            if self.row[coord] in board.empty_locations:
                word = '%s%s' % (word, letter)
            unoccupied = coord + 1 >= len(self.row) or self.row[coord + 1] in board.empty_locations

            if letter in old_arc.letter_set and unoccupied:
                self.record_play(leftmost, word)
            if new_arc is not None and coord + 1 < len(self.row):
                self.gen(leftmost, pos + 1, word, rack, new_arc)

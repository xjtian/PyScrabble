__author__ = 'Jacky'

from copy import deepcopy
import pdb

from engine.game import ScrabbleGame
from engine.move import Move
from engine import board

from lexicon.gaddag import GaddagState


class StrategyBase(object):
    """
    Base class for strategies.
    """

    def __init__(self, game):
        """
        Create a new static scrabble strategy for a specific game.

        Parameters:
            game:
                The ScrabbleGame for the strategy.

        @type game: ScrabbleGame
        """
        self.game = game

        # (int * int) set of which board positions are anchors
        self.anchors = set()

    def find_anchors(self):
        """
        Computes the set of all anchor squares for the ScrabbleGame
        associated with this strategy. Sets self.anchors.

        Returns:
            anchors:
                (int * int) set of anchor positions. Same object
                as self.anchors.
        """
        for row in xrange(0, len(self.game.board)):
            for col in xrange(0, len(self.game.board[row])):
                if self.game.board[row][col] not in board.empty_locations:
                    # Occupied tile, so adjacent empties are anchors

                    # Check above position
                    if row - 1 >= 0 and self.game.board[row - 1][col] in board.empty_locations:
                        self.anchors.add((row - 1, col))

                    # Check below position
                    if row + 1 < len(self.game.board):
                        if self.game.board[row + 1][col] in board.empty_locations:
                            self.anchors.add((row + 1, col))

                    # Check left position
                    if col - 1 >= 0 and self.game.board[row][col - 1] in board.empty_locations:
                        self.anchors.add((row, col - 1))

                    # Check right position
                    if col + 1 < len(self.game.board[row]):
                        if self.game.board[row][col + 1] in board.empty_locations:
                            self.anchors.add((row, col + 1))

        return self.anchors

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
        self.a_x = -1
        self.a_y = -1

    def generate_moves(self):
        self.find_anchors()

        if self.game.history is None:
            self.anchors.add((7, 7))

        rack = self.game.players[self.game.current_turn].rack
        gen_moves = set()
        for pos in self.anchors:
            self.a_x, self.a_y = pos
            gen_moves |= self.move_finder(0, Move(), rack, self.game.gaddag.root)

            m = Move()
            m.horizontal = False
            gen_moves |= self.move_finder(0, m, rack, self.game.gaddag.root)

        gen_moves = list(gen_moves)
        for move in gen_moves:
            move.sort_letters()

            success = self.game.set_candidate_move(move)
            if not success:
                pdb.set_trace()
                assert success  # Sanity check

            success = self.game.validate_candidate()
            if not success:
                pdb.set_trace()
                assert success  # Sanity check

            self.game.remove_candidate()

        return gen_moves

    def move_finder(self, pos, move, rack, state):
        """
        Recursive move finding algorithm that generates all valid plays
        given a Scrabble game.

        Parameters:
            pos:
                Integer value indicating which square the algorithm is
                looking at relative to the original anchor (0 is the anchor).
            move:
                Move candidate that has been built so far.
            rack:
                Player rack at this point of the move generation.
            state:
                The GADDAG state that the algorithm is currently at.

        @type move: Move
        @type state: GaddagState
        @type pos: int
        @type rack: list
        """
        # TODO: blanks

        # REMEMBER: when generating to the left, you MUST switch
        # directions before you can make any conclusion about the
        # validity of the current move.

        # Base cases
        if len(rack) == 0:
            return set()

        x, y = self.__pos_arithmetic(self.a_x, self.a_y, pos, move.horizontal)
        if x < 0 or x >= len(self.game.board):
            return set()
        if y < 0 or y >= len(self.game.board[x]):
            return set()

        cur_letter = self.game.board[x][y]
        if cur_letter not in board.empty_locations:
            # This position is occupied. Jump to the next GADDAG state and
            # see if it's possible to have any words

            if cur_letter not in state.arcs:
                # There are no possible extensions
                return set()

            next_state = state.arcs[cur_letter]
            if pos <= 0:
                # Generating to the left, so let's try to keep moving left
                left_result = self.move_finder(pos - 1, deepcopy(move), deepcopy(rack), next_state)

                # What if we switched directions?
                # Look for a delimiter first!
                right_result = set()
                if '|' in next_state.arcs:
                    next_state = next_state.arcs['|']
                    right_result = self.move_finder(1, deepcopy(move), deepcopy(rack), next_state)

                # All moves possible from this branch of the decision tree
                # is the union of all 3 of these sets - keep going left,
                # start going right, and stop right here
                return left_result | right_result
            else:
                # Generating to the right, so changing to the left is not
                # an option. Only option is to keep going right!
                # Can we end the move right here on this occupied spot?
                cur_result = set()
                if cur_letter in state.letter_set:
                    cur_result.add(deepcopy(move))

                right_result = self.move_finder(pos + 1, deepcopy(move), deepcopy(rack), next_state)

                return right_result | cur_result

        else:
            # This position is empty, so let's see what we can play here
            # If we put a letter down here, it must be in the current
            # state's arcs, the perpendicular cross set if it exists,
            # and the rack.
            if move.horizontal:
                cross_set = self.game.vertical_crosses[x][y]
            else:
                cross_set = self.game.horizontal_crosses[x][y]
            rack_set = set(rack)

            if cross_set is not None:
                valid_letters = set(state.arcs.keys()) & cross_set & rack_set
            else:
                valid_letters = set(state.arcs.keys()) & rack_set

            if pos <= 0:
                # Generating to the left, so let's try to keep moving left.
                left_result = set()
                for letter in valid_letters:
                    assert(letter in rack and letter in state.arcs)     # Sanity check
                    r = deepcopy(rack)
                    r.remove(letter)

                    m = deepcopy(move)
                    m.add_letter(letter, (x, y))

                    left_result |= self.move_finder(pos - 1, m, r, state.arcs[letter])

                # Now let's try to switch directions and generate to the right.
                # Look for the delimiter, go to that state, and set pos to 1.
                right_result = set()
                if '|' in state.arcs:
                    next_state = state.arcs['|']
                    m, r = deepcopy(move), deepcopy(rack)
                    right_result = self.move_finder(1, m, r, next_state)

                return left_result | right_result

            else:
                # Generating to the right
                # Can we end the move right here?
                if cross_set is not None:
                    valid_letters = cross_set & state.letter_set & rack_set
                else:
                    valid_letters = state.letter_set & rack_set

                cur_result = set()
                for letter in valid_letters:
                    m = deepcopy(move)
                    m.add_letter(letter, (x, y))

                    cur_result.add(m)

                # Can we keep going to the right?
                recursive_result = set()
                for letter in valid_letters:
                    assert(letter in rack and letter in state.arcs)     # Sanity check
                    r = deepcopy(rack)
                    r.remove(letter)

                    m = deepcopy(move)
                    m.add_letter(letter, (x, y))

                    recursive_result |= self.move_finder(pos + 1, m, r, state.arcs[letter])

                return recursive_result | cur_result

    def __pos_arithmetic(self, x, y, value, horizontal):
        if horizontal:
            return x, y + value
        else:
            return x + value, y

__author__ = 'Jacky'

from copy import deepcopy

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
        x, y = self.__pos_arithmetic(self.a_x, self.a_y, pos, move.horizontal)

        cur_letter = self.game.board[x][y]
        if cur_letter not in board.empty_locations:
            # This position is occupied. Jump to the next GADDAG state and
            # see if it's possible to have any words

            # Can we end the move right here on this occupied spot?
            if cur_letter in state.letter_set:
                cur_result = {deepcopy(move)}
            else:
                cur_result = set()

            if cur_letter not in state.arcs:
                # There are no possible extensions
                return cur_result

            next_state = state.arcs[cur_letter]
            if pos <= 0:
                # Generating to the left, so let's try to keep moving left
                left_result = self.move_finder(pos - 1, deepcopy(move), deepcopy(rack), next_state)

                # What if we switched directions?
                right_result = self.move_finder(1, deepcopy(move), deepcopy(rack), next_state)

                # All moves possible from this branch of the decision tree
                # is the union of all 3 of these sets - keep going left,
                # start going right, and stop right here
                return left_result | right_result | cur_result
            else:
                # Generating to the right, so changing to the left is not
                # an option. Only option is to keep going right!
                # TODO: look for a delimiter first!
                right_result = self.move_finder(pos + 1, deepcopy(move), deepcopy(rack), next_state)

                return right_result | cur_result

        else:
            # This position is empty, so let's see what we can play here
            # Can we end the move right here?
            cur_result = set()
            for letter in rack:
                if letter in state.letter_set:
                    m = deepcopy(move)
                    m.add_letter(letter, (x, y))

                    cur_result.add(m)

            if pos <= 0:
                # Generating to the left, so let's try to keep moving left
                for i, letter in enumerate(rack):
                    if letter in state.arcs:
                        # Add this letter to the move, remove from rack and recurse
                        r = deepcopy(rack)
                        r.pop(i)

                        m = deepcopy(move)
                        m.add_letter(letter, (x, y))

                        left_result = self.move_finder(pos - 1, m, r, state.arcs[letter])

                # TODO: look for delimiter and start moving right
            else:
                # Generating to the right, can only keep going
                # TODO: implement this
                pass

    def __pos_arithmetic(self, x, y, value, horizontal):
        if horizontal:
            return x, y + value
        else:
            return x + value, y

__author__ = 'Jacky'

from engine.game import ScrabbleGame
from engine import board


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

    def gen(self, word, rack, state):
        pass

    def go_on(self, pos, letter, word, rack, new_arc, old_arc):
        pass

    def __pos_arithmetic(self, x, y, value, horizontal):
        if horizontal:
            return x, y + value
        else:
            return x + value, y

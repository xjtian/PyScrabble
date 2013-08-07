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

        anchors = []
        for i, letter in enumerate(line):
            if i == 0:
                continue

            if letter not in board.empty_locations:
                # Look left
                left = line[i - 1]
                if left in board.empty_locations:
                    anchors.append(i - 1)

        # Handle 2 special cases - totally empty line and full line
        # except last position. Anchor is leftmost empty.
        if len(anchors) == 0:
            if line[0] in board.empty_locations:
                anchors.append(0)
            elif line[-1] in board.empty_locations:
                anchors.append(len(line) - 1)

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

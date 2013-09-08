__author__ = 'Jacky'

default_board = [
    list('#..2...#...2..#'),
    list('.@...3...3...@.'),
    list('..@...2.2...@..'),
    list('2..@...2...@..2'),
    list('....@.....@....'),
    list('.3...3...3...3.'),
    list('..2...2.2...2..'),
    list('#..2...*...2..#'),
    list('..2...2.2...2..'),
    list('.3...3...3...3.'),
    list('....@.....@....'),
    list('2..@...2...@..2'),
    list('..@...2.2...@..'),
    list('.@...3...3...@.'),
    list('#..2...#...2..#')
]

word_multipliers = {'#': 3, '@': 2, '*': 2, '.': 1}
letter_multipliers = {'3': 3, '2': 2, '.': 1}

empty_locations = {'#', '@', '.', '3', '2', '*'}


class BoardPosition(object):
    def __init__(self, letter, pos):
        self.pos = pos
        self.letter = letter

    def __eq__(self, other):
        return self.pos == other.pos and self.letter == other.letter

    def __hash__(self):
        return hash((self.pos, self.letter))


def get_prefix(board, x, y, horizontal):
    """
    Returns the prefix leading up to the given position on the board (x, y).

    Parameters:
        board:
            The Scrabble board to perform the search on.
        x:
            x-coordinate (0-based row) of the square to search for.
        y:
            y-coordinate (0-based column) of the square to search for.
        horizontal:
            True to search horizontally, False to search vertically.

    Returns:
        The prefix leading up to the given position as a string. Will be
        empty if no prefix exists.
    """
    return ''.join(__pre_suff_helper(board, x, y, horizontal, True))


def get_suffix(board, x, y, horizontal):
    """
    Returns the suffix leading up to the given position on the board (x, y).

    Parameters:
        board:
            The Scrabble board to perform the search on.
        x:
            x-coordinate (0-based row) of the square to search for.
        y:
            y-coordinate (0-based column) of the square to search for.
        horizontal:
            True to search horizontally, False to search vertically.

    Returns:
        The suffix after the given position as a string. Will be empty
        if no suffix exists.
    """
    return ''.join(__pre_suff_helper(board, x, y, horizontal, False))


def __pre_suff_helper(s_board, x, y, horizontal, pre):
    """
    Helper function for get_prefix and get_suffix, which are basically
    friendlier aliases. Note this function returns an array, not a string.
    """
    i = -1 if pre else 1
    sub = []

    # If the end/beginning of the word lies on an edge, no need
    # to check for suffix/prefix.
    if (y + i >= len(s_board[x]) or y + i < 0) if horizontal \
            else (x + i >= len(s_board) or x + i < 0):
        return sub

    l = s_board[x][y + i] if horizontal else s_board[x + i][y]
    while l not in empty_locations:
        sub.append(l)
        i += -1 if pre else 1
        if (y + i >= len(s_board[x]) if horizontal else x + i >= len(s_board))\
                or (y + i < 0 if horizontal else x + i < 0):
            break
        l = s_board[x][y + i] if horizontal else s_board[x + i][y]

    if pre:
        sub.reverse()

    return sub


__author__ = 'Jacky'

import re
from copy import deepcopy

from engine.board import default_board, empty_locations
from engine.move import BoardPosition, Move


def parse_scenario(filename):
    with open(filename, 'r') as f:
        lines = map(lambda s: s.rstrip(), f.readlines())

    lines = filter(lambda s: len(s) > 0 and not s.startswith('!:'), lines)
    i = 0
    while i < len(lines):
        line = lines[i]
        board = []
        if line != 'BEGIN BOARD':
            raise IOError('Improperly formatted scenario file, line %d: expected BEGIN BOARD.' % i)

        i += 1
        line = lines[i]
        while line != 'END BOARD':
            board.append(list(line))
            i += 1
            line = lines[i]

        if len(board) == 0:
            board = deepcopy(default_board)

        i += 1
        candidate_letters = lines[i]

        i += 1
        r_match = re.match(r'^(\d+), (\d+)$', lines[i])
        if not r_match:
            raise IOError('Improperly formatted scenario file, line %d: candidate position.' % i)
        candidate_pos = tuple(map(int, r_match.groups()))

        i += 1
        if lines[i] == 'H':
            candidate_dir = True
        elif lines[i] == 'V':
            candidate_dir = False
        else:
            raise IOError('Improperly formatted scenario file, line %d: candidate direction.' % i)

        i += 1
        j = int(lines[i])
        if j == 1:
            exp_result = True
        elif j == 0:
            exp_result = False
        else:
            raise IOError('Improperly formatted scenario file, line %d: expected result.' % i)

        exp_score = -1
        if exp_result:
            i += 1
            exp_score = int(lines[i])

        i += 1  # Increment before beginning of next iteration
        candidate = Move()

        offset = 0
        for j, letter in enumerate(candidate_letters):
            if candidate_dir:
                x, y = candidate_pos[0], candidate_pos[1] + j + offset
                while y < len(board[x]) and board[x][y] not in empty_locations:
                    offset += 1
                    y += 1
                candidate.positions.append(BoardPosition(letter, (x, y)))
            else:
                x, y = candidate_pos[0] + j + offset, candidate_pos[1]
                while x < len(board) and board[x][y] not in empty_locations:
                    offset += 1
                    x += 1
                candidate.positions.append(BoardPosition(letter, (x, y)))
        candidate.horizontal = candidate_dir

        yield {'board': board, 'candidate': candidate, 'result': exp_result, 'score': exp_score}


def parse_cross_set(filename):
    with open(filename, 'r') as f:
        lines = map(lambda s: s.rstrip(), f.readlines())

    lines = filter(lambda s: len(s) > 0 and not s.startswith('!:'), lines)
    i = 0
    while i < len(lines):
        line = lines[i]
        board = []
        if line != 'BEGIN BOARD':
            raise IOError('Improperly formatted scenario file, line %d: expected BEGIN BOARD.' % i)

        i += 1
        line = lines[i]
        while line != 'END BOARD':
            board.append(list(line))
            i += 1
            line = lines[i]

        if len(board) == 0:
            board = deepcopy(default_board)

        i += 1
        candidate_letters = lines[i]

        i += 1
        r_match = re.match(r'^(\d+), (\d+)$', lines[i])
        if not r_match:
            raise IOError('Improperly formatted scenario file, line %d: candidate position.' % i)
        candidate_pos = tuple(map(int, r_match.groups()))

        i += 1
        if lines[i] == 'H':
            candidate_dir = True
        elif lines[i] == 'V':
            candidate_dir = False
        else:
            raise IOError('Improperly formatted scenario file, line %d: candidate direction.' % i)

        i += 1  # Increment before beginning of next iteration
        line = lines[i]
        if line != 'BEGIN CROSSES':
            raise IOError('Improperly formatted scenario file, line %d: expected BEGIN CROSSES.' % i)

        i += 1
        line = lines[i]
        crosses = []
        while line != 'END CROSSES':
            cross = {}

            r_match = re.match(r'^(\d+), (\d+)$', line)
            if not r_match:
                raise IOError('Improperly formatted scenario file, line %d: cross position.' % i)

            cross['x'], cross['y'] = tuple(map(int, r_match.groups()))

            i += 1
            line = lines[i]
            if line[0] == '-':
                cross['horizontal'] = True
            elif line[0] == '|':
                cross['horizontal'] = False
            else:
                raise IOError('Improperly formatted scenario file, line %d: cross direction.' % i)

            i += 1
            line = lines[i]
            cross['letters'] = set(line)

            crosses.append(cross)
            i += 1
            line = lines[i]

        candidate = Move()

        offset = 0
        for j, letter in enumerate(candidate_letters):
            if candidate_dir:
                x, y = candidate_pos[0], candidate_pos[1] + j + offset
                while y < len(board[x]) and board[x][y] not in empty_locations:
                    offset += 1
                    y += 1
                candidate.positions.append(BoardPosition(letter, (x, y)))
            else:
                x, y = candidate_pos[0] + j + offset, candidate_pos[1]
                while x < len(board) and board[x][y] not in empty_locations:
                    offset += 1
                    x += 1
                candidate.positions.append(BoardPosition(letter, (x, y)))
        candidate.horizontal = candidate_dir

        yield {'board': board, 'candidate': candidate, 'crosses': crosses}


def main():
    for d in parse_scenario('./engine/test/scenarios/test_scenario.txt'):
        print d


if __name__ == '__main__':
    main()

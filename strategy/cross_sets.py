__author__ = 'Jacky'

from engine import board


def redo_crosses(move, h_cross, v_cross, s_board, gaddag):
    """
    Given a board and move candidate, generates the changed cross sets
    resulting from the move in-place.

    Parameters:
        move:
            Move object to generate crosses for.
        h_cross:
            2D array of horizontal cross sets that correspond to the board.
            This parameter is altered in-place.
        v_cross:
            2D array of vertical cross sets that correspond to the board.
            This parameter is altered in-place.
        s_board:
            Scrabble board to generate cross sets for.
        gaddag:
            GADDAG of the lexicon to use.

    Returns:
        (h_cross, v_cross):
            2D arrays of horizontal and vertical cross sets, respectively.
            These are the same objects as passed into the function.
    """
    move.sort_letters()
    fx, fy = move.positions[0].pos
    lx, ly = move.positions[-1].pos

    # Clear the cross-sets of newly-occupied positions
    for bpos in move.positions:
        x, y = bpos.pos
        h_cross[x][y] = set()
        v_cross[x][y] = set()

    # IMPORTANT: assumes move tiles are in sorted order already
    # Build the main body of the move word - FIXED: include skipped
    # board tiles as well
    move_word = ''
    i = 0
    if move.horizontal:
        for y in xrange(fy, ly + 1):
            if s_board[fx][y] in board.empty_locations:
                move_word += move.positions[i].letter
                i += 1
            else:
                move_word += s_board[fx][y]
    else:
        for x in xrange(fx, lx + 1):
            if s_board[x][fy] in board.empty_locations:
                move_word += move.positions[i].letter
                i += 1
            else:
                move_word += s_board[x][fy]

    move_suffix = board.get_suffix(s_board, lx, ly, move.horizontal)
    move_prefix = board.get_prefix(s_board, fx, fy, move.horizontal)
    word = move_word + move_suffix + move_prefix

    # Parallel letter sets off first/last letters in move
    # ---------------------------------------------------
    # Are these mid-sets?

    mid_checker = move.positions[0]
    mid_suffix = move_word[1:] + move_suffix

    left, right = mid_cross(mid_checker, move_prefix, mid_suffix, not move.horizontal, s_board, gaddag)
    left_mid = left is not None
    right_mid = right is not None

    if left_mid and not right_mid:
        _, right = gaddag.cross_sets(word)
    elif not left_mid and right_mid:
        left, _ = gaddag.cross_sets(word)
    elif not left_mid and not right_mid:
        left, right = gaddag.cross_sets(word)

    if move.horizontal:
        if fy - len(move_prefix) > 0:
            h_cross[fx][fy - len(move_prefix) - 1] = left
        if ly + len(move_suffix) < len(s_board[lx]) - 1:
            h_cross[lx][ly + len(move_suffix) + 1] = right
    else:
        if fx - len(move_prefix) > 0:
            v_cross[fx - len(move_prefix) - 1][fy] = left
        if lx + len(move_suffix) < len(s_board) - 1:
            v_cross[lx + len(move_suffix) + 1][ly] = right

    for bp in move.positions:
        x, y = bp.pos

        prefix = board.get_prefix(s_board, x, y, not move.horizontal)
        suffix = board.get_suffix(s_board, x, y, not move.horizontal)

        # Are either of the cross sets mid-crosses?
        left, right = mid_cross(bp, prefix, suffix, move.horizontal, s_board, gaddag)
        left_mid = left is not None
        right_mid = right is not None

        word = prefix + bp.letter + suffix

        if left_mid and not right_mid:
            _, right = gaddag.cross_sets(word)
        elif not left_mid and right_mid:
            left, _ = gaddag.cross_sets(word)
        elif not left_mid and not right_mid:
            left, right = gaddag.cross_sets(word)

        # Assign the new cross-sets here
        if move.horizontal:
            if x - len(prefix) > 0:
                if s_board[x - len(prefix) - 1][y] in board.empty_locations:
                    v_cross[x - len(prefix) - 1][y] = left

            if x + len(suffix) < len(s_board) - 1:
                if s_board[x + len(suffix) + 1][y] in board.empty_locations:
                    v_cross[x + len(suffix) + 1][y] = right
        else:
            if y - len(prefix) > 0:
                if s_board[x][y - len(prefix) - 1] in board.empty_locations:
                    h_cross[x][y - len(prefix) - 1] = left

            if y + len(suffix) < len(s_board[x]) - 1:
                if s_board[x][y + len(suffix) + 1] in board.empty_locations:
                    h_cross[x][y + len(suffix) + 1] = right


def mid_cross(bp, prefix, suffix, horizontal, s_board, gaddag):
    """
    Returns if the cross-set to be updated associated with the specified
    grid location is a mid-cross or not. Returns the cross-set if it is
    or None if it isn't.

    Parameters:
        bp:
            BoardPosition of the letter of the move being tested.
        prefix:
            Prefix leading up to this position.
        suffix:
            Suffix leading up to this position.
        horizontal:
            Whether the candidate is horizontal or not. Note this
            method will return the perpendicular cross-set to the value
            of this parameter.
        board:
            The board to generate the cross sets for.
        gaddag:
            The GADDAG of the lexicon to search within.

    Returns:
        (left_cross, right_cross):
            None if there is no mid-cross associated with the position
            and direction, or the cross-set if there is.
    """
    x, y = bp.pos
    left_cross, right_cross = None, None

    word = prefix + bp.letter + suffix

    # Check coord - prefix length - 2 to determine if middle cross on left/above
    # Check coord + suffix length + 2 to determine if middle cross on right/below
    if horizontal:
        mid_check = x - len(prefix) - 2
        if mid_check >= 0 and s_board[mid_check][y] not in board.empty_locations:
            # The left (above) cross is a mid-cross
            mid_prefix = board.get_prefix(s_board, mid_check + 1, y, False)

            left_cross = gaddag.mid_set(mid_prefix, word)

        mid_check = x + len(suffix) + 2
        if mid_check < len(s_board) and s_board[mid_check][y] not in board.empty_locations:
            # The right (below) cross is a mid-cross
            mid_suffix = board.get_suffix(s_board, mid_check - 1, y, False)

            right_cross = gaddag.mid_set(word, mid_suffix)
    else:
        mid_check = y - len(prefix) - 2
        if mid_check >= 0 and s_board[x][mid_check] not in board.empty_locations:
            # The left cross is a mid-cross
            mid_prefix = board.get_prefix(s_board, x, mid_check + 1, True)

            left_cross = gaddag.mid_set(mid_prefix, word)

        mid_check = y + len(suffix) + 2
        if mid_check < len(s_board[x]) and s_board[x][mid_check] not in board.empty_locations:
            # The right cross is a mid-cross
            mid_suffix = board.get_suffix(s_board, x, mid_check - 1, True)

            right_cross = gaddag.mid_set(word, mid_suffix)

    return left_cross, right_cross

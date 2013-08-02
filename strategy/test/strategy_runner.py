__author__ = 'jacky'

from string import letters
from engine.game import ScrabbleGame
from lexicon.lexicon_set import read_lexicon
from lexicon.gaddag import gaddag_from_file

from strategy.strategies import StaticScoreStrategy

game = ScrabbleGame()
strat = StaticScoreStrategy(game)
columns = letters[:len(game.board[0])].upper()

# Test using the fake wordlist and bag?
TEST = False


def ignore_err(fn):
    def decorator():
        try:
            fn()
        except ValueError:
            print '\nYou typed something wrong.\n'

    return decorator


def print_game():
    print '    ' + ' '.join(columns)
    for i, row in enumerate(game.board):
        print '%2d| %s' % (i, ' '.join(row))

    print '\nSCORES'
    scores = game.get_scores()
    for k, v in scores.items():
        print '%s: %d' % (k, v)

    info = game.current_player_info()

    print "\n%s's rack:" % info['name']
    print info['rack']


def start_game():
    name = raw_input('Enter player 1 name: ')
    game.add_player(name)

    name = raw_input('Enter player 2 name: ')
    game.add_player(name)

    game.start_game()


@ignore_err
def get_move():
    RE_INVALID = 'INVALID MOVE CANDIDATE\n'

    print '\nMenu:\n1. Play a move\n2. Exchange tiles\n3. Pass\n4. Generate Move'
    choice = int(raw_input('Please Choose: '))
    print

    if choice == 1:
        letters = raw_input('Enter the tiles you want to play: ').upper()
        x = int(raw_input('Row number: '))
        y = columns.index(raw_input('Column Letter: ').upper())
        h = raw_input('H for horizontal, V for vertical: ').upper()

        if game.set_candidate(letters, (x, y), h == 'H'):
            if game.validate_candidate():
                print '\n%s played %s at (%d, %d) for %d points\n' % (
                    game.current_player_info()['name'], letters, x, y, game.candidate.score)
                game.commit_candidate()
            else:
                print RE_INVALID
                game.remove_candidate()
                get_move()
        else:
            print RE_INVALID
            get_move()
    elif choice == 2:
        letters = raw_input('Enter the tiles you want to exchange: ').upper()

        if game.exchange_tiles(letters):
            print 'Tiles successfully exchanged'
        else:
            print 'Unable to exchange tiles. Try again\n'
            get_move()
    elif choice == 3:
        game.pass_turn()
    elif choice == 4:
        moves = strat.generate_moves()
        moves = sorted(moves, cmp=lambda x, y: cmp(x.score, y.score), reverse=True)

        for move in moves:
            print ''.join(map(lambda bp: bp.letter, move.positions))
            print move.score

        m = moves[0]
        m.sort_letters()
        pos = m.positions[0].pos
        letters = ''.join(map(lambda bp: bp.letter, m.positions))

        success = game.set_candidate(letters, pos, m.horizontal)
        assert success  # Sanity check
        success = game.validate_candidate()
        assert success  # Sanity check

        print '\n%s played %s at (%d, %d) for %d points\n' % (
            game.current_player_info()['name'], letters, pos[0], pos[1], game.candidate.score
        )
        game.commit_candidate(crosses=True)


def main():
    if TEST:
        WORDLIST = './wordlists/test_list1.txt'
        game.lexicon_set = read_lexicon(WORDLIST)
        game.gaddag = gaddag_from_file(WORDLIST)
        game.bag = list('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
                        'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD'
                        'EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
    else:
        WORDLIST = './wordlists/OSPD4_stripped.txt'
        game.lexicon_set = read_lexicon(WORDLIST)
        game.gaddag = gaddag_from_file(WORDLIST)

    start_game()
    while not game.game_over:
        print_game()
        get_move()

    print '\n-----Game Over!-----'
    print 'Final scores: '
    scores = game.get_scores()
    for k, v in scores.items():
        print '%s: %d' % (k, v)

    # This doesn't care about ties, but it'll do for now.
    winner = max(scores.items(), key=scores.get)
    print 'The winner was %s with %d points!' % (winner[0], winner[1])

if __name__ == '__main__':
    main()

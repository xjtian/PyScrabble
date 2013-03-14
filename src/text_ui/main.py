__author__ = 'jacky'

from string import letters
from engine.game import ScrabbleGame

game = ScrabbleGame()
columns = letters[:len(game.board[0])].upper()


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


def get_move():
    RE_INVALID = 'INVALID MOVE CANDIDATE\n'

    print '\nMenu:\n1. Play a move\n2. Exchange tiles\n3. Pass'
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


def main():
    start_game()
    while not game.game_over:
        print_game()
        get_move()

if __name__ == '__main__':
    main()

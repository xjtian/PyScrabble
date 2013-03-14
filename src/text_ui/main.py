__author__ = 'jacky'

from engine.game import ScrabbleGame

game = ScrabbleGame()


def print_game():
    for row in game.board:
        print ' '.join(row)

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


start_game()
print_game()

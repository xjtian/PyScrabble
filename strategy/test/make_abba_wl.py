__author__ = 'Jacky'

from itertools import product

with open('./wordlists/ABBA.txt', 'w') as f:
    for i in xrange(1, 6):
        for s in product('AB', repeat=i):
            f.write(''.join(s))
            f.write('\n')

__author__ = 'Jacky'

from itertools import permutations


# Generates all possible permutations of the string 'ABCDE' as
# wordlist1.
with open('./engine/test/wordlists/wordlist1.txt', 'w') as f:
    word = 'ABCDE'
    for i in xrange(2, len(word) + 1):
        for perm in permutations(word, i):
            f.write(''.join(perm))
            f.write('\n')
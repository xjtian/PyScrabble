PyScrabble
==========

This is a project to create a lookahead Scrabble AI in Python, similar to how http://www.scrabulizer.com/ works if you select to sort moves by "value".

Progress
--------

As of 5/22/2013, the basic game API is finished and there is a console UI to play scrabble against 1-3 other human opponents. 

Todo
----
* Implement a static move generator (no lookahead, picks highest-scoring move)
* Add scalable difficulty setting to static move generator
* Implement lookahead AI that only accounts for future scores
* Implement lookahead AI that accounts for future scores and tile "leave values", as well as possible Bingo's.
* Tentative: exhaustive search approach when the bag is exhausted?

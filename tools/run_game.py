#!/usr/bin/env python

import os
import sys

os.chdir('../game')
sys.path.insert(0, '../game')

import coders_in_space
while True:
    print coders_in_space.play_game('board/test_board.cis', ('bob_bot', 'john_bot'), no_gui=True, no_splash = True)

raw_input('Press Enter to continue...')

#!/usr/bin/env python

import os
import sys

os.chdir('../game')
sys.path.insert(0, '../game')

import coders_in_space
coders_in_space.play_game('board/test_board.cis', ('bob_bot', 'john_bot'), no_gui=False, no_splash = True)

raw_input('Press Enter to continue...')

#!/usr/bin/env python

import os
import sys

os.chdir('../game')
sys.path.insert(0, '../game')

import coders_in_space
coders_in_space.play_game('board/test_board.cis', ('bob', 'john_bot'),screen_size=(191,56), no_gui=False, no_splash=False)

raw_input('Press Enter to continue...')

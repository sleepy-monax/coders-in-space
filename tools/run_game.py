#!/usr/bin/env python

import os
import sys

os.chdir('../game')
sys.path.insert(0, '../game')

import coders_in_space
coders_in_space.play_game('board/test_board.cis', ('dumby','Johndumb', 'dumbly', 'dumbinspace'),screen_size=(193,58), no_gui=False, no_splash=False, max_rounds_count = 100)

raw_input('Press Enter to continue...')

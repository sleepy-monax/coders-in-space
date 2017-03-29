#!/usr/bin/env python

import os
import sys

os.chdir('../game')
sys.path.insert(0, '../game')

import coders_in_space
coders_in_space.play_game('random', ('dumbInSpace', 'dumby', 'dumbo', 'botbot'), screen_size=(190, 50), no_gui=False, no_splash=False, max_rounds_count=100)

raw_input('Press Enter to continue...')

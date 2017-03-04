#!/usr/bin/env python

import os
import sys

os.chdir('../game')
sys.path.insert(0, '../game')

import coders_in_space

coders_in_space.play_game('board/test_board.cis', ('distant', 'john_bot'), distant_id = 1, distant_ip = '127.0.0.1')

raw_input('Press Enter to continue...')

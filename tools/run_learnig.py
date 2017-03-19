#!/usr/bin/env python

import os
import sys

os.chdir('../game')
sys.path.insert(0, '../game')

import coders_in_space
coders_in_space.train_neural_network(50, 0.1)

raw_input('Press Enter to continue...')

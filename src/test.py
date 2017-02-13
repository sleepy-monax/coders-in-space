# -*- coding: utf-8 -*-
"""
Ce fichier est juste là pour tester le code il sera suprimé quand le moment viendra.
"""
import codeinspace
import gui
import os
print os.name
print 'please make the windows full screen and press enter...'
raw_input()
gui.cls()
game_stats = codeinspace.new_game('test\\test0.cis', ['Nicolas Rebel Of Space', 'ai'])
while True:
    codeinspace.show_board(game_stats, True)
    raw_input()
    gui.cls()

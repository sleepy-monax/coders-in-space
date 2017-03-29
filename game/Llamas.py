# -*- coding: utf-8 -*-
from graphics import *
from time import sleep


while True:
    for color in ['grey', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']:
        for bcolor in ['grey', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']:
            c = create_canvas(35, 42, True)
            put_ascii_art(c, 0, 0, "llamas", color, bcolor,transparency_char = u'─')
            print_canvas(c)

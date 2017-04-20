# -*- coding: utf-8 -*-
from graphics import *
from time import sleep


while True:
    for color in ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan']:
        c = create_canvas(35, 42, True)
        put_ascii_art(c, 0, 0, "llamas", color, None, transparency_char = u'─')
        print_canvas(c)
        sleep(0.05)

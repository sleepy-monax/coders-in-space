# -*- coding: utf-8 -*-
from termcolor import *
import os

def cls():
    """
    Clear the terminal screen.
    """
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def creat_canvas(width, height, enable_color = True):
    """
    Create a new utf-8 canvas.

    Parameterr
    ---------
    height : height of the game view (int).
    width : width of the game view (int).
    enable_color : enable color in the game view (bool)

    Return
    ------
    canva : utf-8 canvas (dic).

    Version
    -------
    specification: v1. Nicolas Van Bossuyt (10/2/2017)
                   v2. Nicolas Van Bossuyt (13/2/2017)
    implementation: v1. Nicolas Van Bossuyt (10/2/2017)
                    v2. Nicolas Van Bossuyt (13/2/2017)
    """

    canvas = {'size': (width, height), 'color': enable_color, 'grid': {}}

    for x in range(width):
        for y in range(height):
            canvas['grid'][(x,y)] = {'color':None, 'back_color':None, 'char':' '}

    canvas = put_box(canvas, 0, 0, width, height, 'single')
    canvas = put_string(canvas, width - 32, height - 1, '| canvas size : %d, %d |' % (width, height))
    return canvas

def put(canvas, x, y, char, color = None, back_color = None):
    """
    Put the specified char in the canvas.

    Parameter
    ---------
    canvas : game view to put the char in (dic).
    x, y : coordinate of were to put the char (int).
    char : char to put (str).
    color, back_color : color for the char (string).

    Version
    -------
    specification v1. Nicolas Van Bossuyt (10/2/2017)
    implementation v1. Nicolas Van Bossuyt (10/2/2017)
    """

    # Check if the coordinate is in the bound of the game view.
    if x < canvas['size'][0] and x>=0 and\
    y < canvas['size'][1] and y >= 0:

        # Put the char a the coordinate.
        canvas['grid'][(x,y)]['char'] = char
        canvas['grid'][(x,y)]['color'] = color

        # Add the 'on_' at the start of the back_color string.
        if not back_color == None:
            canvas['grid'][(x,y)]['back_color'] = 'on_' + back_color
        else:
            canvas['grid'][(x,y)]['back_color'] = None

    return canvas

def put_rectangle(canvas, x, y, width, height, char, color = None, back_color = None):
    """
    Draw a rectangle in the string buffer.

    Parameters
    ----------
    x, y : coordinate of the rectangle (int).
    width, height : size of the rectangle (int).
    color, back_color : color for the char (string).

    return
    ------
    canvas : canvas whith the rectangle (dic).

    Version
    -------
    specification v1. Nicolas Van Bossuyt (10/2/2017)
    implementation v1. Nicolas Van Bossuyt (10/2/2017)
    """

    for w in range(width):
        for h in range(height):
            canvas = put(canvas, x + w, y + h, char, color, back_color)

    return canvas

def put_box(canvas, x, y, width, height, mode = 'double', color = None, back_color = None):
    """
    Put a box in the game view.

    Parameters
    ----------
    x, y : coordinate of the rectangle (int).
    width, height : size of the rectangle (int).
    mode : double ou single line <'double'|'single'> (str).
    color, back_color : color for the char (string).

    return
    ------
    canvas : canvas whith the box (dic).

    Version
    -------
    specification v1. Nicolas Van Bossuyt (10/2/2017)
    implementation v1. Nicolas Van Bossuyt (10/2/2017)
    """
    if mode == 'double':
        put_rectangle(canvas, x, y, width, height, u'═', color, back_color)
        put_rectangle(canvas, x, y + 1, width, height - 2,u'║', color, back_color)
        put(canvas, x, y, u'╔', color, back_color)
        put(canvas, x, y + height - 1, u'╚', color, back_color)
        put(canvas, x + width - 1, y, u'╗', color, back_color)
        put(canvas, x + width - 1, y + height - 1, u'╝', color, back_color)

    elif mode == 'single':
        put_rectangle(canvas, x, y, width, height, u'─', color, back_color)
        put_rectangle(canvas, x, y + 1, width, height - 2,u'│', color, back_color)
        put(canvas, x, y, u'┌', color, back_color)
        put(canvas, x, y + height - 1, u'└', color, back_color)
        put(canvas, x + width - 1, y, u'┐', color, back_color)
        put(canvas, x + width - 1, y + height - 1, u'┘', color, back_color)

    put_rectangle(canvas, x + 1 , y + 1, width - 2, height - 2, ' ')

    return canvas

def put_string(canvas, x, y, string, direction_x = 1, direction_y = 0, color = None, back_color = None):
    """
    Put a specified string in the canvas.

    Parameter
    ---------
    x, y : coordinate of the string (int).
    direction_x, direction_y : direction to draw the string (int).
    canvas : game view to put the string (dic).

    Return
    ------
    canvas : game view with the new string (dic).

    Notes
    -----
    direction_x, direction_y : Muste be -1, 0 or 1.

    Version
    -------
    specification v1. Nicolas Van Bossuyt (10/2/2017)
    implementation v1. Nicolas Van Bossuyt (10/2/2017)
    """

    for char in string:
        canvas = put(canvas, x, y, char, color, back_color)
        x += direction_x
        y += direction_y

    return canvas

def print_canvas(canvas):
    """
    Print the game view in the terminal.

    Parameter
    ---------
    canvas : string buffer to draw on screen.

    Version
    -------
    specification v1. Nicolas Van Bossuyt (10/2/2017)
    implementation v1. Nicolas Van Bossuyt (10/2/2017)
    """

    canvas_width = canvas['size'][0]
    canvas_height = canvas['size'][1]

    for y in range(canvas_height):
        line = ''
        for x in range(canvas_width):
            grid_item = canvas['grid'][(x,y)]
            char = grid_item['char']
            color = grid_item['color']
            back_color = grid_item['back_color']

            if (canvas['color']):
                line = line + colored(char, color, back_color)
            else:
                line = line + char
        print line

def try_gui_lib():
    v = creat_canvas(20,20)
    put_box(v, 0,0, 19, 3, 'double', 'yellow', 'on_blue')
    put_string(v, 1,1,' Code In Space ! ',1,0, 'yellow', 'on_blue')
    print_canvas(v)

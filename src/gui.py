# -*- coding: utf-8 -*-
from termcolor import *

def creat_game_view(width, height):
    """
    Create a new view buffer for the gui.

    Parameterr
    ---------
    height : height of the game view (int).
    width : width of the game view (int).

    Return
    ------
    game_view : the new game view (dic).

    Version
    -------
    specification v1. Nicolas Van Bossuyt (10/2/2017)
    implementation v1. Nicolas Van Bossuyt (10/2/2017)
    """

    game_view = {'size': (width, height), 'grid': {}}

    for x in range(width):
        for y in range(height):
            game_view['grid'][(x,y)] = {'color':None, 'back_color':None, 'char':' '}

    return game_view
def put(game_view, x, y, char, color = None, back_color = None):
    """
    Put the specified char in the game_view.

    Parameter
    ---------
    game_view : game view to put the char in (dic).
    x, y : coordinate of were to put the char (int).
    char : char to put (str).
    color, back_color : color for the char (string).

    Version
    -------
    specification v1. Nicolas Van Bossuyt (10/2/2017)
    implementation v1. Nicolas Van Bossuyt (10/2/2017)
    """

    # Check if the coordinate is in the bound of the game view.
    if x < game_view['size'][0] and x>=0 and\
    y < game_view['size'][1] and y >= 0:

        # Put the char a the coordinate.
        game_view['grid'][(x,y)]['char'] = char
        game_view['grid'][(x,y)]['color'] = color
        game_view['grid'][(x,y)]['back_color'] = back_color

    return game_view

def put_rectangle(game_view, x, y, width, height, char, color = None, back_color = None):
    """
    Draw a rectangle in the string buffer.

    Parameters
    ----------
    x, y : coordinate of the rectangle (int).
    width, height : size of the rectangle (int).
    color, back_color : color for the char (string).

    return
    ------
    game_view : game view whith the rectangle (dic).

    Version
    -------
    specification v1. Nicolas Van Bossuyt (10/2/2017)
    implementation v1. Nicolas Van Bossuyt (10/2/2017)
    """

    for w in range(width):
        for h in range(height):
            game_view = put(game_view, x + w, y + h, char, color, back_color)

    return game_view

def put_box(game_view, x, y, width, height, mode = 'double', color = None, back_color = None):
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
    game_view : game view whith the rectangle (dic).

    Version
    -------
    specification v1. Nicolas Van Bossuyt (10/2/2017)
    implementation v1. Nicolas Van Bossuyt (10/2/2017)
    """
    if mode == 'double':
        put_rectangle(game_view, x, y, width, height, u'═', color, back_color)
        put_rectangle(game_view, x, y + 1, width, height - 2,u'║', color, back_color)
        put(game_view, x, y, u'╔', color, back_color)
        put(game_view, x, y + height - 1, u'╚', color, back_color)
        put(game_view, x + width - 1, y, u'╗', color, back_color)
        put(game_view, x + width - 1, y + height - 1, u'╝', color, back_color)

    elif mode == 'single':
        put_rectangle(game_view, x, y, width, height, u'─', color, back_color)
        put_rectangle(game_view, x, y + 1, width, height - 2,u'│', color, back_color)
        put(game_view, x, y, u'┌', color, back_color)
        put(game_view, x, y + height - 1, u'└', color, back_color)
        put(game_view, x + width - 1, y, u'┐', color, back_color)
        put(game_view, x + width - 1, y + height - 1, u'┘', color, back_color)

    return game_view

def put_string(game_view, x, y, string, direction_x = 1, direction_y = 0, color = None, back_color = None):
    """
    Put a specified string in the game_view.

    Parameter
    ---------
    x, y : coordinate of the string (int).
    direction_x, direction_y : direction to draw the string (int).
    game_view : game view to put the string (dic).

    Return
    ------
    game_view : game view with the new string (dic).

    Notes
    -----
    direction_x, direction_y : Muste be -1, 0 or 1.

    Version
    -------
    specification v1. Nicolas Van Bossuyt (10/2/2017)
    implementation v1. Nicolas Van Bossuyt (10/2/2017)
    """

    for char in string:
        game_view = put(game_view, x, y, char, color, back_color)
        x += direction_x
        y += direction_y

    return game_view

def print_game_view(game_view):
    """
    Print the game view in the terminal.

    Parameter
    ---------
    game_view : string buffer to draw on screen.

    Version
    -------
    specification v1. Nicolas Van Bossuyt (10/2/2017)
    implementation v1. Nicolas Van Bossuyt (10/2/2017)
    """

    game_view_width = game_view['size'][0]
    game_view_height = game_view['size'][1]

    for y in range(game_view_height):
        line = ''
        for x in range(game_view_width):
            grid_item = game_view['grid'][(x,y)]
            char = grid_item['char']
            color = grid_item['color']
            back_color = grid_item['back_color']
            line = line + colored(char, color, back_color)

        print line

def try_gui_lib():
    v = creat_game_view(20,20)
    put_box(v, 0,0, 19, 3, 'double', 'yellow', 'on_blue')
    put_string(v, 1,1,' Code In Space ! ',1,0, 'yellow', 'on_blue')
    print_game_view(v)

try_gui_lib()

"""
=====
=GUI= This section of code is use for all the user inteface stuff.
=====
"""

def creat_game_view(width, height):
    """
    Create a new view buffer for the gui.

    Parameter
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
            game_view['grid'][(x,y)] = ' '

    return game_view


def put(x, y, char, game_view):
    """
    Put the specified char in the game_view.

    Parameter
    ---------
    x, y : coordinate of were to put the char (int).
    char : char to put (str).

    Version
    -------
    specification v1. Nicolas Van Bossuyt (10/2/2017)
    implementation v1. Nicolas Van Bossuyt (10/2/2017)
    """

    if x < game_view['size'][0] and x>=0 and\
    y < game_view['size'][1] and y >= 0:
        game_view['grid'][(x,y)] = char

    return game_view

def put_rectangle(x,y, width, height, char, game_view):
    """
    Draw a rectangle in the string buffer.

    Parameters
    ----------
    x, y : coordinate of the rectangle (int).
    width, height : size of the rectangle (int).

    return
    ------
    game_view : game view whith the rectangle (dic).

    Version
    -------
    specification v1. Nicolas Van Bossuyt (10/2/2017)
    implementation v1. Nicolas Van Bossuyt (10/2/2017)
    """

    raise NotImplemented

def put_string(x, y, string, direction_x, direction_y, game_view):
    """
    Put a specified string in the game_view.

    Parameter
    ---------
    x, y : coordinate of the string (int).
    direction_x, direction_y : direction to draw the string (int).

    Return
    ------
    game_view : game view with the new string (dic).

    Version
    -------
    specification v1. Nicolas Van Bossuyt (10/2/2017)
    implementation v1. Nicolas Van Bossuyt (10/2/2017)
    """

    for char in string:
        game_view = put(x, y, char, game_view)
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

    for i in game_view:
        line = ''
        for j in i:
            line += j

        print line

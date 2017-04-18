# -*- coding: utf-8 -*-


from random import seed, randint
from os import path


# Gui framework
# ==============================================================================
# framework for easy user interface creation.

# Canvas creation and printing.
# ------------------------------------------------------------------------------
# Create and print a canvas in the user console.


def create_canvas(width, height, enable_color = True):
    """
    Create a new char canvas.

    Parameters
    ----------
    height: height of the game view (int).
    width: width of the game view (int).
    enable_color: enable color in the game view (bool)

    Return
    ------
    canvas: 2D ascii canvas (dic).

    Version
    -------
    Specification: Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 10/02/17)
    """

    # Initialize the canvas.
    canvas = {'size': (width, height), 'color': enable_color, 'grid': {}}

    # Create canvas's tiles.
    for x in range(width):
        for y in range(height):
            canvas['grid'][(x,y)] = {'color':None, 'back_color':None, 'char':' '}

    return canvas


def print_canvas(canvas, x = 0, y = 0):
    """
    Print canvas in the terminal.

    Parameters
    ----------
    canvas: canvas to print on screen (dic).
    (optional) x, y: coodinate in the terminal (int).

    Version
    -------
    Specification: Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 10/02/17)
    """

    canvas_width = canvas['size'][0]
    canvas_height = canvas['size'][1]

    # Hide and set cursor coordinates.
    line = '\033[?25l\033[%d;%dH' % (x, y)

    for y in range(canvas_height):
        for x in range(canvas_width):

            # Get coordinate.
            grid_item = canvas['grid'][(x,y)]

            # Get coordinate information.
            char = grid_item['char']
            color = grid_item['color']
            back_color = grid_item['back_color']

            if (canvas['color']):
                line = line + set_color(char, color, back_color)
            else:
                line = line + char

        line += '\n'

    # Print, remove the laste \n et reset the print cursor..
    print line[:-1] + '\033[?25h\033[0;0H'


# Canvas drawing.
# ------------------------------------------------------------------------------
# All tools and brush to draw on the canvas.


def put(canvas, x, y, char, color = None, back_color = None):
    """
    Put a character in the canvas.

    Parameters
    ----------
    canvas: canvas to draw in (dic).
    x, y: coordinate of were to put the char (int).
    char: char to put (str).
    (optiona) color, back_color: color for the char (string).

    Return
    ------
    canvas: canvas with the char put on it (dic).

    Version
    -------
    Specification: Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 10/02/17)
    """

    # Check if the coordinate is in the bound of the canvas.
    if x < canvas['size'][0] and x >= 0 and\
       y < canvas['size'][1] and y >= 0:

        # Put the char a the coordinate.
        canvas['grid'][(x,y)]['char'] = char
        canvas['grid'][(x,y)]['color'] = color
        canvas['grid'][(x,y)]['back_color'] = back_color

    return canvas


def put_ascii_art(canvas, x, y, ascii_art_name, color = None, back_color = None, transparency_char = None):
    """
    Put a ascii art in the canvas.

    Parameters
    ----------
    canvas: canvas to draw in (dic).
    x, y: coordinate to pute the art (int).
    ascii_art_name: name of the art file (string).
    canvas: canvas to put the art on it (dic).
    (optiona) color, back_color: color for the ASCII art (string).
    transparency_char: ignored char (str).

    Return
    ------
    canvas: game view with te ascii art (dic).

    Version
    -------
    Specification: Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (V1. 15/02/17)
                    Nicolas Van Bossuyt (v2. 26/02/17)
    """
    
    
    art_path = 'art/' + ascii_art_name + '.txt'
    if (not path.isfile(art_path)): 
        return canvas
    
    art_file = open(art_path,'r')

    line_index = 0

    for line in art_file:
        char_index = 0
        for char in line.replace('\n', ''):
            if char != transparency_char:
                put(canvas, x + char_index, y + line_index, char, color, back_color)

            char_index += 1
        line_index += 1

    art_file.close()

    return canvas


def put_ascii_text(canvas, font, text, x, y, color = None, back_color = None):
    """
    Put a ascii art text in the canvas.

    Parameters
    ----------
    canvas: canvas to draw in (dic).
    font: font to use (dic).
    string: string to put in the canvas (str).

    Return
    ------
    canvas: the canvas with the string on it (dic).

    Version
    -------
    Specification: Nicolas Van Bossuyt (v1. 27/02/17)
    """
    char_x = 0

    if font is None:
        canvas = put_text(canvas, x, y, text, 1, 0, color, back_color)
        return canvas
    
    for char in text:
        char_ascii = font[char]
        char_width = char_ascii['width']
        char_text = char_ascii['text']

        line_index = 0
        for line in char_text.split('\n'):
            canvas = put_text(canvas, x + char_x, y + line_index, line, 1, 0, color, back_color)
            line_index += 1

        char_x += char_width

    return canvas


def load_ascii_font(font_name):
    """
    Load ascii font from a txt file.

    Parameter
    ---------
    font_name: name of the font (str).

    Return
    ------
    font: font face from the file (dic).

    Version
    -------
    Specification: Nicolas Van Bossuyt (v1. 27/02/17)

    Notes
    -----
    Load font in figlet format (http://www.figlet.org).
    """

    chars = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_'abcdefghijklmnopqrstuvwxyz{|}~ÄÖÜäöüβ"
    font = {}
    char_index = 0
    current_char = ''
    current_char_width = 0
    
    font_path = 'art/%s' % (font_name)
    if (not path.isfile(font_name)): 
        return None
    f = open(font_path, 'r')

    for line in f:
        current_char_width = len(line.replace('@', ''))
        current_char += line.replace('@', '')

        if line.endswith('@@\n'):
            font[chars[char_index]] = {}
            font[chars[char_index]]['text'] = current_char
            font[chars[char_index]]['width'] = current_char_width

            current_char = ''
            current_char_width = 0
            char_index += 1

    f.close()

    return font


def mesure_ascii_text(font, text):
    """"
    Return the lenght of a ascii art text.

    Parameters
    ----------
    font: font to mesure the string (dic).
    string: text to mesure (str)

    Return
    ------
    lenght: lenght of the string (int).

    Version
    -------
    Specification: Nicolas Van Bossuyt (v1. 27/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 22/02/17)
    """
    lenght = 0
    if font is None:
        return len(text)

    for char in text:
        char_ascii = font[char]
        char_width = char_ascii['width']
        lenght += char_width

    return lenght


def put_canvas(canvas, canvas_bis, x, y):
    """
    Put a canvas in the canvas.

    Parameters
    ----------
    canvas: canvas to draw in (dic).
    canvas_bis: canvas to put in the main canvas (dic).
    x, y: coordinate of the canvas (int).

    Return
    ------
    canvas: the canvas with the other canvas on it (dic).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 27/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 22/02/17)
    """

    for cx in range(canvas_bis['size'][0]):
        for cy in range(canvas_bis['size'][1]):
            char = canvas_bis['grid'][(cx, cy)]
            canvas = put(canvas, cx + x, cy + y, char['char'], char['color'], char['back_color'])

    return canvas


def put_window(canvas, window_content, title, x, y, width, height, style="double"):
    """
    Put a window with a windows content in the main canvas.
     
    Parameters
    ----------
    canvas: canvas to draw in (dic).
    window_content: content of the window (dic).
    title: title of the window (str).
    x, y: coordinate of the window (int).
    width, height: size of the window (int).
    (optional) style: Style of the window (str).
    
    Return
    ------
    canvas: the canvas with the window on it (dic).
    """
    c = create_canvas(width, height, True)
    c = put_canvas(c, window_content, 1, 1)
    c = put_box(c, 0, 0, width, height, style)
    c = put_text(c, 1, 0, "| %s |" % title)

    canvas = put_canvas(canvas, c, x, y)

    return canvas


def put_box(canvas, x, y, width, height, mode = 'double', color = None, back_color = None):
    """
    Put a box in the canvas.

    Parameters
    ----------
    canvas: canvas to draw in (dic).
    x, y: coordinate of the rectangle (int).
    width, height: size of the rectangle (int).
    mode: double ou single line <'double'|'single'> (str).
    color, back_color: color for the char (string).

    Return
    ------
    canvas: canvas whith the box (dic).

    Version
    -------
    Specification: Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 10/02/17)
    """

    rec_char = ()

    if mode == 'double':
        rect_char = (u'═', u'║', u'╔', u'╚', u'╗', u'╝')
    elif mode == 'single':
        rect_char = (u'─', u'│', u'┌', u'└', u'┐', u'┘')

    # Put borders.
    put_rectangle(canvas, x, y, width, 1, rect_char[0], color, back_color)
    put_rectangle(canvas, x, y + height - 1, width, 1, rect_char[0], color, back_color)

    put_rectangle(canvas, x, y, 1, height, rect_char[1], color, back_color)
    put_rectangle(canvas, x + width - 1, y, 1, height, rect_char[1], color, back_color)

    # Put corners.
    put(canvas, x, y, rect_char[2], color, back_color)
    put(canvas, x, y + height - 1, rect_char[3], color, back_color)
    put(canvas, x + width - 1, y, rect_char[4], color, back_color)
    put(canvas, x + width - 1, y + height - 1, rect_char[5], color, back_color)

    return canvas


def put_rectangle(canvas, x, y, width, height, char, color = None, back_color = None):
    """
    Put a filled rectangle in the canvas.

    Parameters
    ----------
    canvas: canvas to draw in (dic).
    x, y: coordinate of the rectangle (int).
    width, height: size of the rectangle (int).
    color, back_color: color for the char (string).

    Return
    ------
    canvas: canvas whith the rectangle (dic).

    Version
    -------
    Specification: Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 10/02/17)
    """

    for w in range(width):
        for h in range(height): canvas = put(canvas, x + w, y + h, char, color, back_color)

    return canvas


def put_stars_field(canvas, x, y, width, height, r_seed = 0):
    """
    Put a stars field in the canvas.

    Parameters
    ----------
    canvas: canvas to draw in (dic).
    x, y, w, h: location and size of the stars field (int)
    (optional) r_seed: random seed (int).

    Return
    ------
    canvas: the canvas with the stars field on it (dic).

    Version
    -------
    Specification: Nicolas Van Bossuyt (v1. 27/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 22/02/17)
    """
    void_char = ['.', '*', '\'']
    seed(r_seed)

    for star_x in range(width):
        for star_y in range(height):
            if randint(0, 20) == 0:
                canvas = put_text(canvas, x + star_x, y +star_y, void_char[randint(0, 2)])
            else:
                canvas = put_text(canvas, x + star_x, y +star_y, ' ')

    seed()
    return canvas


def put_text(canvas, x, y, text, direction_x = 1, direction_y = 0, color = None, back_color = None):
    """
    Put a text in the canvas.

    Parameters
    ----------
    canvas: canvas to draw in (dic).
    x, y: coordinate of the string (int).
    direction_x, direction_y: direction to draw the string (int).

    Return
    ------
    canvas: game view with the new string (dic).

    Notes
    -----
    direction_x, direction_y: Muste be -1, 0 or 1.

    Version
    -------
    Specification: Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 10/02/17)
    """

    for char in text:
        canvas = put(canvas, x, y, char, color, back_color)
        x += direction_x
        y += direction_y

    return canvas


def set_color(text, foreground_color, background_color):
    """
    Change the color of a text.

    Parameters
    ----------
    text: string to color (str).
    fore_color: name of the foreground color (str).
    back_color: name of the background color (str).

    Return
    ------
    colored_text: colored string (str).

    Notes
    -----
    Colors: grey, red, green, yellow, blue, magenta, cyan, white.

    ANSI color escape sequences: http://ascii-table.com/ansi-escape-sequences.php

    Version
    -------
    Specification: Nicolas Van Bossuyt (v1. 27/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 27/02/17)
    """
    color = { 'grey': 0, 'red': 1, 'green': 2, 'yellow': 3, 'blue': 4, 'magenta': 5, 'cyan': 6, 'white': 7 }
    reset = '\033[0m'
    format_string = '\033[%dm%s'

    if foreground_color is not None: text = format_string % (color[foreground_color] + 30, text)
    if background_color is not None: text = format_string % (color[background_color] + 40, text)

    text += reset

    return text

# ======================================================================================================================
# ======================================================================================================================

import os
import shlex
import struct
import platform
import subprocess

def get_terminal_size():
    """ 
    Get the size of the terminal window.
    
    Return
    ------
    size : size of the terminal window (tuple(int, int))

    Originally retrieved from
    -------------------------
    http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    """
    current_os = platform.system()
    size = None

    if current_os == 'Windows':
        size = _get_terminal_size_windows()
        if size is None:
            size = _get_terminal_size_tput()

    elif current_os in ['Linux', 'Darwin'] or current_os.startswith('CYGWIN'):
        size = _get_terminal_size_linux()

    if size is None:
        return (90, 60)  # default value
    else:
        return size


def _get_terminal_size_windows():
    try:
        from ctypes import windll, create_string_buffer
        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom,
             maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            sizex = right - left + 1
            sizey = bottom - top + 1
            return (sizex, sizey)
    except:
        pass


def _get_terminal_size_tput():
    # get terminal width
    # src: http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window
    try:
        cols = int(subprocess.check_call(shlex.split('tput cols')))
        rows = int(subprocess.check_call(shlex.split('tput lines')))
        return (cols, rows)
    except:
        pass


def _get_terminal_size_linux():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            cr = struct.unpack('hh',
                               fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
            return cr
        except:
            pass

    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            return None
    return int(cr[1]), int(cr[0])

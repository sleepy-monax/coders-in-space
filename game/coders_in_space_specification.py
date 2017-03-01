
# Game
# ==============================================================================
# Create a new game and play it.

def play_game(level_name, players_list, no_splash = False):
	"""
	Main game function which runs the game loop.

	Parameters
	----------
	level_name: name of the level (str)
	players_list: list of the players(list)

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

def new_game(level_name, players_list):
	"""
	Create a new game from a '.cis' file.

	Parameters
	----------
	level_name : name of the path to .cis file (str).
	players_list : list of players (list).

	Return
	-------
	game_stats : new game stats (dic).

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

def splash_game():
	"""
	Show the splash screen.
	"""

def end_game(game_stats):
	"""
	Show the end game screen.

	Parameter
	---------
	game_stats : stats of the game (dic).
	"""

def is_game_continue(game_stats):
	"""
	Check if a player has won the game.

	Parameters
	----------
	game_stats : game before comand execution (dic)

	Return
	------
	True if the game is not over (no one has won yet), False if someone has won.

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    """
def calculate_value(player, game_stats):
	"""
	calculate the total ship value of a player.

	Parameters
	----------
	player : name of the player to count value (str)
	game_stats : game before comand execution (dic)

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

# Input
# ==============================================================================
# Get input from each player.

def get_game_input(player_name, buy_ship, game_stats):
	"""
	get input from a specified player.

	Parameters
	----------
	player_name : name of the player to get input (str).

	Version
	-------
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	implemetation : Niolas Van Bossuyt (V1. 15/02/17)
	"""


# Player
# ------------------------------------------------------------------------------
# Human player interaction with the game.

def get_human_input(player_name, buy_ship, game_stats):
	"""
	Get input from a human player.

	Parameters
	----------
	player_name : Name of the player to get input from (str).
	buy_ship : the player need to buy a ship (str).
	game_stats : stats of the game (dic).

	Returns
	-------
	player_input : input from the player (str).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

def show_ship_list(player_name, game_stats):
	"""
	Show spaceships information to the player.

	Parameters
	----------
	player_name: name of the player to show the information (str).
	game_stats: stats of the game (dic).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

def show_game_board(game_stats, color = True):
	"""
	Show the game to the user screen.

	Parameter
	---------
	game_stats : game to show on screen (dic).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

# A.I.
# ------------------------------------------------------------------------------
# AI interactions

def get_ai_input(player_name, buy_ship, game_stats):
	"""
	Get the game input from the ai.

	Parameter
	---------
	player_name : name of the player (str).
	game_stats : game stat of the current game (dic).

	Return
	------
	ai_input : game input from the ai (str).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

# Remote player
# ------------------------------------------------------------------------------
# Handeling remote player command.

def get_remote_input():
	# Wait and see.
	pass

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
	height : height of the game view (int).
	width : width of the game view (int).
	enable_color : enable color in the game view (bool)

	Return
	------
	canva : new char canva (dic).

	Version
	-------
	specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	"""

def print_canvas(canvas, x = 0, y = 0):
	"""
	Print the game view in the terminal.

	Parameter
	---------
	canvas : canvas to print on screen (dic).
	x, y : coodinate in the terminal (int).

	Version
	-------
	specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	implementation : Nicolas Van Bossuyt (v1. 10/02/2017)
	"""

# Canvas drawing.
# ------------------------------------------------------------------------------
# All tools and brush to draw on the canvas.

def put(canvas, x, y, char, color = None, back_color = None):
	"""
	Put the specified char in the canvas.

	Parameters
	----------
	canvas : game view to put the char in (dic).
	x, y : coordinate of were to put the char (int).
	char : char to put (str).
	color, back_color : color for the char (string).

	Return
	------
	canvas : canvas with the char put on it (dic).

	Version
	-------
	specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	"""

def put_rectangle(canvas, x, y, width, height, char, color = None, back_color = None):
	"""
	Put and fill a rectangle in the canvas.

	Parameters
	----------
	x, y : coordinate of the rectangle (int).
	width, height : size of the rectangle (int).
	color, back_color : color for the char (string).

	Return
	------
	canvas : canvas whith the rectangle (dic).

	Version
	-------
	specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	"""

def put_box(canvas, x, y, width, height, mode = 'double', color = None, back_color = None):
	"""
	Put a box in the canvas.

	Parameters
	----------
	x, y : coordinate of the rectangle (int).
	width, height : size of the rectangle (int).
	mode : double ou single line <'double'|'single'> (str).
	color, back_color : color for the char (string).

	Return
	------
	canvas : canvas whith the box (dic).

	Version
	-------
	specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	"""

def put_string(canvas, x, y, string, direction_x = 1, direction_y = 0, color = None, back_color = None):
	"""
	Put a specified string in the canvas.

	Parameters
	----------
	canvas : canavas to put the string (dic).
	x, y : coordinate of the string (int).
	direction_x, direction_y : direction to draw the string (int).

	Return
	------
	canvas : game view with the new string (dic).

	Notes
	-----
	direction_x, direction_y : Muste be -1, 0 or 1.

	Version
	-------
	specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	"""

def put_ascii_art(canvas, x, y, ascii_art_name, color = None, back_color = None, transparency_char = None):
	"""
	Put a ascii art in the in the canvas.

	Parameters
	----------
	x, y : coordinate to pute the art (int).
	ascii_art_name : name of the art file (string).
	canvas : canvas to put the art on it (dic).
	transparency_char : ignored char.

	Return
	------
	canvas : game view with te ascii art (dic).

	Version
	-------
	specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	"""

def put_stars_field(c, x, y, w, h, r_seed = None):
	"""
	Put a stars field in the canvas.

	Parameters
	----------
	c : canvas to pute stars on it (dic)
	x, y, w, h : location and size of the stars field (int)
	r_seed : random seed (int).

	Return
	------
	canvas : the canvas with the stars field on it (dic).

	Version
	-------
	specification  : Nicolas Van Bossuyt (v1. 01/03/17)
	"""

def put_canvas(canvas, canvas_bis, x, y):
	"""
	Put a canvas in a canvas.

	Parameters
	----------
	canavas : canvas to put the canvas in (dic).
	canvas_bis : the canvas to put in the main canvas (dic).
	x, y : coordinate of the canavas (int).

	Return
	------
	canvas : the canvas with the other canvas on it (dic).

	Version
	-------
	specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	"""

def load_ascii_font(font_name):
	"""
	Load ascii font from a txt file.

	Parameter
	---------
	font_name : name of the font (str).

	Return
	------
	font : font face from the file (dic).

	Version
	-------
	specification  : Nicolas Van Bossuyt (v1. 01/03/17)

	Notes
	-----
	Load font in figlet format (http://www.figlet.org).
	"""

def put_ascii_text(c, font, string, x, y, color = None, back_color = None):
	"""
	Put a string in the canvas with a ascii font.

	Parameters
	----------
	canvas : canvas to put the ascii text (dic).
	font : font to use (dic).
	string : string to put in the canvas (str).

	Return
	------
	canvas : the canvas with the string on it (dic).

	Version
	-------
	specification  : Nicolas Van Bossuyt (v1. 01/03/17)
	"""

def colored(text, fore_color, back_color):
	"""
	Color a string.

	Parameters
	----------
	text : string to color (str).
	fore_color : name of the foreground color (str).
	back_color : name of the background color (str).

	Return
	------
	colored_text : colored string (str).

	Notes
	-----
	Colors : grey, red, green, yellow, blue, magenta, cyan, white.
	Ansi escape sequences : http://ascii-table.com/ansi-escape-sequences.php

	Version
	-------
	specification  : Nicolas Van Bossuyt (v1. 01/03/17)
	"""
# Game commands
# ==============================================================================
# Game command parsing and execution.

# Command Parsing
# ------------------------------------------------------------------------------
# From a string to a game command.

def parse_command(commands, player_name, game_stats):
	"""
	Parse a command from a player and run it.

	Parameters
	----------
	command : command from the player (str).
	game_stats : stat of the game (dic).

	Return
	------
	game_stats : game stat after the command execution (dic).

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

# Ship creation
# ------------------------------------------------------------------------------
# Buy and create a spaceship.

def command_buy_ships(ships, player, game_stats):
	"""
	Allow a player to buy some spaceships.

	Parameters
	----------
	ships : spaceships to buy (str).
	player : name of the player (str).
	game_stats : stat of the game (dic).

	Return
	------
	game_stats : game stats after the operation (dic).

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

def create_ship(player_name, ship_name, ship_type, game_stats):
	"""
	Create and add a new ship.

	Parameters
	----------
	player_name : name of the owner of the ship (str).
	ship_name : Name of the ship (str).
	ship_type : Model of the ship (str).
	game_stats : stats of the game (str).

	Return
	------
	game_stats : stats after adding the new ship (dic).

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

# Move Command
# ------------------------------------------------------------------------------
# Make shipe move, rotate, and go faste and furiouse.

def command_change_speed(ship, change, game_stats):
	"""
	Increase the speed of a ship.

	Parameters
	----------
	ship : name of the ship to Increase the speed (str).
	change : the way to change the speed <"slower"|"faster"> (str).
	game_stats : stats of the game (dic).

	Returns
	-------
	game_stats : the game after the command execution (dic)

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

def command_rotate(ship, direction, game_stats):
	"""
	Rotate the ship.

	Parameters
	----------
	ship : name of the ship to Increase the speed.
	direction : the direction to rotate the ship <"left"|"right">(str)
	game_stats : stats of the game (dic).

	Returns
	-------
	new_game_stats : the game after the command execution.

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

def do_moves(game_stats):
	"""
	Apply move to ships.

	Parameters
	----------
	game_stats : stats of the game (dic)

	Return
	------
	game_stats : stats of the game after the moves (dic)

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

def take_abandonned_ship(game_stats):
	""" determine who become the owner of the abandonned ship.

	Parameters
	----------
	game_stats: state of the game before the call of this function (dico)

	Returns
	-------
	game_stats: state of the game after the call of this function (dico)

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

# Attack Command
# ------------------------------------------------------------------------------
# Allow ship to attack each other.

def command_attack(ship, ship_coordinate, target_coordinate, game_stats):
	"""
	Determine if the attack works and do it.

	Parameters
	----------
	ship_location : coodinate of the first ship (tuple(int, int)).
	coordinate : coordinate of the tile to attack (tuple(int,int)).
	game_stats : stats of the game (dic).

	Return
	------
	new_game_stats : the game after the command execution (dic).

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

# Utils
# ==============================================================================
# Somme usefull function for a simple life.

def direction_to_vector2D(direction):
	"""
	Convert a string direction to a vector2D.

	Parameter
	---------
	direction : direction to convert <up|down|left|right|up-left|up-right|down-left|down-right>(str).

	Return
	------
	vector : vector2D from direction (tuple(int, int)).

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

def parse_game_file(path):
	"""
	Parse a .cis file and returns its content.

	Parameter
	---------
	path : path of the .cis file (str).

	Return
	------
	parsed_data : data contained in the .cis file (dic).

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

def create_game_board(file_name, board_size, lost_ships_count):
	"""
	Create a new cis file.

	Parameters
	----------
	file_name : name of the cis file (str).
	board_size : size of the game board (tuple(int, int)).
	lost_ships_count : number of lost ship on the game board (int).

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

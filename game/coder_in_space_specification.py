# -*- coding: utf-8 -*-
"""
.     .       .  .   . .   .   . .    +  .
  .     .  :     .    .. :. .___---------___.
	   .  .   .    .  :.:. _".^ .^ ^.  '.. :"-_. .
	.  :       .  .  .:../:            . .^  :.:\.
		.   . :: +. :.:/: .   .    .        . . .:\
 .  :    .     . _ :::/:               .  ^ .  . .:\
  .. . .   . - : :.:./.                        .  .:\
  .      .     . :..|:                    .  .  ^. .:|
	.       . : : ..||        .                . . !:|
  .     . . . ::. ::\(                           . :)/
 .   .     : . : .:.|. ######              .#######::|
 :.. .  :-  : .:  ::| .#######           ..########: |
 .  .  .  ..  .  .. :\ ########          :######## :/
  .        .+ :: : -.:\ ########       . ########.:/
	.  .+   . . . . :.:\. #######       #######..:/
	  :: . . . . ::.:..:.\           .   .   ..:/
   .   .   .  .. :  -::::.\.       | |     . .:/
	  .  :  .  .  .-:.":.::.\             ..:/
 .      -.   . . . .: .:::.:.\.           .:/
.   .   .  :      : ....::_:..:\   ___.  :/
   .   .  .   .:. .. .  .: :.:.:\       :/
	 +   .   .   : . ::. :.:. .:.|\  .:/|
	 .         +   .  .  ...:: ..|  --.:|
.      . . .   .  .  . ... :..:.."(  ..)"
 .   .       .      :  .   .: ::/  .  .::\

_________            .___                    .__           _________
\_   ___ \  ____   __| _/___________  ______ |__| ____    /   _____/__________    ____  ____
/    \  \/ /  _ \ / __ |/ __ \_  __ \/  ___/ |  |/    \   \_____  \\____ \__  \ _/ ___\/ __ \
\     \___(  <_> ) /_/ \  ___/|  | \/\___ \  |  |   |  \  /        \  |_> > __ \\  \__\  ___/
 \________/\____/\_____|\_____>__|  /______> |__|___|__/ /_________/   __(______/\_____>_____>
###################################################################|__|#######################
"""

def play_game(level_name, players_list):
	"""
	Main game function which runs the game loop.

	Parameters
	----------
	level_name: name of the level (str)
	players_list: list of the players(list)

	Version
	-------
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

def do_moves(game_stats):
	"""
	Apply move to ships.

	Parameter
	---------
	game_stats : stats of the game (dic)

	Return
	------
	game_stats : stats of the game after the moves (dic)

	Version
	-------
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/O2/17)
	"""

def get_game_input(player_name, game_stats):
	"""
	Get input from a specified player.

	Parameter
	---------
	player_name : name of the player to get input (str).

	Version
	-------
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
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
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
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
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
	"""

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
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
	"""

def show_board(game_stats, color = True):
	"""
	Show the game on the user's screen.

	Parameter
	---------
	game_stats : game to show on screen (dic).

	Version
	-------
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
	"""

def get_player_input(player_name, game_stats):
	"""
	Get and return input from the player.

	Parameters:
	----------
	Player_name : Name of the player (str).
	game_stats : the stats of the game (dic).

	Return:
	-------
	player_input : the input from the player (str).

	Version
	-------
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
	"""

def creat_canvas(width, height, enable_color = True):
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
	specification : Nicolas Van Bossuyt (v1. 10/2/17)
	"""

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
	specification : Nicolas Van Bossuyt (v1. 10/2/17)
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
	specification : Nicolas Van Bossuyt (v1. 10/2/17)
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
	specification : Nicolas Van Bossuyt (v1. 10/2/17)
	"""

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
	specification : Nicolas Van Bossuyt (v1. 10/2/17)
	"""

def put_ascii_art(canvas, x, y, ascii_art_name, color = None, back_color = None):
	"""
	Put a ascii art in the in the canvas.

	Parameters
	----------
	x, y : coordinate to pute the art (int).
	ascii_art_name : name of the art file (string).
	canvas : game view to put the art on it (dic).

	return
	------
	canvas : game view with te ascii art (dic).

	Version
	-------
	specification : Nicolas Van Bossuyt (v1. 10/2/17)
	"""

def print_canvas(canvas):
	"""
	Print the canvas in the terminal.

	Parameter
	---------
	canvas : canvas to print on screen (dic).

	Version
	-------
	specification : Nicolas Van Bossuyt (v1. 10/2/17)
	"""

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
	specification v1. Nicolas Van Bossuyt (10/2/2017)
	"""

def command_buy_ships(ships, player, game_stats):
	"""
	Allow a player to buy some ships.

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
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
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
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
	"""

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
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
	"""

def command_rotate(ship, direction, game_stats):
	"""
	Rotate the ship.

	Parameters
	----------
	ship : name of the ship to rotate (str).
	direction : the direction to rotate the ship <"left"|"right">(str)
	game_stats : stats of the game (dic).

	Returns
	-------
	new_game_stats : the game after the command execution (dic).

	Version
	-------
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
	"""

def rotate_vector_2D(vector, radian):
	"""
	Rotate a vector in a 2D space by a specified angle in radian.

	Parameters
	----------
	vector : 2D vector ton rotate (tuple(int,int)).
	radian : angle appli to the 2D vector (float).

	Return
	------
	vector : rotate vector 2d (tuple(int,int)).

	Version
	-------
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
	"""

def command_attack(ship, ship_location, coordinate, game_stats):
	"""
	determine if the attack works and do it.

	Parameters
	----------
	ship_location : coodinate of the first ship (tuple(int, int)).
	coordinate : coordinate of the tile to attack (tuple(int,int)).
	game_stats : stats of the game (dic).

	Returns
	-------
	new_game_stats : the game after the command execution (dic).

	Version
	-------
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
	"""

# (...)Ouais, ça va être bien, ça va être très bien même… Bon, bien sûr, y faut imaginer.
# - Jamel Debbouze, Astérix & Obélix : Mission Cléopâtre (2002), écrit par Alain Chabat, René Goscinny, Albert Uderzo

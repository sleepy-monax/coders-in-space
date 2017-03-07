"""
						 ___---------___
					   _".^ .^ ^.  '.. :"-_
					 /:            . .^  :.:\
				   /: .   .    .        . . .:\
				  /:               .  ^ .  . .:\
				 /.                        .  .:\
				|:                    .  .  ^. .:|
				||        .                . . !:|
				\(                           . :)/
				|. ######              .#######::|
				 |.#######           ..########:|
				 \ ########          :######## :/
				  \ ########       . ########.:/
				   \. #######       #######..:/
					 \           .   .   ..:/
					  \.       | |     . .:/
						\             ..:/
						 \.           .:/
						   \   ___/  :/
							\       :/
							 |\  .:/|
							 |  --.:|
							 "(  ..)"
							/  .  .::\
"""
def play_game(level_name, players_list, no_splash = False, no_gui = False, screen_size = (190, 50), distant_id = None, distant_ip = None, verbose_connection = False, max_rounds_count = 10, network = None):
	"""
	Main function that executes the game loop.

	Parameters
	----------
	level_name: name of the level (str).
	players_list: list of players (list).
    (optional) no_splash : ship the splash screen (bool).
	(optional) no_gui : disable game user interface (bool).
	(optional) screen_size : size of the terminal window (tuple(int, int)).
	(optional) distant_id : ID of the distant player (int).
	(optional) distant_ip : IP of the distant player (str).
	(optional) verbose_connection : anabled connection output in terminal (bool).
	(optional) max_rounds_count : number of rounds (int).

	Return
	------
	winner_name : name of the winner (str).

    Note
    ----
    Recomanded screen_size : (190, 50).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""
def new_game(level_name, players_list, connection = None):
	"""
	Create a new game from a '.cis' file.

	Parameters
	----------
	level_name : name of the path to .cis file (str).
	players_list : list of players (list).
    (optional) connection : distant player connection (tuple).

	Return
	-------
	game_stats : new game stats (dic).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""
def show_splash_game(game_stats):
	"""
	Show the splash screen.

	Parameter
	---------
	game_stats : stats of the game (dic).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""
	def clear_canvas(canvas):
		"""
		clear the canvas.
		
		Parameter
		---------
		canvas: canva to clear (dic).
		
		return
		------
		canvas: canva after cleaning (dic).
		
		Version
		-------
		Specification : Bayron Mahy (v1. 11/02/17)
		"""
def show_end_game(game_stats):
	"""
	Show the end game screen.

	Parameter
	---------
	game_stats : stats of the game (dic).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""
def is_game_continue(game_stats):
	"""
	Check if the game continue.

	Parameter
	---------
	game_stats : stats of the game (dic).

	Return
	------
	False if the game is over.

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 24/02/17)
    """
def calculate_value(player_name, game_stats):
	"""
	Calculate the total ship value of a player.

	Parameters
	----------
	player_name : name of the player to count value (str)
	game_stats : game before comand execution (dic)

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 24/02/17)
	"""
def get_game_input(player_name, buy_ships, game_stats):
	"""
	Get input from a specified player.

	Parameters
	----------
	player_name : name of the player to get input (str).
    buy_ships : True, if players buy their boats (bool).
    game_stats : stats of the game (dic).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""
def get_human_input(player_name, buy_ship, game_stats):
	"""
	Get input from a human player.

	Parameters
	----------
	player_name : Name of the player to get input from (str).
	buy_ships : True, if players buy their boats (bool).
	game_stats : stats of the game (dic).

	Returns
	-------
	player_input : input from Human (str).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""
def show_ship_list(player_name, game_stats):
	"""
	Show spaceships information on the terminal.

	Parameters
	----------
	player_name: name of the player to show the information (str).
	game_stats: stats of the game (dic).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""
def show_game_board(game_stats):
	"""
	Show game board on the teminal.

	Parameter
	---------
	game_stats : stats of the game (dic).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""
def get_ai_input(player_name, buy_ships, game_stats):
	"""
	Get input from a AI player.

	Parameters
	----------
	player_name : name of the player (str).
    buy_ships : True, if players buy their boats (bool).
	game_stats : stats of the game (dic).

	Return
	------
	ai_input : game input from AI (str).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""
def get_distant_input(game_stats):
	"""
	Get input from a distant player.

	Parameter
	---------
	game_stats : stats of the game (dic).

	Return
	------
	remote_input : input from distant player (str).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
                     Nicolas Van Bossuyt (v2. 03/03/17)
	"""
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
	canvas : 2D ascii canvas (dic).

	Version
	-------
	Specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	"""
def print_canvas(canvas, x = 0, y = 0):
	"""
	Print canvas in the terminal.

	Parameters
	----------
	canvas : canvas to print on screen (dic).
	(optional) x, y : coodinate in the terminal (int).

	Version
	-------
	Specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	"""
def put(canvas, x, y, char, color = None, back_color = None):
	"""
	Put a character in the canvas.

	Parameters
	----------
	canvas : canvas to draw in (dic).
	x, y : coordinate of were to put the char (int).
	char : char to put (str).
	(optiona) color, back_color : color for the char (string).

	Return
	------
	canvas : canvas with the char put on it (dic).

	Version
	-------
	Specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	"""
def put_ascii_art(canvas, x, y, ascii_art_name, color = None, back_color = None, transparency_char = None):
	"""
	Put a ascii art in the canvas.

	Parameters
	----------
    canvas : canvas to draw in (dic).
	x, y : coordinate to pute the art (int).
	ascii_art_name : name of the art file (string).
	canvas : canvas to put the art on it (dic).
	transparency_char : ignored char.

	Return
	------
	canvas : game view with te ascii art (dic).

	Version
	-------
	Specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	"""
def put_ascii_text(canvas, font, text, x, y, color = None, back_color = None):
	"""
	Put a ascii art text in the canvas.

	Parameters
	----------
	canvas : canvas to draw in (dic).
	font : font to use (dic).
	string : string to put in the canvas (str).

	Return
	------
	canvas : the canvas with the string on it (dic).

	Version
	-------
	Specification  : Nicolas Van Bossuyt (v1. 27/02/17)
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
	Specification  : Nicolas Van Bossuyt (v1. 27/02/17)

	Notes
	-----
	Load font in figlet format (http://www.figlet.org).
	"""
	chars = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_'abcdefghijklmnopqrstuvwxyz{|}~ÄÖÜäöüβ"
def mesure_ascii_text(font, text):
	""""
	Return the lenght of a ascii art text.

	Parameters
	----------
	font : font to mesure the string (dic).
	string : text to mesure (str)

	Return
	------
	lenght : lenght of the string (int).

	Version
	-------
	Specification  : Nicolas Van Bossuyt (v1. 27/02/17)
	"""
def put_canvas(canvas, canvas_bis, x, y):
	"""
	Put a canvas in the canvas.

	Parameters
	----------
	canvas : canvas to draw in (dic).
	canvas_bis : canvas to put in the main canvas (dic).
	x, y : coordinate of the canvas (int).

	Return
	------
	canvas : the canvas with the other canvas on it (dic).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 27/02/17)
	"""
def put_box(canvas, x, y, width, height, mode = 'double', color = None, back_color = None):
	"""
	Put a box in the canvas.

	Parameters
	----------
    canvas : canvas to draw in (dic).
	x, y : coordinate of the rectangle (int).
	width, height : size of the rectangle (int).
	mode : double ou single line <'double'|'single'> (str).
	color, back_color : color for the char (string).

	Return
	------
	canvas : canvas whith the box (dic).

	Version
	-------
	Specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	"""
def put_rectangle(canvas, x, y, width, height, char, color = None, back_color = None):
	"""
	Put a filled rectangle in the canvas.

	Parameters
	----------
    canvas : canvas to draw in (dic).
	x, y : coordinate of the rectangle (int).
	width, height : size of the rectangle (int).
	color, back_color : color for the char (string).

	Return
	------
	canvas : canvas whith the rectangle (dic).

	Version
	-------
	Specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	"""
def put_stars_field(canvas, x, y, width, height, r_seed = None):
	"""
	Put a stars field in the canvas.

	Parameters
	----------
	canvas : canvas to draw in (dic).
	x, y, w, h : location and size of the stars field (int)
	r_seed : random seed (int).

	Return
	------
	canvas : the canvas with the stars field on it (dic).

	Version
	-------
	Specification  : Nicolas Van Bossuyt (v1. 27/02/17)
	"""
def put_text(canvas, x, y, text, direction_x = 1, direction_y = 0, color = None, back_color = None):
	"""
	Put a text in the canvas.

	Parameters
	----------
	canvas : canvas to draw in (dic).
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
	Specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	"""
def set_color(text, foreground_color, background_color):
	"""
	Change the color of a text.

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

	ANSI color escape sequences : http://ascii-table.com/ansi-escape-sequences.php

    Version
	-------
	Specification  : Nicolas Van Bossuyt (v1. 27/02/17)
	"""
def parse_command(commands, player_name, game_stats):
	"""
	Parse a player's command and execute it

	Parameters
	----------
	command : command from a player (str).
	game_stats : stat of the game (dic).

	Return
	------
	game_stats : new stats of the game (dic).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""
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
	game_stats : new stats of the game (dic).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
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
	game_stats : new stats of the game (dic).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
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
	game_stats : new stats of the game (dic).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""
def command_rotate(ship, direction, game_stats):
	"""
	Rotate the ship.

	Parameters
	----------
	ship : name of the ship to Increase the speed (str).
	direction : the direction to rotate the ship <"left"|"right">(str)
	game_stats : stats of the game (dic).

	Returns
	-------
	game_stats : new stats of the game (dic).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""
def rotate_vector_2D(vector, theta):
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
	Specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	"""
def to_unit_vector(vector):
	"""
	Convert a vector to a unit vector.

	Parameter
	---------
	vector : vector to convert (tuple(float, float)).

	Return
	------
	unit_vector : a unit vector between 1 and -1 (tuple(int, int)).

	Version
	-------
	Specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	"""
	def convert(value):
		"""
		round the value from float to int with specifical criterium.
		
		parameter
		---------
		value: value to convert
		
		return
		------
		1, -1, 0: Value after round.
		
		Version
		-------
		Specification: Bayron Mahy (v1. 11/02/2017)
		"""
def do_moves(game_stats):
	"""
	Apply move to ships.

	Parameters
	----------
	game_stats : stats of the game (dic).

	Return
	------
	game_stats : new stats of the game (dic).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""
def take_abandonned_ship(game_stats):
	"""
    Determine who become the owner of the abandonned ship.

	Parameters
	----------
	game_stats : stats of the game (dic).

	Returns
	-------
	game_stats : new stats of the game (dic).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""
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
	game_stats : new stats of the game (dic).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
	"""
def get_distance(coord1, coord2, size):
	"""
	Get distance between two point in a tore space.

	Parameters
	----------
	coord1 : coordinate of the first point (tupe(int, int)).
	coord2 : coordinate of the second point (tupe(int, int)).
	size : size of the tore (tupe(int, int))

	Return
	------
	Distance : distance of the two point (int).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
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
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
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
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""
def create_game_board(file_name, board_size, lost_ships_count):
	"""
	Create a new "coders in space"'s board file.

	Parameters
	----------
	file_name : name of the cis file (str).
	board_size : size of the game board (tuple(int, int)).
	lost_ships_count : number of lost ship on the game board (int).

	Version
	-------
	Specification  : Nicolas Van Bossuyt (v1. 25/02/17)
	"""

# -*- coding: utf-8 -*-
import string
from command import *
from gui import *
from ai import *
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
	Main game function thats run the game loop.

	parameters
	----------

	level_name: name of the level (str)
	players_list: list of the players(tuple)

	Version
	-------
	specification : Bayron Mahy (v1. 14/02/2017)

	implementation : Not done yet
	"""

	game_stats = new_game(level_name, player_list)

	# Players create their ships.

	# Game loop.
	while game_stats['is_game_continue']:

		# getting players input.

		# Do ships moves.

		# Do Attack

		pass

def new_game(level_name, players_list):
	"""
	Create a new game from a '.cis' file.

	Parameters
	----------
	level_name : name of the level to play in (str).
	players_list : list of players (list).

	Return
	-------
	game_stats : new game stats (dic).

	Version
	-------
	specification : Nicolas Van Bossuyt (v1. 09/02/2017)
					Bayron Mahy (v2. 10/02/2017)

	implementation : Bayron Mahy (v1. 10/02/2017)
			 		Bayron Mahy (v2. 10/02/2017)
			 		Nicolas Van Bossuyt (v3. 10/02/2017)
			 		Bayron Mahy (v4. 10/02/2017)
	"""

	# Create game_stats dictionary.
	game_file = parse_game_file(level_name)
	game_stats = {'board':{}, 'players':{},'model_ship':{}, 'ships': {},'board_size': game_file['size'],'level_name': level_name, 'nb_rounds': 0, 'max_nb_rounds': 10*len(players_list), 'is_game_continue':True}

	# Create ship specs sheet.
	game_stats['model_ship']['fighter'] = {'icon': u'F', 'max_heal':3, 'max_speed':5, 'damages':1, 'range':5, 'price':10}
	game_stats['model_ship']['destroyer'] = {'icon': u'D', 'max_heal':8, 'max_speed':2, 'damages':2, 'range':7, 'price':20}
	game_stats['model_ship']['battlecruiser'] = {'icon': u'B', 'max_heal':20, 'max_speed':1, 'damages':4, 'range':10, 'price':30}

	# Create the game board.
	for line in range(game_file['size'][0]):
		for column in range(game_stats['board_size'][1]):
			game_stats['board'][(line,column)] = []

	# Create players.
	for player in players_list:
		if player == 'ai' or play_game == 'distant':
			player_type = player
		else:
			player_type = 'human'

		game_stats['players'][player] = {'name': player, 'money':100, 'nb_ship': 0, 'type':player_type, 'color':''}

	# place lost ships
	for ships in game_file['ships']:
		game_stats['ships'][ships[2]]= { 'type':ships[3], 'heal_points':game_stats['model_ship'][ships[3]]['max_heal'],'direction':ships[4], 'speed':0, 'owner': 'none', 'postion': [ships[0],ships[1]] }
		game_stats['board'][(ships[0],ships[1])].append(ships[2])

	return game_stats

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
	specification : Nicolas Van Bossuyt (v1. 09/02/2017)
	implementation : Nicolas Van Bossuyt (v1. 09/02/2017)
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
		specification : Nicolas Van Bossuyt (v1. 09/02/2017)
		implementation : Nicolas Van Bossuyt (v1. 09/02/2017)
		"""
		vector = ()

		if direction == 'up':
			vector = (0,1)

		elif direction == 'up-right':
			vector = (1,1)

		elif direction == 'right':
			vector = (1,0)

		elif direction == 'down-right':
			vector = (1,-1)

		elif direction == 'down':
			vector = (0,-1)

		elif direction == 'down-left':
			vector = (-1,-1)

		elif direction == 'left':
			vector = (-1,0)

		elif direction == 'up-left':
			vector = (-1,1)

		return vector

	# Split file lines and remove '\n' chars.
	with file(path,'r') as cis_file:
		file_content = [line.strip() for line in cis_file]

	# Get the size of the gameboard.
	size_str = file_content[0].split(' ')
	size = (int(size_str[0]),int(size_str[1]))

	# Get lost space ship in the new game.
	ships_list = []
	for line_index in range(len(file_content) - 1):
		try:
			ship_str = file_content[line_index + 1].split(' ')
			ship_name_and_type = ship_str[2].split(':')
			ship = (int(ship_str[0]), int(ship_str[1]), ship_name_and_type[0], ship_name_and_type[1], direction_to_vector2D(ship_str[3]))
			ships_list.append(ship)
		except:
			pass

	# Create parsed data dictionary and return it.
	parsed_data = {'size':size,'ships':ships_list}

	return parsed_data

def show_board(game_stats, color = True):
	"""
	Show the game to the user screen.

	Parameter
	---------
	game_stats : game to show on screen (dic).

	Version
	-------
	specification : Nicolas Van Bossuyt (v1. 09/02/2017)
	implementation : Nicolas Van Bossuyt (v1. 09/02/2017)

	"""

	# Create a new canvas.
	c = creat_canvas(190, 50, color)

	# Create the board frame.
	on_screen_board_size = (game_stats['board_size'][0]*3 + 5, game_stats['board_size'][1] + 3)
	put_box(c, 0, 0, on_screen_board_size[0], on_screen_board_size[1])
	put_string(c, 2, 0, u'| Code in space : %s |' % (game_stats['level_name']))

	# Put horizontal coordinate.
	coordinate_string = ''
	for i in range(1, game_stats['board_size'][0] + 1):
		value_string = str(i)
		if len(value_string) == 1:
			value_string = ' ' + value_string
		value_string += ' '
		coordinate_string += value_string

	put_string(c, 4, 1, coordinate_string, 1, 0, 'blue', 'white')

	# Put vertical coordinate.
	for i in range(1, game_stats['board_size'][1] +1):
		value_string = str(i)
		if len(value_string) == 1:
			value_string = ' ' + value_string
		put_string(c,1,i + 1,value_string + ' ', 1,0, 'blue', 'white')

	# Put game board.
	for x in range(game_stats['board_size'][0]):
		for y in range(game_stats['board_size'][1]):
			on_screen_board_tile = (x*3 + 4, y + 2)

			# Check how many ship there are in the board tile.
			if len(game_stats['board'][(x,y)]) == 0:
				# When there are only one, show juste nothing.
				put_string(c, on_screen_board_tile[0], on_screen_board_tile[1], ' .')

			elif len(game_stats['board'][(x,y)]) == 1:
				# When there are one, show somme information about.
				ship_name = game_stats['board'][(x,y)][0]
				ship_type = game_stats['ships'][ship_name]['type']
				ship_icon = game_stats['model_ship'][ship_type]['icon']
				ship_owner = game_stats['ships'][ship_name]['owner']

				if ship_owner == 'none':
					# The ship is a abandoned one.
					put_string(c, on_screen_board_tile[0] + 1, on_screen_board_tile[1], ship_icon,1,0,'white', 'green')
				else:
					# The ship have a owner.
					ship_owner_color = game_stats['player'][['ships'][ship_name]['owner']]['color']
					put_string(c, on_screen_board_tile[0] + 1, on_screen_board_tile[1], ship_icon,1,0,'white', ship_owner_color)

			else:
				# in other case show how many ship there are in the tile.
				put_string(c, on_screen_board_tile[0], on_screen_board_tile[1], '!' + str(len(game_stats['board'][(x,y)])),1,0,'white', 'green')

	# Create player liste frame.
	on_screen_player_board_size = (len(game_stats['players']) * 30 + 2, c['size'][1] - on_screen_board_size[1])
	put_box(c, 0, on_screen_board_size[1], on_screen_player_board_size[0], on_screen_player_board_size[1])
	put_string(c, 1, on_screen_board_size[1], u'| Players |')

	player_count = 0
	for player in game_stats['players']:
		location = ((player_count * 30) + 1, on_screen_board_size[1] + 1,)
		put_box(c, location[0], location[1], 30, 5, 'single')

		# Put player informations.
		put_string(c, location[0] + 2, location[1] , '| ' + game_stats['players'][player]['name'] + ' |')
		put_string(c, location[0] + 2, location[1] + 1, 'Type : ' + game_stats['players'][player]['type'])
		put_string(c, location[0] + 2, location[1] + 2, 'Money : ' + str(game_stats['players'][player]['money']) + '$')
		put_string(c, location[0] + 2, location[1] + 3, 'Spaceship count : ' + str(game_stats['players'][player]['nb_ship']))

		player_count += 1

	# Show the game board in the terminal.
	print_canvas(c)

def get_player_input(player_name, game_stats):
	"""
	Get and return input form the player.

	Parameter:
	----------
	Player_name : Name of the player (str).
	game_stats : the stats of the game (dic).

	Return:
	-------
	player_input : the input from the player (str).
	"""

	raise NotImplementedError

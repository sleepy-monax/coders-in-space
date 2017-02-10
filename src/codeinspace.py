# -*- coding: utf-8 -*-
import string
from command import *
from gui import *
from ai import *

def new_game(path, list_players):
	"""
	Create a new game from a '.cis' file.

	Parameters
	----------
	path : to the cis file (str).
	list_players: list of players (list).

	Return
	-------
	game_stats : new game stats (dic).

	Version
	-------
	specification : Nicolas Van Bossuyt (v1. 09/02/2017)
					Bayron Mahy (v2. 10/02/2017)

	implementation : Bayron Mahy (v1. 10/02/2017)
					 Bayron Mahy (v2. 10/02/2017)
					 Nicolas Van Bossuyt (v3. 11/02/2017)
	"""

	# Create game_stats dictionary.
	game_stats = {'board':{}, 'players':{},'model_ship':{}, 'ship': {},'board_size': (0,0), 'rounds': 0, 'max_nb_rounds': 10*len(list_players)}
	game_file = parse_game_file(path)

	# Create the game board.
	for line in range(game_file['size'][0]):
			for column in range(game_file['size'][1]):
				game_stats['board'][(line,column)] = '$none'
	game_stats['board_size'] = game_file['size']

	# Create players.
	for player in list_players:
		if player == 'ai':
			player_type = 'ai'
		elif play_game == 'distant':
			player_type = 'distant'
		else:
			player_type = 'human'

		game_stats['players'][player] = {'name': player, 'money':100, 'nb_ship': 0, 'type':player_type}

	# Create ship specs sheet.
	game_stats['model_ship']['fighter']={'max_heal':3, 'max_speed':5, 'damages':1, 'range':5, 'price':10}
	game_stats['model_ship']['destroyer']={'max_heal':8, 'max_speed':2, 'damages':2, 'range':7, 'price':20}
	game_stats['model_ship']['battlecruiser']={'max_heal':20, 'max_speed':1, 'damages':4, 'range':10, 'price':30}

	return game_stats

def parse_game_file(path):
	"""
	Parse a cis file give us his content.

	Parameter
	---------
	path : path of the cis file (str).

	Return
	------
	parsed_data : data containe in the cis file (dic).

	Version
	-------
	specification : Nicolas Van Bossuyt (v1. 09/02/2017)
	implementation : Nicolas Van Bossuyt (v1. 09/02/2017)
	"""

	# Split file lines and remove '\n' chars.
	with file(path,'r') as f:
		file_content = [i.strip() for i in f]

	# Get the size of the gameboard.
	size_str = file_content[0].split(' ')
	size = (int(size_str[0]),int(size_str[1]))

	# Get lost space ship in the new game.
	ships_list = []
	for i in range(len(file_content) - 1):
		ship_str = file_content[i + 1].split(' ')
		ship = (int(ship_str[0]), int(ship_str[1]), ship_str[2])
		ships_list.append(ship)

	# Create parsed data dictionary and return it.
	parsed_data = {'size':size,'ships':ships_list}

	return parsed_data

def play_game():
	"""
	Main game function thats run the game loop.
	"""

	raise NotImplementedError

def show_board(game_stats):
	"""
	Show the game to the user screen.

	Parameter
	---------
	game_stats : game to show on screen (dic).
	"""

	# Create a new game_view.
	v = creat_game_view(160,60)

	# Create the board frame.
	on_screen_board_size = (game_stats['board_size'][0]*3 + 5, game_stats['board_size'][1] + 3)
	put_box(v, 0, 0, on_screen_board_size[0], on_screen_board_size[1])
	put_string(v, 2, 0, '| Game Board |', 1, 0, 'blue', 'on_white')

	# Put horizontal coordinate.
	coordinate_string = ''
	for i in range(game_stats['board_size'][0]):
		value_string = str(i)
		if len(value_string) == 1:
			value_string = ' ' + value_string

		value_string += ' '

		coordinate_string += value_string

	put_string(v,4,1,coordinate_string, 1,0, 'blue', 'on_white')

	# Put vertical coordinate.
	for i in range(game_stats['board_size'][1]):
		value_string = str(i)
		if len(value_string) == 1:
			value_string = ' ' + value_string
		put_string(v,2,i + 2,value_string, 1,0, 'blue', 'on_white')

	# Create player liste frame.
	on_screen_player_board_size = (v['size'][0] - on_screen_board_size[0] - 1, on_screen_board_size[1])
	put_box(v, on_screen_board_size[0] + 1, 0, on_screen_player_board_size[0], on_screen_player_board_size[1])
	put_string(v, on_screen_board_size[0] + 3, 0, '| Players |', 1,0, 'blue', 'on_white')

	player_count = 0
	for player_key in game_stats['players']:
		location = (on_screen_board_size[0] + 2, 1 + (player_count * 6))
		put_box(v, location[0], location[1], on_screen_player_board_size[0] - 2, 6,  'single')

		# Put player informations.
		put_string(v, location[0] + 1, location[1] + 1, game_stats['players'][player_key]['name'],1,0, 'blue', 'on_white')
		put_string(v, location[0] + 1, location[1] + 2, 'Type : ' + game_stats['players'][player_key]['type'])
		put_string(v, location[0] + 1, location[1] + 3, 'Money : ' + str(game_stats['players'][player_key]['money']) + '$', 1,0, 'yellow')
		put_string(v, location[0] + 1, location[1] + 4, 'Spaceship count : ' + str(game_stats['players'][player_key]['nb_ship']))

		player_count += 1


	print_game_view(v)

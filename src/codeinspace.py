# -*- coding: utf-8 -*-
import string
from command import *
from gui import *
from ai import *
"""
 __   __   __   ___               __   __        __   ___
/  ` /  \ |  \ |__     | |\ |    /__` |__)  /\  /  ` |__
\__, \__/ |__/ |___    | | \|    .__/ |    /~~\ \__, |___

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
  :.. .  :-  : .:  ::|.#######           ..########:|
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
 
                 .___       .__                                            
  ____  ____   __| _/____   |__| ____     _________________    ____  ____  
_/ ___\/  _ \ / __ |/ __ \  |  |/    \   /  ___/\____ \__  \ _/ ___\/ __ \ 
\  \__(  <_> ) /_/ \  ___/  |  |   |  \  \___ \ |  |_> > __ \\  \__\  ___/ 
 \___  >____/\____ |\___  > |__|___|  / /____  >|   __(____  /\___  >___  >
     \/           \/    \/          \/       \/ |__|       \/     \/    \/ 
"""
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
			 Nicolas Van Bossuyt (v3. 10/02/2017)
			 Bayron Mahy (v4. 10/02/2017)
	"""

	# Create game_stats dictionary.
	game_file = parse_game_file(path)
	game_stats = {'board':{}, 'players':{},'model_ship':{}, 'ships': {},'board_size': game_file['size'], 'nb_rounds': 0, 'max_nb_rounds': 10*len(list_players)}

	# Create the game board.
	for line in range(game_file['size'][0]):
		for column in range(game_stats['board_size'][1]):
			game_stats['board'][(line,column)] = []

	# Create players.
	for player in list_players:
		if player == 'ai' or play_game == 'distant':
			player_type = player
		else:
			player_type = 'human'

		game_stats['players'][player] = {'name': player, 'money':100, 'nb_ship': 0, 'type':player_type, 'color':''}

	# Create ship specs sheet.
	game_stats['model_ship']['fighter']={'icon': u'F', 'max_heal':3, 'max_speed':5, 'damages':1, 'range':5, 'price':10}
	game_stats['model_ship']['destroyer']={'icon': u'D', 'max_heal':8, 'max_speed':2, 'damages':2, 'range':7, 'price':20}
	game_stats['model_ship']['battlecruiser']={'icon': u'B', 'max_heal':20, 'max_speed':1, 'damages':4, 'range':10, 'price':30}

	#place the bonus ships
	for ships in game_file['ships']:
		game_stats['ships'][ships[2]]= { 'type':ships[3], 'heal_points':game_stats['model_ship'][ships[3]]['max_heal'],'direction':ships[4], 'speed':0, 'owner': 'none', 'postion': [ships[0],ships[1]] }
		game_stats['board'][(ships[0],ships[1])].append(ships[2])

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
	def direction_to_vector2D(direction):
		"""
		Convert a string direction to a vector2D.

		Parameter
		---------
		direction : direction to convert <up|down|left|right|up-left|up-right|down-left|down-right>(str).

		Return
		------
		vector : vector2D from direction (tuple(float, float)).
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
	with file(path,'r') as f:
		file_content = [i.strip() for i in f]

	# Get the size of the gameboard.
	size_str = file_content[0].split(' ')
	size = (int(size_str[0]),int(size_str[1]))

	# Get lost space ship in the new game.
	ships_list = []
	for i in range(len(file_content) - 1):
		try:
			ship_str = file_content[i + 1].split(' ')
			ship_name_and_type = ship_str[2].split(':')
			ship = (int(ship_str[0]), int(ship_str[1]), ship_name_and_type[0], ship_name_and_type[1], direction_to_vector2D(ship_str[3]))
			ships_list.append(ship)
		except:
			pass

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
	v = creat_game_view(190,50)

	# Create the board frame.
	on_screen_board_size = (game_stats['board_size'][0]*3 + 5, game_stats['board_size'][1] + 3)
	put_box(v, 0, 0, on_screen_board_size[0], on_screen_board_size[1])
	put_string(v, 2, 0, u'| # Game Board |')

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

	# Put game board.
	for x in range(game_stats['board_size'][0]):
		for y in range(game_stats['board_size'][1]):
			on_screen_board_tile = (x*3 + 4, y + 2)

			# Check how many ship there are in the board tile.
			if len(game_stats['board'][(x,y)]) == 0:
				# When there are only one, show juste nothing.
				put_string(v, on_screen_board_tile[0], on_screen_board_tile[1], ' .')

			elif len(game_stats['board'][(x,y)]) == 1:
				# When there are one, show somme information about.
				ship_name = game_stats['board'][(x,y)][0]
				ship_type = game_stats['ship'][ship_name]['type']
				ship_icon = game_stats['model_ship'][ship_type]['icon']
				ship_owner = game_stats['ship'][ship_name]['owner']

				if ship_owner == 'none':
					put_string(v, on_screen_board_tile[0] + 1, on_screen_board_tile[1], ship_icon,1,0,'white', 'on_green')
				else:
					ship_owner_color = game_stats['player'][['ship'][ship_name]['owner']]['color']
					put_string(v, on_screen_board_tile[0] + 1, on_screen_board_tile[1], ship_icon,1,0,'white', 'on_green')

			else:
				pass
				# in other case show how many ship there are in the tile.


	# Create player liste frame.
	on_screen_player_board_size = (v['size'][0] - on_screen_board_size[0] - 1, on_screen_board_size[1])
	put_box(v, on_screen_board_size[0] + 1, 0, on_screen_player_board_size[0], on_screen_player_board_size[1])
	put_string(v, on_screen_board_size[0] + 3, 0, u'| (^_^) Players |')

	player_count = 0
	for player in game_stats['players']:
		location = (on_screen_board_size[0] + 2, 2 + (player_count * 6))
		put_box(v, location[0], location[1], on_screen_player_board_size[0] - 2, 6, 'single')

		# Put player informations.
		put_string(v, location[0] + 2, location[1] , '| ' + game_stats['players'][player]['name'] + ' |')
		put_string(v, location[0] + 2, location[1] + 2, 'Type : ' + game_stats['players'][player]['type'])
		put_string(v, location[0] + 2, location[1] + 3, 'Money : ' + str(game_stats['players'][player]['money']) + '$')
		put_string(v, location[0] + 2, location[1] + 4, 'Spaceship count : ' + str(game_stats['players'][player]['nb_ship']))

		player_count += 1


	print_game_view(v)

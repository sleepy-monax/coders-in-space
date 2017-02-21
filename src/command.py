# -*- coding: utf-8 -*-
import math

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
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
	implementation : Nicolas Van Bossuyt (V1. 10/2/2017)
	"""

	commands = commands.split(' ')
	for cmd in commands:
		try:
			sub_cmd = cmd.split(':')
			ship_name = player_name + '_' + sub_cmd[0]
			ship_action = sub_cmd[1]
		except:
			continue

		if ship_action == 'slower' or ship_action == 'faster':
			# Speed command :
			game_stats = command_change_speed(ship_name, ship_action, game_stats)
		elif ship_action == 'left' or ship_action == 'right':
			# Rotate command :
			game_stats = command_rotate(ship_name, ship_action, game_stats)
		else:
			# Attack command :
			ship_action = ship_action.split('-')
			coordinate = (int(ship_action[0]) - 1, int(ship_action[1]) - 1)
			game_stats['pending_attacks'].append((ship_name, game_stats['ships'][ship_name]['position'], coordinate))

	return game_stats

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
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
	implementation : Nicolas Van Bossuyt (v1. 14/2/17)
	"""

	for ship in ships.split(' '):
		if ship == '':
			continue

		ship = ship.split(':')
		ship_price = game_stats['model_ship'][ship[1]]['price']

		if ship_price <= game_stats['players'][player]['money']:
			game_stats['players'][player]['money'] -= ship_price
			create_ship(player, '%s_%s' % (player, ship[0]), ship[1], game_stats)

	return game_stats

def create_ship(player_name, ship_name, ship_type, game_stats):
	game_stats['ships'][ship_name] = {'type':ship_type, 'heal_points':game_stats['model_ship'][ship_type]['max_heal'], 'direction':game_stats['players'][player_name]['ships_starting_direction'], 'speed':0, 'owner': player_name, 'position': game_stats['players'][player_name]['ships_starting_point']}
	game_stats['board'][game_stats['players'][player_name]['ships_starting_point']].append(ship_name)
	game_stats['players'][player_name]['nb_ships'] += 1

	return game_stats

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
	implementation : Bayron Mahy (v1. 10/02/2017)
	"""
	type = game_stats['ships'][ship]['type']

	# Make the ship move faster.
	if change == 'faster' and game_stats['ships'][ship]['speed'] < game_stats['model_ship'][type]['max_speed']:
		game_stats['ships'][ship]['speed']+=1

	# Make the ship move slower.
	elif change == 'slower' and gamestats['ship'][ship]['speed'] > 0:
		game_stats['ships'][ship]['speed']-=1

	# Show a message when is a invalide change.
	else:
		print 'you cannot make that change on the speed of this ship'

	return game_stats

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
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
	implementation : Nicolas Van Bossuyt (v1. 10/2/2017)
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
		specification : Nicolas Van Bossuyt (v1. 10/2/17)
		implementation : Nicolas Van Bossuyt (v1. 10/2/2017)
		"""

		# Here is were the magic append.
		new_vector = ( int(vector[0] * math.cos(radian) - vector[1] * math.sin(radian)), int(vector[0] * math.sin(radian) + vector[1] * math.cos(radian)))
		return new_vector

	if direction == 'left':
		game_stats['ships'][ship]['direction'] = rotate_vector_2D(game_stats['ships'][ship]['direction'], -math.pi / 4)
	elif direction == 'right':
		game_stats['ships'][ship]['direction'] = rotate_vector_2D(game_stats['ships'][ship]['direction'], math.pi / 4)

	return game_stats

def command_attack(ship, ship_coordinate, target_coordinate, game_stats):
	"""
	determine if the attack works and do it.

	Parameters
	----------
	ship_coordinate : coodinate of the first ship (tuple(int, int)).
	target_coordinate : coordinate of the tile to attack (tuple(int,int)).
	game_stats : stats of the game (dic).

	Returns
	-------
	new_game_stats : the game after the command execution (dic).

	Version
	-------
	specification : Nicolas Van Bossuyt (v1. 10/2/2017)
	implementation : Alisson Leist (v1. 14/2/2017)
	"""

	# Retriving information from game_stats.
	board_width=game_stats['board_size'][0]
	board_height=game_stats['board_size'][1]
	damages=game_stats['ships'][ship]['damages']

	# Getting distance between ship and taget.
	if target_coordinate[0] + ship_coordinate[0] <=board_width/2:
		if target_coordinate[0] < ship_coordinate[0]:
			target_coordinate[0]+=board_width
		else:
			target_coordinate[0]+=board_width

	if target_coordinate[1] + ship_coordinate[1]<=board_height/2:
		if target_coordinate[1] < ship_coordinate[1]:
			target_coordinate[1]+=board_height
		else:
			ship_coordinate[1]+=board_height

	if abs((target_coordinate[0] - ship_coordinate[0])) + abs((target_coordinate[1] - ship_coordinate[1])) <= game_stats ['ships'][ship]['range'] :
		if not game_stats['board'][target_coordinate] == []:
			game_stats['nb_rounds']=0
			# Give damages to all ship on targe coordinate.
			for target_ship in game_stats['board'][target_coordinate]:
				# Give damages to the taget ship.
				game_stats['ships'][target_ship]['heal_point']-=damages
				if game_stats['ships'][target_ship]['heal_point']<=0:
					# Remove the space ship.
					game_stats['board'][target_coordinate].remove(target_ship)
					game_stats['players'][game_stats['ships'][target_ship]['owner']]['nb_ships'] -=1

	return game_stats

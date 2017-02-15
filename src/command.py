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
	specification v1. Nicolas Van Bossuyt (10/2/2017)
	implementation v1. Nicolas Van Bossuyt (10/2/2017)
	"""
	commands = commands.split(' ')

	for cmd in commands:
		sub_cmd = cmd.split(':')
		ship_name = player_name + '_' + sub_cmd[0]
		ship_action = sub_cmd[1]

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
			game_stats[pending_attacks].append((ship_name, game_stats['ships'][ship_name]['location'], coordinate))

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
	"""

	for ship in ships.split(' '):
		ship = ship.split[':']
		ship_price = game_stats['model_ship'][ship[1]]['price']

		if ship_price >= game_stats['players'][player]['money']:
			game_stats['players'][player]['money'] -= ship_price
			create_ship(player_name, '%s_%s' % (player_name, ship[0]), ship[1], game_stats)

def create_ship(player_name, ship_name, ship_type, game_stats):
	game_stats['ships'][ship_name] = { 'type':ships[3], 'heal_points':game_stats['model_ship'][ship_type]['max_heal'],'direction':game_stats['player_name']['ships_starting_direction'], 'speed':0, 'owner': player_name, 'postion': game_stats['player_name']['ships_starting_point']}
	game_stats['board'][game_stats['player_name']['ships_starting_point']].append(ship_name)

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
	specification : Nicolas Van Bossuyt (v1. 09/02/2017)
	implementation : Bayron Mahy (v1. 10/02/2017)
	"""
	type = game_stats['ship'][ship]['type']

	# Make the ship move faster.
	if change == 'faster' and gamestats['ship'][ship]['speed'] < gamestats['model_ship'][type]['max_speed']:
		game_stats['ships'][ship]['speed']+=1

	# make the ship move slower.
	elif change == 'slower' and gamestats['ship'][ship]['speed'] > 0:
		game_stats['ships'][ship]['speed']-=1

	# show a message when is a invalide change.
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

 	specification v1. Nicolas Van Bossuyt (10/2/2017)
	implementation v1. Nicolas Van Bossuyt (10/2/2017)
	"""

	def rotate_vector_2D(vector, radian):
		"""
		Rotate a vector in a 2D space by a specified angle in radian.

		Parameters        ----------
		vector : 2D vector ton rotate (tuple(int,int)).
		radian : angle appli to the 2D vector (float).

		return
		------
		vector : rotate vector 2d (tuple(int,int)).

		Version
		-------
		specification v1. Nicolas Van Bossuyt (10/2/2017)
		implementation v1. Nicolas Van Bossuyt (10/2/2017)
		"""
		new_vector = (.0,.0)

		# Here is were the magic append.
		new_vector[0] = vector[0] * math.cos(radian) - vector[1] * math.sin(radian)
		new_vector[1] = vector[0] * math.sin(radian) + vector[1] * math.cos(radian)
		return new_vector

	if direction == 'left':
		gamestats['ships'][ship]['direction'] = rotate_vector_2D(gamestats['ships'][ship]['direction'], -math.pi / 4)
	elif direction == 'right':
		gamestats['ships'][ship]['direction'] = rotate_vector_2D(gamestats['ships'][ship]['direction'], math.pi / 4)

	return game_stats

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
	new_game_stats : the game after the command execution.

	Version
	-------
	specification v1. Nicolas Van Bossuyt (10/2/2017)
	implementation v1.Alisson Leist (14/2/2017)
	"""
	board_width=game_stats['board_size'][0]
	board_lenght=game_stats['board_size'][1]

	damages=game_stats ['ships'][ship]['damages']

	if coordinate[0]+ship_location[0]<=board_width/2:
		if coordinate[0]<ship_location[0]:
			coordinate[0]+=board_width
		else:
			ship_location[0]+=board_width

	if coordinate[1]+ship_location[1]<=board_lenght/2:
		if coordinate[1]<ship_location[1]:
			coordinate[1]+=board_lenght
		else:
			ship_location[1]+=board_lenght
	distance= abs((coordinate[0] - ship_location[0])) + abs((coordinate[1] - ship_location[1]))


	if distance<=game_stats ['ships'][ship]['range'] :

		if not game_stats['board'][coordinate] == []:
			game_stats['nb_rounds']=0

			for element in game_stats['board'][coordinate] :

				game_stats['ships'][element]['heal_point']-=damages

				if game_stats['ships'][element]['heal_point']<=0:
					game_stats['board'][coordinate].remove(element)
	return new_game_stats

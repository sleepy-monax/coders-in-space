# -*- coding: utf-8 -*-
import math

def parse_command(commands, game_stats):
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
		ship_name = sub_cmd[0]
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
			game_stats = command_attack(ship_name, coordinate, game_stats)

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
		game_stats['ship'][ship]['speed']+=1

	# make the ship move slower.
	elif change == 'slower' and gamestats['ship'][ship]['speed'] > 0:
		game_stats['ship'][ship]['speed']-=1

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
		gamestats['ship'][ship]['direction'] = rotate_vector_2D(gamestats['ship'][ship]['direction'], -math.pi / 4)
	elif direction == 'right':
		gamestats['ship'][ship]['direction'] = rotate_vector_2D(gamestats['ship'][ship]['direction'], math.pi / 4)

	return game_stats

def command_attack(ship, coordinate, game_stats):
	"""
	Rotate the ship.

	Parameters
	----------
	ship : name of the ship to Increase the speed.
	coordinate : coordinate of the tile to attack (tuple(int,int)).
	game_stats : stats of the game (dic).

	Returns
	-------
	new_game_stats : the game after the command execution.
	"""
	board_width=game_stats['board_size'][0]
	board_lenght=game_stats['board_size'][1]

	damages=game_stats ['ships'][ship]['damages']
	ship_location=game_stats['ships'][ship]['position']

	distance= (coordinate[0] - ship_location[0]) + (coordinate[1] - ship_location[1])
	distance_2=(ship_location[0]+board_width -coordinate[0]) + (coordinate[1]-ship_location[1])
	

	if distance<=game_stats ['ships'][ship]['range'] :

		if not game_stats['board'][coordinate] == []:
		    game_stats['nb_rounds']=0

		    for element in game_stats['board'][coordinate] :

		        game_stats['ships'][element]['heal_point']-=damages

		        if game_stats['ships'][element]['heal_point']<=0:
			    game_stats['board'][coordinate].remove(element)
	return new_game_stats

def convert_coordinate(coordinate):
    abscissa=game_stats[coordinate][0]
    orderly=game_stats[coordinate][1]

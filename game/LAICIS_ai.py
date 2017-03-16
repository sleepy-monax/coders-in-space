# -*- coding: utf-8 -*-
from random import *
from pickle import *
from math import exp

# L.A.C.I.S.
# ==============================================================================
# [L]earning [A]rtificial [I]nteligence for [C]oders [I]n [S]pace.

def get_ai_input(game_stats, player_name):
	"""
	Get input from a AI player.

	Parameter
	---------
	player_name: name of the player (str).
	buy_ships: True, if players buy their boats (bool).
	game_stats: stats of the game (dic).

	Return
	------
	ai_input: game input from AI (str).

	Version
	-------
	Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

    return ''

def get_ai_spaceships(player_name, game_stats):
    """
    Get ships buy inputs from the ai.

    Parameters
    ----------
    player_name: name of the player (str).
    buy_ships: True, if players buy their boats (bool).
    game_stats: stats of the game (dic).

    Return
    ------
    ai_input: game input from AI (str).

    Version
    -------
    Specification: Nicolas Van Bossuyt (v1. 10/03/17)
    Implementation: Nicolas Van Bossuyt (v1. 10/03/17)
    """
    return 'arow:fighter stardestroyer:destroyer race_cruiser:battlecruiser'

def get_dumb_ai_input(game_stats, player_name):
	"""
	Get input from a AI player.

	Parameter
	---------
	player_name: name of the player (str).
	buy_ships: True, if players buy their boats (bool).
	game_stats: stats of the game (dic).

	Return
	------
	ai_input: game input from AI (str).

	Version
	-------
	Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

    action = ['faster', 'slower', 'left', 'right']

    ai_input = ''

    for ship in game_stats['ships']:
        if (game_stats['ships'][ship]['owner'] == player_name):
            ai_input += ship.replace(player_name + '_','') + ':' + action[randint(0, len(action) - 1 )] + ' '

    return ai_input[:-1]
def get_dumb_ai_spaceships(player_name, game_stats):
    """
    Get ships buy inputs from the ai.

    Parameters
    ----------
    player_name: name of the player (str).
    buy_ships: True, if players buy their boats (bool).
    game_stats: stats of the game (dic).

    Return
    ------
    ai_input: game input from AI (str).

    Version
    -------
    Specification: Nicolas Van Bossuyt (v1. 10/03/17)
    Implementation: Nicolas Van Bossuyt (v1. 10/03/17)
    """


    return 'arow:fighter stardestroyer:destroyer race_cruiser:battlecruiser'

# AI - command corection.
# ------------------------------------------------------------------------------
# Because nothing is perfect.

def turn(game_stats, ship, direction):
def speed(game_stats, ship, change):
def attack(game_stats, ship):

def get_nearby_ship(game_stats, ship_owner):
def get_distance(coord1, coord2, size):
    """
    Get distance between two point in a tore space.

    Parameters
    ----------
    coord1: coordinate of the first point (tupe(int, int)).
    coord2: coordinate of the second point (tupe(int, int)).
    size: size of the tore (tupe(int, int))

    Return
    ------
    Distance: distance of the two point (int).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt, Alisson Leist (v1. 14/2/17)
                    Nicolas Van Bossuyt (v2. 09/03/17)
    """

    def distance(a, b, size):
        size -= 1
        if abs(a - b) > size / 2:
            a += size
        return abs(a - b)

    return distance(coord1[0], coord2[0], size[0]) + distance(coord1[1], coord2[1], size[1])
def convert_coordinates(coord, size):
    """
    Apply tore space to coordinates.

    Parameters
    ----------
    coord: coordinates to convert (tuple(int, int))
    size: Size of the tore.

    Return
    ------
    converted_coord: coord with the tore applied.
    """
    def convert(a, size):
        # Apply toric space.
        if a >= size:
            a -= size
        elif a < 0:
            a += size

        return a

    return (convert(coord[0], size[0]), convert(coord[1], size[1]))

# Neural network
# ------------------------------------------------------------------------------
# Neural computing is cool :)

def create_neural_network(neural_structure):
	"""
	Create a neural network from a neural structure description.

	Parameter
	---------
	neural_structure: neural structure description of the network (tuple(ints)).

	Return
	------
	neural_network: neural network create from the neural structure description (dic).
	"""
	neural_network = {}
	layer = 0

	for layer_nodes_count in neural_structure:
		neural_network[layer] = {}
		for node in range(layer_nodes_count):
			neural_network[layer][node] = {'value': 0, 'links': {}}
			if not layer == 0:
				for link in range(len(neural_network[layer - 1 ])):
					neural_network[layer][node]['links'][link] = randint(-100, 100) * 0.01

		layer += 1

	return neural_network

def compute_neural_network(neural_network, neural_input):
	"""
	Compute output from a neural network with specified inputes.

	Parameters
	----------
	neural_network: neural network to use (dic).
	neural_input: data to input in the neural network (list(float)).

	Return
	------
	neural_ouput: output from the neural_network (list(float))
	"""

	# Compute the neural network.
	for layer in neural_network:
		for node in neural_network[layer]:
			if layer == 0:
				neural_network[layer][node]['value'] = neural_input[node]
			else:
				neural_network[layer][node]['value'] = 0
				for link in neural_network[layer][node]['links']:
					neural_network[layer][node]['value'] += neural_network[layer - 1][link]['value'] * neural_network[layer][node]['links'][link]
				neural_network[layer][node]['value'] = sigmoid(neural_network[layer][node]['value']) * 2 - 1
	output = []
	layer = len(neural_network) - 1
	for node in neural_network[layer]:
		output.append(neural_network[layer][node]['value'])

	return output

def randomize_neural_network(neural_network, rnd_strength):
	"""
	Randomize connection of a neural_network.

	Parameters
	----------
	neural_network: network to randomize connection (dic).
	rnd_strength: strength of the random change (float).

	Return
	------
	neural_network: randomized neural_network (dic).
	"""
	multi = [0., 1., -1.]
	for layer in neural_network:
		for node in neural_network[layer]:
			for link in neural_network[layer][node]['links']:
				neural_network[layer][node]['links'][link] += rnd_strength * multi[randint(0, len(multi) - 1)]

	return neural_network

def save_neural_network(neural_network, file_path):
	"""
	Save a neural network in a file.

	Parameters
	----------
	neural_network: neural network to save in the file (dic).
	file_path: path to save the neural network (str).
	"""
	file = open(file_path,'w')
	pickle.dump(neural_network, file_path)
	file.close()

def load_neural_network(file_path):
	"""
	Load neural network from a file.

	Parameter
	---------
	file_path: path of the file to load the neural network from (str).

	Return
	------
	neural_network: loaded neural network (dic).
	"""
	file = open(file_path,'r')
	neural_network=pickle.load(file_path)
	file.close()
	return neural_network

def sigmoid (x):
	return 1 / (1 + exp(-x))

def sigmoid_(x):
	return x * (1 - x)

# Neural network training
# ------------------------------------------------------------------------------
#

def train_neural_network(neural_network, max_iteration, learn_strength):
	"""
	Train the neural network.

	Parameters
	----------
	neural_network: neural network to train (dic).
	max_iteration: max iteration of the trainning algorithme (dic).
	learn_strenght: strenght of the learning algorithme (dic).

	Return
	------
	neural_network: trained neural network (dic).
	"""

def force_learn_neural_network(neural_network, neural_input, expected_neural_output, strenght):
	"""
	Force the neural network to learn something.

	Parameters
	----------
	neural_network: neural network to train (dic).
	neural_input: data to input in the neural network (list(float)).
	expected_neural_output: expected_neural_output from the neural network (list(float)).

	Return
	------
	neural_network: trained neural network (dic).
    """

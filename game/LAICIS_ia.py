# -*- coding: utf-8 -*-
from random import *
from pickle import *
from math import exp

# A.I.
# ------------------------------------------------------------------------------
# AI interactions

def get_ai_input(player_name, buy_ships, game_stats):
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

	if buy_ships:
		return 'f:fighter d:destroyer b:battlecruiser'

    # Todo AI logic.

def ship_to_neural_input(game_stats, player_name, ship_name):
	"""
	Convert a ship to a neural network input.

	Parameters
	----------
	game_stats: stats of the game (dic).
	player_name: name of the player (str).
	ship_name: name of the ship to convert data (str).

	Return
	------
	ship_data: ship data in neural input format (list(float))
	"""
	ship = game_stats['ships'][ship_name]
	ship_type = ship['type']
	ship_type_data = []

	if ship_type == 'destroyer':
		ship_type_data = [1.,-1., -1.]
	elif ship_type == 'fighter':
		ship_type_data = [-1.,1.,-1.]
	else:
		ship_type_data = [-1.,-1.,1.]

	# Get the heal.
	ship_heal_data = ship['heal_points'] / game_stats['model_ship'][ship_type]['max_heal']

	# Get the owner.
	ship_owner = ship['owner']
	ship_owner_data = []

	if ship_owner == 'none':
		ship_owner_data = [1.,-1., -1.]
	elif ship_owner == player_name:
		ship_owner_data = [-1.,1., -1.]
	else:
		ship_owner_data = [-1.,-1., 1.]

	ship_direction_data = list(ship['direction'])

	ship_position_data = [ship['position'][0] / game_stats['board_size'][0], ship['position'][1] / game_stats['board_size'][1], ship_heal_data]

	return [].append(ship_type_data).append(ship_owner_data).append(ship_direction_data).append(ship_position_data)


def neural_output_to_game_input(neural_ouput, ship_name, game_stats):
	"""
	Convert a neural output into a game_input.

	Parameters
	----------
	neural_ouput: output from the neural_ouput (list(float)).
	game_stats: stats of the game (dic).

	Return
	------
	game_input: input for the game (str).
	"""

# AI helper
# ------------------------------------------------------------------------------
# Because everyone isn't perfect.

def help_attack(game_stats, ship_name, original_attack):
    """
    Fix the ai attack command.

    Parameters
    ----------
    game_stats: stats of the game (dic).
    ship_name: curent ship name (str).
    orginal_attack : attack command to fix (str).

    Return
    ------
    fix_attack_command: fixed attack command (str).
    """


# Neural network
# ==============================================================================
# Wow so... so... neural !

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

def get_fitness(game_stats, player_name):
	"""
	Get the fitness of the ai.

	Parameters
	----------
	game_stats: stats of the game (dic).
	player_name: name of the player (str).

	Return
	------
	fitness: fitness of the player (float).
	"""

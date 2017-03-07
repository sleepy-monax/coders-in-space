# -*- coding: utf-8 -*-
def get_ai_input(player_name, buy_ships, game_stats):
    """
	Get input from a AI player.

	Parameter
	---------
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

def create_neural_network(neural_structure):
    """
    Create a neural network from a neural structure description.

    Parameter
    ---------
    neural_structure : neural structure description of the network (tuple(ints)).

    Return
    ------
    neural_network : neural network create from the neural structure description (dic).
    """

def compute_neural_network(neural_network, neural_input):
    """
    Compute output from a neural network with specified inputes.

    Parameters
    ----------
    neural_network : neural network to use (dic).
    neural_input : data to input in the neural network (list(float)).

    Return
    ------
    neural_ouput : output from the neural_network (list(float))
    """

def randomize_neural_network(neural_network, rnd_strength):
    """
    Randomize connection of a neural_network.

    Parameters
    ----------
    neural_network : network to randomize connection (dic).
    rnd_strength : strength of the random change (float).

    Return
    ------
    neural_network : randomized neural_network (dic).
    """

def save_neural_network(neural_network, file_path):
    """
    Save a neural network in a file.
    """

def load_neural_network(file_path):
    """
    Load neural network from a file.
    """

def traine_neural_network(neural_network, max_iteration, learn_strength):
    """
    Traine the neural network.
    """

def get_fitness(game_stats, player_name):
    """
    Get the fitness of the ai.
    """

def convert_dict_to_list(dictionnary):
    """
    Convert a dictionnary to a list.
    """

def convert_list_to_dict(list):
    """
    Convert a list in to a dictionnary.
    """
def sigmoid (x): return 1/(1 + exp(-x))
def sigmoid_(x): return x * (1 - x)

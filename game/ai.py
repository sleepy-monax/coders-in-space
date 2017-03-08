from neural import *
import os

def get_ai_input(player_name, buy_ships, game_stats):
	"""
	Get input from a AI player.

	Parameter
	---------
	player_name : name of the player (str).
	buy_ships : True, if players buy their boats (bool).
	network : think network for the AI.
	game_stats : stats of the game (dic).

	Return
	------
	ai_input : game input from AI (str).

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	Implementation : Nicolas Van Bossuyt (v1. 27/02/17)
	"""

	if buy_ships:
		return 'f:fighter d:destroyer b:battlecruiser'

	def get_ship_data(game_stats, ship, player):
		# Get the type.
		ship = game_stats['ships'][ship]
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
		elif ship_owner == player:
			ship_owner_data = [-1.,1., -1.]
		else:
			ship_owner_data = [-1.,-1., 1.]

		ship_direction_data = list(ship['direction'])

		ship_position_data = [ship['position'][0] / game_stats['board_size'][0], ship['position'][1] / game_stats['board_size'][1], ship_heal_data]

		return (ship_type_data  + ship_owner_data + ship_direction_data + ship_position_data)

	def to_input(ship_name, data_input, game_stats):
		input_id = data_input[:5]
		input_id = input_id.index(max(input_id))
		input_str = ''
		if input_id == 0:
			input_str = 'left'

		elif input_id == 1:
			input_str = 'right'

		elif input_id == 2:
			input_str = 'faster'

		elif input_id == 3:
			input_str = 'slower'

		elif input_id == 4:
			attack_range = game_stats['model_ship'][game_stats['ships'][ship_name]['type']]['range']
			attack_offset = input_data[-2:]
			input_str = '%d-%d' % (game_stats['ships'][ship_name]['position'][0] + int(attack_range * attack_offset[0]),\
								   game_stats['ships'][ship_name]['position'][1] + int(attack_range * attack_offset[1]))


		return '%s:%s' % (ship_name.replace(player_name + '_',''), input_str)


	# Load network.
	network = game_stats['network'][player_name]

	# Get model_ship data.
	# Name               / heal / Speed / Damages / range / price
	fighter_data       = [3     , 5     , 1       ,5      , 10]
	destroyer_data     = [8     , 2     , 2       ,7      , 20]
	battlecruiser_data = [20    , 1     , 4       ,10     , 30]

	chip_data = fighter_data + destroyer_data + battlecruiser_data

	# Create a copy of the neural network and run it!
	current_network = network.copy()
	orders = ''
	for player_ship in game_stats['ships']:
		if game_stats['ships'][player_ship]['owner'] == player_name:

			memory = [0, 0] * 8
			output_data = []

			for other_ship in game_stats['ships']:
				if game_stats['ships'][other_ship]['owner'] != player_name:
					input_data = chip_data + get_ship_data(game_stats, player_ship, player_name) + get_ship_data(game_stats, other_ship, player_name) + memory
					output_data = convert_dictionnary(run_network(current_network, input_data))
					memory = output_data[-len(memory):]

			order_data = output_data[:7]
			orders += to_input(player_ship, order_data, game_stats) + ' '

	return orders[:-1]

def convert_dictionnary(dico):
	dic_list = []
	for key in dico:
		dic_list.append(dico[key])

	return dic_list

from neural import *

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
    Implementation : Nicolas Van Bossuyt (v1. 27/02/17)
	"""

	if buy_ships:
		return 'f:fighter d:destroyer b:battlecruiser'

    def get_ship_data(game_stats, ship, player):
        # Get the type.
        ship_type = ship['type']
        ship_type_data = ()

        if ship_type == 'destroyer':
            ship_type_data = (1.,-1., -1.)
        elif ship_type == 'fighter':
            ship_type_data = (-1.,1.,-1.)
        else:
            ship_type_data = (-1.,-1.,1.)

        # Get the heal.
        ship_heal_data = ship['heal'] / game_stats['model_ship'][ship_type]['max_heal']

        # Get the owner.
        ship_owner = ship['owner']
        ship_owner_data = ()

        if ship_owner == 'none':
            ship_owner_data = (1.,-1., -1.)
        elif ship_owner == player:
            ship_owner_data = (-1.,1., -1.)
        else:
            ship_owner_data = (-1.,-1., 1.)

        ship_direction_data = ship['direction']

        ship_position_data = (ship['postion'][0] / game_stats['board_size'][0], ship['postion'][1] / game_stats['board_size'][1])

        return ship_type_data + ship_heal_data + ship_owner_data + ship_direction_data + ship_position_data


    # Name               / heal / Speed / Damages / range / price
    fighter_data       = (3     , 5     , 1       ,5      , 10)
    destroyer_data     = (8     , 2     , 2       ,7      , 20)
    battlecruiser_data = (20    , 1     , 4       ,10     , 30)

    chip_data = fighter_data + destroyer_data + battlecruiser_data

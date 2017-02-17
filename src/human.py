from gui import *

def get_human_input(player_name, buy_ship, game_stats):
    """
    Get input from a human player.

    Parameters
    ----------
    player_name : Name of the player to get input from (str).
    buy_ship : the player need to buy a ship (str).
    game_stats : stats of the game (dic).

    Returns
    -------
    player_input : input from the player (str).
    """

    # Show header.
    c = create_canvas(190, 1)
    put_box(c, 0, 0, 190, 3, 'single')
    put_string(c, 3, 0, '| It\'s %s\'s turn |' % player_name)
    print_canvas(c)

    while True:
        player_input = raw_input(player_name + ':~$')
        if '/' in player_input:
            c = create_canvas(190, 50)
            put_box(c, 0, 0, 190, 3)
            if player_input == '/help-ship-creation':
                show_help_ship_creation(c)
                print_canvas(c)
            elif player_input == '/help-game-command':
                show_help_game_command(c)
                print_canvas(c)
            elif player_input == '/show-ships-list':
                show_ships_list(c, player_name, game_stats)
                print_canvas(c)
            elif player_input == '/show-game-board':
                show_board(game_stats)
            else:
                print 'Wrong input'
        else:
            return player_input

def show_help_ship_creation(c):
    put_string(c, 3, 0, '| HELP : ship creation |' % player_name)
    put_string(c, 3, 3, 'Ship type')
    put_string(c, 1, 4, '-'*188)

def show_help_game_command(c):
    put_string(c, 3, 0, '| HELP : game command |' % player_name)

def show_ships_list(c, player_name, game_stats):
    put_string(c, 3, 0, '| Your spaceships |' % player_name)

def show_board(game_stats, color = True):
	"""
	Show the game to the user screen.

	Parameter
	---------
	game_stats : game to show on screen (dic).

	Version
	-------
	Version
	-------
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
	implementation : Nicolas Van Bossuyt (v1. 15/02/2017)

	"""

	# Create a new canvas.
	c = create_canvas(190, 50, color)
	put_ascii_art(c, c['size'][0] - 65, game_stats['board_size'][1] - 25, 'alien')

	# Create the board frame.
	on_screen_board_size = (game_stats['board_size'][0]*3 + 5, game_stats['board_size'][1] + 3)
	put_box(c, 0, 0, on_screen_board_size[0], on_screen_board_size[1])
	put_string(c, 2, 0, u'| Code in space : %s |' % (game_stats['level_name']))

	# Put horizontal coordinate.
	coordinate_string = ''
	for i in range(1, game_stats['board_size'][0] + 1):
		value_string = str(i)
		if len(value_string) == 1:
			value_string = ' ' + value_string
		value_string += ' '
		coordinate_string += value_string

	put_string(c, 4, 1, coordinate_string, 1, 0, 'blue', 'white')

	# Put vertical coordinate.
	for i in range(1, game_stats['board_size'][1] +1):
		value_string = str(i)
		if len(value_string) == 1:
			value_string = ' ' + value_string
		put_string(c,1,i + 1,value_string + ' ', 1,0, 'blue', 'white')

	# Put game board.
	for x in range(game_stats['board_size'][0]):
		for y in range(game_stats['board_size'][1]):
			on_screen_board_tile = (x*3 + 4, y + 2)

			# Check how many ship there are in the board tile.
			if len(game_stats['board'][(x,y)]) == 0:
				# When there are only one, show juste nothing.
				put_string(c, on_screen_board_tile[0], on_screen_board_tile[1], ' .')

			elif len(game_stats['board'][(x,y)]) == 1:
				# When there are one, show somme information about.
				ship_name = game_stats['board'][(x,y)][0]
				ship_type = game_stats['ships'][ship_name]['type']
				ship_icon = game_stats['model_ship'][ship_type]['icon']
				ship_owner = game_stats['ships'][ship_name]['owner']

				if ship_owner == 'none':
					# The ship is a abandoned one.
					put_string(c, on_screen_board_tile[0] + 1, on_screen_board_tile[1], ship_icon,1,0,'white', 'green')
				else:
					# The ship have a owner.
					ship_owner_color = game_stats['player'][['ships'][ship_name]['owner']]['color']
					put_string(c, on_screen_board_tile[0] + 1, on_screen_board_tile[1], ship_icon,1,0,'white', ship_owner_color)

			else:
				# in other case show how many ship there are in the tile.
				put_string(c, on_screen_board_tile[0], on_screen_board_tile[1], '!' + str(len(game_stats['board'][(x,y)])),1,0,'white', 'green')

	# Put players liste frame.
	on_screen_player_board_size = (len(game_stats['players']) * 30 + 2, c['size'][1] - on_screen_board_size[1])
	put_box(c, 0, on_screen_board_size[1], on_screen_player_board_size[0], on_screen_player_board_size[1])
	put_string(c, 1, on_screen_board_size[1], u'| Players |')

    # Put players liste.
	player_count = 0
	for player in game_stats['players']:
		location = ((player_count * 30) + 1, on_screen_board_size[1] + 1,)
		put_box(c, location[0], location[1], 30, 5, 'single')

		# Put player informations.
		put_string(c, location[0] + 2, location[1] , '| ' + game_stats['players'][player]['name'] + ' |')
		put_string(c, location[0] + 2, location[1] + 1, 'Type : ' + game_stats['players'][player]['type'])
		put_string(c, location[0] + 2, location[1] + 2, 'Money : ' + str(game_stats['players'][player]['money']) + '$')
		put_string(c, location[0] + 2, location[1] + 3, 'Spaceship count : ' + str(game_stats['players'][player]['nb_ships']))

		player_count += 1
	# Show the game board in the terminal.
	print_canvas(c)

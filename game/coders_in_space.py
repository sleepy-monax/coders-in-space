# -*- coding: utf-8 -*-

# Alien
# ==============================================================================
# A cool friend to get in touch wile coding.

"""
						 ___---------___
					   _".^ .^ ^.  '..:"-_
					 /:			. .^:.  :\
				   /: .   .	.		. . .:\
				  /:			   .  ^ .  . .:\
				 /.						.  .:\
				|:					.  .  ^. .:|
				||		.				. . !:|
				\(							.:)/
				|. ######			  .#######::|
				 |.#######		   ..########:|
				 \ ########		   :########:/
				  \ ########	   . ########.:/
				   \. #######	   #######..:/
					 \		   .   .   ..:/
					  \.	   | |	 . .:/
						\			 ..:/
						 \.		   .:/
						   \   ___/  :/
							\	   :/
							 |\  .:/|
							 |  --.:|
							 "(  ..)"
							/  .  .::\
"""

# Imports
# ==============================================================================
# Import some cool component for the game.


from math import *
from time import sleep  # because everyone needs to rest.
from graphics import *
from remote_play import notify_remote_orders, get_remote_orders, connect_to_player, disconnect_from_player
import os
import sys
import random


# Game
# ==============================================================================
# Create a new game and play it.

# Constant for match template.
human_vs_ai = ('human', 'ai')
human_vs_human = ('human', 'human')
human_vs_remote = ('human', 'remote')
ai_vs_ai = ('ai', 'ai')
ai_vs_human = ('ai', 'human')
ai_vs_remote = ('ai', 'remote')
remote_vs_ai = ('remote', 'ai')
remote_vs_human = ('remote', 'human')

def play_game(level_name, players_names, players_types, no_splash=False, no_gui=False, remote_id=None, remote_ip=None, max_rounds_count=10):
    """
	Main function that executes the game loop.

	Parameters
	----------
	level_name:    name of game level (str).
	players_names: names of players (list(string)).
	players_types: types of players (list(string)).
	
	(optional) no_splash: ship the splash screen (bool).
	(optional) no_gui:    disable game user interface (bool).
	(optional) remote_id: ID of the remote player (int).
	(optional) remote_ip: IP of the remote player (str).
	(optional) max_rounds_count: number of rounds (int).

	Return
	------
	game_data: game data at the end of the game (str).

    Version
    -------
    Specification:  Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
					Nicolas Van Bossuyt (v2. 25/04/2017)
    Implementation: Bayron Mahy, Nicolas Van Bossuyt (v1. 15/02/17)
					Nicolas Van Bossuyt (v2. 25/04/2017)
    """

    # Create the new game.
    is_remote_game = (remote_id != None and remote_ip != None)

    # Show the splash screen.
    if not no_splash:
        show_splash_game(is_remote_game)

    # Connected to the remote player.
    if is_remote_game:
        print "CodersInSpace - Online multiplayer"
        game_data = initialize_game(level_name, players_names, players_types, max_rounds_count, connect_to_player(remote_id, remote_ip, True))
    else:
        game_data = initialize_game(level_name, players_names, players_types, max_rounds_count)

    # Setup game loop.
    is_ship_buy = True
    game_running = True
    total_turn = -1

	# The mian game loop.
    while game_running:
        if total_turn > -1:
            write_log(game_data, u'It\'s turn nb %d' % (total_turn), 0)

        # Show the game board to the human player.
        if not no_gui:
            show_game_board(game_data)

        # Cleaning the pending_attack list.
        game_data['pending_attacks'] = []
        pending_command = []

        # getting players input.
        for player in players_names:
            if is_ship_buy or game_data['players'][player]['nb_ships'] > 0:
                pending_command.append((player, get_game_input(player, is_ship_buy, game_data)))
            else:
                write_log(game_data, player + ' has lost all these ships, so he has nothing to do.', 1)

        # Executing pending commands.
        for command in pending_command:
            if is_ship_buy:
                game_data = command_buy_ships(command[1], command[0], game_data)
            else:
                game_data = parse_command(command[1], command[0], game_data)

        is_ship_buy = False

        # Show the game board to the human player.
        if not no_gui:
            show_game_board(game_data)

        # Do game loop.
        game_data = do_moves(game_data)
        game_data = take_abandonned_ship(game_data)
        game_data = do_attack(game_data)

        # Increment the turn counter.
        game_data['nb_rounds'] += 1
        total_turn += 1
        game_running = is_game_continue(game_data)

    # Disconnect the remote player.
    if is_remote_game:
        disconnect_from_player(game_data['players']['remote']['connection'])

    # Show the end game screen.
    if not no_splash:
        show_end_game(game_data)
        raw_input()

    return game_data


def initialize_game(level_name, players_names, players_types, max_rounds_count, connection=None):
    """
	Create a new game from a '.cis' file.

	Parameters
	----------
	level_name: name of game level (str).
	players_names: names of players (list(string)).
	players_types: types of players (list(string)).
	max_rounds_count: maximum round count (int).
	(optional) connection: connection to the remote player.

	Return
	-------
	game_data: new game stats (dic).

	Version
	-------
	Specification:  Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
					Nicolas Van Bossuyt (v2 25/04/2017).
					
	Implementation: Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
					Bayron Mahy, Nicolas Van Bossuyt (v2. 13/02/17)
					Nicolas Van Bossuyt (v3. 23/02/17)
					Nicolas Van Bossuyt (v4. 25/04/17)
	"""
    # Create the log file.
    open('log.txt', 'w').close()

    # Create random a random game board.
    if level_name == 'random':
        create_game_board('board/random.cis', (30, 30), 26)
        level_name = 'board/random.cis'

    # Create game_data dictionary.
    game_file = parse_game_file(level_name)
    game_data = {'board': {},
                 'players': {},
                 'model_ship': {},
                 'ships': {},
                 'board_size': game_file['size'],
                 'level_name': level_name,
                 'nb_rounds': -1,
                 'pending_attacks': [],
                 'game_logs': [],
                 'winners': [],
                 'is_remote_game': connection is not None,
                 'max_nb_rounds': max_rounds_count - 1}

    # Create ship specs sheet.
    game_data['model_ship']['fighter'] =       {'icon': u'F', 'max_heal': 3, 'max_speed': 5, 'damages': 1, 'range': 5, 'price': 10}
    game_data['model_ship']['destroyer'] =     {'icon': u'D', 'max_heal': 8, 'max_speed': 2, 'damages': 2, 'range': 7, 'price': 20}
    game_data['model_ship']['battlecruiser'] = {'icon': u'B', 'max_heal': 20, 'max_speed': 1, 'damages': 4, 'range': 10, 'price': 30}

    # Create the game board.
    for line in range(game_file['size'][0]):
        for column in range(game_data['board_size'][1]):
            game_data['board'][(line, column)] = []

    # Place lost ships.
    for ships in game_file['ships']:
        game_data['ships'][ships[2]] = {'type': ships[3], 'heal_points': game_data['model_ship'][ships[3]]['max_heal'],
                                        'facing': ships[4], 'speed': 0, 'owner': 'none',
                                        'location': (ships[0], ships[1]), 'objective': 'none', 'objective_path': []}
        game_data['board'][(ships[0], ships[1])].append(ships[2])

    index_player = 0

    for player in players_names:
        # Create new player.
        if index_player < 4:
            game_data['players'][player] = {'name': player, 'money': 100, 'nb_ships': 0}

            # Set the player type.
            game_data['players'][player]['type'] = players_types[index_player]

            # Set player starting pos.
            if index_player == 0:
                game_data['players'][player]['ships_starting_point'] = (9, 9)
                game_data['players'][player]['ships_starting_facing'] = (1, 1)
                game_data['players'][player]['color'] = 'red'

            elif index_player == 1:
                game_data['players'][player]['ships_starting_point'] = (game_data['board_size'][0] - 10, game_data['board_size'][1] - 10)
                game_data['players'][player]['ships_starting_facing'] = (-1, -1)
                game_data['players'][player]['color'] = 'blue'

            elif index_player == 2:
                game_data['players'][player]['ships_starting_point'] = (game_data['board_size'][0] - 10, 9)
                game_data['players'][player]['ships_starting_facing'] = (-1, 1)
                game_data['players'][player]['color'] = 'yellow'

            elif index_player == 3:
                game_data['players'][player]['ships_starting_point'] = (9, game_data['board_size'][1] - 10)
                game_data['players'][player]['ships_starting_facing'] = (1, -1)
                game_data['players'][player]['color'] = 'magenta'

        else:
            write_log(game_data, 'There is too many player, %s is a loser he must be watch you playing' % (player), 1)

        index_player += 1

    if connection is not None:
        game_data['players']['remote']['connection'] = connection

    return game_data


def show_splash_game(is_remote_game=False):
    """
	Show the splash screen.

	Parameter
	---------
	game_data: data of the game (dic).

	Version
	-------
	Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	Implementation: Nicolas Van Bossuyt (v1. 27/02/17)
	"""

    def clear_canvas(canvas, padding=0):
        """
        clear the canvas.

        Parameter
        ---------
        canvas: canva to clear (dic).

        return
        ------
        canvas: canva after cleaning (dic).

        Version
        -------
        Specification: Bayron Mahy (v1. 11/02/17)
        Implementation: Nicolas Van Bossuyt (v1. 27/02/17)
        """

        canvas = put_box(canvas, padding, 0, screen_size[0] - padding, screen_size[1])
        canvas = put_stars_field(canvas, 1 + padding, 1, screen_size[0] - 2 - padding, screen_size[1] - 2, 0)

        return canvas

    # Setup main canvas.
    rows, columns = get_terminal_size()
    screen_size = (int(rows), int(columns))
    c = create_canvas(screen_size[0], screen_size[1])

    # print the alien.
    c = clear_canvas(c)
    c = put_ascii_art(c, screen_size[0] / 2 - 17, screen_size[1] / 2 - 12, 'alien', 'green')
    print_canvas(c)
    sleep(1)

    # Print Groupe 24 logo.
    c = clear_canvas(c)
    c = put_ascii_art(c, screen_size[0] / 2 - 53, screen_size[1] / 2 - 5, 'groupe24')
    print_canvas(c)
    sleep(1)

    # Print coders in space logo.
    padding = 0

    if is_remote_game:
        padding = 61

    c = create_canvas(screen_size[0], screen_size[1])
    c = clear_canvas(c, padding)

    game_title = 'Coders In Space'
    game_copyright = '(c) 2017 - 3342 Groupe24 corp.'
    font_standard = load_ascii_font('font_standard.txt')
    text_width = mesure_ascii_text(font_standard, game_title)
    text_location = ((screen_size[0] - padding) / 2 - text_width / 2 + padding, screen_size[1] / 2 - 5)

    c = put_ascii_text(c, font_standard, game_title, text_location[0], text_location[1], 'yellow')
    c = put_text(c, text_location[0], text_location[1] + 7, '-' * text_width)
    c = put_text(c, text_location[0] + text_width - len(game_copyright), text_location[1] + 9, game_copyright,
                 color='yellow')

    print_canvas(c)


def show_end_game(game_data):
    """
    Show the end game screen.

    Parameter
    ---------
    game_data: data of the game (dic).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    implementation: Nicolas Van Bossuyt (v1. 27/02/17)
    """
    
    # Setup main canvas.
    rows, columns = get_terminal_size()
    screen_size = (int(rows), int(columns))

    # Load ascii fonts.
    font_small = load_ascii_font('font_small.txt')
    font_standard = load_ascii_font('font_standard.txt')

    # Create the ascii canvas.
    c = create_canvas(screen_size[0], screen_size[1])
    c = put_box(c, 0, 0, screen_size[0], screen_size[1])
    c = put_stars_field(c, 1, 1, screen_size[0] - 2, screen_size[1] - 2)

    line_index = 0

    # Text property.
    text_lenght = 0
    text_location = (0, 0)
    text_font = font_small
    text_color = 'white'

    # Put players stats.
    for player in game_data['players']:
        if player != 'none':
            if player in game_data['winners']:
                # The player win the game.
                text_lenght = mesure_ascii_text(font_standard, player)
                text_font = font_standard
                text_color = game_data['players'][player]['color']

            else:
                # The player lost the game.
                text_lenght = mesure_ascii_text(font_small, player)
                text_location = (95 - int(text_lenght / 2), line_index * 11 + 2)
                text_font = font_small
                text_color = 'white'

            text_location = (screen_size[0] / 2 - int(text_lenght / 2), line_index * 11 + 2)

            # Put player informations.
            c = put_ascii_text(c, text_font, player, text_location[0], text_location[1], text_color)
            c = put_text(c, text_location[0], text_location[1] + 6, '_' * text_lenght)
            c = put_text(c, text_location[0], text_location[1] + 8,
                         "%d spaceships" % (game_data['players'][player]['nb_ships']))
            c = put_text(c, text_location[0], text_location[1] + 9, "%d G$" % (calculate_value(player, game_data)))

            line_index += 1

    # Print the canvas in the terminal.
    print_canvas(c)


def is_game_continue(game_data):
    """
	Check if the game continue.

	Parameter
	---------
	game_data: data of the game (dic).

	Return
	------
	False if the game is over. (Bool))

	Version
	-------
	Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 24/02/17)
	Implementation: Alisson Leist (v1. 24/02/17)
	"""

    not_loser = []

    # Checking playert thats have more than on ships
    for player in game_data['players']:
        if player != 'none' and game_data['players'][player]['nb_ships'] > 0:
            not_loser.append(player)

    # Check if the game continue.
    if len(not_loser) > 1 and game_data['nb_rounds'] <= game_data['max_nb_rounds']:
        return True

    winners = {}
    for player in not_loser:
        winners[player] = calculate_value(player, game_data)

    max_value = 0
    max_value_owners = []

    for player in winners:
        if winners[player] > max_value:

            max_value = winners[player]
            max_value_owners = []
            max_value_owners.append(player)

        elif winners[player] == max_value:
            max_value_owners.append(player)

    game_data['winners'] = max_value_owners

    return False


def calculate_value(player_name, game_data):
    """
	Calculate the total ship value of a player.

	Parameters
	----------
	player_name: name of the player to count value (str)
	game_data: game before command execution (dic)

	Version
	-------
	Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 24/02/17)
	Implementation: Alisson Leist (v1. 24/02/17)
	"""
    total_value = 0

    for ship in game_data['ships']:
        if game_data['ships'][ship]['owner'] == player_name:
            total_value += game_data['model_ship'][game_data['ships'][ship]['type']]['price']

    return total_value


# Input
# ==============================================================================
# Get input from each player.


def get_game_input(player_name, buy_ships, game_data):
    """
	Get input from a specified player.

	Parameters
	----------
	player_name: name of the player to get input (str).
	buy_ships: True, if players buy their boats (bool).
	game_data: data of the game (dic).

	Version
	-------
	Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	Implementation: Niolas Van Bossuyt (V1. 15/02/17)
	"""
    player_input = ''
    player_type = game_data['players'][player_name]['type']

    if player_type == 'human':
        # get input from the human player.
        player_input = get_human_input(player_name, buy_ships, game_data)

    elif player_type == 'ai':
        # Get input from the dumb ai.
        if buy_ships:
            player_input = get_ai_spaceships(player_name, game_data)
        else:
            player_input = get_ai_input(game_data, player_name)

    elif player_type == 'remote':
        # Get input from the remote player.
        player_input = get_remote_input(game_data)

    # Send the order to the remote player.
    if game_data['is_remote_game'] and (player_type == 'human' or player_type == 'ai' or player_type == 'ai_dumb'):
        notify_remote_orders(game_data['players']['remote']['connection'], player_input)

    write_log(game_data, '[%s] %s' % (player_name, player_input), 3)

    return player_input


# Player
# ------------------------------------------------------------------------------
# Human player interaction with the game.


def get_human_input(player_name, buy_ship, game_data):
    """
	Get input from a human player.

	Parameters
	----------
	player_name: Name of the player to get input from (str).
	buy_ships: True, if players buy their boats (bool).
	game_data: data of the game (dic).

	Returns
	-------
	player_input: input from Human (str).

	Version
	-------
	Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	Implementation: Nicolas Van Bosuyt (v1. 22/02/17)
	"""
    while True:
        # Setup main canvas.
        screen_size = get_terminal_size()

        # Show the game board to the human player.
        show_game_board(game_data)
        # Getting human player input.
        c = create_canvas(screen_size[0], 5)
        c = put_box(c, 0, 0, screen_size[0], 5, 'single')
        c = put_text(c, 1, 0, '| PLAYER INPUT |')
        print_canvas(c, screen_size[1] - 4, 0)

        player_input = raw_input(set_color('\033[%d;%dH %s>' % (screen_size[1] - 2, 3, player_name),
                                           game_data['players'][player_name]['color'], 'white'))

        # Run human player command.
        if '/' in player_input:

            if player_input == '/ship-list':
                show_ship_list(player_name, game_data)
        else:
            return player_input


def show_ship_list(player_name, game_data):
    """
	(use for debug) Show spaceships information on the terminal.

	Parameters
	----------
	player_name: name of the player to show the information (str).
	game_data: data of the game (dic).

	Version
	-------
	Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	Implementation: Nicolas Van Bossuyt (v1. 22/02/17)
	"""

    # Setup main canvas.
    screen_size = get_terminal_size()

    c_ship_list = create_canvas(106, 10 + len(game_data['ships']) + len(game_data['players']) * 4)
    put_box(c_ship_list, 0, 0, c_ship_list['size'][0], c_ship_list['size'][1], 'double')
    put_text(c_ship_list, 3, 0, '[ Spaceships ]')
    line_index = 0

    # Show ships models.
    c_ship_list = put_text(c_ship_list, 3, 2, '// Spaceships Models //')
    c_ship_list = put_text(c_ship_list, 1, 3, '-' * 104)

    for ship_model_name in game_data['model_ship']:
        ship_model = game_data['model_ship'][ship_model_name]
        c_ship_list = put_text(c_ship_list, 3, 4 + line_index,
                               '[%s] %s // heal: %spv ~ speed: %skm/s ~ damages: %spv ~ attack range: %skm ~ price: %sG$ ' % (
                                   ship_model['icon'], ship_model_name, ship_model['max_heal'], ship_model['max_speed'],
                                   ship_model['damages'], ship_model['range'], ship_model['price']))
        line_index += 1

    c_ship_list = put_text(c_ship_list, 1, 4 + line_index, '-' * 104)

    for player in game_data['players']:
        # Show Players's ships.

        line_index += 4

        if player == 'none':
            c_ship_list = put_text(c_ship_list, 3, 2 + line_index, '// Abandonned spaceships //')
        else:
            c_ship_list = put_text(c_ship_list, 3, 2 + line_index, '// %s\'s spaceships //' % (player),
                                   color=game_data['players'][player]['color'])

        c_ship_list = put_text(c_ship_list, 1, 3 + line_index, '-' * 104)

        if game_data['players'][player]['nb_ships'] > 0:
            for ship_name in game_data['ships']:
                ship = game_data['ships'][ship_name]
                if ship['owner'] == player:
                    c_ship_list = put_text(c_ship_list, 3, 4 + line_index,
                                           '[%s] %s // heal: %spv ~ speed: %skm/s ~ Facing: %s ~ NextPos: %s' % (
                                               game_data['model_ship'][ship['type']]['icon'], ship_name,
                                               ship['heal_points'], ship['speed'], str(ship['facing']),
                                               str(predict_next_pos(game_data, ship_name))))
                    line_index += 1
        else:
            c_ship_list = put_text(c_ship_list, 3, 4 + line_index, 'Sorry no space ships:/')
            line_index += 1

        c_ship_list = put_text(c_ship_list, 1, 4 + line_index, '-' * 104)

    is_scroll_continue = True
    scroll = 0

    while is_scroll_continue:
        c_window = create_canvas(screen_size[0], screen_size[1])
        c_window = put_box(c_window, 0, 0, screen_size[0], screen_size[1])

        c_window = put_canvas(c_window, c_ship_list, 1, 1 + scroll)
        print_canvas(c_window)

        is_scroll_continue = (c_ship_list['size'][1] - screen_size[1]) > abs(scroll)

        if is_scroll_continue:
            raw_input('\033[%d;%dHPress enter to scroll...' % (screen_size[1], 1))
        else:
            raw_input('\033[%d;%dHPress enter to exit...' % (screen_size[1], 3))
        scroll -= 10


def show_game_board(game_data):
    """
	Show game board on the teminal.

	Parameter
	---------
	game_data: data of the game (dic).

	Version
	-------
	Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17).
				   Nicolas Van Bossuyt (v2. 19/03/17).

	Implementation: Nicolas Van Bossuyt (v4. 10/02/17).
	"""

    # Setup main canvas.
    screen_size = get_terminal_size()
    c = create_canvas(*screen_size)

    # Render child canvas.
    c_game_board = render_game_board(game_data) # The game board.
    c_ship_list = render_ship_list(game_data, 30, screen_size[1] - 2) # The list 
    c_game_logs = render_game_logs(game_data, c_game_board['size'][0], 10)

    # Put somme nice decoration.
    c = put_ascii_art(c, 1, screen_size[1] - 25, 'planet')
    if (screen_size > 190):
        c_screen = put_ascii_art(c, 185, screen_size[1] - 25, 'planet')
    c = put_box(c, 0, 0, screen_size[0], screen_size[1], 'single')

    # Put child canvas in the main canvas.
    game_board_pos = (screen_size[0] / 2 - (c_game_board['size'][0] + 2) / 2,
                      screen_size[1] / 2 - (c_game_board['size'][1] + 2) / 2 - (c_game_logs['size'][1] + 2) / 2)

    c = put_window(c, c_game_board, 'GAME BOARD', game_board_pos[0], game_board_pos[1], c_game_board['size'][0] + 2,
                   c_game_board['size'][1] + 2)
    c = put_window(c, c_game_logs, 'GAME LOGS', game_board_pos[0], game_board_pos[1] + c_game_board['size'][1] + 2,
                   c_game_logs['size'][0] + 2, c_game_logs['size'][1] + 2)

    if game_board_pos[0] - (c_ship_list['size'][0] + 2) > 0:
        c = put_window(c, c_ship_list, 'SHIP LIST', 0, 0, c_ship_list['size'][0] + 2, c_ship_list['size'][1] + 2)

    print_canvas(c)


def render_game_board(game_data):
    """
	Render the game board.

	Parameter
	---------
	game_data: data of the game (dic).

	Return
	------
	game_board_canvas: rendered game board (dic)
	"""
    # Setup the drawing canvas.
    board_size = game_data['board_size']
    c = create_canvas(board_size[0] * 3 + 3, board_size[1] + 1)
    c = put_stars_field(c, 0, 0, *c['size'])
    offset = 0

    # Put coordinates.
    for i in range(max(board_size)):
        val_str = str(i + 1)
        val_str = ' ' * (3 - len(val_str)) + val_str

        # Horizontal
        c = put_text(c, 3 + offset * 3, 0, val_str, 1, 0, 'grey', 'white')

        # Vertical
        c = put_text(c, 0, 1 + offset, val_str, 1, 0, 'grey', 'white')
        offset += 1

    # Put Spaceships on the game board.
    for location in game_data['board']:
        # Get ships on given location and the location on the screen.
        ships_at_location = game_data['board'][location]
        on_canvas_location = (3 + location[0] * 3, location[1] + 1)
        
        # There are only on ship on the location.
        if len(ships_at_location) == 1:
        
            # Get all ships informations.
            ship_name = ships_at_location[0]
            ship = game_data['ships'][ship_name]
            ship_owner = ship['owner']
            ship_icon = ship_name.replace('%s_' % ship_owner, '').upper()[0]
            ship_color = 'white'
            ship_facing = ship['facing']

            # Set the color to white if the ship dosen't have any owner.
            if ship_owner != 'none':
                ship_color = game_data['players'][ship_owner]['color']

            # Put facing line.
            facing_char = '|' # The ship is facing 'up' or 'down'.

            if ship_facing == (1, 1) or ship_facing == (-1, -1):
                facing_char = '\\' # The ship is facing 'up-left' or 'down-right'.
            elif ship_facing == (1, -1) or ship_facing == (-1, 1):
                facing_char = '/' # The ship is facing 'up-right' or 'down-left'.
            elif ship_facing == (1, 0) or ship_facing == (-1, 0):
                facing_char = u'─' # The ship is facing 'left' or 'right'.

            # Put the ship and the direction line on the game board.
            put_text(c, on_canvas_location[0] + 1, on_canvas_location[1], ship_icon, 1, 0, ship_color, None)
            put_text(c, on_canvas_location[0] + 1 + ship_facing[0], on_canvas_location[1] + ship_facing[1],
                     facing_char, 1, 0, ship_color, None)

        # There are more than one ship on the location, show how many there are.
        elif len(ships_at_location) > 1:
            put_text(c, on_canvas_location[0], on_canvas_location[1], '[%d]' % len(ships_at_location), 1, 0, 'green', None)

    # Show attack location on the game board.
    for location in game_data['pending_attacks']:
        location = location[2]
        on_canvas_location = (3 + location[0] * 3, location[1] + 1)
        put_text(c, on_canvas_location[0], on_canvas_location[1], '[', 1, 0, 'white', 'red')
        put_text(c, on_canvas_location[0] + 2, on_canvas_location[1], ']', 1, 0, 'white', 'red')

    return c


def render_ship_list(game_data, width, height):
    """
	Render the ship_list.

	Parameter
	---------
	game_data: data of the game (dic).

	Return
	------
	ship_list_canvas: rendered ship list (dic).
	"""
    # Setup the drawing canvas.
    c = create_canvas(width, height)
    ship_count = len(game_data['ships'])
    ship_index = 0

    # Put list header.
    put_text(c, 0, 0, ' T | X   Y | Name' + ' ' * 25, 1, 0, 'grey', 'white')
    for player in game_data['players']:
        ship_index += 1
        y = ship_index + 1
        
        # Put all information about the players.
        put_text(c, 1, y, '%s (t:%s s:%d)' % (
            player, game_data['players'][player]['type'], game_data['players'][player]['nb_ships']))
        put_text(c, 0, y + 1, '-' * width)
        ship_index += 2
        
        # get all space ship of a player.
        for ship in game_data['ships']:
            if game_data['ships'][ship]['owner'] == player:
                y = ship_index + 1
                
                # Put information about the selected spaceship.
                
                # Ship type.
                put_text(c, 1, y, game_data['ships'][ship]['type'].upper()[0])

                # Ship coordinates
                put_text(c, 4, y, str(game_data['ships'][ship]['location']))

                # Ship name.
                put_text(c, 14, y, ship[len(player + '_'):], 1, 0,
                         game_data['players'][game_data['ships'][ship]['owner']]['color'])

                ship_index += 1

    return c


def render_game_logs(game_data, width, height):
    """
	Render the game logs.
	
	Parameter
	---------
	game_data: data of the game (dic).

	Return
	------
	game_logs_canvas: rendered game logs (dic).
	"""
    # Setup the canvas.
    c = create_canvas(width, height)
    y = 0

    message_color = ['blue', 'yellow', 'red', None]
    message_prefix = ['  I ', ' /!\\', ' !!!', '  > ']

    # Put all message in the logs screen.
    for message in game_data['game_logs'][-height:]:
        c = put_text(c, 5, y, message[1], 1, 0)
        c = put_text(c, 0, y, message_prefix[message[0]], 1, 0, message_color[message[0]])
        y += 1

    return c


# Remote player
# ------------------------------------------------------------------------------
# Handeling remote player command.


def get_remote_input(game_data):
    """
	Get input from a remote player.

	Parameter
	---------
	game_data: data of the game (dic).

	Return
	------
	remote_input: input from remote player (str).

	Version
	-------
	Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
					 Nicolas Van Bossuyt (v2. 03/03/17)
	Implementation: Nicolas Van Bossuyt (v1. 03/03/17)
	"""

    return get_remote_orders(game_data['players']['remote']['connection'])


# A.I.C.I.S
# ------------------------------------------------------------------------------
# [A]rtificial [I]nteligence for [C]oders [I]n [S]pace.


def get_ai_input(game_data, player_name):
    """
	Get input from an AI player.
	Parameter
	---------
	player_name: name of the player (str).
	game_data:   state of the game (dic).
	Return
	------
	ai_input: game input from AI (str).
	Version
	-------
	Specification:  Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	Implementation: Nicolas Van Bossuyt (v1. 16/03/17)
                    Nicolas Van Bossuyt (v2. 26/04/17)
	"""
    action = ['faster', 'slower', 'left', 'right', 'attack']

    ai_input = ''

    for ship_name in game_data['ships']:
        ship = game_data['ships'][ship_name]
        if ship['owner'] == player_name:
            if ship['objective'] == 'none' or len(ship['objective_path']) == 0:
                sucess = False
                while not sucess:
                    # Try again !
                    ship['objective'] = random.choice(get_ships(game_data, player_name))
                    start_node = node(ship['location'], ship['facing'])
                    end_node = node(game_data['ships'][ship['objective']]['location'])
                
                    sucess, ship['objective_path'] =  path_finding(start_node, game_data['model_ship'][ship['type']]['max_speed'], end_node, game_data['board_size'])
            ship_action = ''
        

            to_do_node = ship['objective_path'].pop()
            
            if to_do_node['to_do'] == 'none': # Nothing to do => Attack somebody.
                ship_action = attack(game_data, ship_name)
            else: # Do the "to do" node.
                ship_action = to_do_node['to_do']
            
            if ship['objective'] in game_data['ships']:
                objective_ship = game_data['ships'][ship['objective']]
                
                if get_distance(ship['location'], objective_ship['location'], game_data['board_size']) <= game_data['model_ship'][ship['type']]['range']:
                    # The objective ship is in the attack range.
                    if not (objective_ship['owner'] == 'None' or objective_ship['owner'] == player_name):
                        # The ship is friendly => don't attack.
                        
                        ship_action = attack(game_data, ship_name)
                        ship['objective'] = 'none'
                        
                ai_input += '%s:%s ' % (ship_name[len(player_name) + 1:], ship_action)
            else:
                ship['objective'] = 'none'

    return ai_input[:-1]
    
def filter_ships(ships, exclude_owner):
    fonded_ships = []
    for ship in game_data['ships']:
        if game_data['ships'][ship]['owner'] != exclude_owner:
            fonded_ships.append(ship)
            
    return fonded_ships
 
def get_ship_owner(ships, owner):
    fonded_ships = []
    for ship in ships:
        if ships[ship]['owner'] == owner:
            fonded_ships.append(ship)
            
    return fonded_ships

def get_ai_spaceships(player_name, game_data):
    """
	Determine what ships to buy and turn it into a regulated command.
    
	Parameters
	----------
	player_name: name of the player (str).
	game_data:   state of the game (dic).
    
	Return
	------
	ai_input: game input from AI (str).
    
	Version
	-------
	Specification:  Nicolas Van Bossuyt (v1. 10/03/17)
				    Bayron Mahy (v2. 17/03/17)
	Implementation: Nicolas Van Bossuyt (v1. 10/03/17)
					Alisson Leist (v2. 21/04/17)
	"""

    ai_input = ''
    name = 0

    ship_name_list = ['Apple-Pen', 'Akbar', 'amiral', 'bob', 'fob', 'I\'m_Bob_Lenon', 'Frenay-Acceleray', 'Pomme_Verte',
                      'pew-pew-pew', 'Algobot', 'blblblblblblbl', 'Stack-overflow', 'mu', 'Seiyar', '24', 'Monax']
    ship_type_name = {'f': 'fighter', 'b': 'battlecruiser', 'd': 'destroyer'}
    if len(game_data['ships']) == 0:

        ship_type = ['b', 'b', 'd', 'd']

    else:
        abandonned_ships_rate = game_data['board_size'][0] * game_data['board_size'][1] / len(game_data['ships'])

        if abandonned_ships_rate <= 25:
            ship_type = ['f', 'f', 'f', 'f', 'f', 'f', 'f', 'f', 'f', 'f']

        elif abandonned_ships_rate <= 50:
            ship_type = ['b', 'd', 'f', 'f', 'f', 'f', 'f']

        else:
            ship_type = ['b', 'b', 'd', 'f', 'f', 'f']

    for element in ship_type:
        ship_name = ship_name_list[name]
        name += 1
        ai_input += '%s:%s ' % (ship_name, ship_type_name[element])

    return ai_input[:-1]

# Ships AIs
# -----------------------------------------------------------------------------
#

def get_fighter_action(game_data, ship, owner):
    """
	Get action for a fighter.
	
	Parameters
	----------
	game_data: data of the game (dic).
	ship:      name of the ship to get input from (str).
	owner:     name of the owner of the ship (str).
	
	Return
	------
	action: action for this ship(str).
	
	Version
	-------
	Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 31/03/17)
	"""
    # Get objective.
    
    # Find path to the objective.
    
    # Move to the objective.
    
    # If move is none, attack something.
    pass


def get_destroyer_action(game_data, ship, owner):
    """
	Get action for a destroyer.
	
    Parameters
	----------
	game_data: data of the game (dic).
	ship: name of the ship to get input from (str).
	owner: name of the owner of the ship (str).
    
	Return
	------
    action: action for this ship(str).
	
	Version
	-------
	Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 31/03/17)
	"""
    # If friend battle cuiser is'nt in range, move to it.
    
    # If the friend battlecruiser and objective is in randge, attack the objective.
    pass


def get_battlecruiser_action(game_data, ship, owner):
    """
	Get action for a battlecruiser.
    
	Parameters
	----------
	game_data: data of the game (dic).
	ship: name of the ship to get input from (str).
	owner: name of the owner of the ship (str).
    
	Return
	------
	action: action for this ship(str).
	
	
	Version
	-------
	Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 31/03/17).
	"""
    # Find a abojective.
    
    # Move to the objective.
    
    # if the objective is in the attack range, attack !
    
    pass

# Ai - sub function.
# -----------------------------------------------------------------------------
# Pathfinding, 
    
def path_finding_test():
    while True:
        sucess, _ = path_finding(node((randint(0, 39), randint(0, 39)), (1, 1)), 1, node((randint(0, 39), randint(0, 39))), (40, 40))
        if sucess:raw_input()
        
def path_finding(start_node, max_speed, end_node, board_size, best_distance = sys.maxint, path = [], max_distance = 8):
    
    # Show the path finding animation
    c = create_canvas(board_size[0] + 2, board_size[1] + 2)
    for n in path:
        c = put(c, n['location'][0] + 1, n['location'][1] + 1, ' ', 'white', 'green')
    c = put(c, end_node['location'][0] + 1, end_node['location'][1] + 1, ' ', 'white', 'white')
    c = put_box(c, 0, 0, board_size[0] + 2, board_size[1] + 2)
    c = put_text(c, 2, 0, '| Path Finding... |')
    print_canvas(c)
    
    nodes = get_next_nodes(start_node, end_node, max_speed, board_size)
    
    dict_sort(nodes, 'distance')
    
    max_distance -= 1
    
    if max_distance == 0:
        return False, None
    
    for node in nodes:
        new_path = list(path)
        new_path.append(node)
        
        if node['location'] == end_node['location']:

            return True, new_path
        else:
            objective_finded, path_to_objective = path_finding(node, max_speed, end_node, board_size, best_distance, new_path, max_distance)

            if objective_finded:
                return True, path_to_objective
        
                 
    return False, path
                
                
def get_next_nodes(start_node, end_node, max_speed, board_size, just_rotate = False):
    nodes = []
    
    speed = start_node['speed']
    
    if not just_rotate and speed < max_speed and get_slow_down(speed) < get_distance(start_node['location'], end_node['location'], board_size):
        next_location = next_pos(start_node['location'], start_node['facing'], speed + 1, board_size)
        nodes.append(node(next_location, start_node['facing'], get_distance(next_location, end_node['location'], board_size), speed + 1, 'faster'))
    
        next_location = next_pos(start_node['location'], start_node['facing'], speed - 1, board_size)
        nodes.append(node(next_location, start_node['facing'], get_distance(next_location, end_node['location'], board_size), speed - 1, 'slower'))
        
    if not just_rotate and speed > 0:
        # Do nothing.
        next_location = next_pos(start_node['location'], start_node['facing'], speed, board_size)
        nodes.append(node(next_location, start_node['facing'], get_distance(next_location, end_node['location'], board_size), speed, 'none'))
    
    if speed > 0:
        # Rotate left.
        v = to_unit_vector(rotate_vector_2d(start_node['facing'], -45))
        next_location = next_pos(start_node['location'], v, speed, board_size)
        nodes.append(node(next_location, v, get_distance(next_location, end_node['location'], board_size), speed, 'left'))
        
        # Rotate right.
        v = to_unit_vector(rotate_vector_2d(start_node['facing'], 45))
        next_location = next_pos(start_node['location'], v, speed, board_size)
        nodes.append(node(next_location, v, get_distance(next_location, end_node['location'], board_size), speed, 'right'))
   
    return nodes
    
    
def node(location, facing = (0, 0), distance = 0, speed = 0, to_do = 'none'):
    """
    Create a new path finding node.
    
    Parameters
    ----------
    location: location of the node (tuple(int, int)).
    facing: facing of the node (tuple(int, int)).
    distance: distance to the objective (int).
    speed: speed of the node.
    to_do: Order to do.
    """
    return {'location': location, 'facing': facing, 'distance':distance, 'speed': speed, 'to_do': to_do}
    
    
def get_slow_down(speed):
    x = 0
    for i in range(speed):
        x += i
    return x
    
    
def move_to(game_data, ship, objective):
    """
	Move a ship at given objective.
	
	Parameters
	----------
	game_data: data of the game (dic).
	ship: name of the ship to move (str).
	objective: destination of the ship (tuple(int, int)).
	
	Return
	------
	input: input to execute <left, right, faster, slower>(str).
	
	
	Version
	-------
	Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 31/03/17).
	Implementation: Bayron Mahy (v1. 16/04/17).
	"""
    pass


# AI - command corection.
# ------------------------------------------------------------------------------
# Because nothing is perfect.

def speed(game_data, ship, change):
    """
	Check if LAICIS can increase/decrease the speed of its ship
	parameters
	----------
	game_data: game's data (dic).
	ship: targeted ship (str).
	change: change applied by LAICIS to the ship (str).
	return
	------
	'%s:%s' % (ship, change): regular input for the game loop (str).
	Version
	-------
	Specification: Bayron Mahy (v1. 20/03/17)
	Implementation: Bayron Mahy (v1. 20/03/17)
					Nicolas Van Bossuyt (v2. 29/03/17)
	"""

    ship_type = game_data['ships'][ship]['type']
    ship_speed = game_data['ships'][ship]['speed']
    ship_max_speed = game_data['model_ship'][ship_type]['max_speed']

    if (change == 'faster' and ship_speed + 1 > ship_max_speed):
        return 'slower'
    elif (change == 'slower' and ship_speed - 1 < 0):
        return 'faster'
    else:
        return change


def attack(game_data, ship):
    """
	Attack command of LAICIS.

	Parameters
	----------
	game_data: data of the game (dic).
	ship: name of the current ship (str).

	Return
	------
	attack input (str)

	Version
	-------
	Specification: Nicolas Van Bossuyt (v1. 19/03/17).
	Implementation: Nicolas Van Bossuyt (v1. 19/03/17).
					Bayron Mahy (v2. 22/03/17).
	"""

    ship_pos = game_data['ships'][ship]['location']
    ship_range = game_data['model_ship'][game_data['ships'][ship]['type']]['range']
    ship_owner = game_data['ships'][ship]['owner']
    nearby_ships = get_nearby_ship(game_data, ship, ship_range)

    if len(nearby_ships) > 0:
        ships_targeted = []

        for perhaps_target in nearby_ships:
            if game_data['ships'][perhaps_target]['owner'] != ship_owner and game_data['ships'][perhaps_target][
                'owner'] != 'none':
                ships_targeted.append(perhaps_target)

        if len(ships_targeted) > 0:

            targets_life = []

            for target in ships_targeted:
                targets_life.append(game_data['ships'][target]['heal_points'])

            final_target = ships_targeted[targets_life.index(min(targets_life))]
            target_location = predict_next_pos(game_data, final_target)
            return '%d-%d' % (target_location[0] + 1, target_location[1] + 1)

    return ''


def get_nearby_ship(game_data, target_ship, search_range):
    """
	Make a list of around ship in range.

	Parameters
	----------
	game_data: state of the game (dic).
	target_ship: name of the ship (str).
	search_range : randge for the search (int).

	Return
	------
	ships_around: list of ship around the ship (list(str)).

	Version
	-------
	Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	Implementation: Bayron Mahy, Nicolas Van Bossuyt (v1. 16/03/17)
	"""
    ship_location = ()
    ship_location = game_data['ships'][target_ship]['location']
    x, y = 0, 0
    dx = 0
    dy = -1
    nearby_ships = []

    for i in range((search_range * 2) ** 2):
        if (-search_range < x <= search_range) and (-search_range < y <= search_range) and abs(x) + abs(
                y) <= search_range:

            location = convert_coordinates((ship_location[0] + x, ship_location[1] + y), game_data['board_size'])

            if len(game_data['board'][location]) > 0:
                nearby_ships.extend(game_data['board'][location])

        if x == y or (x < 0 and x == -y) or (x > 0 and x == 1 - y):
            dx, dy = -dy, dx

        x, y = x + dx, y + dy

    return nearby_ships


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
	Distance: distance between the two points (int).

	Version
	-------
	Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
				   Bayron Mahy (v2. 19/03/17)
	Implementation: Nicolas Van Bossuyt, Alisson Leist (v1. 14/02/17)
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
	size: Size of the tore tupe(int, int).

	Return
	------
	converted_coord: coord with the tore applied.

	Version
	-------
	Specification: Nicolas Van Bossuyt (v1. 09/03/17)
	Implementation: Nicolas Van Bossuyt (v1. 09/03/17)

	"""

    def convert(a, size):
        size -= 1
        if a >= size:
            a -= size
        elif a < 0:
            a += size

        return a

    return (convert(coord[0], size[0]), convert(coord[1], size[1]))


def predict_next_pos(game_data, ship_name):
    """
	Predict the next location of a space ship.

	Parameters
	----------
	game_data: data of the game (dic).
	ship_name: name of the spaceship to predicte the next location (str).

	Return
	------
	predicted_postion : predicte_postion of the spaceship (tuple(int, int)).

	Version
	-------
	Specification: Nicolas Van Bossuyt (v1. 19/03/17).
	Implementation: Nicolas Van Bossuyt (v1. 19/03/17).
					Bayron Mahy (v2. 22/03/17).
	"""

    speed = game_data['ships'][ship_name]['speed']
    location = game_data['ships'][ship_name]['location']
    facing = game_data['ships'][ship_name]['facing']

    return next_pos(location, facing, speed, game_data['board_size'])
    
    
def next_pos(location, facing, speed, board_size):
    return convert_coordinates((location[0] + facing[0] * speed, location[1] + facing[1] * speed), board_size)

# Game commands
# ==============================================================================
# Game command parsing and execution.

# Command Parsing
# ------------------------------------------------------------------------------
# Take a string and turn it into game command.

def parse_command(commands, player_name, game_data):
    """
	Parse a player's command and execute it

	Parameters
	----------
	command: command from a player (str).
	game_data: game's data (dic).

	Return
	------
	game_data: new data of the game (dic).

	Version
	-------
	Specification:  Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	Implementation: Nicolas Van Bossuyt (V1. 10/02/17)
	"""
    commands = commands.split(' ')

    for ship_command in commands:
        sub_command = ship_command.split(':')

        if len(sub_command) == 2:
            ship_name = '%s_%s' % (player_name, sub_command[0])
            ship_command = sub_command[1]

            # Check if the space ships existe in the game.
            if ship_name in game_data['ships']:

                # Rotate command.
                if ship_command == 'left' or ship_command == 'right':
                    game_data = command_rotate(ship_name, ship_command, game_data)

                # Speed command
                elif ship_command == 'faster' or ship_command == 'slower':
                    game_data = command_change_speed(ship_name, ship_command, game_data)

                # In other case speed command.
                else:
                    attack_location = ship_command.split('-')
                    if len(attack_location) == 2:
                        attack_location = (int(attack_location[1]) - 1, int(attack_location[0]) - 1)
                        game_data['pending_attacks'].append(
                            (ship_name, game_data['ships'][ship_name]['location'], attack_location))

    return game_data


# Ship creation
# ------------------------------------------------------------------------------
# Buy and create a spaceship.

def command_buy_ships(ships, player, game_data):
    """
	Allow a player to buy some spaceships.

	Parameters
	----------
	ships: spaceships to buy (str).
	player: name of the player (str).
	game_data: stat of the game (dic).

	Return
	------
	game_data: new data of the game (dic).

	Version
	-------
	Specification:  Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	Implementation: Nicolas Van Bossuyt (v1. 14/02/17)
					Nicolas Van Bossuyt (v2. 23/02/17)
	"""
    for ship in ships.split(' '):
        ship = ship.split(':')

        if len(ship) == 2:
            # Allow human player to dont have to write the full ship type name.
            ships_type_convert = {'f': 'fighter', 'd': 'destroyer', 'b': 'battlecruiser'}
            ship[1] = ships_type_convert[ship[1][0]]

            # Get the price of the space ship.
            ship_price = game_data['model_ship'][ship[1]]['price']

            if ship_price <= game_data['players'][player]['money']:
                game_data['players'][player]['money'] -= ship_price
                create_ship(player, '%s_%s' % (player, ship[0]), ship[1], game_data)

    return game_data


def create_ship(player_name, ship_name, ship_type, game_data):
    """
	Create and add a new ship.

	Parameters
	----------
	player_name: name of the owner of the ship (str).
	ship_name: Name of the ship (str).
	ship_type: Model of the ship (str).
	game_data: data of the game (str).

	Return
	------
	game_data: new data of the game (dic).

	Version
	-------
	Specification:  Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
	Implementation: Nicolas Van Bossuyt (v1. 15/02/17)
	"""

    # Creatting the new space ship and add to the game_data.
    game_data['ships'][ship_name] = {
        'type': ship_type, 'heal_points': game_data['model_ship'][ship_type]['max_heal'],
        'facing': game_data['players'][player_name]['ships_starting_facing'],
        'speed': 0, 'owner': player_name,
        'location': game_data['players'][player_name]['ships_starting_point'],
        
        # Just for the ai.
        'objective': 'none',
        'objective_path': []
    }

    game_data['board'][game_data['players'][player_name]['ships_starting_point']].append(ship_name)
    game_data['players'][player_name]['nb_ships'] += 1

    return game_data


# Move Command
# ------------------------------------------------------------------------------
# Make shipe move, rotate, and go faste and furiouse.

def command_change_speed(ship, change, game_data):
    """
	Increase the speed of a ship.

	Parameters
	----------
	ship: name of the ship to Increase the speed (str).
	change: the way to change the speed <"slower"|"faster"> (str).
	game_data: data of the game (dic).

	Returns
	-------
	game_data: new data of the game (dic).

	Version
	-------
	Specification:  Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	Implementation: Bayron Mahy (v1. 10/02/17)
	"""

    type = game_data['ships'][ship]['type']

    # Make the ship move faster.
    if change == 'faster' and game_data['ships'][ship]['speed'] < game_data['model_ship'][type]['max_speed']:
        game_data['ships'][ship]['speed'] += 1

    # Make the ship move slower.
    elif change == 'slower' and game_data['ships'][ship]['speed'] > 0:
        game_data['ships'][ship]['speed'] -= 1

    # Show a message when is a invalide change.
    else:
        write_log(game_data, 'you cannot make that change on the speed of "' + ship + '"', 2)

    return game_data


def command_rotate(ship, facing, game_data):
    """
	Rotate the ship.

	Parameters
	----------
	ship: name of the ship to Increase the speed (str).
	facing: the facing to rotate the ship <"left"|"right">(str)
	game_data: data of the game (dic).

	Returns
	-------
	game_data: new data of the game (dic).

	Version
	-------
	Specification:  Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	Implementation: Nicolas Van Bossuyt (v1. 10/02/17)
					Nicolas Van Bossuyt (v2. 22/02/17)
	"""
    v = (0, 0)
    if facing == 'left':
        v = rotate_vector_2d(game_data['ships'][ship]['facing'], -45)
    elif facing == 'right':
        v = rotate_vector_2d(game_data['ships'][ship]['facing'], 45)

    game_data['ships'][ship]['facing'] = to_unit_vector(v)
    return game_data


def rotate_vector_2d(vector, theta):
    """
	Rotate a vector in a 2d space by a specified angle in radian.

	Parameters
	----------
	vector: 2d vector ton rotate (tuple(int,int)).
	radian: angle appli to the 2d vector (float).

	Return
	------
	vector: rotate vector 2d (tuple(int,int)).

	Version
	-------
	Specification:  Nicolas Van Bossuyt (v1. 10/02/17)
	Implementation: Nicolas Van Bossuyt (v1. 10/02/17)
					Nicolas Van Bossuyt (v2. 22/02/17)
	"""

    theta = radians(theta)
    dc, ds = cos(theta), sin(theta)
    x, y = vector[0], vector[1]
    x, y = dc * x - ds * y, ds * x + dc * y

    return (x, y)


def to_unit_vector(vector):
    """
	Convert a vector to a unit vector.

	Parameter
	---------
	vector: vector to convert (tuple(float, float)).

	Return
	------
	unit_vector: a unit vector between 1 and -1 (tuple(int, int)).

	Version
	-------
	Specification:  Nicolas Van Bossuyt (v1. 10/02/17)
	Implementation: Nicolas Van Bossuyt (v1. 22/02/17)
	"""

    def convert(value):
        if value > 0.25:
            return 1
        elif value < -0.25:
            return -1

        return 0

    return (convert(vector[0]), convert(vector[1]))


def do_moves(game_data):
    """
	Apply move to ships.

	Parameters
	----------
	game_data: data of the game (dic).

	Return
	------
	game_data: new data of the game (dic).

	Version
	-------
	Specification:  Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	Implementation: Alisson Leist (v1. 20/02/17)
					Nicolas Van Bosuuyt (v2. 23/02/17)
					Nicolas Van Bossuyt (v3. 09/03/17)
	"""
    for ship in game_data['ships']:
        location = game_data['ships'][ship]['location']
        new_location = predict_next_pos(game_data, ship)

        # Move the ship.
        game_data['board'][location].remove(ship)
        game_data['board'][new_location].append(ship)
        game_data['ships'][ship]['location'] = new_location

    return game_data


def take_abandonned_ship(game_data):
    """
	Check on the board if an abandonned ship can be taken.

	Parameters
	----------
	game_data: data of the game (dic).

	Returns
	-------
	game_data: new data of the game (dic).

	Version
	-------
	Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	Implementation: Bayron Mahy (v1. 21/02/17)
					Bayron Mahy (v2. 22/02/17)
					Nicolas Van Bossuyt (v3. 09/03/17)
	"""

    for location in game_data['board']:
        ships = game_data['board'][location]
        owners = []
        abandoned_ships = []

        if len(ships) >= 2:
            for ship in ships:
                ship_owner = game_data['ships'][ship]['owner']
                if ship_owner == 'none':
                    abandoned_ships.append(ship)
                else:
                    owners.append(ship_owner)

        if len(owners) == 1:
            owner = owners[0]
            for ship in abandoned_ships:
                abandoned_ship = game_data['ships'][ship].copy()

                # Remove the old ship.
                del game_data['ships'][ship]
                game_data['board'][abandoned_ship['location']].remove(ship)

                # Create the new one.
                abandoned_ship['owner'] = owner
                new_ship_name = "%s_%s" % (owner, ship)

                if new_ship_name in game_data['ships']:
                    new_ship_name += '_2'

                # Place the new ship on the game board.
                game_data['board'][abandoned_ship['location']].append(new_ship_name)
                game_data['ships'][new_ship_name] = abandoned_ship
                game_data['players'][owner]['nb_ships'] += 1
                write_log(game_data, '%s as take %s !' % (owner, new_ship_name), 0)

    return game_data


# Attack Command
# ------------------------------------------------------------------------------
# Allow ship to attack each other.

def command_attack(ship, ship_coordinate, target_coordinate, game_data):
    """
	Determine if the attack works and do it.

	Parameters
	----------
	ship_location: coodinate of the first ship (tuple(int, int)).
	coordinate: coordinate of the tile to attack (tuple(int,int)).
	game_data: data of the game (dic).

	Return
	------
	game_data: new data of the game (dic).

	Version
	-------
	Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
	Implementation: Alisson Leist (v1. 14/2/17)
					Bayron Mahy, Alisson Leist (v2. 20/02/17)
					Alisson Leist (v3. 17/03/17)
					Alisson Leist (v4. 24/03/17)
	"""
    ship_type = game_data['model_ship'][game_data['ships'][ship]['type']]

    damages = ship_type['damages']
    distance = get_distance(ship_coordinate, target_coordinate, game_data['board_size'])

    if distance <= ship_type['range'] and len(game_data['board'][target_coordinate]) != 0:
        game_data['nb_rounds'] = 0

        # Give damages to all ship on targe coordinate.
        for target_ship in game_data['board'][target_coordinate]:
            # Give damages to the taget ship.
            game_data['ships'][target_ship]['heal_points'] -= damages

            if game_data['ships'][target_ship]['heal_points'] <= 0:
                write_log(game_data, '%s kill %s' % (ship, target_ship), 1)

                # Remove the space ship.
                game_data['board'][target_coordinate].remove(target_ship)
                if game_data['ships'][target_ship]['owner'] != 'none':
                    game_data['players'][game_data['ships'][target_ship]['owner']]['nb_ships'] -= 1

                del game_data['ships'][target_ship]
            else:
                write_log(game_data, '%s shot %s' % (ship, target_ship), 1)

    return game_data


def do_attack(game_data):
    """
	Apply attacks to ships.

	Parameters
	----------
	game_data: data of the game (dic).

	Return
	------
	game_data: new data of the game (dic).

	Version
	-------
	Specification: Nicolas Van Bossuyt (v1. 20/03/17)
	Implementation: Nicolas Van Bossuyt (v1. 20/03/17)
	"""

    # Do Attack
    for pending_attack in game_data['pending_attacks']:
        if pending_attack[0] in game_data['ships']:
            game_data = command_attack(pending_attack[0], pending_attack[1], pending_attack[2], game_data)

    return game_data


# Utils
# ==============================================================================
# Somme use full function for a simple life. And also parse game file.

def parse_game_file(path):
    """
	Parse a .cis file and returns its content.

	Parameter
	---------
	path: path of the .cis file (str).

	Return
	------
	parsed_data: data contained in the .cis file (dic).

	Version
	-------
	Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	Implementation: Nicolas Van Bossuyt (v2. 15/02/17)
	"""
	
    # Split file lines and remove '\n' chars.
    cis_file = open(path, 'r')
    file_content = [line.strip() for line in cis_file]
    cis_file.close()

    # Get the size of the gameboard.
    size_str = file_content[0].split(' ')
    size = (int(size_str[1]), int(size_str[0]))

    # Get lost space ship in the file..
    ships_list = []
    for line_index in range(len(file_content) - 1):
        ship_str = file_content[line_index + 1].split(' ')
		
        if len(ship_str) == 4:
            ship_name_and_type = ship_str[2].split(':')
			
            ship = (int(ship_str[1]) - 1,			 # Y location of the ship.
					int(ship_str[0]) - 1,			 # X location of the ship.
					ship_name_and_type[0],			 # Name of the ship.
					ship_name_and_type[1],			 # Type of the ship.
					facing_to_vector2d(ship_str[3])) # Facing of the ship.
					
            ships_list.append(ship)

    # Create parsed data dictionary and return it.
    parsed_data = {'size': size, 'ships': ships_list}

    return parsed_data


def facing_to_vector2d(facing):
    """
	Convert a string facing to a vector2d.

	Parameter
	---------
	facing: facing to convert <up|down|left|right|up-left|up-right|down-left|down-right>(str).

	Return
	------
	vector: vector2d from facing (tuple(int, int)).

	Version
	-------
	Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	Implementation: Nicolas Van Bossuyt (v1. 11/02/17)
	"""

    convert = {'up': (0, -1), 'up-right': (1, -1), 'right': (1, 0), 'down-right': (1, 1), 'down': (0, 1), 'down-left': (-1, 1), 'left': (-1, 0), 'up-left': (-1, -1)}
    return convert[facing]


def vector2d_to_facing(vector):
    """
	Convert a string facing to a vector2d.

	Parameter
	---------
	vector: vector2d to convert in facing (tuple(int, int)).

	Return
	------
	facing: facing <up|down|left|right|up-left|up-right|down-left|down-right>(str).

	Version
	-------
	Specification: Nicolas Van Bossuyt (v1. 18/04/17)
	Implementation: Nicolas Van Bossuyt (v1. 18/04/17)
	"""
    convert = {(0, 1): 'up', (-1, 1): 'up-left', (-1, 0): 'left', (-1, -1): 'down-left', (0, -1): 'down', (1, 0): 'right', (1, -1): 'down-right', (1, 1): 'up-right'}
    return convert[vector]


def write_log(game_data, message, type=0):
    """
	Write a message in the game logs.
	
	Parameters
	----------
	game_data: data of the game (dic).
	message: message to print to game logs (str).
	(optional) type: type of the message <0 = info|1 = warning|2 = error>
	
	Return
	------
	game_data: new data of the game (dic)
	
	Version
	-------
	Specification: Nicolas Van Bossuyt (v1. 18/04/2017)
	Implementation: Nicolas Van Bossuyt (v1. 18/04/2017)
	"""

    game_data['game_logs'].append((type, message))
    f = open('log.txt', 'r')
    txt = f.read();
    f.close()

    txt += '%s\n' % message

    f = open('log.txt', 'w')
    f.write(txt)
    f.close()

    return game_data


def create_game_board(file_name, board_size, lost_ships_count):
    """
	Create a new "coders in space"'s board file.

	Parameters
	----------
	file_name: name of the cis file (str).
	board_size: size of the game board (tuple(int, int)).
	lost_ships_count: number of lost ship on the game board (int).

	Version
	-------
	Specification: Nicolas Van Bossuyt (v1. 25/02/17)
	Implementation: Nicolas Van Bossuyt (v1.25/02/17)
	"""
    ship_type =   ['fighter', 'destroyer', 'battlecruiser']
    ship_facing = ['up', 'up-left', 'up-right', 'left', 'right', 'down', 'down-left', 'down-right']
	
    buffer = '' # Create the string buffer for the file.
    buffer += "%d %d\n" % (board_size[0], board_size[1]) # Add the first of the file whith the size of the game board.

    for i in range(lost_ships_count):
        buffer += '%d %d %s:%s %s\n' % (randint(0, board_size[0] - 1), # Y coodinate of the ship.
										randint(0, board_size[1] - 1), # X coodinate of the ship.
										'ship_' + str(i), 			   # Name of the ship.
										ship_type[randint(0, len(ship_type) - 1)],     # Type of the ship.
										ship_facing[randint(0, len(ship_facing) - 1)]) # Facing of the ship
    
	# Saving the game board to a file.
	f = open(file_name, 'w')
    f.write(buffer)
    f.close()

    
def dict_sort(items, key):
        """ Implementation of bubble sort """
        for i in range(len(items)):
                for j in range(len(items)-1-i):
                        if items[j][key] > items[j+1][key]:
                                items[j], items[j+1] = items[j+1], items[j] 

# Use for quick debuging.
if __name__ == '__main__':
    play_game('board/battlefield.cis', ('Botbot', 'A.I.C.I.S.'), ai_vs_ai, max_rounds_count = 1000)

# -*- coding: utf-8 -*-

# Alien
# ==============================================================================
# A cool friend to get in touch wile coding.

"""
                         ___---------___
                       _".^ .^ ^.  '..:"-_
                     /:            . .^:.  :\
                   /: .   .    .        . . .:\
                  /:               .  ^ .  . .:\
                 /.                        .  .:\
                |:                    .  .  ^. .:|
                ||        .                . . !:|
                \(                            .:)/
                |. ######              .#######::|
                 |.#######           ..########:|
                 \ ########           :########:/
                  \ ########       . ########.:/
                   \. #######       #######..:/
                     \           .   .   ..:/
                      \.       | |     . .:/
                        \             ..:/
                         \.           .:/
                           \   ___/  :/
                            \       :/
                             |\  .:/|
                             |  --.:|
                             "(  ..)"
                            /  .  .::\
"""

# Imports
# ==============================================================================
# Import some cool component for the game.
from time import sleep #because everyone needs to rest.
from math import *
from random import randint, seed
from remote_play import notify_remote_orders, get_remote_orders, connect_to_player, disconnect_from_player
from graphics import *
from LAICIS_ia import *

# Game
# ==============================================================================
# Create a new game and play it.

def play_game(level_name, players_list, no_splash = False, no_gui = False, screen_size = (190, 50), distant_id = None, distant_ip = None, verbose_connection = False, max_rounds_count = 10):
    """
    Main function that executes the game loop.

    Parameters
    ----------
    level_name: name of the level (str).
    players_list: list of players (list).
    (optional) no_splash: ship the splash screen (bool).
    (optional) no_gui: disable game user interface (bool).
    (optional) screen_size: size of the terminal window (tuple(int, int)).
    (optional) distant_id: ID of the distant player (int).
    (optional) distant_ip: IP of the distant player (str).
    (optional) verbose_connection: anabled connection output in terminal (bool).
    (optional) max_rounds_count: number of rounds (int).

    Return
    ------
    winner_name: name of the winner (str).

    Note
    ----
    Recomanded screen_size: (190, 50).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Bayron Mahy, Nicolas Van Bossuyt (v1. 15/02/17)
    """
    # Create the new game.
    is_distant_game = distant_id != None and distant_ip != None

    if is_distant_game:
        game_stats = new_game(level_name, players_list, connect_to_player(distant_id, distant_ip, verbose_connection))
    else:
        game_stats = new_game(level_name, players_list)

    game_stats['screen_size'] = screen_size
    game_stats['max_nb_rounds'] = max_rounds_count

    # Show the splash screen.
    if not no_splash:
        show_splash_game(game_stats)
        raw_input() # wait the player pressing enter.

    is_ship_buy = True
    game_running = True
    # Game loop.
    while game_running:

        # Show the game board to the human player.
        if not no_gui:
            show_game_board(game_stats)


        # Cleaning the pending_attack list.
        game_stats['pending_attack'] = []

        # getting players input.
        for player in players_list:

            # Get current player input.
            if is_ship_buy:
                game_stats = command_buy_ships(get_game_input(player, True, game_stats), player, game_stats)
            else:
                if game_stats['players'][player]['nb_ships'] > 0:
                    game_stats = parse_command(get_game_input(player, False, game_stats), player, game_stats)
                elif game_stats['players'][player]['type'] != 'none':
                    game_stats['game_logs'].append(player + ' has lost all these ships, so he has nothing to do.')

        is_ship_buy = False

        # Do ships moves.
        game_stats = do_moves(game_stats)

        # Take all abandonned ships.
        game_stats = take_abandonned_ship(game_stats)

        # Do Attack
        for pending_attack in game_stats['pending_attacks']:
            game_stats = command_attack(pending_attack[0], pending_attack[1], pending_attack[2], game_stats)

        game_stats['nb_rounds'] += 1
        game_running = is_game_continue(game_stats)

    # Disconect the remote player.
    if is_distant_game:
        disconnect_from_player(game_stats['players']['distant']['connection'])

    # Show the end game screen.
    if not no_splash:
        show_end_game(game_stats)

    return game_stats['winners']

def new_game(level_name, players_list, connection = None):
    """
    Create a new game from a '.cis' file.

    Parameters
    ----------
    level_name: name of the path to .cis file (str).
    players_list: list of players (list).
    (optional) connection: distant player connection (tuple).

    Return
    -------
    game_stats: new game stats (dic).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/2017)
                    Bayron Mahy, Nicolas Van Bossuyt (v2. 13/02/2017)
                    Nicolas Van Bossuyt (v3. 23/02/17)
    """

    # Create game_stats dictionary.
    game_file = parse_game_file(level_name)
    game_stats = {'board':{},
                  'players':{},
                  'model_ship':{},
                  'ships': {},
                  'board_size': game_file['size'],
                  'level_name': level_name,
                  'nb_rounds': -1,
                  'max_nb_rounds': 10,
                  'pending_attacks': [],
                  'game_logs': [],
                  'winners': [],
                  'is_remote_game': connection != None,
                  }

    # Create ship specs sheet.
    game_stats['model_ship']['fighter'] = {'icon': u'F', 'max_heal':3, 'max_speed':5, 'damages':1, 'range':5, 'price':10}
    game_stats['model_ship']['destroyer'] = {'icon': u'D', 'max_heal':8, 'max_speed':2, 'damages':2, 'range':7, 'price':20}
    game_stats['model_ship']['battlecruiser'] = {'icon': u'B', 'max_heal':20, 'max_speed':1, 'damages':4, 'range':10, 'price':30}

    # Create the game board.
    for line in range(game_file['size'][0]):
        for column in range(game_stats['board_size'][1]):
            game_stats['board'][(line,column)] = []

    # Place lost ships.
    for ships in game_file['ships']:
        game_stats['ships'][ships[2]]= { 'type':ships[3], 'heal_points':game_stats['model_ship'][ships[3]]['max_heal'],'direction':ships[4], 'speed':0, 'owner': 'none', 'position': (ships[0],ships[1]) }
        game_stats['board'][(ships[0],ships[1])].append(ships[2])

    index_player=1

    for player in players_list:
        if 'bot' in player:
            player_type = 'ai'
        elif 'dumb' in player:
            player_type = 'ai_dumb'
        elif player == 'distant':
            player_type = 'distant'
        else:
            player_type = 'human'

        # Create new player.
        if index_player <= 4:
            game_stats['players'][player] = {'name': player,'money':100,'nb_ships': 0,'type': player_type, 'fitness': 0}

            if index_player==1:
                game_stats['players'][player]['ships_starting_point'] = (9, 9)
                game_stats['players'][player]['ships_starting_direction'] = (1, 1)
                game_stats['players'][player]['color'] ='red'

            elif index_player==2:
                game_stats['players'][player]['ships_starting_point'] = (game_stats['board_size'][0]-10, game_stats['board_size'][1]-10)
                game_stats['players'][player]['ships_starting_direction'] = (-1, -1)
                game_stats['players'][player]['color'] = 'blue'

            elif index_player==3:
                game_stats['players'][player]['ships_starting_point'] = (game_stats['board_size'][0]-10, 9)
                game_stats['players'][player]['ships_starting_direction'] = (-1, 1)
                game_stats['players'][player]['color'] = 'yellow'

            elif index_player==4:
                game_stats['players'][player]['ships_starting_point'] = (9, game_stats['board_size'][1]-10)
                game_stats['players'][player]['ships_starting_direction'] = (1, -1)
                game_stats['players'][player]['color'] = 'magenta'

        else:
            game_stats['game_logs'].append('There is too many player the player %s is a loser he must be watch you playing' % (player))

        index_player+=1

    if connection != None:
        game_stats['players']['distant']['connection'] = connection

    return game_stats

def show_splash_game(game_stats):
    """
    Show the splash screen.

    Parameter
    ---------
    game_stats: stats of the game (dic).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 27/02/17)
    """

    def clear_canvas(canvas):
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
        canvas = put_box(canvas, 0, 0, screen_size[0], screen_size[1])
        canvas = put_stars_field(canvas, 1, 1, screen_size[0] - 2, screen_size[1] - 2, 1)
        return canvas

    screen_size = game_stats['screen_size']
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
    c = clear_canvas(c)
    c = put_ascii_art(c, screen_size[0] / 2 - 69, screen_size[1] / 2 - 5, 'coders_in_space', 'yellow')
    print_canvas(c)

def show_end_game(game_stats):
    """
    Show the end game screen.

    Parameter
    ---------
    game_stats: stats of the game (dic).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    implementation: Nicolas Van Bossuyt (v1. 27/02/17)
    """

    screen_size = game_stats['screen_size']

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
    for player in game_stats['players']:
        if player != 'none':
            if player in game_stats['winners']:
                # The player win the game.
                text_lenght = mesure_ascii_text(font_standard, player)

                text_font = font_standard
                text_color = game_stats['players'][player]['color']

            else:
                # The player lost the game.
                text_lenght = mesure_ascii_text(font_small, player)
                text_location = (95 - int(text_lenght / 2), line_index*11 + 2)
                text_font = font_small
                text_color = 'white'

            text_location = (screen_size[0] / 2 - int(text_lenght / 2), line_index*11 + 2)

            # Put player informations.
            c = put_ascii_text(c, text_font, player, text_location[0], text_location[1], text_color)
            c = put_text(c, text_location[0], text_location[1] + 6, '_' * text_lenght)
            c = put_text(c, text_location[0], text_location[1] + 8, "%d spaceships" % (game_stats['players'][player]['nb_ships']))
            c = put_text(c, text_location[0], text_location[1] + 9, "%d G$" % (calculate_value(player, game_stats)))

            line_index += 1

    # Print the canvas in the terminal.
    print_canvas(c)

def is_game_continue(game_stats):
    """
    Check if the game continue.

    Parameter
    ---------
    game_stats: stats of the game (dic).

    Return
    ------
    False if the game is over.

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 24/02/17)
    Implementation: Alisson Leist (v1. 24/02/17)
    """

    not_loser = []

    # Checking playert thats have more than on ships
    for player in game_stats['players']:
        if player != 'none' and game_stats['players'][player]['nb_ships'] > 0:
            not_loser.append(player)

    # Check if the game continue.
    if len(not_loser) > 1 and game_stats['nb_rounds'] <= game_stats['max_nb_rounds']:

        return True


    winners = {}
    for player in not_loser:
        winners[player] = calculate_value(player, game_stats)

    max_value = 0
    max_value_owners = []

    for player in winners:
        if winners[player] > max_value:

            max_value = winners[player]
            max_value_owners = []
            max_value_owners.append(player)

        elif winners[player] == max_value:
            max_value_owners.append(player)

    game_stats['winners'] = max_value_owners

    return False

def calculate_value(player_name, game_stats):
    """
    Calculate the total ship value of a player.

    Parameters
    ----------
    player_name: name of the player to count value (str)
    game_stats: game before comand execution (dic)

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 24/02/17)
    Implementation: Alisson Leist (v1. 24/02/17)
    """
    total_value = 0

    for ship in game_stats['ships']:
        if game_stats['ships'][ship]['owner'] == player_name:
            total_value += game_stats['model_ship'][ game_stats['ships'][ship]['type'] ]['price']

    return total_value

# Input
# ==============================================================================
# Get input from each player.

def get_game_input(player_name, buy_ships, game_stats):
    """
    Get input from a specified player.

    Parameters
    ----------
    player_name: name of the player to get input (str).
    buy_ships: True, if players buy their boats (bool).
    game_stats: stats of the game (dic).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Niolas Van Bossuyt (V1. 15/02/17)
    """
    player_input = ''
    player_type = game_stats['players'][player_name]['type']

    if player_type == 'human':
        # get input from the human player.
        player_input = get_human_input(player_name, buy_ships, game_stats)

    elif player_type == 'ai':
        # get input from the ai.
        if buy_ships:
            player_input = get_ai_spaceships(player_name, game_stats)
        else:
            player_input = get_ai_input(player_name, game_stats)

    elif player_type == 'dumb_ai':
        # Get input from the dumb ai.
        if buy_ships:
            player_input = get_dumb_ai_spaceships(player_name, game_stats)
        else:
            player_input = get_dumb_ai_input(player_name, game_stats)

    elif player_type == 'distant':
        # Get input from the distant player.
        player_input = get_distant_input(game_stats)

    # Send the order to the remote player.
    if game_stats['is_remote_game'] and (player_type == 'human' or player_type == 'ai' or player_type == 'ai_dumb'):
        notify_remote_orders(game_stats['players']['distant']['connection'], player_input)

    return player_input

# Player
# ------------------------------------------------------------------------------
# Human player interaction with the game.

def get_human_input(player_name, buy_ship, game_stats):
    """
    Get input from a human player.

    Parameters
    ----------
    player_name: Name of the player to get input from (str).
    buy_ships: True, if players buy their boats (bool).
    game_stats: stats of the game (dic).

    Returns
    -------
    player_input: input from Human (str).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bosuyt (v1. 22/02/17)
    """

    while True:
        # Show the game board to the human player.
        show_game_board(game_stats)
        # Getting human player input.
        player_input = raw_input('\033[%d;%dH %s:' % (game_stats['screen_size'][1], 3, player_name))

        # Run human player command.
        if '/' in player_input:

            if player_input == '/ship-list':
                show_ship_list(player_name, game_stats)
            else:
                print 'Wrong input'
        else:
            return player_input

def show_ship_list(player_name, game_stats):
    """
    Show spaceships information on the terminal.

    Parameters
    ----------
    player_name: name of the player to show the information (str).
    game_stats: stats of the game (dic).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 22/02/17)
    """
    screen_size = game_stats['screen_size']

    c_ship_list = create_canvas(106, 10 + len(game_stats['ships']) + len(game_stats['players']) * 4)
    put_box(c_ship_list, 0, 0, c_ship_list['size'][0], c_ship_list['size'][1], 'double')
    put_text(c_ship_list, 3, 0, '[ Spaceships ]')
    line_index = 0

    # Show ships models.
    c_ship_list = put_text(c_ship_list, 3, 2, '// Spaceships Models //')
    c_ship_list = put_text(c_ship_list, 1, 3, '-'*104)

    for ship_model_name in game_stats['model_ship']:
        ship_model = game_stats['model_ship'][ship_model_name]
        c_ship_list = put_text(c_ship_list, 3, 4 + line_index, '[%s] %s // heal: %spv ~ speed: %skm/s ~ damages: %spv ~ attack range: %skm ~ price: %sG$ ' % (ship_model['icon'], ship_model_name, ship_model['max_heal'], ship_model['max_speed'], ship_model['damages'], ship_model['range'], ship_model['price']))
        line_index+=1

    c_ship_list = put_text(c_ship_list, 1, 4 + line_index, '-'*104)

    for player in game_stats['players']:
        # Show Players's ships.

        line_index += 4

        if player == 'none':
            c_ship_list = put_text(c_ship_list, 3, 2 + line_index, '// Abandonned spaceships //')
        else:
            c_ship_list = put_text(c_ship_list, 3, 2 + line_index, '// %s\'s spaceships //' % (player), color=game_stats['players'][player]['color'])

        c_ship_list = put_text(c_ship_list, 1, 3 + line_index, '-'*104)

        if game_stats['players'][player]['nb_ships'] > 0:
            for ship_name in game_stats['ships']:
                ship = game_stats['ships'][ship_name]
                if ship['owner'] == player:
                    c_ship_list = put_text(c_ship_list, 3, 4 + line_index, '[%s] %s // heal: %spv ~ speed: %skm/s ~ Facing: %s' % (game_stats['model_ship'][ship['type']]['icon'], ship_name, ship['heal_points'], ship['speed'], str(ship['direction'])))
                    line_index+=1
        else:
            c_ship_list = put_text(c_ship_list, 3, 4 + line_index, 'Sorry no space ships:/')
            line_index+=1

        c_ship_list = put_text(c_ship_list, 1, 4 + line_index, '-'*104)

    is_scroll_continue = True
    scroll = 0

    while is_scroll_continue:
        c_window = create_canvas(screen_size[0], screen_size[1])
        c_window = put_box(c_window, 0, 0, screen_size[0], screen_size[1])

        c_window = put_canvas(c_window, c_ship_list, 1, 1 + scroll)
        print_canvas(c_window)

        is_scroll_continue = ( c_ship_list['size'][1] - screen_size[1] ) > abs(scroll)

        if is_scroll_continue:
            raw_input('\033[%d;%dHPress enter to scroll...' % (screen_size[1], 1))
        else:
            raw_input('\033[%d;%dHPress enter to exit...' % (screen_size[1], 3))
        scroll-=10

def show_game_board(game_stats):
    """
    Show game board on the teminal.

    Parameter
    ---------
    game_stats: stats of the game (dic).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 10/02/2017)
                    Nicolas Van Bossuyt (v2. 12/02/2017)
                    Nicolas Van Bossuyt (v3. 13/02/2017)
                    Nicolas Van Bossuyt (v4. 19/02/2017)
                    Nicolas Van Bossuyt (v5. 23/02/2017)
                    Nicolas Van Bossuyt (v6. 01/03/2017)
    """
    screen_size = game_stats['screen_size']

    # Create a the main canvas.
    c_screen = create_canvas(screen_size[0], screen_size[1])

    # Put a cool artwork on the background.
    c_screen = put_ascii_art(c_screen, 1, screen_size[1] - 30, 'planet')
    c_screen = put_box(c_screen, 0, 0, screen_size[0], screen_size[1], 'single')

    # Create the board frame.
    # --------------------------------------------------------------------------
    game_board_size = (game_stats['board_size'][0]*3 + 5, game_stats['board_size'][1] + 3)
    c_board = create_canvas(game_board_size[0], game_board_size[1])
    c_board = put_box(c_board, 0, 0, game_board_size[0], game_board_size[1])
    c_board = put_text(c_board, 2, 0, u'[ Coders In Space: %s ] %s / %s Rounds' % (game_stats['level_name'], game_stats['nb_rounds'], game_stats['max_nb_rounds']))
    c_board = put_stars_field(c_board, 1, 1, game_board_size[0] - 2, game_board_size[1] - 2, 1)

    # Put horizontal coordinate.
    coordinate_string = ''
    for i in range(1, game_stats['board_size'][0] + 1):
        value_string = str(i)
        if len(value_string) == 1:
            value_string = ' ' + value_string
        value_string += ' '
        coordinate_string += value_string

    c_board = put_text(c_board, 4, 1, coordinate_string, 1, 0, 'blue', 'white')

    # Put vertical coordinate.
    for i in range(1, game_stats['board_size'][1] +1):
        value_string = str(i)
        if len(value_string) == 1:
            value_string = ' ' + value_string
        c_board = put_text(c_board, 1, i + 1, value_string + ' ', 1, 0, 'blue', 'white')

    # Put game board.
    for x in range(game_stats['board_size'][0]):
        for y in range(game_stats['board_size'][1]):
            on_screen_board_tile = (x*3 + 4, y + 2)

            if len(game_stats['board'][(x,y)]) == 1:
                # When there are one, show somme information about.
                ship_name = game_stats['board'][(x,y)][0]
                ship_type = game_stats['ships'][ship_name]['type']
                ship_icon = game_stats['model_ship'][ship_type]['icon']
                ship_owner = game_stats['ships'][ship_name]['owner']
                ship_owner_color = None

                # Print ship on gameboard.
                if game_stats['ships'][ship_name]['owner'] != 'none':
                    ship_owner_color = game_stats['players'][game_stats['ships'][ship_name]['owner']]['color']

                ship_direction = game_stats['ships'][ship_name]['direction']
                ship_speed = game_stats['ships'][ship_name]['speed']

                # Pur direction line.
                direction_char = '|'

                if ship_direction == (1, 1) or ship_direction == (-1, -1):
                    direction_char = '\\'
                elif ship_direction == (1, -1) or ship_direction == (-1, 1):
                    direction_char = '/'
                elif ship_direction == (1, 0) or ship_direction == (-1, 0):
                    direction_char = u'─'

                c_board = put_text(c_board, on_screen_board_tile[0] + 1 + ship_direction[0], on_screen_board_tile[1]  + ship_direction[1], direction_char, 1, 0, 'white', ship_owner_color)
                c_board = put_text(c_board, on_screen_board_tile[0] + 1, on_screen_board_tile[1], ship_icon,1,0,'white', ship_owner_color)
            elif len(game_stats['board'][(x,y)]) > 0:
                # in other case show how many ship there are in the tile.
                c_board = put_text(c_board, on_screen_board_tile[0], on_screen_board_tile[1], '!' + str(len(game_stats['board'][(x,y)])),1,0,'white', 'green')

    c_screen = put_canvas(c_screen, c_board, screen_size[0] / 2 - c_board['size'][0] / 2, int((screen_size[1] - 7) / 2) - c_board['size'][1] / 2)

    # Put players liste frame.
    # --------------------------------------------------------------------------
    players_bord_size = (len(game_stats['players']) * 30 + 2, 7)
    players_bord_location = (0, screen_size[1] - 7)

    c_screen = put_box(c_screen, 0, players_bord_location[1], players_bord_size[0], players_bord_size[1])
    c_screen = put_text(c_screen, 1, players_bord_location[1], u'[ Players ]')

    # Put players liste.
    player_count = 0
    for player in game_stats['players']:
        if player != 'none':
            location = ((player_count * 30) + 1, players_bord_location[1] + 1,)
            c_screen = put_box(c_screen, location[0], location[1], 30, 5, 'single')

            # Put player informations.
            c_screen = put_text(c_screen, location[0] + 2, location[1] , '[ ' + game_stats['players'][player]['name'] + ' ]', color=game_stats['players'][player]['color'])
            c_screen = put_text(c_screen, location[0] + 2, location[1] + 1, 'Type: ' + game_stats['players'][player]['type'])
            c_screen = put_text(c_screen, location[0] + 2, location[1] + 2, 'Money: ' + str(game_stats['players'][player]['money']) + '$')
            c_screen = put_text(c_screen, location[0] + 2, location[1] + 3, 'Spaceship count: ' + str(game_stats['players'][player]['nb_ships']))

            player_count += 1

    # Put Game Logs frame.
    # --------------------------------------------------------------------------
    logs_size = (screen_size[0] - players_bord_size[0], 7)
    logs_location = (players_bord_size[0], screen_size[1] - 7)

    c_screen = put_box(c_screen, logs_location[0], logs_location[1], logs_size[0], logs_size[1])
    c_screen = put_text(c_screen, logs_location[0] + 1, logs_location[1],u'[ Game Logs ]')

    line_index = 1
    for line in game_stats['game_logs'][-5:]:
        c_screen = put_text(c_screen, logs_location[0] + 1, logs_location[1] + line_index, line)
        line_index +=1

    # Show the game board in the terminal.
    print_canvas(c_screen)

# A.I.
# ------------------------------------------------------------------------------
# AI interactions

def get_ai_input(player_name, game_stats):
    """
    Get input from a AI player.

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
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 27/02/17)
    """

    action = ['faster', 'slower', 'left', 'right']

    ai_input = ''

    for ship in game_stats['ships']:
        if (game_stats['ships'][ship]['owner'] == player_name):
            ai_input += ship.replace(player_name + '_','') + ':' + action[randint(0, len(action) - 1 )] + ' '

    return ai_input[:-1]

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

# Remote player
# ------------------------------------------------------------------------------
# Handeling remote player command.

def get_distant_input(game_stats):
    """
    Get input from a distant player.

    Parameter
    ---------
    game_stats: stats of the game (dic).

    Return
    ------
    remote_input: input from distant player (str).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
                     Nicolas Van Bossuyt (v2. 03/03/17)
    Implementation: Nicolas Van Bossuyt (v1. 03/03/17)
    """

    connection = game_stats['players']['distant']['connection']
    return get_remote_orders(connection)

# Game commands
# ==============================================================================
# Game command parsing and execution.

# Command Parsing
# ------------------------------------------------------------------------------
# From a string to a game command.

def parse_command(commands, player_name, game_stats):
    """
    Parse a player's command and execute it

    Parameters
    ----------
    command: command from a player (str).
    game_stats: stat of the game (dic).

    Return
    ------
    game_stats: new stats of the game (dic).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (V1. 10/02/17)
    """

    commands = commands.split(' ')
    for cmd in commands:
        if cmd == '':
            continue

        try:
            sub_cmd = cmd.split(':')
            ship_name = player_name + '_' + sub_cmd[0]
            ship_action = sub_cmd[1]

            if ship_action == 'slower' or ship_action == 'faster':
                # Speed command:
                game_stats = command_change_speed(ship_name, ship_action, game_stats)
            elif ship_action == 'left' or ship_action == 'right':
                # Rotate command:
                game_stats = command_rotate(ship_name, ship_action, game_stats)
            else:
                # Attack command:
                coordinate_str = ship_action.split('-')
                coordinate = (int(coordinate_str[0]) - 1, int(coordinate_str[1]) - 1)
                game_stats['pending_attacks'].append((ship_name, game_stats['ships'][ship_name]['position'], coordinate))

        except Exception:
            game_stats['game_logs'].append('Something wrong append with this command :')
            game_stats['game_logs'].append(str(commands))

    return game_stats

# Ship creation
# ------------------------------------------------------------------------------
# Buy and create a spaceship.

def command_buy_ships(ships, player, game_stats):
    """
    Allow a player to buy some spaceships.

    Parameters
    ----------
    ships: spaceships to buy (str).
    player: name of the player (str).
    game_stats: stat of the game (dic).

    Return
    ------
    game_stats: new stats of the game (dic).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 14/02/17)
                    Nicolas Van Bossuyt (v2. 23/02/17)
    """

    for ship in ships.split(' '):

        if ship == '': continue

        ship = ship.split(':')

        # Allow human player to dont have to write the full ship type name.
        if ship[1][0] == 'f':
            ship[1] = 'fighter'
        elif ship[1][0] == 'd':
            ship[1] = 'destroyer'
        elif ship[1][0] == 'b':
            ship[1] = 'battlecruiser'

        ship_price = game_stats['model_ship'][ship[1]]['price']

        if ship_price <= game_stats['players'][player]['money']:
            game_stats['players'][player]['money'] -= ship_price
            create_ship(player, '%s_%s' % (player, ship[0]), ship[1], game_stats)

    return game_stats

def create_ship(player_name, ship_name, ship_type, game_stats):
    """
    Create and add a new ship.

    Parameters
    ----------
    player_name: name of the owner of the ship (str).
    ship_name: Name of the ship (str).
    ship_type: Model of the ship (str).
    game_stats: stats of the game (str).

    Return
    ------
    game_stats: new stats of the game (dic).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
    Implementation: Nicolas Van Bossuyt (v1. 15/02/2017)
    """

    # Creatting the new space ship and add to the game_stats.
    game_stats['ships'][ship_name] = {'type':ship_type, 'heal_points':game_stats['model_ship'][ship_type]['max_heal'], 'direction':game_stats['players'][player_name]['ships_starting_direction'], 'speed':0, 'owner': player_name, 'position': game_stats['players'][player_name]['ships_starting_point']}
    game_stats['board'][game_stats['players'][player_name]['ships_starting_point']].append(ship_name)
    game_stats['players'][player_name]['nb_ships'] += 1

    return game_stats

# Move Command
# ------------------------------------------------------------------------------
# Make shipe move, rotate, and go faste and furiouse.

def command_change_speed(ship, change, game_stats):
    """
    Increase the speed of a ship.

    Parameters
    ----------
    ship: name of the ship to Increase the speed (str).
    change: the way to change the speed <"slower"|"faster"> (str).
    game_stats: stats of the game (dic).

    Returns
    -------
    game_stats: new stats of the game (dic).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Bayron Mahy (v1. 10/02/2017)
    """
    type = game_stats['ships'][ship]['type']

    # Make the ship move faster.
    if change == 'faster' and game_stats['ships'][ship]['speed'] < game_stats['model_ship'][type]['max_speed']:
        game_stats['ships'][ship]['speed']+=1

    # Make the ship move slower.
    elif change == 'slower' and game_stats['ships'][ship]['speed'] > 0:
        game_stats['ships'][ship]['speed']-=1

    # Show a message when is a invalide change.
    else:
        game_stats['game_logs'].append('you cannot make that change on the speed of "' + ship + '"')

    return game_stats

def command_rotate(ship, direction, game_stats):
    """
    Rotate the ship.

    Parameters
    ----------
    ship: name of the ship to Increase the speed (str).
    direction: the direction to rotate the ship <"left"|"right">(str)
    game_stats: stats of the game (dic).

    Returns
    -------
    game_stats: new stats of the game (dic).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 10/02/17)
                    Nicolas Van Bossuyt (v2. 22/02/17)
    """
    v = (0, 0)
    if direction == 'left':
        v = rotate_vector_2D(game_stats['ships'][ship]['direction'], -45)
    elif direction == 'right':
        v = rotate_vector_2D(game_stats['ships'][ship]['direction'], 45)

    game_stats['ships'][ship]['direction'] = to_unit_vector(v)
    return game_stats

def rotate_vector_2D(vector, theta):
    """
    Rotate a vector in a 2D space by a specified angle in radian.

    Parameters
    ----------
    vector: 2D vector ton rotate (tuple(int,int)).
    radian: angle appli to the 2D vector (float).

    Return
    ------
    vector: rotate vector 2d (tuple(int,int)).

    Version
    -------
    Specification: Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 10/02/17)
                    Nicolas Van Bossuyt (v2. 22/02/17)
    """

    theta = radians(theta)
    dc, ds = cos(theta), sin(theta)
    x, y = vector[0], vector[1]
    x, y = dc*x - ds*y, ds*x + dc*y

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
    Specification: Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 22/02/17)
    """

    def convert(value):
        """
        round the value from float to int with specifical criterium.

        parameter
        ---------
        value: value to convert

        return
        ------
        1, -1, 0: Value after round.

        Version
        -------
        Specification: Bayron Mahy (v1. 11/02/2017)
    	Implementation: Nicolas Van Bossuyt (v1. 22/02/17)
        """
        if value > 0.25:
            return 1
        elif value < -0.25:
            return -1

        return 0

    return (convert(vector[0]), convert(vector[1]))

def do_moves(game_stats):
    """
    Apply move to ships.

    Parameters
    ----------
    game_stats: stats of the game (dic).

    Return
    ------
    game_stats: new stats of the game (dic).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Alisson Leist (v1. 20/02/17)
                    Nicolas Van Bosuuyt (v2. 23/02/17)
                    Nicolas Van Bossuyt (v3. 09/03/17)
    """
    for element in game_stats['ships']:
        # Get ship position.
        position = game_stats['ships'][element]['position']

        # Compute new position of the ship.
        move = (game_stats['ships'][element]['speed'] * game_stats['ships'][element]['direction'][0], game_stats['ships'][element]['speed'] * game_stats['ships'][element]['direction'][1])
        new_position = convert_coordinates((position[0] + move[0], position[1] + move[1]), game_stats['board_size'])

        # Move the ship.
        game_stats['board'][position].remove(element)
        game_stats['board'][new_position].append(element)
        game_stats['ships'][element]['position'] = new_position



    return game_stats

def take_abandonned_ship(game_stats):
    """
    Check on the board if an abandonned ship can be taken.

    Parameters
    ----------
    game_stats: stats of the game (dic).

    Returns
    -------
    game_stats: new stats of the game (dic).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Bayron Mahy (v1. 21/02/17)
                    Bayron Mahy (v2. 22/02/17)
                    Nicolas Van Bossuyt (v3. 09/03/17)
    """

    for location in game_stats['board']:
        ships = game_stats['board'][location]
        owners = []
        abandoned_ships = []

        if len(ships) >= 2:
            for ship in ships:
                ship_owner = game_stats['ships'][ship]['owner']
                if ship_owner == 'none':
                    abandoned_ships.append(ship)
                else:
                    owners.append(ship_owner)

        if len(owners) == 1:
            owner = owners[0]
            for ship in abandoned_ships:
                abandoned_ship = game_stats['ships'][ship].copy()

                # Remove the old ship.
                del game_stats['ships'][ship]
                game_stats['board'][abandoned_ship['position']].remove(ship)

                # Create the new one.
                abandoned_ship['owner'] = owner
                new_ship_name = "%s_%s" % (owner,ship)

                if new_ship_name in game_stats['ships']:
                    new_ship_name += '2'

                # Place the new ship on the game board.
                game_stats['board'][abandoned_ship['position']].append(new_ship_name)
                game_stats['ships'][new_ship_name] = abandoned_ship
                game_stats['players'][owner]['nb_ships'] += 1

                game_stats['game_logs'].append('%s as take %s !' % (owner, new_ship_name))
                game_stats['players'][owner]['fitness']+=65


    return game_stats

# Attack Command
# ------------------------------------------------------------------------------
# Allow ship to attack each other.

def command_attack(ship, ship_coordinate, target_coordinate, game_stats):
    """
    Determine if the attack works and do it.

    Parameters
    ----------
    ship_location: coodinate of the first ship (tuple(int, int)).
    coordinate: coordinate of the tile to attack (tuple(int,int)).
    game_stats: stats of the game (dic).

    Return
    ------
    game_stats: new stats of the game (dic).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
    Implementation: Alisson Leist (v1. 14/2/17)
                    Bayron Mahy, Alisson Leist (v2. 20/02/17)
    """
    ship_type = game_stats['model_ship'][game_stats['ships'][ship]['type']]
    damages = ship_type['damages']
    distance = get_distance(ship_coordinate, target_coordinate, game_stats['board_size'])

    if distance <= ship_type['range']:
        if len(game_stats['board'][target_coordinate]) != 0:
            game_stats['nb_rounds'] = 0
            # Give damages to all ship on targe coordinate.
            for target_ship in game_stats['board'][target_coordinate]:

                # Give damages to the taget ship.
                game_stats['ships'][target_ship]['heal_points'] -= damages

                if game_stats['ships'][target_ship]['heal_points'] <= 0:
					#tell to ai if that's a good action.
                    if game_stats['ships'][target_ship]['owner'] !=game_stats['ships'][ship]['owner']:
                        game_stat['players'][game_stats['ships'][ship]['owner']]['fitness']+=100
                    else:
                        game_stat['players'][game_stats['ships'][ship]['owner']]['fitness']-=100
                    # Remove the space ship.
                    game_stats['board'][target_coordinate].remove(target_ship)
                    game_stats['players'][game_stats['ships'][target_ship]['owner']]['nb_ships'] -=1
                    del game_stats['ships'][target_ship]

    return game_stats



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
    Implementation: Nicolas Van Bossuyt (v2. 15/02/2017)
    """
    # Split file lines and remove '\n' chars.
    cis_file = open(path,'r')
    file_content = [line.strip() for line in cis_file]
    cis_file.close()

    # Get the size of the gameboard.
    size_str = file_content[0].split(' ')
    size = (int(size_str[0]),int(size_str[1]))

    # Get lost space ship in the file..
    ships_list = []
    for line_index in range(len(file_content) - 1):
        try:
            ship_str = file_content[line_index + 1].split(' ')
            ship_name_and_type = ship_str[2].split(':')
            ship = (int(ship_str[0]), int(ship_str[1]), ship_name_and_type[0], ship_name_and_type[1], direction_to_vector2D(ship_str[3]))
            ships_list.append(ship)
        except:
            pass

    # Create parsed data dictionary and return it.
    parsed_data = {'size':size,'ships':ships_list}

    return parsed_data

def direction_to_vector2D(direction):
    """
    Convert a string direction to a vector2D.

    Parameter
    ---------
    direction: direction to convert <up|down|left|right|up-left|up-right|down-left|down-right>(str).

    Return
    ------
    vector: vector2D from direction (tuple(int, int)).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 11/02/17)
    """
    vector = ()

    if direction == 'up':
        vector = (0,1)

    elif direction == 'up-right':
        vector = (1,1)

    elif direction == 'right':
        vector = (1,0)

    elif direction == 'down-right':
        vector = (1,-1)

    elif direction == 'down':
        vector = (0,-1)

    elif direction == 'down-left':
        vector = (-1,-1)

    elif direction == 'left':
        vector = (-1,0)

    elif direction == 'up-left':
        vector = (-1,1)

    return vector

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
    ship_type = ['fighter', 'destroyer', 'battlecruiser']
    ship_direction = ['up', 'up-left', 'up-right', 'left', 'right', 'down', 'down-left', 'down-right']

    f = open(file_name, 'w')

    print >>f, "%d %d" % (board_size[0], board_size[1])

    for i in range(lost_ships_count):
        print >>f, '%d %d %s:%s %s' % (random.randint(0, board_size[0] - 1),\
        random.randint(0, board_size[1] - 1), 'ship_' + str(i),  ship_type[random.randint(0, len(ship_type) - 1)],\
        ship_direction[random.randint(0, len(ship_direction) - 1)])

    f.close()

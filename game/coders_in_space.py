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

from math import *
from time import sleep  # because everyone needs to rest.
from graphics import *
from remote_play import notify_remote_orders, get_remote_orders, connect_to_player, disconnect_from_player

# Game
# ==============================================================================
# Create a new game and play it.

def play_game(level_name, players_list, no_splash=False, no_gui=False, screen_size=(190, 50), distant_id=None,
              distant_ip=None, verbose_connection=False, max_rounds_count=10):
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
    game_data: game data at the end of the game (str).

    Note
    ----
    Recomanded screen_size: (190, 50).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Bayron Mahy, Nicolas Van Bossuyt (v1. 15/02/17)
    """
    # Create the new game.
    is_distant_game = (distant_id != None and distant_ip != None)

    if is_distant_game:
        game_data = new_game(level_name, players_list, connect_to_player(distant_id, distant_ip, verbose_connection))
    else:
        game_data = new_game(level_name, players_list)

    game_data['screen_size'] = screen_size
    game_data['max_nb_rounds'] = max_rounds_count

    # Show the splash screen.
    if not no_splash:
        show_splash_game(game_data)
        raw_input()  # wait the player pressing enter.

    is_ship_buy = True
    game_running = True
    # Game loop.
    while game_running:

        # Show the game board to the human player.
        if not no_gui:
            show_game_board(game_data)

        # Cleaning the pending_attack list.
        game_data['pending_attack'] = []

        # getting players input.
        for player in players_list:

            # Get current player input.
            if is_ship_buy:
                game_data = command_buy_ships(get_game_input(player, True, game_data), player, game_data)
            else:
                if game_data['players'][player]['nb_ships'] > 0:
                    p_input = get_game_input(player, False, game_data)
                    game_data = parse_command(p_input, player, game_data)
                elif game_data['players'][player]['type'] != 'none':
                    game_data['game_logs'].append(player + ' has lost all these ships, so he has nothing to do.')

        is_ship_buy = False

        # Do game loop.
        game_data = do_moves(game_data)
        game_data = take_abandonned_ship(game_data)
        game_data = do_attack(game_data)

        game_data['nb_rounds'] += 1
        game_running = is_game_continue(game_data)

    # Disconect the remote player.
    if is_distant_game:
        disconnect_from_player(game_data['players']['distant']['connection'])

    # Show the end game screen.
    if not no_splash:
        show_end_game(game_data)

    return game_data


def new_game(level_name, players_list, connection=None):
    """
    Create a new game from a '.cis' file.

    Parameters
    ----------
    level_name: name of the path to .cis file (str).
    players_list: list of players (list).
    (optional) connection: distant player connection (tuple).

    Return
    -------
    game_data: new game stats (dic).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
                    Bayron Mahy, Nicolas Van Bossuyt (v2. 13/02/17)
                    Nicolas Van Bossuyt (v3. 23/02/17)
    """
    # Create random a random game board.
    if level_name == 'random':
        create_game_board('board/random.cis', (40, 40), randint(0, 1000000))
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
                 'max_nb_rounds': 10,
                 'pending_attacks': [],
                 'game_logs': [],
                 'winners': [],
                 'is_remote_game': connection is not None}

    # Create ship specs sheet.
    game_data['model_ship']['fighter'] = {'icon': u'F', 'max_heal': 3, 'max_speed': 5, 'damages': 1, 'range': 5,
                                          'price': 10}
    game_data['model_ship']['destroyer'] = {'icon': u'D', 'max_heal': 8, 'max_speed': 2, 'damages': 2, 'range': 7,
                                            'price': 20}
    game_data['model_ship']['battlecruiser'] = {'icon': u'B', 'max_heal': 20, 'max_speed': 1, 'damages': 4, 'range': 10,
                                                'price': 30}
    # (here  we can define new spaceship type if you want).

    # Create the game board.
    for line in range(game_file['size'][0]):
        for column in range(game_data['board_size'][1]):
            game_data['board'][(line, column)] = []

    # Place lost ships.
    for ships in game_file['ships']:
        game_data['ships'][ships[2]] = {'type': ships[3], 'heal_points': game_data['model_ship'][ships[3]]['max_heal'],
                                        'direction': ships[4], 'speed': 0, 'owner': 'none',
                                        'position': (ships[0], ships[1])}
        game_data['board'][(ships[0], ships[1])].append(ships[2])

    index_player = 1

    for player in players_list:
        # Create new player.
        if index_player <= 4:
            game_data['players'][player] = {'name': player, 'money': 100, 'nb_ships': 0}

            # Set player type.
            if 'bot' in player or player == 'LAICIS':
                game_data['players'][player]['type'] = 'ai'
            elif 'dumb' in player:
                game_data['players'][player]['type'] = 'ai_dumb'
            elif player == 'distant':
                game_data['players'][player]['type'] = 'distant'
            else:
                game_data['players'][player]['type'] = 'human'

            # Set player starting pos.
            if index_player == 1:
                game_data['players'][player]['ships_starting_point'] = (9, 9)
                game_data['players'][player]['ships_starting_direction'] = (1, 1)
                game_data['players'][player]['color'] = 'red'

            elif index_player == 2:
                game_data['players'][player]['ships_starting_point'] = (
                game_data['board_size'][0] - 10, game_data['board_size'][1] - 10)
                game_data['players'][player]['ships_starting_direction'] = (-1, -1)
                game_data['players'][player]['color'] = 'blue'

            elif index_player == 3:
                game_data['players'][player]['ships_starting_point'] = (game_data['board_size'][0] - 10, 9)
                game_data['players'][player]['ships_starting_direction'] = (-1, 1)
                game_data['players'][player]['color'] = 'yellow'

            elif index_player == 4:
                game_data['players'][player]['ships_starting_point'] = (9, game_data['board_size'][1] - 10)
                game_data['players'][player]['ships_starting_direction'] = (1, -1)
                game_data['players'][player]['color'] = 'magenta'

        else:
            game_data['game_logs'].append(
                'There is too many player the player %s is a loser he must be watch you playing' % (player))

        index_player += 1

    if connection is not None:
        game_data['players']['distant']['connection'] = connection

    return game_data


def show_splash_game(game_data):
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

    screen_size = game_data['screen_size']
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

    screen_size = game_data['screen_size']

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
        # get input from the ai.
        if buy_ships:
            player_input = get_ai_spaceships(game_data, player_name)
        else:
            player_input = get_ai_input(game_data, player_name)

    elif player_type == 'ai_dumb':
        # Get input from the dumb ai.
        if buy_ships:
            player_input = get_dumb_ai_spaceships(player_name, game_data)
        else:
            player_input = get_dumb_ai_input(player_name, game_data)

    elif player_type == 'distant':
        # Get input from the distant player.
        player_input = get_distant_input(game_data)

    # Send the order to the remote player.
    if game_data['is_remote_game'] and (player_type == 'human' or player_type == 'ai' or player_type == 'ai_dumb'):
        notify_remote_orders(game_data['players']['distant']['connection'], player_input)

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
        # Show the game board to the human player.
        show_game_board(game_data)
        # Getting human player input.
        player_input = raw_input(set_color('\033[%d;%dH %s>' % (game_data['screen_size'][1], 3, player_name),
                                           game_data['players'][player_name]['color'], None))

        # Run human player command.
        if '/' in player_input:

            if player_input == '/ship-list':
                show_ship_list(player_name, game_data)
            else:
                print 'Wrong input'
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
    screen_size = game_data['screen_size']

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
                                           '[%s] %s // heal: %spv ~ speed: %skm/s ~ Facing: %s' % (
                                           game_data['model_ship'][ship['type']]['icon'], ship_name,
                                           ship['heal_points'], ship['speed'], str(ship['direction'])))
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


def show_game_board(game_data, hightlight_ship=None):
    """
    Show game board on the teminal.

    Parameter
    ---------
    game_data: data of the game (dic).
    (optional) hightlight_ship: ship to hightlight (str).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
                   Nicolas Van Bossuyt (v2. 19/03/17)

    Implementation: Nicolas Van Bossuyt (v0.1. 10/02/17)
                    - Initial Implementation
                    Nicolas Van Bossuyt (v0.2. 12/02/17)
                    - Add ship direction.
                    Nicolas Van Bossuyt (v0.3. 13/02/17)
                    - Add player panel.
                    Nicolas Van Bossuyt (v0.4. 19/02/17)
                    - Screen refresh.
                    Nicolas Van Bossuyt (v1.1. 23/02/17)
                    - Game log on screen.
                    Nicolas Van Bossuyt (v2.0. 01/03/17)
                    - Add Ship list.
                    Nicolas Van Bossuyt (v2.1. 19/03/17)
                    - Improve ship list.
    """
    screen_size = game_data['screen_size']

    # Create a the main canvas.
    c_screen = create_canvas(screen_size[0], screen_size[1])

    # Put a cool artwork on the background.
    c_screen = put_ascii_art(c_screen, 1, screen_size[1] - 30, 'planet')
    if (screen_size > 190):
        c_screen = put_ascii_art(c_screen, 191, screen_size[1] - 30, 'planet')
    c_screen = put_box(c_screen, 0, 0, screen_size[0], screen_size[1], 'single')

    # Create the board frame.
    # --------------------------------------------------------------------------
    game_board_size = (game_data['board_size'][0] * 3 + 5, game_data['board_size'][1] + 3)
    c_board = create_canvas(game_board_size[0], game_board_size[1])
    c_board = put_box(c_board, 0, 0, game_board_size[0], game_board_size[1])
    c_board = put_text(c_board, 2, 0, u'[ Game Board ]')
    c_board = put_stars_field(c_board, 1, 1, game_board_size[0] - 2, game_board_size[1] - 2, 1)

    # Put horizontal coordinate.
    coordinate_string = ''
    for i in range(1, game_data['board_size'][0] + 1):
        value_string = str(i)
        if len(value_string) == 1:
            value_string = ' ' + value_string
        value_string += ' '
        coordinate_string += value_string

    c_board = put_text(c_board, 4, 1, coordinate_string, 1, 0, 'grey', 'white')

    # Put vertical coordinate.
    for i in range(1, game_data['board_size'][1] + 1):
        value_string = str(i)
        if len(value_string) == 1:
            value_string = ' ' + value_string
        c_board = put_text(c_board, 1, i + 1, value_string + ' ', 1, 0, 'grey', 'white')

    # Put game board.
    for x in range(game_data['board_size'][0]):
        for y in range(game_data['board_size'][1]):
            on_screen_board_tile = (x * 3 + 4, y + 2)

            if len(game_data['board'][(x, y)]) == 1:
                # When there are one, show somme information about.
                ship_name = game_data['board'][(x, y)][0]
                ship_type = game_data['ships'][ship_name]['type']
                ship_icon = game_data['model_ship'][ship_type]['icon']
                ship_owner = game_data['ships'][ship_name]['owner']
                ship_owner_color = None

                # Print ship on gameboard.
                if game_data['ships'][ship_name]['owner'] != 'none':
                    ship_owner_color = game_data['players'][game_data['ships'][ship_name]['owner']]['color']

                ship_direction = game_data['ships'][ship_name]['direction']
                ship_speed = game_data['ships'][ship_name]['speed']

                # Put direction line.
                direction_char = '|'

                if ship_direction == (1, 1) or ship_direction == (-1, -1):
                    direction_char = '\\'
                elif ship_direction == (1, -1) or ship_direction == (-1, 1):
                    direction_char = '/'
                elif ship_direction == (1, 0) or ship_direction == (-1, 0):
                    direction_char = u'─'

                # Put the space sip in the gameboard.
                if ship_name == hightlight_ship:
                    c_board = put_text(c_board, on_screen_board_tile[0] + 1, on_screen_board_tile[1], ship_icon, 1, 0,
                                       ship_owner_color, 'yellow')
                else:
                    c_board = put_text(c_board, on_screen_board_tile[0] + 1, on_screen_board_tile[1], ship_icon, 1, 0,
                                       ship_owner_color)

                c_board = put_text(c_board, on_screen_board_tile[0] + 1 + ship_direction[0],
                                   on_screen_board_tile[1] + ship_direction[1], direction_char, 1, 0, ship_owner_color)

            elif len(game_data['board'][(x, y)]) > 0:
                # in other case show how many ship there are in the tile.
                c_board = put_text(c_board, on_screen_board_tile[0], on_screen_board_tile[1],
                                   '[%d]' % (len(game_data['board'][(x, y)])), 1, 0, 'green')

    game_board_location = (
    screen_size[0] / 2 - (c_board['size'][0] - 31) / 2, (screen_size[1] - 7) / 2 - c_board['size'][1] / 2)
    c_screen = put_canvas(c_screen, c_board, game_board_location[0], game_board_location[1])

    # Ships list
    # ---------------------------------------------------------------------------

    nb_ships = len(game_data['ships'])
    max_nb_ships = game_board_size[1] - 8
    c_ships = {}
    is_to_big = False

    print game_board_size[1];

    if (nb_ships) + 8 > game_board_size[1]:
        c_ships = create_canvas(30, game_board_size[1] - 5)
        is_to_big = True
    else:
        c_ships = create_canvas(30, nb_ships + 3)

    ship_index = 0
    for ship in game_data['ships']:
        if ship_index <= max_nb_ships:
            ship_data = game_data['ships'][ship]
            ship_name = ship
            ship_color = None

            if ship_data['owner'] != 'none':
                ship_color = game_data['players'][ship_data['owner']]['color']
                ship_name = ship_name.replace(ship_data['owner'] + '_', '')

            c_ships = put_text(c_ships, 1, ship_index + 2,
                               str("(%d, %d)" % (ship_data['position'][0] + 1, ship_data['position'][1] + 1)),
                               color=ship_color)
            c_ships = put_text(c_ships, 10, ship_index + 2, ship_name, color=ship_color)

        ship_index += 1

    c_ships = put_text(c_ships, 1, 1, ' X,  Y  | Name' + ' ' * 20, color='grey', back_color='white')

    if is_to_big:
        c_ships = put_box(c_ships, 0, 0, 30, game_board_size[1] - 5)
        c_ships = put_text(c_ships, 1, c_ships['size'][1] - 1, '...')
    else:
        c_ships = put_box(c_ships, 0, 0, 30, nb_ships + 3)

    c_ships = put_text(c_ships, 1, 0, '[ Ships ]')

    c_screen = put_canvas(c_screen, c_ships, game_board_location[0] - 31, game_board_location[1] + 5)

    # Game info
    # --------------------------------------------------------------------------
    c_info = create_canvas(30, 5)

    c_info = put_text(c_info, 1, 1, 'Board:')
    c_info = put_text(c_info, 8, 1, game_data['level_name'])

    c_info = put_text(c_info, 1, 2, 'Round:')
    c_info = put_text(c_info, 8, 2, '%s /%s' % (game_data['nb_rounds'], game_data['max_nb_rounds']))

    c_info = put_text(c_info, 1, 3, 'Ships:')
    c_info = put_text(c_info, 8, 3, str(len(game_data['ships'])))

    c_info = put_box(c_info, 0, 0, 30, 5)

    c_info = put_text(c_info, 1, 0, '[ Coders In Space ]')
    c_screen = put_canvas(c_screen, c_info, game_board_location[0] - 31, game_board_location[1])

    # Put players liste frame.
    # --------------------------------------------------------------------------
    players_bord_size = (len(game_data['players']) * 30 + 2, 7)
    players_bord_location = (0, screen_size[1] - 7)

    c_screen = put_box(c_screen, 0, players_bord_location[1], players_bord_size[0], players_bord_size[1])
    c_screen = put_text(c_screen, 1, players_bord_location[1], u'[ Players ]')

    # Put players list.
    player_count = 0
    for player in game_data['players']:
        if player != 'none':
            location = ((player_count * 30) + 1, players_bord_location[1] + 1,)
            c_screen = put_box(c_screen, location[0], location[1], 30, 5, 'single')

            # Put player informations.
            c_screen = put_text(c_screen, location[0] + 2, location[1],
                                '[ ' + game_data['players'][player]['name'] + ' ]',
                                color=game_data['players'][player]['color'])
            c_screen = put_text(c_screen, location[0] + 2, location[1] + 1,
                                'Type: ' + game_data['players'][player]['type'])
            c_screen = put_text(c_screen, location[0] + 2, location[1] + 2,
                                'Money: ' + str(game_data['players'][player]['money']))
            c_screen = put_text(c_screen, location[0] + 2, location[1] + 3,
                                'Spaceship count: ' + str(game_data['players'][player]['nb_ships']))

            player_count += 1

    # Put Game Logs frame.
    # --------------------------------------------------------------------------
    logs_size = (screen_size[0] - players_bord_size[0], 7)
    logs_location = (players_bord_size[0], screen_size[1] - 7)

    c_screen = put_box(c_screen, logs_location[0], logs_location[1], logs_size[0], logs_size[1])
    c_screen = put_text(c_screen, logs_location[0] + 1, logs_location[1], u'[ Game Logs ]')

    line_index = 1
    for line in game_data['game_logs'][-5:]:
        c_screen = put_text(c_screen, logs_location[0] + 1, logs_location[1] + line_index, line)
        line_index += 1

    # Show the game board in the terminal.
    print_canvas(c_screen)


# Remote player
# ------------------------------------------------------------------------------
# Handeling remote player command.
def get_distant_input(game_data):
    """
    Get input from a distant player.

    Parameter
    ---------
    game_data: data of the game (dic).

    Return
    ------
    remote_input: input from distant player (str).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
                     Nicolas Van Bossuyt (v2. 03/03/17)
    Implementation: Nicolas Van Bossuyt (v1. 03/03/17)
    """

    connection = game_data['players']['distant']['connection']
    return get_remote_orders(connection)


# A.I.
# ==============================================================================
# AI interactions

# L.A.I.C.I.S.
# ------------------------------------------------------------------------------
# [L]earning [A]rtificial [I]nteligence for [C]oders [I]n [S]pace.
def get_ai_input(game_data, player_name):
    """
    Get input from an AI player.

    Parameter
    ---------
    player_name: name of the player (str).
    game_data: state of the game (dic).

    Return
    ------
    ai_input: game input from AI (str).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 16/03/17)
    """

    action = ['faster', 'slower', 'left', 'right', 'attack']

    ai_input = ''

    for ship in game_data['ships']:
        if game_data['ships'][ship]['owner'] == player_name:
            ship_action = action[randint(0, len(action) - 1)]

            if ship_action == 'slower' or ship_action == 'faster':
                ship_action = speed(game_data, ship, ship_action)
            elif ship_action == 'attack':
                ship_action = attack(game_data, ship)

            ai_input += '%s:%s ' % (ship, ship_action)

    return ai_input[:-1].replace(player_name + '_', '')


def get_ai_spaceships(player_name, game_data):
    """
    Determine what ships to buy and turn it into a regulated command.

    Parameters
    ----------
    player_name: name of the player (str).
    game_data: state of the game (dic).

    Return
    ------
    ai_input: game input from AI (str).

    Version
    -------
    Specification: Nicolas Van Bossuyt (v1. 10/03/17)
                   Bayron Mahy (v2. 17/03/17)
    Implementation: Nicolas Van Bossuyt (v1. 10/03/17)
    """

    return 'arow:fighter stardestroyer:destroyer race_cruiser:battlecruiser'


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

    ship_pos = game_data['ships'][ship]['position']
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
            target_coords = convert_coordinates(
                (game_data['ships'][final_target]['position'][0], game_data['ships'][final_target]['position'][1]),
                game_data['board_size'])
            return '%d-%d' % (target_coords[0] + 1, target_coords[1] + 1)

    return ''


def predict_next_pos(game_data, ship_name):
    """
    Predict the next position of a space ship.

    Parameters
    ----------
    game_data: data of the game (dic).
    ship_name: name of the spaceship to predicte the next position (str).

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
    position = game_data['ships'][ship_name]['position']
    direction = game_data['ships'][ship_name]['direction']
    predicted_postion = convert_coordinates((position[0] + direction[0] * speed, position[1] + direction[1] * speed),
                                            game_data['board_size'])

    return predicted_postion


# D.A.I.C.I.S
# ------------------------------------------------------------------------------
# [D]umb [A]rtificial [I]nteligence for [C]oders [I]n [S]pace.
def get_dumb_ai_input(player_name, game_data, ):
    """
    Get input from an AI player.

    Parameter
    ---------
    player_name: name of the player (str).

    game_data: state of the game (dic).

    Return
    ------
    ai_input: game input from AI (str).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 16/03/17)
    """

    action = ['faster', 'slower', 'left', 'right']

    ai_input = ''

    for ship in game_data['ships']:
        if game_data['ships'][ship]['owner'] == player_name:
            ai_input += ship.replace(player_name + '_', '') + ':' + action[randint(0, len(action) - 1)] + ' '

    return ai_input[:-1]


def get_dumb_ai_spaceships(player_name, game_data):
    """
    Take random ships to make the army of the dumb AI

    Parameters
    ----------
    player_name: name of the player (str).

    game_data: state of the game (dic).

    Return
    ------
    ai_input: game input from AI (str).

    Version
    -------
    Specification: Nicolas Van Bossuyt (v1. 10/03/17)
    Implementation: Bayron Mahy (v1. 17/03/17)
    """

    ship_name_list = ['Apple-Pen', 'Akbar', 'amiral', 'bob', 'fob', 'I\'m_Bob_Lenon', 'Frenay-Acceleray', '',
                      'pew-pew-pew', 'Algobot', 'blblblblblblbl', 'Stack-overflow', 'mu', 'Seiyar', '25']
    ship_type_list = game_data['model_ship'].keys()

    money = 100
    army = ''

    while money > 0:
        ship_type = ship_type_list[randint(0, len(ship_type_list) - 1)]
        ship_name = ship_name_list[randint(0, len(ship_name_list) - 1)]

        if not ship_name in army:
            army += '%s:%s ' % (ship_name, ship_type)
            money -= game_data['model_ship'][ship_type]['price']

    return army[:-1]


# AI - command corection.
# ------------------------------------------------------------------------------
# Because nothing is perfect.
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
    ship_coords = ()
    ship_coords = game_data['ships'][target_ship]['position']
    x, y = 0, 0
    dx = 0
    dy = -1
    nearby_ships = []

    for i in range((search_range * 2) ** 2):
        if (-search_range < x <= search_range) and (-search_range < y <= search_range) and abs(x) + abs(
                y) <= search_range:

            coords = convert_coordinates((ship_coords[0] + x, ship_coords[1] + y), game_data['board_size'])

            if len(game_data['board'][coords]) > 0:
                nearby_ships.extend(game_data['board'][coords])

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
        """subbtract or add board size to coordinate depending on their position.

        Parameters
        ----------
        a: coordinate to convert (int).
        size: board size to add/sub (int).

        Return
        ------
        a: coordinate after convertion (int).

        Version
        -------
        Specification: Bayron Mahy (v1. 22/02/17)
        Implementation: Nicolas Van Bossuyt (v1. 10/03/17)
        """
        # Apply toric space.
        if a >= size:
            a -= size
        elif a < 0:
            a += size

        return a

    return (convert(coord[0], size[0]), convert(coord[1], size[1]))


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
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
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
                    attack_coords = ship_command.split('-')
                    if len(attack_coords) == 2:
                        attack_coords = (int(attack_coords[0]) - 1, int(attack_coords[1]) - 1)
                        game_data['pending_attacks'].append(
                            (ship_name, game_data['ships'][ship_name]['position'], attack_coords))

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
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 14/02/17)
                    Nicolas Van Bossuyt (v2. 23/02/17)
    """
    for ship in ships.split(' '):

        ship = ship.split(':')

        # Allow human player to dont have to write the full ship type name.
        if ship[1][0] == 'f':
            ship[1] = 'fighter'
        elif ship[1][0] == 'd':
            ship[1] = 'destroyer'
        elif ship[1][0] == 'b':
            ship[1] = 'battlecruiser'

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
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
    Implementation: Nicolas Van Bossuyt (v1. 15/02/17)
    """

    # Creatting the new space ship and add to the game_data.
    game_data['ships'][ship_name] = {'type': ship_type, 'heal_points': game_data['model_ship'][ship_type]['max_heal'],
                                     'direction': game_data['players'][player_name]['ships_starting_direction'],
                                     'speed': 0, 'owner': player_name,
                                     'position': game_data['players'][player_name]['ships_starting_point']}
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
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
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
        game_data['game_logs'].append('you cannot make that change on the speed of "' + ship + '"')

    return game_data


def command_rotate(ship, direction, game_data):
    """
    Rotate the ship.

    Parameters
    ----------
    ship: name of the ship to Increase the speed (str).
    direction: the direction to rotate the ship <"left"|"right">(str)
    game_data: data of the game (dic).

    Returns
    -------
    game_data: new data of the game (dic).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 10/02/17)
                    Nicolas Van Bossuyt (v2. 22/02/17)
    """
    v = (0, 0)
    if direction == 'left':
        v = rotate_vector_2d(game_data['ships'][ship]['direction'], -45)
    elif direction == 'right':
        v = rotate_vector_2d(game_data['ships'][ship]['direction'], 45)

    game_data['ships'][ship]['direction'] = to_unit_vector(v)
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
    Specification: Nicolas Van Bossuyt (v1. 10/02/17)
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
    Specification: Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 22/02/17)
    """

    def convert(value):
        """
        turn the float value into int with specifical criterium.

        parameter
        ---------
        value: value to convert

        return
        ------
        1, -1, 0: Value after round.

        Version
        -------
        Specification: Bayron Mahy (v1. 11/02/17)
        Implementation: Nicolas Van Bossuyt (v1. 22/02/17)
        """
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
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Alisson Leist (v1. 20/02/17)
                    Nicolas Van Bosuuyt (v2. 23/02/17)
                    Nicolas Van Bossuyt (v3. 09/03/17)
    """
    for ship in game_data['ships']:
        position = game_data['ships'][ship]['position']
        new_position = predict_next_pos(game_data, ship)

        # Move the ship.
        game_data['board'][position].remove(ship)
        game_data['board'][new_position].append(ship)
        game_data['ships'][ship]['position'] = new_position

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
                game_data['board'][abandoned_ship['position']].remove(ship)

                # Create the new one.
                abandoned_ship['owner'] = owner
                new_ship_name = "%s_%s" % (owner, ship)

                if new_ship_name in game_data['ships']:
                    new_ship_name += '2'

                # Place the new ship on the game board.
                game_data['board'][abandoned_ship['position']].append(new_ship_name)
                game_data['ships'][new_ship_name] = abandoned_ship
                game_data['players'][owner]['nb_ships'] += 1
                game_data['game_logs'].append('%s as take %s !' % (owner, new_ship_name))

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
                game_data['game_logs'].append('%s kill %s' % (ship, target_ship))

                # Remove the space ship.
                game_data['board'][target_coordinate].remove(target_ship)
                if game_data['ships'][target_ship]['owner'] != 'none':
                    game_data['players'][game_data['ships'][target_ship]['owner']]['nb_ships'] -= 1

                del game_data['ships'][target_ship]

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
    size = (int(size_str[0]), int(size_str[1]))

    # Get lost space ship in the file..
    ships_list = []
    for line_index in range(len(file_content) - 1):
        ship_str = file_content[line_index + 1].split(' ')
        if len(ship_str) == 4:
            ship_name_and_type = ship_str[2].split(':')
            ship = (int(ship_str[0]), int(ship_str[1]), ship_name_and_type[0], ship_name_and_type[1],
                    direction_to_vector2d(ship_str[3]))
            ships_list.append(ship)

    # Create parsed data dictionary and return it.
    parsed_data = {'size': size, 'ships': ships_list}

    return parsed_data


def direction_to_vector2d(direction):
    """
    Convert a string direction to a vector2d.

    Parameter
    ---------
    direction: direction to convert <up|down|left|right|up-left|up-right|down-left|down-right>(str).

    Return
    ------
    vector: vector2d from direction (tuple(int, int)).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 11/02/17)
    """
    vector = ()

    if direction == 'up':
        vector = (0, 1)

    elif direction == 'up-right':
        vector = (1, 1)

    elif direction == 'right':
        vector = (1, 0)

    elif direction == 'down-right':
        vector = (1, -1)

    elif direction == 'down':
        vector = (0, -1)

    elif direction == 'down-left':
        vector = (-1, -1)

    elif direction == 'left':
        vector = (-1, 0)

    elif direction == 'up-left':
        vector = (-1, 1)

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

    print >> f, "%d %d" % (board_size[0], board_size[1])

    for i in range(lost_ships_count):
        print >> f, '%d %d %s:%s %s' % (randint(0, board_size[0] - 1), randint(0, board_size[1] - 1), 'ship_' + str(i),
                                        ship_type[randint(0, len(ship_type) - 1)], \
                                        ship_direction[randint(0, len(ship_direction) - 1)])

    f.close()

if __name__ == '__main__':
    play_game('random', ('dumbInSpace', 'dumby', 'dumbo', 'botbot'), screen_size=(190, 50), no_gui=False, no_splash=False, max_rounds_count=100)

import colored
import random
import math
import remote_play


def start_game(config_name, player_one_type, player_two_type, player_id, opponent_ip='127.0.0.1'):
    """
    The main function to start the game.

    Parameters
    ----------
    config_name: the name of the file configuration (str)
    player_one_type: the type of the first player (str)
    player_two_type: the type of the second player (str)
    player_id: id of the player (int)
    opponent_ip: the ip of the opponent (str)

    Returns
    -------
    None

    Version
    -------
    specification: Thomas Blanchy (v.2 09/03/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    # All the data structures that will be used
    ships_type = {
        'Scout': {
            'size': 9,
            'life': 3,
            'attack': 1,
            'range': 3,
            'cost': 3
        },
        'Warship': {
            'size': 21,
            'life': 18,
            'attack': 3,
            'range': 5,
            'cost': 9
        },
        'Excavator-S': {
            'size': 1,
            'tonnage': 1,
            'life': 2,
            'cost': 1
        },
        'Excavator-M': {
            'size': 5,
            'tonnage': 4,
            'life': 3,
            'cost': 2
        },
        'Excavator-L': {
            'size': 9,
            'tonnage': 8,
            'life': 6,
            'cost': 4
        }
    }
    ships_structure = {
        'Scout': [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)],
        'Warship': [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1), (-2, -1), (-2, 0),
                    (-2, 1), (-1, 2), (0, 2), (1, 2), (2, 1), (2, 0), (2, -1), (1, -2), (0, -2), (-1, -2)],
        'Excavator-S': [(0, 0)],
        'Excavator-M': [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)],
        'Excavator-L': [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (2, 0), (0, 2), (-2, 0), (0, -2)]
    }
    game_board = {}
    ships_ingame = {}
    players = {}
    ia_target = {}
    max_round = 200

    # Load information from the config file
    info = load_file(config_name)
    game_board['size'] = load_size(info)
    game_board['portals'] = load_portals(info)
    game_board['asteroids'] = load_asteroids(info)
    game_board['empty_round_left'] = max_round
    game_board['total_round'] = 1
    game_board['total_ore_on_board'] = 0

    for asteroid in game_board['asteroids']:
        game_board['total_ore_on_board'] += asteroid['ore']

    # Create names for the players
    id_player = 0
    name_list = ['Thomas', 'Mathilde', 'Moussa', 'Elena', 'Cyril', 'Joaquim']
    for player in [player_one_type, player_two_type]:
        print('Random name for player %d ...' % id_player)
        id_player += 1
        name = random.choice(name_list)
        name_list.remove(name)
        if player == 'remote':
            name += '$'

        players[name] = {}
        players[name]['type'] = player  # Which type the player is (human, IA, remote)
        players[name]['ore'] = 4  # Each player starts with 4 ores
        players[name]['total_recolted'] = 0
        players[name]['ships'] = []  # List of ships the player owns

    no_damage_in_the_round = True

    # Connexion reseau
    connection = ''
    if 'remote' in [player_one_type, player_two_type]:
        connection = remote_play.connect_to_player(player_id, opponent_ip, True)

    while check_end_game(game_board, no_damage_in_the_round, max_round):
        new_orders = {
            'buy_orders': [],
            'lock_orders': [],
            'unlock_orders': [],
            'move_orders': [],
            'attack_orders': []
        }

        # 1 : notify puis get
        # 2 : get puis notify

        if player_id == 1:
            order_1 = ia(list(players.keys())[0], ia_target, game_board, players, ships_ingame, ships_type,
                         ships_structure)
            remote_play.notify_remote_orders(connection, order_1)
            order_2 = remote_play.get_remote_orders(connection)

            interpret_orders(new_orders, order_1, list(players.keys())[0], ships_type, players, ships_ingame,
                             game_board)
            interpret_orders(new_orders, order_2, list(players.keys())[1], ships_type, players, ships_ingame,
                             game_board)
        elif player_id == 2:
            order_1 = remote_play.get_remote_orders(connection)
            order_2 = ia(list(players.keys())[1], ia_target, game_board, players, ships_ingame, ships_type,
                         ships_structure)
            remote_play.notify_remote_orders(connection, order_2)

            interpret_orders(new_orders, order_1, list(players.keys())[0], ships_type, players, ships_ingame,
                             game_board)
            interpret_orders(new_orders, order_2, list(players.keys())[1], ships_type, players, ships_ingame,
                             game_board)

        # Buying Phase
        buy_ships(new_orders['buy_orders'], players, ships_ingame, ships_type, game_board)

        # Lock/Unlock Phase
        lock_ship(new_orders['lock_orders'], game_board, ships_ingame, players)
        unlock_ship(new_orders['unlock_orders'], game_board, ships_ingame, players)

        # Move Phase
        move_ship(new_orders['move_orders'], ships_ingame)

        # Attack Phase
        no_damage_in_the_round = \
            attack_ship(new_orders['attack_orders'], game_board, ships_ingame, ships_type, players, ships_structure)

        # Recolt Phase
        collect_ores(game_board, ships_ingame, players, ships_type)

        # Show board & information
        draw_board(game_board, ships_ingame, ships_structure, players)
        show_information(game_board, players, ships_ingame, False)
        game_board['total_round'] += 1

    end_game(players, game_board)
    print('Game Over!')


#
#   UI
#


def draw_board(info, ships, ships_structure, players):
    """
    Draw the game board and refresh every round.

    Parameters
    ----------
    info: the information of the game (dictionary)
    ships: the ships in game (dictionary)
    ships_structure: the structure of the ships (dictionary)
    players: the information of the players (dictionary)

    Returns
    -------
    None

    Version
    -------
    specification: Joaquim Peremans (v.1 05/03/2018)
    implementation: Joaquim Peremans (v.1 15/04/2018)
    """

    board = []
    build_empty_board(info, board)
    add_portals_to_board(board, info)
    add_ships_to_board(board, ships, ships_structure, players)
    add_asteroids_to_board(board, info)

    for row in board:
        for col in row:
            print(col, end=' ')
        print('')


def build_empty_board(info, board):
    """
    Build the empty board with the size and the length of the config.

    Parameters
    ----------
    info: all the information of the game (dictionary)
    board: the current game board (list)

    Returns
    -------
    None

    Version
    -------
    specification: Joaquim Peremans (v.1 15/04/2018)
    implementation: Joaquim Peremans (v.1 15/04/2018)
    """

    for i in range(info['size'][0]):
        sub_list = []
        for j in range(info['size'][1]):
            sub_list.append('\u2591')  # \u25A1
        board.append(sub_list)


def add_ships_to_board(board, ships, ships_structure, players):
    """
    Add the ships in game to the board.

    Parameters
    ----------
    board: the current game board (list)
    ships: the ships in game (dictionary)
    ships_structure: the structure of the ships (dictionary)
    players: the information of the players (dictionary)

    Returns
    -------
    None

    Version
    -------
    specification: Joaquim Peremans (v.1 05/03/2018)
    implementation: Joaquim Peremans (v.1 15/04/2018)
    """

    ship_colors = [1, 21]  # Colors of colored : 1=red, 21=blue
    for ship in ships:
        owner_index = list(players.keys()).index(get_player_from_ship(ship, players))
        color = colored.fg(ship_colors[owner_index])
        ship_c = ships[ship]['position'][0]
        ship_r = ships[ship]['position'][1]
        ship_type = ships[ship]['type']

        structure = ships_structure[ship_type]

        for pos in structure:  # \u25A0
            board[ship_c + int(pos[0]) - 1][ship_r + int(pos[1]) - 1] = color + '\u2588' + colored.attr('reset')


def add_asteroids_to_board(board, info):
    """
    Add the asteroids to the board.

    Parameters
    ----------
    board: the current game board (list)
    info: the data structure with the asteroids (dictionary)

    Returns
    -------
    None

    Version
    -------
    specification: Joaquim Peremans (v.1 05/03/2018)
    implementation: Joaquim Peremans (v.1 15/04/2018)
    """

    for asteroid in info['asteroids']:
        pos_r = asteroid['position'][0]
        pos_c = asteroid['position'][1]
        ore = asteroid['ore']
        color = colored.fg(2) if ore > 0.1 else colored.fg(15)  # Green if filled or white if empty
        board[int(pos_r) - 1][int(pos_c) - 1] = color + '\u25D8' + colored.attr('reset')


def add_portals_to_board(board, info):
    """
    Add the portals to the board.

    Parameters
    ----------
    board: the current game board (list)
    info: the data structure with the portals (dictionary)

    Returns
    -------
    None

    Version
    -------
    specification: Joaquim Peremans (v.1 05/03/2018)
    implementation: Joaquim Peremans (v.1 15/04/2018)
    """

    portal_colors = [174, 45]  # Colors of colored : 174=light_red, 45=light_blue
    for portal in info['portals']:
        portal_index = info['portals'].index(portal)
        color = colored.fg(portal_colors[portal_index])
        pos_r = portal['position'][0]
        pos_c = portal['position'][1]
        for i in range(-2, 3):
            for j in range(-2, 3):  # \u25CC
                board[int(pos_r) + i - 1][int(pos_c) + j - 1] = color + '\u2591' + colored.attr('reset')


def show_information(info, players, ships_ingame, minimal):
    """
    Display all the information of the game

    Parameters
    ----------
    info: the data structure with the asteroids and the portals (dictionary)
    players: the information of the players (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    minimal: if show the minimal version or not (bool)

    Returns
    -------
    None

    Version
    -------
    specification: Thomas Blanchy (v.1 23/04/2018)
    implementation: Thomas Blanchy (v.1 23/04/2018)
    """

    current_length = 81

    # Player name line
    name_line = '|%s:%s|' % ((' ' * 39), (' ' * 39))
    for player in players:
        ship_colors = [1, 21]
        owner_index = list(players.keys()).index(player)
        color = colored.fg(ship_colors[owner_index])
        player_name = color + player + colored.attr('reset')

        start = 0
        if list(players.keys()).index(player) == 1:
            start = (41 - len(player)) + len(player_name)

        name_length = len(player)
        start_index = start + int((((current_length - 3) / 2) - name_length) / 2)
        end_index = start_index + name_length
        name_line = name_line[:start_index] + player_name + name_line[end_index:]

    # Build ships info lines
    ships_lines = []
    current_index = 0
    len_player_ships = []
    for player in players:
        len_player_ships.append(len(players[player]['ships']))

    current_max = -1
    for value in len_player_ships:
        if value > current_max or current_max == -1:
            current_max = value

    while current_index < current_max:
        ship_info_line = '|'
        for player in players:
            if current_index < len(players[player]['ships']):
                ship = players[player]['ships'][current_index]
                ship_info = ships_ingame[ship]

                ship_type = str(ship_info['type'])
                if ship_type.startswith('E'):
                    ship_type = ship_type[0] + ship_type[-2:]
                else:
                    ship_type = ship_type[0]

                ship_pos = '(%d,%d)' % (ship_info['position'][0], ship_info['position'][1])

                ship_ore = ''
                if ship_type.startswith('E'):
                    ship_ore += '%.1f' % ship_info['ore']

                ship_info_line += ' %s | %s |%s| %s | %s :' % \
                                  (ship + (' ' * (9 - len(ship))),
                                   ship_type + (' ' * (4 - len(ship_type))),
                                   ship_pos + (' ' * (7 - len(ship_pos))),
                                   str(ship_info['life']) + (' ' * (4 - len(str(ship_info['life'])))),
                                   ship_ore + (' ' * (3 - len(ship_ore))))
            else:
                ship_info_line += '           |      |       |      |     :'

        ship_info_line = ship_info_line[:-1] + '|'
        ships_lines.append(ship_info_line)
        current_index += 1

    # Portal life line
    portal_line = '| '
    for portal in info['portals']:
        portal_side_length = 40
        p_life = portal['life']
        offset = 0
        if p_life < 10:
            offset = 2
        elif p_life < 100:
            offset = 1
        portal_line += 'Portal life : %d%s' % (p_life, ' ' * (portal_side_length - (19 - offset)))

        if info['portals'].index(portal) == 0:
            portal_line += ': '
        else:
            portal_line += '|'

    # Current Ore & Total Ore line
    ore_line = '| '
    total_recolted_line = '| '
    for player in players:
        ore_side_length = 40
        current_ore = players[player]['ore']
        total_recolted = players[player]['total_recolted']
        offset_ore = 0
        offset_recolted = 0

        if current_ore < 10:
            offset_ore = 2
        elif current_ore < 100:
            offset_ore = 1

        if total_recolted < 10:
            offset_recolted = 2
        elif total_recolted < 100:
            offset_recolted = 1

        ore_line += 'Current Ore : %d%s' % (current_ore, ' ' * (ore_side_length - (19 - offset_ore)))
        total_recolted_line += 'Total Recolted : %d%s' % \
                               (total_recolted, ' ' * (ore_side_length - (22 - offset_recolted)))

        if list(players.keys()).index(player) == 0:
            ore_line += ': '
            total_recolted_line += ': '
        else:
            ore_line += '|'
            total_recolted_line += '|'

    print('-' * current_length)
    print(name_line)
    print('[%s:%s]' % ('=' * 39, '=' * 39))
    print(portal_line)
    print(ore_line)
    print(total_recolted_line)
    print('[%s:%s]' % ('-' * 39, '-' * 39))
    if not minimal:
        print('| Name      | Type | Pos   | Life | Ore : Name      | Type | Pos   | Life | Ore |')
        for ship_line in ships_lines:
            print(ship_line)

    asteroid_lines = []
    for i in range(0, len(info['asteroids']), 6):
        asteroid_line = '|'
        for n in range(i, i + 6):
            if n < len(info['asteroids']):
                asteroid = info['asteroids'][n]
                asteroid_info = '(%d,%d): %d' % (asteroid['position'][0], asteroid['position'][1], asteroid['ore'])
                asteroid_line += ' %s%s |' % (asteroid_info, ' ' * (11 - len(asteroid_info)))
            else:
                asteroid_line += '             |'
        asteroid_lines.append(asteroid_line)

    ore_started = info['total_ore_on_board']
    current_ore = 0
    for asteroid in info['asteroids']:
        current_ore += asteroid['ore']
    ore_ratio = current_ore / ore_started

    asteroid_title = 'Asteroids - %.2f%s of Ore' % (ore_ratio * 100, '%')

    print('[%s]' % ('=' * 83))
    print('|%s%s%s|' % ((' ' * (int(math.floor((83 - len(asteroid_title)) / 2)))),
                        asteroid_title,
                        (' ' * (int(math.ceil((83 - len(asteroid_title)) / 2))))))
    print('[%s]' % ('-' * 83))
    for a_line in asteroid_lines:
        print(a_line)
    print('-' * 85)

#
#   Actions
#


def buy_ships(orders, players, ships_ingame, ships_type, info):
    """
    Add the new ships according to the orders.

    Parameters
    ----------
    orders: the buy orders of the round (list)
    players: the information of the players (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    ships_type: the features of the ships (dictionary)
    info: the data structure with the portals and the asteroids (dictionary)

    Returns
    -------
    None

    Version
    -------
    specification: Joaquim Peremans (v.1 05/03/2018)
    implementation: Joaquim Peremans (v.1 15/04/2018)
    """

    for order in orders:
        ship_name = order['order'].split(':')[0]
        ship_type = order['order'].split(':')[1][0].upper() + order['order'].split(':')[1][1:]

        # Remove ore from player bank
        price = ships_type[ship_type]['cost']
        players[order['player_name']]['ore'] = players[order['player_name']]['ore'] - price

        # Add to ships_ingame -> 'name': (type, position, life, if exca: ore)
        ships_ingame[ship_name] = {}
        ships_ingame[ship_name]['type'] = ship_type

        # Get the portal of the player
        player_portal = get_portal_from_player(order['player_name'], players, info)

        ships_ingame[ship_name]['position'] = [player_portal['position'][0], player_portal['position'][1]]
        ships_ingame[ship_name]['life'] = ships_type[ship_type]['life']

        if ship_type in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
            ships_ingame[ship_name]['ore'] = 0

        # Add to players -> 'name' to players[player_name]['ships']
        players[order['player_name']]['ships'].append(ship_name)


def move_ship(orders, ships_ingame):
    """
    Move the ship to the position (x,y)

    Parameters
    ----------
    orders: the move orders of the round (list)
    ships_ingame: the information of the ships on the board (dictionary)

    Returns
    -------
    None

    Version
    -------
    specification: Joaquim Peremans (v.1 05/03/2018)
    implementation: Joaquim Peremans (v.1 15/04/2018)
    """

    for order in orders:
        ship_name = order['order'].split(':')[0]
        new_position = order['order'].split(':')[1].replace('@', '')
        new_position = new_position.split('-')
        new_position = [int(new_position[0]), int(new_position[1])]
        ships_ingame[ship_name]['position'] = new_position


def attack_ship(orders, info, ships_ingame, ships_type, players, ships_structure):
    """
    Launch an attack based on the ship concerned.

    Parameters
    ----------
    orders: the attack orders of the round (list)
    info: the data structure with the portals and the asteroids (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    ships_type: the features of the ships (dictionary)
    players: the information of the players (dictionary)
    ships_structure: the structure of the ships (dictionary)

    Returns
    -------
    damage: if there was any damage done (bool)

    Version
    -------
    specification: Joaquim Peremans, Thomas Blanchy (v.2 20/04/2018)
    implementation: Joaquim Peremans, Thomas Blanchy (v.2 20/04/2018)
    """

    is_damage = False
    for order in orders:
        ship_name = order['order'].split(':')[0]
        target_pos = [int(order['order'].split(':')[1].split('-')[0].replace('*', '')),
                      int(order['order'].split(':')[1].split('-')[1])]

        # Check portal damage
        for portal in info['portals']:
            portal_structure = [(-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2),
                                (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2),
                                (0, -2), (0, -1), (0, 0), (0, 1), (0, 2),
                                (1, -2), (1, -1), (1, 0), (1, 1), (1, 2),
                                (2, -2), (2, -1), (2, 0), (2, 1), (2, 2)]

            for p_pos in portal_structure:
                portal_pos = portal['position']
                if target_pos[0] == portal_pos[0] + p_pos[0] and target_pos[1] == portal_pos[1] + p_pos[1]:
                    damage = ships_type[ships_ingame[ship_name]['type']]['attack']
                    if damage > portal['life']:
                        damage = portal['life']
                    portal['life'] -= damage
                    is_damage = True

        # Check ship damage
        for ship in ships_ingame:
            ship_structure = ships_structure[ships_ingame[ship]['type']]
            for s_ship in ship_structure:
                ship_pos = ships_ingame[ship]['position']
                if target_pos[0] == ship_pos[0] + s_ship[0] and target_pos[1] == ship_pos[1] + s_ship[1]:
                    damage = ships_type[ships_ingame[ship_name]['type']]['attack']
                    ships_ingame[ship]['life'] -= damage
                    is_damage = True

    # Remove dead ships
    for i in range(len(ships_ingame) - 1, -1, -1):
        ship = list(ships_ingame.keys())[i]
        if ships_ingame[ship]['life'] <= 0:
            del ships_ingame[ship]

            # Delete ships from locked ships on asteroids
            for asteroid in info['asteroids']:
                ships_locked = asteroid['ships_locked']
                if ship in ships_locked:
                    ships_locked.remove(ship)

            # Delete ships from locked ships on portals
            for portal in info['portals']:
                ships_locked = portal['ships_locked']
                if ship in ships_locked:
                    ships_locked.remove(ship)

            # Delete ships from players ships
            for player in players:
                if ship in players[player]['ships']:
                    players[player]['ships'].remove(ship)

    if is_damage:
        return False
    else:
        return True


def collect_ores(info, ships_ingame, players, ships_type):
    """
    Collect the ores from the asteroids locked by a ship and unload the ores in the portal if a ship is locked

    Parameters
    ----------
    info: the information of the game (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    players: the information of the players (dictionary)
    ships_type: the features of the ships (dictionary)

    Returns
    -------
    None

    Version
    -------
    specification: Thomas Blanchy (v.2 09/03/2018)
    implementation: Thomas Blanchy, Cyril Weber (v.1 15/04/2018)
    """

    # Collect ores from asteroids
    for asteroid in info['asteroids']:
        ships_locked = asteroid['ships_locked']
        if len(ships_locked) > 0:
            ores_left = asteroid['ore']  # Ores left to collect in the asteroid
            ores_rate = asteroid['rate']  # The rate of giving of the asteroid
            nb_ships = len(ships_locked)  # The number of ships locked to the asteroid

            max_ores = {}  # Data structure used to compute the number of ores to give to each ship

            # The part where we compute the max number of ores to give to a ship
            for ship in ships_locked:
                capacity = ships_type[ships_ingame[ship]['type']]['tonnage'] - ships_ingame[ship]['ore']
                # If the rate is greater than the capacity of the ship ...
                if ores_rate > capacity:
                    # ... we can only give the capacity of the ship
                    max_ores[ship] = capacity
                else:
                    # ... or we can give the rate of the asteroid because there is enough place
                    max_ores[ship] = ores_rate

            # The maximum number of ores to give to all the ships
            total_ores_to_give = 0
            for o in max_ores:
                total_ores_to_give += max_ores[o]

            # If the number of ores to give is less than what's left in the asteroid ...
            if total_ores_to_give < ores_left:
                for ship in ships_locked:
                    # ... we can give to each ship the max they can have
                    ships_ingame[ship]['ore'] += max_ores[ship]
                    asteroid['ore'] -= max_ores[ship]
            # The max number is greater than what's left in the asteroid -> we have to split
            else:
                new_ores_left = ores_left  # We save ores_left to modify it
                new_nb_ships = nb_ships  # We save nb_ships to modify it

                # While there are ores left in the asteroid
                while new_ores_left > 0.1:
                    # We compute the minimum of the ores the ships can collect
                    current_min = -1
                    for o in max_ores:
                        if max_ores[o] < current_min or current_min == -1:
                            current_min = max_ores[o]

                    # We multiply the min by the number of ships to see if we can give that min to all the ships
                    if current_min * nb_ships <= new_ores_left:
                        for ship in max_ores:
                            ships_ingame[ship]['ore'] += current_min  # We give the min to each ships
                            asteroid['ore'] -= current_min
                            new_ores_left -= current_min  # We subtract the min to see what's left to the asteroid
                            max_ores[ship] -= current_min  # We subtract the min to see what the ship can recolt
                    # If the min is greater to what the ships can recolt
                    else:
                        ores_to_give = new_ores_left / new_nb_ships
                        for ship in max_ores:
                            ships_ingame[ship]['ore'] += ores_to_give
                            asteroid['ore'] -= ores_to_give
                            new_ores_left -= ores_to_give
                            max_ores[ship] -= current_min

                    # We remove the full ships
                    new_max_ores = {}
                    for o in max_ores:
                        if max_ores[o] > 0:
                            new_max_ores[o] = max_ores[o]
                    new_nb_ships -= (len(max_ores.keys()) - len(new_max_ores.keys()))
                    max_ores = new_max_ores

    # Load ores to portals
    for portal in info['portals']:
        ships_locked = portal['ships_locked']
        for ship in ships_locked:
            if ships_ingame[ship]['ore'] > 0:
                for player in players:
                    if ship in players[player]['ships']:
                        players[player]['ore'] += ships_ingame[ship]['ore']
                        players[player]['total_recolted'] += ships_ingame[ship]['ore']
                        ships_ingame[ship]['ore'] = 0


def lock_ship(orders, info, ships_ingame, players):
    """
    Lock a ship to a certain position, asteroid or portal.

    Parameters
    ----------
    orders: the lock orders of the round (list)
    info: all the informatiin of the game (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    players: the information of the players (dictionary)

    Returns
    -------
    None

    Version
    -------
    specification: Thomas Blanchy (v.3 16/04/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    for order in orders:
        if order:
            ship_name = order['order'].split(':')[0]
            asteroid = get_asteroid_from_position(ships_ingame[ship_name]['position'], info)

            if asteroid:
                if ship_name not in asteroid['ships_locked']:
                    asteroid['ships_locked'].append(ship_name)
            else:
                owner = get_player_from_ship(ship_name, players)
                portal = get_portal_from_player(owner, players, info)
                if ships_ingame[ship_name]['position'] == portal['position']:
                    if ship_name not in portal['ships_locked']:
                        portal['ships_locked'].append(ship_name)


def unlock_ship(orders, info, ships_ingame, players):
    """
    Unlock a ship if it is locked to an asteroid or a portal.

    Parameters
    ----------
    orders: the unlock orders of the round (list)
    info: all the informatiin of the game (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    players: the information of the players (dictionary)

    Returns
    -------
    None

    Version
    -------
    specification: Thomas Blanchy (v.2 09/03/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    for order in orders:
        if order:
            ship_name = order['order'].split(':')[0]
            asteroid = get_asteroid_from_position(ships_ingame[ship_name]['position'], info)
            if asteroid:
                if ship_name in asteroid['ships_locked']:
                    asteroid['ships_locked'].remove(ship_name)
            else:
                owner = get_player_from_ship(ship_name, players)
                portal = get_portal_from_player(owner, players, info)
                if ships_ingame[ship_name]['position'] == portal['position']:
                    if ship_name in portal['ships_locked']:
                        portal['ships_locked'].remove(ship_name)


#
#   File loading
#


def load_file(config_name):
    """
    Get all the information in the game file.

    Parameters
    ----------
    config_name: the name of the config file (str)

    Returns
    -------
    info: the information of the game file (list)

    Version
    -------
    specification: Cyril Weber (v.1 03/03/2018)
    implementation: Cyril Weber (v.1 15/04/2018)
    """

    fh = open(config_name, 'r')
    info = fh.readlines()
    for line in info:
        info[info.index(line)] = line.replace('\n', '')
    fh.close()
    return info


def load_size(file_info):
    """
    Get the size of the board.

    Parameters
    ----------
    file_info: the information of the game file (list)

    Returns
    -------
    size: the size of the game board (list)

    Version
    -------
    specification: Cyril Weber (v.1 03/03/2018)
    implementation: Cyril Weber (v.1 15/04/2018)
    """

    coords = file_info[1].split(' ')
    size = [int(coords[0]), int(coords[1])]
    return size


def load_portals(file_info):
    """
    Get the portals of the game.

    Parameters
    ----------
    file_info: the information of the game file (list)

    Returns
    -------
    portals: the position of each portals (list)

    Version
    -------
    specification: Cyril Weber (v.1 03/03/2018)
    implementation: Cyril Weber (v.1 15/04/2018)
    """

    portals = file_info[file_info.index('portals:') + 1:file_info.index('asteroids:')]
    portals_pos = []
    for portal in portals:
        coords = portal.split(' ')
        portal_pos = {
            'position': [int(coords[0]), int(coords[1])],
            'life': 100,
            'ships_locked': []
        }
        portals_pos.append(portal_pos)
    return portals_pos


def load_asteroids(file_info):
    """
    Get all the asteroids in the game.

    Parameters
    ----------
    file_info: the information of the game file (list)

    Returns
    -------
    asteroids: all the asteroids (list)

    Version
    -------
    specification: Cyril Weber (v.1 03/03/2018)
    implementation: Cyril Weber (v.1 15/04/2018)
    """

    asteroids = file_info[file_info.index('asteroids:') + 1:]
    asteroids_info = []
    for asteroid in asteroids:
        infos = asteroid.split(' ')
        aster = {
            'position': [int(infos[0]), int(infos[1])],
            'ore': int(infos[2]),
            'rate': int(infos[3]),
            'ships_locked': []
        }
        asteroids_info.append(aster)
    return asteroids_info


#
#   Orders
#


def interpret_orders(new_orders, orders, player_name, ships_type, players, ships_ingame, info):
    """
    Get all the orders written by a player and translate them.

    Parameters
    ----------
    new_orders: the orders to make this round (dictionary)
    orders: the orders written by a player (str)
    player_name: the name of the player who did the order (str)
    ships_type: the types of the ships (dictionary)
    players: the information of the players (dictionary)
    ships_ingame: the ships currently on the board (dictionary)
    info: all the information of the game (dictionary)

    Returns
    -------
    None

    Version
    -------
    specification: Thomas Blanchy (v.1 03/03/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    if len(orders.strip()) > 0:
        all_orders = orders.strip().split(' ')
        for order in all_orders:
            order_name = order.split(':')[1]

            if order_name.startswith('@'):
                move_order = new_move_order(order, player_name, players, ships_ingame, info)

                if move_order:
                    new_orders['move_orders'].append(move_order)
            elif order_name.startswith('*'):
                attack_order = new_attack_order(order, player_name, players, ships_ingame, ships_type, info)

                if attack_order:
                    new_orders['attack_orders'].append(attack_order)
            elif order_name.startswith('release'):
                release_order = new_unlock_order(order, player_name, players, ships_ingame, info)

                if release_order:
                    new_orders['unlock_orders'].append(release_order)
            elif order_name.startswith('lock'):
                lock_order = new_lock_order(order, player_name, players, ships_ingame, info)

                if lock_order:
                    new_orders['lock_orders'].append(lock_order)
            elif (order_name[0].upper() + order_name[1:]) in ships_type.keys():
                buy_order = new_buy_order(order, player_name, ships_type, ships_ingame, players)

                if buy_order:
                    new_orders['buy_orders'].append(buy_order)
            else:
                print('Order not recognized')


def new_move_order(order, player_name, players, ships_ingame, info):
    """
    Insert a new move order.

    Parameters
    ----------
    order: the move order (str)
    player_name: the name of the player who did the order (str)
    players: the information of the players (dictionary)
    ships_ingame: the ships currently on the board (dictionary)
    info: all the information of the game (dictionary)

    Returns
    -------
    move_order: the new move order (dictionary)

    Version
    -------
    specification: Thomas Blanchy (v.2 01/04/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    # Extract the new position from the order
    ship_name = order.split(':')[0]
    new_position = order.split(':')[1].replace('@', '')
    new_position = new_position.split('-')
    new_position = [int(new_position[0]), int(new_position[1])]

    # Check if the player own the ship
    if ship_name in players[player_name]['ships']:
        # Check if the new pos next to the old one
        current_pos = ships_ingame[ship_name]['position']
        if abs(new_position[0] - current_pos[0]) <= 1 and abs(new_position[1] - current_pos[1]) <= 1:
            # Check if the new pos is in the board
            board_size = info['size']
            ship_radius = get_ship_radius(ships_ingame[ship_name]['type'])

            if new_position[0] - ship_radius > 0 or new_position[1] - ship_radius > 0 \
                    or new_position[0] + ship_radius > board_size[0] or new_position[1] + ship_radius > board_size[1]:

                new_order = {
                    'order': order,
                    'player_name': player_name
                }

                return new_order


def new_attack_order(order, player_name, players, ships_ingame, ships_type, info):
    """
    Insert a new attack order.

    Parameters
    ----------
    order: the attack order (str)
    player_name: the name of the player who did the order (str)
    players: the information of the players (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    ships_type: the features of the ships (dictionary)
    info: the data structure with the portails and the asteroids (dictionary)

    Returns
    -------
    attack_order: the new attack order (dictionary)

    Version
    -------
    specification: Thomas Blanchy (v.1 03/03/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    # order is type : ship_name:*r-c
    ship_name = order.split(':')[0]
    target_pos = [int(order.split(':')[1].split('-')[0].replace('*', '')), int(order.split(':')[1].split('-')[1])]

    # Check in board
    if target_pos[0] >= 1 and target_pos[1] >= 1:
        if target_pos[0] <= info['size'][0] and target_pos[1] <= info['size'][1]:
            # Check property
            if ship_name in players[player_name]['ships']:
                # Check Range
                if check_range(ship_name, [target_pos[0], target_pos[1]], ships_ingame, ships_type):
                    # Check ship type
                    if ships_ingame[ship_name]['type'] in ['Scout', 'Warship']:
                        new_order = {
                            'order': order,
                            'player_name': player_name
                        }

                        return new_order


def new_buy_order(order, player_name, ships_type, ships_ingame, players):
    """
    Insert a new buy order.

    Parameters
    ----------
    order: the buy order (str)
    player_name: the name of the player who did the order (str)
    ships_type: the types of the ships (dictionary)
    ships_ingame: the ships currently on the board (dictionary)
    players: the information of the players (dictionary)

    Returns
    -------
    buy_order: the new buy order (dictionary)

    Version
    -------
    specification: Thomas Blanchy (v.1 03/03/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    ship_name = order.split(':')[0]
    ship_type = order.split(':')[1][0].upper() + order.split(':')[1][1:]

    price = ships_type[ship_type]['cost']
    money_in_bank = players[player_name]['ore']

    if money_in_bank >= price:  # Check if enough money in the bank
        if ship_name not in ships_ingame.keys():
            new_order = {
                'order': order,
                'player_name': player_name
            }

            return new_order


def new_lock_order(order, player_name, players, ships_ingame, info):
    """
    Register a new order with the name of the ship to lock

    Parameters
    ----------
    order: the order containing the name of the ship to lock (str)
    player_name: the name of the player who did the order (str)
    players: the information of the players (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    info: the data structure with the asteroids and the portals (dictionary)

    Returns
    -------
    order: the new lock order (dictionary)

    Version
    -------
    specification: Thomas Blanchy (v.1 03/03/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    ship_name = order.split(':')[0]

    # Check if own the ship
    if ship_name in players[player_name]['ships']:
        ship_pos = ships_ingame[ship_name]['position']

        # Check if it is an Excavator
        if ships_ingame[ship_name]['type'] in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
            for asteroid in info['asteroids']:
                if asteroid['position'] == ship_pos:
                    if ship_name not in asteroid['ships_locked']:
                        new_order = {
                            'order': order,
                            'player_name': player_name
                        }

                        return new_order

            for portal in info['portals']:
                if portal['position'] == ship_pos:
                    if ship_name not in portal['ships_locked']:
                        new_order = {
                            'order': order,
                            'player_name': player_name
                        }

                        return new_order


def new_unlock_order(order, player_name, players, ships_ingame, info):
    """
    Register a new order with the name of the ship to unlock

    Parameters
    ----------
    order: the order containing the name of the ship to unlock (str)
    player_name: the name of the player who did the order (str)
    players: the information of the players (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    info: the data structure of the asteroids and the portals (dictionary)

    Returns
    -------
    order: the new order (dictionary)

    Version
    -------
    specification: Thomas Blanchy (v.1 03/03/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    ship_name = order.split(':')[0]

    # Check if own the ship
    if ship_name in players[player_name]['ships']:
        ship_pos = ships_ingame[ship_name]['position']

        # Check if it is an Excavator
        if ships_ingame[ship_name]['type'] in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
            for asteroid in info['asteroids']:
                if asteroid['position'] == ship_pos:
                    if ship_name in asteroid['ships_locked']:
                        new_order = {
                            'order': order,
                            'player_name': player_name
                        }

                        return new_order

            for portal in info['portals']:
                if portal['position'] == ship_pos:
                    if ship_name in portal['ships_locked']:
                        new_order = {
                            'order': order,
                            'player_name': player_name
                        }

                        return new_order


#
#   End Game
#


def check_end_game(info, damage, max_round):
    """
    Check if a portal is destroyed or no damage has been done for 20 turns.

    Parameters
    ----------
    info: all the information of the game (dictionary)
    damage: if there was any damage on the round (bool)
    max_round: the maximum of rounds without damage (int)

    Returns
    -------
    ended: if the game is ended (bool)

    Version
    -------
    specification: Cyril Weber, Thomas Blanchy (v.3 16/05/2018)
    implementation: Cyril Weber, Thomas Blanchy (v.2 16/05/2018)
    """

    if damage:
        info['empty_round_left'] -= 1
    else:
        info['empty_round_left'] = max_round
    if info['empty_round_left'] == 0:
        return False
    for portal in info['portals']:
        if portal['life'] <= 0:
            return False
    return True


def end_game(players, info):
    """
    Make the steps to end the game, write the winner.

    Parameters
    ----------
    players: the information of the players (dictionary)
    info: the data structure with the portals and the asteroids (dictionary)

    Returns
    -------
    None

    Version
    -------
    specification: Cyril Weber (v.1 04/03/2018)
    implementation: Cyril Weber (v.1 15/04/2018)
    """

    print('%s won the game!' % get_winner(players, info))


def get_winner(players, info):
    """
    Returns the winner's name of the game according to the damage and the ore.

    Parameters
    ----------
    players: the information of the players (dictionary)
    info: the data structure with the portals and the asteroids (dictionary)

    Returns
    -------
    winner: the name of the winner (str)

    Version
    -------
    specification: Cyril Weber (v.1 04/03/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    portals_life = []
    # We save the life of all the portals
    for portal in info['portals']:
        portals_life.append(portal['life'])

    total_ores_recolted = []
    # We save the total recolted ores of all players
    for player in players:
        total_ores_recolted.append(players[player]['total_recolted'])

    current_max_portal_life = -100
    nb_max = 0

    # We check the highest value in the life of the portals
    for n in portals_life:
        if n > current_max_portal_life or current_max_portal_life == -100:
            current_max_portal_life = n
            nb_max = 1
        elif current_max_portal_life == n:
            nb_max += 1

    # If there is only one portal with the highest life value ...
    if nb_max == 1:
        for player in players:
            # ... We check for all player if their portal has the highest life value
            if get_portal_from_player(player, players, info)['life'] == current_max_portal_life:
                return player
    # If their are at least 2 portals with the same highest life ...
    else:
        current_max_ores = -100
        nb_max_ores = 0

        # ... We check the highest value in the total recolted ores
        for j in total_ores_recolted:
            if j > current_max_ores or current_max_ores == -100:
                current_max_ores = j
                nb_max_ores = 1
            elif current_max_ores == j:
                nb_max_ores += 1

        # If there is only one player with the highest value of total recolted ores ...
        if nb_max_ores == 1:
            for player in players:
                # ... We check for all players who has the highest value of total recolted ores
                if players[player]['total_recolted'] == current_max_ores:
                    return player
            else:
                return 'Nobody'


#
#   IA Functions
#

def ia(name, targets, info, players, ships_ingame, ships_type, ships_structure):

    orders = []

    # Lock orders to an asteroid
    for asteroid in info['asteroids']:
        for ship in players[name]['ships']:
            if ships_ingame[ship]['type'] in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
                stock = ships_type[ships_ingame[ship]['type']]['tonnage'] - ships_ingame[ship]['ore']
                if asteroid['position'] == ships_ingame[ship]['position'] and stock > 0:
                    if asteroid['ore'] > 0.01:
                        if ship not in asteroid['ships_locked']:
                            orders.append('%s:lock' % ship)

    # Lock orders to a portal
    for portal in info['portals']:
        for ship in players[name]['ships']:
            if ships_ingame[ship]['type'] in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
                if portal['position'] == ships_ingame[ship]['position'] and ships_ingame[ship]['ore'] > 0:
                    if ship not in portal['ships_locked']:
                        orders.append('%s:lock' % ship)

    # Unlock orders from an asteroid
    # -> for every enemy ship : if dist(enemy, ship) <= range(enemy) + 1 -> unlock
    for asteroid in info['asteroids']:
        for ship in asteroid['ships_locked']:
            if ship in players[name]['ships']:
                if ships_ingame[ship]['ore'] == ships_type[ships_ingame[ship]['type']]['tonnage'] \
                        or asteroid['ore'] < 0.1:
                    orders.append('%s:release' % ship)

    # Unlock orders from a portal
    for portal in info['portals']:
        for ship in portal['ships_locked']:
            if ship in players[name]['ships']:
                if ships_ingame[ship]['ore'] == 0:
                    orders.append('%s:release' % ship)

    # Buy orders
    player_ore = players[name]['ore']
    if not players[name]['ships'] and player_ore == 4:
        orders.append('%s#%d:excavator-M' % (name[:3], random.randint(0, 999)))
        orders.append('%s#%d:excavator-M' % (name[:3], random.randint(0, 999)))
    else:
        types_to_buy = []
        can_buy = True

        nb_s, nb_m, nb_l, nb_scout, nb_warship = 0, 0, 0, 0, 0  # Max: nb_s=6 nb_m=4 nb_l=2
        for p_ship in players[name]['ships']:
            if ships_ingame[p_ship]['type'] == 'Excavator-S':
                nb_s += 1
            elif ships_ingame[p_ship]['type'] == 'Excavator-M':
                nb_m += 1
            elif ships_ingame[p_ship]['type'] == 'Excavator-L':
                nb_l += 1
            elif ships_ingame[p_ship]['type'] == 'Scout':
                nb_scout += 1
            elif ships_ingame[p_ship]['type'] == 'Warship':
                nb_warship += 1

        enemy_scout, enemy_warship = 0, 0
        player_index = list(players.keys()).index(name)
        enemy_player = list(players.keys())[abs(player_index - 1)]
        for enemy_ship in players[enemy_player]['ships']:
            if ships_ingame[enemy_ship]['type'] == 'Scout':
                enemy_scout += 1
            elif ships_ingame[enemy_ship]['type'] == 'Warship':
                enemy_warship += 1

        while can_buy and player_ore > 0:
            if nb_s == 4 and nb_m == 2 and nb_l == 2:
                if enemy_warship + 1 > nb_warship and player_ore >= ships_type['Warship']['cost']:
                    # Buy warship
                    types_to_buy.append('warship')
                    player_ore -= ships_type['Warship']['cost']
                    nb_warship += 1
                elif enemy_scout + 2 > nb_scout and player_ore >= ships_type['Scout']['cost']:
                    # Buy Scout
                    types_to_buy.append('scout')
                    player_ore -= ships_type['Scout']['cost']
                    nb_scout += 1
                else:
                    can_buy = False
            else:
                if info['total_round'] % 2 == 0:
                    if enemy_warship + 2 > nb_warship and player_ore >= ships_type['Warship']['cost']:
                        # Buy warship
                        types_to_buy.append('warship')
                        player_ore -= ships_type['Warship']['cost']
                        nb_warship += 1
                    elif enemy_scout + 1 > nb_scout and player_ore >= ships_type['Scout']['cost']:
                        # Buy Scout
                        types_to_buy.append('scout')
                        player_ore -= ships_type['Scout']['cost']
                        nb_scout += 1
                    elif nb_s < 4 and player_ore >= ships_type['Excavator-S']['cost']:
                        types_to_buy.append('excavator-S')
                        player_ore -= ships_type['Excavator-S']['cost']
                        nb_s += 1
                    elif nb_m < 2 and player_ore >= ships_type['Excavator-M']['cost']:
                        types_to_buy.append('excavator-M')
                        player_ore -= ships_type['Excavator-M']['cost']
                        nb_m += 1
                    elif nb_l < 2 and player_ore >= ships_type['Excavator-L']['cost']:
                        types_to_buy.append('excavator-L')
                        player_ore -= ships_type['Excavator-L']['cost']
                        nb_l += 1
                    else:
                        can_buy = False
                else:
                    if nb_s < 4 and player_ore >= ships_type['Excavator-S']['cost']:
                        types_to_buy.append('excavator-S')
                        player_ore -= ships_type['Excavator-S']['cost']
                        nb_s += 1
                    elif nb_m < 2 and player_ore >= ships_type['Excavator-M']['cost']:
                        types_to_buy.append('excavator-M')
                        player_ore -= ships_type['Excavator-M']['cost']
                        nb_m += 1
                    elif nb_l < 2 and player_ore >= ships_type['Excavator-L']['cost']:
                        types_to_buy.append('excavator-L')
                        player_ore -= ships_type['Excavator-L']['cost']
                        nb_l += 1
                    elif enemy_warship + 2 > nb_warship and player_ore >= ships_type['Warship']['cost']:
                        # Buy warship
                        types_to_buy.append('warship')
                        player_ore -= ships_type['Warship']['cost']
                        nb_warship += 1
                    elif enemy_scout + 1 > nb_scout and player_ore >= ships_type['Scout']['cost']:
                        # Buy Scout
                        types_to_buy.append('scout')
                        player_ore -= ships_type['Scout']['cost']
                        nb_scout += 1
                    else:
                        can_buy = False

        for type_buy in types_to_buy:
            ship_name = '%s#%d' % (name[:3], random.randint(0, 999))
            orders.append('%s:%s' % (ship_name, type_buy))

    # Update all ships target to know where to move and where to attack
    for player_ship in players[name]['ships']:
        set_ship_target(name, [player_ship, ships_ingame[player_ship]['type']],
                        targets, info, players, ships_ingame, ships_type)

    attack_this_round = []
    # Attack orders
    for ship in players[name]['ships']:
        if ships_ingame[ship]['type'] in ['Scout', 'Warship']:
            player_index = list(players.keys()).index(name)
            enemy_player = list(players.keys())[abs(player_index - 1)]

            # Handle attack other ships
            pos_to_attack = []
            for enemy_ship in players[enemy_player]['ships']:
                ship_structure = []
                for enemy_ship_structure in ships_structure[ships_ingame[enemy_ship]['type']]:
                    ship_structure.append([ships_ingame[enemy_ship]['position'][0] + enemy_ship_structure[0],
                                           ships_ingame[enemy_ship]['position'][1] + enemy_ship_structure[1]])

                for enemy_ship_structure in ship_structure:
                    if check_range(ship, enemy_ship_structure, ships_ingame, ships_type):
                        pos_to_attack.append([enemy_ship_structure[0], enemy_ship_structure[1]])

            # Handle attack enemy portal
            enemy_portal = get_portal_from_player(enemy_player, players, info)
            portal_structure = [(-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2),
                                (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2),
                                (0, -2), (0, -1), (0, 0), (0, 1), (0, 2),
                                (1, -2), (1, -1), (1, 0), (1, 1), (1, 2),
                                (2, -2), (2, -1), (2, 0), (2, 1), (2, 2)]

            portal_pos_to_attack = []
            for portal_element in portal_structure:
                r_pos = enemy_portal['position'][0] + portal_element[0]
                c_pos = enemy_portal['position'][1] + portal_element[1]

                if check_range(ship, [r_pos, c_pos], ships_ingame, ships_type):
                    portal_pos_to_attack.append([r_pos, c_pos])

            all_pos = pos_to_attack.copy()
            all_pos.extend(portal_pos_to_attack)
            attacked = False

            for attack_pos in all_pos:
                if attack_pos in portal_pos_to_attack and attack_pos in pos_to_attack \
                        and not check_friendly_ship(name, attack_pos, players, ships_ingame):
                    if not attacked:
                        orders.append('%s:*%d-%d' % (ship, attack_pos[0], attack_pos[1]))
                        attacked = True
                        attack_this_round.append(ship)

            if not attacked:
                for attack_pos in all_pos:
                    if attack_pos in portal_pos_to_attack \
                            and not check_friendly_ship(name, attack_pos, players, ships_ingame):
                        if not attacked:
                            orders.append('%s:*%d-%d' % (ship, attack_pos[0], attack_pos[1]))
                            attacked = True
                            attack_this_round.append(ship)

            if not attacked:
                for attack_pos in all_pos:
                    if attack_pos in pos_to_attack \
                            and not check_friendly_ship(name, attack_pos, players, ships_ingame):
                        if not attacked:
                            orders.append('%s:*%d-%d' % (ship, attack_pos[0], attack_pos[1]))
                            attacked = True
                            attack_this_round.append(ship)

    # Move orders
    current_ore = 0
    for asteroid in info['asteroids']:
        current_ore += asteroid['ore']

    for ship in players[name]['ships']:
        if ship not in attack_this_round:
            current_pos = ships_ingame[ship]['position']
            target_position = targets[ship]
            current_ore = 0
            for asteroid in info['asteroids']:
                current_ore += asteroid['ore']

            ship_type = ships_ingame[ship]['type']
            r_delta = target_position[0] - ships_ingame[ship]['position'][0]
            c_delta = target_position[1] - ships_ingame[ship]['position'][1]

            # --- Apply movement to the target
            if not check_range(ship, target_position, ships_ingame, ships_type) \
                    or ship_type in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
                r_move = 0 if target_position[0] == current_pos[0] else r_delta / abs(r_delta)
                c_move = 0 if target_position[1] == current_pos[1] else c_delta / abs(c_delta)

                new_pos_r = current_pos[0] + r_move
                new_pos_c = current_pos[1] + c_move
                orders.append('%s:@%d-%d' % (ship, new_pos_r, new_pos_c))

    return ' '.join(orders)


def set_ship_target(owner_name, ship, targets, info, players, ships_ingame, ships_type):
    """
    Set target of a Scout according to the best asteroids

    Parameters
    ----------
    owner_name: the name of the player who own the Scout (str)
    ship: the name and the type of the ship (tuple)
    targets: the current targets of the Scout on the board (dictionary)
    info: the information of the asteroids on the board (dictionary)
    players: the information of the players (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    ships_type: the features of all the types of ship (dictionary)

    Returns
    -------
    None

    Version
    -------
    specification: Thomas Blanchy
    implementation: Thomas Blanchy
    """

    ore_started = info['total_ore_on_board']
    current_ore = 0
    for asteroid in info['asteroids']:
        current_ore += asteroid['ore']
    ore_ratio = current_ore / ore_started

    if ships_ingame[ship[0]]['type'] == 'Scout':
        # Check if enemy extractor left to avoid targeting asteroids if nobody comes to recolt
        extractor_left = False
        player_index = list(players.keys()).index(owner_name)
        enemy_player = list(players.keys())[abs(player_index - 1)]
        enemy_portal = info['portals'][abs(player_index - 1)]
        for enemy_ship in players[enemy_player]['ships']:
            if ships_ingame[enemy_ship]['type'].startswith('Excavator'):
                extractor_left = True

        if enemy_close(ship[0], players, ships_ingame, ships_type):
            enemy_s = enemy_close(ship[0], players, ships_ingame, ships_type)
            targets[ship[0]] = ships_ingame[enemy_s]['position']
        elif ore_ratio > 0.1 and extractor_left:  # Still some ore left -> Target ships on asteroids
            if ship[0] in targets:
                for asteroid in info['asteroids']:
                    if asteroid['position'][0] == targets[ship[0]][0] \
                            and asteroid['position'][1] == targets[ship[0]][1]:
                        if asteroid['ore'] < 0.1:
                            # Find best asteroid to attack
                            best_asteroid = dict(find_best_asteroid_to_attack(owner_name, info, targets, players))
                            targets[ship[0]] = [best_asteroid['position'][0], best_asteroid['position'][1]]
            else:
                # Find best asteroid to attack
                best_asteroid = get_closest_asteroid(info, enemy_portal['position'])
                targets[ship[0]] = [best_asteroid['position'][0], best_asteroid['position'][1]]
        else:  # -> Target enemy portal as there is not any ore left
            targets[ship[0]] = [enemy_portal['position'][0], enemy_portal['position'][1]]
    elif ships_ingame[ship[0]]['type'] == 'Warship':
        # Always target enemy portal
        for player in players:
            if ship[0] not in players[player]['ships']:
                portal = get_portal_from_player(player, players, info)
                targets[ship[0]] = [portal['position'][0], portal['position'][1]]
    else:
        # Excavator : target closest asteroid
        space_left = ships_type[ships_ingame[ship[0]]['type']]['tonnage'] - ships_ingame[ship[0]]['ore']
        if space_left > 0.01 and current_ore > 0.01:
            closest_asteroid = get_closest_asteroid(info, ships_ingame[ship[0]]['position'])
            targets[ship[0]] = [closest_asteroid['position'][0], closest_asteroid['position'][1]]
        else:
            owner_name = get_player_from_ship(ship[0], players)
            portal_pos = get_portal_from_player(owner_name, players, info)
            targets[ship[0]] = [portal_pos['position'][0], portal_pos['position'][1]]


def find_best_asteroid_to_attack(player, info, targets, players):
    """
    Find the best asteroid with the max ores and who's not targeted yet.

    Parameters
    ----------
    player: the name of the attacker (str)
    info: the information of the elements on the board (dictionary)
    targets: the current targets of the ships (dictionary)
    players: the information of the players (dictionary)

    Returns
    -------
    asteroid: the best asteroid (dictionary)

    Version
    -------
    specification: Thomas Blanchy
    implementation: Thomas Blanchy
    """

    current_max = -1
    best_asteroid = ''

    new_list_asteroids = []
    if len(targets) > 0:
        for asteroid in info['asteroids']:
            a_pos = asteroid['position']
            can_be_targeted = True
            for target in targets:
                t_pos = targets[target]
                if t_pos[0] == a_pos[0] and t_pos[1] == a_pos[1] and target in players[player]['ships']:
                    can_be_targeted = False
            if can_be_targeted:
                new_list_asteroids.append(asteroid)
    else:
        new_list_asteroids = info['asteroids']

    for asteroid in new_list_asteroids:
        if asteroid['ore'] > current_max or asteroid['ore'] == -1:
            current_max = asteroid['ore']
            best_asteroid = asteroid
    return best_asteroid


def check_friendly_ship(player_name, position, players, ships_ingame):
    """
    Check whether or not there is a ship at the position.

    Parameters
    ----------
    player_name: the name of the player (str)
    position: the position targeted (list)
    players: the information of the players (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)

    Returns
    -------
    ship: whether there is a friendly ship or not (bool)

    Version
    -------
    specification: Thomas Blanchy (v.1 16/05/2018)
    implementation: Thomas Blanchy (v.1 16/05/2018)
    """

    for ship in players[player_name]['ships']:
        if position == ships_ingame[ship]['position']:
            return True
    return False


def enemy_close(ship_name, players, ships_ingame, ships_type):
    """
    Check if there is any enemy attack ship close to a certain ship.

    Parameters
    ----------
    ship_name: the name of the ship (str)
    players: the information of the players (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    ships_type: the features of the different ships (dictionary)

    Returns
    -------
    enemy: if there is any enemy or not (bool)

    Version
    -------
    specification: Thomas Blanchy
    implementation: Thomas Blanchy
    """

    ship_pos = ships_ingame[ship_name]['position']
    player = get_player_from_ship(ship_name, players)
    player_index = list(players.keys()).index(player)
    enemy_player = list(players.keys())[abs(player_index - 1)]

    for enemy_ship in players[enemy_player]['ships']:
        enemy_ship_type = ships_ingame[enemy_ship]['type']

        if enemy_ship_type in ['Scout', 'Warship']:
            enemy_ship_pos = ships_ingame[enemy_ship]['position']

            r_delta = abs(enemy_ship_pos[0] - ship_pos[0])
            c_delta = abs(enemy_ship_pos[1] - ship_pos[1])

            if r_delta + c_delta <= ships_type[ships_ingame[enemy_ship]['type']]['range'] + 3:
                return enemy_ship
    return False


#
#   Help functions
#


def get_portal_from_player(player_name, players, info):
    """
    Returns the portal of the player

    Parameters
    ----------
    player_name: the name of the player (str)
    players: the information of the players (dictionary)
    info: the data structure with the portals and the asteroids (dictionary)

    Returns
    -------
    portal: the information of the portal (dictionary)

    Version
    -------
    specification: Thomas Blanchy (v.1 15/04/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    # First portal goes to first player ...
    player_index = list(players.keys()).index(player_name)
    player_portal = info['portals'][player_index]
    return player_portal


def get_player_from_ship(ship_name, players):
    """
    Returns the name of the owner of a ship

    Parameters
    ----------
    ship_name: the name of the ship (str)
    players: the information of the players (dictionary)

    Returns
    -------
    player: the name of the owner of the ship (str)

    Version
    -------
    specification: Cyril Weber (v.1 15/04/2018)
    implementation: Cyril Weber (v.1 15/04/2018)
    """

    for player in players:
        if ship_name in players[player]['ships']:
            return player


def is_locked(ship_name, info, ships_ingame):
    """
    Check if a ship is locked

    Parameters
    ----------
    ship_name: the name of the ship (str)
    info: the data structure with the portals and the asteroids (dictionary)
    ships_ingame: the ships on the board (dictionary)

    Returns
    -------
    locked: if the ship is locked or not (bool)

    Version
    -------
    specification: Joaquim Peremans (v.1 15/04/2018)
    implementation: Joaquim Peremans (v.1 15/04/2018)
    """

    if ships_ingame[ship_name]['type'] in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
        for asteroid in info['asteroids']:
            if ship_name in asteroid['ships_locked']:
                return True
        return False
    else:
        return False


def get_asteroid_from_position(position, info):
    """
    Get the information of an asteroid according to its position

    Parameters
    ----------
    position: the position of the asteroid (list)
    info: the data structure with the portals and the asteroids (info)

    Returns
    -------
    asteroid: the information of the asteroid (dictionary)

    Version
    -------
    specification: Thomas Blanchy (v.1 15/04/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    for asteroid in info['asteroids']:
        if position[0] == asteroid['position'][0] and position[1] == asteroid['position'][1]:
            return asteroid
    return False


def get_ship_radius(ship_type):
    """
    Get the radius of a specific type of ship

    Parameters
    ----------
    ship_type: the type of the ship (str)

    Returns
    -------
    radius: the radius of the ship (int)

    Version
    -------
    specification: Thomas Blanchy (v.1 15/03/2018)
    implementation: Thomas Blanchy (v.1 15/03/2018)
    """

    types = {
        'Scout': 1,
        'Warship': 2,
        'Excavator-S': 0,
        'Excavator-M': 1,
        'Excavator-L': 2
    }

    return types[ship_type]


def get_closest_asteroid(info, position):
    """
    Returns the closest asteroid on the board from a certain position

    Parameters
    ----------
    info: the data structure with the portals and the asteroids (dictionary)
    position: the position from where to check (list)

    Returns
    -------
    asteroid: the closest asteroid (dictionary)

    Version
    -------
    specification: Thomas Blanchy (v.1 12/04/2018)
    implementation: Thomas Blanchy (v.1 12/04/2018)
    """

    current_closest_asteroid = info['asteroids'][0]
    current_distance = -1

    for asteroid in info['asteroids']:
        if asteroid['ore'] > 0.1:
            asteroid_pos = asteroid['position']
            distance = abs(position[0] - asteroid_pos[0]) + abs(position[1] - asteroid_pos[1])

            close = False
            if distance < current_distance or current_distance == -1:
                close = True

            if close:
                current_closest_asteroid = asteroid
                current_distance = distance

    return current_closest_asteroid


def check_range(attacker, target_pos, ships_ingame, ships_type):
    """
    Check if a ship is in the range of another ship.

    Parameters
    ----------
    attacker: the name of the attacker's ship (str)
    target_pos: the position of the target (list)
    ships_ingame: the ships currently on the board (dictionary)
    ships_type: the types of the ships (dictionary)

    Returns
    -------
    range: if the ships are close enough (bool)

    Version
    -------
    specification: Thomas Blanchy (v.2 01/04/2018)
    implementation: Thomas Blanchy (v.1 9/04/2018)
    """

    attacker_ship = ships_ingame[attacker]

    # |r2 - r1| + |c2 - c1|
    r_value = abs(target_pos[0] - attacker_ship['position'][0])
    c_value = abs(target_pos[1] - attacker_ship['position'][1])
    distance = r_value + c_value

    if attacker_ship['type'] in ['Warship', 'Scout']:
        return distance <= ships_type[attacker_ship['type']]['range']
    else:
        return True

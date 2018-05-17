# coding: utf-8

# Importations
import copy
import random
import os
from termcolor import colored

import AI_gr_21 as ai
import remote_play as remote

# ----------------- Utils --------------------


# Utils - Useful actions


def fill_ship_with_ores(ship, ship_types, ores):
    """ Fills a ship with a specified amount of ores

    Parameters
    ----------
    ship: The ship that gets the ores (dict)
    ship_types: The different types of ships (dict)
    ores: The amount of ores we want to give to the ship (float)

    Return
    ------
    overflow: The overflow of ores (float)

    Note
    ----
    The overflow is the amount of ores that the ship can not get.
    The capacity of ores of a ship is limited according to its type.

    The ship must be an excavator.

    Version
    -------
    specification: Poitier Pierre, Thys Killian (v.1 01/04/28)
    implementation: Poitier Pierre, Thys Killian (v.1 01/04/28)
    """

    ship_type_data = ship_types[ship['type']]
    ship_weight = float(ship_type_data['weight'])

    ship_capacity = ship_weight - ship['carried_ores']

    overflow = 0.0

    if ores > ship_capacity:

        ship['carried_ores'] = ship_weight
        overflow = ores - ship_capacity

    else:

        ship['carried_ores'] += ores

    return overflow


def distribute_ores(blue_ships_names, red_ships_names, blue_ships, red_ships, ship_types, ores):
    """ Distributes an amount of ores between ships

    Parameters
    ----------
    blue_ships_names: The names of the blue ships (list)
    red_ships_names: The names of the red ships (list)
    blue_ships: All the blue player's ships (dict)
    red_ships: All the red player's ships (dict)
    ship_types: The different types of ships (dict)
    ores: The amount of ores that we distribute (float)

    Returns
    -------
    overflow: The overflow of ores (float)

    Note
    ----
    The ships must not be full, and the number of ships must be positive

    Version
    -------
    specification: Poitier Pierre, Thys Killian (v.1 01/04/18)
    implementation: Poitier Pierre, Thys Killian (v.1 01/04/18)
    """

    overflow = 0.0

    ores_per_ship = ores / (len(blue_ships_names) + len(red_ships_names))

    for ship_name in blue_ships_names:

        ship = blue_ships[ship_name]

        overflow += fill_ship_with_ores(ship, ship_types, ores_per_ship)

    for ship_name in red_ships_names:

        ship = red_ships[ship_name]

        overflow += fill_ship_with_ores(ship, ship_types, ores_per_ship)

    return overflow


def damage_ship(ship, damages):
    """ Damages a ship with a specified amount of damages

    Parameters
    ---------
    ship: The ship which is going to be damaged (dict)
    damages: The amount of damages (int)

    Note
    ----
    The life of a ship can not be negative

    Version
    -------
    specification: Renaud Thiry, Poitier Pierre (v.2 04/03/18)
    implementation: Renaud Thiry (v.1 16/03/18)
    """

    # Check if we kill the ship or just do some damages

    if damages >= ship['life']:
        ship['life'] = 0
    else:
        ship['life'] -= damages


def hit_portal(portal, target_x, target_y, damages):
    """ Checks if the target is a portal, in this case damages it

    Parameters
    ----------
    portal: The player's portal (dict)
    target_x: The X position of the target (int)
    target_y: The Y position of the target (int)
    damages: The amount of damage taken by a hit portal (int)

    Note
    ----
    If a portal is hit, it is instantly damaged

    Version
    -------
    specification: Poitier Pierre (v.1 16/03/18)
    implementation: Poitier Pierre (v.1 16/03/18)
    """

    distances = ai.get_distance_ship_location(portal, target_x, target_y)

    if distances[0] < 3 and distances[1] < 3:

        if portal['life'] <= damages:
            portal['life'] = 0
        else:
            portal['life'] -= damages


def check_game_over(blue_portal, red_portal, turn_without_damage):
    """ Checks whether the game is over

    Parameters
    ----------
    blue_portal: The blue player's portal (dict)
    red_portal: The red player's portal (dict)
    turn_without_damage: Number of turns without any damage (int)

    Returns
    -------
    game_is_over: True if the game is over, False otherwise (bool)
    winner: The Winner [blue, red, or equality] (str)

    Version
    -------
    specifications: Renaud Thiry, Pierre Poitier (v.1->v.2 01/03/18)
    implementation: Poitier Pierre (v.1 08/03/18)
    """

    blue_portal_life = blue_portal['life']
    red_portal_life = red_portal['life']

    is_over = False

    winner = 'nobody'

    if blue_portal_life == 0 and red_portal_life != 0:
        is_over = True
        winner = 'red'

    elif red_portal_life == 0 and blue_portal_life != 0:
        is_over = True
        winner = 'blue'

    elif blue_portal_life == 0 and red_portal_life == 0:
        is_over = True
        winner = 'equality'

    elif turn_without_damage >= 200:
        is_over = True

        if blue_portal_life > red_portal_life:
            winner = 'blue'
        elif red_portal_life > blue_portal_life:
            winner = 'red'
        else:
            winner = 'equality'

    if winner == 'equality':

        blue_ores = blue_portal['ores']
        red_ores = red_portal['ores']

        if blue_ores > red_ores:
            winner = 'blue'
        elif red_ores > blue_ores:
            winner = 'red'

    return is_over, winner


# --------------- Main functions of the game ---------------

# Initialization functions


def read_config_file(file_path):
    """ Reads a configuration file and returns some properties

    Parameter
    ---------
    file_path: The path of the configuration file (str)

    Returns
    -------
    properties: The properties (tuple)

    Raises
    ------
    FileNotFoundError: if the configuration file does not exist

    Notes
    -----
    The properties are:
        1 - map_properties: The size of the map [rows, columns] (tuple)
        2 - blue_portal: The blue player's portal [life, ores, ships, position_x, position_y] (dict)
        3 - red_portal: The red player's portal [life, ores, ships, position_x, position_y] (dict)
        4 - asteroids: The asteroids on the map (dict)

    The asteroids are identified with an ID (position) like this: 'X_Y'
        They contain these keys: ores, ores_per_turn, locked_ships

    Version
    -------
    specification: Killian Thys, Pierre Poitier (v.2 27/02/18)
    implementation: Pierre Poitier (v.1 14/03/18)
    """

    # Open the configuration file

    if os.path.exists(file_path) and file_path.lower().endswith('.mw'):
        config_file = open(file_path, 'r')
    else:
        raise FileNotFoundError('Configuration file not found !')

    # Basic templates of the returned properties

    blue_portal = {'life': 100, 'ores': 4.0, 'ships': []}
    red_portal = {'life': 100, 'ores': 4.0, 'ships': []}
    map_properties = ()
    asteroids = {}

    # The state say what configure
    # States: 1 = size, 2 = portals, 3 = asteroids
    config_target_state = 0

    for line in config_file.readlines():

        # Remove the '\n'
        if line.endswith('\n'):
            line = line[:-1]

        # Check if we need to change the target
        if not line.endswith(':'):
            line_components = str.split(line, ' ')

            if config_target_state == 1:
                map_properties = (int(line_components[0]), int(line_components[1]))

            elif config_target_state == 2:
                # Check if the blue portal is done, otherwise, set the red portal
                if 'position_x' not in blue_portal:
                    blue_portal['position_x'] = int(line_components[1])
                    blue_portal['position_y'] = int(line_components[0])
                else:
                    red_portal['position_x'] = int(line_components[1])
                    red_portal['position_y'] = int(line_components[0])

            elif config_target_state == 3:
                asteroid_id = line_components[1] + '_' + line_components[0]
                asteroids[asteroid_id] = {
                    'position_x': int(line_components[1]),
                    'position_y': int(line_components[0]),
                    'ores': float(line_components[2]),
                    'ores_per_turn': int(line_components[3]),
                    'locked_ships': [[], []]
                }

        # Change the target state (size, portals, or asteroids)
        elif line == 'size:':
            config_target_state = 1
        elif line == 'portals:':
            config_target_state = 2
        elif line == 'asteroids:':
            config_target_state = 3

    # Finally close the file and return the properties

    config_file.close()

    return map_properties, blue_portal, red_portal, asteroids


def create_initial_board_content(map_properties):
    """ Creates the matrix of the board from the map properties

    Parameters
    ----------
    map_properties: The properties of the Map (tuple)

    Returns
    -------
    board_matrix: The matrix of the board (list)

    Note
    ----
    The matrix is a list of lists

    Version
    -------
    specification: Killian Thys (v.1 27/02/18)
    implementation: Poitier Pierre (v.2 03/03/18)
    """

    # The matrix of the board, which is going to contain the rows (list of lists)
    board_matrix = []

    # Size of the map
    rows_nbr = map_properties[0]
    columns_nbr = map_properties[1]

    # Create the bottom border
    bottom_border = list('||' + ('-' * columns_nbr) + '|')

    # Create the top border
    top_border_up = bottom_border[:]
    top_border_down = bottom_border[:]

    # Add the position indicators in the top border
    for n in range(1, columns_nbr // 5):
        position_nbr = n * 5
        if position_nbr > 9:
            top_border_up[position_nbr + 1] = str(position_nbr)[0]
            top_border_down[position_nbr + 1] = str(position_nbr)[1]
        else:
            top_border_down[position_nbr + 1] = str(position_nbr)

    # Add the top border to the matrix
    board_matrix.append(top_border_up)
    board_matrix.append(top_border_down)

    for row in range(1, rows_nbr+2):
        # Add the left border in the row
        if (row % 5) == 0:
            # Add a position indicator
            row_content = str(row)

            if len(row_content) < 2:
                row_content += '|'
        else:
            # Add a basic left border
            row_content = '||'

        # Fill the row with empty tiles
        row_content += ' ' * columns_nbr
        # Add the right border
        row_content += '|'

        # Add the row to the matrix of the board
        board_matrix.append(list(row_content))

    # Add the bottom border
    board_matrix.append(bottom_border)

    return board_matrix

# Interpretation functions


def read_user_input(user_input, ship_types):
    """ Reads the user's input and returns the commands they want to execute

    Parameter
    ---------
    ship_types: Dictionary of the ship types (dict)
    user_input: The user's input (str)

    Returns
    -------
    commands: The commands the user wants to execute (dict)

    Note
    ----
    The returned dictionary has these keys:
        - buy: A list of tuples containing the name and the type of a ship (list)
        - lock: A list of name of ship (list)
        - release: A list of name of ship (list)
        - move: A list of tuples containing the name of a ship and a position (list)
        - attack: A list of tuples containing the name of a ship and a position (list)

    Version
    -------
    specifications: Pierre Poitier, Renaud Thiry (v.1 27/02/18)
    implementation: Renaud Thiry, Poitier Pierre(v.1->v.2 13/03/18)
    """

    # Creates empty lists

    lock = []
    release = []
    move = []
    attack = []
    buy = []

    unique_action_ships = []
    cancel_actions_ships = []

    # Splits the user input into its different commands unless they're invalid
    input_content = user_input.split(' ')

    for user_command in input_content:

        user_command_content = user_command.split(':')

        # Check if the user's command is valid
        if len(user_command_content) == 2:
            # Separate the concerned ship and the action of the command
            ship_name = user_command_content[0]
            action = user_command_content[1]

            # The command wants to:
            if action == 'lock':                                    # Lock the ship
                lock.append(ship_name)

            elif action == 'release':                               # Release the ship
                release.append(ship_name)

            elif action.startswith('@') or action.startswith('*'):  # Move or attack

                action_content = str.split(action[1:], '-')

                # Check if the action is valid [length, digit]
                if (len(action_content) == 2) and action_content[0].isdigit() and action_content[1].isdigit():

                    # Create a command and add it to move or attack list

                    command = (ship_name, int(action_content[1]), int(action_content[0]))

                    if action[0] == '@':
                        move.append(command)

                        if ship_name in unique_action_ships:
                            cancel_actions_ships.append(ship_name)
                        else:
                            unique_action_ships.append(ship_name)

                    elif action[0] == '*':
                        attack.append(command)

            elif action in ship_types:                              # Buy a ship
                buy.append((ship_name, action))

    move = [command for command in move if not command[0] in cancel_actions_ships]

    return {'lock': lock, 'release': release, 'move': move, 'attack': attack, 'buy': buy}


def get_naive_ai_command(ships, ship_types, portal, asteroids):
    """ Get the command of the naive AI

    Parameter
    ---------
    ships: The ships of the AI (dict)
    ship_types: The different types of ship (dict)
    portal: The portal of the AI (dict)
    asteroids: All the asteroids on the map (dict)

    Returns
    -------
    AI_command: The command of the naive AI (str)

    Note
    ----
    The naive AI plays randomly

    Version
    -------
    specification: Poitier Pierre (v.1 30/03/18)
    implementation: Poitier Pierre (v.1 30/03/18)
    """

    command = ''

    ship_types_names = list(ship_types.keys())
    nbr_ship_types = len(ship_types_names)

    if len(ships) == 0:
        new_ship_name = ai.generate_ship_name(ships, {})
        new_ship_type = ship_types_names[random.randint(0, nbr_ship_types - 1)]

        ship_price = ship_types[new_ship_type]['price']

        if ship_price <= portal['ores']:
            command = ai.add_buy_command(command, new_ship_name, new_ship_type, portal, ship_types, asteroids, {})

    for ship_name in ships:
        ship = ships[ship_name]
        ship_x = ship['position_x']
        ship_y = ship['position_y']

        if random.randint(0, 5) != 0:

            # Buy
            if random.randint(0, 1) == 1:
                new_ship_name = ai.generate_ship_name(ships, [])
                new_ship_type = ship_types_names[random.randint(0, nbr_ship_types - 1)]

                ship_price = ship_types[new_ship_type]['price']

                if ship_price <= portal['ores']:
                    command = ai.add_buy_command(
                        command,
                        new_ship_name,
                        new_ship_type,
                        portal,
                        ship_types,
                        asteroids,
                        {}
                    )

            # Release
            if random.randint(0, 4) == 1 and 'locked' in ship:
                if ship['locked']:
                    command = ai.add_release_command(command, ship_name)
                else:
                    command = ai.add_lock_command(command, ship_name)

            # Attack
            if random.randint(0, 3) == 1:
                ship_type_data = ship_types[ship['type']]

                if 'range' in ship_type_data:
                    ship_range = ship_type_data['range']
                    range_x = random.randint(0, ship_range)
                    range_y = random.randint(0, ship_range - range_x)

                    new_x_target = ship_x + random.randint(-range_x, range_x)
                    new_y_target = ship_y + random.randint(-range_y, range_y)

                    command = ai.add_attack_command(command, ship_name, new_x_target, new_y_target)

            # Move
            elif random.randint(0, 5) != 5:
                new_x_position = ship_x + random.randint(-1, 1)
                new_y_position = ship_y + random.randint(-1, 1)
                command = ai.add_move_command(command, ship_name, new_x_position, new_y_position)

    return command


# Action functions


def buy_ship(ship_to_buy, player_ships, ship_types, player_portal):
    """ Buys a ship and adds it to the ships

    Parameters
    ----------
    ship_to_buy: The ship the player wants to buy (tuple)
    player_ships: The ships of the player (dict)
    ship_types: The different types of ships in the game (dict)
    player_portal: The player's portal (dict)

    Note
    ----
    The bought ship is added to the player's ships

    Version
    -------
    specifications: Killian Thys, Poitier Pierre (v.2 09/03/18)
    implementation: Killian Thys (v.1 12/03/18)
    """

    ship_name = ship_to_buy[0]
    ship_type = ship_to_buy[1]

    # Check if the type of the ship exists
    if ship_type in ship_types and ship_name not in player_ships:

        ship_price = ship_types[ship_type]['price']

        # Check if the player has enough ores
        if player_portal['ores'] >= ship_price:
            player_portal['ores'] -= ship_price

            # Create initial ship structure
            bought_ship = {
                'life': ship_types[ship_type]['life'],
                'type': ship_type,
                'position_x': player_portal['position_x'],
                'position_y': player_portal['position_y']
            }

            # Check if the ship is an excavator or an aggressive ship
            if ship_type.startswith('excavator'):
                bought_ship['locked'] = False
                bought_ship['carried_ores'] = 0.0

            # Finally add it to the ships
            player_ships[ship_name] = bought_ship


def lock_ship(ship, ship_name, team, asteroids, portal):
    """ Locks a ship on an asteroid or a portal

    Parameter
    ---------
    ship: The ship which is going to be locked (dict)
    ship_name: The name of the ship which is going to be locked (str)
    team: The player's team ID [0 or 1] (int)
    asteroids: The asteroids on the map (dict)
    portal: The concerned player's portal (dict)

    Note
    ----
    When a ship is locked it can't move

    A ship can only be locked on an asteroid or a portal

    The ID of the team is 0 for the blue team, and 1 for the red team

    Version
    -------
    specifications: Pierre Poitier, Killian Thys (v.2 01/03/18)
    implementation: Killian Thys, Poitier Pierre (v.2 12/03/18)
    """

    # Check if the ship is an excavator
    if 'locked' in ship and not ship['locked']:

        ship_pos_x = ship['position_x']
        ship_pos_y = ship['position_y']

        # The position Id is the ID of an asteroid on the specified position
        position_id = str(ship_pos_x) + '_' + str(ship_pos_y)

        # Lock on the asteroid, if it exists
        if position_id in asteroids:
            ship['locked'] = True
            asteroids[position_id]['locked_ships'][team].append(ship_name)

        # Lock on the portal if it exists at this position
        elif ship_pos_x == portal['position_x'] and ship_pos_y == portal['position_y']:
            ship['locked'] = True
            portal['ships'].append(ship_name)


def release_ship(ship, ship_name, team, asteroids, portal):
    """ Releases a locked ship

    Parameters
    ----------
    ship: Ship which is going to be locked (dict)
    ship_name: The name of the ship which is going to be locked (str)
    team: The player's team ID (int)
    asteroids: The asteroids on the map (dict)
    portal: The concerned player's portal (dict)

    Note
    ----
    A ship can only be released if it was locked before

    The ID of the team is 0 for the blue team and 1 for the red team

    Version
    -------
    specifications: Pierre Poitier, Killian Thys (v.2 01/03/18)
    implementation: Killian Thys, Poitier Pierre (v.2 12/03/18)
    """

    if 'locked' in ship and ship['locked']:
        ship['locked'] = False

        # Check if the ship is on an asteroid, otherwise it is on a portal

        position_id = str(ship['position_x']) + '_' + str(ship['position_y'])
        if position_id in asteroids:
            asteroids[position_id]['locked_ships'][team].remove(ship_name)

        else:
            portal['ships'].remove(ship_name)


def move_ship(ship_name, ships, target_x, target_y, map_properties):
    """ Moves the designated ship to targeted coordinates

    Parameters
    ----------
    ship_name: The ship to move (str)
    ships: The player's ships (dict)
    target_x: The targeted x coordinate (int)
    target_y: The targeted y coordinate (int)
    map_properties: The properties of the map (tuple)

    Note
    ----
    The ship can only move to a nearby position

    Version
    -------
    specification: Killian Thys (v.1 01/03/18
    implementation: Poitier Pierre (v.2 19/03/18)
    """

    # Get the difference between the two positions and check if they are too far or not

    ship = ships[ship_name]

    delta_x = target_x - ship['position_x']
    delta_y = target_y - ship['position_y']

    is_locked = False

    if 'locked' in ship and ship['locked']:
        is_locked = True

    # Check if the position is next to the ship
    if delta_x in range(-1, 2) and delta_y in range(-1, 2) and not is_locked:

        map_rows = map_properties[0]
        map_columns = map_properties[1]

        # Check if the ship is close enough to check if the wall is blocking it
        if (
            target_x - 2 < 1 or
            target_x + 2 > map_columns or
            target_y - 2 < 1 or
            target_y + 2 > map_rows
        ):
            ship_type = ship['type']

            can_move = False

            # Check if the ship can move according to its hit-box

            if ship_type == 'scout' or ship_type == 'excavator-M':
                can_move = target_x in range(2, map_columns) and target_y in range(2, map_rows)

            elif ship_type == 'warship' or ship_type == 'excavator-L':
                can_move = target_x in range(3, map_columns - 1) and target_y in range(3, map_rows - 1)

            elif target_x in range(1, map_columns + 1) and target_y in range(1, map_rows + 1):
                can_move = True

            if can_move:
                ship['position_x'] = target_x
                ship['position_y'] = target_y

        else:
            ship['position_x'] = target_x
            ship['position_y'] = target_y


def attack_target(ship, ship_types, blue_ships, red_ships, target_position_x, target_position_y,
                  blue_portal, red_portal):
    """Attacks a targeted position and damage the ships we collide

    Parameters
    ----------
    ship: The ship that will attack (dict)
    ship_types: The types of the ships (dict)
    blue_ships: The blue player's ships (dict)
    red_ships: The red player's ships (dict)
    target_position_x: The X coordinate of the ship to attack (int)
    target_position_y: The Y coordinate of the ship to attack (int)
    blue_portal: The blue player's portal (dict)
    red_portal: The red player's portal (dict)

    Returns
    -------
    ship_damaged: True if a ship is damaged, otherwise False

    Note
    ----
    All the ships in the position are damaged, even the allies

    Version
    -------
    specification: Killian Thys (v.1 01/03/18)
    implementation: Renaud Thiry, Poitier Pierre (v.2 20/03/18)
    """

    distances = ai.get_distance_ship_location(ship, target_position_x, target_position_y)

    ship_type = ship_types[ship['type']]

    # Check if the ship can shoot at this position
    if 'attack' in ship_type and distances[2] <= ship_types[ship['type']]['range']:

        # Get the amount of damages the ship do
        damages = ship_type['attack']

        # Get the
        hit_ships = ai.collide_at(ship_types, blue_ships, red_ships, target_position_x, target_position_y)

        # Damage the hit ships

        damaged_ship = False

        for ship_name in hit_ships[0]:
            damage_ship(blue_ships[ship_name], damages)
            damaged_ship = True

        for ship_name in hit_ships[1]:
            damage_ship(red_ships[ship_name], damages)
            damaged_ship = True

        hit_portal(blue_portal, target_position_x, target_position_y, damages)
        hit_portal(red_portal, target_position_x, target_position_y, damages)

        return damaged_ship


def remove_dead_ships(ships):
    """ Removes the dead ships

    Parameter
    ---------
    ships: The ships, even dead ships (dict)

    Version
    -------
    specifications: Pierre Poitier (v.1 01/03/18)
    implementation: Killian Thys, Poitier Pierre (v.2 12/3/18)
    """

    ships_to_delete = []

    for ship_name in ships:
        ship = ships[ship_name]
        if ship['life'] <= 0:
            ships_to_delete.append(ship_name)

    for ship_name in ships_to_delete:
        del ships[ship_name]


def execute_commands(blue_commands, red_commands, blue_ships, red_ships, ship_types,
                     asteroids, blue_portal, red_portal, map_properties):
    """ Executes commands in the right order based on the dictionary of commands

    Parameters
    ----------
    blue_commands: Commands of the blue team (dict)
    red_commands: Commands of the red team (dict)
    blue_ships: All ships under blue command (dict)
    red_ships: All ships under red command (dict)
    ship_types: The different types of ships in the game (dict)
    asteroids: The asteroids in the map (dict)
    blue_portal: The blue team data (dict)
    red_portal: The red team data (dict)
    map_properties: The properties of the map [rows, columns] (tuple)

    Returns
    -------
    ship_damaged: True if a ship is damaged, otherwise False

    Note
    ----
    The commands dictionary must contain these keys:
     - buy: The list of ships to buy (list)
     - lock: The list of ships to lock (list)
     - release: The list of ships to release (list)
     - move: The list of ship move requests (list)
     - attack: The list of ship attack requests (list)

    Version
    -------
    specifications: Killian Thys (v.1 02/03/18)
    implementation: Renaud Thiry, Poitier Pierre (v.1 21/03/18)
    """

    # Buy Phase

    # Blue
    if len(blue_commands['buy']) > 0 and blue_portal['ores'] > 0:

        for purchasing_ship in blue_commands['buy']:
            buy_ship(purchasing_ship, blue_ships, ship_types, blue_portal)
    # Red
    if len(red_commands['buy']) > 0 and red_portal['ores'] > 0:

        for purchasing_ship in red_commands['buy']:
            buy_ship(purchasing_ship, red_ships, ship_types, red_portal)

    # Locking Phase

    # Blue
    if len(blue_commands['lock']) > 0:
        for locking_ship in blue_commands['lock']:
            if locking_ship in blue_ships:
                lock_ship(blue_ships[locking_ship], locking_ship, 0, asteroids, blue_portal)

    # Red
    if len(red_commands['lock']) > 0:
        for locking_ship in red_commands['lock']:
            if locking_ship in red_ships:
                lock_ship(red_ships[locking_ship], locking_ship, 1, asteroids, red_portal)

    # Releasing Phase

    # Blue
    if len(blue_commands['release']) > 0:
        for releasing_ship in blue_commands['release']:
            if releasing_ship in blue_ships:
                release_ship(blue_ships[releasing_ship], releasing_ship, 0, asteroids, blue_portal)

    # Red
    if len(red_commands['release']) > 0:
        for releasing_ship in red_commands['release']:
            if releasing_ship in red_ships:
                release_ship(red_ships[releasing_ship], releasing_ship, 1, asteroids, red_portal)

    # Moving Phase

    blue_moved_ships = []
    red_moved_ships = []

    # Blue
    if len(blue_commands['move']) > 0:
        for moving_data in blue_commands['move']:
            if moving_data[0] in blue_ships:
                move_ship(moving_data[0], blue_ships, moving_data[1], moving_data[2], map_properties)
                blue_moved_ships.append(moving_data[0])

    # Red
    if len(red_commands['move']) > 0:
        for moving_data in red_commands['move']:
            if moving_data[0] in red_ships:
                move_ship(moving_data[0], red_ships, moving_data[1], moving_data[2], map_properties)
                red_moved_ships.append(moving_data[0])

    # Combat Phase

    ship_damaged = False

    # Blue
    if len(blue_commands['attack']) > 0:

        for attacking_data in blue_commands['attack']:
            ship_name = attacking_data[0]

            if ship_name not in blue_moved_ships:

                ship_damaged = attack_target(
                    blue_ships[ship_name],
                    ship_types,
                    blue_ships,
                    red_ships,
                    attacking_data[1],
                    attacking_data[2],
                    blue_portal,
                    red_portal
                )

    # Red
    if len(red_commands['attack']) > 0:

        for attacking_data in red_commands['attack']:
            ship_name = attacking_data[0]

            if ship_name not in red_moved_ships:

                ship_damaged = attack_target(
                    red_ships[ship_name],
                    ship_types,
                    blue_ships,
                    red_ships,
                    attacking_data[1],
                    attacking_data[2],
                    blue_portal,
                    red_portal
                )

    return ship_damaged

# Mining functions


def mine_ores(blue_ships, red_ships, asteroids, ship_types):
    """ Mines ore for some ships locked onto an asteroid

    Parameters
    ----------
    blue_ships: The blue player's ships (dict)
    red_ships: The red player's ships (dict)
    asteroids: The asteroids on the board (dict)
    ship_types: The ship types (dict)

    Note
    ----
    All the ships onto an asteroid mine each turn

    Version
    -------
    specifications: Renaud Thiry (v.1 01/03/18)
    implementation: Killian Thys, Poitier Pierre (v.2 23/03/18)
    """

    for asteroid_name in asteroids:
        asteroid = asteroids[asteroid_name]

        blue_locked_ships = asteroid['locked_ships'][0]
        red_locked_ships = asteroid['locked_ships'][1]

        # Get the ships which are not full

        blue_mining_ships = [
            ship_name for ship_name in blue_locked_ships if
            ship_name in blue_ships and
            blue_ships[ship_name]['carried_ores'] != ship_types[blue_ships[ship_name]['type']]['weight']
        ]

        red_mining_ships = [
            ship_name for ship_name in red_locked_ships if
            ship_name in red_ships and
            red_ships[ship_name]['carried_ores'] != ship_types[red_ships[ship_name]['type']]['weight']
        ]

        ores = asteroid['ores']
        ores_per_turn = asteroid['ores_per_turn']

        if ores < ores_per_turn:
            ores_per_turn = ores

        # While there are mining ships and some ores to mine, the process is not over

        while len(blue_mining_ships) + len(red_mining_ships) > 0 and ores_per_turn > 0:

            ores_per_turn = distribute_ores(
                blue_mining_ships,
                red_mining_ships,
                blue_ships,
                red_ships,
                ship_types,
                ores_per_turn
            )

            # Remove the full ships

            blue_mining_ships = [
                ship_name for ship_name in blue_mining_ships if
                blue_ships[ship_name]['carried_ores'] != ship_types[blue_ships[ship_name]['type']]['weight']
            ]

            red_mining_ships = [
                ship_name for ship_name in red_mining_ships if
                red_ships[ship_name]['carried_ores'] != ship_types[red_ships[ship_name]['type']]['weight']
            ]


def send_ores_to_portal(blue_ships, red_ships, blue_portal, red_portal):
    """
     Sends ship's ores to the portal, if they are onto it

     Parameters
     ----------
     blue_ships: The blue ships (dict)
     red_ships: The red ships (dict)
     blue_portal: The blue portal (dict)
     red_portal: The red portal (dict)

     Note
     ----
     A ship must be on its portal to send its ores

     Version
     -------
     specification: Poitier Pierre (v.1 03/03/18)
     implementation: Poitier Pierre (v.1 30/03/18)
    """

    blue_locked_ships = blue_portal['ships']
    red_locked_ships = red_portal['ships']

    # Storing ores into blue portal for blue ships
    for ship_name in blue_locked_ships:

        blue_portal['ores'] += blue_ships[ship_name]['carried_ores']
        blue_ships[ship_name]['carried_ores'] = 0

    # Storing ores into red portal for red ships
    for ship_name in red_locked_ships:

        red_portal['ores'] += red_ships[ship_name]['carried_ores']
        red_ships[ship_name]['carried_ores'] = 0

# Display


def fill_board(board_content, asteroids, blue_ships, red_ships, ship_types, blue_portal, red_portal, map_properties):
    """ Fill the board with our game contents

    Parameters
    ----------
    board_content: The matrix of the board (list)
    asteroids: The asteroids on the map (dict)
    blue_ships: The blue player's ships (dict)
    red_ships: The red player's ships (dict)
    ship_types: The different types of ships (dict)
    blue_portal: The blue player's portal (dict)
    red_portal: The red player's portal (dict)
    map_properties: The properties of the map [rows, columns] (tuple)

    Notes
    -----
    The portals have this pattern: X
    The asteroids have this pattern: A

    The superposition have these patterns:  ! (orange) when two ships are superposed
                                            ? (orange) when a ship and a portal, or asteroid are superposed

    The aggressive ships have this pattern: @
    The excavators have these patterns: # when free
                                        O when mining

    Each ship and portal has the color of its team [blue or red]
    The asteroids are green

    Version
    -------
    specification: Poitier Pierre (v.1 05/03/18)
    implementation: Poitier Pierre (v.1 25/03/18)
    """

    map_offset_x = 1
    map_offset_y = 1

    # Draw portals

    # Blue portal
    blue_portal_x = blue_portal['position_x']
    blue_portal_y = blue_portal['position_y']

    for x_index in range(blue_portal_x - 2, blue_portal_x + 3):
        for y_index in range(blue_portal_y - 2, blue_portal_y + 3):
            board_content[map_offset_y + y_index][map_offset_x + x_index] = colored('X', 'cyan')

    # Red portal
    red_portal_x = red_portal['position_x']
    red_portal_y = red_portal['position_y']

    for x_index in range(red_portal_x - 2, red_portal_x + 3):
        for y_index in range(red_portal_y - 2, red_portal_y + 3):
            board_content[map_offset_y + y_index][map_offset_x + x_index] = colored('X', 'red')

    # Draw asteroids

    for asteroid_name in asteroids:
        asteroid = asteroids[asteroid_name]
        board_content[map_offset_y + asteroid['position_y']][map_offset_y + asteroid['position_x']] = 'A'

    # Draw blue ships

    for ship_name in blue_ships:
        ship = blue_ships[ship_name]
        ship_hit_box = ship_types[ship['type']]['hit_box']
        ship_x = ship['position_x']
        ship_y = ship['position_y']

        for x_index in range(ship_x - 2, ship_x + 3):
            for y_index in range(ship_y - 2, ship_y + 3):

                # Check the old tile on the board to check if we need to draw an superposition
                old_pattern = board_content[map_offset_y + y_index][map_offset_x + x_index]

                # Choose the appropriated pattern

                pattern = colored('@', 'cyan')

                # In case of superposition with field (asteroids and portals)
                if old_pattern == 'X' or old_pattern == 'A':
                    pattern = colored('?', 'green')

                # Other interposition
                elif not old_pattern == ' ':
                    pattern = colored('!', 'green')

                # Without interposition, excavator case
                elif ship['type'].startswith('excavator'):
                    if ship['locked']:
                        pattern = colored('O', 'cyan')
                    else:
                        pattern = colored('#', 'cyan')

                # Set the tile pattern

                x_index_box = x_index - ship_x + 2
                y_index_box = y_index - ship_y + 2

                # Draw each tile of the hit-box of the ship
                if ship_hit_box[x_index_box][y_index_box] == 'a':
                    board_content[map_offset_y + y_index][map_offset_x + x_index] = pattern

    # Draw red ships

    for ship_name in red_ships:
        ship = red_ships[ship_name]
        ship_hit_box = ship_types[ship['type']]['hit_box']
        ship_x = ship['position_x']
        ship_y = ship['position_y']

        for x_index in range(ship_x - 2, ship_x + 3):
            for y_index in range(ship_y - 2, ship_y + 3):

                if x_index in range(1, map_properties[1]+1) and y_index in range(1, map_properties[0]+1):

                    # Check the old tile on the board to check if we need to draw an superposition
                    old_pattern = board_content[map_offset_y + y_index][map_offset_x + x_index]

                    # Choose the appropriated pattern

                    pattern = colored('@', 'red')

                    # In case of superposition with field (asteroids and portals)
                    if old_pattern == 'X' or old_pattern == 'A':
                        pattern = colored('?', 'green')

                    # Other interposition
                    elif not old_pattern == ' ':
                        pattern = colored('!', 'green')

                    # Without interposition, excavator case
                    elif ship['type'].startswith('excavator'):
                        if ship['locked']:
                            pattern = colored('O', 'red')
                        else:
                            pattern = colored('#', 'red')

                    # Set the tile pattern

                    x_index_box = x_index - ship_x + 2
                    y_index_box = y_index - ship_y + 2

                    # Draw each tile of the hit-box of the ship
                    if ship_hit_box[x_index_box][y_index_box] == 'a':
                        board_content[map_offset_y + y_index][map_offset_x + x_index] = pattern


def display_board(board_content, blue_portal, red_portal, blue_ships, red_ships, map_properties):
    """Displays the board

    Parameters
    ----------
    board_content: The matrix of the board (list)
    blue_portal: The blue player's portal (dict)
    red_portal: The red player's portal (dict)
    blue_ships: The blue player's ships (dict)
    red_ships: The red player's ships (dict)
    map_properties: The properties of the map [rows, columns] (tuple)

    Note
    ----
    The information is displayed at the right of the map [portals, blue ships, red ships]

    Version
    -------
    specifications: Renaud Thiry, Poitier Pierre (v.2 27/02/18)
    implementation: Poitier Pierre (v.2 24/03/18)
    """

    print('\n')

    # Set the information which is displayed at the right of the map

    # Portals information
    portals_information = [
        'Portal 1 (blue)',
        '--Life: %d' % blue_portal['life'],
        '--Ores: %d' % blue_portal['ores'],
        '--Ships: %d' % len(blue_ships),

        '----------',

        'Portal 2 (red)',
        '--Life: %d' % red_portal['life'],
        '--Ores: %d' % red_portal['ores'],
        '--Ships: %d' % len(red_ships)
    ]

    # Ships information

    blue_player_ships_info = ['Player 1: Ships (blue)']

    red_player_ships_info = ['Player 2: Ships (red)']

    # Fill the ships information according to each ship

    # Blue ships

    for ship_name in blue_ships:
        ship = blue_ships[ship_name]
        ship_type = ship['type']
        blue_player_ships_info.append('Ship: ' + ship_name)
        blue_player_ships_info.append('--Type: ' + ship_type)
        blue_player_ships_info.append('--Life: ' + str(ship['life']))

        if ship_type.startswith('excavator'):
            blue_player_ships_info.append('--Ores: ' + str(ship['carried_ores']))
            blue_player_ships_info.append(('--Locked: ' + str(ship['locked'])))

        blue_player_ships_info.append('--Position: (%d, %d)' % (ship['position_y'], ship['position_x']))

    # Red ships

    for ship_name in red_ships:
        ship = red_ships[ship_name]
        ship_type = ship['type']
        red_player_ships_info.append('Ship: ' + ship_name)
        red_player_ships_info.append('--Type: ' + ship_type)
        red_player_ships_info.append('--Life: ' + str(ship['life']))

        if ship_type.startswith('excavator'):
            red_player_ships_info.append('--Ores: ' + str(ship['carried_ores']))
            red_player_ships_info.append(('--Locked: ' + str(ship['locked'])))

        red_player_ships_info.append('--Position: (%d, %d)' % (ship['position_y'], ship['position_x']))

    nbr_blue_info = len(blue_player_ships_info)
    nbr_red_info = len(red_player_ships_info)
    nbr_portal_info = len(portals_information)

    # Display the matrix of the board (map + information)

    for index, row_list in enumerate(board_content):

        row_string = ''

        # Display the map
        for tile in row_list:
            row_string += tile

        # Display the information

        row_length = len(row_string)

        # Show portals information
        if nbr_portal_info > index:

            row_string += ' ' + portals_information[index]

        # Show blue ships information
        if nbr_blue_info > index:

            # Align the information
            info_pos = (row_length + 16) - len(row_string)

            row_string += info_pos * ' ' + '| ' + blue_player_ships_info[index]

        # Show red ships information
        if nbr_red_info > index:

            # Align the information
            info_pos = (row_length + 40) - len(row_string)

            row_string += info_pos * ' ' + '| ' + red_player_ships_info[index]

        # Finally print the row with the map and the information
        print(row_string)

    # Save the length of the last row to check where the information exceed the map height
    last_displayed_map_line = map_properties[0] + 3

    # Get the position of the last row to align the information
    last_displayed_map_column = map_properties[1] + 3

    # Check if there is an overflow of information (if exceed the map)
    if nbr_blue_info > last_displayed_map_line or nbr_red_info > last_displayed_map_line:

        # We look at the largest information to display it properly

        # Check what information has the largest overflow
        if nbr_blue_info > nbr_red_info:
            largest_info = blue_player_ships_info
            largest_info_offset = 16
            largest_nbr_info = nbr_blue_info
            smallest_nbr_info = nbr_red_info
        else:
            largest_info = red_player_ships_info
            largest_info_offset = 40
            largest_nbr_info = nbr_red_info
            smallest_nbr_info = nbr_blue_info

        # Overflow with information about the ships of the two teams
        for index in range(last_displayed_map_line, smallest_nbr_info):
            row_string = ''
            row_string += (last_displayed_map_column + 16) * ' ' + '| '
            row_string += blue_player_ships_info[index]
            row_string += ((last_displayed_map_column + 40) - len(row_string)) * ' ' + '| '
            row_string += red_player_ships_info[index]
            print(row_string)

        # Overflow of one team
        for index in range(last_displayed_map_line + (smallest_nbr_info - last_displayed_map_line), largest_nbr_info):
            row_string = (last_displayed_map_column + largest_info_offset) * ' ' + '| '
            row_string += largest_info[index]
            print(row_string)


def run_game(config_file_path, player_1='human', player_2='human', player_ip='127.0.0.1'):
    """ Runs the game (Mining Wars)

    Parameter
    ---------
    config_file_path: The path of the configuration file [*.ws] (str)
    player_1: The type of player (str, optional, default=human)
    player_2: The type of player (str, optional, default=human)
    external_command: An external command, execute with the external players (str)
    player_ip: The IP of the external player, if they exist (str, optional, default=127.0.0.1)

    Raises
    ------
    ValueError if the type of player must be naive_ai, human or normal_ai.
    ValueError if the two players are external

    Note
    ----
    'player_1' and 'player_2' must be 'human', 'naive_ai', 'normal_ai', or 'external'.

    'player_1' and 'player_2' are both 'human' by default.

    The external command is empty by default.
    This command is executed by the players who are defined as 'external'.

    Version
    -------
    specifications: Pierre Poitier, Killian Thys (v.2 20/04/18)
    implementation: Renaud Thiry, Poitier Pierre, Killian Thys (v.2 20/04/18)
    """

    connection = None

    if player_1 == 'external' and player_2 == 'external':
        raise ValueError('The two players are external')

    elif player_2 == 'external':
        print('Connected to %s as player 1' % player_ip)
        connection = remote.connect_to_player(1, player_ip, True)

    elif player_1 == 'external':
        print('Connected to %s as player 2' % player_ip)
        connection = remote.connect_to_player(2, player_ip, True)

    # Set up the configuration of the game

    configurations = read_config_file(config_file_path)

    # Initialize the portals and the asteroids

    map_properties = configurations[0]

    blue_portal = configurations[1]
    red_portal = configurations[2]

    asteroids = configurations[3]

    # The matrix of the board
    empty_board_content = create_initial_board_content(map_properties)

    # The different types of ship
    ship_types = {
        'scout': {
            'life': 3, 'price': 3, 'attack': 1, 'range': 3, 'hit_box': ['.....', '.aaa.', '.aaa.', '.aaa.', '.....']
        },
        'warship': {
            'life': 18, 'price': 9, 'attack': 3, 'range': 5, 'hit_box': ['.aaa.', 'aaaaa', 'aaaaa', 'aaaaa', '.aaa.']
        },
        'excavator-S': {
            'life': 2, 'price': 1, 'weight': 1, 'hit_box': ['.....', '.....', '..a..', '.....', '.....']
        },
        'excavator-M': {
            'life': 3, 'price': 2, 'weight': 4, 'hit_box': ['.....', '..a..', '.aaa.', '..a..', '.....']
        },
        'excavator-L': {
            'life': 6, 'price': 4, 'weight': 8, 'hit_box': ['..a..', '..a..', 'aaaaa', '..a..', '..a..']
        }
    }

    # The users' ship
    blue_ships = {
    }

    red_ships = {
    }

    # We add the portals and the asteroids to the first displayed board
    fill_board(
        empty_board_content,
        asteroids,
        {},
        {},
        ship_types,
        blue_portal,
        red_portal,
        map_properties
    )

    # First display of the board
    display_board(empty_board_content, blue_portal, red_portal, {}, {}, map_properties)

    game_over = False
    winner = 'nobody'

    turn_without_damage = 0
    turn = 0
    red_ai_memory = {}
    blue_ai_memory = {}

    while not game_over:
        turn += 1
        board_content = copy.deepcopy(empty_board_content)

        # Get the user's command

        # ---- Blue User (1) -----

        # Get the command of the blue user

        if player_1 == 'human':
            blue_user_input = input('Blue [USER] command: ')
            blue_user_commands = read_user_input(blue_user_input, ship_types)

        elif player_1 == 'external':

            # Get the command of the external player
            blue_user_input = remote.get_remote_orders(connection)
            blue_user_commands = read_user_input(blue_user_input, ship_types)
            print('Blue [AI] command:', blue_user_input)

        elif player_1 == 'naive_ai':

            blue_user_input = get_naive_ai_command(blue_ships, ship_types, blue_portal, asteroids)
            blue_user_commands = read_user_input(blue_user_input, ship_types)
            print('Blue [AI] command:', blue_user_input)

        elif player_1 == 'normal_ai':
            blue_user_input, blue_ai_memory = ai.get_ai_command(
                blue_ai_memory,
                turn,
                blue_ships,
                red_ships,
                ship_types,
                asteroids,
                blue_portal,
                red_portal,
                map_properties
            )
            blue_user_commands = read_user_input(blue_user_input, ship_types)
            print('Blue [AI] command:', blue_user_input)

        else:
            raise ValueError('Player_1 type does not exist !')

        # If the other player is external, send them our orders

        if player_2 == 'external':
            remote.notify_remote_orders(connection, blue_user_input)

        # ---- Red user ----

        # Get the command of the red user

        if player_2 == 'human':
            red_user_input = input('Red [USER] command: ')
            red_user_commands = read_user_input(red_user_input, ship_types)

        elif player_2 == 'external':

            # Get the command of the external player
            red_user_input = remote.get_remote_orders(connection)
            red_user_commands = read_user_input(red_user_input, ship_types)
            print('Red [AI] command: ', red_user_input)

        elif player_2 == 'naive_ai':

            red_user_input = get_naive_ai_command(red_ships, ship_types, red_portal, asteroids)
            red_user_commands = read_user_input(red_user_input, ship_types)
            print('Red [AI] command: ', red_user_input)

        elif player_2 == 'normal_ai':
            red_user_input, red_ai_memory = ai.get_ai_command(
                red_ai_memory,
                turn,
                red_ships,
                blue_ships,
                ship_types,
                asteroids,
                red_portal,
                blue_portal,
                map_properties
            )
            red_user_commands = read_user_input(red_user_input, ship_types)
            print('Red [AI] command: ', red_user_input)

        else:
            raise ValueError('Player_2 type does not exist !')

        # If the other player is external, send them our orders

        if player_1 == 'external':
            remote.notify_remote_orders(connection, red_user_input)

        ship_damaged = execute_commands(
            blue_user_commands,
            red_user_commands,
            blue_ships,
            red_ships,
            ship_types,
            asteroids,
            blue_portal,
            red_portal,
            map_properties
        )

        if ship_damaged:
            turn_without_damage = 0
        else:
            turn_without_damage += 1

        # Remove all the dead ships
        remove_dead_ships(blue_ships)
        remove_dead_ships(red_ships)

        # Mines or give them to a portal
        mine_ores(blue_ships, red_ships, asteroids, ship_types)
        send_ores_to_portal(blue_ships, red_ships, blue_portal, red_portal)

        # Fill the matrix of the board and display it
        fill_board(board_content, asteroids, blue_ships, red_ships, ship_types, blue_portal, red_portal, map_properties)
        display_board(board_content, blue_portal, red_portal, blue_ships, red_ships, map_properties)

        # Check if the game is over, and if it is, check who is the winner
        game_over, winner = check_game_over(blue_portal, red_portal, turn_without_damage)

    if winner == 'equality':
        print('There is an equality between the players! How did you do that ?')
    else:
        print('The %s player win!' % winner)

    if connection is not None:
        remote.disconnect_from_player(connection)


run_game('../maps/cross.mw', 'external', 'normal_ai', '138.48.160.133')

from termcolor import colored
from AI_gr_42 import *
from remote_play import *
import time


def convert_orders(player, command_line, players_entities):
    """
    Convert the command line string that player send to sort the orders into a data structure
    to simplify access to the information.

    Parameters
    ---------
    player: the player we are converting orders for, must be p1 or p2 (str)
    command_line: the complete line containing orders for the current player's turn (str)
    players_entities: the data structure containing information about the entities of both player (dict)

    Return
    ------
    players_commands: the data structure containing the sorted and simplified orders (dict)

    Version
    -------
    Specification: Aniss Grabsi (v.2 24/03/2018)
    Implementation: Aniss Grabsi (v.2 24/03/2018)
    """

    # Default empty data structure creation for the current player
    orders = {'buying_stage': {'warship': [], 'scout': [], 'excavator-S': [], 'excavator-M': [], 'excavator-L': []},
              'locking_stage': {'lock': [], 'release': []},
              'attack_stage': {},
              'move_stage': {}}

    # Ignore empty command_line
    if command_line:
        # Isolate each order
        chopped_orders = command_line.split(' ')

        # Populate data structure
        for order in chopped_orders:
            ship_name = order.split(':')[0]
            action = order.split(':')[1]

            # Action is to lock or release the ship
            if action == 'lock' or action == 'release':
                if ship_name in players_entities[player] and 'state' in players_entities[player][ship_name]:
                    orders['locking_stage'][action] += [ship_name]

                else:
                    print("[warning][%s] '%s' was ignored because '%s' don't exist or is not an extractor" % (player, order, ship_name))

            # Action is to attack coordinates
            elif '*' in action:
                if ship_name not in orders['move_stage'] and ship_name not in orders['attack_stage']:
                    orders['attack_stage'][ship_name] = action.replace('*', '')

                else:
                    print("[warning][%s] '%s' was ignored because %s has already a move or attack action for this turn." % (player, order, ship_name))

            # Action is to move to coordinates
            elif '@' in action:
                if ship_name not in orders['move_stage'] and ship_name not in orders['attack_stage']:
                    orders['move_stage'][ship_name] = action.replace('@', '')

                else:
                    print("[warning][%s] '%s' was ignored because %s has already a move or attack action for this turn." % (player, order, ship_name))

            # Action is to buy a new ship
            elif action in orders['buying_stage']:  # if action is to buy ship

                # Prevent buying twice the same ship (same name)
                already_buying = False
                for ship_type in orders['buying_stage']:
                    if ship_name in orders['buying_stage'][ship_type]:
                        already_buying = True

                if ship_name not in players_entities[player] and not already_buying:
                    orders['buying_stage'][action] += [ship_name]

                else:
                    print("[warning][%s] '%s' was ignored because you are already trying to buy a ship called '%s' or "
                          "you already have a '%s' in your owned ships" % (player, order, ship_name, ship_name))

            # Order is not recognised
            else:
                print("[ERROR][%s]: order '%s' is not recognised. --> skipping..." % (player, order))

    return orders


def game_over(nodmg_turn, end_turn, players_entities):
    """
    Checks if game is over. So when portal are destroyed or we hit the last turn with no damage
    to any ship or portal.

    Parameters
    ----------
    nodmg_turn: the current number of turn without any damage dealt (int)
    end_turn: the maximum number of turn we can have without any damage dealt (int)
    players_entities: the data structure containing information about ships (dict)

    Returns
    -------
    True: if game is over
    False: otherwise

    Version
    -------
    Specification: Aniss Grabsi (v.1 30/03/2018)
    Implementation: Aniss Grabsi (v.1 30/03/2018)
    """

    # Count how many players are dead
    deads = []

    for player in players_entities:
        if players_entities[player]['portal']['hp'] <= 0 or nodmg_turn > end_turn:
            deads += [player]

    if len(deads) == 2:
        # Check their ore
        dead1_ore = players_entities[deads[0]]['portal']['ore']
        dead2_ore = players_entities[deads[1]]['portal']['ore']

        if dead1_ore == dead2_ore:
            print('It\'s a tie nobody lost nobody won.')
        elif dead1_ore > dead2_ore:
            print('Congratulations %s you won the game because you have more ore than your opponent !' % deads[0])
        else:
            print('Congratulations %s you won the game because you have more ore than your opponent !' % deads[1])

        return True

    elif len(deads) == 1:
        print('The %s has lost his portal and lost ...'
              '\nCongratulations to the other player you were better !' % deads[0])
        return True

    else:
        return False


def prepare_game(config_file, board, players_entities, available_entities):
    """
    Prepare the game by completing data structures with parameters from the board config file.

    Parameters
    ----------
    config_file: the config file containing info about the board. (str)
    board: the data structure containing information about the board (dict)
    players_entities: the data structure containing information about ships (dict)
    available_entities: existing type of ships to buy (dict)

    Returns
    -------
    board: the data structure to populate with board information with its default values (dict)
    players_entities: the data structure to populate with entities information with its default values (dict)

    Version
    -------
    Specification: Aniss Grabsi (v.1 29/03/2018)
    Implementation: Aniss Grabsi (v.1 29/03/2018)
    """

    # Complete the board data structure
    fh = open(config_file)
    config_lines = fh.readlines()
    fh.close()

    for line_id, line in enumerate(config_lines):
        if 'size' in line:
            # Get size
            size = config_lines[line_id + 1].strip('\n').split(' ')

            # Store size
            board['size'] = '%s-%s' % (size[0], size[1])

        elif 'portals' in line:
            # Get portals
            portalp1 = config_lines[line_id + 1].strip('\n').split(' ')
            portalp2 = config_lines[line_id + 2].strip('\n').split(' ')

            # Store portals
            board['portalp1'] = '%s-%s' % (portalp1[0], portalp1[1])
            board['portalp2'] = '%s-%s' % (portalp2[0], portalp2[1])

        elif 'asteroids' in line:
            for asteroid_info in config_lines[line_id + 1:]:
                # Get current asteroid
                current_ast = asteroid_info.strip('\n').split(' ')
                ast_coord = '%s-%s' % (current_ast[0], current_ast[1])
                ast_supply = int(current_ast[2])
                ast_type = int(current_ast[3])

                # Store current asteroid
                board['asteroids'][ast_coord] = {'type': ast_type, 'supply': ast_supply}

    # Add portal information to players_entities data structure
    for player in players_entities:
        players_entities[player]['portal'] = generate_entity(player, 'portal', available_entities, board)

    return board, players_entities


def execute_game(players_entities, available_entities, board, nodmg_turn, ai_player, enemy_player, connection):
    """
    Execute the game following the stage order and returns the updated data structures.

    Parameters
    ----------
    players_entities: the data structure containing information about ships (dict)
    available_entities: the data structure containing the available entities (dict)
    board: the data structure containing information about the board and asteroids (dict)
    nodmg_turn: the actual number of turns without damage taken by any entity (int)
    ai_player: the id the ai player is for this game (str)
    enemy_player: the id the enemy player is for this game (str)
    connection: the socket connection with the enemy player

    Return
    ------
    players_entities: the data structure containing information about ships (dict)
    board: the data structure containing information about the board and asteroids (dict)
    nodmg_turn: the number of turns without any damage dealt to any entity (int)

    Version
    -------
    Specification: Aniss Grabsi (v.1 31/03/2018)
    Implementation: Aniss Grabsi (v.2 14/04/2018)
    """

    # Init
    players_commands = {}

    # Get commands from both players
    ai_command_line = ai_build_orders(players_entities, board, ai_player, enemy_player)

    if ai_player == 'p1':
        notify_remote_orders(connection, ai_command_line)
        enemy_command_line = get_remote_orders(connection)

    else:
        enemy_command_line = get_remote_orders(connection)
        notify_remote_orders(connection, ai_command_line)

    print('ai => %s' % ai_command_line)
    print('enemy => %s' % enemy_command_line)
    # Convert orders
    players_commands[ai_player] = convert_orders(ai_player, ai_command_line, players_entities)
    players_commands[enemy_player] = convert_orders(enemy_player, enemy_command_line, players_entities)

    # 1. Buying Stage
    players_entities = buy_ship(players_commands, players_entities, available_entities, board)

    # 2. Lock/unlock stage
    players_entities = lock_unlock(players_entities, players_commands, board)

    # 3. Move and attack stage
    players_entities = move(players_commands, players_entities, board)
    players_entities, damage_detected = attack(check_attack(players_commands, players_entities), players_entities)

    # 4. Mine and deposit stage
    players_entities, board = mining(players_entities, board)
    players_entities = deposit(players_entities)

    # 5. Show board
    show_board(players_entities, board, ai_player)

    # Check the number of turns without any damage taken
    if damage_detected:
        nodmg_turn = 0  # reset counter

    else:
        nodmg_turn += 1

    print('-------------- END ---------------')

    return players_entities, board, nodmg_turn


def get_excavators(asteroid, players_entities):
    """
    Get every excavators who are not full and are locked to the specified asteroid.

    Parameters
    ----------
    asteroid: the coordinate(name) of the asteroid to get excavators from (str)
    players_entities: the data structure containing information about ships (dict)

    Returns
    -------
    excavators: the list of excavators (list)

    Version
    -------
    Specification: Nicolas Frantz (v.2 07/04/2018)
    Implementation: Nicolas Frantz, Aniss Grabsi (v.3 07/04/2018)
    """

    excavators = []

    for player in players_entities:
        for entity in players_entities[player]:
            entity_info = players_entities[player][entity]

            # Get every non-full locked excavator
            if 'state' in entity_info and entity_info['state'] == 'locked':
                excavator_center = len(entity_info['coords']) // 2
                if entity_info['current_storage'] < entity_info['max_storage']:

                    # Compare them with the asteroid
                    if entity_info['coords'][excavator_center] == asteroid:
                        excavators += [[entity, player]]

    return excavators


def sort_excavators(unsorted_excavs, players_entities):
    """
    Sort a list of excavator by left space in their storage (from lowest to highest)

    Parameters
    ----------
    unsorted_excavs: the list of unsorted excavators, get it from get_excavators() function (list)
    players_entities: the data structure containing information about ships (dict)

    Return
    ------
    sorted_excavs: the sorted list of excavators (list)

    Version
    -------
    Specification: Nicolas Frantz (v.2 07/04/2018)
    Implementation: Nicolas Frantz, Aniss Grabsi (v.3 07/04/2018)
    """

    sorted_excavs = []

    for excavator in unsorted_excavs:

        # Get current excavator and player we are checking and its left space
        curr_excav_name = excavator[0]
        curr_excav_player = excavator[1]
        curr_excav_info = players_entities[curr_excav_player][curr_excav_name]
        curr_excav_leftspace = curr_excav_info['max_storage'] - curr_excav_info['current_storage']

        # First iteration we add a first ship
        if not sorted_excavs:
            sorted_excavs += [excavator]

        else:
            excav_sorted_id = 0
            while excav_sorted_id < len(sorted_excavs) and excavator not in sorted_excavs:

                # Get the sorted excavator corresponding the excavator_sorted_id
                sorted_excav_name = sorted_excavs[excav_sorted_id][0]
                sorted_excav_player = sorted_excavs[excav_sorted_id][1]
                sorted_excav_info = players_entities[sorted_excav_player][sorted_excav_name]
                sorted_excav_leftspace = sorted_excav_info['max_storage'] - sorted_excav_info['current_storage']

                # Compare left space of both ships
                if curr_excav_leftspace < sorted_excav_leftspace:
                    sorted_excavs.insert(excav_sorted_id, excavator)
                else:
                    excav_sorted_id += 1

            # Add the excavator as last ship if previous loop couldn't find a suitable place
            if excavator not in sorted_excavs:
                sorted_excavs += [excavator]

    return sorted_excavs


def mining(players_entities, board):
    """
    Make the excavators locked on every asteroids mine for the turn.

    Parameters
    ----------
    players_entities: the data structure containing information about ships (dict)
    board: the data structure containing information about the board and asteroids (dict)

    Return
    ------
    players_entities: the updated data structure with new values for current_ore of excavators (dict)
    board: the updated data structure with new values for supply of asteroids (dict)

    Version
    -------
    Specification: Nicolas Frantz (v.2 07/04/2018)
    Implementation: Nicolas Frantz, Aniss Grabsi (v.3 07/04/2018)
    """

    for ast in board['asteroids']:
        unsorted_excavs = get_excavators(ast, players_entities)
        sorted_excavs = sort_excavators(unsorted_excavs, players_entities)

        excav_not_treated = len(sorted_excavs)
        for sorted_excav in sorted_excavs:

            # excavator needed variables
            excav_name = sorted_excav[0]
            excav_player = sorted_excav[1]
            excav_info = players_entities[excav_player][excav_name]
            excav_leftspace = excav_info['max_storage'] - excav_info['current_storage']

            # asteroid needed variables
            ast_info = board['asteroids'][ast]
            allowed_ore_per_excav = ast_info['supply'] / excav_not_treated

            # Check in which case we are
            if allowed_ore_per_excav < ast_info['type'] and allowed_ore_per_excav <= excav_leftspace:
                mined_ore = allowed_ore_per_excav

            elif ast_info['type'] < excav_leftspace:
                mined_ore = ast_info['type']

            else:
                mined_ore = excav_leftspace

            # Update players_entities and board
            players_entities[excav_player][excav_name]['current_storage'] += mined_ore
            board['asteroids'][ast]['supply'] -= mined_ore
            if board['asteroids'][ast]['supply'] <= 0.01:
                board['asteroids'][ast]['supply'] = 0

            excav_not_treated -= 1

    return players_entities, board


def lock_unlock(players_entities, players_commands, board):
    """
    Lock and unlock excavator ships.

    Parameters
    -----------
    players_entities: contains the ships of both players (dict)
    players_commands: contains the command of the player concerning the locking and unlocking of ships (dict)
    board: contains information of the asteroids (dict)
    Return
    ------
    players_entities: the updated data structure with modified state (dict)

    Version
    -------
    Specification: Nicolas Frantz (v.2 30/03/2018)
    Implementation: Nicolas Frantz(v.3 30/03/2018)
    """

    for player in players_commands:
        portal_info = players_entities[player]['portal']
        portal_center_id = len(portal_info['coords']) // 2
        portal_center = portal_info['coords'][portal_center_id]

        # Locking
        for ship in players_commands[player]['locking_stage']['lock']:
            ship_info = players_entities[player][ship]
            ship_center_id = len(ship_info['coords']) // 2
            ship_center = ship_info['coords'][ship_center_id]

            if ship_center in board['asteroids'] or ship_center == portal_center:
                players_entities[player][ship]['state'] = 'locked'

        # Releasing
        for ship in players_commands[player]['locking_stage']['release']:
            players_entities[player][ship]['state'] = 'unlocked'

    return players_entities


def check_attack(players_commands, players_entities):
    """
    Check if the ships can attack the targeted coordinate

    Parameters
    ----------
    players_commands: contains the command of the player concerning attacking (dict)
    players_entities: contains the ships of both players (dict)

    Return
    ------
    can_be_attacked: the list of coordinates that must be attacked associated with the damage to apply to each (dict)

    Version
    -------
    Specification: Aniss Grabsi (v.2 30/03/2018)
    Implementation: Aniss Grabsi (v.2 30/03/2018)
    """

    # initialize coordinates who will be attacked
    can_be_attacked = {}

    # Iterate on each player's order asking to make a ship attack a coordinate
    for player in players_commands:
        for ship in players_commands[player]['attack_stage']:

            # Check if ship is owned by the right player and can deal damage.
            if ship in players_entities[player] and 'damage' in players_entities[player][ship]:

                # Check if the ship has the range to shoot
                target_coords = players_commands[player]['attack_stage'][ship]
                ship_coords = players_entities[player][ship]['coords']
                ship_center = ship_coords[len(ship_coords) // 2]
                ship_max_range = players_entities[player][ship]['range']

                curr_row = int(ship_center.split('-')[0])
                curr_col = int(ship_center.split('-')[1])

                target_row = int(target_coords.split('-')[0])
                target_col = int(target_coords.split('-')[1])

                if abs(target_row - curr_row) + abs(target_col - curr_col) <= ship_max_range:

                    # Make a list of coordinates associated with total damage to apply
                    if target_coords not in can_be_attacked:
                        can_be_attacked[target_coords] = players_entities[player][ship]['damage']
                    else:
                        can_be_attacked[target_coords] += players_entities[player][ship]['damage']

    return can_be_attacked


def attack(to_damage, players_entities):
    """
    it applies the specified damage to any ship on the specified coordinates got from the to_damage dictionary.

    Parameters
    ----------
    to_damage: the coordinates and damage to apply (dict)
    players_entities: contains the ships of both players (dict)

    Return
    -------
    players_entities: the updated data structure with modified hp. (dict)
    damage_detected: True if damage has been applied to any ship or portal and False otherwise (bool)

    Version
    -------
    Specification: Aniss Grabsi (v.1 26/02/2018)
    Implementation: Aniss Grabsi (v.2 30/03/2018)
    """

    ships_to_delete = []
    damage_detected = False

    for coord in to_damage:
        for player in players_entities:
            for ship in players_entities[player]:

                # Apply damage if possible
                ship_info = players_entities[player][ship]
                if coord in ship_info['coords']:
                    players_entities[player][ship]['hp'] -= to_damage[coord]
                    damage_detected = True

                    # Remove destroyed ships
                    if ship_info['hp'] <= 0 and ship != 'portal':  # Avoid deleting portal because ore is stored in it
                        ships_to_delete += [ship]

            for destroyed_ship in ships_to_delete:
                del players_entities[player][destroyed_ship]

            ships_to_delete = []

    return players_entities, damage_detected


def move(players_commands, players_entities, board):
    """
    Move the ships on the board

    Parameters
    ----------
    players_commands: contains the commands of the player concerning moving (dict)
    players_entities: contains the coordinate of the ships of both players (dict)
    board: used to get the size of the board for borders (dict)

    Return
    ------
    players_entities: the updated data structure with modified coordinates (dict)

    Version
    -------
    Specification: Aniss Grabsi (v.1 26/02/2018)
    Implementation: Aniss Grabsi (v.2 30/03/2018)
    """

    # Get board borders
    max_row = int(board['size'].split('-')[0])
    max_col = int(board['size'].split('-')[1])

    # Iterate on each player's order asking to make a ship move
    for player in players_commands:
        for ship in players_commands[player]['move_stage']:

            # Checks if ship is owned by the right player and is not locked
            if ship in players_entities[player]:
                if 'state' not in players_entities[player][ship] or players_entities[player][ship]['state'] == 'unlocked':

                    # Get current and destination rows and columns (from the center of the ship)
                    curr_coords = players_entities[player][ship]['coords']
                    dest_coords = players_commands[player]['move_stage'][ship]

                    curr_row = int(curr_coords[len(curr_coords) // 2].split('-')[0])
                    curr_col = int(curr_coords[len(curr_coords) // 2].split('-')[1])
                    dest_row = int(dest_coords.split('-')[0])
                    dest_col = int(dest_coords.split('-')[1])

                    # Checks if the ship is moving by exactly 1 box
                    row_move = dest_row - curr_row
                    column_move = dest_col - curr_col

                    if abs(row_move) <= 1 and abs(column_move) <= 1:

                        # For each part of the ship check if it respects board border
                        is_in_board = True
                        new_coords = []
                        for ship_part in players_entities[player][ship]['coords']:
                            new_row = int(ship_part.split('-')[0]) + row_move
                            new_column = int(ship_part.split('-')[1]) + column_move
                            new_coords += ['%s-%s' % (new_row, new_column)]

                            if new_row < 1 or new_row > max_row or new_column < 1 or new_column > max_col:
                                is_in_board = False

                        if is_in_board:
                            # Apply new coordinates to data structure
                            players_entities[player][ship]['coords'] = new_coords

                        else:
                            print("[ERROR][%s] the ship '%s' can't go to '%s' because it's out of border !" % (player, ship, dest_coords))

    return players_entities


def get_topleft_corner(player, board):
    """
    get the row and column of the top left box by starting from the center
    of the portal.

    Parameters
    ----------
    player: the player portal to calculate from, p1 or p2 (str)
    board: the dict containing information about the board (dict)

    Returns
    -------
    row: the row of the top left corner. (int)
    column: the column of the top left corner. (int)

    Version
    -------
    Specification: Aniss Grabsi (v.1 26/02/2018)
    Implementation: Aniss Grabsi (v.1 24/03/2018)
    """

    portal_center = board['portal%s' % player].split('-')

    topleft_row = int(portal_center[0]) - 2
    topleft_column = int(portal_center[1]) - 2

    return topleft_row, topleft_column


def generate_entity(player, ship_type, available_entities, board):
    """
    Spawn a new entity when it is bought by the buy_ship function or at
    the beginning of a game to generate the 2 portals.

    Parameters
    ----------
    player: the player to give the ship to (str)
    ship_type: the type of ship (str)
    available_entities: the data structure containing the available entities (dict)
    board: the data structure containing information about the board (dict)

    Return
    ------
    entity_info: a dict containing the information of the generated entity (dict)

    Version
    -------
    Specification: Aniss Grabsi (v.1 26/02/2018)
    Implementation: Aniss Grabsi (v.1 24/03/2018)
    """

    # copy ship info from default available ship data structure
    entity_info = available_entities[ship_type].copy()
    del entity_info['model']

    # initialize needed parameters for the loop
    current_row, current_column = get_topleft_corner(player, board)
    coords = []
    box_nb = 0

    # go through the 25 boxes
    for nb_row in range(5):
        for nb_column in range(5):

            if available_entities[ship_type]['model'][box_nb] == '#':
                coords += ['%s-%s' % (current_row, current_column)]

            box_nb += 1
            current_column += 1

        current_row += 1
        current_column -= 5

    entity_info['coords'] = coords

    return entity_info


def show_board(players_entities, board, ai_player):
    """
    Show the board and her components (ships, portals, asteroids) following some priority rules.

    Parameters
    ----------
    players_entities: contains every entity that the player owns (dict)
    board: contains basic info about the board such as its size and the location of asteroids (dict)
    ai_player: the id the ai player is for this game (str)

    Version
    -------
    Spécification: Gérard Elian (v.2 23/03/2018)
    Implémentation: Gérard Elian (v.2 30/03/2018)
    """

    # Note: this version has been modified so it can show up nearly properly in canopy
    # please use a terminal to get the real look of the UI

    rows = int(board['size'].split('-')[0]) + 1

    columns = int(board['size'].split('-')[1]) + 1

    # first border
    print('# ' * (columns + 1))

    for row in range(1, rows):
        line = '# '

        for column in range(1, columns):
            coord = '%s-%s' % (row, column)
            ast_detected = False

            # Asteroids have the highest priority to be shown so we start with them
            for ast in board['asteroids']:
                if ast == coord:
                    line += colored('☢ ', 'yellow', attrs=['bold'])
                    ast_detected = True

            # Check for other entities only if no ast were found
            if not ast_detected:

                taken_entity = ()

                # Checks wich entity we should show if there is more than one on this coord
                for player in players_entities:
                    for entity in players_entities[player]:

                        entity_info = players_entities[player][entity]

                        if coord in entity_info['coords']:

                            if not taken_entity:
                                taken_entity = (entity, player)

                            else:
                                # Compare the entity priority with the priority of the taken entity
                                taken_entity_info = players_entities[taken_entity[1]][taken_entity[0]]

                                if entity_info['priority'] > taken_entity_info['priority']:
                                    taken_entity = (entity, player)

                                elif entity_info['priority'] == taken_entity_info['priority'] and player == ai_player:
                                    taken_entity = (entity, player)

                # Show the selected entity part on board

                if not taken_entity:
                    line += '· '

                else:
                    player = taken_entity[1]
                    entity = taken_entity[0]
                    entity_info = players_entities[player][entity]

                    # Portals
                    if entity_info['type'] == 'portal':

                        portal_center_id = len(entity_info['coords']) // 2

                        # Colors of the center of ai player's portal
                        if entity_info['coords'][portal_center_id] == coord:

                            if player == ai_player:

                                if entity_info['hp'] > 25:
                                    line += colored('⬯ ', 'red')
                                else:
                                    line += colored('⬯ ', 'red', attrs=['bold'])
                            else:  # enemy
                                if entity_info['hp'] > 25:
                                    line += colored('⬯ ', 'green')
                                else:
                                    line += colored('⬯ ', 'green', attrs=['bold'])

                        # Colors of the rest of ai player's portal
                        else:
                            if player == ai_player:
                                if entity_info['hp'] > 25:
                                    line += colored('⬮ ', 'red')
                                else:
                                    line += colored('⬮ ', 'red', attrs=['bold'])

                            else:  # enemy
                                if entity_info['hp'] > 25:
                                    line += colored('⬮ ', 'green')
                                else:
                                    line += colored('⬮ ', 'green', attrs=['bold'])

                    # Excavators
                    elif 'state' in entity_info:

                        # Colors of the excavators of ai player
                        if player == ai_player:
                            if entity_info['hp'] > 1:
                                line += colored('⚒ ', 'red')
                            else:
                                line += colored('⚒ ', 'red', attrs=['bold'])

                        # Colors of the excavators of enemy
                        else:
                            if entity_info['hp'] > 1:
                                line += colored('⚒ ', 'green')
                            else:
                                line += colored('⚒ ', 'green', attrs=['bold'])

                    # Attacking ships
                    else:
                        # Colors of the attacking ships of ai player
                        if player == ai_player:
                            if entity_info['hp'] > 2:
                                line += colored('✈ ', 'red')
                            else:
                                line += colored('✈ ', 'red', attrs=['bold'])

                        # Colors of the attacking ships of enemy
                        else:
                            if entity_info['hp'] > 2:
                                line += colored('✈ ', 'green')
                            else:
                                line += colored('✈ ', 'green', attrs=['bold'])
        line += '# '
        print(line)

    # last border
    print('# ' * (columns + 1))


def deposit(players_entities):
    """
    When locked on a portal, stores the ore in the player's portal and remove ore from ship

    Parameters
    ----------
    players_entities: the data structure containing information about ships and portals (dict)

    Return
    -------
    players_entities:

    Version
    -------
    Specification: Nicolas Frantz (v.2 02/04/2018)
    Implementation: Nicolas Frantz(v.3 02/04/2018)
    """

    for player in players_entities:
        for entity in players_entities[player]:
            entity_info = players_entities[player][entity]
            portal_info = players_entities[player]['portal']

            if 'state' in entity_info and entity_info['state'] == 'locked':

                entity_center_id = len(entity_info['coords']) // 2
                entity_center = entity_info['coords'][entity_center_id]

                portal_center_id = len(portal_info['coords']) // 2
                portal_center = portal_info['coords'][portal_center_id]

                if entity_center == portal_center:

                    # Deposit the gathered ore
                    players_entities[player]['portal']['ore'] += entity_info['current_storage']
                    players_entities[player][entity]['current_storage'] = 0

    return players_entities


def buy_ship(players_commands, players_entities, available_entities, board):
    """
    Buy a ship in exchange of ore.

    Parameters
    ----------
    players_commands: contains the commands to buy a ship (dict)
    players_entities: contains information about ships and portals (dict)
    available_entities: contains information about the available ships to buy (dict)
    board: contains information about the map (dict)

    Return
    ------
    players_entities: the updated data structure with new ships (dict)

    Version
    ------
    Specification: Gérard Elian (v.2 23/03/2018)
    Implementation: Gérard Elian (v.1 30/03/2018)
    """

    for player in players_commands:
        for ship_type in players_commands[player]['buying_stage']:

            for ship_name in players_commands[player]['buying_stage'][ship_type]:

                player_ore = players_entities[player]['portal']['ore']
                ship_cost = available_entities[ship_type]['cost']

                # Check if the player has enough ore to buy a ship
                if player_ore >= ship_cost:
                    players_entities[player]['portal']['ore'] -= ship_cost
                    players_entities[player][ship_name] = generate_entity(player, ship_type, available_entities, board)

                else:
                    print("[warning][%s] You don't have enough ore to buy '%s' -> skipping..." % (player, ship_name))

    return players_entities


def play_one_game(end_turn=20, map_location='default_map.mw', ai_player='p1', enemy_player='p2', ip='127.0.0.1'):
    """
    Play one entire game from start to end.

    Parameters
    ----------
    end_turn: the number of maximum turns without damage taken by any entities (int)
    map_location: the path to the map wanted to be used for the game (str)
    ai_player: the id the ai player is for this game (str)
    enemy_player: the id the enemy player is for this game (str)
    ip: the ip of the remote player (str)

    Version
    -------
    Specification: Aniss Grabsi (16/04/2018)
    Implementation: Aniss Grabsi (16/04/2018)
    """

    #############################
    ## Default data structures ##
    #############################
    board = {'asteroids': {}}
    players_entities = {'p1': {}, 'p2': {}}

    available_entities = {'warship': {'hp': 18, 'damage': 3, 'range': 5, 'cost': 9, 'type': 'warship',
                                      'priority': 1, 'model': [' ', '#', '#', '#', ' ',
                                                               '#', '#', '#', '#', '#',
                                                               '#', '#', '#', '#', '#',
                                                               '#', '#', '#', '#', '#',
                                                               ' ', '#', '#', '#', ' ']},

                          'scout': {'hp': 3, 'damage': 1, 'range': 3, 'cost': 3, 'type': 'scout',
                                    'priority': 3, 'model': [' ', ' ', ' ', ' ', ' ',
                                                             ' ', '#', '#', '#', ' ',
                                                             ' ', '#', '#', '#', ' ',
                                                             ' ', '#', '#', '#', ' ',
                                                             ' ', ' ', ' ', ' ', ' ', ]},

                          'excavator-S': {'hp': 2, 'current_storage': 0, 'cost': 1, 'max_storage': 1,
                                          'type': 'excavator-S',
                                          'priority': 5, 'state': 'unlocked', 'model': [' ', ' ', ' ', ' ', ' ',
                                                                                        ' ', ' ', ' ', ' ', ' ',
                                                                                        ' ', ' ', '#', ' ', ' ',
                                                                                        ' ', ' ', ' ', ' ', ' ',
                                                                                        ' ', ' ', ' ', ' ', ' ']},
                          'excavator-M': {'hp': 3, 'current_storage': 0, 'cost': 2, 'max_storage': 4,
                                          'type': 'excavator-M',
                                          'priority': 4, 'state': 'unlocked', 'model': [' ', ' ', ' ', ' ', ' ',
                                                                                        ' ', ' ', '#', ' ', ' ',
                                                                                        ' ', '#', '#', '#', ' ',
                                                                                        ' ', ' ', '#', ' ', ' ',
                                                                                        ' ', ' ', ' ', ' ', ' ']},

                          'excavator-L': {'hp': 6, 'current_storage': 0, 'cost': 4, 'max_storage': 8,
                                          'type': 'excavator-L',
                                          'priority': 2, 'state': 'unlocked', 'model': [' ', ' ', '#', ' ', ' ',
                                                                                        ' ', ' ', '#', ' ', ' ',
                                                                                        '#', '#', '#', '#', '#',
                                                                                        ' ', ' ', '#', ' ', ' ',
                                                                                        ' ', ' ', '#', ' ', ' ']},
                          'portal': {'hp': 100, 'ore': 4, 'type': 'portal',
                                     'priority': 0, 'model': ['#', '#', '#', '#', '#',
                                                              '#', '#', '#', '#', '#',
                                                              '#', '#', '#', '#', '#',
                                                              '#', '#', '#', '#', '#',
                                                              '#', '#', '#', '#', '#']}}

    nodmg_turn = 0
    connection = connect_to_player(int(enemy_player[1:]), ip, True)

    # Get the board and generate default entities
    board, players_entities = prepare_game(map_location, board, players_entities, available_entities)

    # Connect to player
    while not game_over(nodmg_turn, end_turn, players_entities):
        players_entities, board, nodmg_turn = execute_game(players_entities, available_entities, board, nodmg_turn, ai_player, enemy_player, connection)

    # When game_over is true
    print('\O/ Game ended \O/')

    disconnect_from_player(connection)

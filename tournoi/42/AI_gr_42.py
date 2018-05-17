def get_enemies_having_range(coords, enemy_player, players_entities):
    """
    Gets number of enemy ships who can attack the specified coordinates list and also gets the closest enemy attack
    ship and excavator to these coordinates

    Parameters
    ----------
    coords: the coordinates to check (list)
    enemy_player: the id the enemy player is (str)
    players_entities: the data structure containing ships and portals of both player (dict)

    Return
    ------
    has_range = the number of scouts and warships who can attack and the closest enemy attack ship and excavator (list)

    Version
    -------
    Specification: Nicolas Frantz (v.1 05/05/2018)
    Implementation: Nicolas Frantz (v.1 05/05/2018)
    """
    # Initialize loop
    enemy_scouts = 0
    enemy_warships = 0
    closest_attack_ship_coords = None
    closest_excav_coords = None
    has_range = []

    for coord in coords:
        # Get row and col of the coordinates who are being checked
        checked_row = int(coord.split('-')[0])
        checked_col = int(coord.split('-')[1])

        for ship in players_entities[enemy_player]:
            ship_info = players_entities[enemy_player][ship]

            if ship_info['type'] != 'portal':
                # Get row and col of enemy ship center
                ship_center_id = len(ship_info['coords']) // 2
                ship_center = ship_info['coords'][ship_center_id]
                ship_row = int(ship_center.split('-')[0])
                ship_col = int(ship_center.split('-')[1])

                # Get the distances
                difference_row = abs(checked_row - ship_row)
                difference_col = abs(checked_col - ship_col)
                curr_distance = max(difference_row, difference_col)

                # Get the closest enemy attack ship
                if 'range' in ship_info:
                    if closest_attack_ship_coords is None or curr_distance < selected_attack_distance:
                        selected_attack_distance = curr_distance
                        closest_attack_ship_coords = ship_center

                # Get the closest enemy excavator
                if 'state' in ship_info:
                    if closest_excav_coords is None or curr_distance < selected_excav_distance:
                        selected_excav_distance = curr_distance
                        closest_excav_coords = ship_center

                # Get the number of enemy ships who have range to attack the coordinates
                if 'range' in ship_info and ship_info['range'] >= difference_row + difference_col:
                    if ship_info['type'] == 'scout':
                            enemy_scouts += 1

                    if ship_info['type'] == 'warship':
                            enemy_warships += 1

    has_range += [enemy_scouts, enemy_warships, closest_attack_ship_coords, closest_excav_coords]

    return has_range


def can_attack(ship, target, player, players_entities):
    """
    Checks if the given ship can attack the target coordinates

    Parameters
    ----------
    ship: the name of the ship to check (str)
    target: the coordinates of the target to check (str)
    player: the player owning the ship (str)
    players_entities: the data structure containing ships and portals of both player (dict)

    Return
    ------
    True if the ship can attack, False if not

    Version
    -------
    Specification: Nicolas Frantz (v.1 05/05/2018)
    Implementation: Nicolas Frantz (v.1 05/05/2018)
    """
    # Get information about the ship
    ship_info = players_entities[player][ship]
    ship_center_id = len(ship_info['coords']) // 2
    ship_center = ship_info['coords'][ship_center_id]
    ship_row = int(ship_center.split('-')[0])
    ship_col = int(ship_center.split('-')[1])

    # Get target row and col
    target_row = int(target.split('-')[0])
    target_col = int(target.split('-')[1])

    # Check if it can attack the specified target
    needed_range = abs(target_row - ship_row) + abs(target_col - ship_col)
    if ship_info['range'] >= needed_range:
        return True
    else:
        return False


def ai_handle_attackers(players_entities, board, ai_player, enemy_player):
    """
    Randomly select the movements the ai will do next turn.

    Parameters
    ----------
    players_entities: contains ships and portals of both players (dict)
    board: information about the board such as asteroids and board border (dict)
    ai_player: the id the ai player is (str)
    enemy_player: the id the enemy player is (str)

    Return
    ------
    commands : moves for the turn formatted following game rules (str)

    Version
    -------
    Specification: Nicolas Frantz (v.2 01/05/2018)
    Implementation: Nicolas Frantz (v.2 01/05/2018)
    """
    commands = ''

    # Get the row and col of enemy's portal
    enemy_portal_info = players_entities[enemy_player]['portal']
    enemy_portal_center_id = len(enemy_portal_info['coords']) // 2
    enemy_portal_center = enemy_portal_info['coords'][enemy_portal_center_id]

    # Calculate the number of scouts and warships we have
    total_ai_scouts = 0
    total_ai_warships = 0

    for ship in players_entities[ai_player]:
        ship_info = players_entities[ai_player][ship]
        if ship_info['type'] == 'scout':
            total_ai_scouts += 1
        if ship_info['type'] == 'warship':
            total_ai_warships += 1

    # Do things
    for ai_ship in players_entities[ai_player]:
        ship_info = players_entities[ai_player][ai_ship]

        if 'range' in ship_info:
            # Get ship center, row and col
            ship_center_id = len(ship_info['coords']) // 2
            ship_center = ship_info['coords'][ship_center_id]

            # Get the number of scouts and warships who can attack our ship
            # Also find the closest enemy attack ship and excavator
            has_range = get_enemies_having_range(ship_info['coords'], enemy_player, players_entities)
            enemy_scouts_in_range = has_range[0]
            enemy_warships_in_range = has_range[1]
            closest_attack_ship_coords = has_range[2]
            closest_excav_coords = has_range[3]

            # Select the commands for scouts
            if ship_info['type'] == 'scout':
                # Attack enemy scouts who can attack us
                if enemy_scouts_in_range > 0:
                    commands += ai_attack(players_entities, ai_ship, board, ai_player, enemy_player)

                # Attack the enemy portal when we have 3 scouts or when there is no more excavators
                elif total_ai_scouts >= 3 or closest_excav_coords is None:
                    if can_attack(ai_ship, enemy_portal_center, ai_player, players_entities):
                        commands += ai_attack(players_entities, ai_ship, board, ai_player, enemy_player)

                    # Get closer to portal
                    else:
                        next_coordinates = ai_move_ship(ship_center, enemy_portal_center)
                        commands += '%s:@%s ' % (ai_ship, next_coordinates)

                # We attack excavators
                elif closest_excav_coords is not None:
                    # Attack if in range
                    if can_attack(ai_ship, closest_excav_coords, ai_player, players_entities):
                        commands += ai_attack(players_entities, ai_ship, board, ai_player, enemy_player)

                    # Get closer to enemy excavator
                    else:
                        next_coordinates = ai_move_ship(ship_center, closest_excav_coords)
                        commands += '%s:@%s ' % (ai_ship, next_coordinates)

            # Select the commands for warships
            else:
                # Attack any scouts or warships who can attack us
                if enemy_scouts_in_range > 0 or enemy_warships_in_range > 0:
                    commands += ai_attack(players_entities, ai_ship, board, ai_player, enemy_player)

                else:
                    # If we have only 1 warship move to closest enemy attack ship (if it exists)
                    if total_ai_warships == 1 and closest_attack_ship_coords is not None:
                            next_coordinates = ai_move_ship(ship_center, closest_attack_ship_coords)
                            commands += '%s:@%s ' % (ai_ship, next_coordinates)

                    # Attack the portal with the next warships [2:->[
                    else:
                        # Attack if in range
                        if can_attack(ai_ship, enemy_portal_center, ai_player, players_entities):
                            commands += ai_attack(players_entities, ai_ship, board, ai_player, enemy_player)

                        # Get closer to portal
                        else:
                            next_coordinates = ai_move_ship(ship_center, enemy_portal_center)
                            commands += '%s:@%s ' % (ai_ship, next_coordinates)

                        total_ai_warships -= 1

    return commands


def get_attack_ratio(players_entities, attacking_ships, player):
    """
    Get the current percentage of attacking ships of a player

    Parameters
    ----------
    players_entities: the data structure containing all the ships (dict)
    attacking_ships: the amount of attacking ships (int)
    player: the player id to check (str)

    Return
    ------
    ratio: the ratio of attacking ships

    Version
    -------
    Specification: Aniss Grabsi (v.1 28/04/2018)
    Implementation: Aniss Grabsi (v.1 28/04/2018)
    """

    # Get current ratio except if we don't have any ships yet

    attacking_ratio = 100  # default
    if len(players_entities[player]) - 1 != 0:
        attacking_ratio = attacking_ships / (len(players_entities[player]) - 1) * 100

    return attacking_ratio


def ai_purchase_selection(players_entities, board, ai_player):
    """
    Select the purchases the ai will do next turn.

    Parameters
    ----------
    players_entities: list of ships and portals of both players (dict)
    board: the data structure containing information about the board (dict)
    ai_player: the id the ai player is (str)

    Return
    ------
    commands : purchases for the turn formatted following game rules (str)

    Version
    -------
    Specification: Aniss Grabsi (v.1 28/04/2018)
    Implementation: Aniss Grabsi (v.1 28/04/2018)
    """
    # Initializing the command string
    commands = ''

    # Get total available ore in asteroids
    total_ast_ore = 0
    for ast in board['asteroids']:
        total_ast_ore += board['asteroids'][ast]['supply']

    # Get other needed information
    enemy_damage_ability = 0
    ai_damage_ability = 0

    total_excav_space = 0
    nb_ai_excavs = 0
    nb_ai_attacking_ships = 0
    ai_ore = players_entities[ai_player]['portal']['ore']

    for player in players_entities:
        for ship in players_entities[player]:
            ship_info = players_entities[player][ship]

            # Ignore portal
            if ship_info['type'] != 'portal':

                # Our AI
                if player == ai_player:
                    # Checks if we have an excavator
                    if 'state' in ship_info:
                        total_excav_space += ship_info['max_storage']
                        nb_ai_excavs += 1

                    # Checks if we have an attacking ship
                    elif 'damage' in ship_info:
                        nb_ai_attacking_ships += 1
                        ai_damage_ability += ship_info['damage']

                # Enemy
                elif 'damage' in ship_info:
                    enemy_damage_ability += ship_info['damage']

    # Get current ratio attacking ratio
    attacking_ratio = get_attack_ratio(players_entities, nb_ai_attacking_ships, ai_player)

    # Get perfect amount of excavators to buy
    perfect_excav_amount = round(total_ast_ore / 8)

    # Apply information
    # Handle dangerous situation
    if enemy_damage_ability > 1.3 * ai_damage_ability:  # dangerous = enemy has more than 30% of our damage power
        for attack_ship in [(9, 'warship'), (3, 'scout')]:
            ship_price = attack_ship[0]
            ship_type = attack_ship[1]

            currently_buying = []
            while ai_ore >= ship_price and enemy_damage_ability > 1.3 * ai_damage_ability:
                ship_name = define_name(players_entities, currently_buying, ship_type, ai_player)
                commands += '%s:%s ' % (ship_name, ship_type)

                # Update loop values
                ai_ore -= ship_price
                currently_buying += [ship_name]
                if ship_type == 'warship':
                    ai_damage_ability += 3
                else:
                    ai_damage_ability += 1

    # Handle normal situation
    else:
        # Keep a minimum of 30% attack ships ratio
        if attacking_ratio < 30:
            # Buy best attack ship until ratio is reached
            for attack_ship in [(9, 'warship'), (3, 'scout')]:
                ship_price = attack_ship[0]
                ship_type = attack_ship[1]

                currently_buying = []
                while attacking_ratio < 30 and ai_ore >= ship_price:
                    ship_name = define_name(players_entities, currently_buying, ship_type, ai_player)
                    commands += '%s:%s ' % (ship_name, ship_type)

                    # Update loop values
                    ai_ore -= ship_price
                    nb_ai_attacking_ships += 1
                    attacking_ratio = get_attack_ratio(players_entities, nb_ai_attacking_ships, ai_player)
                    currently_buying += [ship_name]

        # Limit the number of excavators according to the available ore in the game
        elif perfect_excav_amount > nb_ai_excavs:
            # Buy excavator-M until perfect_excav_amount is reached
            currently_buying = []
            while perfect_excav_amount > nb_ai_excavs and ai_ore >= 2:
                ship_name = define_name(players_entities, currently_buying, 'excavator-M', ai_player)
                commands += '%s:%s ' % (ship_name, 'excavator-M')

                # Update loop values
                ai_ore -= 2
                currently_buying += [ship_name]
                nb_ai_excavs += 1

        # When everything is ok we build an army
        elif total_ast_ore >= 9 or ai_ore >= 9:
            # Buy only warship if there is enough ore in ast to do it
            currently_buying = []
            while ai_ore >= 9:
                ship_name = define_name(players_entities, currently_buying, 'warship', ai_player)
                commands += '%s:%s ' % (ship_name, 'warship')

                # Update loop values
                currently_buying += [ship_name]
                ai_ore -= 9
        else:
            # Buy scouts when there is no more ore in ast and we don't have enough for warship
            currently_buying = []
            while ai_ore >= 3:
                ship_name = define_name(players_entities, currently_buying, 'scout', ai_player)
                commands += '%s:%s ' % (ship_name, 'scout')

                # Update loop values
                currently_buying += [ship_name]
                ai_ore -= 3

    return commands


def ai_select_dest(players_entities, board, excavator_name, ai_player, enemy_player):
    """
    Select the best asteroid for an excavator to go to or tell the excavator to go back to the base

    Parameters
    ----------
    players_entities: information about ships and portals (dict)
    board: information about the board such as asteroids (dict)
    excavator_name: the name of the excavator to check (str)
    ai_player: the id the ai player is (str)
    enemy_player: the id the enemy player is (str)

    Return
    ------
    target: the ast selected or the portal for the given excavator (str)

    Version
    -------
    Specification: Aniss Grabsi (v.1 01/05/2018)
    Implementation: Aniss Grabsi (v.1 01/05/2018)
    """
    # Get needed excavator info
    excav_info = players_entities[ai_player][excavator_name]

    # Get needed portal info
    portal_info = players_entities[ai_player]['portal']
    portal_center_id = len(portal_info['coords']) // 2
    portal_center = portal_info['coords'][portal_center_id]
    portal_row = int(portal_center.split('-')[0])
    portal_col = int(portal_center.split('-')[1])

    # Get needed information about every asteroid
    ast_choices = {}
    total_ast_ore = 0
    for ast in board['asteroids']:
        # Get ast info
        ast_info = board['asteroids'][ast]
        ast_row = int(ast.split('-')[0])
        ast_col = int(ast.split('-')[1])
        total_ast_ore += ast_info['supply']
        # Filter out empty asteroids
        if ast_info['supply'] > 0:
            # Calculate distance between ast and portal
            ast_choices[ast] = {}
            ast_choices[ast]['distance'] = max(abs(ast_row - portal_row), abs(ast_col - portal_col))
            have_range = get_enemies_having_range([ast], enemy_player, players_entities)

            # Calculate potential damage that might be taken on this asteroid
            total_damage = 0
            if have_range:
                scouts_having_range = have_range[0]
                warships_having_range = have_range[1]
                total_damage = scouts_having_range + 3 * warships_having_range

            ast_choices[ast]['damage'] = total_damage

    # Select the best asteroid if we are not full
    best_ast = None
    for curr_ast in ast_choices:
        if best_ast is None:
            best_ast = curr_ast
        else:
            if ast_choices[curr_ast]['damage'] < ast_choices[best_ast]['damage']:
                best_ast = curr_ast

            elif ast_choices[curr_ast]['damage'] == ast_choices[best_ast]['damage'] \
                    and ast_choices[curr_ast]['distance'] < ast_choices[best_ast]['distance']:
                    best_ast = curr_ast

    # Select the portal if we are full or if there is no more ore in other asteroids or if we are chased
    has_range = get_enemies_having_range(excav_info['coords'], enemy_player, players_entities)
    ennemies_in_range = has_range[0] + has_range[1]

    if excav_info['current_storage'] == excav_info['max_storage'] or total_ast_ore == 0 or ennemies_in_range > 0:
        target_coord = portal_center
    else:
        target_coord = best_ast

    return target_coord


def ai_move_ship(curr_coord, dest_coord):
    """
    Moves a ship given its current and final destination

    Parameters
    ----------
    curr_coord: the current coordinates of the ship (str)
    dest_coord: the target coordinates of the ship (str)

    Return
    ------
    next_coordinates: the coordinates the specified ship must go to for the next turn (str)

    Version
    -------
    Specification: Aniss Grabsi (v.1 01/05/2018)
    Implementation: Aniss Grabsi (v.2 02/05/2018)
    """

    curr_row = int(curr_coord.split('-')[0])
    curr_col = int(curr_coord.split('-')[1])
    dest_row = int(dest_coord.split('-')[0])
    dest_col = int(dest_coord.split('-')[1])

    # Check rows
    if dest_row - curr_row > 0:
        curr_row += 1
    elif dest_row - curr_row < 0:
        curr_row -= 1

    # Check columns
    if dest_col - curr_col > 0:
        curr_col += 1
    elif dest_col - curr_col < 0:
        curr_col -= 1

    next_coordinates = '%s-%s' % (curr_row, curr_col)

    return next_coordinates


def ai_handle_excavators(players_entities, board, ai_player, enemy_player):
    """
    Handles the excavator by determining if they need to move, lock or unlock themselves

    Parameters
    ----------
    players_entities: information about ships and portals (dict)
    board: information about the board such as asteroids (dict)
    ai_player: the id the ai player is (str)
    enemy_player: the id the enemy player is (str)

    Return
    ------
    commands : lock/unlock/move actions for the turn formatted following game rules (str)

    Version
    -------
    Specification: Aniss Grabsi (v.1 01/05/2018)
    Implementation: Aniss Grabsi (v.2 02/05/2018)
    """

    commands = ''
    for ship_name in players_entities[ai_player]:
        ship_info = players_entities[ai_player][ship_name]

        # Filter out non-excavators
        if 'state' in ship_info:
            # Get needed information
            ship_center_id = len(ship_info['coords']) // 2
            ship_center = ship_info['coords'][ship_center_id]
            ship_row = int(ship_center.split('-')[0])
            ship_col = int(ship_center.split('-')[1])

            target = ai_select_dest(players_entities, board, ship_name, ai_player, enemy_player)

            # When we are on the target
            if target == ship_center:
                if ship_info['state'] == 'unlocked':
                    commands += '%s:lock ' % ship_name

            # When we are not on the target
            else:
                if ship_info['state'] == 'locked':
                    commands += '%s:release ' % ship_name

                if target is not None:
                    # Check if there is no danger on the target coord and go to target
                    next_coords = ai_move_ship(ship_center, target)
                    target_row = int(target.split('-')[0])
                    target_col = int(target.split('-')[1])

                    # Calculate new list of coordinates for the ship
                    row_move = target_row - ship_row
                    column_move = target_col - ship_col

                    new_coords = []
                    for ship_part in players_entities[ai_player][ship_name]['coords']:
                        new_row = int(ship_part.split('-')[0]) + row_move
                        new_column = int(ship_part.split('-')[1]) + column_move
                        new_coords += ['%s-%s' % (new_row, new_column)]

                    has_range = get_enemies_having_range(new_coords, enemy_player, players_entities)
                    ennemies_in_range = has_range[0] + has_range[1]

                    # Move to target if it's safe
                    if ennemies_in_range == 0:
                        commands += '%s:@%s ' % (ship_name, next_coords)

    return commands


def define_name(players_entities, currently_buying, ship_type, ai_player):
    """
    Choose a name for the ship we are buying by analyzing the name of the current ships we own

    Parameters
    ----------
    players_entities: contains ships and portals of both players (dict)
    currently_buying: additional names we are currently buying (list)
    ship_type: the type of ship we want (str)
    ai_player: the id the ai player is (str)

    Return
    ------
    name: the chosen name

    Version
    -------
    Specification: Nicolas Frantz (v.1 08/04/2018)
    Implementation: Nicolas Frantz (v.1 08/04/2018)
    """

    # List of name id's
    ships_nb = [0]
    for ship in players_entities[ai_player]:
        ship_info = players_entities[ai_player][ship]

        if ship_info['type'] != 'portal':  # except portal type
            if ship_info['type'] == ship_type:
                # check the assigned id of the ship
                nb = ship[len(ship_type):]
                ships_nb += [int(nb)]

    for ship in currently_buying:
        nb = ship[len(ship_type):]
        ships_nb += [int(nb)]

    name = '%s%d' % (ship_type, max(ships_nb) + 1)

    return name


def get_attackable_coord(players_entities, board, ship, player):
    """
    Get the coordinates that the attacking ship can attack.

    Parameters
    ----------
    players_entities: list of ships and portals of both players (dict)
    board: the information about the board (dict)
    ship: the name of the ship that will attack (str)
    player: the player who owns the ship (str)

    Return
    ------
    attackable_coords : list of coordinates that the attacking ship can attack (list)

    Version
    -------
    Specification: Gérard Elian (v.1 04/05/2018)
    Implementation: Gérard Elian (v.2 04/05/2018)
    """
    # Get map borders
    max_row = int(board['size'].split('-')[0])
    max_col = int(board['size'].split('-')[1])

    # Get the coords of the center of the ship
    player_ship = players_entities[player][ship]
    center_id = len(player_ship['coords']) // 2
    ship_center = player_ship['coords'][center_id]

    ship_row = int(ship_center.split('-')[0])
    ship_column = int(ship_center.split('-')[1])
    ship_range = player_ship['range'] + 1  # added 1 to easily iterate after
    attackable_coords = []

    # For each row starting from center
    for row_in_range in range(ship_range):
        target_row_up = ship_row + row_in_range
        target_row_down = ship_row - row_in_range

        # For each column starting from center
        for column_in_range in range(ship_range - row_in_range):
            target_column_right = ship_column + column_in_range
            target_column_left = ship_column - column_in_range

            # defines the list of attackable coords of the ship
            if target_row_up <= max_row:
                if target_column_right <= max_col:
                    attackable_coords += ['%s-%s' % (target_row_up, target_column_right)]

                if target_column_left > 0 and target_column_left != target_column_right:
                    attackable_coords += ['%s-%s' % (target_row_up, target_column_left)]

            if target_row_down > 0 and target_row_down != target_row_up:
                if target_column_right <= max_col:
                    attackable_coords += ['%s-%s' % (target_row_down, target_column_right)]

                if target_column_left > 0 and target_column_left != target_column_right:
                    attackable_coords += ['%s-%s' % (target_row_down, target_column_left)]

    return attackable_coords


def ai_attack(players_entities, ship, board, ai_player, enemy_player):
    """
    Select the coord that the ai will attack next turn.

    Parameters
    ----------
    players_entities: list of ships and portals of both players (dict)
    ship: the ship called by move that will attack
    board: the board of the game that contains the amount of ore that each asteroïd contains (dict)
    ai_player: the id the ai player is (str)
    enemy_player: the id the enemy player is (str)

    Return
    ------
    commands : attack for the specified ship formatted following game rules (str)

    Version
    -------
    Specification: Gérard Elian (v.2 04/05/2018)
    Implementation: Gérard Elian (v.3 05/05/2018)
    """

    attackable_coords = get_attackable_coord(players_entities, board, ship, ai_player)

    # Define the priority of the entity that the ship attacks (the ship will attack the highest priority)
    target_priority = {}
    ai_ship_info = players_entities[ai_player][ship]

    # Get total ore in asteroids
    total_ast_ore = 0
    for ast in board['asteroids']:
        total_ast_ore += board['asteroids'][ast]['supply']

    for attack_coord in attackable_coords:
        # Initialize the priority for the current attack_coord
        priority_attack = 0

        for entity in players_entities[enemy_player]:
            # Get center of enemy entity
            enemy_entity_info = players_entities[enemy_player][entity]
            enemy_entity_center_id = len(enemy_entity_info['coords']) // 2
            enemy_entity_center = enemy_entity_info['coords'][enemy_entity_center_id]

            # Check if a coord in attackable_coords corresponds to a coord of an enemy ship
            if attack_coord in enemy_entity_info['coords']:

                # If it's an excavator
                if 'state' in enemy_entity_info:

                    # If it makes sense to attack an excavator
                    if total_ast_ore != 0 and enemy_entity_info['current_storage'] != 0:

                        if enemy_entity_info['type'] == 'excavator-L':
                            priority_attack += 5

                        elif enemy_entity_info['type'] == 'excavator-M':
                            priority_attack += 4

                        else:  # entity is excavator-S
                            priority_attack += 3

                # If it's a warship
                elif enemy_entity_info['type'] == 'warship':
                    if ai_ship_info['type'] == 'warship':
                        priority_attack += 2
                    else:
                        priority_attack += 0.5

                # If it's a scout
                elif enemy_entity_info['type'] == 'scout':
                    priority_attack += 6

                # If it's the portal
                elif enemy_entity_info['type'] == 'portal':
                    priority_attack += 1

                # Prioritize the center of the enemy ship
                if attack_coord == enemy_entity_center:
                    priority_attack += 3

                # if our entities are on the same coords as the target coordinates
                for our_entity in players_entities[ai_player]:
                    our_entity_info = players_entities[ai_player][our_entity]

                    if attack_coord in our_entity_info['coords']:
                        priority_attack -= 20

                # When an attack can kill an enemy entity
                if enemy_entity_info['hp'] <= ai_ship_info['damage']:
                    priority_attack += 20
                    if enemy_entity_info['type'] == 'portal':
                        priority_attack += 9000  # FINISH HIM !!

            target_priority[attack_coord] = priority_attack  # put it in dict

    # Select the coordinate with highest priority
    selected_coord = None
    for coord in target_priority:
        if selected_coord is None:
            selected_coord = coord

        # Select the current coord if it's higher than the already selected
        elif target_priority[coord] > target_priority[selected_coord]:

            selected_coord = coord

    commands = '%s:*%s ' % (ship, selected_coord)

    return commands


def ai_build_orders(players_entities, board, ai_player, enemy_player):
    """
    Gather every commands string from every ai functions and merge them into one string

    Parameters
    ----------
    players_entities: existing entities of both players (dict)
    board: information about the board (dict)
    ai_player: the id the ai player is (str)
    enemy_player: the id the enemy player is (str)

    Returns
    -------
    complete_command_line: the complete line containing orders for the next turn (str)

    Version
    -------
    Specification: Nicolas Frantz, Aniss Grabsi (v.3 05/05/2018)
    Implementation: Aniss Grabsi (v.3 05/05/2018)
    """

    complete_command_line = ai_purchase_selection(players_entities, board, ai_player)
    complete_command_line += ai_handle_excavators(players_entities, board, ai_player, enemy_player)
    complete_command_line += ai_handle_attackers(players_entities, board, ai_player, enemy_player)

    # Clean unnecessary spaces
    complete_command_line = complete_command_line.strip(' ')

    return complete_command_line

import random
import mining_wars_gr_13 as mw


def generate_command(player, players, ships, asteroids, ship_types, turn, board_width, board_height):
    """Generate a command for the AI.

    Parameters
    ----------
    player: player's information (dict)
    players: players' information (list of dicts)
    ships: ships' information (list of dicts)
    asteroids: asteroids' information (list of dicts)
    ship_types: possible ship types (dict)
    turn: turn number (int)
    board_width,board_height: board's size (ints)

    Returns
    -------
    command: player's command (str)

    Versions
    --------
    specification: Pierre Luycx (v.1 28/04/2018)
    implementation: Alexis Wordui, Pierre Luycx & Sami Quoilin (v.1 28/04/2018)

    """

    command = []

    enemy = players[1] if player['player_n'] == 0 else players[0]

    local_ships = {}
    enemy_ships = {}

    # Get information about every ship
    for name, ship in ships.items():
        if name.endswith(str(player['player_n'])):
            ships_list = local_ships
        else:
            ships_list = enemy_ships

        ships_list[name[:-1]] = {
            'x': ship['x'],
            'y': ship['y'],
            'hp': ship['hp'],
            'ores': ship['ores'],
            'shape': ship['shape'],
            'range': ship['range'],
            'tonnage': ship['tonnage'],
            'type': ship['type'],
            'locked': ship['locked_on'] is not None}

    # Generate buy commands
    # compute total tonnage
    total_tonnage = 0
    for name, ship in local_ships.items():
        total_tonnage += ship['tonnage']

    total_ores_available = 0
    for asteroid in asteroids:
        total_ores_available += asteroid['ores']

    # buy an excavator every 4 turns, else buy an attack ship
    if turn % 4 == 0 and total_tonnage < 0.9 * total_ores_available:
        if total_tonnage < 4:
            ship_type = 'excavator-S'
        elif total_tonnage < 7:
            ship_type = 'excavator-M'
        else:
            ship_type = 'excavator-L'
    elif total_tonnage < 7:
        ship_type = 'scout'
    else:
        ship_type = 'warship'

    # check if we have enough ores
    if player['ores'] >= ship_types[ship_type]['cost']:
        ship_name = generate_ship_name()
        command.append('%s:%s' % (ship_name, ship_type))
        local_ships[ship_name] = {
            'x': player['x'],
            'y': player['y'],
            'hp': ship_types[ship_type]['hp'],
            'ores': 0,
            'shape': ship_types[ship_type]['shape'],
            'range': ship_types[ship_type]['range'],
            'tonnage': ship_types[ship_type]['tonnage'],
            'type': ship_type,
            'locked': False}

    # Generate move/lock/release commands for the excavators
    for name, ship in local_ships.items():
        if ship['type'].startswith('excavator'):

            # lock/release a portal
            if ship['x'] == player['x'] and ship['y'] == player['y']:
                if ship['locked'] and ship['ores'] == 0:
                    command.append('%s:release' % name)
                    ship['locked'] = False

                elif not ship['locked'] and ship['ores'] > 0:
                    command.append('%s:lock' % name)
                    ship['locked'] = True

            # lock/release an asteroid
            for asteroid in asteroids:
                if ship['x'] == asteroid['x'] and ship['y'] == asteroid['y']:
                    if ship['locked'] and (ship['ores'] == ship['tonnage'] or asteroid['ores'] == 0):
                        command.append('%s:release' % name)
                        ship['locked'] = False

                    elif not ship['locked'] and ship['ores'] < ship['tonnage'] and asteroid['ores'] > 0:
                        command.append('%s:lock' % name)
                        ship['locked'] = True

            # move to reach an asteroid or the portal
            if not ship['locked']:
                if ship['ores'] == 0:

                    # find the nearest non empty asteroid
                    nearest_asteroid = None
                    min_distance = -1
                    for asteroid in asteroids:
                        distance = mw.compute_manhattan_distance(ship['x'], ship['y'], asteroid['x'], asteroid['y'])
                        if asteroid['ores'] > 0 and (min_distance == -1 or distance < min_distance):
                            nearest_asteroid = asteroid
                            min_distance = distance

                    if nearest_asteroid is not None:
                        command.append(generate_move_action(name, ship, nearest_asteroid['x'], nearest_asteroid['y']))

                else:
                    command.append(generate_move_action(name, ship, player['x'], player['y']))

    # Generate attack/move commands for the attacking ships
    # get enemy ships near the portal
    enemies_near_portal = []
    for name, ship in enemy_ships.items():
        if not ship['type'].startswith('excavator') and mw.compute_manhattan_distance(player['x'], player['y'],
                                                                                      ship['x'], ship['y']) < 5:
            enemies_near_portal.append(name)

    # for every local ships
    for name, ship in local_ships.items():
        if not ship['type'].startswith('excavator'):

            # get enemies at range
            enemies_at_range = []
            for enemy_name, enemy_ship in enemy_ships.items():
                for x_offset, y_offset in enemy_ship['shape']:
                    x, y = enemy_ship['x'] + x_offset, enemy_ship['y'] + y_offset
                    if mw.compute_manhattan_distance(ship['x'], ship['y'], x, y) <= ship['range']:
                        enemies_at_range.append((enemy_name, x, y))

            # get enemy portal coordinates at range
            portal_at_range = []
            for y in range(enemy['y'] - 2, enemy['y'] + 3):
                for x in range(enemy['x'] - 2, enemy['x'] + 3):
                    if mw.compute_manhattan_distance(ship['x'], ship['y'], x, y) <= ship['range']:
                        portal_at_range.append((x, y))

            # if enemy at range, attack it
            if len(enemies_at_range) > 0:

                # we will check which ship to attack in priority
                ship_already_hit = False
                lowest_hp, lowest_hp_x, lowest_hp_y = 0, 0, 0
                best_type, best_type_x, best_type_y = '', 0, 0

                for enemy_name, x, y in enemies_at_range:
                    enemy_ship = enemy_ships[enemy_name]

                    if enemy_ship['hp'] < ship_types[enemy_ship['type']]['hp']:
                        ship_already_hit = True
                    if lowest_hp == 0 or enemy_ship['hp'] < lowest_hp:
                        lowest_hp, lowest_hp_x, lowest_hp_y = enemy_ship['hp'], x, y
                    if best_type == '' or compare_ship_types(enemy_ship['type'], best_type):
                        best_type, best_type_x, best_type_y = enemy_ship['type'], x, y

                # if a ship is already hit, attack it
                if ship_already_hit:
                    command.append('%s:*%d-%d' % (name, lowest_hp_y, lowest_hp_x))

                # else, attack the most powerful ship
                else:
                    command.append('%s:*%d-%d' % (name, best_type_y, best_type_x))

            # else if enemy portal at range, attack it
            elif len(portal_at_range) > 0:
                x, y = random.choice(portal_at_range)
                command.append('%s:*%d-%d' % (name, y, x))

            # else if enemy near own portal, move to reach it
            elif len(enemies_near_portal) > 0:
                command.append(generate_move_action(name, ship, player['x'], player['y']))

            # else move to enemy portal
            else:
                command.append(generate_move_action(name, ship, enemy['x'], enemy['y']))

    return ' '.join(command)


def generate_move_action(name, ship, x, y):
    """Generate an action to move a ship to reach a given position.

    Parameters
    ----------
    name: ship's name (str)
    ship: ship's information (str)
    x,y: targeted position (ints)

    Returns
    -------
    action: generated action (str)

    Versions
    --------
    specification: Sami Quoilin (v.1 29/04/2018)
    implementation: Sami Quoilin (v.1 29/04/2018)

    """

    if x > ship['x']:
        ship['x'] += 1
    elif x < ship['x']:
        ship['x'] -= 1

    if y > ship['y']:
        ship['y'] += 1
    elif y < ship['y']:
        ship['y'] -= 1

    return '%s:@%d-%d' % (name, ship['y'], ship['x'])


def compare_ship_types(left, right):
    """Tell whether one ship type is more powerful than another one.

    Parameters
    ----------
    left: left operand (str)
    right: right operand (str)

    Returns
    -------
    result: if left > right (bool)

    Versions
    --------
    specification: Pierre Luycx (v.1 28/04/2018)
    implementation: Pierre Luycx (v.1 28/04/2018)

    """

    return (left == 'excavator-M' and right == 'excavator-S') or \
           (left == 'excavator-L' and right in ('excavator-S', 'excavator-M')) or \
           (left == 'scout' and right.startswith('excavator')) or \
           (left == 'warship' and right != 'warship')


def generate_ship_name():
    """Generate random ship name.

    Returns
    -------
    name: generated name (str)

    Versions
    --------
    specification: Alexis Wordui (v.1 02/05/2018)
    implementation: Alexis Wordui (v.1 02/05/2018)

    """

    return random.choice(('evil', 'super', 'fastest', 'dark', 'better', 'big', 'small', 'huge', 'mighty', 'black',
                          'black', 'white', 'red', 'green', 'blue', 'ultra', 'mega', 'hyper', 'incredible')) + \
           random.choice(('Brouette', 'Python', 'Bicycle', 'Frenay', 'Chaise', 'Table', 'Light', 'Troll', 'Dwarf',
                          'Mage', 'Computer', 'Door', 'Sword', 'Cow', 'Rocket', 'Bot', 'Finger', 'Warrior')) + \
           str(random.randint(0, 999))

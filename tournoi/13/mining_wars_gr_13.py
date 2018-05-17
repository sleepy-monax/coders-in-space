import random
import AI_gr_13 as ai
import remote_play


def play_game(board_path, local_ai, remote_id, remote_ip='127.0.0.1', colored_output=True):
    """Start and run the game.

    Parameters
    ----------
    board_path: path to the board's file (str)
    local_ai: whether the local player is an AI (bool)
    remote_id: id of the remote player (1 or 2)
    remote_ip: ip of the remote player (str)
    colored_output: whether the board should be printed in color (bool)

    Versions
    --------
    specification: Pierre Luycx (v.1 23/02/2018)
                   Pierre Luycx (v.2 29/04/2018) - remote play parameters added
    implementation: Sami Quoilin (v.1 09/03/2018)
                    Pierre Luycx (v.2 13/04/2018)
                    Pierre Luycx (v.3 29/04/2018) - remote play added

    """

    ship_types = {
        'scout': {'tonnage': 0, 'hp': 3, 'attack': 1, 'range': 3, 'cost': 3,
                  'shape': ((-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1))},
        'warship': {'tonnage': 0, 'hp': 18, 'attack': 3, 'range': 5, 'cost': 9,
                    'shape': ((-1, -2), (0, -2), (1, -2), (-2, -1), (-1, -1), (0, -1), (1, -1),
                              (2, -1), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (-2, 1),
                              (-1, 1), (0, 1), (1, 1), (2, 1), (-1, 2), (0, 2), (1, 2))},
        'excavator-S': {'tonnage': 1, 'hp': 2, 'attack': 0, 'range': 0, 'cost': 1,
                        'shape': ((0, 0),)},
        'excavator-M': {'tonnage': 4, 'hp': 3, 'attack': 0, 'range': 0, 'cost': 2,
                        'shape': ((0, -1), (-1, 0), (0, 0), (1, 0), (0, 1))},
        'excavator-L': {'tonnage': 8, 'hp': 6, 'attack': 0, 'range': 0, 'cost': 4,
                        'shape': ((0, -2), (0, -1), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (0, 1), (0, 2))}
    }

    players, asteroids, board_width, board_height = load_board(board_path)
    ships = {}

    # connect to remote player
    connection = remote_play.connect_to_player(remote_id, remote_ip)

    # main loop
    turn = 0
    consecutive_non_damage_turn = 0
    playing = True
    while playing:

        # draw the board
        print()
        print('==== MINING WARS ====')
        print('Turn %d' % (turn + 1))
        show_board(players, ships, asteroids, board_width, board_height, colored_output)

        # get players' commands
        commands = []
        for player_i in range(2):
            # local player
            if player_i != remote_id - 1:
                if local_ai:
                    commands.append(ai.generate_command(players[player_i], players, ships, asteroids, ship_types, turn, board_width, board_height))
                    print('Player %d command: %s' % (player_i + 1, commands[-1]))

                else:
                    commands.append(input('Player %d command: ' % (player_i + 1)))

                remote_play.notify_remote_orders(connection, commands[-1])

            # remote player
            else:
                commands.append(remote_play.get_remote_orders(connection))
                print('Player %d command: %s' % (player_i + 1, commands[-1]))

        # handle the commands
        if play_turn(players, ships, asteroids, commands, ship_types, board_width, board_height):
            consecutive_non_damage_turn = 0

            for player in players:
                if player['hp'] == 0:
                    playing = False
                    print('Player %d lose!' % (player['player_n'] + 1))

        else:
            consecutive_non_damage_turn += 1

            if consecutive_non_damage_turn >= 200:
                playing = False
                print('No ship or portal has been hit since 200 turns, it\'s a draw!')

        turn += 1

    print('Game finished in %d turns.' % turn)

    # disconnect from remote player
    remote_play.disconnect_from_player(connection)


def load_board(board_path):
    """Load board infos from a given file.

    Parameters
    ----------
    board_path: path to the board's file (str)

    Returns
    -------
    players: loaded players' infos (list)
    asteroids: loaded asteroids (list)
    board_width: board's width (int)
    board_height: board's height (int)

    Versions
    --------
    specification: Pierre Luycx (v.1 23/02/2018)
                   Pierre Luycx (v.2 08/03/2018) - board's size returns added
                   Sami Quoilin (v.3 09/03/2018) - throws removed
    implementation: Pierre Luycx (v.1 09/03/2018)

    """

    players = []
    asteroids = []
    width, height = 0, 0

    data_type = ''
    with open(board_path, 'r') as file:
        for line in file:
            line = line.rstrip()  # remove the endline with str.rstrip

            if line.endswith(':'):
                data_type = line[:-1]

            else:
                data = [int(number) for number in line.split(' ')]

                if data_type == 'size':
                    width, height = data[1], data[0]
                elif data_type == 'portals':
                    players.append({'x': data[1], 'y': data[0], 'hp': 100, 'ores': 4, 'player_n': len(players), 'locked_ships': []})
                elif data_type == 'asteroids':
                    asteroids.append({'x': data[1], 'y': data[0], 'ores': data[2], 'ores_per_turn': data[3], 'locked_ships': []})

    return players, asteroids, width, height


def play_turn(players, ships, asteroids, commands, ship_types, board_width, board_height):
    """Execute a command played by a player.

    Parameters
    ----------
    players: players playing the commmand (list)
    ships: ships of the player (dict)
    asteroids: asteroids (list)
    commands: player's respective commands (list)
    ship_types: types of ships (dict)
    board_width,board_height: board's size (ints)

    Returns
    -------
    attack_succeeded: whether an attack has succedeed this turn (bool)

    Versions
    --------
    specification: Sami Quoilin (v.1 02/03/2018)
                   Pierre Luycx (v.2 08/03/2018) - board's size and ship_types parameters added
                   Pierre Luycx (v.3 13/04/2018) - attack_succeeded return value added
    implementation: Pierre Luycx (v.1 16/03/2018)

    """

    locked_or_released_ships = []
    moving_or_attacking_ship = []

    moves = []
    attacks = []

    for player_i in range(len(players)):
        if len(commands[player_i]) > 0:
            actions = [command.split(':') for command in commands[player_i].split(' ')]

            for name, action in actions:
                name += str(player_i)
                if action in ship_types:
                    buy(players[player_i], name, action, ships, ship_types)

                elif name not in ships:
                    print('Error: you don\'t own the ship "%s"!' % name[:-1])

                elif action == 'lock':
                    if name in locked_or_released_ships:
                        print('Error: the ship "%s" has already been locked/released!' % name[:-1])
                    elif lock(name, players, ships, asteroids):
                        locked_or_released_ships.append(name)

                elif action == 'release':
                    if name in locked_or_released_ships:
                        print('Error: the ship "%s" has already been locked/released!' % name[:-1])
                    elif release(name, ships):
                        locked_or_released_ships.append(name)

                elif action.startswith('@'):
                    y, x = [int(coord) for coord in action[1:].split('-')]
                    moves.append((name, x, y))

                elif action.startswith('*'):
                    y, x = [int(coord) for coord in action[1:].split('-')]
                    attacks.append((name, x, y))

                else:
                    print('Error: unknown action "%s:%s"!' % (name, action))

    # Move ships
    for name, x, y in moves:
        if name in moving_or_attacking_ship:
            print('Error: the ship "%s" has already moved!' % name[:-1])
        elif move(name, x, y, ships, board_width, board_height):
            moving_or_attacking_ship.append(name)

    # Handle attacks
    at_least_one_attack_succeeded = False
    ships_to_remove = []

    for name, x, y in attacks:
        if name in moving_or_attacking_ship:
            print('Error: the ship "%s" has already moved/attacked!' % name[:-1])
        else:
            success, attack_succeeded, destroyed_ships = attack(name, x, y, players, ships)
            if success:
                moving_or_attacking_ship.append(name)
            if attack_succeeded:
                at_least_one_attack_succeeded = True

            for destroyed_name in destroyed_ships:
                if destroyed_name not in ships_to_remove:
                    ships_to_remove.append(destroyed_name)

    # Release and remove destroyed ships
    for name in ships_to_remove:
        if ships[name]['locked_on'] is not None:
            release(name, ships)

        del ships[name]

    # Harvest the ore
    harvest(players, ships, asteroids)

    return at_least_one_attack_succeeded


def buy(player, name, ship_type, ships, ship_types):
    """Buy a ship of a given type for a player.

    Parameters
    ----------
    player: the player buying the ship (dict)
    name: name given to the ship (str)
    ship_type: name of the ship type being bought (str)
    ships: current ships in the game (dict)
    ship_types: possible ship types (dict)

    Versions
    --------
    specification: Pierre Luycx (v.1 23/02/2018)
                   Pierre Luycx (v.2 05/03/2018) - throws removed
                   Pierre Luycx (v.3 09/03/2018) - ship_types parameter added
    implementation: Alexis Wordui (v.1 15/03/2018)

    """

    if name in ships:
        print('Error: the ship "%s" already exists!' % name[:-1])
    elif ship_type not in ship_types:
        print('Error: ship type "%s" doesn\'t exist!' % ship_type)
    elif player['ores'] < ship_types[ship_type]['cost']:
        print('Error: you don\'t have enough ore to buy the ship "%s"!' % name[:-1])

    else:
        stats = ship_types[ship_type]

        player['ores'] -= stats['cost']
        ships[name] = {'x': player['x'], 'y': player['y'], 'hp': stats['hp'], 'locked_on': None, 'ores': 0,
                       'shape': stats['shape'], 'tonnage': stats['tonnage'], 'attack': stats['attack'],
                       'range': stats['range'], 'type': ship_type}


def lock(name, players, ships, asteroids):
    """Lock a ship.

    Parameters
    ----------
    name: name of the ship that you want to lock (str)
    players: players' informations (list)
    ships: current ships in the game (dict)
    asteroids: asteroids' informations

    Returns
    -------
    success: if no error occurred (bool)

    Versions
    --------
    specification: Alexis Wordui (v.1 23/02/2018)
                   Sami Quoilin (v.2 08/03/2018) - x and y parameters removed
                   Sami Quoilin (v.3 16/03/2018) - ships parameter added
                   Pierre Luycx (v.4 13/04/2018) - players and asteroids parameters added
    implementation: Sami Quoilin (v.1 30/03/2018)
                    Pierre Luycx (v.2 13/04/2018) - possibility to lock a portal added

    """

    ship = ships[name]

    # check if the ship has the ability to lock
    if ship['tonnage'] == 0:
        print('Error: the ship "%s" can\'t be locked!' % name[:-1])
        return False

    elif ship['locked_on'] is not None:
        print('Error: the ship "%s" is already locked!' % name[:-1])
        return False

    else:
        # check if the ship is on any lockable object
        for targets in (asteroids, players):
            for target in targets:
                if ship['x'] == target['x'] and ship['y'] == target['y']:
                    # lock the ship
                    ship['locked_on'] = target
                    target['locked_ships'].append(name)

        return True


def release(name, ships):
    """Release a ship.

    Parameters
    ----------
    name: name of the ship that you want to release (str)
    ships: current ships in the game (dict)

    Returns
    -------
    success: if no error occurred (bool)

    Versions
    --------
    specification: Pierre Luycx (v.1 13/04/2018)
    implementation: Pierre Luycx (v.1 13/04/2018)

    """

    ship = ships[name]

    if ship['locked_on'] is None:
        print('Error: the ship "%s" is not locked!' % name[:-1])
        return False

    else:

        ship['locked_on']['locked_ships'].remove(name)
        ship['locked_on'] = None
        return True


def move(name, x, y, ships, board_width, board_height):
    """Move a ship to a given position.

    Parameters
    ----------
    name: name of the ship that you want to move (str)
    x,y: coordinates that you want to go to (ints)
    ships: current ships on the board
    board_width,board_height: board's size (ints)

    Returns
    -------
    success: if no error occurred (bool)

    Versions
    --------
    specification: Alexis Wordui (v.1 23/02/2018)
                   Pierre Luycx (v.2 08/03/2018) - board's size parameters added
                   Pierre Luycx (v.3 09/03/2018) - ships parameter added
    implementation: Pierre Luycx (v.1 09/03/2018)

    """

    ship = ships[name]

    if ship['locked_on'] is not None:
        print('Error: the locked ship "%s" can\'t move!' % name[:-1])
        return False

    elif x < ship['x'] - 1 or x > ship['x'] + 1 or y < ship['y'] - 1 or y > ship['y'] + 1:
        print('Error: the ship "%s" can\'t move that far!' % name[:-1])
        return False

    else:
        in_bounds = True
        for x_offset, y_offset in ship['shape']:
            if x + x_offset <= 0 or x + x_offset > board_width or y + y_offset <= 0 or y + y_offset > board_height:
                in_bounds = False
                print('Error: the ship "%s" can\'t go outside of the board\'s bounds!' % name[:-1])

        if in_bounds:
            ship['x'] = x
            ship['y'] = y

        return True


def attack(name, x, y, players, ships):
    """Attack a ship or a portal at a given position.

    Parameters
    ----------
    name: name of the ship wich want attack, must be warship (str)
    x,y: coordinates that you want to attack (ints)
    players: players' informations (list)
    ships: current ships in the game (dict)

    Returns
    -------
    success: if no error occurred (bool)
    attack_succeeded: whether the attack succedeed (bool)
    destroyed_ships: destroyed ship's names (list)

    Versions
    --------
    specification: Alexis Wordui (v.1 23/02/2018)
                   Alexis Wordui (v.2 09/03/2018) - players and ships parameters added
                   Sami Quoilin (v.3 15/03/2018) - returns clause removed
                   Pierre Luycx (v.4 13/04/2018) - attack_succeeded return value added
    implementation: Sami Quoilin (v.1 15/03/2018)
                    Pierre Luycx (v.1 30/03/2018) - check if a portal is hit

    """

    ship = ships[name]
    attack_succeeded = False

    if ship['attack'] == 0:
        print('Error: the ship "%s" can\'t attack!' % name[:-1])
        return False, False, []

    elif ship['range'] < compute_manhattan_distance(ship['x'], ship['y'], x, y):
        print('Error: the ship "%s" can\'t shoot that far!' % name[:-1])
        return False, False, []

    else:

        # Check if a portal is hit
        for player in players:
            if x >= player['x'] - 2 and x <= player['x'] + 2 and y >= player['y'] - 2 and y <= player['y'] + 2:
                player['hp'] -= ship['attack']
                if player['hp'] < 0:
                    player['hp'] = 0

                attack_succeeded = True
                print('Player %d\'s portal has been hit and it has %d hp left!' % (player['player_n'] + 1, player['hp']))

        # Check if a ship is hit
        destroyed_ships = []
        for targeted_ship_name, targeted_ship in ships.items():
            for x_offset, y_offset in targeted_ship['shape']:
                if x == targeted_ship['x'] + x_offset and y == targeted_ship['y'] + y_offset:
                    targeted_ship['hp'] -= ship['attack']
                    if targeted_ship['hp'] <= 0:
                        targeted_ship['hp'] = 0
                        destroyed_ships.append(targeted_ship_name)

                    attack_succeeded = True
                    print('The ship "%s" has been hit, it has %d hp left!' % (targeted_ship_name[:-1], targeted_ship['hp']))

    return True, attack_succeeded, destroyed_ships


def harvest(players, ships, asteroids):
    """Move ores from asteroids to extractors and from extractors to portals.

    Parameters
    ----------
    players: players' information (list)
    ships: ships' information (dict)
    asteroids: asteroids' information (list)

    Versions
    --------
    specification: Alexis Wordui (v.1 08/03/2018)
    implementation: Alexis Wordui (v.1 08/03/2018)

    """

    for asteroid in asteroids:
        ores_available = asteroid['ores']
        ores_per_ship = asteroid['ores_per_turn']
        n_ships = len(asteroid['locked_ships'])

        if n_ships * ores_per_ship > ores_available:
            ores_per_ship = ores_available / n_ships

        harvesting_ships = asteroid['locked_ships'].copy()

        while len(harvesting_ships) > 0 and ores_available > 0:
            full_ships = []

            for name in harvesting_ships:
                ship = ships[name]

                ores_harvested = min(ores_per_ship, ship['tonnage'] - ship['ores'])
                ores_available -= ores_harvested

                ship['ores'] += ores_harvested
                if ship['ores'] == ship['tonnage']:
                    full_ships.append(name)

            for name in full_ships:
                harvesting_ships.remove(name)

        if ores_available < 0:  # can happen with float operations
            asteroid['ores'] = 0
        else:
            asteroid['ores'] = ores_available

    for player in players:
        for name in player['locked_ships']:
            ship = ships[name]

            player['ores'] += ship['ores']
            ship['ores'] = 0


def show_board(players, ships, asteroids, width, height, colored_output=False):
    """Display the board on the screen.

    Parameters
    ----------
    players: portals to display (list)
    ships: ships to display (dict)
    asteroids: asteroids to display (list)
    width: the width of the board (int)
    height: the width of the board (int)
    colored_output: whether the output should be colored (bool)

    Versions
    --------
    specification: Pierre Luycx (v.1 23/02/2018)
                   Alexis Wordui (v.2 16/03/2018) - description of player parameters changed
                   Alexis Wordui (v.3 30/03/2018) - width and height parameters added
    implementation: Pierre Luycx (v.1 30/03/2018)
                    Pierre Luycx (v.2 29/04/2018) - show_player_information merged

    """

    if colored_output:
        colors = ['\u001b[34m', '\u001b[31m']
        reset_color = '\u001b[0m'
    else:
        colors = ['', '']
        reset_color = ''

    board = []
    for x in range(width):
        board.append([])
        for x in range(height):
            board[-1].append('.')

    # draw portals
    for player in players:
        for y in range(player['y'] - 3, player['y'] + 2):
            for x in range(player['x'] - 3, player['x'] + 2):
                board[x][y] = colors[player['player_n']] + 'o' + reset_color

    # draw ships
    for name, ship in ships.items():
        for x_offset, y_offset in ship['shape']:
            board[ship['x'] + x_offset - 1][ship['y'] + y_offset - 1] = colors[int(name[-1])] + '#' + reset_color

    # draw asteroids
    for asteroid in asteroids:
        board[asteroid['x'] - 1][asteroid['y'] - 1] = '*'

    # render the board
    for y in range(height):
        for x in range(width):
            print(board[x][y], end='')
        print()  # new line

    # show players information
    for player in players:
        print('%sPlayer %d%s: %d hp, %d ores' % (colors[player['player_n']], player['player_n'] + 1, reset_color, player['hp'], player['ores']))

        for name, ship in ships.items():
            if name.endswith(str(player['player_n'])):
                print('- %s "%s%s%s" %d-%d: %d hp, %d ores' % (ship['type'], colors[player['player_n']], name[:-1], reset_color, ship['y'], ship['x'], ship['hp'], ship['ores']))


def compute_manhattan_distance(x1, y1, x2, y2):
    """Compute distance between two coordinates.

    Parameters
    ----------
    x1,y1: first coordinates (ints)
    x2,y2: second coordinates (ints)

    Returns
    -------
    distance: distance between the coordinates (int)

    Versions
    --------
    specification: Pierre Luycx (v.1 08/03/2018)
    implementation: Pierre Luycx (v.1 08/03/2018)

    """

    return abs(x2 - x1) + abs(y2 - y1)


def generate_naive_command(player, players, ships, asteroids, ship_types, board_width, board_height):
    """Generate a naive random command for the IA.

    Parameters
    ----------
    player: player's information (dict)
    players: players (list)
    ships: ships' information (dict)
    asteroids: asteroids' information (list)
    ship_types: possible ship types (dict)
    board_width,board_height: board's size (ints)

    Returns
    -------
    command: generated command (str)

    Notes
    -----
    This function is unused since the definitive AI is implemented.

    Versions
    --------
    specification: Pierre Luycx (v.1 02/03/2018)
                   Pierre Luycx (v.2 08/03/2018) - board's size parameters added
    implementation: Pierre Luycx (v.1 30/03/2018)
                    Sami Quoilin (v.2 15/04/2018) - check for illegal actions

    """

    command = []

    # Get information about every ship of the player
    local_ships = {}
    for name, ship in ships.items():
        if name.endswith(str(player['player_n'])):
            local_ships[name[:-1]] = {
                'x': ship['x'],
                'y': ship['y'],
                'shape': ship['shape'],
                'range': ship['range'],
                'type': ship['type'],
                'locked': ship['locked_on'] is not None}

    # Buy new ships
    ores = player['ores']
    while ores > 0:
        name = 'ship%d' % random.randint(0, 9999)
        ship_type, cost = get_random_ship_type(ores, ship_types)

        ores -= cost
        local_ships[name] = {
            'x': player['x'],
            'y': player['y'],
            'shape': ship_types[ship_type]['shape'],
            'range': ship_types[ship_type]['range'],
            'type': ship_type,
            'locked': False}

        command.append('%s:%s' % (name, ship_type))

    # Lock/release ships
    for name, ship in local_ships.items():
        if ship['type'].startswith('excavator') and random.randint(0, 1):
            for targets in (players, asteroids):
                for target in targets:
                    if ship['x'] == target['x'] and ship['y'] == target['y']:
                        command.append('%s:%s' % (name, 'release' if ship['locked'] else 'lock'))
                        ship['locked'] = not ship['locked']

    # Move or attack
    for name, ship in local_ships.items():
        dice = random.randint(0, 2)
        if dice == 0:
            if not ship['locked'] and random.randint(0, 1):
                x, y = ship['x'] + random.randint(-1, 1), ship['y'] + random.randint(-1, 1)

                movable = True
                for x_offset, y_offset in ship['shape']:
                    if x + x_offset <= 0 or x + x_offset > board_width or y + y_offset <= 0 or y + y_offset > board_height:
                        movable = False

                if movable:
                    ship['x'], ship['y'] = x, y
                    command.append('%s:@%d-%d' % (name, y, x))

        elif dice == 1:
            if not ship['type'].startswith('excavator') and random.randint(0, 1):
                x, y = ship['x'], ship['y']

                area_at_range = []
                for board_y in range(board_height):
                    for board_x in range(board_width):
                        if compute_manhattan_distance(x, y, board_x, board_y) <= ship['range']:
                            area_at_range.append((board_x, board_y))

                x, y = random.choice(area_at_range)
                command.append('%s:*%d-%d' % (name, y, x))

    return ' '.join(command)


def get_random_ship_type(n_ores, ship_types):
    """Return which type of ship to buy given our amount of ores.

    Parameters
    ----------
    n_ores: player's amount of ores (int)
    ship_types: ship's types (dict)

    Returns
    ------
    type: type of ship to buy (str)
    cost: price of the ship (int)

    Notes
    -----
    This function is unused since the definitive AI is implemented.

    Versions
    --------
    specification: Sami Quoilin (v.1 15/04/2018)
    implementation: Sami Quoilin (v.1 15/04/2018)

    """

    if n_ores >= ship_types['warship']['cost']:
        ship_type = random.choice(('scout', 'warship', 'excavator-S', 'excavator-M', 'excavator-L'))
    elif n_ores >= ship_types['excavator-L']['cost']:
        ship_type = random.choice(('scout', 'excavator-S', 'excavator-M', 'excavator-L'))
    elif n_ores >= ship_types['scout']['cost']:
        ship_type = random.choice(('scout', 'excavator-S', 'excavator-M',))
    elif n_ores >= ship_types['excavator-M']['cost']:
        ship_type = random.choice(('excavator-S', 'excavator-M'))
    elif n_ores >= ship_types['excavator-S']['cost']:
        ship_type = 'excavator-S'
    else:
        return '', 0

    cost = ship_types[ship_type]['cost']

    return ship_type, cost

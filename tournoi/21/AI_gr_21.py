import math
import random

# Utils - Distances and positions


def get_distance(ax, ay, bx, by):
    """ Returns the distances between two locations: a and b

    Parameters:
    -----------
    ax: X position of a (int)
    ay: Y position of a (int)
    bx: X position of b (int)
    by: Y position of b (int)

    Returns
    -------
    distances: The X, Y, and Manhattan distance between the two locations (tuple)

    Note
    ----
    - x_distance: The X distance (int)
    - y_distance: The Y distance (int)
    - manhattan_distance: The distance of Manhattan (float)

    Version
    -------
    specification: Poitier Pierre (v.1 04/03/18)
    implementation: Poitier Pierre (v.1 14/03/18)
    """

    x_distance = math.fabs(ax - bx)
    y_distance = math.fabs(ay - by)
    manhattan_distance = math.fabs(bx - ax) + math.fabs(by - ay)

    return x_distance, y_distance, manhattan_distance


def get_distance_between_entities(first_entity, second_entity):
    """ Returns the distances between two entities

    Parameters
    ----------
    first_entity: The first entity (dict)
    second_entity: The second entity (dict)

    Returns
    -------
    distances: The tuple of the distance (tuple)

    Notes
    -----
    An entity is a dictionary with these keys: position_x, and position_y

    The returned tuple has this structure:
        - x_distance: The distance between the two entities on the X axis (int)
        - y_distance: The distance between the two entities on the Y axis (int)
        - distance: Manhattan distance between the two entities (float)

    Version
    -------
    specification: Killian Thys, Poitier Pierre (v.1->v.2 04/03/18)
    implementation: Poitier Pierre (v.1 19/03/18)
    """

    return get_distance(
        first_entity['position_x'],
        first_entity['position_y'],
        second_entity['position_x'],
        second_entity['position_y']
    )


def get_distance_ship_location(ship, x, y):
    """ Get the distances between a ship and a specified location

    Parameters
    ----------
    ship: The concerned ship (dict)
    x: The X position of the location (int)
    y: The Y position of the location (int)

    Returns
    -------
    distances: The X, Y, and Manhattan distance between the ship and the location (tuple)

    Version
    -------
    specification: Poitier Pierre (v.1 04/03/18)
    implementation: Poitier Pierre (v.1 14/03/18)
    """

    return get_distance(ship['position_x'], ship['position_y'], x, y)


def collide_at(ship_types, blue_ships, red_ships, position_x, position_y):
    """ Returns the ships which we collide in a specified position

    Parameters
    ----------
    ship_types: The different types of ships in the game (dict)
    blue_ships: The blue player's ships (dict)
    red_ships: The red player's ships (dict)
    position_x: The X position (int)
    position_y: the Y position (int)

    Returns
    -------
    hit_ships: The ships we collide in the position (tuple)

    Note
    ----
    The hit_ships tuple contains two lists: the blue hit ships, and the red hit ships

    We do a distinction between the two teams for the AI

    Version
    -------
    specification: Poitier Pierre (v.1 20/03/18)
    implementation: Poitier Pierre (v.1 20/03/18)
    """

    hit_ships = ([], [])

    for ship_name in blue_ships:

        ship = blue_ships[ship_name]
        distances = get_distance_ship_location(ship, position_x, position_y)

        # Check if the ship is close enough to have a possibility of collision
        if distances[0] < 3 and distances[1] < 3:

            # Convert the position from the board to the hit box
            hit_box_x = position_x - ship['position_x'] + 2
            hit_box_y = position_y - ship['position_y'] + 2

            # Check if we collide or not

            hit_state = ship_types[ship['type']]['hit_box'][hit_box_y][hit_box_x]

            if hit_state == 'a':
                hit_ships[0].append(ship_name)

    # Repeat the operation for the other team
    for ship_name in red_ships:
        ship = red_ships[ship_name]
        distances = get_distance_ship_location(ship, position_x, position_y)

        if distances[0] < 3 and distances[1] < 3:

            hit_box_x = position_x - ship['position_x'] + 2
            hit_box_y = position_y - ship['position_y'] + 2

            hit_state = ship_types[ship['type']]['hit_box'][hit_box_y][hit_box_x]

            if hit_state == 'a':
                hit_ships[1].append(ship_name)

    return hit_ships


# Utils -- AI


def find_interesting_asteroids(ship, aggressive_rival_ships, ship_types, asteroids):
    """ Finds the interesting asteroids for the designated ship

    Parameters
    ----------
    ship: The ship we want to find asteroids for (dict)
    aggressive_rival_ships: The rival player's aggressive ships (dict)
    ship_types: The different ship types (dict)
    asteroids: The asteroids of the game (dict)

    Returns
    -------
    interesting_asteroids: The name of the most interesting asteroids for the designated ship (list containing str)

    Note
    ----
    The ship must be an excavator

    The "interesting" asteroids are selected according to these factors:
        - Rival ships can shoot on the asteroid (Priority 1)
        - Enough ores to fill the ship (Priority 2)
        - Rival ships nearby the asteroid (Priority 3)

    In case of emergency, the ship uses the priorities to choose at least 1/3 of the asteroids (up-rounded)

    Version
    -------
    specification: Killian Thys (v.1 01/03/18)
    implementation: Pierre Poitier, Killian Thys (v.1 26/04/18)
    """

    interesting_asteroids = []

    # These asteroids can be shot by a rival ship
    attackable_asteroids = []
    # These asteroids are not able to fill the stock of the ship
    poor_asteroids = []
    # These asteroids are near a rival ship
    dangerous_area_asteroids = []

    for asteroid_name in asteroids:

        asteroid = asteroids[asteroid_name]

        asteroid_x = asteroid['position_x']
        asteroid_y = asteroid['position_y']

        is_interesting = True

        if asteroid['ores'] < (ship_types[ship['type']]['weight'] - ship['carried_ores']):
            is_interesting = False
            poor_asteroids.append(asteroid_name)

        for rival_ship_name in aggressive_rival_ships:

            rival_ship = aggressive_rival_ships[rival_ship_name]

            distance = get_distance_ship_location(rival_ship, asteroid_x, asteroid_y)[2]

            rival_ship_range = ship_types[rival_ship['type']]['range']

            if distance <= rival_ship_range:
                is_interesting = False
                attackable_asteroids.append(asteroid_name)

            elif distance <= rival_ship_range + 3:
                is_interesting = False
                dangerous_area_asteroids.append(asteroid_name)

        if is_interesting:
            interesting_asteroids.append(asteroid_name)

    if len(interesting_asteroids) == 0:
        interesting_asteroids += dangerous_area_asteroids

    if len(interesting_asteroids) == 0:
        interesting_asteroids += poor_asteroids

    return list(set(interesting_asteroids))


def choose_best_asteroid(excavator_ship, interesting_asteroids, asteroids, ally_portal, rival_portal, nearby='self'):
    """ Chooses the best asteroid from a list of interesting asteroids

    Parameters
    ----------
    excavator_ship: The excavator which chooses an asteroid (dict)
    interesting_asteroids: The interesting asteroids for a ship (list)
    asteroids: All the asteroids on the map (dict)
    ally_portal: The ally portal data (dict)
    rival_portal: The rival portal data (dict)
    nearby: The element we want to be closer to (str, optional, default='self')

    Returns
    -------
    coordinates: The coordinates of the asteroid (str), or None if there is not any interesting

    Raise
    -----
    ValueError if the value of nearby is invalid

    Note
    -----
    The ship must have this key: 'interesting_asteroids'

    'nearby' can be:
        (closer to the ship which chooses an asteroid)
        - self
        (or closer to a portal)
        - ally_portal
        - rival_portal

    Chooses an asteroid according to:
        - distance
        - mining speed

    The returned coordinates of the asteroid have this structure: x_y

    Version
    -------
    specification: Killian Thys, Poitier Pierre (v.2 24/03/18)
    implementation: Pierre Poitier (v.1 26/04/18)
    """

    interesting_asteroids_names = interesting_asteroids

    if len(interesting_asteroids_names) > 0:

        # Define the position of the target we want to be closer to

        if nearby == 'self':

            target_x = excavator_ship['position_x']
            target_y = excavator_ship['position_y']

        elif nearby == 'ally_portal':

            target_x = ally_portal['position_x']
            target_y = ally_portal['position_y']

        elif nearby == 'rival_portal':

            target_x = rival_portal['position_x']
            target_y = rival_portal['position_y']

        else:
            raise ValueError('The value nearby has an invalid value !')

        # Get the first asteroid and use it as default choice

        closer_asteroid_name = interesting_asteroids[0]
        closer_asteroid = asteroids[closer_asteroid_name]
        min_distance = get_distance_ship_location(closer_asteroid, target_x, target_y)[2]

        # Get the asteroid which is the closest of the target

        for asteroid_name in interesting_asteroids_names:

            asteroid = asteroids[asteroid_name]

            distance = get_distance_ship_location(asteroid, target_x, target_y)[2]

            if distance < min_distance:
                closer_asteroid_name = asteroid_name
                closer_asteroid = asteroid
                min_distance = distance

        # Check if there is a more interesting asteroid not too far, according to the ores per turn

        best_ores_per_turn = closer_asteroid['ores_per_turn']
        more_interesting_asteroid_name = ''

        for asteroid_name in interesting_asteroids_names:

            asteroid = asteroids[asteroid_name]
            asteroid_ores_per_turn = asteroid['ores_per_turn']

            distance = get_distance_ship_location(asteroid, target_x, target_y)[2]

            if distance < min_distance + 5 and asteroid_ores_per_turn > best_ores_per_turn:
                more_interesting_asteroid_name = asteroid_name
                best_ores_per_turn = asteroid_ores_per_turn

        if more_interesting_asteroid_name == '':
            return closer_asteroid_name
        else:
            return more_interesting_asteroid_name

    else:

        return None


def can_attack_next_turn(ship, ship_types, position_x, position_y):
    """ Check if the ship can attack a specified position at the next turn

    Parameters
    ----------
    ship: The ship which is able to attack at the next turn (dict)
    ship_types: The different types of ship in the game (dict)
    position_x: The checked X position (int)
    position_y: The checked Y position (int)

    Returns
    ------
    can_attack: True if the ship can attack this position at the next turn, otherwise False

    Note
    ----
    The ship must be able to attack

    Version
    -------
    specification: Pierre Poitier, Killian Thys (v.1 26/04/18)
    implementation: Pierre Poitier (v.1 01/05/18)
    """

    ship_range = ship_types[ship['type']]['range']

    distances = get_distance_ship_location(ship, position_x, position_y)

    if distances[2] <= ship_range + 1:
        return True
    else:
        return False


def is_safe_next_turn(ship_pos_x, ship_pos_y, ship_type, ship_types, rival_aggressive_ships):
    """ Check if a ship, at the next turn, is safe or not

    Parameters
    ----------
    ship_pos_x: The X position of the ship (int)
    ship_pos_y: The Y position of the ship (int)
    ship_type: The type of the ship (str)
    ship_types: The different types of ships (dict)
    rival_aggressive_ships: The aggressive ships of the rival (dict)

    Returns
    -------
    is_safe: True if the ship is safe, otherwise False (bool)
    dangerous_ship: All the rival ships which can attack our ship (list)
    """

    is_safe = True

    if rival_aggressive_ships:
        ship_hit_box = ship_types[ship_type]['hit_box']

        dangerous_ships = []

        for rival_ship_name in rival_aggressive_ships:
            rival_ship = rival_aggressive_ships[rival_ship_name]

            is_safe = True

            for x in range(ship_pos_x - 2, ship_pos_x + 3):
                for y in range(ship_pos_y - 2, ship_pos_y + 3):

                    if (
                            ship_hit_box[y - ship_pos_y + 2][x - ship_pos_x + 2] == 'a' and
                            can_attack_next_turn(rival_ship, ship_types, x, y)
                    ):
                        dangerous_ships.append(rival_ship_name)
                        is_safe = False

    else:
        is_safe = True
        dangerous_ships = {}

    return is_safe, dangerous_ships


def ship_go_to(ship, rival_aggressive_ships, ship_types, destination_x, destination_y, map_properties):
    """ Sets the next position of the ship, according to its destination and the rival ships

    Parameters
    ----------
    ship: The ship which wants to reach its destination (dict)
    rival_aggressive_ships: All the rival aggressive ships (dict)
    ship_types: The different types of ships (dict)
    destination_x: The X coordinate of the destination of the ship (int)
    destination_y: The Y coordinate of the destination of the ship (int)
    map_properties: The rows and columns of the map [rows(int), columns(int)] (tuple)

    Returns
    -------
    ship_next_x_position: The next X position of the ship (int) or None if the ship has reached its destination
    ship_next_y_position: The next Y position of the ship (int) or None if the ship has reached its destination

    Note
    ----
    The ship try to avoid aggressive ships

    Version
    -------
    specification: Thiry Renaud, Poitier Pierre (v.1 23/04/18)
    specification: Poitier Pierre (v.1 23/04/18)
    """

    ship_x = ship['position_x']
    ship_y = ship['position_y']

    ship_type = ship['type']

    if ship_x != destination_x or ship_y != destination_y:

        move_x = 0
        move_y = 0

        # Look at the next position of the ship

        if destination_x > ship_x:
            move_x = 1
        elif destination_x < ship_x:
            move_x = -1

        if destination_y > ship_y:
            move_y = 1
        elif destination_y < ship_y:
            move_y = -1

        next_pos_x = ship_x + move_x
        next_pos_y = ship_y + move_y

        # If the next position is not safe, try to find a better one

        if not is_safe_next_turn(next_pos_x, next_pos_y, ship_type, ship_types, rival_aggressive_ships)[0]:

            next_pos_x = ship_x
            next_pos_y = ship_y

            best_position_destination_dist = 0

            last_position_y = map_properties[0]
            last_position_x = map_properties[1]

            for y in range(ship_y - 1, ship_y + 2):
                for x in range(ship_x - 1, ship_x + 2):

                    distances = get_distance(x, y, destination_x, destination_y)

                    if (
                        0 < x < last_position_x and
                        0 < y < last_position_y and
                        (distances[2] < best_position_destination_dist or best_position_destination_dist == 0) and
                        is_safe_next_turn(x, y, ship_type, ship_types, rival_aggressive_ships)[0]
                    ):
                        best_position_destination_dist = distances[2]

                        next_pos_x = x
                        next_pos_y = y

        return next_pos_x, next_pos_y

    else:

        ship['action'] = (None, )

        return None, None


# Utils - IA

def generate_ship_name(ships, future_ships):
    """ Generate a random name for a ship

    Parameter
    ---------
    ships: Already existing ships (dict)
    future_ships: the future ships (dict)

    Returns
    -------
    ship_name: The random name for a ship (str)

    Version
    -------
    specification: Poitier Pierre (v.1 23/03/18)
    implementation: Poitier Pierre, Thys Killian (v.1 23/03/18)
    """

    ship_name = ''

    available_characters = list('ABCDEFGHIJKLMNOPQRSTUVXYZ')

    for n in range(random.randint(3, 6)):
        ship_name += available_characters[random.randint(0, len(available_characters) - 1)]

    while (ship_name in ships) or (ship_name in future_ships):
        ship_name += available_characters[random.randint(0, len(available_characters) - 1)]

    return ship_name


def add_buy_command(current_command, ship_name, ship_type, ally_portal, ship_types, asteroids, future_ships):
    """ Add to the current command a buy action

    Parameters
    ----------
    current_command: The current command (str)
    ship_name: The name of the bought ship (str)
    ship_type: The type of ship (str)
    ally_portal: the ally portal (dict)
    ship_types: all types of ship (dict)
    asteroids: all asteroids (dict)
    future_ships: all ships that will be bought next turn (dict)

    Returns
    -------
    actualized_command: The command with the buy action (str)

    Version
    -------
    specification: Poitier Pierre (v.1 23/03/18)
    implementation: Poitier Pierre, Thys Killian (v.1 23/03/18)
    """

    create_future_ship_data(ship_name, ally_portal, ship_type, ship_types, asteroids, future_ships)

    return current_command + ' ' + ship_name + ':' + ship_type


def add_move_command(current_command, ship_name, destination_x, destination_y):
    """ Add to the current command a move action

    Parameters
    ----------
    current_command: The current command (str)
    ship_name: The name of the moving ship (str)
    destination_x: The X position of destination (int)
    destination_y: The Y position of destination (int)

    Returns
    -------
    actualized_command: The command with the move action (str)

    Version
    -------
    specification: Poitier Pierre (v.1 23/03/18)
    implementation: Poitier Pierre, Thys Killian (v.1 23/03/18)
    """

    if destination_x is None or destination_y is None:
        return current_command

    else:
        return current_command + ' ' + ship_name + ':@' + str(destination_y) + '-' + str(destination_x)


def add_attack_command(current_command, ship_name, target_x, target_y):
    """ Add to the current command an attack action

    Parameters
    ----------
    current_command: The current command (str)
    ship_name: The name of the attacking ship (str)
    target_x: The X targeted position (int)
    target_y: The Y targeted position (int)

    Returns
    -------
    actualized_command: The command with the attack action (str)

    Version
    -------
    specification: Poitier Pierre (v.1 23/03/18)
    implementation: Poitier Pierre, Thys Killian (v.1 23/03/18)
    """

    return current_command + ' ' + ship_name + ':*' + str(target_y) + '-' + str(target_x)


def add_lock_command(current_command, ship_name):
    """ Add to the current command a lock action

    Parameters
    ----------
    current_command: The current command (str)
    ship_name: The name of the locking ship (str)

    Returns
    -------
    actualized_command: The command with the lock action (str)

    Version
    -------
    specification: Poitier Pierre (v.1 23/03/18)
    implementation: Poitier Pierre, Thys Killian (v.1 23/03/18)
    """

    return current_command + ' ' + ship_name + ':lock'


def add_release_command(current_command, ship_name):
    """ Add to the current command a release action

    Parameters
    ----------
    current_command: The current command (str)
    ship_name: The name of the releasing ship (str)

    Returns
    -------
    actualized_command: The command with the release action (str)

    Version
    -------
    specification: Poitier Pierre (v.1 23/03/18)
    implementation: Poitier Pierre, Thys Killian (v.1 23/03/18)
    """

    return current_command + ' ' + ship_name + ':release'


def separate_aggressive_passive_ships(ships):
    """ Returns two dictionaries, one with the aggressive ships, and another with the passive ships

    Parameter
    ---------
    ships: All the ships, aggressive ones and passive ones (dict)

    Returns
    -------
    aggressive_ships: All the aggressive ships (dict)
    passive_ships: All the passive ships (dict)

    Version
    -------
    specification: Thiry Renaud, Poitier Pierre (v.1 23/04/18)
    implementation: Thiry Renaud (v.1 23/04/18)
    """

    aggressive_ships = {}
    passive_ships = {}

    for ship_name in ships:
        ship = ships[ship_name]
        ship_type = ship['type']

        # Only excavators are passive
        if ship_type.startswith('excavator'):
            passive_ships[ship_name] = ship
        else:
            aggressive_ships[ship_name] = ship

    return aggressive_ships, passive_ships


def get_buyable_ships(ores, ship_types):
    """ Returns the buyable ships

    Parameter
    ---------
    ores: The player's ores (int)
    ship_types: The different kinds of ships (dict)

    Returns
    -------
    buyable_ships: All the buyable ships (dict)

    Note
    ----
    Buyable ships has as keys each type of ships, associated to the amount of them we can buy

    Version
    -------
    specification: Poitier Pierre (v.1 23/04/18)
    specification: Thiry Renaud, Poitier Pierre (v.1 23/04/18)
    """

    buyable_ships = {}

    for type_name in ship_types:
        if ores != 0:
            buyable_ships[type_name] = ship_types[type_name]['price'] // ores
        else:
            buyable_ships[type_name] = 0

    return buyable_ships


def add_action_to_ship(ai_memory, ship_name, ship_type, action_type, action):
    """ Adds an action to a specified ship

    Parameters
    ----------
    ai_memory: The memory of the AI (dict)
    ship_name: The name of the ship that gets the action (str)
    ship_type: The type of the ship (str)
    action_type: The type of the action (str)
    action: The action to do (tuple)

    Raises
    ------
    ValueError if the action type does not exist

    Notes
    -----
    The different types of actions are:
        - move: Move to a specified location [x, y] (tuple)
        - back: Back to the portal [True/False, None] (tuple)

        (excavators only)
        - mine: Want to mine a specified asteroid [True/False, None] (tuple)

        (aggressive ships only)
        - attack: Want to attack a specified ship [ship_name, None] (tuple)

    Version
    -------
    specification: Thys Killian, Poitier Pierre (v.1 23/04/18)
    specification: Thiry Renaud, Thys Killian, Poitier Pierre (v.1 23/04/18)
    """

    if ship_name not in ai_memory['actions']:
        ai_memory['actions'][ship_name] = {'move': (None, None), 'back': (None, None)}

        if ship_type.startswith('excavator'):
            ai_memory['actions'][ship_name]['mine'] = (None, None)

        else:
            ai_memory['actions'][ship_name]['attack_ship'] = (None, None)
            ai_memory['actions'][ship_name]['attack_portal'] = (None, None)

    if (
            action_type == 'move' or
            action_type == 'back' or
            action_type == 'mine' or
            action_type == 'attack_ship' or
            action_type == 'attack_portal'
    ):
        ai_memory['actions'][ship_name][action_type] = action

    else:
        raise ValueError('The action type %s does not exist !' % action_type)


def create_future_ship_data(ship_name, ally_portal, ship_type, ship_types, asteroids, future_ships):
    """ Create the data of a future ship

    Parameters
    ----------
    ship_name: The name of the future ship (str)
    ally_portal: The ally portal (dict)
    ship_type: The type of the future ship (str)
    ship_types: The different types of ships in the game (dict)
    asteroids: All the asteroids on the map (dict)
    future_ships: All the future ships (dict)

    Raises
    ------
    ValueError if the type of the ship does not exist

    Note
    ----
    The future ships are simulated, but not yet on the board

    Version
    -------
    specification: Thys Killian (v.1 23/04/18)
    specification: Thiry Renaud (v.1 23/04/18)
    """

    if ship_type in ship_types:

        ship_type_data = ship_types[ship_type]

        ship_data = {
            'position_x': ally_portal['position_x'],
            'position_y': ally_portal['position_y'],
            'life': ship_type_data['life'],
            'type': ship_type
        }

        if ship_type.startswith('excavator'):
            ship_data['locked'] = False
            ship_data['carried_ores'] = 0.0
            ship_data['interesting_asteroids'] = find_interesting_asteroids(ship_data, {}, ship_types, asteroids)

        future_ships[ship_name] = ship_data

    else:
        raise ValueError('Unknown type of ship: %s' % ship_type)


def evaluate_capacities(
        ally_ships,
        rival_ships,
        ship_types,
        buyable_ally_ships,
        buyable_rival_ships
):
    """ Evaluates the capacities of both teams

    Parameters
    ----------
    ally_ships: All the ally ships (dict)
    rival_ships: All the rival ships (dict)
    ship_types: The different ship types (dict)
    buyable_ally_ships: The ally buyable ships (dict)
    buyable_rival_ships: The rival buyable ships (dict)

    Returns
    -------
    capacities: The capacities of both teams (dict)

    Note
    ----
    The capacities are:
    - offensive capacities (sum of attack of all the ships of each team)
    - mining capacities (sum of weight of all the ships of each team)

    The capacities structure looks like this:

    capacities:
        ally:
            - offensive
            - mining
        rival:
            - offensive
            - mining

    Version
    -------
    specification: Thiry Renaud, Thys Killian, Poitier Pierre (v.1 01/05/18)
    specification: Thiry Renaud, Thys Killian, Poitier Pierre (v.1 01/05/18)
    """

    capacities = {
        'ally': {
            'offensive': 0,
            'mining': 0
        },
        'rival': {
            'offensive': 0,
            'mining': 0
        }
    }

    # Calculate the capacities of the existing ships

    for ship_name in ally_ships:

        ship = ally_ships[ship_name]
        ship_type = ship['type']

        if ship_type == 'scout' or ship_type == 'warship':
            capacities['ally']['offensive'] += ship_types[ship_type]['attack']
        else:
            capacities['ally']['mining'] += ship_types[ship_type]['weight']

    for ship_name in rival_ships:

        ship = rival_ships[ship_name]
        ship_type = ship['type']

        if ship_type == 'scout' or ship_type == 'warship':
            capacities['rival']['offensive'] += ship_types[ship_type]['attack']

        else:
            capacities['rival']['mining'] += ship_types[ship_type]['weight']

    # Add the capacities of the buyable ships

    for ship_type in buyable_ally_ships:

        buyable_ships_nbr = buyable_ally_ships[ship_type]

        if ship_type.startswith('excavator'):
            capacities['ally']['mining'] += ship_types[ship_type]['weight'] * buyable_ships_nbr

        else:
            capacities['ally']['offensive'] += ship_types[ship_type]['attack'] * buyable_ships_nbr

    for ship_type in buyable_rival_ships:

        buyable_ships_nbr = buyable_rival_ships[ship_type]

        if ship_type.startswith('excavator'):
            capacities['rival']['mining'] += ship_types[ship_type]['weight'] * buyable_ships_nbr

        else:
            capacities['rival']['offensive'] += ship_types[ship_type]['attack'] * buyable_ships_nbr

    return capacities


def evaluate_advantage(capacities):
    """ Evaluates the advantage of a team relative to the other one

    Parameters:
    -----------
    capacities: The capacities of both teams (dict)

    Returns:
    --------
    advantage: The indexes of the advantages of the AI (dict)

    Note:
    -----
    The advantage has these keys:
        - mining
        - offense
    and their values are into [-2, 2]

    Each advantage is evaluated from -2 to 2 for offense and mining capacities

    Version
    -------
    specification: Renaud Thiry (v.1 04/05/18)
    implementation: Renaud Thiry (v.1 04/05/18)

    """

    ally_capacities = capacities['ally']
    enemy_capacities = capacities['rival']

    # Offense

    ally_offensive = ally_capacities['offensive']
    enemy_offensive = enemy_capacities['offensive']

    # Calculates the difference in defensive capacities and fix a limit of "high advantage"

    offensive_delta = ally_offensive - enemy_offensive

    high_offense_advantage = enemy_offensive // 4

    if high_offense_advantage < 1:
        high_offense_advantage = 1

    # Evaluate the offensive capacity

    if offensive_delta == 0:
        offensive_advantage = 0

    # If the ally has the advantage

    elif offensive_delta > high_offense_advantage:
        offensive_advantage = 2

    elif offensive_delta > 0:
        offensive_advantage = 1

    # If he has the disadvantage

    elif offensive_delta < -high_offense_advantage:
        offensive_advantage = -2

    else:
        offensive_advantage = -1

    # Mining

    ally_mining = ally_capacities['mining']
    enemy_mining = enemy_capacities['mining']

    # Calculates the difference in mining capacities and fix a limit of "high advantage"

    mining_delta = ally_mining - enemy_mining

    high_mining_advantage = enemy_mining // 4

    if high_mining_advantage < 1:
        high_mining_advantage = 1

    if mining_delta == 0:
        mining_advantage = 0

    # In case of advantage

    elif mining_delta > high_mining_advantage:
        mining_advantage = 2

    elif mining_delta > 0:
        mining_advantage = 0

    # In case of disadvantage

    elif mining_delta < -high_mining_advantage:
        mining_advantage = -2

    else:
        mining_advantage = -1

    return {'mining': mining_advantage, 'offense': offensive_advantage}


def excavator_limit_reached(asteroids, excavator_ships):
    """ Decides whether there are enough excavators for the team

    Parameters:
    -----------
    asteroids: All the asteroids on the map (dict)
    excavator_ships: All the excavators of a team (dict)

    Returns
    -------
    reached: True if the limit is reached, otherwise False

    Version
    -------
    specification: Poitier Pierre (v.1 01/05/18)
    specification: Thiry Renaud, Thys Killian (v.1 01/05/18)
    """

    limit_ratio = 3

    asteroids_number = 0

    for asteroid_id in asteroids:
        if asteroids[asteroid_id]['ores'] > 0:
            asteroids_number += 1

    if len(excavator_ships) == 0:
        return False

    elif asteroids_number // len(excavator_ships) > limit_ratio:
        return True

    else:
        return False


def choose_ships_to_buy(
        current_command,
        ores,
        advantages,
        ally_ships,
        ally_excavators,
        ship_types,
        asteroids,
        ally_portal,
        future_ships
):
    """ Choose what ships to buy

    Parameters
    ----------
    current_command: The current command of the AI (str)
    ores: The ores of the AI (int)
    advantages: The advantages of the concerned team (dict)
    ally_ships: All the ally ships (dict)
    ally_excavators: All the ally excavators (dict)
    ship_types: The different types of ships (dict)
    asteroids: All the asteroids on the map (dict)
    ally_portal: The ally portal (dict)
    future_ships: All ships being bought this turn (dict)

    Returns
    -------
    actualized_ai_command: The actualize command of the ai (str)

    Version
    -------
    specification: Poitier Pierre (v.1 01/05/18)
    implementation: Thiry Renaud, Thys Killian, Poitier Pierre (v.1 01/05/18)
    """

    commands = current_command

    mining_advantage = advantages['mining']
    offense_advantage = advantages['offense']

    order = 'excavator'

    if mining_advantage == -2:
        order = 'excavator'
    elif offense_advantage == -2:
        order = 'attack'
    elif mining_advantage == -1:
        order = 'excavator'
    elif offense_advantage == -1:
        order = 'excavator'
    elif offense_advantage == 2:
        order = 'attack_warship'
    elif mining_advantage >= 0:
        order = 'attack'

    want_to_buy = True

    if order == 'excavator' and not excavator_limit_reached(asteroids, ally_excavators):

        while want_to_buy:

            if ores >= 2:

                generated_ship_name = generate_ship_name(ally_ships, future_ships)

                commands = add_buy_command(
                    commands,
                    generated_ship_name,
                    'excavator-M',
                    ally_portal,
                    ship_types,
                    asteroids,
                    future_ships
                )

                ores -= 2

            else:
                want_to_buy = False

    elif order == 'attack_warship':

        while want_to_buy:

            if ores >= 9:

                generated_ship_name = generate_ship_name(ally_ships, future_ships)

                commands = add_buy_command(
                    commands,
                    generated_ship_name,
                    'warship',
                    ally_portal,
                    ship_types,
                    asteroids,
                    future_ships
                )

                ores -= 9

            else:
                want_to_buy = False

    else:

        while want_to_buy:

            if ores >= 9:

                generated_ship_name = generate_ship_name(ally_ships, future_ships)

                commands = add_buy_command(commands, generated_ship_name, 'warship', ally_portal, ship_types,
                                           asteroids, future_ships)

                ores -= 9

            elif ores >= 3:

                generated_ship_name = generate_ship_name(ally_ships, future_ships)

                commands = add_buy_command(commands, generated_ship_name, 'scout', ally_portal, ship_types,
                                           asteroids, future_ships)

                ores -= 3

            else:
                want_to_buy = False

    return commands


def stay_safe(ai_memory, ally_ships, rival_aggressive_ships, ship_types, map_properties):
    """ Checks if the ships is safe next turn, otherwise try to prepare the ships

    Parameters
    ----------
    ai_memory: The memory of the AI (dict)
    ally_ships: All the ally ships (dict)
    rival_aggressive_ships: All the aggressive rival ships (dict)
    ship_types: All the different types of ships (dict)
    map_properties: The rows and columns of the map [rows(int), columns(int)] (tuple)

    Note
    ----
    Force move a ship in danger

    Version
    -------
    specification: Poitier Pierre (v.1 01/05/18)
    implementation: Thiry Renaud, Thys Killian, Poitier Pierre (v.1 01/05/18)
    """

    commands = ''

    for ship_name in ally_ships:

        ship = ally_ships[ship_name]

        ship_x = ship['position_x']
        ship_y = ship['position_y']

        ship_type = ship['type']

        is_safe, dangerous_ships = is_safe_next_turn(ship_x, ship_y, ship_type, ship_types, rival_aggressive_ships)

        # Check if a ship is in danger

        if not is_safe:
            ship_go_to(ship, rival_aggressive_ships, ship_types, ship_x, ship_y, map_properties)

            # The excavators flee
            if ship_type.startswith('excavator'):

                if ship['locked']:
                    add_release_command(commands, ship_name)

                if ship_name not in ai_memory['escaping']:
                    ai_memory['escaping'].append(ship_name)

            else:

                stay = True

                # In case of equality, the aggressive ships attack

                if ship_type == 'scout':

                    for rival_ship_name in dangerous_ships:

                        if rival_aggressive_ships[rival_ship_name]['type'] == 'warship':
                            stay = False

                if not stay:
                    ai_memory['escaping'].append(ship_name)

                else:

                    rival_ship_name = dangerous_ships[0]
                    rival_ship_type = rival_aggressive_ships[rival_ship_name]['type']
                    add_action_to_ship(
                        ai_memory,
                        ship_name,
                        ship_type,
                        'attack_ship',
                        (rival_ship_name,
                         rival_ship_type)
                    )

        else:

            # If the ship is safe, remove it from the escaping ships

            if ship_name in ai_memory['escaping']:
                index = ai_memory['escaping'].index(ship_name)
                del ai_memory['escaping'][index]


def send_excavator_mine(
        excavator_name,
        ally_excavators,
        rival_aggressive_ships,
        ship_types,
        ally_portal,
        rival_portal,
        asteroids,
        ai_memory,
        map_properties
):
    """
    Sends an excavator to a good asteroid if there is one

    Parameters:
    ------------
    excavator_name: the name of the excavator (str)
    ally_excavators: all ally excavators (dict)
    rival_aggressive_ships: all enemy damage dealers (dict)
    ship_types: all types of ship (dict)
    ally_portal: the ally portal (dict)
    rival_portal: the enemy portal (dict)
    asteroids: all asteroids on the map (dict)
    ai_memory: the memory of the ai with the current multi-turn actions (dict)
    map_properties: size of the map (list)

    Note:
    -----
    If there isn't anymore asteroid to mine the excavators will simulate an attack onto the enemy portal

    Version
    -------
    specification: Thys Killian, Poitier Pierre (v.1 01/05/18)
    specification: Poitier Pierre (v.1 01/05/18)
    """

    ship = ally_excavators[excavator_name]

    # Find the best asteroid to mine

    interesting_asteroids = find_interesting_asteroids(
        ship,
        rival_aggressive_ships,
        ship_types,
        asteroids
    )

    if len(interesting_asteroids) > 0:

        targeted_asteroid = choose_best_asteroid(
            ally_excavators[excavator_name],
            interesting_asteroids,
            asteroids,
            ally_portal,
            rival_portal
        )

        asteroid = asteroids[targeted_asteroid]

        # Tell to the excavator to mine this asteroid

        add_action_to_ship(
            ai_memory, excavator_name, 'excavator', 'move', (asteroid['position_x'], asteroid['position_y'])
        )

        add_action_to_ship(
            ai_memory, excavator_name, 'excavator', 'mine', (asteroid['position_x'], asteroid['position_y'])
        )

    # If there isn't any interesting asteroid
    else:

        # Send excavators towards enemy to, hopefully, simulate an attack
        ship_go_to(ally_excavators[excavator_name], rival_aggressive_ships,
                   ship_types, rival_portal['position_x'], rival_portal['position_y'], map_properties)


def execute_actions(
        current_command,
        ai_memory,
        ally_ships,
        ally_excavators,
        rival_ships,
        rival_excavators,
        rival_aggressive_ships,
        ship_types,
        ally_portal,
        rival_portal,
        asteroids,
        map_properties
):

    """
    Executes multi-turn actions

    Parameters:
    -----------
    current_command: the current sate of the turn's command line (str)
    ai_memory: the memory of the ai with the current multi-turn actions (dict)
    ally_ships: all ally ships (dict)
    ally_excavators: all ally excavators (dict)
    ally_aggressive_ships: all ally damage dealers (dict)
    rival_ships: all rival ships (dict)
    rival_excavators: all rival excavators (dict)
    rival_aggressive_ships: all enemy damage dealers (dict)
    ship_types: all types of ship (dict)
    ally_portal: the ally portal (dict)
    rival_portal: the enemy portal (dict)
    asteroids: all asteroids on the map (dict)
    map_properties: size of the map (list)

    Return:
    -------
    Command: the new state of the turn's command line (str)

    Version
    -------
    specification: Thiry Renaud, Thys Killian, Poitier Pierre (v.1 01/05/18)
    specification: Thiry Renaud, Thys Killian, Poitier Pierre (v.1 01/05/18)
    """

    command = current_command

    already_attacked_ships = []

    ally_portal_x = ally_portal['position_x']
    ally_portal_y = ally_portal['position_y']

    for ship_name in ally_ships:

        ship = ally_ships[ship_name]

        ship_x = ship['position_x']
        ship_y = ship['position_y']

        ship_type = ship['type']

        ai_actions = ai_memory['actions']

        # Create the default actions template of the ship
        if ship_name not in ai_actions:
            add_action_to_ship(ai_memory, ship_name, ship_type, 'move', (None, None))

        # ---- For the excavators ----
        if ship_type.startswith('excavator'):

            # Update the target of the excavator and check if we need to lock

            if ship_name not in ai_memory['escaping'] and ai_actions[ship_name]['back'] == (None, None):

                target_coordinates = ai_actions[ship_name]['mine']

                # Check if the ship is on its targeted asteroid
                if ship_x == target_coordinates[0] and ship_y == target_coordinates[1]:

                    asteroid_id = str(ship_x) + '_' + str(ship_y)
                    targeted_asteroid = asteroids[asteroid_id]

                    # Check if the asteroid is still exploitable
                    if(
                            targeted_asteroid['ores'] > 0 and
                            not ship['locked'] and
                            not ship_types[ship_type]['weight'] == ship['carried_ores']
                    ):
                        command = add_lock_command(command, ship_name)

                    elif targeted_asteroid['ores'] == 0 or ship_types[ship_type]['weight'] == ship['carried_ores']:

                        # The ship back to the portal

                        command = add_release_command(command, ship_name)

                        add_action_to_ship(ai_memory, ship_name, ship_type, 'back', (True, None))

                else:

                    # Update the target and do its journey

                    send_excavator_mine(
                        ship_name,
                        ally_excavators,
                        rival_aggressive_ships,
                        ship_types,
                        ally_portal,
                        rival_portal,
                        asteroids,
                        ai_memory,
                        map_properties
                    )

            # If the ship is backing and it is on the ally portal
            elif(
                    ai_actions[ship_name]['back'] != (None, None) and
                    ship_x == ally_portal_x and
                    ship_y == ally_portal_y
            ):

                if ship['locked']:

                    ai_actions[ship_name]['back'] = (None, None)

                    # Release the ship and send it to mine
                    command = add_release_command(command, ship_name)

                    send_excavator_mine(
                        ship_name,
                        ally_excavators,
                        rival_aggressive_ships,
                        ship_types,
                        ally_portal,
                        rival_portal,
                        asteroids,
                        ai_memory,
                        map_properties
                    )

                else:

                    # Lock the ship to the portal

                    command = add_lock_command(command, ship_name)

        # ---- For the aggressive ships ----
        else:

            # Choose how and when shoot on a rival ship

            ship_actions = ai_actions[ship_name]

            if ship_actions['attack_portal'] != (None, None):

                # Attack the portal

                rival_portal_distance = get_distance_between_entities(rival_portal, ship)[2]

                if (rival_portal_distance - ship_types[ship_type]['range']) <= 2:

                    # Shoot at the rival portal

                    rival_portal_x = rival_portal['position_x']
                    rival_portal_y = rival_portal['position_y']

                    shoot_x = None
                    shoot_y = None

                    for pos_x in range(rival_portal_x - 2, rival_portal_x + 3):

                        for pos_y in range(rival_portal_y - 2, rival_portal_y + 3):

                            distance = get_distance_ship_location(ship, pos_x, pos_y)[2]

                            if distance <= ship_types[ship_type]['range']:

                                shoot_x = pos_x
                                shoot_y = pos_y

                    if shoot_x is not None and shoot_y is not None:

                        command = add_attack_command(
                            command,
                            ship_name,
                            shoot_x,
                            shoot_y
                        )

                    else:

                        # Go to the rival portal
                        pos_x, pos_y = ship_go_to(
                            ship,
                            rival_aggressive_ships,
                            ship_types,
                            rival_portal['position_x'],
                            rival_portal['position_y'],
                            map_properties
                        )

                        command = add_move_command(command, ship_name, pos_x, pos_y)

                else:

                    # Go to the rival portal
                    pos_x, pos_y = ship_go_to(
                        ship,
                        rival_aggressive_ships,
                        ship_types,
                        rival_portal['position_x'],
                        rival_portal['position_y'],
                        map_properties
                    )

                    command = add_move_command(command, ship_name, pos_x, pos_y)

            elif ship_name not in ai_memory['escaping'] and ship_actions['back'] == (None, None):

                # Select the target of a ship

                targeted_ship_name = ''

                minimum_distance = None

                for rival_excavator_name in rival_excavators:

                    rival_excavator = rival_ships[rival_excavator_name]

                    distance = get_distance_between_entities(ship, rival_excavator)[2]

                    if minimum_distance is None or minimum_distance > distance:

                        targeted_ship_name = rival_excavator_name

                for rival_ship_name in rival_aggressive_ships:

                    rival_ship = rival_ships[rival_ship_name]

                    distances_rival_portal = get_distance_between_entities(rival_ship, ally_portal)
                    distances_ally_portal = get_distance_between_entities(ship, ally_portal)

                    if distances_rival_portal < distances_ally_portal:

                        ship_type = ship['type']
                        rival_ship_type = rival_ship['type']

                        if not (ship_type == 'scout' and rival_ship_type == 'warship'):
                            targeted_ship_name = rival_ship_name

                add_action_to_ship(ai_memory, ship_name, ship_type, 'attack_ship', (targeted_ship_name, None))

                # Check if the ship we want to attack exists, otherwise don't attack
                if targeted_ship_name in rival_ships:

                    targeted_ship = rival_ships[targeted_ship_name]

                    targeted_ship_x = targeted_ship['position_x']
                    targeted_ship_y = targeted_ship['position_y']

                    targeted_ship_hit_box = ship_types[targeted_ship['type']]['hit_box']

                    can_attack = False

                    shoot_pos_x = 0
                    shoot_pos_y = 0

                    # Check if we can attack the rival ship

                    for target_pos_x in range(targeted_ship_x - 2, targeted_ship_x + 3):
                        for target_pos_y in range(targeted_ship_y - 2, targeted_ship_y + 2):

                            if(
                                target_pos_x in range(1, map_properties[1]) and
                                target_pos_y in range(1, map_properties[0]) and
                                targeted_ship_hit_box
                                [target_pos_y - targeted_ship_y + 2]
                                [target_pos_x - targeted_ship_x + 2] == 'a'
                            ):
                                distances = get_distance_ship_location(ship, target_pos_x, target_pos_y)

                                # If the position is closer enough, attack it
                                if distances[2] <= ship_types[ship['type']]['range']:
                                    can_attack = True

                                    shoot_pos_x = target_pos_x
                                    shoot_pos_y = target_pos_y

                    if can_attack:

                        already_attacked_ships.append(ship_name)
                        command = add_attack_command(command, ship_name, shoot_pos_x, shoot_pos_y)

                    else:

                        # If we can't attack our target, go closer
                        destination_x, destination_y = ship_go_to(
                            ship,
                            rival_aggressive_ships,
                            ship_types,
                            targeted_ship_x,
                            targeted_ship_y,
                            map_properties
                        )

                        command = add_move_command(command, ship_name, destination_x, destination_y)

                else:
                    # If the ship we want attack is not here, we don't want to attack either
                    ai_memory['actions'][ship_name]['attack'] = (None, None)

        ship_actions = ai_memory['actions'][ship_name]

        if ship_actions['back'] != (None, None):
            if ship_x != ally_portal_x or ship_y != ally_portal_y:
                destination_x, destination_y = ship_go_to(
                    ship,
                    rival_aggressive_ships,
                    ship_types,
                    ally_portal_x,
                    ally_portal_y,
                    map_properties
                )

                command = add_move_command(command, ship_name, destination_x, destination_y)

        elif ship_actions['move'] != (None, None) and ship_name not in already_attacked_ships:
            action = ship_actions['move']

            destination_x, destination_y = ship_go_to(
                ship,
                rival_aggressive_ships,
                ship_types,
                action[0],
                action[1],
                map_properties
            )

            command = add_move_command(command, ship_name, destination_x, destination_y)

    return command


def get_ai_command(
        ai_memory,
        turn_number,
        ally_ships,
        rival_ships,
        ship_types,
        asteroids,
        ally_portal,
        rival_portal,
        map_properties
):
    """ Returns the command of the AI.

    Parameters
    ----------
    ai_memory: All the elements the AI uses over the long term (dict)
    turn_number: The number of elapsed turn (int)
    ally_ships: All the ally ships (dict)
    rival_ships: All the rival ships (dict)
    ship_types: The different types of ships in the game (dict)
    asteroids: The asteroids of the game (dict)
    ally_portal: The ally portal data (dict)
    rival_portal: The rival portal data (dict)
    map_properties: The rows and columns of the map [rows(int), columns(int)] (tuple)

    Returns
    -------
    ai_command: The command of the AI (str)

    Notes
    -----
    The memory of the AI is initialized in the first turn of the game.

    The first turn is the turn number 1.

    Version
    -------
    specification: Thiry Renaud, Thys Killian, Poitier Pierre (v.1 05/05/18)
    specification: Thiry Renaud, Thys Killian, Poitier Pierre (v.1 05/05/18)
    """

    ally_aggressive_ships, ally_excavators = separate_aggressive_passive_ships(ally_ships)

    rival_aggressive_ships, rival_excavators = separate_aggressive_passive_ships(rival_ships)

    # Some ships that does not exist yet, they are simulated
    future_ships = {}

    ai_command = ''

    ores = ally_portal['ores']

    if turn_number == 1:

        ai_memory['rival_bought_aggressive'] = False
        ai_memory['actions'] = {}
        ai_memory['escaping'] = []

        # AI state: 1 for early game, 2 for continuity, 3 for rush the portal
        ai_memory['ai_state'] = 1

        # Check if there are asteroids

        if not asteroids:

            # Buy a scout
            scout_name = generate_ship_name(ally_ships, future_ships)
            ai_command = add_buy_command(
                ai_command,
                scout_name,
                'scout',
                ally_portal,
                ship_types,
                asteroids,
                future_ships
            )

            # Attack rival_portal

            rival_portal_x = rival_portal['position_x']
            rival_portal_y = rival_portal['position_y']

            add_action_to_ship(
                ai_memory,
                scout_name,
                'scout',
                'attack_portal',
                (rival_portal_x, rival_portal_y)
            )

        else:
            # Buy 2 excavators

            first_excavator_name = generate_ship_name(ally_ships, future_ships)
            second_excavator_name = generate_ship_name(ally_ships, future_ships)

            while first_excavator_name == second_excavator_name:
                second_excavator_name = generate_ship_name(ally_ships, future_ships)

            ai_memory['excavator_mine_close_rival'] = second_excavator_name

            ai_command = add_buy_command(
                ai_command,
                first_excavator_name,
                'excavator-M',
                ally_portal,
                ship_types,
                asteroids,
                future_ships
            )

            ai_command = add_buy_command(
                ai_command,
                second_excavator_name,
                'excavator-M',
                ally_portal,
                ship_types,
                asteroids,
                future_ships
            )

            create_future_ship_data(
                first_excavator_name,
                ally_portal,
                'excavator-M',
                ship_types,
                asteroids,
                future_ships
            )

            create_future_ship_data(
                second_excavator_name,
                ally_portal,
                'excavator-M',
                ship_types,
                asteroids,
                future_ships
            )

            # Set the action for excavator 1 (go to the closest asteroid to the ally portal)

            interesting_asteroids = find_interesting_asteroids(
                future_ships[first_excavator_name],
                rival_aggressive_ships,
                ship_types,
                asteroids
            )

            targeted_asteroid = choose_best_asteroid(
                future_ships[first_excavator_name],
                interesting_asteroids,
                asteroids,
                ally_portal,
                rival_portal,
                'ally_portal'
            )

            positions = targeted_asteroid.split('_')

            add_action_to_ship(
                ai_memory,
                first_excavator_name,
                'excavator-M',
                'move',
                (int(positions[0]), int(positions[1]))
            )

            # Set the action for excavator 2 (go to an asteroid close to the rival portal)
            targeted_asteroid = choose_best_asteroid(
                future_ships[second_excavator_name],
                interesting_asteroids,
                asteroids,
                ally_portal,
                rival_portal,
                'rival_portal'
            )

            positions = targeted_asteroid.split('_')

            add_action_to_ship(
                ai_memory,
                second_excavator_name,
                'excavator-M',
                'move',
                (int(positions[0]), int(positions[1]))
            )

    ai_state = ai_memory['ai_state']

    stay_safe(ai_memory, ally_ships, rival_aggressive_ships, ship_types, map_properties)

    if ai_state == 1 and turn_number != 1:

        if not ai_memory['rival_bought_aggressive'] and len(rival_aggressive_ships) > 0:

            ai_memory['rival_bought_aggressive'] = True

            excavator_name = ai_memory['excavator_mine_close_rival']
            excavator_data = ally_ships[excavator_name]

            interesting_asteroids = find_interesting_asteroids(
                excavator_data,
                rival_aggressive_ships,
                ship_types,
                asteroids
            )

            targeted_asteroid = choose_best_asteroid(
                excavator_data,
                interesting_asteroids,
                asteroids,
                ally_portal,
                rival_portal,
                'rival_portal'
            )

            add_action_to_ship(
                ai_memory,
                excavator_name,
                'excavator-M',
                'move',
                (int(targeted_asteroid[0]), int(targeted_asteroid[3]))
            )

        if ores >= 3:

            ai_command = add_buy_command(ai_command, generate_ship_name(ally_ships, future_ships), 'scout', ally_portal,
                                         ship_types, asteroids, future_ships)
            ores -= 3
            ai_memory['ai_state'] = 2

    elif ai_state == 2:

        # Get the buyable ships

        ally_buyable_ships = get_buyable_ships(ores, ship_types)
        rival_buyable_ships = get_buyable_ships(rival_portal['ores'], ship_types)

        # Choose the ships to buy to stabilize the capacities

        if turn_number >= 10:

            # Computes the advantages

            capacities = evaluate_capacities(
                ally_ships,
                rival_ships,
                ship_types,
                ally_buyable_ships,
                rival_buyable_ships
            )

            advantages = evaluate_advantage(capacities)

            ai_command = choose_ships_to_buy(
                ai_command,
                ores,
                advantages,
                ally_ships,
                ally_excavators,
                ship_types,
                asteroids,
                ally_portal,
                future_ships
            )

            # Checks if the AI is very advantaged in both criteria and sets the ai_state to 3

            if advantages['mining'] == 2 and advantages['offense'] == 2:
                ai_memory['ai_state'] = 3

        else:

            advantages = {'mining': 0, 'offense': 0}

            ai_command = choose_ships_to_buy(
                ai_command,
                ores,
                advantages,
                ally_ships,
                ally_excavators,
                ship_types,
                asteroids,
                ally_portal,
                future_ships
            )

    elif ai_state == 3:

        # Check how many ships the ai can buy

        number_buyable_warships = int(ores // 9)
        number_buyable_scouts = int((ores - number_buyable_warships * 9) // 3)

        rival_portal_x = rival_portal['position_x']
        rival_portal_y = rival_portal['position_y']

        # Buy all them and set their action to attack the portal

        taken_names = []

        for warship_nbr in range(number_buyable_warships):

            warship_name = generate_ship_name(ally_ships, future_ships)

            while warship_name in taken_names:
                warship_name = generate_ship_name(ally_ships, future_ships)

            taken_names.append(warship_name)

            add_action_to_ship(ai_memory, warship_name, 'warship', 'attack_portal', (rival_portal_x, rival_portal_y))

            add_buy_command(ai_command, warship_name, 'warship', ally_portal,
                            ship_types, asteroids, future_ships)
            ores -= 9

        for scout_nbr in range(number_buyable_scouts):

            scout_name = generate_ship_name(ally_ships, future_ships)

            while scout_name in taken_names:
                scout_name = generate_ship_name(ally_ships, future_ships)

            taken_names.append(scout_name)

            add_action_to_ship(ai_memory, scout_name, 'scout', 'attack_portal', (rival_portal_x, rival_portal_y))

            add_buy_command(ai_command, scout_name, 'scout', ally_portal,
                            ship_types, asteroids, future_ships)
            ores -= 3

        # Check if the ships on the board attack the rival portal, otherwise set their action

        ai_actions = ai_memory['actions']

        for ship_name in ally_aggressive_ships:

            if ship_name in ai_actions and ai_actions[ship_name]['attack_portal'] == (None, None):
                ai_memory['actions'][ship_name]['attack_portal'] = (rival_portal_x, rival_portal_y)

    ai_command = execute_actions(
        ai_command,
        ai_memory,
        ally_ships,
        ally_excavators,
        rival_ships,
        rival_excavators,
        rival_aggressive_ships,
        ship_types,
        ally_portal,
        rival_portal,
        asteroids,
        map_properties
    )

    return ai_command, ai_memory

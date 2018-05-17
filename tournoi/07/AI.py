import mining_wars_gr_07 as mw
import random
from operator import itemgetter


def AI(ships, players, info_ships, asteroids, map_width, map_height, turn, index, AI_data):
    """Return AI's actions.

    Parameters
    ----------
    ships: informations about existing ships (dict)
    players: informations the players (dict)
    info_ships: properties of each type of ships (dict)
    asteroids: informations about the asteroids (list)
    map_width: width of the game field (int)
    map_height: height of the game field (int)
    turn: number of turns (int)
    index: index of the AI player in the players structure (int)
    AI_data: AI's saved data (dict)

    Return
    ------
    AI_actions: commands of the AI (str)
    AI_data: updated AI's saved data (dict)

    Version
    -------
    Specifications: Martin Balfroid (v. 1 20/04/2018)
                    Martin Balfroid (v. 2 22/04/2018)
    Implementation: Martin Balfroid (v. 1 20/04/2018)
                    Martin Balfroid (v. 2 22/04/2018)
                    Martin Balfroid (v. 3 28/04/2018)
                    Jules Dejaeghere (v.4 03/05/2018)
    """
    # Index and info about the opponent player
    opponent_id = (index + 1) % 2
    opponent = players[opponent_id]

    # Information about the AI
    player = players[index]
    budget = player['ore']
    AI_actions = ''
    loosing = (opponent['portal_life'] > player['portal_life'] or (
    opponent['portal_life'] == player['portal_life'] and opponent['total_ore'] > player['total_ore']))

    # TURN 1
    if turn == 1:
        # Buy one excavator-S
        buy_action, AI_data = buy_ship('excavator-S', AI_data, index)
        AI_actions += buy_action
        first_ship_name = buy_action.split(':')[0]

        # Move excavator-S towards closest asteroid
        ship_pos = tuple(player['portal'])
        best_asteroid = list()
        dist = map_height * map_width
        for ast in asteroids:
            trip = len(ship_trip(ship_pos, tuple(ast[0:2])))
            if trip < dist:
                best_asteroid = ast
                dist = trip

        best_asteroid_pos = tuple(best_asteroid[0:2])
        next_pos = ship_trip(ship_pos, best_asteroid_pos)[0]
        AI_actions += move_ship(first_ship_name, next_pos)

    # Next turns
    else:

        # TURN 2
        if turn == 2:
            # -----  Buy  ----- #
            # Get a list of the opponent's ship type
            opponent_ships_types = [info['type'] for (name, info) in ships.items() if info['player'] == opponent_id]
            # The names of the opponent's ship (excluding names already taken by the AI player's ship)
            oships_names = [name[0] for (name, info) in ships.items() if
                            info['player'] == opponent_id and (name[0], index) not in AI_data['taken_name']]

            # Copy the name of one ship of the other player
            # Assuming that a lot of people will misread the rules as 'All names of ships must be unique'
            # In fact it's the two player can have ship with the same name
            # It can lead to a tricky/sly win if the other see this as illegal move when it is not
            # If the other player has no ships, the variable is set to None
            random_copied_name = None if len(oships_names) == 0 else random.choice(oships_names)
            # Add the random copied name to the list of taken name for this player
            if random_copied_name is not None:
                AI_data['taken_name'].append((random_copied_name, index))

            # If we have enough ores and the opponent has a scout or can buy one next turn
            if budget >= 3 and ('scout' in opponent_ships_types or opponent['ore'] >= 3):
                # The ship with a copied name will be a scout
                copied_named_ship_type = 'scout'
            else:
                # The ship with a copied name will be a excavator-M
                copied_named_ship_type = 'excavator-M'
                AI_data['return_portal'][(random_copied_name, index)] = False

                # Buy a excavator-S
                buy_action, AI_data = buy_ship('excavator-S', AI_data, index)
                AI_actions += buy_action

            # Buy the ship with a copied name
            if random_copied_name is not None:
                AI_actions += '%s:%s ' % (random_copied_name, copied_named_ship_type)
            # If the other player has no ships, we assign a random name
            else:
                buy_action, AI_data = buy_ship(copied_named_ship_type, AI_data, index)
                AI_actions += buy_action

        buy_cmd = str()
        if not turn == 2:
            AI_data, buy_cmd = buy_behaviour(players, info_ships, AI_data, index, loosing, asteroids, ships)
            AI_actions += buy_cmd

        AI_ships = {name: info for (name, info) in ships.items() if name[1] == index}

        if buy_cmd:
            # Add new ships to AI_ships
            buy_cmd = buy_cmd.strip(' ')
            buy_cmd = buy_cmd.split(' ')
            buy_cmd = [data.split(':') for data in buy_cmd]

            for cmd in buy_cmd:
                name = cmd[0]
                ship_type = cmd[1]

                AI_ships[(name, index)] = {'type': ship_type, 'load': 0, 'life': info_ships[ship_type]['life'],
                    'position': player['portal'], 'player': index, 'state': 'unlocked'}

        for (ship_name, ship_info) in AI_ships.items():
            # EXCAVATOR
            if ship_info['type'].startswith('excavator'):
                AI_data, exc_actions = excavator_behaviour(ship_name, player, info_ships, AI_data, asteroids, AI_ships)
                AI_actions += exc_actions
            # FIGHT SHIP
            else:
                # {**a, **b} merge the two dictionnary
                AI_actions += fight_behaviour(ship_name, players, info_ships, {**ships, **AI_ships})

    print(AI_actions)
    return AI_actions.rstrip(' '), AI_data


def buy_ship(ship_type, AI_data, ply_index):
    """Generate the command to buy a ship (with a random name)

    Parameters
    ----------
    ship_type: the type of the ship to buy (str)
    AI_data: AI's saved data (dict)
    ply_index: the player's index (int)

    Return
    -------
    cmd: the command (str)
    AI_data: updated AI's saved data (dict)

    Version
    ------
    Specifications: Martin Balfroid (v. 1 20/04/2018)
    Implementation: Martin Balfroid (v. 1 20/04/2018)
                    Jules Dejaeghere (v.2 04/05/2018)
    """
    random_name = random.choice(AI_data['name'])
    ship_name = random_name
    # Handle if the name was already choosen (for this player)
    index = 2
    while (ship_name, ply_index) in AI_data['taken_name']:
        ship_name = '%s_%d' % (random_name, index)
        index += 1

    AI_data['taken_name'].append((ship_name, ply_index))
    if ship_type.startswith('excavator'):
        AI_data['return_portal'][(ship_name, ply_index)] = False

    AI_data['last_buy'] = ship_type
    return '%s:%s ' % (ship_name, ship_type), AI_data


def move_ship(ship_name, to_pos):
    """Generate the command to move a ship

    Parameters
    ----------
    ship_name: the ship's name (str)
    to_pos: the position to move (2-sized tuple)

    Return
    ------
    cmd: the command (str)

    Notes
    -----
    The purpose of this function is to have a more legible code

    Version
    ------
    Specifications: Martin Balfroid (v. 1 27/04/2018)
    Implementation: Martin Balfroid (v. 1 27/04/2018)
    """
    return '%s:@%s-%s ' % (ship_name, to_pos[0], to_pos[1])


def lock_ship(ship_name):
    """Generate the command to lock a ship

    Parameters
    ----------
    ship_name: the ship's name (str)

    Return
    ------
    cmd: the command (str)

    Notes
    -----
    The purpose of this function is to have a more legible code

    Version
    ------
    Specifications: Martin Balfroid (v. 1 27/04/2018)
    Implementation: Martin Balfroid (v. 1 27/04/2018)
    """
    return '%s:lock ' % ship_name


def release_ship(ship_name):
    """Generate the command to release a ship

    Parameters
    ----------
    ship_name: the ship's name (str)

    Return
    ------
    cmd: the command (str)

    Notes
    -----
    The purpose of this function is to have a more legible code

    Version
    ------
    Specifications: Martin Balfroid (v. 1 27/04/2018)
    Implementation: Martin Balfroid (v. 1 27/04/2018)
                    Jules Dejaeghere (v.2 04/05/2018)
    """
    return '%s:release ' % ship_name


def fire_ship(ship_name, target_pos):
    """Generate the command to make a ship fire

    Parameters
    ----------
    ship_name: the ship's name (str)
    target_pos: the target's position (2-sized tuple)

    Return
    ------
    cmd: the command (str)

    Notes
    -----
    The purpose of this function is to have a more legible code

    Version
    ------
    Specifications: Martin Balfroid (v. 1 27/04/2018)
    Implementation: Martin Balfroid (v. 1 27/04/2018)
    """
    return '%s:*%s-%s ' % (ship_name, target_pos[0], target_pos[1])


def find_best_asteroid(point, asteroids, ship_name, ships, info_ships, id=0):
    """Find the most interesting asteroid (in relation to a certain point).
    In other word, find the asteroid with the greater score.

    Parameters
    ----------
    point: center of the ship (2-sized tuple)
    asteroids: informations about all the asteroids (list)
    ship_name: name of the ship to find the best asteroid for (tuple)
    ships: informations about existing ships (dict)
    info_ships: properties of each type of ships (dict)
    id: index of the best asteroid to return (0 is THE best, 1 is the second best,...) (int, optional)

    Return
    ------
    asteroid: the most interesting asteroid (in relation to a certain ship) (list)

    Notes
    -----
    ship_type is None when we don't care about it

    Version
    -------
    Specifications: Martin Balfroid (v. 1 22/04/2018)
                    Martin Balfroid (v. 2 27/04/2018)
                    Jules Dejaeghere (v.3 03/05/2018)
    Implementation: Martin Balfroid (v. 1 22/04/2018)
                    Martin Balfroid (v. 2 27/04/2018)
                    Jules Dejaeghere (v.3 03/05/2018)
    """
    best_asteroid = list()
    # Generate a list of tuple like (ast_info, score)
    for asteroid in asteroids:
        best_asteroid.append((asteroid, asteroid_score(point, asteroid, ship_name, ships, info_ships)))

    # Sort the list according to the score.  First is the best
    best_asteroid = sorted(best_asteroid, key=itemgetter(1))

    if id < len(best_asteroid) - 1:
        return best_asteroid[id][0]

    else:
        return best_asteroid[0][0]


def asteroid_score(point, asteroid, ship_name, ships, info_ships):
    """Compute the score of an asteroid (in relation to a certain point)

    Parameters
    ----------
    point: the point to compare (2-sized tuple)
    asteroid: information about the asteroid (list)
    ship_name: name of the ship to find the best asteroid for (tuple)
    ships: information about existing ships (dict)
    info_ships: properties of each type of ships (dict)

    Return
    ------
    score: score of the asteroid (float)

    Notes
    -----
    Lower is the score, best it is
    score = nb turns needed to go and fill the ship of ore

    Version
    ------
    Specifications: Martin Balfroid (v.1 22/04/2018)
                    Martin Balfroid (v.2 27/04/2018)
                    Jules Dejaeghere (v.3 03/05/2018)
    Implementation: Martin Balfroid (v.1 22/04/2018)
                    Martin Balfroid (v.2 27/04/2018)
                    Jules Dejaeghere (v.3 03/05/2018)
                    Martin Balfroid (v.4 12/05/2018)
    """

    free_space = info_ships[ships[ship_name]['type']]['max_load'] - ships[ship_name]['load']
    ast_pos = tuple(asteroid[0:2])
    dist_to_ast = len(ship_trip(point, ast_pos))
    if asteroid[3] != 0 and asteroid[2] != 0:
        return dist_to_ast + free_space / asteroid[3]
    else:
        return 1000 * dist_to_ast


def ship_trip(from_pos, to_pos, include_from_pos=False):
    """Get all the points where the ship will be to travel from a position to another.

    Parameters:
    ----------
    from_pos: from position (2-sized tuple)
    to_pos: to position (2-sized tuple)
    include_from_pos: include from position in the trip (bool, optional)

    Return:
    -------
    trip: all the points where the ship will be to travel from a position to another. (List[2-sized tuple])

    Version
    ------
    Specifications: Martin Balfroid (v. 1 21/04/2018)
                    Martin Balfroid (v.2 05/05/2018)
    Implementation: Martin Balfroid (v. 1 21/04/2018)
                    Martin Balfroid (v.2 05/05/2018)
    """
    trip = [from_pos] if include_from_pos else list()
    while to_pos != from_pos:
        # Compute the distance in each axis
        y_dis = to_pos[0] - from_pos[0]
        x_dis = to_pos[1] - from_pos[1]
        # Compute the direction in each axis
        y_dir = y_dis // abs(y_dis) if y_dis != 0 else 0
        x_dir = x_dis // abs(x_dis) if x_dis != 0 else 0

        from_pos = (from_pos[0] + y_dir, from_pos[1] + x_dir)
        trip.append(from_pos)

    return trip


def excavator_behaviour(ship_name, player, info_ships, AI_data, asteroids, AI_ships):
    """Give the next action of an excavator
    
    Parameters
    ----------
    ship_name: tuple with the name and the ship number (tuple)
    player: informations the AI player (dict)
    info_ships: properties of each type of ships (dict)
    AI_data: AI's saved data (dict)
    asteroids: informations about the asteroids (list)
    AI_ships: informations about existing ships owned by AI (dict)
    
    Returns
    -------
    AI_data: updated AI's saved data (dict)
    cmds: commands generated (str)
    
    Version
    -------
    Specifications: Jules Dejaeghere (v.1 02/05/2018)
    Implementation: Jules Dejaeghere (v.1 02/05/2018)
    """

    # Create variables    
    cmds = str()
    position = AI_ships[ship_name]['position']
    return_portal = AI_data['return_portal'][ship_name]
    empty = AI_ships[ship_name]['load'] == 0
    full = AI_ships[ship_name]['load'] == info_ships[AI_ships[ship_name]['type']]['max_load']
    locked = AI_ships[ship_name]['state'] == 'locked'
    portal_pos = tuple(player['portal'])
    best_ast_pos = tuple(find_best_asteroid(position, asteroids, ship_name, AI_ships, info_ships)[0:2])

    # Define target
    target = portal_pos if return_portal else best_ast_pos
    on_target = tuple(AI_ships[ship_name]['position']) == target

    # Check if ship have to return to portal
    if on_target and ((empty and return_portal) or (full and not return_portal)):
        # Toggle using XOR (^)
        return_portal ^= True

        # Redefine target
        target = portal_pos if return_portal else best_ast_pos
        on_target = tuple(AI_ships[ship_name]['position']) == target

    elif full:
        return_portal = True

    # Generate cmds
    if not on_target:
        if locked:
            cmds += release_ship(ship_name[0])

        next_pos = ship_trip(tuple(AI_ships[ship_name]['position']), target)[0]
        cmds += move_ship(ship_name[0], next_pos)

    elif on_target:
        if not locked:
            cmds += lock_ship(ship_name[0])

    # Update AI_data and return values       
    AI_data['return_portal'][ship_name] = return_portal

    return AI_data, cmds


def closest_pt_in_hb(pos, target_hitbox):
    """Get the hitbox's closest point to a certain position.

    Parameters:
    -----------
    pos: the position to check (2-sized tuple)
    hitbox: list containing all the points of the entity we target (List[2-sized tuple])

    Returns
    -------
    closest_pt: closest point to a certain position (2-sized tuple)
    closest_pt_dis: the distance between the position and the closest point (int)

    Version:
    --------
    Specification: Martin Balfroid (v. 1 02/02/2018)
    Implementation: Martin Balfroid (v. 1 02/02/2018)
    """
    closest_pt, closest_pt_dis = None, 10 ** 10
    for point in target_hitbox:
        dis = len(ship_trip(pos, point))
        if dis < closest_pt_dis:
            closest_pt_dis = dis
            closest_pt = point

    return closest_pt, closest_pt_dis


def closest_pt_at_range(ship_pos, hitbox, fire_range):
    """Get the closest point where a ship can hit the hitbox.

    Parameters:
    -----------
    ship_pos: the ship's center position (2-sized tuple)
    hitbox: list containing all the points of a ship (List[2-sized tuple])
    fire_range: the fire range (int)

    Returns
    -------
    closest_pt_rg: the closest point where a ship can hit the hitbox (2-sized tuple)
    
    Version:
    --------
    Specification: Martin Balfroid (v. 1 03/02/2018)
    Implementation: Martin Balfroid (v. 1 03/02/2018)
    """
    # Get the hitbox's closest point to the ship position.
    closest_pt_hb = closest_pt_in_hb(ship_pos, hitbox)[0]
    # Get all the points where the ship will be to travel to the point compute previously
    ship_trip_to_closest_pt = ship_trip(ship_pos, closest_pt_hb, True)

    # Get all the points in the trip at range distance
    pt_in_ship_trip_at_range = [pt for pt in ship_trip_to_closest_pt if mw.distance(pt, closest_pt_hb) <= fire_range]
    # Get the closest point at range in the ship trip
    closest_pt_rg = closest_pt_in_hb(ship_pos, hitbox)[0]

    return closest_pt_rg


def buy_behaviour(players, info_ships, AI_data, index, loosing, asteroids, ships):
    """Give the next buy actions

    Parameters
    ----------
    players: informations the players (list of dict)
    players: informations the players (list of dict)
    info_ships: properties of each type of ships (dict)
    AI_data: AI's saved data (dict)
    index: index of the AI player in the players structure (int)
    loosing: True if we are loosing the game (bool)
    asteroids: information about the asteroids (list)
    ships: information about existing ships (dict)

    Returns
    -------
    AI_data: AI's saved data (dict)
    cmds: commands to buy ships (str)

    Version
    -------
    Specifications: Jules Dejaeghere (v.1 04/05/2018)
    Implementation: Jules Dejaeghere (v.1 04/05/2018)
                    Jules Dejaeghere (v.2 05/05/2018)
                    Martin Balfroid (v.3 12/05/2018)
                    Martin Balfroid (v.4 15/05/2018)
    """

    # Define variables
    budget = players[index]['ore']
    cmds = ''
    AI_ships = {name: ship for (name, ship) in ships.keys() if name[1] == index}
    fships = {name: ship for (name, ship) in AI_ships.keys() if not ship['type'].startswith('excavator')}
    eships = {name: ship for (name, ship) in AI_ships.keys() if ship['type'].startswith('excavator')}
    # Opponent ships
    oindex = (index + 1) % 2
    oships = {name: ship for (name, ship) in ships.keys() if name[1] == oindex}
    ofships = {name: ship for (name, ship) in oships.keys() if not ship['type'].startswith('excavator')}
    oeships = {name: ship for (name, ship) in oships.keys() if ship['type'].startswith('excavator')}

    # How many ores can we get per turn
    mining_power = sum((info_ships[exc['type']]['max_load'] for exc in eships.values()))
    omining_power = sum((info_ships[exc['type']]['max_load'] for exc in oeships.values()))
    total_ore = players[index]['total_ore']
    ototal_ore = players[oindex]['total_ore']

    # Indicates how much we dominate economically the game (in %)
    eco_dom = dom_score(mining_power, omining_power, total_ore, ototal_ore)

    # How many damage can we do per turn
    fire_power = sum((info_ships[fship['type']]['attack'] for fship in fships.values()))
    ofire_power = sum((info_ships[ofship['type']]['attack'] for ofship in ofships.values()))
    portal_hp = players[index]['portal_life']
    oportal_hp = players[oindex]['portal_life']

    # Indicates how much we dominate militarily the game (in %)
    mil_dom = dom_score(fire_power, ofire_power, portal_hp, oportal_hp)
    # How many ores remaining in the map
    remaining_ore = sum((ast[2] for ast in asteroids))

    # We have more mining power that ores left
    ore_shortage = (remaining_ore <= mining_power)

    # If we need to level up our economic domination
    # Except if we can not improve it because there is a shortage of ore
    if eco_dom < mil_dom and not ore_shortage:
        # If we are very badly economicaly dominate, buy a as mu
        while budget >= 1 and eco_dom <= 0.25:
            # Buy an excavator-S
            cmd, AI_data = buy_ship('excavator-S', AI_data, index)
            budget -= 1
            cmds += cmd
            # Update eco_dom
            mining_power += info_ships['excavator-S']['max_load']
            eco_dom = dom_score(mining_power, omining_power, total_ore, ototal_ore)
        while budget >= 2 and eco_dom <= 0.75:
            # Buy an excavator-M
            cmd, AI_data = buy_ship('excavator-M', AI_data, index)
            budget -= 2
            cmds += cmd
            # Update eco_dom
            mining_power += info_ships['excavator-M']['max_load']
            eco_dom = dom_score(mining_power, omining_power, total_ore, ototal_ore)
    else:
        while budget >= 3 and mil_dom <= 0.75:
            # Buy a scout
            cmd, AI_data = buy_ship('scout', AI_data, index)
            budget -= 3
            cmds += cmd
            # Update mil_dom
            fire_power += info_ships['scout']['attack']
            mil_dom = dom_score(fire_power, ofire_power, portal_hp, oportal_hp)

    # If we are doing really well both militarly and economically we spare to buy a warship
    if budget >= 9 and mil_dom > 0.75 and eco_dom > 0.75:
        # Buy a warship
        cmd, AI_data = buy_ship('warship', AI_data, index)
        budget -= 9
        cmds += cmd

    return AI_data, cmds


def dom_score(fleet_pw, ofleet_pw, stat_ind, ostat_ind):
    """Compute the domination score (economic or military)

    Parameters
    ----------
    fleet_pw: the power of a certain type of the player's fleet (int)
    fleet_pw: the power of a certain type of the opponent's fleet (int)
    stat_ind: a status indicator use in the equation (int)
    ostat_ind: a status indicator use in the equation (int)

    Returns
    -------
    score: the domination score (float, range[0,1])

    Notes
    -----
    if it's economic domination :   (o)fleet_pw is the fight ships fleet
                                    (o)stat_ind is the total ore of each player
    else if it's war domination :   (o)fleet_pw is the mining ships fleet
                                    (o)stat_ind is the life of each player's portal

    Version
    -------
    Specification: Martin Balfroid (v.1 15-05-18)
    Implementation: Martin Balfroid (v.1 15-05-18)
    """
    # If both player have no fleet
    if fleet_pw + ofleet_pw == 0:
        return stat_ind / (stat_ind + ostat_ind)
    if stat_ind + ostat_ind == 0:
        return fleet_pw / (fleet_pw + ofleet_pw)

    return (fleet_pw / (fleet_pw + ofleet_pw) + stat_ind / (stat_ind + ostat_ind)) / 2

def fight_behaviour(ship_name, players, info_ships, ships):
    """The behaviour of fight ship (scout, warship)

    Parameters:
    -----------
    ship_name: the name of the ship with the id of the owner (Tuple(str, int))
    player: informations the AI player (dict)
    info_ships: properties of each type of ships (dict)
    ships: information about existing ships (dict)

    Returns:
    --------
    cmds: commands to fight (str)

    Version
    -------
    Specifications: Martin Balfroid (v.1 04/05/2018)
                    Jules Dejaeghere (v.2 06/05/2018)
                    Martin Balfroid (v. 3 06/05/2018)
    Implementation: Martin Balfroid (v.1 05/05/2018)
                    Jules Dejaeghere (v.2 06/05/2018)
                    Martin Balfroid (v.3 06/05/2018)
    """

    #   ------ Define variables --------
    portal_fig = []
    for x in range(-2, 2 + 1):
        portal_fig += [(x, y) for y in range(-2, 2 + 1) if (x, y) != (0, 0)]
    # The index of the AI player
    index = ship_name[1]

    # Opponent variables
    o_index = (index + 1) % 2
    o_ships = {name: ship for (name, ship) in ships.items() if name[1] == o_index}
    o_fight_ships = {name: ship for (name, ship) in o_ships.items() if not name[0].startswith('excavator')}
    o_mining_ships = {name: ship for (name, ship) in o_ships.items() if name[0].startswith('excavator')}
    o_portal = tuple(players[o_index]['portal'])
    o_portal_hb = mw.hitbox(o_portal, portal_fig)

    # AI variables
    fight_ships = {name: ship for (name, ship) in o_ships.items() if not name[0].startswith('excavator')}

    ship_pos = tuple(ships[ship_name]['position'])
    ship_type = ships[ship_name]['type']
    portal = tuple(players[index]['portal'])
    hitbox_current_ship = mw.hitbox(ship_pos, info_ships[ship_type]['fig'])
    reach = info_ships[ship_type]['range']

    cmds = ''

    # List of all the possible actions for the current ship
    # Structure: [(priority, act_type, target), ]
    batch_actions = list()

    # --------  Define all the next possibles actions for the current ship --------
    for o_ship in o_ships.values():
        o_ship_pos = tuple(o_ship['position'])
        o_ship_type = o_ship['type']
        o_ship_hb = mw.hitbox(o_ship_pos, info_ships[o_ship_type]['fig'])
        # Find possibles target points
        reachable = [pt for pt in o_ship_hb if pt not in hitbox_current_ship and mw.distance(ship_pos, pt) <= reach]
        # Distance between the opponent ship and opponent portal
        dis_oships_oportal = len(ship_trip(o_portal, o_ship_pos))
        # Distance between the AI portal and the opponent ships
        dis_portal_oships = len(ship_trip(portal, o_ship_pos))

        # If the current ship meets a an opponent ship closer of our portal than his
        # Fire the o_ship without firing our own ship (if possible)
        if dis_oships_oportal > dis_portal_oships and reachable:
            batch_actions.append((1, 'fire', reachable[0]))

        # If a o_ship is very close of our portal
        # Send our closest fight ship to fire on it
        if dis_oships_oportal > dis_portal_oships * 2:
            # Find our closest ship of the o_ship which is close to our portal
            # Ignore our ship that are close of the opponent portal
            closest_fight_ship = None
            shortest_dis = 10 ** 10
            for fight_ship in fight_ships.values():

                # The position of the fight ship
                fight_ship_pos = tuple(fight_ship['position'])
                # The distance between the fight ship and the opponent ship
                dis_fship_oship = len(ship_trip(tuple(fight_ship['position']), tuple(o_ship['position'])))
                # The distance between the fight ship and the opponent portal
                dis_oportal_fship = len(ship_trip(o_portal, fight_ship_pos))
                # The distance between the fight ship and the AI portal
                dis_portal_fship = len(ship_trip(portal, fight_ship_pos))

                # Find the closest ship from the opponent ship and our portal
                if dis_fship_oship < shortest_dis and dis_oportal_fship > dis_portal_fship:
                    shortest_dis = dis_fship_oship
                    closest_fight_ship = fight_ship

            # If the closest ship is the current ship, target the o_ship and fire when in range
            if ship_name == closest_fight_ship:
                # If ship is in range, fire
                if reachable:
                    batch_actions.append((2, 'fire', reachable[0]))
                # Else, track it
                else:
                    batch_actions.append((2, 'move', ship_trip(ship_pos, o_ship_pos)[0]))

    # List reachable points (in range without firing ourselves)
    reachable = [pt for pt in o_portal_hb if pt not in hitbox_current_ship and mw.distance(ship_pos, pt) <= reach]
    # If the current ship is able to fire the portal (without firing himself), do it!
    if len(reachable) != 0:
        batch_actions.append((0, 'fire', reachable[0]))

    # If ship cant do anything else than going to the opponent's portal, go there
    else:
        target = closest_pt_at_range(ship_pos, o_portal_hb, reach)
        batch_actions.append((0, 'move', ship_trip(ship_pos, target)[0]))

    # --------  Select best action to do in the list and generate command line --------
    # Sort all possibles actions by priority
    if batch_actions:
        batch_actions = sorted(batch_actions, key=itemgetter(0), reverse=True)
        action = batch_actions[0]
        action_type = action[1]

        if action_type == 'fire':
            cmds += fire_ship(ship_name[0], action[2])
        elif action_type == 'move':
            cmds += move_ship(ship_name[0], action[2])

        # Check if only one action has been selected
        if len(cmds.split(' ')) > 1:
            cmds = cmds.split(' ')[0] + ' '

    return cmds

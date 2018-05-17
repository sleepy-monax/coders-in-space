#-*- coding: utf-8 -*-
import sys
from termcolor import colored
from random import randint
import time
import copy
import remote_play


def start_game(file, p1, p2, online, player_id=None, remote_IP=None):
    """Start the game and continue until the game is over.
    Actions of player are asked at every turns.
    The file has to be stoked in the same repertory.

    Parameter
    ---------
    file: name of the file (string)
    p1: True if the player 1 is a player, False otherwise (bool)
    p2: False if the player 2 is a player, False otherwise (bool)
    online: True if the game is online, False otherwise (bool)
    player_id: player's number of the online player, has to be 1 or 2 and online = True (int, optional)
    remote_IP: IP of the online player (str, optional)

    Note
    ----
    it's the only one function that has to be called
    the online player define by player_id doesn't matter of the p1/p2 associated
    only one player can be online

    Version
    -------
    specification: José Balon (v.1 02/03/2018)
    implementation: José Balon (v.1 21/03/2018)"""

    # initialisation
    configurations = configurations_treatment(file)
    data = data_creation(configurations)
    game_is_over = False

    # online initialisation
    if online:
        connection = remote_play.connect_to_player(player_id, remote_IP, False)

    # running
    while not game_is_over:

        # display
        print(UI_display(data))

        # wait a second if there is no player
        if not p1 and not p2:
            for i in range(1, 0, -1):
                print(i, end=' ')
                time.sleep(1)
            print('\n')

        # actions of players
        orders = {'buy': [], '(un)lock': [], 'move': [], 'attack': []}

        # ask player 1
        if online and player_id == 1:
            order = remote_play.get_remote_orders(connection)
        elif p1:
            print('player_1 (' + str(data['ores']['player_1']) + '),', end=' ')

            for entity in data['player_1']:
                print(entity + str(data['player_1'][entity]['pos'][0]), end=', ')
            print('\n')

            order = input('Actions of player 1: ')

            remote_play.notify_remote_orders(connection, order)
        else:
            order = AI(data, 'player_1')
        if online and player_id != 1:
            remote_play.notify_remote_orders(connection, order)

        orders = ask_orders(orders, order, 'player_1')

        # ask player 2
        if online and player_id == 2:
            order = remote_play.get_remote_orders(connection)
        elif p1:
            print('player_2 (' + str(data['ores']['player_2']) + '),', end=' ')

            for entity in data['player_2']:
                print(entity + str(data['player_2'][entity]['pos'][0]), end=', ')
            print('\n')

            order = input('Actions of player 2: ')

            remote_play.notify_remote_orders(connection, order)
        else:
            order = AI(data, 'player_2')
        if online and player_id != 2:
            remote_play.notify_remote_orders(connection, order)

        orders = ask_orders(orders, order, 'player_2')

        # phase 1
        data = purchase_phase(data, orders)

        # phase 2
        data = lock_phase(data, orders)

        # phase 3.1
        data = move_phase(data, orders)

        # phase 3.2
        data = attack_phase(data, orders)

        # phase 4
        data = mining_phase(data)

        game_is_over = is_game_over(data)

    print(stats_display(data))


def configurations_treatment(file):
    """Return a dictionary contains the parameters contents in the file.

    Parameter
    ---------
    file: name of the file (string)

    Return
    ------
    configurations: parameters of the game (dico)

    Notes
    -----
    configurations is composed with 4 keys:
        'size':(line, column) (tuple)
            line: number of lines of the board (int)
            column: number of columns of the board (int)
        'portal_1':(line, column) (tuple)
        'portal_2':(line, column) (tuple)
        'asteroids':[dictionaries for every asteroids] (list)
            dictionaries:
                'pos':(line, column)
                'amount': amount of the asteroid (int)
                'speed': mining speed (int)
    configurations file have to be in the same repertory

    Version
    -------
    specification: José Balon (v.2 19/03/2018)
    implementation: José Balon (v.2 16/04/2018)"""

    # read the configuration file
    fh = open(file, 'r')
    lines = fh.readlines()
    fh.close()

    # initialisation
    configurations = {}
    asteroids = {}

    # treat lines
    while lines:

        # first part of the file
        if 'size:' in lines[0]:
            size = str.split(str.split(lines[1], '\n')[0], ' ')
            configurations['size'] = (int(size[0]), int(size[1]))
            lines = lines[2:]

        # second part of the file
        elif 'portals:' in lines[0]:
            portal_1 = str.split(str.split(lines[1], '\n')[0], ' ')
            portal_2 = str.split(str.split(lines[2], '\n')[0], ' ')
            configurations['portal_1'] = (int(portal_1[0]),int(portal_1[1]))
            configurations['portal_2'] = (int(portal_2[0]),int(portal_2[1]))
            lines = lines[3:]

        # third part of the file
        elif 'asteroids:' in lines[0]:
            nb = 1
            for asteroid in lines[1:]:
                asteroid = str.split(str.split(asteroid, '\n')[0], ' ')
                pos, amount, speed = (int(asteroid[0]), int(asteroid[1])), int(asteroid[2]), int(asteroid[3])
                asteroids[str(nb)] = {'pos': pos, 'amount': amount, 'speed': speed}
                nb += 1
            lines = lines[nb + 1:]
            configurations['asteroids'] = asteroids

        else:
            raise ValueError('File is not correctly done')

    return configurations


def data_creation(configurations):
    """Create a data structure contains data about every entities.

    Parameter
    ---------
    configurations: parameters of the game (dico)

    return
    ------
    data: data of entities (dico)

    note
    ----
    data contains as much keys (their names) as number of entities (ships, asteroids, portals) on the board.
    they contain dictionaries as well, depend of their type
    and all positions of them in a list with the center on the first position
    that contain every data of them, and the owner
    data contains as well the size of the board, portals of players, ores owned by players,
    the total of ores collected and the number of turn with out damage:
        'board_size':(line, column) (tuple)
        'portal_nb': {'pos': [ list of (line, column)], 'life': int}
        'ores': {'player_1: int, ...}
        'total_ores': {'player_1: int, ...}
        'turns_with_no_dmg': (int)
        'asteroids': {asteroids}
        'player_nb': {ships of the player}


    Version
    -------
    specification: José Balon (v.3 19/03/2018)
    implementation: José Balon (v.2 16/04/2018)"""

    # initialisation
    data = {}
    ores = 4
    p_life = 100

    # treat configurations to data
    data['board_size'] = configurations['size']
    data['portal_1'] = {'pos': entity_positions(configurations['portal_1'], 'p'), 'life': p_life}
    data['portal_2'] = {'pos': entity_positions(configurations['portal_2'], 'p'), 'life': p_life}
    data['ores'] = {'player_1': ores, 'player_2': ores}
    data['total_ores'] = {'player_1': ores, 'player_2': ores}
    data['turns_with_no_dmg'] = 0
    data['asteroids'] = configurations['asteroids']
    data['player_1'] = {}
    data['player_2'] = {}

    return data


def entity_positions(center, type):
    """Return all the positions of the entity

    Parameter
    ---------
    center: center of the portal (tuple)
    type: 'S', 'M', 'L' for excavator, 'p' for portal, 's' for scout and 'w' for warship (str)

    Return
    ------
    pos: positions of the entity (list)

    Version
    -------
    specification: José Balon (v.1 19/03/2018)
    implementation: José Balon (v.1 19/03/2018)"""

    # initialisation
    pos = []
    size = []

    # warship size
    if type == 'w':
        lines = columns = (0, 1, 2, -1, -2)
        # generate combinations
        for line in lines:
            for column in columns:
                if not (line == 2 and column == 2) and not (line == 2 and column == -2) and \
                        not (line == -2 and column == 2) and not (line == -2 and column == -2):
                    size.append((line, column))

    # excavator-M and excavator-L size
    elif type == 'M' or type == 'L':
        # excavator-M
        if type == 'M':
            lines = columns = (0, 1, -1)
        # excavator-L
        else:
            lines = columns = (0, 1, 2, -1, -2)
        # generate combinations
        for line in lines:
            for column in columns:
                if line == 0 or column == 0:
                    size.append((line, column))

    # others (excavator-S, portal, scout) size, same pattern
    else:
        # excavator-S
        if type == 'S':
            lines = columns = (0,)
        # portal
        elif type == 'p':
            lines = columns = (0, 1, 2, -1, -2)
        # scout
        elif type == 's':
            lines = columns = (0, 1, -1)
        # generate combinations
        for line in lines:
            for column in columns:
                size.append((line, column))

    # generate positions
    for s in size:
        pos.append((center[0] + s[0], center[1] + s[1]))

    return pos


def ask_orders(orders, actions, player):
    """Return orders filled with actions of the player.

    Parameters
    ----------
    orders: contains actions of players (dico)
    actions: orders of the player for the turn (str)
    player: player who did actions

    Return
    ------
    orders: contains actions of players

    Note
    ----
    orders has 4 keys:
        'buy': [dictionaries for every actions] (list)
            dictionaries:
                'player': player who order (str)
                'type': type of the purchase (str)
                'name': name of the entity (str)
        '(un)lock': [dictionaries for every actions] (list)
            dictionaries:
                'name': name of the entity (str)
                'player': player who order (str)
                'state': state to put the entity, 'lock' or 'unlock' (str)
        'move': [dictionaries for every actions] (list)
            'dictionaries':
                'name': name of the entity (str)
                'pos': (line, column) (tuple)
                'player': player who order (str)
        'attack': [dictionaries for every actions]
            dictionaries:
                'name': name of the entity (str)
                'pos': (line, column) (tuple)
                'player': player who order (str)

    Version
    -------
    specification: José Balon (v.1 02/03/2018)
    implementation: José balon (v.1 16/03/2018)"""

    # compute if there is orders to compute
    if actions != '':
        # making a list of every action, even if only one action
        if ' ' in actions:
            actions = str.split(actions, ' ')
        else:
            actions = [actions]

        for action in actions:
            action = str.split(action, ':')

            # treat move
            if action[1][0] == '@':
                pos = str.split(action[1][1:], '-')
                for i in range(len(pos)):
                    pos[i] = int(pos[i])
                orders['move'].append({'pos': tuple(pos), 'player': player, 'name': action[0]})

            # treat attack
            elif action[1][0] == '*':
                pos = str.split(action[1][1:], '-')
                for i in range(len(pos)):
                    pos[i] = int(pos[i])
                orders['attack'].append({'pos': tuple(pos), 'player': player, 'name': action[0]})

            # treat (un)lock
            elif action[1] == 'lock' or action[1] == 'release':
                orders['(un)lock'].append({'name': action[0], 'player': player, 'state': action[1]})

            # treat buy
            elif action[1] == 'scout' or action[1] == 'warship' or action[1] == 'excavator-S' or \
                    action[1] == 'excavator-M' or action[1] == 'excavator-L':
                orders['buy'].append({'name': action[0], 'type': action[1], 'player': player})

    return orders


def purchase_phase(data, orders):
    """Make every actions of the first phase (buy).

    Parameters
    ----------
    data: data of entities (dico)
    orders: contains actions of players (dico)

    Return
    ------
    data: data of entities (dico)

    Version
    -------
    specification: José Balon (v.1 02/03/2018)
    implementation: José Balon (v.2 16/04/2018)"""

    for action in orders['buy']:

        # definition of variables
        purchase = True
        player, name, type = action['player'], action['name'], action['type']
        ores = data['ores'][player]
        if player == 'player_1':
            center = data['portal_1']['pos'][0]
        else:
            center = data['portal_2']['pos'][0]

        if name not in data[player]:

            # fighting ships
            if type == 'scout' or type == 'warship':

                # scout purchase
                if type == 'scout' and ores >= 3:
                    pos, life, attack, range = entity_positions(center, 's'), 3, 1, 3
                    cost = 3

                # warship purchase
                elif type == 'warship' and ores >= 9:
                    pos, life, attack, range = entity_positions(center, 'w'), 18, 3, 5
                    cost = 9

                # impossible to purchase
                else:
                    purchase = False

                # compute in data structure
                if purchase:
                    data[player][name] = {'type': type, 'pos': pos, 'life': life, 'moved': False, 'attack': attack,
                                          'range': range}
                    data['ores'][player] -= cost

                    print('%s has been bought as a %s by %s' % (name, type, player))

            # mining ships
            else:

                excavator = type[-1]

                # excavator-S purchase
                if type == 'excavator-S' and ores >= 1:
                    pos, tonnage, life = entity_positions(center, 'S'), 1, 2
                    cost = 1

                # excavator-M purchase
                elif type == 'excavator-M' and ores >= 2:
                    pos, tonnage, life = entity_positions(center, 'M'), 2, 3
                    cost = 2

                # excavator-L purchase
                elif type == 'excavator-L' and ores >= 4:
                    pos, tonnage, life = entity_positions(center, 'L'), 8, 6
                    cost = 4

                # impossible to purchase
                else:
                    purchase = False

                # compute in data structure
                if purchase:
                    data[player][name] = {'type': 'excavator', 'pos': pos, 'excavator': excavator,
                                          'tonnage': tonnage, 'life': life, 'state': 'release', 'ores': 0}
                    data['ores'][player] -= cost

                    print('%s has been bought as a %s by %s' % (name, type, player))

    return data


def lock_phase(data, orders):
    """Make every actions of the second phase ((un)lock).

    Parameters
    ----------
    data: data of entities (dico)
    orders: contains actions of players (dico)

    Return
    ------
    data: data of entities (dico)

    Version
    -------
    specification: José Balon (v.1 02/03/2018)
    implementation: José Balon (v.2 16/04/2018)"""

    # proces every (un)lock order
    for action in orders['(un)lock']:

        # initialisation
        name, player, state = action['name'], action['player'], action['state']

        # analyse if it's an excavator
        if name in data[player] and data[player][name]['type'] == 'excavator':
            ship_pos = data[player][name]['pos'][0]
            # analyse if there is only one order
            if not other_order(name, orders['(un)lock']):
                permission = False
                if state == 'release':
                    permission = True

                # analyse if it's on his own portal or on an asteroid
                # own portal
                if player == 'player_1':
                    portal = 'portal_1'
                else:
                    portal = 'portal_2'
                portal = data[portal]['pos']
                if pos_in_positions(ship_pos, portal):
                    permission = True
                # on an asteroid
                if not permission:
                    e = 1
                    while not permission and str(e) in data['asteroids']:
                        if ship_pos == data['asteroids'][str(e)]['pos']:
                            permission = True
                        else:
                            e += 1

                # do the state modification if everything is ok
                if permission:
                    data[player][name]['state'] = state

                    print('%s has been change to %s by %s' % (name, state, player))

    return data


def other_order(name, orders):
    """ Tell if there is more than 1 order of the same type for a ship
    (2 orders of moving, attacking,...)

    Parameters
    ----------
    name: name of the ship to seek orders (str)
    orders: list of orders (dico)

    Return
    ------
    False if only 1 order for the ship, True otherwise (bool)

    Version
    -------
    specification: José Balon (v.1 16/04/2018)
    implementation: José Balon (v.1 16/04/2018)"""

    # initialisation
    nb = 0

    # loop
    for action in orders:
        if action['name'] == name:
            nb += 1
        if nb >= 2:
            return True

    return False


def pos_in_positions(pos, positions):
    """Check if pos is in positions.

    Parameters
    ----------
    pos: position sought (tuple (int, int))
    positions: positions to check in (list)

    Return
    ------
    True if pos is in positions, False otherwise

    Version
    -------
    specification: José Balon (v.1 20/03/2018)
    implementation: José Balon (v.1 20/03/2018)"""

    for position in positions:
        if position == pos:
            return True
    return False


def move_phase(data, orders):
    """Make every actions of the third phase (move).

    Parameters
    ----------
    data: data of entities (dico)
    orders: contains actions of players (dico)

    Return
    ------
    data: data of entities (dico)

    Version
    -------
    specification: José Balon (v.2 20/03/2018)
    implementation: José balon (v.2 16/04/2018)"""

    # keep in memory which ship move
    moved = {'player_1': [], 'player_2': []}

    # treat move's orders
    for action in orders['move']:

        name, player, pos = action['name'], action['player'], action['pos']

        # analyse if it's possible
        if name in data[player]:

            # initialisation
            permission = True
            type = data[player][name]['type']
            origin_l, origin_c = data[player][name]['pos'][0][0], data[player][name]['pos'][0][1]
            destination_l, destination_c = pos[0], pos[1]
            board_l, board_c = data['board_size'][0], data['board_size'][1]

            # block locked excavators
            if type == 'excavator' and data[player][name]['state'] == 'lock':
                permission = False
                print(1)

            # analyse if there is another order for the same ship
            if permission and other_order(name, orders['move']):
                permission = False
                print(2)

            # analyse if the destination is next to the origin
            if permission and not (abs(origin_l - destination_l) <= 1 and abs(origin_c - destination_c) <= 1):
                permission = False
                print(3)

            # analyse if ship doesn't go out of the board
            if permission:
                # excavators
                excavator = None
                if type == 'excavator':
                    excavator = data[player][name]['excavator']
                # excavator-S
                if excavator == 'S' and not (1 <= destination_l and destination_l <= board_l and 1 <= destination_c and destination_c <= board_c):
                    permission = False
                    print(4)
                # scout and excavator-M
                elif type == 'scout' or excavator == 'M':
                    if not (2 <= destination_l and destination_l <= board_l and 2 <= destination_c and destination_c <= board_c):
                        permission = False
                        print(5)
                # warship and excavator-L
                elif type == 'warship' or excavator == 'L':
                    if not (3 <= destination_l and destination_l <= board_l and 3 <= destination_c and destination_c <= board_c):
                        permission = False
                        print(6)

            # move ship if everything is ok
            if permission:
                # prepare for entity_positions
                if type == 'excavator':
                    type = data[player][name]['excavator']
                elif type == 'scout':
                    type = 's'
                else:
                    type = 'w'

                pos = entity_positions(pos, type)
                data[player][name]['pos'] = pos
                data[player][name]['moved'] = True
                moved[player].append(name)

                # display
                pos = pos[0]
                print('%s has moved to %s by %s' % (name, pos, player))

            else:
                print('%s can\'t move' % name)

    # set ships that has not move to False
    for player in ('player_1', 'player_2'):
        for entity in data[player]:
            if entity not in moved[player]:
                data[player][entity]['moved'] = False

    return data


def attack_phase(data, orders):
    """Make every actions of the second part of the third phase (attack).

    Parameters
    ----------
    data: data of entities (dico)
    orders: contains actions of players (dico)

    Return
    ------
    data: data of entities (dico)

    Version
    -------
    specification: José Balon (v.1 02/03/2018)
    implementation: José Balon (v.2 16/04/2018)"""

    # keep in memory entities that got shooted
    shooted_entities = {'player_1': [], 'player_2': []}
    dmg_in_the_turn = False

    # treat every attack's order
    for action in orders['attack']:

        # initialisation
        name, player, target = action['name'], action['player'], action['pos']

        # analyse if it's possible
        if name in data[player] and data[player][name]['type'] != 'excavator' and not data[player][name]['moved']\
                and not other_order(name, orders['attack']):
            damage = data[player][name]['attack']
            shooter = data[player][name]['pos'][0]

            # compute Manhattan's distance between the shooter and the targeted case
            distance_of_M = abs(target[0] - shooter[0]) + abs(target[1] - shooter[1])
            if distance_of_M <= data[player][name]['range']:
                print('%s shoot at %s by %s' % (name, target, player))

                # seek every entities shooted
                for player in ('player_1', 'player_2'):
                    for entity in data[player]:

                        # analyse if the entity is shooted
                            if pos_in_positions(target, data[player][entity]['pos']):
                                data[player][entity]['life'] -= damage
                                shooted_entities[player].append(entity)
                                dmg_in_the_turn = True

                                print('%s from %s has %i life point left' % (entity, player, data[player][entity]['life']))

                # seek if a portal is touched
                for portal in ('portal_1', 'portal_2'):
                    if pos_in_positions(target, data[portal]['pos']):
                        data[portal]['life'] -= damage
                        dmg_in_the_turn = True

                        print('%s has %i life point left' % (portal, data[portal]['life']))

    # actualise statistics
    if not dmg_in_the_turn:
        data['turns_with_no_dmg'] += 1

        print('There is %i turns with no damage done' % (data['turns_with_no_dmg']))
    else:
        data['turns_with_no_dmg'] = 0

        # delete dead entities
        for player in ('player_1', 'player_2'):
            for entity in shooted_entities[player]:
                if entity in data[player] and data[player][entity]['life'] <= 0:
                    del data[player][entity]

                    print('%s from %s has died' % (entity, player))

    return data


def mining_phase(data):
    """Make every actions of the fourth phase (mining).

    Parameters
    ----------
    data: data of entities (dico)

    Return
    ------
    data: data of entities (dico)

    Version
    -------
    specification: José Balon (v.1 02/03/2018)
    implementation: José Balon (v.3 02/05/2018)"""

    # compute from asteroids to excavators
    for asteroid in data['asteroids']:

        # initialisation
        pos = data['asteroids'][asteroid]['pos']
        speed = data['asteroids'][asteroid]['speed']
        underminable = 0
        excavators_to_compute = {'player_1': [], 'player_2': []}
        capacity = {'player_1': {}, 'player_2': {}}
        empty = False

        # seek excavators on the asteroid
        for player in ('player_1', 'player_2'):
            for entity in data[player]:
                if data[player][entity]['type'] == 'excavator' and data[player][entity]['pos'][0] == pos\
                        and data[player][entity]['state'] == 'lock':
                    excavators_to_compute[player].append(entity)
                    # keep in memory how many ores it can takes
                    tonnage = data[player][entity]['tonnage']
                    ores = data[player][entity]['ores']
                    available = round(tonnage - ores, 3)
                    if available > speed:
                        available = speed
                    capacity[player][entity] = available
                    underminable += capacity[player][entity]

        # set the maximum that the asteroids can give
        if underminable > data['asteroids'][asteroid]['amount']:
            underminable = data['asteroids'][asteroid]['amount']
            empty = True

        # mining
        if excavators_to_compute['player_1'] or excavators_to_compute['player_2']:
            # initialisation to treat by the less capacity
            ores_given = underminable / (len(excavators_to_compute['player_1']) + len(excavators_to_compute['player_2']))
            ores_given = round(ores_given, 3)
            every_capacity = []
            for player in ('player_1', 'player_2'):
                for excavator in capacity[player]:
                    c = capacity[player][excavator]
                    if c not in every_capacity:
                        every_capacity.append(c)
            every_capacity = sorted(every_capacity)

            # loop
            for cap in every_capacity:
                for player in ('player_1', 'player_2'):
                    for ship in capacity[player]:
                        if capacity[player][ship] == cap:
                            if cap >= ores_given:
                                data[player][ship]['ores'] += ores_given
                                underminable -= ores_given
                                data['asteroids'][asteroid]['amount'] -= ores_given
                            else:
                                data[player][ship]['ores'] += cap
                                underminable -= cap
                                data['asteroids'][asteroid]['amount'] -= cap

                            del excavators_to_compute[player][excavators_to_compute[player].index(ship)]
                            if excavators_to_compute['player_1'] or excavators_to_compute['player_2']:
                                ores_given = underminable / (len(excavators_to_compute['player_1']) + len(
                                    excavators_to_compute['player_2']))
                                ores_given = round(ores_given, 3)

        # completely drain the asteroid
        if empty:
            data['asteroids'][asteroid]['amount'] = 0

    # compute from excavators to owner portal
    for player in ('player_1', 'player_2'):
        for entity in data[player]:
            if data[player][entity]['type'] == 'excavator' and data[player][entity]['state'] == 'lock':
                portal = 'portal_' + player[-1]
                if pos_in_positions(data[player][entity]['pos'][0], data[portal]['pos']):
                    ores = data[player][entity]['ores']
                    data[player][entity]['ores'] = 0
                    data['total_ores'][player] += ores
                    data['ores'][player] += ores

    return data


def UI_display(data):
    """Display the UI.

    Parameters
    ----------
    data: data of entities (dico)

    Return
    ------
    display: chain to print (str)

    Version
    -------
    specification: José Balon (v.2 09/03/2018)
    implementation: José Balon (v.1 16/04/2018)"""

    # initialisation
    UI = []
    board_size = data['board_size']

    # create data structure that hold positions
    for line in range(0, board_size[0]):
        UI.append([])
        for column in range(0, board_size[1]):
            UI[line].append({'type': None, 'player': None})

    # put portals in UI
    for portal in ('portal_1', 'portal_2'):
        position = data[portal]['pos']

        # translate board to data structure
        UI_position = []
        for new_pos in position:
            UI_position += [(new_pos[0] - 1, new_pos[1] - 1)]

        for pos in UI_position:
            player = 'player_' + portal[-1]
            UI[pos[0]][pos[1]]['type'] = '1'
            UI[pos[0]][pos[1]]['player'] = player

    # put asteroids in UI
    for asteroid in data['asteroids']:
        pos = data['asteroids'][asteroid]['pos']

        # convert pos to the UI
        pos = (pos[0] - 1, pos[1] - 1)

        if data['asteroids'][asteroid]['amount'] == 0:
            type = '2'
        else:
            type = '3'
        UI[pos[0]][pos[1]]['type'] = type

    # put every ship in UI
    for player in ('player_1', 'player_2'):
        for entity in data[player]:
            type = data[player][entity]['type']
            position = data[player][entity]['pos']
            e = 1

            # translate board to data structure
            UI_position = []
            for new_pos in position:
                UI_position += [(new_pos[0] - 1, new_pos[1] - 1)]

            # define the type
            if type == 'excavator':
                fillable = data[player][entity]['tonnage'] - data[player][entity]['ores']
                if data[player][entity]['state'] == 'release':
                    if fillable > 0:
                        type = '5'
                    else:
                        type = '6'
                elif fillable > 0:
                    type = '7'
                else:
                    type = '8'

            elif type == 'scout':
                type = '9'

            else:
                type = '10'

            for pos in UI_position:
                if e > 1:
                    type = '4'

                # empty slot or on portal
                if not UI[pos[0]][pos[1]]['type'] or UI[pos[0]][pos[1]]['type'] == '1':
                    UI[pos[0]][pos[1]]['type'] = type
                    UI[pos[0]][pos[1]]['player'] = player

                # same symbol
                elif UI[pos[0]][pos[1]]['type'] == type:
                    if player != UI[pos[0]][pos[1]]['player']:
                        UI[pos[0]][pos[1]]['player'] = 'both'

                # center superior than asteroids and ship case
                elif e == 1 and UI[pos[0]][pos[1]]['type'] in ('2', '3', '4'):
                    UI[pos[0]][pos[1]]['type'] = type
                    UI[pos[0]][pos[1]]['player'] = player

                elif e == 1:
                    if UI[pos[0]][pos[1]]['type'] != type:
                        UI[pos[0]][pos[1]]['type'] = '11'
                    if UI[pos[0]][pos[1]]['player'] != player:
                        UI[pos[0]][pos[1]]['player'] = 'both'

                e += 1

    # definition of the UI
    design = {'player_1': 'blue', 'player_2': 'red', None: 'white', 'both': 'magenta', '1': '×', '2': 'ø', '3': 'o',
              '4': '•', '5': 'ᚇ', '6': 'ᚈ', '7': 'ᚂ', '8': 'ᚃ', '9': '♣', '10': '♠', '11': '∗'}

    # computing the final string to display
    display = ''
    for line in UI:
        for column in line:
            display += '|'
            if not column['type']:
                display += ' '
            else:
                c_display = colored(design[column['type']], design[column['player']])
                display += c_display
        display += '|\n'

    return display


def is_game_over(data):
    """Return the state of the game.

    Parameter
    ---------
    data: data of entities (dico)

    Return
    ------
    True if the game is ended, False otherwise (bool)

    Version
    -------
    specification: José Balon (v.1 02/03/2018)
    implementation: José Balon (v.1 21/03/2018)"""

    if data['turns_with_no_dmg'] == 200:
        return True
    for portal in ('portal_1', 'portal_2'):
        if data[portal]['life'] <= 0:
            return True

    return False


def stats_display(data):
    """Display results of the game.

    Parameter
    ---------
    data: data of entities (dico)

    Version
    -------
    specification: José Balon (v.1 02/03/2018)
    implementation: José Balon (v.1 22/03/2018)"""

    winner = None

    # determine the winner by the destruction of portal
    if data['portal_1']['life'] <= 0:
        if not data['portal_2']['life'] <= 0:
            winner = 'player_2'

    elif data['portal_2']['life'] <= 0:
        if not data['portal_1']['life'] <= 0:
            winner = 'player_1'

    # determine the winner by portal's life left
    elif not data['portal_2']['life'] <= 0 and not data['portal_1']['life'] <= 0:
        p_1_life, p_2_life = data['portal_1']['life'], data['portal_2']['life']
        if p_1_life > p_2_life:
            winner = 'player_1'
        elif p_1_life < p_2_life:
            winner = 'player_2'

    # determine the winner by the total ores extracted
    elif not winner:
        p_1_ores, p_2_ores = data['player_1']['total_ores'], data['player_2']['total_ores']
        if p_1_ores > p_2_ores:
            winner = 'player_1'
        elif p_1_ores < p_2_ores:
            winner = 'player_2'

    # final sentence
    if not winner:
        return 'This is a draw!'

    else:
        return 'The winner is %s. Congratulations!' % winner


def AI_naive(data, player):
    """Return some random actions should be done by a player.

    Parameters
    ----------
    data: data of entities (dico)
    player: player who played by the AI (str)

    Return
    ------
    AI_orders: actions for the turn of the AI (str)

    Version
    -------
    specification: José Balon (v.2 22/03/2018)
    implementation: José Balon (v.1 16/04/2018)"""

    AI_orders = ''

    # do 1 buy if possible
    possibilities = []
    ores = data['ores'][player]
    if ores >= 1:
        possibilities = ['excavator-S', 'excavator-M', 'scout', 'excavator-L', 'warship']
        if ores < 9:
            del (possibilities[4])
            if ores < 4:
                del (possibilities[3])
                if ores < 3:
                    del (possibilities[2])
                    if ores < 2:
                        del (possibilities[1])

    if possibilities != []:
        type = possibilities[randint(0, len(possibilities) - 1)]

        name = 'AI_' + str(randint(0, 99))
        AI_orders += name + ':' + type + ' '

    # move (or not, or attack, or lock) randomly every ship
    for entity in data[player]:
            position = data[player][entity]['pos'][0]
            new_pos = (position[0] + randint(-1, 1), position[1] + randint(-1, 1))

            AI_orders += entity + ':' + '@' + str(new_pos[0]) + '-' + str(new_pos[1]) + ' '

    AI_orders = AI_orders[:-1]

    return AI_orders


def AI(data, player):
    """Return orders chosen by the AI player.

    Parameters
    ----------
    data: data of the game (dico)
    player: player's turn (str)

    Return
    ------
    orders: action of the player

    Note
    ----
    it needs the random API

    Version
    -------
    specification: José balon (v.1 04/05/2018)
    implementation: José balon (v.1 04/05/2018)"""

    # initialisation
    source = copy.deepcopy(data)
    orders = ''
    if player == 'player_1':
        enemy_player = 'player_2'
        portal = 'portal_1'
        enemy_portal = 'portal_2'
    else:
        enemy_player = 'player_1'
        portal = 'portal_2'
        enemy_portal = 'portal_1'

    portal_center = source[portal]['pos'][0]
    enemy_portal_center = source[enemy_portal]['pos'][0]

    # ships purchase
    # initialisation
    purchase = True
    excavator_purchase = False

    # compute the difference between player
    asset_1 = asset_compute(data, 'player_1')
    asset_2 = asset_compute(data, 'player_2')

    if player == 'player_1' and asset_1 > asset_2 * 1.5:
        difference = True
    elif player == 'player_2' and asset_2 > asset_1 * 1.5:
        difference = True
    else:
        difference = False


    # loop
    while purchase:
        ores = source['ores'][player]

        if difference:
            if ores >= 9:
                source, order = AI_purchase(source, player, 'warship')
                orders += order

            elif ores >= 3:
                source, order = AI_purchase(source, player, 'scout')
                orders += order

            else:
                purchase = False

        else:
            nb_excavators = 0
            nb_asteroids = 0
            nb_S = 0
            nb_M = 0
            nb_scout = 0
            nb_warship = 0
            enemy_nb_scout = 0
            enemy_nb_warship = 0

            # compute the number of ship
            for entity in source[player]:
                if source[player][entity]['type'] == 'excavator':
                    nb_excavators += 1

                    if source[player][entity]['excavator'] == 'S':
                        nb_S += 1

                    elif source[player][entity]['excavator'] == 'M':
                        nb_M += 1

                elif source[player][entity]['type'] == 'scout':
                    nb_scout += 1

                elif source[player][entity]['type'] == 'warship':
                    nb_warship += 1

            # compute the number of enemy ship
            for entity in source[enemy_player]:
                if source[enemy_player][entity]['type'] == 'scout':
                    enemy_nb_scout += 1

                elif source[enemy_player][entity]['type'] == 'warship':
                    enemy_nb_warship += 1

            # compute the number of asteroids
            for asteroid in source['asteroids']:
                if source['asteroids'][asteroid]['amount'] > 0:
                    nb_asteroids += 1

            # compute if more excavator are necessary
            if nb_excavators < nb_asteroids * 2:
                excavator_purchase = True

            # if it needs more excavator-S
            if excavator_purchase and nb_S < 4 and ores >= 1:
                source, order = AI_purchase(source, player, 'excavator-S')
                orders += order

            # if AI has less warship
            elif nb_warship < enemy_nb_warship and ores >= 9:
                source, order = AI_purchase(source, player, 'wharship')
                orders += order

            # if AI has less scout or AI needs more scout
            elif (nb_scout < enemy_nb_scout and ores >= 3) or (nb_scout < 1 and ores >= 3):
                source, order = AI_purchase(source, player, 'scout')
                orders += order

            # if AI needs more excavator-M
            elif excavator_purchase and nb_M < 2 and ores >= 2:
                source, order = AI_purchase(source, player, 'excavator-M')
                orders += order

            elif excavator_purchase and ores >= 4:
                source, order = AI_purchase(source, player, 'excavator-L')
                orders += order

            elif ores >= 9:
                source, order = AI_purchase(source, player, 'excavator-S')
                orders += order

            else:
                purchase = False

    # ship's actions
    for entity in source[player]:
        pos = source[player][entity]['pos'][0]

        # extractors actions
        if source[player][entity]['type'] == 'excavator':
            ores = source[player][entity]['ores']
            tonnage = source[player][entity]['tonnage']
            on_portal = pos_in_positions(pos, source[portal]['pos'])
            targetable = False

            # locked situation
            if source[player][entity]['state'] == 'lock':

                # compute if the excavator is targetable
                for enemy_ship in source[enemy_player]:
                    if source[enemy_player][enemy_ship]['type'] != 'excavator':
                        is_shoot = shootable(source[enemy_player][enemy_ship]['pos'][0], source[enemy_player][enemy_ship]['range'], source[player][entity]['pos'])
                        if is_shoot:
                            targetable = True

                # can be shoot or full or going to be empty
                if targetable or ores == tonnage or on_portal:
                    source[player][entity]['state'] = 'release'
                    orders += entity + ':' + 'release' + ' '

                # compute the extracted asteroid is empty
                else:
                    for asteroid in source['asteroids']:
                        if pos == source['asteroids'][asteroid]['pos'] and source['asteroids'][asteroid]['amount'] == 0:
                            source[player][entity]['state'] = 'release'
                            orders += entity + ':' + 'release' + ' '

            # released situation
            if source[player][entity]['state'] == 'release':

                # if an enemy ship can shoot him
                if targetable:
                    orders += entity + ':@' + move_to(pos, portal_center) + ' '

                # (almost) full excavator
                elif tonnage - ores < 0.5:
                    if on_portal:
                        orders += entity + ':' + 'lock' + ' '

                    # compute the pos to go (to portal)
                    else:
                        orders += entity + ':@' + move_to(pos, portal_center) + ' '

                # moving to an asteroid
                else:
                    every_dist = []
                    possible_ast = {}

                    # seek not empty asteroids
                    for asteroid in source['asteroids']:
                        if source['asteroids'][asteroid]['amount'] != 0:
                            dist = dist_M(pos, source['asteroids'][asteroid]['pos'])
                            every_dist.append(dist)

                            if dist not in possible_ast:
                                possible_ast[dist] = []

                            possible_ast[dist].append(asteroid)

                    # compute the closer
                    every_dist = sorted(every_dist)

                    if every_dist != []:
                        # if excavator is on the asteroid
                        if every_dist[0] == 0:
                            orders += entity + ':' + 'lock' + ' '

                        else:
                            destination = move_to(pos, source['asteroids'][possible_ast[every_dist[0]][0]]['pos'])
                            orders += entity + ':@' + destination + ' '

                    # if there's no asteroids left
                    else:
                        destination = move_to(pos, enemy_portal_center)
                        orders += entity + ':@' + destination + ' '


        # warships actions
        else:
            center = source[player][entity]['pos'][0]
            range = source[player][entity]['range']
            targets = {}
            portal_target, portal_target_pos = shootable(center, range, source[enemy_portal]['pos'])

            # seek targetable enemy ship
            for enemy_ship in source[enemy_player]:
                targetable, target_pos = shootable(center, range, source[enemy_player][enemy_ship]['pos'])

                if targetable:
                    targets[enemy_ship] = target_pos

            # if there's a target
            if targets != {}:

                # short the lowest (life)
                target = None
                for possible_target in targets:
                    if target == None or source[enemy_player][possible_target]['life'] < source[enemy_player][target]['life']:
                        target = possible_target

                # compute when scout is upper than enemy ship
                if source[player][entity]['type'] == 'warship' or source[player][entity]['life'] >= source[enemy_player][target]['life'] or pos_in_positions(source[player][entity]['pos'][0], source[portal]['pos']):

                    # create the order
                    orders += entity + ':*' + str(targets[target][0]) + '-' + str(targets[target][1]) + ' '
                    source[enemy_player][target]['life'] -= source[player][entity]['attack']

                else:
                    destination = move_to(pos, portal_center)
                    orders += entity + ':@' + destination + ' '

            # enemy portal target
            elif portal_target:
                orders += entity + ':*' + str(portal_target_pos[0]) + '-' + str(portal_target_pos[1]) + ' '

            # no target
            else:
                enemy_excavator = {}
                enemy_excavator_dist = []

                # seek if an enemy warship can shoot him
                targetable = False
                for enemy_ship in source[enemy_player]:
                    if source[enemy_player][enemy_ship]['type'] == 'warship':
                        targetable, target_pos = shootable(source[enemy_player][enemy_ship]['pos'][0],source[enemy_player][enemy_ship]['range'], source[player][entity]['pos'])

                    # compute the distance to every enemy excavator
                    elif source[enemy_player][enemy_ship]['type'] == 'excavator':
                        distance = dist_M(source[player][entity]['pos'][0], source[enemy_player][enemy_ship]['pos'][0])

                        if distance not in enemy_excavator:
                            enemy_excavator[distance] = []
                            enemy_excavator_dist.append(distance)
                        enemy_excavator[distance].append(enemy_ship)

                # can be shooted
                if targetable and not pos_in_positions(source[player][entity]['pos'][0], source[portal]['pos']):
                    destination = move_to(pos, portal_center)
                    orders += entity + ':@' + destination + ' '

                # going to enemy excavator
                elif enemy_excavator_dist != []:
                    # seek the closest enemy excavators
                    enemy_excavator_dist = sorted(enemy_excavator_dist)

                    # short the lowest (ores)
                    target = None
                    for possible_target in enemy_excavator[enemy_excavator_dist[0]]:
                        if target == None or source[enemy_player][possible_target]['ores'] < \
                                source[enemy_player][target]['ores']:
                            target = possible_target

                    # treat order
                    destination = source[enemy_player][target]['pos'][0]
                    destination = move_to(pos, destination)
                    orders += entity + ':@' + destination + ' '

                # going to enemy portal
                else:
                    destination = move_to(pos, enemy_portal_center)
                    orders += entity + ':@' + destination + ' '

    if orders != '':
        orders = orders[:-1]

    return orders


def asset_compute(data, player):
    """Return the asset of player

    Parameters
    ----------
    data: data of the game (dico)
    player: player's turn (str)

    Return
    ------
    asset: amount of the asset of the player (int)

    Version
    -------
    specification: José balon (v.1 04/05/2018)
    implementation: José balon (v.1 04/05/2018)"""

    # initialisation
    asset = 0

    # compute
    asset += data['ores'][player]

    for ship in data[player]:
        type = data[player][ship]['type']

        if type == 'scout':
            asset += 3
        elif type == 'warship':
            asset += 9

    return asset


def AI_purchase(source, player, type):
    """Return source with the purchase of the ship

    Parameters
    ----------
    source: data of the game (dico)
    player: player to evaluate (str)
    type: type of the ship to buy, can be 'warship', 'scout', 'excavator-S', 'excavator-M' or 'excavator-L' (str)

    Return
    ------
    source: data of the game (dico)
    order: the order executed (str)

    Notes
    -----
    does not evaluate if the player can purchase the ship, it only modifies the data structure as asked

    Version
    -------
    specification: José balon (v.1 04/05/2018)
    implementation: José balon (v.1 04/05/2018"""

    # name generator
    unused = False
    possibilities = ['Matricule']

    while not unused:
        name = possibilities[randint(0, len(possibilities) - 1)]
        name += str(randint(1000, 5000))
        if name not in source[player]:
            unused = True

    # add to source
    # initialisation
    if player == 'player_1':
        center = source['portal_1']['pos'][0]
    else:
        center = source['portal_2']['pos'][0]

    # fighting ships
    if type == 'scout' or type == 'warship':

        # scout purchase
        if type == 'scout':
            pos, life, attack, range = entity_positions(center, 's'), 3, 1, 3
            cost = 3

        # warship purchase
        elif type == 'warship':
            pos, life, attack, range = entity_positions(center, 'w'), 18, 3, 5
            cost = 9

        # compute in data structure
        source[player][name] = {'type': type, 'pos': pos, 'life': life, 'moved': False, 'attack': attack, 'range': range}
        source['ores'][player] -= cost

    # mining ships
    else:

        excavator = type[-1]

        # excavator-S purchase
        if type == 'excavator-S':
            pos, tonnage, life = entity_positions(center, 'S'), 1, 2
            cost = 1

        # excavator-M purchase
        elif type == 'excavator-M':
            pos, tonnage, life = entity_positions(center, 'M'), 2, 3
            cost = 2

        # excavator-L purchase
        elif type == 'excavator-L':
            pos, tonnage, life = entity_positions(center, 'L'), 8, 6
            cost = 4

        # compute in data structure
        source[player][name] = {'type': 'excavator', 'pos': pos, 'excavator': excavator, 'tonnage': tonnage,
                                'life': life, 'state': 'release', 'ores': 0}
        source['ores'][player] -= cost

    # create order
    order = name + ':' + type + ' '

    return source, order


def dist_M(pos_1, pos_2):
    """Return the distance of Manathan between 2 position

    Parameters
    ----------
    pos_1: first position (tuple)
    pos_2: second position (tuple)

    Return
    ------
    distance: distance of Manathan (int)

    Version
    -------
    specification: José Balon v.1 (06/05/2018)
    implementation: José Balon v.1 (06/05/2018)"""

    return abs(pos_1[0] - pos_2[0]) + abs(pos_1[1] - pos_2[1])


def move_to(initial_pos, destination_pos):
    """Return the next position to move to go (dist of M == 1).

    Parameters
    ----------
    initial_pos: the position where the ship is (tuple)
    destination_pos: the position where the ship has to go (tuple)

    Return
    ------
    position: position to next move (str)

    Notes
    -----
    position is an str for order: str(int) + '-' + str(int)

    Version
    -------
    specification: José Balon v.1 (06/05/2018)
    implementation: José Balon v.1 (06/05/2018)"""

    # compute the line direction
    if initial_pos[0] < destination_pos[0]:
        l = 1
    elif initial_pos[0] > destination_pos[0]:
        l = -1
    else:
        l = 0

    # compute the column direction
    if initial_pos[1] < destination_pos[1]:
        c = 1
    elif initial_pos[1] > destination_pos[1]:
        c = -1
    else:
        c = 0

    return str(initial_pos[0] + l) + '-' + str(initial_pos[1] + c)


def total_scope(pos, max_range):
    """Return every position that the ship can shoot.

    parameters
    ----------
    pos: position to shoot from (tuple)
    max_range: range of the ship (int)

    Return
    ------
    scope: position shootable (list)

    Version
    -------
    specification: José Balon v.1 (06/05/2018)
    implementation: José Balon v.1 (06/05/2018)"""

    # initialisation
    scope = []
    max_range += 1

    # range of attack
    for line in range(0, max_range):
        for column in range(0, max_range):
            for i in (-1, 1):
                scope.append((pos[0] + line * i, pos[1] + column * i))
    return scope


def shootable(origin, range, positions):
    """Return if the origin can shoot to one of the positions given and the specific position(only one)

    Parameters
    ----------
    origin: position which shoot from (tuple)
    range: range of the ship (int)
    positions: positions of the target (list)

    Return
    ------
    targetable: True if it shootable, False otherwise (bool)
    target_pos: position shootable, None otherwise (tuple, None)

    Version
    -------
    specification: José Balon (v.1 16/05/2018)
    implementation : José Balon (v.1 16/05/2018)"""

    for pos in positions:
        if dist_M(origin, pos) <= range:
            return True, pos
    return False, None


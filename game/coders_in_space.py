# -*- coding: utf-8 -*-

# Coders In Space - Final Version.
# Wrote by Alisson Leist, Bayron Mahy and Nicolas Van Bossuyt

from math import *
from time import sleep  # because everyone needs to rest.
from graphics import *
from remote_play import notify_remote_orders, get_remote_orders, connect_to_player, disconnect_from_player
import os, sys, random

# Constant for battle template.
human_vs_ai = ('human', 'ai')
human_vs_human = ('human', 'human')
human_vs_remote = ('human', 'remote')
ai_vs_ai = ('ai', 'ai')
ai_vs_human = ('ai', 'human')
ai_vs_remote = ('ai', 'remote')
remote_vs_ai = ('remote', 'ai')
remote_vs_human = ('remote', 'human')

# Constant for logs type.
log_info = 0
log_warning = 1
log_error = 2
log_input = 3
log_death = 4


# +------------------------------------------------------------------------------------------------------------------+ #
# | Game Loop                                                                                                        | #
# +------------------------------------------------------------------------------------------------------------------+ #

def play_game(level_name, players_names, players_types, remote_id=None, remote_ip=None, max_rounds_count=20):
    """
    Main function which executes the game loop.

    Parameters
    ----------
    level_name:    name of game level (str).
    players_names: names of players (list(string)).
    players_types: types of players (list(string)).

    (optional) no_splash: ship the splash screen (bool).
    (optional) no_gui:    disable game user interface (bool).
    (optional) remote_id: ID of the remote player (int).
    (optional) remote_ip: IP of the remote player (str).
    (optional) max_rounds_count: number of rounds (int).

    Return
    ------
    game_data: game data at the end of the game (str).

    Version
    -------
    Specification:  Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
                    Nicolas Van Bossuyt (v2. 25/04/2017)
    Implementation: Bayron Mahy, Nicolas Van Bossuyt (v1. 15/02/17)
                    Nicolas Van Bossuyt (v2. 25/04/2017)
    """

    # Create the new game.
    is_remote_game = (remote_id != None and remote_ip != None)



    # Connected to the remote player.
    if is_remote_game:
        print "CodersInSpace - Online multiplayer : Initialazing..."
        game_data = initialize_game(level_name, players_names, players_types, max_rounds_count,
                                    connect_to_player(remote_id, remote_ip, True))
    else:
        game_data = initialize_game(level_name, players_names, players_types, max_rounds_count)

    # Show the splash screen.
    show_splash_game(game_data, is_remote_game)

    # Setup game loop.
    is_ship_buy = True
    game_running = True
    total_turn = -1

    # The main game loop.
    while game_running:  

        # Cleaning the pending_attack list.
        game_data['pending_attacks'] = []
        pending_command = []

        if total_turn > -1:
            write_log(game_data, u'It\'s turn nb %d' % (total_turn), log_info)

        # Show the game board to the human player.
        show_game_screen(game_data)
        raw_input()
        
		# getting players input.
        for player in players_names:
            if is_ship_buy or game_data['players'][player]['nb_ships'] > 0:
                pending_command.append((player, get_game_input(player, is_ship_buy, game_data)))
            else:
                write_log(game_data, player + ' has lost all these ships, so he has nothing to do.', log_warning)

        # Executing pending commands.
        for command in pending_command:
            if is_ship_buy:
                game_data = command_buy_ships(command[1], command[0], game_data)
            else:
                game_data = parse_command(command[1], command[0], game_data)

        is_ship_buy = False

        # Show the game board to the human player.
        show_game_screen(game_data)

        # Do game loop.
        game_data = do_moves(game_data)
        game_data = take_abandoned_ship(game_data)
        game_data = do_attack(game_data)
		
		
        # Increment the round counter.
        game_data['nb_rounds'] += 1
        total_turn += 1
        game_running = is_game_continue(game_data)

    show_game_screen(game_data)

    # Disconnect the remote player.
    if is_remote_game:
        disconnect_from_player(game_data['connection'])

    # Show the end game screen.
    show_end_game(game_data)
    raw_input()

    return game_data


def initialize_game(level_name, players_names, players_types, max_rounds_count, connection=None):
    """
    Create a new game from a '.cis' file.

    Parameters
    ----------
    level_name: name of game level (str).
    players_names: names of players (list(string)).
    players_types: types of players (list(string)).
    max_rounds_count: maximum round count (int).
    (optional) connection: connection to the remote player.

    Return
    -------
    game_data: new game stats (dic).

    Version
    -------
    Specification:  Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
                    Nicolas Van Bossuyt (v2 25/04/2017).

    Implementation: Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
                    Bayron Mahy, Nicolas Van Bossuyt (v2. 13/02/17)
                    Nicolas Van Bossuyt (v3. 23/02/17)
                    Nicolas Van Bossuyt (v4. 25/04/17)
    """
    # Create the log file.
    open('log.txt', 'w').close()

    # Create a random game board.
    if level_name == 'random':
        create_random_game_board('board/random.cis', (30, 30), 26)
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
                 'pending_attacks': [],
                 'game_logs': [],
                 'winners': [],
                 'is_remote_game': connection is not None,
                 'max_nb_rounds': max_rounds_count}

    # Create ship specs sheet.
    game_data['model_ship']['fighter'] = {'icon': u'F', 'max_heal': 3, 'max_speed': 5, 'damages': 1, 'range': 5,
                                          'price': 10}
    game_data['model_ship']['destroyer'] = {'icon': u'D', 'max_heal': 8, 'max_speed': 2, 'damages': 2, 'range': 7,
                                            'price': 20}
    game_data['model_ship']['battlecruiser'] = {'icon': u'B', 'max_heal': 20, 'max_speed': 1, 'damages': 4, 'range': 10,
                                                'price': 30}

    # Create the game board.
    for line in range(game_file['size'][0]):
        for column in range(game_data['board_size'][1]):
            game_data['board'][(line, column)] = []

    # Place abandonned ships.
    for ships in game_file['ships']:
        game_data['ships'][ships[2]] = {'type': ships[3], 'heal_points': game_data['model_ship'][ships[3]]['max_heal'],
                                        'facing': ships[4], 'speed': 0, 'owner': 'none',
                                        'location': (ships[0], ships[1]), 'objective': 'none', 'objective_path': []}
        game_data['board'][(ships[0], ships[1])].append(ships[2])

    index_player = 0

    for player in players_names:
        # Create new player.
        if index_player < 4:
            game_data['players'][player] = {'name': player, 'money': 100, 'nb_ships': 0, 'objectives': []}

            # Set the player type.
            game_data['players'][player]['type'] = players_types[index_player]

            # Set player starting pos.
            if index_player == 0:
                game_data['players'][player]['ships_starting_point'] = (9, 9)
                game_data['players'][player]['ships_starting_facing'] = (1, 1)
                game_data['players'][player]['color'] = 'red'

            elif index_player == 1:
                game_data['players'][player]['ships_starting_point'] = (
                    game_data['board_size'][0] - 10, game_data['board_size'][1] - 10)
                game_data['players'][player]['ships_starting_facing'] = (-1, -1)
                game_data['players'][player]['color'] = 'blue'

            elif index_player == 2:
                game_data['players'][player]['ships_starting_point'] = (game_data['board_size'][0] - 10, 9)
                game_data['players'][player]['ships_starting_facing'] = (-1, 1)
                game_data['players'][player]['color'] = 'yellow'

            elif index_player == 3:
                game_data['players'][player]['ships_starting_point'] = (9, game_data['board_size'][1] - 10)
                game_data['players'][player]['ships_starting_facing'] = (1, -1)
                game_data['players'][player]['color'] = 'magenta'

        else:
            write_log(game_data, 'There is too many player, %s is a loser he must be watch you playing' % player, log_warning)

        index_player += 1

    if connection is not None:
        game_data['connection'] = connection

    return game_data


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
    Specification:  Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Alisson Leist (v1. 20/02/17)
                    Nicolas Van Bosuuyt (v2. 23/02/17)
                    Nicolas Van Bossuyt (v3. 09/03/17)
    """
    for ship in game_data['ships']:
        location = game_data['ships'][ship]['location']
        new_location = predict_next_location(game_data, ship)

        # Move the ship.
        game_data['board'][location].remove(ship)
        game_data['board'][new_location].append(ship)
        game_data['ships'][ship]['location'] = new_location

    return game_data


def take_abandoned_ship(game_data):
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
                    if not ship_owner in owners:
                        owners.append(ship_owner)

        if len(owners) == 1:
            owner = owners[0]
            for ship in abandoned_ships:
                abandoned_ship = game_data['ships'][ship].copy()

                # Remove the old ship.
                del game_data['ships'][ship]
                game_data['board'][abandoned_ship['location']].remove(ship)

                # Create the new one.
                abandoned_ship['owner'] = owner
                new_ship_name = "%s_%s" % (owner, ship)

                if new_ship_name in game_data['ships']:
                    new_ship_name += '_2'

                # Place the new ship on the game board.
                game_data['board'][abandoned_ship['location']].append(new_ship_name)
                game_data['ships'][new_ship_name] = abandoned_ship
                game_data['players'][owner]['nb_ships'] += 1
                write_log(game_data, '%s as take %s !' % (owner, new_ship_name), log_info)

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

    # Checking players who pocess more than one ship
    for player in game_data['players']:
        if player != 'none' and game_data['players'][player]['nb_ships'] > 0:
            not_loser.append(player)

    # Check if the game continue.
    if len(not_loser) > 1 and game_data['nb_rounds'] < game_data['max_nb_rounds']:
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
    Compute the total ship value of a player.

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


# +------------------------------------------------------------------------------------------------------------------+ #
# | Players                                                                                                          | #
# +------------------------------------------------------------------------------------------------------------------+ #

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
        # Get input from the dumb ai.
        if buy_ships:
            player_input = get_ai_spaceships(player_name, game_data)
        else:
            player_input = get_ai_input(game_data, player_name)

    elif player_type == 'remote':
        # Get input from the remote player.
        player_input = get_remote_input(game_data, player_name)

    # Send the order to the remote player.
    if game_data['is_remote_game'] and (player_type == 'human' or player_type == 'ai' or player_type == 'ai_dumb'):
        notify_remote_orders(game_data['connection'], player_input)

    write_log(game_data, '[%s] %s' % (player_name, player_input), log_input)

    return player_input


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
    # Setup main canvas.
    screen_size = get_terminal_size()

    # Show the game board to the human player.
    show_game_screen(game_data)

    # Add a input box.
    c = create_canvas(screen_size[0], 5)
    c = put_box(c, 0, 0, screen_size[0], 5, 'single')
    c = put_text(c, 1, 0, '| PLAYER INPUT |')
    print_canvas(c, screen_size[1] - 4, 0)

    # Getting human player input.
    player_input = raw_input(set_color('\033[%d;%dH %s>' % (screen_size[1] - 2, 3, player_name),
                                       game_data['players'][player_name]['color'], 'white'))
    return player_input


def get_remote_input(game_data, player_name):
    """
    Get input from a remote player.

    Parameter
    ---------
    game_data: data of the game (dic).
    player_name: name of the player (str).

    Return
    ------
    remote_input: input from remote player (str).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
                     Nicolas Van Bossuyt (v2. 03/03/17)
    Implementation: Nicolas Van Bossuyt (v1. 03/03/17)
    """

    print '[ WAITING FOR INPUT from %s ]' % player_name
    return get_remote_orders(game_data['connection'])


def get_ai_input(game_data, player_name):
    """
    Get input from an AI player.
    
    Parameter
    ---------
    player_name: name of the player (str).
    game_data:   state of the game (dic).
    
    Return
    ------
    ai_input: game input from AI (str).
    
    Version
    -------
    Specification:  Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 16/03/17)
                    Nicolas Van Bossuyt (v2. 26/04/17)
    """
    ai_input = ''
    ai_ships = get_ship_by_owner(game_data['ships'], player_name)
    ship_index = 0

    for ship_name in ai_ships:
        ship_index += 1
        ship = game_data['ships'][ship_name]

        print '\033[0;0H[ ' + player_name + ' ]' + ' ' * 3
        print '[ Thinking : %d/%d ]' % (ship_index, len(ai_ships))

        if ship['type'] == 'fighter':
            abandoned_ships = get_ship_by_owner(game_data['ships'], 'none')
            if len(abandoned_ships) > 0:
                ship_order = get_fighter_action(game_data, ship_name, player_name)
            else:
                ship_order = get_battleship_action(game_data, ship_name, player_name)
        else:
            ship_order = get_battleship_action(game_data, ship_name, player_name)
        
        if ship_order != '':
            ai_input += '%s:%s ' % (ship_name[len(player_name) + 1:], ship_order)

    return ai_input[:-1]


def get_ai_spaceships(player_name, game_data):
    """
    Determine what ships to buy and turn it into a regulated command.

    Parameters
    ----------
    player_name: name of the player (str).
    game_data:   state of the game (dic).

    Return
    ------
    ai_input: game input from AI (str).

    Version
    -------
    Specification:  Nicolas Van Bossuyt (v1. 10/03/17)
                    Bayron Mahy (v2. 17/03/17)
    Implementation: Nicolas Van Bossuyt (v1. 10/03/17)
                    Alisson Leist (v2. 21/04/17)
    """
    ship_type_name = {'f': 'fighter', 'b': 'battlecruiser', 'd': 'destroyer'}

    ships_names = ['ARC-170', 'V-19', 'V-WINGS', 'X-WINGS', 'TIE-FIGHTER', 'DROID-starfighter', 'Dart', 'Eos', 'Furies', 
                   'Hoosier', 'Huey_Long', 'Hurricane', 'Hyperion', 'Iron_Fist', 'Iron_Justice', 'Jackson_V', 'Ha\'tak',
                   'Heracles', 'Heraclion', 'Hermes', 'Hydra', 'Juno', 'Medusa', 'Nemesis', 'Nimrod', 'Olympic', 'Fury',
                   'Apollo', 'Cadmus', 'Cerberus', 'Charon', 'Churchill', 'Damocles', 'Delphi', 'Excalibur', 'Herakles',
                   'Norad_II', 'Puddle_Jumper', 'Saragossa', 'Adventurer', 'The_Watcher', 'Alexander', 'ISS_Adventurer',
                   'BS_Galactica', 'SC_Juggernaut', 'Victory', 'BC_Pilgrim', 'Achilles', 'Agamemnon', 'Emperor\'s_Fury',
                   'Jackson\'s_Revenge', 'ISS_Europa', 'Orion', 'Persephone', 'Pollux', 'Pournelle', 'Roanoke', 'Talos',
                   'Theseus', 'Vesta', 'Zeus', 'Agrippa', 'Aeneas', 'Aleksander', 'Amphitrite', 'Antigone', 'Leviathan',
                   'Bucephalus', 'Circe', 'Bismarck', 'Gray_Tiger', 'Helios', 'Hephaestus', 'Titan',  'Cyrus', 'Geisha',
                   'Palatine', 'Patroclus', 'Thunder_Child', 'Theodore_G._Bilbo', 'Kimeran_Juggernaut', 'Scion', 'Loki', 
                   'Valor_of_Vardona','Napoleon', 'Ragnorak', 'Metis', 'Merrimack', 'Norad_III', 'Phobos', 'Tahoe', 'B',
                   'Kimera', 'Meleager']

    random.shuffle(ships_names)

    ships_patern = []
    abandonned_ships_count = len(get_ship_by_owner(game_data['ships'], 'none'))

    if abandonned_ships_count == 0:
        ships_patern = ['b', 'b', 'd', 'd']
    else:

        if abandonned_ships_count >= 50:
            ships_patern = ['f', 'f', 'f', 'f', 'f', 'f', 'f', 'f', 'f', 'f']

        elif abandonned_ships_count >= 10:
            ships_patern = ['b', 'd', 'f', 'f', 'f', 'f', 'f']

        else:
            ships_patern = ['b', 'b', 'd', 'f', 'f', 'f']

    ai_input = ''

    while len(ships_patern) > 0:
        ship_type = ship_type_name[ships_patern.pop()]
        ship_name = ships_names.pop()
        ai_input += '%s:%s ' % (ship_name, ship_type)

    return ai_input[:-1]


# +------------------------------------------------------------------------------------------------------------------+ #
# | Artificial Intelligence                                                                                          | #
# +------------------------------------------------------------------------------------------------------------------+ #

def get_fighter_action(game_data, ship_name, owner):
    """
    Get action for a fighter.
    
    Parameters
    ----------
    game_data: data of the game (dic).
    ship_name: name of the ship to get input from (str).
    
    Return
    ------
    action: action for this ship(str).
    
    Version
    -------
    Specification:  Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 31/03/17)
    Implementation: Bayron Mahy, Nicolas Van Bossuyt (v1. 28/04/17)
    """
    # Get data of the ship.
    ship = game_data['ships'][ship_name]

    # If the ship as no objective or no path to it, find a new one.
    if ship['objective'] == 'none' or len(ship['objective_path']) == 0 or not ship['objective'] in game_data['ships']:

        # Get abandoned ships.
        abandoned_ships = get_ship_by_owner(game_data['ships'], 'none')
        if len(abandoned_ships) > 0:

            random.shuffle(abandoned_ships)
            success = False

            while len(abandoned_ships) > 0 and not success:

                # Get the objective.
                ship['objective'] = abandoned_ships.pop()
                objective_ship = game_data['ships'][ship['objective']]

                # Get the nodes for the pathfinding
                start_node = node(ship['location'], ship['facing'], 0, ship['speed'])
                end_node = node(objective_ship['location'], objective_ship['facing'])

                # Get the shortest path to the objective.
                success, path = path_finding(start_node, game_data['model_ship'][ship['type']]['max_speed'], end_node,
                                             game_data['board_size'], [], 8)

                if success:
                    ship['objective_path'] = path
        else:
            # If there are no abandoned ships, do random action.
            return do_random_action(game_data, ship_name)

    # The spaceship follow the path only whent it have a objective.
    action = follow_path(game_data, ship_name)

    # If the ships as nothing to do in order to follow the path => attack !
    if action == 'none':
        return attack(game_data, ship_name)
    else:
        return action



def get_battleship_action(game_data, ship_name, owner):
    """
    Get action for a battlecruiser.
    Parameters
    ----------
    game_data: data of the game (dic).
    ship_name: name of the ship to get input from (str).
    owner: name of the owner of the ship (str).

    Return
    ------
    action: action for this ship(str).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 31/03/17).
    Implementation : Alisson Leist (v1. 28/04/17).
    """

    ship = game_data['ships'][ship_name]

    # Get the objective of the ship.
    if not ship['objective'] in game_data['ships']:
        # Get the close
        close_objectives = get_nearby_ship(game_data, ship_name, game_data['model_ship'][game_data['ships'][ship_name]['type']]['range'])
        final_objective = []
        for ship_object in close_objectives:
            ship_owner = game_data['ships'][ship_object]['owner']
            if not ship_owner in ['none', owner]:
                final_objective.append(ship_object)

        if len(final_objective) > 0:
            ship['objective'] = final_objective[0]
        else:
            # Get a random objective.
            objectives = filter_ships(game_data['ships'], owner)
            random.shuffle(objectives)
            ship['objective'] = objectives[0]

    # Get ship object from objective name.
    objective = game_data['ships'][ship['objective']]

    if get_distance(ship['location'], objective['location'], game_data['board_size']) <= \
            game_data['model_ship'][ship['type']]['range']:
        return attack(game_data, ship_name)
    else:
        action = get_closer(game_data, ship_name, objective['location'])

        if action == 'none':
            action = attack(game_data, ship_name)

        return action


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
    ship_location = game_data['ships'][target_ship]['location']
    x, y = 0, 0
    dx = 0
    dy = -1
    nearby_ships = []

    for i in range((search_range) ** 2):
        if (-search_range < x <= search_range) and (-search_range < y <= search_range) and abs(x) + abs(y) <= search_range:

            location = convert_coordinates((ship_location[0] + x, ship_location[1] + y), game_data['board_size'])

            if len(game_data['board'][location]) > 0:
                nearby_ships.extend(game_data['board'][location])

        if x == y or (x < 0 and x == -y) or (x > 0 and x == 1 - y):
            dx, dy = -dy, dx

        x, y = x + dx, y + dy

    return nearby_ships


# +------------------------------------------------------------------------------------------------------------------+ #
# | Actions                                                                                                          | #
# +------------------------------------------------------------------------------------------------------------------+ #

def follow_path(game_data, ship_name):
    """
    Make a ship follow a path, found by the path finding.

    Parameters
    ----------
    game_data: data of the game (dic).
    ship_name: name of the space ship (str).

    Return
    ------
    order: the order to do in order to follow the path <none|left|right|faster|slower>(str).
    
    Version
    -------
    Specification:  Nicolas Van Bossuyt (v1. 28/04/17)
    Implementation: Nicolas Van Bossuyt (v1. 28/04/17)
    """
    ship = game_data['ships'][ship_name]
    if len(ship['objective_path']) > 0:
        to_do_node = ship['objective_path'].pop(0)

        return to_do_node['to_do']

    return 'none'


def get_closer(game_data, ship_name, objective):
    """
    Move a ship at given coordinates.

    Parameters
    ----------
    game_data: data of the game (dic).
    ship_name: name of the ship to move (str).
    objective: destination of the ship (tuple(int, int)).

    Return
    ------
    input: input to execute <left, right, faster, slower>(str).


    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 31/03/17).
    Implementation: Bayron Mahy (v1. 16/04/17).
    """

    ship = game_data['ships'][ship_name]
    nodes = get_next_step(node(ship['location'], ship['facing'], 0, ship['speed']), node(objective),
                          game_data['model_ship'][ship['type']]['max_speed'], game_data['board_size'])

    dict_sort(nodes, 'distance')
    return nodes[0]['to_do']


def do_random_action(game_data, ship_name):
    """
    The space ship do a random action.

    Parameters
    ----------
    game_data: data of the game (dic).
    ship_name: name of the ship (str).

    Return
    ------
    action: randomly chosen action (str).
    
    Version
    -------
    Specification:  Nicolas Van Bossuyt (v1. 28/04/17)
    Implementation: Nicolas Van Bossuyt (v1. 28/04/17)
    """
    actions = ['faster', 'slower', 'left', 'right', 'attack']

    action = random.choice(actions)
    if action == 'faster' or action == 'slower':
        return speed(game_data, ship_name, action)
    if action == 'attack':
        return attack(game_data, ship_name)

    return action

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
    Attack command of AICIS.

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
    ship_pos = game_data['ships'][ship]['location']
    ship_range = game_data['model_ship'][game_data['ships'][ship]['type']]['range']
    ship_owner = game_data['ships'][ship]['owner']
    nearby_ships = get_nearby_ship(game_data, ship, ship_range)

    if len(nearby_ships) > 0:
        ships_targeted = []

        for perhaps_target in nearby_ships:
            if game_data['ships'][perhaps_target]['owner'] != ship_owner and\
               game_data['ships'][perhaps_target]['owner'] != 'none' and\
               get_distance(ship_pos, predict_next_location(game_data, perhaps_target), game_data['board_size']) <= ship_range:
                ships_targeted.append(perhaps_target)

        if len(ships_targeted) > 0:

            targets_life = []

            for target in ships_targeted:
                targets_life.append(game_data['ships'][target]['heal_points'])

            final_target = ships_targeted[targets_life.index(min(targets_life))]
            target_location = predict_next_location(game_data, final_target)
            return '%d-%d' % (target_location[1] + 1, target_location[0] + 1)

    return ''


# +------------------------------------------------------------------------------------------------------------------+ #
# | Path finding                                                                                                     | #
# +------------------------------------------------------------------------------------------------------------------+ #

def path_finding(start_node, max_speed, end_node, board_size, path=[], max_distance=8):
    """
    Find the shortest path to a objective.

    Parameters
    ----------
    start_node: the starting point of the path (dic).
    max_speed: maximum speed of the ship (int).
    end_node: the objective of the path finding (dic).
    board_size: size of the game_board (tuple(int, int)).
    (optional) path: path find by the pathfinding (list(node))
    (optional) max_distance: maximum distance of the path finding (int).

    Return
    ------
    shortess_path: the shortest path to the end node (list(steps)).
    
    Version
    -------
    Specification:  Nicolas Van Bossuyt (v1. 28/04/17)
    Implementation: Nicolas Van Bossuyt (v1. 28/04/17)
    """
    steps = get_next_step(start_node, end_node, max_speed, board_size)

    dict_sort(steps, 'distance')

    max_distance -= 1

    if max_distance == 0:
        return False, None

    for step in steps:
        new_path = list(path)
        new_path.append(step)

        if step['location'] == end_node['location']:
            # show_path(new_path, end_node, board_size)
            return True, new_path
        else:
            objective_find, path_to_objective = path_finding(step, max_speed, end_node,
                                                             board_size, new_path, max_distance)

            if objective_find:
                return True, path_to_objective

    return False, path


def get_next_step(start_node, end_node, max_speed, board_size):
    """
    Get the next step of a path finding path.

    Parameters
    ----------
    start_node: the starting point of the path (dic).
    end_node: the objective of the path finding (dic).
    max_speed: maximum speed of the ship (int).
    board_size: size of the game_board (tuple(int, int)).

    Return
    ------
    nex_step: the next step of the path (dic).
    
    Version
    -------
    Specification:  Nicolas Van Bossuyt (v1. 28/04/17)
    Implementation: Nicolas Van Bossuyt (v1. 28/04/17)
    """
    nodes = []

    speed = start_node['speed']

    if speed > 0:
        # Rotate left.
        v = to_unit_vector(rotate_vector_2d(start_node['facing'], -45))
        next_step_location = next_location(start_node['location'], v, speed, board_size)
        nodes.append(node(next_step_location, v, get_distance(next_step_location, end_node['location'], board_size), speed, 'left'))

        # Rotate right.
        v = to_unit_vector(rotate_vector_2d(start_node['facing'], 45))
        next_step_location = next_location(start_node['location'], v, speed, board_size)
        nodes.append(node(next_step_location, v, get_distance(next_step_location, end_node['location'], board_size), speed, 'right'))

    if speed < max_speed:
        next_step_location = next_location(start_node['location'], start_node['facing'], speed + 1, board_size)
        nodes.append(node(next_step_location, start_node['facing'], get_distance(next_step_location, end_node['location'], board_size), speed + 1, 'faster'))

    if speed > 0:
        next_step_location = next_location(start_node['location'], start_node['facing'], speed - 1, board_size)
        nodes.append(node(next_step_location, start_node['facing'], get_distance(next_step_location, end_node['location'], board_size), speed - 1, 'slower'))

        # Do nothing.
        next_step_location = next_location(start_node['location'], start_node['facing'], speed, board_size)
        nodes.append(node(next_step_location, start_node['facing'], get_distance(next_step_location, end_node['location'], board_size), speed, 'none'))

    return nodes


def node(location, facing=(0, 0), distance=0, speed=0, to_do='none'):
    """
    Create a new path finding node.

    Parameters
    ----------
    location: location of the node (tuple(int, int)).
    facing: facing of the node (tuple(int, int)).
    distance: distance to the objective (int).
    speed: speed of the node.
    to_do: Order to do.
    
    Return
    ------
    node: path finding node (dic).
    
    Version
    -------
    Specification:  Nicolas Van Bossuyt (v1. 28/04/17)
    Implementation: Nicolas Van Bossuyt (v1. 28/04/17)
    """
    return {'location': location, 'facing': facing, 'distance': distance, 'speed': speed, 'to_do': to_do}


def show_path(path, end_node, board_size):
    """
    (DEBUG) Show a path found by the pathfinding.

    Parameters
    ----------
    path: path find by the pathfinding (list(node))
    end_node: the objective of the path finding (dic).
    board_size: size of the game_board.
    """

    # Setup the drawing canvas.
    c = create_canvas((board_size[0] * 3) + 2, board_size[1] + 2)
    c = put_box(c, 0, 0, c['size'][0], c['size'][1])
    c = put_text(c, 2, 0, '| Path Finding... |')

    # Put path steps.
    for n in path:
        c = put(c, (n['location'][0] * 3 + 1) + 1, n['location'][1] + 1, ' ', 'white', 'green')

    # Put end point
    c = put(c, (end_node['location'][0] * 3 + 1) + 1, end_node['location'][1] + 1, ' ', 'white', 'white')

    print_canvas(c)


# +------------------------------------------------------------------------------------------------------------------+ #
# | Users Interfaces                                                                                                 | #
# +------------------------------------------------------------------------------------------------------------------+ #

def show_splash_game(game_data, is_remote_game=False):
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

    def clear_canvas(canvas, padding=0):
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

        canvas = put_box(canvas, padding, 0, screen_size[0] - padding, screen_size[1])
        canvas = put_stars_field(canvas, 1 + padding, 1, screen_size[0] - 2 - padding, screen_size[1] - 2, 0)

        return canvas

    # Setup main canvas.
    rows, columns = get_terminal_size()
    screen_size = (int(rows), int(columns))
    c = create_canvas(screen_size[0], screen_size[1])

    # print the alien.
    c = clear_canvas(c)
    c = put_ascii_art(c, screen_size[0] / 2 - 17, screen_size[1] / 2 - 12, 'alien', 'green')
    print_canvas(c)
    sleep(1)

    c = create_canvas(screen_size[0], screen_size[1])
    c = clear_canvas(c)

    game_title = 'Coders In Space'
    game_copyright = '(c) 2017 - 3342 Groupe24 corp.'
    font_standard = load_ascii_font('font_standard.txt')
    text_width = mesure_ascii_text(font_standard, game_title)
    text_location = ((screen_size[0]) / 2 - text_width / 2, screen_size[1] / 2 - 5)

    c = put_ascii_text(c, font_standard, game_title, text_location[0], text_location[1], 'yellow')
    c = put_text(c, text_location[0], text_location[1] + 7, '-' * text_width)
    c = put_text(c, text_location[0] + text_width - len(game_copyright), text_location[1] + 9, game_copyright, color='yellow')
    print_canvas(c)

    game_screen = render_game_screen(game_data)

    slide_animation(c, game_screen)


def show_game_screen(game_data):
    """
    Show game board on the teminal.

    Parameter
    ---------
    game_data: data of the game (dic).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17).
                   Nicolas Van Bossuyt (v2. 19/03/17).

    Implementation: Nicolas Van Bossuyt (v4. 10/02/17).
    """
    c = render_game_screen(game_data)
    print_canvas(c)


def render_game_screen(game_data):
    """
    Render the game screen.
    
    Parameter
    ---------
    game_data: data of the game (dic).
    
    Return
    ------
    game_screen: rendered game_screen (canvas).
    """
    # Setup main canvas.
    screen_size = get_terminal_size()
    c = create_canvas(*screen_size)

    # Render child canvas.
    c_game_board = render_game_board(game_data)  # The game board.
    c_ship_list = render_ship_list(game_data, 34, screen_size[1] - 2)  # The list
    c_game_logs = render_game_logs(game_data, c_game_board['size'][0], 10)

    # Put some nice decoration.
    c = put_ascii_art(c, 1, screen_size[1] - 25, 'planet')
    if screen_size > 190:
        c = put_ascii_art(c, 185, screen_size[1] - 25, 'planet')

    c = put_box(c, 0, 0, screen_size[0], screen_size[1], 'single')

    # Put child canvas in the main canvas.
    game_board_pos = (((screen_size[0] - c_ship_list['size'][0]) / 2 - (c_game_board['size'][0] + 2) / 2) + c_ship_list['size'][0],
                      screen_size[1] / 2 - (c_game_board['size'][1] + 2) / 2 - (c_game_logs['size'][1] + 2) / 2)

    c = put_window(c, c_game_board, 'GAME BOARD', game_board_pos[0], game_board_pos[1], c_game_board['size'][0] + 2,
                   c_game_board['size'][1] + 2)
    c = put_window(c, c_game_logs, 'GAME LOGS', game_board_pos[0], game_board_pos[1] + c_game_board['size'][1] + 2,
                   c_game_logs['size'][0] + 2, c_game_logs['size'][1] + 2)

    if game_board_pos[0] - (c_ship_list['size'][0] + 2) > 0:
        c = put_window(c, c_ship_list, 'SHIP LIST', 0, 0, c_ship_list['size'][0] + 2, c_ship_list['size'][1] + 2)

    return c


def render_game_board(game_data):
    """
    Render the game board.

    Parameter
    ---------
    game_data: data of the game (dic).

    Return
    ------
    game_board_canvas: rendered game board (dic)
    
    Version
    -------
    Specification:  Nicolas Van Bossuyt (v1. 10/04/17)
    Implementation: Nicolas Van Bossuyt (v1. 10/04/17)
    """
    # Setup the drawing canvas.
    board_size = game_data['board_size']
    c = create_canvas(board_size[0] * 3 + 3, board_size[1] + 1)
    # c = put_stars_field(c, 0, 0, *c['size'])
    offset = 0

    # Put coordinates.
    dark = False
    for i in range(max(board_size)):
        val_str = str(i + 1)
        val_str = ' ' * (3 - len(val_str)) + val_str

        if dark:
            # Horizontal
            c = put_text(c, 3 + offset * 3, 0, val_str, 1, 0, 'white', 'grey')

            # Vertical
            c = put_text(c, 0, 1 + offset, val_str, 1, 0, 'white', 'grey')
        else:
            # Horizontal
            c = put_text(c, 3 + offset * 3, 0, val_str, 1, 0, 'grey', 'white')

            # Vertical
            c = put_text(c, 0, 1 + offset, val_str, 1, 0, 'grey', 'white')

        dark = not dark
        offset += 1

    # Put Spaceships on the game board.
    for location in game_data['board']:
        # Get ships on given location and the location on the screen.
        ships_at_location = game_data['board'][location]
        on_canvas_location = (3 + location[0] * 3, location[1] + 1)

        # There are only on ship on the location.
        if len(ships_at_location) == 1:

            # Get all ships informations.
            ship_name = ships_at_location[0]
            ship = game_data['ships'][ship_name]
            ship_owner = ship['owner']
            ship_icon = ship_name.replace('%s_' % ship_owner, '').upper()[0]
            ship_color = 'white'
            ship_facing = ship['facing']

            # Set the color to white if the ship dosen't have any owner.
            if ship_owner != 'none':
                ship_color = game_data['players'][ship_owner]['color']

            # Put facing line.
            facing_char = '|'  # The ship is facing 'up' or 'down'.

            if ship_facing == (1, 1) or ship_facing == (-1, -1):
                facing_char = '\\'  # The ship is facing 'up-left' or 'down-right'.
            elif ship_facing == (1, -1) or ship_facing == (-1, 1):
                facing_char = '/'  # The ship is facing 'up-right' or 'down-left'.
            elif ship_facing == (1, 0) or ship_facing == (-1, 0):
                facing_char = u'─'  # The ship is facing 'left' or 'right'.

            # Put the ship and the facing line on the game board.
            put_text(c, on_canvas_location[0] + 1, on_canvas_location[1], ship_icon, 1, 0, ship_color, None)
            if ship_owner != 'none':
                put_text(c, on_canvas_location[0] + 1 + ship_facing[0], on_canvas_location[1] + ship_facing[1],
                     facing_char, 1, 0, ship_color, None)

        # There are more than one ship on the location, show how many there are.
        elif len(ships_at_location) > 1:
            put_text(c, on_canvas_location[0], on_canvas_location[1], '[%d]' % len(ships_at_location), 1, 0, 'green',
                     None)

    # Show attack location on the game board.
    for location in game_data['pending_attacks']:
        location = location[2]
        on_canvas_location = (3 + location[0] * 3, location[1] + 1)
        put_text(c, on_canvas_location[0], on_canvas_location[1], '[', 1, 0, 'red')
        put_text(c, on_canvas_location[0] + 2, on_canvas_location[1], ']', 1, 0, 'red')

    return c


def render_ship_list(game_data, width, height):
    """
    Render the ship_list.

    Parameter
    ---------
    game_data: data of the game (dic).

    Return
    ------
    ship_list_canvas: rendered ship list (dic).
    
    Version
    -------
    Specification:  Nicolas Van Bossuyt (v1. 10/04/17)
    Implementation: Nicolas Van Bossuyt (v1. 10/04/17)
    """
    # Setup the drawing canvas.
    c = create_canvas(width, height)
    ship_index = 0

    # Put list header.
    put_text(c, 0, 0, ' T | h | X   Y | Name' + ' ' * 25, 1, 0, 'grey', 'white')
    for player in game_data['players']:
        ship_index += 1
        y = ship_index + 1

        # Put all information about the players.
        put_text(c, 1, y, '%s (t:%s s:%d)' % (
            player, game_data['players'][player]['type'], game_data['players'][player]['nb_ships']))
        put_text(c, 0, y + 1, '-' * width)
        ship_index += 2

        # get all space ship of a player.
        for ship in get_ship_by_owner(game_data['ships'], player):
            y = ship_index + 1

            # Put information about the selected spaceship.

            # Ship type.
            put_text(c, 1, y, game_data['ships'][ship]['type'].upper()[0])

            # ships heal
            put_text(c, 5, y, str(game_data['ships'][ship]['heal_points']))

            # Ship coordinates
            ship_location = list(game_data['ships'][ship]['location'])
            ship_location = (ship_location[1] + 1, ship_location[0] + 1)
            put_text(c, 8, y, str(ship_location))

            # Ship name.
            put_text(c, 17, y, ship[len(player + '_'):], 1, 0,
                     game_data['players'][game_data['ships'][ship]['owner']]['color'])

            ship_index += 1

    return c


def render_game_logs(game_data, width, height):
    """
    Render the game logs.

    Parameter
    ---------
    game_data: data of the game (dic).

    Return
    ------
    game_logs_canvas: rendered game logs (dic).
    
    Version
    -------
    Specification:  Nicolas Van Bossuyt (v1. 10/04/17)
    Implementation: Nicolas Van Bossuyt (v1. 10/04/17)
    """
    # Setup the canvas.
    c = create_canvas(width, height)
    y = 0

    message_color = ['blue', 'yellow', 'red', None, 'red']
    message_prefix = ['  I ', ' /!\\', ' !!!', '  > ', ' X.X']

    # Put all message in the logs screen.
    for message in game_data['game_logs'][-height:]:
        c = put_text(c, 5, y, message[1], 1, 0)
        c = put_text(c, 0, y, message_prefix[message[0]], 1, 0, message_color[message[0]])
        y += 1

    return c


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

    # Setup main canvas.
    rows, columns = get_terminal_size()
    screen_size = (int(rows), int(columns))

    # Load ascii fonts.
    font_small = load_ascii_font('font_small.txt')
    font_standard = load_ascii_font('font_standard.txt')

    # Create the ascii canvas.
    c = create_canvas(screen_size[0], screen_size[1])
    c = put_box(c, 0, 0, screen_size[0], screen_size[1])
    c = put_stars_field(c, 1, 1, screen_size[0] - 2, screen_size[1] - 2)

    line_index = 0

    # Put players stats.
    for player in game_data['players']:
        if player != 'none':
            if player in game_data['winners']:
                # The player win the game.
                text_length = mesure_ascii_text(font_standard, player)
                text_font = font_standard
                text_color = game_data['players'][player]['color']

            else:
                # The player lost the game.
                text_length = mesure_ascii_text(font_small, player)
                text_font = font_small
                text_color = 'white'

            text_location = (screen_size[0] / 2 - int(text_length / 2), line_index * 11 + 2)

            # Put player information.
            c = put_ascii_text(c, text_font, player, text_location[0], text_location[1], text_color)
            c = put_text(c, text_location[0], text_location[1] + 6, '_' * text_length)
            c = put_text(c, text_location[0], text_location[1] + 8, "%d spaceships" % (game_data['players'][player]['nb_ships']))
            c = put_text(c, text_location[0], text_location[1] + 9, "%d G$" % (calculate_value(player, game_data)))

            line_index += 1

    # Print the canvas in the terminal.
    print_canvas(c)


# +------------------------------------------------------------------------------------------------------------------+ #
# | Game commands                                                                                                    | #
# +------------------------------------------------------------------------------------------------------------------+ #

def parse_command(commands, player_name, game_data):
    """
    Parse a player's command and execute it

    Parameters
    ----------
    commands: commands from a player (str).
    game_data: game's data (dic).

    Return
    ------
    game_data: new data of the game (dic).

    Version
    -------
    Specification:  Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (V1. 10/02/17)
    """
    commands = commands.split(' ')

    for ship_command in commands:
        sub_command = ship_command.split(':')

        for ship in sub_command[0].split(','):
            if len(sub_command) == 2:
                ship_name = '%s_%s' % (player_name, ship)
                ship_command = sub_command[1]

                # Check if the space ship exists in the game.
                if ship_name in game_data['ships']:

                    # Rotate command.
                    if ship_command == 'left' or ship_command == 'right':
                        game_data = command_rotate(ship_name, ship_command, game_data)

                    # Speed command
                    elif ship_command == 'faster' or ship_command == 'slower':
                        game_data = command_change_speed(ship_name, ship_command, game_data)

                    # In other case speed command.
                    else:
                        attack_location = ship_command.split('-')
                        if len(attack_location) == 2:
                            attack_location = (int(attack_location[1]) - 1, int(attack_location[0]) - 1)
                            game_data['pending_attacks'].append((ship_name, game_data['ships'][ship_name]['location'], attack_location))

    return game_data


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
    Specification:  Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 14/02/17)
                    Nicolas Van Bossuyt (v2. 23/02/17)
    """
    for ship in ships.split(' '):
        ship = ship.split(':')

        if len(ship) == 2:
            # Allow human player to dont have to write the full ship type name.
            ships_type_convert = {'f': 'fighter', 'd': 'destroyer', 'b': 'battlecruiser'}
            ship[1] = ships_type_convert[ship[1][0]]

            # Get the price of the space ship.
            ship_price = game_data['model_ship'][ship[1]]['price']

            if ship_price <= game_data['players'][player]['money']:
                game_data['players'][player]['money'] -= ship_price
                ship_name = '%s_%s' % (player, ship[0])

                if not ship_name in game_data['ships']:
                    create_ship(player, ship_name, ship[1], game_data)
                else:
                    write_log(game_data, "%s is already created." % ship_name, log_error)

    return game_data


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
    Specification:  Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Bayron Mahy (v1. 10/02/17)
    """

    type = game_data['ships'][ship]['type']

    # Make the ship move faster.
    if change == 'faster' and game_data['ships'][ship]['speed'] < game_data['model_ship'][type]['max_speed']:
        game_data['ships'][ship]['speed'] += 1

    # Make the ship move slower.
    elif change == 'slower' and game_data['ships'][ship]['speed'] > 0:
        game_data['ships'][ship]['speed'] -= 1

    # Show a message when is a invalid change.
    else:
        write_log(game_data, 'you cannot make that change on the speed of "' + ship + '"', log_error)

    return game_data


def command_rotate(ship, facing, game_data):
    """
    Rotate the ship.

    Parameters
    ----------
    ship: name of the ship to Increase the speed (str).
    facing: the facing to rotate the ship <"left"|"right">(str)
    game_data: data of the game (dic).

    Returns
    -------
    game_data: new data of the game (dic).

    Version
    -------
    Specification:  Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 10/02/17)
                    Nicolas Van Bossuyt (v2. 22/02/17)
    """
    v = (0, 0)
    if facing == 'left':
        v = rotate_vector_2d(game_data['ships'][ship]['facing'], -45)
    elif facing == 'right':
        v = rotate_vector_2d(game_data['ships'][ship]['facing'], 45)

    game_data['ships'][ship]['facing'] = to_unit_vector(v)
    return game_data


def command_attack(ship, ship_coordinate, target_coordinate, game_data):
    """
    Determine if the attack works and do it.

    Parameters
    ----------
    ship: focus ships (str).
    ship_location: coodinates of the first ship (tuple(int, int)).
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

    if distance <= ship_type['range']:
        if len(game_data['board'][target_coordinate]) != 0:
            game_data['nb_rounds'] = 0

            # Give damages to all ships on targeted coordinate.
            ships_to_remove = []

            for target_ship in game_data['board'][target_coordinate]:
                if  game_data['ships'][target_ship]['owner'] != 'none':
                    # Give damages to the tageted ship.
                    game_data['ships'][target_ship]['heal_points'] -= damages

                    if game_data['ships'][target_ship]['heal_points'] <= 0:
                        # The ship is death -> add to the ships to remove from
                        ships_to_remove.append(target_ship)
                    else:
                        write_log(game_data, '%s shot %s' % (ship, target_ship), log_warning)

            # Remove ships from the game.
            for death_ship in ships_to_remove:
                game_data['board'][target_coordinate].remove(death_ship)
                game_data['players'][game_data['ships'][death_ship]['owner']]['nb_ships'] -= 1
                del game_data['ships'][death_ship]
                
                write_log(game_data, '%s kill %s' % (ship, death_ship), log_death)
                
        else:
            write_log(game_data, '%s shoot failed %s!' % (ship, str(target_coordinate)), log_warning)
    else:
        write_log(game_data, '%s shoot out of range !' % ship, log_error)

    return game_data


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
                    Nicolas Van Bossuyt (v3. 03/05/17)
    """

    def distance(a, b, size):
        # size -= 1
    
        if a > b:
            a, b = b, a

        if abs(a - b) > size / 2:
            a += size

        return abs(a - b)

    return distance(coord1[0], coord2[0], size[0]) + distance(coord1[1], coord2[1], size[1])


def convert_coordinates(coordinates, board_size):
    """
    Apply tore space to coordinates.

    Parameters
    ----------
    coordinates: coordinates to convert (tuple(int, int))
    board_size: Size of the tore tupe(int, int).

    Return
    ------
    converted_coord: coord with the tore applied.

    Version
    -------
    Specification: Nicolas Van Bossuyt (v1. 09/03/17)
    Specification: Nicolas Van Bossuyt (v1. 09/03/17)
    Implementation: Nicolas Van Bossuyt (v1. 09/03/17)
    """

    def convert(a, size):

        if a >= size:
            a -= size
        elif a < 0:
            a += size

        return a

    return convert(coordinates[0], board_size[0]), convert(coordinates[1], board_size[1])


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
    Specification:  Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
    Implementation: Nicolas Van Bossuyt (v1. 15/02/17)
    """

    # Creating the new space ship and add to the game_data.
    game_data['ships'][ship_name] = {
        'type': ship_type, 'heal_points': game_data['model_ship'][ship_type]['max_heal'],
        'facing': game_data['players'][player_name]['ships_starting_facing'],
        'speed': 0, 'owner': player_name,
        'location': game_data['players'][player_name]['ships_starting_point'],

        # Just for the ai.
        'objective': 'none',
        'objective_path': []
    }

    game_data['board'][game_data['players'][player_name]['ships_starting_point']].append(ship_name)
    game_data['players'][player_name]['nb_ships'] += 1

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
    Specification:  Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 10/02/17)
                    Nicolas Van Bossuyt (v2. 22/02/17)
    """

    theta = radians(theta)
    dc, ds = cos(theta), sin(theta)
    x, y = vector[0], vector[1]
    x, y = dc * x - ds * y, ds * x + dc * y

    return x, y


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
    Specification:  Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 22/02/17)
    """

    def convert(value):

        if value > 0.25:
            return 1
        elif value < -0.25:
            return -1

        return 0

    return convert(vector[0]), convert(vector[1])


def predict_next_location(game_data, ship_name):
    """
    Predict the next location of a space ship.

    Parameters
    ----------
    game_data: data of the game (dic).
    ship_name: name of the spaceship to predicte the next location (str).
    facing: facing of the ship (tuple)

    Return
    ------
    predicted_location : predicte location of the spaceship (tuple(int, int)).
    
    Version
    -------
    Specification: Nicolas Van Bossuyt (v1. 19/03/17).
    Implementation: Nicolas Van Bossuyt (v1. 19/03/17).
                    Bayron Mahy (v2. 22/03/17).
    """

    ship_location = game_data['ships'][ship_name]['location']
    ship_facing = game_data['ships'][ship_name]['facing']
    ship_speed = game_data['ships'][ship_name]['speed']

    return next_location(ship_location, ship_facing, ship_speed, game_data['board_size'])


def next_location(ship_location, ships_facing, ship_speed, game_board_size):
    """
    Predict the next location of a space ship base on his speed and facing.

    Parameters
    ----------
    ship_location: location of the space ship (tuple(int, int))
    ships_facing: facing of the space ship (tuple(int, int))
    ship_speed: speed of the space ship (int).
    game_board_size: size of the game board (tuple(int, int))

    Return
    ------
    predicted_location : predicte location of the spaceship (tuple(int, int)).
    
    Version
    -------
    Specification:  Nicolas Van Bossuyt (v1. 10/04/17)
    Implementation: Nicolas Van Bossuyt (v1. 10/04/17)
    """
    return convert_coordinates((ship_location[0] + ships_facing[0] * ship_speed,
                                ship_location[1] + ships_facing[1] * ship_speed), game_board_size)


# +------------------------------------------------------------------------------------------------------------------+ #
# | Game board files                                                                                                 | #
# +------------------------------------------------------------------------------------------------------------------+ #

def create_random_game_board(file_name, board_size, lost_ships_count):
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
    ship_facing = ['up', 'up-left', 'up-right', 'left', 'right', 'down', 'down-left', 'down-right']

    buffer = ''  # Create the string buffer for the file.
    buffer += "%d %d\n" % (board_size[0], board_size[1])  # Add the first of the file whith the size of the game board.

    for i in range(lost_ships_count):
        buffer += '%d %d %s:%s %s\n' % (randint(1, board_size[0]),  # Y coodinate of the ship.
                                        randint(1, board_size[1]),  # X coodinate of the ship.
                                        'ship_' + str(i),           # Name of the ship.
                                        ship_type[randint(0, len(ship_type) - 1)],      # Type of the ship.
                                        ship_facing[randint(0, len(ship_facing) - 1)])  # Facing of the ship

    # Saving the game board to a file.
    f = open(file_name, 'w')
    f.write(buffer)
    f.close()


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
    size = (int(size_str[1]), int(size_str[0]))

    # Get lost space ship in the file..
    ships_list = []
    for line_index in range(len(file_content) - 1):
        ship_str = file_content[line_index + 1].split(' ')

        if len(ship_str) == 4:
            ship_name_and_type = ship_str[2].split(':')

            ship = (int(ship_str[1]) - 1,  # Y location of the ship.
                    int(ship_str[0]) - 1,  # X location of the ship.
                    ship_name_and_type[0],  # Name of the ship.
                    ship_name_and_type[1],  # Type of the ship.
                    facing_to_vector2d(ship_str[3]))  # Facing of the ship.

            ships_list.append(ship)

    # Create parsed data dictionary and return it.
    parsed_data = {'size': size, 'ships': ships_list}

    return parsed_data


def facing_to_vector2d(facing):
    """
    Convert a string facing to a vector2d.

    Parameter
    ---------
    facing: facing to convert <up|down|left|right|up-left|up-right|down-left|down-right>(str).

    Return
    ------
    vector: vector2d from facing (tuple(int, int)).

    Version
    -------
    Specification: Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
    Implementation: Nicolas Van Bossuyt (v1. 11/02/17)
    """

    convert = {'up': (0, -1), 'up-right': (1, -1), 'right': (1, 0), 'down-right': (1, 1), 'down': (0, 1),
               'down-left': (-1, 1), 'left': (-1, 0), 'up-left': (-1, -1)}
    return convert[facing]


# +------------------------------------------------------------------------------------------------------------------+ #
# | Misc                                                                                                             | #
# +------------------------------------------------------------------------------------------------------------------+ #

def filter_ships(ships, exclude_owner):
    """
    Get a list of all space ships alive wihout these of a specifique owner.
     
    Parameters
    ----------
    ships: list of ships to filter (list(dic)).
    exclude_owner: owner to exclude from the list (str).
    
    Return
    ------
    ships: filtered ships (list(str)).
    
    Version
    -------
    Specification:  Nicolas Van Bossuyt (v1. 28/04/17)
    Implementation: Nicolas Van Bossuyt (v1. 28/04/17)
    """
    founded_ships = []
    for ship in ships:
        if ships[ship]['owner'] != exclude_owner:
            founded_ships.append(ship)

    return founded_ships


def get_ship_by_owner(ships, owner):
    """
    Get the list of all ships of a owner.
    
    Parameters
    ----------
    ships: list of ships to filter (list(dic)).
    exclude_owner: owner of the spaceships (str).
    
    Return
    ------
    ships: filtered ships (list(str)).
    
    Version
    -------
    Specification:  Nicolas Van Bossuyt (v1. 28/04/17)
    Implementation: Nicolas Van Bossuyt (v1. 28/04/17)
    """
    founded_ships = []
    for ship in ships:
        if ships[ship]['owner'] == owner:
            founded_ships.append(ship)

    return founded_ships


def vector2d_to_facing(vector):
    """
    Convert a string facing to a vector2d.

    Parameter
    ---------
    vector: vector2d to convert in facing (tuple(int, int)).

    Return
    ------
    facing: facing <up|down|left|right|up-left|up-right|down-left|down-right>(str).

    Version
    -------
    Specification: Nicolas Van Bossuyt (v1. 18/04/17)
    Implementation: Nicolas Van Bossuyt (v1. 18/04/17)
    """
    convert = {(0, 1): 'up', (-1, 1): 'up-left', (-1, 0): 'left', (-1, -1): 'down-left', (0, -1): 'down',
               (1, 0): 'right', (1, -1): 'down-right', (1, 1): 'up-right'}
    return convert[vector]


def write_log(game_data, message, type=0):
    """
    Write a message in the game logs.
    
    Parameters
    ----------
    game_data: data of the game (dic).
    message: message to print to game logs (str).
    (optional) type: type of the message <0 = info|1 = warning|2 = error>
    
    Return
    ------
    game_data: new data of the game (dic)
    
    Version
    -------
    Specification: Nicolas Van Bossuyt (v1. 18/04/2017)
    Implementation: Nicolas Van Bossuyt (v1. 18/04/2017)
    """
    prefix = ['INFO', 'WARN', 'ERRO', 'INPU', 'KILL']
    game_data['game_logs'].append((type, message))



    f = open('log.txt', 'r')
    txt = f.read()
    f.close()

    txt += '%s - %s\n' % (prefix[type], message)

    f = open('log.txt', 'w')
    f.write(txt)
    f.close()

    return game_data


def dict_sort(items, key):
    """
    Sort dictionary by a specific key.
    
    Parameters
    ----------
    items: dictionaries to sort (list(dic)).
    key: use for sorting dictionary (dic key).
    
    Returns
    -------
    sorted_dictionaries: (list(dic)).
    
    Version
    -------
    Specification:  Nicolas Van Bossuyt (v1. 28/04/17)
    Implementation: Nicolas Van Bossuyt (v1. 28/04/17)
    """
    for i in range(len(items)):
        for j in range(len(items) - 1 - i):
            if items[j][key] > items[j + 1][key]:
                items[j], items[j + 1] = items[j + 1], items[j]
    return items


# Use for quick debuging.

if __name__ == '__main__':
    play_game('board/random.cis', ('NicolasLeRebelDeL\'espace', 'A.I.C.I.S.'), ai_vs_ai)

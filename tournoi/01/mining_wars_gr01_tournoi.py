# -*- coding: utf-8 -*-
import os
import random
import remote_play as r










def IA_test(player_nbr_IA, game):
    """
    """

    name = ['AA1', 'Alabama', 'Alfred', 'Allegheny', 'Anderson', 'Arctic(AF7)', 'Arizona', 'Arkansas', 'Aroostock', 'Atlanta', 'Bagley', 'Baltimore', 'Boise', 'Bonhomme', 'Bonhomme', 'Bonhomme', 'Boston', 'Brooklyn', 'Brooks', 'California', 'Casco', 'Chicago', 'Chicago', 'Colorado', 'Columbus', 'Commodore', 'Concord', 'Connecticut', 'Constellation', 'Constellation', 'Constitution', 'Constitution', 'Constitution', 'Constitution', 'Cushing', 'Davis', 'Davis', 'Delaware', 'DeLong', 'Dent', 'Dolphin', 'Downes', 'Enterprise', 'Enterprise', 'Ericsson', 'Erie', 'Erie', 'Essex', 'Farragut', 'Florida', 'Flusser', 'Fulton', 'Gannet', 'Garfish', 'General', 'Georgia', 'Gleaves', 'Gloucester', 'Grayback', 'Hartford', 'Henderson', 'Henley', 'Holland', 'Holland', 'Hopkins', 'Hornet', 'Houston', 'Hudson', 'Idaho', 'Independence', 'Independence', 'Indiana', 'Indianapolis', 'Iowa', 'Jupiter', 'K5', 'Kearsarge', 'L6', 'Langley', 'Langley', 'Lehigh', 'Lexington', 'Lexington', 'Ludlow', 'M1', 'MacDonough', 'Mackenzie', 'Mackerel', 'Marblehead', 'Maryland', 'Massachusetts', 'Mayflower', 'Mayrant', 'Medusa', 'Melville', 'Mendota', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Monadnock', 'Monaghan', 'Monitor', 'Monocacy', 'Nebraska', 'Nevada', 'New', 'New', 'Newark', 'Nitro', 'Northampton', 'O3', 'Ohio', 'Oklahoma', 'Olympia', 'Onondaga', 'Oregon', 'Owl', 'Panay', 'Patoka', 'Paulding', 'PC26', 'PC405', 'PC451', 'PE33', 'Pennsylvania', 'Pennsylvania', 'Pennsylvania', 'Pensacola', 'Petrel', 'Philadelphia', 'Plunger', 'Porpoise', 'Porter', 'Portland', 'Powhatan', 'Princeton', 'PT8', 'R26', 'R3', 'Raleigh', 'Ranger', 'Relief', 'Rhode', 'S1(SS105)', 'S4', 'S48', 'Saint', 'Salamonie', 'Salem', 'Salmon', 'Salt', 'Saratoga', 'Sassacus', 'Savannah', 'Seal', 'Snapper', 'Somers', 'Stiletto', 'Stiletto', 'Swordfish', 'Tarantula', 'Texas', 'Thrasher', 'Tuna', 'United', 'V2', 'V4', 'V5', 'Vesuvius', 'Virginia', 'Wadsworth', 'Wampanoag', 'Washington', 'Wasp', 'Wasp', 'West', 'Wichita', 'Winslow', 'Wright', 'Yorktown', 'Yorktown', 'YT161']

    ## IA first implementation

    IA_order = ''

    if game['nbr_tour_played'] == 0:

        for i in range(3):
            ships_name = name[random.randint(0, len(name))-1]

            if ships_name not in game['player'][str(player_nbr_IA)]['excavators']:

                IA_order += ships_name + ':excavator-S '

    if game['nbr_tour_played'] > 0:

        for excavator in game['player'][str(player_nbr_IA)]['excavators']:

            IA_order += excavator + ':release '

            if game['player'][str(player_nbr_IA)]['excavators'][excavator][5] < game['player'][str(player_nbr_IA)]['excavators'][excavator][6]:
                position_asteroids = []
                asteroids_on_board = []
                for asteroid_nbr in range(len(game['asteroids'])):
                    position_asteroids = [int(game['asteroids'][str(asteroid_nbr)]['x']), int(game['asteroids'][str(asteroid_nbr)]['y'])]
                    asteroids_on_board += [[str(asteroid_nbr), position_asteroids]]

                asteroid_to_reach = ['null', 1000]
                pos_x_exc = game['player'][str(player_nbr_IA)]['excavators'][excavator][1]
                pos_y_exc = game['player'][str(player_nbr_IA)]['excavators'][excavator][2]

                for asteroid in asteroids_on_board:
                    pos_x_ast = asteroid[1][0]
                    pos_y_ast = asteroid[1][1]

                    if abs(int(pos_x_exc) - int(pos_x_ast)) >= abs(int(pos_y_exc) - int(pos_y_ast)):
                        dist = abs(int(pos_x_exc) - int(pos_x_ast))

                    elif abs(int(pos_y_exc) - int(pos_y_ast)) > abs(int(pos_x_exc) - int(pos_x_ast)):
                        dist = abs(int(pos_y_exc) - int(pos_y_ast))

                    if dist < asteroid_to_reach[1] and game['asteroids'][asteroid[0]]['nbr_ore'] > 0:

                        asteroid_to_reach[0] = asteroid[0]
                        asteroid_to_reach[1] = dist

                if int(pos_y_exc) == int(game['asteroids'][asteroid_to_reach[0]]['y']) and int(pos_x_exc) == int(game['asteroids'][asteroid_to_reach[0]]['x']):
                    IA_order += excavator + ':lock '

                else:
                    if int(pos_x_exc) < int(game['asteroids'][asteroid_to_reach[0]]['x']):
                        pos_x_ext_to_go = int(pos_x_exc) + 1

                    elif int(pos_x_exc) > int(game['asteroids'][asteroid_to_reach[0]]['x']):
                        pos_x_ext_to_go = int(pos_x_exc) - 1

                    elif int(pos_x_exc) == int(game['asteroids'][asteroid_to_reach[0]]['x']):
                        pos_x_ext_to_go = int(pos_x_exc)

                    if int(pos_y_exc) < int(game['asteroids'][asteroid_to_reach[0]]['y']):
                        pos_y_ext_to_go = int(pos_y_exc) + 1

                    elif int(pos_y_exc) > int(game['asteroids'][asteroid_to_reach[0]]['y']):
                        pos_y_ext_to_go = int(pos_y_exc) - 1

                    elif int(pos_y_exc) == int(game['asteroids'][asteroid_to_reach[0]]['y']):
                        pos_y_ext_to_go = int(pos_y_exc)

                    IA_order += excavator + ":@" + str(pos_x_ext_to_go) + "-" + str(pos_y_ext_to_go) + ' '

            elif game['player'][str(player_nbr_IA)]['excavators'][excavator][5] == game['player'][str(player_nbr_IA)]['excavators'][excavator][6]:

                portal_nbr = 'portal_' + str(player_nbr_IA)
                portal_x = int(game[portal_nbr]['x'])
                portal_y = int(game[portal_nbr]['y'])
                pos_x_exc = int(game['player'][str(player_nbr_IA)]['excavators'][excavator][1])
                pos_y_exc = int(game['player'][str(player_nbr_IA)]['excavators'][excavator][2])

                IA_order += excavator + ':release '

                if int(pos_y_exc) == int(portal_y) and int(pos_x_exc) == int(portal_x):
                    IA_order += excavator + ':lock '

                else:
                    if pos_x_exc < portal_x:
                        pos_x_ext_to_go = pos_x_exc + 1

                    elif pos_x_exc > portal_x:
                        pos_x_ext_to_go = pos_x_exc - 1

                    elif pos_x_exc == portal_x:
                        pos_x_ext_to_go = pos_x_exc

                    if pos_y_exc < portal_y:
                        pos_y_ext_to_go = pos_y_exc + 1

                    elif pos_y_exc > portal_y:
                        pos_y_ext_to_go = pos_y_exc + - 1

                    elif pos_y_exc == portal_y:
                        pos_y_ext_to_go = pos_y_exc

                    IA_order += excavator + ":@" + str(pos_x_ext_to_go) + "-" + str(pos_y_ext_to_go) + ' '
#_---------

        if game['player'][str(player_nbr_IA)]['ore'] > 3:

            ships_name = name[random.randint(0, len(name))-1]

            if ships_name not in game['player'][str(player_nbr_IA)]['ships']:

                IA_order += ships_name + ':scout '

        if len(game['player'][str(player_nbr_IA)]['ships']) > 0:

            if int(player_nbr_IA) == 1:
                portal = 'portal_2'

            elif int(player_nbr_IA) == 2:
                portal = 'portal_1'

            for ships in game['player'][str(player_nbr_IA)]['ships']:

                pos_x_ship = int(game['player'][str(player_nbr_IA)]['ships'][ships][1])
                pos_y_ship = int(game['player'][str(player_nbr_IA)]['ships'][ships][2])
                portal_y = int(game[portal]['y'])
                portal_x = int(game[portal]['x'])

                if int(pos_y_ship) == int(portal_y) and int(pos_x_ship) == int(portal_x):
                        x_to_shoot = pos_x_ship + 2
                        y_to_shoot = pos_y_ship + 1
                        IA_order += ships + ':*' + str(x_to_shoot) + '-' + str(y_to_shoot) + ' '

                else:

                    if pos_x_ship < portal_x:
                        pos_x_ship_to_go = pos_x_ship + 1

                    elif pos_x_ship > portal_x:
                        pos_x_ship_to_go = pos_x_ship - 1

                    elif pos_x_ship == portal_x:
                        pos_x_ship_to_go = pos_x_ship

                    if pos_y_ship < portal_y:
                        pos_y_ship_to_go = pos_y_ship + 1

                    elif pos_y_ship > portal_y:
                        pos_y_ship_to_go = pos_y_ship + - 1

                    elif pos_y_ship == portal_y:
                        pos_y_ship_to_go = pos_y_ship

                    print(pos_y_ship_to_go, pos_x_ship_to_go)

                    IA_order += ships + ":@" + str(pos_x_ship_to_go) + "-" + str(pos_y_ship_to_go) + ' '

    IA_order = IA_order.strip(' ')

    print(IA_order)

    game['command_IA'][str(player_nbr_IA)] = IA_order












def IA_test_2(player_nbr_IA, game):
    """
    """

    print(player_nbr_IA)
    name = ['AA1', 'Alabama', 'Alfred', 'Allegheny', 'Anderson', 'Arctic(AF7)', 'Arizona', 'Arkansas', 'Aroostock', 'Atlanta', 'Bagley', 'Baltimore', 'Boise', 'Bonhomme', 'Bonhomme', 'Bonhomme', 'Boston', 'Brooklyn', 'Brooks', 'California', 'Casco', 'Chicago', 'Chicago', 'Colorado', 'Columbus', 'Commodore', 'Concord', 'Connecticut', 'Constellation', 'Constellation', 'Constitution', 'Constitution', 'Constitution', 'Constitution', 'Cushing', 'Davis', 'Davis', 'Delaware', 'DeLong', 'Dent', 'Dolphin', 'Downes', 'Enterprise', 'Enterprise', 'Ericsson', 'Erie', 'Erie', 'Essex', 'Farragut', 'Florida', 'Flusser', 'Fulton', 'Gannet', 'Garfish', 'General', 'Georgia', 'Gleaves', 'Gloucester', 'Grayback', 'Hartford', 'Henderson', 'Henley', 'Holland', 'Holland', 'Hopkins', 'Hornet', 'Houston', 'Hudson', 'Idaho', 'Independence', 'Independence', 'Indiana', 'Indianapolis', 'Iowa', 'Jupiter', 'K5', 'Kearsarge', 'L6', 'Langley', 'Langley', 'Lehigh', 'Lexington', 'Lexington', 'Ludlow', 'M1', 'MacDonough', 'Mackenzie', 'Mackerel', 'Marblehead', 'Maryland', 'Massachusetts', 'Mayflower', 'Mayrant', 'Medusa', 'Melville', 'Mendota', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Monadnock', 'Monaghan', 'Monitor', 'Monocacy', 'Nebraska', 'Nevada', 'New', 'New', 'Newark', 'Nitro', 'Northampton', 'O3', 'Ohio', 'Oklahoma', 'Olympia', 'Onondaga', 'Oregon', 'Owl', 'Panay', 'Patoka', 'Paulding', 'PC26', 'PC405', 'PC451', 'PE33', 'Pennsylvania', 'Pennsylvania', 'Pennsylvania', 'Pensacola', 'Petrel', 'Philadelphia', 'Plunger', 'Porpoise', 'Porter', 'Portland', 'Powhatan', 'Princeton', 'PT8', 'R26', 'R3', 'Raleigh', 'Ranger', 'Relief', 'Rhode', 'S1(SS105)', 'S4', 'S48', 'Saint', 'Salamonie', 'Salem', 'Salmon', 'Salt', 'Saratoga', 'Sassacus', 'Savannah', 'Seal', 'Snapper', 'Somers', 'Stiletto', 'Stiletto', 'Swordfish', 'Tarantula', 'Texas', 'Thrasher', 'Tuna', 'United', 'V2', 'V4', 'V5', 'Vesuvius', 'Virginia', 'Wadsworth', 'Wampanoag', 'Washington', 'Wasp', 'Wasp', 'West', 'Wichita', 'Winslow', 'Wright', 'Yorktown', 'Yorktown', 'YT161']

    ## IA first implementation

    IA_order = ''

    if len(game['player'][str(player_nbr_IA)]['excavators']) < 2 and game['player'][str(player_nbr_IA)]['ore'] > 2:

        for i in range(2):
            ships_name = name[random.randint(0, len(name))-1]

            if ships_name in game['player'][str(player_nbr_IA)]['excavators']:

                ships_name = ships_name + str(random.randint(0,1000))

            IA_order += ships_name + ':excavator-M '

    if game['nbr_tour_played'] > 0:

        for excavator in game['player'][str(player_nbr_IA)]['excavators']:

            IA_order += excavator + ':release '

            if game['player'][str(player_nbr_IA)]['excavators'][excavator][5] < game['player'][str(player_nbr_IA)]['excavators'][excavator][6]:
                position_asteroids = []
                asteroids_on_board = []
                for asteroid_nbr in range(len(game['asteroids'])):
                    position_asteroids = [int(game['asteroids'][str(asteroid_nbr)]['x']), int(game['asteroids'][str(asteroid_nbr)]['y'])]
                    asteroids_on_board += [[str(asteroid_nbr), position_asteroids]]

                asteroid_to_reach = ['null', 1000]
                pos_x_exc = game['player'][str(player_nbr_IA)]['excavators'][excavator][1]
                pos_y_exc = game['player'][str(player_nbr_IA)]['excavators'][excavator][2]

                for asteroid in asteroids_on_board:
                    pos_x_ast = asteroid[1][0]
                    pos_y_ast = asteroid[1][1]

                    if abs(int(pos_x_exc) - int(pos_x_ast)) >= abs(int(pos_y_exc) - int(pos_y_ast)):
                        dist = abs(int(pos_x_exc) - int(pos_x_ast))

                    elif abs(int(pos_y_exc) - int(pos_y_ast)) > abs(int(pos_x_exc) - int(pos_x_ast)):
                        dist = abs(int(pos_y_exc) - int(pos_y_ast))

                    if dist < asteroid_to_reach[1] and game['asteroids'][asteroid[0]]['nbr_ore'] > 0:

                        asteroid_to_reach[0] = asteroid[0]
                        asteroid_to_reach[1] = dist

                if int(pos_y_exc) == int(game['asteroids'][asteroid_to_reach[0]]['y']) and int(pos_x_exc) == int(game['asteroids'][asteroid_to_reach[0]]['x']):
                    IA_order += excavator + ':lock '

                else:
                    if int(pos_x_exc) < int(game['asteroids'][asteroid_to_reach[0]]['x']):
                        pos_x_ext_to_go = int(pos_x_exc) + 1

                    elif int(pos_x_exc) > int(game['asteroids'][asteroid_to_reach[0]]['x']):
                        pos_x_ext_to_go = int(pos_x_exc) - 1

                    elif int(pos_x_exc) == int(game['asteroids'][asteroid_to_reach[0]]['x']):
                        pos_x_ext_to_go = int(pos_x_exc)

                    if int(pos_y_exc) < int(game['asteroids'][asteroid_to_reach[0]]['y']):
                        pos_y_ext_to_go = int(pos_y_exc) + 1

                    elif int(pos_y_exc) > int(game['asteroids'][asteroid_to_reach[0]]['y']):
                        pos_y_ext_to_go = int(pos_y_exc) - 1

                    elif int(pos_y_exc) == int(game['asteroids'][asteroid_to_reach[0]]['y']):
                        pos_y_ext_to_go = int(pos_y_exc)

                    IA_order += excavator + ":@" + str(pos_x_ext_to_go) + "-" + str(pos_y_ext_to_go) + ' '

            elif game['player'][str(player_nbr_IA)]['excavators'][excavator][5] == game['player'][str(player_nbr_IA)]['excavators'][excavator][6]:

                portal_nbr = 'portal_' + str(player_nbr_IA)
                portal_x = int(game[portal_nbr]['x'])
                portal_y = int(game[portal_nbr]['y'])
                pos_x_exc = int(game['player'][str(player_nbr_IA)]['excavators'][excavator][1])
                pos_y_exc = int(game['player'][str(player_nbr_IA)]['excavators'][excavator][2])

                IA_order += excavator + ':release '

                if int(pos_y_exc) == int(portal_y) and int(pos_x_exc) == int(portal_x):
                    IA_order += excavator + ':lock '

                else:
                    if pos_x_exc < portal_x:
                        pos_x_ext_to_go = pos_x_exc + 1

                    elif pos_x_exc > portal_x:
                        pos_x_ext_to_go = pos_x_exc - 1

                    elif pos_x_exc == portal_x:
                        pos_x_ext_to_go = pos_x_exc

                    if pos_y_exc < portal_y:
                        pos_y_ext_to_go = pos_y_exc + 1

                    elif pos_y_exc > portal_y:
                        pos_y_ext_to_go = pos_y_exc + - 1

                    elif pos_y_exc == portal_y:
                        pos_y_ext_to_go = pos_y_exc

                    IA_order += excavator + ":@" + str(pos_x_ext_to_go) + "-" + str(pos_y_ext_to_go) + ' '
#_---------

        if game['player'][str(player_nbr_IA)]['ore'] > 3 and len(game['player'][str(player_nbr_IA)]['ships']) < 100:

            ships_name = name[random.randint(0, len(name))-1]

            if ships_name in game['player'][str(player_nbr_IA)]['ships']:

                ships_name = ships_name + str(random.randint(0,1000))

            IA_order += ships_name + ':scout '

        elif game['player'][str(player_nbr_IA)]['ore'] > 9:

            ships_name = name[random.randint(0, len(name))-1]

            if ships_name in game['player'][str(player_nbr_IA)]['ships']:

                ships_name = ships_name + str(random.randint(0,1000))

            IA_order += ships_name + ':warship '

        if len(game['player'][str(player_nbr_IA)]['ships']) > 0:

            if int(player_nbr_IA) == 1:
                portal = 'portal_2'

            elif int(player_nbr_IA) == 2:
                portal = 'portal_1'

            for ships in game['player'][str(player_nbr_IA)]['ships']:

                pos_x_ship = int(game['player'][str(player_nbr_IA)]['ships'][ships][1])
                pos_y_ship = int(game['player'][str(player_nbr_IA)]['ships'][ships][2])
                portal_y = int(game[portal]['y'])
                portal_x = int(game[portal]['x'])

                if int(pos_y_ship) == int(portal_y) and int(pos_x_ship) == int(portal_x):
                        if game['player'][str(player_nbr_IA)]['ships'][ships][0] == 'scout':
                            x_to_shoot = pos_x_ship + 2
                            y_to_shoot = pos_y_ship + 1
                        elif game['player'][str(player_nbr_IA)]['ships'][ships][0] == 'warship':
                            x_to_shoot = pos_x_ship + 2
                            y_to_shoot = pos_y_ship + 2
                        IA_order += ships + ':*' + str(x_to_shoot) + '-' + str(y_to_shoot) + ' '

                else:

                    if pos_x_ship < portal_x:
                        pos_x_ship_to_go = pos_x_ship + 1

                    elif pos_x_ship > portal_x:
                        pos_x_ship_to_go = pos_x_ship - 1

                    elif pos_x_ship == portal_x:
                        pos_x_ship_to_go = pos_x_ship

                    if pos_y_ship < portal_y:
                        pos_y_ship_to_go = pos_y_ship + 1

                    elif pos_y_ship > portal_y:
                        pos_y_ship_to_go = pos_y_ship + - 1

                    elif pos_y_ship == portal_y:
                        pos_y_ship_to_go = pos_y_ship

                    print(pos_y_ship_to_go, pos_x_ship_to_go)

                    IA_order += ships + ":@" + str(pos_x_ship_to_go) + "-" + str(pos_y_ship_to_go) + ' '



    IA_order = IA_order.strip(' ')

    print(IA_order)

    game['command_IA'][str(player_nbr_IA)] = IA_order

    return(IA_order)








def save_command(player_nbr, game, raw_command = ''):
    """This function ask the players to give their commands

    Parameters:
    ----------
        player_nbr: player who have to give his commands (str)
        raw_command = command entered by the IA (str) (facultative)
        game: informations over the game (dic)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 03/04/2018)
        implementation: Jamoulle Quentin (v.1 03/04/2018)
                        Antoine Valentin (v.2 09/04/2018)
    """
    raw_command = raw_command.split(' ')
    new_command = []
    if raw_command[0] != '':
        for i in raw_command:
            if ':' in i:
                command = i.split(':')
                command = [(command[0], command[1])]
                new_command += command

    game['new_command'][str(player_nbr)] = new_command










def create_game(game, path):
    """This function create the board of the game with the different portals and asteroids

    Parameters:
    ----------
        game: dictionnary where the informations will be saved (dic)
        path: path of the parameter of the game (str)

    Notes:
    -----
        The dictionnary should exist

   versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 03/04/2018)
        implementation: Jamoulle Quentin (v.1 03/04/2018)
                        Antoine Valentin (v.2 09/04/2018)
    """

    # cwd = os.getcwd()
    #path = cwd + '/game.mw'

    fh = open(path, 'r')
    lines = fh.readlines()

    for i in range(len(lines)):
        if 'size' in lines[i]:
            size = lines[i+1]
            line = size[0:2]
            colomn = size[3:5]

        elif 'portals' in lines[i]:
            portal_1 = lines[i+1]
            portal_1 = portal_1.strip()
            portal_1 = portal_1.split(' ')
            portal_2 = lines[i+2]
            portal_2 = portal_2.strip()
            portal_2 = portal_2.split(' ')

        elif 'asteroids' in lines[i]:
            asteroids_data = lines[i+1:]
            asteroids = {}
            for a in range(len(asteroids_data)):
                nbr = str(a)
                new_asteroid = str(asteroids_data[a].strip())
                new_asteroid = new_asteroid.split(' ')
                if new_asteroid[0] != "":
                    asteroids[nbr] = {}
                    asteroids[nbr]['x'] = new_asteroid[0]
                    asteroids[nbr]['y'] = new_asteroid[1]
                    asteroids[nbr]['nbr_ore'] = int(new_asteroid[2])
                    asteroids[nbr]['ore_per_tour'] = int(new_asteroid[3])
                    asteroids[nbr]['locked_excavators'] = []

    game['board'] = {}
    game['board']['lines'] = colomn
    game['board']['colomn'] = line

    game['portal_1'] = {}
    game['portal_1']['x'] = int(portal_1[0])
    game['portal_1']['y'] = int(portal_1[1])
    game['portal_1']['life'] = 100
    game['portal_1']['shootable_area'] = []

    game['portal_2'] = {}
    game['portal_2']['x'] = int(portal_2[0])
    game['portal_2']['y'] = int(portal_2[1])
    game['portal_2']['life'] = 100
    game['portal_2']['shootable_area'] = []

    game['asteroids'] = {}
    game['asteroids'] = asteroids

    game['player'] = {}
    for i in [1,2]:
        i = str(i)
        game['player'][i] = {}
        game['player'][i]['ore'] = 4.00
        game['player'][i]['ships'] = {}
        game['player'][i]['excavators'] = {}

    game['new_command'] = {}
    game['new_command']['1'] = []
    game['new_command']['2'] = []

    game['no_attack'] = 0
    game['nbr_tour_played'] = 0

    game['shootable_vessels'] = {}

    game['command_IA'] = {}
    game['command_IA']['1'] = ''
    game['command_IA']['2'] = ''

#-------------------------------------------------------------------------------

def create_board(game):
    """
	Parameters :

	       game : informations over the game (dic)

	This function create the dic of the board

	Return :

	       game: informations over the game (dic)

    """
    board = game['board']
    printed_board = []

    #create the frame of the board

    for i in range(int(board['lines'])+2):
        line = []
        for i in range(int(board['colomn'])+2):
            line.append('  ')

        printed_board.append(line)
    for lines in range(int(board['lines'])+2):
        for colomn in range(int(board['colomn'])+2):
            if lines == 0 :
                printed_board[lines][colomn] = '\033[1;36;47m  \033[0;30;48m'

            if lines == int(board['lines'])+1:
                printed_board[lines][colomn] = '\033[1;37;47m  \033[0;30;48m'

            if colomn == int(board['colomn'])+1 or colomn == 0:
                printed_board[lines][colomn] = '\033[1;37;47m  \033[0;30;48m'

    #place portal player 1

    portal_center = (game['portal_1']['x'], game['portal_1']['y'])
    game['portal_1']['shootable_area'] = []
    for y in range(portal_center[0]-2, portal_center[0]+3):
        for x in range(portal_center[1]-2, portal_center[1]+3):
            printed_board[x][y] = '\033[1;37;45m  \033[0;30;48m'
            game['portal_1']['shootable_area'] += [(y,x)]

    #place portal player 2

    portal_center = (game['portal_2']['x'], game['portal_2']['y'])
    game['portal_2']['shootable_area'] = []
    for y in range(portal_center[0]-2, portal_center[0]+3):
        for x in range(portal_center[1]-2, portal_center[1]+3):
            printed_board[x][y] = '\033[1;37;42m  \033[0;30;48m'
            game['portal_2']['shootable_area'] += [(y,x)]

    #place vessels

    for player_nbr in [1,2]:
        vessels_to_place = game['player'][str(player_nbr)]['ships']
        for key in vessels_to_place:
            if vessels_to_place[key][0] == 'scout':
                if player_nbr == 1:
                    to_print = '\033[1;37;45mSS\033[0;30;48m'

                else:
                    to_print =  '\033[1;37;42mSS\033[0;30;48m'

                for y in range(int(vessels_to_place[key][1])-1, int(vessels_to_place[key][1])+2):
                    for x in range(int(vessels_to_place[key][2])-1, int(vessels_to_place[key][2])+2):
                        printed_board[x][y] = to_print

            if vessels_to_place[key][0] == 'warship':
                if player_nbr == 1:
                    to_print = '\033[1;37;45mWW\033[0;30;48m'

                else:
                    to_print =  '\033[1;37;42mWW\033[0;30;48m'

                for x in range(int(vessels_to_place[key][1])-2, int(vessels_to_place[key][1])+3):
                    for y in range(int(vessels_to_place[key][2])-1, int(vessels_to_place[key][2])+2):
                        printed_board[y][x] = to_print

                for x in range(int(vessels_to_place[key][1])-1, int(vessels_to_place[key][1])+2):
                    for y in range(int(vessels_to_place[key][2])-2, int(vessels_to_place[key][2])+3):
                        printed_board[y][x] = to_print

    #place excavators

    for player_nbr in [1,2]:
        excavators_to_place = game['player'][str(player_nbr)]['excavators']
        for key in excavators_to_place:
            if player_nbr == 1:
                color = '\033[1;37;45m'

            elif player_nbr == 2:
                color = '\033[1;37;42m'

            if 'S' in excavators_to_place[key][0]:
                printed_board[int(excavators_to_place[key][2])][int(excavators_to_place[key][1])] = color + '°°\033[0;30;48m'

            elif 'M' in excavators_to_place[key][0]:
                for x in range(int(excavators_to_place[key][1])-1, int(excavators_to_place[key][1])+2):
                    printed_board[int(excavators_to_place[key][2])][x] = color + '°°\033[0;30;48m'

                for y in range(int(excavators_to_place[key][2])-1, int(excavators_to_place[key][2])+2):
                    printed_board[y][int(excavators_to_place[key][1])] = color + '°°\033[0;30;48m'

            elif 'L' in excavators_to_place[key][0]:
                for x in range(int(excavators_to_place[key][1])-2, int(excavators_to_place[key][1])+3):
                    printed_board[int(excavators_to_place[key][2])][x] = color + '°°\033[0;30;48m'

                for y in range(int(excavators_to_place[key][2])-2, int(excavators_to_place[key][2])+3):
                    printed_board[y][int(excavators_to_place[key][1])] = color + '°°\033[0;30;48m'

    #place asteroids

    asteroids_to_place = game['asteroids']
    for key in asteroids_to_place:
        if int(key) < 10:
            name = '0' +key

        else:
            name = key

        printed_board[int(asteroids_to_place[key]['y'])][int(asteroids_to_place[key]['x'])] = '\033[1;30;43m'+name+'\033[0;30;48m'

    game['board']['to_print'] = printed_board

#-------------------------------------------------------------------------------

def print_informations_player(player_nbr, game):
    """This function print the informations of the selected player

    Parameters:
    ----------
	player_nbr : player you want to print the informations (str)
        game : dictionnary contenning all the informations of the game (dic)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 04/04/2018)
        implementation: Jamoulle Quentin (v.1 04/04/2018)
                        Antoine Valentin (v.2 09/04/2018)

    """
    info_player = game['player'][player_nbr]
    if player_nbr == '1':
        colour = '\033[0;35;48m'
        portal = 'portal_1'

    else:
        colour = '\033[0;32;48m'
        portal = 'portal_2'

    print( colour + '\nPlayer ' + player_nbr + '\033[0;30;48m\t%d hp' %(game[portal]['life']))
    print('ore: ' + str(info_player['ore']))
    print('ships:')
    for key in info_player['ships']:
        name = info_player['ships'][str(key)][0]
        life = info_player['ships'][str(key)][3]
        pos_x = int(info_player['ships'][str(key)][1])
        pos_y = int(info_player['ships'][str(key)][2])
        print('\t%s: %s\t\t%d hp\tpos: x: %d y:%d' %(key, name, life, pos_x, pos_y))

    print('excavators:')
    for key in info_player['excavators']:
        name = info_player['excavators'][str(key)][0]
        life = info_player['excavators'][str(key)][3]
        pos_x = int(info_player['excavators'][str(key)][1])
        pos_y = int(info_player['excavators'][str(key)][2])
        status = info_player['excavators'][str(key)][4]
        stock = info_player['excavators'][str(key)][5]
        max_ore = info_player['excavators'][str(key)][6]
        print('\t%s: %s\t%dhp\tpos: x:%d y:%d\tstatus:%s\tstock: %.1f/%d' %(key, name, life, pos_x, pos_y, status, stock, max_ore))

    print('')

#-------------------------------------------------------------------------------

def print_informatons_asterroids(game):
    """This function will print the informations about the asteroids

    parameter:
    ---------
        game: informations over the game (dic)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 04/04/2018)
        implementation: Jamoulle Quentin (v.1 04/04/2018)
                        Antoine Valentin (v.2 09/04/2018)

    """
    asteroids = game['asteroids']
    print('\033[1;33;48mAsteroids:\033[0;30;48m')
    for key in range(len(asteroids)):
        name = str(key)
        if key < 10:
            name = '0' + name
        key = str(key)
        nbr_ore = asteroids[key]['nbr_ore']
        ore_tour = asteroids[key]['ore_per_tour']
        x = int(asteroids[key]['x'])
        y = int(asteroids[key]['y'])
        print('\t%s:\t%d ore\t%d o/t\tpos: x: %d y: %d' %(name, nbr_ore, ore_tour, x, y))

#-------------------------------------------------------------------------------

def print_board(game):
    """This function will print the board for the UI

    Parameters:
    ----------
        game: informations over the game (dic)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 04/04/2018)
        implementation: Jamoulle Quentin (v.1 04/04/2018)
                        Antoine Valentin (v.2 09/04/2018)

    """
    for i in range(len(game['board']['to_print'])):
        printed_line = ''
        for t in range(len(game['board']['to_print'][i])):
            printed_line += game['board']['to_print'][i][t]
        print(printed_line)

#-------------------------------------------------------------------------------

def print_UI(game):
    """This function will print all the UI (board + players informations + asteroids informations)

    Parameters:
    ----------
            game: informations over the game (dic)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 04/04/2018)
        implementation: Jamoulle Quentin (v.1 04/04/2018)
                        Antoine Valentin (v.2 09/04/2018)
    """
    create_board(game)
    print_informations_player('1', game)
    print_board(game)
    print_informations_player('2', game)
    print_informatons_asterroids(game)
    print('\nIf nobody attacks: %d tours left.' %(20-game['no_attack']))

#-------------------------------------------------------------------------------

def ask_command(player_nbr, game, raw_command = ''):
    """This function ask the players to give their commands

    Parameters:
    ----------
        player_nbr: player who have to give his commands (str)
        raw_command = command entered by the IA (str) (facultative)
        game: informations over the game (dic)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 03/04/2018)
        implementation: Jamoulle Quentin (v.1 03/04/2018)
                        Antoine Valentin (v.2 09/04/2018)
    """
    if raw_command == '':
        raw_command += input('Whats your command player %s? ' %(player_nbr))
    raw_command = raw_command.split(' ')
    new_command = []
    if raw_command[0] != '':
        for i in raw_command:
            if ':' in i:
                command = i.split(':')
                command = [(command[0], command[1])]
                new_command += command

    game['new_command'][player_nbr] = new_command

#-------------------------------------------------------------------------------

def enought_ore_to_buy(player_nbr, purchase, game):
    """This function test if the player has enought ore to buy his purchase

    Parameters:
    -----------
        player: The player who wants to buy (str)
        purchase: The purchase (int)
        game: informations over the game (dic)

    Returns:
    -------
        true: The player can bought the purchase (bool)
	false: The player can't buy the purchase (bool)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 04/04/2018)
        implementation: Jamoulle Quentin (v.1 04/04/2018)
                        Antoine Valentin (v.2 09/04/2018)
    """

    if game['player'][player_nbr]['ore'] >= purchase:
        return(True)

    else:
        return(False)

#-------------------------------------------------------------------------------

def buy_fase(game):
    """This function create a new ship for the selected player

    Parameters:
    ----------
        game: informations over the game (dic)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 04/04/2018)
        implementation: Jamoulle Quentin (v.1 04/04/2018)
                        Antoine Valentin (v.2 09/04/2018)

    """
    for player_nbr in ['1','2']:
        command = game['new_command'][player_nbr]
        if int(player_nbr) == 1:
            portal = 'portal_1'

        elif int(player_nbr) == 2:
            portal = 'portal_2'

        for i in range(len(command)):
            new_vessels = []
            if command[i][1] == 'scout' and enought_ore_to_buy(player_nbr, 3, game):
                new_vessels = ['scout', game[portal]['x'], game[portal]['y'], 3, True]
                game['player'][player_nbr]['ships'][command[i][0]] = new_vessels
                game['player'][player_nbr]['ore'] -= 3

            elif command[i][1] == 'warship' and enought_ore_to_buy(player_nbr, 9, game):
                new_vessels = ['warship', game[portal]['x'], game[portal]['y'], 18, True]
                game['player'][player_nbr]['ships'][command[i][0]] = new_vessels
                game['player'][player_nbr]['ore'] -= 9

            elif 'excavator' in command[i][1]:
                if 'S' in command[i][1] and enought_ore_to_buy(player_nbr, 1, game):
                    new_vessels = [command[i][1], int(game[portal]['x']), int(game[portal]['y']), 2, 'release', 0, 1, True]
                    game['player'][player_nbr]['excavators'][command[i][0]] = new_vessels
                    game['player'][player_nbr]['ore'] -= 1

                elif 'M' in command[i][1] and enought_ore_to_buy(player_nbr, 2, game):
                    new_vessels = [command[i][1], int(game[portal]['x']), int(game[portal]['y']), 3, 'release', 0, 4, True]
                    game['player'][player_nbr]['excavators'][command[i][0]] = new_vessels
                    game['player'][player_nbr]['ore'] -= 2

                elif 'L' in command[i][1] and enought_ore_to_buy(player_nbr, 4, game):
                    new_vessels = [command[i][1], int(game[portal]['x']), int(game[portal]['y']), 6, 'release', 0, 8, True]
                    game['player'][player_nbr]['excavators'][command[i][0]] = new_vessels
                    game['player'][player_nbr]['ore'] -= 4

#-------------------------------------------------------------------------------

def lock_release_fase(game):
    """This function locks the ship to the asteroids

    Parameters:
    ----------
	name_ship : name of the ship to lock (str)
	game: informations over the game (dic)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 04/04/2018)
        implementation: Jamoulle Quentin (v.1 04/04/2018)
                        Antoine Valentin (v.2 09/04/2018)

    """
    position_asteroids = []
    asteroids_on_board = []
    for asteroid_nbr in range(len(game['asteroids'])):
        position_asteroids = [(int(game['asteroids'][str(asteroid_nbr)]['x']), int(game['asteroids'][str(asteroid_nbr)]['y']))]
        asteroids_on_board += [[str(asteroid_nbr), position_asteroids]]

    for player_nbr in ['1','2']:
        if player_nbr == '1':
            portal = 'portal_1'

        elif player_nbr == '2':
            portal = 'portal_2'

        command = game['new_command'][player_nbr]
        for i in range(len(command)):
            if command[i][0] in game['player'][player_nbr]['excavators']:
                for a in range(len(asteroids_on_board)):
                    pos_excavator = (int(game['player'][player_nbr]['excavators'][command[i][0]][1]),int(game['player'][player_nbr]['excavators'][command[i][0]][2]))
                    if command[i][1] == 'lock' and game['player'][player_nbr]['excavators'][command[i][0]][4] != 'lock':
                        if [pos_excavator] == asteroids_on_board[a][1]:
                            game['player'][player_nbr]['excavators'][command[i][0]][4] = 'lock'
                            game['asteroids'][asteroids_on_board[a][0]]['locked_excavators'] += [[player_nbr, command[i][0]]]

                        elif pos_excavator == (game[portal]['x'], game[portal]['y']):
                            game['player'][player_nbr]['excavators'][command[i][0]][4] = 'lock'
                            game['player'][player_nbr]['ore'] += game['player'][player_nbr]['excavators'][command[i][0]][5]
                            game['player'][player_nbr]['excavators'][command[i][0]][5] = 0

                    if command[i][1] == 'release' and game['player'][player_nbr]['excavators'][command[i][0]][4] != 'release' and [pos_excavator] == asteroids_on_board[a][1]:
                        game['player'][player_nbr]['excavators'][command[i][0]][4] = 'release'
                        locked_excavators = []
                        for excavators in game['asteroids'][asteroids_on_board[a][0]]['locked_excavators']:
                            if [player_nbr, command[i][0]] != excavators:
                                locked_excavators += [excavators]
                        game['asteroids'][asteroids_on_board[a][0]]['locked_excavators'] = locked_excavators
                    elif command[i][1] == 'release' and game['player'][player_nbr]['excavators'][command[i][0]][4] != 'release' and pos_excavator in game[portal]['shootable_area']:
                        game['player'][player_nbr]['excavators'][command[i][0]][4] = 'release'

#-------------------------------------------------------------------------------

def deplacement_in_limits(vessel_type, place, game):
    """This function will says if a vessel will be out the board after deplacement or not

    parameters:
    ----------
        vessel_type: type of the vessel to deplace (str)
        place: place where the vessel have to deplace (tuple)
        game: informations over the game (dic)

    returns:
    -------
        True: the vessel stay in the board (bool)
        False: the vessel will be out the board (bool)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 05/04/2018)
        implementation: Jamoulle Quentin (v.1 05/04/2018)
                        Antoine Valentin (v.2 09/04/2018)

    """
    place_x = place[0]
    place_y = place[1]

    board_lenght = int(game['board']['colomn'])
    board_height = int(game['board']['lines'])

    if (vessel_type == 'scout') and (place_x > 1 and place_x <= board_lenght -1) and (place_y > 1 and place_y <= board_height -1):
        return(True)

    elif (vessel_type == 'warship') and (place_x > 2 and place_x <= board_lenght -2) and (place_y > 2 and place_y <= board_height -2):
        return(True)

    elif (vessel_type == 'excavator-S') and (place_x > 0 and place_x <= board_lenght) and (place_y > 0 and place_y <= board_height):
        return(True)

    elif (vessel_type == 'excavator-M') and (place_x > 1 and place_x <= board_lenght -1) and (place_y > 1 and place_y <= board_height -1):
        return(True)

    elif (vessel_type == 'excavator-L') and (place_x > 2 and place_x <= board_lenght -2) and (place_y > 2 and place_y <= board_height -2):
        return(True)

    else:
        return(False)

#-------------------------------------------------------------------------------

def deplacement_fase(game):
    """This function deplaces the ships and the excavators

    Parameter:
    ---------
        game : informations over the game (dic)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 05/04/2018)
        implementation: Jamoulle Quentin (v.1 05/04/2018)
                        Antoine Valentin (v.2 09/04/2018)
    """
    for player_nbr in ['1', '2']:
        commands = game['new_command'][player_nbr]
        for i in range(len(commands)):
            deplacement = ''
            if '@' in commands[i][1]:
                deplacement += commands[i][1].strip('@')
                deplacement = deplacement.split('-')
                x = deplacement[0]
                y = deplacement[1]
                if commands[i][0] in game['player'][player_nbr]['excavators'] and game['player'][player_nbr]['excavators'][commands[i][0]][7]:
                    vessel_type = game['player'][player_nbr]['excavators'][commands[i][0]][0]
                    if deplacement_in_limits(vessel_type, (int(x), int(y)), game) and game['player'][player_nbr]['excavators'][commands[i][0]][4] != 'lock':
                        delta_x = int(game['player'][player_nbr]['excavators'][commands[i][0]][1]) - int(x)
                        delta_y = int(game['player'][player_nbr]['excavators'][commands[i][0]][2]) - int(y)
                        if delta_x in [-1,0,1] and delta_y in [-1,0,1]:
                            game['player'][player_nbr]['excavators'][commands[i][0]][1] = x
                            game['player'][player_nbr]['excavators'][commands[i][0]][2] = y
                            game['player'][player_nbr]['excavators'][commands[i][0]][7] = False

                elif commands[i][0] in game['player'][player_nbr]['ships'] and game['player'][player_nbr]['ships'][commands[i][0]][4]:
                    vessel_type = game['player'][player_nbr]['ships'][commands[i][0]][0]
                    if deplacement_in_limits(vessel_type, (int(x), int(y)), game):
                        delta_x = int(game['player'][player_nbr]['ships'][commands[i][0]][1]) - int(x)
                        delta_y = int(game['player'][player_nbr]['ships'][commands[i][0]][2]) - int(y)
                        if delta_x in [-1,0,1] and delta_y in [-1,0,1]:
                            game['player'][player_nbr]['ships'][commands[i][0]][1] = x
                            game['player'][player_nbr]['ships'][commands[i][0]][2] = y
                            game['player'][player_nbr]['ships'][commands[i][0]][4] = False

#-------------------------------------------------------------------------------

def fight_portal(game):
    """This function will fight the portals

    parameters:
    ----------
        game: informations over the game (dic)

    returns:
    -------
        true: the portal were attacked (bool)
        false: the portal were not attacked (bool)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 05/04/2018)
        implementation: Jamoulle Quentin (v.1 05/04/2018)
                        Antoine Valentin (v.2 09/04/2018)
    """
    attack = False
    for player_nbr in ['1','2']:
        command = game['new_command'][player_nbr]
        for i in range(len(command)):
            if '*' in command[i][1]:
                place = command[i][1].strip('*')
                x = int(place.split('-')[0])
                y = int(place.split('-')[1])
                hit_place = (x, y)
                if command[i][0] in game['player'][player_nbr]['ships'] and game['player'][player_nbr]['ships'][command[i][0]][4]:
                    if hit_place in game['portal_1']['shootable_area']:
                        if game['player'][player_nbr]['ships'][command[i][0]][0] == 'scout':
                            attack = True
                            game['portal_1']['life'] -= 1

                        elif game['player'][player_nbr]['ships'][command[i][0]][0] == 'warship':
                            attack = True
                            game['portal_1']['life'] -= 3

                    elif (x, y) in game['portal_2']['shootable_area']:
                        if game['player'][player_nbr]['ships'][command[i][0]][0] == 'scout':
                            attack = True
                            game['portal_2']['life'] -= 1

                        elif game['player'][player_nbr]['ships'][command[i][0]][0] == 'warship':
                            attack = True
                            game['portal_2']['life'] -= 3

    if game['portal_1']['life'] < 0:
        game['portal_1']['life'] = 0
    if game['portal_2']['life'] < 0:
        game['portal_2']['life'] = 0

    return(attack)

#-------------------------------------------------------------------------------

def shootable_vessels(game):
    """Make a dictionnary that will know where there is a shootable vessel

    parameters:
    ----------
        game: informations over the game (dic)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 04/04/2018)
        implementation: Jamoulle Quentin (v.1 04/04/2018)
                        Antoine Valentin (v.2 09/04/2018)
    """
    shootable_vessels = []
    for player_nbr in ['1','2']:
        for vessels in ['ships', 'excavators']:
            for vessel_name in game['player'][player_nbr][vessels]:
                shootable_area =[]
                center_x = int(game['player'][player_nbr][vessels][vessel_name][1])
                center_y = int(game['player'][player_nbr][vessels][vessel_name][2])
                if game['player'][player_nbr][vessels][vessel_name][0] == 'scout':
                    for x in range(center_x - 1, center_x + 2):
                        for y in range(center_y - 1, center_y + 2):
                            shootable_case = [(x, y)]
                            shootable_area += shootable_case

                elif game['player'][player_nbr][vessels][vessel_name][0] == 'warship':
                    for x in range(center_x - 2, center_x + 3):
                        for y in range(center_y - 1, center_y + 2):
                            shootable_case = [(x, y)]
                            shootable_area += shootable_case

                    for x in range(center_x - 1, center_x + 2):
                        for y in range(center_y - 2, center_y + 3):
                            shootable_case = [(x, y)]
                            shootable_area += shootable_case

                elif game['player'][player_nbr][vessels][vessel_name][0] == 'excavator-S':
                    shootable_area = [(center_x, center_y)]

                elif game['player'][player_nbr][vessels][vessel_name][0] == 'excavator-M':
                    for x in range(center_x - 1, center_x + 2):
                        shootable_case = [(x, center_y)]
                        shootable_area += shootable_case

                    for y in range(center_y - 1, center_y + 2):
                        shootable_case = [(center_x, y)]
                        shootable_area += shootable_case

                elif game['player'][player_nbr][vessels][vessel_name][0] == 'excavator-L':
                    for x in range(center_x - 2, center_x + 3):
                        shootable_case = [(x, center_y)]
                        shootable_area += shootable_case

                    for y in range(center_y - 2, center_y + 3):
                        shootable_case = [(center_x, y)]
                        shootable_area += shootable_case

                shootable_vessels += [[player_nbr, vessels, vessel_name, shootable_area]]

    game['shootable_vessels'] = shootable_vessels

#-------------------------------------------------------------------------------

def hit_verified(hit_place, game):
    """This function will verrify if the attack's vessel will hit something

    parameters:
    ----------
        hit_place: coor of the shoot (x, y) (tuple)
        game: informations over the game (dic)

    returns:
    -------
        true: the attack hit something (bool)
        false: the attack does not hit anything (bool)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 05/04/2018)
        implementation: Jamoulle Quentin (v.1 05/04/2018)
                        Antoine Valentin (v.2 09/04/2018)
    """
    for i in range(len(game['shootable_vessels'])):
        if hit_place in game['shootable_vessels'][i][3]:
            return(True)

    return(False)

#-------------------------------------------------------------------------------

def hit_vessel(shooted_vessel_new, type_vessel, game):
    """This function will hit a vessel

    parameters:
    ----------
        shooted_vessel: informations over the shooted vessel (list)
        type_vessel: type of the ship who shoot ('scout' or 'warship') (str)
        game: informations over the game (dic)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 05/04/2018)
        implementation: Jamoulle Quentin (v.1 05/04/2018)
                        Antoine Valentin (v.2 09/04/2018)
    """
    if type_vessel == 'scout':
        game['player'][shooted_vessel_new[0]][shooted_vessel_new[1]][shooted_vessel_new[2]][3] -= 1

    elif type_vessel == 'warship':
        game['player'][shooted_vessel_new[0]][shooted_vessel_new[1]][shooted_vessel_new[2]][3] -= 3

#-------------------------------------------------------------------------------

def shooted_vessel_function(hit_place, game):
    """This function will give a list of hitted vessels by a shoot at hit_place

    parameters:
    ----------
        hit_place: coor of the shoot (x, y) (tuple)
        game: informations over the game (dic)

    return:
    ------
        shooted_vessel: list of vessel shooted by the attack (list)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 04/04/2018)
        implementation: Jamoulle Quentin (v.1 04/04/2018)
                        Antoine Valentin (v.2 09/04/2018)
    """
    shooted_vessel = []
    for i in range(len(game['shootable_vessels'])):
        if hit_place in game['shootable_vessels'][i][3]:
            shooted_vessel += [(game['shootable_vessels'][i][0], game['shootable_vessels'][i][1], game['shootable_vessels'][i][2])]

    return(shooted_vessel)

#-------------------------------------------------------------------------------

def vessel_alive(player_nbr, vessel_type, vessel_name, game):
    """This function test if a vessel is still alive and delete him if not
    parameters:
    ---------
        player_nbr: player who own the vessel (str)
        vessel_type: type of vessel ('ships' or 'excavators') (str)
        vessel_name: name of the vessel to test (str)
        game: informations over the game (dic)

    returns:
    -------
        true: the vessel is still alive (bool)
        false: the vessel is no more alive (bool)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 04/04/2018)
        implementation: Jamoulle Quentin (v.1 04/04/2018)
                        Antoine Valentin (v.2 09/04/2018)
    """
    if game['player'][player_nbr][vessel_type][vessel_name][3] > 0:
        return(True)
    else :
        return(False)

#-------------------------------------------------------------------------------

def fight_fase(game):
    """This function will let the vessels attack

    parameters:
    ----------
        game: informations over the game (dic)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 05/04/2018)
        implementation: Jamoulle Quentin (v.1 05/04/2018)
                        Antoine Valentin (v.2 09/04/2018)

    """
    attacked = fight_portal(game)
    shootable_vessels(game)
    for player_nbr in ['1','2']:
        command = game['new_command'][player_nbr]
        for i in range(len(command)):
            if '*' in command[i][1] and command[i][0] in game['player'][player_nbr]['ships']:
                type_vessel = game['player'][player_nbr]['ships'][command[i][0]][0]
                center_vessel_x = int(game['player'][player_nbr]['ships'][command[i][0]][1])
                center_vessel_y = int(game['player'][player_nbr]['ships'][command[i][0]][2])
                shooted_vessel = []
                hit_place = (int(command[i][1].strip('*').split('-')[0]), int(command[i][1].split('-')[1]))
                if type_vessel == 'scout':
                    vessel_range = 3

                elif type_vessel == 'warship':
                    vessel_range = 5

                hit_range = []
                for x in range(center_vessel_x - vessel_range, center_vessel_x + vessel_range):
                    for y in range(center_vessel_y - vessel_range, center_vessel_y + vessel_range):
                        hit_range +=  [(x, y)]

                if hit_place in hit_range and hit_verified(hit_place, game):
                    shooted_vessel = shooted_vessel_function(hit_place, game)
                    for a in range(len(shooted_vessel)):
                        hit_vessel(shooted_vessel[a], type_vessel, game)
                        game['player'][player_nbr]['ships'][command[i][0]][4] = False
                        attacked = True

    for player_nbr in ['1','2']:
        for vessel_type in ['ships','excavators']:
            to_delete = []
            for vessel_name in game['player'][player_nbr][vessel_type]:
                if not vessel_alive(player_nbr, vessel_type, vessel_name, game):
                    to_delete += [vessel_name]

            for i in range(len(to_delete)):
                del game['player'][player_nbr][vessel_type][to_delete[i]]

    if attacked == True:
        game['no_attack'] = 0

    else:
        game['no_attack'] += 1

#-------------------------------------------------------------------------------

def action_vessels(game):
    """This function will renitialize the right to attack/move a vessel

    parameters:
    ----------
        game: informations over the game (dic)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 04/04/2018)
        implementation: Jamoulle Quentin (v.1 04/04/2018)
                        Antoine Valentin (v.2 09/04/2018)
    """
    for player_nbr in ['1','2']:
        for type_vessel in ['ships','excavators']:
            if type_vessel == 'ships':
                dico_place_info = 4

            elif type_vessel == 'excavators':
                dico_place_info = 7

            for vessel_name in game['player'][player_nbr][type_vessel]:
                game['player'][player_nbr][type_vessel][vessel_name][dico_place_info] = True

#-------------------------------------------------------------------------------

def ore_harvest(game):
    """This function will give the ore to the locked excavators

    parameters:
    ----------
        game: informations over the game (dic)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 04/04/2018)
        implementation: Jamoulle Quentin (v.1 04/04/2018)
                        Antoine Valentin (v.2 09/04/2018)
    """
    for asteroid_nbr in game['asteroids']:
        i=0
        while i < game['asteroids'][asteroid_nbr]['ore_per_tour']:
            full_excavators = 0
            for locked_excavator in game['asteroids'][asteroid_nbr]['locked_excavators']:
                if game['player'][locked_excavator[0]]['excavators'][locked_excavator[1]][5] >= game['player'][locked_excavator[0]]['excavators'][locked_excavator[1]][6]:
                    full_excavators += 1

            if game['asteroids'][asteroid_nbr]['nbr_ore'] >= (len(game['asteroids'][asteroid_nbr]['locked_excavators'])):
                for locked_excavator in game['asteroids'][asteroid_nbr]['locked_excavators']:
                    if game['player'][locked_excavator[0]]['excavators'][locked_excavator[1]][5] < game['player'][locked_excavator[0]]['excavators'][locked_excavator[1]][6]:
                        game['player'][locked_excavator[0]]['excavators'][locked_excavator[1]][5] += 1
                        game['asteroids'][asteroid_nbr]['nbr_ore'] -= 1

            elif game['asteroids'][asteroid_nbr]['nbr_ore'] < (len(game['asteroids'][asteroid_nbr]['locked_excavators'])):
                for locked_excavator in game['asteroids'][asteroid_nbr]['locked_excavators']:
                    if game['player'][locked_excavator[0]]['excavators'][locked_excavator[1]][5] < game['player'][locked_excavator[0]]['excavators'][locked_excavator[1]][6]:
                        game['player'][locked_excavator[0]]['excavators'][locked_excavator[1]][5] += (game['asteroids'][asteroid_nbr]['nbr_ore'])/(len(game['asteroids'][asteroid_nbr]['locked_excavators'])-full_excavators)

                game['asteroids'][asteroid_nbr]['nbr_ore'] = 0

            i += 1

#-------------------------------------------------------------------------------

def end_of_game(game):
    """This function test if the game is not finish

    parameters:
    ----------
	game: informations over the game (dic)

    returns:
    -------
        true: the game is finished (bool)
        false: the game is not finished (bool)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 05/04/2018)
        implementation: Jamoulle Quentin (v.1 05/04/2018)
                        Antoine Valentin (v.2 09/04/2018)

    """
    if game['portal_1']['life'] > 0 and game['portal_2']['life'] > 0 and game['no_attack'] <= 200:
            return(False)
    else:
        return(True)

#-------------------------------------------------------------------------------

def game_tour(player_1, player_2, game):
    """This function play one tour of the game

    parameters:
    ----------
        player_1: False if the player is an IA (bool)
        player_2: False if the player is an IA (bool)
        game: informations over the game (dic)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 05/04/2018)
        implementation: Jamoulle Quentin (v.1 05/04/2018)
                        Antoine Valentin (v.2 09/04/2018)
                        Jamoulle Quentin (v.3 27/04/2018)
    """
    print_UI(game)
    if player_2 == False:
        orders = IA_test_2(2, game)
        save_command(1, game, r.get_remote_orders(connection))
        save_command(2, game, orders)
        r.notify_remote_orders(connection, orders)

    if player_1 == False:
        orders = IA_test_2(1, game)
        save_command(1, game, orders)
        r.notify_remote_orders(connection, orders)
        save_command(2, game, r.get_remote_orders(connection))

    print(game['new_command']['2'])

    # ask_command('1', game, game['command_IA']['1'])
    # ask_command('2', game, game['command_IA']['2'])
    buy_fase(game)
    lock_release_fase(game)
    deplacement_fase(game)
    fight_fase(game)
    ore_harvest(game)
    action_vessels(game)

    if not end_of_game(game):
        game['nbr_tour_played'] += 1
        game_tour(player_1, player_2, game)

#-------------------------------------------------------------------------------

def game(path, player_1, player_2):
    """This function is the function to launch the game from his beggining to his end

    parameters:
    ----------
        path: path of the parameter's files for the game (str)

    versions:
    --------
        specification:  Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 05/04/2018)
        implementation: Jamoulle Quentin (v.1 05/04/2018)
                        Antoine Valentin (v.2 09/04/2018)
    """
    game = {}
    create_game(game, path)

    # new_vessels = ['excavator-S', int(game[portal_1]['x']), int(game[portal_1]['y']), 2, 'release', 0, 1, True]
    # game['player']['1']['excavators']['quentin'] = new_vessels

    game_tour(player_1, player_2, game)
    print_UI(game)
    print('\033[1;31;48m\n***\n\nGAME OVER\n\n***\033[0;30;48m')

#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------


#Implemaentation IA

def IA(player_nbr, game):
    """This function will remplace the shoosen player by a naive IA

    paramaters:
    ----------
        player_nbr: shoosen player (str)
        game:informations over the game (dic)

    return:
    ------
        command: command the the shossen player will play

    versions:
    --------
        specifications: Baestle Antoine (v.1 15/02/2018)
                        Jamoulle Quentin (v.2 07/04/2018)
        implementation: Jamoulle Quentin (v.1 07/04/2018)
                        Antoine Valentin (v.2 07/04/2018)
                        Jamoulle Quentin (v.3 08/04/2018)
                        Antoine Valentin (v.4 08/04/2018)
    """

    command = ''

    #buy fase
    action = random.randint(0,5)
    if action == 0:             #buy a scout
        name = 'scout' + str(len(game['player'][player_nbr]['ships']))
        new_command = name + ':scout '
        command += new_command

    elif action == 1:            #buy warship
        name = 'warship' + str(len(game['player'][player_nbr]['ships']))
        new_command = name + ':warship '
        command += new_command

    elif action == 2:
        name = 'S_' + str(len(game['player'][player_nbr]['excavators']))
        new_command = name + ':excavator-S '
        command += new_command

    elif action == 3:
        name = 'M_' + str(len(game['player'][player_nbr]['excavators']))
        new_command = name + ':excavator-M '
        command += new_command

    elif action == 4:
        name = 'L_' + str(len(game['player'][player_nbr]['excavators']))
        new_command = name + ':excavator-L '
        command += new_command

        #do nothing if action == 5 --> no attack
        #do also nothing if they did not have enough ore

    #deplacement fase
    for ships in (game['player'][player_nbr]['ships']):
        direction = random.randint(0, 4)
        if direction == 0:          #go up
            new_place = int(game['player'][player_nbr]['ships'][ships][1]) - 1
            game['player'][player_nbr]['ships'][ships][1] = new_place

        elif direction == 1:         #go down
            new_place = int(game['player'][player_nbr]['ships'][ships][1]) + 1
            game['player'][player_nbr]['ships'][ships][1] = new_place

        elif direction == 2:        #go left
            new_place = int(game['player'][player_nbr]['ships'][ships][2]) - 1
            game['player'][player_nbr]['ships'][ships][2] = new_place

        elif direction == 3:
            new_place = int(game['player'][player_nbr]['ships'][ships][2]) + 1
            game['player'][player_nbr]['ships'][ships][2] = new_place

        command += ships + ':@' + str(game['player'][player_nbr]['ships'][ships][1]) + '-' + str(game['player'][player_nbr]['ships'][ships][2]) + ' '

    for excavators in (game['player'][player_nbr]['excavators']):
        direction = random.randint(0, 4)                #0:up 1:down 2:left 3:right 4:dont move
        if direction == 0:          #go up
            new_place = int(game['player'][player_nbr]['excavators'][excavators][1]) - 1
            game['player'][player_nbr]['excavators'][excavators][1] = new_place

        elif direction == 1:         #go down
            new_place = int(game['player'][player_nbr]['excavators'][excavators][1]) + 1
            game['player'][player_nbr]['excavators'][excavators][1] = new_place

        elif direction == 2:        #go left
            new_place = int(game['player'][player_nbr]['excavators'][excavators][2]) - 1
            game['player'][player_nbr]['excavators'][excavators][2] = new_place

        elif direction == 3:        #go right
            new_place = int(game['player'][player_nbr]['excavators'][excavators][2]) + 1
            game['player'][player_nbr]['excavators'][excavators][2] = new_place

        command += excavators + ':@' + str(game['player'][player_nbr]['excavators'][excavators][1]) + '-' + str(game['player'][player_nbr]['excavators'][excavators][2]) + ' '

        #do nothing if direction == 4 (stay on his place)

    #lock/release fase
    for excavators in (game['player'][player_nbr]['excavators']):
        action = random.randint(0, 2)               #0:try to lock 1:try to release 2:do nothing
        if action == 0:             #try to lock
            command += excavators + ':lock '

        elif action == 1:           #try to release
            command += excavators + ':release '

        #do nothing if action == 2

    #fight fase
    for ships in (game['player'][player_nbr]['ships']):
        action = random.randint(0, 1)               #0:try to attack 1:do nothing
        if action == 0:             #try to attack (do not respect the manathan distance)

            place_x = int(game['player'][player_nbr]['ships'][ships][1]) + random.randint(0, 4)
            place_y = int(game['player'][player_nbr]['ships'][ships][2]) + random.randint(0, 4)
            command += ships + ':*' + str(place_x) + '-' + str(place_y) + ' '

    game['command_IA'][str(player_nbr)] = command

#-------------------------------------------------------------------------------


print(r.get_IP())

path = os.getcwd()
path += '/../maps/cross.mw'

player_id = 1
remote_ip = '138.48.160.152'
connection = r.connect_to_player(player_id, remote_ip, True)

if player_id == 1:
	game(path, True, False)

elif player_id == 2:
	game(path, False, True)

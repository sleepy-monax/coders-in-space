# -*- coding: utf-8 -*-
from colored import fg, attr,bg 
import os
import random
import time
import remote_play


def play_the_game(file_name, type1, type2, player, IP_adress):
    """plays the game by calling multiple fonctions

    Parameters
    ----------
    file_name : name of the main file (str)
    type 1 : type of the player (str)
    type 2 : type of the player (str)

    specifications : Moussa El Hafid
    implementation : Moussa El Hafid
    """

    # Initialization of the game

    ships_player_1 = []
    ships_player_2 = []

    game = {'player_1': {'ore': 4,
                         'ships': {},
                         'portal': {'life': 100, 'position': []}
                         },
            'player_2': {'ore': 4,
                         'ships': {},
                         'portal': {'life': 100, 'position': []}}
            }

    ships_to_buy = {'scout': {'life': 3, 'strength': 1, 'reach': 3, 'type': 'scout', 'cost': 3},
                    'warship': {'life': 18, 'strength': 3, 'reach': 5, 'type': 'warship', 'cost': 9},
                    'excavator-S': {'life': 2, 'tonnage': 1, 'capacity': 0, 'type': 'excavator-S', 'cost': 1,
                                    'state': 'unlocked'},
                    'excavator-M': {'life': 3, 'tonnage': 4, 'capacity': 0, 'type': 'excavator-M', 'cost': 2,
                                    'state': 'unlocked'},
                    'excavator-L': {'life': 6, 'tonnage': 9, 'capacity': 0, 'type': 'excavator-L', 'cost': 4,
                                    'state': 'unlocked'}
                    }

    # reading the file and getting the informations

    #os.chdir('C:\\Users\\elhaf\\Desktop\\Cours\\Development labs\\Maps')

    file = open(file_name, 'r')
    file_lines = file.readlines()
    file.close()

    for number, i in enumerate(file_lines):
        file_lines[number] = i.strip()

    size_line, size_column = file_lines[1].split(" ")
    size_line = int(size_line)
    size_column = int(size_column)

    portal_1_x, portal_1_y = file_lines[3].split(' ')
    portal_1_x = int(portal_1_x)
    portal_1_y = int(portal_1_y)

    portal_2_x, portal_2_y = file_lines[4].split(' ')
    portal_2_x = int(portal_2_x)
    portal_2_y = int(portal_2_y)

    game['player_1']['portal']['position'].append((portal_1_x, portal_1_y))
    game['player_2']['portal']['position'].append((portal_2_x, portal_2_y))

    asteroids = {}

    # getting asteroids info

    nb_asteroid = 1
    for line in file_lines[6:]:
        line = line.split(' ')
        asteroids['a_' + str(nb_asteroid)] = {'position': (int(line[0]), int(line[1])), 'ores': int(line[2]),
                                              'ores_per_turn': int(line[3])}
        nb_asteroid += 1

    # boardgame creation and loop that plays the game

    connection = remote_play.connect_to_player(player, IP_adress,True)



    nb_tours_no_degats = 0
    nb_row = 1
    boardgame = create_boardgame(size_line, size_column)

    while game_over(game, nb_tours_no_degats) == False:
        final_line_1 = []
        final_line_2 = []
        print("--- TOUR N°%i ---" % nb_row)
        touched = executions_instructions(game, boardgame, ships_player_1, ships_player_2, asteroids, type1, type2,
                                          ships_to_buy, size_line, size_column, nb_asteroid, nb_row, connection)

        for player in game:
            for asteroid in asteroids:
                for excavator_name in game[player]['ships']:
                    if 'excavator' in game[player]['ships'][excavator_name]['type']:
                        extract_ores(excavator_name, asteroid, asteroids, game, ships_player_1, ships_player_2)
                        drop_ores(excavator_name, game, ships_player_1, ships_player_2)

        show_the_board(ships_player_1, ships_player_2, boardgame, size_line, size_column, game, asteroids, nb_row,final_line_1,final_line_2)
        nb_row += 1

        if len(touched) == 0:
            nb_tours_no_degats += 1
        else:
            nb_tours_no_degats = 0

        time.sleep(0.12)

    if game['player_1']['portal']['life'] < game['player_2']['portal']['life']:
        winner = "Player _2"

    elif game['player_1']['portal']['life'] > game['player_2']['portal']['life']:
        winner = "Player _1"

    elif game['player_1']['portal']['life'] > game['player_2']['portal']['life']:
        if game['player_1']['ore'] < game['player_2']['ore']:
            winner = "Player _2"
        elif game['player_2']['ore'] < game['player_1']['ore']:
            winner = "Player _1"
        else:
            winner = "Ex Equo"

    if nb_tours_no_degats == 200:
        if game['player_1']['ore'] < game['player_2']['ore']:
            winner = "Player _2"
        elif game['player_2']['ore'] < game['player_1']['ore']:
            winner = "Player _1"
        else:
            winner = "Ex Equo"
    print('Game Over ', winner, ' You won !')


def IA_function(game, player, asteroids, nb_asteroid, nb_row):
    """Artificial intelligence who plays the game

        Parameters
        -----------
        game: dictionary of the game data (dict)
        player: player that uses the AI 'player_1' or 'player_2' (str)
        asteroids: dictionary of asteroids data (dict)
        nb_asteroid : number of asteroids in the game (int)

        Return
        ------
        Order

        Specification : Moussa El Hafid
        Implementation : Margaux Foulon V1.0 (28-04-2018)
                       : Margaux Foulon, Moussa El Hafid, Thomas Mestre V2.0 (07-05-3018)
        """

    if player == "player_1":
        player_adv = "player_2"
    elif player == "player_2":
        player_adv = "player_1"

    if player == "player_1":
        IA_name = "Tokyo#" + str(random.randint(0, 1000))
    elif player == "player_2":
        IA_name = "Berlin#" + str(random.randint(0, 1000))

    orders = ""

    # achat des vaisseaux
    # -------------------------------------------------------------------------------------------------------------------------------------------

    ore = game[player]['ore']
    nb_aste = 0

    nb_excavator = 0

    for ship_name in game[player]['ships']:
        if 'excavator' in game[player]['ships'][ship_name]['type']:
            nb_excavator +=1

    if nb_excavator < 3 :
        for asteroid in asteroids:
            if asteroids[asteroid]['ores'] > 0:
                nb_aste += 1

        if nb_asteroid >= 1:  # achat en fontion du nombre d'asteroides "remplis" puis en fonction de l'ore du joueur

            if ore > 4:
                ship_1 = '%s:excavator-L ' % IA_name
                orders += ship_1
                ore -= 4

            elif ore >= 2:
                ship_2 = '%s:excavator-M ' % IA_name
                orders += ship_2
                ore -= 2

            elif ore > 1:
                ship_3 = '%s:excavator-S ' % IA_name
                orders += ship_3
                ore -= 1


    else :
        nb_ship_adv = 0
        for ship_name_adv in game[player_adv]['ships']:
            nb_ship_adv += 1

        if nb_ship_adv >= 2:
            # faire en fonction du nombre de vaisseau adversaire
            if ore >= 9:
                ship_4 = '%s:warship ' % IA_name
                orders += ship_4

            elif ore > 3:
                ship_5 = '%s:scout ' % IA_name
                orders += ship_5

    # se verrouiller/se déverrouiller
    # -------------------------------------------------------------------------------------------------------------------------------------------
    for ship_name in game[player]['ships']:  # en fonction de l'ore
        if 'excavator' in game[player]['ships'][ship_name]['type']:

            for asteroid in asteroids:
                ores_left = asteroids[asteroid]['ores']
                if game[player]['ships'][ship_name]['position'][0] == asteroids[asteroid]['position']:  # sur asteroide
                    if ores_left > 0 and game[player]['ships'][ship_name][
                        'state'] == 'unlocked' and game[player]['ships'][ship_name]['capacity'] < game[player]['ships'][ship_name][
                        'tonnage']:  # si l'astéroide a encore de l'ore il reste lock ou se lock
                        lock = '%s' % ship_name + ':lock '
                        ores_left -= asteroids[asteroid]['ores_per_turn']
                        orders += lock

                    elif (asteroids[asteroid]['ores'] <= 0 and game[player]['ships'][ship_name]['state'] == 'locked' \
                            )or (game[player]['ships'][ship_name]['capacity'] == game[player]['ships'][ship_name][
                        'tonnage'] and \
                            game[player]['ships'][ship_name][
                                'state'] == 'locked'):  # si l'astéroide n'a plus d'ore ou le vaisseau est rempli on se déverouille.
                        unlock = '%s' % ship_name + ':release '
                        orders += unlock

            if game[player]['ships'][ship_name]['position'][0] == game[player]['portal']['position'][0]:  # sur portail

                if game[player]['ships'][ship_name]['state'] == 'locked' and game[player]['ships'][ship_name][
                    'capacity'] == 0:  # si le vaisseau a plus d'ore sur lui

                    unlock = '%s' % ship_name + ':release '
                    orders += unlock

                elif game[player]['ships'][ship_name]['state'] == 'unlocked' and game[player]['ships'][ship_name][
                    'capacity'] == game[player]['ships'][ship_name][
                    'tonnage']:  # si le vaisseau doit déposer son ore
                    lock = '%s' % ship_name + ':lock '
                    orders += lock

    # attaquer
    # -------------------------------------------------------------------------------------------------------------------------------------------
    for ship_name in game[player]['ships']:

        if "excavator" not in game[player]['ships'][ship_name]['type']:
            x1 = game[player]['ships'][ship_name]['position'][0][0]
            x2 = game[player]['ships'][ship_name]['position'][0][1]

            # attaquer le portail
            for position in game[player_adv]['portal']['position']:
                y1 = position[0]
                y2 = position[1]

                manhattan = abs(x1 - y1) + abs(x2 - y2)
                reach = game[player]['ships'][ship_name]['reach']

                if reach >= manhattan:  # si le vaisseau est dans la portée
                    position = '%i-%i' % (y1, y2)
                    attack = '%s:*' % ship_name + position + " "
                    orders += attack

            # attaquer le vaisseau

            for ship_name_adv in game[player_adv]['ships']:

                for position in game[player_adv]['ships'][ship_name_adv]['position']:
                    y1 = position[0]
                    y2 = position[1]

                    manhattan = abs(x1 - y1) + abs(x2 - y2)
                    if "excavator" not in game[player]['ships'][ship_name]['type']:
                        reach = game[player]['ships'][ship_name]['reach']

                        if reach >= manhattan:  # si le vaisseau est dans la portée
                            position = '%i-%i' % (y1, y2)
                            attack = '%s:*' % ship_name + position + " "
                            orders += attack

    for ship_name in game[player]['ships']:
        move = ''
        if 'excavator' in game[player]['ships'][ship_name]['type']:
            x1 = game[player]['ships'][ship_name]['position'][0][0]
            x2 = game[player]['ships'][ship_name]['position'][0][1]
            # deplacement des extracteurs
            if game[player]['ships'][ship_name]['state'] == 'unlocked':

                # 1.  direction vers le portail car l'extracteur est plein

                if game[player]['ships'][ship_name]['capacity'] == game[player]['ships'][ship_name]['tonnage']:
                    # si le vaisseau va vers le portail car il est plein

                    y1 = game[player]['portal']['position'][0][0]
                    y2 = game[player]['portal']['position'][0][1]

                    if x1 < y1:
                        if x2 < y2:
                            x = x1 + 1
                            y = x2 + 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 > y2:
                            x = x1 + 1
                            y = x2 - 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 == y2:
                            x = x1 + 1
                            y = x2
                            move = "%s:@%s-%s " % (ship_name, x, y)

                    elif x1 > y1:
                        if x2 < y2:
                            x = x1 - 1
                            y = x2 + 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 > y2:
                            x = x1 - 1
                            y = x2 - 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 == y2:
                            x = x1 - 1
                            y = x2
                            move = "%s:@%s-%s " % (ship_name, x, y)

                    elif x1 == y1:
                        if x2 < y2:
                            x = x1
                            y = x2 + 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 > y2:
                            x = x1
                            y = x2 - 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 == y2:
                            x = x1
                            y = x2
                            move = "%s:@%s-%s " % (ship_name, x, y)


                # 3.  direction vers un asteroide car l'extracteur est vide
                else:

                    x1 = game[player]['ships'][ship_name]['position'][0][0]
                    x2 = game[player]['ships'][ship_name]['position'][0][1]

                    min = 100

                    z1 = game[player]['portal']['position'][0][0]
                    z2 = game[player]['portal']['position'][0][1]

                    for asteroid in asteroids:
                        if asteroids[asteroid]['ores'] > 0:
                            y1 = asteroids[asteroid]['position'][0]
                            y2 = asteroids[asteroid]['position'][1]

                            ##determination de l'asteroide le plus proche (asteroid_close)
                            manhattan = abs(x1 - y1) + abs(x2 - y2)

                            if manhattan < min:
                                min = manhattan
                                z1 = asteroids[asteroid]['position'][0]
                                z2 = asteroids[asteroid]['position'][1]

                    if x1 < z1:
                        if x2 < z2:
                            x = x1 + 1
                            y = x2 + 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 > z2:
                            x = x1 + 1
                            y = x2 - 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 == z2:
                            x = x1 + 1
                            y = x2
                            move = "%s:@%s-%s " % (ship_name, x, y)

                    elif x1 > z1:
                        if x2 < z2:
                            x = x1 - 1
                            y = x2 + 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 > z2:
                            x = x1 - 1
                            y = x2 - 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 == z2:
                            x = x1 - 1
                            y = x2
                            move = "%s:@%s-%s " % (ship_name, x, y)

                    elif x1 == z1:
                        if x2 < z2:
                            x = x1
                            y = x2 + 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 > z2:
                            x = x1
                            y = x2 - 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 == z2:
                            x = x1
                            y = x2
                            move = "%s:@%s-%s " % (ship_name, x, y)
        orders += move

        # 4. direction vers un vaisseau adverse est dans les environs du portail

        if game[player]['ships'][ship_name]['type'] == 'scout' or game[player]['ships'][ship_name][
            'type'] == 'warship':  # deplacement des attaquants

            for ship_name_adv in game[player_adv]['ships']:
                x1 = game[player]['ships'][ship_name]['position'][0][0]
                x2 = game[player]['ships'][ship_name]['position'][0][1]
                y1 = game[player]['portal']['position'][0][0]
                y2 = game[player]['portal']['position'][0][1]
                z1 = game[player_adv]['ships'][ship_name_adv]['position'][0][0]
                z2 = game[player_adv]['ships'][ship_name_adv]['position'][0][1]

                portal_ship = abs(x1 - x2) + abs(y1 - y2)  # distance entre portail et vaisseau
                portal_adv = abs(y1 - y2) + abs(z1 - z2)  # distance entre portail et vaisseau adversaire
                ship_adv = abs(x1 - x2) + abs(z1 - z2)  # distance entre vaisseau et vaisseau adversaire

                # vaisseau menacant le portail :

                if portal_adv < 10 and portal_ship < portal_adv and ship_adv > game[player]['ships'][ship_name][
                    'reach']:
                    # si le vaisseau adv est dans le rayon de 10 autour du portail
                    # si la distance entre le portail et notre vaisseau est < que celle entre le vaisseau adv et notre portail
                    # c-à-d que si le vaisseau est entre le portail et le vaisseau adv
                    # et que la distance entre le vaisseau et le vaisseau adv est plus grande que son coup,
                    # bouger le vaisseau vers le vaisseau adv pour defendre son portail

                    if x1 < z1:
                        if x2 < z2:
                            x = x1 + 1
                            y = x2 + 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 > z2:
                            x = x1 + 1
                            y = x2 - 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 == z2:
                            x = x1 + 1
                            y = x2
                            move = "%s:@%s-%s " % (ship_name, x, y)

                    elif x1 > z1:
                        if x2 < z2:
                            x = x1 - 1
                            y = x2 + 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 > z2:
                            x = x1 - 1
                            y = x2 - 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 == z2:
                            x = x1 - 1
                            y = x2
                            move = "%s:@%s-%s " % (ship_name, x, y)

                    elif x1 == z1:
                        if x2 < z2:
                            x = x1
                            y = x2 + 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 > z2:
                            x = x1
                            y = x2 - 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 == z2:
                            x = x1
                            y = x2
                            move = "%s:@%s-%s " % (ship_name, x, y)

                # 5.  direction vers portail adverse pour attaquer

                else:
                    x1 = game[player]['ships'][ship_name]['position'][0][0]
                    x2 = game[player]['ships'][ship_name]['position'][0][1]
                    y1 = game[player_adv]['portal']['position'][0][0]
                    y2 = game[player_adv]['portal']['position'][0][1]

                    if x1 < y1:
                        if x2 < y2:
                            x = x1 + 1
                            y = x2 + 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 > y2:
                            x = x1 + 1
                            y = x2 - 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 == y2:
                            x = x1 + 1
                            y = x2
                            move = "%s:@%s-%s " % (ship_name, x, y)

                    elif x1 > y1:
                        if x2 < y2:
                            x = x1 - 1
                            y = x2 + 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 > y2:
                            x = x1 - 1
                            y = x2 - 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 == y2:
                            x = x1 - 1
                            y = x2
                            move = "%s:@%s-%s " % (ship_name, x, y)

                    elif x1 == y1:
                        if x2 < y2:
                            x = x1
                            y = x2 + 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 > y2:
                            x = x1
                            y = x2 - 1
                            move = "%s:@%s-%s " % (ship_name, x, y)

                        elif x2 == y2:
                            x = x1
                            y = x2
                            move = "%s:@%s-%s " % (ship_name, x, y)
            orders += move

    orders = orders.strip(" ")

    return orders


def executions_instructions(game, boardgame, ships_player_1, ships_player_2, asteroids, type1, type2, ships_to_buy,
                            size_line, size_column, nb_asteroid, nb_row, connection):
    """ executes the instructions

    Parameters
    ----------
    game : dictionary of the game (dict)
    boardgame : dictionary of the boardgame(dict)
    ships_player_1 : list of ships of the player 1 (list)
    ships_player_2 : list of ships of the player 2 (list)
    asteroids : dictionary of the asteroids (dict)
    type1 : type of the player 1 (str)
    type2 : type of the player 2 (str)
    ships_to_buy : dictionary of the ships you can buy (dict)

    Specifications : Moussa El Hafid
    Implementation : Moussa El Hafid
    """
    if type1 == 'IA':
        instructions_pl_1 = str(IA_function(game, 'player_1', asteroids, nb_asteroid, nb_row))
        remote_play.notify_remote_orders(connection, instructions_pl_1)

    elif type1 == 'player':
        instructions_pl_1 = whatdoyouwant()

    elif type1 == 'remote':
        instructions_pl_1 = remote_play.get_remote_orders(connection)

    if type2 == 'IA':
        instructions_pl_2 = str(IA_function(game, 'player_2', asteroids, nb_asteroid, nb_row))
        remote_play.notify_remote_orders(connection, instructions_pl_2)

    elif type2 == 'player':
        instructions_pl_2 = whatdoyouwant()

    elif type2 == 'remote':
        instructions_pl_2 = remote_play.get_remote_orders(connection)

    buy_1 = []
    lock_unlock_1 = []
    move_attack_1 = []
    ship_move_attack_1 = ""

    player_1 = instructions_pl_1.split(" ")

    for instruction in player_1:

        if "@" in instruction or "*" in instruction:
            ship, action = instruction.split(":")

            if not ship in ship_move_attack_1:
                move_attack_1.append(instruction)
                ship_move_attack_1 += "%s " % ship

        elif "lock" in instruction or "release" in instruction:
            lock_unlock_1.append(instruction)

        elif "scout" in instruction or "warship" in instruction or "excavator" in instruction:
            buy_1.append(instruction)


        elif "exit" in instruction:
            raise ValueError('stopping')

    buy_2 = []
    lock_unlock_2 = []
    move_attack_2 = []
    ship_move_attack_2 = ""

    player_2 = instructions_pl_2.split(" ")

    for instruction in player_2:

        if "@" in instruction or "*" in instruction:
            ship, action = instruction.split(":")

            if not ship in ship_move_attack_2:
                move_attack_2.append(instruction)
                ship_move_attack_2 += "%s " % ship

        elif "lock" in instruction or "release" in instruction:
            lock_unlock_2.append(instruction)

        elif "scout" in instruction or "warship" in instruction or "excavator" in instruction:
            buy_2.append(instruction)

        elif "exit" in instruction:
            raise ValueError('stopping')

    for buying_1 in buy_1:
        ship_name, ship_type = buying_1.split(":")
        buy_ships('player_1', ship_name, ship_type, game, ships_to_buy, ships_player_1, ships_player_2, boardgame)

    for buying_2 in buy_2:
        ship_name, ship_type = buying_2.split(":")
        buy_ships('player_2', ship_name, ship_type, game, ships_to_buy, ships_player_1, ships_player_2, boardgame)

    for un_locking_1 in lock_unlock_1:
        ship_name, state = un_locking_1.split(":")

        if ship_name in ships_player_1:
            if state == 'lock':
                lock(ship_name, game, ships_player_1, ships_player_2, asteroids)

            elif state == 'release':
                unlock(ship_name, game, ships_player_1, ships_player_2, asteroids)

    for un_locking_2 in lock_unlock_2:
        ship_name, state = un_locking_2.split(":")

        if ship_name in ships_player_2:
            if state == 'lock':
                lock(ship_name, game, ships_player_1, ships_player_2, asteroids)

            elif state == 'release':
                unlock(ship_name, game, ships_player_1, ships_player_2, asteroids)
    touched = ""
    for move_attack_1 in move_attack_1:
        ship_name, action = move_attack_1.split(":")

        if ship_name in ships_player_1:

            x, y = action[1:].split("-")
            x = int(x)
            y = int(y)

            if "*" in action:
                touched += attack(ships_player_1, ships_player_2, ship_name, game, (x, y))

            elif "@" in action:
                    move_ship('player_1', asteroids, ships_player_1, ships_player_2, ship_name, game, boardgame, (x, y),
                              size_line, size_column)

    for move_attack_2 in move_attack_2:
        ship_name, action = move_attack_2.split(":")

        if ship_name in ships_player_2:

            x, y = action[1:].split("-")
            x = int(x)
            y = int(y)

            if "*" in action:
                touched += attack(ships_player_1, ships_player_2, ship_name, game, (x, y))

            elif "@" in action:
                    move_ship('player_2', asteroids, ships_player_1, ships_player_2, ship_name, game, boardgame, (x, y),
                              size_line, size_column)

    return touched

def game_over(game, nb_tours_no_degats):
    """ Checks if the game is over

    Parameter
    ---------
    game : dictionary of the game (dict)
    nb_tours_no_degats : number of rows without degat (int)

    Return
    -------
    True or False (bool)

    specifications: Margaux Foulon
    Implementation : Margaux Foulon
    """
    if game['player_1']['portal']['life'] <= 0 or game['player_2']['portal']['life'] <= 0:
        return True
    elif nb_tours_no_degats == 200:
        return True
    else:
        return False

def create_boardgame(size_line, size_column):
    """ Creates the board game

    Parameter
    ---------
    size_line : number of lines (int)
    size_column : number of columns (int)

    Specification: Moussa El Hafid
    Implementation : Moussa El Hafid

    """

    boardgame = {}

    for line in range(1, size_line + 1):
        for column in range(1, size_column + 1):
            boardgame["%i,%i" % (line, column)] ="\u25A0"
    return boardgame


def show_board(ships_player_1, ships_player_2, boardgame, size_line, size_column, game, asteroids, nb_row,final_line_1,final_line_2):
    """ show the board after modifications, this function will be called at the end of every round

    Parameters
    ---------
    boardgame : dictionary of the board game (dict)
    size_line : number of lines (int)
    size_column : number of columns (int)
    game : dictionary of the game (dict)

    specifications : Moussa El Hafid
    implementation : Moussa El Hafid
    """

    place_portals(ships_player_1, ships_player_2, game, boardgame, nb_row)

    place_ships(ships_player_1, ships_player_2, game, boardgame)

    place_asteroids(asteroids, boardgame)

    for lines in range(1, size_line + 1):
        line = ""
        for columns in range(1, size_column + 1):
            line += boardgame["%i,%i" % (lines, columns)] + ' '
        final_line_1.append(line)




def show_player_info(ships_player_1, ships_player_2, boardgame, size_line, size_column, game, asteroids, nb_row,final_line_1,final_line_2):

    # -*- coding: utf-8 -*-
    current_length = 81
    ships_lines = []
    current_index = 0
    len_player_ships = []
    for player in game:
        len_player_ships.append(len(game[player]['ships']))

    current_max = -1
    for value in len_player_ships:
        if value > current_max or current_max == -1:
            current_max = value

    while current_index < current_max:
        ship_info_line = '|'
        for player in game:
            if current_index < len(list(game[player]['ships'])):
                ship = list(game[player]['ships'])[current_index]

                ship_type = game[player]['ships'][ship]['type']
                ship_ore = ''
                if ship_type.startswith('e'):
                    ship_type = "E" + ship_type[-2:]
                    ship_ore += '%.1f' % game[player]['ships'][ship]['capacity']
                elif ship_type.startswith('w'):
                    ship_type = "W"
                else:
                    ship_type = "S"

                ship_pos = str(game[player]['ships'][ship]['position'][0])

                ship_info_line += ' %s | %s |%s| %s | %s :' % \
                                  (ship + (' ' * (10 - len(ship))),
                                   ship_type + (' ' * (4 - len(ship_type))),
                                   ship_pos + (' ' * (8 - len(ship_pos))),
                                   str(game[player]['ships'][ship]['life']) + (
                                           ' ' * (4 - len(str(game[player]['ships'][ship]['life'])))),
                                   ship_ore + (' ' * (3 - len(ship_ore))))
            else:
                ship_info_line += '            |      |        |      |     :'

        ship_info_line = ship_info_line[:-1] + '|'
        ships_lines.append(ship_info_line)
        current_index += 1

    # Portal life line
    portal_line = '| '
    for player in game:
        portal_side_length = 40
        p_life = game[player]['portal']['life']
        offset = 0
        if p_life < 10:
            offset = 2
            if p_life < 0:
                offset = 1
        elif p_life < 100:
            offset = 1
        portal_line += 'Portal life : %d%s  ' % (p_life, ' ' * (portal_side_length - (19 - offset)))

        if list(game).index(player) == 0:
            portal_line += ': '
        else:
            portal_line += '|'

    # Current Ore & Total Ore line
    ore_line = '| '
    for player in game:
        ore_side_length = 40
        current_ore = game[player]['ore']
        offset_ore = 0

        if current_ore < 10:
            offset_ore = 2
        elif current_ore < 100:
            offset_ore = 1

        ore_line += 'Current Ore : %d%s  ' % (current_ore, ' ' * (ore_side_length - (19 - offset_ore)))

        if list(game.keys()).index(player) == 0:
            ore_line += ': '

        else:
            ore_line += '|'

    final_line_2.append('=' * 85)
    final_line_2.append('|                Player 1                 :                Player 2                 |')
    final_line_2.append('=' * 85)
    final_line_2.append(portal_line)
    final_line_2.append(ore_line)

    final_line_2.append('-' * 85)
    final_line_2.append('| Name       | Type | Pos    | Life | Ore : Name       | Type | Pos    | Life | Ore |')
    for ship_line in ships_lines:
        final_line_2.append(ship_line)

    asteroid_lines = []

    ast_nb = 0
    asteroid_line = '|'
    for asteroid in asteroids:
        ast_nb += 1

        asteroid_info = '(%d,%d): %d' % (asteroids[asteroid]['position'][0], asteroids[asteroid]['position'][1], asteroids[asteroid]['ores'])
        asteroid_line += ' %s%s |' % (asteroid_info, ' ' * (11 - len(asteroid_info)))
        if ast_nb == 6:
            asteroid_lines.append(asteroid_line)
            asteroid_line = "|"
        if ast_nb == 12:
            asteroid_lines.append(asteroid_line)
            asteroid_line = "|"
        if ast_nb == 18:
            asteroid_lines.append(asteroid_line)
            asteroid_line = "|"
        elif ast_nb == len(list(asteroids)):
            asteroid_lines.append(asteroid_line)




    final_line_2.append('%s' % ('=' * 85))
    final_line_2.append('|%sAsteroids%s|' % ((' ' * 37), (' ' * 37)))
    final_line_2.append('%s' % ('-' * 85))
    for a_line in asteroid_lines:
        final_line_2.append(a_line)

    final_line_2.append("=====================================================================================")


def show_the_board(ships_player_1, ships_player_2, boardgame, size_line, size_column, game, asteroids, nb_row,final_line_1,final_line_2):

    show_board(ships_player_1, ships_player_2, boardgame, size_line, size_column, game, asteroids, nb_row,
                   final_line_1, final_line_2)

    show_player_info(ships_player_1, ships_player_2, boardgame, size_line, size_column, game, asteroids, nb_row,
                   final_line_1, final_line_2)

    final_line = ""
    if size_column > 50:
        for i in range(len(final_line_1)):
            final_line += final_line_1[i] + "\n"

        for j in range(len(final_line_2)):
            final_line += final_line_2[j] + "\n"

        print(final_line)
    else:

        while len(final_line_1) < len(final_line_2):
            final_line_1.append(" " * 158)

        while len(final_line_1) > len(final_line_2):
            final_line_2.append(" " * 81)

        for i in range (len(final_line_1)):
            final_line += final_line_1[i] + " " +final_line_2[i]+ "\n"
        print(final_line)


def whatdoyouwant():
    """asks the player what he wants to do

    Return
    ------
    instructions : what the player wants to do (list)

    specifications : Thomas Mestre
    Implementation : Thomas Mestre"""

    instructions = input("What do you want to do ?")

    return instructions


def buy_ships(player, ship_name, ship_type, game, ships_to_buy, ships_player_1, ships_player_2, boardgame):
    """Buy a ship and give it a name


    Parameters
    ----------
    player : player who buys the ship (str)
    ship_name : name to give to the ship (str)
    ship_type : type of the ship you want to buy (str)
    game : dictionary to add the ship (dict)
    ships_to_buy: dictionary of ships you can buy (dict)
    ships_player_1 : list of ships of the player 1 (list)
    ships_player_2 : list of ships of the player 2 (list)
    boardgame : dictionary of the boardgame (dict)

    specifications : Thomas Mestre
    implementation : Moussa El Hafid"""

    if ships_to_buy[ship_type]['cost'] < game[player]['ore']:

        game[player]['ore'] -= ships_to_buy[ship_type]['cost']

        if player == 'player_1':
            ships_player_1.append(ship_name)

        elif player == 'player_2':
            ships_player_2.append(ship_name)

        position = game[player]['portal']['position'][0]

        game[player]['ships'][ship_name] = ships_to_buy[ship_type].copy()

        game[player]['ships'][ship_name]['position'] = [(position)]

        all_position(ships_player_1, ships_player_2, game, ship_name)


    elif ships_to_buy[ship_type]['cost'] > game[player]['ore']:
        print("you don't have enough ore")


def lock(excavator_name, game, ships_player_1, ships_player_2, asteroids):
    """lock the excavator to an asteroid or a portal

    Parameters
    ----------
    excavator_name : name of the extractor (str)

    specifications :Thomas Mestre
    implementation : Moussa El Hafid (V1.0 01/04/2018)
    implementation : Moussa El Hafid, Thomas Mestre (V2.0 08/04/2018)"""

    if excavator_name in ships_player_1:
        player = 'player_1'
    elif excavator_name in ships_player_2:
        player = 'player_2'

    if game[player]['ships'][excavator_name]['position'][0] == game[player]['portal']['position'][0] and \
            game[player]['ships'][excavator_name]['state'] == 'unlocked':
        game[player]['ships'][excavator_name]['state'] = 'locked'

    for asteroid_position in asteroids:

        if game[player]['ships'][excavator_name]['position'][0] == asteroids[asteroid_position]['position'] and \
                game[player]['ships'][excavator_name]['state'] == 'unlocked':
            game[player]['ships'][excavator_name]['state'] = 'locked'



def unlock(excavator_name, game, ships_player_1, ships_player_2, asteroids):
    """unlock the excavator

    Parameters
    ----------
    excavator_name : name of the extractor (str)
    game : dictionary of the game (dict)
    ships_player_1 : list of ships of the player 1 (list)
    ships_player_2 : list of ships of the player 2 (list)
    asteroids : dictionary of the asteroids (dict)


    specifications :Thomas Mestre
    implementation : Moussa El Hafid (V1.0 01/04/2018)
    implementation : Moussa El Hafid, Thomas Mestre (V2.0 08/04/2018)
    """
    if excavator_name in ships_player_1:
        player = 'player_1'
    elif excavator_name in ships_player_2:
        player = 'player_2'
    if "excavator" in game[player]['ships'][excavator_name]['type']:
        if game[player]['ships'][excavator_name]['position'][0] == game[player]['portal']['position'][0] and \
                game[player]['ships'][excavator_name]['state'] == 'locked':
            game[player]['ships'][excavator_name]['state'] = 'unlocked'

        for asteroid_position in asteroids:
            if game[player]['ships'][excavator_name]['position'][0] == asteroids[asteroid_position]['position'] and \
                    game[player]['ships'][excavator_name]['state'] == 'locked':
                game[player]['ships'][excavator_name]['state'] = 'unlocked'


def attack(ships_player_1, ships_player_2, ship_name, game, position):
    """attack the position (abscissa,ordinate)

    Parameters
    -----------
    ships_player_1 : list of ships of the player 1 (list)
    ships_player_2 : list of ships of the player 2 (list)
    ship_name : the name of the ship who wants to attack (str)
    game : dictionary of the game data (dict)
    position : position to attack (tupl)

    specifications : Margaux Foulon
    implementation : Margaux Foulon, Moussa El Hafid
    """
    touched = ""

    if ship_name in ships_player_1:
        player = 'player_1'

    elif ship_name in ships_player_2:
        player = 'player_2'

    if check_reach(game, player, ship_name, position) == True:

        for ship_name_1 in game['player_1']['ships']:

            if position in game['player_1']['ships'][ship_name_1]['position']:
                game['player_1']['ships'][ship_name_1]['life'] -= game[player]['ships'][ship_name]['strength']
                touched += ship_name_1 + ","

        if position in game['player_1']['portal']['position']:
            game['player_1']['portal']['life'] -= game[player]['ships'][ship_name]['strength']
            touched += "portal player 1 "

        for ship_name_2 in game['player_2']['ships']:

            if position in game['player_2']['ships'][ship_name_2]['position']:
                game['player_2']['ships'][ship_name_2]['life'] -= game[player]['ships'][ship_name]['strength']
                touched += ship_name_2 + " "

        if position in game['player_2']['portal']['position']:
            game['player_2']['portal']['life'] -= game[player]['ships'][ship_name]['strength']
            touched += "portal player 2 "

        for player in game:

            for i in range(len(game[player]['ships']) - 1, -1, -1):
                ship = list(game[player]['ships'].keys())[i]
                if game[player]['ships'][ship]['life'] <= 0:
                    print('The ship %s has been destroyed.' % ship)
                    if player == 'player_1':
                        for ship_id, ship_name in enumerate(ships_player_1):
                            if ship_name == ship:
                                del ships_player_1[ship_id]
                    elif player == 'player_2':
                        for ship_id, ship_name in enumerate(ships_player_2):
                            if ship_name == ship:
                                del ships_player_2[ship_id]
                    del game[player]['ships'][ship]

    return touched


def all_position(ships_player_1, ships_player_2, game, ship_name='portal'):
    """ Add all the position of the ships/portals

    Parameters
    -----------
    ships_player_1 : list of ships of the player 1 (list)
    ships_player_2 : list of ships of the player 2 (list)
    game : dictionary that contains data of the game (dict)
    ship_name: name of the ship or portal by default (str)

    specification : Moussa El Hafid
    implementation : Moussa El Hafid
    """

    if ship_name == 'portal':
        for player_nr in range(1, 3):

            x = game['player_%i' % player_nr]['portal']['position'][0][0]
            y = game['player_%i' % player_nr]['portal']['position'][0][1]

            for pos_x in range(x - 2, x + 3):
                for pos_y in range(y - 2, y + 3):

                    if pos_x == x and pos_y == y:
                        None

                    else:
                        game['player_%i' % player_nr]['portal']['position'].append((pos_x, pos_y))

    else:
        if ship_name in ships_player_1:
            player = 'player_1'

        elif ship_name in ships_player_2:
            player = 'player_2'

        ship_type = game[player]['ships'][ship_name]['type']

        x = game[player]['ships'][ship_name]['position'][0][0]
        y = game[player]['ships'][ship_name]['position'][0][1]

        if ship_type == 'scout':
            for pos_x in range(x - 1, x + 2):
                for pos_y in range(y - 1, y + 2):
                    if pos_x == x and pos_y == y:
                        None

                    else:
                        game[player]['ships'][ship_name]['position'].append((pos_x, pos_y))

        elif ship_type == 'warship':
            for pos_x in range(x - 2, x + 3):
                for pos_y in range(y - 2, y + 3):
                    if pos_x == x and pos_y == y or pos_x == x + 2 and pos_y == y + 2 or pos_x == x - 2 and pos_y == y - 2 or pos_x == x + 2 and pos_y == y - 2 or pos_x == x - 2 and pos_y == y + 2:
                        None

                    else:
                        game[player]['ships'][ship_name]['position'].append((pos_x, pos_y))

        elif ship_type == 'excavator-S':
            None
        elif ship_type == 'excavator-M':
            game[player]['ships'][ship_name]['position'].append((x + 1, y))
            game[player]['ships'][ship_name]['position'].append((x - 1, y))
            game[player]['ships'][ship_name]['position'].append((x, y + 1))
            game[player]['ships'][ship_name]['position'].append((x, y - 1))

        elif ship_type == 'excavator-L':
            game[player]['ships'][ship_name]['position'].append((x + 1, y))
            game[player]['ships'][ship_name]['position'].append((x + 2, y))
            game[player]['ships'][ship_name]['position'].append((x - 1, y))
            game[player]['ships'][ship_name]['position'].append((x - 2, y))
            game[player]['ships'][ship_name]['position'].append((x, y + 1))
            game[player]['ships'][ship_name]['position'].append((x, y + 2))
            game[player]['ships'][ship_name]['position'].append((x, y - 1))
            game[player]['ships'][ship_name]['position'].append((x, y - 2))


def move_ship(player, asteroids, ships_player_1, ships_player_2, ship_name, game, boardgame, destination, size_line,
              size_column):
    """ Moves the ship

    Parameter
    ----------
    player : player who wants to move the ship (str)
    ships_player_1 : list of ships of the player 1 (list)
    ships_player_2 : list of ships of the player 2 (list)
    ship_name : ship to move (str)
    game : dictionary that contains game data (dict)
    gameboard : dictionary of the board (dict)
    line : line where to move (int)
    column : column where to move (int)

    specification : Moussa El Hafid
    implementation : Moussa El Hafid
    """

    ship_type = game[player]['ships'][ship_name]['type']

    if ship_type == 'excavator-S' or ship_type == 'excavator-M' or ship_type == 'excavator-L':
        if game[player]['ships'][ship_name]['state'] == 'locked':
            return 'you cannot move %s it is locked' % ship_name

    pos_x = game[player]['ships'][ship_name]['position'][0][0]
    pos_y = game[player]['ships'][ship_name]['position'][0][1]

    # check if the ship doesn't go out of the board

    if game[player]['ships'][ship_name]['type'] == 'scout' or game[player]['ships'][ship_name]['type'] == 'excavator-M':
        if destination[0] == 1 or destination[0] == size_line - 1 or destination[1] == 1 or destination[
            1] == size_column - 1:
            return ("you cannot move %s out of the board" % ship_name)

    elif game[player]['ships'][ship_name]['type'] == 'warship' or game[player]['ships'][ship_name][
        'type'] == 'excavator-L':
        if destination[0] <= 2 or destination[0] >= size_line - 1 or destination[1] <= 2 or destination[
            1] >= size_column - 1:
            return ("you cannot move %s out of the board" % ship_name)
    elif game[player]['ships'][ship_name]['type'] == 'excavator-S':
        if destination[0] <= 0 or destination[0] > size_line or destination[1] <= 0 or destination[1] > size_column:
            return ("you cannot move %s out of the board" % ship_name)

    # check if the player moves one case only

    if destination[0] in range(pos_x - 1, pos_x + 2) and destination[1] in range(pos_y - 1, pos_y + 2):

        for positions in game[player]['ships'][ship_name]['position']:
            boardgame["%i,%i" % (positions[0], positions[1])] = "\u25A0"

        del game[player]['ships'][ship_name]['position']

        game[player]['ships'][ship_name]['position'] = [destination]

        all_position(ships_player_1, ships_player_2, game, ship_name)

        return ('%s moved' % (ship_name))

    else:
        return ('you cannot move %s more than one case' % ship_name)


def place_ships(ships_player_1, ships_player_2, game, boardgame):
    """ Place the ship on the board

    Parameters
    -----------
    ships_player_1 : list of ships of the player 1 (list)
    ships_player_2 : list of ships of the player 2 (list)
    ship_name : name of the ship (str)
    game : dictionary that contains game data (dict)
    boardgame : dictionary of the board (dict)

    specification : Moussa El Hafid
    implementation : Moussa El Hafid
    """

    reset = attr('reset')

    # Place the ships on the board

    for player in game:
        if player == 'player_1':
            color = fg('red')

        elif player == 'player_2':
            color = fg('green')

        for ship in game[player]['ships']:

            for positions in game[player]['ships'][ship]['position']:
                boardgame["%i,%i" % (positions[0], positions[1])] = color + "\u25A0" + reset


def place_portals(ships_player_1, ships_player_2, game, boardgame, nb_row):
    """ Place the portals on the board

    Parameters
    -----------
    ships_player_1 : list of ships of the player 1 (list)
    ships_player_2 : list of ships of the player 2 (list)
    game : dictionary that contains game data (dict)
    boardgame : dictionary of the board (dict)

    specification : Moussa El Hafid
    implementation : Moussa El Hafid
    """
    if nb_row == 1:
        all_position(ships_player_1, ships_player_2, game)

    # Place the portals on the board

    for positions in game['player_1']['portal']['position']:
        boardgame["%i,%i" % (positions[0], positions[1])] = fg('dark_sea_green_5b') + "\u25A0" + attr('reset')

    for positions in game['player_2']['portal']['position']:
        boardgame["%i,%i" % (positions[0], positions[1])] = fg('magenta') + "\u25A0" + attr('reset')


def place_asteroids(asteroids, boardgame):
    """ Place the astroids on the board

    Parameters
    ----------
    asteroids : dictionary with the asteroids (dict)
    boardgame : boardgame : dictionary of the board (dict)

    specification : Moussa El Hafid
    implementation : Moussa El Hafid
    """
    reset = attr('reset')

    # Place the asteroids on the board

    for asteroid_nr in asteroids:
        positions = asteroids[asteroid_nr]['position']

        if asteroids[asteroid_nr]['ores'] > 0:
            boardgame["%i,%i" % (positions[0], positions[1])] = (fg('blue') + "\u25D8" + reset)
        else:
            boardgame["%i,%i" % (positions[0], positions[1])] = (fg('white') + "\u25D8" + reset)


def check_reach(game, player, ship_name, position):
    """Check if a ship can attack the position

    Parameters
    ----------
    player : player who play
    ship_name : name of the ship to take its position (str)
    position : position of the attack
    dictionary : dictionary to get position of the ship

    specifications : Margaux Foulon
    implementation : Margaux Foulon
    """

    x1 = position[0]
    x2 = position[1]
    y1 = game[player]['ships'][ship_name]['position'][0][0]
    y2 = game[player]['ships'][ship_name]['position'][0][1]

    # Compute distance of manhattan

    manhattan = abs(x1 - y1) + abs(x2 - y2)

    if manhattan <= game[player]['ships'][ship_name]['reach']:
        return True
    else:
        return False


def extract_ores(excavator_name, asteroid_name, asteroids, game, ships_player_1, ships_player_2):
    """ extract ores from the asteroid

    Parameters
    ----------
    excavator_name : name of the extractor (str)
    astéroid_name : name of the asteroid (str)
    asteroides : dictionary of the asteroid (dict)
    game : dictionary of the game (dict)

    specifications : Margaux Foulon
    implementation : Margaux Foulon
    """
    if excavator_name in ships_player_1:
        player = 'player_1'

    elif excavator_name in ships_player_2:
        player = 'player_2'

    if 'excavator' in game[player]['ships'][excavator_name]['type']:
        if game[player]['ships'][excavator_name]['state'] == 'locked':
            if asteroids[asteroid_name]['position'] == game[player]['ships'][excavator_name]['position'][0] and \
                    asteroids[asteroid_name]['ores'] > 0 and game[player]['ships'][excavator_name]['capacity'] < \
                    game[player]['ships'][excavator_name]['tonnage']:
                if game[player]['ships'][excavator_name]['capacity'] + asteroids[asteroid_name]['ores_per_turn'] <= \
                        game[player]['ships'][excavator_name]['tonnage']:
                    take_out = 0

                elif game[player]['ships'][excavator_name]['capacity'] + asteroids[asteroid_name]['ores_per_turn'] > \
                        game[player]['ships'][excavator_name]['tonnage']:
                    take_out = game[player]['ships'][excavator_name]['capacity'] + asteroids[asteroid_name][
                        'ores_per_turn'] - game[player]['ships'][excavator_name]['tonnage']

                game[player]['ships'][excavator_name]['capacity'] += asteroids[asteroid_name]['ores_per_turn'] - abs(
                    take_out)
                asteroids[asteroid_name]['ores'] -= asteroids[asteroid_name]['ores_per_turn'] + abs(take_out)


def drop_ores(excavator_name, game, ships_player_1, ships_player_2):
    """drop the ores in the player portal

    Parameters
    ----------
    excavator_name : name of the extractor (str)
    astéroid_name : name of the asteroid (str)
    asteroides : dictionary of the asteroid (dict)
    game : dictionary of the game (dict)

    specifications : Margaux Foulon
    implementation : Margaux Foulon
    """

    if excavator_name in ships_player_1:
        player = 'player_1'

    elif excavator_name in ships_player_2:
        player = 'player_2'

    if 'excavator' in game[player]['ships'][excavator_name]['type']:
        if game[player]['ships'][excavator_name]['state'] == 'locked':
            if game[player]['portal']['position'][0] == game[player]['ships'][excavator_name]['position'][0]:
                game[player]['ore'] += game[player]['ships'][excavator_name]['capacity']
                game[player]['ships'][excavator_name]['capacity'] = 0



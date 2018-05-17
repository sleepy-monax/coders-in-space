from random import randint


def ai(player, game_data, config):
    """
    Calculate what the IA will do.

    Parameters:
    -----------
    player : tell the IA, which player she is (0 or 1) (int)
    config: dictionary with all game parameters (dic)
    game_data: dictionary with all data structure of the game (dic)

    Return:
    -------
    order: the orders of the IA (string)

    Version:
    --------
    spec: Ryan Rennoir V.1 (07/04/2018)
        Ryan Rennoir, Arnaud Schmetz V.2(06/05/2018)
    impl: Arnaud Schmetz V.1 (09/04/2018)
        Ryan Rennoir, Arnaud Schmetz V.2(06/05/2018)
    """
    orders = ''

    # Unpacking the data structure
    vessel_stats = game_data[0]
    player_estate = game_data[1]

    vessel_counter = {'excavator-S': 0, 'excavator-M': 0, 'excavator-L': 0, 'scout': 0, 'warship': 0}
    for vessel in vessel_stats[player]:
        v_stats = vessel_stats[player][vessel]
        vessel_type = v_stats[0]
        vessel_counter[vessel_type] += 1

    # shopping
    ore = player_estate[player]['ore_amount']
    vessel_name = 'vessel_%s' % randint(1, 10)

    if vessel_counter['excavator-M'] < 2 and ore >= 4:
        while vessel_name in player_estate[player]['vessel']:
            vessel_name += '%s' % randint(1, 10)

        orders += '%s:excavator-M ' % vessel_name

    elif vessel_counter['scout'] < 3 <= ore:
        while vessel_name in player_estate[player]['vessel']:
            vessel_name += '%s' % randint(1, 10)

        orders += '%s:scout ' % vessel_name

    elif vessel_counter['excavator-L'] < 1 and ore >= 4:
        while vessel_name in player_estate[player]['vessel']:
            vessel_name += '%s' % randint(1, 10)

        orders += '%s:excavator-L ' % vessel_name

    elif vessel_counter['warship'] < 2 and ore >= 9:
        while vessel_name in player_estate[player]['vessel']:
            vessel_name += '%s' % randint(1, 10)

        orders += '%s:warship ' % vessel_name

    elif player_estate[player]['vessel'] == [] and ore == 1:
        while vessel_name in player_estate[player]['vessel']:
            vessel_name += '%s' % randint(1, 10)

        orders += '%s:excavator-S ' % vessel_name

    if len(vessel_stats[player]) != 0:

        attacker = {}
        excavator = {}

        for ships in vessel_stats[player]:
            ships_data = vessel_stats[player][ships]

            if ships_data[0] in ('scout', 'warship'):
                attacker.update({ships: ships_data})
            else:
                excavator.update({ships: ships_data})

        # lock / release and/or move for excavator
        orders = ai_mining(player, excavator, game_data, config, orders)

        # attack/move for attackers
        if player == 1:
            enemy = 0
        else:
            enemy = 1

        if vessel_stats[enemy]:
            orders = ai_attack(player, attacker, excavator, game_data, config, orders)

    return orders


def ai_attack(player, attacker, excavator, game_data, config, orders):
    """
    Calculate what the IA will do with the vessel capable of attacking.

    Parameters:
    -----------
    player : tell the IA, which player she is (0 or 1) (int)
    attacker: dictionary wih all attacker stats (dic)
    excavator: dictionary with all excavator stats (dic)
    game_data: list with all data structure (list)
    config: dictionary with all game parameters (dic)
    orders: orders of the ai (str)

    Return:
    -------
    orders: the orders of the IA (string)

    Version:
    --------
    spec: Ryan Rennoir V.1 (07/04/2018)
        Ryan Rennoir, Arnaud Schmetz V.2(06/05/2018)
    impl: Arnaud Schmetz V.1 (09/04/2018)
        Ryan Rennoir, Arnaud Schmetz V.2(06/05/2018)
    """
    vessel_stats = game_data[0]
    player_estate = game_data[1]

    if player == 1:
        enemy_player = 0
    else:
        enemy_player = 1

    # Main loop trough vessel
    for attacker_name, attacker_stats in attacker.items():
        order_attack_ia = ''

        vessel_type = attacker_stats[0]
        vessel_center = attacker_stats[1]
        vessel_distance = []
        v_range = config[vessel_type][1]

        if vessel_stats[enemy_player]:
            # Compute the enemy distance
            for enemy in vessel_stats[enemy_player]:
                enemy_data = vessel_stats[enemy_player][enemy]
                coord = enemy_data[1]

                # Measures the Manhattan distance(|row_b - row_a| + |column_b - column_a|)
                delta = abs(coord[0] - vessel_center[0]) + abs(coord[1] - vessel_center[1])

                vessel_distance.append([enemy, delta])

            # Find the closest vessel
            closest = min(vessel_distance)
            vessel_index = vessel_distance.index(closest)
            vessel_name = vessel_distance[vessel_index][0]

            # Compute the base distance
            enemy_base = player_estate[enemy_player]['base']
            delta_base = abs(enemy_base[0] - vessel_center[0]) + abs(enemy_base[1] - vessel_center[1])

            # Enemy target coordinate
            enemy_center = vessel_stats[enemy_player][vessel_name][1]
            coord_enemy_r = enemy_center[0]
            coord_enemy_c = enemy_center[1]

            # Check if the base is attacked
            base_attacked = False
            defend_base = ''
            for base_attacker in vessel_stats[enemy_player]:
                base_attacker_stats = vessel_stats[enemy_player][base_attacker]
                base = player_estate[player]['base']
                enemy_coord = base_attacker_stats[1]

                delta_b_attack = abs(base[0] - enemy_coord[0]) + abs(base[1] - enemy_coord[1])

                if delta_b_attack <= 5:
                    # Vessel in the secure zone
                    base_attacked = True
                    delta_target = abs(vessel_center[0] - enemy_coord[0]) + abs(vessel_center[1] - enemy_coord[1])

                    if delta_target <= v_range:
                        # Vessel in range: attack
                        defend_base = '%s:*%s-%s ' % (attacker_name, enemy_coord[0], enemy_coord[0])

                    else:
                        # Vessel out of range: move
                        defend_base = '%s:@%s-%s ' % (attacker_name, enemy_coord[0], enemy_coord[1])

            # Check if an excavator is attacked
            excavator_attacked = False
            defend_excavator = ''

            for enemy_vessel in vessel_stats[enemy_player]:
                enemy_vessel_data = vessel_stats[enemy_player][enemy_vessel]
                enemy_center = enemy_vessel_data[1]
                for excavator_name, excavator_stats in excavator.items():
                    excavator_coord = excavator_stats[1]

                    _delta = abs(excavator_coord[0] - enemy_center[0]) + abs(excavator_coord[1] - enemy_center[1])

                    if _delta <= 5:
                        # Excavator can be attacked
                        excavator_attacked = True

                        if _delta <= v_range or vessel_center == enemy_base:
                            # Enemy in range of the vessel
                            defend_excavator = '%s:*%s-%s ' % (attacker_name, enemy_center[0], enemy_center[1])

                        else:
                            # Enemy out of range move to the enemy
                            defend_excavator = '%s:@%s-%s ' % (attacker_name, enemy_center[0], enemy_center[1])

            # Chose the right order
            if delta_base <= v_range:
                # Attack the base in range
                order_attack_ia += '%s:*%s-%s ' % (attacker_name, enemy_base[0], enemy_base[1])

            elif base_attacked:
                # Move or attack the vessel near the base
                order_attack_ia += defend_base

            elif excavator_attacked:
                # Move to the excavator or defend it
                order_attack_ia += defend_excavator

            elif v_range >= closest[1]:
                # Attack the closest enemy
                order_attack_ia += '%s:*%s-%s ' % (attacker_name, coord_enemy_r, coord_enemy_c)

            else:
                # Move to the enemy base or random move(1/10)
                random = randint(1, 10)

                if random == 1:
                    # Move random
                    direction_row = randint(1, 2)
                    direction_column = randint(1, 2)
                    case = config['general'][0]

                    # Random direction
                    if direction_row == 1:
                        vessel_center[0] += case
                    else:
                        vessel_center[0] -= case

                    if direction_column == 1:
                        vessel_center[1] += case
                    else:
                        vessel_center[1] -= case

                    order_attack_ia += '%s:@%s-%s ' % (attacker_name, vessel_center[0], vessel_center[1])

                else:
                    order_attack_ia += '%s:@%s-%s ' % (attacker_name, enemy_base[0], enemy_base[1])
        else:
            # Compute the base distance
            enemy_base = player_estate[enemy_player]['base']
            delta_base = abs(enemy_base[0] - vessel_center[0]) + abs(enemy_base[1] - vessel_center[1])

            if delta_base <= v_range:
                # Attack the base in range
                order_attack_ia += '%s:*%s-%s ' % (attacker_name, enemy_base[0], enemy_base[1])

            else:
                order_attack_ia += '%s:@%s-%s ' % (attacker_name, enemy_base[0], enemy_base[1])

        orders += order_attack_ia

    return orders


def ai_mining(player, excavator, game_data, config, orders):
    """
    Calculate what the IA will do with the vessel capable of mining.

    Parameters:
    -----------
    player : tell the IA, which player she is (0 or 1) (int)
    excavator: dictionary with all excavator stats (dic)
    game_data: dictionary with all data structure of the game (dic)
    config: dictionary with all game parameters (dic)
    orders: orders of the ai (str)

    Return:
    -------
    orders: the orders of the IA (string)

    Version:
    --------
    spec: Ryan Rennoir V.1 (07/04/2018)
        Ryan Rennoir, Arnaud Schmetz V.2(06/05/2018)
    impl: Arnaud Schmetz V.1 (09/04/2018)
        Ryan Rennoir, Arnaud Schmetz V.2(06/05/2018)
    """
    player_estate = game_data[1]
    final_coordinate = game_data[7]
    environment_stats = game_data[2]

    base = player_estate[player]['base']

    for excavator_name, excavator_stats in excavator.items():
        order_excavator_ia = ''

        vessel_type = excavator_stats[0]
        max_ore = config[vessel_type][2]
        ore = excavator_stats[3]
        v_center = excavator_stats[1]

        if max_ore == ore:

            if excavator_stats[4] == 'lock':
                # Release
                order_excavator_ia += '%s:release ' % excavator_name

                # Check if the vessel is already trying to move
                if excavator_name in final_coordinate[player]:

                    # Check if the target isn't the base
                    target_coordinate = final_coordinate[player][excavator_name]
                    if target_coordinate == base:
                        # Already going to base
                        order_excavator_ia += ''

                else:
                    # Go to base
                    order_excavator_ia += '%s:@%s-%s ' % (excavator_name, base[0], base[1])

            elif v_center == base:
                order_excavator_ia += '%s:lock ' % excavator_name

        elif ore == 0:

            target_asteroid = []

            for asteroid in environment_stats['asteroid']:

                coord_asteroid = asteroid[0]

                # Chose a asteroid with ore
                if asteroid[1] != 0:
                    asteroid_index = environment_stats['asteroid'].index(asteroid)

                    # Compute the distance
                    distance = abs(coord_asteroid[0] - v_center[0]) + abs(coord_asteroid[1] - v_center[1])
                    target_asteroid.append([asteroid_index, distance])

            if len(target_asteroid) != 0:
                closest_asteroids = []

                for asteroids in target_asteroid:
                    closest_asteroids.append(asteroids[1])

                closest_distance = min(closest_asteroids)
                closest = closest_asteroids.index(closest_distance)
                asteroid_stats = environment_stats['asteroid'][closest]
                coord_asteroid = asteroid_stats[0]
                ore_asteroid = asteroid_stats[1]

                if v_center == base:
                    if excavator_stats[4] == 'lock':
                        order_excavator_ia += '%s:release ' % excavator_name

                    if excavator_name not in final_coordinate[player]:
                        order_excavator_ia += '%s:@%s-%s ' % (excavator_name, coord_asteroid[0], coord_asteroid[1])

                elif v_center == coord_asteroid:

                    if ore_asteroid > 0:
                        order_excavator_ia += '%s:lock ' % excavator_name

        else:
            if v_center == base:
                order_excavator_ia += '%s:lock ' % excavator_name

            else:
                for asteroid in environment_stats['asteroid']:
                    if v_center == asteroid[0] and asteroid[1] == 0:
                        order_excavator_ia += '%s:release ' % excavator_name

                order_excavator_ia += '%s:@%s-%s ' % (excavator_name, base[0], base[1])

        orders += order_excavator_ia

    return orders

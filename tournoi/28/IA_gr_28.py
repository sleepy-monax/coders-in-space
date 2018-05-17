# -*- coding: utf-8 -*-
import time
import socket
import remote_play

def ia_orders (players_infos, ships_infos, general_infos, nb_ships_bought, player_id, enemy_id):
    """ Gives the IA's orders.
    
    Parameters:
    -----------
    players_infos: data structure with informations of the players (dict)
    
    ships_infos: data structure with all features of the five different types of ships (dict)
    
    general_infos: dictionary with size of the board, position of portals and asteroids (dict) 
    
    nb_ships_bought: number of ships bought by IA during the game (int)
    
    player_id: player_1 or player_2 (str)
    
    enemy_id: player_1 or player_2 (str)
    
    Returns:
    --------
    ia_orders: decision of the IA (str)
    
    nb_ships_bought: number of ships bought by IA during the game (int)
    
    Version
    -------
    specification: Grégoire de Sauvage (v.1, 12/04/18)
    implementation: Grégoire de Sauvage, Martin Grifnée, Florent Delwiche (v.1, 06/05/18)
    """
    orders_ia = ''
    nb_IA_ships = 0
    nb_ore = players_infos['player_%d'%player_id]['nb_ore']
    nb_deplacement = 0
     
    if players_infos['player_%d'%player_id]['ships'] == {}:
        nb_IA_ships = 0
    else:
        for ship in players_infos['player_%d'%player_id]['ships']:
            nb_IA_ships += 1
     
    #buy round
    nb_scout = 0
    nb_warship = 0
    nb_excavator_S = 0
    nb_excavator_M = 0
    nb_excavator_L = 0                                       
    total_ore = 0
    
    for nb_asteroid in general_infos['asteroids']:
        total_ore += general_infos['asteroids'][nb_asteroid][1]
    
    ore_per_player = total_ore/2
    
    if nb_IA_ships == 0:
        if ore_per_player >= 8:
            if players_infos['player_%d'%player_id]['nb_ore'] >=4:
                if orders_ia == '':
                    orders_ia += 'ship_%d:excavator-M ship_%d:excavator-M'%(nb_ships_bought, nb_ships_bought+1)
                else:
                    orders_ia += 'ship_%d:excavator-M ship_%d:excavator-M'%(nb_ships_bought, nb_ships_bought+1)
                nb_ships_bought += 2
                nb_IA_ships += 2
                nb_ore -= 2*ships_infos['excavator-M']['price']
        
        elif ore_per_player >= 4:
            if players_infos['player_%d'%player_id]['nb_ore'] >=4:
                if orders_ia == '':
                    orders_ia += 'ship_%d:excavator-M'%(nb_ships_bought)
                else:
                    orders_ia += 'ship_%d:excavator-M'%(nb_ships_bought)
                nb_ships_bought += 1
                nb_IA_ships += 1
                nb_ore -= ships_infos['excavator-M']['price']
            
    
    else:
        for name_ship in players_infos['player_%d'%player_id]['ships']:
            if players_infos['player_%d'%player_id]['ships'][name_ship]['type'] == 'scout':
                nb_scout += 1
            if players_infos['player_%d'%player_id]['ships'][name_ship]['type'] == 'warship':
                nb_warship += 1
            if players_infos['player_%d'%player_id]['ships'][name_ship]['type'] == 'excavator-S':
                nb_excavator_S += 1
            if players_infos['player_%d'%player_id]['ships'][name_ship]['type'] == 'excavator-M':
                nb_excavator_M += 1
            if players_infos['player_%d'%player_id]['ships'][name_ship]['type'] == 'excavator-L':
                nb_excavator_L += 1
    
        nb_excavator = nb_excavator_S + nb_excavator_M + nb_excavator_L
        purchase = True 
        if nb_excavator != 0:
            while purchase == True:
                if ore_per_player/nb_excavator > 8 or ore_per_player == 0:
                    if nb_excavator_M >= 2:
                        if nb_scout == 0:         
                            if nb_ore >=3:
                                if orders_ia == '':
                                    orders_ia += 'ship_%d:scout'%(nb_ships_bought)
                                else:
                                    orders_ia +=' ship_%d:scout'%(nb_ships_bought)
                                nb_scout += 1
                                nb_ships_bought += 1
                                nb_IA_ships += 1
                                nb_ore -= ships_infos['scout']['price']
                            else:
                                purchase = False            
                    if nb_scout == 1:
                        if nb_ore >=3:
                            if orders_ia == '':
                                orders_ia += 'ship_%d:excavator-M'%(nb_ships_bought)
                            else:
                                orders_ia += ' ship_%d:excavator-M'%(nb_ships_bought)
                            nb_excavator_M += 1
                            nb_ships_bought += 1
                            nb_IA_ships += 1
                            nb_ore -= ships_infos['excavator-M']['price']
                        else:
                            purchase = False
                        
                else:
                    if nb_ore >= 9:
                        if orders_ia == '':
                            orders_ia += 'ship_%d:warship'%(nb_ships_bought)
                        else:
                            orders_ia += ' ship_%d:warship'%(nb_ships_bought)
                        nb_warship += 1
                        nb_ships_bought += 1
                        nb_IA_ships += 1
                        nb_ore -= ships_infos['warship']['price']
                    else:
                        purchase = False
    
    list_orders = orders_ia.split(' ')
    position_portal = general_infos['portals']['player_%d'%player_id]
    for orders in list_orders:
        nb_deplacement = 0
        if orders != '':
            ship, order = orders.split(':')
            if 'excavator' in order:
                closest_asteroid = []
                for ast_ind in range (0,len(general_infos['asteroids'].keys())):
                    asteroid = str(ast_ind + 1)
                    if general_infos['asteroids'][asteroid][1] == 0:
                        closest_asteroid.append(999)
                    else:
                        manathan_distance_ship = abs(position_portal[0]-general_infos['asteroids'][asteroid][0][0])+abs(position_portal[1]-general_infos['asteroids'][asteroid][0][1])
                        closest_asteroid.append(manathan_distance_ship)                                        
                    
                asteroid_index = closest_asteroid.index(min(closest_asteroid))
                asteroid_id = str(asteroid_index + 1)
                asteroid_pos = general_infos['asteroids'][asteroid_id][0]
                    
                #If they aren't on the same line and column
                if position_portal[0] != asteroid_pos[0] and position_portal[1] != asteroid_pos[1]:
                    if position_portal[0] > asteroid_pos[0]:
                        if position_portal[1] > asteroid_pos[1]:
                            orders_ia += ' %s:@%d-%d'%(ship, position_portal[0]-1, position_portal[1]-1)
                        else:
                            orders_ia += ' %s:@%d-%d'%(ship, position_portal[0]-1, position_portal[1]+1)
                    else:
                        if position_portal[1] > asteroid_pos[1]:
                            orders_ia += ' %s:@%d-%d'%(ship, position_portal[0]+1, position_portal[1]-1)
                        else:
                            orders_ia += ' %s:@%d-%d'%(ship, position_portal[0]+1, position_portal[1]+1)
                #If they aren't on the same line but on the same column
                elif position_portal[0] != asteroid_pos[0] and position_portal[1] == asteroid_pos[1]:
                    if position_portal[0] > asteroid_pos[0]:
                        orders_ia += ' %s:@%d-%d'%(ship, position_portal[0]-1, position_portal[1])
                    else:
                        orders_ia += ' %s:@%d-%d'%(ship, position_portal[0]+1, position_portal[1])
                #If they aren't on the same column but on the same line
                elif position_portal[0] == asteroid_pos[0] and position_portal[1] != asteroid_pos[1]:
                    if position_portal[1] > asteroid_pos[1]:
                        orders_ia += ' %s:@%d-%d'%(ship, position_portal[0], position_portal[1]-1)
                    else:
                        orders_ia += ' %s:@%d-%d'%(ship, position_portal[0], position_portal[1]+1)
            else:
                enemy_portal = general_infos['portals']['player_%d'%enemy_id]
                if position_portal[0] != enemy_portal[0] and position_portal[1] != enemy_portal[1]:
                    if position_portal[0] > enemy_portal[0]:
                        if position_portal[1] > enemy_portal[1]:
                            orders_ia += ' %s:@%d-%d'%(ship, position_portal[0]-1, position_portal[1]-1)
                        else:
                            orders_ia += ' %s:@%d-%d'%(ship, position_portal[0]-1, position_portal[1]+1)
                    else:
                        if position_portal[1] > enemy_portal[1]:
                            orders_ia += ' %s:@%d-%d'%(ship, position_portal[0]+1, position_portal[1]-1)
                        else:
                            orders_ia += ' %s:@%d-%d'%(ship, position_portal[0]+1, position_portal[1]+1)
                #If they aren't on the same line but on the same column
                elif position_portal[0] != enemy_portal[0] and position_portal[1] == enemy_portal[1]:
                    if position_portal[0] > enemy_portal[0]:
                        orders_ia += ' %s:@%d-%d'%(ship, position_portal[0]-1, position_portal[1])
                    else:
                        orders_ia += ' %s:@%d-%d'%(ship, position_portal[0]+1, position_portal[1])
                #If they aren't on the same column but on the same line
                elif position_portal[0] == enemy_portal[0] and position_portal[1] != enemy_portal[1]:
                    if position_portal[1] > enemy_portal[1]:
                        orders_ia += ' %s:@%d-%d'%(ship, position_portal[0], position_portal[1]-1)
                    else:
                        orders_ia += ' %s:@%d-%d'%(ship, position_portal[0], position_portal[1]+1)                       
 
    if nb_IA_ships > 0:

        for ship in players_infos['player_%d'%player_id]['ships']:
            ship_infos = players_infos['player_%d'%player_id]['ships'][ship]
            nb_deplacement = 0          
            
            if orders_ia == '':
                #Lock and release round
                if 'excavator' in ship_infos['type']:
                    if ship_infos['lock'] == 'no':
                        for asteroid in general_infos['asteroids']:
                            if ship_infos['nb_ore'] != ship_infos['tonnage']:
                                if  ship_infos['position'] == general_infos['asteroids'][asteroid][0] and general_infos['asteroids'][asteroid][1] > 0:
                                    orders_ia += '%s:lock'%ship
                        
                        if  ship_infos['position'] == general_infos['portals']['player_%d'%player_id]:
                            if ship_infos['nb_ore'] > 0:         
                                orders_ia += '%s:lock'%ship
                     
                    if ship_infos['lock'] == 'yes':
                        for asteroid in general_infos['asteroids']:
                            if  ship_infos['position'] == general_infos['asteroids'][asteroid][0]:
                                if  ship_infos['nb_ore'] == ship_infos['tonnage'] and general_infos['asteroids'][asteroid][1] > 0:
                                    orders_ia += '%s:release'%ship
                                elif general_infos['asteroids'][asteroid][1] == 0:
                                    orders_ia += '%s:release'%ship
                        if  ship_infos['position'] == general_infos['portals']['player_%d'%player_id]:
                            if ship_infos['nb_ore'] == 0:    
                                orders_ia += '%s:release'%ship
            #Orders with a space                                        
            else:
                if 'excavator' in ship_infos['type']:
                    if ship_infos['lock'] == 'no':
                        for asteroid in general_infos['asteroids']:
                            if ship_infos['nb_ore'] != ship_infos['tonnage']:
                                if  ship_infos['position'] == general_infos['asteroids'][asteroid][0] and general_infos['asteroids'][asteroid][1] > 0:
                                    orders_ia += ' %s:lock'%ship
                        
                        if  ship_infos['position'] == general_infos['portals']['player_%d'%player_id]:
                            if ship_infos['nb_ore'] > 0:         
                                orders_ia += ' %s:lock'%ship
                     
                    if ship_infos['lock'] == 'yes':
                        for asteroid in general_infos['asteroids']:
                            if  ship_infos['position'] == general_infos['asteroids'][asteroid][0]:
                                if  ship_infos['nb_ore'] == ship_infos['tonnage'] and general_infos['asteroids'][asteroid][1] > 0:
                                    orders_ia += ' %s:release'%ship
                                elif general_infos['asteroids'][asteroid][1] == 0:
                                    orders_ia += ' %s:release'%ship
                        if  ship_infos['position'] == general_infos['portals']['player_%d'%player_id]:
                            if ship_infos['nb_ore'] == 0:    
                                orders_ia += ' %s:release'%ship    
            
            if orders_ia == '':
                #Excavators' deplace round
                if 'excavator' in ship_infos['type']:
                    if ship_infos['lock'] == 'no':        
                        if ship_infos['nb_ore'] > 0:
                            #If they aren't on the same line and column
                            if ship_infos['position'][0] != general_infos['portals']['player_%d'%player_id][0] and ship_infos['position'][1] != general_infos['portals']['player_%d'%player_id][1]:
                                if ship_infos['position'][0] > general_infos['portals']['player_%d'%player_id][0]:
                                    if ship_infos['position'][1] > general_infos['portals']['player_%d'%player_id][1]:
                                        orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1]-1)
                                    else:
                                        orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1]+1)
                                else:
                                    if ship_infos['position'][1] > general_infos['portals']['player_%d'%player_id][1]:
                                        orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1]-1)
                                    else:
                                        orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1]+1)
                            #If they aren't on the same line but on the same column
                            elif ship_infos['position'][0] != general_infos['portals']['player_%d'%player_id][0] and ship_infos['position'][1] == general_infos['portals']['player_%d'%player_id][1]:
                                if ship_infos['position'][0] > general_infos['portals']['player_%d'%player_id][0]:
                                    orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1])
                                else:
                                    orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1])
                            #If they aren't on the same column but on the same line
                            elif ship_infos['position'][0] == general_infos['portals']['player_%d'%player_id][0] and ship_infos['position'][1] != general_infos['portals']['player_%d'%player_id][1]:
                                if ship_infos['position'][1] > general_infos['portals']['player_%d'%player_id][1]:
                                    orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0], ship_infos['position'][1]-1)
                                else:
                                    orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0], ship_infos['position'][1]+1)
                
                        elif ship_infos['nb_ore'] == 0:
                            if ship_infos['lock'] == 'no':
                                closest_asteroid = []
                                for ast_ind in range (0,len(general_infos['asteroids'].keys())):
                                    asteroid = str(ast_ind + 1)
                                    if general_infos['asteroids'][asteroid][1] == 0:
                                        closest_asteroid.append(999)
                                    else:
                                        manathan_distance_ship = abs(ship_infos['position'][0]-general_infos['asteroids'][asteroid][0][0])+abs(ship_infos['position'][1]-general_infos['asteroids'][asteroid][0][1])
                                        closest_asteroid.append(manathan_distance_ship)                                        
                                
                                asteroid_index = closest_asteroid.index(min(closest_asteroid))    
                                asteroid_id = str(asteroid_index + 1)
                                asteroid_pos = general_infos['asteroids'][asteroid_id][0]
                                
                                if nb_deplacement == 0:
                                    #If they aren't on the same line and column
                                    if ship_infos['position'][0] != asteroid_pos[0] and ship_infos['position'][1] != asteroid_pos[1]:
                                        if ship_infos['position'][0] > asteroid_pos[0]:
                                            if ship_infos['position'][1] > asteroid_pos[1]:
                                                orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1]-1)
                                                nb_deplacement += 1
                                            else:
                                                orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1]+1)
                                                nb_deplacement += 1
                                        else:
                                            if ship_infos['position'][1] > asteroid_pos[1]:
                                                orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1]-1)
                                                nb_deplacement += 1
                                            else:
                                                orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1]+1)
                                                nb_deplacement += 1
                                    #If they aren't on the same line but on the same column
                                    elif ship_infos['position'][0] != asteroid_pos[0] and ship_infos['position'][1] == asteroid_pos[1]:
                                        if ship_infos['position'][0] > asteroid_pos[0]:
                                            orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1])
                                            nb_deplacement += 1
                                        else:
                                            orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1])
                                            nb_deplacement += 1
                                    #If they aren't on the same column but on the same line
                                    elif ship_infos['position'][0] == asteroid_pos[0] and ship_infos['position'][1] != asteroid_pos[1]:
                                        if ship_infos['position'][1] > asteroid_pos[1]:
                                            orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0], ship_infos['position'][1]-1)
                                            nb_deplacement += 1
                                        else:
                                            orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0], ship_infos['position'][1]+1)
                                            nb_deplacement += 1
                
                     
            else:
                if 'excavator' in ship_infos['type']:        
                #Excavators' deplace round
                    if ship_infos['lock'] == 'no':        
                        if ship_infos['nb_ore'] > 0:
                            #If they aren't on the same line and column
                            if ship_infos['position'][0] != general_infos['portals']['player_%d'%player_id][0] and ship_infos['position'][1] != general_infos['portals']['player_%d'%player_id][1]:
                                if ship_infos['position'][0] > general_infos['portals']['player_%d'%player_id][0]:
                                    if ship_infos['position'][1] > general_infos['portals']['player_%d'%player_id][1]:
                                        orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1]-1)
                                    else:
                                        orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1]+1)
                                else:
                                    if ship_infos['position'][1] > general_infos['portals']['player_%d'%player_id][1]:
                                        orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1]-1)
                                    else:
                                        orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1]+1)
                            #If they aren't on the same line but on the same column
                            elif ship_infos['position'][0] != general_infos['portals']['player_%d'%player_id][0] and ship_infos['position'][1] == general_infos['portals']['player_%d'%player_id][1]:
                                if ship_infos['position'][0] > general_infos['portals']['player_%d'%player_id][0]:
                                    orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1])
                                else:
                                    orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1])
                            #If they aren't on the same column but on the same line
                            elif ship_infos['position'][0] == general_infos['portals']['player_%d'%player_id][0] and ship_infos['position'][1] != general_infos['portals']['player_%d'%player_id][1]:
                                if ship_infos['position'][1] > general_infos['portals']['player_%d'%player_id][1]:
                                    orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0], ship_infos['position'][1]-1)
                                else:
                                    orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0], ship_infos['position'][1]+1)
                
                        elif ship_infos['nb_ore'] == 0:
                            if ship_infos['lock'] == 'no':
                                closest_asteroid = []
                                for ast_ind in range (0,len(general_infos['asteroids'].keys())):
                                    asteroid = str(ast_ind + 1)
                                    if general_infos['asteroids'][asteroid][1] == 0:
                                        closest_asteroid.append(999)
                                    else:
                                        manathan_distance_ship = abs(ship_infos['position'][0]-general_infos['asteroids'][asteroid][0][0])+abs(ship_infos['position'][1]-general_infos['asteroids'][asteroid][0][1])
                                        closest_asteroid.append(manathan_distance_ship)                                        
                                
                                asteroid_index = closest_asteroid.index(min(closest_asteroid))    
                                asteroid_id = str(asteroid_index + 1)
                                asteroid_pos = general_infos['asteroids'][asteroid_id][0]
                                
                                if nb_deplacement == 0:
                                    #If they aren't on the same line and column
                                    if ship_infos['position'][0] != asteroid_pos[0] and ship_infos['position'][1] != asteroid_pos[1]:
                                        if ship_infos['position'][0] > asteroid_pos[0]:
                                            if ship_infos['position'][1] > asteroid_pos[1]:
                                                orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1]-1)
                                                nb_deplacement += 1
                                            else:
                                                orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1]+1)
                                                nb_deplacement += 1
                                        else:
                                            if ship_infos['position'][1] > asteroid_pos[1]:
                                                orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1]-1)
                                                nb_deplacement += 1
                                            else:
                                                orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1]+1)
                                                nb_deplacement += 1
                                    #If they aren't on the same line but on the same column
                                    elif ship_infos['position'][0] != asteroid_pos[0] and ship_infos['position'][1] == asteroid_pos[1]:
                                        if ship_infos['position'][0] > asteroid_pos[0]:
                                            orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1])
                                            nb_deplacement += 1
                                        else:
                                            orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1])
                                            nb_deplacement += 1
                                    #If they aren't on the same column but on the same line
                                    elif ship_infos['position'][0] == asteroid_pos[0] and ship_infos['position'][1] != asteroid_pos[1]:
                                        if ship_infos['position'][1] > asteroid_pos[1]:
                                            orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0], ship_infos['position'][1]-1)
                                            nb_deplacement += 1
                                        else:
                                            orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0], ship_infos['position'][1]+1)
                                            nb_deplacement += 1
                                                                     
            if orders_ia == '':
                
                if 'warship' in ship_infos['type'] or 'scout' in ship_infos['type']:
                    #Ships' attack and deplace round 
                    enemy_ships_names = []
                    closest_enemy_ship = []
                    if players_infos['player_%d'%enemy_id]['ships'] != {}:
                        for enemy_ships in players_infos['player_%d'%enemy_id]['ships']:
                            enemy_ships_names.append(enemy_ships)
                            ship_enemy_infos = players_infos['player_%d'%enemy_id]['ships'][enemy_ships]
                            manathan_ship = abs(ship_enemy_infos['position'][0]-ship_infos['position'][0]) + abs(ship_enemy_infos['position'][1]-ship_infos['position'][1])
                            closest_enemy_ship.append(manathan_ship)
                        
                        enemy_ship = enemy_ships_names[closest_enemy_ship.index(min(closest_enemy_ship))]
                        ship_1_infos = players_infos['player_%d'%enemy_id]['ships'][enemy_ship]
                        manathan_distance_ship = min(closest_enemy_ship)
                        
                    else:
                        manathan_distance_ship = 999
                    
                    
                    if nb_deplacement == 0:

                        manathan_distance_portal = abs(general_infos['portals']['player_%d'%enemy_id][0]-ship_infos['position'][0]) + abs(general_infos['portals']['player_%d'%enemy_id][1]-ship_infos['position'][1])
                        
                        #If an enemy ship or a portal is in range of ship attack 
                        if ship_infos['type'] == 'warship':
                            #Compute the reach of the warship and tells if the warship can make a shoot on enemy portal or ship
                            
                            warship_reach_position = [[ship_infos['position'][0]-5,ship_infos['position'][1]],[ship_infos['position'][0]-4,ship_infos['position'][1]+1],
                                                      [ship_infos['position'][0]-3,ship_infos['position'][1]+2],[ship_infos['position'][0]-2,ship_infos['position'][1]+3],
                                                      [ship_infos['position'][0]-1,ship_infos['position'][1]+4],[ship_infos['position'][0],ship_infos['position'][1]+5],
                                                      [ship_infos['position'][0]+5,ship_infos['position'][1]],[ship_infos['position'][0]+4,ship_infos['position'][1]+1],
                                                      [ship_infos['position'][0]+3,ship_infos['position'][1]+2],[ship_infos['position'][0]+2,ship_infos['position'][1]+3],
                                                      [ship_infos['position'][0]+1,ship_infos['position'][1]+4],[ship_infos['position'][0]+4,ship_infos['position'][1]-1],
                                                      [ship_infos['position'][0]+3,ship_infos['position'][1]-2],[ship_infos['position'][0]+2,ship_infos['position'][1]-3],
                                                      [ship_infos['position'][0]+1,ship_infos['position'][1]-4],[ship_infos['position'][0],ship_infos['position'][1]-5],
                                                      [ship_infos['position'][0]-4,ship_infos['position'][1]-1],[ship_infos['position'][0]-3,ship_infos['position'][1]-2],
                                                      [ship_infos['position'][0]-2,ship_infos['position'][1]-3],[ship_infos['position'][0]-1,ship_infos['position'][1]-4],
                                                      [ship_infos['position'][0]+4,ship_infos['position'][1]],[ship_infos['position'][0]+3,ship_infos['position'][1]],
                                                      [ship_infos['position'][0]+3,ship_infos['position'][1]-1],[ship_infos['position'][0]+3,ship_infos['position'][1]+1],
                                                      [ship_infos['position'][0]-4,ship_infos['position'][1]],[ship_infos['position'][0]-3,ship_infos['position'][1]],
                                                      [ship_infos['position'][0]-3,ship_infos['position'][1]-1],[ship_infos['position'][0]-3,ship_infos['position'][1]+1],
                                                      [ship_infos['position'][0],ship_infos['position'][1]+4],[ship_infos['position'][0],ship_infos['position'][1]+3],
                                                      [ship_infos['position'][0]-1,ship_infos['position'][1]+3],[ship_infos['position'][0]+1,ship_infos['position'][1]+3],
                                                      [ship_infos['position'][0],ship_infos['position'][1]-4],[ship_infos['position'][0],ship_infos['position'][1]-3],
                                                      [ship_infos['position'][0]-1,ship_infos['position'][1]-3],[ship_infos['position'][0]+1,ship_infos['position'][1]-3],
                                                      [ship_infos['position'][0]+2,ship_infos['position'][1]-2],[ship_infos['position'][0]-2,ship_infos['position'][1]-2],
                                                      [ship_infos['position'][0]-2,ship_infos['position'][1]+2],[ship_infos['position'][0]+2,ship_infos['position'][1]+2]]
                            
                            for position in range (0,len(warship_reach_position)):
                                for row in range (general_infos['portals']['player_%d'%enemy_id][0]-2,general_infos['portals']['player_%d'%enemy_id][0]+2):
                                    for column in range (general_infos['portals']['player_%d'%enemy_id][1]-2,general_infos['portals']['player_%d'%enemy_id][1]+2):
                                        enemy_portal_position = [row,column]
                                        
                                        if warship_reach_position[position] == enemy_portal_position and nb_deplacement == 0:
                                            orders_ia += '%s:*%d-%d'%(ship, warship_reach_position[position][0], warship_reach_position[position][1])
                                            nb_deplacement += 1
                                            
                            #Look at the type of enemy ship and compare center position and other parts position of enemy ship with warship reach positions
                            
                            if closest_enemy_ship != []:
                                if ship_1_infos['type'] == 'excavator-S':
             
                                    excavator_S = [ship_1_infos['position']]
                    
                                    for position in range (0,len(warship_reach_position)):
                     
                                        if warship_reach_position[position] == excavator_S[0] and nb_deplacement == 0:
                                            orders_ia += '%s:*%d-%d'%(ship, warship_reach_position[position][0], warship_reach_position[position][1])
                                            nb_deplacement += 1    
                        
                
                           
            
                                elif ship_1_infos['type'] == 'excavator-M': 
                
                                    excavator_M = [ship_1_infos['position'], [ship_1_infos['position'][0], ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] -1],
                                                    [ship_1_infos['position'][0] +1, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] -1, ship_1_infos['position'][1]]]
                 
                                    for position in range (0,len(warship_reach_position)):
                                        for enemy_position in range (0,len(excavator_M)): 
                                            if warship_reach_position[position] == excavator_M[enemy_position] and nb_deplacement == 0:
                                                orders_ia += '%s:*%d-%d'%(ship, warship_reach_position[position][0], warship_reach_position[position][1])
                                                nb_deplacement += 1    
                
                                elif ship_1_infos['type'] == 'excavator-L':
                
                                    excavator_L = [ship_1_infos['position'],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] +2],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] -1],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] -2],
                                                    [ship_1_infos['position'][0] +1, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] +2, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] -1, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] -2, ship_1_infos['position'][1]]]
                                
                                    for position in range (0,len(warship_reach_position)):
                                        for enemy_position in range (0,len(excavator_L)): 
                                            if warship_reach_position[position] == excavator_L[enemy_position] and nb_deplacement == 0:
                                                orders_ia += '%s:*%d-%d'%(ship, warship_reach_position[position][0], warship_reach_position[position][1])
                                                nb_deplacement += 1

            
                                elif ship_1_infos['type'] == 'scout': 
                 
                                    scout = [ship_1_infos['position'],
                                            [ship_1_infos['position'][0], ship_1_infos['position'][1] +1],
                                            [ship_1_infos['position'][0], ship_1_infos['position'][1] -1],
                                            [ship_1_infos['position'][0] +1, ship_1_infos['position'][1]],
                                            [ship_1_infos['position'][0] -1, ship_1_infos['position'][1]],
                                            [ship_1_infos['position'][0] +1, ship_1_infos['position'][1] +1],
                                            [ship_1_infos['position'][0] -1, ship_1_infos['position'][1] -1],
                                            [ship_1_infos['position'][0] +1, ship_1_infos['position'][1]-1],
                                            [ship_1_infos['position'][0] -1, ship_1_infos['position'][1]+1]]
                                    
                                    for position in range (0,len(warship_reach_position)):
                                        for enemy_position in range (0,len(scout)): 
                                            if warship_reach_position[position] == scout[enemy_position] and nb_deplacement == 0:
                                                orders_ia += '%s:*%d-%d'%(ship, warship_reach_position[position][0], warship_reach_position[position][1])
                                                nb_deplacement += 1

            
                                else: 
                    
                                    if ship_1_infos['type'] == 'warship':
                 
                                        warship = [ship_1_infos['position'],[ship_1_infos['position'][0], ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] -1],[ship_1_infos['position'][0] -1, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] +1, ship_1_infos['position'][1]],[ship_1_infos['position'][0] +1, ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0] -1, ship_1_infos['position'][1] -1],[ship_1_infos['position'][0] +1, ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0] -1, ship_1_infos['position'][1] -1],[ship_1_infos['position'][0], ship_1_infos['position'][1] +2],
                                                    [ship_1_infos['position'][0] +1, ship_1_infos['position'][1] +2],[ship_1_infos['position'][0] -1, ship_1_infos['position'][1] +2],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] -2],[ship_1_infos['position'][0] +1, ship_1_infos['position'][1] -2],
                                                    [ship_1_infos['position'][0] -1, ship_1_infos['position'][1] -2],[ship_1_infos['position'][0] +2, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] +2, ship_1_infos['position'][1] +1],[ship_1_infos['position'][0] +2, ship_1_infos['position'][1] -1],
                                                    [ship_1_infos['position'][0] -2, ship_1_infos['position'][1]],[ship_1_infos['position'][0] -2, ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0] -2, ship_1_infos['position'][1] -1]]
                        
                                        for position in range (0,len(warship_reach_position)):
                                            for enemy_position in range (0,len(warship)): 
                                                if warship_reach_position[position] == warship[enemy_position] and nb_deplacement == 0:
                                                    orders_ia += '%s:*%d-%d'%(ship, warship_reach_position[position][0], warship_reach_position[position][1])
                                                    nb_deplacement += 1
                    
                    if nb_deplacement == 0:    
                        
                        if closest_enemy_ship != []:    
                            enemy_ship = enemy_ships_names[closest_enemy_ship.index(min(closest_enemy_ship))]
                            ship_1_infos = players_infos['player_%d'%enemy_id]['ships'][enemy_ship]
                            manathan_distance_ship = min(closest_enemy_ship)
                        
                        manathan_distance_portal = abs(general_infos['portals']['player_%d'%enemy_id][0]-ship_infos['position'][0]) + abs(general_infos['portals']['player_%d'%enemy_id][1]-ship_infos['position'][1])
                        
                        if ship_infos['type'] == 'scout':
                            #Compute the reach of the scout and tells if the warship can make a shoot on enemy portal or ship (centers and parts of the ship)
                            
                            
                            scout_reach_position = [[ship_infos['position'][0]-3,ship_infos['position'][1]],[ship_infos['position'][0]-2,ship_infos['position'][1]+1],
                                                      [ship_infos['position'][0]-1,ship_infos['position'][1]+2],[ship_infos['position'][0],ship_infos['position'][1]+3],
                                                      [ship_infos['position'][0]+1,ship_infos['position'][1]+2],[ship_infos['position'][0]+2,ship_infos['position'][1]+1],
                                                      [ship_infos['position'][0]+3,ship_infos['position'][1]],[ship_infos['position'][0]+2,ship_infos['position'][1]-1],
                                                      [ship_infos['position'][0]+1,ship_infos['position'][1]-2],[ship_infos['position'][0],ship_infos['position'][1]-3],
                                                      [ship_infos['position'][0]-1,ship_infos['position'][1]-2],[ship_infos['position'][0]-2,ship_infos['position'][1]-1],
                                                      [ship_infos['position'][0]-2,ship_infos['position'][1]],[ship_infos['position'][0]+2,ship_infos['position'][1]],
                                                      [ship_infos['position'][0],ship_infos['position'][1]-2],[ship_infos['position'][0],ship_infos['position'][1]+2]]
                                                      
                            
                            #Look if the scout can reach a portal case
                            for position in range (0,len(scout_reach_position)):
                                for row in range (general_infos['portals']['player_%d'%enemy_id][0]-2,general_infos['portals']['player_%d'%enemy_id][0]+2):
                                    for column in range (general_infos['portals']['player_%d'%enemy_id][1]-2,general_infos['portals']['player_%d'%enemy_id][1]+2):
                                        enemy_portal_position = [row,column]
                                        
                                        if scout_reach_position[position] == enemy_portal_position and nb_deplacement == 0:
                                            orders_ia += '%s:*%d-%d'%(ship, scout_reach_position[position][0], scout_reach_position[position][1])
                                            nb_deplacement += 1
                                            
                            
                            if closest_enemy_ship != []:
                                #Look at the type of enemy ship and compare center position and other parts position of enemy ship with scout reach positions
                                if ship_1_infos['type'] == 'excavator-S':
             
                                    excavator_S = [ship_1_infos['position']]
                 
                                    for position in range (0,len(scout_reach_position)):
                        
                                        if scout_reach_position[position] == excavator_S[0] and nb_deplacement == 0:
                                            orders_ia += '%s:*%d-%d'%(ship, scout_reach_position[position][0], scout_reach_position[position][1])
                                            nb_deplacement += 1    
                        
                
                                elif ship_1_infos['type'] == 'excavator-M': 
             
                                    excavator_M = [ship_1_infos['position'], [ship_1_infos['position'][0], ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] -1],
                                                    [ship_1_infos['position'][0] +1, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] -1, ship_1_infos['position'][1]]]
                    
                                    for position in range (0,len(scout_reach_position)):
                                        for enemy_position in range (0,len(excavator_M)): 
                                            if scout_reach_position[position] == excavator_M[enemy_position] and nb_deplacement == 0:
                                                orders_ia += '%s:*%d-%d'%(ship, scout_reach_position[position][0], scout_reach_position[position][1])
                                                nb_deplacement += 1    
                
                                elif ship_1_infos['type'] == 'excavator-L':
                
                                    excavator_L = [ship_1_infos['position'],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] +2],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] -1],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] -2],
                                                    [ship_1_infos['position'][0] +1, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] +2, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] -1, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] -2, ship_1_infos['position'][1]]]
                                
                                    for position in range (0,len(scout_reach_position)):
                                        for enemy_position in range (0,len(excavator_L)): 
                                            if scout_reach_position[position] == excavator_L[enemy_position] and nb_deplacement == 0:
                                                orders_ia += '%s:*%d-%d'%(ship, scout_reach_position[position][0], scout_reach_position[position][1])
                                                nb_deplacement += 1

            
                                elif ship_1_infos['type'] == 'scout': 
                 
                                    scout = [ship_1_infos['position'],
                                            [ship_1_infos['position'][0], ship_1_infos['position'][1] +1],
                                            [ship_1_infos['position'][0], ship_1_infos['position'][1] -1],
                                            [ship_1_infos['position'][0] +1, ship_1_infos['position'][1]],
                                            [ship_1_infos['position'][0] -1, ship_1_infos['position'][1]],
                                            [ship_1_infos['position'][0] +1, ship_1_infos['position'][1] +1],
                                            [ship_1_infos['position'][0] -1, ship_1_infos['position'][1] -1],
                                            [ship_1_infos['position'][0] +1, ship_1_infos['position'][1]-1],
                                            [ship_1_infos['position'][0] -1, ship_1_infos['position'][1]+1]]
                                
                                    for position in range (0,len(scout_reach_position)):
                                        for enemy_position in range (0,len(scout)): 
                                            if scout_reach_position[position] == scout[enemy_position] and nb_deplacement == 0:
                                                orders_ia += '%s:*%d-%d'%(ship, scout_reach_position[position][0], scout_reach_position[position][1])
                                                nb_deplacement += 1

            
                                else: 
                 
                                    if ship_1_infos['type'] == 'warship':
                    
                                        warship = [ship_1_infos['position'],[ship_1_infos['position'][0], ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] -1],[ship_1_infos['position'][0] -1, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] +1, ship_1_infos['position'][1]],[ship_1_infos['position'][0] +1, ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0] -1, ship_1_infos['position'][1] -1],[ship_1_infos['position'][0] +1, ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0] -1, ship_1_infos['position'][1] -1],[ship_1_infos['position'][0], ship_1_infos['position'][1] +2],
                                                    [ship_1_infos['position'][0] +1, ship_1_infos['position'][1] +2],[ship_1_infos['position'][0] -1, ship_1_infos['position'][1] +2],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] -2],[ship_1_infos['position'][0] +1, ship_1_infos['position'][1] -2],
                                                    [ship_1_infos['position'][0] -1, ship_1_infos['position'][1] -2],[ship_1_infos['position'][0] +2, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] +2, ship_1_infos['position'][1] +1],[ship_1_infos['position'][0] +2, ship_1_infos['position'][1] -1],
                                                    [ship_1_infos['position'][0] -2, ship_1_infos['position'][1]],[ship_1_infos['position'][0] -2, ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0] -2, ship_1_infos['position'][1] -1]]
                     
                                        for position in range (0,len(scout_reach_position)):
                                            for enemy_position in range (0,len(warship)): 
                                                if scout_reach_position[position] == warship[enemy_position] and nb_deplacement == 0:
                                                    orders_ia += '%s:*%d-%d'%(ship, scout_reach_position[position][0], scout_reach_position[position][1])
                                                    nb_deplacement += 1
                        
                       
                       
                        manathan_distance_portal = abs(general_infos['portals']['player_%d'%enemy_id][0]-ship_infos['position'][0]) + abs(general_infos['portals']['player_%d'%enemy_id][1]-ship_infos['position'][1])
                        #If an enemy portal is nearer, ship attack goes to portal     
                        
                        if manathan_distance_portal <= manathan_distance_ship and nb_deplacement == 0:
                            
                            #If they aren't on the same line and column
                            if ship_infos['position'][0] != general_infos['portals']['player_%d'%enemy_id][0] and ship_infos['position'][1] != general_infos['portals']['player_%d'%enemy_id][1]:
                                if ship_infos['position'][0] > general_infos['portals']['player_%d'%enemy_id][0]:
                                    if ship_infos['position'][1] > general_infos['portals']['player_%d'%enemy_id][1]:
                                        orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1]-1)
                                        nb_deplacement += 1
                                    else:
                                        orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1]+1)
                                        nb_deplacement += 1
                                else:
                                    if ship_infos['position'][1] > general_infos['portals']['player_%d'%enemy_id][1]:
                                        orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1]-1)
                                        nb_deplacement += 1
                                    else:
                                        orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1]+1)
                                        nb_deplacement += 1
                            #If they aren't on the same line but on the same column
                            elif ship_infos['position'][0] != general_infos['portals']['player_%d'%enemy_id][0] and ship_infos['position'][1] == general_infos['portals']['player_%d'%enemy_id][1]:
                                if ship_infos['position'][0] > general_infos['portals']['player_%d'%enemy_id][0]:
                                    orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1])
                                    nb_deplacement += 1
                                else:
                                    orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1])
                                    nb_deplacement += 1
                            #If they aren't on the same column but on the same line
                            elif ship_infos['position'][0] == general_infos['portals']['player_%d'%enemy_id][0] and ship_infos['position'][1] != general_infos['portals']['player_%d'%enemy_id][1]:
                                if ship_infos['position'][1] > general_infos['portals']['player_%d'%enemy_id][1]:
                                    orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0], ship_infos['position'][1]-1)
                                    nb_deplacement += 1
                                else:
                                    orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0], ship_infos['position'][1]+1)
                                    nb_deplacement += 1
                        
                        
                        #If enemy ship is nearer, ship attack goes to enemy ship             
                        elif manathan_distance_portal > manathan_distance_ship and nb_deplacement == 0:
                            #If they aren't on the same line and column
                            if ship_infos['position'][0] != ship_1_infos['position'][0] and ship_infos['position'][1] != ship_1_infos['position'][1]:
                                if ship_infos['position'][0] > ship_1_infos['position'][0]:
                                    if ship_infos['position'][1] > ship_1_infos['position'][1]:
                                        orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1]-1)
                                        nb_deplacement += 1
                                    else:
                                        orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1]+1)
                                        nb_deplacement += 1
                                else:
                                    if ship_infos['position'][1] > ship_1_infos['position'][1]:
                                        orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1]-1)
                                        nb_deplacement += 1
                                    else:
                                        orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1]+1)
                                        nb_deplacement += 1
                            #If they aren't on the same line but on the same column
                            elif ship_infos['position'][0] != ship_1_infos['position'][0] and ship_infos['position'][1] == ship_1_infos['position'][1]:
                                if ship_infos['position'][0] > ship_1_infos['position'][0]:
                                    orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1])
                                    nb_deplacement += 1
                                else:
                                    orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1])
                                    nb_deplacement += 1
                            #If they aren't on the same column but on the same line
                            elif ship_infos['position'][0] == ship_1_infos['position'][0] and ship_infos['position'][1] != ship_1_infos['position'][1]:
                                if ship_infos['position'][1] > ship_1_infos['position'][1]:
                                    orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0], ship_infos['position'][1]-1)
                                    nb_deplacement += 1
                                else:
                                    orders_ia += '%s:@%d-%d'%(ship, ship_infos['position'][0], ship_infos['position'][1]+1)                                                        
                                    nb_deplacement += 1
            
            
            else:
                if 'warship' in ship_infos['type'] or 'scout' in ship_infos['type']:
                    #Ships' attack and deplace round 
                    enemy_ships_names = []
                    closest_enemy_ship = []
                    if players_infos['player_%d'%enemy_id]['ships'] != {}:
                        for enemy_ships in players_infos['player_%d'%enemy_id]['ships']:
                            enemy_ships_names.append(enemy_ships)
                            ship_enemy_infos = players_infos['player_%d'%enemy_id]['ships'][enemy_ships]
                            manathan_ship = abs(ship_enemy_infos['position'][0]-ship_infos['position'][0]) + abs(ship_enemy_infos['position'][1]-ship_infos['position'][1])
                            closest_enemy_ship.append(manathan_ship)
                        
                        enemy_ship = enemy_ships_names[closest_enemy_ship.index(min(closest_enemy_ship))]
                        ship_1_infos = players_infos['player_%d'%enemy_id]['ships'][enemy_ship]
                        manathan_distance_ship = min(closest_enemy_ship)
                        
                    else:
                        manathan_distance_ship = 999
                    
                    
                    if nb_deplacement == 0:

                        manathan_distance_portal = abs(general_infos['portals']['player_%d'%enemy_id][0]-ship_infos['position'][0]) + abs(general_infos['portals']['player_%d'%enemy_id][1]-ship_infos['position'][1])
                        
                        #If an enemy ship or a portal is in range of ship attack 
                        if ship_infos['type'] == 'warship':
                            #Compute the reach of the warship and tells if the warship can make a shoot on enemy portal or ship
                            
                            warship_reach_position = [[ship_infos['position'][0]-5,ship_infos['position'][1]],[ship_infos['position'][0]-4,ship_infos['position'][1]+1],
                                                      [ship_infos['position'][0]-3,ship_infos['position'][1]+2],[ship_infos['position'][0]-2,ship_infos['position'][1]+3],
                                                      [ship_infos['position'][0]-1,ship_infos['position'][1]+4],[ship_infos['position'][0],ship_infos['position'][1]+5],
                                                      [ship_infos['position'][0]+5,ship_infos['position'][1]],[ship_infos['position'][0]+4,ship_infos['position'][1]+1],
                                                      [ship_infos['position'][0]+3,ship_infos['position'][1]+2],[ship_infos['position'][0]+2,ship_infos['position'][1]+3],
                                                      [ship_infos['position'][0]+1,ship_infos['position'][1]+4],[ship_infos['position'][0]+4,ship_infos['position'][1]-1],
                                                      [ship_infos['position'][0]+3,ship_infos['position'][1]-2],[ship_infos['position'][0]+2,ship_infos['position'][1]-3],
                                                      [ship_infos['position'][0]+1,ship_infos['position'][1]-4],[ship_infos['position'][0],ship_infos['position'][1]-5],
                                                      [ship_infos['position'][0]-4,ship_infos['position'][1]-1],[ship_infos['position'][0]-3,ship_infos['position'][1]-2],
                                                      [ship_infos['position'][0]-2,ship_infos['position'][1]-3],[ship_infos['position'][0]-1,ship_infos['position'][1]-4],
                                                      [ship_infos['position'][0]+4,ship_infos['position'][1]],[ship_infos['position'][0]+3,ship_infos['position'][1]],
                                                      [ship_infos['position'][0]+3,ship_infos['position'][1]-1],[ship_infos['position'][0]+3,ship_infos['position'][1]+1],
                                                      [ship_infos['position'][0]-4,ship_infos['position'][1]],[ship_infos['position'][0]-3,ship_infos['position'][1]],
                                                      [ship_infos['position'][0]-3,ship_infos['position'][1]-1],[ship_infos['position'][0]-3,ship_infos['position'][1]+1],
                                                      [ship_infos['position'][0],ship_infos['position'][1]+4],[ship_infos['position'][0],ship_infos['position'][1]+3],
                                                      [ship_infos['position'][0]-1,ship_infos['position'][1]+3],[ship_infos['position'][0]+1,ship_infos['position'][1]+3],
                                                      [ship_infos['position'][0],ship_infos['position'][1]-4],[ship_infos['position'][0],ship_infos['position'][1]-3],
                                                      [ship_infos['position'][0]-1,ship_infos['position'][1]-3],[ship_infos['position'][0]+1,ship_infos['position'][1]-3],
                                                      [ship_infos['position'][0]+2,ship_infos['position'][1]-2],[ship_infos['position'][0]-2,ship_infos['position'][1]-2],
                                                      [ship_infos['position'][0]-2,ship_infos['position'][1]+2],[ship_infos['position'][0]+2,ship_infos['position'][1]+2]]
                            
                            for position in range (0,len(warship_reach_position)):
                                for row in range (general_infos['portals']['player_%d'%enemy_id][0]-2,general_infos['portals']['player_%d'%enemy_id][0]+2):
                                    for column in range (general_infos['portals']['player_%d'%enemy_id][1]-2,general_infos['portals']['player_%d'%enemy_id][1]+2):
                                        enemy_portal_position = [row,column]
                                        
                                        if warship_reach_position[position] == enemy_portal_position and nb_deplacement == 0:
                                            orders_ia += ' %s:*%d-%d'%(ship, warship_reach_position[position][0], warship_reach_position[position][1])
                                            nb_deplacement += 1
                                            
                            #Look at the type of enemy ship and compare center position and other parts position of enemy ship with warship reach positions
                            
                            if closest_enemy_ship != []:
                                if ship_1_infos['type'] == 'excavator-S':
             
                                    excavator_S = [ship_1_infos['position']]
                    
                                    for position in range (0,len(warship_reach_position)):
                     
                                        if warship_reach_position[position] == excavator_S[0] and nb_deplacement == 0:
                                            orders_ia += ' %s:*%d-%d'%(ship, warship_reach_position[position][0], warship_reach_position[position][1])
                                            nb_deplacement += 1    
                        
                
                           
            
                                elif ship_1_infos['type'] == 'excavator-M': 
                
                                    excavator_M = [ship_1_infos['position'], [ship_1_infos['position'][0], ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] -1],
                                                    [ship_1_infos['position'][0] +1, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] -1, ship_1_infos['position'][1]]]
                 
                                    for position in range (0,len(warship_reach_position)):
                                        for enemy_position in range (0,len(excavator_M)): 
                                            if warship_reach_position[position] == excavator_M[enemy_position] and nb_deplacement == 0:
                                                orders_ia += ' %s:*%d-%d'%(ship, warship_reach_position[position][0], warship_reach_position[position][1])
                                                nb_deplacement += 1    
                
                                elif ship_1_infos['type'] == 'excavator-L':
                
                                    excavator_L = [ship_1_infos['position'],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] +2],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] -1],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] -2],
                                                    [ship_1_infos['position'][0] +1, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] +2, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] -1, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] -2, ship_1_infos['position'][1]]]
                                
                                    for position in range (0,len(warship_reach_position)):
                                        for enemy_position in range (0,len(excavator_L)): 
                                            if warship_reach_position[position] == excavator_L[enemy_position] and nb_deplacement == 0:
                                                orders_ia += ' %s:*%d-%d'%(ship, warship_reach_position[position][0], warship_reach_position[position][1])
                                                nb_deplacement += 1

            
                                elif ship_1_infos['type'] == 'scout': 
                 
                                    scout = [ship_1_infos['position'],
                                            [ship_1_infos['position'][0], ship_1_infos['position'][1] +1],
                                            [ship_1_infos['position'][0], ship_1_infos['position'][1] -1],
                                            [ship_1_infos['position'][0] +1, ship_1_infos['position'][1]],
                                            [ship_1_infos['position'][0] -1, ship_1_infos['position'][1]],
                                            [ship_1_infos['position'][0] +1, ship_1_infos['position'][1] +1],
                                            [ship_1_infos['position'][0] -1, ship_1_infos['position'][1] -1],
                                            [ship_1_infos['position'][0] +1, ship_1_infos['position'][1]-1],
                                            [ship_1_infos['position'][0] -1, ship_1_infos['position'][1]+1]]
                                    
                                    for position in range (0,len(warship_reach_position)):
                                        for enemy_position in range (0,len(scout)): 
                                            if warship_reach_position[position] == scout[enemy_position] and nb_deplacement == 0:
                                                orders_ia += ' %s:*%d-%d'%(ship, warship_reach_position[position][0], warship_reach_position[position][1])
                                                nb_deplacement += 1

            
                                else: 
                    
                                    if ship_1_infos['type'] == 'warship':
                 
                                        warship = [ship_1_infos['position'],[ship_1_infos['position'][0], ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] -1],[ship_1_infos['position'][0] -1, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] +1, ship_1_infos['position'][1]],[ship_1_infos['position'][0] +1, ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0] -1, ship_1_infos['position'][1] -1],[ship_1_infos['position'][0] +1, ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0] -1, ship_1_infos['position'][1] -1],[ship_1_infos['position'][0], ship_1_infos['position'][1] +2],
                                                    [ship_1_infos['position'][0] +1, ship_1_infos['position'][1] +2],[ship_1_infos['position'][0] -1, ship_1_infos['position'][1] +2],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] -2],[ship_1_infos['position'][0] +1, ship_1_infos['position'][1] -2],
                                                    [ship_1_infos['position'][0] -1, ship_1_infos['position'][1] -2],[ship_1_infos['position'][0] +2, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] +2, ship_1_infos['position'][1] +1],[ship_1_infos['position'][0] +2, ship_1_infos['position'][1] -1],
                                                    [ship_1_infos['position'][0] -2, ship_1_infos['position'][1]],[ship_1_infos['position'][0] -2, ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0] -2, ship_1_infos['position'][1] -1]]
                        
                                        for position in range (0,len(warship_reach_position)):
                                            for enemy_position in range (0,len(warship)): 
                                                if warship_reach_position[position] == warship[enemy_position] and nb_deplacement == 0:
                                                    orders_ia += ' %s:*%d-%d'%(ship, warship_reach_position[position][0], warship_reach_position[position][1])
                                                    nb_deplacement += 1
                    
                    if nb_deplacement == 0:    
                        
                        if closest_enemy_ship != []:    
                            enemy_ship = enemy_ships_names[closest_enemy_ship.index(min(closest_enemy_ship))]
                            ship_1_infos = players_infos['player_%d'%enemy_id]['ships'][enemy_ship]
                            manathan_distance_ship = min(closest_enemy_ship)
                        
                        manathan_distance_portal = abs(general_infos['portals']['player_%d'%enemy_id][0]-ship_infos['position'][0]) + abs(general_infos['portals']['player_%d'%enemy_id][1]-ship_infos['position'][1])
                        
                        if ship_infos['type'] == 'scout':
                            #Compute the reach of the scout and tells if the warship can make a shoot on enemy portal or ship (centers and parts of the ship)
                            
                            
                            scout_reach_position = [[ship_infos['position'][0]-3,ship_infos['position'][1]],[ship_infos['position'][0]-2,ship_infos['position'][1]+1],
                                                      [ship_infos['position'][0]-1,ship_infos['position'][1]+2],[ship_infos['position'][0],ship_infos['position'][1]+3],
                                                      [ship_infos['position'][0]+1,ship_infos['position'][1]+2],[ship_infos['position'][0]+2,ship_infos['position'][1]+1],
                                                      [ship_infos['position'][0]+3,ship_infos['position'][1]],[ship_infos['position'][0]+2,ship_infos['position'][1]-1],
                                                      [ship_infos['position'][0]+1,ship_infos['position'][1]-2],[ship_infos['position'][0],ship_infos['position'][1]-3],
                                                      [ship_infos['position'][0]-1,ship_infos['position'][1]-2],[ship_infos['position'][0]-2,ship_infos['position'][1]-1],
                                                      [ship_infos['position'][0]-2,ship_infos['position'][1]],[ship_infos['position'][0]+2,ship_infos['position'][1]],
                                                      [ship_infos['position'][0],ship_infos['position'][1]-2],[ship_infos['position'][0],ship_infos['position'][1]+2]]
                                                      
                            
                            #Look if the scout can reach a portal case
                            for position in range (0,len(scout_reach_position)):
                                for row in range (general_infos['portals']['player_%d'%enemy_id][0]-2,general_infos['portals']['player_%d'%enemy_id][0]+2):
                                    for column in range (general_infos['portals']['player_%d'%enemy_id][1]-2,general_infos['portals']['player_%d'%enemy_id][1]+2):
                                        enemy_portal_position = [row,column]
                                        
                                        if scout_reach_position[position] == enemy_portal_position and nb_deplacement == 0:
                                            orders_ia += ' %s:*%d-%d'%(ship, scout_reach_position[position][0], scout_reach_position[position][1])
                                            nb_deplacement += 1
                                            
                            
                            if closest_enemy_ship != []:
                                #Look at the type of enemy ship and compare center position and other parts position of enemy ship with scout reach positions
                                if ship_1_infos['type'] == 'excavator-S':
             
                                    excavator_S = [ship_1_infos['position']]
                 
                                    for position in range (0,len(scout_reach_position)):
                        
                                        if scout_reach_position[position] == excavator_S[0] and nb_deplacement == 0:
                                            orders_ia += ' %s:*%d-%d'%(ship, scout_reach_position[position][0], scout_reach_position[position][1])
                                            nb_deplacement += 1    
                        
                
                                elif ship_1_infos['type'] == 'excavator-M': 
             
                                    excavator_M = [ship_1_infos['position'], [ship_1_infos['position'][0], ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] -1],
                                                    [ship_1_infos['position'][0] +1, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] -1, ship_1_infos['position'][1]]]
                    
                                    for position in range (0,len(scout_reach_position)):
                                        for enemy_position in range (0,len(excavator_M)): 
                                            if scout_reach_position[position] == excavator_M[enemy_position] and nb_deplacement == 0:
                                                orders_ia += ' %s:*%d-%d'%(ship, scout_reach_position[position][0], scout_reach_position[position][1])
                                                nb_deplacement += 1    
                
                                elif ship_1_infos['type'] == 'excavator-L':
                
                                    excavator_L = [ship_1_infos['position'],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] +2],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] -1],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] -2],
                                                    [ship_1_infos['position'][0] +1, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] +2, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] -1, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] -2, ship_1_infos['position'][1]]]
                                
                                    for position in range (0,len(scout_reach_position)):
                                        for enemy_position in range (0,len(excavator_L)): 
                                            if scout_reach_position[position] == excavator_L[enemy_position] and nb_deplacement == 0:
                                                orders_ia += ' %s:*%d-%d'%(ship, scout_reach_position[position][0], scout_reach_position[position][1])
                                                nb_deplacement += 1

            
                                elif ship_1_infos['type'] == 'scout': 
                 
                                    scout = [ship_1_infos['position'],
                                            [ship_1_infos['position'][0], ship_1_infos['position'][1] +1],
                                            [ship_1_infos['position'][0], ship_1_infos['position'][1] -1],
                                            [ship_1_infos['position'][0] +1, ship_1_infos['position'][1]],
                                            [ship_1_infos['position'][0] -1, ship_1_infos['position'][1]],
                                            [ship_1_infos['position'][0] +1, ship_1_infos['position'][1] +1],
                                            [ship_1_infos['position'][0] -1, ship_1_infos['position'][1] -1],
                                            [ship_1_infos['position'][0] +1, ship_1_infos['position'][1]-1],
                                            [ship_1_infos['position'][0] -1, ship_1_infos['position'][1]+1]]
                                
                                    for position in range (0,len(scout_reach_position)):
                                        for enemy_position in range (0,len(scout)): 
                                            if scout_reach_position[position] == scout[enemy_position] and nb_deplacement == 0:
                                                orders_ia += ' %s:*%d-%d'%(ship, scout_reach_position[position][0], scout_reach_position[position][1])
                                                nb_deplacement += 1

            
                                else: 
                 
                                    if ship_1_infos['type'] == 'warship':
                    
                                        warship = [ship_1_infos['position'],[ship_1_infos['position'][0], ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] -1],[ship_1_infos['position'][0] -1, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] +1, ship_1_infos['position'][1]],[ship_1_infos['position'][0] +1, ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0] -1, ship_1_infos['position'][1] -1],[ship_1_infos['position'][0] +1, ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0] -1, ship_1_infos['position'][1] -1],[ship_1_infos['position'][0], ship_1_infos['position'][1] +2],
                                                    [ship_1_infos['position'][0] +1, ship_1_infos['position'][1] +2],[ship_1_infos['position'][0] -1, ship_1_infos['position'][1] +2],
                                                    [ship_1_infos['position'][0], ship_1_infos['position'][1] -2],[ship_1_infos['position'][0] +1, ship_1_infos['position'][1] -2],
                                                    [ship_1_infos['position'][0] -1, ship_1_infos['position'][1] -2],[ship_1_infos['position'][0] +2, ship_1_infos['position'][1]],
                                                    [ship_1_infos['position'][0] +2, ship_1_infos['position'][1] +1],[ship_1_infos['position'][0] +2, ship_1_infos['position'][1] -1],
                                                    [ship_1_infos['position'][0] -2, ship_1_infos['position'][1]],[ship_1_infos['position'][0] -2, ship_1_infos['position'][1] +1],
                                                    [ship_1_infos['position'][0] -2, ship_1_infos['position'][1] -1]]
                     
                                        for position in range (0,len(scout_reach_position)):
                                            for enemy_position in range (0,len(warship)): 
                                                if scout_reach_position[position] == warship[enemy_position] and nb_deplacement == 0:
                                                    orders_ia += ' %s:*%d-%d'%(ship, scout_reach_position[position][0], scout_reach_position[position][1])
                                                    nb_deplacement += 1
                        
                       
                       
                        manathan_distance_portal = abs(general_infos['portals']['player_%d'%enemy_id][0]-ship_infos['position'][0]) + abs(general_infos['portals']['player_%d'%enemy_id][1]-ship_infos['position'][1])
                        #If an enemy portal is nearer, ship attack goes to portal     
                        
                        if manathan_distance_portal <= manathan_distance_ship and nb_deplacement == 0:
                            
                            #If they aren't on the same line and column
                            if ship_infos['position'][0] != general_infos['portals']['player_%d'%enemy_id][0] and ship_infos['position'][1] != general_infos['portals']['player_%d'%enemy_id][1]:
                                if ship_infos['position'][0] > general_infos['portals']['player_%d'%enemy_id][0]:
                                    if ship_infos['position'][1] > general_infos['portals']['player_%d'%enemy_id][1]:
                                        orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1]-1)
                                        nb_deplacement += 1
                                    else:
                                        orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1]+1)
                                        nb_deplacement += 1
                                else:
                                    if ship_infos['position'][1] > general_infos['portals']['player_%d'%enemy_id][1]:
                                        orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1]-1)
                                        nb_deplacement += 1
                                    else:
                                        orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1]+1)
                                        nb_deplacement += 1
                            #If they aren't on the same line but on the same column
                            elif ship_infos['position'][0] != general_infos['portals']['player_%d'%enemy_id][0] and ship_infos['position'][1] == general_infos['portals']['player_%d'%enemy_id][1]:
                                if ship_infos['position'][0] > general_infos['portals']['player_%d'%enemy_id][0]:
                                    orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1])
                                    nb_deplacement += 1
                                else:
                                    orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1])
                                    nb_deplacement += 1
                            #If they aren't on the same column but on the same line
                            elif ship_infos['position'][0] == general_infos['portals']['player_%d'%enemy_id][0] and ship_infos['position'][1] != general_infos['portals']['player_%d'%enemy_id][1]:
                                if ship_infos['position'][1] > general_infos['portals']['player_%d'%enemy_id][1]:
                                    orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0], ship_infos['position'][1]-1)
                                    nb_deplacement += 1
                                else:
                                    orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0], ship_infos['position'][1]+1)
                                    nb_deplacement += 1
                        
                        
                        #If enemy ship is nearer, ship attack goes to enemy ship             
                        elif manathan_distance_portal > manathan_distance_ship and nb_deplacement == 0:
                            #If they aren't on the same line and column
                            if ship_infos['position'][0] != ship_1_infos['position'][0] and ship_infos['position'][1] != ship_1_infos['position'][1]:
                                if ship_infos['position'][0] > ship_1_infos['position'][0]:
                                    if ship_infos['position'][1] > ship_1_infos['position'][1]:
                                        orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1]-1)
                                        nb_deplacement += 1
                                    else:
                                        orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1]+1)
                                        nb_deplacement += 1
                                else:
                                    if ship_infos['position'][1] > ship_1_infos['position'][1]:
                                        orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1]-1)
                                        nb_deplacement += 1
                                    else:
                                        orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1]+1)
                                        nb_deplacement += 1
                            #If they aren't on the same line but on the same column
                            elif ship_infos['position'][0] != ship_1_infos['position'][0] and ship_infos['position'][1] == ship_1_infos['position'][1]:
                                if ship_infos['position'][0] > ship_1_infos['position'][0]:
                                    orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]-1, ship_infos['position'][1])
                                    nb_deplacement += 1
                                else:
                                    orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0]+1, ship_infos['position'][1])
                                    nb_deplacement += 1
                            #If they aren't on the same column but on the same line
                            elif ship_infos['position'][0] == ship_1_infos['position'][0] and ship_infos['position'][1] != ship_1_infos['position'][1]:
                                if ship_infos['position'][1] > ship_1_infos['position'][1]:
                                    orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0], ship_infos['position'][1]-1)
                                    nb_deplacement += 1
                                else:
                                    orders_ia += ' %s:@%d-%d'%(ship, ship_infos['position'][0], ship_infos['position'][1]+1)                                                        
                                    nb_deplacement += 1    
                                                                       
    return (orders_ia, nb_ships_bought)
    
def decrypt_orders(IA_orders, player_id, enemy_id, enemy_orders):
    """Decrypt and make a dictionary from the string orders of each player
      
    Parameters
    ----------
    IA_orders: string orders of the IA (str)
    
    player_id: player_1 or player_2 (str) 
    
    enemy_id: player_1 or player_2 (str)y
    
    enemy_orders: string orders of the enemy
    
    Returns
    -------
    orders: dictionary with all orders of each player per turn (dict)
      
    Notes
    -----
    The player can order nothing so the string orders could be empty.
    The IA is the second player.  
    Version
    -------
    specification: Martin Grifnée (v.2 09/04/18) 
    implementation: Martin Grifnée (v.1 09/04/18)  
    """
    orders = {'player_1':{},'player_2':{}}
        
    str_orders_1 = enemy_orders
     
    if len(str_orders_1) != 0:
         
        elements_1 = str_orders_1.split(' ')
     
        for element in elements_1:
         
            list_value = []
            key, value = element.split(':')
            list_value.append(value)
         
            if key in orders['player_%d'%enemy_id]:
             
                orders['player_%d'%enemy_id][key].append(value)
             
            else:
                orders['player_%d'%enemy_id][key] = list_value
         
     
    str_orders_2 = IA_orders
     
    if len(str_orders_2) != 0:
     
        elements_2 = str_orders_2.split(' ')    
     
        for element in elements_2:
         
            list_value = []
            key, value = element.split(':')
            list_value.append(value)
         
            if key in orders['player_%d'%player_id]:
             
                orders['player_%d'%player_id][key].append(value)
         
            else:
                orders['player_%d'%player_id][key] = list_value
    
    return orders

def buy_ships (ships_infos, players_infos, orders, board_info):
    """The player buys ships and excavators and return the choices
    
    Parameters
    ----------
    ships_infos: data structure with all informations of ships and excavators (dict)
    
    players_infos: data structure with all the ships and excavators of each player (dict)
    
    orders: dictionary with all orders of each player per turn (dict)
    
    board_info: dictionary with all informations of the board (dcit)
    
    board: list of list that contains the board (list)    
    
    Returns
    -------
    players_infos: new choices updated in the data structure (dict)
    
    Version
    -------
    specification: Grégoire de Sauvage (v.2 16/04/18)
    implementation: Grégoire de Sauvage (v.2 16/04/18)
    """
    
    for player in orders:
        for ship in orders[player]:
                
            #If player buys a scout
            if 'scout' in orders[player][ship]:
                #Check if player has enough money
                if ships_infos['scout']['price'] <= players_infos[player]['nb_ore']:
                    #Pays the ship
                    players_infos[player]['nb_ore'] -= ships_infos['scout']['price']
                    
                    #Adds ship in players_infos
                    players_infos[player]['ships'][ship] = {'portee':3, 'type':'scout', 'position':board_info['portals'][player], 'life':ships_infos['scout']['life']}
                    
                                                    
            #If player buys a warship
            if 'warship' in orders[player][ship]:
                #Check if player has enough money
                if ships_infos['warship']['price'] <= players_infos[player]['nb_ore']:
                    #Pays the ship
                    players_infos[player]['nb_ore'] -= ships_infos['warship']['price']
                    
                    #Adds ship in players_infos
                    players_infos[player]['ships'][ship] = {'portee':5, 'type':'warship', 'position':board_info['portals'][player], 'life':ships_infos['warship']['life']}           
            
            
            #If player buys an excavator-S
            if 'excavator-S' in orders[player][ship]:
                #Check if player has enough money
                if ships_infos['excavator-S']['price'] <= players_infos[player]['nb_ore']:
                    #Pays the ship
                    players_infos[player]['nb_ore'] -= ships_infos['excavator-S']['price']
                    
                    #Adds ship in players_infos
                    players_infos[player]['ships'][ship] = {'lock':'no', 'nb_ore':0, 'type':'excavator-S', 'position':board_info['portals'][player], 'life':ships_infos['excavator-S']['life'], 'tonnage':ships_infos['excavator-S']['tonnage']}
            
        
            #If player buys an excavator-M
            if 'excavator-M' in orders[player][ship]:
                #Check if player has enough money
                if ships_infos['excavator-M']['price'] <= players_infos[player]['nb_ore']:
                    #Pays the ship
                    players_infos[player]['nb_ore'] -= ships_infos['excavator-M']['price']
                   
                    #Adds ship in players_infos
                    players_infos[player]['ships'][ship] = {'lock':'no', 'nb_ore':0, 'type':'excavator-M', 'position':board_info['portals'][player], 'life':ships_infos['excavator-M']['life'], 'tonnage':ships_infos['excavator-M']['tonnage']}
                    
                    
            #If player buys an excavator-L
            if 'excavator-L' in orders[player][ship]:
                #Check if player has enough money
                if ships_infos['excavator-L']['price'] <= players_infos[player]['nb_ore']:
                    #Pays the ship
                    players_infos[player]['nb_ore'] -= ships_infos['excavator-L']['price']
                    
                    #Adds ship in players_infos
                    players_infos[player]['ships'][ship] = {'lock':'no', 'nb_ore':0, 'type':'excavator-L', 'position':board_info['portals'][player], 'life':ships_infos['excavator-L']['life'], 'tonnage':ships_infos['excavator-L']['tonnage']}
                    
                    
    return players_infos

def lock (players_infos, general_infos,orders):
    """Locking phase of excavators to asteroids or portals
      
    Parameters
    ----------
    players_infos: data structure with excavators of each player (dict)
      
    general_infos: dictionary with all position of asteroids (dict)
      
    orders: dictionary with all orders of each player per turn (dict)
      
    Returns
    -------
    players_infos: new operations of locking for the excavators (dict)
    
    general_infos: new operations of locking to the asteroids (dict)  
      
    Version
    -------
    specification: Martin Grifnée (v.2 15/04/18)
    implementation: Martin Grifnée (v.2 08/04/18) 
    """
    for players in orders:
         
        for key in orders[players]:
             
            if 'lock' in orders[players][key]:
                 
                    for keys in general_infos['portals']:
                             
                        if players_infos[players]['ships'][key]['position'] == general_infos['portals'][keys]:
                         
                            players_infos[players]['ships'][key]['lock'] = 'yes'
                         
                    for keys_2 in general_infos['asteroids']:  
                         
                        if players_infos[players]['ships'][key]['position'] == general_infos['asteroids'][keys_2][0]:
                                     
                            players_infos[players]['ships'][key]['lock'] = 'yes'
                            general_infos['asteroids'][keys_2][3] += 1
                                 
                             
    return (players_infos,general_infos)
    
def release (players_infos,general_infos,orders):
    """Delocking phase of excavators to asteroids
      
    Parameters
    ----------
    players_infos: data structure with excavators of each player (dict)
      
    orders: dictionary with all orders of each player per turn (dict)
      
    Returns
    -------
    players_infos: new operations of delocking for the excavators (dict)
    
    general_infos: new operations of release to the asteroids (dict)  
    
    Version
    -------
    specification: Martin Grifnée (v.2, 30/03/18)    
    implementation: Martin Grifnée (v.2, 06/04/18)   
    """
     
    for players in orders:
         
        for key in orders[players]:
             
            if 'release' in orders[players][key]:
                 
                for keys in general_infos['portals']:
                 
                    if players_infos[players]['ships'][key]['position'] == general_infos['portals'][keys]:
                         
                        players_infos[players]['ships'][key]['lock'] = 'no'
                             
                 
                for keys_2 in general_infos['asteroids']:  
                         
                    if players_infos[players]['ships'][key]['position'] == general_infos['asteroids'][keys_2][0]:
                                     
                        players_infos[players]['ships'][key]['lock'] = 'no'
                         
                        general_infos['asteroids'][keys_2][3] -= 1
                             
    return (players_infos, general_infos)
    
def deplace_ships (players_infos,general_infos,orders):
    """Deplace ships and excavators
      
    Parameters
    ----------
    players_infos: data structure with all the ships and excavators of each player (dict)
      
    general_infos: dictionary with size of the board, position of portals and asteroids (dict)
     
    orders: dictionary with all orders of each player per turn (dict)
      
    Returns
    -------
    players_infos: new moves of ships and excavators (dict)
      
    Version
    -------
    specification: Martin Grifnée (v.2 11/04/18)
    implementation: Martin Grifnée (v.1 12/04/18)  
    """
     
    for players in orders:
          
        for key in orders[players]:
              
            for element in range (0,len(orders[players][key])):
                 
                if '@' in orders[players][key][element]:
                     
                    str_deplace = orders[players][key][element][1:]
                     
                    rw, cl = str_deplace.split('-')
                     
                    future_position = [int(rw),int(cl)]
                     
                     
                    if players_infos[players]['ships'][key]['type'] == 'excavator-S' and players_infos[players]['ships'][key]['moved'] == False:
                        if players_infos[players]['ships'][key]['lock'] == 'no':     
                            for rows in range (1,general_infos['board']['size'][0]+1):
                                for columns in range (1,general_infos['board']['size'][1]+1):
                             
                                    possible_pos_exc_S = [rows,columns]
                                 
                                    diff_rows = players_infos[players]['ships'][key]['position'][0] - future_position[0]
                                    diff_columns = players_infos[players]['ships'][key]['position'][1] - future_position[1] 
                                 
                                    if future_position == possible_pos_exc_S and abs(diff_rows)<2 and abs(diff_columns)<2:
                                    
                                        players_infos[players]['ships'][key]['position'] = future_position
                                        players_infos[players]['ships'][key]['moved'] = True
                                         
                     
                    elif players_infos[players]['ships'][key]['type'] == 'excavator-M' or players_infos[players]['ships'][key]['type'] == 'scout' and players_infos[players]['ships'][key]['moved'] == False:
                        if players_infos[players]['ships'][key]['type'] == 'excavator-M':
                            if players_infos[players]['ships'][key]['lock'] == 'no':                 
                                for rows in range (2,general_infos['board']['size'][0]):
                                    for columns in range (2,general_infos['board']['size'][1]):
                             
                                        possible_pos_exc_M_scout = [rows,columns]
                                 
                                        diff_rows = players_infos[players]['ships'][key]['position'][0] - future_position[0]
                                        diff_columns = players_infos[players]['ships'][key]['position'][1] - future_position[1]
                                 
                                        if future_position == possible_pos_exc_M_scout and abs(diff_rows)<2 and abs(diff_columns)<2:
                                    
                                            players_infos[players]['ships'][key]['position'] = future_position
                                            players_infos[players]['ships'][key]['moved'] = True
                        else:
                            for rows in range (2,general_infos['board']['size'][0]):
                                    for columns in range (2,general_infos['board']['size'][1]):
                             
                                        possible_pos_exc_M_scout = [rows,columns]
                                 
                                        diff_rows = players_infos[players]['ships'][key]['position'][0] - future_position[0]
                                        diff_columns = players_infos[players]['ships'][key]['position'][1] - future_position[1]
                                 
                                        if future_position == possible_pos_exc_M_scout and abs(diff_rows)<2 and abs(diff_columns)<2:
                                    
                                            players_infos[players]['ships'][key]['position'] = future_position
                                            players_infos[players]['ships'][key]['moved'] = True                                     
                                         
                    else:
                        if players_infos[players]['ships'][key]['type'] == 'excavator-L' or players_infos[players]['ships'][key]['type'] == 'warship' and players_infos[players]['ships'][key]['moved'] == False:
                            if players_infos[players]['ships'][key]['type'] == 'excavator-L': 
                                if players_infos[players]['ships'][key]['lock'] == 'no':
                            
                                    for rows in range(3,general_infos['board']['size'][0]-1):
                                        for columns in range (3,general_infos['board']['size'][1]-1):
                             
                                            possible_pos_exc_L_warship = [rows,columns]
                                 
                                            diff_rows = players_infos[players]['ships'][key]['position'][0] - future_position[0]
                                            diff_columns = players_infos[players]['ships'][key]['position'][1] - future_position[1]
                                     
                                            if future_position == possible_pos_exc_L_warship and abs(diff_rows)<2 and abs(diff_columns)<2:
                                    
                                                players_infos[players]['ships'][key]['position'] = future_position
                                                players_infos[players]['ships'][key]['moved'] = True
                                     
                            else:
                                for rows in range(3,general_infos['board']['size'][0]-1):
                                        for columns in range (3,general_infos['board']['size'][1]-1):
                             
                                            possible_pos_exc_L_warship = [rows,columns]
                                 
                                            diff_rows = players_infos[players]['ships'][key]['position'][0] - future_position[0]
                                            diff_columns = players_infos[players]['ships'][key]['position'][1] - future_position[1]
                                     
                                            if future_position == possible_pos_exc_L_warship and abs(diff_rows)<2 and abs(diff_columns)<2:
                                    
                                                players_infos[players]['ships'][key]['position'] = future_position
                                                players_infos[players]['ships'][key]['moved'] = True                 
    
    return players_infos 

def attack(players_infos,general_infos,orders,nb_turn_without_damage):
    """Attack a ship or a portal with another ship
     
    Parameters
    ---------
    players_infos: dictionary with the information of the player(dict)
     
    general_infos: dictionary with size of the board, position of portals and asteroids (dict)
     
    orders: dictionary with all orders of each player per turn (dict)
    
    nb_turn_without_damage: number of turn without any damage to ships and portals (int) 
    
    Returns
    -------
    players_infos: number of HP left of the ships and portals (dict)
     
    Notes
    -----
    If a ship is destroyed (0HP), it will be removed from players_infos.
     
    Version
    -------
    specification: Martin Grifnée (v.3, 27/04/2018)
    implementation: Martin Grifnée (v.2, 15/04/2018) 
    """
    attacks_warship = []
     
    attacks_scout = []
     
    for players in orders:
         
        for key in orders[players]:
             
            for element in range (0,len(orders[players][key])):
                 
                if '*' in orders[players][key][element]:
                     
                    str_attack = orders[players][key][element][1:]
                     
                    rw, cl = str_attack.split('-')
                     
                    future_attack_position = [int(rw),int(cl)]
                     
                     
                    if players_infos[players]['ships'][key]['type'] == 'warship' and players_infos[players]['ships'][key]['moved'] == False:
                         
                        diff_rows = players_infos[players]['ships'][key]['position'][0] - future_attack_position[0]
                        diff_columns = players_infos[players]['ships'][key]['position'][1] - future_attack_position[1]
                         
                        if abs(diff_rows) < 6 and abs(diff_columns) < 6:
                             
                            attacks_warship.append(future_attack_position)
                             
                        else:
                            print('You didn\'t respect the reach of the warship')
                             
                    elif players_infos[players]['ships'][key]['type'] == 'scout' and players_infos[players]['ships'][key]['moved'] == False:     
                         
                        diff_rows = players_infos[players]['ships'][key]['position'][0] - future_attack_position[0]
                        diff_columns = players_infos[players]['ships'][key]['position'][1] - future_attack_position[1]
                         
                        if abs(diff_rows) < 4 and abs(diff_columns) < 4:
                             
                            attacks_scout.append(future_attack_position)
                     
                        else:
                            print('You didn\'t respect the reach of the scout')
                             
    ## Regarde si les tirs touchent les vaisseaux et leurs parties et si oui, ceux-ci perdent de la vie                        
    for player in players_infos:
        for name_ship in players_infos[player]['ships']:
         
            if players_infos[player]['ships'][name_ship]['type'] == 'excavator-S':
             
                excavator_S = [players_infos[player]['ships'][name_ship]['position']]
                 
                for position in range (0,len(attacks_warship)):
                     
                    if attacks_warship[position] == excavator_S[0]:
                        players_infos[player]['ships'][name_ship]['life'] -= 3
                        nb_turn_without_damage = 0
                
                for position in range (0,len(attacks_scout)):
                     
                    if attacks_scout[position] == excavator_S[0]:
                        players_infos[player]['ships'][name_ship]['life'] -= 1   
                        nb_turn_without_damage = 0
         
            elif players_infos[player]['ships'][name_ship]['type'] == 'excavator-M': 
             
                excavator_M = [players_infos[player]['ships'][name_ship]['position'], 
                    [players_infos[player]['ships'][name_ship]['position'][0], players_infos[player]['ships'][name_ship]['position'][1] +1],
                    [players_infos[player]['ships'][name_ship]['position'][0], players_infos[player]['ships'][name_ship]['position'][1] -1],
                    [players_infos[player]['ships'][name_ship]['position'][0] +1, players_infos[player]['ships'][name_ship]['position'][1]],
                    [players_infos[player]['ships'][name_ship]['position'][0] -1, players_infos[player]['ships'][name_ship]['position'][1]]]
                 
                for position in range (0,len(excavator_M)):
                    for att_position in range (0,len(attacks_warship)):
                     
                        if attacks_warship[att_position] == excavator_M[position]:
                            players_infos[player]['ships'][name_ship]['life'] -= 3
                            nb_turn_without_damage = 0
                    
                    for att_position in range (0,len(attacks_scout)):
                     
                        if attacks_scout[att_position] == excavator_M[position]:
                            players_infos[player]['ships'][name_ship]['life'] -= 1
                            nb_turn_without_damage = 0
            
            elif players_infos[player]['ships'][name_ship]['type'] == 'excavator-L': 
             
                excavator_L = [players_infos[player]['ships'][name_ship]['position'],
                        [players_infos[player]['ships'][name_ship]['position'][0], players_infos[player]['ships'][name_ship]['position'][1] +1],
                        [players_infos[player]['ships'][name_ship]['position'][0], players_infos[player]['ships'][name_ship]['position'][1] +2],
                        [players_infos[player]['ships'][name_ship]['position'][0], players_infos[player]['ships'][name_ship]['position'][1] -1],
                        [players_infos[player]['ships'][name_ship]['position'][0], players_infos[player]['ships'][name_ship]['position'][1] -2],
                        [players_infos[player]['ships'][name_ship]['position'][0] +1, players_infos[player]['ships'][name_ship]['position'][1]],
                        [players_infos[player]['ships'][name_ship]['position'][0] +2, players_infos[player]['ships'][name_ship]['position'][1]],
                        [players_infos[player]['ships'][name_ship]['position'][0] -1, players_infos[player]['ships'][name_ship]['position'][1]],
                        [players_infos[player]['ships'][name_ship]['position'][0] -2, players_infos[player]['ships'][name_ship]['position'][1]]]
                 
                for position in range (0,len(excavator_L)):
                    for att_position in range (0,len(attacks_warship)):
                     
                        if attacks_warship[att_position] == excavator_L[position]:
                            players_infos[player]['ships'][name_ship]['life'] -= 3
                            nb_turn_without_damage = 0
                    
                    for att_position in range (0,len(attacks_scout)):
                     
                        if attacks_scout[att_position] == excavator_L[position]:
                            players_infos[player]['ships'][name_ship]['life'] -= 1
                            nb_turn_without_damage = 0
            
            elif players_infos[player]['ships'][name_ship]['type'] == 'scout': 
                 
                scout = [players_infos[player]['ships'][name_ship]['position'],
                    [players_infos[player]['ships'][name_ship]['position'][0], players_infos[player]['ships'][name_ship]['position'][1] +1],
                    [players_infos[player]['ships'][name_ship]['position'][0], players_infos[player]['ships'][name_ship]['position'][1] -1],
                    [players_infos[player]['ships'][name_ship]['position'][0] +1, players_infos[player]['ships'][name_ship]['position'][1]],
                    [players_infos[player]['ships'][name_ship]['position'][0] -1, players_infos[player]['ships'][name_ship]['position'][1]],
                    [players_infos[player]['ships'][name_ship]['position'][0] +1, players_infos[player]['ships'][name_ship]['position'][1] +1],
                    [players_infos[player]['ships'][name_ship]['position'][0] -1, players_infos[player]['ships'][name_ship]['position'][1] -1],
                    [players_infos[player]['ships'][name_ship]['position'][0] +1, players_infos[player]['ships'][name_ship]['position'][1]-1],
                    [players_infos[player]['ships'][name_ship]['position'][0] -1, players_infos[player]['ships'][name_ship]['position'][1]+1]]
                 
                for position in range (0,len(scout)):
                    for att_position in range (0,len(attacks_warship)):
                     
                        if attacks_warship[att_position] == scout[position]:
                            players_infos[player]['ships'][name_ship]['life'] -= 3
                            nb_turn_without_damage = 0
                    
                    for att_position in range (0,len(attacks_scout)):
                     
                        if attacks_scout[att_position] == scout[position]:
                            players_infos[player]['ships'][name_ship]['life'] -= 1
                            nb_turn_without_damage = 0
            else: 
                 
                if players_infos[player]['ships'][name_ship]['type'] == 'warship':
                 
                    warship = [players_infos[player]['ships'][name_ship]['position'],
                        [players_infos[player]['ships'][name_ship]['position'][0], players_infos[player]['ships'][name_ship]['position'][1] +1],
                        [players_infos[player]['ships'][name_ship]['position'][0], players_infos[player]['ships'][name_ship]['position'][1] -1],
                        [players_infos[player]['ships'][name_ship]['position'][0] -1, players_infos[player]['ships'][name_ship]['position'][1]],
                        [players_infos[player]['ships'][name_ship]['position'][0] +1, players_infos[player]['ships'][name_ship]['position'][1]],
                        [players_infos[player]['ships'][name_ship]['position'][0] +1, players_infos[player]['ships'][name_ship]['position'][1] +1],
                        [players_infos[player]['ships'][name_ship]['position'][0] -1, players_infos[player]['ships'][name_ship]['position'][1] -1],
                        [players_infos[player]['ships'][name_ship]['position'][0] +1, players_infos[player]['ships'][name_ship]['position'][1] +1],
                        [players_infos[player]['ships'][name_ship]['position'][0] -1, players_infos[player]['ships'][name_ship]['position'][1] -1],
                        [players_infos[player]['ships'][name_ship]['position'][0], players_infos[player]['ships'][name_ship]['position'][1] +2],
                        [players_infos[player]['ships'][name_ship]['position'][0] +1, players_infos[player]['ships'][name_ship]['position'][1] +2],
                        [players_infos[player]['ships'][name_ship]['position'][0] -1, players_infos[player]['ships'][name_ship]['position'][1] +2],
                        [players_infos[player]['ships'][name_ship]['position'][0], players_infos[player]['ships'][name_ship]['position'][1] -2],
                        [players_infos[player]['ships'][name_ship]['position'][0] +1, players_infos[player]['ships'][name_ship]['position'][1] -2],
                        [players_infos[player]['ships'][name_ship]['position'][0] -1, players_infos[player]['ships'][name_ship]['position'][1] -2],
                        [players_infos[player]['ships'][name_ship]['position'][0] +2, players_infos[player]['ships'][name_ship]['position'][1]],
                        [players_infos[player]['ships'][name_ship]['position'][0] +2, players_infos[player]['ships'][name_ship]['position'][1] +1],
                        [players_infos[player]['ships'][name_ship]['position'][0] +2, players_infos[player]['ships'][name_ship]['position'][1] -1],
                        [players_infos[player]['ships'][name_ship]['position'][0] -2, players_infos[player]['ships'][name_ship]['position'][1]],
                        [players_infos[player]['ships'][name_ship]['position'][0] -2, players_infos[player]['ships'][name_ship]['position'][1] +1],
                        [players_infos[player]['ships'][name_ship]['position'][0] -2, players_infos[player]['ships'][name_ship]['position'][1] -1]]
                     
                    for position in range (0,len(warship)):
                        for att_position in range (0,len(attacks_warship)):
                     
                            if attacks_warship[att_position] == warship[position]:
                                players_infos[player]['ships'][name_ship]['life'] -= 3
                                nb_turn_without_damage = 0
                        
                        for att_position in range (0,len(attacks_scout)):
                     
                            if attacks_scout[att_position] == warship[position]:
                                players_infos[player]['ships'][name_ship]['life'] -= 1
                                nb_turn_without_damage = 0
    
    ## Regarde si les tirs touchent les portails et si oui, ceux-ci perdent de la vie
    for players in general_infos['portals']:
         
        for row in range (general_infos['portals'][players][0]-2,general_infos['portals'][players][0]+2):
            for column in range (general_infos['portals'][players][1]-2,general_infos['portals'][players][1]+2):
                 
                portal_position = [row,column]
                 
                for att_position in range (0,len(attacks_warship)):
                     
                    if attacks_warship[att_position] == portal_position:
                        players_infos[players]['portal_life'] -= 3
                        nb_turn_without_damage = 0 
                
                for att_position in range (0,len(attacks_scout)):
                     
                    if attacks_scout[att_position] == portal_position:
                        players_infos[players]['portal_life'] -= 1
                        nb_turn_without_damage = 0
    
    ## Fait deux listes des noms des vaisseaux de chaque joueur
    ships_names_player_1 = []
    for keys in players_infos['player_1']['ships']:
         
        ships_names_player_1.append(keys)    
     
    ships_names_player_2 = []
    for keys in players_infos['player_2']['ships']:
         
        ships_names_player_2.append(keys)
     
    ## Supprime les vaisseaux qui sont détruits (<=0HP)
    i = 0
    nb_keys = len(players_infos['player_1']['ships'])
    while i<nb_keys:  
        
        if players_infos['player_1']['ships'][ships_names_player_1[i]]['life'] <= 0:
            del players_infos['player_1']['ships'][ships_names_player_1[i]]
        i += 1           
             
    i = 0   
    nb_keys = len(players_infos['player_2']['ships'])
    while i<nb_keys:      
                 
        if players_infos['player_2']['ships'][ships_names_player_2[i]]['life'] <= 0:
            del players_infos['player_2']['ships'][ships_names_player_2[i]]     
        i += 1
     
    return (players_infos,nb_turn_without_damage) 

def loading (players_infos, general_infos, nb_ore_player_1, nb_ore_player_2):
    """Set the money of the asteroid in the excavator
     
    Parameters
    ----------
    players_infos: dictionnary with the information of the player (dict)
     
    general_infos: dictionary with all position of asteroids (dict)
     
    Returns 
    ------
    players_infos: new amounts of ore of the players (dict)
     
    general_infos: number ore left in asteroids (dict)
     
    Notes
    ----- 
    If the asteroid has no more ore available, it will be removed from general_infos.
     
    Version
    -------
    specification: Martin Grifnee (v.1 04/03/18) 
    implementation: Florent Delwiche (v.2, 14/04/18) 
    """
    for nb_of_asteroid in general_infos['asteroids']:
        position_asteroid = general_infos['asteroids'][nb_of_asteroid][0]
        nb_ore_asteroid = general_infos['asteroids'][nb_of_asteroid][1]
        crop = general_infos['asteroids'][nb_of_asteroid][2]
        nb_ship_asteroid = general_infos['asteroids'][nb_of_asteroid][3]
        for player in players_infos:
        
            for ship in players_infos[player]['ships']:
                if 'lock' in players_infos[player]['ships'][ship]:
                    if players_infos[player]['ships'][ship]['lock'] == 'yes':
                
                        position_ship = players_infos[player]['ships'][ship]['position']
                        tonnage = players_infos[player]['ships'][ship]['tonnage']
                        nb_ore_ship = players_infos[player]['ships'][ship]['nb_ore']
                        position_asteroid = general_infos['asteroids'][nb_of_asteroid][0]
                       
                        if position_asteroid == position_ship:
                            if tonnage >= nb_ore_ship + crop:
                                if nb_ore_asteroid >= crop * nb_ship_asteroid: 
                                    nb_ore_ship += crop
                                    nb_ore_asteroid -= crop
                                    nb_ship_asteroid -= 1
                                    if player == 'player_1':
                                        nb_ore_player_1 += crop
                                    else:
                                        nb_ore_player_2 += crop
                                else:
                                    rest = nb_ore_asteroid / nb_ship_asteroid
                                    nb_ore_ship += rest
                                    nb_ore_asteroid -= rest
                                    nb_ship_asteroid -= 1
                                    if player == 'player_1':
                                        nb_ore_player_1 += rest
                                    else:
                                        nb_ore_player_2 += rest
                            else:
                                if nb_ore_asteroid >= crop * nb_ship_asteroid:
                                    nb_ore_ship += tonnage - nb_ore_ship
                                    nb_ore_asteroid -= tonnage - nb_ore_ship
                                    nb_ship_asteroid -= 1
                                    if player == 'player_1':
                                        nb_ore_player_1 += rest
                                    else:
                                        nb_ore_player_2 += rest
                                else:
                                    if nb_ore_asteroid > tonnage - nb_ore_ship:
                                        nb_ore_ship += tonnage - nb_ore_ship
                                        nb_ore_asteroid -= tonnage - nb_ore_ship
                                        nb_ship_asteroid -= 1
                                        if player == 'player_1':
                                            nb_ore_player_1 += rest
                                        else:
                                            nb_ore_player_2 += rest
                                    else:
                                        rest = nb_ore_asteroid
                                        nb_ore_ship += nb_ore_asteroid
                                        nb_ore_asteroid = 0
                                        if player == 'player_1':
                                            nb_ore_player_1 += rest
                                        else:
                                            nb_ore_player_2 += rest
                        
                        
                        if nb_ore_asteroid < 0.25:
                            nb_ore_asteroid = 0  
                        players_infos[player]['ships'][ship]['nb_ore'] = nb_ore_ship
                        general_infos['asteroids'][nb_of_asteroid][1] = nb_ore_asteroid
                         
                
    return (players_infos, general_infos, nb_ore_player_1, nb_ore_player_2)

def unloading (players_infos, general_infos):
    """Set the money of the excavator in the portal
      
    Parameters
    ----------
    players_infos: dictionnary with the information of the player (dict)
      
    general_infos: dictionary with all position (dict)
      
    Returns 
    -------
    players_infos: new amount of ore in the portal of each player (dict)
          
    Version
    -------
    specification: Florent Delwiche (v.2, 20/03/2018)
    implementation: Florent Delwiche (v.1, 13/04/18)  
    """
     
    for player in players_infos:
         
        for ship in players_infos[player]['ships']:
            if 'lock' in players_infos[player]['ships'][ship]:
                if players_infos[player]['ships'][ship]['lock'] == 'yes':
                    if players_infos[player]['ships'][ship]['position'] == general_infos['portals'][player]:
                        players_infos[player]['nb_ore'] += players_infos[player]['ships'][ship]['nb_ore']
                        players_infos[player]['ships'][ship]['nb_ore'] = 0
 
    return players_infos

def update_board (players_infos, general_infos):
    """Modify and update the board after deplacements and attacks
    
    Parameters
    ----------
    players_infos: data structure with all the ships and excavators of each player (dict)
     
    general_infos: general_infos: dictionary with size of the board, position of portals and asteroids (dict)
    
    board: list of list that contains the board (list)
    
    Returns
    -------
    board: new positions of ships on the board (list)
    
    Version
    -------
    specification: Martin Grifnée (v.2, 16/04/18)
    implementation: Martin Grifnée (v.2, 24/04/18)
    """
    #Creation of the board without portals and asteroids
    board = general_infos['board']['size'][0]*[u' ☐ '] #lines of the board
    
    for i in range(len(board)):
        board[i] = general_infos['board']['size'][1]*[u' ☐ ']#columns of the board
    
    #Creation of the portals and asteroids (☑ is an asteroid and ☒ is the portals)
        #portals
    for square in general_infos:
        if square == 'portals':
            for squares in general_infos[square]:
                for lines in range(general_infos[square][squares][0]-3, general_infos[square][squares][0]+2):
                    for columns in range(general_infos[square][squares][1]-3, general_infos[square][squares][1]+2):
                        board [lines][columns] = u' ☒ '
        #asteroids
        elif square == 'asteroids':
            for asteroid in general_infos[square]:
                board [general_infos[square][asteroid][0][0]-1][general_infos[square][asteroid][0][1]-1] = u' ☑ '
    
    # Update the position of ships
    
    for player in players_infos:
        for ship in players_infos[player]['ships']:
        
            if players_infos[player]['ships'][ship] != {}:
                
                if players_infos[player]['ships'][ship]['type'] == 'scout':
                
                    for lines in range(players_infos[player]['ships'][ship]['position'][0]-2, players_infos[player]['ships'][ship]['position'][0]+1):
                                for columns in range(players_infos[player]['ships'][ship]['position'][1]-2, players_infos[player]['ships'][ship]['position'][1]+1):
                                    board [lines][columns] = u' ✯ '
                                    
                elif players_infos[player]['ships'][ship]['type'] == 'warship':         
                    #high line
                    line = players_infos[player]['ships'][ship]['position'][0]-3
                    for columns in range(players_infos[player]['ships'][ship]['position'][1]-2, players_infos[player]['ships'][ship]['position'][1]+1):
                        board [line][columns] = u' ☓ '
                    #center
                    for lines in range(players_infos[player]['ships'][ship]['position'][0]-2, players_infos[player]['ships'][ship]['position'][0]+1):
                        for columns in range(players_infos[player]['ships'][ship]['position'][1]-3, players_infos[player]['ships'][ship]['position'][1]+2):
                            board [lines][columns] = u' ☓ '
                    #low line
                    extremity = players_infos[player]['ships'][ship]['position'][0]+1
                    for columns in range(players_infos[player]['ships'][ship]['position'][1]-2, players_infos[player]['ships'][ship]['position'][1]+1):
                        board [extremity][columns] = u' ☓ '
    
    
                elif players_infos[player]['ships'][ship]['type'] == 'excavator-L':
                
                    for lines in range(players_infos[player]['ships'][ship]['position'][0]-3, players_infos[player]['ships'][ship]['position'][0]+2): 
                                board [lines][players_infos[player]['ships'][ship]['position'][1]-1] = u' ✈ '
                                
                    lines = players_infos[player]['ships'][ship]['position'][0]-1
                    for columns in range(players_infos[player]['ships'][ship]['position'][1]-3, players_infos[player]['ships'][ship]['position'][1]+2):
                        board [lines][columns] = u' ✈⛟'
                        
                    board [players_infos[player]['ships'][ship]['position'][0]][players_infos[player]['ships'][ship]['position'][1]-1] = u' ✈ ' 
                    
                       
                elif players_infos[player]['ships'][ship]['type'] == 'excavator-M':
                    
                    board [players_infos[player]['ships'][ship]['position'][0]-2][players_infos[player]['ships'][ship]['position'][1]-1] = u' ★ '
                                
                    lines = players_infos[player]['ships'][ship]['position'][0]-1
                    for columns in range(players_infos[player]['ships'][ship]['position'][1]-2, players_infos[player]['ships'][ship]['position'][1]+1):
                        board [lines][columns] = u' ★⛟'
                                
                    board [players_infos[player]['ships'][ship]['position'][0]][players_infos[player]['ships'][ship]['position'][1]-1] = u' ★ '
                    
                else:
                    # For excavator-S
                    board [players_infos[player]['ships'][ship]['position'][0]-1][players_infos[player]['ships'][ship]['position'][1]-1] = u' ♦♦ '                                                                                                                  
    
    return board

def check_game_is_over(players_infos, general_infos, nb_turn_whithout_damage, nb_ore_player_1, nb_ore_player_2):
    """Check if game is over
     
    Parameters
    ----------
    players_infos: dictionnary with the information of the players (dict)
    
    general_infos: dictionnary with the health points of the portals (dict)
    
    nb_turn_without_damage: nb_turns without any kind of damage (int)  
    
    Returns
    -------
    winner: winner of Mining Wars (str)
    
    Version
    -------
    specification: Florent Delwiche (v.1, 02/03/18)
    implementation: Florent Delwiche (v.1, 11/04/18) 
    """
    winner =''
    
      
    if players_infos['player_1']['portal_life'] <= 0:
        winner = 'player_2'
    elif players_infos['player_2']['portal_life'] <= 0:
        winner = 'player_1'

        
    if nb_turn_whithout_damage == 200: 
        
        if players_infos['player_1']['portal_life'] > players_infos['player_2']['portal_life']:
            winner = 'player_1'
            
        elif players_infos['player_1']['portal_life'] < players_infos['player_2']['portal_life']:
            winner = 'player_2'
        
        else:
            if nb_ore_player_1 > nb_ore_player_2:
                winner = 'player_1'
            elif nb_ore_player_1 < nb_ore_player_2:
                winner = 'player_2'
            else:
                winner = 'no winner'

        
    return (winner)
    
def read_config_file (board_file, general_infos):
    """Creates the database of the board from the configuration file.
     
    Parameters
    ----------
    board_file: file that contains informations of the board (str)
     
    general_infos: empty dictionary (dict)
     
    Returns
    -------
    general_infos: dictionary that contains all the informations of the board (dict)
     
    Version
    -------
    specification: Grégoire de Sauvage (v1 01/03/2018)
    implementation: Grégoire de Sauvage (v1 10/04/2018)  
    """
    config_file = open (board_file,'r')
    lines = config_file.readlines()
    config_file.close()
    
    new_lines = []
    
    for line in lines:
        new_line = line.strip('\n')
        new_lines.append(new_line)
        
        
    nb_line = 1
    
    for element in new_lines:
        
        if nb_line == 1:
            key = element.split(':')
            contents_key = new_lines[nb_line].split(' ')
            dico = {key[0]:0}
            general_infos['board'] = dico
            general_infos['board'][key[0]] = [int(contents_key[0]), int(contents_key[1])]
            
        if nb_line == 3:
            key = element.split(':')
            contents_key = [new_lines[nb_line].split(' '), new_lines[nb_line+1].split(' ')]
            general_infos[key[0]] = {'player_1':[int(contents_key[0][0]),int(contents_key[0][1])], 'player_2':[int(contents_key[1][0]),int(contents_key[1][1])]}
            
        if nb_line == 6:
            key = element.split(':')
            general_infos[key[0]] = {}
            nb_asteroid = 1
            for asteroid in new_lines[nb_line:]:
                contents_key = asteroid.split(' ')
                general_infos['asteroids']['%d'%nb_asteroid] = [[int(contents_key[0]), int(contents_key[1])], int(contents_key[2]), int(contents_key[3])]
                nb_asteroid += 1
        nb_line += 1
    ## Creation of a fourth element in the list for each asteroids which corresponds to the number of extractors locked to this asteroid   
    for keys_id in general_infos['asteroids']:
        
        general_infos['asteroids'][keys_id].append(0)
        
    
    return general_infos


def board_creation (board_info):
    """Creates the board without printing it.
    
    Parameters
    ----------
    board_info: dictionnary that contains board's information (dictionnary)
    
    Returns
    -------
    board: a list of lists that contains the lines and columns of the board (list)
    
    Version
    -------
    specification: Grégoire de Sauvage (v.1 04/03/18)
    implementation: Grégoire de Sauvage (v.2 06/04/18)
    """
    #Creation of the board without portals and asteroids
    board = board_info ['board']['size'][0]*[u' ☐ '] #lines of the board
    
    for i in range(len(board)):
        board[i] = board_info['board']['size'][1]*[u' ☐ ']#columns of the board
    
    #Creation of the portals and asteroids (☑ is an asteroid and ☒ is the portals)
        #portals
    for square in board_info:
        if square == 'portals':
            for squares in board_info [square]:
                for lines in range(board_info[square][squares][0]-3, board_info[square][squares][0]+2):
                    for columns in range(board_info[square][squares][1]-3, board_info[square][squares][1]+2):
                        board [lines][columns] = u' ☒ '
        #asteroids
        elif square == 'asteroids':
            for asteroid in board_info [square]:
                board [board_info[square][asteroid][0][0]-1][board_info[square][asteroid][0][1]-1] = u' ☑ '
    
    return board


def display_board (board, board_infos):
    """Prints the board.
    
    Parameters
    ----------
    board: list of lists
    
    board_infos: data structure with general informations of the board
    
    Version
    -------
    specification: Grégoire de Sauvage (v.1 03/03/18)
    implementation: Grégoire de Saugave (v.1 20/03/18)
    """
    lines = ''
    nb_lines = 1
    
    for k in range(1, board_infos['board']['size'][1]+1):
        if k == 1:
            lines += '   ' + str(k)
        elif k < 10 and k > 1:
            lines += '  ' + str(k)
        else:
            lines += ' ' + str(k)
        
    lines += '\n'
     
    for i in range(len(board)):
        if nb_lines < 10:
            lines += str(nb_lines) + ' '
        else:
            lines += str(nb_lines)
        
        for j in range(len(board[i])):
            lines += str(board [i][j])
        lines += '\n'
        nb_lines += 1
    
    print (lines)
    
def get_IP():
    """Returns the IP of the computer where get_IP is called.
    
    Returns
    -------
    computer_IP: IP of the computer where get_IP is called (str)
    
    Notes
    -----
    If you have no internet connection, your IP will be 127.0.0.1.
    This IP address refers to the local host, i.e. your computer.
    
    """   
    
    return socket.gethostbyname(socket.gethostname())


def connect_to_player(player_id, remote_IP='127.0.0.1', verbose=False):
    """Initialise communication with remote player.
    
    Parameters
    ----------
    player_id: player id of the remote player, 1 or 2 (int)
    remote_IP: IP of the computer where remote player is (str, optional)
    verbose: True only if connection progress must be displayed (bool, optional)
    
    Returns
    -------
    connection: sockets to receive/send orders (tuple)
    
    Notes
    -----
    Initialisation can take several seconds.  The function only
    returns after connection has been initialised by both players.
    
    Use the default value of remote_IP if the remote player is running on
    the same machine.  Otherwise, indicate the IP where the other player
    is running with remote_IP.  On most systems, the IP of a computer
    can be obtained by calling the get_IP function on that computer.
        
    """ 
    
    # init verbose display
    if verbose:
        print('\n-------------------------------------------------------------')
        
    # open socket (as server) to receive orders
    socket_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_in.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # deal with a socket in TIME_WAIT state

    if remote_IP == '127.0.0.1':
        local_IP = '127.0.0.1'
    else:
        local_IP = get_IP()
    local_port = 42000 + (3-player_id)
    
    try:
        if verbose:
            print('binding on %s:%d to receive orders from player %d...' % (local_IP, local_port, player_id))
        socket_in.bind((local_IP, local_port))
    except:
        local_port = 42000 + 100+ (3-player_id)
        if verbose:
            print('   referee detected, binding instead on %s:%d...' % (local_IP, local_port))
        socket_in.bind((local_IP, local_port))

    socket_in.listen(1)
    if verbose:
        print('   done -> now waiting for a connection on %s:%d\n' % (local_IP, local_port))

    # open client socket used to send orders
    socket_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # deal with a socket in TIME_WAIT state
    
    remote_port = 42000 + player_id
    
    connected = False
    msg_shown = False
    while not connected:
        try:
            if verbose and not msg_shown:
                print('connecting on %s:%d to send orders to player %d...' % (remote_IP, remote_port, player_id))
            socket_out.connect((remote_IP, remote_port))
            connected = True
            if verbose:
                print('   done -> now sending orders to player %d on %s:%d' % (player_id, remote_IP, remote_port))
        except:
            if verbose and not msg_shown:
                print('   connection failed -> will try again every 100 msec...')
            time.sleep(.1)

            msg_shown = True
            
    if verbose:
        print()

    # accept connection to the server socket to receive orders from remote player
    socket_in, remote_address = socket_in.accept()
    if verbose:
        print('now listening to orders from player %d' % (player_id))
            
    # end verbose display
    if verbose:
        print('\nconnection to remote player %d successful\n-------------------------------------------------------------\n' % player_id)

    # return sockets for further use     
    return (socket_in, socket_out)


def disconnect_from_player(connection):
    """End communication with remote player.
    
    Parameters
    ----------
    connection: sockets to receive/send orders (tuple)
    
    """
    
    # get sockets
    socket_in = connection[0]
    socket_out = connection[1]
    
    # shutdown sockets
    socket_in.shutdown(socket.SHUT_RDWR)    
    socket_out.shutdown(socket.SHUT_RDWR)
    
    # close sockets
    socket_in.close()
    socket_out.close()
    
    
def notify_remote_orders(connection, orders):
    """Notifies orders of the local player to a remote player.
    
    Parameters
    ----------
    connection: sockets to receive/send orders (tuple)
    orders: orders of the local player (str)
        
    Raises
    ------
    IOError: if remote player cannot be reached
    
    """
     
    # get sockets
    socket_in = connection[0]
    socket_out = connection[1]

    # deal with null orders (empty string)
    if orders == '':
        orders = 'null'
    
    # send orders
    try:
        socket_out.sendall(orders.encode())
    except:
        raise IOError('remote player cannot be reached')


def get_remote_orders(connection):
    """Returns orders from a remote player.

    Parameters
    ----------
    connection: sockets to receive/send orders (tuple)
        
    Returns
    ----------
    player_orders: orders given by remote player (str)

    Raises
    ------
    IOError: if remote player cannot be reached
            
    """
   
    # get sockets
    socket_in = connection[0]
    socket_out = connection[1]

    # receive orders    
    try:
        orders = socket_in.recv(65536).decode()
    except:
        raise IOError('remote player cannot be reached')
        
    # deal with null orders
    if orders == 'null':
        orders = ''
        
    return orders
    
def creation_and_display (board_info, board_file):
    """General function to create and display the board
     
    Parameters
    ----------
    board_info : data structure with general innformations of the board
    
    Returns
    -------
    board : data structure that contains the board
    
    general_infos : data structure with general infos of the board
    
    Version
    -------
    specification: Martin Grifnée (v.2 16/04/2018)
    implementation: Grégoire de Sauvage (v.1 16/04/16)
    """
    
    general_infos = read_config_file (board_file, board_info)
    
    board = board_creation (general_infos)
    
    display_board (board, general_infos)
    
    return (general_infos, board)
    

    
def run_game (general_infos,board,player_id,enemy_id,remote_IP,verbose):
    """Run the game turn per turn
     
    Parameters
    ----------
    general_infos: dictionary with size of the board, position of portals and asteroids (dict)
    
    board: list of list that contains the board (list)  
    
    player_id: player_1 or player_2 (str) 
    
    enemy_id: player_1 or player_2 (str) 
    
    Version
    -------
    specification: Martin Grifnée (v.1, 04/03/2018)
    implementation: Martin Grifnée (v.1, 15/04/18)
    """
    ships_infos = {'scout':{'life':3, 'dammage':1, 'portee':3, 'price':3},
               'warship':{'life':18, 'dammage':3, 'portee':5, 'price':9},
               'excavator-S':{'life':2, 'price':1, 'tonnage':1},
               'excavator-M':{'life':3, 'price':2, 'tonnage':4},
               'excavator-L':{'life':6, 'price':4, 'tonnage':8}}
               
    players_infos = {'player_1':{'ships':{},'nb_ore':4,'portal_life':100},
                 'player_2':{'ships':{},'nb_ore':4,'portal_life':100}}
    
    connection = remote_play.connect_to_player(player_id, remote_IP, verbose)

    game_is_over = False
    nb_turn_without_damage = 0
    nb_ships_bought = 0
    nb_ship_bought = 0
    nb_turns = 1
    nb_ore_player_1 = 0
    nb_ore_player_2 = 0
    while game_is_over == False:
        
        if player_id == 'player_1':
            IA_order_1, nb_ships_bought = ia_orders (players_infos, ships_infos, general_infos, nb_ships_bought, player_id, enemy_id)    
            print('The orders of the first IA: %s' %(IA_order_1))
            notify_remote_orders(connection, IA_order_1)
            print('--------------------------------------------------------------------------------------------------------------------------------------------------')
            IA_order_2, nb_ship_bought = ia_orders (players_infos, ships_infos, general_infos, nb_ship_bought, enemy_id, player_id)
            print('The orders of the second IA: %s' %(IA_order_2))
            IA_order_2 = get_remote_orders(connection)
            print('--------------------------------------------------------------------------------------------------------------------------------------------------')
        else:
            IA_order_2, nb_ships_bought = ia_orders (players_infos, ships_infos, general_infos, nb_ships_bought, enemy_id, player_id)    
            print('The orders of the first IA: %s' %(IA_order_2))
            notify_remote_orders(connection, IA_order_2)
            print('--------------------------------------------------------------------------------------------------------------------------------------------------')
            IA_order_1, nb_ship_bought = ia_orders (players_infos, ships_infos, general_infos, nb_ship_bought, player_id, enemy_id)
            print('The orders of the second IA: %s' %(IA_order_1))
            IA_order_1 = get_remote_orders(connection)
            print('--------------------------------------------------------------------------------------------------------------------------------------------------')
            
        orders = decrypt_orders(IA_order_1,player_id,enemy_id,IA_order_2)
        
        players_infos = buy_ships (ships_infos, players_infos, orders, general_infos)
        
        
        for player in players_infos:
            if players_infos[player]['ships'] != {}:
                for name_ship in players_infos[player]['ships']:
                    players_infos[player]['ships'][name_ship]['moved'] = False

        
        players_infos, general_infos = lock (players_infos, general_infos,orders)
         
        
        players_infos, general_infos = release (players_infos,general_infos,orders)
        
        
        players_infos = deplace_ships (players_infos,general_infos,orders)
        
        nb_turn_without_damage += 1
        
        players_infos,nb_turn_without_damage = attack(players_infos,general_infos,orders,nb_turn_without_damage)
        print ('nb turn without damage :%d'%nb_turn_without_damage) 
        players_infos, general_infos, nb_ore_player_1, nb_ore_player_2 = loading (players_infos, general_infos, nb_ore_player_1, nb_ore_player_2)
        print('--------------------------------------------------------------------------------------------------------------------------------------------------')  
        
        players_infos = unloading (players_infos, general_infos)
        
        for player in players_infos:
            infos = ''
            infos += '%s:'%player
            infos += 'portal_life:%d, nb_ore:%d'%(players_infos[player]['portal_life'], players_infos[player]['nb_ore']) 
            for ship in players_infos[player]['ships']:
                infos += '\n'+ '%s: %s'%(ship, players_infos[player]['ships'][ship])
            print(infos)
        
        print('--------------------------------------------------------------------------------------------------------------------------------------------------')
        print(general_infos) 
        print('--------------------------------------------------------------------------------------------------------------------------------------------------')
        board = update_board (players_infos, general_infos)
        
        
        display_board (board, general_infos)
        
        
        winner =  check_game_is_over(players_infos, general_infos, nb_turn_without_damage, nb_ore_player_1, nb_ore_player_2)

        print("""
        
        
        
        """)
        if winner == '':
            nb_turns += 1
            print('This is the turn number %d' %(nb_turns))
            print('>>>>>>>')
            print('>>>>>>>')
        
        if winner == 'player_1' or winner == 'player_2' or winner == 'no winner':
            game_is_over = True
        
        time.sleep(0.3)
    
    return winner
    
def mining_wars (board_file,player_id,enemy_id,remote_IP,verbose):
    """General function of the game
    
    Parameters
    ----------
    board_file: file that contains informations of the board (file)
    
    player_id: define player_1 or player_2 (str)
    
    enemy_id: player_1 or player_2 (str) 
    
    Version
    -------
    specification: Martin Grifnée (v.3 04/05/18)
    implementation: Grégoire de Sauvage (v.1 16/04/18)
    """
    general_info = {}
    general_infos, board = creation_and_display (general_info, board_file)

    winner = run_game (general_infos,board,player_id,enemy_id,remote_IP,verbose)
    
    print('%s win the game'%(winner))
    

# -*- coding: utf-8 -*-
from colored import fg, bg, attr
import os
import random
import time
from remote_play import connect_to_player, notify_remote_orders, get_remote_orders, disconnect_from_player, get_IP

def main(data_file, players, types, player_ID=None, ip=None):
    """Base function which start a game
    
    Parameters
    ----------
    data_file: file .cis which contents the game size and the abandonned spaceships(file)
    players: name of the players (tuple)
    types: type of players (tuple)
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    
    game_data = create_data(data_file, players, types, player_ID, ip)
    
    print_board(game_data)
    
    game_data = create_fleet(game_data)
    game_data = create_fleet(game_data)
    
    while not game_data['end_game'][1]:
            
        if game_data['players'][game_data['player_turn']]['player_type'] == 'advanced_ai':
            orders = advanced_ai(game_data, 'move')
            if game_data['statut_connection']:
                notify_remote_orders(game_data['connection'], orders)
                
        elif game_data['players'][game_data['player_turn']]['player_type'] == 'basic_ai':
            orders = basic_ai(game_data, 'move')
            if game_data['statut_connection']:
                notify_remote_orders(game_data['connection'], orders)
        
        elif game_data['players'][game_data['player_turn']]['player_type'] == 'player':
            orders = get_player_input()
            if game_data['statut_connection']:
                notify_remote_orders(game_data['connection'], orders)
            
        elif game_data['players'][game_data['player_turn']]['player_type'] == 'remote':
            orders = get_remote_orders(game_data['connection'])
               
        game_data = motion(orders, game_data)

    print_board(game_data)
    

def create_data(data_file, players, types, player_ID, ip):
    """With a file .cis, creating the initial dictionnary which would be use to play to the game
    
    Parameters
    ----------
    data_file: contents of the .cis file with the game size and the abandonned spaceships(list)
    players: name of the players (tuple)
    types: type of the players (tuple)
    
    Return
    ------
    game_data:contain all the information about the game (dict)
    
    Version:
    --------
    Specification: Bastien Nicolas, Thomas Bouteille, Aurélien Champagne (v0.1, 03/04/2017)
    Implementation: Bastien Nicolas (v0.1, 10/03/2017)
                    Bastien Nicolas (v0.2, 18/04/2017)
    """
    #initialisation of the data file(.cis)
    fh = open(data_file, 'r')
    content = fh.readlines()
    fh.close()
    
    #Initialisation of the game_data
    game_data = {'board':{},
                 'game_size' : [],
                 'spaceships':{},
                 'all_spaceships':[],
                 'all_abandonned_spaceships':{},
                 'turn_actions': [[], []],
                 'players':{},
                 'spaceships_stats':{},
                 'turn':0,#Turn without any ship being hit
                 'deaths_turn':[]} #the ship that the ai focus
                 
    
    #Split the size of the board in 2 parts [x,y]
    game_data['game_size'] = content[0].strip().split(' ')
    game_data['game_size'] = (int(game_data['game_size'][0]), int(game_data['game_size'][1]))
    
    #Creating the board data with a tuple of coords as a key and a list as a value
    for x in range(game_data['game_size'][1]+1):
        for y in range(game_data['game_size'][0]+1):
            if not x == 0 or y == 0:
                game_data['board'][y,x]=[]
    
    #Initialisation of the basic statistic of each spaceship
    game_data['spaceships_stats']['fighter'] = {'icon':'F', 'max_health':3, 'max_speed':5, 'damages':1, 'range':5, 'price':10}
    game_data['spaceships_stats']['destroyer'] = {'icon':'D','max_health':8, 'max_speed':2, 'damages':2, 'range':7, 'price':20}
    game_data['spaceships_stats']['battlecruiser'] = {'icon':'B','max_health':20, 'max_speed':1, 'damages':4, 'range':10, 'price':30}
    
    #Creating data for each player, at first the player 1 then the player 2
    number_player = 1
    
    for player in players:
        game_data['players'][str(number_player)]={}
        game_data['players'][str(number_player)]['pseudo'] = player
        game_data['players'][str(number_player)]['money'] = 100
        game_data['players'][str(number_player)]['list_spaceships'] = []
        game_data['players'][str(number_player)]['player_type'] = types[number_player-1]
        game_data['players'][str(number_player)]['ai_focus']={}
        game_data['players'][str(number_player)]['locked_fire_position']=[]#Use to know which position has been target during the previous turn
        
        if number_player == 1:
            game_data['players'][str(number_player)]['color'] = 'green'
        
        else:
            game_data['players'][str(number_player)]['color'] = 'red'
        
        number_player += 1
        
    game_data['player_turn'] = '1'
    
    #current game statut
    game_data['end_game'] = ['', False]
    
    #Adding abandonned spaceships to the game data and adding them in the board data
    for spaceship in content[1:]:
        data_spaceship = spaceship.strip().split(' ')
        spaceship_position = [int(data_spaceship[0]),int(data_spaceship[1])]
        content = data_spaceship[2].split(':')
        spaceship_name = content[0]
        spaceship_type = content[1]
        game_data['spaceships'][spaceship_name] = {'type':spaceship_type,
                                                   'owner':'none',
                                                   'health':game_data['spaceships_stats'][spaceship_type]['max_health'],
                                                   'speed': 0,
                                                   'position':spaceship_position,
                                                   'direction':data_spaceship[3],
                                                   'next_moves': []}
        
        game_data['board'][(spaceship_position[0], spaceship_position[1])].append(spaceship_name)
        game_data['all_spaceships'].append(spaceship_name)
        game_data['all_abandonned_spaceships'][spaceship_name] = game_data['spaceships'][spaceship_name]['position']
    
    game_data['statut_connection'] = False
    
    if types[0] == 'remote' or types[1] == 'remote':
        if ip != None:
           game_data['connection'] = connect_to_player(player_ID, ip, True)
           
        else: 
            game_data['connection'] = connect_to_player(player_ID)
             
        game_data['statut_connection'] = True
    
    print_board(game_data)
    
    return game_data
    
def create_fleet(game_data):
    """Creating a fleet a the beginning of the game, and placing them on the game board
    
    Parameters:
    -----------
    game_data: contain all the information about the game (dict)
    
    return:
    -------
    game_data: contain all the information about the game (dict)
    
    Version:
    --------
    Specification: Bastien Nicolas, Thomas Bouteille, Aurélien Champagne (v0.1, 03/04/2017)
    Implémentation: Bastien Nicolas (v0.1, 18/04/17)
    """
    #get player input
    if game_data['players'][game_data['player_turn']]['player_type'] == 'advanced_ai':
        orders = advanced_ai(game_data, 'create_fleet')
        if game_data['statut_connection']:
            notify_remote_orders(game_data['connection'], orders)
            
    elif game_data['players'][game_data['player_turn']]['player_type'] == 'basic_ai':
        orders = basic_ai(game_data, 'create_fleet')
        if game_data['statut_connection']:
            notify_remote_orders(game_data['connection'], orders)
        
    elif game_data['players'][game_data['player_turn']]['player_type'] == 'remote':
        orders = get_remote_orders(game_data['connection'])
        
    else:
        orders = get_player_input()
        if game_data['statut_connection']:
            notify_remote_orders(game_data['connection'], orders)
    
    player_orders = split_orders(orders)
    
    for order in player_orders:
        spaceship_name = order[0]
        spaceship_type = order[1]
        
        #Check if a player as already a spaceship with the same name
        check_data_spaceships = 0
        for spaceship in game_data['spaceships']:
            if spaceship == spaceship_name:
                check_data_spaceships = 1
        
        #Setting the initial position for the spaceships of the player 1
        if game_data['player_turn'] == '1':
            spaceship_position = [10, 10]
            spaceship_direction = 'down-right'
            
        #Setting the initial position for the spaceships of the player 2
        else:
            spaceship_position = [game_data['game_size'][0]-9, game_data['game_size'][1]-9]
            spaceship_direction = 'up-left'
        
        #Removing the good amount of money
        game_data['players'][game_data['player_turn']]['money'] -= game_data['spaceships_stats'][spaceship_type]['price']
        
        #Adding the player spaceships into the game_data
        if not check_data_spaceships == 1 and game_data['players'][game_data['player_turn']]['money'] >= 0:
            game_data['spaceships'][spaceship_name]={'type':spaceship_type,
                                                     'owner':game_data['player_turn'],
                                                     'health':game_data['spaceships_stats'][spaceship_type]['max_health'],
                                                     'speed': 0,
                                                     'position':spaceship_position,
                                                     'direction':spaceship_direction,
                                                     'next_moves': []}
                
            
            #Adding the player's spaceship into his inventory
            game_data['players'][game_data['player_turn']]['list_spaceships'] += [spaceship_name]
            
            #Adding the spaceship onto the board
            game_data['board'][(spaceship_position[0], spaceship_position[1])].append(spaceship_name)
            
            game_data['all_spaceships'].append(spaceship_name)
    
    #Reseting the players money account
    game_data['players'][game_data['player_turn']]['money'] = 0
    
    #changing player turn
    if game_data['player_turn'] == '1':
        game_data['player_turn'] = '2'
    else:
        game_data['player_turn'] = '1'
    
    print_board(game_data)
    
    #new game_data
    return game_data


def print_board(game_data):
    """Display the game board
    
    Parameters:
    -----------
    game_data: contain all the information about the game (dict)
    
    Version:
    --------
    Specification: Bastien Nicolas, Thomas Bouteille, Aurélien Champagne (v0.1, 03/04/2017) 
    Implémentation: Champagne Aurelien (v0.1, 31/03/2017)
                    Bastien Nicolas (v0.2, 18/04/2017)
    """  
    sentence = ''
    all_spaceships = game_data['all_spaceships']
    players_spaceships = []
    
    for spaceship in all_spaceships:
        if not game_data['spaceships'][spaceship]['owner'] == 'none':
            players_spaceships += [spaceship]
            
    turn_actions = game_data['turn_actions']
    space1 = 0
    space2 = False
    
    for y in range(game_data['game_size'][0]+1):
        for x in range(game_data['game_size'][1]+1):
            if not y == 0:
                if x == 0:
                    if y < 10:
                        sentence += '%s%s0%s%s '%(fg('blue'),bg('white'),str(y),attr(0))
                    else:
                        sentence += '%s%s%s%s '%(fg('blue'),bg('white'),str(y),attr(0))
                    
                elif len(game_data['board'][(y,x)]) == 0:
                    sentence += '   '
                elif len(game_data['board'][(y,x)]) == 1:
                    
                    if not game_data['spaceships'][game_data['board'][(y,x)][0]]['owner'] == 'none':
                        color = bg(game_data['players'][str(game_data['spaceships'][game_data['board'][(y,x)][0]]['owner'])]['color'])
                        sentence += '%s%s%s%s  '%(fg('white'), color,game_data['spaceships_stats'][game_data['spaceships'][game_data['board'][(y,x)][0]]['type']]['icon'], attr(0))
                    else:
                        sentence += '%s%s  '%(fg('white'),game_data['spaceships_stats'][game_data['spaceships'][game_data['board'][(y,x)][0]]['type']]['icon'])
                        
                else:
                    owner = ''
                    same_owner = True
                    for spaceship in game_data['board'][(y,x)]:
                        if owner == '':
                            owner = game_data['spaceships'][spaceship]['owner']
                        elif not owner == game_data['spaceships'][spaceship]['owner']:
                            same_owner = False
                    
                    if same_owner:
                        color = bg(game_data['players'][game_data['spaceships'][game_data['board'][(y,x)][0]]['owner']]['color'])
                    else:
                        color = bg('light_blue')
                        
                    sentence += '%s%s%s%s  '%(fg('white'), color,str(len(game_data['board'][(y,x)])),attr(0))
            else:
                if x == 0:
                    sentence += '%s   %s'%(bg('white'), attr(0))
                elif x < 10:
                    sentence += '%s%s0%s %s'%(fg('blue'),bg('white'),str(x),attr(0))
                else:
                    sentence += '%s%s%s %s'%(fg('blue'),bg('white'),str(x),attr(0))
        
        if not len(players_spaceships) == 0 and y != 0:
            state_spaceships = players_spaceships[0]
            players_spaceships = players_spaceships[1:]
            
            sentence+= '    %s'%fg(game_data['players'][game_data['spaceships'][state_spaceships]['owner']]['color'])+state_spaceships +'%s(%s): %s, %s/%s, %s, %s%s'%(attr(0), game_data['spaceships'][state_spaceships]['type'], str(game_data['spaceships'][state_spaceships]['speed']), str(game_data['spaceships'][state_spaceships]['health']), str(game_data['spaceships_stats'][game_data['spaceships'][state_spaceships]['type']]['max_health']), str(game_data['spaceships'][state_spaceships]['position']), game_data['spaceships'][state_spaceships]['direction'], ' '*20)+'\n'
                
                
        elif len(players_spaceships) == 0 and not space1 > 2:
            if space1 == 1:
                sentence +='    '+ '-'*50 + '\n'
            else:
                sentence +=' '*60+'\n'
            space1 += 1
            
        elif game_data['end_game'][1] and y != 0 and not space2:
            sentence += '    The winner is %s%s\n'%(game_data['players'][game_data['end_game'][0]]['pseudo'], ' '*30)
            space2 = True
            
        elif len(turn_actions[0]) == 0 and not space2 and not game_data['end_game'][1]:
            sentence+= '%s'%' '*50 + '\n'
            space2 = True
            
        elif not len(turn_actions[0]) == 0 and y != 0:
            action = turn_actions[0]
            turn_actions[0] = turn_actions[0][1:]
            
            if not action[0][0] in game_data['deaths_turn']:
                if game_data['spaceships'][action[0][0]]['owner'] == 'none':
                    color = 'white'
                else:
                    color = game_data['players'][game_data['spaceships'][action[0][0]]['owner']]['color']
                sentence+='    %s%s: %s%s%s'%(fg(color),action[0][0], action[0][1], attr(0), ' '*40) + '\n'
            else:
                sentence+='\n'
        
        elif not len(turn_actions[1]) == 0 and y != 0:
            action = turn_actions[1]
            turn_actions[1] = turn_actions[1][1:]
            
            if not action[0][0] in game_data['deaths_turn']:
                if game_data['spaceships'][action[0][0]]['owner'] == 'none':
                    color = 'white'
                else:
                    color = game_data['players'][game_data['spaceships'][action[0][0]]['owner']]['color']
                sentence+='    %s%s: %s%s%s'%(fg(color),action[0][0], action[0][1], attr(0), ' '*40) + '\n'
            else:
                sentence+='\n'
            
        else:
            sentence+= '%s'%' '*50 + '\n'
            
    #remove the previous turn from the screen and print the new one
    sentence = '\033[0;0H'+sentence +'\nTour: %s%s\n'%(str(game_data['turn']), ' '*40*3) +'\nDeaths: %s%s\n'%(str(game_data['deaths_turn']), ' '*40*3)
        
    print sentence

def get_player_input():
    """Get the orders from a player
    
    Return:
    -------
    player_order: orders of the player (list)
    
    Version:
    --------
    Specification: Bastien Nicolas, Thomas Bouteille, Aurélien Champagne (v0.1, 03/04/2017) 
    implementation: Champagne Aurelien (v0.1, 03/04/2017) 
    """
    player_order = raw_input('')
    
    return player_order
    

def split_orders(orders):
    """
    """
    orders = orders.split(' ')
    
    final_player_order = []
    for order in orders:
        final_player_order += [order.split(':')]
        
    return final_player_order
    
def basic_ai(game_data, action):
    """Random AI decisions
    
    Parameters
    ----------
    game_data: contain all the information about the game (dict)
    action: choose between move or create_fleet (str)
    
    Return:
    -------
    ai_order: orders of the ai (list)
    
    Version:
    --------
    Specification: Bastien Nicolas, Thomas Bouteille, Aurélien Champagne (v0.1, 03/04/2017) 
    implementation: Bastien Nicolas, Thomas Bouteille, Aurélien Champagne (v0.1, 18/04/2017)
    """
    ai_order = ''
    if action == 'move':
        move_available = ('faster', 'slower', 'fire', 'right', 'left', 'none')
        
        for spaceship in game_data['players'][game_data['player_turn']]['list_spaceships']:
            move = random.choice(move_available)
            
            if not move =='none':
                if move == 'fire':
                    move = str(random.randint(1, game_data['game_size'][0]))+'-'+str(random.randint(1, game_data['game_size'][1]))

                ai_order += spaceship +':'+ move +' '
    else:
        i=1
        while i < 6:
            types = ('fighter', 'battlecruiser', 'destroyer')

            spaceship_name = 'ship_'+game_data['players'][game_data['player_turn']]['pseudo']+'_'+str(len(game_data['players'][game_data['player_turn']]['list_spaceships'])+i)
            spaceship_type = random.choice(types)

            ai_order += spaceship_name + ':' + spaceship_type + ' '
            i+=1
        
    return ai_order[:-1]

def advanced_ai(game_data, action):
    """More evolved AI decisions
    
    Return:
    -------
    AI_order: orders of the AI (list)
    
    Version:
    --------
    Specification: Bastien Nicolas, Thomas Bouteille, Aurélien Champagne (v0.1, 03/04/2017) 
    implementation: Champagne Aurelien (v0.1, 18/04/2017)  
                    Bastien Nicolas, Thomas Bouteille, Aurélien Champagne (v0.1, 21/04/2017)
                    Bastien Nicolas (v0.3, 28/04/2017)
    """
    ai_order = ''
    spaceships_ai = ('battlecruiser', 'battlecruiser', 'destroyer', 'fighter', 'fighter')
    
    if action == 'create_fleet':
        for i in range(1, len(spaceships_ai)+1):
            spaceship_name = 'ship_'+game_data['players'][game_data['player_turn']]['pseudo']+'_'+str(len(game_data['players'][game_data['player_turn']]['list_spaceships'])+i)
            spaceship_type = spaceships_ai[i-1]
            
            ai_order += spaceship_name + ':' + spaceship_type + ' '
        
    else:
        ai_order = ''
        for spaceship in game_data['players'][game_data['player_turn']]['list_spaceships']:
            if len(game_data['spaceships'][spaceship]['next_moves']) == 0:
                start_path = {'spaceship' : spaceship, 'position': game_data['spaceships'][spaceship]['position'], 'direction': game_data['spaceships'][spaceship]['direction'], 'speed': game_data['spaceships'][spaceship]['speed'], 'max_speed': game_data['spaceships_stats'][game_data['spaceships'][spaceship]['type']]}
                
                check_target = abandonned_ships_nearby(game_data, spaceship)
                    
                for already_use_target in game_data['players'][game_data['player_turn']]['ai_focus']:
                    if already_use_target in check_target:
                        del check_target[already_use_target]
                
                end_path = find_target(game_data, check_target, spaceship)
                
                next_moves = []
                if len(end_path) != 0:
                    
                    game_data['players'][game_data['player_turn']]['ai_focus'][end_path] = game_data['spaceships'][end_path]['position']
                    next_moves = path_finding(game_data, start_path, game_data['spaceships'][end_path]['position'], game_data['game_size'])
                    
                if len(next_moves) == 0:
                    if game_data['spaceships'][spaceship]['speed'] == 0:
                        next_moves = ['faster']
                    
                    elif game_data['spaceships'][spaceship]['direction'] == 'down' or game_data['spaceships'][spaceship]['direction'] == 'up':
                        choice = ('left', 'right')
                        next_moves = [random.choice(choice)]
                        
                    else:
                        next_moves = ['none']
                    
                    
                move = next_moves[0]
                
                if move == 'none':
                    check_target = ennemy_ships_in_range(game_data, spaceship)
                    
                    if len(check_target) != 0:
                        end_path = find_target(game_data, check_target, spaceship)
                        
                        futur_position = changing_position(game_data, end_path, game_data['spaceships'][end_path]['position'], game_data['spaceships'][end_path]['direction'], game_data['spaceships'][end_path]['speed'])
                        
                        move = '%s-%s'%(str(futur_position[0]),str(futur_position[1]))
                
                game_data['spaceships'][spaceship]['next_moves'] = next_moves[1:]
                
            else:
                move = game_data['spaceships'][spaceship]['next_moves'][0]
                game_data['spaceships'][spaceship]['next_moves'] = game_data['spaceships'][spaceship]['next_moves'][1:]
                
                if move == 'none':
                    check_target = ennemy_ships_in_range(game_data, spaceship)
                    
                    if len(check_target) != 0:
                        end_path = find_target(game_data, check_target, spaceship)
                        
                        futur_position = changing_position(game_data, end_path, game_data['spaceships'][end_path]['position'], game_data['spaceships'][end_path]['direction'], game_data['spaceships'][end_path]['speed'])
                        
                        move = '%s-%s'%(str(futur_position[0]),str(futur_position[1]))
            
            ai_order += spaceship + ':' + move + ' '
            
            
        #Check if an ennemi ship is in range
        #ennemy_ship_in_range = ennemy_ship_in_range(game_data)
        #if len(ennemy_ship_in_range) != 0:
            #for i in range(0, len(ennemy_ship_in_range)+1):
                #ai_order += ennemy_ship_in_range[i][0]+'faster '
            #Check if the ai ship is in the range of the ennemi ship
            #if ship_in_ennemy_range(game_data):
                #Determine whether to shot at ennemi ship or run depending of the position of the ship and the strengh of the ennemi ship
                #run_or_gun(game_data)
        #look for the closest abandonned spaceship and go capture it
        #elif abandonned_ship_nearby(game_data):
            #go toward it
        #look if there is a focus of an ennemi ship
        #elif game_data['ai_focus'] == "":
            #if there is no focus, find one
            #find_target(game_data)
        #go take down the focused ship
        #else:
    return ai_order[:-1]
    
def path_finding(game_data, start_path, end_path, game_size, next_orders = []):
    """calcul the sequence of commands of a ship to make him reach a target
    
    Parameters:
    -----------
    game_data : contain all the information about the game (dict)
    start_path: information about the orders of a ship (dict)
    end_path:
    game_size:     
    next_orders:
        
    Return:
    -------
    

    """
    best_choice = ['', [], '']
    ship_name = start_path['spaceship']
    start_position = start_path['position']
    actions = ['faster', 'slower', 'left', 'right', 'none']
    
    if start_position == end_path or len(next_orders) == 15:
        return next_orders
        
    else:
        check_position = {}
        for action in actions:
            if action == 'faster' and start_path['speed'] < game_data['spaceships_stats'][game_data['spaceships'][ship_name]['type']]['max_speed']:
                check_position[action] = [changing_position(game_data, ship_name, start_position, start_path['direction'], start_path['speed']+1), start_path['direction']]
                
            elif action == 'slower' and start_path['speed'] != 0:
                check_position[action] = [changing_position(game_data, ship_name, start_position, start_path['direction'], start_path['speed']-1), start_path['direction']]
                
            elif action == 'left':
                new_direction = rotating(ship_name, action, start_path['direction'], game_data)
                check_position[action] = [changing_position(game_data, ship_name, start_position, new_direction, start_path['speed']), new_direction]
                
            elif action == 'right':
                new_direction = rotating(ship_name, action, start_path['direction'], game_data)
                check_position[action] = [changing_position(game_data, ship_name, start_position, new_direction, start_path['speed']), new_direction]
                
            elif action == 'none':
                check_position[action] = [changing_position(game_data, ship_name, start_position, start_path['direction'], start_path['speed']), start_path['direction']]
                
        for position in check_position:
                
            if len(best_choice[0]) == 0 or get_distance(end_path, check_position[position][0], game_size) == 0:
                best_choice[0] = position #name of the command
                best_choice[1] = check_position[position][0] #coord after the command
                best_choice[2] = check_position[position][1] #direction after the command
                
            elif (end_path[1] == start_position[1] or end_path[0] == start_position[0]) and (start_path['direction'] != 'down' or start_path['direction'] != 'up'):
                if start_path['direction'] == 'up-left' or start_path['direction'] == 'down-right':
                    best_choice[0] = 'right'
                    best_choice[1] = check_position['right'][0]
                    best_choice[2] = check_position['right'][1]
                    
                elif start_path['direction'] == 'up-right' or start_path['direction'] == 'down-left':
                    best_choice[0] = 'left'
                    best_choice[1] = check_position['left'][0]
                    best_choice[2] = check_position['left'][1]
                    
            #elif check_position['left'][0][1] == end_path[1] and check_position['left'][0][0] == end_path[0] and start_path['direction'] == 'down-right':
                #best_choice[0] = 'left'
                #best_choice[1] = check_position['left'][0]
                #best_choice[2] = check_position['left'][1]
                
            #elif check_position['right'][0][1] == end_path[1] and check_position['left'][0][0] == end_path[0] and start_path['direction'] == 'down-left':
                #best_choice[0] = 'right'
                #best_choice[1] = check_position['right'][0]
                #best_choice[2] = check_position['right'][1]
                    
            elif end_path[1] > start_position[1] and start_path['direction'][-5:] != 'right':
                best_choice[0] = 'left'
                best_choice[1] = check_position['left'][0]
                best_choice[2] = check_position['left'][1]
                
            elif end_path[1] < start_position[1] and start_path['direction'][-4:] != 'left':
                best_choice[0] = 'right'
                best_choice[1] = check_position['right'][0]
                best_choice[2] = check_position['right'][1]
                
            elif get_distance(start_position, check_position[position][0], game_size) > get_distance(start_position, best_choice[1], game_size):
                best_choice[0] = position
                best_choice[1] = check_position[position][0]
                best_choice[2] = check_position[position][1]
                
        if best_choice[0] == 'faster':
            start_path['speed'] += 1
            
        elif best_choice[0] == 'slower':
            start_path['speed'] -= 1
            
        elif best_choice[0] == 'left' or best_choice[0] == 'right':
            start_path['direction'] = best_choice[2]
            
        start_path['position'] = best_choice[1]
        
        return path_finding(game_data, start_path, end_path, game_size, next_orders+[best_choice[0]])
    
def ennemy_ships_in_range(game_data, spaceship):
    """Check if there are ennemy ships in range of a spaceship
    
    Parameters
    ----------
    game_data: contain all the information about the game (dictionnary)
    spaceship: the ai's spaceship (str)
    
    Returns
    -------
    result:
    """
    spaceship_position = game_data['spaceships'][spaceship]['position']
    result = {}
    
    X = Y = game_data['spaceships_stats'][game_data['spaceships'][spaceship]['type']]['range']*2
    x = y = 0
    dx = 0
    dy = -1
    for i in range(max(X, Y)**2):
        if (-X/2 < x <= X/2) and (-Y/2 < y <= Y/2):
            
            spaceship_position = [spaceship_position[0]+y, spaceship_position[1]+x]
            spaceship_position = check_corner(game_data, spaceship_position)
            
            if len(game_data['board'][(spaceship_position[0], spaceship_position[1])]) != 0:
                for case_spaceship in game_data['board'][(spaceship_position[0], spaceship_position[1])]:
                    if game_data['spaceships'][case_spaceship]['owner'] != 'none' and game_data['spaceships'][case_spaceship]['owner'] != game_data['spaceships'][spaceship]['owner']:
                        result[case_spaceship]=game_data['spaceships'][case_spaceship]['position']
                        
        if x == y or (x < 0 and x == -y) or (x > 0 and x == 1-y):
            dx, dy = -dy, dx
        x, y = x+dx, y+dy
        
    return result
    
def abandonned_ships_nearby(game_data, spaceship):
    """Check if there is an abandonned spacehips in range of the ai's ship
    
    Parameters
    ----------
    game_data: contain all the information about the game (dictionnary)
    spaceship: the ai's spaceship (str)
    
    Returns
    -------
    result:
        
    Version:
    -------
    Specification: Bastien Nicolas, Thomas Bouteille, Aurélien Champagne (v0.1, 03/04/2017) 
    Implémentation: Bastien Nicolas (v0.1, 27/04/2017)     
    """
    result = {}
    
    for y in range(1, game_data['game_size'][0]+1):
        for x in range(1, game_data['game_size'][1]+1):
            if len(game_data['board'][(y, x)]) != 0:
                for case_spaceship in game_data['board'][(y, x)]:
                    if game_data['spaceships'][case_spaceship]['owner'] == 'none':
                        result[case_spaceship]=game_data['spaceships'][case_spaceship]['position']
        
    return result
    
def ship_in_ennemy_range(game_date):
    """
    
    """
    
def run_or_gun(game_data):
    """
    
    """

def find_target(game_data, possible_target, spaceship):
    """Find the closest target of a spaceship
    
    Parameters
    ----------
    game_data:
    possible_target:
    spaceship:
    
    Returns
    -------
    target:
    
    Version
    -------
    Spécification: Bastien Nicolas (v0.1, 28/04/2017)
    Implémentation: Bastien Nicolas (v0.1, 28/04/2017)
    """
    target = ''
    game_size = game_data['game_size']
    for coord_spaceship in possible_target:
        if target == '':
            target = coord_spaceship
        elif get_distance(game_data['spaceships'][target]['position'],game_data['spaceships'][spaceship]['position'], game_size) > get_distance(possible_target[coord_spaceship], game_data['spaceships'][spaceship]['position'], game_size) and get_distance(possible_target[coord_spaceship], game_data['spaceships'][spaceship]['position'], game_size) != 0:
            target = coord_spaceship
            
    return target
        
def get_distance (target_1, target_2, size):
    """
    """
    return distance(int(target_1[0]), int(target_2[0]), int(size[0])) + distance(int(target_1[1]), int(target_2[1]), int(size[1]))

def distance(a, b, size):
    """
    """
    size -= 1
    if abs(a - b) > size / 2:
        a += size
    
    return abs(a - b)
    
def motion(order, game_data):
    """Perform spaceships's movements (attack, acceleration, direction, brake)
    
    Parameters:
    -----------
    order: a list with all the orders (list)
    game_data: contain all the information about the game (dict)
    
    Return:
    -------
    game_data: contain all the information about the game (dict)
    
    Version:
    --------
    Specification: Bastien Nicolas, Thomas Bouteille, Aurélien Champagne (v0.1, 03/04/2017)
    Implementation : Thomas Bouteille (v0.2, 19/03/2017) 
    """
    order = split_orders(order)
    already_play_spaceships = []
    game_data['deaths_turn'] = []
    #Execute the code if and only if the user has given orders
    if order[0] != ['']:
        #Loop to make all the orders
        for movement in order:
            ship_name = movement[0]
            ship_order = movement[1]
            
            command_execute = True
            
            for ship in already_play_spaceships:
                if ship_name == ship:
                    command_execute = False
            
            already_play_spaceships.append(ship_name)
                    
            if not game_data['spaceships'][ship_name]['owner'] == 'none' and command_execute:
            #Determine which order to execute
                if ship_order == 'faster':
                    accelerating(ship_name, game_data)
                elif ship_order == 'slower':
                    breaking(ship_name, game_data)
                elif ship_order == 'left' or ship_order == 'right':
                    game_data['spaceships'][ship_name]['direction'] = rotating(ship_name, ship_order, game_data['spaceships'][ship_name]['direction'], game_data)
                    
                #The fire order is encode by the user with a '-', the program will check later if it is possible the shot this position or if the position even exist
                elif '-' in ship_order:
                    fire(ship_name, ship_order, game_data) 
      
    #Change player turn and refresh the board if both player have made their order
    if game_data['player_turn'] == '2':
        game_data['player_turn'] = '1'
        game_data['turn_actions'][1] = order
        game_data['turn'] += 1 #add a turn to the game
        refresh_game_data(game_data)
        shoot_target_location(game_data)
        end_game(game_data)
        print_board(game_data)
        game_data['turn_actions'] = [[], []]
        time.sleep(0.4)
    else: 
        game_data['player_turn'] = '2'
        if order[0] != ['']:
            game_data['turn_actions'][0] = order
        
    #Check if the game is over or not  
    return game_data
            
         
def refresh_game_data(game_data):
    """Make the ships change position if they are moving
    
    Parameters:
    -----------
    game_data : Contain all the information about the game(dict)
    
    Versions
    --------
        specification: Bouteille Thomas (v0.1, 24/02/17)
        implementation: Bouteille Thomas (v0.1, 24/02/17)
                        Nicolas Bastien (v0.2, 26/04/17)
    """
    
    for ship_name in game_data['spaceships']:
    #Change the position all the ship depending of their speed and direction
        old_position = game_data['spaceships'][ship_name]['position']
        ship_direction = game_data['spaceships'][ship_name]['direction']
        ship_speed = game_data['spaceships'][ship_name]['speed']
        current_position = old_position    
        
        #If the spaceships is abandoned it doesn't move so game_data modifications are useless
        if game_data['spaceships'][ship_name]['owner'] != 'none':
            
            current_position = changing_position(game_data, ship_name, current_position, ship_direction, ship_speed)
            
            #Edit the ship's position
            game_data['spaceships'][ship_name]['position'] = current_position
            
            #Edit the game_board
            current_position =  game_data['spaceships'][ship_name]['position']
            game_data['board'][(old_position[0], old_position[1])].remove(ship_name)
            game_data['board'][(current_position[0], current_position[1])].append(ship_name)
            
       
        else:
            players_ships = [0,0]
            all_ships_on_position = game_data['board'][(current_position[0], current_position[1])]
            #Take all the ship in this position
            for ships in all_ships_on_position:
                
                ship_owner = game_data['spaceships'][ships]['owner']
                #Dertermine if the ship belong to the first or to the second player
                if ship_owner == '1':
                    players_ships[0] += 1
                elif ship_owner == '2':
                    players_ships[1] += 1
            
            #Check if there are 2 ships from different players on the same case
            if players_ships[0] == 0 and players_ships[1] != 0:
                game_data['spaceships'][ship_name]['owner'] = '2'
                game_data['players'][game_data['spaceships'][ship_name]['owner']]['list_spaceships'] += [ship_name]
                
                if ship_name in game_data['players']['1']['ai_focus']:
                    del game_data['players']['1']['ai_focus'][ship_name]
                    
                elif ship_name in game_data['players']['2']['ai_focus']:
                    del game_data['players']['2']['ai_focus'][ship_name]
                    
                del game_data['all_abandonned_spaceships'][ship_name]
                
            elif players_ships[1] == 0 and players_ships[0] != 0:
                game_data['spaceships'][ship_name]['owner'] = '1'
                game_data['players'][game_data['spaceships'][ship_name]['owner']]['list_spaceships'] += [ship_name]
                
                if ship_name in game_data['players']['1']['ai_focus']:
                    del game_data['players']['1']['ai_focus'][ship_name]
                elif ship_name in game_data['players']['2']['ai_focus']:
                    del game_data['players']['2']['ai_focus'][ship_name]
                    
                del game_data['all_abandonned_spaceships'][ship_name]
                
def changing_position(game_data, ship_name, current_position, ship_direction, ship_speed):
    """Changing the position of the ship with is actual position and speed
    
    Parameters
    ----------
    game_data:
    ship_name:
    current_position:
        
    Returns
    -------
    current_position:
        
    Versions
    --------
    specifications:Bastien Nicolas, Thomas Bouteille, Aurélien Champagne (v0.1, 03/04/2017)
    implementation: Bouteille Thomas (V0.1, 03/04/17)
                    Bastien Nicolas (v0.2, 26/04/17)
    """
    
    ship_x_position = current_position[1]
    ship_y_position = current_position[0]
    
    #up
    if ship_direction == 'up':
        current_position = [ship_y_position - ship_speed, current_position[1]]
    #up-right
    elif ship_direction == 'up-right':
        current_position = [ship_y_position - ship_speed, ship_x_position + ship_speed]
    #right
    elif ship_direction == 'right':
        current_position = [current_position[0], ship_x_position + ship_speed]
    #down-right
    elif ship_direction == 'down-right':
        current_position = [ship_y_position + ship_speed, ship_x_position + ship_speed]
    #down
    elif ship_direction == 'down':
        current_position = [ship_y_position + ship_speed, current_position[1]]
    #down-left
    elif ship_direction == 'down-left':
        current_position = [ship_y_position + ship_speed, ship_x_position - ship_speed]
    #left
    elif ship_direction == 'left':
        current_position = [current_position[0], ship_x_position - ship_speed]
    #up-left
    else:
        current_position = [ship_y_position - ship_speed, ship_x_position - ship_speed]
    
    check_corner(game_data, current_position)
    
    return current_position
    
def check_corner(game_data, current_position):
    """
    """
    game_border = [game_data['game_size'][0], game_data['game_size'][1]]
    
    #Check if the ship is not on the edge of the upper or the bottom border, change the position if the ship has overextended the border
    delta_y = current_position[0]
    if delta_y > game_border[0]:
        delta_y = delta_y - game_border[0]
    elif delta_y <= 0:
        delta_y = game_border[0] - abs(delta_y)
    current_position[0] = delta_y
    
    #Check if the ship is not on the edge of the right or the left border, change the position if the ship has overextended the border
    delta_x = current_position[1]
    if delta_x > game_border[1]:
        delta_x = delta_x - game_border[1]
    elif delta_x <= 0:
        delta_x = game_border[1] - abs(delta_x)
    current_position[1] = delta_x
    
    return current_position
               
def accelerating(ship_name, game_data):
    """Accelerate the speed of the ship by 1
    
    Parameters:
    -----------
        ship_name : the name of the ship (str)
        game_data : the dictionary containing all the data for the game (dict)
        
    Notes:
    ------
        can't accelerate more than the maximum speed of the ship
        
    Versions
    --------
        specification: Bouteille Thomas (v0.1, 24/02/17)
        implementation: Bouteille Thomas (v0.1, 24/02/17)
    """
    #take the type and the current speed of the ship
    ship_type = game_data['spaceships'][ship_name]['type']
    ship_speed = game_data['spaceships'][ship_name]['speed']
    
    #take the maximum speed that the ship can have
    max_speed = game_data['spaceships_stats'][ship_type]['max_speed']
    
    #Check if the maximum speed is not already reached, raise an error if so
    if ship_speed <= max_speed:
        game_data['spaceships'][ship_name]['speed'] +=1
    
    
def breaking(ship_name, game_data):    
    """Slow down the speed of the ship by 1
    
    Parameters:
    -----------
        ship_name : the name of the ship (str)
        game_data : the dictionary containing all the data for the game (dict)
        
    Notes:
    ------
        Can't break anymore if the ship is at null speed
        
    Versions
    --------
        specification: Bouteille Thomas (v0.1, 24/02/17)
        implementation: Bouteille Thomas (v01,24/02/2017)
    """
    #take the current speed of the ship
    ship_speed = game_data['spaceships'][ship_name]['speed']
    #Check if the ship is not at nul speed
    if ship_speed > 0:
        game_data['spaceships'][ship_name]['speed'] -=1
     
        
def rotating(ship_name, direction, old_direction, game_data):
    """Rotate the ship in the given direction
    
    Parameters:
    -----------
        ship_name : The name of the ship (str)
        direction : The direction of rotation (str)
        game_data : the dictionary containing all the data for the game (dict)
        
    Notes:
    ------
        Rotation of 45° to one direction
        
    Versions
    --------
        specification: Bouteille Thomas (v0.1, 24/02/17)
        implementation: Bouteille Thomas(v0.1, 24/02/2017)
    """
        
    #if the ship is looking to the right, take the current looking direction and make it turn to the right
    if direction == 'right':
        if old_direction == 'up':
            new_direction = 'up-right'
        elif old_direction == 'up-right':
            new_direction = 'right'
        elif old_direction == 'right':
            new_direction = 'down-right'
        elif old_direction == 'down-right':
            new_direction = 'down'
        elif old_direction == 'down':
            new_direction = 'down-left'
        elif old_direction == 'down-left':
            new_direction = 'left'
        elif old_direction == 'left':
            new_direction = 'up-left'
        else:
            new_direction = 'up'
    #if the ship is looking to the left, take the current looking direction and make it turn to the left
    else:
        if old_direction == 'up':
            new_direction = 'up-left'
        elif old_direction == 'up-right':
            new_direction = 'up'
        elif old_direction == 'right':
            new_direction = 'up-right'
        elif old_direction == 'down-right':
            new_direction = 'right'
        elif old_direction == 'down':
            new_direction = 'down-right'
        elif old_direction == 'down-left':
            new_direction = 'down'
        elif old_direction == 'left':
            new_direction = 'down-left'
        else:
            new_direction = 'left'
            
    return new_direction


def fire(ship_name, fire_position, game_data):
    """Open fire with the ship
    
    Parameters:
    -----------
        ship_name : The name of the ship (str)
        fire_position : the position where the ship much shoot (str)
        game_data : the dictionary containing all the data for the game (dict)
        
    Notes:
    ------
        The range of the fire depends on the ship stats
        
    Versions
    --------
        specification: Bouteille Thomas (v0.1, 24/02/17)
        implementation: Bouteille Thomas (v0.1, 21/03/2017)
    """
    
    #Variables initialization
    fire_coordinates = fire_position.split('-') #Coordinates where the ship much shoot at
    fire_coordinates = (int(fire_coordinates[0]), int(fire_coordinates[1])) #Change the type of the element in the list from string to int
    
    ship_type = game_data['spaceships'][ship_name]['type']
    attack_damage = game_data['spaceships_stats'][ship_type]['damages'] #The number of domage that the ship does
    ship_position = game_data['spaceships'][ship_name]['position'] #The position of the ship which is firing
    ship_range = game_data['spaceships_stats'][ship_type]['range'] #The maximum range of the ship which is firing
 
    desired_range = abs(fire_coordinates[0] - ship_position[0]) + abs(fire_coordinates[1] - ship_position[1]) #The range that the ship much shoot at
    
    #check if the desiered_range is lower than the actual range of the ship
    if desired_range <= ship_range:
        game_data['players'][game_data['player_turn']]['locked_fire_position'].append([fire_coordinates[0], fire_coordinates[1], attack_damage]) #Lock the fire coordonates for the next turn and the domage of the attack
    
def shoot_target_location(game_data):
    """Shoot the previously locked locations
    
    Parameters:
    -----------
       game_data : the dictionary containing all the data for the game (dict)
       
    Versions
    --------
        specification: Bouteille Thomas (v0.1, 24/02/17)
        implementation: Bouteille Thomas (v0.1, 24/02/17)
    """
    for player in ('1', '2'):
        for target in game_data['players'][player]['locked_fire_position']:
            #Variables initialization
            fire_location = (target[0], target[1])
            attack_damage = target[2]
            ship_on_target = game_data['board'][fire_location]
    
            #check if there is a ship on the location target
            for ship in ship_on_target:
                game_data['spaceships'][ship]['health'] -= attack_damage #Subtracted the health of the targeted ship to the attack domage
                game_data['turn'] = 0
                
                if game_data['spaceships'][ship]['health'] < 1:
                    game_data['all_spaceships'].remove(ship)
                    game_data['players'][game_data['spaceships'][ship]['owner']]['list_spaceships'].remove(ship)
                    spaceship_position = game_data['spaceships'][ship]['position']
                    game_data['board'][(spaceship_position[0], spaceship_position[1])].remove(ship)
                    game_data['deaths_turn'].append(ship)
                    del game_data['spaceships'][ship]
                    
        game_data['players'][player]['locked_fire_position'] = []
    
    
#A revoir
def end_game(game_data):
    """Final game screen that display the results of the game
    
    Parameters:
    -----------
    game_data: contain all the information about the game (dict)
    
    Notes:
    ------
    The player who don't have any ship left lose
    If no more attack after 10 rounds then the players who has the largest fleet win
    If both players have the same score then random winner
    
    Version:
    --------
    Specification: Bastien Nicolas, Thomas Bouteille, Aurélien Champagne (v0.1, 03/04/2017) 
    implementation : Champagne Aurelien (v0.1, 03/03/2017)
                   
    """
    if game_data['turn'] > 1:

        if game_data['turn']==10:
            #Loop to get the price of each ship and sum them for each player
            money = [0,0]
            for ship_name in game_data['spaceships']:
                ship_type = game_data['spaceships'][ship_name]['type']
                ship_price = game_data['spaceships_stats'][ship_type]['price']
                if game_data['spaceships'][ship_name]['owner'] == '1':
                    money[0] += ship_price
                elif game_data['spaceships'][ship_name]['owner'] == '2':
                    money[1] += ship_price
                    
            if money[0] == money[1]:
                if random.randint(1,2) == 1:
                    winner = '1'
                else:
                    winner = '2'
                                                          
            elif money[0] > money[1]:
                winner = '1'
            else:
                winner = '2'  

            game_data['end_game'] = [winner, True]
            
        elif len(game_data['players']['1']['list_spaceships']) == 0:
            game_data['end_game'] = ['2', True]
            
        elif len(game_data['players']['2']['list_spaceships']) == 0: 
            game_data['end_game'] = ['1', True]
            
        if game_data['statut_connection'] and game_data['end_game'][1]:
            disconnect_from_player(game_data['connection'])
    
main('cis.cis', ('moi', 'remote'), ('advanced_ai', 'remote'), 2, '138.48.160.133')
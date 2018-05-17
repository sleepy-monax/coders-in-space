#test IA
# -*- coding: utf-8 -*-

    
#Import
from random import randint
from copy import deepcopy, copy
import termcolor

import remote_play


##Ex. of a configuration_file
fh= open ('config_file.mw','w')
fh.write('size:\n')
fh.write('27 20\n')
fh.write('portals:\n')
fh.write('4 5\n')
fh.write('21 9\n')
fh.write('asteroids:\n')
fh.write('1 2 24 1\n')
fh.write('8 7 10 2\n')
fh.write('4 12 11 1\n')
fh.write('16 15 10 2\n')
fh.write('10 16 10 2\n')
fh.write('15 3 10 2\n')
fh.write('25 10 10 2\n')
fh.close()
name_file ='config_file.mw'

def create_ds_game_board (name_file):
    """Create the data structure which will be used to show the current game to the users. 
    Parameters
    ----------
    name_file: the path of the file to read which contains the instructions of the game (str)
    Returns
    -------
    game_board: the data structure which contains all the informations about the game (dict)
    Notes
    -----
    game_board={'size_board':(20, 30),
            'portail_1':{'coordinates': (4,3), 'health':8},
            'portail_2':{'coordinates':(8,2), 'health':20}, 
            'asteroide':{(5,5):{'tonnage_tour':1, 'capacité_max':24},(8,1):{'tonnage':2, 'capacité_max':12}}}            
    The .mw file has exactly three parts: Size(One element), Portails(Two elements), Asteroids(Every asteroids)

    Specification
    Maï (v1: 05/03/2018)
    Maï (v2: 27/03/2018)
    Implementation
    Maï (v1: 30/03/2018)
    
    """
    #copy the rules of the game
    fh= open(name_file, 'r')
    copy_rules= fh.readlines()      #copy_rules=['size:\n','']
    fh.close()

    game_board={'asteroids':{}} 
    while len(copy_rules) > 1:    
        first_rule= copy_rules[1].split('\n')[0]
        lines= first_rule.split(' ')[0]
        columns = first_rule.split(' ')[1]      
        coordinates=(int(lines), int(columns)) 
    
        if str.startswith(copy_rules[0],'size:\n'):          
            game_board['size_board']=coordinates    #board_game={'size_board':('20','30')}
            copy_rules= copy_rules[2:]         #change the condition of the loop, delete copy_rules[0,1]  
                  
        elif str.startswith(copy_rules[0], 'portals:\n'): 
            if str.startswith(copy_rules[2], 'asteroids:\n'):
                game_board['portail_2']={'coordinates': coordinates, 'health':100, 'area': find_area(list(coordinates),'portail')}
                copy_rules= copy_rules[2:]
            else:
                game_board['portail_1']={'coordinates': coordinates, 'health':100, 'area': find_area(list(coordinates),'portail')}
                del copy_rules[1] 
                                
        else: 
     
            info_asteroid={'tonnage_round':int(first_rule.split(' ')[3]),'max_capacity':int(first_rule.split(' ')[2])}
            game_board['asteroids'][coordinates]= info_asteroid           
            #change the condition of the loop
            del copy_rules[1]
    return game_board

def buy_ship(type_ship, name_ship, name_player, ship_players, players, game_board, list_of_ship):
    """Modifie the gamer's ore and give him a ship.
    Parameters
    ----------
    type_ship: the type  of the wanted ship (str)
    name_ship: the name of the new ship (str)
    name_player: the name of the player which has bought the ship (player_1 or player_2) (str)
    players: the data structure of the players which contains the informations about the players (dict)
    ship_players: the data structure which contains all the names of the ships (dict)
    game_board: the data structure which contains all the informations about the game (dict)
    list_of_ship: the dictionnary which contains the caracteristics about the ships (dict)               
    Returns
    -------
    ship_players: the data structure which contains all the ships owned by all the players (dict)
    players: the specific data_structure about the players(dict)  
    Notes
    -----
    -type_ship has to be: scout,warship, excavator-S/M/L
    -players={player_1:{'ore':4, 'ships':{'Larry':[], 'Dany':[]}}}
    -list_of_ship={'excavator-S':{'scope':0, 'vie_initiale':2, 'attack':0, 'tonnage':1, 'cost':1}}
    
    Specification
    Sindy Willems (v1: 05/03/2018)
    Implementation
    Sindy Willems, Maï Leroy, Léopold Van Beirs (v1: 30/03/2018)       
    """
    cost_ship= list_of_ship[type_ship]['cost']  
    if cost_ship <= players[name_player]['ore']:        
        players[name_player]['ore']= players[name_player]['ore'] - cost_ship        
        
        # caracteristics of the ship to add to the  data structure     
        new_name={'health':list_of_ship[type_ship]['vie_initiale'],'type_ship': type_ship, 'owner': name_player, 'lock': False, 'actual_tonnage':0}        
        name_portail= players[name_player]['name_portail']
        new_name['coordinates']= list(game_board[name_portail]['coordinates'])
        
        #Add to the data structure
        ship_players[name_player][name_ship]= new_name        
        players[name_player]['ships'][name_ship]= find_area (list(game_board[name_portail]['coordinates']),type_ship)
    
    return (ship_players, players)
  
def lock_release(command, name_ship, name_player, ship_players, players, game_board):
    """lock or unlock an extractor on a asteroid to dump or take ore.
    Parameters
    ----------
    command: the instruction to do (str)
    name_ship: the name of the ship which locks or unlocks (str)
    ship_players: the data structure which contains the informations about the ships (dict)
    players: the data structure which contains the informations about the players (dict)
    game_board: the data structure which contains the informations about the game (dict)
    Returns
    -------
    ship_players: the data structure of the game which contains the informations about the ships (dict)
  
    Specification
    Sindy Willems (v1 05/03/2018)
    Maï Leroy (v2: 27/03/2018)
    Implementation
    Sindy Willems, Maï Leroy (v1: 30/03/2018)	
    """
    if (ship_players[name_player][name_ship]['type_ship'] != 'warship') and (ship_players[name_player][name_ship]['type_ship'] != 'scout'):
        #Verif if on the portail
        name_portail= players[name_player]['name_portail']
        if ship_players[name_player][name_ship]['coordinates'] == list(game_board[name_portail]['coordinates']):
            if command == 'lock':
                ship_players[name_player][name_ship]['lock']= True
            elif command == 'release':
                ship_players[name_player][name_ship]['lock']= False
            return (ship_players)
        #Verif if on the asteroid
        for asteroids in game_board['asteroids']:
            if ship_players[name_player][name_ship]['coordinates'] == list(asteroids) :
                if command == 'lock':
                    ship_players[name_player][name_ship]['lock']= True
                elif command == 'release':     
                    ship_players[name_player][name_ship]['lock']= False    
    return ship_players
def find_area(coordinates, type_ship):
    """Find the complete size of the ship according to its type an its middle.
    Parameters
    ----------
    coordinate_ship:  the coordinates of the ship (list)
    type_ship: the type of the ship (str)
    Returns
    -------
    area: the total size of the ship (list of list)
    Notes
    -----
    -area=[[4,5],[4,6],[4,7]]
    -coordinate_ship=[4,5]
    -type_ship can be : 'excavator-S','excavator-M','excavator-L','scout','warship' or 'portail' (str)
    
    Specification
    Maï Leroy (v1: 05/03/2018)
    Implementation
    Maï Leroy, Sindy Willems (v1: 30/03/2018)
    
    """
    area= []
    element_x , element_y= 0, 0
    
    if type_ship == 'portail':  
        for element_x in range (5):
            for element_y in range (5):
                new_coord=[coordinates[0]- 2 +element_x,coordinates[1]-2 + element_y]
                area.append(new_coord)
    
    elif type_ship =='excavator-M' or type_ship == 'excavator-L':
        area.append(coordinates) 
        new_coord_x, new_coord_y, new_coord_xy, new_coord_yx=copy(coordinates), copy(coordinates), copy(coordinates), copy(coordinates)
        
        new_coord_x[0]=new_coord_x[0] + 1
        new_coord_y[0]=new_coord_y[0] - 1
        new_coord_xy[1]= new_coord_xy[1] + 1
        new_coord_yx[1]= new_coord_yx[1] -1
        area.append(new_coord_y)
        area.append(new_coord_x)  
        area.append(new_coord_xy)
        area.append(new_coord_yx)  
        area= deepcopy(area)
        
        if type_ship == 'excavator-L':
            new_coord_x[0]=new_coord_x[0] + 1
            new_coord_y[0]=new_coord_y[0] - 1
            new_coord_xy[1]= new_coord_xy[1] + 1
            new_coord_yx[1]= new_coord_yx[1] -1
            area.append(new_coord_y)
            area.append(new_coord_x)  
            area.append(new_coord_xy)
            area.append(new_coord_yx)        
    elif type_ship == 'scout' or type_ship == 'warship' :
        element_x, element_y = 0, 0
        for element_x in range (3):
            for element_y in range (3):
                coord=[coordinates[0]- 1+element_x,coordinates[1]- 1+element_y]
                area.append(coord)
                                        
        if type_ship == 'warship':
            iteration1,iteration2= 0,0
            for iteration1 in range (2):
                element_x= copy(coordinates)
                element_x[0]= element_x[0] -2 + (4*iteration1)
                area.append(element_x)
                element_y,element_z= copy(element_x), copy(element_x)
                element_y[1]= element_y[1] + 1
                element_z[1]= element_z[1]- 1
                area.append(element_y)
                area.append(element_z)
                
            for iteration2 in range (2):
                element_x= copy(coordinates)
                element_x[1]= element_x[1] -2 + (4*iteration2)
                area.append(element_x)
                element_y,element_z= copy(element_x), copy(element_x)
                element_y[0]= element_y[0] + 1
                element_z[0]= element_z[0]- 1
                area.append(element_y)
                area.append(element_z)               
    else:
        area.append(coordinates)            
    return (area)
def update_area_ship(coordinates, type_ship,  name_ship, name_player, players):
    """ Update the players data structure which contains the data structure with the area of the ship.
    Parameters
    ----------
    coordinates: the coordinates of the ship (list)
    type_ship: the type of the ship (str)
    name_ship: the name of the ship (str)
    name_player: the name of the player (str)
    players: the data structure which contains the informations about the players (dict)
    Returns
    -------
    players: the data structure which contains the informations about the players(dict)
    
    Specification
    Maï Leroy (v1: 30/03/2018)
    Implementation
    Maï Leroy (v1: 30/03/2018)   
    """
    players[name_player]['ships'][name_ship]= find_area(coordinates, type_ship)
    return players

def move_ship(new_coordinates, name_ship, name_player, ship_players, players, game_board):
    """modifie the coordinates of the ship and change its position on the game board.
    Parameters
    ----------
    new coordinates: the wanted coordinates to move (list)
    name_ship: the name of the ship to move (str)
    name_player: the name of the player who owns the ship (str)
    ship_players: the data structure which contains the informations about the ships (dict)
    players: the data structure which contains the informations about the players (dict)
    game_board: the data structure which contains the main informations about the game (dict)   
    Returns
    -------
    ship_players: the data structure which contains the informations about the ships (dict)
    players: the data structure which contains the informations about the players (dict)
    
    Specification
    Maï Leroy (v1: 05/03/2018)
    Maï Leroy (v2: 30/03/2018)
    Sindy Willems (v3: 21/05/2018)
    Implementation
    Maï Leroy, Sindy Willems, Léopold Van Beirs (v1: 30/03/2018)
    """
    if ship_players[name_player][name_ship]['lock'] == False:   #condition to move
        area_ship= players[name_player]['ships'][name_ship]     #the total area of the ship to move    
        
        size_game= game_board['size_board']
        middle_coordinates= ship_players[name_player][name_ship]['coordinates']
        
        #check if the ship can move and is on the game board 
        if check_if_move(area_ship,new_coordinates, size_game, middle_coordinates) :
            ship_players[name_player][name_ship]['coordinates']= new_coordinates
            type_ship= ship_players[name_player][name_ship]['type_ship']    
            players= update_area_ship(new_coordinates, type_ship, name_ship, name_player, players)       
    return (ship_players, players)
def check_if_move(area_ship, new_coordinates, size_game, middle_coordinates):
    """Check if the ship can move or not and if the new coordinates are into the game board or not.
    Parameters
    ----------
    area_ship: the area of the ship to move (list)
    new_coordinates: the wanted coordinates to move (list)
    size_game: the size of the game (tuple)
    middle_coordinates: the coordinates of the middle of the ship (list)
    Returns
    -------
    True if ship can move , False otherwise (bool)
         
    Specification
    Léopold Van Beirs (v1: 05/03/2018)
    Léopold Van Beirs (v1: 30/03/2018)
    Implementation
    Léopold Van Beirs, Sindy Willems, Maï Leroy (v1: 30/03/2018)
    
    """ 
    for area in area_ship:
        if (area[0] > size_game[0]) or (area[0]< 0) or (area[1] > size_game[1]) or (area[1] < 0):
            return (False)    
    next_to= False
    #verif if next to the coordinates   
    if ((middle_coordinates[0] ==  new_coordinates[0]) and (middle_coordinates[1]+1 ==  new_coordinates[1] )) or ((middle_coordinates[0] ==  new_coordinates[0]) and (middle_coordinates[1]-1 ==  new_coordinates[1] )) :
        #go up and down 
        next_to= True
    elif ((middle_coordinates[0]+1 ==  new_coordinates[0]) and (middle_coordinates[1] ==  new_coordinates[1] )) or ((middle_coordinates[0]-1 ==  new_coordinates[0]) and (middle_coordinates[1] ==  new_coordinates[1] )):
        next_to = True
    elif ((middle_coordinates[0]+1 ==  new_coordinates[0]) and (middle_coordinates[1]+1 ==  new_coordinates[1] )) or ((middle_coordinates[0]+1 ==  new_coordinates[0]) and (middle_coordinates[1]-1 ==  new_coordinates[1] )):
        next_to = True
    elif ((middle_coordinates[0]-1 ==  new_coordinates[0]) and (middle_coordinates[1]+1 ==  new_coordinates[1] )) or ((middle_coordinates[0]-1 ==  new_coordinates[0]) and (middle_coordinates[1]-1 ==  new_coordinates[1] )):
        next_to = True
    elif ((middle_coordinates[0] ==  new_coordinates[0]) and (middle_coordinates[1] ==  new_coordinates[1] )) or ((middle_coordinates[0] ==  new_coordinates[0]) and (middle_coordinates[1] ==  new_coordinates[1] )):
        next_to = True
    return (next_to)
  
def manhattan_distance(coordinates_fire, coordinate_ship):
    """Compute the scope of the ship.
    Parameters
    ----------
    coordinates_fire: the coordinates that the player wants to attack (list)
    coordinates_ship: the coordinates of the ship which attacks (list)    
    Returns
    -------
    scope: the total scope of the ship (int)
        
    Specification
    Leopold Van Beirs (v1: 05/03/2018)
    Léopold Van Beirs (v2: 27/03/2018)
    Implementation
    Léopold Van Beirs (v1: 30/03/2018)
    
    """ 
    #find the total scope that ship can have
    r1, c1= coordinate_ship[0], coordinate_ship[1]
    r2, c2= coordinates_fire[0], coordinates_fire[1]
    compute1= r2-r1
    if compute1 < 0:
        compute1= r1-r2
    compute2= c2- c1
    if compute2 < 0:
        compute2= c1-c2
    scope= compute1 + compute2   
    return (scope)
              
def fire_ship(coordinates_fire, name_ship,name_player, ship_players, players, game_board, list_of_ship, without_dammage):
    """Cause damages to the opponent ship and reduce its points of life.    
    Parameters
    ----------
    coordinates_fire: the coordinates of the fire position (list)
    name_ship: the new name of the ship which attacks  (str) 
    name_player: the name of the player (str)
    ship_players: the data structure which contains the informations about the ships (dict)
    players: the data structure which contains the informations about the game (dict)
    game_board: the data structure which contains the informations about the game (dict)
    list_of_ships: the dictionnary which contains the caracteristics about the ships (dict)
    without_dammage: the compute value which can end the game (int)
    Returns
    -------
    ship_players: the data structure which contains the informations about the ships (dict)
    game_board: the data structure which contains the informations of the current game (dict)
    without_dammage: the compute value which can end the game (int)
    
    See also
    --------
    -Use check_if_fire, manhattan_distance
    
    Specification
    Léopold Van Beirs (v1: 05/03/2018)
    Léopold Van Beirs (v2: 27/03/2018)
    Implementation
    Léopold Van Beirs, Maï Leroy, Sindy Willems (v1: 30/03/2018)
    """  
    type_ship= ship_players[name_player][name_ship]['type_ship']  
    if (type_ship == 'scout') or (type_ship == 'warship'):
        scope= manhattan_distance(coordinates_fire, ship_players[name_player][name_ship]['coordinates'] )   #find the total scope that ship can have and use manatthan distance 
        if scope <= list_of_ship[type_ship]['scope']:         #    check if the new coordinates are reachable    
            name_affect_ship, name_affect_portail= check_if_fire(coordinates_fire,players, game_board)        #check if there is some ships/portails in the area of the scope
            if (len(name_affect_ship)>0) or (len(name_affect_portail)):
                without_dammage = 0
            for dammaged in name_affect_ship:
                dammaged= dammaged.split ('*')
                ship_players[dammaged[0]][dammaged[1]]['health']= ship_players[dammaged[0]][dammaged[1]]['health']- list_of_ship[type_ship]['attack']
            if len(name_affect_portail) > 3:
                game_board[name_affect_portail]['health']= game_board[name_affect_portail]['health']- list_of_ship[type_ship]['attack']        
    return (ship_players, game_board, without_dammage)
def check_if_fire(coordinates_fire,players, game_board):
    """Check if the fire position affects an other ship or a portail.
    Parameters
    ----------
    coordinates_fire: the coordinates that the player wants to attack (list)
    players: the data structure which contains the informations about the game (dict)
    game_board: the data structure which contains the informations of the game (dict)
    Returns
    -------
    name_affect_ship: all the ships which have been damaged (list)
    name_affect_portail: all the portails which have been damaged (list)
    
    Specification
    Sindy Willems (v1: 05/03/2018)
    Implementation
    Sindy Willems (v1: 30/03/2018)
    """   
    name_affect_portail= []
    name_affect_ship= []
    #take the names of the ships
    for name_player in players:
        for name_ship in players[name_player]['ships']:
            for area in players[name_player]['ships'][name_ship]:
                if (area[0] == coordinates_fire[0]) and (area[1] == coordinates_fire[1]):
                    name_affect_ship.append(name_player+ '*'+ name_ship)
    name_portail= 'portail'
    number= 0
    for number in range (2):
        name_portail= 'portail_' + (str(number+1))
        for area_portail in game_board[name_portail]['area']:
            if area_portail == coordinates_fire:
                name_affect_portail= name_portail    
    return (name_affect_ship, name_affect_portail)  
def load_dump (ship_players, players,game_board, list_of_ship):
    """Load or dump the ore. 
    Parameters
    ----------
    ship_players: the list which contains the ships of the players (dict)
    players: the data structure which contains the informations about the players (dict)
    game_board: the data_structure which contains the main informations about the game (dict)
    list_of_ship:the data structure which contains the caracteristics of the ships (dict)   
    Returns
    -------
    ship_players: the data_structure which contains the information about the ships (dict)
    players: the data structure which contains the informations about the players (dict)
    game_board: the data structure which contained the informations about the game (dict)
    Notes
    -----
    Excavator only can dump or load the ore on an asteroid or a portail
    
    Specification
    Sindy Willems (v1: 27/03/2018)
    Implementation
    Maï Leroy, Sindy Willems (v1: 30/03/018)
    Sindy Willems (v2: 25/04/18)
    """
    
    asteroids_capacity= {}
    for asteroid in game_board['asteroids']:
        if game_board['asteroids'][asteroid]['max_capacity'] >= 1:
            asteroids_capacity[asteroid]= {'player_1':{}, 'player_2':{}, 'total_tonnage':0,'nb_ships':0}
    
    #sort the ships in different dictionnaries
    for name_player in ship_players:  
        coordinates_portail= game_board[players[name_player]['name_portail']]['coordinates']
        for name_ship in ship_players[name_player]:      
            if (ship_players[name_player][name_ship]['lock'] == True):  
                actual_tonnage= ship_players[name_player][name_ship]['actual_tonnage']  
                type_ship = ship_players[name_player][name_ship]['type_ship'] 
                coordinates_ship= tuple(ship_players[name_player][name_ship]['coordinates'])
                
                #if on portail and has ore and locked
                if (coordinates_ship == coordinates_portail ) and (actual_tonnage >0 ) :     
                    players[name_player]['ore']+= actual_tonnage
                    ship_players[name_player][name_ship]['actual_tonnage']= 0 
                #if it can have one more ore and on asteroid
                elif (coordinates_ship in asteroids_capacity) and (list_of_ship[type_ship]['tonnage'] >= (actual_tonnage+ 1)) : 
                  	#Add the name of the ship to the dict and the ore that it still can have. 
                    asteroids_capacity[coordinates_ship][name_player][name_ship]= list_of_ship[type_ship]['tonnage']- actual_tonnage   
                    tonnage_round = game_board['asteroids'][coordinates_ship]['tonnage_round']
                    asteroids_capacity[coordinates_ship]['total_tonnage']+= tonnage_round
    #asteroids_capacity={(1, 2):{'player_1':{}, 'player_2':{}, 'total_tonnage':INT, 'nb_of_ship'}
    for asteroid in asteroids_capacity:
        tonnage_round = game_board['asteroids'][asteroid]['tonnage_round']
        #enough ore on the asteroid
        if (asteroids_capacity[asteroid]['total_tonnage'] * tonnage_round) <= game_board['asteroids'][asteroid]['max_capacity'] :           
            for elements in asteroids_capacity[asteroid]:
                
                if str.startswith(elements, 'player'):
                    for name_ship in asteroids_capacity[asteroid][elements]:
                        tonnage_ship= asteroids_capacity[asteroid][elements][name_ship]
                        name_player= 'player_2'
                        if elements == 'player_1':
                            name_player= 'player_1'
                        
                        for init_round in range (tonnage_round):
                        #tonage_ship: the ore the excavator can still have (difference between the tonnage and actual_tonnage)
                            if tonnage_ship >=1:
                                tonnage_ship -= 1                            
                                game_board['asteroids'][asteroid]['max_capacity'] -= 1
                                ship_players[name_player][name_ship]['actual_tonnage']+= 1   
        #not enough ore for all exacavators on asteroid
        else:
            for number_round in range (tonnage_round):
              	# if enough ore on the asteroid
                if asteroids_capacity[asteroid]['total_tonnage'] >= asteroids_capacity[asteroid]['nb_of_ships'] :
                		for elements in asteroids_capacity[asteroid]:
                		    if str.startswith(elements, 'player') :
                		        for name_ship in asteroids_capacity[asteroid][elements]:
                		            tonnage_ship= asteroids_capacity[asteroid][elements][name_ship]   #can take the ore
                		            if tonnage_ship >=1:
                                		game_board['asteroids'][asteroid]['max_capacity']-= 1
                                		ship_players[elements][name_ship]['actual_tonnage']+= 1
                                		asteroids_capacity[asteroid][elements][name_ship]-= 1
                	#if not enough ore on the asteroid and there more than 1 excavator on it
                else:
                    #compute the ore left on the asteroid 
                    ore_left= game_board[asteroid]['max_capacity'] + 0.00
                    #divide the ore into the nb of ships
                    divide_ore= ore_left/ asteroids_capacity[asteroid]['nb_ships']
                    game_board['asteroids'][asteroid]['max_capacity']= 0
                    for elements in asteroids_capacity[asteroid]:
                        if str.startswith(elements,'player'):
                            for name_ship in asteroids_capacity[asteroid][elements]:
                                if (asteroids_capacity[asteroid][elements] - divide_ore) <=0:
                                    ship_players[elements][name_ship]['actual_tonnage']+= divide_ore
                      
                            
    return (ship_players, players, game_board)
      
def check_life_ships(ship_players, players):
    """Check the life of the ships and delete them if the have no points of life anymore.
    Parameters
    ----------
    ship_player: the data structure which contains the informations about the ships (dict)
    players: the data structure which contains the informations about the players (dict)
    Returns
    -------
    ship_players: the data structure which contains the informations about the ships and which has been modified (dict)
    players: the data structure which contains the information about the players (dict)   
    See also
    --------
    -Use function delete_ship (name_ship,name_player,ship_players, players)
    
    Specification
    Sindy Willems (v1: 05/03/2018)
    Maï Leroy (v2: 27/03/2018)
    Implementation
    Maï Leroy, Sindy Willems (v1: 30/03/2018)
    """  
    ship_players_2=  deepcopy(ship_players)  
    for name_player in ship_players_2:
        for name_ship in ship_players_2[name_player]:
            if ship_players_2[name_player][name_ship]['health'] <= 0:
                ship_players, players= delete_ship(name_ship,name_player,ship_players, players)
    return (ship_players, players)
def delete_ship(name_ship,name_player,ship_players, players):
    """Delete the ships of the board.
    Parameters
    ----------
    name_ships: the name of the ship (str)
    name_player: the name of the player (str)
    ship_players: the data structure which contains the informations about the ships (dict)
    players: the data structure which contains the informations about the players (dict)
    Returns
    -------
    ship_players: the data_structure which contains the ships (dict)
    players: the data structure which contains the informations about the players (dict)  
    
    Specification:
    Maï Leroy (v1: 05/03/2018)
    Implementation
    Maï Leroy (v1: 30/03/2018)
    """
    del ship_players[name_player][name_ship]
    del players[name_player]['ships'][name_ship]    
    return (ship_players, players) 

def end_game(game_board, without_dammage):
    """ Check if it's the end of the game or not. 
    Parameters
    ----------
    game_board: the data structure which contains all the informations of the game (dict)
    whitout_damage: variable which computes the number of rounds (int)  
    Returns
    -------
    True if the game is ended
    False otherwise  
    Notes
    -----
    -Check the number of rounds (20 rounds without dammages )
    -Check life of portals
    
    Specification
    Leopold Van Beirs (v1: 05/03/2018)
    Implementation
    Leopold Van Beirs (v1: 30/03/2018)
    
    """
    if without_dammage > 200:
        return (True)
        
    if game_board['portail_1']['health'] <=0 or game_board['portail_2']['health'] <=0:
        return (True)
    return (False)    #Otherwise

def who_win(players,game_board):
    """ Check who wins the game.
    Parameters
    ----------
    players: the data_structure which contains the informations about the players (dict)
    game_board: the data structure which contains all the informations of the game (dict)
    Returns
    -------
    message: the message with the name of the winner (str)    
    Notes
    -----
    if the two portals are still there :     
    -Check  health of the portals (who has the most wins)
    if health poratls are equal :
    -Check number of ore (who has the most wins)
    
    Specification
    Sindy Willems (v1: 05/03/2018)
    Implementation
    Sindy Willems (v1/ 30/03/2018)
    
    """
    message= 'No one wins the game. It s exaequo'
    if players['player_1']['ore'] != players['player_2']['ore']:
        if players['player_1']['ore'] > players['player_2']['ore'] :
            message= 'player_1 wins'        
        elif players['player_1']['ore']  < players['player_2']['ore'] :
            message= 'player_2 wins'    
    
    if game_board['portail_1']['health'] != game_board['portail_2']['health']:
        if game_board['portail_1']['health'] > game_board['portail_2']['health']:
            message= 'Player 1 wins the game'
        elif game_board['portail_1']['health'] < game_board['portail_2']['health']:
            message= 'Player 2 wins the game'
    return (message)
    
def complete_game(player_1, player_2 ,name_file, remote_ip= None ):
    """Play the game 
    Parameters
    ----------
    player_1:the type of the player who plays the game (IA, player, remote)(str)
    player_2:the type of the player who plays the game (IA, player, remote)(str)
    name_file: the entire path of the configuration file (str)   
    Notes
    -----
    -Use all the function
    
    Specification:
    Maï Leroy (v1: 20/03/2018)
    Implementation:
    Maï Leroy, Léopold Van Beirs, Sindy Willems (v1: 05/04/2018)    
    """  
    #create data structure
    game_board= create_ds_game_board (name_file)
    ship_players={'player_1':{}, 'player_2':{}} 
    players={'player_1':{'ore':4, 'ships':{},'name_portail': 'portail_1'}, 'player_2':{'ore':4, 'ships':{},'name_portail': 'portail_2'}}
    list_of_ship={'excavator-S':{'scope':0, 'vie_initiale':2, 'attack':0, 'tonnage':1, 'cost':1},
              'excavator-M':{'scope':0, 'vie_initiale':3, 'attack':0, 'tonnage':4, 'cost':2},
              'excavator-L':{'scope': 0, 'vie_initiale': 6, 'attack': 0, 'tonnage': 8, 'cost': 4},
              'scout':{'scope':3, 'vie_initiale':3, 'attack':1, 'tonnage':0, 'cost':3},
              'warship':{'scope': 5, 'vie_initiale': 18, 'attack': 3, 'tonnage': 0, 'cost': 9}
             }
             
    #for the tournament
    if player_1 == 'remote' or player_2 =='remote':
        player_IP = 2
        if player_1 == 'remote':
            player_IP = 1
        else:
            player_IP= 2
        verbose = False
        print(player_IP, remote_ip)
        connection = remote_play.connect_to_player(player_IP, remote_ip, False)
    without_dammage= 0
    while not (end_game(game_board, without_dammage)):
        without_dammage+= 1
         
        if player_1 == 'remote' or player_2== 'remote':
            if player_1 == 'IA':
                instruction_player_1 = IA('player_1',ship_players, players,game_board, list_of_ship)
                remote_play.notify_remote_orders(connection, instruction_player_1)
                instruction_player_2= remote_play.get_remote_orders(connection)
                
            elif player_2 == 'IA':
                instruction_player_1 = remote_play.get_remote_orders(connection)
                instruction_player_2 = IA('player_1',ship_players, players,game_board, list_of_ship)
                remote_play.notify_remote_orders(connection, instruction_player_2 )
                
        #the game without tournament
        else:
            if player_1== 'IA':
                print ('IA is player_1')
                instruction_player_1 = IA('player_1',ship_players, players,game_board, list_of_ship)
           
            else:        # player_1 == 'player':
                print ('%s is player_1'%player_1)
                instruction_player_1 = str(input('What are your instruction for the game ?'))
        
            if player_2 == 'IA':
                print ('IA is player_2')
                instruction_player_2 = IA('player_2',ship_players, players,game_board, list_of_ship)
            else:				 # player_2 == 'player':
                print ('%s is player_2'%player_2)
                instruction_player_2 = str (input('What are your instruction for the game? '))
            
        sorted_instruction_player_1 = give_instruction (instruction_player_1)
        sorted_instruction_player_2 = give_instruction (instruction_player_2)
        
        correct_instruction_player_1 = controle_of_instruction ('player_1', sorted_instruction_player_1, ship_players, list_of_ship, game_board)
        correct_instruction_player_2 = controle_of_instruction ('player_2', sorted_instruction_player_2, ship_players, list_of_ship, game_board)
        
        #buy_ship
        for name_ship in correct_instruction_player_1['buy']:
            ship_players, players =buy_ship(correct_instruction_player_1['buy'][name_ship], name_ship, 'player_1',ship_players, players, game_board, list_of_ship)            
        for name_ship in correct_instruction_player_2 ['buy']:
            ship_players, players =buy_ship(correct_instruction_player_2 ['buy'][name_ship], name_ship, 'player_2',ship_players, players, game_board, list_of_ship)        
        #lock or release
        for name_ship in correct_instruction_player_1 ['lock']:
            ship_players =lock_release('lock',name_ship, 'player_1', ship_players, players,game_board)            
        for name_ship in correct_instruction_player_2 ['lock']:
            ship_players =lock_release('lock',name_ship, 'player_2', ship_players, players,game_board)
        for name_ship in correct_instruction_player_1 ['release']:
            ship_players =lock_release('release',name_ship, 'player_1', ship_players, players,game_board)        
        for name_ship in correct_instruction_player_2 ['release']:
            ship_players =lock_release('release',name_ship, 'player_2', ship_players, players,game_board) 
            
        #move_ship
        for name_ship in correct_instruction_player_1 ['move']:
            ship_players, players =move_ship(correct_instruction_player_1 ['move'][name_ship], name_ship,'player_1', ship_players,players, game_board)
            
        for name_ship in correct_instruction_player_2 ['move']:
            ship_players, players =move_ship(correct_instruction_player_2 ['move'][name_ship], name_ship,'player_2', ship_players,players, game_board)       
        #attack_ship 
        for name_ship in correct_instruction_player_1 ['attack']:
            ship_players, game_board, without_dammage =fire_ship(correct_instruction_player_1 ['attack'][name_ship], name_ship,'player_1', ship_players, players, game_board, list_of_ship, without_dammage)
            
        for name_ship in correct_instruction_player_2 ['attack']:
            ship_players, game_board, without_dammage =fire_ship(correct_instruction_player_2 ['attack'][name_ship], name_ship,'player_2', ship_players, players, game_board, list_of_ship, without_dammage)           
        #dump_ore
        ship_players, players, game_board = load_dump (ship_players, players,game_board, list_of_ship)     
        #delete ships 
        ship_players, players=check_life_ships(ship_players, players)
        #UI
        show_ui(ship_players, players, game_board)        
    print (who_win(players,game_board))  
    #disconnect_from_player(connection)      
    return ('End of the game. Thanks for playing :-) ')
  
def give_instruction(instruction):
    """Give the instructions to the game to play.
    Parameters
    ----------
    instruction: the instructions the player gives to the game (str)    
    Returns
    -------
    correct_instruction: instruction sorted by the function controle_of_instruction (dict)    
    Notes
    -----
    sorted_instruction={'lock':[], 'release':[], 'attack':{}, 'move':{}, 'buy':{}}
    -lock: list which contains the name of the ships to lock 
    -release: list which contains the name of the ships to release from the asteroids or the portails
    -attack: dict which contains the name of the ship (key), and the coordinates of the attack (list)
    -move: dict which contains the name of the ship (key), and the coordinates of the direction to move(list)
    -buy: dict which contains the name of the ship (str)(key) to buy and the type of the ship (str)
    
    Specification
    Maï Leroy (v1: 05/03/2018)
    Maï Leroy (v1: 27/03/2018)
    Implementation
    Maï Leroy (v1: 30/03/2018)
    """   
    #create dict
    sorted_instruction={'lock':[], 'release':[], 'attack':{}, 'move':{}, 'buy':{}}
    instruction= instruction.split (' ')
    
    elements= 0         
    for elements in range(len(instruction)):  
        one_instruction= instruction[elements].split(':')       #one_instruction=['Larry', '@20-30']
        if len(one_instruction) <2:
            one_instruction= one_instruction    #do nothing
        elif one_instruction[1] == 'lock':
            name_locked =sorted_instruction['lock']  #Rem : sorted_instruction['release']= sorted_instruction['release'].append(one_instruction[0]) don't work
            name_locked.append(one_instruction[0])
            sorted_instruction['lock']= name_locked            
        elif one_instruction[1] == 'release':
            name_released= sorted_instruction['release']
            name_released.append(one_instruction[0])
            sorted_instruction['release']= name_released
            
        elif (str.startswith(one_instruction[1],'*')) or (str.startswith(one_instruction[1],'@')):      
            direction= one_instruction[1].split('-')    #['@20','30']
            if (str.startswith(one_instruction[1],'*')):
                #attack the ships
                coordinates=[int(direction[0].split('*')[1]), int(direction[1])]
                sorted_instruction['attack'][one_instruction[0]]=coordinates
                
            elif (str.startswith(one_instruction[1],'@')):
                #move the ships
                coordinates=[int(direction[0].split('@')[1]), int(direction[1])]
                sorted_instruction['move'][one_instruction[0]]=coordinates
            
        elif one_instruction[1] == 'excavator-M' or one_instruction[1] == 'excavator-S' or one_instruction[1] == 'excavator-L' or one_instruction[1] == 'scout' or one_instruction[1] == 'warship':
            sorted_instruction['buy'][one_instruction[0]]=one_instruction[1]         
    return (sorted_instruction)        
def controle_of_instruction(name_player, sorted_instruction, ship_players, list_of_ships, game_board):
    """Controle if the instructions are correct and no unreleasable.
    Parameters
    ----------
    sorted_instruction: the informations sorted by type of instructions (dict)
    ship_players: the data structure which contains the informations about the players' ships (dict)
    list_of_ship: the data strucure which contains the caracteristics of the ships (dict)
    game_board: the data structure which contains the informations about the current game (dict)
    Returns
    -------
    correct_instruction: the correct instruction which is no unreal (dict)
    Notes
    -----            
    -sorted_instruction={'lock':[name_ship], 'release':[name_ship], 'attack':{name_ship:[x,y], name_ship:[x,y]}, 'move':{}, 'buy':{name_ship:[name_player,]}}
            
    Specification:
    Sindy Willems (v1: 05/03/2018)
    Implementation
    Sindy Willems, Maï Leroy (v1: 30/03/2018)
    """
    correct_instruction={'lock':[], 'release':[], 'attack':{}, 'move':{}, 'buy':{}}
    name_used = []    
    #buy the ships 
    for bought in sorted_instruction['buy']:
        if not( bought in ship_players[name_player]):
            correct_instruction['buy'][bought]= sorted_instruction['buy'][bought]    
    #Verif excavator can  lock or release  
    for excavator in sorted_instruction['lock']:
        if excavator in ship_players[name_player]:
            type_ship = ship_players[name_player][excavator]['type_ship']
            if ((type_ship == 'excavator-S') or (type_ship == 'excavator-M') or (type_ship == 'excavator-L')) :
                list_lock= correct_instruction['lock']
                list_lock.append(excavator)
                correct_instruction['lock']= list_lock
                name_used.append(excavator)
        else:
            if (excavator in sorted_instruction['buy']) and (sorted_instruction['buy'][excavator] != 'scout' or sorted_instruction['buy'][excavator != 'warship']):
                correct_instruction['lock']= correct_instruction['lock'].append(excavator)
        
    for excavator in sorted_instruction['release']:
        if excavator in ship_players[name_player]:
            type_ship = ship_players[name_player][excavator]['type_ship']
            if ((type_ship == 'excavator-S') or (type_ship == 'excavator-M') or (type_ship == 'excavator-L')) :
                list_lock= correct_instruction['release']
                list_lock.append(excavator)
                correct_instruction['release']= list_lock
                name_used.append(excavator)
        else:
            if (excavator in sorted_instruction['buy']) and (sorted_instruction['buy'][excavator] != 'scout' and sorted_instruction['buy'][excavator] != 'warship'):
                correct_instruction['release']= correct_instruction['release'].append(excavator)                
    #verify that the ship can attack 
    size_game= game_board['size_board']
    for attack_ship in sorted_instruction['attack']:
        if attack_ship in ship_players[name_player]:
            if ship_players[name_player][attack_ship]['type_ship'] == 'scout' or ship_players[name_player][attack_ship]['type_ship'] == 'warship':
                if (sorted_instruction['attack'][attack_ship][0] < size_game[0]) or (sorted_instruction['attack'][attack_ship][1] < size_game[1]):
                    correct_instruction['attack'][attack_ship]= sorted_instruction['attack'][attack_ship]
                    name_used.append(attack_ship)
        else:
            if (attack_ship in sorted_instruction['buy']) and (sorted_instruction['buy'][attack_ship] == 'scout' or sorted_instruction['buy'][attack_ship] == 'warship'):
                correct_instruction['attack'][attack_ship]= sorted_instruction['attack'][attack_ship]
                name_used.append(attack_ship)
    
    for move_ship in sorted_instruction['move']:
        if not(move_ship in name_used):
            if move_ship in ship_players[name_player]:
                if (sorted_instruction['move'][move_ship][0] <= size_game[0]) and (sorted_instruction['move'][move_ship][1] <= size_game[1]):
                    correct_instruction['move'][move_ship]= sorted_instruction['move'][move_ship]
            else:
                if (move_ship in sorted_instruction['buy']):
                    correct_instruction['move'][move_ship]= sorted_instruction['move'][move_ship] 
    return (correct_instruction)
def show_ui(ship_players, players, game_board):
    """Show the entire game (portails, ships,...).
    Parameters
    ----------
    game_board: the data structure which contains the informations about current the game (dict)
    players: the data structure which contains the informations about the players (dict)
    ship_players: the data structure which contains the informations about the ships (dict)
    
    Specification
    Maï Leroy, Sindy Willems, Léopold Van Beirs (v1: 13/04/2018)
    Implementation
    Sindy Willems, Maï Leroy, Léopold Van Beirs (v1: 14/04/2018)
    
    """
    lines = game_board['size_board'][0]
    columns= game_board['size_board'][1]
    cases = create_ds_cases(lines, columns)
    
    for area_portail in game_board['portail_1']['area']:
        position_x, position_y= area_portail[0], area_portail[1]
        update_color_case(position_x, position_y, 'portail', cases, 'player_1')
    for area_portail in game_board['portail_2']['area']:
        position_x, position_y= area_portail[0], area_portail[1]
        update_color_case(position_x, position_y, 'portail', cases, 'player_2') 
    for name_player in players:
        for name_ship in players[name_player]['ships']:
            for position in players[name_player]['ships'][name_ship]:
                position_x, position_y = position[0], position[1]
                update_color_case(position_x, position_y, 'ship', cases, name_player)        
    for asteroids in game_board['asteroids']: 
        position_x, position_y= asteroids[0], asteroids[1]
        update_color_case(position_x, position_y, 'asteroid', cases)
         
    show_game(lines, columns, cases)   
    
    #show information
    print ('Portail_1 is at coordinates: %s'% str(game_board['portail_1']['coordinates']))
    print ('Portail_2 is at coordinates: %s'% str(game_board['portail_2']['coordinates']))
    for asteroids in game_board['asteroids']:
        actual_tonnage=  game_board['asteroids'][asteroids]['max_capacity']
        print ('Asteroid %s has %d ore'%(asteroids, actual_tonnage))
    for name_player in ship_players:
        ore_player= players[name_player]['ore']
        health_portail= game_board[players[name_player]['name_portail']]['health']
        print ('Player %s has: %d ore, his portail has :%d'%(name_player, ore_player, health_portail ))
        for name_ship in ship_players[name_player]:
            position= ship_players[name_player][name_ship]['coordinates']
            health_ship= ship_players[name_player][name_ship]['health']
            lock= str(ship_players[name_player][name_ship]['lock'])
            type_ship= ship_players[name_player][name_ship]['type_ship']
            print ('- %s the %s is at %s and his health is %d and locked: %s '%(name_ship,type_ship, position, health_ship, lock))
def create_ds_cases(lines, columns):
    """Create a list which contains the cases of the game.
    Paramaters
    ----------
    lines: nb of lines (int)
    columns: nb of columns (int)
    Returns
    -------
    cases: the list which contains all the cases of the game (list)
        
    Specification
    Maï Leroy (v1: 09/04/2018)
    Implementation
    Maï Leroy (v1: 09/04/2018)
    """   
    return [['    ' for column in range (1,columns+1)] for line in range (1, lines+1)]

def show_game(lines, columns, cases):
    """Show the game board.
    Parameters
    ----------
    lines: nb of rows (int)
    columns: nb of columns (int)
    cases: the list which contains all the cases of the game (list)
    
    Specification
    Maï Leroy (v1: 13/04/2018)
    Implementation
    Maï Leroy, Sindy Willems, Léopold Van Beirs (v1: 14/04/2018)    
    """ 
    show_columns= '  '
    for nb_columns in range(columns):
        if nb_columns <10:
            show_columns+= '  ' + str(nb_columns + 1) + '  ' 
        else:
            show_columns+= '  ' + str(nb_columns + 1)  + ' '   
    print (show_columns)
    print ('------'*columns)
    
    for line in range (lines):       
        if line < 9:
            show_lines = ' %s ' %(line+1)
        else:
            show_lines= '%s ' %(line+ 1)
        
        # create other lines    
        for column in range(1, columns+1):
            show_lines += '|' + cases[line][column-1]
        show_lines += '|    '    
        print (show_lines)
        print ('------'* columns)
    
def update_color_case(position_y, position_x, type_show, cases, player= None):
    """Change the color of the cases of the game in terms of the type of the thing to show.
    Parameters
    ---------
    position_x: the row of the case to color (int)
    position_y: the column of the case to color (int)
    type_show: the type of the thing to show (portail, ship, asteroid) (str)
    player: the name of the player (str)
    cases: the data structure which contains the cases of the game (list)
    Return
    ------
    cases: the data structure which contains the cases of the game (list)
    Specification
    Maï Leroy (v1: 13/04/2018)
    Sindy Willems (v2: 21/05/2018)
    Implementation
    Maï Leroy (v1: 14/04/2018)
    """
    if type_show == 'asteroid':
        color = 'on_grey'
    elif (type_show == 'portail' ):
        color = 'on_red'
        if player == 'player_1':
            color = 'on_blue'
    elif (type_show == 'ship'):
        color = 'on_magenta'
        if player == 'player_2':
            color = 'on_cyan'
    else:
        color = None
        
    # Color change
    cases[position_y -1][position_x -1] = '    '
    cases[position_y -1][position_x -1] = termcolor.colored(cases[position_y -1][position_x -1], None, color)
    return (cases)
  
def IA(name_player,ship_players, players,game_board, list_of_ship):
    """ The IA created by the groupe 23 in order to win the challenge.
    Parameters
    ----------
    name_player: the name of the player (str)
    ship_players: the data structure which contains the informations about the ships (dict)
    players: the data structure which contains the informations about players (dict)
    game_board: the data structure which contains the informations about the current game (dict)
    list_of_ship: the dictionnary which contains the caracteristics about the ships (dict) 
    Returns
    -------
    instruction: the instruction to give to the function (str)
    
    Specification
    Maï Leroy (v1: 05/03/2018)
    Implementation
    Léopold Van Beirs, Sindy Willems, Maï Leroy (v1: 13/04/2018)

    """
    attacks= []
    excavators = []
    ennemies=[]
   
    for name_ship in ship_players[name_player]:
        type_ship= ship_players[name_player][name_ship]['type_ship']
        if type_ship == 'scout' or type_ship == 'warship':
            attacks.append(name_ship)
        else:
            excavators.append(name_ship)
                        
    instruction=''
    buy_ship=''
    lock_release=''
    attack_ship=''
    move_ship= ''
    name_buy=[]
    name_used=[]   
    
    ore_asteroid = []
    for asteroid in game_board['asteroids']:
        if game_board['asteroids'][asteroid]['max_capacity'] > 2:
            ore_asteroid.append(list(asteroid))  
    #buy_ships
    ore_player= players[name_player]['ore']
    if (len(excavators) == 0) and (len(attacks)== 0) and (len(ore_asteroid)> 0) and (ore_player>0):      
        if ore_player >= 3:
            name_buy,buy_ship= give_name_IA(name_buy, name_player,ship_players)
            instruction+= buy_ship + ':scout '
            ore_player -= 3
        if ore_player >0: 
            name_buy,buy_ship= give_name_IA(name_buy, name_player,ship_players)
            instruction+= buy_ship + ':excavator-S '
            ore_player -=1
    if (len(excavators) == 0) and (len(ore_asteroid)> 0) and (ore_player>0):    
        if ore_player >= 4:
            name_buy,buy_ship= give_name_IA(name_buy, name_player,ship_players)
            instruction+= buy_ship + ':excavator-L '
            ore_player -= 4          
        elif ore_player >=2:
            name_buy,buy_ship= give_name_IA(name_buy, name_player,ship_players)
            instruction+= buy_ship + ':excavator-M '
            ore_player -= 2 
        elif ore_player >0:
            name_buy,buy_ship= give_name_IA(name_buy, name_player,ship_players)
            instruction+= buy_ship + ':excavator-S '
            ore_player -= 1  
     
    if (len(attacks) == 0): 
        if ore_player >= 9:
            name_buy,buy_ship= give_name_IA(name_buy, name_player,ship_players)
            instruction += buy_ship + ':warship '
            ore_player -= 9
        elif ore_player >= 3:
            name_buy,buy_ship= give_name_IA(name_buy, name_player,ship_players)
            instruction += buy_ship + ':scout '
            ore_player -= 3

    #lock_release
    if len(excavators)> 0:                
       
        for excavator in excavators:
            type_excavator = ship_players[name_player][excavator]['type_ship']
            actual_tonnage = ship_players[name_player][excavator]['actual_tonnage']
            coordinates_portail= list(game_board[players[name_player]['name_portail']]['coordinates'])
            
            
            if ship_players[name_player][excavator]['lock'] == False:      
                #IF on it's portail
                if (ship_players[name_player][excavator]['coordinates'] )== coordinates_portail:      
                    #if excavator has to dump its ore  
                    if actual_tonnage > 0:  
                        lock_release+= excavator + ':lock '
                        name_used.append(excavator)
                #IF it's on a asteroid which has more than 2 ore
                elif ship_players[name_player][excavator]['coordinates'] in ore_asteroid: 
                    #IF it can load ore       
                    if actual_tonnage < list_of_ship[type_excavator]['tonnage']:    
                        lock_release+= excavator + ':lock '
                        name_used.append(excavator) 
                        
            elif ship_players[name_player][excavator]['lock'] == True:        
                if ship_players[name_player][excavator]['coordinates'] == coordinates_portail:    
                    #IF it has no more ore to dump
                    if actual_tonnage <=0: 
                        lock_release+= excavator + ':release '
                        
                    else:   #IF it has ore to dump
                        name_used.append (excavator)
                elif ship_players[name_player][excavator]['coordinates'] in ore_asteroid:   
                    if actual_tonnage == list_of_ship[type_excavator]['tonnage']:
                        lock_release+= excavator + ':release ' 
                    else:
                        name_used.append(excavator)         
                else:
                    lock_release+= excavator + ':release '
    #attack_ship
    if len (attacks) > 0:
        if name_player == 'player_1':       #find the name of the ennemy
            name_ennemy= 'player_2'
            for ennemy in ship_players['player_2']:
                ennemies.append(ennemy)
                
        else:  
            name_ennemy= 'player_1' 
            for ennemy in ship_players['player_1']:
                ennemies.append(ennemy)
                

        name_ennemy_portail= players[name_ennemy]['name_portail']
        coordinates_ennemy_portail= list(game_board[name_ennemy_portail]['coordinates'])
        ennemy_portail={'coordinates':coordinates_ennemy_portail ,'name': name_ennemy_portail,'health':game_board[name_ennemy_portail]['health']}     
        name_victims={}     
           
        for attack in attacks:
            type_attack = ship_players[name_player][attack]['type_ship']
            coordinates_attack = ship_players[name_player][attack]['coordinates']
            max_scope= list_of_ship[type_attack]['scope']
            
            distance_ennemy = manhattan_distance (coordinates_attack, coordinates_ennemy_portail)
            in_scope = False
            if distance_ennemy <= max_scope:   
                in_scope= True

            ennemy_portail['distance']= distance_ennemy
            ennemy_portail['in_scope']= in_scope
            name_victims[attack]= ennemy_portail
            
            for victim in ship_players[name_ennemy]:
                coordinates_ennemy = ship_players[name_ennemy][victim]['coordinates']
                distance_ennemy = manhattan_distance(coordinates_attack ,coordinates_ennemy)
                if distance_ennemy <= name_victims[attack]['distance']:  #compute the distance
                    in_scope= False     #compute if the ship can fire the opponent ship or portail
                    if distance_ennemy <= max_scope:
                        in_scope= True
                                            
                    ennemy_health = ship_players[name_ennemy][victim]['health']
                    if distance_ennemy == name_victims[attack]['distance']:
                        #take the ennemy with the least points of life
                        if (ennemy_health < name_victims[attack]['health']) and (name_victims[attack]['name'] != name_ennemy_portail):       
                            name_victims[attack]={'health':ennemy_health, 'name': victim ,'distance': distance_ennemy, 'in_scope': in_scope, 'coordinates': coordinates_ennemy}
                    else:
                        name_victims[attack]={'health':ennemy_health, 'name': victim ,'distance': distance_ennemy, 'in_scope': in_scope, 'coordinates':coordinates_ennemy} 
              
            if name_victims[attack]['in_scope'] == True:    # if the ennemy is on the scope and attack it               
                attack_ship+= attack +':*' + str(name_victims[attack]['coordinates'][0]) + '-' + str(name_victims[attack]['coordinates'][1]) + ' '
                name_used.append(attack)
                    
    #move_ attack ship
    if len(attacks) > 0 :
        for attack in attacks:
            if not(attack in name_used): 
                coordinates_target= name_victims[attack]['coordinates']
                coordinates_reach = move_ship_IA(ship_players[name_player][attack]['coordinates'], coordinates_target)
                move_ship+= attack + ':@' + coordinates_reach + ' '
    #move excavator            
    if len(excavators) > 0:
        for excavator in excavators:
            if not(excavator in name_used):
                coordinates_excavator = ship_players[name_player][excavator]['coordinates']
                type_excavator= ship_players[name_player][excavator]['type_ship']
                actual_tonnage= ship_players[name_player][excavator]['actual_tonnage']
                if actual_tonnage >= (list_of_ship[type_excavator]['tonnage']):# full or almost full (-1) :GO portail
                    portail_player= game_board[players[name_player]['name_portail']]['coordinates']
                    coordinates_target = portail_player            
                
                else:
                    if len(ore_asteroid) > 0 :    #not full and asteroid disponible: GO the closest
                        reach_asteroid= {'distance': 100}
                        for asteroid in ore_asteroid:
                            distance_asteroid = manhattan_distance(coordinates_excavator, asteroid)
                            if distance_asteroid < reach_asteroid['distance']:
                                reach_asteroid={'distance': distance_asteroid, 'name': asteroid}
                        coordinates_target= reach_asteroid['name']
                    
                    else: #not full and not asteroid disponible: go to the opposite portail
                        coordinates_target= game_board[name_ennemy_portail]['coordinates']
                    
                coordinates_reach = move_ship_IA(coordinates_excavator, coordinates_target)
                move_ship+= excavator + ':@'+ coordinates_reach + ' '

    instruction+= lock_release + attack_ship + move_ship
    instruction = instruction[:len(instruction)-1]    
    return (instruction)
    
def give_name_IA(name_buy, name_player,ship_players):
    """Give the name to the ship
    Parameters
    ----------
    name_buy: the list which contains the name of the ships that the IA has just bought (list of str)
    name_player: the name of the player ('player_2' or' player_1') (str)
    ship_players: the data structure which contains the information about the ships (dict)
    Returns
    -------
    name_ship: the name of the new_ship (str)
    
    Specification
    Maï Leroy (v1: 11/03/2018)
    Implementation
    Maï Leroy, Sindy Willems, Léopold Van Beirs (v1: 05/04/2018)
    """
    suffix= str(randint (0, 50))
    name=['Arryn','Baratheon','Bolton','Frey','Martell','Lannister','Greyjoy','Stark','Tully','Targaryen','Tyrell']
    ship= name[randint(0, len(name)-1)]    
    name_ship= ship + 'I' + suffix
    
    if (not (name_ship in ship_players[name_player])) and (not(name_ship in name_buy)):
        name_buy.append(name_ship)
        return (name_buy,name_ship)    
    else:
        return (give_name_IA(name_buy,ship_players))

def move_ship_IA(coordinates_ship, coordinates_target):
    """move the ship of the player in order to reach a certain position.
    Parameters
    ----------
    coordinates_ship: the coordinates of the ship of the IA (list)
    coordinates_target: the coordinates of the target (list)
    Returns
    -------
    coordinates_reach: the coordinates to reach (str)
    
    Specification
    Maï Leroy (v1: 30/03/2018)
    Implementation
    Maï Leroy, Léopold Van Beirs (v1: 05/04/2018)    
    """       
    coordo0, coordo1= coordinates_ship[0],coordinates_ship[1] 
    if coordo0 < coordinates_target[0]:
        coordo0+= 1
    elif coordo0 > coordinates_target[0]:
        coordo0 -= 1
    if coordo1 < coordinates_target[1]:
        coordo1 += 1
    elif coordo1 > coordinates_target[1]:
        coordo1 -= 1  
    #updated ship_player
    return (str(coordo0)+ '-'+ str(coordo1))          
 

##The complete game                                                         
#a=complete_game('IA','remote','/home/users/100/siwillem/Desktop/Game/gameboard_2_gr_17.mw','remote_ip=168.48.160.113')
#print (a)








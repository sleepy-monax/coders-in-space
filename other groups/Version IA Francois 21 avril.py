# -*- coding: utf-8 -*-
# LECLERE Arthur – BERNARD François – DARDENNE Florine – GROUPE 15

from remote_play import get_IP, connect_to_player, disconnect_from_player, notify_remote_orders, get_remote_orders  
from termcolor import colored, cprint
from random import randint, choice
from os import system
from pickle import load

def start_game(data):
    """Start the game (coordinates = number of lines and columns) and set the dictionnary up
    
    Parameter
    ---------
    game: the information of the game (dico)
    
    Return
    ------
    game: the information of the game (dico)
    
    Notes
    -----
    coordinates[0] must be between 30 and 40, coordinates[1] must be between 30 and 60
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 23/02/2017)
    implémentation : Arthur Leclère, François Bernard (v.1 23/02/2017)
    """
    
    #Creation of the first dictionary keys necessary at the beginning of the game
    game = {}
    game['board'] = {}
    game['ships'] = {}
    game['ships']['fighter'] = {}
    game['ships']['fighter']['max speed'] = 5
    game['ships']['fighter']['hit points'] = 3
    game['ships']['fighter']['attack'] = 1 
    game['ships']['fighter']['range'] = 5 
    game['ships']['fighter']['cost'] = 10
    game['ships']['destroyer'] = {}
    game['ships']['destroyer']['max speed'] = 2
    game['ships']['destroyer']['hit points'] = 8
    game['ships']['destroyer']['attack'] = 2
    game['ships']['destroyer']['range'] = 7
    game['ships']['destroyer']['cost'] = 20
    game['ships']['battlecruiser'] = {}
    game['ships']['battlecruiser']['max speed'] = 1
    game['ships']['battlecruiser']['hit points'] = 20
    game['ships']['battlecruiser']['attack'] = 4
    game['ships']['battlecruiser']['range'] = 10
    game['ships']['battlecruiser']['cost'] = 30
    for player_id in (1,2):
        game[player_id] = {}
        game[player_id]['coins'] = 100
        game[player_id]['ships'] = {}
    game['size'] = {}
    game['future_explosions'] = {}
    game['list_moves'] = []
    game['ships_hit'] = []
    game['ships_taken'] = []
    game['names'] = ['Florine', 'Francois', 'Arthur', 'Eloise', 'Pol', 'Simon', 'Clement', 'Colin', 'Benoit', 'Julie', 'Alain', 'Jose', 'Charles', 'James', 'Maxime', 'Jacky', 'John', 'Kevin', 'Maurice', 'Marcel', 'Pietro']
    game['targets'] =[]
    #Reading of the file that contains the information about the game : size of the board and location of the abandonned ships
    read_file(game, data)
    return game

def read_file(game, data):
    """Reads the data with the abandoned ships
    
    Parameter
    ---------
    game: the information of the game (dico)
    data: the file with the data (file)
    
    Return
    ------
    game: the information of the game (dico)
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 23/02/2017)
    implémentation: Florine Dardenne (v.1 23/02/2017)
    """
    
    #Opening the file that contains the information about the game
    file = open(data,'r')
    #Catching the informations
    info = file.readlines()
    #the first line is the informations about the size of the board
    first_line = info[0]
    #Cleaning the informations
    first_line = first_line[:-1]
    first_line = first_line.split(' ')
    #Setting the informations in the dictionnary and putting them in a list
    game['size']['lines'] = int(first_line[0])
    game['size']['columns'] = int(first_line[1])
    #Creating the key in the dictionnary for the abandonned ships
    game[0] = {}
        
    for line in info[1:]:
        #Cleaning the informations of every line and putting them in some lists
        line = line[:-1]
        line = line.split(' ')
        #Creating a list in the list with the name and the type of the abandonned ship
        name_type = line[2].split(':')
        #Setting the informations about the ship on the board in the dictionnary
        if not((int(line[0])),(int(line[1]))) in game['board']:
            game['board'][(int(line[0])),(int(line[1]))] = []
            game['board'][(int(line[0])),(int(line[1]))] = [(0,name_type[0])]
        else:
            game['board'][(int(line[0])),(int(line[1]))].append ((0,name_type[0]))
        #Setting the other informations in the dictionnary
        game[0][name_type[0]] = {}
        game[0][name_type[0]]['lines'] = int(line[0])
        game[0][name_type[0]]['columns'] = int(line[1])
        game[0][name_type[0]]['type'] = name_type[1]
        game[0][name_type[0]]['orientation'] = {}
        
        #Modifying the form of the orientation
        if line[3] == 'up':
            orientation = 90
        elif line[3] == 'down':
            orientation = 270
        elif line[3] == 'left':
            orientation = 180
        elif line[3] == 'right':
            orientation = 0
        elif line[3] == 'up-left':
            orientation = 135
        elif line[3] == 'up-right':
            orientation = 45
        elif line[3] == 'down-left':
            orientation = 225
        elif line[3] == 'down-right':
            orientation = 315
        else:
            orientation=0
        game[0][name_type[0]]['orientation'] = orientation
    #Closing the file
    file.close()
    return game
    
def display_board(game):
    """Display the board
    
    Parameter
    ----------
    game: the information of the game (dico)
    
    Return
    ------
    game: the information of the game (dico)
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 23/02/2017)
    implémentation: Arthur Leclère (v.1 28/02/2017)
    implémentation: Arthur Leclère (v.1 --> v.2 07/03/2017)
    implémentation: Arthur Leclère (v.2 --> v.3 14/03/2017)
    """
    
    #Creating for each player an empty list of ships
    for player_id in (1, 2):
        list_ships = []
        #Adding every ships of the player in the list of ships
        for ships in game[player_id]['ships']:
            list_ships.append (ships)
        #Displaying the player and his id in black underlined
        player_info = colored('player %d: ', 'grey', None, ['underline']) % player_id
        #For every ship in the list of ships, changing the form of the orientation from degree to an arrow
        for i in range(len(list_ships)):
            #Getting the orientation of the ships, putting it in a variable
            ship_orientation = game[player_id]['ships'][list_ships[i]]['orientation']
            if ship_orientation == 0:
                orientation = '→'
            if ship_orientation == 45:
                orientation = '↗'
            if ship_orientation == 90:
                orientation = '↑'
            if ship_orientation == 135:
                orientation = '↖'
            if ship_orientation == 180:
                orientation = '←'
            if ship_orientation == 225:
                orientation = '↙'
            if ship_orientation == 270:
                orientation = '↓'
            if ship_orientation == 315:
                orientation = '↘'
            #Displaying all the informations of the ships of the player with the name of the ship, the number of hit points, the speed and the orientation
            info_ship =  '%s %s hp:%d %s sp:%d or:%s; ' % (list_ships[i],(game[player_id]['ships'][list_ships[i]]['lines'],game[player_id]['ships'][list_ships[i]]['columns']),game[player_id]['ships'][list_ships[i]]['hit points'],game[player_id]['ships'][list_ships[i]]['type'],game[player_id]['ships'][list_ships[i]]['speed'],orientation)
            #Displaying the informations of only three ships by line
            if i%3 == 0 and i != 0:
                player_info += '\n' + info_ship
            else:
                player_info += info_ship
        print player_info
    #Creating the first line of the board and displaying it in black and underlined                   
    header = '   |'
    for i in range (1, 10):
        header += '0' + str(i) + '|'
    for i in range (10, game ['size']['columns'] + 1):
        header += str(i) + '|'
    cprint (header, 'grey', None, ['underline'])
    #Creating all the lines of the board 
    for i in range (1, game ['size']['lines'] + 1):
        #First creating the first part of the line, the number of the line
        if i in range (1,10):
            line = '0' + str (i) + ' |'
        else: 
            line = str (i) + ' |'
        line = colored(line, 'grey', None, ['underline'])
        for j in range (1,game ['size']['columns']+ 1):
            #Then creating the boxes 
            #Checking if there is a ship on the box or not 
            if (i,j) not in game['board']:
                element = colored('  |', 'grey', None, ['underline']) 
            #Check if there is more than one ship on the box
            elif len(game['board'][(i,j)]) > 1:
                ship_0 = 0
                ship_1 = 0
                ship_2 = 0
                #Counting the number of ships of every player on the box
                for ship in game['board'][(i,j)]:
                    if ship[0] == 1:
                        ship_1 += 1
                    elif ship[0] == 2:
                        ship_2 += 1 
                    elif ship[0] == 0:
                        ship_0 +=1
                #Display the number of ships there are on the box in the color of the player, black for the abandoned ships, red for the player 2 and blue for the player 1
                if ship_0 == 0 and ship_1 == 0:
                    element = colored (str(ship_2) + ' ', 'red', None, ['underline']) + '|' 
                elif ship_0 == 0 and ship_2 ==0:
                    element = colored (str(ship_1) + ' ', 'cyan', None, ['underline']) + '|' 
                elif ship_1 == 0 and ship_2==0:
                    element = colored (str(ship_0) + ' ', None, None, ['underline']) + '|'
                elif ship_0 ==0:
                    element = colored (str(ship_1), 'cyan', None, ['underline']) + colored (str(ship_2), 'red', None, ['underline']) + '|' 
                else:
                    element = colored (str(ship_0), None, None, ['underline']) + colored (str(ship_1), 'cyan', None, ['underline']) + colored (str(ship_2), 'red', None, ['underline']) + '|' 
            #If there is only one ship on the box, displaying the pawn in the right color
            elif game['board'][(i,j)][0][0] == 1:
                element = colored ('♛', 'cyan', None, ['underline']) + '|'
            elif game['board'][(i,j)][0][0] == 2:
                element = colored ('♛', 'red', None, ['underline']) + '|'
            else:
                element = colored ('♟', None, None, ['underline']) + '|'
            line+= element 
        print line  
        
def display_ships_actions(game):
    """Display all ships moves (whether ships moved, have been hit by a missil, exploded or whether abandoned ships have been taken) from the last turn + the number of turns
    
    Parameters
    ----------
    game: the information of the game (dico)   
    
    Return
    ------
    game: the information of the game (dico)
     
    Version
    -------
    spécification: Arthur Leclère (v.1 12/04/2017)
    implémentation: Arthur Leclère (v.1 12/04/2017)
    """
    #Collecting information about ships moves
    ships_moves = ''
    if game['list_moves'] != []:
        ships_moves +=  colored('ships moves: ', 'grey', None, ['underline'])
        for i in range(len(game['list_moves'])):
            if i%6 == 0 and i != 0:
                ships_moves += '\n' + game['list_moves'][i]
            else:
                ships_moves += game['list_moves'][i]
        game['list_moves'] = []
        ships_moves = ships_moves[:-2]
    
    #Collecting information about ships hit by a missil
    ships_hit = ''
    if game['ships_hit'] != []:
        ships_hit +=  colored('ships hit: ', 'grey', None, ['underline'])
        for i in range(len(game['ships_hit'])):
            if i%6 == 0 and i != 0:
                ships_hit += '\n' + game['ships_hit'][i]
            else:    
                ships_hit += game['ships_hit'][i]
        game['ships_hit'] = []
        ships_hit = ships_hit[:-2]
        
    #Collecting information about abandoned ships taken
    ships_taken = ''
    if game['ships_taken'] != []:
        ships_taken +=  colored('ships taken: ', 'grey', None, ['underline'])
        for i in range(len(game['ships_taken'])):
            if i%6 == 0 and i != 0:
                ships_taken += '\n' + game['ships_taken'][i]
            else:
                ships_taken += game['ships_taken'][i]
        game['ships_taken'] = []
        ships_taken = ships_taken[:-2]
    
    #Displaying information whether there is something to display
    if ships_moves != '':
        print ships_moves
    if ships_hit != '':
        print ships_hit
    if ships_taken != '':
        print  ships_taken
    print colored('turns: ', 'grey', None, ['underline']) + '%d' % game['turns']
        
    return game              

def get_IA_orders(game, player_id):
    """Returns orders chosen by IA player.
    
    Parameters
    ----------
    game: the information of the game (dico)
    player_id: number of the player (int)
    
    Return
    ------
    orders: orders chosen by IA player (str)
    
    Version
    -------
    spécification: Arthur Leclère (v.1 14/03/2017)
    implémentation: Arthur Leclère (v.1 14/03/2017)
    """
    
    #Checking if it's the first turn of the game
    if 'turns' not in game:
        #Asking to the IA what it wants to buy 
        orders = raw_input('What do you want to buy? You can chose fighter or destroyer or battlecruiser? name:type  ')
    else:
        #Asking to the IA what it wants to do with its ships
        orders = raw_input('To which ship do you want to give an order and what do you want to ask him ? (order = faster or slower or (right/left) or yy-xx) name:action ')
    #Returning the orders 
    return orders
        
def IA_buy_ships(game, player_id):
    """IA player choses ramdomly which ships it wants to buy
    
    Parameters
    ----------
    game: the information of the game (dico)
    player_id: number of the player, 1 or 2 (int)
    
    Return
    ------
    orders: the orders given by the IA (str)
    
    Version
    -------
    spécification: Arthur Leclère (v.1 28/03/2017)
    implémentation: Arthur Leclère (v.1 28/03/2017)
    """
    
    ships = ['fighter', 'battlecruiser', 'destroyer']
    orders = ''
    money = 100
    #While there is enough money to buy a ship, buy new ships
    while money >= 10:
        #The name of the ship is chosen in a list of names in the dictionnary and then it's removed from the list 
        name = choice(game['names'])
        game['names'].remove(name)
        #The type of the ship is chosen in the list 'ships'
        type = 'fighter'
        #Checking if the player has enough money to buy this ship, creating the string with the orders and then remove the cost of the ship from the money of the player
        if game['ships'][type]['cost'] <= money:
            ship = name + ':' + type + ' '
            money -= game['ships'][type]['cost']
            orders += ship
    orders = orders[:-1]
    return orders
    
def IA_give_orders(game, player_id):
    """IA player choses ramdomly which move it wants to do
    
    Parameters
    ----------
    game: the information of the game (dico)
    player_id: number of the player, 1 or 2 (int)
    
    Return
    ------
    orders: the orders given by the IA (str)
    
    Version
    -------
    spécification: Arthur Leclère (v.1 28/03/2017)
    implémentation: Arthur Leclère (v.1 28/03/2017)
    """
    
    orders = ''
    #For every ship of the player, chosing an action
    for ship in game[player_id]['ships']:
        actions = ['faster', 'slower', 'left', 'right', 'coordinates', '']
        name = ship
        # if the ship has already reached its maximum speed, removing 'faster' from the possible actions 
        if game[player_id]['ships'][ship]['speed'] == game['ships'][game[player_id]['ships'][ship]['type']]['max speed']:
            actions.remove('faster')
            action = choice(actions)
        #if the ship has already reached its minimum speed, removing 'slower' from the possible actions
        elif game[player_id]['ships'][ship]['speed'] == 0:
            actions.remove('slower')
            action = choice(actions)
        #Chosing the action
        else:
            action = choice(actions)
        if action == 'coordinates':
            #Chosing the coordinates in the board 
            line = randint(1, game['size']['lines'])
            column = randint(1, game['size']['columns'])
            #Checking if the coordinates are in the range of the ship
            while (abs(line- game[player_id]['ships'][ship]['lines'])+abs(column-game[player_id]['ships'][ship]['columns'])) > game['ships'][game[player_id]['ships'][ship]['type']]['range']:
                line = randint(1, game['size']['lines'])
                column = randint(1, game['size']['columns'])
            action = str(line) + '-' + str(column)
        if action == '':
            ship_action = ''
        else:
            ship_action = name + ':' + action + ' '
        orders += ship_action
    orders = orders[:-1]
    return orders

def buy_ships (game, player_id, orders=False):
    """Ask a player which ships he wants to buy
    
    Parameters
    ----------
    game: the information of the game (dico)
    player_id: number of the player, 1 or 2 (int)
    orders: the orders of the buying(optional)
        
    Return
    ------
    game: the information of the game (dico)
    
    Notes
    -----
    The players have only 100 coins to buy the ships, number of coins cannot be negative
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 23/02/2017)
    implémentation: Arthur Leclère (v.1 23/02/2017)
    implémentation: François Bernard (v.1 --> v.2 28/03/2017)
    """
    
    ## ask the player what he wants to buy
    game[player_id]['ships'] = {}
    if orders:
        achats = orders.split(' ')
    else:
        if player_id == 1:
            achats = raw_input('What do you want to buy? You can chose fighter or destroyer or battlecruiser? name:type  ')
        elif player_id == 2:
            achats = IA_buy_ships(game, 2)
        achats = achats.split(' ')
    
    ## create a list on the correct coordinates
    if player_id == 1:
        game['board'][(10,10)] = []
    else:
        game['board'][(game['size']['lines'] - 9, game['size']['columns'] - 9)] = []    
    
    ## for each ship the player buys, put all the information in the dictionnary
    for achat in achats:
        if ':' in achat:
            achat = achat.split(':')
            name = achat[0]
            type = achat[1] 
            if type not in ('fighter', 'destroyer', 'battlecruiser'):
                print 'Player %d, this ship type : %s is not a valid ship type. So this order will not be executed.' % (player_id, type)
            else : 
                ## if a player has not enough money to buy all the ships he wants, ignore the order
                if game['ships'][type]['cost'] > game[player_id]['coins']:
                    print 'Player %d, you do not have enough coins to buy this %s called %s. So this order will not be executed.' % (player_id, type, name)
                else:  
                    game[player_id]['coins'] -= game['ships'][type]['cost']
                    game[player_id]['ships'][name] = {}
                    game[player_id]['ships'][name]['type'] = type
                    game[player_id]['ships'][name]['speed'] = 0
                    game[player_id]['ships'][name]['hit points'] = game['ships'][type]['hit points']
                    if player_id == 1:
                        game[player_id]['ships'][name]['lines'] = 10
                        game[player_id]['ships'][name]['columns'] = 10
                        game[player_id]['ships'][name]['orientation'] = 315
                        game ['board'][(10,10)].append((1,name))
                    else:
                        game[player_id]['ships'][name]['lines'] = game['size']['lines'] - 9
                        game[player_id]['ships'][name]['columns'] = game['size']['columns'] - 9
                        game[player_id]['ships'][name]['orientation'] = 135
                        game['board'][(game['size']['lines'] - 9, game['size']['columns'] - 9)].append((2, name))
    
    return game

def slower(game, ship, player_id):
    """Brake a ship
    
    Parameters
    ----------
    game: the information of the game (dico)
    ship: name of the ship (str)
    player_id: number of the player, 1 or 2 (int)
    
    Return
    ------
    game: the information of the game (dico)
    
    Notes
    -----
    The speed cannot be negative
    The ship must exist in the player's ships
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 14/02/2017)
    implémentation: Florine Dardenne (v.1 21/02/2017)
    """
    
    #Checking if the ship has already reached its minimum speed and if not, modify the speed in the dictionnary
    if game[player_id]['ships'][ship]['speed'] > 0 :
        game[player_id]['ships'][ship]['speed'] -= 1
    else:
        print 'Player %d, your ship called %s has already reached its minimum speed.' % (player_id, ship)
        
    return game

def faster(game, ship, player_id):
    """Accelerate a ship
    
    Parameters
    ----------
    game: the information of the game (dico)
    ship: name of the ship (str)
    player_id: number of the player, 1 or 2 (int)
    
    Return
    ------
    game: the information of the game (dico)
    
    Notes
    -----
    The speed cannot be higher than the maximum speed of the ship
    The ship must exist in the player's ships
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 14/02/2017)
    implémentation: Florine Dardenne (v.1 21/02/2017)
    """
    
    #Checking if the ship has already reached its max speed and if not, modify the speed in the dictionnary 
    if game[player_id]['ships'][ship]['speed'] < game['ships'][game[player_id]['ships'][ship]['type']]['max speed']:
        game[player_id]['ships'][ship]['speed'] +=1
    else:
        print 'Player %d, your ship called %s has already reached its maximum speed.' % (player_id, ship)
    
    return game
    
def turn(game, ship, direction, player_id):
    """Turn the ship
    
    Parameters
    ----------
    game: the information of the game (dico)
    ship: name of the ship (str)
    direction: direction of the rotation = left or right (str)
    player_id: number of the player, 1 or 2 (int)
    
    Return
    ------
    game: the information of the game (dico)
    
    Notes
    -----
    The ship must exist in the player's ships
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard  (v.1 14/02/2017)
    implémentation: Florine Dardenne (v.1 21/02/2017)
    """
    
    #Setting the dictionnary with the new orientation
    if direction == 'right':
        game[player_id]['ships'][ship]['orientation'] -= 45    
    elif direction == 'left':
        game[player_id]['ships'][ship]['orientation'] += 45
    #Checking if the orientation is still a number between 0 and 360 degrees and modifying it if it's not the case     
    if game[player_id]['ships'][ship]['orientation'] < 0:
        game[player_id]['ships'][ship]['orientation'] += 360    
            
    elif game[player_id]['ships'][ship]['orientation'] > 359:
        game[player_id]['ships'][ship]['orientation'] -= 360
    
    return game

def attack(game, ship, coordinate, player_id):
    """Attack another ship
    
    Parameters
    ----------
    game: the information of the game (dico)
    ship: name of the ship (str)
    coordinate: coordinates of the ship the player wants to attack (tuple)
    player_id: number of the player, 1 or 2 (int)
    
    Returns
    ------
    game: the information of the game (dico)
    future_explosions: list of all future explosions (list)
    
    Notes
    -----
    Coordinates must be on the board
    If the coordinates are out of range, the ship cannot launch the missil
    The ship must exist in the player's ships 
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard  (v.1 14/02/2017)
    implémentation: Florine Dardenne (v.1 21/02/2017)
    implémentation: Florine Dardenne, François Bernard (v.1 --> v.2 23/02/2017)
    """
    
    #Checking whether the coordinate is in the board size
    if (int(coordinate[0]) > game['size']['lines']) or (int(coordinate[0]) < 1) or (int(coordinate[1]) > game['size']['columns']) or (int(coordinate[1]) < 1):
        future_explosions = ''
        print 'Player %d, the coordinate you entered %s is not in the board size.' % (player_id, coordinate)
    else:
        #Calculating the distance between the ship that attacks and the coordinates he has chosen 
        difference_lines = abs(int(coordinate[0]) - game[player_id]['ships'][ship]['lines'])
        difference_columns= abs(int(coordinate[1]) - game[player_id]['ships'][ship]['columns'])
        if difference_lines > game['size']['lines']/2:
            difference_lines = game['size']['lines'] - difference_lines
        if difference_columns > game['size']['columns']/2:
            difference_columns = game['size']['columns'] - difference_columns
        #Checking if the coordinates are in the range of the ship
        if difference_lines + difference_columns <= game['ships'][game[player_id]['ships'][ship]['type']]['range']:
            future_explosions = (coordinate, game['ships'][game[player_id]['ships'][ship]['type']]['attack'])
        else:
            future_explosions = ''
            print 'Player %d, the coordinate %s where %s wants to shoot is out of range.' % (player_id, coordinate, ship)
    return game,future_explosions

def give_and_execute_orders(game, player_id, orders=False):
    """Ask the player what move he wants to make and does it 
    
    Parameters
    ---------
    game: the information of the game (dico)
    player_id: id of the player (int)
    orders: the instructions of the player(str)
    
    Returns
    -------
    game: the information of the game (dico)
    list_future_explosions: list of the future explosions (list)
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 23/02/2017)
    implémentation: Florine Dardenne (v.1 21/02/2017)
    implémentation: François Bernard, Florine Dardenne (v.1 --> v.2 24/02/2017)
    implémentation: Arthur Leclère (v.2 --> v.3 31/03/2017)
    """
    
    list_future_explosions = []
    #Checking if the parameter orders is given 
    if orders != False:
        orders = orders 
    else:
        #Get the orders of the player 1 : the human and of the player 2 : the IA
        if player_id == 1:
            orders = raw_input('To which ship do you want to give an order and what do you want to ask him ? (order = faster or slower or (right/left) or yy-xx) name:action ')
        elif player_id == 2:
            orders = IA_give_orders(game, 2)
    #Check if there is something to do
    if orders != '':
        #Putting the instructions about the differents ships in a list 
        instructions = orders.split(' ')
        list_of_ships=[]
        #For every instruction, creating a list with instruction for every ships
        for instruction in instructions:
            instruction = instruction.split(':')
            ship = instruction[0]
            #Check if the player didn't give two instructions to one ship
            if ship not in list_of_ships:
                list_of_ships.append(ship)
            #Check if the ship belongs to the player who tries to give an order to 
                if ship not in game[player_id]['ships']:
                    print 'Player %d, %s is not your ship. Your order will not be executed.' % (player_id, ship)
                else:
                    #Executing the orders by calling the right function 
                    order = instruction[1]
                    future_explosions = ''
                    if order == '':
                        print 'Invalid instruction. So, your order will not not be executed.'
                    elif order == 'slower':
                        slower(game,ship, player_id)
                        
                    elif order == 'faster':
                        faster(game,ship,player_id)
        
                    elif order == 'left' or order == 'right':
                        turn(game,ship,order,player_id)
                        
                    elif len(order) > 2 and ((type(order[0]) == str and order[1] == '-' and type(order[2]) == str) or (type(order[0]) == str and type(order[1]) == str and order[2] == '-' and type(order[3]) == str)):
                        coordinate = order.split ('-')
                        game, future_explosions = (attack(game,ship, (int(coordinate[0]), int (coordinate[1])) ,player_id))
                    else:
                        print 'Player %d, this order : %s, is an invalid instruction. So, your order will not not be executed.' % (player_id, order)
                    #Adding the futures explosions to a list that will be used later because the explosions happen after the moves 
                    if future_explosions != '':
                            list_future_explosions.append(future_explosions)
            else:
                print 'Player %d, you already gave an order to this ship : %s' % (player_id, ship)
    return game,list_future_explosions
        
def move (game, player_id, ship):
    """Move the ship of the player_id
    
    Parameters
    ----------
    game: the information of the game (dico)
    player_id: number of the player_id (int)
    ship: name of the ship (str)    
    
    Return
    ------
    game: the information of the game (dico)
    
    Note
    ----
    The board is a torus : if a ship reaches the borders of the board it reappears on the other side of the board
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 14/02/2017)
    implémentation: François Bernard (v.1 23/02/2017)
    implémentation: François Bernard (v.1 --> v.2 28/02/2017) 
    implémentation: Florine Dardenne (v.2 --> v.3 07/04/2017)
    """
    
    orientation = game[player_id]['ships'][ship]['orientation']
    speed = game[player_id]['ships'][ship]['speed']
    ## check whether the speed of the ship is zero or not, if not remove the ship from the case and the dico
    if speed > 0:
        game['board'][(game[player_id]['ships'][ship]['lines'],game[player_id]['ships'][ship]['columns'])].remove((player_id,ship))
        if game['board'][(game[player_id]['ships'][ship]['lines'],game[player_id]['ships'][ship]['columns'])] == []:
            del game['board'][(game[player_id]['ships'][ship]['lines'],game[player_id]['ships'][ship]['columns'])]
    
        ## change the information of the ship on the dictionnary
        if orientation in (0, 45, 315):
            game[player_id]['ships'][ship]['columns'] += speed
        elif orientation in (135, 180, 225):
            game[player_id]['ships'][ship]['columns'] -= speed
        if orientation in (45, 90, 135):
            game[player_id]['ships'][ship]['lines'] -= speed
        elif orientation in (225, 270, 315):
            game[player_id]['ships'][ship]['lines'] += speed
        
            
        ## if the coordinates are not on the board, change them
        if game[player_id]['ships'][ship]['lines'] <= 0:
            game[player_id]['ships'][ship]['lines'] += game['size']['lines']
        elif game[player_id]['ships'][ship]['lines'] > game['size']['lines'] :
            game[player_id]['ships'][ship]['lines'] -= game['size']['lines']
        if game[player_id]['ships'][ship]['columns'] <= 0:
            game[player_id]['ships'][ship]['columns'] += game['size']['columns']
        elif game[player_id]['ships'][ship]['columns'] > game['size']['columns'] :
            game[player_id]['ships'][ship]['columns'] -= game['size']['columns']
    
        ## put the new information about the board in the dictionnary
        if (game[player_id]['ships'][ship]['lines'],game[player_id]['ships'][ship]['columns']) not in game ['board']:
            game['board'][(game[player_id]['ships'][ship]['lines'],game[player_id]['ships'][ship]['columns'])] = [(player_id,ship)]
        else:
            game['board'][(game[player_id]['ships'][ship]['lines'],game[player_id]['ships'][ship]['columns'])].append ((player_id,ship))
        ship_move = '%s moved to (%d, %d) - ' % (ship, game[player_id]['ships'][ship]['lines'],game[player_id]['ships'][ship]['columns'])
        game['list_moves'].append(ship_move)
    return game
    
def catch_abandoned_ships(game,IA):
    """Catch the abandoned ships
    
    Parameter
    ---------
    game: the information of the game (dico)
    
    Return
    ------
    game: the information of the game (dico)
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 23/02/2017)
    implémentation: Arthur Leclère, François Bernard (v.1 23/02/2017)
    implémentation: Arthur Leclère (v.1 --> v.2 28/03/2017)
    """
    
    #Checking the coordinates in the dictionnary
    for coordinates in game['board']:
        #Checking the player_id of the last ship in the list 
        player_id = game['board'][coordinates][len(game['board'][coordinates]) - 1][0]
        #Checking if there are some abandoned ships on the box and if there are at least to ships and that the last ship on the box is from the player 1 or 2  
        if game['board'][coordinates][0][0] == 0 and len(game['board'][coordinates]) >= 2 and player_id != 0:
            ships_on_coordinate = []
            for i in range(len(game['board'][coordinates])):
                ship_id = game['board'][coordinates][i][0]
                #Add the player_id in the list if there is one of its pawn on the box
                if ship_id not in ships_on_coordinate:
                    ships_on_coordinate.append(ship_id)
            #If the length of the list is greater than 2, then the abandoned ship is taken
            if len(ships_on_coordinate) == 2:
                for i in range(len(game['board'][coordinates])):
                    if game['board'][coordinates][i][0] == 0:
                            ship = game['board'][coordinates][i][1]
                            if ship in game[player_id]['ships']:
                                new_ship = ship + '_2'
                            else:
                                new_ship = ship
                            game['board'][coordinates][i] = (player_id,new_ship)
                            game[player_id]['ships'][new_ship] = {}
                            game[player_id]['ships'][new_ship]['speed'] = 0
                            game[player_id]['ships'][new_ship]['orientation'] = game[0][ship]['orientation']
                            game[player_id]['ships'][new_ship]['hit points'] = game['ships'][game[0][ship]['type']]['hit points']
                            game[player_id]['ships'][new_ship]['type'] = game[0][ship]['type']
                            game[player_id]['ships'][new_ship]['lines'] = coordinates[0]
                            game[player_id]['ships'][new_ship]['columns'] = coordinates[1]
                            if IA:
                                game[player_id]['ships'][new_ship]['way_to_follow'] = 'no_objective'
                            ship_taken = 'Player %d has taken %s - ' % (player_id, ship)
                            game['ships_taken'].append(ship_taken)
                            del game[0][ship]
    return game  
    
def check_explosions(game, list_future_explosions):
    """Check whether ships are hit or not by missils
    
    Parameters
    ----------
    game: the information of the game (dico)
    list_future_explosions: list of the future explosions (list)
    
    Returns
    ------
    game: the information of the game (dico)
    is_ship_hit: True if a ship was hit by a missil this turn, False otherwise (bool)
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 23/02/2017)
    implémentation: François Bernard (v.1 28/02/2017)
    implémentation: François Bernard (v.1 --> v.2 07/03/2017)
    """
    
    is_ship_hit = False
    #Checking if there are some future explosions
    if list_future_explosions != []:
        for player_id in (1, 2):
            for ships in game[player_id]['ships'].keys():
                for explosions in list_future_explosions:
                    #checking for every player, for every boat, if a boat is hit
                    if (game[player_id]['ships'][ships]['lines'], game[player_id]['ships'][ships]['columns']) == explosions[0]:
                        game [player_id]['ships'][ships]['hit points'] -= explosions[1]
                        ship_hit = '%s has been hit by a missil - ' % ships
                        game['ships_hit'].append(ship_hit)
                        is_ship_hit = True
                #Removing the ship if it has no more hit points 
                if game[player_id]['ships'][ships]['hit points']<=0:
                    game['board'][(game[player_id]['ships'][ships]['lines'], game[player_id]['ships'][ships]['columns'])].remove ((player_id, ships))
                    if game['board'][(game[player_id]['ships'][ships]['lines'], game[player_id]['ships'][ships]['columns'])] == []:
                        del game['board'][(game[player_id]['ships'][ships]['lines'], game[player_id]['ships'][ships]['columns'])]
                    del game[player_id]['ships'][ships]
                    ship_exploded = '%s exploded - '% ships
                    game['ships_hit'].append(ship_exploded)
    return game, is_ship_hit
       
def check_game_over(game):
    """Checks whether there has been 10 turns without any killed ships and count the points to say who is the winner
     
    Parameter
    ---------
    game: the information of the game (dico)
    
    Return
    -------
    loser: player_id of the player who lost (int)
    
    Notes
    -----
    If there has been 10 turns without any damaged ships, this is a victory by points for the player who owns the greatest amount of coins (considering his ships)
    If there is a tie after counting the points, the winner is chosen randomly
    If a player kills all the ships of the other player, this is a total victory for him

    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 23/02/2017)
    implémentation: Florine Dardenne (v.1 20/02/2017)
    implémentation: Arthur Leclère (v.1 --> v.2 23/02/2017)
    implémentation: Arthur Leclère, Florine Dardenne (v.2 --> v.3 24/03/2017)
    """
    #Checking if the number of turn without a hit is greater than 9 
    if game['turns'] > 9:
        score_1 = 0
        score_2 = 0
        #Creating a list of score to later only use the player id to modify the score 
        score = [score_1, score_2]
        #Checking the type of the all the ships of the 2 players 
        for player_id in (1,2):
            for ship in game[player_id]['ships']:
                ship_type = game[player_id]['ships'][ship]['type']
                #Modifying the scores
                if ship_type == 'battlecruiser':
                    score[player_id - 1] += 30
                elif ship_type == 'destroyer':
                    score[player_id - 1] += 20
                elif ship_type == 'fighter':
                    score[player_id - 1] += 10
        #Checking who has the lower score and so who losts                
        if score[0] > score[1]:
            loser = 2
        elif score[0] == score[1]:
            loser = randint(1,2)
        else:
            loser = 1
        print'Player %d lost, victory by points for the other player !' % loser
        
    #Checking if the number of turn without a hit is less than 10
    elif game['turns'] < 10:
        #Creating a list of losers 
        losers = []
        #Checking for every player if he still has ships, otherwise putting him in the list of losers 
        for player_id in (1,2):
            if game[player_id]['ships'] == {}:
                losers.append(player_id)
        #If there are no losers, loser =0
        if losers == []:
            loser = 0
        else:
            #If there are two losers, loser=3
            if len(losers) == 2:
                loser = 3
                print 'Both player lost, it is a tie'
            #If there is only one loser, loser=player_id of the loser 
            elif len(losers) == 1:
                loser = losers[0]
                print'Player %d lost, total victory for the other player !' % losers[0]
    #Return the number attributed to loser, 0--> no loser, 1--> player 1 lost, 2--> player 2 lost, 3--> players 1 and 2 lost 
    return loser
       
def one_turn(game, connection, player_id=False, IA = False):
    """Do all the actions of one turn
    
    Parameter
    ---------
    game: the information of the game (dico)
    player_id: 1 if the player 1 plays online, 2 if the player 2 plays online, False it is an offline game (optional)
    connection: information about the connection, False if it is not given (optional)
    
    Return
    ------
    game: the information of the game (dico)
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 23/02/2017)
    spécification: Florine Dardenne, Arthur Leclère (v.1 --> v.2 09/04/2017)
    implémentation: François Bernard(v.1 27/02/2017)
    implémentation: Arthur Leclère(v.1 --> v.2 24/03/2017)
    """
    
    #Displaying all ships moves from the last turn and the board
    game = display_ships_actions(game)
    display_board(game)
    print game
    #Checking if the game is on one computer or 2 differents computers and then execute a turn of the game
    if connection != False:
        if player_id == 1:
            if not IA:
                orders_1 = get_IA_orders(game, 1)
            else: 
                orders_1 = get_IA_order (game, 1)
            game, list_future_explosions_1 = give_and_execute_orders(game, 1, orders_1)
            notify_remote_orders(connection, orders_1)
            orders_2 = get_remote_orders(connection)
            game, list_future_explosions_2 = give_and_execute_orders(game, 2, orders_2)
        elif player_id == 2:
            orders_1 = get_remote_orders(connection)
            game, list_future_explosions_1 = give_and_execute_orders(game, 1, orders_1)
            if not IA:
                orders_2 = get_IA_orders(game, 2)
            else:
                orders_2 = get_IA_order (game, 2)
            game, list_future_explosions_2 = give_and_execute_orders(game, 2, orders_2)
            notify_remote_orders(connection, orders_2)
    else:
        game, list_future_explosions_1 = give_and_execute_orders(game, 1)
        orders_2 = get_IA_order(game, 2)
        game, list_future_explosions_2 = give_and_execute_orders(game, 2, orders_2)
    #Making the ships move on the board 
    for player_id in (1, 2):
        for ship in game[player_id]['ships']:
            game = move(game, player_id, ship)
    game = catch_abandoned_ships(game,IA)
    game, is_ship_hit_1 = check_explosions(game, list_future_explosions_1)
    game, is_ship_hit_2 = check_explosions(game, list_future_explosions_2)
    #Adding a turn without hit or reinitialize the count
    if is_ship_hit_1 or is_ship_hit_2:
        game['turns']=0
    elif not is_ship_hit_1 and not is_ship_hit_2:
        game['turns'] +=1
    #Scrolling automatically the screen 
    system('clear')
    return game

def entire_game(data, player_id=False, remote_IP='127.0.0.1', IA= False):
    """Play entire game (online vs another player or offline vs the IA)
    
    Parameters
    ----------
    data : path to the file (str)
    player_id : 1 if the player 1 plays online, 2 if the player 2 plays online, False it is an offline game (int, optional)
    remote_IP : remote IP of the player the user wants to reach (str, optional)
        
    Version
    -------
    spécification: François Bernard (v.1 27/02/2017)
    spécification: Florine Dardenne, Arthur Leclère (v.1 --> v.2 09/04/2017)
    implémentation: François Bernard (v.1 27/02/2017)
    implémentation: Arthur Leclère, Florine Dardenne (v.1 --> v.2 31/03/2017)
    implémentation: Arthur Leclère (v.2 --> v.3 03/04/2017)
    """
    
    #Starting the game
    game = start_game(data)
    display_board(game)
    #Check if the game is between 2 computers, against an IA or on one computer
    if remote_IP != '127.0.0.1':
        if player_id == 1:
            connection = connect_to_player(2, remote_IP, True)
            if not IA:
                orders_1 = get_IA_orders(game, 1)
            else:
                orders_1 = IA_buy_ships(game, 1)
            notify_remote_orders(connection, orders_1)
            game = buy_ships(game, 1, orders_1)
            orders_2 = get_remote_orders(connection) 
            game = buy_ships(game, 2, orders_2)
            if IA:
                game = IA_start_game (game, 1)
        elif player_id == 2:
            connection = connect_to_player(1, remote_IP, True)
            orders_1 = get_remote_orders(connection)
            game = buy_ships(game, 1, orders_1)
            if not IA:
                orders_2 = get_IA_orders(game, 2)
            else:
                orders_2 = IA_buy_ships(game, 2)
            notify_remote_orders(connection, orders_2)
            game = buy_ships(game, 2, orders_2)
            if IA:
                game = IA_start_game(game, 2)
                
    else:
        game = buy_ships(game, 1)
        game = buy_ships(game, 2)
        game = IA_start_game(game, 2)
        connection = False
    #Scrolling automatically the screen
    system('clear')
    #Initializing the number of turn without ship hit by a missil
    game['turns'] = 0
    #Playing the game until someone has lost it 
    while check_game_over(game) == 0:
        one_turn(game, connection, player_id, IA)
    print 'Game is over'
    if remote_IP != '127.0.0.1':
        disconnect_from_player(connection)
    
def left(ship, player_id):
    """Turn the ship left
    
    Parameters
    ----------
    ship: name of the ship (str)
    player_id: number of the player, 1 or 2 (int)
    
    Notes
    -----
    The ship must exist in the player's ships
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard  (v.1 14/02/2017)
    implémentation: Florine Dardenne (v.1 21/02/2017)
    """
    
    ship['orientation'] += 45
    if ship['orientation'] < 0:
        ship['orientation'] += 360    
            
    elif ship['orientation'] > 359:
        ship['orientation'] -= 360
            
def right(ship, player_id):
    """Turn the ship right
    
    Parameters
    ----------
    ship: name of the ship (str)
    player_id: number of the player, 1 or 2 (int)
    
    Notes
    -----
    The ship must exist in the player's ships
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard  (v.1 14/02/2017)
    implémentation: Florine Dardenne (v.1 21/02/2017)
    """
    
    ship['orientation'] -= 45  
        
    if ship['orientation'] <0:
        ship['orientation'] += 360    
            
    elif ship['orientation'] > 359:
        ship['orientation'] -= 360

def faster2(ship,player_id):
    """Accelerate a ship
    
    Parameters
    ----------
    ship: name of the ship (str)
    player_id: number of the player, 1 or 2 (int)
    
    Notes
    -----
    The speed cannot be higher than the maximum speed of the ship
    The ship must exist in the player's ships
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 14/02/2017)
    implémentation: Florine Dardenne (v.1 21/02/2017)
    """
    
    ship['speed']+=1

def slower2(ship,player_id):
    """Brake a ship
    
    Parameters
    ----------
    ship: name of the ship (str)
    player_id: number of the player, 1 or 2 (int)
    
    Notes
    -----
    The speed cannot be negative
    The ship must exist in the player's ships
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 14/02/2017)
    implémentation: Florine Dardenne (v.1 21/02/2017)
    """
    
    if ship['speed'] > 0:
        ship['speed'] -= 1
 
def move2 (ship, player_id):
    """Move the ship of the player_id
    
    Parameters
    ----------
    player_id: number of the player_id (int)
    ship: name of the ship (str)    
    
    Notes
    -----
    The board is a torus : if a ship reaches the borders of the board it reappears on the other side of the board
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 14/02/2017)
    implémentation: François Bernard (v.1 23/02/2017)
    implémentation: François Bernard (v.1 --> v.2 28/02/2017) 
    implémentation: Florine Dardenne (v.2 --> v.3 07/04/2017)
    """

    ## change the information of the ship on the dictionnary
    if ship['orientation'] in (0, 45, 315):
            ship['columns'] += ship['speed']
    elif ship['orientation'] in (135, 180, 225):
            ship['columns'] -= ship['speed']
    if ship['orientation'] in (45, 90, 135):
            ship['lines'] -= ship['speed']
    elif ship['orientation'] in (225, 270, 315):
            ship['lines'] += ship['speed'] 
                               
## Pour importer le dico
fh = open('/home/users/100/fldarden/Documents/dico_IA_7.pkl', 'rb')
dico = load(fh)
fh.close ()  

## Retourne les chemins les + courts pour nous et notre adversaire
def length_abandonned_ship(game, ship):
    """Return the shortest ways from the starting point to a coordinate for the 2 players
    
    Parameters
    ----------
    game: the information of the game (dico)
    ship: name of the ship (str)
    
    Returns
    -------
    chemin_1: shortest ways from the starting point to a coordinate for the player 1 (list)     
    chemin_2: shortest ways from the starting point to a coordinate for the player 2 (list)     
    
    Notes
    -----
    The board is a torus : if a ship reaches the borders of the board it reappears on the other side of the board
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 14/02/2017)
    implémentation: François Bernard (v.1 23/02/2017)
    implémentation: François Bernard (v.1 --> v.2 28/02/2017)
    """
    
    nb_lines = game[0][ship]['lines']
    nb_columns = game[0][ship]['columns']
    if nb_lines > 30:
        nb_lines -= game ['size']['lines']
    if nb_columns > 30:
        nb_columns -= game ['size']['columns']
    nb_lines -= 10
    nb_columns -= 10
    best_nothing = 5
    for chemin in dico[(nb_lines, nb_columns)][315]:
        nb_nothing =0
        for i in range(len(dico[(nb_lines, nb_columns)][315][0])):
            if chemin [i] == 'nothing':
                nb_nothing += 1
        if nb_nothing < best_nothing:
            best_nothing = nb_nothing
            chemin_1 = chemin
    nb_lines = game[0][ship]['lines']
    nb_columns = game[0][ship]['columns']
    if nb_lines < 11:
        nb_lines += game['size']['lines']
    if nb_columns < 11:
        nb_columns += game ['size']['columns']
    nb_lines -= (game['size']['lines'] - 9)
    nb_columns -= (game['size']['columns'] - 9)
    best_nothing = 5
    for chemin in dico[(nb_lines, nb_columns)][135]:
        nb_nothing = 0
        for i in range(len(dico[(nb_lines, nb_columns)][135][0])):
            if chemin [i] == 'nothing':
                nb_nothing +=1
        if nb_nothing < best_nothing:
            best_nothing = nb_nothing
            chemin_2 = chemin
    return chemin_1, chemin_2
    
## Mets dans le dico de chaque vaisseau le chemin qu'il devra emprunter (début du jeu)
def IA_start_game(game, player_id):
    """Attribute some abandoned ships to catch to some ships
    
    Parameters
    ----------
    game: the information of the game (dico)
    ship: name of the ship (str)
    
    Returns
    -------
    game: the information of the game (dico)
    
    Notes
    -----
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 14/02/2017)
    implémentation: François Bernard (v.1 23/02/2017)
    implémentation: François Bernard (v.1 --> v.2 28/02/2017)
    """
    ways_to_follow =[]
    for abandonned_ship in game[0]:
        chemin_1, chemin_2 = length_abandonned_ship(game, abandonned_ship)
        print len (chemin_1)
        print len (chemin_2)
        if (player_id == 1 and len(chemin_1) <= len(chemin_2)):
            ways_to_follow.append(chemin_1)
            game['targets'].append(abandonned_ship)
        if (player_id == 2 and len(chemin_1) >= len(chemin_2)):
            ways_to_follow.append (chemin_2)
            game['targets'].append(abandonned_ship)
    print ways_to_follow
    list_targets = game['targets']
    for ship in game[player_id]['ships']:
        if ways_to_follow != []:
            game[player_id]['ships'][ship]['way_to_follow'] = ways_to_follow [0]
            game[player_id]['ships'][ship]['target']= list_targets[0]
            del list_targets[0]
            del ways_to_follow [0]
        else:
            game[player_id]['ships'][ship]['way_to_follow'] = 'no_objective'
    return game 
    
## Retourne l'ordre complet à envoyer (pour chaque tour)
def get_IA_order(game, player_id):
    """Return the orders given by the non-naïve IA 
    
    Parameters
    ----------
    game: the information of the game (dico)
    player_id: number of the player_id (int)
    
    Return
    -------
    orders: orders chosen by IA player (str)    
    
    Notes
    -----
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 14/02/2017)
    implémentation: François Bernard (v.1 23/02/2017)
    implémentation: François Bernard (v.1 --> v.2 28/02/2017)
    """ 
    
    orders =''
    actions = ['faster', 'right', 'left', 'slower']
    order = choice (actions)
    for ship in game[player_id]['ships']:
        if game[player_id]['ships'][ship]['way_to_follow'] == []:
            new_objective(game, ship, player_id)
        function = game[player_id]['ships'][ship]['way_to_follow'][0]
        if (ship_in_range (game, player_id, ship) and function == 'nothing') or (game[player_id]['ships'][ship]['way_to_follow'] == 'no_objective') or 'way_to_follow' not in game[player_id]['ships'][ship] :
            orders += ship + ':' + order +' '
        else:
            if function == faster or function == faster2:
                order = 'faster'
            elif function == slower or function == slower2:
                order = 'slower'
            elif function == left:
                order = 'left'
            elif function == right:
                order = 'right'
            else:
                order = ''
            print order
            del game[player_id]['ships'][ship]['way_to_follow'][0]
            orders += ship + ':' + order +' '
    orders = orders[:-1]
    return orders
    
## Retourne True si notre vaisseau est dans la portée d'un vaisseau ennemi
def ship_in_range(game, player_id, ship):
    """Return whether the ship is in the range of an ennemy ship
    
    Parameters
    ----------
    game: the information of the game (dico)
    player_id: number of the player_id (int)
    ship: name of the ship (str)
    
    Return
    -------
    is_in_range: True if the ship is in the range of an ennemy ship, False otherwise (bool)     
    
    Notes
    -----
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 14/02/2017)
    implémentation: François Bernard (v.1 23/02/2017)
    implémentation: François Bernard (v.1 --> v.2 28/02/2017)
    """ 
    
    is_in_range = False
    ennemy_id = 3 - player_id
    for ennemy_ship in game [ennemy_id]['ships']:
        difference_lines = abs(game[player_id]['ships'][ship]['lines'] - game[ennemy_id]['ships'][ennemy_ship]['lines'])
        difference_columns= abs(game[player_id]['ships'][ship]['columns'] - game[ennemy_id]['ships'][ennemy_ship]['columns'])
        if difference_lines > game['size']['lines']/2:
            difference_lines = game['size']['lines'] - difference_lines
        if difference_columns > game['size']['columns']/2:
            difference_columns = game['size']['columns'] - difference_columns
        #Checking if the coordinates are in the range of the ship
        if difference_lines + difference_columns <= game['ships'][game[ennemy_id]['ships'][ennemy_ship]['type']]['range']:
            is_in_range = True
    return is_in_range
    
def new_objective(game, ship, player_id):
    """Add a new objective (abandoned ship to catch or xyz) to a ship which has just caught an abandoned ship
    
    Parameters
    ----------
    game: the information of the game (dico)
    player_id: number of the player_id (int)
    ship: name of the ship (str)
    
    Notes
    -----
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 14/02/2017)
    implémentation: François Bernard (v.1 23/02/2017)
    implémentation: François Bernard (v.1 --> v.2 28/02/2017)
    """ 
    
    ennemy_id = 3 - player_id
    for abandonned_ship in game[0]:
        if abandonned_ship not in game['targets'] and game[player_id]['ships'][ship]['way_to_follow'] ==[] :
            line = game[0][abandonned_ship]['lines'] - game[player_id]['ships'][ship]['lines']
            column = game[0][abandonned_ship]['columns'] - game[player_id]['ships'][ship]['columns']
            if line > 20:
                line -= game['size']['lines']
            if line < - 20:
                line += game['size']['lines']
            if column > 20:
                column -= game['size']['columns']
            if column < -20:
                column += game['size']['columns']
            chemins = list_of_choices()
            objective = True
            best_chemin = best_way(chemins, game[player_id]['ships'][ship]['speed'],(line, column), game[player_id]['ships'][ship]['orientation'], game[player_id]['ships'][ship]['type'])
            print best_chemin
            if best_chemin == []:
                objective = False
            else:
                for ennemy_ship in game[ennemy_id]['ships']:
                    line = game[0][abandonned_ship]['lines'] - game[ennemy_id]['ships'][ennemy_ship]['lines']
                    column = game[0][abandonned_ship]['columns'] - game[ennemy_id]['ships'][ennemy_ship]['columns']
                    if line > 20:
                        line -= game['size']['lines']
                    if line < -20:
                        line += game['size']['lines']
                    if column > 20:
                        column -= game['size']['columns']
                    if column < -20:
                        column += game['size']['columns']
                    ennemy_chemin = best_way(chemins, game[ennemy_id]['ships'][ennemy_ship]['speed'],(line, column), game[ennemy_id]['ships'][ennemy_ship]['orientation'], game[ennemy_id]['ships'][ennemy_ship]['type'])
                    print ennemy_chemin
                    if ennemy_chemin !=[] and best_chemin!=[]and len(ennemy_chemin[0]) <= len(best_chemin[0]):
                        objective = False
            if objective:
                best_nothing = 6
                for chemin in best_chemin:
                    nb_nothing = 0
                    for i in range(len(chemin)):
                        if chemin [i]== 'nothing':
                            nb_nothing +=1
                    if nb_nothing < best_nothing:
                        best_nothing = nb_nothing
                        way_to_follow = chemin
                game[player_id]['ships'][ship]['way_to_follow'] = way_to_follow
                if game[player_id]['ships'][ship]['target'] in game['targets']:
                    game['targets'].remove(game[player_id]['ships'][ship]['target'])
                del game[player_id]['ships'][ship]['target']
                game['targets'].append(abandonned_ship)
                game[player_id]['ships'][ship]['target'] = abandonned_ship
    if game[player_id]['ships'][ship]['way_to_follow'] == []:
        game[player_id]['ships'][ship]['way_to_follow'] = 'no_objective'

def best_way(chemins, speed, coordinates, orientation, ship_type):
    """Return the best chemin to a coordinate for a ship in function of its starting coordinate, speed, orientation and type
    
    Parameters
    ----------
    chemins: all the possible ways in 5 turns (list)
    speed: speed of the ship (int)
    coordinates: coordinate of the ship (tuple)
    orientation: orientation of the ship (int)
    ship_type: type of the ship (str)
    
    Return
    ------
    best_chemin: best way for the ship to an abandoned ship (list)  
    
    Notes
    -----
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 14/02/2017)
    implémentation: François Bernard (v.1 23/02/2017)
    implémentation: François Bernard (v.1 --> v.2 28/02/2017)
    """ 
     
    best_chemin =[]
    best_turn = 12
    for chemin in chemins:
        ship = {}
        ship['speed'] = speed
        ship ['lines'] = 0
        ship['columns'] = 0
        ship['orientation'] = orientation
        turns = 0
        while turns < len(chemin) and (ship['lines'], ship['columns']) != coordinates:
            if ((ship_type == 'battlecruiser' and ship['speed'] == 1) or (ship_type == 'destroyer' and ship['speed'] == 2) or (ship_type == 'fighter' and ship['speed'] == 5 )) and chemin[turns] == faster: 
                del chemin[turns]
            else:
                if chemin[turns] != 'nothing':
                    chemin[turns](ship, 1)
                move2 (ship, 1)
                turns += 1
        if (ship['lines'], ship['columns']) == coordinates:
            if chemin[:turns] not in best_chemin:
                if turns < best_turn:
                    best_chemin = [chemin[:turns]]
                    best_turn = turns
                elif turns == best_turn:
                    best_chemin.append(chemin[:turns])
                    

    return best_chemin

def list_of_choices():
    """Return a tree choice
    
    Return
    ------
    chemins: all the possible ways in 5 turns (list)
    
    Notes
    -----
    
    Version
    -------
    spécification: Arthur Leclère, Florine Dardenne, François Bernard (v.1 14/02/2017)
    implémentation: François Bernard (v.1 23/02/2017)
    implémentation: François Bernard (v.1 --> v.2 28/02/2017)
    """ 
    
    choices = [faster2, left, right, slower2, 'nothing']
    chemins = []  
    for choice in choices :
        for choice_1 in choices:
            for choice_2 in choices:
                for choice_3 in choices:
                    for choice_4 in choices:
                        for choice_5 in choices:
                            list_choices = [choice, choice_1, choice_2, choice_3, choice_4, choice_5]
                            nb_faster = 0
                            nb_slower = 0
                            for function in list_choices:
                                if function == faster2:
                                    nb_faster +=1
                                if function == slower2:
                                    nb_slower +=1
                            if nb_faster < 6 and nb_faster > 0 and nb_faster >=  nb_slower:
                                chemins.append(list_choices)

    print len(chemins)
    return chemins

entire_game("donnees_2.cis", False, '127.0.0.1', False)

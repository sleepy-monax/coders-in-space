# -*- coding: utf-8 -*-
from random import randint
import random
import os
import remote_play

#A faire à la fin : vérifier spécifications et paramètres 
#dico en paramètre si on en a besoin (pas obligatoire mais mieux)
#return le dictionnaire si on l'a modifié (pas obligatoire mais mieux)

#start_game('C:\Users\dupontad\Downloads', 'plateau.txt', 'adri', 'IA')

def start_game(path, file_name, player_1, player_2, ip):
    """The function which starts a game.
     
    Parameters
    -----------
    path : the path to access the file (str)
    file_name : the name of the file (str)
    player_1 : the type of the first player (str)
    player_2 : the type of the second player (str)
    
    Note
    ----
    if you want to play against an IA, player must be named 'IA'
    if you want to play, give your name
        
    Version
    -------
    specification : Adrien Dupont (v.1 27/02/18)
    implémentation : Elisa Etienne (v.1 09/03/18)
    implémentation : Adrien Dupont (v.2 12/04/18)
    """
    if player_1 == 'IA':
        player_id = 2
    
    else :
        player_id = 1
        
    connection = remote_play.connect_to_player(player_id, ip, True)
    
    #creating the mandatory dictionnaries
    informations = {}
    informations = reading_file_board(path, file_name)
    
    teams = {}
    teams = creating_teams_dic(informations, player_1, player_2)
    
    #vérifier x et y row et range
    
    #finds the size of the board
    nb_rows = informations['size']['nb_rows']
    nb_columns = informations['size']['nb_columns']
    
    #loop
    nb_turns = 0
    
    while end_game(teams, player_1, player_2) == False:
        
        #displays all the informations about both teams
        show_informations(teams, informations)
        
        #takes the orders from player_1 and applies them
        
        #si je suis le joueur 1
        if player_1 == 'IA':
            orders = smart_IA(teams, informations, nb_turns, player_1)
            print (orders)
            remote_play.notify_remote_orders(connection, orders)
            teams = take_orders(orders, player_1, teams, informations)
            orders = remote_play.get_remote_orders(connection)
            teams = take_orders(orders, player_2, teams, informations)
        
        #si je suis le joueur 2
        else:
            orders = remote_play.get_remote_orders(connection)
            teams = take_orders(orders, player_1, teams, informations)
            orders = smart_IA(teams, informations, nb_turns, player_2)
            print (orders)
            remote_play.notify_remote_orders(connection, orders)
            teams = take_orders(orders, player_2, teams, informations)

        nb_turns +=1
        
        #4ème phase
        teams, informations = collect(teams, informations)
        teams = ores_drop_off(teams)
        teams = clear_dictionary (teams)
        board_printing(teams, informations, nb_rows, nb_columns)
        
    #if eng_game() returns 'True', then the game is over
    print('Game Over. Thanks for playing!')
    
def end_game(teams, player_1, player_2):
    """ Checks if the game is over.
    
    Parameters
    ----------
    teams : dictionnary with all the teams' informations (team a and team b) (dict)
    player_1 : the name of the first player (str)
    player_2 : the name of the second player (str)
    
    Returns
    -------
    status : True or False in function of its status
    
    Version
    -------
    specification : Elisa Etienne (v.1 27/02/18)
    implementation : Elisa Etienne (v.1 30/03/18)
    """
    
    if teams[player_1]['portal']['p_1']['life'] <= 0 and teams[player_2]['portal']['p_1']['life'] <= 0:
        print('No one wins!')
        return True
        
    elif teams[player_2]['portal']['p_1']['life'] <= 0:
        print('The %s wins the game!' %(player_1))
        return True
        
    elif teams[player_1]['portal']['p_1']['life'] <= 0:
        print('The %s wins the game!' %(player_2))
        return True
        
    else :
        return False
        
def take_orders(orders, player, teams, informations):
    """ Takes the orders and applies them.
    
    Parameters
    -------------
    orders : the sentence with all the orders (str)
    player : the team which gives the orders (str)
    teams : dictionnary with all the teams' informations (team a and team b) (dict)
    informations : the dictionnary with all the informations about the portals coords, the asteroids and the board's size in it. (dict)
    
    Returns
    ---------
    teams : dictionnary (actualized) with all the teams' informations (team a and team b) (dict)
    
    Version
    -------
    specification : Elisa Etienne and Adrien Dupont(v.1 27/02/18)
    specification : Valentin Kanen (v.2 21/04/18)
    implementation : Elisa Etienne (v.1 30/03/18)
    implementation : Adrien Dupont (v.2 12/04/18)
    """
    type_construction = ('scout', 'warship','excavator-S','excavator-M','excavator-L')
    lockings = ('lock','release')
    
    orders = orders.split(' ')
    liste = []
    for i in orders :
        order = i.split(':')
        liste.append(order)
    
    for i in liste :

        for j in i:

            if j in type_construction :
                #buy(teams, buyer, construct_type, name)
                teams = buy(teams, player, j, i[0])

            if j in lockings :
                
                excavator_name = i[0]
                futur_status = j
                
                #switch_lock(teams, excavator, statement, owner)
                teams = switch_lock(teams, excavator_name, futur_status, player)

            for coords in j :
                if coords == '@':
                    coords = j.split('@')
                    coords = str(coords[1]).split('-')
                    
                    coord_x = int(coords[0])
                    coord_y = int(coords[1])
                    
                    warship_name = i[0]
                    #move_construction(teams, new_x, new_y, construct_name, owner)
                    teams = move_construction(teams, coord_x, coord_y, warship_name, player,informations)

                elif coords == '*':
                    coords = j.split('*')
                    coords = str(coords[1]).split('-')
                    
                    coord_x = int(coords[0])
                    coord_y = int(coords[1])
                    
                    warship_name = i[0]
                    
                    #! les coords[1] et coords[0] sont en str.
                    #attack(teams, attacker, x, y, player)
                    teams = attack(teams, warship_name, coord_x, coord_y, player)
                    
    return(teams)
    #/!\ l'ordre des actions est-il respecté comme ceci ?? Vu que je suis l'ordre de la liste je ne suis pas totalement sûre              
    #comment mettre une élimination en cas de non respect de syntaxe ?
    #order exemple : 'dave:scout olivaw:*32-4 robbie:lock speedy:release dave:@21-4'
        


def find_coords(teams, owner, construct_type, construct_name):
    """ Computes all the slots occupied by a construction in function of its type and its center.

    Parameters
    ----------
    teams : dictionnary with all the teams' informations (team a and team b) (dict)
    owner : the name of the team which owns the construction (str)
    construct_type : the type of the construction (str)
    construct_name : the name of the construction (str)
    
    Returns
    -------
    coords : the coords occupied by the construction ((x,y),(x,y),...) (list)
    
    Notes
    -----
    owner must be 'team_a' or 'team_b'
    construct_type must be 'warships','excavators','portal'
    
    Version
    -------
    specification : Adrien Dupont (v.1 27/02/18)
    specification : Adrien Dupont (v.2 09/03/18)
    implentation : Adrien Dupont (v.1 12/03/18)
    """
    #si la construction sort?
    
    construct = '/'
    
    #finds the center
    #if construct_name in teams[owner][construct_type]:
    center_x = teams[owner][construct_type][construct_name]['position_x']
    center_y = teams[owner][construct_type][construct_name]['position_y']
    construct = teams[owner][construct_type][construct_name]['type']
            
    if construct == 'scout':
        list_x = (center_x-1,center_x,center_x+1,center_x-1,center_x,center_x+1,center_x-1,center_x,center_x+1)
        list_y = (center_y-1,center_y-1,center_y-1,center_y,center_y,center_y,center_y+1,center_y+1,center_y+1)

    elif construct == 'warship':
        list_x = (center_x-1, center_x, center_x+1, center_x-1, center_x, center_x+1, center_x-2, center_x-1,center_x,center_x+1,center_x+2,center_x-2, center_x-1,center_x,center_x+1,center_x+2,center_x-2, center_x-1,center_x,center_x+1,center_x+2)
        list_y = (center_y-2, center_y-2, center_y-2, center_y+2, center_y+2, center_y+2, center_y-1,center_y-1,center_y-1,center_y-1,center_y-1,center_y,center_y,center_y,center_y,center_y, center_y+1,center_y+1,center_y+1,center_y+1,center_y+1)
            
    elif construct == 'excavator-S':
        list_x = ((center_x,))
        list_y = ((center_y,))
        
    elif construct == 'excavator-M':
        list_x = (center_x-1, center_x, center_x, center_x, center_x+1)
        list_y = (center_y, center_y-1,center_y, center_y+1, center_y)
        
    elif construct == 'excavator-L':
        list_x = (center_x-2, center_x-1, center_x, center_x, center_x, center_x, center_x, center_x+1, center_x+2)
        list_y = (center_y, center_y, center_y, center_y-2, center_y-1, center_y+1, center_y+2, center_y, center_y)
    
    elif construct == 'P':
        list_x = (center_x-2,center_x-1,center_x,center_x+1,center_x+2,center_x-2,center_x-1,center_x,center_x+1,center_x+2,center_x-2,center_x-1,center_x,center_x+1,center_x+2,center_x-2,center_x-1,center_x,center_x+1,center_x+2,center_x-2,center_x-1,center_x,center_x+1,center_x+2)
        list_y = (center_y-2,center_y-2,center_y-2,center_y-2,center_y-2,center_y-1,center_y-1,center_y-1,center_y-1,center_y-1,center_y,center_y,center_y,center_y,center_y,center_y+1,center_y+1,center_y+1,center_y+1,center_y+1,center_y+2,center_y+2,center_y+2,center_y+2,center_y+2)
    
    coords_list = (list_x, list_y)

    return(coords_list)
    
    #to use the coords:
        
    #list_x = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]
    #list_y = [10,20,30,40,50,60,70,80,90,100,110,120,130,140]
    #coords=(liste_x,liste_y)
    
    #for i in coords[1]:
    #    print(i)
    
    #    coord x = list_x[i]
    #    coord y = list_y[i]
    
def move_construction(teams, new_x, new_y, construct_name, owner, informations):
    """ Moves a construction to new_x, new_y.
    
    Parameters
    ----------
    teams : dictionnary with all the teams' informations (team a and team b) (dict)
    new_x : the new x to move the center to (int)
    new_y : the new y to move the center to (int)
    construct_name : the name of the construction (str)
    owner : the name of the team which owns the construction (str)
    informations : the dictionnary with all the informations about the portals coords, the asteroids and the board's size in it. (dict)
    
    Returns
    -------
    teams : dictionnary (actualized) with all the teams' informations (team a and team b) (dict)
    
    Version
    -------
    specification : Adrien Dupont (v.1 27/02/18)
    specification : Adrien Dupont (v.2 09/03/18)
    specification : Valentin Kanen (v.2 21/04/18)
    implentation : Adrien Dupont (v.1 15/03/18)
    implentation : Valentin Kanen (v.2 21/04/18)
    """
    #si la construction sort?
    #attention à la condition d'un déplacement d'1 case max!
    
    all_possibilities = ('warships', 'excavators', 'portal')
        
    for possibility in all_possibilities:
        if construct_name in teams[owner][possibility]:
            construct_type = possibility
    
    center_x = teams[owner][construct_type][construct_name]['position_x']
    center_y = teams[owner][construct_type][construct_name]['position_y']
    
    if center_x <= new_x+1 and center_x >= new_x-1  and center_y <= new_y+1 and center_y >= new_y-1:
        teams[owner][construct_type][construct_name]['position_x'] = new_x
        teams[owner][construct_type][construct_name]['position_y'] = new_y
        
        x_max = informations['size']['nb_columns']
        y_max = informations['size']['nb_rows']
        type_const = teams[owner][construct_type][construct_name]['type']
              
        if type_const == 'excavator-S':
            if new_x<=0 or new_y<=0 or new_x>x_max or new_y>y_max:
                teams[owner][construct_type][construct_name]['position_x']=center_x
                teams[owner][construct_type][construct_name]['position_y']=center_y
                print ('Impossible to quit the board')
                
        elif type_const == 'excavator-M' or type_const=='scout':
            if new_x-1<=0 or new_y-1<=0 or new_x+1>x_max or new_y+1>y_max:
                teams[owner][construct_type][construct_name]['position_x']=center_x
                teams[owner][construct_type][construct_name]['position_y']=center_y
                print ('Impossible to quit the board')
                
        elif type_const == 'excavator-L' or type_const=='warship':
            if new_x-2<=0 or new_y-2<=0 or new_x+2>x_max or new_y+2>y_max:
                teams[owner][construct_type][construct_name]['position_x']=center_x
                teams[owner][construct_type][construct_name]['position_y']=center_y
                print ('Impossible to quit the board')
        else:  
            print('Construction moved')
        
    else:
        print('Wrong move')
    

    return(teams)
    
def board_printing(teams, informations, nb_columns, nb_rows):
    """ Prints the board of the game with all the informations on it.
    
    Parameters
    ----------
    teams : dictionnary with all the teams' informations (team a and team b) (dict)
    informations : the dictionnary with all the informations about the portals coords, the asteroids and the board's size in it. (dict)
    nb_colums : number of columns wanted (int)
    nb_rows : number of rows wanted (int)
    
    Notes
    -----
    The board must be big enough to launch the game with the portals positions
    
    Version
    -------
    specification : Valentin Kanen (v.1 27/02/18)
    specification : Adrien Dupont (v.2 09/03/18)
    implentation : Adrien Dupont (v.1 12/03/18)
    """
    
    grid = []

    nb_rows += 1
    nb_columns += 1
    
    #grid_making
    for row in range(nb_rows):
        grid.append([])
        for column in range(nb_columns):
            grid[row].append('. ')
    
    tableau = ''
    
    check_row = 0
    check_column = 0

    #adds the numbers on the columns
    for column in range(nb_columns):
        if check_column >= 10 :
            check_column = str(check_column)
            check_column = check_column[1]
        grid[0][column] = str(check_column) + ' '
        check_column = int(check_column)
        check_column += 1

    #adds the numbers on the side of the rows
    for row in range(nb_rows):
        if check_row >= 10 :
            check_row = str(check_row)
            check_row = check_row[1]
        grid[row][0] = str(check_row) + ' '
        check_row = int(check_row)
        check_row += 1
        
    check_row = 0
    check_column = 0
    
    #find_coords
    list_constructs = ['warships','excavators','portal']
    #teams[team][construct_type][construct_name]
    
    for team in teams:
        #player_1 and player_2
        
        for construct_type in list_constructs:
            #warships, excavators, portal
            
            for construct_name in teams[team][construct_type]:
                #e_1, e_2 ou w_1, W_2 ou p_1,p_2
                
                coords = find_coords(teams, team, construct_type, construct_name)
                #liste_x = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]
                #liste_y = [10,20,30,40,50,60,70,80,90,100,110,120,130,140]
                
                coord_nb = 0
                for element in coords[0]:
                    x = coords[0][coord_nb]
                    y = coords[1][coord_nb]
                    grid[x][y] = 'x '
                    coord_nb += 1
                    
    for asteroid in informations['asteroids']:
        x = informations['asteroids'][asteroid]['position_x']
        y = informations['asteroids'][asteroid]['position_y']
        grid[x][y] = '* '
    
    #makes a beautiful board
    while nb_rows > check_row:
        tableau += '\n'
        check_row+=1
        check_column = 0
        while nb_columns > check_column:
            tableau += grid[check_row-1][check_column]
            check_column+=1
    
    print(tableau)
    
def buy(teams, buyer, construct_type, name):
    """ Allows the player to buy a construction, and withdrawns the price to his gold.
    
    Parameters
    ----------
    teams : dictionnary with all the teams' informations (team a and team b) (dict)
    buyer : the name of the buying team (str)
    construct_type : the type of the boat/construction (str)
    name : the name of the new ship (str)
    
    Return
    ------
    teams : dictionnary (actualized) with all the teams' informations (team a and team b) (dict)
    
    Notes
    -----
    The construct_type must be scout, warship, excavator-S, excavator-M or excavator-L.
    
    Version
    -------
    specification : Valentin Kanen (v.1 27/02/18)
    specification : Adrien Dupont (v.2 09/03/18)
    implentation : Adrien Dupont (v.1 12/03/18)
    implentation : Adrien Dupont (v.2 12/04/18)
    """
    center_x = teams[buyer]['portal']['p_1']['position_x']
    center_y = teams[buyer]['portal']['p_1']['position_y']
        
    if construct_type == 'scout':
        if teams[buyer]['gold'] >= 3:
            teams[buyer]['gold'] -= 3
            teams[buyer]['warships'][name] = {'position_x':center_x, 'position_y':center_y, 'type':'scout', 'life':3}
        else:
            print('Not enough gold')
        
    elif construct_type == 'warship':
        if teams[buyer]['gold'] >= 9:
            teams[buyer]['gold'] -= 9
            teams[buyer]['warships'][name] = {'position_x':center_x, 'position_y':center_y, 'type':'warship', 'life':18}
        else:
            print('Not enough gold')
        
    elif construct_type == 'excavator-S':
        if teams[buyer]['gold'] >= 1:
            teams[buyer]['gold'] -= 1
            teams[buyer]['excavators'][name] = {'position_x':center_x, 'position_y':center_y, 'type':'excavator-S', 'life':2, 'status':'release', 'ores':0}
        else:
            print('Not enough gold')
                   
    elif construct_type == 'excavator-M':
        if teams[buyer]['gold'] >= 2:
            teams[buyer]['gold'] -= 2
            teams[buyer]['excavators'][name] = {'position_x':center_x, 'position_y':center_y, 'type':'excavator-M', 'life':3, 'status':'release','ores':0}
        else:
            print('Not enough gold')
                    
    elif construct_type == 'excavator-L':
        if teams[buyer]['gold'] >= 4:
            teams[buyer]['gold'] -= 4
            teams[buyer]['excavators'][name] = {'position_x':center_x, 'position_y':center_y, 'type':'excavator-L', 'life':6, 'status':'release','ores':0}
        else:
            print('Not enough gold')
                  
    return(teams)
    
def show_informations(teams, informations):
    """ Gives all the informations about the player's turn.
    
    Parameters
    ----------
    teams : dictionnary with all the teams' informations (team a and team b) (dict)
    informations : the dictionnary with all the informations about the portals coords, the asteroids and the board's size in it. (dict)
    
    Version
    -------
    specification : Adrien Dupont (v.1 09/03/18)
    
    """
    for team in teams:
        all_warships = ''
        all_excavators = ''
        all_asteroids = ''
        
        for warship in teams[team]['warships']:
            all_warships += warship
            warship_x = teams[team]['warships'][warship]['position_x']
            warship_y = teams[team]['warships'][warship]['position_y']
            coords = '(%d,%d)' % (warship_x, warship_y)
            all_warships += coords
            all_warships += ', '
            
        for excavator in teams[team]['excavators']:
            all_excavators += excavator
            excavator_x = teams[team]['excavators'][excavator]['position_x']
            excavator_y = teams[team]['excavators'][excavator]['position_y']
            coords = '(%d,%d)' % (excavator_x, excavator_y)
            all_excavators += coords
            status = teams[team]['excavators'][excavator]['status']
            all_excavators += ' %s' % (status)
            all_excavators += ', '
            
        gold_amount = teams[team]['gold']
        
        portal_x = teams[team]['portal']['p_1']['position_x']
        portal_y = teams[team]['portal']['p_1']['position_y']
        portal_coords = '(%d,%d)' % (portal_x, portal_y)
        portal_life = teams[team]['portal']['p_1']['life']
        
        for asteroid in informations['asteroids']:
            all_asteroids += asteroid
            asteroid_x = informations['asteroids'][asteroid]['position_x']
            asteroid_y = informations['asteroids'][asteroid]['position_y']
            nb_ores = informations['asteroids'][asteroid]['ores']
            coords = '(%d,%d) and has %f ores' % (asteroid_x, asteroid_y, nb_ores)
            all_asteroids += coords
            all_asteroids += ', '
            
            
            
            
        print('%s owns those warships : %sand those excavators : %sand has %d gold. The coords of his portal are %s with %d life.' % (team, all_warships, all_excavators, gold_amount, portal_coords, portal_life))
        #reçois les résultats des fonctions : buy, switch_lock, move_construction, attack et aussi end_game
        
    print('The asteroids are in %s.' % (all_asteroids))
        
def compute_perimeter(teams, attacker, x, y, player):
    """Computes the Manhattan's Distance to see if the target is reachable or not.
    
    Parameters
    ----------
    teams : dictionnary with all the teams' informations (team a and team b) (dict)
    attacker : the warship which attacks (str)
    x : the coord in x of the target (int)
    y : the coord in y of the target (int)
    player : the team giving the orders (str)
    
    Notes
    -----
    player must be 'team_a' or 'team_b'
    
    Returns
    -------
    True if the target is reachable
    False if the target isn't reachable
    
    Version
    -------
    specification : Adrien Dupont (v.1 09/03/18)
    implementation : Valentin Kanen (v.1 30/03/18)
    """
    
    if teams[player]['warships'][attacker]['type']=='scout':
        
        if abs(teams[player]['warships'][attacker]['position_x'] - x) + abs(teams[player]['warships'][attacker]['position_y'] - y) <=3:
            return True
        else :
            return False
            
    elif teams[player]['warships'][attacker]['type']== 'warship':
        
        if abs(teams[player]['warships'][attacker]['position_x'] - x) + abs(teams[player]['warships'][attacker]['position_y'] - y) <=5:
             return True
        else :
            return False

    else :
          return False
          #checks if the order is legal or not
          
def switch_lock(teams, excavator, new_status, owner):
    """Changes the excavator's status
    
    Parameters
    ----------
    teams : dictionnary with all the teams' informations (team a and team b) (dict)
    excavator : the name of the excavator which will change (str)
    new_status : the current excavator's status (str)
    owner : the owner of the excavator (str)
    
    Return
    ------
    teams : dictionnary (actualized) with all the teams' informations (team a and team b) (dict)
    
    Version
    -------
    specification : Valentin Kanen (v.1 09/03/18)
    implementation : Valentin Kanen (v.1 30/03/18)
    """
            
    if new_status == teams[owner]['excavators'][excavator]['status']:
        print ('This excavator has already the good statement')  
            
    elif new_status == 'release':
        teams[owner]['excavators'][excavator]['status'] = 'release'
        
    elif new_status == 'lock':
        teams[owner]['excavators'][excavator]['status'] = 'lock'
    
    return(teams)
    
def attack(teams, attacker, x, y, player):
    """Computes the attacks for the warships
    
    Parameters
    ----------
    teams : dictionnary with all the teams' informations (team a and team b) (dict)
    attacker : the warship which attacks (str)
    x : the coord in x of the target (int)
    y : the coord in y of the target (int)
    player : the name of the player (str)
    
    Return
    ------
    teams : dictionnary (actualized) with all the teams' informations (team a and team b) (dict)
    
    Version
    -------
    specification : Adrien Dupont (v.1 12/04/18)
    implementation : Valentin Kanen (v.1 12/04/18)
    implementation : Adrien Dupont (v.2 12/04/18)
    """
    
   
    attacker_type = teams[player]['warships'][attacker]['type']
    
    if compute_perimeter(teams, attacker, x, y, player) == True:
        
        all_possibilities = ('warships', 'excavators', 'portal')
        
        for owner in teams:
            for possibility in all_possibilities:
                for building in teams[owner][possibility]:
                    
                    coords = find_coords(teams, owner, possibility, building)
                    #find_coords(teams, owner, construct_type, construct_name)
                    
                    for coord in range(len(coords[0])):
                        
                        coord_x = coords[0][coord]
                        coord_y = coords[1][coord]
                    
                        if coord_x == x and coord_y == y and attacker_type == 'scout':
                            teams[owner][possibility][building]['life'] -= 1
                            
                            
                        elif coord_x == x and coord_y == y and attacker_type == 'warship':
                            teams[owner][possibility][building]['life'] -= 3
                            
                            

    
    return(teams)

def reading_file_board(path, file_name):
    """ Reads the file with all the informations about the portals coords, the asteroids and the board's size.
    
    Parameters
    ----------
    path : the complete path to the file # example : '/Users/elisa_000/Documents/Labo de dvp' (str)
    file_name : the name of the file (str)
    
    Returns
    -------
    informations : the dictionnary with all the informations about the portals coords, the asteroids and the board's size in it. (dict)
    
    Version
    -------
    specification : Adrien Dupont (v.1 12/04/18)
    implementation : Elisa Etienne (v.1 12/04/18)
    
    """

    os.chdir(path)
    os.getcwd()
    os.path.exists(file_name)
    
    file = open(file_name, 'r')
    lines = file.readlines()
    file.close()
    
    for number, i in enumerate(lines):
        lines[number] = i.strip()
    
    informations = {}
    
    lines[1]= lines[1].split(' ')
    informations['size']={'nb_columns': int(lines[1][0]),'nb_rows': int(lines[1][1])}
    
    informations['portals'] = {}
    
    lines[3]= lines[3].split(' ')
    informations['portals']['p_1']= {'position_x':int(lines[3][0]),'position_y': int(lines[3][1]), 'type':'P', 'life':100}
    
    lines[4]= lines[4].split(' ')
    informations['portals']['p_2']= {'position_x':int(lines[4][0]),'position_y': int(lines[4][1]), 'type':'P', 'life':100}
    
    #print(informations)
    
    informations['asteroids'] ={}
    a = 1
    for line in lines[6:]:
        line = line.split(' ')
        name_asteroid = 'a_' + str(a)
        informations['asteroids'][name_asteroid]= {'position_x': int(line[0]), 'position_y': int(line[1]), 'ores': int(line[2]), 'ores_per_turn': int(line[3])}
        a += 1

    return(informations)
    
def collect(teams,informations):
    """ Collects the ores from the asteroids to the excavators
    
    Parameters
    ----------
    teams : dictionnary with all the teams' informations (team a and team b) (dict)
    informations : the dictionnary with all the informations about the portals coords, the asteroids and the board's size in it. (dict)
    
    Returns
    -------
    teams : dictionnary (actualized) with all the teams' informations (team a and team b) (dict)
    
    Version
    -------
    specification : Valentin Kanen (v.1 14/04/18)
    implementation : Valentin Kanen (v.1 14/04/18)
    """
    
    nb_excavators = 0
    
    for asteroid in informations['asteroids']:

        for owner in teams:
            for excavator in teams[owner]['excavators']:
                if teams[owner]['excavators'][excavator]['status'] == 'lock' and teams[owner]['excavators'][excavator]['position_x'] == informations['asteroids'][asteroid]['position_x'] and teams[owner]['excavators'][excavator]['position_y'] == informations['asteroids'][asteroid]['position_y']:
                    
                    nb_excavators+=1

        if nb_excavators != 0:
            ores_available = informations['asteroids'][asteroid]['ores']/nb_excavators
            print (ores_available)
            
            for owner in teams:
                for excavator in teams [owner]['excavators']:
                    if teams [owner]['excavators'][excavator]['status']=='lock' and teams [owner]['excavators'][excavator]['position_x'] == informations['asteroids'][asteroid]['position_x'] and teams [owner]['excavators'][excavator]['position_y'] == informations['asteroids'][asteroid]['position_y']:
                                
                        if teams [owner]['excavators'][excavator]['type'] == 'excavator-S' and informations['asteroids'][asteroid]['ores_per_turn'] + teams[owner]['excavators'][excavator]['ores'] > 1 and ores_available > 1- teams[owner]['excavators'][excavator]['ores']:                      
                            teams [owner]['excavators'][excavator]['ores'] = 1
                            informations['asteroids'][asteroid]['ores'] -= (1- teams[owner]['excavators'][excavator]['ores'])
                                             
                        elif teams [owner]['excavators'][excavator]['type'] == 'excavator-M' and informations['asteroids'][asteroid]['ores_per_turn'] + teams[owner]['excavators'][excavator]['ores'] > 4 and ores_available > 4 - teams[owner]['excavators'][excavator]['ores']:
                            teams [owner]['excavators'][excavator]['ores'] = 4
                            informations['asteroids'][asteroid]['ores'] -= (4- teams[owner]['excavators'][excavator]['ores'])
                                        
                        elif teams [owner]['excavators'][excavator]['type'] == 'excavator-L'and informations['asteroids'][asteroid]['ores_per_turn'] + teams[owner]['excavators'][excavator]['ores'] > 8 and ores_available > 8 - teams [owner]['excavators'][excavator]['ores']:
                            teams [owner]['excavators'][excavator]['ores']=8
                            informations['asteroids'][asteroid]['ores']-= (8 - teams [owner]['excavators'][excavator]['ores'])
                                        
                        elif ores_available < informations['asteroids'][asteroid]['ores_per_turn'] :
                            teams[owner]['excavators'][excavator]['ores'] += ores_available
                            informations['asteroids'][asteroid]['ores'] -= ores_available
                            
                        elif ores_available >= informations['asteroids'][asteroid]['ores_per_turn']:  
                            teams [owner]['excavators'][excavator]['ores'] += informations['asteroids'][asteroid]['ores_per_turn']
                            informations['asteroids'][asteroid]['ores'] -= informations['asteroids'][asteroid]['ores_per_turn']
                            
                    if informations['asteroids'][asteroid]['ores']<0.0001:
                        informations['asteroids'][asteroid]['ores']=0
                         
        nb_excavators = 0 
    
    return(teams, informations)
    
def creating_teams_dic(informations, player_1, player_2):
    """ Creates the dictionnary called "teams" with all the teams' informations (team a and team b) (dict)
    
    Parameters
    ----------
    informations : the dictionnary with all the informations about the portals coords, the asteroids and the board's size in it. (dict)
    player_1 : the name of the first player / team (str)
    player_2 : the name of the second player /team (str)
    
    Returns
    -------
    teams : dictionnary with all the teams' informations (team a and team b) (dict)
    
    Notes
    -----
    If you want to play against an IA, name one of your players "IA"
    
    Version
    -------
    specification : Adrien Dupont (v.1 13/04/18)
    implementation : Adrien Dupont (v.1 13/04/18)
    """
    
    teams = {}
    
    owners = (player_1, player_2)
    
    for owner in owners:
        
        teams[owner] = {}
        
        teams[owner]['warships'] = {}
        
        teams[owner]['excavators'] = {}
        
        teams[owner]['portal'] = {}
        
        if owner == player_1:
            teams[owner]['portal']['p_1'] = informations['portals']['p_1']
        else :
            teams[owner]['portal']['p_1'] = informations['portals']['p_2']
        
        teams[owner]['gold'] = 4
        
    return(teams)
    
def ores_drop_off(teams):
    """ Drops off the ores in the excavators into the portal
    
    Parameters
    ----------
    teams : the dictionnary with all the teams' informations (team a and team b) (dict)
    
    Returns
    -------
    teams : the dictionnary (actualized) with all the teams' informations (team a and team b) (dict)
    
    Version:
    -------
    specification : Valentin Kanen (v.1 13/04/18)
    implementation : Valentin Kanen (v.1 13/04/18)
    """
    
    for owner in teams: 
        for excavator in teams[owner]['excavators']:
            for portal in teams[owner]['portal']:
            
                if teams[owner]['excavators'][excavator]['position_x'] == teams[owner]['portal'][portal]['position_x'] and teams[owner]['excavators'][excavator]['position_y'] == teams[owner]['portal'][portal]['position_y'] and teams[owner]['excavators'][excavator]['status'] == 'lock':
                    
                    teams[owner]['gold'] += teams[owner]['excavators'][excavator]['ores']   
                    teams[owner]['excavators'][excavator]['ores'] = 0
                      
    return(teams)
    # rajouter pour toutes les coordonnées du portail
    
def IA_orders_computer(teams, informations, player_name):
    """ Create a string of characters with all the orders that the IA needs to do.
    
    Parameters
    ----------
    teams : dictionnary with all the teams' informations (team a and team b) (dict)
    names : list with all of the names used in the game (list)
    
    Return 
    ------
    orders_ia : the order of the iA (str)
        
    Version
    -------
    specification and implementation : Elisa Etienne (v.1 30/03/18)
    implementation : Adrien Dupont (v.2 16/04/18)
    """
    type_construction = ('scout', 'warship','excavator-S','excavator-M','excavator-L')
    
    #x_max = informations['size']['nb_columns']
    #y_max = informations['size']['nb_ranges']
    
    orders_ia = ''
    
    #adds the order "buy a warship" to the string ajoute à la chaîne d'acheter un bateau.
    name = str(randint(0,999))
    construction = type_construction[randint(0,4)]
    #chooses a name and a type to the warship
    order = name + ':' + construction + ' '
    #adds it to the list
    orders_ia += order
        
    #choisis un excavator pour se lock ou délock
    if len(teams[player_name]['excavators']) > 0:
        name = random.choice(list(teams[player_name]['excavators']))
        status = ('lock', 'release')
        choice = random.choice(list(status))
        order = name + ':' + choice
                
    #chooses a warship that will move
    if len(teams[player_name]['warships']) > 0:
        name = random.choice(list(teams[player_name]['warships']))
        x = teams[player_name]['warships'][name]['position_x']
        y = teams[player_name]['warships'][name]['position_y'] 
        
        x += randint(-1,1)
        y += randint(-1,1)

        order = name + ':@' + str(x) + '-' + str(y) + ' '
        orders_ia += order
        
    #chooses a warship that will move
    if len(teams[player_name]['excavators']) > 0:
        name = random.choice(list(teams[player_name]['excavators']))
        x = teams[player_name]['excavators'][name]['position_x']
        y = teams[player_name]['excavators'][name]['position_y'] 
        
        x += randint(-1,1)
        y += randint(-1,1)

        order = name + ':@' + str(x) + '-' + str(y) + ' '
        orders_ia += order
        
    #chooses a warship that will attack
    if len(teams[player_name]['warships']) > 0:
        name = random.choice(list(teams[player_name]['warships']))
        x = teams[player_name]['warships'][name]['position_x']
        y = teams[player_name]['warships'][name]['position_y'] 
        
        if teams[player_name]['warships'][name]['type'] == 'scout':
            x += randint(-3,3)
            y += randint(-3,3)
            
        else :
            x += randint(-5,5)
            y += randint(-5,5)
            
        order = name + ':@' + str(x) + '-' + str(y) + ' '
        orders_ia += order

    orders_ia = orders_ia[:-1]

    return(orders_ia)
    
    
def smart_IA(teams, informations, nb_turns, player):
    """ Creates a string with smart instructions (orders) in function of the positions of the portals, asteroids, warships and excavators for the game "mining wars".
    
    Parameters
    ----------
    teams : dictionnary with all the teams' informations (player_1 and player_2) (dict)
    informations : the dictionnary with all the informations about the portals coords, the asteroids coords and the size of the board in it. (dict)
    nb_turns : the number of the turns playing (int)
    player: player using the smart intelligence (str)
    
    Returns
    -------
    orders : the smart instructions to play the game (str)
    
    Version
    --------
    specification : Adrien Dupont (v.1 22/04/2018)
    implementation : Elisa Etienne (v.1 25/04/2018)
    implementation : Elisa Etienne (v.2 26/04/2018)
    """
    
    #ATTENTION AUX INSTRUCTIONS :
    #pas de coups illégaux
    #pas sortir du plateau
    #pas se déplacer et attaquer en même temps avec le même vaisseau
    #se déplacer d'une case max 
    #respecter la syntaxe : a:b ; a:@x-y ; a:*x-y ; a:lock/release
    
    
    #type_construction = ('scout', 'warship','excavator-S','excavator-M','excavator-L')
    
    #x_max = informations['size']['nb_columns']
    #y_max = informations['size']['nb_ranges']
    
    orders = ''
    
    nb_ores = teams[player]['gold']
    
    if nb_turns == 0:
        orders = str(randint(0,999)) + ':excavator-M ' + str(randint(0,999)) + ':excavator-M '
    
    else :
        ores_asteroids=0
        nb_excavators=0
        ores_excavators=0
            
        if nb_ores >= 9 :
            name = str(randint(0,999)) 
            orders += name + ':warship '
            
        for excavator in teams[player]['excavators']:
            nb_excavators+=1
            ores_excavators+= teams[player]['excavators'][excavator]['ores']
        
        for asteroid in informations ['asteroids']:
            ores_asteroids+=informations ['asteroids'][asteroid]['ores']
        
        ores = nb_ores + ores_asteroids + ores_excavators
        
        if nb_ores >= 2 and nb_excavators<3 and ores_asteroids > 8:
            name = str(randint(0,999)) 
            orders += name + ':excavator-M ' 
            
        if nb_ores>= 3 and ores < 9:
            name = str (randint(0,999))
            orders += name + ':scout '
            
                                
        for excavator in teams[player]['excavators']:
            orders += order_excavator(teams,informations,excavator,player)
            
        if len(teams[player]['warships']) != 0 :
                
            for warship in teams[player]['warships']:
                orders += str(order_warship(teams, informations, warship,player))
                
    orders= orders[:-1]

    return(orders)
    

def order_excavator(teams, informations, type_name, player):
    """ Gives the order for one excavator in function of the ores in charge and the distance between the excavator and the nearrest asteroid
    
    Parameters
    ----------
    teams : dictionnary with all the teams' informations (player_1 and player_2) (dict)
    informations : the dictionnary with all the informations about the portals coords, the asteroids coords and the size of the board in it. (dict)
    type_name : the name of the excavator (str)
    player: player using the smart intelligence (str)
    
    Return
    ------
    orders : the order for the excavator (movement or lock/release) (str)
    
    Version
    -------
    specification : Elisa Etienne (v.1 25/04/2018)
    implementation : Elisa Etienne (v.1 26/04/2018)
    """
    orders =''
    x_exc = teams[player]['excavators'][type_name]['position_x']
    y_exc = teams[player]['excavators'][type_name]['position_y']
    new_direction_x =teams[player]['excavators'][type_name]['position_x']
    new_direction_y =teams[player]['excavators'][type_name]['position_y']
    
    for team in teams:
        if team != player:
            player_1 = team
    
    #déplacement vers le portail si l'excavateur est plein.
    ores=0
    for asteroid in informations['asteroids']:
        ores+=informations['asteroids'][asteroid]['ores']
        
    if teams[player]['excavators'][type_name]['type'] == 'excavator-S' and teams[player]['excavators'][type_name]['ores'] == 1 or teams[player]['excavators'][type_name]['type'] == 'excavator-M'and teams[player]['excavators'][type_name]['ores'] == 4 or teams[player]['excavators'][type_name]['type'] == 'excavator-L' and teams[player]['excavators'][type_name]['ores'] == 8 or ores == 0:
        new_direction_x = teams[player]['portal']['p_1']['position_x']
        new_direction_y = teams[player]['portal']['p_1']['position_y']
           
    #déplacement vers un astéroïde si l'excavateur n'est pas rempli.
    
    elif teams[player]['excavators'][type_name]['type'] == 'excavator-S' and teams[player]['excavators'][type_name]['ores'] != 1 or teams[player]['excavators'][type_name]['type'] == 'excavator-M'and teams[player]['excavators'][type_name]['ores'] != 4 or teams[player]['excavators'][type_name]['type'] == 'excavator-L' and teams[player]['excavators'][type_name]['ores'] != 8  :
        
        #chercher la distance minimale entre le portail et l'astéroide 
        min_dist = 1000
        
        for asteroid in informations['asteroids']:
            position_x_asteroid = informations['asteroids'][asteroid]['position_x']
            position_y_asteroid = informations['asteroids'][asteroid]['position_y']
            
            distance = abs(x_exc - position_x_asteroid) + abs(y_exc - position_y_asteroid)
            
            if distance <= min_dist and informations ['asteroids'][asteroid]['ores'] > 0:
                min_dist = distance
                new_direction_x = position_x_asteroid
                new_direction_y = position_y_asteroid
                
                
    #déplacement vers le portail si l'excavateur va se faire tirer dessus alors qu'il prend de l'ore.
    
    for warship in teams[player_1]['warships']:
        x_p = teams[player_1]['warships'][warship]['position_x']
        y_p = teams[player_1]['warships'][warship]['position_y']
        
        distance = abs(x_exc - x_p) + abs(x_exc - y_p)
        
        if teams [player_1]['warships'][warship]['type'] == 'warship' and distance <= 6 and teams [player]['excavators'][type_name]['status']=='lock' or teams [player_1]['warships'][warship]['type'] == 'scout' and distance <= 5 and teams [player]['excavators'][type_name]['status']== 'lock':
            new_direction_x = teams[player]['portal']['p_1']['position_x']
            new_direction_y = teams[player]['portal']['p_1']['position_y']
             
    
                
        
    if new_direction_x < x_exc :
        new_direction_x = x_exc -1
        
    elif new_direction_x > x_exc :
        new_direction_x = x_exc + 1
        
    if new_direction_y < y_exc :
       new_direction_y = y_exc - 1
        
    elif new_direction_y > y_exc :
        new_direction_y = y_exc +1   
        
    orders += str(type_name) + ':@'+ str(new_direction_x) +'-' + str(new_direction_y) + ' ' 

    
    #verrouille si la position de l'excavateur est sur l'astéroide
    if new_direction_x == x_exc and new_direction_y == y_exc and teams[player]['excavators'][type_name]['status'] == 'release':
        orders += str(type_name) + ':lock '
    elif teams[player]['excavators'][type_name]['status'] == 'lock':
        orders += str(type_name) +':release '
    
    return orders
        
def order_warship(teams, informations, type_name,player):
    """ Gives the order for one warship or scout in function of the fact that ennemy has a warship or not
    
    Parameters
    ----------
    teams : dictionnary with all the teams' informations (player_1 and player_2) (dict)
    informations : the dictionnary with all the informations about the portals coords, the asteroids coords and the size of the board in it. (dict)
    type_name : the name of the warship (str)
    player: player using the smart intelligence (str)
    
    Return
    ------
    orders : the order for the warship (attack or movement) (str)
    
    Version
    -------
    specification : Elisa Etienne (v.1 25/04/2018)
    implementation : Elisa Etienne (v.1 26/04/2018)
    """
    orders =''
    
    for team in teams:
        if team != player:
            player_1 = team
    
    x_w = teams[player]['warships'][type_name]['position_x']
    y_w = teams[player]['warships'][type_name]['position_y']

    #si l'ennemi n'a pas de bateau ni d'excavateur (stratégie commune)
    if len(teams[player_1]['warships']) == 0 and len (teams[player_1]['excavators']) == 0:
            
        x_p = teams[player_1]['portal']['p_1']['position_x']
        y_p = teams[player_1]['portal']['p_1']['position_y']
            
    
    #si l'ennemi a un bateau :    
    elif len (teams[player_1]['warships']) != 0 :
        
        #stratégie scout
        if teams[player]['warships'][type_name]['type'] == 'scout' :
            nb_scouts=0
            min_dist =1000
            
            for warship in teams [player_1]['warships']:
                if teams[player_1]['warships'][warship]['type'] == 'scout':
                    nb_scouts+=1
                    
                    x_p = teams[player_1]['warships'][warship]['position_x']
                    y_p = teams[player_1]['warships'][warship]['position_y']
                
                    distance = abs(x_w - x_p) + abs(x_w - y_p)
                
                    if distance <= min_dist :
                        min_dist = distance
                        x_p = teams[player_1]['warships'][warship]['position_x']
                        y_p = teams[player_1]['warships'][warship]['position_y']
            
            #si pas d'excavateur, foncer vers le portail            
            if nb_scouts==0 and len(teams[player_1]['excavators']) == 0:
                x_p = teams[player_1]['portal']['p_1']['position_x']
                y_p = teams[player_1]['portal']['p_1']['position_y']
            
            #si encore excavateur, foncer vers excavateur    
            elif nb_scouts == 0 and len (teams[player_1]['excavators']) != 0:        
                min_dist = 1000
            
                for excavator in teams[player_1]['excavators']:
                    x_p = teams[player_1]['excavators'][excavator]['position_x']
                    y_p = teams[player_1]['excavators'][excavator]['position_y']
                    
                    distance = abs(x_w - x_p) + abs(x_w - y_p)
                    
                    if distance <= min_dist :
                        min_dist = distance
                        x_p = teams[player_1]['excavators'][excavator]['position_x']
                        y_p = teams[player_1]['excavators'][excavator]['position_y']
                                         
        #statégie warship
        elif teams[player]['warships'][type_name]['type'] == 'warship' :
                
            min_dist = 1000
        
            for warship in teams[player_1]['warships']:
                x_p = teams[player_1]['warships'][warship]['position_x']
                y_p = teams[player_1]['warships'][warship]['position_y']
                
                distance = abs(x_w - x_p) + abs(x_w - y_p)
                
                if distance <= min_dist :
                    min_dist = distance
                    x_p = teams[player_1]['warships'][warship]['position_x']
                    y_p = teams[player_1]['warships'][warship]['position_y']
        
    #si l'ennemi n'a pas de bateau mais a un excavateur (stratégie commune)
    elif len (teams[player_1]['warships']) == 0 and len (teams[player_1]['excavators']) != 0:
        
        min_dist = 1000
    
        for excavator in teams[player_1]['excavators']:
            x_p = teams[player_1]['excavators'][excavator]['position_x']
            y_p = teams[player_1]['excavators'][excavator]['position_y']
            
            distance = abs(x_w - x_p) + abs(x_w - y_p)
            
            if distance <= min_dist :
                min_dist = distance
                x_p = teams[player_1]['excavators'][excavator]['position_x']
                y_p = teams[player_1]['excavators'][excavator]['position_y']
            
                                    
    distance = abs(x_w - x_p) + abs(y_w - y_p)
        
    #quand la distance d'attaque est trop grande, on continue d'avancer.                                                                        
    if distance > 5 and teams[player]['warships'][type_name]['type']== 'warship' or distance > 3 and teams[player]['warships'][type_name]['type']== 'scout':
            
            if x_p < x_w :
                new_x_w = x_w - 1
            elif x_p > x_w :
                new_x_w = x_w +1
            else :
                new_x_w = x_w
            
            if y_p < y_w :
                new_y_w = y_w - 1
            elif y_p > y_w :
                new_y_w = y_w + 1
            else:
                new_y_w = y_w
                
            orders += str(type_name) + ':@'+ str(new_x_w) +'-' + str(new_y_w) + ' '
    
    #quand la distance est bonne, on attaque
    
    if distance <= 5 and teams[player]['warships'][type_name]['type']== 'warship' or distance <= 3 and teams[player]['warships'][type_name]['type']== 'scout':
        orders += str(type_name) + ':*' + str(x_p) +'-' + str(y_p) + ' '
        
    return(orders)
        
def clear_dictionary (teams):
    """Delete excavators and warships when they don't have life anymore
    
    Parameters
    ----------
    teams :  dictionnary with all the teams' informations (team a and team b) (dict)
    
    Returns
    -------
    teams :  dictionnary with all the teams' informations (team a and team b) (dict)
    
    Version
    -------
    specification: Valentin Kanen (v.1 27/04/2018)
    implémentation: ELisa Etienne et Valentin Kanen (v.1 27/04/2018) 
    """
    names_list=[]
    all_possibilities = ('warships','excavators')
    
    for player in teams:
        for possibility in all_possibilities:
            for name in teams [player][possibility]:
                names_list.append(name)

            for build_names in names_list:
                if build_names in teams[player][possibility]:
                    if teams [player][possibility][build_names]['life']<=0:
                        del teams [player][possibility][build_names]
    return(teams)
    
start_game('../maps/', 'cross.mw', 'IA', 'gr_1', '138.48.160.152')

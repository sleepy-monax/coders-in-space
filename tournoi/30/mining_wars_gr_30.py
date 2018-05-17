# -*- coding: utf-8 -*-
from termcolor import colored, cprint
import random
import copy
import time
import remote_play

def order(orders_player_A, orders_player_B):            
    
    """Returns a dictionnary with all the orders
    
    Parameters
    ----------        
    orders_player_A: the orders of the player A (str)
    orders_player_B: the orders of the player B (str)
    
    Returns
    -------
    orders: the dictionnary containing the orders (dict)
    
    Version
    -------
    specification: Julien (v.1 23/03/18)
    implementation: Julien (v.1 09/04/18)
    """
        
    orders = {'purchase':{'player_A':{},
                          'player_B':{}},
                  'lock':{'player_A':{},
                          'player_B':{}}, 
                  'move':{'player_A':{},
                          'player_B':{}}, 
                  'attack':{'player_A':{},
                            'player_B':{}}}
                            
    iteration = 0
    for player_order in [orders_player_A, orders_player_B]:
        
        if iteration == 0:
            player = 'player_A'
        if iteration == 1:
            player = 'player_B'    
        iteration += 1

        if player_order != '' :   #si le joueur donne un ordre
            player_order = player_order.split(' ')
            for demand in player_order:
                
                name, task = demand.split (':')
                
                if task == 'scout' or task == 'warship' or task == 'excavator-S' or task == 'excavator-M' or task == 'excavator-L' : #si c'est un ordre de création de vaisseau
                    orders['purchase'][player][name] = task
                
                if task == 'lock' or task == 'release' :    
                    orders['lock'][player][name] = task
                    
                if '@' in task :    #si c'est un ordre de mouvement
                    task = task.strip ('@')
                    task = task.split ('-')
                    task[0] = int(task[0])
                    task[1] = int(task[1])
                    orders['move'][player][name] = task
                    
                
                if '*' in task :   #si c'est un ordre d'attaque
                    task = task.strip ('*')
                    task = task.split ('-')
                    task[0] = int(task[0])
                    task[1] = int(task[1])
                    orders['attack'][player][name] = task
                    
    return orders
    

def read_file(fh):
    
    """Read the file and put all the information in the main dictionnary:
    
    Parameters
    ----------        
    fh: the file (.mw) with the starting information (file)
    
    Returns 
    -------
    teams : the dictionnary containing the data about the players (dict)
    asteroids : the dictionnary containing the data about the asteroids (dict)
    nb_column : number of columns of the board (int)
    nb_row : number of rows of the board (int)
    
    Version
    -------
    specification: Julien (v.1 23/02/18)
    implementation: Julien (v.1 09/04/18)
    """
    
    fh = open(fh,'r')
    lines = fh.readlines()
    
    asteroids = {}
             
    teams = {'player_A':{'spaceship':{},
                         'portal':{'life':100, 'position':{'center':[0,0], 'others':[[-2,-2],[-2,-1],[-2,0],[-2,1],[-2,2],[-1,2],[-1,-2],[-1,-1],[-1,0],[-1,1],[-1,2],[0,-2],[0,-1],[0,1],[0,2],[1,-2],[1,-1],[1,0],[1,1],[1,2],[2,-2],[2,-1],[2,0],[2,1],[2,2]]}},
                         'ore':4,
                         'total_ore_loaded':0},
            
             'player_B':{'spaceship':{},
                         'portal':{'life':100, 'position':{'center':[0,0], 'others':[[-2,-2],[-2,-1],[-2,0],[-2,1],[-2,2],[-1,2],[-1,-2],[-1,-1],[-1,0],[-1,1],[-1,2],[0,-2],[0,-1],[0,1],[0,2],[1,-2],[1,-1],[1,0],[1,1],[1,2],[2,-2],[2,-1],[2,0],[2,1],[2,2]]}},
                         'ore':4,
                         'total_ore_loaded':0}}
    
    
    for element in range(len(lines)):
        lines[element] = lines[element].split(' ')
    
    nb_row = int(lines[1][0])
    nb_column = int(lines[1][1])
    
    #--------portals------------
    
    teams['player_A']['portal']['position']['center'][0] = int(lines[3][0])
    teams['player_A']['portal']['position']['center'][1] = int(lines[3][1])

    teams['player_B']['portal']['position']['center'][0] = int(lines[4][0]) 
    teams['player_B']['portal']['position']['center'][1] = int(lines[4][1])
    
    for player in teams:
        iteration = 0
        while iteration < len(teams[player]['portal']['position']['others']):
            teams[player]['portal']['position']['others'][iteration][0] += teams[player]['portal']['position']['center'][0]   
            teams[player]['portal']['position']['others'][iteration][1] += teams[player]['portal']['position']['center'][1]   #place les autres positions du portail
            iteration += 1
            
            
    #--------asteroids------------
    
    nb_lines = len(lines) - 1 
    asteroid_number = 1
    nb_asteroids = len(lines) - 6
    number = nb_lines - nb_asteroids
    
    while nb_lines > number: 
        
        asteroids['asteroid_' + str(asteroid_number)] = {}
        asteroids['asteroid_' + str(asteroid_number)]['position'] = [int(lines[nb_lines][0]),int(lines[nb_lines][1])]
        asteroids['asteroid_' + str(asteroid_number)]['ore'] = int(lines[nb_lines][2])
        asteroids['asteroid_' + str(asteroid_number)]['loading_ore'] = int(lines[nb_lines][3])
        
        asteroid_number += 1
        nb_lines -= 1
    
    fh.close()
    
    return teams, asteroids, nb_row, nb_column



def create_board(fh):
    """Create the board with the portals and asteroids and create the dictionnaries of the asteroids and players
    
    Parameters
    ----------
    fh: the file (.mw) with the starting information (file)
    
    Returns
    -------
    teams: the dictionnary containing the data about the players (dict)
    asteroids : the dictionnary containing the data about the asteroids (dict)
    nb_row : number of rows of the board (int) 
    nb_column : number of columns of the board (int)
    grid : list of lists containing the elements of the board (list) 
    
    Version
    -------
    specification: Julien (v.1 23/02/18)
    implementation: Hugo (v.1 14/04/18)
    """
    
    teams, asteroids, nb_row, nb_column = read_file(fh)
    
    grid = []
    nb_row += 1
    nb_column += 1

    for line in range(nb_row):
        grid.append([])
        for column in range(nb_column):
            grid[line].append('☐')
    
    column_number = 0
    for column in range(nb_column):
        if column_number >= 10 :
            column_number = str(column_number)
            column_number = column_number[1]
        grid[0][column] = str(column_number) + ' '
        column_number = int(column_number)
        column_number += 1
        
    row_number = 0
    for row in range(nb_row):
        if row_number >= 10 :
            row_number = str(row_number)
            row_number = row_number[1]
        grid[row][0] = str(row_number) + ' '
        row_number = int(row_number)
        row_number += 1
        
    return teams, asteroids, nb_row, nb_column, grid
    
    
    
def show_board(teams, asteroids, nb_column, nb_row, grid):
    """Display the board with all its components (portals, asteroids and spaceships)
     
    Parameters
    ----------
    teams : the dictionnary containing the data about the players (dict)
    asteroids : the dictionnary containing the data about the asteroids (dict)
    nb_column : number of columns of the board (int)
    nb_row : number of rows of the board (int)
    
    Version
    -------
    specification : Julien (v.1 05/03/18)
    implementation: Hugo (v.1 14/04/18)
    """
    
    #-----------------grid----------
        
    for line in range(nb_row):
        grid.append([])
        for column in range(nb_column):
            grid[line][column] = u'\u2610'
     
    column_number = 0
    for column in range(nb_column):
        if column_number >= 10 :
            column_number = str(column_number)
            column_number = column_number[1]
        grid[0][column] = str(column_number) + ' '
        column_number = int(column_number)
        column_number += 1
        
    row_number = 0
    for row in range(nb_row):
        if row_number >= 10 :
            row_number = str(row_number)
            row_number = row_number[1]
        grid[row][0] = str(row_number) + ' '
        row_number = int(row_number)
        row_number += 1
     
     
    #--------------portals------------------
     
    for player in teams:                          
        portal_position_y = teams[player]['portal']['position']['center'][0] 
        portal_position_x = teams[player]['portal']['position']['center'][1]                    
        grid[portal_position_y][portal_position_x] = colored(u'\u2610', 'grey', 'on_grey')    #place le centre des portails
        
        iteration = 0
        while iteration < len(teams[player]['portal']['position']['others']):      
            portal_y_other = teams[player]['portal']['position']['others'][iteration][0]
            portal_x_other = teams[player]['portal']['position']['others'][iteration][1] 
            grid[portal_y_other][portal_x_other] = colored(u'\u2610', 'grey', 'on_grey')   #place les autres positions des portails
            iteration += 1
            
            
    #--------------spaceships------------------
    
    for player in teams:
        
        for spaceship_name in teams[player]['spaceship']:      
            spaceship_y = teams[player]['spaceship'][spaceship_name]['position']['center'][0]
            spaceship_x = teams[player]['spaceship'][spaceship_name]['position']['center'][1] 
            
            if player == 'player_A':
                grid[spaceship_y][spaceship_x] = colored(u'\u2610', 'blue', 'on_blue')   #place les vaisseaux de l'équipe A 
                
            if player == 'player_B':
                grid[spaceship_y][spaceship_x] = colored(u'\u2610', 'red', 'on_red')   #place les vaisseaux de l'équipe A 
            
            iteration = 0
            while iteration < len(teams[player]['spaceship'][spaceship_name]['position']['others']):
                spaceship_x_other = teams[player]['spaceship'][spaceship_name]['position']['others'][iteration][1]       
                spaceship_y_other = teams[player]['spaceship'][spaceship_name]['position']['others'][iteration][0]
                
                if player == 'player_A':
                    grid[spaceship_y_other][spaceship_x_other] = colored(u'\u2610', 'blue', 'on_blue')
                    
                if player == 'player_B':
                    grid[spaceship_y_other][spaceship_x_other] = colored(u'\u2610', 'red', 'on_red')
                iteration += 1
    
    #--------------asteroids------------------
     
    for asteroid in asteroids:
        asteroid_x = asteroids[asteroid]['position'][1]        
        asteroid_y = asteroids[asteroid]['position'][0]      
        grid[asteroid_y][asteroid_x] = u'\u2605'   #place les astéroides


    #--------------board------------------
    
    board = ''
    for row in range(nb_row):
        board += '\n'
        for column in range(nb_column):
            board += grid[row][column]

    print(board)



def purchase(teams, spaceships, spaceship_name, spaceship_variety, player):
    """Create a new spaceship and add it to the dictionnary of the player and to the board
    
    Parameters
    ----------
    teams: the dictionnary containing the data about the players (dict)
    spaceships: the dictionnary containing the basic data about the different spaceships the player can buy (dict)
    spaceship_name: the name of the spaceship that the player wants to buy (str)
    spaceship_variety : the variety of the spaceship (str)
    player: the name of the player (str)
    
    Returns
    -------
    teams: the dictionnary containing the data about the players (dict)
        
    Version
    -------
    specification: Sarah (v.1 23/02/18)
    implementation: Sarah (v.1 24/04/18)
    """
    
    spaceship_list = []
    for vaisseau_team_A in teams['player_A']['spaceship']:
        spaceship_list.append(vaisseau_team_A)
    for vaisseau_team_B in teams['player_B']['spaceship']:
        spaceship_list.append(vaisseau_team_B)
        
    if spaceship_name not in spaceship_list:
        if teams[player]['ore'] >= spaceships[spaceship_variety]['cost']:  #si le joueur a l'argent pour acheter le vaisseau
            teams[player]['ore'] -= spaceships[spaceship_variety]['cost']   #retire l'argent de l'achat du vaisseau de la réserve d'argent du joueur
            teams[player]['spaceship'][spaceship_name] = {}   #crée un nouveau vaisseau vide
            teams[player]['spaceship'][spaceship_name] = copy.deepcopy(spaceships[spaceship_variety])  #ajoute toute les donnée de ce vaissseau à partir du vaisseau type
            teams[player]['spaceship'][spaceship_name]['position']['center'] = [teams[player]['portal']['position']['center'][0],
                                                                                teams[player]['portal']['position']['center'][1]]#place le vaisseau au centre du portail
            
            iteration = 0
            while iteration < len(teams[player]['spaceship'][spaceship_name]['position']['others']):
                teams[player]['spaceship'][spaceship_name]['position']['others'][iteration][0] += teams[player]['spaceship'][spaceship_name]['position']['center'][0]   
                teams[player]['spaceship'][spaceship_name]['position']['others'][iteration][1] += teams[player]['spaceship'][spaceship_name]['position']['center'][1]   #place les autres positions du vaisseau
                iteration += 1

    return teams
    


def lock(teams, spaceship_name, asteroids, given_order, player):
    """Lock and unlock the excavators on the asteroids
    
    Parameters
    ----------
    teams: the dictionnary containing the data about the players (dict)
    spaceship_name: the name of the spaceship that the player wants to lock on the asteroid (str)
    asteroids : the dictionnary containing the data about the asteroids (dict)
    order: the orders of the player (str)
    player: the name of the player (str)
    
    Returns
    -------
    teams: the dictionnary containing the data about the players (dict)
    
    Version
    -------
    specification: Sarah (v.1 23/02/18)
    implementation: Sarah (v.1 14/04/18)
    """
    
    player_spaceships = []
    for vaisseau in teams[player]['spaceship']:   #liste des vaisseaux que le joueur possède déjà
        player_spaceships.append(vaisseau)
    
    if spaceship_name in player_spaceships:   #si le vaisseau appartient au joueur
        spaceship_type = teams[player]['spaceship'][spaceship_name]['type']
        if spaceship_type == 'excavator-S' or spaceship_type == 'excavator-M' or spaceship_type == 'excavator-L':
            if given_order == 'lock':
                for asteroid in asteroids:
                    if teams[player]['spaceship'][spaceship_name]['position']['center'] == asteroids[asteroid]['position']:   #si le centre du vaisseau est bien sur un astéroide
                        teams[player]['spaceship'][spaceship_name]['lock'] = asteroid   #verrouille l'extracteur sur l'astéroide
                
                if teams[player]['spaceship'][spaceship_name]['position']['center'] == teams[player]['portal']['position']['center']:   #si l'extracteur est sur le portail
                    teams[player]['spaceship'][spaceship_name]['lock'] = 'portal'   #verrouille l'extracteur sur le portail
                                
            if given_order == 'release':
                if teams[player]['spaceship'][spaceship_name]['lock'] != '':   #si l'extrateur est déjà verrouillé
                    teams[player]['spaceship'][spaceship_name]['lock'] = ''   #déverrouille l'extracteur
    
    return teams
    
    
    
def move(player, teams, spaceship_name, destination, nb_row, nb_column):
    """Move the spaceships on the board and check if it stays in the board
    
    Parameters
    ----------
    player: the name of the player (str)
    teams: the dictionnary containing the data about the players (dict)
    spaceship_name : name of the spaceship moving (str)
    destination : position where the spaceship moves (list)
    nb_column : number of columns of the board (int)
    nb_row : number of rows of the board (int)
    
    Return
    -------
    original_teams: the same teams than at the beginning of the function (dict)
    teams: the dictionnary containing the data about the players (dict)
        
    Version
    -------
    specification: Sarah (v.1 23/02/18)
    implementation: Hugo (v.1 14/04/18)
    """
    
    original_teams = copy.deepcopy(teams)
    
    player_spaceships = []
    for vaisseau in teams[player]['spaceship']:   #liste des vaisseaux que le joueur possède déjà
        player_spaceships.append(vaisseau)
        
    if spaceship_name in player_spaceships:   #si le vaisseau appartient au joueur
        
        if teams[player]['spaceship'][spaceship_name]['action'] == 'no':   #si le vaisseau ne s'est pas déplacé ou a attaqué ce tour ci 
        
            destination_y = destination[0] - teams[player]['spaceship'][spaceship_name]['position']['center'][0]
            destination_x = destination[1] - teams[player]['spaceship'][spaceship_name]['position']['center'][1]
                
            if destination_y in [-1,0,1] and destination_x in [-1,0,1]:
            
                teams[player]['spaceship'][spaceship_name]['position']['center'][0] += destination_y       #bouge le centre du vaisseau
                teams[player]['spaceship'][spaceship_name]['position']['center'][1] += destination_x
                
                iteration = 0
                while iteration < len(teams[player]['spaceship'][spaceship_name]['position']['others']):
                    teams[player]['spaceship'][spaceship_name]['position']['others'][iteration][0] += destination_y   #bouge les autres cases du vaisseau
                    teams[player]['spaceship'][spaceship_name]['position']['others'][iteration][1] += destination_x
                    iteration +=1
                    
                #---------------------------------------check board-------------------------------------
                
                if teams[player]['spaceship'][spaceship_name]['position']['center'][0] <= 0 or teams[player]['spaceship'][spaceship_name]['position']['center'][0] >= nb_row :
                    return original_teams
                    
                if teams[player]['spaceship'][spaceship_name]['position']['center'][1] <= 0 or teams[player]['spaceship'][spaceship_name]['position']['center'][1] >= nb_column :
                    return original_teams
                    
                iteration = 0
                while iteration < len(teams[player]['spaceship'][spaceship_name]['position']['others']):
                    if teams[player]['spaceship'][spaceship_name]['position']['others'][iteration][0] <= 0 or teams[player]['spaceship'][spaceship_name]['position']['others'][iteration][0] >= nb_row:
                        return original_teams
                    if teams[player]['spaceship'][spaceship_name]['position']['others'][iteration][1] <= 0 or teams[player]['spaceship'][spaceship_name]['position']['others'][iteration][1] >= nb_column:
                        return original_teams
                    iteration +=1
                    
                else:
                    return teams
                 
            else:
                return original_teams
        else:
            return original_teams
    else:
        return original_teams   
            


def attack(teams, attacker, position_attacked, player):
    """Make a spaceship attack a position and check if this position is occupied
    
    Parameters
    ----------
    teams: the dictionnary containing the data about the players (dict)
    attacker: name of the spaceship which attacks (str)
    position_attacked: the position attacked (list)
    player: the name of the player (str)
    
    Returns
    -------
    teams: the dictionnary containing the data about the players (dict)
    damage: return True if a damage is done this turn and False if not (bool)
    
    Version
    -------
    specification: Hugo (v.1 23/02/18)
    implementation: Hugo (v.1 14/04/18)
    """  
    
    damage = False
    
    player_spaceships = []
    for spaceship in teams[player]['spaceship']:   #liste des vaisseaux que le joueur possède déjà
        player_spaceships.append(spaceship)
    
    if attacker in player_spaceships:
        dist = distance(teams[player]['spaceship'][attacker]['position']['center'], position_attacked) #calcule la distance entre le vaisseau et le point ciblé
        if dist <= teams[player]['spaceship'][attacker]['range']:   #check si la distance entre le vaisseau et l'endroit ciblé est inférieur ou égal à la portée du vaisseau
            
            if teams[player]['spaceship'][attacker]['action'] == 'no':   #si le vaisseau ne s'est pas déplacé ou a attaqué ce tour ci  
                
                for player_name in teams:
                    for spaceship_name in teams[player_name]['spaceship']:   
                        if teams[player_name]['spaceship'][spaceship_name]['position']['center'] == position_attacked or position_attacked in teams[player_name]['spaceship'][spaceship_name]['position']['others']:   #check si des se trouvent à l'endroit ciblé
                            teams[player_name]['spaceship'][spaceship_name]['life'] -= teams[player]['spaceship'][attacker]['attack']  #occasionne les dégats suivant l'attaque de l'attaquant
                            damage = True   #des dégats ont été occasioné durant ce tour ci
                            
                    if teams[player_name]['portal']['position']['center'] == position_attacked or position_attacked in teams[player_name]['portal']['position']['others']:   #check si des se trouvent à l'endroit ciblé
                        teams[player_name]['portal']['life'] -= teams[player]['spaceship'][attacker]['attack']  #occasionne les dégats suivant l'attaque de l'attaquant
                        damage = True   #des dégats ont été occasioné durant ce tour ci
                    
                    
    return teams, damage
    

def reset_action(teams):
    """Resets the action of all spaceship to no
    
    Parameter
    ----------
    teams: the dictionnary containing the data about the players (dict)
    
    Return
    ------
    teams: the dictionnary containing the data about the players (dict)
    """
    
    for player in teams:
        for spaceship_name in teams[player]['spaceship']:
            teams[player]['spaceship'][spaceship_name]['action'] = 'no'
            
    return teams


def distance(point_A, point_B):
    """Compute the distance between two points
    Parameters
    ----------
    point_A : first point of the distance (list)
    point_B : second point of the distance (list)
    
    Return
    -------
    distance: the distance between two points (int)
    
    Version
    -------
    specification: Sarah (v.1 23/02/18)
    implementation: Sarah (v.1 14/04/18)
    """

    return abs(point_A[0]-point_B[0])+abs(point_A[1]-point_B[1])
    
    
    
def spaceship_killed(teams):
    """Check if some spaceships are dead and delete the dead ones from the dictionnary
    
    Parameters
    ----------
    teams: the dictionnary containing the data about the players (dict)
    
    Return
    -------
    teams: the dictionnary containing the data about the players (dict)
    
    Version
    -------
    specification: Hugo (v.1 23/02/18)
    implementation: Hugo (v.1 14/04/18)
    """
    
    for player in teams:
    
        spaceship_name_list = []   
        
        for name in teams[player]['spaceship']:
            spaceship_name_list.append(name)   #ajoute tous les noms présents dans l'équipe dans la liste
                        
        for spaceship_name in spaceship_name_list:
            if teams[player]['spaceship'][spaceship_name]['life'] <= 0: 
                del teams[player]['spaceship'][spaceship_name]   #si un vaisseau de l'équipe n'a plus de vie, il est retiré du dictionnaire principal
    
    return teams


def ore_loading_1_excavator (teams, asteroids, asteroid, attached_spaceships) :
    """
    Parameters
    ----------
    teams : the dictionnary containing the data about the players (dict)
    asteroids : the dictionnary containing the data about the asteroids (dict)
    asteroid : name of the asteroid (str)
    attached_spaceships : list containing the name of the excavator locked on the asteroid (list)
    
    Returns
    -------
    teams : the dictionnary containing the data about the players (dict)
    asteroids : the dictionnary containing the data about the asteroids (dict)
    """
    
    for excavator in attached_spaceships :
        if excavator in teams['player_A']['spaceship'] :
            remaining_capacity = teams['player_A']['spaceship'][excavator]['tonnage'] - teams['player_A']['spaceship'][excavator]['current_ore']
        elif excavator in teams['player_B']['spaceship'] :
            remaining_capacity = teams['player_B']['spaceship'][excavator]['tonnage'] - teams['player_B']['spaceship'][excavator]['current_ore']
        
        if remaining_capacity > 0 :
            if asteroids[asteroid]['ore'] >= asteroids[asteroid]['loading_ore'] :
                if remaining_capacity >= asteroids[asteroid]['loading_ore'] :
                    
                    for player in teams :
                        if excavator in teams[player]['spaceship'] :
                            
                            teams[player]['spaceship'][excavator]['current_ore'] += asteroids[asteroid]['loading_ore']
                            asteroids[asteroid]['ore'] -= asteroids[asteroid]['loading_ore']
                            
                elif remaining_capacity < asteroids[asteroid]['loading_ore'] :
                    
                    for player in teams :
                        if excavator in teams[player]['spaceship'] :
                            
                            teams[player]['spaceship'][excavator]['current_ore'] += remaining_capacity
                            asteroids[asteroid]['ore'] -= remaining_capacity
                                            
            elif asteroids[asteroid]['ore'] < asteroids[asteroid]['loading_ore'] :
                if remaining_capacity >= asteroids[asteroid]['ore'] :
                    
                    for player in teams :
                        if excavator in teams[player]['spaceship'] :
                            
                            teams[player]['spaceship'][excavator]['current_ore'] += asteroids[asteroid]['ore']
                            asteroids[asteroid]['ore'] -= asteroids[asteroid]['ore']
                            
                elif remaining_capacity < asteroids[asteroid]['ore'] :
                    
                    for player in teams :
                        if excavator in teams[player]['spaceship'] :
                            
                            teams[player]['spaceship'][excavator]['current_ore'] += remaining_capacity
                            asteroids[asteroid]['ore'] -= remaining_capacity
                
                    
    return teams, asteroids
    
def ore_loading_several_excavators (teams, asteroids, asteroid, attached_spaceships) :
    """
    Parameters
    ----------
    teams : the dictionnary containing the data about the players (dict)
    asteroids : the dictionnary containing the data about the asteroids (dict)
    asteroid : name of the asteroid (str)
    attached_spaceships : list containing the name of the excavator locked on the asteroid (list)
    
    Returns
    -------
    teams : the dictionnary containing the data about the players (dict)
    asteroids : the dictionnary containing the data about the asteroids (dict)
    """
    
    ore_to_give = asteroids[asteroid]['loading_ore'] * len(attached_spaceships)
    given_ore = 0
    
    while given_ore < ore_to_give :
        
        remaining_capacities = []
        not_full_attached_spaceships = []
    
        for excavator in attached_spaceships :
            
            if excavator in teams['player_A']['spaceship'] :
                remaining_capacity = teams['player_A']['spaceship'][excavator]['tonnage'] - teams['player_A']['spaceship'][excavator]['current_ore']
            elif excavator in teams['player_B']['spaceship'] :
                remaining_capacity = teams['player_B']['spaceship'][excavator]['tonnage'] - teams['player_B']['spaceship'][excavator]['current_ore']
                
            if remaining_capacity > 0 :
                remaining_capacities.append (remaining_capacity)
                not_full_attached_spaceships.append (excavator)
                
        if len(not_full_attached_spaceships) != 0 :
            ore_to_give = asteroids[asteroid]['loading_ore'] * len(not_full_attached_spaceships)
            ore_by_excavator = asteroids[asteroid]['ore'] / len(not_full_attached_spaceships)
            sorted(remaining_capacities)
            minimum_capacity = remaining_capacities [0]
                      
        else :        
            ore_by_excavator = 0
            minimum_capacity = 0
            
        if ore_by_excavator >= asteroids[asteroid]['loading_ore'] :

            if minimum_capacity >= asteroids[asteroid]['loading_ore'] :
                    
                for player in teams :
                    for excavator in not_full_attached_spaceships :
                        if excavator in teams[player]['spaceship'] :
                            
                            teams[player]['spaceship'][excavator]['current_ore'] += asteroids[asteroid]['loading_ore']
                            asteroids[asteroid]['ore'] -= asteroids[asteroid]['loading_ore']
                            given_ore += asteroids[asteroid]['loading_ore']
                                                                                
            elif minimum_capacity < asteroids[asteroid]['loading_ore'] :
                
                for player in teams :
                    for excavator in not_full_attached_spaceships :
                        if excavator in teams[player]['spaceship'] :
                            
                            teams[player]['spaceship'][excavator]['current_ore'] += minimum_capacity
                            asteroids[asteroid]['ore'] -= minimum_capacity
                            given_ore += minimum_capacity
                                                
        elif ore_by_excavator < asteroids[asteroid]['loading_ore']:
            
            if minimum_capacity >= ore_by_excavator :
                
                for player in teams :
                    for excavator in not_full_attached_spaceships :
                        if excavator in teams[player]['spaceship'] :
                            
                            teams[player]['spaceship'][excavator]['current_ore'] += ore_by_excavator
                            asteroids[asteroid]['ore'] -= ore_by_excavator
                            given_ore += ore_by_excavator
                            print (ore_by_excavator)
                                                                               
            elif minimum_capacity < ore_by_excavator :
                
                for player in teams :
                    for excavator in not_full_attached_spaceships :
                        if excavator in teams[player]['spaceship'] :
                            
                            teams[player]['spaceship'][excavator]['current_ore'] += minimum_capacity
                            asteroids[asteroid]['ore'] -= minimum_capacity
                            given_ore += minimum_capacity  
                                                    
        if asteroids[asteroid]['ore'] == 0 or ore_by_excavator == 0:
           given_ore = 9999
            
    return teams, asteroids    
       
def ore_loading_main (teams, asteroids) :
    """
    Parameters
    ----------
    teams : the dictionnary containing the data about the players (dict)
    asteroids : the dictionnary containing the data about the asteroids (dict)
    
    Returns
    -------
    teams : the dictionnary containing the data about the players (dict)
    asteroids : the dictionnary containing the data about the asteroids (dict)
    """
    
    for asteroid in asteroids :
        
        if asteroids[asteroid]['ore'] != 0 :
            
            attached_spaceships = []
                    
            for player in teams :
                for excavator in teams[player]['spaceship'] :
                    if teams[player]['spaceship'][excavator]['lock'] == asteroid :
                        attached_spaceships.append (excavator)
                        
            if len(attached_spaceships) == 1 :
                
                teams, asteroids = ore_loading_1_excavator (teams, asteroids, asteroid, attached_spaceships)
            
            elif len(attached_spaceships) > 1 :
                
                teams, asteroids = ore_loading_several_excavators (teams, asteroids, asteroid, attached_spaceships)
                
    return teams, asteroids
    
    
    
def ore_unloading(teams):
    """Unload ore from an excavator to the portal
    
    Parameters
    ----------
    teams: the dictionnary containing the data about the players (dict)
    player: the name of the player (str)
    
    Returns
    -------
    teams: the dictionnary containing the data about the players (dict)
        
    Version
    -------
    specification: Hugo (v.1 23/02/18)
    implementation: Sarah (v.1 14/04/18)
    """
    for player in teams:
        for excavator in teams[player]['spaceship']:
                if teams[player]['spaceship'][excavator]['lock'] == 'portal':
                    teams[player]['ore'] += teams[player]['spaceship'][excavator]['current_ore']
                    teams[player]['total_ore_loaded'] += teams[player]['spaceship'][excavator]['current_ore']  #ceci pourrait être dans ore_loading mais les règles ne sont pas assez précises à ce sujet
                    teams[player]['spaceship'][excavator]['current_ore'] = 0
                    teams[player]['spaceship'][excavator]['lock'] == ''
                    
    return teams



def random_name(teams):
    """Return a random name that is not already in the game
    
    Parameters
    ----------
    teams: the dictionnary containing the data about the players (dict)
    
    Returns
    -------
    name: the random name that is not already in the game (str)
    
    Version
    -------
    specification: Hugo (v.1 23/03/18)
    implementation: Hugo (v.1 14/04/18)
    """
    
    name_list = ['Larry_Banbelle','Jean_Meurdesoif','Lara_Clette','Jean_Bon','Claire_Delune','Yvon_Gagner','Aude_Vaissel','Yvon_Lachever','Candy_Ratons','Yvan_Dubois',
                 'Alain_Proviste','Vic_Tim','Sarah_Coursi','Gerard_Mensoif','Alain_Posteur','Aubin_Didon','Caesar_Hyène','Charles_Atant','Laurent_Houtan','Paul_Ochon', 'Benoit', 'Anne', 'Julie', 'Hugo', 'Sarah', 'Julien', 'Popeye', 'Lanfeust', 'Adrien', 'Elisa', 'Valentin']
                 
    spaceship_name_list = [] #cette liste comportera les noms déjà présent dans le jeu
    
    for player in teams:
        for spaceship_name in teams[player]['spaceship']:
            spaceship_name_list.append(spaceship_name)
            
    while True:        
        name = name_list[random.randint(0, 30)]  #prise d'un nom au hasard dans name_list
        if name not in spaceship_name_list:  #si le nom est déjà présent dans le jeu
            print (name)
            return name  #renvoie le nom s'il n'est présent ni dans l'équipe A ni dans l'équipe B
        
def move_AI(player, spaceship_AI, teams, destination_name, asteroids):
    """
    Parameters
    ----------
    player: the name of the player (str)
    spaceship_AI: the name of the spaceship moving (str)
    teams: the dictionnary containing the data about the players (dict)
    destination_name: the name of the destination. ex: portal, enemy_portal, asteroid(1,2,...)  (str)
    asteroids : dictionnary containing the data about the asteroids (dict) 
    
    Returns
    -------
    x_position: the number of the column the spaceship has to go to (str)
    y_position: the number of the row the spaceship has to go to (str)
    
    Version
    -------
    specification: Hugo (v.1 3/05/18)
    implementation: Hugo (v.1 3/05/18)
    
    """
    
    #-------get both positions-------------
    position_y_spaceship = teams[player]['spaceship'][spaceship_AI]['position']['center'][0]
    position_x_spaceship = teams[player]['spaceship'][spaceship_AI]['position']['center'][1]
    
    if destination_name == 'portal':
        position_y_destination = teams[player]['portal']['position']['center'][0]
        position_x_destination = teams[player]['portal']['position']['center'][1]
    
    elif destination_name == 'enemy_portal':
        if player == 'player_A':
            enemy_player = 'player_B'
        elif player == 'player_B':
            enemy_player = 'player_A'
    
        position_y_destination = teams[enemy_player]['portal']['position']['center'][0]
        position_x_destination = teams[enemy_player]['portal']['position']['center'][1]    
    
    elif 'asteroid' in destination_name:
        position_y_destination = asteroids[destination_name]['position'][0]
        position_x_destination = asteroids[destination_name]['position'][1]
        
        
    #------compute----------
    
    #--x position--
    
    if position_x_spaceship > position_x_destination:
        x_position = teams[player]['spaceship'][spaceship_AI]['position']['center'][1] - 1
        
    elif position_x_spaceship < position_x_destination:
        x_position = teams[player]['spaceship'][spaceship_AI]['position']['center'][1] + 1
        
    else:
        x_position = teams[player]['spaceship'][spaceship_AI]['position']['center'][1]
        
    #--y position--
    
    if position_y_spaceship > position_y_destination:
        y_position = teams[player]['spaceship'][spaceship_AI]['position']['center'][0] - 1
        
    elif position_y_spaceship < position_y_destination:
        y_position = teams[player]['spaceship'][spaceship_AI]['position']['center'][0] + 1
        
    else:
        y_position = teams[player]['spaceship'][spaceship_AI]['position']['center'][0]
    
    
    return x_position, y_position
    
    
def get_nearest_asteroid(teams,asteroids,spaceship_name, player):
    """return the name of the nearest asteroid not empty in the board
    
    Parameters
    ----------
    teams : dictionnary containing the data about the players (dict)
    asteroids : dictionnary containing the data about the asteroids (dict) 
    spaceship_name : name of the spaceship from which we want to find the nearest asteroid (str)
    player : the name of the player (str)
    
    Returns
    -------
    asteroid_name : name of the nearest asteroid (str)
    portal: the spaceship needs to go back to the portal (str)
    
    Version
    -------
    specification: Julien, Sarah (v.1 3/05/18)
    implementation: Julien, Sarah, Hugo (v.1 3/05/18)
    """
    
    distance_min = -1 
    nb_empty_asteroids = 0
    for asteroid in asteroids:
        if asteroids[asteroid]['ore'] != 0 : 
            dist= distance(teams[player]['spaceship'][spaceship_name]['position']['center'], asteroids[asteroid]['position'])
            if distance_min == -1 or dist < distance_min: 
                distance_min = dist
                asteroid_name = asteroid 
                
        else:
            nb_empty_asteroids += 1
            if nb_empty_asteroids == len(asteroids):
                asteroid_name = 'portal'
            
    return asteroid_name 
    
    
    
def check_spaces_in_orders(orders):
    """
    Parameter
    --------
    orders: the string containing all the orders of the AI of this turn (str)
    
    Return
    ------
    orders: the string containing all the orders of the AI of this turn (str)
    
    Version
    -------
    specification: Hugo, Sarah (v.1 3/05/18)
    implementation: Hugo, Sarah (v.1 3/05/18)
    
    """
    
    if orders != '':
        orders += ' '
    return orders
    
    

def AI(teams, spaceships, asteroids, player, turn_AI):
    """give orders from AI for the lap
    
    Parameters
    ----------
    teams: the dictionnary containing the data about the players (dict)
    spaceships : the dictionnary containing the basic data about the different spaceships the player can buy (dict)
    asteroids : the dictionnary containing the data about the asteroids (dict)
    player: the name of the player (str)
    turn_AI: the number of turn that AI played (int)
    
    Returns
    -------
    orders: the string containing all the orders of the AI of this turn (str)
    
    Version
    -------
    specification: Hugo, Sarah, Julien (v.1 3/05/18)
    implementation: Hugo, Sarah, Julien (v.1 3/05/18)
    """
    
    
    orders = ''
    if turn_AI == 1:
        orders += str(random_name(teams) + ':excavator-L')
    
    elif teams[player]['ore'] >= 9:
        orders += str(random_name(teams) + ':warship')
    elif teams[player]['ore'] == 8:
            
        name_1 = random_name(teams)
        orders = check_spaces_in_orders(orders)
        orders += str(name_1 + ':scout')
        
        name_2 = random_name(teams)
        while name_2 == name_1:
            name_2 = random_name(teams)
        orders = check_spaces_in_orders(orders)
        orders += str(name_2 + ':scout')
        
        name_3 = random_name(teams)
        while name_3 == name_1 or name_3 == name_2:
            name_3 = random_name(teams)
        orders = check_spaces_in_orders(orders)
        orders += str(name_3 + ':excavator-M')
    
    else:
        nb_empty_asteroids = 0
        for asteroid in asteroids:
            if asteroids[asteroid]['ore'] == 0:
                nb_empty_asteroids += 1
        if nb_empty_asteroids == len(asteroids) and teams[player]['ore'] >= 3:
            orders += str(random_name(teams) + ':scout')
        


    for spaceship_AI in teams[player]['spaceship']:
        if teams[player]['spaceship'][spaceship_AI]['type'] == 'scout' or teams[player]['spaceship'][spaceship_AI]['type'] == 'warship':
            
            if player == 'player_A':
                enemy_player = 'player_B'
            elif player == 'player_B':
                enemy_player = 'player_A'
                
            action = False
            
            
            #-----check if enemy on the way-------
            
            for enemy_spaceship in teams[enemy_player]['spaceship']:
                
                iteration = 0
                while iteration < len(teams[enemy_player]['spaceship'][enemy_spaceship]['position']['others']):
                    dist = distance(teams[player]['spaceship'][spaceship_AI]['position']['center'], teams[enemy_player]['spaceship'][enemy_spaceship]['position']['others'][iteration])
                    
                    if dist <= teams[player]['spaceship'][spaceship_AI]['range']:
                        orders = check_spaces_in_orders(orders)
                        orders += str(spaceship_AI + ':*' + str(teams[enemy_player]['spaceship'][enemy_spaceship]['position']['others'][iteration][0]) + '-' + str(teams[enemy_player]['spaceship'][enemy_spaceship]['position']['others'][iteration][1]))
                        iteration = 999999
                        action = True
                    iteration +=1
                
            #-----check if it is possible to attack the enemy portal------
            
            if action == False:
                attack = False
                iteration = 0
                while iteration < len(teams[enemy_player]['portal']['position']['others']):
                    dist = distance(teams[player]['spaceship'][spaceship_AI]['position']['center'], teams[enemy_player]['portal']['position']['others'][iteration])
                    if dist <= teams[player]['spaceship'][spaceship_AI]['range']:
                        orders = check_spaces_in_orders(orders)
                        orders += str(spaceship_AI + ':*' + str(teams[enemy_player]['portal']['position']['others'][iteration][0]) + '-' + str(teams[enemy_player]['portal']['position']['others'][iteration][1]))
                        iteration == 999999
                        attack = True
                    iteration += 1
                
                
                #-------move the spaceship to the enemy portal-------
                
                if attack == False: 
                    x_position, y_position = move_AI(player, spaceship_AI, teams, 'enemy_portal', asteroids)  
                    orders = check_spaces_in_orders(orders)
                    orders += str(spaceship_AI + ':@' + str(y_position) + '-' + str(x_position))
                
            
            
        elif teams[player]['spaceship'][spaceship_AI]['type'] == 'excavator-S' or teams[player]['spaceship'][spaceship_AI]['type'] == 'excavator-M' or teams[player]['spaceship'][spaceship_AI]['type'] == 'excavator-L':
            if teams[player]['spaceship'][spaceship_AI]['current_ore'] == teams[player]['spaceship'][spaceship_AI]['tonnage']:
                if 'asteroid' in teams[player]['spaceship'][spaceship_AI]['lock']:
                    orders = check_spaces_in_orders(orders)
                    orders += str(spaceship_AI + ':release')
                    x_position, y_position = move_AI(player, spaceship_AI, teams, 'portal', asteroids)
                    orders = check_spaces_in_orders(orders)
                    orders += str(spaceship_AI + ':@' + str(y_position) + '-' + str(x_position))
                    
                elif teams[player]['spaceship'][spaceship_AI]['position']['center'] != teams[player]['portal']['position']['center']:
                    x_position, y_position = move_AI(player, spaceship_AI, teams, 'portal', asteroids)
                    orders = check_spaces_in_orders(orders)
                    orders += str(spaceship_AI + ':@' + str(y_position) + '-' + str(x_position))
                    
                elif teams[player]['spaceship'][spaceship_AI]['lock'] != 'portal':
                    orders = check_spaces_in_orders(orders)
                    orders += str(spaceship_AI + ':lock')
                    
            else:
                if teams[player]['spaceship'][spaceship_AI]['lock'] == 'portal':
                    orders = check_spaces_in_orders(orders)
                    orders += str(spaceship_AI + ':release')
                    asteroid_name = get_nearest_asteroid(teams,asteroids,spaceship_AI, player)
                    x_position, y_position = move_AI(player, spaceship_AI, teams, asteroid_name, asteroids)
                    orders = check_spaces_in_orders(orders)
                    orders += str(spaceship_AI + ':@' + str(y_position)+ '-' + str(x_position))
                    
                else:
                    check_condition = False
                    check_loop = False     
                    
                    #------condition 1---------
                    
                    for asteroid in asteroids:
                        if asteroids[asteroid]['ore'] != 0:
                            if teams[player]['spaceship'][spaceship_AI]['position']['center'] == asteroids[asteroid]['position']:  #check si le vaisseau est sur un asteroide
                                check_loop = True
                                                    
                    #------condition 2---------
                    
                    if check_loop == False:   #si la condition 1 n'est pas remplie
                        asteroid_name = get_nearest_asteroid(teams,asteroids,spaceship_AI, player)
                        x_position, y_position = move_AI(player, spaceship_AI, teams, asteroid_name, asteroids)  
                        orders = check_spaces_in_orders(orders)
                        orders += str(spaceship_AI + ':@' + str(y_position) + '-' + str(x_position))   #le vaisseau se dirige vers l'asteroide non vide le plus proche
                        check_condition = True
                                            
                    if check_condition == False:   #si les conditions 1 et 2 ne sont pas remplies
                        
                        #------condition 3---------
                        
                        if teams[player]['spaceship'][spaceship_AI]['lock'][:8] != 'asteroid':
                            orders = check_spaces_in_orders(orders)
                            orders += str(spaceship_AI + ':lock')
                                                   
                        #------condition 4---------
                        
                        else:   #si les conditions 1, 2 et 3 ne sont pas remplies
                            asteroid = teams[player]['spaceship'][spaceship_AI]['lock']
                            if asteroids[asteroid]['ore'] == 0:
                                orders = check_spaces_in_orders(orders)
                                orders += str(spaceship_AI + ':release')
                                x_position, y_position = move_AI(player, spaceship_AI, teams, 'portal', asteroids)
                                orders = check_spaces_in_orders(orders)
                                orders += str(spaceship_AI + ':@' + str(y_position) + '-' + str(x_position))   #le vaisseau se dirige vers le portail
                                
    print(orders)
    return orders
        


def check_end_game(teams, global_damage, nb_turn):
    """Check if a player wins the game and print who is the winner
    
    Parameters
    ----------
    teams: the dictionnary containing the data about the players (dict)
    damage: True if a damage has been done this turn and False if not (bool)
    turn: the number of turns played without any dammage done (int)
    
    Returns
    -------
    nb_turn: the number of turns played without any dammage done (int)
    game_over : the game is over (bool)
    False : the game is not over (bool) 
        
    Version
    -------
    specification: Julien (v.1 23/02/18)
    implementation: Hugo (v.1 14/04/18)
    """
    
    game_over = True

    if global_damage == True:
        nb_turn = 0
    elif global_damage == False:
        nb_turn += 1

    if teams['player_A']['portal']['life'] <= 0 and teams['player_B']['portal']['life'] <= 0:    #choix arbitraire fait par le groupe car ce n'est pas précisé dans les consignes
        print('Draw, no one win the game')   #si les 2 portails sont détruits au même tour, il y a égalité
        return game_over, nb_turn
    
    elif teams['player_A']['portal']['life'] <= 0:  
        cprint('The player B win the game', 'cyan', 'on_red')  #si le portail de l'équipe A n'a plus de vie, l'équipe B gagne
        return game_over, nb_turn
    
    elif teams['player_B']['portal']['life'] <= 0:
        cprint('The player A win the game', 'white', 'on_cyan')   #si le portail de l'équipe B n'a plus de vie, l'équipe A gagne
        return game_over, nb_turn
        
    elif nb_turn > 200:
        if teams['player_A']['portal']['life'] > teams['player_B']['portal']['life']:
            cprint('The player A win the game', 'white', 'on_cyan')
            return game_over, nb_turn
            
        elif teams['player_A']['portal']['life'] < teams['player_B']['portal']['life']:
            cprint('The player B win the game', 'cyan', 'on_red')
            return game_over, nb_turn
            
        else:
            if teams['player_A']['total_ore_loaded'] > teams['player_B']['total_ore_loaded']:
                cprint('The player A win the game', 'white', 'on_cyan')
                return game_over, nb_turn
                
            elif teams['player_A']['total_ore_loaded'] < teams['player_B']['total_ore_loaded']:
                cprint('The player B win the game', 'cyan', 'on_red')
                return game_over, nb_turn
            
            else:
                print('Draw, no one win the game')
                return game_over, nb_turn
                
    else:
        return False, nb_turn




def game(fh, player_id, remote_IP):
    
    """Play the game with all the main functions
    
    Parameters
    ----------        
    fh: the file (.mw) with the starting information (file)
    player_id : id of the other player (int)
    remote_IP : IP of the other player's computer (str)
    
    Version
    -------
    specification: Julien (v.1 23/02/18)
    implementation: Hugo (v.1 14/04/18)
    """
    
    spaceships = {'scout':{'size':9,'type':'scout', 'life':3,'attack':1,'range':3,'cost':3, 'action':'no', 'lock':'', 'position':{'center':[0,0],'others':[[1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,1],[1,-1],[-1,-1]]}},
                  'warship':{'size':21,'type':'warship', 'life':18,'attack':3,'range':5,'cost':9, 'action':'no', 'lock':'', 'position':{'center':[0,0],'others':[[1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,1],[1,-1],[-1,-1],[2,0],[2,1],[2,-1],[0,2],[1,2],[-1,2],[-2,0],[-2,1],[-2,-1],[0,-2],[1,-2],[-1,-2]]}},
                  'excavator-S':{'size':1,'type':'excavator-S', 'tonnage':1, 'current_ore':0, 'life':2,'cost':1, 'action':'no', 'lock':'', 'position':{'center':[0,0],'others':[[0,0]]}},
                  'excavator-M':{'size':5,'type':'excavator-M', 'tonnage':4, 'current_ore':0, 'life':3,'cost':2, 'action':'no', 'lock':'', 'position':{'center':[0,0],'others':[[1,0],[-1,0],[0,1],[0,-1]]}},
                  'excavator-L':{'size':9,'type':'excavator-L', 'tonnage':8, 'current_ore':0, 'life':6,'cost':4, 'action':'no', 'lock':'', 'position':{'center':[0,0],'others':[[1,0],[-1,0],[0,1],[0,-1],[0,2],[0,-2],[2,0],[-2,0]]}}}
    
    connection = remote_play.connect_to_player(player_id, remote_IP, False)
    
    teams, asteroids, nb_row, nb_column, grid = create_board(fh)
    show_board(teams, asteroids, nb_column, nb_row, grid)
    nb_turn = 1
    turn_AI = 1
    
    game_over = False
    while game_over == False:
        
        print(teams)
            
        if player_id == 2:
            orders_player_A = AI(teams, spaceships, asteroids, 'player_A', turn_AI)
            remote_play.notify_remote_orders(connection, orders_player_A)
            orders_player_B = remote_play.get_remote_orders(connection)
            print(orders_player_B)
            
        elif player_id == 1:
            orders_player_A = remote_play.get_remote_orders(connection)
            orders_player_B = AI(teams, spaceships, asteroids, 'player_B', turn_AI)
            remote_play.notify_remote_orders(connection, orders_player_B)
            print(orders_player_A)
            
        orders = order(orders_player_A, orders_player_B)
        
        
        #---------purchase---------
        
        for player in teams:
            for purchase_order in orders['purchase'][player]:
                spaceship_name = purchase_order
                spaceship_variety = orders['purchase'][player][purchase_order]
                teams = purchase(teams, spaceships, spaceship_name, spaceship_variety, player)
        
        
        #-----------move-----------
        
        for player in teams:
            for move_order in orders['move'][player]:
                spaceship_name = move_order
                destination = orders['move'][player][move_order]
                teams = move(player, teams, spaceship_name, destination, nb_row, nb_column)
        
 
        #----------attack-----------
        
        global_damage = False
        
        for player in teams:
            for attack_order in orders['attack'][player]:
                attacker = attack_order
                position_attacked = orders['attack'][player][attack_order]
                teams, damage = attack(teams, attacker, position_attacked, player)
                if damage == True:
                    global_damage = True
        
        
        teams = spaceship_killed(teams)
        
        
        #-------- lock ---------
        
        for player in teams:
            for lock_order in orders['lock'][player]:
                spaceship_name = lock_order 
                given_order = orders['lock'][player][lock_order]  
                teams = lock(teams, spaceship_name, asteroids, given_order, player)
        
        
        #----------------
        
        ore_loading_main(teams, asteroids)
        
        ore_unloading(teams)
        
        show_board(teams, asteroids, nb_column, nb_row, grid)
        
        game_over, nb_turn = check_end_game(teams, global_damage, nb_turn)
        
        reset_action(teams)
        
        turn_AI += 1
        
        #time.sleep(0.3)
        



game('../maps/target.mw', 2, '138.48.160.146')
































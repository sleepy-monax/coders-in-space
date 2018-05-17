# -*- coding: utf-8 -*-

import os
import random
from colored import fg,bg, attr
import copy
import remote_play

def creation_board(card_txt):
    """ This function creates the board onwich the game will be played. The size of the board is given by a file.
    
    Parameters
    ----------
    card_txt: this is the file that will be used to create the board and it gives the size of the board (file).
    
    Return
    -------
    board: The data structure of the board (list)
    gate_A: The data structure of the gate of the player A (dictionnary)
    gate_B: The data structure of the gate of the player B (dictionnary)
    asteroides: The data structure of the asteroides (dictionnary)
    size_board: The data structure of the size of the board (tuple)
    
    Version 
    -------
    Specification: Lana Silvagni (v.1 26/02/18)
    Specification: Camille Paindaveine (v.2 16/03/18)
    Specification: Coline Verhoeven (v.3 28/03/18)
    Implementation: Coline Verhoeven / Lana Silvagni (v.1 28/03/18)
    Implementation: Coline Verhoeven / Lana Silvagni / Camille Paindaveine (v.15/04/18)
    """
    
    card = open(card_txt, 'r')  
    fh = card.readlines()
    ##('size:', '39 40', 'portals:', '20 3', '20 38', 'asteroids:', '10 14 12 1', '5 21 12 2') 
    card.close()  
    
    ## Creation of the data structure of the board 
    board = []
    size = fh[1].split(' ')
    lines = int(size[0])
    columns = int(size[1])
    size_board = (lines, columns)
    
    for e in range(lines):
        board.append ([])
        for i in range(columns): 
            board[e].append ([])
            
    ## Add gates
    gate_A = {}
    gate_B = {}     
    for i in range(3, 5):
        portals = fh[i].split(' ') 
        lines = int(portals[0]) 
        columns = int(portals[1]) 
        
        ##Gate A
        if i == 3: 
            gate_A['Centre'] = [lines, columns] 
            gate_A['Position'] = [[lines-2, columns-2],[lines-2, columns-1], [lines-2, columns],[lines-2, columns+1],[lines-2, columns+2],
                                [lines-1, columns-2],[lines-1, columns-1],[lines-1, columns],[lines-1, columns+1], [lines-1, columns+2],
                                    [lines, columns-2],[lines, columns-1],[lines, columns+1],[lines, columns+2],
                                    [lines+1, columns-2],[lines+1, columns-1],[lines+1, columns],[lines+1, columns+1],[lines+1, columns+2],
                                    [lines+2, columns-2],[lines+2, columns-1],[lines+2, columns],[lines+2, columns+1],[lines+2, columns+2]]
            
            gate_A['Ore'] = 4
            gate_A['Life'] = 100
            
            ## Add gate A on the board
            
            board [lines-1][columns-1] += 'a'##Centre
            board [lines-3][columns-3] += 'a'
            board [lines-3][columns-2] += 'a'
            board [lines-3][columns-1] += 'a'
            board [lines-3][columns] += 'a'
            board [lines-3][columns+1] += 'a'
            board [lines-2][columns-3] += 'a'
            board [lines-2][columns-2] += 'a'
            board [lines-2][columns-1] += 'a'
            board [lines-2][columns] += 'a'
            board [lines-2][columns+1] += 'a'
            board [lines-1][columns-3] += 'a'
            board [lines-1][columns-2] += 'a'
            board [lines-1][columns] += 'a'
            board [lines-1][columns+1] += 'a'
            board [lines][columns-3] += 'a'
            board [lines][columns-2] += 'a'
            board [lines][columns-1] += 'a'
            board [lines][columns] += 'a'
            board [lines][columns+1] += 'a'
            board [lines+1][columns-3] += 'a'
            board [lines+1][columns-2] += 'a'
            board [lines+1][columns-1] += 'a'
            board [lines+1][columns] += 'a'
            board [lines+1][columns+1] += 'a'
               
         ## Gate B   
        if i == 4:
            gate_B['Centre'] = [lines, columns]
            gate_B['Position'] = [[lines-2, columns-2],[lines-2, columns-1], [lines-2, columns],[lines-2, columns+1],[lines-2, columns+2],
                                [lines-1, columns-2],[lines-1, columns-1],[lines-1, columns],[lines-1, columns+1], [lines-1, columns+2],
                                    [lines, columns-2],[lines, columns-1],[lines, columns+1],[lines, columns+2],
                                    [lines+1, columns-2],[lines+1, columns-1],[lines+1, columns],[lines+1, columns+1],[lines+1, columns+2],
                                    [lines+2, columns-2],[lines+2, columns-1],[lines+2, columns],[lines+2, columns+1],[lines+2, columns+2]]
                                    
            gate_B['Ore'] = 4
            gate_B['Life'] = 100
            
            ## Add gate B on the board
            board [lines-1][columns-1] += 'b'
            board [lines-3][columns-3] += 'b'
            board [lines-3][columns-2] += 'b'
            board [lines-3][columns-1] += 'b'
            board [lines-3][columns] += 'b'
            board [lines-3][columns+1] += 'b'
            board [lines-2][columns-3] += 'b'
            board [lines-2][columns-2] += 'b'
            board [lines-2][columns-1] += 'b'
            board [lines-2][columns] += 'b'
            board [lines-2][columns+1] += 'b'
            board [lines-1][columns-3] += 'b'
            board [lines-1][columns-2] += 'b'
            board [lines-1][columns] += 'b'
            board [lines-1][columns+1] += 'b'
            board [lines][columns-3] += 'b'
            board [lines][columns-2] += 'b'
            board [lines][columns-1] += 'b'
            board [lines][columns] += 'b'
            board [lines][columns+1] += 'b'
            board [lines+1][columns-3] += 'b'
            board [lines+1][columns-2] += 'b'
            board [lines+1][columns-1] += 'b'
            board [lines+1][columns] += 'b'
            board [lines+1][columns+1] += 'b'
        
    ## Add asteroids 
    lengh = len(fh)
    ## creation of the data strucures of the asteroids
    asteroides = {}
    for i in range(6, lengh):
        asteroids = fh[i].split(' ') 
        lines = int(asteroids[0])
        columns = int(asteroids[1])
        board [lines-1][columns-1] += '*'
        ore = int(asteroids[2])
        possibility= int(asteroids[3])
        asteroides[(lines, columns)] = {'Ore': ore, 'Possibility': possibility, 'Position': [lines, columns] } 
    
    return (board, gate_A, gate_B, asteroides, size_board)

def unlock(gamer, name):
    """ This functions unlocks an extractor out of an asteroid.
    
    Parameters
    ----------
    gamer: The data structure of the gamer who wants to unlock (dictionnary)
    name: The name of the extractor who has to be unlocked (str)
    
    Return
    ------
    gamer: The data structure of the gamer who wants to unlock (dictionnary)
    
    Version
    -------
    Specification: Coline Verhoeven (v.1 02/03/18)
    Specification: Coline Verhoeven / Lana Silvagni (v.2 29/03/18)
    Implementation:  Coline Verhoeven / Lana Silvagni (v.1 29/03/18)
    """
    ## unlock an excavator if he is locked
    if gamer[name]['Type'] == 's' or gamer[name]['Type'] == 'm' or gamer[name]['Type'] == 'l':
        if gamer[name]['Life'] > 0:
            if gamer[name]['State'] == 1:
                gamer[name]['State'] = 0 
                
            else : None 
        else: None
                
    else: None
        
    return gamer
        
        
def lock(gamer, name, asteroides, gate):
    """ This function is used to lock an extractor on an asteroid or a gate to respectively collect and unload ore. 
    An extractor is automaticaly lock if his position is the center of an asteroid or the center of a gate. 
        
    Parameters
    ----------
    gamer:  The data strucure of the gamer who wants to lock an excavator (dictionnary)
    name: The name of the excavator who has to be locked (str)
    asteroides: The data structure of the asteroids (dictionnary)
    gate: The data structure of the gate of the gamer (dictionnary)
    
    Return
    ------
    gamer: The data structure of the gamer (dictionnary)
    
    Version
    -------
    Specification: Coline Verhoeven / Lana Silvagni (v.1 26/02/18)
    Specification: Coline Verhoeven / Lana Silvagni (v.2 29/03/18)
    Implementation: Coline Verhoeven / Lana Silvagni (v.1 29/03/18)
    """
    
    ## Lock an excavator an an asteroid if he is unlock and if his center is on a asteroid
    for i in asteroides:
        if gamer[name]['Type'] == 's' or gamer[name]['Type'] == 'm' or gamer[name]['Type'] == 'l':
            if gamer[name]['Life'] > 0:
                if gamer[name]['State'] == 0:
                    if gamer[name]['Centre'] == asteroides[i]['Position']:
                        gamer[name]['State'] = 1
                    else: None
                else: None
            else: None
        else: None
                    
    ## Lock an excavator on a gate if he is unlock and if his center is on the center of his gate           
    if gamer[name]['Type'] == 's' or gamer[name]['Type'] == 'm' or gamer[name]['Type'] == 'l':
        if gamer[name]['Life'] > 0:
            if gamer[name]['State'] == 0:
                if gamer[name]['Centre'] == gate['Centre']:
                    gamer[name]['State'] = 1        
                else: None
            else: None
        else: None
    else: None
    
    return gamer 

def shop(gamer, gate, name, space_machine, board):
    """ This function buys and places the new starships or the new extractors of the gamer. The space machines are listed in different data structures.
    
    Parameters
    ----------
    gamer: Gamer who buys the space machine (dictionnary)
    name: The name that the gamer have given to his space machine (str)
    gate: The gate of the player who bought something (dictionnary)
    space_machine: The type of space machine that the player buys (str)
    board: The board which is used to add the space machine (list)
    
    Return
    ------
    gate: The data structure of the gate (dictionnary)
    gamer: The data structure of the gamer in wich the new space machine is added (dictionnary)
    board: The data structure of the board in wich the new space machine is added(list) 
    
    Version
    -------
    Specification: Coline Verhoeven (v.1 26/02/18)
    Specification: Camille Paindaveine (v.2 16/03/18)
    Specification: Camille Paindaveine / Lana Silvagni (v.3 28/03/18)
    Implementation: Camille Paindaveine (v.1 16/03/18)
    Implementation: Camille Paindaveine / Lana Silvagni (v.2 28/03/18)
    Implementation: Coline Verhoeven / Lana Silvagni (v.3 29/03/18)
    Implementation: Coline Verhoeven / Lana Silvagni / Camille Paindaveine (v.4 15/04/18) 
    """
    ## buy a space machine if the player has enough ore, place it on his gate, add the new space machine with all his specificities in the data 
    ##structure of the player, delete the price of the space machine from the gate of the player and add the new space machine to the board
    ore = gate['Ore']
    ## Excavator S
    if space_machine == 'excavator-S' and ore >= 1:
        place = copy.deepcopy (gate['Centre'])
        gamer[name] = {'Size' : 1, 'Tonnage' : 1, 'Life': 2, 'Attack': 0, 'Reach': 0, 'State': 0, 'Centre': place, 'Position': [], 'Capacity':0, 'Type':'s'}
        gate ['Ore'] -= 1
        ## Add Excavator S on the board 
        board[place[0]-1][place[1]-1] += 's'
        
    ## Excavator M
    elif space_machine == 'excavator-M' and ore >= 2:
        place = copy.deepcopy (gate['Centre'])
        gamer[name] = {'Size' : 5, 'Tonnage' : 4, 'Life': 3, 'Attack': 0, 'Reach': 0, 'State': 0, 'Centre': place, 'Position' : [[place[0]-1, place[1]],[place[0], place[1]-1], [place[0], place[1]+1],[place[0]+1, place[1]]], 'Capacity':0,'Type':'m' }
        gate ['Ore'] -= 2
        ## Add Excavator M on the board
        board[place[0]-1][place[1]-1] += 'm' ## Centre
        board[place[0]-2][place[1]-1] += 'm'
        board[place[0]-1][place[1]-2] += 'm'
        board[place[0]-1][place[1]] += 'm'
        board[place[0]][place[1]-1] += 'm'
        
    ##Excavator L
    elif space_machine == 'excavator-L' and ore >= 4:
        place = copy.deepcopy (gate['Centre'])
        gamer[name] = {'Size' : 9, 'Tonnage' : 8, 'Life': 6, 'Attack': 0, 'Reach': 0, 'State': 0, 'Centre' : place, 'Position' : [[place[0]-2, place[1]],[place[0]-1,place[1]], [place[0], place[1]-2],[place[0], place[1]-1], [place[0], place[1]+1],[place[0], place[1]+2],[place[0]+1, place[1]], [place[0]+2, place[1]]], 'Capacity':0, 'Type':'l'}
        gate ['Ore'] -= 4
        ## Add Excavator L on the board
        board[place[0]-1][place[1]-1] += 'l' ## Centre
        board[place[0]-3][place[1]-1] += 'l'
        board[place[0]-2][place[1]-1] += 'l'
        board[place[0]-1][place[1]-3] += 'l'
        board[place[0]-1][place[1]-2] += 'l'
        board[place[0]-1][place[1]] += 'l'
        board[place[0]-1][place[1]+1] += 'l'
        board[place[0]][place[1]-1] += 'l'
        board[place[0]+1][place[1]-1] += 'l'   

    ## Scout  
    elif space_machine == 'scout' and ore >= 3:
        place = copy.deepcopy (gate['Centre'])
        gamer[name] = {'Size' : 9, 'Tonnage' : 0, 'Life': 3, 'Attack': 1,'State': 0, 'Reach': 3, 'Centre': place, 'Position' : [[place[0]-1, place[1]-1],[place[0]-1, place[1]],[place[0]-1, place[1]+1],[place[0], place[1]-1], [place[0], place[1]+1],[place[0]+1, place[1]-1],[place[0]+1, place[1]],[place[0]+1, place[1]+1]], 'Type':'v' }
        gate ['Ore'] -= 3
        ## Add scout on the board
        board[place[0]-1][place[1]-1] += 'v' ## Centre
        board[place[0]-2][place[1]-2] += 'v'
        board[place[0]-2][place[1]-1] += 'v'
        board[place[0]-1][place[1]] += 'v'
        board[place[0]-1][place[1]-2] += 'v'
        board[place[0]-2][place[1]] += 'v'
        board[place[0]][place[1]-2] += 'v'
        board[place[0]][place[1]-1] += 'v'
        board[place[0]][place[1]] += 'v' 
    
    ## Warship    
    elif space_machine == 'warship' and ore >= 9:
        place = copy.deepcopy (gate['Centre'])
        gamer[name] = {'Size' : 21, 'Tonnage' : 0, 'Life': 18, 'Attack': 3, 'Reach': 5,'State': 0,  'Centre' : place, 'Position' : [[place[0]-2, place[1]-1],[place[0]-2, place[1]],[place[0]-2, place[1]+1],[place[0]-1, place[1]-2],[place[0]-1, place[1]-1],[place[0]-1, place[1]],[place[0]-1, place[1]+1],[place[0]-1, place[1]+2],[place[0], place[1]-2],[place[0], place[1]-1],[place[0], place[1]+1],[place[0], place[1]+2],[place[0]+1, place[1]-2],[place[0]+1, place[1]-1],[place[0]+1, place[1]],[place[0]+1, place[1]+1],[place[0]+1, place[1]+2],[place[0]+2, place[1]-1],[place[0]+2, place[1]],[place[0]+2, place[1]+1]], 'Type':'w' }
        gate ['Ore'] -= 9
        
        ## Add warship on the board
        board[place[0]-1][place[1]-1] += 'w' ## Centre
        board[place[0]-3][place[1]-2] += 'w'
        board[place[0]-3][place[1]-1] += 'w'
        board[place[0]-3][place[1]] += 'w'
        board[place[0]-2][place[1]-3] += 'w'
        board[place[0]-2][place[1]-2] += 'w'
        board[place[0]-2][place[1]-1] += 'w'
        board[place[0]-2][place[1]] += 'w'
        board[place[0]-2][place[1]+1] += 'w'
        board[place[0]-1][place[1]-3] += 'w'
        board[place[0]-1][place[1]-2] += 'w'
        board[place[0]-1][place[1]] += 'w'
        board[place[0]-1][place[1]+1] += 'w'
        board[place[0]][place[1]-3] += 'w'
        board[place[0]][place[1]-2] += 'w'
        board[place[0]][place[1]-1] += 'w'
        board[place[0]][place[1]] += 'w' 
        board[place[0]][place[1]+1] += 'w'
        board[place[0]+1][place[1]-2] += 'w'
        board[place[0]+1][place[1]-1] += 'w'
        board[place[0]+1][place[1]] += 'w'
    
    return (gate, gamer, board)
    
def shifting(gamer, board, name, line, column, size_board):
    """ This function is used to move a starship or an extractor from a point to another between the 8 cases that surround it.
    
    Parameters
    ----------
    gamer: The data structure of the gamer (dictionnary)
    board: The data structure of the board (list)
    name: The name of the space machine (str)
    line: The line position of the space machine (int)
    column: The column position of the space machine (int)
    size_board: The data structure of the size of the board (tuple)
    
    Return
    ------
    gamer: The data structure of the player (dictionnary)
    board: The data structure of the board (list)
    
    Version
    -------
    Specification: Camille Paindaveine / Lana Silvagni (v.1 26/02/18)
    Specification: Coline Verhoeven /Lana Silvagni (v.2 13/04/18)
    Implementation: Coline Verhoeven / Lana Silvagni (v.1 29/03/18)
    Implementation: Coline Verhoeven / Lana Silvagni (v.2 13/04/18)
    """

    ## Check if the space machine is unlock
    if gamer[name]['State'] == 0:
        if gamer[name]['Life'] > 0:
            ## Check if the new position is not out of the board
            departure = gamer[name]['Centre']
            move_line = int(line) - departure[0]
            move_column = int(column) - departure[1]
            
            accept = 0 
            
            ## Verifie si les mouvements sont autorisés
            for z in range(len(gamer[name]['Position'])):
                if move_line == 0 and move_column == 0:
                    None
                    
                ## Move one case to the right 
                elif move_line == 0 and move_column == 1: 
                    if ((gamer[name]['Position'][z][1]) + 1) > size_board[1]:
                        accept += 1  
                        
                ## Move one case to the left
                elif move_line == 0 and move_column == -1: 
                    if ((gamer[name]['Position'][z][1]) - 1) < 1:
                        accept += 1 
                    
                ## Move one case down
                elif move_line == 1 and move_column == 0:
                    if ((gamer[name]['Position'][z][0]) + 1) > size_board[0]:
                        accept += 1
                    
                ## Move one case up
                elif move_line == - 1 and move_column == 0:
                    if ((gamer[name]['Position'][z][0]) - 1) < 1:
                        accept += 1
                        
                ## Move one case diagonally to the left down
                elif move_line == 1 and move_column == -1 :
                    if ((gamer[name]['Position'][z][0]) + 1) > size_board[0] and (gamer[name]['Position'][z][1] - 1) < 1 :
                        accept += 1 
                
                ## Move one case diagonally to the right down
                elif move_line == 1 and move_column == 1 :
                    if ((gamer[name]['Position'][z][0]) + 1) > size_board[0] and ((gamer[name]['Position'][z][1]) + 1) > size_board[1]:
                        accept += 1 
                        
                ## Move one case diagonally to the left up
                elif move_line == - 1 and move_column == - 1 :
                    if ((gamer[name]['Position'][z][0]) - 1) < 1 and ((gamer[name]['Position'][z][1]) - 1) < 1 :
                        accept += 1 
                
                ## Move one case diagonally to the right up
                elif move_line == - 1 and move_column == 1 :
                    if ((gamer[name]['Position'][z][0])- 1) < 1 and ((gamer[name]['Position'][z][1]) + 1) > size_board[1]:
                        accept += 1 
                
                else : 
                    None
                    
            
            ## Mouvement autorisé
            if accept == 0:
                ## Center
                ## Move one case to the right 
                if move_line == 0 and move_column == 1:
                    center = board[gamer[name]['Centre'][0]- 1][gamer[name]['Centre'][1]-1]
                    delete_center = 0
                    for v in range (len(center)):
                        if delete_center == 0:
                            if center[v] == gamer[name]['Type']:
                                center[v] = ''
                                delete_center += 1
                                
                    ## Add the center of the space machine on his new case
                    gamer[name]['Centre'][1] += 1 
                    board[gamer[name]['Centre'][0]- 1][gamer[name]['Centre'][1]-1] += gamer[name]['Type']
                    
                ## Move one case to the left
                elif move_line == 0 and move_column == -1:
                    center = board[gamer[name]['Centre'][0]- 1][gamer[name]['Centre'][1]-1]
                    delete_center = 0
                    for v in range (len(center)):
                        if delete_center == 0:
                            if center[v] == gamer[name]['Type']:
                                center[v] = ''
                                delete_center += 1
                                
                    ## Add the center of the space machine on his new case
                    gamer[name]['Centre'][1] -= 1 
                    board[gamer[name]['Centre'][0]- 1][gamer[name]['Centre'][1]-1] += gamer[name]['Type']
                
                ## Move one case down
                elif move_line == 1 and move_column == 0:
                    center = board[gamer[name]['Centre'][0]- 1][gamer[name]['Centre'][1]-1]
                    delete_center = 0
                    for v in range (len(center)):
                        if delete_center == 0:
                            if center[v] == gamer[name]['Type']:
                                center[v] = ''
                                delete_center += 1
                    
                                
                ## Add the center of the space machine on his new case
                    gamer[name]['Centre'][0] += 1 
                    board[gamer[name]['Centre'][0]- 1][gamer[name]['Centre'][1]-1] += gamer[name]['Type']
                
                ## Move one case up
                elif move_line == - 1 and move_column == 0:
                    center = board[gamer[name]['Centre'][0]- 1][gamer[name]['Centre'][1]-1]
                    delete_center = 0
                    for v in range (len(center)):
                        if delete_center == 0:
                            if center[v] == gamer[name]['Type']:
                                center[v] = ''
                                delete_center += 1
                                
                ## Add the center of the space machine on his new case
                    gamer[name]['Centre'][0] -= 1 
                    board[gamer[name]['Centre'][0]- 1][gamer[name]['Centre'][1]-1] += gamer[name]['Type']
                    
                ## Move one case diagonally to the left down
                elif move_line == 1 and move_column == -1 :
                    center = board[gamer[name]['Centre'][0]- 1][gamer[name]['Centre'][1]-1]
                    delete_center = 0
                    for v in range (len(center)):
                        if delete_center == 0:
                            if center[v] == gamer[name]['Type']:
                                center[v] = ''
                                delete_center += 1
                                
                    ## Add the center of the space machine on his new case
                    gamer[name]['Centre'][0] += 1
                    gamer[name]['Centre'][1] -= 1 
                    board[gamer[name]['Centre'][0]- 1][gamer[name]['Centre'][1]-1] += gamer[name]['Type']
                    
                ## Move one case diagonally to the right down
                elif move_line == 1 and move_column == 1 : 
                    center = board[gamer[name]['Centre'][0]- 1][gamer[name]['Centre'][1]-1]
                    delete_center = 0
                    for v in range (len(center)):
                        if delete_center == 0:
                            if center[v] == gamer[name]['Type']:
                                center[v] = ''
                                delete_center += 1
                    ## Add the center of the space machine on his new case
                    gamer[name]['Centre'][0] += 1
                    gamer[name]['Centre'][1] += 1 
                    board[gamer[name]['Centre'][0]- 1][gamer[name]['Centre'][1]-1] += gamer[name]['Type']
                    
                ## Move one case diagonally to the left up
                elif move_line == - 1 and move_column == - 1 :
                    center = board[gamer[name]['Centre'][0]- 1][gamer[name]['Centre'][1]-1]
                    delete_center = 0
                    for v in range (len(center)):
                        if delete_center == 0:
                            if center[v] == gamer[name]['Type']:
                                center[v] = ''
                                delete_center += 1
                    ## Add the center of the space machine on his new case
                    gamer[name]['Centre'][0] -= 1
                    gamer[name]['Centre'][1] -= 1 
                    board[gamer[name]['Centre'][0]- 1][gamer[name]['Centre'][1]-1] += gamer[name]['Type']
                    
                ## Move one case diagonally to the right up 
                elif move_line == - 1 and move_column == 1 :
                    center = board[gamer[name]['Centre'][0]- 1][gamer[name]['Centre'][1]-1]
                    delete_center = 0
                    for v in range (len(center)):
                        if delete_center == 0:
                            if center[v] == gamer[name]['Type']:
                                center[v] = ''
                                delete_center += 1
                    ## Add the center of the space machine on his new case
                    gamer[name]['Centre'][0] -= 1
                    gamer[name]['Centre'][1] += 1 
                    board[gamer[name]['Centre'][0]- 1][gamer[name]['Centre'][1]-1] += gamer[name]['Type']
                    
            
                ## Other position
                for place in gamer[name]['Position']:
                    if move_line == 0 and move_column == 0:
                        None
                    
                    ## Move one case to the right 
                    elif move_line == 0 and move_column == 1: 
                        ## Delete from the old case
                        delete = 0 
                        case = board[place[0]- 1][place[1]-1]
                        for i in range (len(case)):
                            if delete == 0:
                                if case[i] == gamer[name]['Type']:
                                    case[i] = ''
                                    delete += 1
                                    
                        ## Add the space machine on his new case
                        place[1] += 1
                        board[place[0]- 1][place[1]-1] += gamer[name]['Type']
                            
                    ## Move one case to the left
                    elif move_line == 0 and move_column == -1: 
                        ## Delete from the old case 
                        delete = 0 
                        case = board[ place[0]- 1][place[1]-1]
                        for i in range (len(case)):
                            if delete == 0:
                                if case[i] == gamer[name]['Type']:
                                    case[i] = ''
                                    delete += 1
                                    
                        ## Add the space machine on his new case
                        place[1] -= 1
                        board[place[0]- 1][place[1]-1] += gamer[name]['Type']
                        
                        
                    ## Move one case down
                    elif move_line == 1 and move_column == 0:
                        
                        ## Delete from the old case 
                        delete = 0 
                        case = board[place[0]- 1][place[1]-1]
                        for i in range (len(case)):
                            if delete == 0:
                                if case[i] == gamer[name]['Type']:
                                    case[i] = ''
                                    delete += 1
                                    
                        ## Add the space machine on his new case
                        place[0] += 1
                        board[place[0]- 1][place[1]-1] += gamer[name]['Type']
                    
                    
                    ## Move one case up
                    elif move_line == - 1 and move_column == 0:
                        
                        ## Delete from the old case 
                        delete = 0 
                        case = board[place[0]- 1][place[1]-1]
                        for i in range (len(case)):
                            if delete == 0:
                                if case[i] == gamer[name]['Type']:
                                    case[i] = ''
                                    delete += 1
                                    
                        ## Add the space machine on his new case
                        place[0] -= 1 
                        board[place[0]- 1][place[1]-1] += gamer[name]['Type']
                            
                            
                    ## Move one case diagonally to the left down
                    elif move_line == 1 and move_column == -1 :
                        
                        
                        ## Delete from the old case 
                        delete = 0 
                        case = board[place[0]- 1][place[1]-1]
                        for i in range (len(case)):
                            if delete == 0:
                                if case[i] == gamer[name]['Type']:
                                    case[i] = ''
                                    delete += 1
                                    
                        ## Add the space machine on his new case
                        place[0] += 1
                        place[1] -= 1
                        board[place[0]- 1][place[1]-1] += gamer[name]['Type']
                            
                    
                    ## Move one case diagonally to the right down
                    elif move_line == 1 and move_column == 1 : 
                        ## Delete from the old case 
                        delete = 0 
                        case = board[place[0]- 1][place[1]-1]
                        for i in range (len(case)):
                            if delete == 0:
                                if case[i] == gamer[name]['Type']:
                                    case[i] = ''
                                    delete += 1
                                    
                        ## Add the space machine on his new case
                        place[0] += 1 
                        place[1] += 1
                        board[place[0]- 1][place[1]-1] += gamer[name]['Type']
                            
                            
                    ## Move one case diagonally to the left up
                    elif move_line == - 1 and move_column == - 1 :
                        ## Delete from the old case 
                        delete = 0 
                        case = board[place[0]- 1][place[1]-1]
                        for i in range (len(case)):
                            if delete == 0:
                                if case[i] == gamer[name]['Type']:
                                    case[i] = ''
                                    delete += 1
                                    
                        ## Add the space machine on his new case
                        place[0] -= 1 
                        place[1] -= 1
                        board[place[0]- 1][place[1]-1] += gamer[name]['Type']
                            
                
                    ## Move one case diagonally to the right up
                    elif move_line == - 1 and move_column == 1 :
                        ## Delete from the old case 
                        delete = 0 
                        case = board[place[0]- 1][place[1]-1]
                        for i in range (len(case)):
                            if delete == 0:
                                if case[i] == gamer[name]['Type']:
                                    case[i] = ''
                                    delete += 1
                                    
                        ## Add the space machine on his new case
                        place[0] -= 1
                        place[1] += 1
                        board[place[0]- 1][place[1]-1] += gamer[name]['Type']
                    
                    else : 
                        None                     
        
    return (gamer,board)
    

def list_attack(gamer, name, line, column, assault):
    """ This function is used to list all the attacks in a data structure.
    
    Parameters
    ----------
    gamer: The data structure of the gamer (dictionnary)
    name: The name of the vessel who wants to attack (str)
    line: The line position of the case that the vessel wants to attack (int)
    column: The column of the case that the vessel wants to attack (int)
    assault: The data structure in wich the attacks are listed (list)
    
    Return
    ------
    assault: The data structure in wich the attacks are listed (list)
    
    Version
    -------
    Specification: Coline Verhoeven / Lana Silvagni (v.1 02/03/18)
    Specification: Coline Verhoeven / Lana Silvagni (v.2 13/04/18)
    Implementation: Coline Verhoeven / Lana Silvagni (v.1 10/04/18)
    """
    
    ## Check if the sapce machine is a warship or a scout
    if gamer[name]['Type'] == 'v' or gamer[name]['Type'] == 'w':
        if gamer[name]['Life'] > 0:
            ## Take the number of damage that he inflicts  
            damage = gamer[name]['Attack']
            
            ## Compute of the reach
            departure = gamer[name]['Centre']
            if (abs(int(line) - departure[0]) + abs(int(column) - departure[1])) <= gamer[name]['Reach']:
                ##The attack is added to the data structure 
                assault.append({'Damage' : damage, 'Position': [int(line), int(column)]})    
    return assault
        

def attack(assault, gamer_A, gamer_B, board, gate_A, gate_B):
    """ This function is used to attack space_machines or a gate.
    
    Parameters
    ----------
    assault: The data structure of the attacks (list)
    gamer_A: The data structure of the gamer A (dictionnary)
    gamer_B: The data structure of the gamer B (dictionnary)
    board: The data structure of the board (list)
    gate_A: The data structure of the gate A (dictionnary)
    gate_B: The data structure of the gate B (dictionnary)
    
    Return
    ------
    gamer_A: The data structure of the gamer A (dictionnary)
    gamer_B: The data structure of the gamer B (dictionnary)
    board: The data structure of the board (list)
    gate_A: The data structure of the gate A (dictionnary)
    gate_B: The data structure of the gate B (dictionnary)
  
    Version
    -------
    Specification: Coline Verhoeven / Lana Silvagni (v.1 26/02/18)
    Specification: Lana Silvagni / Camille Paindaveine (v.2 13/04/18)
    Implementation: Coline Verhoeven / Lana Silvagni (v.1 29/03/18)
    Implementation: Coline Verhoeven / Lana Silvagni (v.2 10/04/18)
    """
    for attack in range (len(assault)):
        for ship in gamer_A:
            if assault[attack]['Position'] == gamer_A[ship]['Centre']:
                gamer_A[ship]['Life'] -= assault[attack]['Damage']
                
            for place in gamer_A[ship]['Position']:
                if place == assault[attack]['Position']:
                    gamer_A[ship]['Life'] -= assault[attack]['Damage']
                    
            ##Put their lifes to dead if their are under or equal to 0           
            if gamer_A[ship]['Life'] <= 0:
                gamer_A[ship]['Life'] = 0
                print (ship, 'is dead')
                    
                ## Cancellation of the centre of the space machine
                center = board[gamer_A[ship]['Centre'][0]- 1][gamer_A[ship]['Centre'][1]-1]
                delete_center = 0
                for element in range (len(center)):
                    if delete_center == 0:
                        if center[element] == gamer_A[ship]['Type']:
                            center[element] = ''
                            delete_center += 1
                        
                ## Cancellation of the cases of the space machine
                for place in gamer_A[ship]['Position']:
                    case = board[place[0]- 1][place[1]-1]
                    delete = 0
                    for element in range (len(case)):
                        if delete == 0:
                            if case[element] == gamer_A[ship]['Type']:
                                case[element] = ''
                                delete += 1
                    
        for ship in gamer_B:
            if assault[attack]['Position'] == gamer_B[ship]['Centre']:
                gamer_B[ship]['Life'] -= assault[attack]['Damage']
                
            for place in gamer_B[ship]['Position']:
                if place == assault[attack]['Position']:
                    gamer_B[ship]['Life'] -= assault[attack]['Damage']
                    
         ##Put their lifes to dead if their are under or equal to 0
            if gamer_B[ship]['Life'] <= 0:
                gamer_B[ship]['Life'] = 0
                print (ship, 'is dead')
                    
                ## Cancellation of the centre of the space machine
                center = board[gamer_B[ship]['Centre'][0]- 1][gamer_B[ship]['Centre'][1]-1]
                delete_center = 0
                for element in range (len(center)):
                    if delete_center == 0:
                        if center[element] == gamer_B[ship]['Type']:
                            center[element] = ''
                            delete_center += 1
                        
                ## Cancellation of the cases of the space machine
                for place in gamer_B[ship]['Position']:    
                    case = board[place[0]- 1][place[1]-1]
                    delete = 0
                    for element in range (len(case)):
                        if delete == 0:
                            if case[element] == gamer_B[ship]['Type']:
                                case[element] = ''
                                delete += 1
                                
        if assault[attack]['Position'] == gate_A['Centre']:
            gate_A['Life'] -= assault[attack]['Damage']
            
        for place in gate_A['Position']:
            if assault[attack]['Position'] == place:
               gate_A['Life'] -= assault[attack]['Damage']
               
        if assault[attack]['Position'] == gate_B['Centre']:
            gate_B['Life'] -= assault[attack]['Damage']
            
        for place in gate_B['Position']:
            if assault[attack]['Position'] == place:
               gate_B['Life'] -= assault[attack]['Damage']
    return (gate_A,gate_B,gamer_A,gamer_B,board)


    
def compute_ore(asteroides, gamer_A, gamer_B, aste, crop):
    """ This function computes the number of ore each player if there are several excavators on that case.
    
    Parameters
    ----------
    asteroides: The data structure of the asteroides (dictionnary)
    gamer_A: The data structure of the gamer A (dictionnary)
    gamer_B: The data structure of the gamer B (dictionnary)
    aste: The position of the asteroid and excavators (list)
    crop: The data structure of excavators which are on the asteroid (dictionnary) 
    
    Return
    ------
    asteroides: The data structure of the asteroides (dictionnary)
    gamer_A: The data structure of the gamer A (dictionnary)
    gamer_B: The data structure of the gamer B (dictionnary)
    crop: The data structure of excavators which are on the asteroid (dictionnary)
    
    Version
    -------
    Specification: Lana Silvagni (v.1 26/02/18)
    Specification: Lana Silvagni (v.2 13/04/18)
    Implementation: Lana Silvagni / Coline Verhoeven (v.1 13/04/18)
    Implementation: Lana Silvagni / Coline Verhoeven (v.2 16/04/18)
    """

    possibility = copy.deepcopy(asteroides[aste]['Possibility'])

    ## If there are enough ore for each excavator in function of the possibility of the asteroid  
    if asteroides[aste]['Ore'] >= (asteroides[aste]['Possibility'] * len(crop)):
        
        ## Compute if all the excavators can have the possibility
        count = 0
        for w in crop:
            means = crop[w]['Tonnage'] - crop[w]['Capacity']
            
            if means < possibility:
                count += 1

            else: 
                None 
        ## If all the excavators can take the possibility
        if count == 0:
            for t in crop:
                crop[t]['Capacity'] += asteroides[aste]['Possibility']
                asteroides[aste]['Ore'] -= asteroides[aste]['Possibility']
                
        ## If all the excavators can't take the possibility
        else: 
            ## Initialization of the key 'Means' for each excavator
            for f in crop:
                crop[f]['Means'] = (crop[f]['Tonnage'] - crop[f]['Capacity'])
                
            while possibility > 0 :
                ## Research the smallest 'Means' and Check if all the excavators are not full
                departure_means = 1
                calculate = 0
                for n in crop:
                    if crop[n]['Means'] > 0 :
                        if departure_means > crop[n]['Means']:
                            departure_means = crop[n]['Means']
                            
                    elif crop[n]['Means'] == 0:
                        calculate +=1 
                        
                ## If all the excavators are full         
                if calculate == len(crop):
                    possibility = 0
                
                ## If there are still some not full excavators
                else:
                    for a in crop:
                        if crop[a]['Means'] >= departure_means:
                            crop[a]['Capacity'] += departure_means
                            crop[a]['Means'] -= departure_means
                    possibility -= departure_means
                        
    ## If there aren't enough ore for each excavator in function of the possibility of the asteroid                        
    elif asteroides[aste]['Ore'] < (asteroides[aste]['Possibility'] * len(crop)):
        
        ore = copy.deepcopy(asteroides[aste]['Ore'])
        
        while ore > .000001 and possibility > 0:
            
            ## Compute the number of the excavators not full
            count = 0 
            for k in crop:
                
                crop[k]['Means'] = (crop[k]['Tonnage'] - crop[k]['Capacity'])
                
                if  crop[k]['Means'] > 0:
                    count += 1
                    
                else:
                    None
                
            ## All the excavators that are full        
            if count == 0:
                ore = 0
                possibility = 0
            ## The excavators that are not full
            else:
                part = ore / count
                
                ## If all the excavators that are not full can take the entire part
                for t in crop:
                    if crop [t]['Means'] >= part:
                        crop[t]['Capacity'] += part
                        asteroides[aste]['Ore'] -= part
                        ore -= part
                        
                
                    ## If some excavators can't take the entire part     
                    elif crop[t]['Means'] < part:

                        ## Research the smallest 'Means'     
                        starting_means = 3000
                        for r in crop:
                            if crop[r]['Means'] > 0 :
                               
                            	if starting_means > crop[r]['Means']:
                               		starting_means = crop[r]['Means']
            
                        if possibility >= starting_means:

                            for d in crop: 
                                
                                if crop[d]['Means'] >= starting_means:
                                    crop[d]['Capacity'] += starting_means
                                    ore -= starting_means
                                    asteroides[aste]['Ore'] -= starting_means
                            
                            possibility -= starting_means
                
                        elif possibility < starting_means:
                        
                            for u in crop: 
                                
                                if crop[u]['Means'] >= possibility:
                                    crop[u]['Capacity'] += possibility
                                    ore -= possibility
                                    asteroides[aste]['Ore'] -= possibility
                        
                            possibility = 0
                            ore = 0
                    
    ## Update the data structure of the two gamer                    
    for i in crop:
        for a in gamer_A:
            if a == i: 
                gamer_A[a]['Capacity'] = crop[i]['Capacity']
        
        for b in gamer_B:
            if b == i: 
                gamer_B[b]['Capacity'] = crop[i]['Capacity'] 
    
    
    return (crop,asteroides,gamer_A,gamer_B)

def harvest(asteroides, gamer_A, gamer_B, aste):
    """ This function is used to collect the ore on a asteroid if there is only one excavator on the asteroid.
    
    Parameters
    ----------
    asteroides: The data structure of the asteroides (dictionnary)
    gamer_A: The data structure of the gamer A (dictionnary)
    gamer_B: The data structure of the gamer B (dictionnary)
    aste: The name of the asteroid on which the player wants to harvest (tuple)
        
    Return
    ------
    asteroides: The data structure of the asteroides (dictionnary)
    gamer_A: The data structure of the gamer A (dictionnary)
    gamer_B: The data structure of the gamer B (dictionnary)
    
    Version
    -------
    Specification: Camille Paindaveine / Lana Silvagni (v.1 26/02/18)
    Specification: Coline Verhoeven / Lana Silvagni / Camille Paindaveine (v.2 13/04/18)
    Implementation: Coline Verhoeven / Lana Silvagni (v.1 29/03/18)
    """
    for ship in gamer_A:
        if gamer_A[ship]['Type'] == 's' or gamer_A[ship]['Type'] == 'm' or gamer_A[ship]['Type'] == 'l':
            means = gamer_A[ship]['Tonnage'] - gamer_A[ship]['Capacity']
            ## There are enough ore on the asteroid for the mean of the ship
            if asteroides[aste]['Ore'] >= means:
                ## If the asteroid can give the same or a bigger quantity than the mean  
                if asteroides[aste]['Possibility'] >= means:
                    gamer_A[ship]['Capacity'] += means
                    asteroides[aste]['Ore']  -= means
                    
                elif asteroides[aste]['Possibility'] < means:
                    gamer_A[ship]['Capacity'] += asteroides[aste]['Possibility']
                    asteroides[aste]['Ore']  -= asteroides[aste]['Possibility']
            
            elif asteroides[aste]['Ore'] < means:
                if asteroides[aste]['Possibility'] >= asteroides[aste]['Ore']:
                    gamer_A[ship]['Capacity'] += asteroides[aste]['Ore']
                    asteroides[aste]['Ore']  = 0
                    
                elif asteroides[aste]['Possibility'] < asteroides[aste]['Ore']:
                    gamer_A[ship]['Capacity'] += asteroides[aste]['Possibility']
                    asteroides[aste]['Ore']  -= asteroides[aste]['Possibility']
                    
    for ship in gamer_B:
        if gamer_B[ship]['Type'] == 's' or gamer_B[ship]['Type'] == 'm' or gamer_B[ship]['Type'] == 'l':
            means = gamer_B[ship]['Tonnage'] - gamer_B[ship]['Capacity']
            ## There are enough ore on the asteroid for the mean of the ship
            if asteroides[aste]['Ore'] >= means:
                ## If the asteroid can give the same or a bigger quantity than the mean  
                if asteroides[aste]['Possibility'] >= means:
                    gamer_B[ship]['Capacity'] += means
                    asteroides[aste]['Ore']  -= means
                    
                elif asteroides[aste]['Possibility'] < means:
                    gamer_B[ship]['Capacity'] += asteroides[aste]['Possibility']
                    asteroides[aste]['Ore']  -= asteroides[aste]['Possibility']
            
            elif asteroides[aste]['Ore'] < means:
                if asteroides[aste]['Possibility'] >= asteroides[aste]['Ore']:
                    gamer_B[ship]['Capacity'] += asteroides[aste]['Ore']
                    asteroides[aste]['Ore']  = 0
                    
                elif asteroides[aste]['Possibility'] < asteroides[aste]['Ore']:
                    gamer_B[ship]['Capacity'] += asteroides[aste]['Possibility']
                    asteroides[aste]['Ore']  -= asteroides[aste]['Possibility']
                    
    return (asteroides, gamer_A,gamer_B)
    
def case_colonizer(asteroides,gamer_A,gamer_B):
    """ This function computes the number of excavators on an asteroid.
    
    Parameters
    ----------
    asteroides: The data structure of the asteroids (dictionnary)
    gamer_A: The data structure of the gamer A (dictionnary)
    gamer_B: The data structure of the gamer B (dictionnary)
    
    See also:
    ---------
    harvest: This function is used to collect the ore on a asteroid if there is only one excavator on the asteroid.
    compute_ore: This function computes the number of ore each player can have if there are several excavators on that case.
    
    Return
    ------
    asteroides: The data structure of the asteroids (dictionnary)
    gamer_A: The data structure of the gamer A (dictionnary)
    gamer_B: The data structure of the gamer B (dictionnary)
    
    Version
    -------
    Specifiaction: Coline Verhoeven / Lana Silvagni (v.1 13/04/18)
    Specifiaction: Coline Verhoeven / Lana Silvagni (v.2 15/04/18)
    Implementation: Coline Verhoeven / Lana Silvagni (v.1 13/04/18)
    """
    
    for e in asteroides:
        n = 0
        crop = {}
        for a in gamer_A:
            if asteroides[e]['Position'] == gamer_A[a]['Centre']:
                if gamer_A[a]['Life'] > 0:
                    if gamer_A[a]['State'] == 1: 
                        n += 1
                        crop[a] = {'Capacity' : gamer_A[a]['Capacity'], 'Tonnage': gamer_A[a]['Tonnage'], 'Type':gamer_A[a]['Type'] }
                        
        for b in gamer_B:
            if asteroides[e]['Position'] == gamer_B[b]['Centre']:
                if gamer_B[b]['Life'] > 0:
                    if gamer_B[b]['State'] == 1: 
                        n += 1 
                        crop[b] = {'Capacity' : gamer_B[b]['Capacity'], 'Tonnage': gamer_B[b]['Tonnage'], 'Type':gamer_B[b]['Type'] }
        
        if n == 1:
            asteroides, gamer_A, gamer_B = harvest(asteroides, gamer_A, gamer_B, e)
            
            
        
        elif n > 1:
            crop, asteroides, gamer_A, gamer_B = compute_ore(asteroides, gamer_A, gamer_B, e, crop)
            
                    
    return (gamer_A, gamer_B, asteroides)

            
            
def unloading (gate_A, gate_B, gamer_A, gamer_B):
    """ This function unloads the ore of the excavator on the gate of the player.
    
    Parameters
    ----------
    gate_A: The data structure of the player A (dictionnary)
    gate_B: The data structure of the player B (dictionnary)
    gamer_A: The data structure of the player A (dictionnary)
    gamer_B: The data structure of the player B (dictionnary)
    
    Return
    ------
    gate_A: The data structure of the player A (dictionnary)
    gate_B: The data structure of the player B (dictionnary)
    gamer_A: The data structure of the player A (dictionnary)
    gamer_B: The data structure of the player B (dictionnary)
    
    Version
    -------
    Specification: Lana Silvagni / Coline Verhoeven / Camille Paindaveine (v.1 13/04/18)
    Implementation : Coline Verhoeven / Lana Silvagni (v.1 13/04/18)
    """
    
    for a in gamer_A:
        if gamer_A[a]['Type'] == 's' or gamer_A[a]['Type'] == 'm' or gamer_A[a]['Type'] == 'l': 
            if gamer_A[a]['Life'] > 0:  
                if gamer_A[a]['Centre'] == gate_A['Centre']:
                    if gamer_A[a]['State'] == 1:
                        gate_A['Ore'] += gamer_A[a]['Capacity']
                        gamer_A[a]['Capacity'] = 0
            else: 
                None
                    
                
    for b in gamer_B:
        if gamer_B[b]['Type'] == 's' or gamer_B[b]['Type'] == 'm' or gamer_B[b]['Type'] == 'l':
            if gamer_B[b]['Life'] > 0:
                if gamer_B[b]['Centre'] == gate_B['Centre']:
                    if gamer_B[b]['State'] == 1:
                        gate_B['Ore'] += gamer_B[b]['Capacity']
                        gamer_B[b]['Capacity'] = 0
            else:
                None
                
                
                
    return (gate_A,gate_B,gamer_A,gamer_B)



def not_game_over(gate_A, gate_B, gamer_A, gamer_B, turn_without_damage, starting, ending):
    """ This function is used when the game is finished. It could be if one of a gate has no more life's point or when 20 laps have been done without any damage.
    
    Parameters
    ----------
    gate_A: The data structure of the gate A (dictionnary)
    gate_B: The data structure of the gate B (dictionnary)
    gamer_A: The data structure of the gamer A (dictionnary)
    gamer_B: The data structure of the gamer B (dictionnary)
    turn: The number of turns without damage (int)
    starting: The data structure of the life of two players before the attacks (dictionnary) 
    ending: The data structure of the life of two players after the attacks (dictionnary)
    
    Return
    ------
    turn: The number of turns without damage (int)
        
    Version
    -------
    Specification: Coline Verhoven / Lana Silvagni (v.1 28/02/18).
    Specification: Lana Silvagni (v.2 15/04/18).
    Implementation: Coline Verhoven / Lana Silvagni (v.1 29/03/18).
    Implementation: Coline Verhoven / Lana Silvagni (v.2 13/04/18).
    """
    
    control = 0
    if gate_A['Life'] <= 0 and gate_B['Life'] > 0:
        print('Player B wins')
        control = 1
        
    elif gate_A['Life'] > 0 and gate_A['Life'] <= 0:
        print('Player A wins')
        control = 1
        
    elif gate_A['Life'] <= 0 and gate_A['Life'] <= 0:
        print('Draw')
        control = 1

                
    verification = 0                         
    for a in starting: 
        for o in ending:
            if a == o: 
                if starting[a]['Life'] > ending[o]['Life']:
                    verification += 1
                
                          
    if verification == 0:
        turn_without_damage = turn_without_damage + 1
        
    elif verification > 0:
        turn_without_damage = 0
        
    if turn_without_damage > 200:
        if gate_A['Life'] > gate_B['Life']:
            print ('Player A wins')
            control = 1
            
        elif gate_A['Life'] < gate_B['Life']:
            print ('Player B wins')
            control = 1
            
        elif gate_A['Life'] == gate_B['Life']:
            
            if gate_A['Ore'] > gate_B['Ore']:
                print('Player A wins')
                control = 1
                
            elif gate_A['Ore'] < gate_B['Ore']:
                print('Player B wins')
                control = 1
                
            else:
                print('Game over for you all') 
                control = 1       
                
                   
    if control == 0:
        return (True, turn_without_damage)
         
    elif control == 1:
        return (False, turn_without_damage) 

    
    
def display(gamer_A, gamer_B, board, gate_A, gate_B, asteroides):
    """ This function is used to print the board at the end of a turn onwich there could have be some changes.

    Parameters
    ----------
    gamer_A: The data structure of the player A (dictionnary).    
    gamer_B: The data structure of the player B (dictionnary).
    board: The data structure of the board (list).
    
    Version
    -------
    Specifiaction: Lana Silvagni (v.1 03/03/18)
    Implementation: Coline Verhoeven (v.1 10/04/18)
    Implementation: Coline Verhoeven (v.2 15/04/18)
    """ 
    
    reset = attr('reset')
    for line in range (len(board)):
        tray  = ''
        
        for column in range(len(board[line])):
            
            if len (board[line][column]) <= 1:
                if board[line][column] == [] or board[line][column] == [''] :
                    tray += '[ ]'
                    
                elif board[line][column] == ['v']:
                    tray += '[v]'
                    
                elif board[line][column] == ['l']:
                    tray += bg('green')+ '[ ]'+ reset
                    
                
                elif board[line][column] == ['s']:
                    tray += bg('magenta')+ '[ ]'+ reset
                    
           	
                elif board[line][column] == ['m']:
                    tray += bg ('cyan')+ '[ ]'+ reset
                    
                    
                elif board[line][column] == ['w']:
                    tray += '[w]'
                    
                elif board[line][column] == ['*']:
                    tray += '[*]'
                
                elif board[line][column] == ['a']: 
                    tray += fg('magenta')+'[ ]'+ reset
                    
                    
                elif board[line][column] == ['b']:
                    
                    tray += fg('red')+'[ ]'+ reset
                    
            
            elif len(board[line][column]) > 1:
                
                case_vide = 0
                for element in board[line][column]:
                    if element != '':
                        case_vide = case_vide + 1
                
                if case_vide == 0:
                    tray += '[ ]'
                
                elif case_vide == 1:
                    for element in board[line][column]:
                        if element == 'v':
                            tray += '[v]'
                                
                        elif element == 'w':
                            tray += '[w]'
                                
                        elif element == 'l':
                            tray += bg('green') + '[ ]'+ reset
                            
                        elif element == 'm':
                            tray += bg('cyan') + '[ ]'+ reset
                                
                        elif element == 's':
                            tray += bg('magenta') + '[ ]'+ reset 
                            
                        elif element == 'a': 
                            tray += fg('magenta')+'[ ]'+ reset
                    
                        elif element == 'b':
                            tray += fg('red')+'[ ]'+ reset
                            
                        elif element == '*':
                            tray += '[*]'
                            
                elif case_vide == 2:
                    gate = 0 
                    for element in board[line][column]: 
                        if element == 'a': 
                            gate = 1
                            
                        elif element == 'b':
                            gate = 2
                    
                    if gate == 0:        
                        tray += '[§]'
                    
                    elif gate == 1:
                        for element in board[line][column]:
                            if element == 'v':
                                tray += fg('magenta')+'['+ reset + 'v' +  fg('magenta') + ']'+ reset
                                    
                            elif element == 'w':
                                tray += fg('magenta')+'['+ reset + 'w' +  fg('magenta') + ']'+ reset
                                    
                            elif element == 'l':
                                tray += bg('green') + fg('magenta')+'[ ]'+ reset 
                                
                            elif element == 'm':
                                tray += bg('cyan') + fg('magenta')+'[ ]'+ reset 
                                
                            elif element == 's':
                                tray += bg('magenta') + fg('magenta')+'[ ]'+ reset 
                                
                            elif element == '*':
                                tray += '[*]'
                            
                        
                    elif gate == 2:
                        for element in board[line][column]:
                            if element == 'v':
                                tray += fg('red')+'['+ reset + 'v' +  fg('red') + ']'+ reset
                                    
                            elif element == 'w':
                                tray += fg('red')+'['+ reset + 'w' +  fg('red') + ']'+ reset
                                    
                            elif element  == 'l':
                                tray += bg('green') + fg('red')+'[ ]' + reset
                                
                            elif element == 'm':
                                tray += bg('cyan') + fg('red')+'[ ]'+ reset 
                                    
                            elif element == 's':
                                tray += bg('magenta') + fg('red')+'[ ]'+ reset 
                            
                            elif element == '*':
                                tray += '[*]'
                
                elif case_vide > 2:
                    gate = 0 
                    for element in board[line][column]: 
                        if element == 'a': 
                            gate = 1
                            
                        elif element == 'b':
                            gate = 2
                            
                    if gate == 0:
                        tray += '[§]'
                        
                    elif gate == 1:
                        tray += fg('magenta')+'['+ reset + '§' +  fg('magenta') + ']'+ reset
                        
                    elif gate == 2:
                        tray += fg('red')+'['+ reset + '§' +  fg('red') + ']'+ reset
                                        
                    
                
        print (tray)
    print ('The asteroides : ', asteroides)
    print (' ')
    print (' ')
    print ('Gate A : ', gate_A)
    print (' ')
    print ('Space machine A : ', gamer_A)
    print (' ')
    print (' ')
    print ('Gate B : ', gate_B)
    print (' ')
    print ('Space machine B', gamer_B)
    print (' ')
    print (' ')
    
def choose_name ():
    """ This function creates randomly a name for a new starship
    Return
    ------
    name: The variable of the created name
        
    Version
    -------
    Specifiaction: Coline Verhoeven / Lana Silvagni / Camille Paindaveine (v.1 04/05/18)
    Implementation: Coline Verhoeven / Lana Silvagni / Camille Paindaveine (v.1 04/05/18)  
    """
    caracteres = "azertyuiopqsdfghjklmwxcvbn" 
    length = 5 
    name = '' 
    count = 0 
 
    while count < length:
        letter = caracteres[random.randint(0, len(caracteres)-1)] 
        name += letter 
        count += 1
        
    return name
def IA(me, you, my_gate, your_gate, asteroides, turn_without_damage, turn, last_choice_rival):
    """ This function is the artificial intelligence of the game 
    
    Parameters
    ----------
    me: My data structure (dictionnary)
    you: Your data structure (dictionnary)
    my_gate: My data structure (dictionnary)
    your_gate: Your date structure (dictionnary)
    asteroides: The data structure of the asteroids (dictionnary)
    turn_without_damage: The variable that counts the number of the turns without damage
    turn: The variable that counts the number of the turns
    last_choice_rival: The last decision of the rival
        
    Returns
    --------
    order: The decisions of our IA
        
    Version
    -------
    Specifiaction: Coline Verhoeven / Lana Silvagni / Camille Paindaveine (v.1 04/05/18)
    Implementation: Coline Verhoeven / Lana Silvagni / Camille Paindaveine (v.1 04/05/18)    
    """
    
    order = []
    
    
## Purchase

    if turn == 0 and my_gate['Ore'] == 4:
        name_1 = choose_name()
        name_2 = choose_name()
        order.append('%s:excavator-M'%name_1)
        order.append('%s:excavator-M'%name_2)
    
    number_excavator_m = 0
    number_scout = 0 
    number_warship = 0    
    for ship in me:
        if me[ship]['Type'] == 'm':
            number_excavator_m += 1
            
        elif  me[ship]['Type'] == 'v':
            number_scout += 1
            
        elif me[ship]['Type'] == 'w':
            number_warship += 1
        
    if number_excavator_m == 2 and number_scout == 1 and my_gate['Ore'] >= 9:
        name = choose_name()
        order.append('%s:warship'%name)
    
    elif number_excavator_m == 2 and number_scout == 0 and my_gate['Ore'] >= 3:
        name = choose_name()
        order.append('%s:scout'%name)
        
    elif number_excavator_m >= 2 and number_scout >= 1 and number_warship >= 1:
        
        if last_choice_rival == '':
            None
        
        
        else:
            decision_rival = last_choice_rival.split(' ') 
            for i in range (len(decision_rival)):
                if decision_rival != '':
                    actions = decision_rival[i].split(':')
                    command_rival = actions[1] 
                    
                    ##If the rival buys a scout 
                    if command_rival == 'scout':
                        if my_gate['Ore'] >= 3:
                            name = choose_name()
                            order.append('%s:scout'%name)
                            
                        elif  my_gate['Ore'] < 3:
                            name = choose_name()
                            order.append('%s:excavator-M'%name)
                            
                        elif my_gate['Ore'] < 2:
                            name = choose_name()
                            order.append('%s:excavator-S'%name)
                            
                        else: None
                    ##If the rival buys a warship        
                    elif command_rival == 'warship':
                        if my_gate['Ore'] >= 9:
                            name = choose_name()
                            order.append('%s:warship'%name)
                        
                        elif  my_gate['Ore'] < 9:
                            name = choose_name()
                            order.append('%s:excavator-L'%name)
                            
                        elif my_gate['Ore'] < 4:
                            name = choose_name()
                            order.append('%s:scout'%name)
                            
                        elif  my_gate['Ore'] < 3:
                            name = choose_name()
                            order.append('%s:excavator-M'%name)
                            
                        elif my_gate['Ore'] < 2:
                            name = choose_name()
                            order.append('%s:excavator-S'%name)
                            
                        else: None    
                        
                    ##If the rival buys a excavator M        
                    elif command_rival == 'excavator-M':
                        if my_gate['Ore'] >= 2:
                            name = choose_name()
                            order.append('%s:excavator-M'%name)
                            
                        elif my_gate['Ore'] < 2:
                            name = choose_name()
                            order.append('%s:excavator-S'%name)
                            
                        else : None
                            
                    ##If the rival buys a excavator L        
                    elif command_rival == 'excavator-L':
                        if my_gate['Ore'] >= 4:
                            name = choose_name()
                            order.append('%s:excavator-L'%name)
                            
                        elif my_gate['Ore'] < 4:
                            name = choose_name()
                            order.append('%s:scout'%name)
                            
                        elif  my_gate['Ore'] < 3:
                            name = choose_name()
                            order.append('%s:excavator-M'%name)
                            
                        elif my_gate['Ore'] < 2:
                            name = choose_name()
                            order.append('%s:excavator-S'%name)
                            
                        else: None    
                            
                    ##If the rival buys a excavator S        
                    elif command_rival == 'excavator-S':
                        if my_gate['Ore'] >= 1:
                            name = choose_name()
                            order.append('%s:excavator-S'%name)
                        
                        else: None
                        
                    else:
                        None 
                        
    ##If all the excavator are death
    if turn > 0:
        excavator_alive = 0
        for ship in me:
            if me[ship]['Type'] == 's' or me[ship]['Type'] == 'm' or me[ship]['Type'] == 'l':
                    ##If all the excavator are death
                if me[ship]['Life'] > 0: 
                    excavator_alive += 1
                    
                else: 
                    None
                    
        if excavator_alive == 0:  
            if my_gate['Ore'] >= 4:
                name = choose_name()
                order.append('%s:excavator-L'%name) 
                
        elif my_gate['Ore'] >= 2:
            name = choose_name()
            order.append('%s:excavator-M'%name)
                
        elif my_gate['Ore'] >= 1:
            name = choose_name()
            order.append('%s:excavator-S'%name)
                    
        ##If all our ships are dead
        all_in_life = 0
        for ship in me:
            if me[ship]['Life'] > 0:
                all_in_life += 1
            else : None
                
            if all_in_life == 0:
                if my_gate['Ore'] >= 9:
                    name = choose_name()
                    order.append('%s:warship'%name)
                    
                elif my_gate['Ore'] >= 4:
                    name = choose_name()
                    order.append('%s:excavator-L'%name)
                    
                elif my_gate['Ore'] >= 3:
                    name = choose_name()
                    order.append('%s:scout'%name)
                        
                elif my_gate['Ore'] >= 2:
                    name = choose_name()
                    order.append('%s:excavator-M'%name)
                        
                elif my_gate['Ore'] >= 1:
                    name = choose_name()
                    order.append('%s:excavator-S'%name)
            
    ## Lock / Unlock / Shifting / Attack
    number_attack = 0
    number_shifting = 0
    for ship in me:
        if me[ship]['Life'] > 0:
            ## Excavator
            if me[ship]['Type'] == 's' or me[ship]['Type'] == 'm' or me[ship]['Type'] == 'l':
                
                ## Locked
                if me[ship]['State'] == 1:
                    
                    ## On the gate
                    if me[ship]['Centre'] == my_gate['Centre']:
                        if me[ship]['Capacity'] == 0:
                            order.append('%s:release'%ship)
                            
                    ## On the asteroids
                    else:
                        for aste in asteroides:
                            if me[ship]['Centre'] == asteroides[aste]['Position']:
                                if me[ship]['Capacity'] == me[ship]['Tonnage'] or asteroides[aste]['Ore'] <= 0 or me[ship]['Capacity'] == (me[ship]['Tonnage']-1):  
                                    order.append('%s:release'%ship)
                                    
                                    
                ##Unlocked                    
                elif me[ship]['State'] == 0:
                    
                    ## On the asteroids
                    for aste in asteroides:
                        if me[ship]['Centre'] == asteroides[aste]['Position']:
                            if me[ship]['Capacity'] < me[ship]['Tonnage'] and asteroides[aste]['Ore'] > 0:
                                order.append('%s:lock'%ship)
                    ## On the gate
                    if me[ship]['Centre'] == my_gate['Centre']:
                        ## If it has something
                        if me[ship]['Capacity'] > 0:
                            order.append('%s:lock'%ship)
                            
                    
                                    
                    ## On the board (shifting)
                    minimum = 800
                    name = ''
                    for aste in asteroides:
                        distance = (abs(int(me[ship]['Centre'][0]) - int(asteroides[aste]['Position'][0]))) + (abs(int(me[ship]['Centre'][1]) - int(asteroides[aste]['Position'][1])))
                        if asteroides[aste]['Ore'] > 0:
                            if distance < minimum:
                                minimum = distance
                                name = copy.deepcopy(asteroides[aste]['Position'])
                            
                        else:
                            None
                    number_shifting = 0       
                    if me[ship]['Capacity'] < me[ship]['Tonnage']:
                        not_empty = 0
                        for aste in asteroides:
                            if asteroides[aste]['Ore'] > 0:
                                not_empty += 1 
                            else: None
                            
                        if not_empty == 0:
                            if number_shifting == 0: 
                                moving_line = int(my_gate['Centre'][0]) - int(me[ship]['Centre'][0])
                                moving_column = int(my_gate['Centre'][1]) - int(me[ship]['Centre'][1])
                                line = int(copy.deepcopy(me[ship]['Centre'][0]))
                                column = int(copy.deepcopy(me[ship]['Centre'][1]))
                                    
                                if moving_line < 0 and moving_column < 0:
                                    line -= 1
                                    column -= 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                        
                                elif moving_line < 0 and moving_column == 0:
                                    line -= 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                        
                                elif moving_line < 0 and moving_column > 0:
                                    line -= 1
                                    column += 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                    
                                elif moving_line == 0 and moving_column > 0:
                                    column += 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                        
                                elif moving_line > 0 and moving_column > 0:
                                    line += 1
                                    column += 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                
                                elif moving_line > 0 and moving_column == 0:
                                    line += 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                        
                                elif moving_line > 0 and moving_column < 0:
                                    line += 1
                                    column -= 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                    
                                elif moving_line == 0 and moving_column < 0:
                                    column -= 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                
                        for aste in asteroides:
                            if number_shifting == 0:
                                if name == asteroides[aste]['Position']:
                                    way_line = asteroides[aste]['Position'][0] - me[ship]['Centre'][0]
                                    way_column = asteroides[aste]['Position'][1] - me[ship]['Centre'][1]
                                    line = copy.deepcopy(me[ship]['Centre'][0])
                                    column = copy.deepcopy(me[ship]['Centre'][1])
                                    
                                    if way_line < 0 and way_column < 0:
                                        line -= 1
                                        column -= 1
                                        order.append('%s:@%d-%d'%(ship, line, column))
                                        number_shifting = 1
                                        
                                    elif way_line < 0 and way_column == 0:
                                        line -= 1
                                        order.append('%s:@%d-%d'%(ship, line, column))
                                        number_shifting = 1
                                        
                                    elif way_line < 0 and way_column > 0:
                                        line -= 1
                                        column += 1
                                        order.append('%s:@%d-%d'%(ship, line, column))
                                        number_shifting = 1
                                    
                                    elif way_line == 0 and way_column > 0:
                                        column += 1
                                        order.append('%s:@%d-%d'%(ship, line, column))
                                        number_shifting = 1
                                        
                                    elif way_line > 0 and way_column > 0:
                                        line += 1
                                        column += 1
                                        order.append('%s:@%d-%d'%(ship, line, column))
                                        number_shifting = 1
                                    
                                    elif way_line > 0 and way_column == 0:
                                        line += 1
                                        order.append('%s:@%d-%d'%(ship, line, column))
                                        number_shifting = 1
                                        
                                    elif way_line > 0 and way_column < 0:
                                        line += 1
                                        column -= 1
                                        order.append('%s:@%d-%d'%(ship, line, column))
                                        number_shifting = 1
                                    
                                    elif way_line == 0 and way_column < 0:
                                        column -= 1
                                        order.append('%s:@%d-%d'%(ship, line, column))
                                        number_shifting = 1
                                    
                    if me[ship]['Capacity'] == me[ship]['Tonnage']:
                        if number_shifting == 0: 
                            moving_line = int(my_gate['Centre'][0]) - int(me[ship]['Centre'][0])
                            moving_column = int(my_gate['Centre'][1]) - int(me[ship]['Centre'][1])
                            line = int(copy.deepcopy(me[ship]['Centre'][0]))
                            column = int(copy.deepcopy(me[ship]['Centre'][1]))
                                
                            if moving_line < 0 and moving_column < 0:
                                line -= 1
                                column -= 1
                                order.append('%s:@%d-%d'%(ship, line, column))
                                number_shifting = 1
                                    
                            elif moving_line < 0 and moving_column == 0:
                                line -= 1
                                order.append('%s:@%d-%d'%(ship, line, column))
                                number_shifting = 1
                                    
                            elif moving_line < 0 and moving_column > 0:
                                line -= 1
                                column += 1
                                order.append('%s:@%d-%d'%(ship, line, column))
                                number_shifting = 1
                                
                            elif moving_line == 0 and moving_column > 0:
                                column += 1
                                order.append('%s:@%d-%d'%(ship, line, column))
                                number_shifting = 1
                                    
                            elif moving_line > 0 and moving_column > 0:
                                line += 1
                                column += 1
                                order.append('%s:@%d-%d'%(ship, line, column))
                                number_shifting = 1
                            
                            elif moving_line > 0 and moving_column == 0:
                                line += 1
                                order.append('%s:@%d-%d'%(ship, line, column))
                                number_shifting = 1
                                    
                            elif moving_line > 0 and moving_column < 0:
                                line += 1
                                column -= 1
                                order.append('%s:@%d-%d'%(ship, line, column))
                                number_shifting = 1
                                
                            elif moving_line == 0 and moving_column < 0:
                                column -= 1
                                order.append('%s:@%d-%d'%(ship, line, column))
                                number_shifting = 1
                                
            ## Scout                       
            elif me[ship]['Type'] == 'v':
                
                ## Attack
                number_attack = 0
                ## Look if there are a starship in his reach
                for machine in you:
                    if number_attack == 0:
                        ##Centre
                        if you[machine]['Life'] > 0:
                            interval_centre = (abs(int(me[ship]['Centre'][0]) - int(you[machine]['Centre'][0])) + abs(int(me[ship]['Centre'][1]) - int(you[machine]['Centre'][1])))
                            if interval_centre ==  me[ship]['Reach']: 
                                target = you[machine]['Centre']
                                order.append('%s:*%d-%d'%(ship, int(target[0]), int(target[1])))
                                number_attack = 1
                            ## Other positions     
                            else:        
                                for place in you[machine]['Position']:
                                    if number_attack == 0:
                                        interval = (abs(int(me[ship]['Centre'][0]) - int(place[0])) + abs(int(me[ship]['Centre'][1]) - int(place[1])))
                                        if interval == me[ship]['Reach']:
                                            target = place
                                            order.append('%s:*%d-%d'%(ship, target[0], target[1]))
                                            number_attack = 1
                                    
                ## Shifting  
                name = ''             
                if number_attack == 0:
                    number_shifting = 0
                    minimum = 800
                    ##Research for the nearest ship 
                    for spacemachine in you:
                        distance = (abs(int(me[ship]['Centre'][0]) - int(you[spacemachine]['Centre'][0]))) + (abs(int(me[ship]['Centre'][1]) - int(you[spacemachine]['Centre'][1])))
                        if you[spacemachine]['Life'] > 0:
                            if distance < minimum:
                                minimum = distance
                                name = spacemachine
        
                    ##Research the ship in the data structure of the rival
                    for machine in you:
                        if number_shifting == 0:
                            if name == machine:
                                
                                ##Calculate the distance between the ship and the rival
                                way_line = int(you[machine]['Centre'][0]) - int(me[ship]['Centre'][0])
                                way_column = int(you[machine]['Centre'][1]) - int(me[ship]['Centre'][1])
                                line = int(copy.deepcopy(me[ship]['Centre'][0]))
                                column = int(copy.deepcopy(me[ship]['Centre'][1]))
                                
                                ##Shifting
                                if way_line < 0 and way_column < 0:
                                    line -= 1
                                    column -= 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                    
                                elif way_line < 0 and way_column == 0:
                                    line -= 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                    
                                elif way_line < 0 and way_column > 0:
                                    line -= 1
                                    column += 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                
                                elif way_line == 0 and way_column > 0:
                                    column += 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                    
                                elif way_line > 0 and way_column > 0:
                                    line += 1
                                    column += 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                
                                elif way_line > 0 and way_column == 0:
                                    line += 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                    
                                elif way_line > 0 and way_column < 0:
                                    line += 1
                                    column -= 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                
                                elif way_line == 0 and way_column < 0:
                                    column -= 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                    
                ##If all the vessels of the rival are dead
                vessels_alive = 0
                for vessel in you:
                    if you[vessel]['Life'] > 0:
                        vessels_alive += 1
                        
                    else: 
                        None
                        
                if vessels_alive == 0:
                    if number_attack == 0 and number_shifting == 0:
                        ##Look if the rival gate is in his reach
                        if number_attack == 0:
                            interval_centre_gate = (abs(int(me[ship]['Centre'][0]) - int(your_gate['Centre'][0])) + abs(int(me[ship]['Centre'][1]) - int(your_gate['Centre'][1])))
                            ##Centre
                            if interval_centre_gate == me[ship]['Reach']:
                                target = your_gate['Centre']
                                order.append('%s:*%d-%d'%(ship, int(target[0]), int(target[1])))
                                number_attack = 1
                            ##Other position        
                            else:
                                for position in your_gate['Position']:
                                    if number_attack == 0:
                                        interval_gate = (abs(int(me[ship]['Centre'][0]) - int(position[0])) + abs(int(me[ship]['Centre'][1]) - int(position[1])))
                                        if interval_gate == me[ship]['Reach']:
                                            target = position
                                            order.append('%s:*%d-%d'%(ship, int(target[0]), int(target[1])))
                                            number_attack = 1
                        
                        
                        if number_attack ==0:
                            if number_shifting == 0:
                                way_line = int(your_gate['Centre'][0]) - int(me[ship]['Centre'][0])
                                way_column = int(your_gate['Centre'][1]) - int(me[ship]['Centre'][1])
                                line = int(copy.deepcopy(me[ship]['Centre'][0]))
                                column = int(copy.deepcopy(me[ship]['Centre'][1]))
                                if way_line < 0 and way_column < 0:
                                    line -= 1
                                    column -= 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                                    
                                elif way_line < 0 and way_column == 0:
                                    line -= 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                                    
                                elif way_line < 0 and way_column > 0:
                                    line -= 1
                                    column += 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                                
                                elif way_line == 0 and way_column > 0:
                                    column += 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                                    
                                elif way_line > 0 and way_column > 0:
                                    line += 1
                                    column += 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                                
                                elif way_line > 0 and way_column == 0:
                                    line += 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                                    
                                elif way_line > 0 and way_column < 0:
                                    line += 1
                                    column -= 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                                
                                elif way_line == 0 and way_column < 0:
                                    column -= 1
                                    order.append('%s:@%d-%d'%(ship, line, column))
                                    number_shifting = 1
                                
                                    
            elif me[ship]['Type'] == 'w':
                
                ## Initialize the counting variables
                number_attack = 0
                number_shifting = 0
                
                ##Look if the rival gate is in his reach
                if number_attack == 0:
                    interval_centre_gate = (abs(int(me[ship]['Centre'][0]) - int(your_gate['Centre'][0])) + abs(int(me[ship]['Centre'][1]) - int(your_gate['Centre'][1])))
                    ##Centre
                    if interval_centre_gate == me[ship]['Reach']:
                        target = your_gate['Centre']
                        order.append('%s:*%d-%d'%(ship, int(target[0]), int(target[1])))
                        number_attack = 1
                    ##Other position        
                    else:
                        for position in your_gate['Position']:
                            if number_attack == 0:
                                interval_gate = (abs(int(me[ship]['Centre'][0]) - int(position[0])) + abs(int(me[ship]['Centre'][1]) - int(position[1])))
                                if interval_gate == me[ship]['Reach']:
                                    target = position
                                    order.append('%s:*%d-%d'%(ship, int(target[0]), int(target[1])))
                                    number_attack = 1
                
                
                if number_attack ==0:
                    if number_shifting == 0:
                        way_line = int(your_gate['Centre'][0]) - int(me[ship]['Centre'][0])
                        way_column = int(your_gate['Centre'][1]) - int(me[ship]['Centre'][1])
                        line = int(copy.deepcopy(me[ship]['Centre'][0]))
                        column = int(copy.deepcopy(me[ship]['Centre'][1]))
                        if way_line < 0 and way_column < 0:
                            line -= 1
                            column -= 1
                            order.append('%s:@%d-%d'%(ship, line, column))
                            number_shifting = 1
                                            
                        elif way_line < 0 and way_column == 0:
                            line -= 1
                            order.append('%s:@%d-%d'%(ship, line, column))
                            number_shifting = 1
                                            
                        elif way_line < 0 and way_column > 0:
                            line -= 1
                            column += 1
                            order.append('%s:@%d-%d'%(ship, line, column))
                            number_shifting = 1
                                        
                        elif way_line == 0 and way_column > 0:
                            column += 1
                            order.append('%s:@%d-%d'%(ship, line, column))
                            number_shifting = 1
                                            
                        elif way_line > 0 and way_column > 0:
                            line += 1
                            column += 1
                            order.append('%s:@%d-%d'%(ship, line, column))
                            number_shifting = 1
                                        
                        elif way_line > 0 and way_column == 0:
                            line += 1
                            order.append('%s:@%d-%d'%(ship, line, column))
                            number_shifting = 1
                                            
                        elif way_line > 0 and way_column < 0:
                            line += 1
                            column -= 1
                            order.append('%s:@%d-%d'%(ship, line, column))
                            number_shifting = 1
                                        
                        elif way_line == 0 and way_column < 0:
                            column -= 1
                            order.append('%s:@%d-%d'%(ship, line, column))
                            number_shifting = 1
                    

    ## Survival
    if number_attack == 0 and number_shifting == 0:
        if turn_without_damage == 199 :
            if my_gate['Ore'] <= your_gate ['Ore']:
                over = 0
                for ship in me:
                    if over == 0:
                        if me[ship]['Type'] == 'v' or me[ship]['Type'] == 'w':
                            line = me[ship]['Centre'][0]
                            column = me[ship]['Centre'][1]
                            order.append('%s:*%d-%d'%(ship, line, column))
                            over += 1
            else:
                None
           
    return ' '.join(order)
    
       
def start(card_txt, player_A,player_id,remote_IP):
    """ This function is the one that starts all the game.
    
    Parameters
    ----------
    card_txt: This is the file that will be used to create the board and it gives the size of the board (file).
    player_A: The type of player A that could be an AI or a physical person (str).
    player_B: The type of player B that could be an AI or a physical person (str).
    
    See also
    --------
    This function will contain all the functions of the game.
    
    Version
    -------
    Specification: Lana Silvagni (v.1 02/03/18)
    Specification: Lana Silvagni (v.2 28/03/18)
    Implementation: Coline Verhoeven (v.1 28/03/18)
    Implementation: Coline Verhoeven (v.2 15/04/18)
    """ 
    
    creation_board(card_txt)

    ## Data structures of the gamers 
    gamer_A = {}
    gamer_B = {}
    ## Initialization of the turns without damage 
    turn_without_damage = 0
    turn = 0
    starting = {}
    ending ={}
    gate_A = creation_board(card_txt)[1]
    gate_B = creation_board(card_txt)[2]
    board = creation_board(card_txt)[0]
    asteroides = creation_board(card_txt)[3] 
    size_board = creation_board(card_txt)[4]
    last_choice_rival_A = ''
    last_choice_rival_B = ''

    connection = remote_play.connect_to_player(player_id, remote_IP, True)


    while not_game_over(gate_A, gate_B, gamer_A, gamer_B, turn_without_damage, starting, ending)[0] == True:
       
        ## Initialization of the data structure of the list attack
        assault = []
        
        ## Choice of the player
        if player_A == 1:
            choice_A = IA(gamer_A, gamer_B, gate_A, gate_B, asteroides,turn_without_damage, turn, last_choice_rival_B)
            
            remote_play.notify_remote_orders(connection, choice_A)
            choice_B =  remote_play.get_remote_orders(connection)
            
   
        else:
            choice_A = remote_play.get_remote_orders(connection)
            
            choice_B = IA(gamer_B, gamer_A, gate_B, gate_A, asteroides,turn_without_damage, turn, last_choice_rival_A)
            remote_play.notify_remote_orders(connection, choice_B)
            
        
        ##Player A

        if choice_A == '':
            
            None
        else:    
            decision_A = choice_A.split(' ')
            for i in range (len(decision_A)):
                action = decision_A[i].split(':')
                command_A = action[1] 
                syntax_A = command_A[0]
                
                ## Purchase
                if command_A == 'scout' or command_A =='warship' or command_A =='excavator-S' or command_A =='excavator-M' or command_A =='excavator-L':
                    gate_A, gamer_A, board = shop(gamer_A, gate_A, action[0], command_A, board)
                    
                ## Lock
                elif action[1] == 'lock':
                    gamer_A = lock(gamer_A, action[0], asteroides, gate_A)
                    
                ## Unlock
                elif action[1] == 'release':
                    gamer_A = unlock(gamer_A, action[0]) 
                    
                ## Shifting
                elif syntax_A == '@':
                    position_A = command_A[1:].split('-')
                    gamer_A, board = shifting(gamer_A, board, action[0], position_A[0], position_A[1], size_board)
                    
                ## Project the attack
                elif syntax_A == '*':
                    position_A = command_A[1:].split('-')
                    assault = list_attack(gamer_A, action[0], position_A[0], position_A[1], assault)
                    
                else: 
                    None
                
                
            
        
        ## Player B
        if choice_B == '':
            None
        else:
            decision_B = choice_B.split(' ')

            for i in range (len(decision_B)):
                actions = decision_B[i].split(':')
                command_B = actions[1] 
                syntax_B = command_B[0] 
                
                ## Purchase
                if command_B == 'scout' or command_B =='warship' or command_B =='excavator-S' or command_B =='excavator-M' or command_B =='excavator-L':
                    gate_B, gamer_B, board = shop(gamer_B, gate_B, actions[0], command_B, board)
                    
                ## Lock
                elif actions[1] == 'lock':
                    gamer_B = lock(gamer_B, actions[0], asteroides, gate_B)
                    
                ## Unlock
                elif actions[1] == 'release':
                    gamer_B = unlock(gamer_B, actions[0])
                
                ## Shifting
                elif syntax_B == '@':
                    position_B = command_B[1:].split('-')
                    gamer_B, board = shifting(gamer_B, board, actions[0], position_B[0], position_B[1], size_board)
                    
                ## Project the attack
                elif syntax_B == '*':
                    position_B = command_B[1:].split('-')
                    assault = list_attack(gamer_B, actions[0], position_B[0], position_B[1], assault)
                    
                else :
                    None
                
        ## Save the departure lives 
        starting = {}
        for n in gamer_A:
            starting[n] = {'Life': gamer_A[n]['Life']}
            
        for h in gamer_B:
           starting[h] = {'Life': gamer_B[h]['Life']}
           

        
        starting['Gate_A'] = {'Life': gate_A['Life']}
        
    
        starting['Gate_B'] = {'Life': gate_B['Life']}
        
            
        ## Attack  
        gate_A, gate_B, gamer_A, gamer_B, board = attack(assault, gamer_A, gamer_B, board, gate_A, gate_B)
        
        ## Harvest
        gamer_A, gamer_B, asteroides = case_colonizer(asteroides,gamer_A,gamer_B)
        
        ##Unloading
        gate_A, gate_B, gamer_A, gamer_B = unloading (gate_A, gate_B, gamer_A, gamer_B)
        
        ## Display of the board
    
        display(gamer_A, gamer_B, board, gate_A, gate_B,asteroides)
        
        ## Save the finish lives
        ending = {}
        for f in gamer_A:
            ending[f] = {'Life': gamer_A[f]['Life']}
            
        for j in gamer_B:
            ending[j] = {'Life': gamer_B[j]['Life']}
            
       
        ending['Gate_A'] = {'Life': gate_A['Life']}
        
        ending['Gate_B'] = {'Life': gate_B['Life']}
        
        turn_without_damage = not_game_over(gate_A, gate_B, gamer_A, gamer_B, turn_without_damage, starting, ending)[1]
        turn += 1
        
        last_choice_rival_A = choice_A
        last_choice_rival_B = choice_B


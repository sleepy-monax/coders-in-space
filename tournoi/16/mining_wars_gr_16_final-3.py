# -*- coding: utf-8 -*-



from random import randint

from termcolor import colored
import time


def start(path,remote_IP, player_id): 
    """This function contains all the game.
    
    Parameters
    ----------
    gameboard.mw: the file where all the information for the board is (file)
    type_blue: the type of the blue player it can be IA or human (str)
    type_pink: the type of the pink player it can be IA or human (str)
    
    Returns
    -------
    array : the dictionary with the lentgh and the width(tuple)
    portals: the dictionary where the information of the portals comes from(dict)
    asteroids: the dictionary with all the information about the asteroids(list)
    nb_ores_blue:the number of ores that has the blue player(int)
    nb_ores_pink:the number of ores that has the pink player(int)
    board:the dictionary with all the positions of the ships (dict)
    
    Notes
    -----
    The lenght has to be <= 40 lines
    The width has to be <= 80 columns
    
    Version
    -------
    specification: Camille Mazuin (v.4 23/03/18) )
    implementation: Camille Mazuin, Henriette Van Marcke, Margot Kesch (v.3 23/03/18)
    
    """
    
    nb_ores_pink=4
    nb_ores_blue=4
    nb_turn = 0
    end_game = False
    
    
    blue_starships={}
    pink_starships={}
    asteroids=[]
    asteroid_temp={} 
    blue_excavators={}
    pink_excavators={}
    portals={}
    pink_portal={}
    blue_portal={}
    board={}
    array=()
    
    
    size_unites ={'portal': [[0,0],[1,0], [-1,0], [0,1], [0,-1], [1,1], [1,-1],[-1,-1], [-1,1],[0,2], [0,-2],[2,0], [-2,0], [2,1], [2,-1], [1,2], [1,-2], [-1,2], [-1,-2],[-2,1],[-2,-1],[2,2],[2,-2],[-2,2],[-2,-2]], 
                  'scout' : [[0,0],[1,0], [-1,0], [0,1], [0,-1], [1,1], [1,-1],[-1,-1], [-1,1] ], 
                  'warship':[[0,0],[1,0], [-1,0], [0,1], [0,-1], [1,1], [1,-1],[-1,-1], [-1,1],[0,2], [0,-2],[2,0], [-2,0], [2,1], [2,-1], [1,2], [1,-2], [-1,2], [-1,-2],[-2,1],[-2,-1]], 
                  'excavator-S': [[0,0]],
                  'excavator-M':[[0,0],[1,0], [-1,0], [0,1], [0,-1]],
                  'excavator-L':[[0,0],[1,0], [-1,0], [0,1], [0,-1],[0,2], [0,-2],[2,0], [-2,0]]}
    
    types={'scout' :{'size' : 9 , 'life' : 3, 'attack' :1 , 'reach' :3 , 'cost' :3 }, 
           'warship' :{'size' :21 , 'life' :18 , 'attack' :3 , 'reach' : 5, 'cost' : 9},
           'excavator-S' :{'size' :1 , 'tonnage' : 1, 'life' : 2, 'cost' :1 },
           'excavator-M' :{'size' :5 , 'tonnage' :4 , 'life' : 3, 'cost' :2 },
           'excavator-L' :{'size' :9 , 'tonnage' :8 , 'life' : 6, 'cost' : 4}}

    fh= open(path, 'r')

    # read the file and put the elements into variables
     
    lines= fh.readlines()
    size=lines[1].split(' ')
    
    if int(size[0])<= 40 and int(size[1])<=80 and int(size[0])>0 and int(size[1])>0:
        array=(int(size[0]),int(size[1]))
    else:
        print('The size of the array is not possible')
    
    blue_position=lines[3].split(' ')
    rb=int(blue_position[0])
    cb=int(blue_position[1])
    blue_portal['r']=rb
    blue_portal['c']=cb
    blue_portal['life']=100
    
    pink_position=lines[4].split(' ')
    rp=int(pink_position[0])
    cp=int(pink_position[1])
    pink_portal['r']=rp
    pink_portal['c']=cp
    pink_portal['life']=100

    portals['blue_portal']=blue_portal
    portals['pink_portal']=pink_portal
    
    size_lines = len(lines)
    ast_list=lines[6:size_lines]
    
                 
   # creation of the dictionnary "board"
                
    for size in size_unites['portal']:
        board[rb+size[0],cb+size[1]]= ['blue_portal']
    
    
    if rp==rb and cb==cp:
        print('The pink and blue portal can not have the same centre')
        
    else:
       for size in size_unites['portal']:
           board[rp+size[0],cp+size[1]]= ['pink_portal']
    
    
    for ast in ast_list:
        a= ast.split(' ')
        ra=int(a[0])
        ca=int(a[1])
        nb_ores=int(a[2])
        tonnage=int(a[3])
        asteroid_temp['r']=ra
        asteroid_temp['c']=ca
        if nb_ores <=24:
            asteroid_temp['nb_ores']=nb_ores
        else:
            print('An asteroid has to have less than 25 ores to start the game. Please change the file and restart the game.')
        asteroid_temp['tonnage']=tonnage
        asteroids.append(asteroid_temp)
        if (ra == rp and ca== cp) or (ra== rb and ca== cb):
            print('An asteroid can not have the same centre as the portal')
        else:
            board[ra,ca]= ['asteroid'] 
   

    verbose=False
    
    connection =connect_to_player(3-player_id, remote_IP, verbose)
              
    
    while end_game == False:
        turn(blue_starships,pink_starships,blue_excavators,pink_excavators,nb_ores_blue,nb_ores_pink,board,array,asteroids,portals,nb_turn,types,end_game,size_unites, player_id, connection)
        display_gameboard(array, portals,asteroids,blue_starships,pink_starships,blue_excavators,pink_excavators, board)
    
    return array, asteroids, portals, nb_ores_blue, nb_ores_pink, board
        
                 
def display_gameboard(array, portals,asteroids,blue_starships,pink_starships,blue_excavators,pink_excavators, board):
    """Displays the gameboard with unities.
    
    Parameters
    ----------
    array : the dictionary with the lentgh and the width(dict)
    portals: the dictionary where the information of the portals comes from(dict)
    asteroids: the dictionary with all the information about the asteroids(dict)
    blue_starships: the dictionnary that contains all the starships of the blue player(dict)
    pink_starships: the dictionnary that contains all the starships of the pink player(dict)
    blue_excavators: the information of the blue excavators after displacement (dict)
    pink_excavators: the information of the pink excavators after displacement (dict)
    board: position of all starships on the gameboard (dict)
    
    Version 
    -------
    specification: Margot Kesch, Henriette Van Marcke, Camille Mazuin (v.2 27/04/18)
    implementation: Camille Mazuin, Henriette Van Marcke, Margot Kesch (v.5 27/04/18)
    
    """
    list_square=[]
    line ='' 

    time.sleep(3)
    
    for ligne in range (array[0]):
        
        line=''
        column = 1
        while column <= array[1]:
            
            if (ligne,column) in board:
                
                    
                list_ship=board[(ligne,column)]
            
                

                if len(list_ship)==1:
                    if list_ship[0] in blue_starships:
                        type_ship= blue_starships[list_ship[0]]['type']
                        if type_ship == 'scout':
                                
                        
                            line+=(colored('\u265F', 'cyan'))
                                    
                        else :
                            line+=(colored('\u265C', 'cyan'))
                                    
                                  
                    elif list_ship[0] in pink_starships:
                        type_ship= pink_starships[list_ship[0]]['type']
                        if type_ship == 'scout':
                            line+=colored('\u265F', 'magenta')
                                    
                        else :
                            line+=colored('\u265C', 'magenta')
                                
                    elif list_ship[0] in blue_excavators:
                        type_ship= blue_excavators[list_ship[0]]['type']
                        state_blue_ship=blue_excavators[list_ship[0]]['state']
                        if type_ship == 'excavators-S':
                            if state_blue_ship=='locked':
                                line+=colored('\u265E', 'red','on_cyan')
                            else :
                                line+=colored('\u265E', 'green','on_cyan')
                        elif type_ship == 'excavators-M':
                            if state_blue_ship=='locked':
                                line+=colored('\u265D', 'red','on_cyan')
                            else :
                                line+=colored('\u265D', 'green','on_cyan')
                        else :
                            if state_blue_ship=='locked':
                                line+=colored('\u265A', 'red','on_cyan')
                            else :
                                line+=colored('\u265A', 'green','on_cyan')
                    elif list_ship[0] in pink_excavators:
                        type_ship= pink_excavators[list_ship[0]]['type']
                        state_pink_ship=pink_excavators[list_ship[0]]['state']
                        if type_ship == 'excavators-S':
                            if state_pink_ship=='locked':
                                line+=colored('\u265E', 'red','on_magenta')
                            else :
                                line+=colored('\u265E', 'green','on_magenta')
                        elif type_ship == 'excavators-M':
                            if state_pink_ship=='locked':
                                line+=colored('\u265D', 'red','on_magenta')
                            else :
                                line+=colored('\u265D', 'green','on_magenta')
                        else :
                            if state_pink_ship=='locked':
                                line+=colored('\u265A', 'red','on_magenta')
                            else :
                                line+=colored('\u265A', 'green','on_magenta')
                    elif list_ship[0]== 'blue_portal':
                        line+=colored('\u265B', 'white', 'on_cyan')
                    elif list_ship[0]== 'pink_portal':
                        line+=colored('\u265B', 'white', 'on_magenta')
                    else :
                        line+=colored('\u2605', 'white')
                        
                        
                elif len(list_ship)>1:
                    for boat in list_ship:
                        if boat in blue_excavators or boat in blue_starships or boat == 'blue_portal':
                            list_square+= ['blue']
                        elif boat in pink_excavators or boat in pink_starships or boat == 'pink_portal':
                            list_square+= ['pink']
                        else :
                            list_square+= ['asteroid']
                  
                        
                    if list_square[0]=='pink':
                        p=0
                        for el_list in list_square:
                            if el_list=='pink':
                                p+=1
                        if p==len(list_square):
                            team='pink'
                        else :
                            team='yellow'
                    elif list_square[0]=='blue':
                        p=0
                        for el_list in list_square:
                            if el_list=='blue':
                                p+=1
                        if p==len(list_square):
                            team='blue'
                        else :
                            team='yellow'
                    else:
                        p=0
                        for el_list in list_square:
                            if el_list=='asteroid':
                                p+=1
                        if p==len(list_square):
                            team='white'
                        else:
                            team='yellow'
                            
                            
                    if 'pink_portal' in list_ship :
                        if team=='pink':
                            line+=(colored('\u2617', 'white', 'on_magenta'))
                                
                        else :
                            line+=(colored('\u2617', 'white', 'on_magenta'))
                    elif 'blue_portal' in list_ship :
                        if team=='blue':
                            line+=(colored('\u2617', 'white', 'on_cyan'))
                                
                        else :
                            line+=(colored('\u2617', 'white', 'on_cyan'))
                    else:
                        if team=='pink' :
                            line+=(colored('\u2617', 'magenta'))
                        elif team=='blue':
                            line+=(colored('\u2617', 'cyan'))
                        elif team=='white':
                            line+=(colored('\u2617', 'white'))
                        else :
                            line+=(colored('\u2617', 'white'))
                                        
                else:
                    line+=('\u25A2')    
            else:
                if (ligne,column) not in board:
                    line+=('\u25A2')
                    
                
            column+=1
        
        print(line)    
    
    
    print('blue_player:%d   pink_player:%d' %(portals['blue_portal']['life'],portals['pink_portal']['life']))
    ##legend
    print('Legend:')
    print('\u265B:portal        \u2605:asteroid      \u265C:warship       \u265F:scout')
    print('\u265E:excavator-S   \u265D:excavator-M   \u265A:excavator-L   \u2617:overlay')
    print('If there is one asteroid on the square: white')
    
  


            
def turn(blue_starships,pink_starships,blue_excavators,pink_excavators,nb_ores_blue,nb_ores_pink,board,array,asteroids,portals,nb_turn,types,end_game,size_unites, player_id, connection):
    """This function is the development of each game round that restarts every time at the end of a round if the game is not over.
    
    Parameters
    ----------
    blue_starships: the dictionnary that contains all the starships of the blue player(dict)
    pink_starships: the dictionnary that contains all the starships of the pink player(dict)
    blue_excavators: the information of the blue excavators after displacement (dict)
    pink_excavators: the information of the pink excavators after displacement (dict)
    nb_ores_blue:the number of ores that has the blue player(int)
    nb_ores_pink: the number of ores that has the pink player (int)    board: position of all starships on the gameboard (dict)
    array : the dictionary with the lentgh and the width(dict)
    asteroids: the dictionnary with all the information about the asteroids(dict)
    portals: the dictionnary where the information of the portals comes from(dict)
    nb_turn: the number of turns without any damage(int)
    types: the dictionnary where all the information on each type of starships is stocked (dict)
    end_game: if the game is finished or not(bool)
    size_unites: the dictionnary which contains all the dimensions of each starships(dict)
    type_blue: the type of the blue player it can be IA or human (str)
    type_pink: the type of the pink player it can be IA or human (str)
    
    specification: Henriette Van Marcke (v.2 15/04/18)
    Version
    -------
    implementation: Camille Mazuin, Margot Kesch, Henriette Van Marcke (v.3 15/04/18)
    
    """
    
    
    blue_list_displace=[]
    pink_list_displace=[]
    
    # asks the player what he wants to do
    
    if player_id == 1:
        blue_answer = smart_IA('blue',blue_excavators, pink_excavators, blue_starships, pink_starships, nb_ores_blue, nb_ores_pink, asteroids, types, portals)
        notify_remote_orders(connection, blue_answer)
        pink_answer =get_remote_orders(connection)
    else:
         blue_answer =get_remote_orders(connection)
         pink_answer = smart_IA('pink',blue_excavators, pink_excavators, blue_starships, pink_starships, nb_ores_blue, nb_ores_pink, asteroids, types, portals)
         notify_remote_orders(connection, pink_answer)
    
   # if type_blue == 'human' and type_pink == 'human':
    #    blue_answer= input('Blue player, what do you want to do?')
     #   pink_answer= input('Pink player, what do you want to do?')
    #elif type_blue == 'IA' and type_pink == 'human':
     #   blue_answer= smart_IA('blue',blue_excavators, pink_excavators, blue_starships, pink_starships, nb_ores_blue, nb_ores_pink, asteroids, types, portals)
      #  pink_answer= input('Pink player, what do you want to do?')  
   # elif type_blue == 'human' and type_pink == 'IA':
    #    blue_answer= input('Blue player, what do you want to do?')
     #   pink_answer= smart_IA('pink',blue_excavators, pink_excavators, blue_starships, pink_starships, nb_ores_blue, nb_ores_pink, asteroids, types, portals)   
    #else:
     #   blue_answer= smart_IA('blue',blue_excavators, pink_excavators, blue_starships, pink_starships, nb_ores_blue, nb_ores_pink, asteroids, types, portals)
      #  pink_answer= smart_IA('pink',blue_excavators, pink_excavators, blue_starships, pink_starships, nb_ores_blue, nb_ores_pink, asteroids, types, portals)
        
       # reads the answers of the player and appeals the necessary fonctions
       
    
    list_blue_answer=blue_answer.split(' ')
    list_pink_answer=pink_answer.split(' ')
        
    for blue_element in list_blue_answer:
            
        if '@' in blue_element:
            infos_blue_move= blue_element.split(':')
            mover= infos_blue_move[0]
            infos_blue_move2=infos_blue_move[1].split('-')
            row_move=int(infos_blue_move2[0][1:])
            column_move=int(infos_blue_move2[1])
            blue_list_displace+=[mover]
            color='blue'
            move_color(blue_starships, blue_excavators,pink_starships, pink_excavators, board, mover, row_move, column_move, array, size_unites,color)
            
    for pink_element in list_pink_answer:
            
        if '@' in pink_element:
            infos_pink_move= pink_element.split(':')
            mover= infos_pink_move[0]
            infos_pink_move2=infos_pink_move[1].split('-')
            row_move=int(infos_pink_move2[0][1:])
            column_move=int(infos_pink_move2[1])
            pink_list_displace+=[mover]
            color='pink'
            move_color(blue_starships, blue_excavators,pink_starships, pink_excavators, board, mover, row_move, column_move, array, size_unites,color)

        
    for blue_element in list_blue_answer:
            
        if '*' in blue_element :
            infos_blue_attack= blue_element.split(':')
            attacker= infos_blue_attack[0]
            infos_blue_attack2=infos_blue_attack[1].split('-')
            row_attack=int(infos_blue_attack2[0][1:])
            column_attack=int(infos_blue_attack2[1])
            for blue_elem in blue_list_displace:
                if blue_elem == attacker:
                    print('Blue player you cannot attack and move with the same starship at the same turn')
                else :
                    color='blue'
                    color_attack(blue_starships, pink_starships, blue_excavators, pink_excavators, portals, nb_turn, types, board, attacker, row_attack, column_attack,color)         
        
    for pink_element in list_pink_answer:
        
        if '*' in pink_element :
            infos_pink_attack= pink_element.split(':')
            attacker= infos_pink_attack[0]
            infos_pink_attack2=infos_pink_attack[1].split('-')
            row_attack=int(infos_pink_attack2[0][1:])
            column_attack=int(infos_pink_attack2[1])
            for pink_elem in pink_list_displace:
                if pink_elem == attacker:
                    print('Pink player you cannot attack and move with the same starship at the same turn')
                else:
                    color='pink'
                    color_attack(blue_starships, pink_starships, blue_excavators, pink_excavators, portals, nb_turn, types, board, attacker, row_attack, column_attack, color) 

         
    for blue_element in list_blue_answer:
                
        if 'lock' in blue_element or 'release' in blue_element:
            infos_blue_lock= blue_element.split(':')
            locker=infos_blue_lock[0]
            state=infos_blue_lock[1]
            color='blue'
            locking_unlocking_color(blue_excavators,pink_excavators,asteroids,portals, locker, state,color)
                
    for pink_element in list_pink_answer:
            
         if 'lock' in pink_element or 'release' in pink_element:
            infos_pink_lock= pink_element.split(':')
            locker=infos_pink_lock[0]
            state=infos_pink_lock[1]
            color='pink'
            locking_unlocking_color(blue_excavators,pink_excavators,asteroids,portals, locker, state,color)

            
    for blue_element in list_blue_answer:        
                
        if 'excavator-S' in blue_element or 'excavator-M' in blue_element or 'excavator-L' in blue_element or 'scout' in blue_element or 'warship' in blue_element:
            infos_blue_buy= blue_element.split(':')
            name_ship=infos_blue_buy[0]
            type_ship=infos_blue_buy[1]
            color= 'blue'
            buying_color_starships(types, blue_starships, portals, pink_starships,name_ship,type_ship, nb_ores_blue, nb_ores_pink, size_unites, board, blue_excavators,pink_excavators,color)
            
    for pink_element in list_pink_answer:
       
        if 'excavator-S' in pink_element or 'excavator-M' in pink_element or 'excavator-L' in pink_element or 'scout' in pink_element or 'warship' in pink_element:
            infos_pink_buy= pink_element.split(':')
            name_ship=infos_pink_buy[0]
            type_ship=infos_pink_buy[1]
            color='pink'
            buying_color_starships(types, blue_starships, portals, pink_starships,name_ship,type_ship, nb_ores_blue, nb_ores_pink, size_unites, board, blue_excavators,pink_excavators,color)

            
                
    if '*' not in blue_answer and '*' not in pink_answer:
        nb_turn +=1
        

    deposit_ores (blue_excavators,pink_excavators,nb_ores_pink,nb_ores_blue) 
    collecting_ores (blue_excavators, pink_excavators,asteroids,board)   
    end(nb_turn, nb_ores_blue, nb_ores_pink, portals)
        
        
        
       



def IA(array):
    """ This function is the naive IA of the game and returns a random order.
    
    Parameters
    ----------
    array: the dictionary with the lentgh and the width(dict)
    
    Return
    ------
    string: the string of actions (str)
    
    Version
    -------
    specification: Henriette Van Marcke, Camille Mazuin, Kesch Margot (v.1 15/04/18)
    implementation: Henriette Van Marcke, Camille Mazuin, Kesch Margot (v.1 15/04/18) 
    
    """
    
    
    answer= randint(1,6)
    if answer== 1:
        string ='rose:scout lys:*%d-%d lavande:release jonquille:@%d-%d  violette:excavator-M'%(randint(0,array[0]), randint(0,array[1]),randint(0,array[0]), randint(0,array[1]))
    elif answer ==2:
        string ='lys:warship rose:@%d-%d violette:release'%(randint(0,array[0]), randint(0,array[1]))
    elif answer ==3:
        string = 'violette:excavator-M lavande:@%d-%d violette:lock'%(randint(0,array[0]), randint(0,array[1]))
    elif answer ==4:
        string = 'lavande:excavator-S rose*%d-%d lavande:lock violette:release'%(randint(0,array[0]), randint(0,array[1]))
    elif answer ==5: 
        string = 'jonquille:scout lavande:lock rose:*%d-%d '%(randint(0,array[0]), randint(0,array[1]))
    else:
        string = 'jonquille:@%d-%d lys*%d-%d violette:locked lavande:@%d-%d'%(randint(0,array[0]), randint(0,array[1]),randint(0,array[0]), randint(0,array[1]),randint(0,array[0]), randint(0,array[1]))

    return string
    
    
    
def smart_IA(color,blue_excavators, pink_excavators, blue_starships, pink_starships, nb_ores_blue, nb_ores_pink, asteroids, types, portals):
    '''This function is the smart IA of the game.
    
    Parameters
    ----------
    blue_starships: the dictionnary that contains all the starships of the blue player(dict)
    pink_starships: the dictionnary that contains all the starships of the pink player(dict)
    blue_excavators: the information of the blue excavators after displacement (dict)
    pink_excavators: the information of the pink excavators after displacement (dict)
    nb_ores_blue:the number of ores that has the blue player(int)
    nb_ores_pink: the number of ores that has the pink player (int)    
    color: the player who is playing (str)
    asteroids: the dictionnary with all the information about the asteroids(dict)
    types: the dictionnary where all the information on each type of starships is stocked (dict)
    portals: the dictionnary where the information of the portals comes from(dict)
    
    Return
    ------
    pink_answer: the answer which contains all the instructions of the blue team(str)
    blue_answer: the answer which contains all the instructions of the blue team(str)
    
    Version
    -------
    specification: Camille Mazuin, Henriette Van Marcke, Margot Kesch (v.1 24/04/18)
    implementation: Camille Mazuin, Margot Kesch, Henriette Van Marcke (v.3 24/04/18)
    
    '''

    attack_excavators= False
    attack_starships= False
    color_excavators={}
    color_starships= {}
    color_answer2=[]
    color_answer=''
    blue_answer=''
    pink_answer=''

        
    
    if color == 'blue':
        color_excavators= blue_excavators
        color_starships= blue_starships
        nb_ores= nb_ores_blue
    
    
    else:
        color_excavators= pink_excavators
        color_starships= pink_starships
        nb_ores= nb_ores_pink
    
    
    # gives the order to buy starships

    if nb_ores >0:
        if nb_ores >= 9:
            ship = 'warship'
        elif nb_ores < 4:
            ship = 'excavator-S'
    
        else:
            rand=randint(1,4)
            if rand==1:
                ship='excavator-S'
            elif rand==2:
                ship='excavator-M'
            elif rand==3:
                ship='excavator-L'
            else:
                ship='scout'
        
       
    #gives a name to each starship
        
        name= randint(1,100)
        while name in color_starships:
            name= randint(1,100)
        color_answer2+= [str(name)+':'+ship]
 

    # gives the order to lock or unlock excavators

    for excavator in color_excavators:
        column=color_excavators[excavator]['column']
        row=color_excavators[excavator]['row']
        state=color_excavators[excavator]['state']
        for asteroid in asteroids:
            r=asteroid['r']
            c=asteroid['c']
            if column==c and row==r: 
                if state=='released':
                    action='lock'
                else :
                    action='release'
                color_answer2+=[str(excavator) + ':'+action]
    
    # gives the order to move or attack
    
    if color == 'blue':
        for star in blue_starships:
            row_blue= blue_starships[star]['row']
            column_blue= blue_starships[star]['column']
            type_blue= blue_starships[star]['type']
            reach_blue= types[type_blue]['reach']
            for exca in pink_excavators:
                row_exca_pink= pink_excavators[exca]['row']
                column_exca_pink= pink_excavators[exca]['column']
                if abs(row_blue-row_exca_pink)+abs(column_blue-column_exca_pink)<= reach_blue:
                    ship_attack= star
                    row_attack= row_exca_pink
                    column_attack=column_exca_pink
                    color_answer2 += [str(ship_attack)+':*'+str(row_attack)+'-'+str(column_attack)]
                    attack_excavators=True
                else:
                    attack_excavators= False
                
            for star2 in pink_starships:
                row_star2_pink= pink_starships[star2]['row']
                column_star2_pink= pink_starships[star2]['column']
                if abs(row_blue-row_star2_pink)+abs(column_blue-column_star2_pink)<= reach_blue:
                    ship_attack= star
                    row_attack= row_star2_pink
                    column_attack=column_star2_pink
                    color_answer2 += [str(ship_attack)+':*'+str(row_attack)+'-'+str(column_attack)]
                    attack_starships= True
                else:
                    attack_starships= False
            # you cannot move and attack with the same ship 
            if attack_starships == False and attack_excavators== False:
                # checks which pink starship is the closest
                minimum=[200,200]
                for exc in pink_excavators:
                    if abs(blue_starships[star]['row']-pink_excavators[exc]['row'])<= minimum[0] and abs(blue_starships[star]['column']-pink_excavators[exc]['column'])<= minimum[1]:
                        minimum[0]= abs(blue_starships[star]['row']-pink_excavators[exc]['row'])
                        minimum[1]= abs(blue_starships[star]['column']-pink_excavators[exc]['column'])
                        row_exc= pink_excavators[exc]['row']
                        column_exc= pink_excavators[exc]['column']
                for st in pink_starships: 
                    if abs(blue_starships[star]['row']-pink_starships[st]['row'])<= minimum[0] and abs(blue_starships[star]['column']-pink_starships[st]['column'])<= minimum[1]:
                        minimum[0]= abs(blue_starships[star]['row']-pink_starships[st]['row'])
                        minimum[1]= abs(blue_starships[star]['column']-pink_starships[st]['column'])
                        row_exc= pink_starships[st]['row']
                        column_exc= pink_starships[st]['column']
                
                if abs(blue_starships[star]['row']-portals['pink_portal']['r'])<= minimum[0] and abs(blue_starships[star]['column']-portals['pink_portal']['c'])<= minimum[1]:
                        minimum[0]= abs(blue_starships[star]['row']-portals['pink_portal']['r'])
                        minimum[1]= abs(blue_starships[star]['column']-portals['pink_portal']['c'])
                        row_exc= portals['pink_portal']['r']
                        column_exc= portals['pink_portal']['c']
            
                if ((abs(blue_starships[star]['row']-row_exc))<=1 and (abs(blue_starships[star]['row']-row_exc))>=0 )and ((abs(blue_starships[star]['column']-column_exc))<=1 and (abs(blue_starships[star]['column']-column_exc))>=0 ):
                    color_answer2 += [str(star)+':@'+str(row_exc)+'-'+str(column_exc)]
                else:
                    row= row_exc-blue_starships[star]['row']
                    column=column_exc-blue_starships[star]['column']
                    while (((row))>1 or ((row))<-1 ) or ((column)>1 or(column)<-1 ):
                        row= row//2
                        column= column//2
                    row_move=blue_starships[star]['row']+ row
                    column_move= blue_starships[star]['column']+ column 
                    color_answer2 += [str(star)+':@'+str(row_move)+'-'+str(column_move)]

        # checks which asteroid is the closest
        minimum= [200,200]
        for ex in blue_excavators:
            for ast in asteroids:
                if abs(blue_excavators[ex]['row']-ast['r'])<= minimum[0] and abs(blue_excavators[ex]['column']-ast['c'])<= minimum[1]:
                    minimum[0]= abs(blue_excavators[ex]['row']-ast['r'])
                    minimum[1]= abs(blue_excavators[ex]['column']-ast['c'])
                    row_ast= ast['r']
                    column_ast= ast['c']
            if ((abs(blue_excavators[ex]['row']-row_ast))<=1 and (abs(blue_excavators[ex]['row']-row_ast))>=0 )and ((abs(blue_excavators[ex]['column']-column_ast))<=1 and (abs(blue_excavators[ex]['column']-column_ast))>=0 ):
                color_answer2 += [str(ex)+':@'+str(row_ast)+'-'+str(column_ast)]
            else:
                row= row_ast-blue_excavators[ex]['row']
                column=column_ast-blue_excavators[ex]['column']
                while (((row))>1 or ((row))<-1 ) or ((column)>1 or(column)<-1 ):
                    row= row//2
                    column= column//2
                row_move=blue_excavators[ex]['row']+ row
                column_move= blue_excavators[ex]['column']+ column 
                color_answer2 += [str(ex)+':@'+str(row_move)+'-'+str(column_move)]


            
        
                
    elif color == 'pink':
        for star in pink_starships:
            row_pink= pink_starships[star]['row']
            column_pink= pink_starships[star]['column']
            type_pink= pink_starships[star]['type']
            reach_pink= types[type_pink]['reach']
            for exca in blue_excavators:
                row_exca_blue= blue_excavators[exca]['row']
                column_exca_blue= blue_excavators[exca]['column']
                if abs(row_pink-row_exca_blue)+abs(column_pink-column_exca_blue)<= reach_pink:
                    ship_attack= star
                    row_attack= row_exca_blue
                    column_attack=column_exca_blue
                    color_answer2 += [str(ship_attack)+':*'+str(row_attack)+'-'+str(column_attack)]
                    attack_excavators=True
                else:
                    attack_excavators= False
                
            for star2 in blue_starships:
                row_star2_blue= blue_starships[star2]['row']
                column_star2_blue= blue_starships[star2]['column']
                if abs(row_pink-row_star2_blue)+abs(column_pink-column_star2_blue)<= reach_pink:
                    ship_attack= star
                    row_attack= row_star2_blue
                    column_attack=column_star2_blue
                    color_answer2 += [str(ship_attack)+':*'+str(row_attack)+'-'+str(column_attack)]
                    attack_starships= True
                else:
                    attack_starships= False
                    
            # you cannot move and attack with the same ship 
            if attack_starships == False and attack_excavators== False:
                # checks which blue starship is the closest
                minimum=[200,200]
                for exc in blue_excavators:
                    if abs(pink_starships[star]['row']-blue_excavators[exc]['row'])<= minimum[0] and abs(pink_starships[star]['column']-blue_excavators[exc]['column'])<= minimum[1]:
                        minimum[0]= abs(pink_starships[star]['row']-blue_excavators[exc]['row'])
                        minimum[1]= abs(pink_starships[star]['column']-blue_excavators[exc]['column'])
                        row_exc= blue_excavators[exc]['row']
                        column_exc= blue_excavators[exc]['column']
                for st in blue_starships: 
                    if abs(pink_starships[star]['row']-blue_starships[st]['row'])<= minimum[0] and abs(pink_starships[star]['column']-blue_starships[st]['column'])<= minimum[1]:
                        minimum[0]= abs(pink_starships[star]['row']-blue_starships[st]['row'])
                        minimum[1]= abs(pink_starships[star]['column']-blue_starships[st]['column'])
                        row_exc= blue_starships[st]['row']
                        column_exc= blue_starships[st]['column']
            
                if abs(pink_starships[star]['row']-portals['blue_portal']['r'])<= minimum[0] and abs(pink_starships[star]['column']-portals['blue_portal']['c'])<= minimum[1]:
                        minimum[0]= abs(pink_starships[star]['row']-portals['blue_portal']['r'])
                        minimum[1]= abs(pink_starships[star]['column']-portals['blue_portal']['c'])
                        row_exc= portals['blue_portal']['r']
                        column_exc= portals['blue_portal']['c']
            
                if ((abs(pink_starships[star]['row']-row_exc))<=1 and (abs(pink_starships[star]['row']-row_exc))>=0 )and ((abs(pink_starships[star]['column']-column_exc))<=1 and (abs(pink_starships[star]['column']-column_exc))>=0 ):
                    color_answer2 += [str(star)+':@'+str(row_exc)+'-'+str(column_exc)]
                else:
                    row= row_exc-pink_starships[star]['row']
                    column=column_exc-pink_starships[star]['column']
                    while (((row))>1 or ((row))<-1 ) or ((column)>1 or(column)<-1 ):
                        row= row//2
                        column= column//2
                    row_move=pink_starships[star]['row']+ row
                    column_move= pink_starships[star]['column']+ column 
                    color_answer2 += [str(star)+':@'+str(row_move)+'-'+str(column_move)]
 
 
        # checks which asteroid is the closest
        minimum= [200,200]           
        for ex in pink_excavators:
            for ast in asteroids:
                if abs(pink_excavators[ex]['row']-ast['r'])<= minimum[0] and abs(pink_excavators[ex]['column']-ast['c'])<= minimum[1]:
                    minimum[0]= abs(pink_excavators[ex]['row']-ast['r'])
                    minimum[1]= abs(pink_excavators[ex]['column']-ast['c'])
                    row_ast= ast['r']
                    column_ast= ast['c']
            if ((abs(pink_excavators[ex]['row']-row_ast))<=1 and (abs(pink_excavators[ex]['row']-row_ast))>=0 )and ((abs(pink_excavators[ex]['column']-column_ast))<=1 and (abs(pink_excavators[ex]['column']-column_ast))>=0 ):
                color_answer2 += [str(ex)+':@'+str(row_ast)+'-'+str(column_ast)]
            else:
                row= row_ast-pink_excavators[ex]['row']
                column=column_ast-pink_excavators[ex]['column']
                while (((row))>1 or ((row))<-1 ) or ((column)>1 or(column)<-1 ):
                    row= row//2
                    column= column//2
                row_move=pink_excavators[ex]['row']+ row
                column_move= pink_excavators[ex]['column']+ column 
                color_answer2 += [str(ex)+':@'+str(row_move)+'-'+str(column_move)]


    # put the elements in the correct list
    for elements in color_answer2:
        color_answer+= str(elements +' ')
    if color== 'blue':
        blue_answer= color_answer
        return blue_answer
    elif color == 'pink':
        pink_answer= color_answer
        return pink_answer

    
    
    
def buying_color_starships(types, blue_starships, portals, pink_starships,name_ship,type_ship, nb_ores_blue, nb_ores_pink, size_unites, board, blue_excavators,pink_excavators,color):
    """ This function lets a player buy a starship.
    
    Parameters
    ----------
    types: the dictionnary where all the information on each type of starships is stocked (dict)
    blue_starships: the dictionnary that contains all the starships of the player(dict)
    pink_starships: the dictionnary that contains all the starships of the pink player(dict)
    portals: the dictionnary where the information of the portals comes from(dict)
    name_ship:the name of the blue player's starship(str)
    type_blue_ship:the type of the blue player's starship(str)
    nb_ores_blue:the number of ores that has the blue player(int)
    nb_ores_pink:the number of ores that has the pink player(int)
    size_unites: the dictionnary which contains all the dimensions of each starships(dict)
    board: position of all starships on the gameboard (dict)
    blue_excavators: the information of the blue excavators after displacement (dict)
    pink_excavators: the information of the pink excavators (dict)
    color: the player who is playing (str)
    
    Returns
    -------
    blue_starships: the dictionnary that contains all the starships of the blue player(dict)
    pink_starships: the dictionnary that contains all the starships of the pink player(dict)
    blue_excavators: the information of the blue excavators after displacement (dict)
    pink_excavators: the information of the pink excavators (dict)
    nb_ores_blue: the number of ores that has the blue player (int)    
    nb_ores_pink: the number of ores that has the pink player (int)  
    board:the dictionary with all the positions of the ships (dict)
    
    Note
    ----
    You cannot buy if you don't have enough money.
    
    Version
    -------
    specification: Henriette Van Marcke (v.3 15/04/18)
    implementation: Margot Kesch, Camille Mazuin, Henriette Van Marcke (v.3 15/04/18) 
    
    """
    
    color_excavators={}
    color_starships= {}
    
    
    if color == 'blue':
        color_excavators= blue_excavators
        color_starships= blue_starships
        nb_ores= nb_ores_blue
        color_portal= 'blue_portal'
    else:
        color_excavators= pink_excavators
        color_starships= pink_starships
        nb_ores= nb_ores_pink
        color_portal= 'pink_portal'
    
    
    
    color_starships2= {} 
    color_excavators2= {}
    buying=True 
    
    cost= types[type_ship]['cost']
    
    
    # checks if the player has enough money
    if nb_ores >= cost: 
        for e in color_starships:
            if e == name_ship:
                buying= False
        for i in color_excavators:
            if i == name_ship:
                buying= False
         
            
       # creates the intermediate dictionnary to put them after in blue_excavators, pink_excavators, blue_starships, pink_starships and board   
        if buying ==False:
            print('%s player you already used this name'%(color))
        else: 
            if type_ship=='excavator-S' or type_ship=='excavator-M' or type_ship=='excavator-L':
                color_excavators2['type']= type_ship
                color_excavators2['row']= portals[color_portal]['r']
                color_excavators2['column']= portals[color_portal]['c']
                color_excavators2['state']='released'
                color_excavators2['nb_ores']= 0
                if type_ship== 'excavator-S':
                    color_excavators2['life']=2
                    color_excavators2['tonnage']=1
                elif type_ship== 'excavator-M':
                    color_excavators2['life']=3
                    color_excavators2['tonnage']=4
                else:
                    color_excavators2['life']=6
                    color_excavators2['tonnage']=8
                color_excavators[name_ship]= color_excavators2                
                for size in size_unites[type_ship]:
                    if (color_excavators2['row']+size[0],color_excavators2['column']+size[1]) in board:
                        board[(color_excavators2['row']+size[0],color_excavators2['column']+size[1])]+= [name_ship]
                    else:
                        board[(color_excavators2['row']+size[0],color_excavators2['column']+size[1])]= [name_ship]
            else: 
                color_starships2['type']= type_ship
                color_starships2['row']= portals[color_portal]['r']
                color_starships2['column']= portals[color_portal]['c']
                if 'scout' == type_ship:
                    color_starships2['life']= 3
                else: 
                    color_starships2['life']= 18
                color_starships[name_ship]= color_starships2
                for size in size_unites[type_ship]:
                    if (color_starships2['row']+size[0],color_starships2['column']+size[1]) in board:
                        board[(color_starships2['row']+size[0],color_starships2['column']+size[1])]+= [name_ship]
                    else:
                        board[(color_starships2['row']+size[0],color_starships2['column']+size[1])]= [name_ship]
                    
                    
                    
                    
            nb_ores -= cost
            
    else:
        print('%s player you do not have enough money'%(color))
    
    return blue_starships,pink_starships, blue_excavators, pink_excavators, nb_ores_blue, nb_ores_pink ,board

   
def locking_unlocking_color(blue_excavators,pink_excavators,asteroids,portals, locker, state,color):
    """ Lock or unlock an excavator on a portal or an asteroid.
    
    Parameters
    ----------
    blue_excavators: the information of the blue excavators (dict)
    pink_excavators: the information of the pink excavators (dict)
    asteroids: the dictionnary with all the information about the asteroids(dict)
    portals: the dictionnary where the information of the portals comes from(dict)
    locker: the excavator that the player want to lock or unlock(str)
    state: the state that the player wants(str)
    color: the player who is playing (str)
    
    Returns
    -------
    blue_excavators: the information of the blue excavators after displacement (dict)
    pink_excavators: the information of the pink excavators after displacement (dict)
        
    Notes:
    ------
    You can't lock in an excavator if it is not on an asteroid or a portal
    You can't unlock your excavator if it is already unlocked
    You can't ask something for the unities of the other player
    
    Version
    -------
    specification: Margot Kesch (v.3 15/04/18)
    implementation: Camille Mazuin, Henriette Van Marcke, Margot Kesch (v.2 15/04/18)
    
    """
    color_excavators={}
    
    
    if color == 'blue':
        color_excavators= blue_excavators
    else:
        color_excavators= pink_excavators
    
    # changes possibly the state of excavators in blue_excavators and pink_excavators
    centre= False
    if locker in color_excavators:
        for aste in asteroids:
            if aste['r']== color_excavators[locker]['row'] and aste['c']== color_excavators[locker]['column']:
                if state== 'released':
                    if color_excavators[locker]['state']== 'locked':
                        color_excavators[locker]['state']= 'released'
                    else:
                        print('%s player, your excavator is already unlocked.'%(color))
                elif state== 'lock':
                    if color_excavators[locker]['state']== 'released':
                        color_excavators[locker]['state']='locked'                    
                    else:
                        print('%s player, your excavator is already locked.'%(color))
                centre= True
        if centre== False:                    
            if portals['blue_portal']['r']== color_excavators[locker]['row'] and portals['blue_portal']['c']== color_excavators[locker]['column']:
                if state== 'released':
                    if color_excavators[locker]['state']== 'locked':
                        color_excavators[locker]['state']= 'released'
                    else:
                        print('%s player, your excavator is already unlocked.'%(color))
                elif state== 'lock':
                    if color_excavators[locker]['state']== 'released':
                        color_excavators[locker]['state']= 'locked'                    
                    else:
                        print('%s player, your excavator is already locked.'%(color))
            
            
            else:
                print('%s player, your excavator is not on the centre of an asteroid or not on your own portal'%(color))
    else:
        print('%s player, the starship is not yours or not an excavator'%(color))
            
                    
    return blue_excavators, pink_excavators            

    
    

def move_color(blue_starships, blue_excavators,pink_starships, pink_excavators, board, mover, row_move, column_move, array, size_unites,color):
    """This function allows te move a starship.
    
    Parameters
    ----------
    blue_starships: the dictionnary that contains all the starships of the blue player(dict)
    blue_excavators: the information of the blue excavators after displacement (dict)
    board: position of all starships on the gameboard (dict)
    mover: the name of the ship which moves(str)
    row_move: the row where the ship moves(int)
    column_move: the column where the ship moves(int)
    array : the dictionary with the lentgh and the width(dict)
    size_unites: the dictionnary which contains all the dimensions of each starships(dict)
    color: the player who is playing (str)
    pink_starships: the dictionnary that contains all the starships of the pink player(dict)
    pink_excavators: the information of the pink excavators after displacement (dict)
    
    Returns
    -------
    blue_starships: the dictionnary that contains all the starships of the blue player(dict)
    blue_excavators: the information of the blue excavators after displacement (dict)
    pink_starships: the dictionnary that contains all the starships of the pink player(dict)
    pink_excavators: the information of the pink excavators after displacement (dict)
    board: position of all starships on the gameboard (dict)
    
    Notes
    -----
    We can move our ships only one square.
    You can't ask something for the unities of the other player
    The starships cannot be out of the gameboard
    
    Version
    -------
    Speficication: Camille Mazuin (v.2 11/04/18)
    Implementation: Camille Mazuin, Margot Kesch, Henriette Van Marcke(v.3 16/04/18)
    
    """
    color_excavators={}
    color_starships= {}
    
    
    if color == 'blue':
        color_excavators= blue_excavators
        color_starships= blue_starships
    else:
        color_excavators= pink_excavators
        color_starships= pink_starships
    
    
    out_starships= False
    out_excavators= False
    list_ships=[]
    if mover in color_starships:
        type_ship= color_starships[mover]['type'] 
        if abs(row_move - color_starships[mover]['row'] ) <=1 and abs(column_move - color_starships[mover]['column'] ) <=1 :
            list_ships= board[(color_starships[mover]['row'], color_starships[mover]['column'])]
            
            #delete the old positions of starships in board
            for ship in list_ships:
                for key in board:
                    lists=board[key]
                    i=0
                    while i <= (len(lists)-1):
                        if lists[i]==mover:
                            del lists[i]
                        else:
                            i=i+1
            # add new positions of starships in board
            color_starships[mover]['row']+= (row_move - color_starships[mover]['row'])
            color_starships[mover]['column']+= (column_move - color_starships[mover]['column'])
            for size in size_unites[type_ship]:
                if (color_starships[mover]['row']+size[0],color_starships[mover]['column']+size[1]) in board:
                    board[(color_starships[mover]['row']+size[0],color_starships[mover]['column']+size[1])]+= [mover]
                else :
                    board[(color_starships[mover]['row']+size[0],color_starships[mover]['column']+size[1])]= [mover]
                    
            #delete the new positions of starships in board if a part of the starships is out of the board 
            for position in board:
                if position[0]> array[0] or position[0]<0  or position[1]> array[1] or position[1]<0:
                    out_starships = True
                    list_ships= board[(position[0], position[1])]
                    for ship in list_ships:
                        for key in board:
                            lists=board[key]
                            i=0
                            while i <= (len(lists)-1):
                                if lists[i]==mover:
                                    del lists[i]
                                else:
                                    i=i+1
                    # add old positions of starships in board
                    color_starships[mover]['row']-= (row_move - color_starships[mover]['row'])
                    color_starships[mover]['column']-= (column_move - color_starships[mover]['column'])
                
                    for size in size_unites[type_ship]:
                        if (color_starships[mover]['row']+size[0],color_starships[mover]['column']+size[1]) in board:
                            board[(color_starships[mover]['row']+size[0],color_starships[mover]['column']+size[1])]+= [mover]
                        else :
                            board[(color_starships[mover]['row']+size[0],color_starships[mover]['column']+size[1])]= [mover]
            if out_starships == True:
                print('%s player you are out of the gameboard, you stay on the same position'%(color))
                        
        else :
            print('%s player, you can only move one square at the time'%(color))
            
        
    elif mover in color_excavators:
        type_ship= color_excavators[mover]['type'] 
        if abs(row_move - color_excavators[mover]['row'] ) <=1 and abs(column_move - color_excavators[mover]['column'] ) <=1 :
            list_ships= board[(color_excavators[mover]['row'], color_excavators[mover]['column'])]
            #delete the old positions of starships in board
            for ship in list_ships:
                for key in board:
                    lists=board[key]
                    i=0
                    while i <= (len(lists)-1):
                        if lists[i]==mover:
                            del lists[i]
                        else:
                            i=i+1
                            
            # add new positions of starships in board
            color_excavators[mover]['row']+= (row_move - color_excavators[mover]['row'])
            color_excavators[mover]['column']+= (column_move - color_excavators[mover]['column'])
            for size in size_unites[type_ship]:
                if (color_excavators[mover]['row']+size[0],color_excavators[mover]['column']+size[1]) in board:
                    board[(color_excavators[mover]['row']+size[0],color_excavators[mover]['column']+size[1])]+= [mover]
                else :
                    board[(color_excavators[mover]['row']+size[0],color_excavators[mover]['column']+size[1])]= [mover]
            for position in board:
                if position[0]> array[0] or position[0]<0  or position[1]> array[1] or position[1]<0:
                    out_excavators = True
                    list_ships= board[(position[0], position[1])]
                    #delete the new positions of starships in board if a part of the starships is out of the board
                    for ship in list_ships:
                        for key in board:
                            lists=board[key]
                            i=0
                            while i <= (len(lists)-1):
                                if lists[i]==mover:
                                    del lists[i]
                                else:
                                    i=i+1
                    # add old positions of starships in board
                    color_excavators[mover]['row']-= (row_move - color_excavators[mover]['row'])
                    color_excavators[mover]['column']-= (column_move - color_excavators[mover]['column'])
                
                    for size in size_unites[type_ship]:
                        if (color_excavators[mover]['row']+size[0],color_excavators[mover]['column']+size[1]) in board:
                            board[(color_excavators[mover]['row']+size[0],color_excavators[mover]['column']+size[1])]+= [mover]
                        else :
                            board[(color_excavators[mover]['row']+size[0],color_excavators[mover]['column']+size[1])]= [mover]
            if out_excavators == True:
                print('%s player you are out of the gameboard, you stay on the same position'%(color))
                        
        else :
            print('%s player, you can only move one square at the time'%(color))
    else :
        print('%s player you can not move with the starships of the other player'%(color))  

    return blue_starships, blue_excavators,pink_starships, pink_excavators, board         

def color_attack(blue_starships, pink_starships, blue_excavators, pink_excavators, portals, nb_turn, types, board, attacker, row_attack, column_attack,color):
    """This function allows to attack a square.
    
    Parameters
    ----------
    blue_starships: the dictionnary that contains all the starships of the blue player(dict)
    pink_starships: the dictionnary that contains all the starships of the pink player(dict)
    blue_excavators: the information of the blue excavators (dict)
    pink_excavators: the information of the pink excavators (dict)
    portals: the dictionnary where the information of the portals comes from(dict)
    nb_turn: the number of turns without any damage(int)
    types: the dictionnary where all the information on each type of starships is stocked (dict)
    board:the dictionary with all the positions of the ships (dict)
    attacker: the blue starship that attacks(str)
    row_attack: the row where you want to attack(int)
    column_attack: the column where you want to attack(int)
    color: the player who is playing (str)
    
     
    Returns
    -------
    blue_starships: the dictionnary that contains all the starships of the blue player(dict)
    pink_starships: the dictionnary that contains all the starships of the pink player(dict)
    blue_excavators: the information of the blue excavators (dict)
    pink_excavators: the information of the pink excavators (dict)
    portals: the dictionnary where the information of the portals comes from(dict)
    nb_turn: the number of turns without any damage(int)
    board:the dictionary with all the positions of the ships (dict)
    
    Notes
    -----
    The starship must have the correct reach in order to attack.
    You can't ask something for the unities of the other player
    
    Version
    -------
    Speficication: Camille Mazuin (v.4 16/04/18)
    Implementation: Margot Kesch, Camille Mazuin, Henriette Van Marcke (v.4 16/04/18) 
    
    """

    color_starships= {}
    
    
    if color == 'blue':
        color_starships= blue_starships
    else:
        color_starships= pink_starships
    
    list_ships= []
    if attacker in color_starships:
        type_attacker= color_starships[attacker]['type']
        row= color_starships[attacker]['row']
        column= color_starships[attacker]['column']
        reach_attacker= types[type_attacker]['reach']
        
        # checks the reach and it is right, the starship attacks
            
        if abs(row_attack-row)+ abs(column_attack-column) <= reach_attacker:
            if (row_attack,column_attack) in board:
                list_ships= board[(row_attack,column_attack)]
                nb_damage= types[type_attacker]['attack']
                for ship in list_ships:
                    if ship == 'blue_portal':
                        nb_life_blue_portal= int(portals['blue_portal']['life']) - nb_damage
                        portals['blue_portal']['life']= nb_life_blue_portal
                    elif ship == 'pink_portal':
                        nb_life_pink_portal= int(portals['pink_portal']['life']) - nb_damage
                        portals['pink_portal']['life']= nb_life_pink_portal
                    elif ship in blue_starships:
                        blue_starships[ship]['life']= int(blue_starships[ship]['life']) - nb_damage
                        
                        # delete the blue starship in board if it is dead
                        if blue_starships[ship]['life'] <=0:
                            del blue_starships[ship]
                                            
                            for key in board:
                                lists=board[key]
                                i=0
                                while i <= (len(lists)-1):
                                    if lists[i]==ship:
                                        del lists[i]
                                    else:
                                        i=i+1
                            
                                           
                    elif ship in pink_starships:
                        pink_starships[ship]['life']= int(pink_starships[ship]['life']) - nb_damage    
                        if pink_starships[ship]['life'] <=0:
                            # delete the pink starship in board if it is dead 
                            del pink_starships[ship]
                            for key in board:
                                lists=board[key]
                                i=0
                                while i <= (len(lists)-1):
                                    if lists[i]==ship:
                                        del lists[i]
                                    else:
                                        i=i+1
                        
                    elif ship in blue_excavators:
                        blue_excavators[ship]['life']= int(blue_excavators[ship]['life']) - nb_damage                
                        if blue_excavators[ship]['life'] <=0:
                            # delete the blue excavator in board if it is dead 
                            del blue_excavators[ship]
                            for key in board:
                                lists=board[key]
                                i=0
                                while i <= (len(lists)-1):
                                    if lists[i]==ship:
                                        del lists[i]
                                    else:
                                        i=i+1
                                         
                    elif ship in pink_excavators:
                        pink_excavators[ship]['life']= int(pink_excavators[ship]['life']) - nb_damage
                        if pink_excavators[ship]['life'] <=0:
                            # delete the pink excavator in board if it is dead 
                            del pink_excavators[ship]
                            for key in board:
                                lists=board[key]
                                i=0
                                while i <= (len(lists)-1):
                                    if lists[i]==ship:
                                        del lists[i]
                                    else :
                                        i=i+1
                                        
                                        
                        
                    nb_turn=0             
                        
            else:
                nb_turn+=1
                print('%s player you touched an empty square'%(color))        
        else:
            print('%s player the reach is not right'%(color))
    else :
        print('%s player you cannot attack with a ship that is not yours or an excavator'%(color))
                            
    return board,nb_turn, portals, blue_starships, pink_starships, blue_excavators, pink_excavators  

                          

def deposit_ores (blue_excavators,pink_excavators,nb_ores_pink,nb_ores_blue):
    """This function deposits the ores on the player's portal.
    
    Parameters
    ----------
    blue_excavators: the information of the blue excavators (dict)
    pink_excavators: the information of the pink excavators (dict)
    nb_ores_pink: the number of ores that has the pink player (int)    
    nb_ores_blue: the number of ores that has the blue player (int)  
      
    Returns
    -------
    blue_excavators: the information of the blue excavators (dict)
    pink_excavators: the information of the pink excavators (dict)
    nb_ores_pink: the number of ores that has the pink player (int)    
    nb_ores_blue: the number of ores that has the blue player (int)  
      
    Notes:
    ------
    The function doesn't deposit ores if the excavator is not locked
    The function doesn't deposit ores if the excavator is not in the centre of a portal
    
    Version
    -------
    specification: Margot Kesch (v.2 29/03/18)
    implementation: Margot Kesch, Camille Mazuin, Henriette Van Marcke (v.1 29/03/18)
    
    """ 
    for excavator in blue_excavators:
        if blue_excavators[excavator]['state'] == 'locked':
            nb_ores_blue+= blue_excavators[excavator]['nb_ores']
            blue_excavators[excavator]['nb_ores'] = 0
    for excavator in pink_excavators:
        if pink_excavators[excavator]['state'] == 'locked':
            nb_ores_pink+= pink_excavators[excavator]['nb_ores']
            pink_excavators[excavator]['nb_ores'] = 0
    
    return nb_ores_pink, nb_ores_blue,pink_excavators, blue_excavators

    
def collecting_ores (blue_excavators, pink_excavators,asteroids,board):
    """This functions collects the ores.
    
    Parameters
    ----------
    blue_excavators: the information of the blue excavators (dict)
    pink_excavators: the information of the pink excavators (dict)
    asteroids: the dictionnary with all the information about the asteroids(dict)
    board:the dictionary with all the positions of the ships (dict)
    
    Returns
    -------
    asteroids: the dictionnary with all the information about the asteroids(dict)
    blue_excavators: the information of the blue excavators (dict)
    pink_excavators: the information of the pink excavators (dict)
   
    Notes
    -----
    You can't collect ores if you are not locked.
    You can't collect ores if the centre of you excavator is not the same as the asteroid's centre.
    
    Version
    -------
    specification: Margot Kesch (v.2 11/04/18)
    implementation: Margot Kesch, Camille Mazuin, Henriette Van Marcke (v.3 16/04/18)
    
    """
    
    sum_tonnage=0
    excavators=[]
    nb_excavators =0
    
    # counts the number of excavators on the same position of the asteroid
    for square in board:
        if 'asteroid' in board[square]:
            for sq in board[square]:
                if sq in blue_excavators:
                    if blue_excavators[sq]['state']=='locked':
                        nb_excavators += 1 
                    if blue_excavators[sq]['row']== square[0] and blue_excavators[sq]['column']== square[1]:
                        excavators+=[sq]
                elif sq in pink_excavators: 
                    if pink_excavators[sq]['state']=='locked':
                        nb_excavators += 1
                    if pink_excavators[sq]['row']== square[0] and pink_excavators[sq]['column']== square[1]:
                        excavators+=[sq] 
            # gives ores to the alone excavator 
            if nb_excavators == 1:
                for oid in asteroids:
                    if oid['r']== square[0] and oid['c']== square[1]:
                        if oid['nb_ores']>0:
                            if excavators[0] in blue_excavators:
                                name_ex= excavators[0] 
                                if (blue_excavators[name_ex]['tonnage']-blue_excavators[name_ex]['nb_ores'])>= (oid['tonnage']):
                                    if int(oid['nb_ores']) >= int(oid['tonnage']):
                                        if blue_excavators[name_ex]['tonnage'] >= (int(oid['tonnage'])+blue_excavators[name_ex]['nb_ores'] ):
                                            blue_excavators[name_ex]['nb_ores']+=  int(oid['tonnage'])
                                            oid['nb_ores']-= oid['tonnage']
                                        
                                    else:
                                        if int(oid['nb_ores']) == 1:
                                            if blue_excavators[name_ex]['tonnage'] >= (1 + blue_excavators[name_ex]['nb_ores']):
                                                blue_excavators[name_ex]['nb_ores']+=  1
                                                oid['nb_ores']-=1
                                                
                            else:
                                name_ex= excavators[0]
                                if (pink_excavators[name_ex]['tonnage']-pink_excavators[name_ex]['nb_ores'])>= (oid['tonnage']):
                                    if int(oid['nb_ores']) >= int(oid['tonnage']):
                                        if pink_excavators[name_ex]['tonnage'] >= (int(oid['tonnage'])+pink_excavators[name_ex]['nb_ores'] ):
                                            pink_excavators[name_ex]['nb_ores']+=  int(oid['tonnage'])
                                            oid['nb_ores']-= oid['tonnage']
                                    else:
                                        if int(oid['nb_ores']) == 1:
                                            if blue_excavators[name_ex]['tonnage'] >= (1 + blue_excavators[name_ex]['nb_ores']):
                                                pink_excavators[name_ex]['nb_ores']+=  1
                                                oid['nb_ores']-=1
                            
            # shares the ores to all excavators                                
            elif nb_excavators >1:
                for oid in asteroids:
                    if oid['r']== square[0] and oid['c']== square[1]:
                        if oid['nb_ores']>0:  
                            for exc in excavators:
                                if exc in blue_excavators:
                                    sum_tonnage += blue_excavators[exc]['tonnage']
                                elif exc in pink_excavators:
                                    sum_tonnage += pink_excavators[exc]['tonnage']
                            # shares the ores if the asteroid has enough ores for all the excavators
                            if sum_tonnage <= oid['nb_ores']:
                                for exca in excavators:
                                    if exca in blue_excavators:
                                        if (blue_excavators[exca]['tonnage']-blue_excavators[exca]['nb_ores'])>= oid['tonnage']:
                                            blue_excavators[exca]['nb_ores'] += oid['tonnage']
                                            oid['nb_ores']-= oid['tonnage']
                                            if blue_excavators[exca]['tonnage'] == blue_excavators[exca]['nb_ores']:
                                                print('Blue player, %s is full so you can release it' %(exca))
                                            
                                        else:
                                            blue_excavators[exca]['nb_ores']+= (blue_excavators[exca]['tonnage']-blue_excavators[exca]['nb_ores'])
                                            oid['nb_ores']-=(blue_excavators[exca]['tonnage']-blue_excavators[exca]['nb_ores'])
                                            print('Blue player, %s is full so you can release it' %(exca))
                                    elif exca in pink_excavators:
                                        if (pink_excavators[exca]['tonnage']-pink_excavators[exca]['nb_ores'])>= oid['tonnage']:
                                            pink_excavators[exca]['nb_ores'] += oid['tonnage']
                                            oid['nb_ores']-= oid['tonnage']
                                            if pink_excavators[exca]['tonnage'] == pink_excavators[exca]['nb_ores']:
                                                print('Pink player, %s is full so you can release it' %(exca))
                                        else:
                                            pink_excavators[exca]['nb_ores']+= (pink_excavators[exca]['tonnage']-pink_excavators[exca]['nb_ores'])
                                            oid['nb_ores']-=(pink_excavators[exca]['tonnage']-pink_excavators[exca]['nb_ores'])
                                            print('Pink player, %s is full so you can release it' %(exca))
                                            
                             # shares the ores if the asteroid hasn't enough ores for all the excavators                       
                            else:
                                exca = excavators[0]
                                if exca in blue_excavators:
                                    # shares the ores if the excavator has enough space to collect ores
                                    if (blue_excavators[exca]['tonnage']-blue_excavators[exca]['nb_ores'])>= ((oid['nb_ores'])/nb_excavators):
                                        blue_excavators[exca]['nb_ores']+= ((oid['nb_ores'])/nb_excavators)
                                        damage = ((oid['nb_ores'])/nb_excavators)
                                        oid['nb_ores']-=((oid['nb_ores'])/nb_excavators)
                                        if blue_excavators[exca]['tonnage'] == blue_excavators[exca]['nb_ores']:
                                            print('Blue player, %s is full so you can release it' %(exca))
                                            
                                    # shares the ores if the excavator hasn't enough space to collect ores   
                                    else:
                                        blue_excavators[exca]['nb_ores']+= (blue_excavators[exca]['tonnage']-blue_excavators[exca]['nb_ores']) 
                                        oid['nb_ores']-=(blue_excavators[exca]['tonnage']-blue_excavators[exca]['nb_ores'])
                                        damage = 0
                                        print('Blue player, %s is full so you can release it' %(exca))
                                           
                                 
                                elif exca in pink_excavators:
                                    # shares the ores if the excavator has enough space to collect ores
                                    if (pink_excavators[exca]['tonnage']-pink_excavators[exca]['nb_ores'])>= ((oid['nb_ores'])/nb_excavators):
                                        pink_excavators[exca]['nb_ores']+= ((oid['nb_ores'])/nb_excavators)
                                        damage = ((oid['nb_ores'])/nb_excavators)
                                        oid['nb_ores']-=((oid['nb_ores'])/nb_excavators)
                                        if pink_excavators[exca]['tonnage'] == pink_excavators[exca]['nb_ores']:
                                            print('Pink player, %s is full so you can release it' %(exca))
                                            
                                    # shares the ores if the excavator hasn't enough space to collect ores
                                    else:
                                        pink_excavators[exca]['nb_ores']+= (pink_excavators[exca]['tonnage']-pink_excavators[exca]['nb_ores']) 
                                        oid['nb_ores']-=(pink_excavators[exca]['tonnage']-pink_excavators[exca]['nb_ores'])
                                        damage=0
                                        print('Pink player, %s is full so you can release it' %(exca))
                            
                                for ex in excavators:
                                    if ex in blue_excavators:
                                        # shares the ores if the excavator has enough space to collect ores
                                        if (blue_excavators[ex]['tonnage']-blue_excavators[ex]['nb_ores'])>= damage and damage !=0:
                                            blue_excavators[ex]['nb_ores']+= damage
                                            oid['nb_ores']-= damage                                            
                                            if blue_excavators[ex]['tonnage'] == blue_excavators[ex]['nb_ores']:
                                                print('Blue player, %s is full so you can release it' %(ex))
                                        elif (blue_excavators[ex]['tonnage']-blue_excavators[ex]['nb_ores'])>= damage and damage ==0:
                                            blue_excavators[ex]['nb_ores']+= ((oid['nb_ores'])/nb_excavators)
                                            damage= ((oid['nb_ores'])/nb_excavators)
                                            oid['nb_ores']-=((oid['nb_ores'])/nb_excavators)
                                            if blue_excavators[ex]['tonnage'] == blue_excavators[ex]['nb_ores']:
                                                print('Blue player, %s is full so you can release it' %(ex))
                                        # shares the ores if the excavator hasn't enough space to collect ores
                                        else:
                                            blue_excavators[ex]['nb_ores']+= (blue_excavators[ex]['tonnage']-blue_excavators[ex]['nb_ores']) 
                                            oid['nb_ores']-=(blue_excavators[ex]['tonnage']-blue_excavators[ex]['nb_ores']) 
                                            print('Blue player, %s is full so you can release it' %(ex))
                                 
                                    elif ex in pink_excavators:
                                        # shares the ores if the excavator has enough space to collect ores
                                        if (pink_excavators[ex]['tonnage']-pink_excavators[ex]['nb_ores'])>= damage and damage !=0:
                                            oid['nb_ores']-=damage
                                            pink_excavators[ex]['nb_ores']+= damage
                                            if pink_excavators[ex]['tonnage'] == pink_excavators[ex]['nb_ores']:
                                                print('Pink player, %s is full so you can release it' %(ex))
                                        elif (pink_excavators[ex]['tonnage']-pink_excavators[ex]['nb_ores'])>= damage and damage ==0:
                                            pink_excavators[ex]['nb_ores']+= ((oid['nb_ores'])/nb_excavators)
                                            damage = ((oid['nb_ores'])/nb_excavators)
                                            oid['nb_ores']-=((oid['nb_ores'])/nb_excavators)
                                            if pink_excavators[ex]['tonnage'] == pink_excavators[ex]['nb_ores']:
                                                print('Pink player, %s is full so you can release it' %(ex))
                                        # shares the ores if the excavator hasn't enough space to collect ores
                                        else:
                                            pink_excavators[ex]['nb_ores']+= (pink_excavators[ex]['tonnage']-pink_excavators[ex]['nb_ores']) 
                                            oid['nb_ores']-=(pink_excavators[ex]['tonnage']-pink_excavators[ex]['nb_ores']) 
                                            print('Pink player, %s is full so you can release it' %(ex))
                                    
                        
    return asteroids, blue_excavators, pink_excavators              
                                
                       
def end(nb_turn, nb_ores_blue, nb_ores_pink, portals):
    """Controles if the game is finished or not.
    
    Parameters
    ----------
    nb_ores_pink: the number of ores that has the pink player (int)    
    nb_ores_blue: the number of ores that has the blue player (int)    
    portals: the dictionnary where the information of the portals comes from(dict)
    nb_turn: the number of turns without any damage(int)
    
    Return
    ------
    end_game: if the game is finished or not(bool)
    
    Version
    -------
    specification: Henriette Van Marcke (v.2 15/04/18)
    implementation: Henriette Van Marcke, Margot Kesch, Camille Mazuin (v.2 15/04/18)
    
    """
            
    nb_life_blue= portals['blue_portal']['life'] 
    nb_life_pink= portals['pink_portal']['life']

                
    if nb_turn == 200 or nb_life_blue <= 0 or nb_life_pink <=0:
        end_game = True 
        if nb_life_blue <= 0 and nb_life_pink > 0 :
            print("The pink player is the winner") 
        elif nb_life_pink <=0 and nb_life_blue >0 : 
            print ("The blue player is the winner")
        else:
            if nb_life_blue > nb_life_pink: 
                print ("The blue player is the winner")
            elif nb_life_blue < nb_life_pink:
                print("The pink player is the winner")  
            else: 
                if nb_ores_pink < nb_ores_blue:
                    print("The blue player is the winner")
                elif nb_ores_blue < nb_ores_pink:
                    print("The pink player is the winner")  
                else :
                    print('There is no winner')
    else:
        end_game= False 
    return end_game 
         



import socket
import time



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









start ('../maps/lost_temple.mw','138.48.160.140',1)
    

    

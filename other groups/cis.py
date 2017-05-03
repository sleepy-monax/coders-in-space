# -*- coding: utf-8 -*-

import random,string,termcolor,sys,os,time
from remote_play import *
print get_IP()
    
def cls():
    """ Clear the console.
    
    Note
    ----
    Author found on the internet.
    """
    os.system('cls' if os.name=='nt' else 'clear')

def tutorial():
    """ Print a tutorial.
    """

    print termcolor.colored('                                              __  _   _   __  _   __    ___         __ __   _   __  __                                                ','blue')
    print termcolor.colored('                                             /   / \ | \ |   | | |       |  \ |    |   | | / \ /   |                                                  ','blue')
    print termcolor.colored('                                             |   | | | | |-- |-  `-,     |  |\|    `-, |-  |-| |   |--                                                ','blue')
    print termcolor.colored('                                             \__ \_/ L_/ |__ | \ __|    _|_ | |    __| |   | | \__ |__                                                ','blue')
    print termcolor.colored('                                                           ___     ___  _   _  ___  _                                                                 ','blue')
    print termcolor.colored('                                                            |  | |  |  / \ | |  |  / \ |                                                              ','blue')
    print termcolor.colored('                                                            |  | |  |  | | |-   |  |-| |                                                              ','blue')
    print termcolor.colored('                                                            |  \_/  |  \_/ | \ _|_ | | L__                                                                ','blue')
    print termcolor.colored('                                                                                                                                                      ','blue')
    print termcolor.colored('------------------------------------------------------------------------------------------------------------------------------------------------------','blue')
    print '                                                                                                                                                      '
    print termcolor.colored('    How to play                                                                                                                                       ','cyan')
    print termcolor.colored('    -----------                                                                                                                                       ','cyan')
    print '             - To buy your ships use <ship_name_1>:<ship_type> <ship_name_2>:<ship_type>...       Example: X-Wing:fighter Unicorn:destroyer           '
    print '             - To give orders to your ships use <ship_name_1>:<order_1> <ship_name_2>:<order_2>   Example: X-Wing:faster Unicorn:left                 '
    print '                    The orders are: - faster: increase your speed by 1     - slower: reduce you speed by 1                                             '
    print '                                    - right: increase your direction by 1  - left: reduce your direction by 1                                         '
    print '                                    - x-y: shoot on the coordinates (x,y)                                                                             '
    print '                                                                                                                                                      '
    print termcolor.colored('    Directions             Interface                                                                                                                  ','cyan')
    print termcolor.colored('    ----------             ---------                                                                                                                  ','cyan')
    print '     8  1  2                        - Player_1\'s ships are green       - If there is only 1 ship on a case the first letter of his type is printed   '
    print '      \ | /                         - Player_2\'s ships are red         - If there are more than 1 ship on a case the number of ships is printed      '
    print '    7 --+-- 3                       - Abandonned ships are light blue   - If there are two players on the same case, the case is blue                 '
    print '      / | \                                                                                                                                           '
    print '     6  5  4                                                                                                                                          '
    print '                                                                                                                                                      '
    print termcolor.colored('    End of the game                                                                                                                                   ','cyan')
    print termcolor.colored('    ---------------                                                                                                                                   ','cyan')
    print '             - A player wins if he killed all his opponent\'s ships                                                                                   '
    print '             - Game end if 10 turns happened without any succesfull shot: - The player with the highest value in ships wins                           '
    print '                                                                          - In case of equality a random player wins                                  '
    print '                                                                                                                                                      '
    print termcolor.colored('    Ships informations                                                                                                                                ','cyan')
    print termcolor.colored('    ------------------                                                                                                                                ','cyan')
    print '                                                                                                                                                      '
    print '             Type     Max.speed  Health  Attack  Scope  Cost                                                                                          '
    print '         ----------------------------------------------------                                                                                         '
    print '         Fighter       |  5   |    3   |   1   |   5   | 10                                                                                           '
    print '         Destroyer     |  2   |    8   |   2   |   7   | 20                                                                                           '
    print '         Battlecruiser |  1   |    20  |   4   |   10  | 30                                                                                           ' 
    print '                                                                                                                                                      '
    print termcolor.colored('                                                                Press enter to start                                                                  ','green')

def start_game(player_1,player_2,file_name):
    """ Run the game.
    
    Parameters
    ----------
    player_1: type of player ('human' or 'ai' or 'distant') (str)
    player_2: type of player ('human' or 'ai' or 'distant') (str)
    file_name: name of the file to read for the ships and the board (str)
    
    Notes
    -----
    The name of the file must end with '.cis'
    
    Versions
    --------
    specification: Antoine Petit, Gilles Dejardin, Etienne Robert (V.1 07/02/17)
    implementation: Antoine Petit, Gilles Dejardin, Etienne Robert (V.2 24/02/17)
    """
    
    cls()
    tutorial()
    raw_input('')
    cls()
    
    connection = None
    if player_1 != 'human' and player_1 != 'ai':
        connection = connect_to_player(1,player_1)
    elif player_2 != 'human' and player_2 != 'ai':
        connection = connect_to_player(2,player_2)
        
    game = create_game(player_1,player_2,file_name)
    game = buy_ships('1',connection,game)
    game = buy_ships('2',connection,game)

    print("\033[0;0H"),
    print_board(game)
    
    while not game_finish(game):
        #time.sleep(0.25)
        
        game,list_to_shoot_1,list_damages_1 = ask_order('1',connection,game)        
        game,list_to_shoot_2,list_damages_2 = ask_order('2',connection,game)
        
        list_to_shoot = list_to_shoot_1 + list_to_shoot_2
        list_damages = list_damages_1 + list_damages_2        
        
        game = move(game)
        game = deal_damages(game,list_to_shoot,list_damages)
        print("\033[0;0H"),
        print_board(game)
        
    print 'Game Over!'
    
    if connection != None:
        disconnect_from_player(connection)
        

def create_game(player_1,player_2,file_name):
    """ Create the dictionnary which contains all the informations about the game.
    
    Parameters
    ----------
    player_1: type of the player 1 (human/AI/distant) (str)
    player_2: type of the player 2 (human/AI/distant) (str)
    file_name: name of the file with the board size and the ships (str)
    
    Return
    ------
    game: All the informations about the game. (dict)
    
    Notes
    -----
    The height and the width of the board are in file_name.    
    
    Versions
    --------
    specification: Antoine Petit, Gilles Dejardin, Etienne Robert (V.1 07/02/17)
    implementation: Antoine Petit, Gilles Dejardin, Etienne Robert (V.1 07/02/17)
    """    
    # create the dictionnary
    game = {'board':{},
            'ships':{'0':{},
                     '1':{},
                     '2':{}},
            'ships_left':{'1':0,
                          '2':0},
            'ships_infos':{'fighter':{'speed':5,'health':3,'attack':1,'scope':5,'cost':10},
                           'destroyer':{'speed':2,'health':8,'attack':2,'scope':7,'cost':20},
                           'battlecruiser':{'speed':1,'health':20,'attack':4,'scope':10,'cost':30}},
            'no_touch':0,
            'board_size':{'height':0,
                          'width':0},
            'players_types':{'1':player_1,
                             '2':player_2}}
    
    # get the board size, create the cases and put them in the dictionnary
    # read the file
    fh = open(file_name,'r')
    save = fh.readlines()
    size_board = save[0]
    fh.close()
    
    # extract the height and the width
    for i in size_board:
        if i == ' ':
            space = size_board.index(i)
    height = int(size_board[:space])
    width = int(size_board[space+1:])
    
    
    game['board_size']['height'] = height
    game['board_size']['width'] = width
    
    # create the cases        
    for y in range(1,width+1):
        for x in range(1,height+1):
            case = (x,y)
            game['board'][case] = []            
    
    game = place_abandonned_ships(file_name,game)
    print("\033[0;0H"),
    print_board(game)
    return game

def print_board(game):
    """ Print the board with the ships and the informations about each ships on the side and under the board.
    
    Parameters
    ----------
    game: all the informations about the game (dict)
    
    Versions    
    --------
    specification: Etienne Robert (V.1 17/02/17)
    implementation: Etienne Robert (V.2 24/03/17)
    """   
    board = game['board']
    
    height = game['board_size']['height']
    width = game['board_size']['width']
    
    # print the y indexes
    print termcolor.colored('  ',None,'on_white'),
    sys.stdout.softspace=0
    for y in range(1,width+1):
        if y%2 == 0:
            color = 'on_white'
        else:
            color = 'on_yellow'
        if y<10:
            print termcolor.colored('%d ' % y,'blue',color),
            sys.stdout.softspace=0
        else:
            print termcolor.colored(y,'blue',color),
            sys.stdout.softspace=0
    print '    Name|Type|Coo.|HP|Speed|Dir.'
    
    # stock all the ships infos
    ships_infos = []
    ships_infos_2 = []
    for player in game['ships']:
        for ships in game['ships'][player]:
            infos = ('%s %s %s %d %d %d' %(ships,game['ships'][player][ships]['type'][:1],game['ships'][player][ships]['position'],game['ships'][player][ships]['health'],game['ships'][player][ships]['speed'],game['ships'][player][ships]['direction']),player)
            ships_infos.append(infos)
    
    if len(ships_infos) > 40:
        ships_infos_2 = ships_infos[40:]
        
    ship_to_print_index = 0
    max_index = len(ships_infos) - 1
        
    # print the x indexes
    for x in range(1,height+1):
        if x%2 == 0:
            color = 'on_white'
        else:
            color = 'on_yellow'
        if x<10:
            print '',
            print termcolor.colored('%d ' % x,'blue',color),
            sys.stdout.softspace=0
        else:
            print '',
            print termcolor.colored(x,'blue',color),
            sys.stdout.softspace=0
        
        for y in range(1,width+1):
            
            # print a letter if there is only one ship on the case
            if len(board[(x,y)]) == 1:
                ship_name = board[(x,y)][0]
                
                if ship_name in game['ships']['0'] and game['ships']['0'][ship_name]['position'] == (x,y):
                    print_a_ship(game,'0',ship_name)
                if ship_name in game['ships']['1'] and game['ships']['1'][ship_name]['position'] == (x,y):
                    print_a_ship(game,'1',ship_name)
                if ship_name in game['ships']['2'] and game['ships']['2'][ship_name]['position'] == (x,y):
                    print_a_ship(game,'2',ship_name) 
            
            # print the number of ships on the case if it is more than one
            elif len(board[(x,y)]) > 1:
                if len(board[(x,y)]) < 10:
                    text = '%d ' % len(board[(x,y)])
                else:
                    text = len(board[(x,y)])
                
                players_on_position = []
                for player in game['ships']:
                    for ship in game['ships'][player]:
                        if game['ships'][player][ship]['position'] == (x,y) and not player in players_on_position:
                            players_on_position.append(player)
                if players_on_position == ['1']:
                    print termcolor.colored(text,None,'on_green'),
                    sys.stdout.softspace=0
                elif players_on_position == ['2']:
                    print termcolor.colored(text,None,'on_red'),
                    sys.stdout.softspace=0
                else:
                    print termcolor.colored(text,None,'on_blue'),
                    sys.stdout.softspace=0
                    
            # print empty case
            else:
                print '. ',
                sys.stdout.softspace=0
        
        # print ships infos on the side        
        if ship_to_print_index <= max_index:
            if ships_infos[ship_to_print_index][1] == '1':
                print termcolor.colored('    %s' % ships_infos[ship_to_print_index][0],'green'),
                print ' '*15,
                sys.stdout.softspace=0
            elif ships_infos[ship_to_print_index][1] == '2':
                print termcolor.colored('    %s' % ships_infos[ship_to_print_index][0],'red'),
                print ' '*15,
                sys.stdout.softspace=0
            else:
                print termcolor.colored('    %s' % ships_infos[ship_to_print_index][0],'cyan'),
                print ' '*15,
                sys.stdout.softspace=0
            ship_to_print_index += 1
        
        else:
            print ' '*40,

        print ' '
     
    # print ships infos under 
    
    #clear the area
    line = game['board_size']['height']+2
    text = ' '*190
    while line < 50:
        print("\033[%d;0H%s" % (line,text)),
        line += 1
           
    if ships_infos_2 != []:
        
        index = 0
        line_index = game['board_size']['height'] +2
        print("\033[%d;1H") % line_index,  
        while index < len(ships_infos_2):
            if index % 5 == 0:
                print ' '
            if ships_infos_2[index][1] == '1':
                print termcolor.colored(ships_infos_2[index][0],'green'),
                print '\t',
            elif ships_infos_2[index][1] == '2':
                print termcolor.colored(ships_infos_2[index][0],'red'),
                print '\t',
            else:
                print termcolor.colored(ships_infos_2[index][0],'cyan'),
                print '\t',
            index += 1
        
        print ' '

def print_a_ship(game,player,ship_name):
    """ Print a ship.
    
    Parameters
    ----------
    game: All the informations about the game. (dict)
    player: The player who own the ship. (str)
    ship_name: Name of the ship. (str)
    
    Versions
    --------
    specification: Etienne Robert (V.1 01/03/17)
    implementation: Etienne Robert (V.1 01/03/17)
    """    
    ship_type = game['ships'][player][ship_name]['type']
        
    if ship_type == 'battlecruiser':
        text = 'B '
    elif ship_type == 'destroyer':
        text = 'D '
    else:
        text = 'F '
        
    if player == '1':
        print termcolor.colored(text,None,'on_green'),
        sys.stdout.softspace=0
    elif player =='2':
        print termcolor.colored(text,None,'on_red'),
        sys.stdout.softspace=0
    elif player == '0':
        print termcolor.colored(text,None,'on_cyan'),
        sys.stdout.softspace=0
    
def buy_ships(player,connection,game):
    """ Buy the ships for a given player.
    
    Parameters
    ----------
    player: Player who buys ships (str)
    connection: connection to player
    game: All the informations about the game. (dict)
    
    Return
    ------
    game: All the informations about the game. (dict)
    
    Versions
    --------
    specification: Etienne Robert (V.1 18/02/17)
    implementation: Etienne Robert (V.1 18/02/17)
    """
    
    player_type = game['players_types'][player]
    
    if player_type == 'ai':
        purchases = ia_ships (player,connection,game)        
    
    elif player_type == 'human':
        print("\033[49;1H"),        
        purchases = raw_input('Player %s, what would you like to buy? ' % player)
    
    else:
        purchases = get_remote_orders(connection)
        
    # extract informations from the answer
    purchase = purchases.split()    

    credits = 100
    for ship in purchase:
        for letter in ship:
            if letter == ':':
                double_point = ship.index(letter)
                name = ship[:double_point]
                ship_type = ship[double_point+1:]
    
        # check credits
        credits_ok = True
        if ship_type == 'battlecruiser' and credits >= 30:
            credits -= 30
        elif ship_type == 'destroyer' and credits >= 20:
            credits -= 20
        elif ship_type == 'fighter' and credits >= 10:
            credits -= 10
        else:
            credits_ok = False
                
        # check name
        name_ok = True
        if name in game['ships'][player]:
            name_ok = False    
            
        # put ship in the save
        if name_ok and credits_ok:
            if player == '1':
                direction = 4
                position = (10,10)
                game['board'][position].append(name)
            else:
                direction = 8
                height = game['board_size']['height']
                width = game['board_size']['width']
                position = (height-9,width-9)
                game['board'][position].append(name)
        
            game['ships'][player][name] = {'type':ship_type, 'health':game['ships_infos'][ship_type]['health'], 'speed':0, 'direction':direction, 'position':position}
            game['ships_left'][player] += 1
    
    if player == '1' and (game['players_types']['2'] not in ('human','ai')) or player == '2' and (game['players_types']['1'] not in ('human','ai')):
        notify_remote_orders(connection,purchases)
        
    return game 

def remove_ship(game):
    """ Remove a ship of the dictionnary and so, of the board, if it is destroyed.
    
    Parameters
    ----------
    game: Information about all the game. (dict)    
    
    Return
    ------
    game: All the informations about the game. (dict)
    
    Version
    -------
    specification: Gilles Dejardin (V.2 24/03/17)
    implementation: Gilles Dejardin,Antoine Petit (V.1 17/02/17)
    """
    dead_ships=[]
    for player in game['ships']:
        if player != '0':
            for ship in game['ships'][player]:
                if game['ships'][player][ship]['health']<=0:
                    dead_ships+= [(player,ship)]
                    
    for to_remove in dead_ships:
        player = to_remove[0]        
        ships = to_remove[1]
        position = game['ships'][player][ships]['position']
        del game['ships'][player][ships]
        game['board'][position].remove(ships)
        game['ships_left'][player]-=1
    return game 
    
def move (game):
    """ Move all the ships on the board according to their speed and their direction and save their new position.
    Parameters
    ----------
    game: All the informations about the game. (dict)
    
    Return
    ------
    game: All the informations about the game. (dict)    
    
    Version
    -------
    specification: Antoine Petit (V.1 17/02/17)
    implementation: Antoine Petit (V.2 28/02/17)
    """  
         
    height = game['board_size']['height']
    width = game['board_size']['width']
    for player in game['ships']:
        if player != '0':
            for name in game['ships'][player]: 
                    
                speed=game['ships'][player][name]['speed']
                coo= game['ships'][player][name]['position']  
                game['board'][coo].remove(name)                                             
                x=coo[0]
                y=coo[1]
                        
                if game['ships'][player][name]['direction'] in (2,3,4):                        
                    y+=speed
                        
                if game['ships'][player][name]['direction'] in (1,2,8):                                            
                    x-= speed
                    
                if game['ships'][player][name]['direction'] in (6,7,8):                    
                    y-= speed
                        
                if game['ships'][player][name]['direction']in (4,5,6):                    
                    x+= speed
                
                if x > height:
                    x-= height            
                if y > width:        
                    y-=width            
                if x <= 0:          
                    x += height           
                if y <= 0:               
                    y += width           
            
                n_coo=(x,y) 
                game['board'][n_coo].append(name)
                game['ships'][player][name]['position']=n_coo
    game = capture(game)
    
    return game
    
def rotate_ship(player,name,turn,game):
    """ Rotate a ship of 1 in the clockwise direction or in the anti-clockwise direction.
    
    Parameters
    ----------
    player: The player who is playing (str)
    name: Name of the ship to rotate. (str)
    turn: Right or left. (str)
    game: All the informations about the game. (dict)
    
    Returns
    -------
    game: All the informations about the game. (dict)
    
    Versions
    --------
    specification: Etienne Robert (v1 17/02/17)
    implementation: Etienne Robert (v1 17/02/17)
    """    
    if turn != 'left' and turn != 'right':
        print 'Invalid direction (use left or right)'
        return False
    
    else:
        direction = game['ships'][player][name]['direction']
        
        if turn == 'left':
            direction -= 1
            if direction == 0:
                direction = 8
        else:
            direction += 1
            if direction == 9:
                direction = 1
                
        game['ships'][player][name]['direction'] = direction
        
    return game
        
def shoot (player,order,name,game) :
    """
    Allow to a ship to shoot according to its scope and make damages to others ships. 
    
    Parameters
    ----------
    player: The player who want to shoot.(str)
    order: The order currently executed.(str)
    name: The name of the ship which ask the order.(str)
    game: All the informations about the game. (dict)
    
    Notes
    -----    
    It is possible to shoot less far than the scope (the scope is a zone not a perimeter)
    
    Return
    ------
    game: All the informations about the game.(dict)
    to_shoot: The coordonate where you want to shoot.(tuple)
    damges: The damages wich will be dealed to a ship according to the type of boat which shoot.(int)
    
    Version
    -------
    specification: Antoine Petit (19/02/17)
    implementation: Antoine Petit (24/02/17)
    """  
    for letter in order :
            
        if letter == '-':
            less = order.index(letter)
            
            x = int(order[:less])
            y = int(order[less+1:])                
            
            to_shoot= (x,y)
            
            position= game['ships'][player][name]['position']             
            ship_type = game['ships'][player][name]['type']
            scope = game['ships_infos'][ship_type]['scope']            
            height = game['board_size']['height']
            width = game['board_size']['width']
            
            coo= give_coo(position,scope,height,width)
            if to_shoot not in coo:
                print '%s Sorry out of range' % name
                damages=0               
            
            else:                 
                damages = game['ships_infos'][ship_type]['attack'] 
                                                                                   
    return game,to_shoot,damages

def ask_order(player,connection,game):
    """ Asks to the player what order he wants to do and executes it.
        It verifies also if the player the AI do not give an order to a ship of the opponent.
    
    Parameters
    ----------
    player: Player who plays. (str)
    connection: connection to player
    game: All the informations about the game. (dict)
  
    Note
    ----
    Only one order by ship.
    
    Version
    -------
    specification: Gilles Dejardin (V2. 24/03/17)
    implementation: Gilles Dejardin, Antoine Petit, Etienne Robert (V1. 19/02/17)
    """
    if game['players_types'][player] == 'human':
        print("\033[49;1H"),     
        orders = raw_input('Player %s what must do your ships? ' % player)
    elif game['players_types'][player] == 'ai':
        orders = get_ia_orders(game,player)
    else:
        orders = get_remote_orders(connection)
    
    list_to_shoot = []
    list_damages = []
    if len(orders) >0:
        orders_list, names_list = order_name_lists(orders)
        
        for element in range (len(orders_list)):
            order = orders_list[element]
            name = names_list[element]
            
            if name not in game['ships'][player]:
                print 'player %s,the ship %s doesn\'t exist or is not your ship.' % (player,name)
            elif '-' in order :
                game,to_shoot,damages = shoot(player,order,name,game)

                list_to_shoot.append(to_shoot)
                list_damages.append(damages) 
                                
            elif order == 'faster':
                game = accelerate(name,game,player)
            elif order == 'slower':
                game = brake(name,game,player)
            elif order == 'left':
                game = rotate_ship(player,name,'left',game)
            elif order == 'right':
                game = rotate_ship(player,name,'right',game)
            elif order not in ('faster','slower','left','right'):
                print 'sorry %s is not an order' % order
    else:
        print 'player %s, You skiped your turn' % player
        
    if player == '1' and (game['players_types']['2'] != 'human' and game['players_types']['2'] != 'ai') or player == '2' and (game['players_types']['1'] != 'human' and game['players_types']['1'] != 'ai'):
        notify_remote_orders(connection,orders)
       
    return game,list_to_shoot,list_damages 
    
def order_name_lists(orders):
    """ With the string of the orders, create two lists. One for the order and one for the name.
        It verifies also if the player or the AI do not give more than one order to the same ship.
    
    Parameters
    ----------
    orders: All the orders enter by the player. (str)
    
    Return
    ------
    orders_list: The different order into a dico. (list)
    names_list: The different ship which receive an order. (list)
    
    Version
    -------
    specification: Gilles Dejardin (V2. 24/03/2017)
    implementation: Gilles Dejardin (V1. 18/02/2017)
    """
    orders_list = []
    names_list = []
    for element in orders:
        if element == ' ':
            one_order = orders[:orders.index(' ')]
            name = one_order[:string.find(one_order,':')]
            if not name in names_list:
                names_list.append(name)
                orders_list.append(one_order[string.find(one_order,':')+1:])
            orders = orders[orders.index(' ')+1:]
    name = orders[:string.find(orders,':')]
    if not name in names_list:
        names_list.append(name)
        orders_list.append(orders[string.find(orders,':')+1:])
    return orders_list, names_list
            
def accelerate(name,game,player):
    """ Increase the speed of the ship.
    
    Parameters
    ----------
    name: Name of the ship. (str)
    game: All the informations about the game. (dict)
    player: Player who plays. (str)
    
    Return
    ------
    game: all the informations about the game (dict)
    
    Version
    -------
    specification : Gilles Dejardin (V1. 19/02/2017)
    implementation : Gilles Dejardin (V1. 19/02/2017)
    """

    ship_type = game['ships'][player][name]['type']
    ship_speed = game['ships'][player][name]['speed']
    
    if ship_type == 'battlecruiser':
        if ship_speed == 0:
            game['ships'][player][name]['speed'] = 1
           
        else:
            print 'Player %s, your Battlecruiser %s can\'t go faster because it advances with his biggest speed.' % (player,name)           
            
    elif ship_type == 'destroyer':
        if ship_speed == 2:
            print 'Player %s, your Destroyer %s can\'t go faster because it advances with his biggest speed.' % (player,name) 
            
        else:
            game['ships'][player][name]['speed'] += 1
                        
    else:
        if ship_speed == 5:
            print 'Player %s, your Fighter %s can\'t go faster because it advances with his biggest speed.' % (player,name) 
          
        else:
            game['ships'][player][name]['speed'] += 1
            
    return game

def brake(name,game,player):
    """ Decrease the speed of the ship.
    
    Parameters
    ----------
    name: Name of the ship. (str)
    game: All the informations about the game. (dict)
    player: Player who plays. (str)
    
    Return
    ------
    game: All informations about the game (dict)
    
    Version
    -------
    specification: Gilles Dejardin (V1. 19/02/2017)
    implementation: Gilles Dejardin (V1. 19/02/2017)
    """
        
    if game['ships'][player][name]['speed'] > 0:
        game['ships'][player][name]['speed']-=1
        
    else:
        print 'Player %s, Your ship %s can brake because it is stopped.' % (player,name)
         
    return game
    
def game_finish(game):
    """ Check if the game is finished.
    
    Returns
    -------
    finish: True if the game is finished, False otherwise. (bool)
    
    Version
    -------
    specification: Etienne Robert (V.1 24/02/17)
    implementation: Etienne Robert (V.1 24/02/17)
    """
    
    print("\033[47;0H"),
    sys.stdout.softspace=0
    
    if game['ships_left']['1'] == 0:
        print 'Player 2 won!'
    
    elif game['ships_left']['2'] == 0:
        print 'Player 1 won!'
   
    elif game['no_touch'] == 15:
        print '15 turns happened without any ship touched.'
        value_1 = 0
        value_2 = 0
        
        for ship in game['ships']['1']:
            ship_type = game['ships']['1'][ship]['type']
            value_1 += game['ships_infos'][ship_type]['cost']
        
        for ship in game['ships']['2']:
            ship_type = game['ships']['2'][ship]['type']
            value_2 += game['ships_infos'][ship_type]['cost']
        
        if value_1 > value_2:
            print 'Player 1 won by value!'
        
        elif value_2 > value_1:
            print 'Player 2 won by value!'
        
        else:
            print 'Equality of value!'
            winner = random.randint(1,2)
            if winner == 1:
                print 'Player 1 won by random!'
            else:
                print 'Player 2 won by random!'            
    
    else:
        return False
    return True
    
def deal_damages(game,list_to_shoot,list_damages):
    """
    Deal the damages to a ship if the ship is touched and remove it if it's destroyed.
    
    Parameters
    ----------
    game: All information about the game.(dict)
    list_to_shoot: The list of coordonnate where you want to shoot.(list)
    list_damages: The list of damages you want to deal on a specific coordonate.(list)
    
    Notes
    -----
    list_damages and list_to_shoot must have the same lenght.
    It is possible to damage friends ships but not abandoned ships.
    
    Return
    ------
    game: All informations about the game.(dict)
    
    Version
    -------
    Specification: Antoine Petit (V.1 03/03/17)
    Implementation: Antoine Petit, Robert Etienne (V.1 03/03/17)
    """
    remove =False
    no_touch = True
    for shoot in list_to_shoot:
        index = list_to_shoot.index(shoot)
        
        for player in game['ships']:
            if player != '0':
                
                for ship in game['ships'][player]:
                    if game['ships'][player][ship]['position'] == shoot:
                        
                        game['ships'][player][ship]['health'] -= list_damages[index]
                        no_touch = False
                        
                        if game['ships'][player][ship]['health']<=0:
                            
                            remove= True
    if remove:
        game=remove_ship(game)
   
    if no_touch:
        game['no_touch'] += 1
    else:
        game['no_touch'] =0
  
    return game
    
def place_abandonned_ships(file_name,game):
    """
    Place the abandonned ships wich are in a file .cis in the key player '0'
    
    Parameters
    ----------
    game: All the informations about the game. (dict)
    
    Return
    ------
    game: All the informations about the game. (dict)    
    
    Version
    -------
    specification: Antoine Petit (V.1 23/02/17)
    implementation: Antoine Petit (V.1 23/02/17)
    """  
    
    fh = open(file_name,'r')
    info = fh.readlines()
    
    fh.close()
    info = info[1:]
    
    for element in info:
        infos=element.split()
        
        x=int(infos[0])
        y=int(infos[1])
        position =(x,y)
        for letter in infos[2]:
            if letter==':':
                double_point = infos[2].index(letter)
                
                name= infos[2][:double_point]
                
                ship_type=infos[2][double_point+1:]
                direction=infos[3]               
                
                if direction =='up':
                    direction=1       
                elif direction =='up-right':
                    direction=2        
                elif direction =='right':
                    direction=3
                elif direction =='down-right':
                    direction=4
                elif direction =='down':
                    direction=5
                elif direction =='down-left':
                    direction=6
                elif direction =='left':
                    direction=7
                else: 
                    direction=8                 
                    
                game['ships']['0'][name]={'type':ship_type, 'health':game['ships_infos'][ship_type]['health'], 'speed':0, 'direction':direction, 'position':position}
                
                game['board'][position]+=[name]
               
    return game
    
def capture (game):
    """ Capture an abandoned ship if a player's ship is on the same case.
    
    Parameters
    ----------
    game: All the informations about the game. (dict)
    
    Return
    ------
    game: All the informations about the game. (dict)
    
    Version
    -------
    specification: Etienne Robert (V.1 15/02/17)
    implementation: Etienne Robert,Antoine Petit (V.2 15/02/17)
    """
    abandonned_ships= []
    for ships in game['ships']['0']:
        abandonned_ships.append(ships)
    
    to_capture=[]   
    for ab_ships in abandonned_ships:
        direction=game['ships']['0'][ab_ships]['direction']
        name= ab_ships
        ship_type=game['ships']['0'][ab_ships]['type']       
        position = game['ships']['0'][ab_ships]['position']                
        
         
        for player in game['ships']:
            if player != '0':                 
                for ship in game['ships'][player]:
                    
                    if name in game['ships'][player]:                       
                        name +='_2'
                    
                    if game['ships'][player][ship]['position']== position and is_capture_ok(game,position) :                                                   

                        info=(player,ab_ships,direction,name,ship_type,position)                      
                                                                                
                        #allow to capture even if more than one ships of the same player are on the position.
                        if info not in to_capture:  
                            to_capture +=[info]                       
                                                     
                                
    for infos in to_capture:
        player= infos[0]
        ab_ships= infos[1]        
        direction=infos[2]
        name=infos[3]
        ship_type=infos[4]
        position=infos[5]
        
        del game['ships']['0'][ab_ships]
        game['ships'][player][name]= {'type':ship_type, 'health':game['ships_infos'][ship_type]['health'], 'speed':0, 'direction':direction, 'position':position}
        game['ships_left'][player]+=1
        game['board'][position].remove(ab_ships)
        game['board'][position].append(name)
    
    return game
    
def is_capture_ok(game,position):
    """ Ckeck if there are an ennemi's ship and a friend's ship on the position of the abandonned ship
    
    Parameters
    ----------
    game: All the informations about the game. (dict)
    position: The position to check (tuple)
    
    Return
    ------
    capture: True if the player capture the abandonned ship, False otherwise
    
    Version
    -------
    specification: Antoine Petit (V.1 04/03/17)
    implementation: Antoine Petit (V.1 04/03/17)
    """

    player_on_position=[]
    if len(game['board'][position])>2:
        for player in game['ships']:
            if player != '0':
                for ship in game['ships'][player]:
                    if game['ships'][player][ship]['position']==position:
                        player_on_position+=[player]
                        
    if '1' in player_on_position and '2' in player_on_position:
        return False       
    else:
        return True 

def ia_ships (player,connection,game):
    """
    Chose randomly the type and the name of ships of the IA 
    
    Parameters
    ----------
    player:Player one or two.(str)
    connection: connection to the player
    game: All informations about the game.(dict)
    
    Retruns
    -------
    game: All informations about the game.(dict)

    Versions    
    --------
    specification: Antoine Petit(V.1 14/03/17)
    implementation: Antoine Petit (V.1 14/03/17)
    """ 
    
    name =['Unicorn','Hodor','Speedy','Groot','Petite_perruche','Aniiiick','Ramsay_Bolton','uNoob',
           'Dominek','Claudy','Kikinu','2good4u','xXkevindu38Xx','Mµ','Josay','Biloute','KeepCalm',
           'Findus','OVNI','Lamasticot','Perdu!','ShootingStar','YourMother','HisFather','Error',
           'Bug','Malhonnete','YeParleMips','Amiiii','IHaveAPen','IHaveAnApple','ApplePen','Mifi',
           '404_not_found','Bubulle','The_Simpsons','Dieu','TheMessy','Barracuda','Darla','Olaf',
           'R2-D2','C-3PO','BB-8','Yoda','Eddy_Malou','Abu_Ramal','Kaniel_Outis','Sylvain_Duriff','Niente_Problem'] 
    to_buy =''
    ship_to_buy=['battlecruiser','destroyer','destroyer','fighter','fighter','fighter']
     
    for ship_type in ship_to_buy:
        
        ship = random.choice(name)        
        name.remove(ship)
        one_ship= ship+':'+ship_type        
        to_buy += one_ship+' '
    return to_buy[:-1]      
    
def get_ia_orders(game,player):
    """
    return the order of the IA
    
    Parameters
    ----------
    player:Player one or two.(str)
    game: All informations about the game.(dict)
    
    Retruns
    -------
    orders: The orders given by the IA.(str)

    Versions    
    --------
    specification: Antoine Petit(V.1 14/03/17)
    implementation: Antoine Petit, Robert Etienne (V.2 30/04/17)
    """ 

    orders=''

    # get player's ships
    ships=[]
    
    for ship in game['ships'][player]:
        ships.append(ship) 

    # get all ranges of opponent's ships
    if player == '1':
        opponent = '2'
    else:
        opponent = '1'

    opponent_ships = []
    for ship in game['ships'][opponent]:
        opponent_ships.append(ship)
    opponent_ranges = []
    height = game['board_size']['height']
    width = game['board_size']['width']

    for ship in opponent_ships:
        position = game['ships'][opponent][ship]['position']
        ship_type = game['ships'][opponent][ship]['type']
        scope = game['ships_infos'][ship_type]['scope']
        opponent_ranges.append(give_coo(position,scope,height,width))

    # get abandonned ships
    abandonned_ships = []
    for ship in game['ships']['0']:
        abandonned_ships.append(ship)

    # get values
    player_value = 0
    for ship in ships:
        ship_type = game['ships'][player][ship]['type']
        player_value += game['ships_infos'][ship_type]['cost']
    opponent_value = 0
    for ship in opponent_ships:
        ship_type = game['ships'][opponent][ship]['type']
        opponent_value += game['ships_infos'][ship_type]['cost']
    auto_shoot = False

    # decide order for each ship
    for ship in ships:
        
        # get infos
        ship_type = game['ships'][player][ship]['type']
        position = game['ships'][player][ship]['position']
        scope = game['ships_infos'][ship_type]['scope']
        speed = game['ships'][player][ship]['speed']
        to_shoot = give_coo(position,scope,height,width)
        possible_position = give_proba(game,player,to_shoot)

        # get the closest abandonned and closest opponent
        if abandonned_ships != []:
            closest_abandonned,distance_abandonned = get_closest_ship(game,abandonned_ships,'0',position)
        if opponent_ships != []:
            closest_opponent,distance_opponent = get_closest_ship(game,opponent_ships,opponent,position)
        
        # check if ship in opponent's range
        ship_vulnerable = False
        for opponent_ship in opponent_ships:
            index = opponent_ships.index(opponent_ship)
            if position in opponent_ranges[index]:
                ship_vulnerable = True

        if not (auto_shoot) and game['no_touch'] == 9 and ship_type == 'fighter' and player_value < opponent_value:
            y = position[0]
            x = position[1]
            if game['ships'][player][ship]['direction'] in (2,3,4): 
                y += speed
            if game['ships'][player][ship]['direction'] in (1,2,8):
                x -= speed
            if game['ships'][player][ship]['direction'] in (6,7,8):
                y -= speed
            if game['ships'][player][ship]['direction']in (4,5,6):
                x += speed

            if y < 1:
            	y += height
            elif y > height:
            	y -= height
            if x < 1:
            	x += width
            elif x > width:
            	x -= width

            possible_position = [(y,x)]
            order = 'shoot'
            auto_shoot = True

        # faster if speed == 0
        elif speed == 0:
            order = 'faster'

        # shoot if necessary
        elif len(possible_position) > 0 and (ship_type != 'fighter' or (ship_type == 'fighter' and abandonned_ships == [])):
            order = 'shoot'
        
        # capture if necessary
        elif abandonned_ships != [] and distance_abandonned < 11 and (ship_type != 'battlecruiser' or (ship_type == 'battlecruiser' and distance_abandonned <= 2)):

            destination = game['ships']['0'][closest_abandonned]['position']
            # remove it from abandonned to not have more than 1 ship for the same abandonned
            i = abandonned_ships.index(closest_abandonned)
            del abandonned_ships[i]
            # move to it
            order = go_somewhere(game,ship,player,destination)

        # random if ship in opponent's range
        elif ship_vulnerable:
            order = random_order(game,speed,ship_type)

        elif distance_opponent < 16:
            destination = game['ships'][opponent][closest_opponent]['position']
            order = go_somewhere(game,ship,player,destination)

        else:
            order = random_order(game,speed,ship_type)

        # make orders with the name and the order
        if order == 'shoot':           

            coo = random.choice(possible_position)
            
            x=str(coo[0])
            y=str(coo[1])
            to_shoot= x+'-'+y
            order=ship+':'+to_shoot
            
        else:
            order=ship+':'+order
            
        orders+=order+' '   
    
    return orders[:-1]
    
def give_coo(position,scope,height,width):   
    """
    return the list whith all coordonate the player can shoot 
    
    Paramaters
    ----------
    position:the position of the ship(tuple)
    scope:the max scope of the ship(int)
    height:the height of the board(int)
    width:the width of the board(int)
    
    Return
    ------
    to_shoot:the list with all the reachable coordonate(list)
    
    Versions    
    --------
    specification: Antoine Petit(V.1 18/03/17)
    implementation: Antoine Petit (V.1 18/03/17)
    
    """   
    up_x= position[0]-scope
    down_x=position[0]+scope
    left_y=position[1]-scope
    right_y=position[1]+scope
    
    list_x=[]    
    while up_x < down_x+1:
        list_x.append(up_x)
        up_x +=1
        
    list_y=[]    
    while left_y < right_y+1:
        list_y.append(left_y)
        left_y+=1
        
    to_shoot_b=[]
    for x in list_x :
        for y in list_y:
            x1=position[0]
            y1=position[1]
            manathan_scope= abs(x-x1)+abs(y-y1)
            if manathan_scope <= scope:            
                coo=(x,y)       
                to_shoot_b.append(coo)                

    to_shoot=[]
    for element in to_shoot_b :
        x=element[0]
        y=element[1]
        
        if x > height:        
            x-= height            
        if y > width:        
            y-=width            
        if x <= 0:          
            x += height           
        if y <= 0:               
            y += width
            
        n_coo=(x,y)
        to_shoot.append(n_coo)
        
    return to_shoot

def give_proba(game,player,to_shoot):
    """
    return the list with the probability of shoot if an ennemy ship is in the scope of your ship.
    
    Parameters
    ----------
    game: All informations about the game.(dict)
    player:Player one or two.(str)
    to_shoot:the list of the coordonate wich are in your scope(list)
    
    Return
    ------
    possible_position: the list of the posible position after the move of an ennemy and if it's in your scope(list)
    
    Version
    -------
    specification: Antoine Petit(V.1 18/03/17)
    implementation: Antoine Petit (V.1 18/03/17)   
    """
    if player =='1':
        other_player='2'
    else:
        other_player='1'
    
    ennemy_infos=[]    
    for ship in game['ships'][other_player]:
        ship_type=game['ships'][other_player][ship]['type']
        position=game['ships'][other_player][ship]['position']
        speed=game['ships'][other_player][ship]['speed']
        direction=game['ships'][other_player][ship]['direction']        
        ennemy_infos+=[(ship_type,position,speed,direction)] 
    
    proba=[]
    for infos in ennemy_infos:
        ship_type=infos[0]
        position=infos[1]         
        x=position[0]
        y=position[1]
        speed =infos[2]
        direction=infos[3]
            
        if direction == 1:
            
            nothing=(x-speed,y)           
            right=(x-speed,y+speed)           
            left=(x-speed,y-speed)           
            faster=(x-speed-1,y)           
            slower=(x-speed+1,y)           
        
        elif direction == 2: 
            
            nothing=(x-speed,y+speed)           
            right=(x,y+speed)           
            left=(x-speed,y)   
            faster=(x-speed-1,y+speed+1)           
            slower=(x-speed+1,y+speed-1)      
        
        elif direction == 3:
        
            nothing=(x,y+speed)    
            right=(x+speed,y+speed)
            left=(x-speed,y+speed)      
            faster=(x,y+speed+1)  
            slower=(x,y+speed-1)     
            
        elif direction == 4:
            
            nothing=(x+speed,y+speed)            
            right=(x+speed,y)      
            left=(x,y+speed)       
            faster=(x+speed+1,y+speed+1)          
            slower=(x+speed-1,y+speed-1)           
            
        elif direction == 5:
            
            nothing=(x+speed,y)           
            right=(x+speed,y-speed)            
            left=(x+speed,y+speed)            
            faster=(x+speed+1,y)            
            slower=(x+speed-1,y)            
            
        elif direction == 6:
            
            nothing=(x+speed,y-speed)            
            right=(x,y-speed)            
            left=(x+speed,y)           
            faster=(x+speed+1,y-speed-1)           
            slower=(x+speed-1,y-speed+1)            
            
        elif direction == 7:
            
            nothing=(x,y-speed)            
            right=(x-speed,y-speed)            
            left=(x+speed,y-speed)            
            faster=(x,y-speed-1)            
            slower=(x,y-speed+1)            
            
        else:            
            nothing=(x-speed,y-speed)            
            right=(x-speed,y)            
            left=(x,y-speed)            
            faster=(x-speed-1,y-speed-1)            
            slower=(x-speed+1,y-speed+1)        
        
        if speed== game['ships_infos'][ship_type]['speed']:
            proba+=[nothing,right,left,slower]
            
        elif speed == 0:
            proba+=[nothing,faster]
            
        else:
            proba+=[nothing,right,left,slower,faster]   
    
    possible_position=[]
    height = game['board_size']['height']
    width = game['board_size']['width']
    
    for position in proba:
        x=position[0]
        y=position[1]        
        
        if x > height:        
            x-= height            
        if y > width:        
            y-=width            
        if x <= 0:          
            x += height           
        if y <= 0:               
            y += width            
        
        n_position=(x,y)        
        
        if n_position in to_shoot:
            possible_position.append(n_position)

    return possible_position

def go_somewhere(game,ship,player,destination):
    """ Give an order to go to a give position.

    Parameters
    ----------
    game: All informations about the game.(dict)
    ship: The ship that must move (str)
    player: The owner of the ship (str)
    destination: Position to go (tuple)

    Returns
    -------
    best_order: The order to give to the ship (str)

    Versions
    --------
    specification: Robert Etienne (V.1 30/04/2017)
    implementation: Robert Etienne, Dejardin Gilles (V.1 30/04/2017)
    """

    min_dist = 9999
    
    nb_cases, can_go_straight = is_go_straight(game,ship,player,destination)
    if can_go_straight == True and game['ships'][player][ship]['type'] == 'fighter':
        order = go_straight(game,ship,player,destination,nb_cases)
        if len(order) > 0:
            best_order = order[0]
            return best_order

    for order in ['nothing','right','left','slower','faster']:
        valid_order = False

        speed = game['ships'][player][ship]['speed']
        direction = game['ships'][player][ship]['direction']
        position = game['ships'][player][ship]['position']
        y = position[0]
        x = position[1]
        ship_type = game['ships'][player][ship]['type']
        
        if order == 'faster' and speed < game['ships_infos'][ship_type]['speed']:
            speed += 1
            valid_order = True
        elif order == 'slower' and speed > 1:
            speed -= 1
            valid_order = True
        elif order == 'left':
            direction -= 1
            if direction == 0:
                direction = 8
            valid_order = True
        elif order == 'right':
            direction += 1
            if direction == 9:
                direction = 1
            valid_order = True

        if game['ships'][player][ship]['direction'] in (2,3,4): 
            y += speed
        if game['ships'][player][ship]['direction'] in (1,2,8):
            x -= speed
        if game['ships'][player][ship]['direction'] in (6,7,8):
            y -= speed
        if game['ships'][player][ship]['direction']in (4,5,6):
            x += speed

        distance = abs(destination[0] - y) + abs(destination[1] - x)
        if distance < min_dist and valid_order:
            min_dist = distance
            best_order = order
        
    return best_order

def random_order(game,speed,ship_type):
    """ Choose a valid random order

    Parameters
    ----------
    game: All informations about the game.(dict)
    speed: speed of the ship that must move (int)
    ship_type: type of the ship that must move (str)

    Returns
    -------
    order: a valid random order (str)

    Versions
    --------
    specification: Robert Etienne (V.1 30/04/2017)
    implementation: Robert Etienne (V.1 30/04/2017)
    """

    possible_orders = ['left','right']
    if speed < game['ships_infos'][ship_type]['speed']:
        possible_orders.append('faster')
    if speed > 0:
        possible_orders.append('slower')

    order = random.choice(possible_orders)
    return order

def get_closest_ship(game,potential_cibles,targeted_player,position):
    """ Get the name of the closest ship in a given team and the distance between it and the given ship.

    Parameters
    ----------
    game: All informations about the game.(dict)
    potential_cibles: all the names of the ships in the targeted team (list)
    targeted_player: the targeted player (str)
    position: position of the ship (tuple)

    Returns
    -------
    closest_cible: name of the closest ship in the given team (str)
    min_dist: distance between the ship and his closest ship (int)

    Versions
    --------
    specification: Robert Etienne (V.1 30/04/2017)
    implementation: Robert Etienne (V.1 30/04/2017)
    """

    min_dist = 9999
    for cible in potential_cibles:
        cible_position = game['ships'][targeted_player][cible]['position']
        manathan_scope = abs(cible_position[0]-position[0]) + abs(cible_position[1]-position[1])
        if manathan_scope < min_dist:
            min_dist = manathan_scope
            closest_cible = cible
    return closest_cible,min_dist

def is_go_straight(game,ship,player,destination):
    """ Look if the fighter which capture and the abandonned ship are on a straight line and if the fighter is directed toward the abandonned ship.
    
    Parameters
    ----------
    game: all information about the game. (dict)
    ship: fighter which go capture. (str)
    player: owner of the ship. (str)
    destination: position to go. (tuple)
    
    Return
    ------
    can_go_straight: if the fighter can go straight to capture the abandonned ship. (bool)
    
    Version
    -------
    specification: Gilles Dejardin (01-05-2017)
    implementation: Gilles Dejardin (01-05-2017)
    """
    #  Variable initialization. 
    can_go_straight = False
    nb_cases = 0
    
    #  Get the position and the direction of the ship.
    ship_pos = game['ships'][player][ship]['position']
    ship_dir = game['ships'][player][ship]['direction']
    
    # Get the height and the width of the board
    height_board = game['board_size']['height']
    width_board = game['board_size']['width']
    
    # Look if the ship and the abandonned ship are in the same vertical line.
    if ship_pos[0] == destination[0]:
        # Take the shortest way. 
        way_1 = max(ship_pos[1],destination[1]) - min(ship_pos[1],destination[1])
        way_2 = width_board - way_1
        nb_cases = min(way_1,way_2)
        # Look if the ship are in the good direction following the way and the position of the two ships.
        if nb_cases == way_1 and ((ship_pos[1] > destination[1] and ship_dir == 7) or (ship_pos[1] < destination[1] and ship_dir == 3)): 
            can_go_straight = True
        elif nb_cases == way_2 and ((ship_pos[1] < destination[1] and ship_dir == 7) or (ship_pos[1] > destination[1] and ship_dir == 3)):
            can_go_straight = True
    
    # Look if the ship and the abandonned ship are in the same horizontal line.
    elif ship_pos[1] == destination[1]:
        # Take the shortest way.
        way_1 = max(ship_pos[0],destination[0]) - min(ship_pos[0],destination[0])
        way_2 = height_board - way_1
        nb_cases = min(way_1,way_2)
        # Look if the ship are in the good direction following the way and the positions of the two ships.
        if nb_cases == way_1 and ((ship_pos[0] > destination[0] and ship_dir == 1) or (ship_pos[0] < destination[0] and ship_dir == 5)):
            can_go_straight = True
        elif nb_cases == way_2 and ((ship_pos[0] < destination[0] and ship_dir == 1) or (ship_pos[0] > destination[0] and ship_dir == 5)):
            can_go_straight = True
     
    # Look if the ship and the abandonned ship are in the same diagonal line.   
    elif abs(destination[0] - ship_pos[0]) == abs(destination[1] - ship_pos[1]):
        # Take the shortest way.
        way_1 = max(ship_pos[1],destination[1]) - min(ship_pos[1],destination[1])
        way_2 = min(height_board,width_board) - way_1
        nb_cases = min(way_1,way_2)
        # Look if the ship are in the good direction following the way and the positions of the two ships.
        if nb_cases == way_1:
            if destination[0] > ship_pos[0] and destination[1] > ship_pos[1] and ship_dir == 4:
                can_go_straight = True
            elif destination[0] > ship_pos[0] and destination[1] < ship_pos[1] and ship_dir == 6:
                can_go_straight = True
            elif destination[0] < ship_pos[0] and destination[1] < ship_pos[1] and ship_dir == 8:
                can_go_straight = True
            elif destination[0] < ship_pos[0] and destination[1] > ship_pos[1] and ship_dir == 2:
                can_go_straight = True
        elif nb_cases == way_2:
            if destination[0] > ship_pos[0] and destination[1] > ship_pos[1] and ship_dir == 8:
                can_go_straight = True
            elif destination[0] > ship_pos[0] and destination[1] < ship_pos[1] and ship_dir == 2:
                can_go_straight = True
            elif destination[0] < ship_pos[0] and destination[1] < ship_pos[1] and ship_dir == 4:
                can_go_straight = True
            elif destination[0] < ship_pos[0] and destination[1] > ship_pos[1] and ship_dir == 6:
                can_go_straight = True

    return nb_cases, can_go_straight
    
def go_straight(game,ship,player,destination,nb_cases):
    """Go to the coordonates of the destination if the ship should just go straight.
    
    Parameters
    ----------
    game: All informations about the game. (dict)
    ship: ship which must go to a destination. (str)
    player: owner of the ship. (str)
    destination: Position of the abandonned ship. (tuple)
    nb_cases: number of cases between the ship which capture and the abandonned ship. (int)
    
    Return
    ------
    order: List of orders to execute to approach of the bandonned ship.
    
    Version
    -------
    specification: Gilles Dejardin (V1. 10-04-2017)
    implementation: Gilles Dejardin (V1. 20-04-2017) 
    """
    # Get the speed of the ship.
    speed = game['ships'][player][ship]['speed']
    
    # For every speed of the fighter and for the number of cases between the fighter and the abandonned ship, give the orders to execute to go on the case of the abandonned ship.
    order = []
    if nb_cases == speed -1:
        order = ['slower'] 
    elif nb_cases == speed:
        order = ['nothing'] 
    elif nb_cases == speed +1 and speed < 5:
        order = ['faster']
    elif nb_cases == 2*speed - 2 and speed > 3:
        order = ['slower','nothing']
    elif nb_cases == 2*speed - 1 and speed > 2:
        order = ['slower','faster']
    elif nb_cases == 2*speed and speed >=2:
        order = ['nothing','nothing']
    elif nb_cases == 2*speed + 1 and speed in (1,2,3,4):
        order = ['faster','slower']
    elif nb_cases == 2*speed + 2 and speed < 5:
        order = ['faster','nothing']
    elif nb_cases == 2*speed + 3 and speed < 4:
        order = ['faster','faster']
    elif nb_cases == 3*speed - 1 and speed in (4,5):
        order = ['nothing','slower','faster']
    elif nb_cases == 3*speed + 1 and speed in (3,4):
        order = ['nothing','faster','slower']
    elif nb_cases == 3*speed + 2 and speed in (2,3,4):
        order = ['faster','slower','faster']
    elif nb_cases == 3*speed + 3 and speed in (1,2,3):
        order = ['nothing','faster','faster']
    elif nb_cases == 3*speed + 4 and speed < 4:
        order = ['faster','faster','slower']
    elif nb_cases == 3*speed + 5 and speed < 4:
        order = ['faster','faster','nothing']
    elif nb_cases == 3*speed + 6 and nb_cases < 3:
        order = ['faster','faster','faster']
    elif nb_cases == 4*speed + 3 and speed in (3,4):
        order = ['faster','nothing','slower','faster']
    elif nb_cases == 4*speed + 5 and speed in (2,3):
        order = ['faster','faster','slower','nothing']
    elif nb_cases == 4*speed + 7 and speed < 3:
        order = ['faster','nothing','faster','faster']
    elif nb_cases == 4*speed + 8 and speed < 3:
        order = ['faster','faster','faster','slower']
    elif nb_cases == 4*speed + 9 and speed < 3:
        order = ['faster','faster','faster','nothing']
    elif nb_cases == 4*speed + 10 and speed < 2:
        order = ['faster','faster','faster','faster']
    elif nb_cases == 5*speed + 10 and speed in (1,2):
        order = ['faster','faster','faster','slower','nothing']
    elif nb_cases == 5*speed + 11 and speed < 3:
        order = ['faster','faster','faster','nothing','slower']
    elif nb_cases == 5*speed + 12 and speed < 3:
        order = ['faster','faster','faster','nothing','nothing']
    elif nb_cases == 5*speed + 13 and speed < 2:
        order = ['faster','faster','faster','faster','slower']
    elif nb_cases == 5*speed + 14 and speed < 2:
        order = ['faster','faster','faster','faster','nothing']
    
    elif speed == 0: 
        if nb_cases == 15:
            order = ['faster','faster','faster','faster','faster']
        elif nb_cases == 16:
            order = ['faster','faster','faster','nothing','faster','slower']
        elif nb_cases == 17:
            order = ['faster','faster','faster','nothing','faster','nothing']
        elif nb_cases == 18:
            order = ['faster','faster','faster','faster','nothing','nothing']
        elif nb_cases == 19:
            order = ['faster','faster','faster','faster','faster','slower']
        elif nb_cases == 20:
            order = ['faster','faster','faster','faster','faster','nothing']
        elif nb_cases == 21:
            order = ['faster','faster','nothing','faster','faster','faster','slower']
        elif nb_cases == 22:
            order = ['faster','faster','faster','faster','faster','slower','slower']
        elif nb_cases == 23:
            order = ['faster','faster','faster','faster','faster','slower','nothing']
        elif nb_cases == 24:
            order = ['faster','faster','faster','faster','faster','nothing','slower']
        elif nb_cases == 25:
            order = ['faster','faster','faster','faster','faster','nothing','nothing']
        elif nb_cases == 26:
            order = ['faster','faster','faster','faster','faster','slower','nothing','slower']
        elif nb_cases == 27:
            order = ['faster','faster','faster','faster','faster','nothing','slower','slower']
        elif nb_cases == 28:
            order = ['faster','faster','faster','faster','faster','nothing','slower','nothing']
        elif nb_cases == 29:
            order = ['faster','faster','faster','faster','faster','nothing','nothing','slower']
        elif nb_cases == 30:
            order = ['faster','faster','faster','faster','faster','nothing','nothing','nothing']
         
    elif speed == 1: 
        if nb_cases == 20:
            order = ['faster','nothing','faster','faster','faster','slower']
        elif nb_cases == 21:
            order = ['faster','faster','nothing','faster','faster','slower']
        elif nb_cases == 22:
            order = ['faster','faster','faster','faster','slower','nothing']
        elif nb_cases == 23:
            order = ['faster','faster','faster','faster','nothing','slower']
        elif nb_cases == 24:
            order = ['faster','faster','faster','faster','nothing','nothing']
        elif nb_cases == 25:
            order = ['faster','faster','faster','faster','slower','nothing','slower']
        elif nb_cases == 26:
            order = ['faster','faster','faster','faster','slower','nothing','nothing']
        elif nb_cases == 27:
            order = ['faster','faster','faster','faster','nothing','slower','nothing']
        elif nb_cases == 28:
            order = ['faster','faster','faster','faster','nothing','nothing','slower']
        elif nb_cases == 29:
            order = ['faster','faster','faster','faster','nothing','nothing','nothing']
        elif nb_cases == 30:
            order = ['faster','faster','faster','faster','nothing','slower','nothing','slower']
        
    elif speed == 2: 
        if nb_cases == 18:
            order = ['faster','faster','slower','faster','nothing']
        elif nb_cases == 19:
            order = ['faster','faster','faster','slower','slower']
        elif nb_cases == 23:
            order = ['faster','faster','faster','slower','nothing','slower']
        elif nb_cases == 24:
            order = ['faster','faster','faster','nothing','slower','slower']
        elif nb_cases == 25:
            order = ['faster','faster','faster','nothing','slower','nothing']
        elif nb_cases == 26:
            order = ['faster','faster','faster','nothing','nothing','slower']
        elif nb_cases == 27:
            order = ['faster','faster','faster','nothing','nothing','nothing']
        elif nb_cases == 28:
            order = ['faster','faster','faster','nothing','slower','nothing','slower']
        elif nb_cases == 29:
            order = ['faster','faster','faster','nothing','nothing','slower','slower']
        elif nb_cases == 30:
            order = ['faster','faster','faster','nothing','nothing','slower','nothing']
        
    elif speed == 3: 
        if nb_cases == 1:
            order = ['slower','slower','slower','right','right','right','right','faster','nothing']
        elif nb_cases == 16:
            order = ['faster','faster','slower','slower']
        elif nb_cases == 19:
            order = ['faster','faster','slower','slower','nothing']
        elif nb_cases == 20:
            order = ['faster','faster','slower','nothing','slower']
        elif nb_cases == 21:
            order = ['faster','faster','nothing','slower','slower']
        elif nb_cases == 22:
            order = ['faster','faster','slower','faster','slower']
        elif nb_cases == 23:
            order = ['faster','faster','nothing','nothing','slower']
        elif nb_cases == 24:
            order = ['faster','faster','nothing','nothing','nothing']
        elif nb_cases == 25:
            order = ['faster','faster','nothing','slower','nothing','slower']
        elif nb_cases == 26:
            order = ['faster','faster','nothing','slower','nothing','nothing']
        elif nb_cases == 27:
            order = ['faster','faster','nothing','nothing','slower','nothing']
        elif nb_cases == 28:
            order = ['faster','faster','nothing','nothing','nothing','slower']
        elif nb_cases == 29:
            order = ['faster','faster','nothing','nothing','nothing','nothing']
        elif nb_cases == 30:
            order = ['faster','faster','nothing','nothing','slower','nothing','slower']
        
    
    elif speed == 4:
        if nb_cases == 1:
            order = ['slower','slower','slower','slower','right','right','right','right','faster','faster','nothing']
        elif nb_cases == 2:
            order = ['slower','slower','slower','slower','right','right','right','right','faster','faster','slower']  
        elif nb_cases == 12:
            order = ['faster','slower','slower']
        elif nb_cases == 15:
            order = ['faster','nothing','nothing']
        elif nb_cases == 16:
            order = ['faster','slower','nothing','slower']
        elif nb_cases == 17:
            order = ['faster','nothing','slower','slower']
        elif nb_cases == 18:
            order = ['faster','slower','faster','slower']
        elif nb_cases == 20:
            order = ['faster','nothing,','nothing','nothing'] 
        elif nb_cases == 21:
            order = ['faster','nothing','slower','nothing','slower']
        elif nb_cases == 22:
            order = ['nothing','faster','slower','faster','slower']
        elif nb_cases == 23:
            order = ['faster','nothing','nothing','slower','nothing']
        elif nb_cases == 24:
            order = ['faster','nothing','nothing','nothing','slower']
        elif nb_cases == 25:
            order = ['faster','nothing','nothing','nothing','nothing']
        elif nb_cases == 26:
            order = ['faster','nothing','nothing','slower','nothing','slower']
        elif nb_cases == 27:
            order = ['faster','nothing','nothing','slower','nothing','nothing']
        elif nb_cases == 28:
            order = ['faster','nothing','nothing','nothing','slower','nothing']
        elif nb_cases == 29:
            order = ['faster','nothing','nothing','nothing','nothing','slower']
        elif nb_cases == 30:
            order = ['faster','nothing','nothing','nothing','nothing','nothing']
    
    
    elif speed == 5:
        if nb_cases == 1:
            order = ['slower','slower','slower','slower','slower','right','right','right','right','faster','faster','faster','nothing']
        elif nb_cases == 2:
            order = ['slower','slower','slower','slower','right','right','right','right','faster','faster','faster','slower']
        elif nb_cases == 3:
            order = ['slower','slower','slower','slower','slower','right','right','right','right','faster','faster','nothing','nothing']
        elif nb_cases == 6:
            order = ['slower','slower','slower','slower','slower','right','right','right','right','faster','faster','slower']
        elif nb_cases == 7:
            order = ['slower','slower'] 
        elif nb_cases == 11:
            order = ['slower','nothing','slower']
        elif nb_cases == 12:
            order = ['nothing','slower','slower']
        elif nb_cases == 13:
            order = ['slower','faster','slower']
        elif nb_cases == 15:
            order = ['nothing','nothing','nothing']
        elif nb_cases == 16:
            order = ['slower','faster','slower','slower']
        elif nb_cases == 17:
            order = ['nothing','nothing','slower','slower']
        elif nb_cases == 18:
            order = ['nothing','slower','faster','slower']
        elif nb_cases == 19:
            order = ['nothing','slower','faster','nothing']
        elif nb_cases == 20:
            order = ['nothing','nothing','nothing','nothing']
        elif nb_cases == 21:
            order = ['nothing','slower','faster','slower','slower']
        elif nb_cases == 22:
            order = ['slower','faster','slower','faster','slower']
        elif nb_cases == 23:
            order = ['nothing','nothing','nothing','slower','nothing']
        elif nb_cases == 24:
            order = ['nothing','nothing','nothing','nothing','slower']
        elif nb_cases == 25:
            order = ['nothing','nothing','nothing','nothing','nothing']
        elif nb_cases == 26:
            order = ['nothing','nothing','nothing','slower','nothing','slower']
        elif nb_cases == 27:
            order = ['nothing','nothing','nothing','nothing','slower','slower']
        elif nb_cases == 28:
            order = ['nothing','nothing','nothing','nothing','slower','nothing']
        elif nb_cases == 29:
            order = ['nothing','nothing','nothing','nothing','nothing','slower']
        elif nb_cases == 30:
            order = ['nothing','nothing','nothing','nothing','nothing','nothing']
    
    return order 

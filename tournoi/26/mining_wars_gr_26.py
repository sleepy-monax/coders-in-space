# -*- coding: utf-8 -*-
import os.path
import sys
import socket
import time
import random
import remote_play

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


def mother(file_path,player_id,remote_IP,verbose):
    '''Main function, launching and running the game.

    parameters
    __________
    file_path: path of the .mw file stocking board informations (str)

    notes
    ----------
    contain 2 inputs for player's name

    version
    -------
    specification & implémentation : Eliott Cherry , Thielen Oscar (v.2 16/04/18)
    '''

    def board_initializing(file_path):
        ''' Read the configuration file, create a board and display it.

        parameters
        ----------
        file_path: is the path of the .mw file stocking board information (str)

        return
        ----------
        board: data structure of the graphic board (dico)
        gb : data structure of the inner-board (list)
        version
        -------
        specification & implémentation : Thielen Oscar (v.2 16/04/18)
        '''

        ##1) CONFIG FILE READING
        # config file opening
        file = open(file_path, 'r')
        lines = file.readlines()
        file.close()

        ##suppresion du texte

        lines = [i for i in lines if not ':' in i]

        ##netoyage de la structure (\n)

        elem_id = 0
        for elements in lines:
            lines[elem_id] = lines[elem_id].rstrip('\n')
            elem_id += 1

        ##agencement de la structure et passage des valeurs en entier numÃ©riques

        gb = []

        gb_id = 0
        nb_ast = 0
        for elements in lines:

            if gb_id == 0:

                gb.append(elements.split(' '))

                gb[0][0] = int(gb[0][0])

                gb[0][1] = int(gb[0][1])


            elif gb_id == 1:

                gb.append([])

                gb[1].append(elements.split(' '))

                gb[1][0][0] = int(gb[1][0][0])

                gb[1][0][1] = int(gb[1][0][1])


            elif gb_id == 2:

                gb[1].append(elements.split(' '))

                gb[1][1][0] = int(gb[1][1][0])

                gb[1][1][1] = int(gb[1][1][1])



            elif gb_id == 3:

                gb.append([])

                gb[2].append(elements.split(' '))

                gb[2][nb_ast][0] = int(gb[2][nb_ast][0])

                gb[2][nb_ast][1] = int(gb[2][nb_ast][1])

                gb[2][nb_ast][2] = int(gb[2][nb_ast][2])

                gb[2][nb_ast][3] = int(gb[2][nb_ast][3])

                nb_ast += 1



            else:

                gb[2].append(elements.split(' '))

                gb[2][nb_ast][0] = int(gb[2][nb_ast][0])

                gb[2][nb_ast][1] = int(gb[2][nb_ast][1])

                gb[2][nb_ast][2] = int(gb[2][nb_ast][2])

                gb[2][nb_ast][3] = int(gb[2][nb_ast][3])

                nb_ast += 1

            gb_id += 1

        ##2.1) BOARD CREATING
        ## variables initiales

        C = gb[0][1]
        L = gb[0][0]

        ## board data structure building
        board = {'t&b': '----|', }
        for idL in range(L):
            for idl in range(C):
                board[idL + 1, idl + 1] = [' ', ' ', '  |']

        ##3) PLACEMENT DES ASTEROIDES ET DES BASES

        asteroides = 'A'
        base = 'B'

        ##asteroides
        for elements in gb[2]:
            coo_ast = (elements[0], elements[1])
            board[coo_ast][1] = asteroides

        ##portals
        coo_portal1 = (gb[1][0][0], gb[1][0][1])
        coo_portal2 = (gb[1][1][0], gb[1][1][1])

        portal1_edge = []
        coo_base_calcul = [(coo_portal1[0] - 2, coo_portal1[1] - 2), (coo_portal2[0] - 2, coo_portal2[1] - 2)]

        for a in range(2):
            for i in range(5):
                for e in range(5):
                    new_coo = (coo_base_calcul[a][0] + i, coo_base_calcul[a][1] + e)

                    portal1_edge.append(new_coo)

        for elements in portal1_edge:
            board[elements][1] = base

        ##2.2) BOARD CREATING
        ##numÃ©rotation des colonnes
        nume_colo = ''
        for elements in range(C):
            ## changement de type pour numÃ©rotation
            numC = elements + 1
            numC = str(numC)
            ##construction
            if len(numC) == 1:
                nume_colo += '| ' + numC + '  '
            else:
                nume_colo += '| ' + numC + ' '
        ##affichage
        print(' X  ' + nume_colo + '|')

        ## constructions lignes

        disp = ''
        x = 1

        for nb_li in range(L):
            for nb_co in range(C):
                disp += (board[(nb_li + 1, nb_co + 1)][0]) + (board[(nb_li + 1, nb_co + 1)][1]) + (
                board[(nb_li + 1, nb_co + 1)][2])

            x += 1
            print((board['t&b'] * (C + 1)))
            if len(str(nb_li + 1)) == 1:
                print(' ' + str(nb_li + 1) + '  |' + disp)
            else:
                print(' ' + str(nb_li + 1) + ' |' + disp)
            disp = ''

        print((board['t&b'] * (C + 1)))

        ##returns
        return board, gb

        ## note : lorsque tu veut afficher un truc sur le plateau il faut le mettre a l'emplacement nÂ° 1 (pas 0 !) de la liste a
        ##la coordonnÃ©e correspondante dans le dico board et il s'affichera dans le quadrillage
        ## pour les coo c'est genre (1,2) ou 1 est la ligne et 2 la colonne
        ## la structure qui sert a afficher graphiquement = board
        ## la structure qui fournit les emplacement de bas, astÃ©roides, ... = gb



    ##----------------------------------------------------------------------------------------------------------
    ## player modifiying
    ##----------------------------------------------------------------------------------------------------------
    def update_player_data (player_1,player_2):
        '''Update the players's data structure
        
        Paramters:
        ____________________
        player_1: data structure for player 1
        player_2: data structure for player 2
        
        Return:
        ____________________
        player_1: data structure for player 1
        player_2: data structure for player 2
        
        version
        -------
        specification & implémentation : Eliott Cherry , Thielen Oscar (v.2 16/04/18)
        '''
    #__PORTAL EDGES________________________________________________________________
        players = (player_1,player_2)
        for player in players:
            coo_portal = player['base']['position']
            portal_edge = []
            coo_base_calcul = (coo_portal[0] - 2, coo_portal[1] - 2)
            
            for i in range(5):
                for e in range(5):
                    new_coo = (coo_base_calcul[0] + i, coo_base_calcul[1] + e)
                    portal_edge.append(new_coo)
            player['base']['edge'] = portal_edge
            
    #__SHIP EDGES________________________________________________________________
            
            for ship in player['ships']:
                coo_ship = player['ships'][ship]['coord']
                ship_edge =[]
    
                if player['ships'][ship]['type'] == 'scout':
                    coo_base_calcul = (coo_ship[0] - 1, coo_ship[1] - 1)
    
                    for i in range(3):
                        for e in range(3):
                            new_coo = (coo_base_calcul[0] + i, coo_base_calcul[1] + e)
    
                            ship_edge.append(new_coo)
    
                elif player['ships'][ship]['type'] == 'warship':
                    coo_base_calcul = (coo_ship[0] - 2, coo_ship[1] - 2)
    
                    for i in range(5):
                        for e in range(5):
                            new_coo = (coo_base_calcul[0] + i, coo_base_calcul[1] + e)
    
                            ship_edge.append(new_coo)
    
                    for coo in ship_edge:
                        
                        if coo == coo_base_calcul or (coo[0] == coo_base_calcul[0]+4 and coo[1] == coo_base_calcul[1] ) or (coo[0] == coo_base_calcul[0] and coo[1] == coo_base_calcul[1]+4 ) or (coo[0] == coo_base_calcul[0]+4 and coo[1] == coo_base_calcul[1]+4 ):
                            a= ship_edge.index(coo)
                            del ship_edge[a]
    
                elif player['ships'][ship]['type'] == 'excavator-S':
                    ship_edge.append(coo_ship)
    
                elif player['ships'][ship]['type'] == 'excavator-M':
                    coo_base_calcul = (coo_ship[0] - 1, coo_ship[1] - 1)
    
                    for i in range(3):
                        for e in range(3):
                            new_coo = (coo_base_calcul[0] + i, coo_base_calcul[1] + e)
    
                            ship_edge.append(new_coo)
    
                    for coo in ship_edge:
                        if coo == coo_base_calcul or (coo[0] == coo_base_calcul[0]+2 and coo[1] == coo_base_calcul[1] ) or (coo[0] == coo_base_calcul[0] and coo[1] == coo_base_calcul[1]+2 ) or (coo[0] == coo_base_calcul[0]+2 and coo[1] == coo_base_calcul[1]+2 ):
                            a= ship_edge.index(coo)
                            del ship_edge[a]
                elif player['ships'][ship]['type'] == 'excavator-L':
                    coo_base_calcul = (coo_ship[0] - 2, coo_ship[1] - 2)
        
                    for i in range(5):
                        for e in range(5):
                            new_coo = (coo_base_calcul[0] + i, coo_base_calcul[1] + e)
    
                            ship_edge.append(new_coo)
                    new_ship_edge =[]
                    for coo in ship_edge:
                        if coo_ship[0] in coo or coo_ship[1] in coo:
                            new_ship_edge.append(coo)
                    ship_edge = new_ship_edge

                player['ships'][ship]['edge'] = ship_edge
                
    #__SHIP REACHES_________________________________________________________________
                
                reach_edge=[]
                
                if player['ships'][ship]['type'] == 'scout':
                    coo_base_calcul = (coo_ship[0] - 3, coo_ship[1] - 3)
                    
                    for i in range(7):
                        for e in range(7):
                            new_coo = (coo_base_calcul[0] + i, coo_base_calcul[1] + e)
                            if abs(new_coo[0]-player['ships'][ship]['coord'][0]) + abs(new_coo[1]-player['ships'][ship]['coord'][1]) <= 3:
                                if new_coo[0]>0 and new_coo[1]>0:
                                    reach_edge.append(new_coo)
                elif player['ships'][ship]['type'] == 'warship':
                    coo_base_calcul = (coo_ship[0] - 5, coo_ship[1] - 5)
                    
                    for i in range(11):
                        for e in range(11):
                            new_coo = (coo_base_calcul[0] + i, coo_base_calcul[1] + e)
                            if abs(new_coo[0]-player['ships'][ship]['coord'][0]) + abs(new_coo[1]-player['ships'][ship]['coord'][1]) <= 5:
                                if new_coo[0]>0 and new_coo[1]>0:
                                    reach_edge.append(new_coo)
                                    
                player['ships'][ship]['reach'] = reach_edge
                
        return player_1,player_2

    ##----------------------------------------------------------------------------------------------------------
    ## gameboard displaying
    ##----------------------------------------------------------------------------------------------------------
    def board_modifing (board, player_1, player_2):
        ''' Modify structure of the board regarding the advancement of the game
        parameters
        ----------
        board: graphic board data structure (dict)
        player_1, player_2: data stucture of the players (dict)
    
        return
        ------
        board : altered data structure of the graphic board
        
        version
        -------
        specification & implémentation : Eliott Cherry  (v.2 16/04/18)
        '''
        players = (player_1, player_2)
  
        for player in players:
            for edge in player['base']['edge']:
                board[edge][1] = 'B'
                board[edge][2] = '0'
            for ship in player['ships']:
                if player['ships'][ship]['type'] == 'scout':
                    ship_icon = 'S'
                elif 'excavator' in player['ships'][ship]['type'] :
                    ship_icon = 'E'
                elif player['ships'][ship]['type'] == 'warship':
                    ship_icon = 'W'
                for edge in player['ships'][ship]['edge']:
                    board[edge][1] = ship_icon  
                    board[edge][2] = '0'
        for case in board:
            if not case == 't&b':
                if board[case][2] != '0':
                    board[case][1] = ' '
                else:
                    board[case][2] = '  |'
                            
    ## PRIORIT2 D AFFICHAGE : SCOUTS > EXCAVATORS > WARSHIPS > BASES          PRIORITE D AFFICHAGE POUR VAISSEAUX ET BASE PLAYER 2
        return board
      

    def naive_ia_playing(config_file_structure, player_1, player_2, nb_turn, phase):
        '''final form of the ia for minning war game.
        player_2 is always the ia
    
        parameters
        ----------
        config_file_structure: data structure of the board (list)
        player_1 and player_2: player's data structure (dic)
        nb_turn: iterable used to create the first ships
        phase: current strategical phase
    
        returns
        -------
        ordres : single turn orders from the ia
        nb_turn : number of turn already played plus one
        phase: current strategical phase
    
        version
        -------
        spÃƒÆ’Ã‚Â©cification et implÃƒÆ’Ã‚Â©mentation : Oscar Thielen (v.1 14/04/18)
        '''
    
        ia = player_2

        print(phase)
        ##returned orders from ia
        ordres = ''
    
        ## base adverse coo
        coo_rogue_base = player_1['base']['edge']
    
        ## rogue ships coord
        rogue_ships = []
        for enemy in player_1['ships']:
            for coo in player_1['ships'][enemy]['edge']:
                rogue_ships.append(coo)
    
        ## my ships
        my_ships = []
        for ship in ia['ships']:
            my_ships.append(ia['ships'][ship]['type'])
        print(my_ships)

        name = random.randint(500, 5000)

        buddy = 0

        buddy_list = []
        for i in ia['ships']:
            buddy_list.append(int(i[0]))
        if len(buddy_list) != 0:
            for elements in range(50):
                if buddy_list.count(elements) == 1:
                    buddy = elements
                else:
                    buddy = max(buddy_list) + 1

    
        if nb_turn == 1:
            ordres += str(buddy) + str(name) + 'abel:excavator-S ' + str(buddy) + str(name) + 'cain:scout '
            phase = 'looting'
    
    
        ##phase 1
        ##-------
        elif phase == 'looting':
    
            ## achat
    
            if len (my_ships) % 2 == 0:
                if ia['ore'] >= 2:
                    ordres += str(buddy) + str(name) +'moise' + ':excavator-M' + ' '
                else:
                    None
            else:
                if ia['ore'] >= 3:
                    ordres += str(buddy) + str(name) + 'cain' + ':scout' + ' '
                else:
                    None
    
    
            ##target definition
    
            for ship in sorted(ia['ships']):
                ##excavators
                if 'exc' in ia['ships'][ship]['type']:
                    if ia['ships'][ship]['target'] == ia['base']['position'] and ia['ships'][ship]['ore'] == ia['ships'][ship]['capacity']:
                        None
                    else:
                        coo_ext = ia['ships'][ship]['coord']
                        liste_ast = []
                        liste_calcul = []
                        for ast in config_file_structure[2]:
                            if ast[2] == 0:
                                None
                            else:
                                liste_ast.append((ast[0], ast[1]))
                        for coo in liste_ast:
                            liste_calcul.append(abs((coo_ext[0] - coo[0]) + (coo_ext[1] - coo[1])))
    
                        ##coo plus petit/proche de la liste
    
                        new_target = liste_ast[liste_calcul.index(min(liste_calcul))]
    
                        ## define ast target
                        ia['ships'][ship]['target'] = new_target
    
                ##scoot and warship
                else:

                    for bud in ia['ships']:
                        if bud == ship :
                            None
                        else:
                            if ship[0] == bud[0] :
                                my_targ = ia['ships'][bud]['target']
                    try:
                        ia['ships'][ship]['target'] = my_targ
                    except:
                        my_targ = player_1['base']['position']
                        ia['ships'][ship]['target'] = my_targ


            ## start playing
    
            for ship in sorted(ia['ships']):
                target = ia['ships'][ship]['target']
                coo_ship = ia['ships'][ship]['coord']
    
                ## scout or warship
                if ia['ships'][ship]['type'] == 'scout' or ia['ships'][ship]['type'] == 'warship':
    
                    for enemy in rogue_ships:
                        if enemy in ia['ships'][ship]['reach']:
                            ordres += ship + ':*' + str(enemy[0]) + '-' + str(enemy[1]) + ' '
                    for spot in coo_rogue_base:
                        if spot in ia['ships'][ship]['reach']:
                            ordres += ship + ':*' + str(spot[0]) + '-' + str(spot[1]) + ' '

    
                    ##mooving scout and warship
                    if ship in ordres:
                        None
                    else:
    
                        if coo_ship[0] > target[0]:
    
                            if coo_ship[1] > target[1]:
                                ordres += ship + ':@' + str(coo_ship[0] - 1) + '-' + str(coo_ship[1] - 1) + ' '
    
                            elif coo_ship[1] < target[1]:
                                ordres += ship + ':@' + str(coo_ship[0] - 1) + '-' + str(coo_ship[1] + 1) + ' '
    
                            else:
                                ordres += ship + ':@' + str(coo_ship[0] - 1) + '-' + str(coo_ship[1]) + ' '
    
                        elif coo_ship[0] < target[0]:
    
                            if coo_ship[1] > target[1]:
                                ordres += ship + ':@' + str(coo_ship[0] + 1) + '-' + str(coo_ship[1] - 1) + ' '
    
                            elif coo_ship[1] < target[1]:
                                ordres += ship + ':@' + str(coo_ship[0] + 1) + '-' + str(coo_ship[1] + 1) + ' '
    
                            else:
                                ordres += ship + ':@' + str(coo_ship[0] + 1) + '-' + str(coo_ship[1]) + ' '
    
                        else:
                            if coo_ship[1] > target[1]:
                                ordres += ship + ':@' + str(coo_ship[0]) + '-' + str(coo_ship[1] - 1) + ' '
    
                            elif coo_ship[1] < target[1]:
                                ordres += ship + ':@' + str(coo_ship[0]) + '-' + str(coo_ship[1] + 1) + ' '
    
    
                ##excavator
                else:
                    if ia['ships'][ship]['coord'] == ia['ships'][ship]['target'] and ia['ships'][ship]['lock'] == True:
    
                        if ia['ships'][ship]['ore'] == 0 or ia['ships'][ship]['ore'] == ia['ships'][ship]['capacity']:
                            ordres += ship + ':release '
    
                    elif ia['ships'][ship]['coord'] == ia['ships'][ship]['target'] and ia['ships'][ship]['lock'] == False:
    
                        if ia['ships'][ship]['ore'] == ia['ships'][ship]['capacity']:
                            if ia['ships'][ship]['target'] == ia['base']['position']:
                                ordres += ship + ':lock '
                            else:
                                ia['ships'][ship]['target'] = ia['base']['position']
                        else:
                            ordres += ship + ':lock '
    
                    ##mooving excavator
                    if coo_ship[0] > target[0]:
    
                        if coo_ship[1] > target[1]:
                            ordres += ship + ':@' + str(coo_ship[0] - 1) + '-' + str(coo_ship[1] - 1) + ' '
    
                        elif coo_ship[1] < target[1]:
                            ordres += ship + ':@' + str(coo_ship[0] - 1) + '-' + str(coo_ship[1] + 1) + ' '
    
                        else:
                            ordres += ship + ':@' + str(coo_ship[0] - 1) + '-' + str(coo_ship[1]) + ' '
    
                    elif coo_ship[0] < target[0]:
    
                        if coo_ship[1] > target[1]:
                            ordres += ship + ':@' + str(coo_ship[0] + 1) + '-' + str(coo_ship[1] - 1) + ' '
    
                        elif coo_ship[1] < target[1]:
                            ordres += ship + ':@' + str(coo_ship[0] + 1) + '-' + str(coo_ship[1] + 1) + ' '
    
                        else:
                            ordres += ship + ':@' + str(coo_ship[0] + 1) + '-' + str(coo_ship[1]) + ' '
    
                    else:
                        if coo_ship[1] > target[1]:
                            ordres += ship + ':@' + str(coo_ship[0]) + '-' + str(coo_ship[1] - 1) + ' '
    
                        elif coo_ship[1] < target[1]:
                            ordres += ship + ':@' + str(coo_ship[0]) + '-' + str(coo_ship[1] + 1) + ' '
    
    
    
            ## confirmation passage en phase 2
            exc = 0
            scout = 0
            for ship in ia['ships']:
                if 'excavator-M' in ia['ships'][ship]['type']:
                    exc += 1
                elif 'scout' in ia['ships'][ship]['type']:
                    scout += 1
            if exc == 2 and scout == 2:
                phase = 'pressuring'


        ##phase 2
        ##-------
        elif phase == 'pressuring':
    
            ## achat

    
            if 'excavator-L' in my_ships:
                if ia['ore'] >= 9:
                    ordres += str(buddy) +str(name) + 'abraham' + ':warship' + ' '
            else:
                if ia['ore'] >= 4:
                    ordres += str(buddy) + str(name) + 'judas' + ':excavator-L' + ' '

                ##target definition
    
            for ship in ia['ships']:
                ##excavators
                if 'exc' in ia['ships'][ship]['type']:
                    if ia['ships'][ship]['target'] == ia['base']['position'] and ia['ships'][ship]['ore'] == \
                            ia['ships'][ship]['capacity']:
                        None
                    else:
                        coo_ext = ia['ships'][ship]['coord']
                        liste_ast = []
                        liste_calcul = []
                        for ast in config_file_structure[2]:
                            if ast[2] == 0:
                                None
                            else:
                                liste_ast.append((ast[0], ast[1]))
                        for coo in liste_ast:
                            liste_calcul.append(abs((coo_ext[0] - coo[0]) + (coo_ext[1] - coo[1])))
    
                        ##coo plus petit/proche de la liste
    
                        new_target = liste_ast[liste_calcul.index(min(liste_calcul))]
    
                        ## define ast target
                        ia['ships'][ship]['target'] = new_target
    
                ##scoot and warship
                else:
                    ia['ships'][ship]['target'] = player_1['base']['position']
    
            ## start playing
    
            for ship in ia['ships']:
                target = ia['ships'][ship]['target']
                coo_ship = ia['ships'][ship]['coord']
    
                ## scout or warship
                if ia['ships'][ship]['type'] == 'scout' or ia['ships'][ship]['type'] == 'warship':
    
                    for enemy in rogue_ships:
                        if enemy in ia['ships'][ship]['reach']:
                            ordres += ship + ':*' + str(enemy[0]) + '-' + str(enemy[1]) + ' '
                    for spot in coo_rogue_base:
                        if spot in ia['ships'][ship]['reach']:
                            ordres += ship + ':*' + str(spot[0]) + '-' + str(spot[1]) + ' '
    
                    ##mooving scout and warship
                    if ship in ordres:
                        None
                    else:
    
                        if coo_ship[0] > target[0]:
    
                            if coo_ship[1] > target[1]:
                                ordres += ship + ':@' + str(coo_ship[0] - 1) + '-' + str(coo_ship[1] - 1) + ' '
    
                            elif coo_ship[1] < target[1]:
                                ordres += ship + ':@' + str(coo_ship[0] - 1) + '-' + str(coo_ship[1] + 1) + ' '
    
                            else:
                                ordres += ship + ':@' + str(coo_ship[0] - 1) + '-' + str(coo_ship[1]) + ' '
    
                        elif coo_ship[0] < target[0]:
    
                            if coo_ship[1] > target[1]:
                                ordres += ship + ':@' + str(coo_ship[0] + 1) + '-' + str(coo_ship[1] - 1) + ' '
    
                            elif coo_ship[1] < target[1]:
                                ordres += ship + ':@' + str(coo_ship[0] + 1) + '-' + str(coo_ship[1] + 1) + ' '
    
                            else:
                                ordres += ship + ':@' + str(coo_ship[0] + 1) + '-' + str(coo_ship[1]) + ' '
    
                        else:
                            if coo_ship[1] > target[1]:
                                ordres += ship + ':@' + str(coo_ship[0]) + '-' + str(coo_ship[1] - 1) + ' '
    
                            elif coo_ship[1] < target[1]:
                                ordres += ship + ':@' + str(coo_ship[0]) + '-' + str(coo_ship[1] + 1) + ' '
    
    
                ##excavator
                else:
                    if ia['ships'][ship]['coord'] == ia['ships'][ship]['target'] and ia['ships'][ship]['lock'] == True:
    
                        if ia['ships'][ship]['ore'] == 0 or ia['ships'][ship]['ore'] == ia['ships'][ship]['capacity']:
                            ordres += ship + ':release '
    
                    elif ia['ships'][ship]['coord'] == ia['ships'][ship]['target'] and ia['ships'][ship][
                        'lock'] == False:
    
                        if ia['ships'][ship]['ore'] == ia['ships'][ship]['capacity']:
                            if ia['ships'][ship]['target'] == ia['base']['position']:
                                ordres += ship + ':lock '
                            else:
                                ia['ships'][ship]['target'] = ia['base']['position']
                        else:
                            ordres += ship + ':lock '
    
                    ##mooving excavator
                    if coo_ship[0] > target[0]:
    
                        if coo_ship[1] > target[1]:
                            ordres += ship + ':@' + str(coo_ship[0] - 1) + '-' + str(coo_ship[1] - 1) + ' '
    
                        elif coo_ship[1] < target[1]:
                            ordres += ship + ':@' + str(coo_ship[0] - 1) + '-' + str(coo_ship[1] + 1) + ' '
    
                        else:
                            ordres += ship + ':@' + str(coo_ship[0] - 1) + '-' + str(coo_ship[1]) + ' '
    
                    elif coo_ship[0] < target[0]:
    
                        if coo_ship[1] > target[1]:
                            ordres += ship + ':@' + str(coo_ship[0] + 1) + '-' + str(coo_ship[1] - 1) + ' '
    
                        elif coo_ship[1] < target[1]:
                            ordres += ship + ':@' + str(coo_ship[0] + 1) + '-' + str(coo_ship[1] + 1) + ' '
    
                        else:
                            ordres += ship + ':@' + str(coo_ship[0] + 1) + '-' + str(coo_ship[1]) + ' '
    
                    else:
                        if coo_ship[1] > target[1]:
                            ordres += ship + ':@' + str(coo_ship[0]) + '-' + str(coo_ship[1] - 1) + ' '
    
                        elif coo_ship[1] < target[1]:
                            ordres += ship + ':@' + str(coo_ship[0]) + '-' + str(coo_ship[1] + 1) + ' '
    
    
    
        ##returns
        ordres = ordres.rstrip()
    
        return player_2, ordres, phase
        

         
        
    def display_game(player_1, player_2, board, config_file_data):
        '''Display the board and vital player's informations on the screen
        parameters
        ------------
        player_1 : data structure for player 1 (dict)
        player_2 : data structure for player 2 (dict)
        board: data structure of the board (str)
        return
        ------------
        player_1 : data structure for player 1 (dict)
        player_2 : data structure for player 2 (dict)
        board: data structure of the graphic board (list)
        config_fil_data: data structure of the board (dict)
        version
        -------
        specification & implémentation : Thielen Oscar (v.2 16/04/18)
        '''
    #___PLAYERS INFOS __________________________________________________________________________________________________
        print('-' * 7 + '\n' + 'PLAYER 1')
        print('-' * 7 + '\n' + 'ore = ' + str(player_1['ore']) + '\n' + 'base HP = ' + str(
            player_1['base']['hp']) + '\n' + 'ships :\n')
        for elements in player_1['ships']:
            print(elements + ':')
            print('---')
            for key, value in player_1['ships'][elements].items():
                if (key == 'size') or (key == 'strengh') or (key == 'reach') or (key == 'cost') :
                    None
                else:
                    print(key, '=', value)
        print('\n' * 2)
        ##player_2
        print('-' * 7 + '\n' + 'PLAYER 2')
        print('-' * 7 + '\n' + 'ore = ' + str(player_2['ore']) + '\n' + 'base HP = ' + str(
            player_2['base']['hp']) + '\n' + 'ships :\n')
        for elements in player_2['ships']:
            print(elements + ':')
            print('---')
            for key, value in player_2['ships'][elements].items():
                if (key == 'size') or (key == 'strengh') or (key == 'reach') or (key == 'cost') :
                    None
                else:
                    print(key, '=', value)
        print('\n' * 2)    
        
    #________________________________________________________________________________________________________________
        board = board_modifing (board, player_1, player_2)
    
        for asteroide in config_file_data[2]:
                    coo_ast = (asteroide[0], asteroide[1])
                    board[coo_ast][1] = 'A'
           ## PRIORIT2 D AFFICHAGE : ASTEROIDES > SCOUTS > EXCAVATORS > WARSHIPS > BASES
    #___________________________________________________________________________________________________________
        C = config_file_data[0][1]
        L = config_file_data[0][0]
        nume_colo = ''
        for elements in range(C):
            ## changement de type pour numÃ©rotation
            numC = elements + 1
            numC = str(numC)
            ##construction
            if len(numC) == 1:
                nume_colo += '| ' + numC + '  '
            else:
                nume_colo += '| ' + numC + ' '
        ##affichage
        print(' X  ' + nume_colo + '|')
        ## constructions et numerotation lignes
        disp = ''
        x = 1
        for nb_li in range(L):
            for nb_co in range(C):
                disp += (board[(nb_li + 1, nb_co + 1)][0]) + (board[(nb_li + 1, nb_co + 1)][1]) + (
                board[(nb_li + 1, nb_co + 1)][2])
            x += 1
            print((board['t&b'] * (C + 1)))
            if len(str(nb_li + 1)) == 1:
                print(' ' + str(nb_li + 1) + '  |' + disp)
            else:
                print(' ' + str(nb_li + 1) + ' |' + disp)
            disp = ''
        print((board['t&b'] * (C + 1)))
         
    def entire_turn (player_1,player_2,board,ships,config_file_data,order_1,order_2):
        '''Run a full turn of the game 
        
        Parameters : 
        ______________
        player_1: data structure of one player  (dico)
        player_2: data structure of one player (dico)
        board: data structure containing the board (dico)
        ships: data structure containing basic ships info (dico)
        config_file_data: data structure containing info from the file, to launch the game (list)
        
        return:
        ______________
        player_1: data structure of one player  (dico)
        player_2: data structure of one player (dico)
        peacefull : usefull variable for sknowing if damages have been occured (bool)
        
        version
        -------
        specification & implémentation : Eliott Cherry (v.2 16/04/18)
        '''
        print (order_1,' ',order_2)
        def single_turn (player_1,player_2,board,ships,config_file_data,peace,order):
            '''Run a turn for a player
                
            Parameters : 
            ______________
            player_1: data structure of one player  (dico)
            player_2: data structure of one player (dico)
            board: data structure containing the board (dico)
            ships: data structure containing basic ships info (dico)
            config_file_data: data structure containing info from the file, to launch the game (list)
            peace: variable usefull for knowing if damage have been occured
            order: orders for a turn 
            return:
            ______________
            player_1: data structure of one player  (dico)
            player_2: data structure of one player (dico)
            peacefull : usefull variable for sknowing if damages have been occured (bool)
            
            version
            -------
            specification & implémentation : Eliott Cherry (v.2 16/04/18)
            '''
            def buy_ship (player,name,command,ships,board):
                '''Buy a ship
                
                Parameters : 
                ______________
                player: data structure for the player playing (dico)
                name: name of the ship attacking (str)
                command: command of the purchase (str)
                ships: data structure containing basic ships info (dico)
                board: data structure containing the board (dico)
                
                return:
                ______________
                player :data structure for the player playing (dico)
                
                version
                -------
                specification & implémentation : Eliott Cherry (v.2 16/04/18)
                '''
                if name in player['ships']:
                    print ('The ship name :%s is unavailable. ' % name)             
                else:
                    if player['ore']< ships[command]['cost']:
                        print ('Unsufficient ressources for buying a %s.' % command)
                                    
                    else:
                        player['ships'][name] = ships[command].copy()
                        player['ships'][name]['coord'] = player['base']['position']
                        player['ore'] -= ships[command]['cost']
                        print('The %s named %s has been bought.' % (command,name))
                return player
            
            def locking_ship (player,name,command,board):
                '''Lock or realease a ship
                
                Parameters : 
                ______________
                player: data structure for the player playing (dico)
                name: name of the ship attacking (str)
                command: command of the purchase (str)
                board: data structure containing the board (dico)
                
                return:
                ______________
                player :data structure for the player playing (dico)
                
                version
                -------
                specification & implémentation : Eliott Cherry (v.2 16/04/18)
                '''
                if name in player['ships']:
                    
                    if command == 'lock' and board[player['ships'][name]['coord']][1] == 'A' and player['ships'][name]['lock'] == False:                    ##ASTEROIDE PRIORITE SUR LA CASE
                        player['ships'][name]['lock'] = True
                        print('The ship %s has been locked on an asteroid.' % name)
                    elif command == 'lock' and player['ships'][name]['coord'] == player['base']['position'] and player['ships'][name]['lock'] == False:
                        player['ships'][name]['lock'] = True
                        print('The ship %s has been locked on his base.' % name)
                    elif command == 'release' and board[player['ships'][name]['coord']][1] == 'A' and player['ships'][name]['lock'] == True:
                        player['ships'][name]['lock'] = False
                        print('The ship %s has been released from an asteroid.' % name)
                    elif command == 'release' and player['ships'][name]['coord'] == player['base']['position'] and player['ships'][name]['lock'] == True:
                        player['ships'][name]['lock'] = False
                        print('The ship %s has been released from his base.' % name)
                    else:
                        print ('The ship %s do not complete requirements for locking/releasing.' % name)
                else:
                    print('The ship %s doesnt exist' % name)
                    
                return player
            
            def move_ship (player,name,dest,config_file_data):
                '''Move a ship
                
                Parameters : 
                ______________
                player: data structure for the player playing (dico)
                name: name of the ship attacking (str)
                dest: destination command of the move (tuple)
                config_file_data: data structure containing info from the file, to launch the game (list)
                
                return:
                ______________
                player :data structure for the player playing (dico)
                
                version
                -------
                specification & implémentation : Eliott Cherry (v.2 16/04/18)
                '''
                if name in player['ships']:
                    
                    if player['ships'][name]['moved'] == False :
                        diff_r = player['ships'][name]['coord'][0] - dest[0]
                        diff_c = player['ships'][name]['coord'][1] - dest[1]
                        if abs(diff_r) < 2 and abs(diff_c) < 2:              ## PORTEE DE MOUVEMENT
                            moveable = 'no'
                            if player['ships'][name]['type'] == 'excavator-S':
                                if (dest[0] > 0 and dest[0] <= config_file_data[0][0]) and (dest[1] > 0 and dest[1] <= config_file_data[0][1]):       ##SORTIE PLATEAU EXC-S
                                    moveable = 'yes'
                            elif player['ships'][name]['type'] == 'scout' or player['ships'][name]['type'] == 'excavator-M':
                                if (dest[0] > 1 and dest[0] <= (config_file_data[0][0] - 1)) and (dest[1] > 1 and dest[1] <= (config_file_data[0][1] - 1)):        ##SORTIE PLATEAU SCOUT EXC-M
                                    moveable = 'yes'
                            else:
                                if (dest[0] > 2 and dest[0] <= (config_file_data[0][0] - 2)) and (dest[1] > 1 and dest[1] <= (config_file_data[0][1] - 2)):       ##SORTIE PLATEAU WARSHIP EXC-L
                                    moveable = 'yes' 
                            if moveable == 'yes':
                                
                                player['ships'][name]['coord'] = dest
                                player['ships'][name]['moved'] = True
                                print('The ship ',name,' has successfully moved to ',dest)
                            else:
                                print ('A ship cannot exit the board s limits. %s tried.' % name)
                        else:
                            print ('A ship can at best move by one case each turn. %s tried.' % name)
                    else:
                        print('The ship %s has already moved this turn.' % name)
                else:
                    print('The ship %s doesnt exist' % name)
                    
                return player    
                            
                    
            def attack_ship (players,player,name,target,peace):
                '''Launch an attack from a ship on a certain case on the board
                
                Parameters : 
                ______________
                players:tuple containing data structure of both players (tuple)
                player: data structure for the player playing (dico)
                name: name of the ship attacking (str)
                target: target of the attack (tuple)
                peace: usefull variable to know if damages have been occured (bool)
                
                return:
                ______________
                players:tuple containing data structure of both players (tuple)
                peace:usefull variable to know if damages have been occured (bool)
                
                version
                -------
                specification & implémentation : Eliott Cherry (v.2 16/04/18)
                '''
                if name in player['ships']:
                    if player['ships'][name]['moved'] == False :
                        if target in player['ships'][name]['reach']:
                            for single_player in players :
                                for ship in single_player['ships']:
                                        if target in single_player['ships'][ship]['edge']:
                                            single_player['ships'][ship]['hp'] -= player['ships'][name]['strengh']
                                            peace = False
                                if target in single_player['base']['edge']:
                                    single_player['base']['hp'] -= player['ships'][name]['strengh']
                                    peace = False
                            player['ships'][name]['moved'] == True
                            print('The ship ',name,' has successfully launched an attack on ',target)
                            
                        else:
                            print('The ship %s is too far away for his target.' % name)
                    else:
                        print('The ship %s has already moved this turn.' % name)
                else:
                    print('The ship %s doesnt exist.' % name)
                                        
                return players , peace
                
            
            players = (player_1,player_2)
            print (order)
            if order == 'none':
                None
            elif order =='stop':
                sys.exit(0) 
            elif order == '':
                None
            else:   
                print (order)     
                order_list = order.split (' ')
                buying_orders = []
                locking_orders = []
                moving_orders = []
                attack_orders = []
                for order in order_list:
                    try:
                        name, command = order.split (':')
                        if command in ships :
                            buying_orders.append (order)
                        elif command == 'lock' or command == 'release':
                            locking_orders.append (order)
                        elif command[0] == '@' :
                            moving_orders.append (order)
                        elif command[0] == '*' :
                            attack_orders.append (order)
                    except ValueError:
                        print('Wrong commands used, you lost your turn.')
                for ship in player_1['ships']:
                        player_1['ships'][ship]['moved'] = False
                    
                for order in buying_orders:
                    name, command = order.split (':')
                    
                        
                    player_1 = buy_ship (player_1,name,command,ships,board)
                player_1,player_2 = update_player_data (player_1,player_2)
                    
                for order in locking_orders:
                    name, command = order.split (':')
                    
                    player_1 = locking_ship (player_1,name,command,board)
                
                for order in moving_orders:
                    name, command = order.split (':')
                    command = command [1:]
                    r , c = command.split ('-')
                    dest = (int(r),int(c))
                    
                    player_1 = move_ship (player_1,name,dest,config_file_data)
                    
                for order in attack_orders:
                    name, command = order.split (':')
                    command = command [1:]
                    r , c = command.split ('-')
                    target = (int(r),int(c))
                    
                    players ,peace = attack_ship (players,player_1,name,target,peace)
                
            return player_1,player_2,peace


        players = (player_1,player_2)
        peace = True
        peacefull = True
        player_1,player_2,peace = single_turn (player_1,player_2,board,ships,config_file_data,peace,order_1)
        if peace ==False:
            peacefull = False
        player_2,player_1,peace = single_turn (player_2,player_1,board,ships,config_file_data,peace,order_2)
        if peace == False:
            peacefull = False
         
        for player in players:
            new_ships = dict()
            for ship, value in player['ships'].items():
                
                    if player['ships'][ship]['hp'] > 0:
                            new_ships[ship] = value
                    else:
                        print('The ship %s has been destroyed.' % ship)
            player['ships'] = new_ships.copy()
        player_1,player_2 = update_player_data (player_1,player_2)
                        
        
        for asteroid in config_file_data[2]:
                capacity =  asteroid[2] 
                speed = asteroid[3] 
                excavators = []
                for player in players:
                    for ship in player['ships']:
                        if player['ships'][ship]['coord'] == (asteroid[0],asteroid[1]) and 'excavator' in player['ships'][ship]['type'] and player['ships'][ship]['lock'] == True:
                            excavators.append(player['ships'][ship])
                                
                    if capacity >= speed * len(excavators):
                        for ship in excavators:
                            if ship['coord'] == (asteroid[0],asteroid[1]) and 'excavator' in ship['type'] and ship['lock'] == True:
                                if ship['ore']+ speed > ship['capacity']:
                                    asteroid[2] += (ship['ore']+ speed - ship['capacity'])
                                    ship['ore'] = ship['capacity']
                                else:
                                    ship['ore'] += speed
                                        
                        asteroid[2] -= len(excavators) * speed 
                                    
                    else:
                        try:
                            distri = capacity/len(excavators)

                            for ship in excavators:
                                if ship['coord'] == (asteroid[0],asteroid[1]) and 'excavator' in ship['type'] and ship['lock'] == True:
                                    if ship['ore']+ distri > ship['capacity']:
                                        asteroid[2] -= distri - (ship['ore']+ distri - ship['capacity'])
                                        ship['ore'] = ship['capacity']
                                    else:
                                        ship['ore'] += distri
                                        asteroid[2] -= distri
                            remaining_excavators = []
                            for ships in excavators:
                                if ship['ore'] < ship['capacity']:
                                    remaining_excavators.append (ship)
                            if asteroid[2] != 0 and len(remaining_excavators) > 0:
                                new_distri = asteroid[2]/len(remaining_excavators)
                                for ship in remaining_excavators:
                                        ship['ore'] += new_distri
                                        asteroid[2] -= new_distri
                            asteroid[2] = 0
                        except:
                            None
        for player in players:
            for ship in player['ships']:
                if player['ships'][ship]['coord'] == player['base']['position'] and 'excavator' in player['ships'][ship]['type'] and player['ships'][ship]['lock'] == True:
                    player['ore'] += player['ships'][ship]['ore']
                    player['ships'][ship]['ore'] = 0
                            
                            
        return peacefull , player_1 , player_2    
      

        
    def ending_conditions (peace,player_1,player_2):
        ''' Check if the game is over
        Parameters:
        _______________
        peace: usefull variable for knowing if the game end
        player_1: data structure of one player  (dico)
        player_2: data structure of one player (dico)
        
        Return:
        ___________________
        Boolean value for end the game
        
        
        version
        -------
        specification & implémentation : Eliott Cherry (v.2 16/04/18)
        '''
        if peace == 200 or player_1['base']['hp'] <= 0 or  player_2['base']['hp'] <= 0 :
            return True
        else:
            return False
    
       
        
    




    ##----------------------------------------------------------------------------------------------------------
    ##test jeu
    ##----------------------------------------------------------------------------------------------------------
    connection = remote_play.connect_to_player(player_id,remote_IP,verbose)
    boxes, game_board = board_initializing(file_path)  
    
    player_1 = {'ore': 4, 'base':{ 'hp': 100, 'position': (game_board[1][0][0],game_board[1][0][1]) }, 'ships': {}}
    player_2 = {'ore': 4, 'base':{ 'hp': 100, 'position' : (game_board[1][1][0],game_board[1][1][1]) },'ships': {}}

    ships = {'scout':{'type': 'scout', 'size': 9, 'hp': 3, 'strengh': 1, 'target': None, 'reach': 3, 'cost': 3, 'coord': (0,0),'moved' : False},
    'warship':{'type': 'warship', 'size': 21, 'hp': 18, 'strengh': 3, 'reach': 5,'target': None, 'cost': 9, 'coord': (0,0),'moved' : False},
    'excavator-S':{'type': 'excavator-S', 'size': 1, 'capacity': 1,'lock': False ,'target': None, 'hp': 2, 'strengh': 0, 'ore': 0, 'cost': 1, 'coord': (0,0),'moved' : False},
    'excavator-M':{'type': 'excavator-M', 'size': 5, 'capacity': 4,'lock': False ,'target': None , 'hp': 3, 'strengh': 0, 'ore': 0, 'cost': 2, 'coord': (0,0),'moved' : False},
    'excavator-L':{'type': 'excavator-L', 'size': 9, 'capacity': 8,'lock': False ,'target': None, 'hp': 6, 'strengh': 0, 'ore': 0, 'cost': 4, 'coord': (0,0),'moved' : False}}
    player_1,player_2 = update_player_data (player_1,player_2)
    
    peace = 0
    
    player = player_id
    nb_turn = 1
    phase = ''
    while ending_conditions (peace,player_1,player_2) == False:
        if player == 1:
            
            player_1 , order_1,phase = naive_ia_playing(game_board, player_2, player_1, nb_turn,phase)
            notify_remote_orders(connection, order_1)
            order_2 = get_remote_orders (connection)
        else:
            player_2 , order_2,phase = naive_ia_playing(game_board, player_1, player_2, nb_turn,phase)
            notify_remote_orders(connection, order_1)
            order_1 = get_remote_orders (connection)
        print (' Turn n°%d' % nb_turn)  
          
        peacefull, player_1 , player_2 = entire_turn (player_1,player_2,boxes,ships,game_board,order_1,order_2)
        nb_turn += 1
        if peacefull == True:
            peace += 1
        else:
            peace =0
        display_game(player_1, player_2, boxes, game_board)

    print ('Game over')





os.chdir()
mother('testboard.mw',player_id,remote_IP,verbose)
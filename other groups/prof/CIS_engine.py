# -*- coding: utf-8 -*-

import colored, math, os, string, time


import remote_play

from CIS_AI import get_AI_purchase, get_AI_actions


# game rules, colors...
SPECS = {'fighter':{'max_speed':5, 'hp':3, 'damage':1, 'range':5, 'cost':10},
         'destroyer':{'max_speed':2, 'hp':8, 'damage':2, 'range':7, 'cost':20},
         'battlecruiser':{'max_speed':1, 'hp':20, 'damage':4, 'range':10, 'cost':30}}

ANGLES = {'up':0, 'down':180, 'left':270, 'right':90, 'up-left':315, 'up-right':45, 'down-left':225, 'down-right':135}

# https://www.w3schools.com/charsets/ref_utf_geometric.asp
# https://www.w3schools.com/charsets/ref_utf_arrows.asp
SHIP_SYMBOLS = {'fighter':{0:'↑',45:'↗',90:'→',135:'↘',180:'↓',225:'↙',270:'←',315:'↖'},
                'destroyer':{0:'⇑',45:'⇗',90:'⇒',135:'⇘',180:'⇓',225:'⇙',270:'⇐',315:'⇖'},
                'battlecruiser':{0:'▲',45:'◥',90:'▶',135:'◢',180:'▼',225:'◣',270:'◀',315:'◤'}}

MIN_NB_ROWS = 30
MIN_NB_COLS = 30

MAX_NB_ROWS = 40
MAX_NB_COLS = 60

FRAME_COLOR = 'grey_58'
SQUARE_D_COLOR = 'grey_15'
SQUARE_L_COLOR = 'grey_23'
IMPACT_D_COLOR = 'salmon_1' #'yellow_1' 
IMPACT_L_COLOR = 'salmon_1'   #'wheat_1'

NEUTRAL_COLOR = 'light_green'
SHIP_COLORS = {1:(15, 226, 220, 215, 208, 202, 196, 1)[::-1],
               2:(153, 14, 6, 69, 33, 27, 24, 21)[::-1]}

FREEZE_DURATION = .2


# game implementation
def load_CIS_file(CIS_file, game):
    """Load a CIS board from a .cis file.
    
    Parameters
    ----------
    CIS_file: name of CIS file (str)
    game: game data structure (dict)
    
    Raises
    ------
    ValueError: if CIS file is empty (no board size specification)
    ValueError: if board size is not correctly specified in CIS file
    ValueError: if board in CIS file is too small (min 40 x 40)
    ValueError: if ships are not correctly specified in CIS file
    
    """
    
    fd = open(CIS_file, 'r')
    lines = fd.readlines()
    fd.close()
    
    # get board size
    if len(lines) == 0:
        raise ValueError, 'CIS file is empty (no board size specification)'

    header = string.translate(lines[0], None, '\n\r')
    
    try:
        nb_rows, nb_cols = header.split()
        game['nb_rows'] = int(nb_rows)
        game['nb_cols'] = int(nb_cols)
    except:
        raise ValueError, 'board size is not correctly specified in CIS file (header:"%s")' % header

    if game['nb_rows'] < MIN_NB_ROWS or game['nb_cols'] < MIN_NB_COLS:
        raise ValueError, 'board size is too small in CIS file: %d x %d' % (game['nb_rows'], game['nb_cols'])
    if game['nb_rows'] > MAX_NB_ROWS or game['nb_cols'] > MAX_NB_COLS:
        raise ValueError, 'board size is too large in CIS file: %d x %d' % (game['nb_rows'], game['nb_cols'])
    
    # create empty board
    game['board'] = {}
    for row in range(game['nb_rows']):
        for col in range(game['nb_cols']):
            game['board'][(row, col)] = []
    
    # place abandoned ships
    game['ships'] = {0:{}, 1:{}, 2:{}}
    for order in lines[1:]:
        order = string.translate(order, None, '\n\r')
        
        try:
            row, col, name_type, orientation = order.split()
            name, type = name_type.split(':')
            row = int(row)-1
            col = int(col)-1
        
            game['board'][(row, col)].append((0, name))
            game['ships'][0][name] = {'pos':(row, col),
                                      'type':type,
                                      'cost':game['specs'][type]['cost'],
                                      'angle':ANGLES[orientation],
                                      'speed':0,
                                      'max_speed':game['specs'][type]['max_speed'],
                                      'hp':game['specs'][type]['hp'],
                                      'max_hp':game['specs'][type]['hp'],
                                      'damage':game['specs'][type]['damage'],
                                      'range':range}
        except:
            raise ValueError, 'ships are not correctly specified in CIS file (order:"%s")' % order


def ship_to_text(game, player_id, ship_name):
    """Returns a text representation of a ship.
    
    Parameters
    ----------
    game: game data structure (dict)
    player_id: player id (int)
    ship_name: ship name (str)    
    
    """
    
    if player_id == 0:
        ship_s = colored.fg(NEUTRAL_COLOR)
    else:
        ship_s = colored.fg(SHIP_COLORS[player_id][int(round(7*float(game['ships'][player_id][ship_name]['hp'])/game['ships'][player_id][ship_name]['max_hp']))])

    ship_s += SHIP_SYMBOLS[game['ships'][player_id][ship_name]['type']][game['ships'][player_id][ship_name]['angle']]
    
    return ship_s

    
def show_CIS_board(game):
    """Show a CIS board.
    
    Parameters
    ----------
    game: game data structure (dict)
    
    """
    
    # freeze to see what is happening
    time.sleep(FREEZE_DURATION)
    
    # clear screen
    os.system('clear')
    
    # display top numbers
    game_s = '%s  '% colored.bg(FRAME_COLOR)
    for col_d in range(1, game['nb_cols']+1):
        if col_d % 5 == 0:
            game_s += string.zfill(str(col_d), 2)
        else:
            game_s += '  '
    game_s += '  %s\n' % colored.attr('reset')

    # display main part
    for row_d in range(1, game['nb_rows']+1):
        # display left numbers
        game_s += colored.bg(FRAME_COLOR)
        if row_d % 5 == 0:
            game_s += string.zfill(str(row_d), 2)
        else:
            game_s += '  '
        game_s += colored.attr('reset')
        
        # display squares
        for col_d in range(1, game['nb_cols']+1):
            ships = game['board'][(row_d-1, col_d-1)]
            
            ship_names = {}
            nb_ships = {}
            
            for player_id in (0, 1, 2):
                ship_names[player_id] = [ship[1] for ship in ships if ship[0] == player_id]
                nb_ships[player_id] = len(ship_names[player_id])
            
            # set square background color
            if (((row_d-1)/5)+((col_d-1)/5)) % 2 == 0:
                if (row_d-1, col_d-1) in game['impacts']:
                    game_s += colored.bg(IMPACT_D_COLOR)
                else:
                    game_s += colored.bg(SQUARE_D_COLOR)
            else:
                if (row_d-1, col_d-1) in game['impacts']:
                    game_s += colored.bg(IMPACT_L_COLOR)
                else:
                    game_s += colored.bg(SQUARE_L_COLOR)
            
            # add symbol on square (left part)
            if nb_ships[1] == 1 or (nb_ships[1] == 2 and nb_ships[2] == 0):
                game_s += ship_to_text(game, 1, ship_names[1][0])
            elif nb_ships[1] >= 2:
                game_s += colored.fg(SHIP_COLORS[1][-1]) + '◉'
            elif nb_ships[2] == 2:
                game_s += ship_to_text(game, 2, ship_names[2][1])
            elif nb_ships[0] in (1, 2):
                game_s += ship_to_text(game, 0, ship_names[0][0])
            else:
                game_s += ' '
            
            # add symbol on square (right part)
            if nb_ships[2] == 1 or (nb_ships[2] == 2 and nb_ships[1] == 0):
                game_s += ship_to_text(game, 2, ship_names[2][0])
            elif nb_ships[2] >= 2:
                game_s += colored.fg(SHIP_COLORS[2][-1]) + '◉'
            elif nb_ships[1] == 2:
                game_s += ship_to_text(game, 1, ship_names[1][1])
            elif nb_ships[0] == 2:
                game_s += ship_to_text(game, 0, ship_names[0][1])
            else:
                game_s += ' '
            
            # reset colors
            game_s += colored.attr('reset')
        
        # display right frame part
        game_s += '%s  %s\n' % (colored.bg(FRAME_COLOR), colored.attr('reset'))
    
    game_s += colored.bg(FRAME_COLOR) + '  '*(game['nb_cols']+2) + colored.attr('reset')

    print game_s
    

def get_purchase(game, player_id):
    """Returns purchase orders for a given player.
    
    Parameters
    ----------
    game: game data structure (dict)
    player_id: id of player (int)
    
    Returns
    -------
    orders: purchase orders (str)
    
    Notes
    -----
    Purchase orders are printed.
    
    """
    
    player_type = game['players'][player_id]['type']

    if player_type == 'human':
        orders = raw_input('purchase order of human player %d: ')
    else:
        if player_type == 'AI':
            orders = get_AI_purchase(game, player_id)
        else:
            orders = get_remote_purchase(game, player_id)
        
        print 'purchase order of player %d: %s' % (player_id, orders)
    
    return orders


def get_remote_purchase(game, player_id):
    """Return purchase order of remote player.
    
    Parameters
    ----------
    game: game data structure (dict)
    player_id: player id of remote player (int)

    Returns
    -------
    orders: purchase orders of remote player (str)
    
    """
    
    return remote_play.get_remote_orders(game['players'][player_id]['connection'])


def purchase_ships(game, orders):
    """Purchase ships for a given player.
    
    Parameters
    ----------
    game: game data structure (dict)
    player_id: id of player (int)
    orders: purchase orders (str)
    
    """
    
    for player_id in (1, 2):
        money = 100
        for order in orders[player_id].split():
            try:
                name, type = order.split(':')
                cost = game['specs'][type]['cost']
                if cost <= money:
                    if player_id == 1:
                        pos = (9, 9)
                        angle = 135
                    else:
                        pos = (game['nb_rows']-10, game['nb_cols']-10)
                        angle = 315
                        
                    game['ships'][player_id][name] = {'pos':pos,
                                                      'type':type,
                                                      'cost':cost,
                                                      'angle':angle,
                                                      'speed':0,
                                                      'max_speed':game['specs'][type]['max_speed'],
                                                      'hp':game['specs'][type]['hp'],
                                                      'max_hp':game['specs'][type]['hp'],
                                                      'damage':game['specs'][type]['damage'],
                                                      'range':game['specs'][type]['range']}

                    game['players'][player_id]['cum_score'] += cost
                  
                    game['board'][pos].append((player_id, name))

                    money -= cost
                else:
                    print 'purchase order "%s" of player %d ignored (not enough money)' % (order, player_id)
            except:
                print 'incorrect purchase order "%s" of player %d ignored' % (order, player_id)


def get_actions(game, player_id):
    """Returns actions of a given player.
    
    Parameters
    ----------
    game: game data structure (dict)
    player_id: id of player (int)
    
    Returns
    -------
    orders (str)
    
    Notes
    -----
    Action orders are printed.
    
    """

    player_type = game['players'][player_id]['type']
    
    if player_type == 'human':
        orders = raw_input('orders of human player %d: ')
    else:
        if player_type == 'AI':
            orders = get_AI_actions(game, player_id)
        else:
            orders = get_remote_actions(game, player_id)
        
        print 'orders of player %d: %s' % (player_id, orders)
    
    return orders


def get_remote_actions(game, player_id):
    """Return purchase order of remote player.
    
    Parameters
    ----------
    game: game data structure (dict)
    player_id: player id of remote player (int)

    Returns
    -------
    orders: action orders of remote player (str)
    
    """
    
    return remote_play.get_remote_orders(game['players'][player_id]['connection'])
    

def apply_actions(game, orders):
    """Apply orders of both players.
    
    Parameters
    ----------
    game: game data structure (dict)
    orders: orders of both players (str)
    
    Returns
    -------
    missiles: missiles fired (list)
    
    Notes
    -----
    Print warning messages for incorrect orders.
    
    """
    
    missiles = []
    
    for player_id in (1, 2):
        for order in orders[player_id].split():
            try:
                ship_name, action = order.split(':')
                ship = game['ships'][player_id][ship_name]
                
                if action == 'faster':
                    speed = ship['speed']
                    if speed < ship['max_speed']:
                        game['ships'][player_id][ship_name]['speed'] = speed + 1
                    else:
                        print '   order "%s" of player %d ignored (max speed reached)' % (order, player_id)
                elif action == 'slower':
                    speed = ship['speed']
                    if speed > 0:
                        game['ships'][player_id][ship_name]['speed'] = speed - 1
                    else:
                        print '   order "%s" of player %d ignored (ship stationary)' % (order, player_id)
                elif action == 'left':
                    game['ships'][player_id][ship_name]['angle'] = (ship['angle']-45) % 360
                elif action == 'right':
                    game['ships'][player_id][ship_name]['angle'] = (ship['angle']+45) % 360
                else:
                    row, col = action.split('-')
                    row = int(row)-1
                    col = int(col)-1

                    if row < 0 or row > game['nb_rows'] or col < 0 or row > game['nb_cols']:
                        print '   order "%s" of player %d ignored (out of board)' % (order, player_id)
                    elif abs(ship['pos'][0]-row) + abs(ship['pos'][1]-col) > ship['range']:
                        print '   order "%s" of player %d ignored (out of reach)' % (order, player_id)
                    else:
                        missiles.append({'pos':(row, col), 'damage':ship['damage']})
            except:
                print 'incorrect order "%s" of player %d ignored' % (order, player_id)
                       
    return missiles


def move_ships(game):
    """Move ships according to their direction and speed.
    
    Parameters
    ----------
    game: game data structure (dict)

    """
    
    for player_id in (1, 2):
        for ship_name in game['ships'][player_id]:
            ship = game['ships'][player_id][ship_name]
            
            game['board'][ship['pos']].remove((player_id, ship_name))
            
            row = ship['pos'][0]
            col = ship['pos'][1]
            speed = ship['speed']
            angle = ship['angle']
            
            game['ships'][player_id][ship_name]['pos'] = ((row-speed * int(round(math.cos(angle*math.pi/180)))) % game['nb_rows'],
                                                          (col+speed * int(round(math.sin(angle*math.pi/180)))) % game['nb_cols'])

            game['board'][game['ships'][player_id][ship_name]['pos']].append((player_id, ship_name))


def impact_missiles(game, missiles):
    """Apply damage by fired missiles.
    
    Parameters
    ----------
    game: game data structure (dict)
    missiles: missiles (list)
        
    """
    
    ship_destroyed = False
    ship_touched = False    

    for missile in missiles:
        pos = missile['pos']
   	damage = missile['damage']
        
        destroyed_ships = []
        
        for player_id, ship_name in game['board'][pos]:
            hp = game['ships'][player_id][ship_name]['hp'] - damage
	    ship_touched = True
            
            if hp > 0:
                game['ships'][player_id][ship_name]['hp'] = hp
            else:
                destroyed_ships.append((pos, player_id, ship_name))
    
        if len(destroyed_ships) > 0:
            ship_destroyed = True
            
        for pos, player_id, ship_name in destroyed_ships:
            game['board'][pos].remove((player_id, ship_name))
            
            game['players'][player_id]['cum_score'] -= game['ships'][player_id][ship_name]['cost']
            
            del game['ships'][player_id][ship_name]

        game['impacts'].append(pos)

    if ship_touched:
        game['nb_void_turns'] = 0
    else:
        game['nb_void_turns'] += 1


def capture_ships(game):
    """Capture abandoned ships.
    
    Parameters
    ----------
    game: game data structure (dict)

    """
    
    captures = []
    for ship_name in game['ships'][0]:
        pos = game['ships'][0][ship_name]['pos']
        
        nb_ships = {}
        for player_id in (1, 2):
            nb_ships[player_id] = len([ship for ship in game['board'][pos] if ship[0] == player_id])
        
        if nb_ships[1] > 0 and nb_ships[2] == 0:
            captures.append((1, pos, ship_name))
        elif nb_ships[2] > 0 and nb_ships[1] == 0:
            captures.append((2, pos, ship_name))

    for new_owner, pos, ship_name in captures:
        if ship_name in game['ships'][new_owner]:
            new_ship_name = ship_name + '_2'
        else:
            new_ship_name = ship_name
            
        game['ships'][new_owner][new_ship_name] = game['ships'][0][ship_name]
        del game['ships'][0][ship_name]
        
        game['players'][new_owner]['cum_score'] += game['ships'][new_owner][new_ship_name]['cost']
                
        game['board'][pos][game['board'][pos].index((0, ship_name))] = (new_owner, new_ship_name)
        
        
def play_CIS(CIS_file,
             player_1_type='AI', player_1_IP='127.0.0.1',
             player_2_type='AI', player_2_IP='127.0.0.1',
             max_nb_void_turns=10, verbose=True):
    """Play a Coders in Space game.
    
    Parameters
    ----------
    CIS_file: name of CIS file (str)
    player_1_type: type of player 1 (str)
    player_1_IP: IP of player 1, if relevant (str)
    player_2_type: type of player 2 (str)
    player_1_IP: IP of player 2, if relevant (str)
    max_nb_void_turns: maximum number of turns without attacks (int)
    verbose: whether engine is verbose (bool)

    Raises
    ------
    ValueError: if board in CIS file is too small
    
    Notes
    -----
    Player type is either human, AI or remote.
    
    """
    
    # init game data structure
    game = {'specs':SPECS,
            'players':{1:{'type':player_1_type, 'IP':player_1_IP, 'cum_score':0},
                       2:{'type':player_2_type, 'IP':player_2_IP, 'cum_score':0}}}
            
    # init connections, if necessary
    for player_id in (1, 2):
        if game['players'][player_id]['type'] == 'remote':
            game['players'][player_id]['connection'] = remote_play.connect_to_player(player_id, remote_IP=game['players'][player_id]['IP'], verbose=True)
                
    # phase 1: create game board
    try:
        load_CIS_file(CIS_file, game)
    except ValueError as e:
        print 'could not load CIS file, abording...\   ' + str(e)
        return
    
    game['impacts'] = []
    show_CIS_board(game)

    # phase 2: place ships on board
    orders = {}
    for player_id in (1, 2):
        orders[player_id] = get_purchase(game, player_id)
    
        if game['players'][3-player_id]['type'] == 'remote':
            remote_play.notify_remote_orders(game['players'][3-player_id]['connection'], orders[player_id])
        
    purchase_ships(game, orders)
    
    show_CIS_board(game)

    # phase 3: repeat turns until game is over
    game['turn'] = 0
    game['nb_void_turns'] = 0
    
    while game['nb_void_turns'] < max_nb_void_turns and len(game['ships'][1]) > 0 and len(game['ships'][2]) > 0:
        show_CIS_board(game)
        game['impacts'] = []
        
        orders = {}
        for player_id in (1, 2):
            orders[player_id] = get_actions(game, player_id)
            
            if game['players'][3-player_id]['type'] == 'remote':
                remote_play.notify_remote_orders(game['players'][3-player_id]['connection'], orders[player_id])

        missiles = apply_actions(game, orders)    

        move_ships(game)

        impact_missiles(game, missiles)   

        capture_ships(game)

        game['turn'] += 1
    
    # end game
    if game['nb_void_turns'] == max_nb_void_turns:
        print 'game ended %d turns (too many turns without damage)' % game['turn']
    else:
        print 'game ended after %d turns (one of the player has no longer any ship)' % game['turn']
        
    print 'player 1 has %d points and player 2 has %d points\n' % (game['players'][1]['cum_score'], game['players'][2]['cum_score'])
    if game['players'][1]['cum_score'] > game['players'][2]['cum_score']:
        print 'winner: player 1'
    elif game['players'][2]['cum_score'] > game['players'][1]['cum_score']:
        print 'winner: player 2'
    else:
        print 'draw: both players have identical score'




# game test
if __name__ == "__main__":
    import sys
    
    CIS_file = sys.argv[1]
    player_1_type = sys.argv[2]
    player_1_IP = sys.argv[3]
    player_2_type = sys.argv[4]
    player_2_IP = sys.argv[5]
    max_nb_void_turns = int(sys.argv[6])
    verbose = bool(sys.argv[7])
    
    play_CIS(CIS_file,
             player_1_type, player_1_IP,
             player_2_type, player_2_IP,
             max_nb_void_turns, verbose)

#-*- coding: utf-8 -*-

import colored, math, os, os.path, string, time

import remote_play

from MW_AI import get_AI_actions


# game rules, colors...     
SPECS = {'scout':{'tonnage':0, 'life':3, 'attack':1, 'range':3, 'cost':3},
         'warship':{'tonnage':0, 'life':18, 'attack':3, 'range':5, 'cost':9},
         'excavator-S':{'tonnage':1, 'life':2, 'attack':0, 'range':0, 'cost':1},
         'excavator-M':{'tonnage':4, 'life':3, 'attack':0, 'range':0, 'cost':2},
         'excavator-L':{'tonnage':8, 'life':6, 'attack':0, 'range':0, 'cost':4}}
         
MASKS = {'scout':((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)),
         'warship':((-2, -1), (-2, 0), (-2, 1), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (2, -1), (2, 0), (2, 1)),
         'excavator-S':((0, 0),),
         'excavator-M':((-1, 0), (0, -1), (0, 0), (0, 1), (1, 0)),
         'excavator-L':((-2, 0), (-1, 0), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (1, 0), (2, 0))}

RADII = {'scout':3,
         'warship':5,
         'excavator-S':1,
         'excavator-M':2,
         'excavator-L':3}


MIN_NB_ROWS = 30
MIN_NB_COLS = 30

MAX_NB_ROWS = 40
MAX_NB_COLS = 80

FRAME_COLOR = 'grey_58'

SQUARE_D_COLOR = 'grey_15'
SQUARE_L_COLOR = 'grey_23'

IMPACT_COLOR = 'orange_red_1'#'salmon_1'

IN_RANGE_PLAYER_1_COLOR = 'plum_1'
IN_RANGE_PLAYER_2_COLOR = 'steel_blue_1a'
IN_RANGE_NEUTRAL_COLOR = 'sea_green_3'

PORTAL_COLORS = {1:'light_coral',
                 2:'deep_sky_blue_1'}

ASTEROID_FULL_COLOR = 'gold_1' #'orange_1'
ASTEROID_EMPTY_COLOR = 'wheat_1' #'orange_1'

NEUTRAL_COLOR = 'light_green'
PLAYER_1_COLOR = 'red'
PLAYER_2_COLOR = 'blue_1'

#SHIP_COLORS = {1:(15, 226, 220, 215, 208, 202, 196, 1),
#               2:(153, 14, 6, 69, 33, 27, 24, 21)}

FREEZE_DURATION = .1

MAX_NB_VOID_TURNS = 200


# game implementation
def load_MW_file(MW_file, game):
    """Load a MW board from a .mw file.
    
    Parameters
    ----------
    MW_file: name of MW file (str)
    game: game data structure (dict)
    
    Raises
    ------
    ValueError: if MV file does not contain at least 6 lines
    ValueError: if board size is not correctly specified in MW file
    ValueError: if board in MW file is too small (min 30 x 30) or too large (max 40 x 80)
    ValueError: if portals or asteroids are not correctly specified in MW file
    
    """
    
    fd = open(MW_file, 'r')
    lines = fd.readlines()
    fd.close()

    # check file size
    if len(lines) < 6:
        raise ValueError('MW file is too short (should be at least 6 lines long, %d found)' % len(lines))
        
    # get board size
    board_cmd = str.strip(lines[0], '\n\r')
    if board_cmd != 'size:':
        raise ValueError('board size header is invalid in MW file: "%s"' % board_cmd)
    
    board_size = str.strip(lines[1], '\n\r')
    try:
        nb_rows, nb_cols = board_size.split()
        game['nb_rows'] = int(nb_rows)
        game['nb_cols'] = int(nb_cols)
    except:
        raise ValueError('board size is invalid in MW file: "%s"' % board_size)

    if game['nb_rows'] < MIN_NB_ROWS or game['nb_cols'] < MIN_NB_COLS:
        raise ValueError('board size is too small in MW file: %d x %d' % (game['nb_rows'], game['nb_cols']))
    if game['nb_rows'] > MAX_NB_ROWS or game['nb_cols'] > MAX_NB_COLS:
        raise ValueError('board size is too large in MW file: %d x %d' % (game['nb_rows'], game['nb_cols']))
    
    # create portals
    portals_cmd = str.strip(lines[2], '\n\r')
    if portals_cmd != 'portals:':
        raise ValueError('portals header is invalid in MW file: "%s"' % portals_cmd)
        
    for player_id, line_id in ((1, 3), (2, 4)):
        portal_pos = str.strip(lines[line_id], '\n\r')
        try:
            row, col = portal_pos.split()
            game['portals'][player_id] = {'pos':(int(row), int(col)), 'life':100}
        except:
            raise ValueError('portal position is invalid for player %d in MW file: "%s"' % (player_id, portal_pos))
            
        if game['portals'][player_id]['pos'][0] < 3 or game['portals'][player_id]['pos'][0] > game['nb_rows']-2 or game['portals'][player_id]['pos'][1] < 3 or game['portals'][player_id]['pos'][1] > game['nb_cols']-2:
            raise ValueError('portal position is invalid for player %d in MW file: "%s"' % (player_id, portal_pos))
    
    # create asteroids
    asteroids_cmd = str.strip(lines[5], '\n\r')
    if asteroids_cmd != 'asteroids:':
        raise ValueError('asteroids header is invalid in MW file:"%s"' % asteroids_cmd)

    for line_id in range(6, len(lines)):
        asteroid_spec = str.strip(lines[line_id], '\n\r')
        try:
            row, col, ore, pace = asteroid_spec.split()
            
            pos = (int(row), int(col))
            ore = int(ore)
            pace = int(pace)
            
            game['asteroids'][pos] = {'ore':ore, 'pace':pace}
        except:
            raise ValueError('asteroid specification is invalid MW file: "%s"' % asteroid_spec)
    
        if pos[0] < 3 or pos[0] > game['nb_rows']-2 or pos[1] < 3 or pos[1] > game['nb_cols']-2 or ore <= 0 or pace not in (1, 2):
            raise ValueError('asteroid specification is invalid in MW file: "%s"' % asteroid_spec)


def show_MW_board(game):
    """Show a MW board.
    
    Parameters
    ----------
    game: game data structure (dict)
    
    """
        
    # display top numbers
    game_s = '%s  ' % colored.bg(FRAME_COLOR)
    for col in range(1, game['nb_cols']+1):
        if col % 5 == 0:
            game_s += str.zfill(str(col), 2)
        else:
            game_s += '  '
    game_s += '  %s' % colored.attr('reset')
    
    # display game status
    game_s += '   turn %d: p1->%d[%.2f/%.2f-%.2f] / p2->%d[%.2f/%.2f-%.2f] (%d void)\n' % (game['turn'],
                                                                                 game['portals'][1]['life'],
                                                                                 game['players'][1]['ore'], game['players'][1]['cum_ore'], game['players'][1]['mined_ore']-game['players'][1]['cum_ore'],
                                                                                 game['portals'][2]['life'],
                                                                                 game['players'][2]['ore'], game['players'][2]['cum_ore'], game['players'][2]['mined_ore']-game['players'][2]['cum_ore'],
                                                                                 game['nb_void_turns'])


    # prepare check ships
    ships = {1:{}, 2:{}}
    for player_id in (1, 2):
        for ship_name in game['ships'][player_id]:
            ship = game['ships'][player_id][ship_name]
            for (drow, dcol) in ship['mask']:
                ships[player_id][(ship['pos'][0]+drow, ship['pos'][1]+dcol)] = True
                    
    # display main part
    for row in range(1, game['nb_rows']+1):
        # display left numbers
        game_s += colored.bg(FRAME_COLOR)
        if row % 5 == 0:
            game_s += str.zfill(str(row), 2)
        else:
            game_s += '  '
        game_s += colored.attr('reset')
        
        # display squares
        for col in range(1, game['nb_cols']+1):
            # compute default color
            if ((row-1)//5+(col-1)//5) % 2 == 0:
                bg_color = colored.bg(SQUARE_D_COLOR)
            else:
                bg_color = colored.bg(SQUARE_L_COLOR)
            
            if (row, col) in game['explosions']:
                # explosion detected
                bg_color = colored.bg(IMPACT_COLOR)
            else:
                if (row, col) in game['asteroids']:
                    # asteroid found
                    if game['asteroids'][(row, col)]['ore'] > 0:
                        bg_color = colored.bg(ASTEROID_FULL_COLOR)
                    else:
                        bg_color = colored.bg(ASTEROID_EMPTY_COLOR)
                else:
                    for player_id in (1, 2):
                        if abs(row-game['portals'][player_id]['pos'][0]) <= 2 and abs(col-game['portals'][player_id]['pos'][1]) <= 2 and game['portals'][player_id]['life'] > 0:
                            # portal found
                            bg_color = colored.bg(PORTAL_COLORS[player_id])
            
            game_s += bg_color
            
            # check ships            
            if (row, col) in ships[1] and (row, col) not in ships[2]:#ships[1] and not ships[2]:
                game_s += colored.fg(PLAYER_1_COLOR)
            elif (row, col) not in ships[1] and (row, col) in ships[2]:#not ships[1] and ships[2]:
                game_s += colored.fg(PLAYER_2_COLOR)
            elif (row, col) in ships[1] and (row, col) in ships[2]:#ships[1] and ships[2]:
                game_s += colored.fg(NEUTRAL_COLOR)
            
            if (row, col) in ships[1] or (row, col) in ships[2]:#ships[1] or ships[2]:
                # square contains a ship
                game_s += '▒▒' # other candidates: ▪█▓▒░
            else:
                # check if square is in range of a ship
                in_range = {1:False, 2:False}
                for player_id in (1, 2):
                    for ship_name in game['ships'][player_id]:
                        ship = game['ships'][player_id][ship_name]
                        if ship['type'] in ('scout', 'warship') and abs(ship['pos'][0]-row) + abs(ship['pos'][1]-col) <= ship['range']:
                            in_range[player_id] = True
                
                if in_range[1] and not in_range[2]:
                    game_s += colored.fg(IN_RANGE_PLAYER_1_COLOR)
                elif not in_range[1] and in_range[2]:
                    game_s += colored.fg(IN_RANGE_PLAYER_2_COLOR)
                elif in_range[1] and in_range[2]:
                    game_s += colored.fg(IN_RANGE_NEUTRAL_COLOR)
                
                if in_range[1] or in_range[2]:
                    # square is empty, but in range
                    game_s += '░░'
                else:
                    # square is empty and not in range
                    game_s += '  '
            
            # reset colors
            game_s += colored.attr('reset')
        
        # display right frame part
        game_s += '%s  %s\n' % (colored.bg(FRAME_COLOR), colored.attr('reset'))
    
    game_s += colored.bg(FRAME_COLOR) + '  '*(game['nb_cols']+2) + colored.attr('reset')

    print(game_s)    
    

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
        orders = input('orders of human player %d: ' % player_id)
    else:
        print('waiting for orders from %s player %d...' % (player_type, player_id))
        
        if player_type == 'AI':
            orders = get_AI_actions(game, player_id)
        else:
            orders = get_remote_actions(game, player_id)
        
        print('%d-long string received from %s player %d' % (len(orders), player_type, player_id))
    
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


def purchase_ships(game, orders):
    """Purchase ships for both players.
    
    Parameters
    ----------
    game: game data structure (dict)
    orders: purchase orders (dict)

    Notes
    -----
    Print warning messages for incorrect orders.
        
    """
    
    for player_id in (1, 2):
        for order in orders[player_id]:
            try:
                ship_name, ship_type = order.split(':')
                
                if ship_type in ('scout', 'warship', 'excavator-S', 'excavator-M', 'excavator-L'):
                    # purchase order detected
                    if game['specs'][ship_type]['cost'] <= game['players'][player_id]['ore']:
                        game['ships'][player_id][ship_name] = {'type':ship_type,
                                                               'tonnage':game['specs'][ship_type]['tonnage'],
                                                               'life':game['specs'][ship_type]['life'],
                                                               'attack':game['specs'][ship_type]['attack'],
                                                               'range':game['specs'][ship_type]['range'],
                                                               'mask':game['masks'][ship_type],
                                                               'pos':game['portals'][player_id]['pos'],
                                                               'status':'released',
                                                               'ore':0}
                                                               
                        game['players'][player_id]['ore'] -= game['specs'][ship_type]['cost']
                    else:
                        print('purchase order "%s" of player %d ignored (not enough ore)' % (order, player_id))
            except:
                print('incorrect order "%s" of player %d ignored' % (order, player_id))
 
 
def lock_and_release(game, orders):
    """Lock/release ships for both players.
    
    Parameters
    ----------
    game: game data structure (dict)
    orders: purchase orders (dict)

    Notes
    -----
    Print warning messages for incorrect orders.
        
    """
    
    for player_id in (1, 2):
        for order in orders[player_id]:
            try:
                ship_name, action = order.split(':')
                
                if action == 'lock' or action == 'release':
                    # lock/release action detected
                    ship = game['ships'][player_id][ship_name]
                    if ship['type'] in ('excavator-S', 'excavator-M', 'excavator-L'): 
                        if (action == 'lock' and ship['status'] == 'released') or (action == 'release' and ship['status'] == 'locked'):
                            if action == 'lock':
                                if ship['pos'] in game['asteroids'] or ship['pos'] == game['portals'][player_id]['pos']:
                                    ship['status'] = 'locked'
                                else:
                                    print('lock/release order "%s" of player %d ignored (nothing to lock)' % (order, player_id))
                            elif action == 'release':
                                ship['status'] = 'released'
                        else:
                            print('lock/release order "%s" of player %d ignored (already locked/released)' % (order, player_id))
                    else:
                        print('lock/release order "%s" of player %d ignored (not an excavator)' % (order, player_id))
            except:
                print('incorrect order "%s" of player %d ignored' % (order, player_id))
 
 
def move_and_fight(game, orders):
    """Execute move and fight orders of both players.
    
    Parameters
    ----------
    game: game data structure (dict)
    orders: orders of both players (str)
    
    Notes
    -----
    Print warning messages for incorrect orders.
    
    """
    
    explosions = []    

    for player_id in (1, 2):
        moving_ships = []
        
        for order in orders[player_id]:
            try:        
                ship_name, action = order.split(':')
                if action[0] == '@':
                    # move action detected
                    row, col = action[1:].split('-')
                    row = int(row)
                    col = int(col)

                    if row >= 1 and row <= game['nb_rows'] and col >= 1 and col <= game['nb_cols']:                
                        ship = game['ships'][player_id][ship_name]

                        if abs(row-ship['pos'][0]) <= 1 and abs(col-ship['pos'][1]) <= 1:
                            inside_board = True
                            for (drow, dcol) in ship['mask']:
                                if row+drow < 1 or row+drow > game['nb_rows'] or col+dcol < 1 or col+dcol > game['nb_cols']:
                                    inside_board = False
                                            
                            if inside_board:
                                ship['pos'] = (row, col)
                                moving_ships.append(ship_name)
                            else:
                                print('move order "%s" of player %d ignored (out of board)' % (order, player_id))
                        else:
                            print('move order "%s" of player %d ignored (out of reach)' % (order, player_id))
                    else:
                        print('move order "%s" of player %d ignored (out of board)' % (order, player_id))
                        
                if action[0] == '*':
                    # fight action detected
                    if ship_name not in moving_ships:
                        row, col = action[1:].split('-')
                        row = int(row)
                        col = int(col)
                        
                        ship = game['ships'][player_id][ship_name]

                        if ship['type'] in ('scout', 'warship'):
                            if row >= 1 and row <= game['nb_rows'] and col >= 1 and col <= game['nb_cols']:
                                if abs(row-ship['pos'][0]) + abs(col-ship['pos'][1]) <= ship['range']:
                                    explosions.append((row, col, ship['attack']))
                                else:
                                    print('fight order "%s" of player %d ignored (out of range)' % (order, player_id))
                            else:
                                print('fight order "%s" of player %d ignored (out of board)' % (order, player_id))
                        else:
                            print('fight order "%s" of player %d ignored (not a fighter)' % (order, player_id))
                    else:
                        print('ship %s of player %d got move (done) and fight (ignored) orders at same turn' % (ship_name, player_id))                     
            except:
                print('incorrect order "%s" of player %d ignored' % (order, player_id))
    
    # deal damage for explosions
    for row, col, attack in explosions:
        # check portals
        for player_id in (1, 2):
            if abs(game['portals'][player_id]['pos'][0]-row) <= 2 and abs(game['portals'][player_id]['pos'][1]-col) <= 2:
                game['portals'][player_id]['life'] -= attack
                if game['portals'][player_id]['life'] < 0:
                    game['portals'][player_id]['life'] = 0
                    
        # check ships
        for player_id in (1, 2):
            destroyed = []
            for ship_name in game['ships'][player_id]:
                ship = game['ships'][player_id][ship_name]
                
                reached = False
                for drow, dcol in ship['mask']:
                    if ship['pos'][0]+drow == row and ship['pos'][1]+dcol == col:
                        reached = True
          
                if reached:
                    ship['life'] -= attack
                    if ship['life'] <= 0:
                        destroyed.append(ship_name)
            
            # remove destroyed ships
            for ship_name in destroyed:
                del game['ships'][player_id][ship_name]

    # record explosions for display + void turn detection    
    for explosion in explosions:
        game['explosions'].append(explosion[:2])


def load_and_unload(game, orders):
    """Load/unload ships for both players.
    
    Parameters
    ----------
    game: game data structure (dict)
    orders: purchase orders (dict)

    Notes
    -----
    Print warning messages for incorrect orders.
        
    """
    
    # check asteroids
    for pos in game['asteroids']:
        asteroid = game['asteroids'][pos]
        
        if asteroid['ore'] > 0:
            # find locked extractors
            locked = []
            for player_id in (1, 2):
                for ship_name in game['ships'][player_id]:
                    ship = game['ships'][player_id][ship_name]
                    if ship['pos'] == pos and ship['status'] == 'locked':
                        locked.append((player_id, ship))
            
            # fill locked extractors progressively
            unused_pace = asteroid['pace']
            while asteroid['ore'] > 0 and len(locked) > 0 and unused_pace > 0:
                # clip with unused pace
                min_capacity = unused_pace
    
                # find ship with smallest remaining capacity
                for player_id, ship in locked:
                    capacity = ship['tonnage'] - ship['ore']
                    if capacity < min_capacity:
                        min_capacity = capacity
                                
                # clip with remaining ore    
                if len(locked)*min_capacity > asteroid['ore']:
                    min_capacity  = asteroid['ore'] / len(locked)
                
                # load excavators (partially, if necessary)
                for player_id, ship in locked:
                    ship['ore'] += min_capacity
                    game['players'][player_id]['mined_ore'] += min_capacity
                    asteroid['ore'] -= min_capacity
                
                # remove excavators that are full
                locked = [(player_id, ship) for player_id, ship in locked if ship['ore'] < ship['tonnage']]

                # reduce pace accordingly
                unused_pace -= min_capacity

                # ensure that numerical precision does not mess things up
                if asteroid['ore'] < 1e-6:
                    asteroid['ore'] = 0
                if unused_pace < 1e-6:
                    unused_pace = 0
        
    # check portals               
    for player_id in (1, 2):
        for ship_name in game['ships'][player_id]:
            ship = game['ships'][player_id][ship_name]
            
            if ship['pos'] == game['portals'][player_id]['pos'] and ship['status'] == 'locked':
                game['players'][player_id]['ore'] += ship['ore']
                game['players'][player_id]['cum_ore'] += ship['ore']
                
                ship['ore'] = 0
            
 
def play_MW(MW_file,
            player_1_type='AI', player_1_IP='127.0.0.1',
            player_2_type='AI', player_2_IP='127.0.0.1',
            max_nb_void_turns=MAX_NB_VOID_TURNS,
            freeze_duration=FREEZE_DURATION,
            verbose=True):
    """Play a Mining Wars game.
    
    Parameters
    ----------
    MW_file: name of MW file (str)
    player_1_type: type of player 1 (str)
    player_1_IP: IP of player 1, if relevant (str)
    player_2_type: type of player 2 (str)
    player_1_IP: IP of player 2, if relevant (str)
    max_nb_void_turns: maximum number of turns without attacks (int)
    freeze_duraction: duration of screen freeze for display (float)
    verbose: whether engine is verbose (bool)

    Raises
    ------
    ValueError: if board in MW file is too small
    
    Notes
    -----
    Player type is either human, AI or remote.
    
    """
    
    # init game data structure
    game = {'specs':SPECS,
            'masks':MASKS,
            'radii':RADII,
            'players':{1:{'type':player_1_type, 'IP':player_1_IP, 'ore':4, 'cum_ore':0, 'mined_ore':0},
                       2:{'type':player_2_type, 'IP':player_2_IP, 'ore':4, 'cum_ore':0, 'mined_ore':0}},
            'portals':{},
            'asteroids':{},
            'ships':{1:{}, 2:{}},
            'explosions':[],
            'turn':1,
            'nb_void_turns':0}
    
    # create connections, if necessary
    for player_id in (1, 2):
        if game['players'][player_id]['type'] == 'remote':
            game['players'][player_id]['connection'] = remote_play.connect_to_player(player_id, remote_IP=game['players'][player_id]['IP'], verbose=True)
    
    # initialise game (create game board)
    try:
        load_MW_file(MW_file, game)
    except ValueError as e:
        print('could not load MW file, abording...\n   ' + str(e))
        return
  
    # initialise display
    os.system('clear')
    print('Mining Wars starting\n   %s player 1 vs. %s player 2 playing on map "%s"' % (game['players'][1]['type'], game['players'][2]['type'], os.path.basename(MW_file[:str.rfind(MW_file, '.mw')])))
    show_MW_board(game)  
      
    # main game loop: repeat turns until game is over
    while game['nb_void_turns'] < max_nb_void_turns and game['portals'][1]['life'] > 0 and game['portals'][2]['life'] > 0:
        # reset explosions
        game['explosions'] = []
       
       # freeze to see what is happening
        if game['players'][1]['type'] != 'human' or game['players'][2]['type'] != 'human':
            print('game freezing %.1f seconds for humans...' % freeze_duration)
            time.sleep(freeze_duration)

        # get orders from players (+remote notification)
        raw_orders = {}
        split_orders = {}
        
        for player_id in (1, 2):
            raw_orders[player_id] = get_actions(game, player_id)

            # basic sanity check
            if str.startswith(raw_orders[player_id], ' '):
                print('*** warning: orders of player %d starts with (a) space(s) -> cleaned ***' % player_id)
            if str.endswith(raw_orders[player_id], ' '):
                print('*** warning: orders of player %d ends with (a) space(s) -> cleaned ***' % player_id)
            if '  ' in raw_orders[player_id]:
                print('*** warning: orders of player %d contains double spaces -> cleaned ***' % player_id)

            # clean orders if necessary
            raw_orders[player_id] = raw_orders[player_id].strip()
            while '  ' in raw_orders[player_id]:
                raw_orders[player_id] = raw_orders[player_id].replace('  ', ' ')
            
            # notify remote player, if any            
            if game['players'][3-player_id]['type'] == 'remote':
                remote_play.notify_remote_orders(game['players'][3-player_id]['connection'], raw_orders[player_id])
                
            # extract individual orders
            split_orders[player_id] = raw_orders[player_id].split(' ')
            if len(split_orders[player_id]) == 1 and len(split_orders[player_id][0]) == 0:
                split_orders[player_id] = []            
        
        # phase 1: buy ships (+show board)
        purchase_ships(game, split_orders)
#    
        # phase 2: (un)lock ships
        lock_and_release(game, split_orders)
#        
        # phase 3: ships move and fight
        move_and_fight(game, split_orders)
        
        # phase 4: (un)load ore for excavator
        load_and_unload(game, split_orders)
        
        # update turn counter   
        game['turn'] += 1
        if len(game['explosions']) > 0:
            game['nb_void_turns'] = 0
        else:
            game['nb_void_turns'] += 1

        # show board after complete turn
        os.system('clear')
        for player_id in (1, 2):
            print('orders of player %d: %s' % (player_id, raw_orders[player_id][:150]))
        show_MW_board(game)
    
    # destroy connections, if necessary
    for player_id in (1, 2):
        if game['players'][player_id]['type'] == 'remote':
            try:
                remote_play.disconnect_from_player(game['players'][player_id]['connection'])
            except:
                pass

    # end game
    print('final score:\n   player 1 -> %d HP and %d ore\n   player 2 -> %d HP and %d ore\n' % (game['portals'][1]['life'], game['players'][1]['cum_ore'], game['portals'][2]['life'], game['players'][2]['cum_ore']))
    
    if game['nb_void_turns'] == max_nb_void_turns:
        print('game ended after %d turns (too many turns without damage)' % game['turn'])

        if game['portals'][1]['life'] > game['portals'][2]['life'] or (game['portals'][1]['life'] == game['portals'][2]['life'] and game['players'][1]['cum_ore'] > game['players'][2]['cum_ore']):
            print('   winner: player 1 (%d HP and %s ore vs. ')
        elif game['portals'][2]['life'] > game['portals'][1]['life'] or (game['portals'][1]['life'] == game['portals'][2]['life'] and game['players'][2]['cum_ore'] > game['players'][1]['cum_ore']):
            print('   winner: player 2')
        else:
            print('   draw: same score (portal life + cum. ore)')
    else:
        print('game ended after %d turns (at least one portal destroyed)' % game['turn'])
        
        if game['portals'][1]['life'] > 0:
            print('   winner: player 1')  
        elif game['portals'][2]['life'] > 0:
            print('   winner: player 2')
        elif game['portals'][1]['cum_ore'] > game['portals'][2]['cum_ore']:
            print('   winner: player 1')  
        elif game['portals'][2]['cum_ore'] > game['portals'][1]['cum_ore']:
            print('   winner: player 2')
        else:
            print('   draw: both portals destroyed and same score (cum. ore)')
            

# game test
if __name__ == "__main__":
    import sys
    
    MW_file = sys.argv[1]
    player_1_type = sys.argv[2]
    player_1_IP = sys.argv[3]
    player_2_type = sys.argv[4]
    player_2_IP = sys.argv[5]
    max_nb_void_turns = int(sys.argv[6])
    freeze_duration = float(sys.argv[7])
    verbose = bool(sys.argv[8])
    
    play_MW(MW_file,
            player_1_type, player_1_IP,
            player_2_type, player_2_IP,
            max_nb_void_turns, freeze_duration, verbose)

# -*- coding: utf-8 -*-
#note: search "edit here" to find places to edit game properties such as
#   unit's lives, their range, etc.
#importing modules
from random import randint
from copy import deepcopy
#prevents issues with "shallow copies", where 2 dictionaries are linked because they use the same items
import os
import remote_play as rp
import time
from importlib import reload

import AI_gr_31
reload(AI_gr_31)

#child function of create_game_board and execute_turn
def gb_manage_unit(name, data, board, action='add'):
    """Add or remove an unit from the data structure of the game board.

    Parameters
    ----------
    name: name of the unit to manage (str)
    data: data structure of the game's data (dict)
    board: data structure of the game board (list)
    action (optional): tells whether to add or remove the given unit (str)

    Returns
    -------
    updated_board: the board updated with the managed unit (list)

    Notes
    -----
    Inputs for the parameter action must be either 'add' or 'remove'.
    This function will give a Python error if the parts to add are off-limits.

    Version
    -------
    specification: Lucas Themelin (v.2 07/04/18)
    implementation: Lucas Themelin (v.1 07/04/18)
    """

    #initializing variables for data values
    type = data[name]['type']
    center_row = data[name]['center'][0]
    center_col = data[name]['center'][1]

    #setting up number of row loops in function of type
    row_range = (0,)
    if type in ('excavator-M', 'scout'):
        row_range = (-1, 0, 1)
    elif type in ('excavator-L', 'portal', 'warship'):
        row_range = (-2, -1, 0, 1, 2)

    for row_position in row_range: #row_position is used to iterate on the rows around center_row
        #setting up number of column loops in function of type and row_position
        column_range = row_range #this will give a square

        if type in ('excavator-M', 'excavator-L') and row_position != 0:
            column_range = (0,)
            #this creates a 1-tile wide cross shape

        if type == 'warship' and row_position not in (-1, 0, 1):
            column_range = (-1, 0, 1)

        for column_position in column_range: #column_position is used to iterate on tiles around center_col
            row_coord = center_row + row_position
            col_coord = center_col + column_position

            #if 'add' and there are no units there yet
            if action == 'add' and board[row_coord][col_coord] == ['']:
                board[row_coord][col_coord][0] = name #replace empty string
            elif action == 'add': #and board[row_coord][col_coord] != ['']
                board[row_coord][col_coord].insert(0, name) #add string at beginning of list

            elif action == 'remove' and board[row_coord][col_coord] == ['']:
                board[row_coord][col_coord][0] = ''
            elif action == 'remove': #and board[row_coord][col_coord] != ['']
                board[row_coord][col_coord].remove(name)

    return board
#end of gb_manage_unit

################################################################################
#End of miscellaneous functions                                                #
################################################################################

def convert_to_tuple(input_str): #child function of convert_file
    """Converts the given string into a tuple.

    Parameters
    ----------
    input_str : the string that will be converted into a tuple (str)

    Returns
    -------
    result : the result of the conversion into a tuple (tuple)
    """

    result = input_str.split(' ')
    for result_id in range(len(result)):
        result[result_id] = int(result[result_id])

    return tuple(result)
#end of convert_to_tuple

def convert_file(file_path): #child function of run_game
    """Converts the configuration file into a data structure.

    Parameters
    ----------
    file_path: the absolute or relative path to the file to convert (str)

    Returns
    -------
    converted_file: data structure containing the configuration file's data (dict)

    Notes
    -----
    The configuration file will be converted into a dictionary, containing the following
    key-value pairs:
        'board_size': size of the board in the format (rows(int), columns(int)) (tuple)
        'portal1': coordinates of player 1's portal in the format (row(int), column(int)) (tuple)
        'portal2': coordinates of the player 2's portal in the format (row(int), column(int)) (tuple)
    For a number N of asteroids, there will be N times the following pair:
        'asteroidN': data of the asteroid number # in the format
            (row(int), column(int), ore(int), mining_rate(int)) (tuple)

    Version
    -------
    specification: Lucas Themelin (v.2 30/03/18)
    implementation: Chengjun Liang, Lucas Themelin (v.1 30/03/18)
    """

    #reading configuration file
    config_file = open(file_path,'r')
    config_data = config_file.readlines()
    config_file.close()

    #removing '\n' at end of lines
    for line_id in range(len(config_data)):
        config_data[line_id] = config_data[line_id].strip('\n')

    #initializing converted_file
    converted_file = {}

    #creating 'board_size':(row, column) pair
    converted_file['board_size'] = convert_to_tuple(config_data[1])
    #line 1 is always board size

    #creating 'portal1':(row, column) pair and  'portal2':(row, column) pair
    converted_file['portal1'] = convert_to_tuple(config_data[3])
    converted_file['portal2'] = convert_to_tuple(config_data[4])
    #line 3 is always portal1 coordinates, line 4 is always portal2 coordinates

    #creating 'asteroidN': (row, column, ore, mining_rate) pairs
    for line_id in range(6, len(config_data)):
        asteroid_name = 'asteroid' + str(line_id-6)
        converted_file[asteroid_name] = convert_to_tuple(config_data[line_id])

    #return converted file data
    return converted_file
#end of convert_file

def create_game_data(file_data): #child function of run_game
    """Creates the data structure of the game's data.

    Parameters
    ----------
    file_data: data structure of the configuration file's data (dict)

    Returns
    -------
    data: data structure of the game's data (dict)

    Notes
    -----
    The game's data structure is a dictionary containing one pair str:dict for every unit in the game.
    The string key is the unit's name, with an additional '0','1' or '2' added to indicate if the unit
    belongs to no one (0), to player 1 (1) or to player 2 (2),
    and the value dictionary contains that unit's properties/data.
    For instance: if both players buy an unit called 'alice', there will be a key 'alice1' for player 1
        and 'alice2' for player 2. This method is foolproof because even if player one buys an unit 'alice2',
        it will be registered as 'alice21'->player 1's unit.
    Exceptional case: player 1's portal is named 'portal1', not 'portal11'.
        Same for 'portal2', it is not named 'portal22'.
    Each value dictionary may contain the following pairs in function of the unit's type:
        'damage' : damage inflicted by the unit when attacking (int)(only available for 'scout' and 'warship' types)
        'center' : coordinates of the unit's center in the format [row(int) , column(int)] (list)(available on every type)
        'locked' : true if an excavator is locked, false if unlocked (bool)(only available for the three excavator types)
        'life' : the unit's current life points (int)(not available for 'asteroid' type)
        'mining_rate' : how many ore per turn can be extracted (int)(only available for 'asteroid' type)
        'ore' : how much ore the unit is carrying (float)(not avaiable for 'scout' and 'warship' types)
           (note: this pair is present on portals to represent how much ore each player owns)
        'owner' : the owner of the unit, either 1 or 2 (int)(not available for 'asteroid' type)
        'range' : attack range of the unit (int)(only available for 'scout' and 'warship' types)
        'type' : unit's type (str)
        'total_ore': amount of ore that a player transfered to his portal during the game, to use as a
            tiebreaker (float)(only available on 'portal' type)

    Version
    -------
    specification: Lucas Themelin (v.2 16/04/18)
    implementation: Lucas Themelin (v.1 16/04/18)
    """

    #data is the dict that will be returned at end of function
    data = {}

    #adding units to data in function of file_data
    for unit_name, unit_data in file_data.items():
        #we can use unit_name for type checking since names in file_data are always portalN, asteroidN or board_size
        if 'portal' in unit_name:
            #initializing portal values
            owner_id = int(unit_name[-1]) #unit_name's last character = player id
            data[unit_name] = {}

            #edit here to change initial portal properties
            data[unit_name]['center'] = list(unit_data) #tuple -> list
            data[unit_name]['life'] = 100
            data[unit_name]['type'] = 'portal'
            data[unit_name]['ore'] = 4.0
            data[unit_name]['owner'] = owner_id
            data[unit_name]['total_ore'] = 0.0

        elif 'asteroid' in unit_name: #elif used to exclude key 'board_size'
            #initializing asteroid values
            full_name = unit_name + '0' #name with added 0 for no owner
            data[full_name] = {}

            coordinates = [unit_data[0], unit_data[1]]
            data[full_name]['center'] = coordinates
            data[full_name]['ore'] = unit_data[2]
            data[full_name]['mining_rate'] = unit_data[3]
            data[full_name]['type'] = 'asteroid'

    return data
#end of create_game_data

def create_game_board(size_data, data): #child function of run_game and execute_turn
    """Creates the data structure of the game board.

    Parameters
    ----------
    size_data: tuple conatining the board's size (tuple)
    data: data structure of the game's data (dict)

    Returns
    -------
    board: data structure of the game board (dict)

    Notes
    -----
    size_data is in the format (number_of_rows(int), number_of_columns(int)).
    The board's data structure is a three-level list (lists in lists in a list).
    The id of the first level list refers to a board row,
    the id of the second level to a board column,
    and the third level list contains a list of every part of unit present on that cell,
        in order of most recently moved unit to least recently.

    It is important to note that every name will have an additional 0, 1 or 2 at the end
            of it's name string to be able to differenciate the owner.
            For instance, if a player decides to name one of his units 'asteroid0'-the player's unit-,
            in game_board, it will appear as the name string 'asteroid01' to differenciate it from
            'asteroid0'-the asteroid-. The latter will appear as 'asteroid00'

    Also note that any tile with coordinate row=0 or column=0 will remain an emtpy tile ('').
        This is because list ids start at 0 but game board coordinates start at 1.
        To avoid having to compute with a difference, we simply never use the row id 0
            or the column id 0.

    Example: print( game_board[row][col] ) will print a list of every part of
        units present on the cell at (row,col) on the board.

    Version
    -------
    specification: Lucas Themelin (v.2 16/04/18)
    implementation: Lucas Themelin (v.1 30/03/18)
    """

    #initializing variables
    nb_rows = size_data[0]
    nb_columns = size_data[1]
    board = []

    #generating empty rows, columns, and tiles
    for row_id in range(nb_rows+1):
        board += [[]]

        for column_id in range(nb_columns+1):
            board[row_id] += [['']]

    for unit_name in data:
        board = gb_manage_unit(unit_name, data, board)

    return board
#end of create_game_board

###############################################################################
#End of game initialization functions
###############################################################################

#child function of render_row
def tile_string(unit_data, board, unit_name, coordinates, colors_dict):
    """Creates a colored string of a given unit's part for one tile.
    Parameters
    ----------
    unit_data: data of a given unit (dict)
    board: data structure of the game board (list)
    unit_name: name of the unit whose parts are to be represented (str)
    coordinates: board coordinates of the parts to render (tuple)
    colors_dict: dictionary of ansi escape sequences for colors (dict)

    Returns
    -------
    result_string: colored string representing the unit type

    Version
    -------
    specification: Lucas Themelin (v.1 05/04/18)
    implementation: Lucas Themelin (v.1 05/04/18)
    """

    #general data of the given unit
    type = unit_data['type'] #str
    owner = unit_data['owner'] #int
    life = '%03.f' % unit_data['life'] #str, 3 digit number
    center = unit_data['center'] #list
    unit_letter = unit_name[0]

    #bools for unit types
    is_excavator = 'excavator' in type
    is_p_or_w = type in ['portal', 'warship']

    #set unit_letter to lowercase for player1 or uppercase for player2
    if owner == 1:
        unit_letter = unit_letter.lower()
    elif owner == 2:
        unit_letter = unit_letter.upper()

    #bools for tiles on center, and left and right from center
    left_from_center = (coordinates[1] == (center[1]-1)) and (coordinates[0] == center[0])
        #true if coordinates is one tile left from center
    right_from_center = (coordinates[1] == (center[1]+1)) and (coordinates[0] == center[0])
        #true if coordinates is one tile right from center
    on_center = coordinates == tuple(center)
        #true if coordinates is the unit center tile

    #unique variables initialization for excavator units;
    #also handles special case of excavator-S type
    if is_excavator:

        #set color and letter for lock tile
        lock_c = colors_dict[type + '_lock']
        #lock = 'v' if locked or  '^' if unlocked
        lock = unit_data['locked'] #bool
        if lock:
            lock = 'v' #bool becomes str
        else:
            lock = '^' #bool becomes str

        if type == 'excavator-S':
            result_string = lock_c + lock
            return result_string
            #we immediately exit function upon excavator-S case encounter
            #   to be able to declare other variables without error,
            #   since excavator-S has no other colors in colors_dict

        else:
            #initializing unique variables
            ore = '%01.f' % unit_data['ore']#str
            ore_c = colors_dict[type + '_ore']

    #end of excavator cases

    base_c = colors_dict[type + '_base']
    life_c = colors_dict[type + '_life']

    if left_from_center and is_excavator:
        result_string = life_c + life[2]
    elif left_from_center and is_p_or_w:
        result_string = life_c + life[0]

    elif on_center and is_excavator:
        result_string = lock_c + lock
    elif on_center and is_p_or_w:
        result_string = life_c + life[1]
    elif on_center and type == 'scout':
        result_string = life_c + life[2]

    elif right_from_center and is_excavator:
        result_string = ore_c + ore
    elif right_from_center and is_p_or_w:
        result_string = life_c + life[2]

    else:
        result_string = base_c + unit_letter

        #return result_string
    return result_string
#end of psw_string

def render_row(data, board, row): #child function of render_board
    """Renders a given row of the game board.

    Parameters
    ----------
    data: data structure of the game's data (dict)
    board: data structure of the game board (list)
    row: board id of the row to render (int)

    Version
    -------
    specification: Lucas Themelin (v.1 03/03/18)
    implementation: Lucas Themelin (v.1 14/03/18)
    """

    #initialize color dictionary for units
    colors_dict = {

        'asteroid_base' : '\x1b[1;32;40m', #used if ore_capacity > 0
        'asteroid_0' : '\x1b[1;31;40m',

        'portal_base' : '\x1b[1;37;45m',
        'portal_life' : '\x1b[1;36;45m',

        'scout_base' : '\x1b[1;37;46m',
        'scout_life' : '\x1b[1;31;46m',

        'warship_base' : '\x1b[1;37;44m',
        'warship_life' : '\x1b[1;31;44m',

        #no excavator-S_base because excavator-S is only one tile that shows lock status
        'excavator-S_lock' : '\x1b[1;37;41m',

        'excavator-M_base' : '\x1b[1;37;43m',
        'excavator-M_life' : '\x1b[1;31;43m',
        'excavator-M_lock' : '\x1b[1;35;43m',
        'excavator-M_ore' : '\x1b[1;34;43m',

        'excavator-L_base' : '\x1b[1;37;42m',
        'excavator-L_life' : '\x1b[1;31;42m',
        'excavator-L_lock' : '\x1b[1;35;42m',
        'excavator-L_ore' : '\x1b[1;34;42m',
    }

    #alternating colors of row id for better readability
    row_id_color = '\x1b[0m'
    if row % 2 == 0:
        row_id_color = '\x1b[1;37;40m'
    row_string = row_id_color + '%03.d'%row #show row number at beginning of line

    #loop initialization
    column_id = 1
    nb_columns = len(board[0]) #the row id doesn't matter we just need the number of columns
    for column_id in range(1, nb_columns):
        current_unit = board[row][column_id][0]
        #does not take the actual most recent unit: create_game_board scrambles unit order

        if current_unit == '': #no unit on that tile
            #empty tiles will be represented as a checker pattern to facilitate positon reading
            ids_sum = row + column_id #to find whether a tile is "black" or "white": use parity
            if (ids_sum % 2) == 0:
                row_string += '\x1b[0m'
            else:
                row_string += '\x1b[0;30;47m'

            row_string += ' '

        else:
            #there is a unit part on that tile
            unit_coord = (row, column_id)
            unit_type = data[current_unit]['type']

            #begin creation of result_string
            if unit_type == 'asteroid':
                #unit type is asteroid
                if data[current_unit]['ore'] == 0:
                    #asteroid is empty
                    result_string = colors_dict['asteroid_0'] + '#'
                else:
                    result_string = colors_dict['asteroid_base'] + '#'

            else:
                unit_data = data[current_unit]
                result_string = tile_string(unit_data, board, current_unit, unit_coord, colors_dict)

            row_string += result_string

    print(row_string + '\x1b[0m') #adding a final reset to prevent colors from overflowing
#end of render_row

def render_board(data, board): #child function of renderUI
    """Renders the game board.

    Parameters
    ----------
    data: data structure of the game's data (dict)
    board: data structure of the game board (list)

    Version
    -------
    specification: Lucas Themelin (v.1 03/03/18)
    implementation: Lucas Themelin (v.1 14/03/18)
    """

    #rendering the column id on top of the board:
        #the first lines are used to render the column ids
        #numbers are rendered vertically to support more columns in the terminal
        #(and also to avoid having to add a bunch of spaces in further functions)
    #creating a list of three digit ids
    col_id_list = []
    for column_id in range(1, len(board[0])):
        col_id_list.append('%03.d'%column_id)

    #rendering the column ids with alternating colors for easier reading
    colors = ['\x1b[0m' , '\x1b[1;37;40m'] #empty string at id 0 is used so choice can be made with 1 and -1
    for digit in range(0, 3, 1):
        row_string = '\x1b[0m' + '   ' #three empty spaces to match row id rendering in every line
        color_toggler = True #used to select color in colors

        for column_id in range(0, len(board[0])-1):
            color_toggler = not color_toggler
            row_string += colors[color_toggler] + col_id_list[column_id][digit]

        print(row_string)
    #end of column id rendering

    #rendering every row, with 3 digit row ids and unit parts
    for row in range(1, len(board)):
        render_row(data, board, row)#child
#end of render_board

#child function of run_game
def renderUI(data, board):
    """Renders the game UI in the terminal.

    Parameters
    ----------
    data: data structure of the game's data (dict)
    board: data structure of the game board (list)

    Version
    -------
    specification: Lucas Themelin (v.1 03/03/18)
    implementation: Lucas Themelin (v.1 08/04/18)
    """
    #render the game board
    render_board(data, board)

    #render the life, ore of each player, as well as every asteroids' status
    life_p1 = data['portal1']['life']
    life_p2 = data['portal2']['life']

    print('\x1b[0m' + 'Portal player 1 life: %d'%life_p1 + ' ; ' + 'Portal player 2 life: %d'%life_p2)

    ore_p1 = data['portal1']['ore']
    ore_p2 = data['portal2']['ore']

    print('Player 1 ore: %d'%ore_p1 + ' ; ' + 'Player 2 ore: %d'%ore_p2)

    #render asteroids' statuses
    for row_id in range(1, len(board)):
        for column_id in range(1, len(board[0])):
            unit_names = board[row_id][column_id]

            if unit_names != ['']: #ignore empty tiles
                for unit_name in unit_names:
                    if unit_name != '': #ignore empty strings; there shouldn't be any but this is a safety
                        unit_type = data[unit_name]['type']
                        if 'asteroid' == unit_type:

                                ast_name = unit_name[0:-1] #removes the 0 at the end that identifies the unit as an asteroid
                                ore = data[unit_name]['ore']
                                rate = data[unit_name]['mining_rate']
                                center = data[unit_name]['center']

                                print(ast_name + ': Ore: %.2f; Mining rate: %.2f; Center: (%d, %d)' %(ore, rate, center[0], center[1]))
#end of renderUI

###############################################################################
#End of UI rendering functions                                                #
###############################################################################

def buy_unit(one_order, owner, data): #child function of execute_turn
    """Buys one unit and names it according to the order, and checks if the owner can afford it.

    Parameters
    ----------
    one_order: string containing the order (string)
    owner: owner of the bought ship (int)
    data: data structure of the  game (dict)

    Notes
    -----
    If a chosen name is already in use, or the owner does not have enough ore,
        the unit will not be purchased.

    Returns
    -------
    data: updated data structure of the game (dict)

    Version
    -------
    specification: Nathan Zampunieris (v.2 16/04/18)
    implementation: Nathan Zampunieris (v.1 13/03/18)
    """
    #edit here to change unit prices
    prices_dict = {
        'scout':3, 'warship':9, 'excavator-S':1,
        'excavator-M':2, 'excavator-L':4
    }

    #cutting order
    one_order = one_order.split(':')

    #initializing variables
    name = one_order[0]
    portal_name = 'portal' + str(owner)
    owner_ore = data[portal_name]['ore']
    unit_type = one_order[1]
    unit_price = prices_dict[unit_type]
    structure = data

    #testing for valid purchase
    if (name not in data) and owner_ore >= unit_price:
        #purchasing, edit here to change initial unit properties
        characteristics = {'scout':{'type':'scout', 'life':3, 'damage':1, 'range':3, 'cost':3},
                           'warship':{'type':'warship', 'life':18, 'damage':3,'range':5,'cost':9},
                           'excavator-S':{'type':'excavator-S', 'life':2, 'cost':1, 'ore':0, 'locked':False},
                           'excavator-M':{'type':'excavator-M', 'life':3, 'cost':2, 'ore':0, 'locked':False},
                           'excavator-L':{'type':'excavator-L', 'life':6, 'cost':4, 'ore':0, 'locked':False},
                           }

        data[name] = characteristics[unit_type]
        data[name]['owner'] = owner
        portal = 'portal' + str(owner)

        data[name]['center'] = data[portal]['center']

        #subtract ore cost
        data[portal_name]['ore'] -= unit_price

    return data
#end of buy_unit

def exc_lock(one_order, data, board): #child function of execute_turn
    """Locks or unlocks an excavator depending on the order.

    Parameters
    ----------
    one_order: string containing the order (string)
    data: data structure of the game's data (dict)
    board: data structure of the game board

    Returns
    -------
    updated_data = updated data structure of the game

    Version
    -------
    specification: Nathan Zampunieris (v.2 16/04/18)
    implementation: Nathan Zampunieris (v.1 13/03/18)
    """
    orders = one_order.split(':')

    #new_state
    if orders[1] == 'lock':
        #check if there is an asteroid or portal to lock on
        center = data[orders[0]]['center']
        for unit in board[ center[0] ][ center[1] ]:
            if data[unit]['type'] in ('portal, asteroid'):
                data[orders[0]]['locked'] = True

    elif orders[1] == 'release':
        data[orders[0]]['locked'] = False

    return data
#end of exc_lock

def move_unit(one_order, data, board): #child function of execute_turn
    """Moves the unit to the ordered destination if the move is legal.

    Parameters
    ----------
    one_order: string containing the order (string)
    data: data structure of the game's data (dict)
    board: data structure of the game board (list)

    Returns
    -------
    updated_data: data structure updated with the moved unit

    Version
    -------
    specification: Nathan Zampunieris, Lucas Themelin (v.2 16/04/18)
    implementation: Nathan Zampunieris (v.2 29/03/18)
    """
    #cutting order
    order = one_order.split(':')

    #initializing variables
    coordinates = order[1][1:]

    coord = coordinates.split('-')
    coordx = [int(coord[0])]
    coordy = [int(coord[1])]

    x_difference = abs(int(coord[0]) - data[order[0]]['center'][0])
    y_difference = abs(int(coord[1]) - data[order[0]]['center'][1])
    valid_range = range(-1, 1+1, 1)

    #testing for valid move, including not moving
    if (x_difference in valid_range) and (y_difference in valid_range) and ( not is_OOB(one_order, data, board) ):
        data[ order[0] ]['center'] = (coordx + coordy)

    return data
#end of move_unit

def unit_attack(one_order, data, board): #child function of execute_turn
    """Gives the unit an order to attack the ordered coordinates.

    Parameters
    ----------
    one_order: string containing the order (string)
    data: data structure of the game (dict)
    board: data structure of the game board (list)

    Returns
    -------
    updated_data: data structure updated with the moved unit

    Version
    -------
    specification: Nathan Zampunieris (v.2 16/04/18)
    implementation: Nathan Zampunieris (v.1 13/03/18)
    """

    orders = one_order.split(':')
    coordinates = orders[1][1:]
    coordinates = coordinates.split('-')

    dist = (abs(int(coordinates[0]) - data[orders[0]]['center'][0]) + abs(int(coordinates[1]) - data[orders[0]]['center'][1]))
            #(sqrt((Xb-Xa)**2))-(sqrt((Yb-Ya)**2))

    if dist <= data[orders[0]]['range'] and ( not is_OOB(one_order, data, board) ):
        targets = board[int(coordinates[0])][int(coordinates[1])]
        if targets != ['']:
            for unit in targets:
                if data[unit]['type'] != 'asteroid':
                    data[unit]['life'] -= data[orders[0]]['damage']
    return data
#end of unit_attack

def portal_transfers(data, board, capacity_dict): #child function of execute_turn
    """Manages ore transfers from excavators to portals.

    Parameters
    ----------
    data: data structure of the game (dict)
    board: data structure of the game board (list)
    capacity_dict: dictionary containning the maximum ore capacity of each excavator type (dict)

    Returns
    -------
    updated_data: data structure updated after the ore transfers

    Version
    -------
    specification: Lucas Themelin (v.1 16/04/18)
    implementation: Lucas Themelin (v.1 16/04/18)
    """
    for unit_name in data:
        unit_type = data[unit_name]['type']

        #find excavators to dump ore to portal
        if 'excavator' in unit_type:
            #initializing variables
            center = data[unit_name]['center']
            on_center = board[ center[0] ][ center[1] ] #list of units which overlay the unit's center
            ally_portal = 'portal' + str( data[unit_name]['owner'] ) #prevents unit from looking for enemy portal
            locked = data[unit_name]['locked']

            #transfer validity check
            if locked and ( ally_portal in on_center ):
                unit_ore = data[unit_name]['ore']

                data[ally_portal]['total_ore'] += unit_ore #add ore to total
                data[ally_portal]['ore'] += unit_ore #add ore to player ore bank
                data[unit_name]['ore'] = 0 #reset excavator ore

    return data
#end of portal_transfers

def asteroid_transfers(data, board, capacity_dict): #child function of execute_turn
    """Manages ore transfers from asteroids to excavators.

    Parameters
    ----------
    data: data structure of the game (dict)
    board: data structure of the game board (list)
    capacity_dict: dictionary containning the maximum ore capacity of each excavator type (dict)

    Returns
    -------
    updated_data: data structure updated after the ore transfers

    Version
    -------
    specification: Lucas Themelin (v.1 16/04/18)
    implementation: Lucas Themelin (v.1 16/04/18)
    """
    mined_asteroids = {}

    for unit_name in data:
        unit_type = data[unit_name]['type']

        #find excavators
        if 'excavator' in unit_type:

            #initializing variables
            unit_ore = data[unit_name]['ore']
            center = data[unit_name]['center']
            on_center = board[ center[0] ][ center[1] ] #list of units which overlay the unit's center
            locked = data[unit_name]['locked']

            #verify if excavator meets mining conditons
            if (unit_ore < capacity_dict[unit_type]) and locked:

                #check for asteroid on excavator location
                for close_name in on_center:
                    if ('asteroid' in close_name):
                        #verify if asteroid exists
                        if (close_name not in mined_asteroids):
                            mined_asteroids[close_name] = [unit_name]
                        else:
                            mined_asteroids[close_name].append(unit_name)

    #starting repartitionning
    for asteroid in mined_asteroids:

        asteroid_ore = data[asteroid]['ore']
        mining_rate = data[asteroid]['mining_rate']
        rate_threshold = 0

        #transfer ore part by part until exhaustion
        while ( asteroid_ore > 0 ) and ( rate_threshold < mining_rate ):
            mining_excavators = deepcopy( mined_asteroids[asteroid] )
            nb_excavators = len( mining_excavators )
            equal_sharing = False #used to toggle equal sharing, which will give equal amounts to every one

            #set ore gain and check for equal sharing condition
            ore_gain = 1
            if nb_excavators > asteroid_ore:
                ore_gain = asteroid_ore / nb_excavators
                equal_sharing = True

            if equal_sharing:
                #check excavators to see if any can disrupt the equal_sharing:
                #   equal sharing requires all excavators to have enough space to hold ore_gain,
                #   because otherwise the sharing is not equal anymore

                for excavator in mining_excavators:
                    #initializing variables for better readability
                    exc_ore = data[excavator]['ore']
                    exc_type = data[excavator]['type']
                    exc_capacity = capacity_dict[exc_type]
                    free_space = exc_capacity - exc_ore

                    if free_space < ore_gain: #proof of disruption
                        equal_sharing = False

            if equal_sharing:
                for excavator in mining_excavators:
                    data[excavator]['ore'] += ore_gain

                asteroid_ore = 0 #trigger while loop exit

            #note that even if equal_sharing == False, ore_gain can be smaller than 1:
            #   because we do ore_gain = asteroid_ore / nb_excavators without
            #   knowing yet if all the excavators can carry that much
            else: #simply give every excavator 1 ore, or less if it lacks space
                for excavator in mining_excavators:
                    exc_ore = data[excavator]['ore']
                    exc_type = data[excavator]['type']
                    exc_capacity = capacity_dict[exc_type]
                    free_space = exc_capacity - exc_ore

                    if free_space < ore_gain:
                        #fill space, and remove excavator from mining_excavators
                        data[excavator]['ore'] += free_space
                        mined_asteroids[asteroid].remove(excavator)
                        #subtract mined ore
                        asteroid_ore -= free_space

                    else:
                        data[excavator]['ore'] += ore_gain
                        asteroid_ore -= ore_gain

            #increase rate_threshold by ore_gain:
            #   in cases where a lot of repartitionning happens, rate_threshold will
            #   increase accordingly by using ore_gain
            rate_threshold += ore_gain

        #set new asteroid_ore:
        data[asteroid]['ore'] = asteroid_ore

    return data
#end of asteroid_transfers

def is_OOB(one_order, data, board):
    """Check if an order destination goes Out Of Bounds.

    Parameters
    ----------
    one_order: string containing the order (string)
    data: data structure of the game (dict)
    board: data structure of the game board (list)

    Returns
    -------
    answer: True if unit goes OOB, False otherwise

    Notes
    -----
    Can be used exclusively with "move" and "attack" orders. Any other type of
        order will cause an error.
    is_OOB does not care whether the order is legal or not.

    Version
    -------
    specification: Lucas Themelin (v.1 17/04/18)
    implementation: Lucas Themelin (v.1 17/04/18)
    """
    #initializing variables
    unit_name = one_order.split(':')[0]
    unit_type = data[unit_name]['type']

    destination = one_order.split(':')[1] #str
    order_type = destination[0]
    destination = destination[1:] #removes @ or * symbol
    destination = destination.split('-') #list of str

    row_limit = len(board)-1
    column_limit = len(board[0])-1

    #determinating size or "radius" so to speak
    hitbox_limit = 0 #for excavator-S or order_type == '*'
    if order_type == '@':
        if unit_type in ('scout', 'excavator-M'):
            hitbox_limit = 1
        elif unit_type in ('warship', 'excavator-L'):
            hitbox_limit = 2

    over_top = int(destination[0]) - hitbox_limit < 1 #part goes below row id 1
    over_bottom = int(destination[0]) + hitbox_limit > row_limit #part goes above max row
    over_left = int(destination[1]) - hitbox_limit < 1 #part goes below col id 1
    over_right = int(destination[1]) + hitbox_limit > column_limit

    OOB_checklist = over_right or over_top or over_left or over_bottom

    return OOB_checklist
#end of is_OOB

def execute_turn(orders1, orders2, data, board): #child function of run_game
    """Executes a game turn according to the orders given by the players

    Parameters
    ----------
    orders1: orders given by the player 1 (str)
    orders2: orders given by the player 2 (str)
    data: data structure of the game's data (dict)
    board: data structure containing the raw data of which unit is where on the board

    Returns
    -------
    updated_data: data structure of the game's data updated with the turn's actions
    updated_board: data structure of the board updated at the end of the turn

    Version
    -------
    specification: Nathan Zampunieris (v.1 10/03/18)
    implementation: Nathan Zampunieris, Themelin Lucas (v.2 06/05/18)
    """

    orders_list = [orders1, orders2]

    buy_list = [[], []]
    lock_list = [[], []]
    move_list = [[], []]
    attack_list = [[], []]

    active_types = ('excavator-S', 'excavator-M', 'excavator-L', 'scout', 'warship')

    #sort orders into lists corresponding to game phases regardless of the order's legal status
    for player_id in (1, 2):
        orders = orders_list[player_id-1]

        if orders != '': #empty strings create out-of-index issues since they cannot be split
            pieces_of_orders = orders.split(' ')

            for order in pieces_of_orders:

                #adding additional '1' or '2' at the end of names, since they are not present in the orders
                unit_name = order.split(':')[0] + str(player_id)
                unit_order = order.split(':')[1]
                order = unit_name + ':' + unit_order

                #print(' - ', unit_name, ' does ', unit_order)

                #bool to check if unit already has a phase 3 order (move or attack)
                has_phase3 = unit_name in (attack_list[player_id-1] + move_list[player_id-1])

                #sequence of if statements to sort order by type;
                #check if unit already has a phase1 order (buy)
                if unit_order in active_types and ( unit_name not in buy_list[player_id-1] ):
                    buy_list[player_id-1].append(order)

                #check if unit already has a phase2 order (lock/release)
                elif unit_order in ('lock', 'release') and unit_name not in lock_list[player_id-1] :
                    lock_list[player_id-1].append(order)

                #check if unit already a phase3 order (move/attack)
                elif unit_order[0] == '@' and not has_phase3:
                    move_list[player_id-1].append(order)

                #check if unit already a phase3 order (move/attack)
                elif unit_order[0] == '*' and not has_phase3:
                    attack_list[player_id-1].append(order)
    #end of sort

    '''
    print()
    print(' - local bought: ', buy_list[1])
    print(' - remote bought: ', buy_list[0])
    print()
    print(' - local moved: ', move_list[1])
    print(' - remote moved: ', move_list[0])
    print()'''

    #check orders' legal status and generate order if legal
    #phase1: purchase
    for player_id in (1, 2):
        for order in buy_list[player_id-1]:

            owner = int( order.split(':')[0][-1] ) #split, take full name, take last character, convert to int
            buy_is_legal = order.split(':')[1] in active_types
            if owner == player_id :
                data = buy_unit(order, owner, data)
            #summary: checks if name already exists, if owner has enough ore,
            #   if owner has enough ore, if bought type is valid

    #phase2: lock/unlock
    for player_id in (1, 2):
        for order in lock_list[player_id-1]:

            unit_name = order.split(':')[0]
            owner = int( unit_name[-1] ) #take full name, take last character, convert to int
            can_change_lock =  'excavator' in data[unit_name]['type']
            if owner == player_id and can_change_lock:
                data = exc_lock(order, data, board)
            #summary: checks if unit type is excavator, if unit belongs to owner,
            #   if unit is on ast. or portal, if state changes

    #phase3: move, then combat
    for player_id in (1, 2):

        for order in move_list[player_id-1]:

            unit_name = order.split(':')[0]
            owner = int( unit_name[-1] ) #take full name, take last character, convert to int
            #verify lock state if unit has one
            locked = ('locked' in data[unit_name]) and (data[unit_name]['locked'])
            move_is_legal = (not locked) and (data[unit_name]['type'] != 'portal')
            if owner == player_id and move_is_legal:
                data = move_unit(order, data, board)
            #summary: checks if unit belongs to owner, if move is adjacent, if it is in bounds,
            #   if unit is unlocked, if unit is not portal
            #asteroid are impossible to move because their names end with an additional 0

        for order in attack_list[player_id-1]:

            unit_name = order.split(':')[0]
            owner = int( unit_name[-1] ) #take full name, take last character, convert to int
            attack_is_legal = data[unit_name]['type'] in ('scout', 'warship')
            if owner == player_id and attack_is_legal:
                data = unit_attack(order, data, board)
            #summary: checks if unit belongs to owner, if unit is scout/warship, if shot is in range,
            #   if target is not asteroid

    #phase4: transfers
    capacity_dict = { 'excavator-S':1, 'excavator-M':4, 'excavator-L':8 }
    data = portal_transfers(data, board, capacity_dict)
    data = asteroid_transfers(data, board, capacity_dict)

    #removing dead units from the game
    dead_list = []
    for unit_name in data:
        if data[unit_name]['type'] != 'asteroid' and \
           data[unit_name]['type'] != 'portal' and \
           data[unit_name]['life'] <= 0:
                dead_list.append(unit_name)

    for dead in dead_list:
        del data[dead]

    #re-creating game_board with new data, the -1 are used to remove empty row and column on id 0
    size_tuple = ( len(board)-1, len(board[0])-1 )
    board = create_game_board(size_tuple, data)

    return data, board
#end of execute_turn

###############################################################################
#End of turn management functions                                             #
###############################################################################

def AI_orders(data, board, AI_memory): #child function of run_game
    """Returns the AI's orders regarding the current turn in a formatted orders string.

    Parameters
    ----------
    data: data structure of the game data (dict)
    board: data structure of the game board (list)
    AI_memory: data structure of the data used by the AI (dict)

    Returns
    -------
    orders_string: string containing the AI's orders (str)
    AI_memory: updated AI_memory after changes in the function (dict)

    Notes
    -----
    AI_memory is a dictionary, which contains the following key-value pairs:
        'draw_timer': remaining turns without damage dealt before draw end (int)
        'current_strategy': name of the strategy currently used by the AI (str)
            Can take values 'slow', 'fast' and 'final'.
        'initial_ore': total ore existing at the initialization of the game (int)
        'buy_seq_id': id of the current unit in a buying sequence (int)
        'exc_seq_id': id of the current excavator size in the sizes sequence (int)
        'AI_units': dictionary of the AI's units system (dict)

    'AI_units' is a dictionnary which assigns an objective and a target to each of the AI's units.
    Keys for the values are the names of the AI's units, excluding 'portal2'. As in game_data, unit names have a number
    at the end of the string to differentiate them between their owners or asteroids.
    Values assigned to the keys are a string in the format 'objective-target', where
        'objective' is 'mine', 'attack', 'tilt', or 'defend';
        'target' is the name of an enemy unit or an asteroid (depending on objective).
    The value string can also be empty if the unit has been assigned an objective and target yet.

    AI_memory is initialized in run_game before the first turn.

    Version
    -------
    specification: Nathan Zampunieris, Themelin Lucas (v.2 03/05/18)
    implementation: Nathan Zampunieris, Themelin Lucas (v.1 06/05/18)
    """

    return AI_gr_31.AI_orders(data, board, AI_memory)

###############################################################################
#End of all sub-functions                                                     #
###############################################################################

def run_game(file_path, remote_id, remote_IP='127.0.0.1'):
    """Runs the game "Mining Wars" until the end is reached.

    Parameters
    ----------
    file_path: the absolute or relative path to the file (str)
    remote_id: player id of the remote player (must be 1 or 2)(int)
    remote_IP: IP of the remote player (str)

    Notes
    -----
    If trying to use a relative path, you will have to manually set the current working directory
        as needed, run_game does not automatically set the current working directory.
        This can be done using
            import os
            os.chdir(path)
    The game will not run if the given path does not exist.

    The game assumes that the configuration file is valid.

    Version
    -------
    specification: Lucas Themelin (v.1 16/04/18)
    implementation: Lucas Themelin (v.1 16/04/18)
    """

    if not ( os.path.exists(file_path) and os.path.isfile(file_path) ):
        print('Sorry, the path you entered is not valid.')

    else:
        #getting configuration file data
        config_data = convert_file(file_path)

        #creating game_data
        game_data = create_game_data(config_data)

        #reverse portal centers if enemy is id2, which is supposed to be reserved for local AI
        if remote_id == 2:
            temp_var = game_data['portal1']['center']
            game_data['portal1']['center'] = game_data['portal2']['center']
            game_data['portal2']['center'] = temp_var

        #creating game_board
        size_tuple = config_data['board_size']
        game_board = create_game_board(size_tuple, game_data)

        #creating a variable to keep track of turns passed without any damage dealt
        initial_draw_timer = 200
        draw_timer = initial_draw_timer

        #init game end check
        game_is_over = game_data['portal1']['life'] <= 0 or game_data['portal2']['life'] <= 0 or draw_timer <= 0

        #computing total ore existing on the board:
        initial_ore = 0
        for unit_name, unit_data in game_data.items():
            if 'ore' in unit_data: #optional safety check
                initial_ore += unit_data['ore']

        #initializing AI_memory: see AI_orders for structure details
        AI_memory = {
            'draw_timer': initial_draw_timer,
            'current_strategy': 'fast', #AI starts with fast strategy
            'buy_seq_id': 0,
            'exc_seq_id': 0,
            'initial_ore': initial_ore,
            'early_game': True,
            'AI_units': {}
        }

        #preparing requirements for connection
        local_connection = rp.get_IP()
        remote_connection = rp.connect_to_player(remote_id, remote_IP, True)

        #game loop
        while (not game_is_over) and (draw_timer > 0):

            '''scroller = input()
            if scroller == 'exit':
                break'''

            #show user interface
            renderUI(game_data, game_board)

            #get orders from AI, send them to remote connection
            ai_orders, AI_memory = AI_orders(game_data, game_board, AI_memory)
            rp.notify_remote_orders(remote_connection, ai_orders)

            #get orders from remote connection
            other_orders = rp.get_remote_orders(remote_connection)

            #debug message
            print('\nlocal orders: ', ai_orders)
            print('remote orders: ', other_orders, '\n')

            #making a dictionary of unit's life points before update to check for damage
            life_dict = {}
            for unit_name, unit_data in game_data.items():
                if ('life' in unit_data):
                    life_dict[unit_name] = unit_data['life']

            #making changes to game according to orders
            game_data, game_board = execute_turn(other_orders, ai_orders, game_data, game_board)

            #verifying after update if any unit has taken damage
            found = False # = has any unit taken damage?
            for unit_name, unit_data in game_data.items():
                if (not found) and ('life' in unit_data) and (unit_name in life_dict):
                    #note: this method cannot check if units bought this turn have taken damage
                    if unit_data['life'] < life_dict[unit_name]:
                        #unit took damage
                        draw_timer = initial_draw_timer
                        found = True

            if (not found):
                #no unit took damage
                draw_timer -= 1

            #update draw_timer in AI_memory
            AI_memory['draw_timer'] = draw_timer

            game_is_over = game_data['portal1']['life'] < 0 or game_data['portal2']['life'] < 0

            #sleep or ask for input to avoid lightspeed gameplay
            #time.sleep(1.4)

            #print(' - draw_timer = ', draw_timer)

        #end of game loop

        #finding winner
        if draw_timer <= 0:
            print('No damage dealt for %d consecutive turns: Game ends with a draw.'%initial_draw_timer)

        else:
            life_p1 = game_data['portal1']['life']
            life_p2 = game_data['portal2']['life']
            if life_p1 != life_p2:
                winner_id = int(life_p1 < life_p2) +1 #return 0+1 if player2 wins, 1+1 if player 2 wins
                print('Different life points;')
            else:
                ore_p1 = game_data['portal1']['total_ore']
                ore_p2 = game_data['portal2']['total_ore']
                if ore_p1 != ore_p2:
                    winner_id = int(ore_p1 < ore_p2) +1 #return 0+1 if player2 wins, 1+1 if player 2 wins
                    print('Different total ore;')

                else:
                    winner_id = 0

            if winner_id == 1:
                print('Other won as player number %d' %winner_id)
            elif winner_id == 2:
                print('AI won as player number %d' %winner_id)
            else: #winner_id == 0
                print('Tie! Nobody wins.')

        #end remote connection
        rp.disconnect_from_player(remote_connection)

#end of run_game()

#END OF MODULE

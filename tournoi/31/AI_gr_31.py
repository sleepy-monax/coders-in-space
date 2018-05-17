#Vocabulary notes:
#1.unit =/= ship
#unit -> any type of units
#ship -> 'scout' and 'warship' types
#2.To 'tilt' is the act of dealing damage to a unit to reset the time left unit draw,
#for the cases where no damage is dealt for a set number of turns.

#import modules
from copy import deepcopy
from random import randint

def units_check(data, AI_memory): #child function of AI_orders
    """Checks whether the unit names in AI_memory's 'AI_units' match the unit names in
    data, and corrects 'AI_units' in case of mismatch.

    Parameters
    ----------
    data: data structure of the game data (dict)
    AI_memory: data structure of the data used by the AI (dict)

    Returns
    -------
    AI_memory: AI_memory with updated 'AI_units' pair (dict)

    Notes
    -----
    units_check corrects two sorts of 'mismatches' based on data:
    1. Removes dead units from AI_memory.
    2. Adds units bought previous turn to AI_memory.

    Version
    -------
    specification: Themelin Lucas (v.1 03/05/18)
    implementation: Themelin Lucas (v.1 03/05/18)
    """

    AI_units_copy = deepcopy(AI_memory['AI_units'])

    #finding and removing dead units (units which exist in AI_memory but not in data)
    for unit_name, unit_value in AI_units_copy.items():
        if unit_name not in data:
            #remove unit
            del AI_memory['AI_units'][unit_name]

    #finding and adding previously bought units (units which exist in data but not in AI_memory):
    for unit_name in data:
        #checking for allied, non-portal units not in AI_memory
        if (unit_name[-1] == '2') and (unit_name != 'portal2') and (unit_name not in AI_memory['AI_units']):
            #add unit in AI_memory without an objective&target
            AI_memory['AI_units'][unit_name] = ''

    return AI_memory
#end of units_check

def total_damage(units_list, data): #child function of decision_organism
    """Returns the total damage potential of the given list of unit names.

    Parameters
    ----------
    units_list: list of units whose total attack damage is to be calculated (list of str)
    data: data structure of the game data (dict)

    Returns
    -------
    damage: total damage potential of the units (int)

    Notes
    -----
    Passing units whose types are not 'scout' or 'watship' as parameter will cause a Python KeyError
    because function uses data[]['damage'] and keys without checking unit type.
    Neither does the function verify that units belong to the AI.

    Version
    -------
    specification: Themelin Lucas (v.1 03/05/18)
    implementation: Themelin Lucas (v.1 03/05/18)
    """
    damage = 0
    for unit_name in units_list:
        damage += data[unit_name]['damage']

    return damage
#end of total_damage

def decision_organism(data, AI_memory): #child function of AI_orders
    """Decides whether the AI should take 'slow', 'fast' or 'final' as it's
    current "strategy".

    Parameters
    ----------
    data: data structure of the game data (dict)
    AI_memory: data structure of the data used by the AI (dict)

    Returns
    -------
    AI_memory: AI_memory with updated 'current_strategy' pair (dict)

    Version
    -------
    specification: Themelin Lucas (v.1 03/05/18)
    implementation: Themelin Lucas (v.1 03/05/18)
    """

    #initializing variables
    current_strategy = AI_memory['current_strategy'] #str
    initial_ore = AI_memory['initial_ore'] #int
    AI_units = AI_memory['AI_units'] #list of str

    attack_portal1_units = [name for name in AI_units if ( AI_units[name] == 'attack&portal1' )]

    threshold = 3/4 * ( (initial_ore-8)/2 ) #= 3/4 of half of the mineable ore on the map

    #switch to 'final' if AI has mined enough ore from the map
    if data['portal2']['total_ore'] >= threshold:
        #verified if enough ore has been mined
            AI_memory['current_strategy'] = 'final'

    return AI_memory
#end of decision_organism

def random_unit_name(data): #child function of buying_orders, sequence_buying
    """Returns a random, unused name for a unit that will belong to the AI.

    Parameters
    ----------
    data: data structure of the game's data (dict)

    Returns
    -------
    name: generated name (str)

    Notes
    -----
    No value is returned if every name in names_list has been used up.
    The returned name does not contain the '2' at the end of the string to indicate owner.
    The function can generate 15625 different names at most.

    Version
    -------
    specification: Nathan Zampunieris, Themelin Lucas (v.1 02/05/18)
    implementation: Nathan Zampunieris, Themelin Lucas (v.1 02/05/18)
    """

    counter = 0 #counter is used to prevent endless loops, just as a safety

    while counter < 200:
        name = chr(randint(97, 122)) + chr(randint(97, 122)) + chr(randint(97, 122)) #names go from aaa to zzz
        if name not in data:
            return name

        counter += 1
#end of random_unit_name

def initial_move(unit, data): #child function of sequence_buying, buying_orders
    """Generates an order to move a unit one tile towards the enemy portal.
    Intented to be used to move newly bought units.

    Parameters
    ----------
    unit: name of the unit to move
    data: data structure of the game data (dict)

    Returns
    -------
    move_order: string of the formatted order (str)

    Notes
    -----
    move_order includes a whitespace at the end.
    """

    unit += '2' #add '2' for get_move_order to work

    #generate a reduced version of data with only the unit's and portal1's centers
    portal1_center = data['portal1']['center']
    portal2_center = data['portal2']['center']
    reduced_data = {
        'portal1': { 'center': portal1_center },
        unit: { 'center': portal2_center }
    }

    #generate and return a move order using reduced_data
    return get_move_order(unit, reduced_data, 'portal1')
#end of initial move

def sequence_buying(data, AI_memory): #child function of buying_orders
    """Generates a string of formatted orders to buy units, but with a sequence_buying
    logic exclusive to 'fast' strategy.

    Parameters
    ----------
    data: data structure of the game data (dict)
    AI_memory: data structure of the data used by the AI (dict)

    Returns
    -------
    buy_string: string containing the formatted orders (str)
    AI_memory: AI_memory with updated 'buy_seq_id' and 'exc_seq_id' (dict)

    Notes
    -----
    buy_string includes a whitespace at the end.
    Immediately adds a movement order after purchase. The move order orients units
        towards the enemy portal.
        It must be done this way because get_move_order is unable to move
        newly bought units because they don't exist in data yet.

    Version
    -------
    specification: Themelin Lucas (v.1 05/05/18)
    implementation: Themelin Lucas (v.1 05/05/18)
    """
    #initializing variables
    price_list = {
        'scout': 3,
        'warship': 9,
        'excavator-S': 1,
        'excavator-M': 2,
        'excavator-L': 4
    }

    initial_ore = AI_memory['initial_ore']
    AI_ore = data['portal2']['ore']
    buy_string = ""

    #fast strategy buying sequence
    buy_seq = ['excavator-', 'scout', 'excavator-', 'excavator-', 'excavator-', 'warship',
    'excavator-', 'excavator-', 'excavator-', 'warship', 'excavator-']

    #excavator size sequence
    exc_seq = ['L', 'M', 'L']

    #getting last used sequence ids
    buy_seq_id = AI_memory['buy_seq_id']
    exc_seq_id = AI_memory['exc_seq_id']

    #calculating total excavator ore capacity
    total_cap = 0
    excavators_gen = (name for name,value in AI_memory['AI_units'].items() if 'mine' in value)
    for unit_name in excavators_gen:
        unit_type = data[unit_name]['type']

        if unit_type == 'excavator-M':
            total_cap += 4
        elif unit_type == 'excavator-L':
            total_cap += 8

    #we start by assuming that buying is possible because all the verifications are done in the while loop
    can_buy = True
    need_excavator = True
    while can_buy:
        #get unit to buy
        current_type = buy_seq[ buy_seq_id ]
        if current_type == 'excavator-':
            current_type += exc_seq[ exc_seq_id ] #adding M or L to 'excavator'

        #checking if purchase is possible
        price = price_list[current_type]
        if price > AI_ore:
            can_buy = False

        #verifying if AI still needs to buy excavators
        need_excavator = total_cap < initial_ore / 4

        if can_buy: #proceeding to build order
            if 'excavator-' in current_type and need_excavator:
                #generate one buy order
                AI_ore -= price
                unit_name = random_unit_name(data)
                buy_string += unit_name + ':' + current_type + ' '
                buy_string += initial_move(unit_name, data)

                #update total_cap
                if current_type == 'excavator-M':
                    total_cap += 4
                elif current_type == 'excavator-L':
                    total_cap += 8

                #update exc_seq_id
                if exc_seq_id < ( len(exc_seq)-1 ):
                    exc_seq_id += 1
                else:
                    exc_seq_id = 0

            elif 'excavator' not in current_type:
                #generate one buy order
                AI_ore -= price
                unit_name = random_unit_name(data)
                buy_string += unit_name + ':' + current_type + ' '
                buy_string += initial_move(unit_name, data)

            #advancing buy_seq_id
            if buy_seq_id < ( len(buy_seq)-1 ):
                buy_seq_id += 1
            else:
                buy_seq_id = 0

    #updating AI_memory's sequences ids
    AI_memory['buy_seq_id'] = buy_seq_id
    AI_memory['exc_seq_id'] = exc_seq_id

    return buy_string, AI_memory
#end of sequence_buying

def buying_orders(data, AI_memory): #child function of AI_orders
    """Returns a string containing multilple formatted orders to buy units.

    Parameters
    ----------
    data: data structure of the game data (dict)
    AI_memory: data structure of the data used by the AI (dict)

    Returns
    -------
    buy_string: string containing the formatted orders (str)
    AI_memory: AI_memory with updated 'buy_seq_id' and 'exc_seq_id' (dict)

    Notes
    -----
    buy_string includes a whitespace at the end.

    Version
    -------
    specification: Themelin Lucas (v.1 05/05/18)
    implementation: Themelin Lucas (v.1 05/05/18)
    """
    #initializing variables
    AI_ore = data['portal2']['ore']
    buy_string = ""
    current_strategy = AI_memory['current_strategy']

    if current_strategy != 'final' and (AI_ore >= 2): #buy units based on a sequence:
        buy_string, AI_memory = sequence_buying(data, AI_memory)

    elif AI_ore >= 3 : #and current_strategy == 'final'
    #maximise warships, rest is used on scouts
        while AI_ore >= 3:
            current_order = ''

            unit_name = random_unit_name(data)
            current_order += unit_name + ':'

            if AI_ore >= 9:
                current_order += 'warship'
                AI_ore -= 9
            else:
                current_order += 'scout'
                AI_ore -= 3

            buy_string += current_order + ' '
    #end of elif

    return buy_string, AI_memory
#end of buying_orders

def unit_can_tilt(unit, data, AI_memory): #child function of get_tilt_order, manage_tilt
    """Tells whether the given unit is able to deal damage to portal1 before
    the game ends with a draw because 20 turns passed without damage.

    Parameters
    ----------
    unit: name of the unit whose tilt possibility is to be checked (str)
    data: data structure of the game data (dict)
    AI_memory: data structure of the data used by the AI (dict)

    Returns
    -------
    answer : True if AI can deal damage to enemy in time, False otherwise (bool)

    Version
    -------
    specification: Themelin Lucas (v.1 05/05/18)
    implementation: Themelin Lucas (v.1 05/05/18)
    """

    time_left = AI_memory['draw_timer']
    can_tilt = False

    #initializing variables
    unit_row, unit_col = data[unit]['center']
    unit_range = data[unit]['range']
    target_row, target_col = data['portal1']['center']

    #calculating number of turns required to move to target
    row_distance = abs(unit_row - target_row)
    col_distance = abs(unit_col - target_col)

    needed_time = max(row_distance, col_distance)
    #needed time to move from A to B
    #= longest side of rectangle triangle formed with AB as hypothenuse

    #approximate reduction based on scout's range and portal's size
    needed_time = needed_time - 1 - 2

    #checking if tilt is possible
    if needed_time <= time_left:
        can_tilt = True

    return can_tilt
#end of unit_can_tilt

def manage_tilt(data, AI_memory): #child function of AI_orders
    """Gives 'tilt' objective to one of the AI's scouts.

    Parameters
    ----------
    data: data structure of the game data (dict)
    AI_memory: data structure of the data used by the AI (dict)

    Returns
    -------
    AI_memory: AI_memory with updated 'AI_units' (dict)

    Version
    -------
    specification: Themelin Lucas (v.1 05/05/18)
    implementation: Themelin Lucas (v.1 05/05/18)
    """

    #find 'tilt' unit if it exists
    AI_units_copy = deepcopy( AI_memory['AI_units'] )
    unit = [name for name, value in AI_units_copy.items() if (value == 'tilt&portal1')][:] #list

    scouts_list = [name for name in AI_units_copy if (data[name]['type'] == 'scout')] #list

    if unit == [] and scouts_list != []: #if no tilt unit has been found, and scouts are available
        chosen_scout = scouts_list[0]

        if len(scouts_list) > 1: #we have multiple scouts
            found_conditions = False
            list_id = 0

            #checking the amount of life the scout needs based on the distance between portals
            p1_row, p1_col = data['portal1']['center']
            p2_row, p2_col = data['portal2']['center']
            max_dist = max( abs(p1_row - p2_row) , abs(p1_col - p2_col) )
            required_life = min( max_dist // 20 , 3) #//20 because units can move for 2 turns, then hit itself

            #trying to find a scout which both can tilt and has full life
            while not(found_conditions) and (list_id < len(scouts_list)):
                loop_unit = scouts_list[ list_id ]

                can_tilt = unit_can_tilt(loop_unit, data, AI_memory)
                life = data[loop_unit]['life']
                enough_life = life >= required_life

                #continue if didn't find a unit which can tilt and has enough life
                found_conditions = can_tilt and enough_life

                list_id += 1
            #end of while loop

            if found_conditions: #suitable scout was found:
                chosen_scout = loop_unit

        AI_memory['AI_units'][chosen_scout] = 'tilt&portal1'

    return AI_memory
#end of manage_tilt

def find_best_asteroid(data, AI_memory): #child function of manage_excavators
    """Find the non-targetted asteroid that presents the best compromise between ore, mining_rate
    and distance from AI's portal.

    Parameters
    ----------
    data: data structure of the game data (dict)
    AI_memory: data structure of the data used by the AI (dict)

    Returns
    -------
    best_ast: name of the best asteroid found (str)

    Version
    -------
    specification: Themelin Lucas (v.1 05/05/18)
    implementation: Themelin Lucas (v.1 05/05/18)
    """
    #find asteroids
    asteroids_list = [name for name in data if (name[-1] == '0')]

    #initialize best_asteroid to any asteroid
    best_ast = asteroids_list[0]
    best_score = 0 #note: higher score == better asteroid

    #find the best asteroid
    for asteroid in asteroids_list:
        #getting movement distance
        row_distance = abs( data['portal2']['center'][0] - data[asteroid]['center'][0] )
        col_distance = abs( data['portal2']['center'][1] - data[asteroid]['center'][1] )
        distance = max(row_distance, col_distance)

        #getting 'free' ore: discounting ore that will be mined by other excavators
        ore = data[asteroid]['ore']
        ##list of excavators which are targeting asteroid
        excavators_list = [name for name,value in AI_memory['AI_units'].items() if (value == 'mine&'+asteroid)]
        for excavator in excavators_list:
            excavator_capacity = 4
            if data[excavator]['type'] == 'excavator-L':
                excavator_capacity += 4
            excavator_capacity -= data[excavator]['ore']

            ore -= excavator_capacity
        #end of for loop

        #getting rate
        rate = data[asteroid]['mining_rate']

        #computing score
        score = ore * rate * 1/distance

        #test score against previous best
        if score > best_score:
            best_ast = asteroid
            best_score = score
    #end of for loop

    return best_ast
#end of find_best_asteroid

def manage_excavators(data, AI_memory): #child function of AI_orders
    """Assign targets to each of each of the AI's excavators.

    Parameters
    ----------
    data: data structure of the game data (dict)
    AI_memory: data structure of the data used by the AI (dict)

    Returns
    -------
    AI_memory: AI_memory with updated 'AI_units' (dict)

    Version
    -------
    specification: Themelin Lucas (v.1 05/05/18)
    implementation: Themelin Lucas (v.1 05/05/18)
    """

    #find excavators that have an objective
    used_list = [(name,value) for name,value in AI_memory['AI_units'].items() if ('mine' in value)]
    #verify if their targets are still relevant
    for name, value in used_list:
        target = value.split('&')[1]

        if data[target]['ore'] < 1:
            AI_memory['AI_units'][name] = '' # == <<no objective>>
    #end of for loop

    #find excavators that do NOT have an objective
    unused_list = [name for name,value in AI_memory['AI_units'].items() if ('excavator' in data[name]['type'] and value == '')]

    for excavator in unused_list:
        AI_memory['AI_units'][excavator] = 'mine&' + find_best_asteroid(data, AI_memory)

    return AI_memory
#end of manage_excavators

def generate_report(data): #child function of manage_attack_fast
    """Classes enemy units from highest to lowest priority.

    Parameters
    ----------
    data: data structure of the game data (dict)

    Returns
    -------
    priority_report: list of enemy unit names, ordered from highest priority to lowest (list)

    Version
    -------
    specification: Themelin Lucas (v.1 05/05/18)
    implementation: Themelin Lucas (v.1 05/05/18)

    Version
    -------
    specification: Themelin Lucas (v.1 05/05/18)
    implementation: Nathan Zampunieris, Themelin Lucas (v.1 05/05/18)
    """

    priority_1 = []
    priority_2 = []
    priority_3 = []
    priority_4 = []

    #we attack enemies only if they are close enough to their portal
    close_units = []
    detection_range = 11
    target_row, target_col = data['portal1']['center']
    row_range = range(target_row - detection_range, target_row + detection_range + 1)
    col_range = range(target_col - detection_range, target_col + detection_range + 1)
    detection_tiles = [[row, col] for row in row_range for col in col_range]
    #lax detection: we only see if the center is in range
    for unit_name, unit_data in [pair for pair in data.items() if (pair[0][-1] == '1')]:
        #if enemy is close enough and hasn't been added yet:
        if (unit_data['center'] in detection_tiles) and (unit_name not in close_units):
            close_units.append(unit_name)

    #iterate through enemy unit names and their data
    for name, value in [pair for pair in data.items() if (pair[0][-1] == '1' and pair[0] in close_units)]:
        if 'excavator' in value['type']:
            if value['ore'] >=4:
                priority_1.append(name)
            else:
                priority_4.append(name)

        elif value['type'] == 'scout':
            priority_3.append(name)

        elif value['type'] == 'warship':
            priority_2.append(name)
    #end of for loop

    #creating report with portal1 as lowest priority enemy
    priority_report = priority_1 + priority_2 + priority_3 + priority_4 + ['portal1']

    return priority_report
#end of generate_report

def manage_attack_fast(data, AI_memory): #child function of manage_ships_fast
    """Gives a target for every unit with objective 'attack'.

    Parameters
    ----------
    data: data structure of the game data (dict)
    AI_memory: data structure of the data used by the AI (dict)

    Returns
    -------
    AI_memory: AI_memory with updated 'AI_units' pair (dict)

    Version
    -------
    specification: Themelin Lucas (v.1 04/05/18)
    implementation: Themelin Lucas (v.1 04/05/18)

    Version
    -------
    specification: Themelin Lucas (v.1 05/05/18)
    implementation: Nathan Zampunieris, Themelin Lucas (v.1 05/05/18)
    """

    priority_report = generate_report(data)

    AI_units = AI_memory['AI_units']
    attack_list = [name for name,value in AI_units.items() if (value.split('&')[0] == 'attack')] #has 'attack' objective
    warships_list = [name for name in attack_list if (data[name]['type'] == 'warship')]
    scouts_list = [name for name in attack_list if (data[name]['type'] == 'scout')]

    ships_available = attack_list != []
    report_id = 0

    while ships_available and (report_id < len(priority_report)-1):
        target = priority_report[ report_id ]
        target_life = data[target]['life']
        needed_warships = target_life // 3
        needed_scouts = target_life % 3
        available_warships = len(warships_list)
        available_scouts = len(scouts_list)

        #assign target to fitting units
        while available_warships > 0 and needed_warships > 0:
            warship = warships_list.pop() #'extract' a warship from the list
            available_warships -= 1
            needed_warships -= 1
            AI_memory['AI_units'][warship] = 'attack&' + target

        needed_scouts += needed_warships*3 #if we didn't have enough warships, use scouts
        while available_scouts > 0 and needed_scouts > 0:
            scout = scouts_list.pop() #'extract' a scout from the list
            available_scouts -= 1
            needed_scouts -= 1
            AI_memory['AI_units'][scout] = 'attack&' + target

        ships_available = (warships_list + scouts_list) != []
        report_id += 1
        #end of while loop

    if ships_available: #would mean that enemy portal will die next turn but we still want to assign objectives
        for unit_name in warships_list+scouts_list:
            AI_memory['AI_units'][unit_name] = 'attack&portal1'

    return AI_memory
#end of manage_attack_fast

def manage_ships_fast(data, AI_memory): #child function of AI_orders
    """Manages units for 'attack' and 'defend' objectives.

    Parameters
    ----------
    data: data structure of the game data (dict)
    AI_memory: data structure of the data used by the AI (dict)

    Returns
    -------
    AI_memory: AI_memory with updated 'AI_units' pair (dict)

    Note
    ----
    Instead of giving units without an 'objective&target' string an objective without a target,
    we give them default targets:
        Default 'attack&' target is 'portal1';
        Default 'defend&' target is 'portal2'.

    Version
    -------
    specification: Themelin Lucas (v.1 05/05/18)
    implementation: Themelin Lucas (v.1 05/05/18)
    """

    #begin repartitionning scouts and warships between 'attack' and 'defend'
    sequence_length = 5
    attack_quantity = 4
    #=> int(attack_quantity) out of int(sequence_length) will have 'attack' objective

    #find current amount of attack and defend units to initialize counter
    units_list = [name for name,value in AI_memory['AI_units'].items() if (value.split('&')[0] in ('attack','defend'))]
    counter = len(units_list)

    #assign default objectives to units without one
    for name in [name for name in AI_memory['AI_units'] if (AI_memory['AI_units'][name] == '' and data[name]['type'] in ('scout','warship') )]:
        if (counter%sequence_length) < attack_quantity:
            AI_memory['AI_units'][name] = 'attack&portal2'
        else:
            AI_memory['AI_units'][name] = 'defend&portal1'

        counter += 1
    #end of for loop

    #manage units with 'attack' objective
    AI_memory = manage_attack_fast(data, AI_memory)

    return AI_memory
#end of manage_ships_fast

def manage_ships_final(data, AI_memory): #child function of AI_orders
    """Manages scouts and warships for the 'final' strategy.

    Parameters
    ----------
    data: data structure of the game data (dict)
    AI_memory: data structure of the data used by the AI (dict)

    Returns
    -------
    AI_memory: AI_memory with updated 'AI_units' pairs (dict)

    Version
    -------
    specification: Themelin Lucas (v.1 05/05/18)
    implementation: Themelin Lucas (v.1 05/05/18)
    """
    #find all units with 'attack' and 'defend' objectives
    AI_ships = [name for name,value in AI_memory['AI_units'].items() if (value.split('&')[0] in ('attack', 'defend', ''))]

    #set their 'objective&target' to 'attack&portal1'
    for name in AI_ships:
        AI_memory['AI_units'][name] = 'attack&portal1'

    return AI_memory
#end of manage_ships_final

def get_move_order(unit, data, target): #child function of other get_X_order() functions
    """Generates a formatted order that moves a given unit one tile closer to a given
    target's center.

    Parameters
    ----------
    unit: name of the unit whose order will be generated (str)
    data: data structure of the game's data (dict)
    target: name of the targetted unit (str)

    Returns
    -------
    order: formatted order of the unit (str)

    Notes
    -----
    get_move_order only generates an order if the unit moves.
    In that case, the order includes a whitespace at the end.

    Version
    -------
    specification: Themelin Lucas (v.1 05/05/18)
    implementation: Themelin Lucas (v.1 05/05/18)
    """

    #initialize variables
    unit_row, unit_col = data[unit]['center']

    target_row, target_col = data[target]['center']

    row_difference = unit_row - target_row
    col_difference = unit_col - target_col

    order = ''

    #determine movement vector
    vector = [0,0]

    if row_difference != 0:
        vector[0] += abs(row_difference) * ( -1/row_difference ) #reduce value to 1 and reverse sign
    if col_difference != 0:
        vector[1] += abs(col_difference) * ( -1/col_difference ) #reduce value to 1 and reverse sign

    end_row = str( unit_row + round(vector[0]) )
    end_col = str( unit_col + round(vector[1]) )

    if vector != [0,0]:
        order = unit[:-1] + ':@' + end_row + '-' + end_col + ' ' #child function of various functions

    return order
#end of get_move_order

def ideal_aim(unit, data, board, target): #child function of get_attack_order, get_defend_order
    """Find the ideal tile to aim at within a given unit's range, or tell if the
    given target is not in range.

    Parameters
    ----------
    unit: name of the unit which will shoot (str)
    data: data structure of the game's data (dict)
    board: data structure of the game board (list)
    target: name of the unit targetted by the group (str)

    Returns
    -------
    aimed_tile: if a tile was found, tile at which the given unit should shoot (list),
        None (NoneType) otherwise.

    Notes
    -----
    aimed_tile is in the format [row(int), column(int)].
    ideal_aim assumes that target exists.
    ideal_aim only works for player2.

    The "ideal" tile to shoot at meets 2 criterias:
        1. Multiple enemy tiles stand on it
        2. The target is one of those enemies.
    The second best tile to shoot at is the tile that is closest to the target's center.
    If the enemy is not in range, no shot should be fired (returns None).

    Version
    -------
    specification: Themelin Lucas (v.1 05/05/18)
    implementation: Themelin Lucas (v.1 05/05/18)
    """

    #initializing variables
    unit_row, unit_col = data[unit]['center']
    unit_range = data[unit]['range']

    target_row, target_col = data[target]['center']

    #find the coordinates of every target tiles in range
    tiles_list = []
    row_limit = len(board)
    col_limit = len(board[0])
    for row_id in [id for id in range(target_row-2, target_row+2+1) if (id < row_limit)]:
        for col_id in [id for id in range(target_col-2, target_col+2+1) if (id < col_limit)]:

            #calculate distances for range check
            row_distance = abs( unit_row - row_id )
            col_distance = abs( unit_col - col_id )
            range_distance = row_distance + col_distance

            #append tiles that belong to target and that are in range:
            if (range_distance <= unit_range) and (target in board[row_id][col_id]):
                tiles_list.append([row_id, col_id])

    #find tile with most different enemy tiles
    aimed_tile = None
    max_enemies = 0
    for tile in tiles_list:
        nb_enemies = 0
        units_list = board[ tile[0] ][ tile[1] ]

        #find number of enemy tiles
        for current_unit in units_list:
            if (current_unit[-1] == '1'):
                nb_enemies += 1
            elif (current_unit[-1] == '2'):
                nb_enemies -= 1 #prevents firing at allied units unless it's worth it

        if nb_enemies > max_enemies:
            max_enemies = nb_enemies
            aimed_tile = [tile[0], tile[1]]

    if max_enemies == 1:
        #at most one enemy can be shot at once: we try to find it's tile closest to it's center

        best_tile = tiles_list[0] #taking any tile to initialize best_tile and best_distance
        best_distance = ( ( best_tile[0]-target_row )**2 + ( best_tile[1]-target_col )**2 )**0.5

        for tile in tiles_list:
            center_distance = ( ( tile[0]-target_row )**2 + ( tile[1]-target_col )**2 )**0.5

            #testing distance against best and checking if unit part is in aimed tiled
            if center_distance < best_distance and (unit not in board[tile[0]][tile[1]]):
                best_distance = center_distance
                best_tile = tile

        aimed_tile = best_tile

    #if max_enemies == 0: no enemies, aimed_tile = None

    return aimed_tile
#end of ideal_aim

def find_mining_action(input_binary):
    """Find the action that corresponds to a given situation.

    Parameters
    ----------
    input_binary: 5 bit binary representing a situation (str)

    Return
    ------
    action: if an action is required: string representing the action to do (str)
            else: None (NoneType)
    """
    #dictionnary which relates every situation to an action;
    #a 'situation' is described as a binary, which itself represents results of
    #   combinatory logic
    LAPFE_dict = {
        '00000':'A',
        '00001':'P',
        '0001x':'P',
        '00100':'A',
        '00101': 'lock',
        '0011x':'lock',
        '01000':'lock',
        '01001':'release',
        '0101x':'P',
        '10xxx':'release',
        '11001':'release',
        '1101x':'release'
    }

    #preparing loop variables
    keys_list = list( LAPFE_dict.keys() )
    key_id = -1
    found = False

    #trying to find a matching partial binary from LAPFE_dict
    while key_id < len(keys_list)-1 and not found:
        key_id += 1
        dict_binary = keys_list[key_id]
        all_equal = True

        #compare every bit
        for bit_id in (0, 1, 2, 3, 4):
            if all_equal and dict_binary[bit_id] not in ('x', input_binary[bit_id]):
                all_equal = False

        if all_equal:
            found = True
    #loop end

    if found:
        return LAPFE_dict[ keys_list[key_id] ]

def get_mining_order(unit, data, board, AI_memory): #child function of AI_orders
    """Get one or two formatted orders for a given unit with a 'mine' objective.

    Parameters
    ----------
    unit: name of the unit whose order will be generated (str)
    data: data structure of the game's data (dict)
    board: data structure of the game board (list)
    AI_memory: data structure of the data used by the AI (dict)

    Returns
    -------
    order: formatted order(s) of the unit (str)

    Notes
    -----
    Parameter board is not used, it only stands there to match other get_X_order function's parameters
    so that it can be called from functions_dict in AI_orders.

    get_mining_order assumes that the target is an asteroid.
    get_mining_order includes a whitespace at the end of order.
    get_mining_order only works for player2.

    Version
    -------
    specification: Themelin Lucas (v.1 05/05/18)
    implementation: Themelin Lucas (v.1 05/05/18)
    """

    target = AI_memory['AI_units'][unit].split('&')[1]
    target_ore = data[target]['ore']
    binary = ''

    #setting up variables for combinatory logic; B_ stands for 'bool'
    #check if unit is locked
    B_locked = data[unit]['locked']
    binary += str( int( B_locked ) )

    #check if unit is on top of the targetted asteroid
    B_asteroid = data[unit]['center'] == data[target]['center']
    binary += str( int( B_asteroid ) )

    #check if unit is on top of the allied portal
    B_portal = data[unit]['center'] == data['portal2']['center']
    binary += str( int( B_portal ) )

    #check if unit is full
    B_full = False
    type = data[unit]['type']
    ore = data[unit]['ore']
    excavatorM_condition = (type == 'excavator-M') and (ore >= 4.0)
    excavatorL_condition = (type == 'excavator-L') and (ore >= 8.0)
    if excavatorM_condition or excavatorL_condition:
        B_full = True
    binary += str( int( B_full ) )

    #check if target is empty
    B_empty = target_ore <= 0
    binary += str( int( B_empty ) )

    #creating a loop to be able to get a second action if first action is release
    order = ''
    need_loop = True
    while need_loop:
        need_loop = False

        action = find_mining_action(binary)

        if action == 'lock':
            #lock excavator on portal or asteroid
            order += unit[:-1] + ':lock '

        elif action == 'release':
            order += unit[:-1] + ':release '
            #unlock excavator

        elif action == 'A':
            #move excavator towards target
            order += get_move_order(unit, data, target)

        elif action == 'P':
            #move excavator towards the AI's portal
            order += get_move_order(unit, data, 'portal2')

        if not need_loop and action == 'release':
            binary = '0' + binary[1:] #set B_locked bit to 0 -> 'unlocked unit'
            need_loop = True
        #end of first order building
    #end of while loop

    return order
#end of get_mining_order

def get_tilt_order(unit, data, board, AI_memory): #child function of AI_orders
    """Get one formatted order for the AI's tilt unit.

    Parameters
    ----------
    unit: name of the unit whose order will be generated (str)
    data: data structure of the game's data (dict)
    board: data structure of the game board (list)
    AI_memory: data structure of the data used by the AI (dict)

    Returns
    -------
    order: formatted order of the unit (str)

    Notes
    -----
    Returned order includes whitespace at the end.
    tilt unit may kill itself if draw_timer runs out next turn and unit only has 1 health.

    Version
    -------
    specification: Themelin Lucas (v.1 05/05/18)
    implementation: Themelin Lucas (v.1 05/05/18)
    """

    #initializing variables
    order = ''
    draw_timer = AI_memory['draw_timer']
    target = 'portal1' #no need to look into AI_memory, tilt target is always portal1
    target_center = data['portal1']['center']

    if unit_can_tilt(unit, data, AI_memory):

        #finding the best of the target's tiles to shoot at
        aimed_tile = ideal_aim(unit, data, board, target)

        #defining tiles "close to center" (center of portal1)
        row_range = range(target_center[0]-1, target_center[0]+1)
        col_range = range(target_center[1]-1, target_center[1]+1)
        close_to_center = [[row,col] for row in row_range for col in col_range]

        #shoot if we're out of time or if unit is close enough to center
        if (draw_timer < 2) or ( list(data[unit]['center']) in close_to_center ):
            order = unit[:-1] + ':*' + str(aimed_tile[0]) + '-' + str(aimed_tile[1]) + ' '

        #if tilt unit isn't aiming at the center, we have to move closer
        else:
            order = get_move_order(unit, data, target)

    elif draw_timer < 2:
        #unit shoots itself to gain time before the end of draw_timer
        aimed_tile = data[unit]['center']
        order = unit[:-1] + ':*' + str(aimed_tile[0]) + '-' + str(aimed_tile[1]) + ' '

    else: #if can't shoot target but has time to move:
        order = get_move_order(unit, data, target)

    return order
#end of get_tilt_order

def get_attack_order(unit, data, board, AI_memory): #child function of AI_orders
    """Get one formatted order for the given unit with 'attack' objective.

    Parameters
    ----------
    unit: name of the unit whose order will be generated (str)
    data: data structure of the game's data (dict)
    board: data structure of the game board (list)
    AI_memory: data structure of the data used by the AI (dict)

    Returns
    -------
    order: formatted order for the unit (str)

    Notes
    -----
    Returned order includes whitespace at the end.

    Version
    -------
    specification: Themelin Lucas (v.1 05/05/18)
    implementation: Themelin Lucas (v.1 05/05/18)
    """

    target = AI_memory['AI_units'][unit].split('&')[1]
    aimed_tile = ideal_aim(unit, data, board, target)
    order = ''

    #target not in range
    if aimed_tile == None:
        order = get_move_order(unit, data, target)

    else: #fire at target
        order = unit[:-1] + ':*' + str(aimed_tile[0]) + '-' + str(aimed_tile[1]) + ' '

    return order
#end of get_attack_order

def get_defend_order(unit, data, board, AI_memory): #child function of AI_orders
    """Get one formatted order for the given unit with 'attack' objective.

    Parameters
    ----------
    unit: name of the unit whose order will be generated (str)
    data: data structure of the game's data (dict)
    target: name of the unit targetted by the unit (str)
    board: data structure of the game board (list)

    Returns
    -------
    order: formatted order for the unit (str)

    Notes
    -----
    Returned order includes whitespace at the end.

    Version
    -------
    specification: Themelin Lucas (v.1 05/05/18)
    implementation: Themelin Lucas (v.1 05/05/18)
    """

    order = ''
    target = AI_memory['AI_units'][unit].split('&')[1]

    #check if any units are in range
    weak_enemies = [name for name in data if (name[-1] == '1') and (data[name]['life'] == 1)]
    other_enemies = [name for name in data if (name[-1] == '1') and (name not in weak_enemies)]

    #find best approaching enemy to fire at
    found_enemy = False
    for enemy in weak_enemies:
        if not found_enemy:
            aimed_tile = ideal_aim(unit, data, board, enemy)
            if aimed_tile != None:
                found_enemy = True

    #if did not find any vulnerable units
    if not found_enemy:
        for enemy in other_enemies:
            if not found_enemy:
                aimed_tile = ideal_aim(unit, data, board, enemy)
                if aimed_tile != None:
                    found_enemy = True

    if found_enemy: #generate shoot order
        order = unit[:-1] + ':*' + str(aimed_tile[0]) + '-' + str(aimed_tile[1]) + ' '

    #if unit isn't standing on the target it defends:
    elif data[unit]['center'] != data[target]['center']:
        order = get_move_order(unit, data, target)

    #else: wait for something to happen

    return order
#end of get_defend_order

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
    Values assigned to the keys are a string in the format 'objective&target', where
        'objective' is 'mine', 'attack', 'tilt', or 'defend';
        'target' is the name of an enemy unit or an asteroid (depending on objective).
    The value string can also be empty if the unit has been assigned an objective and target yet.

    AI_memory is initialized in run_game before the first turn.

    Version
    -------
    specification: Nathan Zampunieris, Themelin Lucas (v.2 03/05/18)
    implementation: Nathan Zampunieris, Themelin Lucas (v.1 03/05/18)
    """

    #initializing local variables
    orders_string = ""
    current_strategy = AI_memory['current_strategy']

    #verifying coherence of units between data and AI_memory
    AI_memory = units_check(data, AI_memory) #CODED & TESTED

    #deciding on strategy
    if current_strategy != 'final':
        AI_memory = decision_organism(data, AI_memory) #CODED & TESTED

    #generating orders to buy units
    orders_string, AI_memory = buying_orders(data, AI_memory) #CODED, TESTED, REREAD

    #manage excavators
    AI_memory = manage_excavators(data, AI_memory) #CODED, TESTED, REREAD

    #handle tilt unit
    AI_memory = manage_tilt(data, AI_memory) #CODED, TESTED, REREAD

    if current_strategy == 'fast':
        AI_memory = manage_ships_fast(data, AI_memory) #CODED, TESTED, REREAD
        #currently assign all defend units to portal1

    else: #strategy == 'final'
        AI_memory = manage_ships_final(data, AI_memory) #CODED, TESTED, REREAD

    #creating a dict to get function from objective
    functions_dict = {
        'attack':get_attack_order, #CODED, TESTED, REREAD
        'defend':get_defend_order, #CODED, SLOPPY TESTED, REREAD
        'mine':get_mining_order, #CODED, TESTED, REREAD
        'tilt':get_tilt_order #CODED, SLOPPY TESTED, REREAD
    }

    #generating orders and adding them to orders_string
    for unit_name, unit_value in AI_memory['AI_units'].items():
        objective = unit_value.split('&')[0]
        #add order to orders
        #orders_string += functions_dict[objective](unit_name, data, board, AI_memory)

        order = functions_dict[objective](unit_name, data, board, AI_memory)
        orders_string += order

    return orders_string[:-1], AI_memory #[:-2] removes end whitespace
#end of AI_orders

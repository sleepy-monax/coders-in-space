# -*- coding: utf-8 -*-

import random
import shutil
import time
import socket

def game_preparation(file):
    """ Prepare the data structures need to play the game based on a .mv file.

    Return
    ------
    - field: list of lists containing the characters contained in each cases of the board (list).
    - redfleet: dictionnary of dictionnaries containing the data of the ships of the red player (dict).
    - bluefleet: dictionnary of dictionnaries containing the data of the ships of the red player (dict).
    - asteroids: list of dictionnaries containing the data of the ships of the red player (list).

    Version
    -------
    - specification: Simon Defrenne (v.2 03/03/18)
    - implementation: Simon Defrenne (v.2 03/03/18)

    """

    # preparation work

    fh = open(file,"r")
    prep = fh.readlines()

    # generate store

    store = {"scout":{"health":3,"attack":1,"range":3,"cost":3},
    "warship":{"health":18,"attack":3,"range":5,"cost":9},
    "excavator-S":{"health":2,"tonnage":1,"cost":1},
    "excavator-M":{"health":3,"tonnage":4,"cost":2},
    "excavator-L":{"health":6,"tonnage":8,"cost":4}}

    # generate fleets and portals

    redfleet = {}
    bluefleet = {}

    redfleet["portal"] = {"type":"portal","health":100,"hitbox":[int(str.split(prep[3]," ")[0]),int(str.split(prep[3]," ")[1])],"ore":4,"locked":[],"identifiant":"R","score":0}
    bluefleet["portal"] = {"type":"portal","health":100,"hitbox":[int(str.split(prep[4]," ")[0]),int(str.split(prep[4]," ")[1])],"ore":4,"locked":[],"identifiant":"B","score":0}

    # generate asteroids

    asteroids = []
    asteroidsprep1 = prep[6:len(prep)]
    for asteroid in asteroidsprep1:
        asteroidsprep2 = str.split(asteroid," ")
        asteroidsprep2[-1] = asteroidsprep2[-1].replace("\n","")
        asteroidsprep3 = {"hitbox":[int(asteroidsprep2[0]),int(asteroidsprep2[1])],"ore":int(asteroidsprep2[2]),"harvest":int(asteroidsprep2[3]),"locked":[]}
        asteroids.append(asteroidsprep3)

    # stock the size of the map

    mapsize = [int(str.split(prep[1]," ")[0])-1,int(str.split(prep[1]," ")[1])-1]

    # cleaning work

    fh.close

    return redfleet,bluefleet,asteroids,store,mapsize

def manhattan_distance(case_1,case_2):
    """ Calculate the distance between two case on the field.

    Parameters
    ----------
    - case_1 : a particular case on the field (list)
    - case_2 : a particular case on the field (list)

    Return
    ------
    - distance: the distance between the two case (int)

    Version
    -------
    - specification: Simon Defrenne (v.1 18/03/18)
    - implementation: Simon Defrenne (v.1 18/03/18)

    """

    x_p,y_p = coordinates(case_1)
    x_e,y_e = coordinates(case_2)
    x_p = int(x_p)
    y_p = int(y_p)
    x_e = int(x_e)
    y_e = int(y_e)
    x1,x2 =  max(x_p,x_e),min(x_p,x_e)
    y1,y2 = max(y_p,y_e),min(y_p,y_e)
    distance = (x1 - x2) + (y1 - y2)
    return distance

def hitbox(ship):
    """Calculate the hitbox of a ship based on its type the localisation of its center.

    Parameters
    ----------
    - ship: ship whose hitbox is asked for (str).

    Returns
    -------
    - hitbox : list of coordinates that represent the ship (list).

    Version
    -------
    - specification: Simon Defrenne (v.1 18/03/18)
    - implementation: Simon Defrenne (v.1 18/03/18)

    """
    ship_type = ship["type"]
    x,y = coordinates(ship["hitbox"])

    full_hitbox = []
    full_hitbox.append([x,y])

    if ship_type == "excavator-M" or ship_type == "excavator-L" or ship_type == "scout" or ship_type == "warship" or ship_type == "portal":
        full_hitbox.append([x+1,y])
        full_hitbox.append([x-1,y])
        full_hitbox.append([x,y+1])
        full_hitbox.append([x,y-1])

    if ship_type == "excavator-L" or ship_type == "warship" or ship_type == "portal":
        full_hitbox.append([x+2,y])
        full_hitbox.append([x-2,y])
        full_hitbox.append([x,y+2])
        full_hitbox.append([x,y-2])

    if ship_type == "scout" or ship_type == "warship" or ship_type == "portal":
        full_hitbox.append([x+1,y+1])
        full_hitbox.append([x-1,y-1])
        full_hitbox.append([x+1,y-1])
        full_hitbox.append([x-1,y+1])

    if ship_type == "warship" or ship_type == "portal":
        full_hitbox.append([x+1,y+2])
        full_hitbox.append([x-1,y-2])
        full_hitbox.append([x+1,y-2])
        full_hitbox.append([x-1,y+2])
        full_hitbox.append([x+2,y+1])
        full_hitbox.append([x-2,y-1])
        full_hitbox.append([x+2,y-1])
        full_hitbox.append([x-2,y+1])

    if ship_type == "portal":
        full_hitbox.append([x+2,y+2])
        full_hitbox.append([x-2,y-2])
        full_hitbox.append([x+2,y-2])
        full_hitbox.append([x-2,y+2])

    return full_hitbox

def coordinates(list_coordinates):
    """ Split a list of two numbers into one abscissa and one ordinate

    Parameters
    ----------
    - list_coordinates : list of two numbers, one abscissa and one ordinate (list)

    Return
    ------
    - x : rank (int)
    - y : column (int)

    Version
    -------
    - specification: Simon Defrenne (v.2 04/05/18)
    - implementation: Simon Defrenne (v.1 03/03/18)

    """

    x = list_coordinates[0]
    y = list_coordinates[1]
    return x,y

def attack(ship,target,fleet,enemy_fleet,store):
    """ The attack of a ship against a target.

    Parameters
    ----------
    - ship : the name of the ship that attacks (dict)
    - target : the targeted case (list)
    - redfleet : the fleet of the red player (dict)
    - bluefleet : the fleet of the blue player (dict)
    - store: the data structure used to stock information on ships based on their types (dict)

    Return
    ------
    - redfleet : the fleet of the red player (dict)
    - bluefleet : the fleet of the blue player (dict)

    Version
    -------
    - specification: Simon Defrenne (v.1 18/03/18)
    - implementation: Simon Defrenne (v.1 18/03/18)
    """
    if ship in fleet:
        
        if fleet[ship]["type"] == "scout" or fleet[ship]["type"] == "warship":
            
            if manhattan_distance(fleet[ship]["hitbox"],target) <= store[fleet[ship]["type"]]["range"] and fleet[ship]["action"] == False:
                
                target[0]= int(target[0])
                target[1]= int(target[1])
                
                for ships in fleet:
                    if target in hitbox(fleet[ships]):
                        fleet[ships]["health"] -= store[fleet[ship]["type"]]["attack"]

                for ships in enemy_fleet:
                    if target in hitbox(enemy_fleet[ships]):
                        enemy_fleet[ships]["health"] -= store[fleet[ship]["type"]]["attack"]

                fleet[ship]["action"] = True

    return fleet,enemy_fleet

def buy(ship_name,ship_type,fleet,store):
    """ Add a specific ship to the chosen fleet.

    Parameters
    ----------
    - ship_name : the chosen name of the ship (str)
    - ship_type : the chosen type of the ship (str)
    - fleet : the fleet in which a ship is added (dict)
    - store: the data structure used to stock information on ships based on their types (dict)

    Return
    ------
    - fleet : the fleet in which a ship is added (dict)

    Version
    -------
    - specification: Simon Defrenne (v.1 18/03/18)
    - implementation: Simon Defrenne (v.1 18/03/18)
    """

    if store[ship_type]["cost"] <= fleet["portal"]["ore"]:
        fleet[ship_name] = {}
        fleet[ship_name]["type"] = ship_type
        fleet[ship_name]["health"] = store[ship_type]["health"]
        fleet[ship_name]["hitbox"] = fleet["portal"]["hitbox"]
        fleet[ship_name]["action"] = False

        if "tonnage" in store[ship_type]:
            fleet[ship_name]["tonnage"] = 0
            fleet[ship_name]["lock"] = False
        fleet["portal"]["ore"] -= store[ship_type]["cost"]

    return fleet

def name_ships(ship_type,fleet):
    """ Allows the IA to create names for a ship it will buy.

    Parameters
    ----------
    - ship_type : the chosen type of ship (str)
    - fleet : the fleet in which a ship is added (dict)

    Returns
    -------
    - ship_name: the name of the ship (str)


    Version
    -------
    - specification: Simon Defrenne (v.1 18/03/18)
    - implementation: Simon Defrenne, Marien (v.1 18/03/18)

    """

    if ship_type == "scout":
        ship_name_1 = "S"
    elif ship_type == "warship":
        ship_name_1 = "W"
    elif ship_type == "excavator-S":
        ship_name_1 = "E"
    elif ship_type == "excavator-M":
        ship_name_1 = "M"
    elif ship_type == "excavator-L":
        ship_name_1 = "L"

    ship_name_1 = fleet["portal"]["identifiant"] + ship_name_1

    right_name = False
    ship_name_2 = 1
    while not right_name:
        ship_name = ship_name_1 + str(ship_name_2)
        if ship_name in fleet:
            ship_name_2 += 1
        else:
            right_name = True

    return ship_name

def move(ship,fleet,target,mapsize):
    """ Move a ship into the target destination.

    Parameters
    ----------
    - ship : the name of the ship that moves (dict)
    - target : the targeted case (list)
    - fleet : the fleet of player (dict)
    - mapsize : list containing the number of rows and columns of the map (list)

    Return
    ------
    - fleet : the fleet of player (dict)

    Version
    -------
    - specification: Simon Defrenne (v.1 23/03/18)
    - implementation: Simon Defrenne (v.1 23/03/18)

    """
    if ship in fleet:

        movement = False

        if manhattan_distance(fleet[ship]["hitbox"],target) <= 2:
            if (not "tonnage" in fleet[ship]) or ("tonnage" in fleet[ship] and not fleet[ship]["lock"]):
                s_type = fleet[ship]["type"]
                if s_type == "warship" or s_type == "excavator-L":
                    if target[0] - 2 > 0:
                        movement = True
                    elif target[0] + 2 <= mapsize[0]:
                        movement = True
                    elif target[1] - 2 > 0:
                        movement = True
                    elif target[1] + 2 <= mapsize[1]:
                        movement = True
                elif s_type == "scout" or s_type == "excavator-M":
                    if target[0] - 1 > 0:
                        movement = True
                    elif target[0] + 1 <= mapsize[0]:
                        movement = True
                    elif target[1] - 1 > 0:
                        movement = True
                    elif target[1] + 1 <= mapsize[1]:
                        movement = True
                elif s_type == "excavator-S":
                    if target[0] > 0:
                        movement = True
                    elif target[0] <= mapsize[0]:
                        movement = True
                    elif target[1] > 0:
                        movement = True
                    elif target[1] <= mapsize[1]:
                        movement = True
        if movement:
            x_s,y_s = coordinates(fleet[ship]["hitbox"])
            x_t,y_t = coordinates(target)
            if (x_s == x_t or y_s == y_t) and manhattan_distance(fleet[ship]["hitbox"],target)==1:
                fleet[ship]["hitbox"]=target
            elif (x_s != x_t and y_s != y_t) and manhattan_distance(fleet[ship]["hitbox"],target)==2:
                fleet[ship]["hitbox"]=target
            fleet[ship]["action"] = True
    return fleet

def locking(ship,order,fleet,asteroids):
    """ Lock or unlock a excavator on a asteroid or its portal.

    Parameters
    ----------
    - ship : the name of the ship that locks/unlocks itself (dict)
    - order : "lock" to lock a ship, "release" to unlock it (str)
    - fleet : the fleet of the ship (dict)
    - asteroids : list of asteroids (list)

    Return
    ------
    - fleet : the fleet of the ship (dict)

    Version
    -------
    - specification: Simon Defrenne (v.1 18/03/18)
    - implementation: Simon Defrenne (v.1 18/03/18)
    """
    if ship in fleet:
        if fleet[ship]["type"] == "excavator-S" or fleet[ship]["type"] == "excavator-M" or fleet[ship]["type"] == "excavator-L":
            if order == "release":
                fleet[ship]["lock"] = False
                if fleet[ship]["hitbox"] == fleet["portal"]["hitbox"]:
                    fleet["portal"]["locked"].remove(ship)
                else:
                    for asteroid in asteroids:
                        if fleet[ship]["hitbox"] == asteroid["hitbox"]:
                            asteroid["locked"].remove(ship)
            elif order == "lock":
                if fleet[ship]["hitbox"] == fleet["portal"]["hitbox"]:
                    fleet["portal"]["locked"].append(ship)
                    fleet[ship]["lock"] = True
                else:
                    for asteroid in asteroids:
                        if fleet[ship]["hitbox"] == asteroid["hitbox"]:
                            fleet[ship]["lock"] = True
                            asteroid["locked"].append(ship)
    return fleet,asteroids

def turn(order_r,order_b, redfleet, bluefleet, store, asteroids,mapsize):
    """ Run a turn of the game based on the orders of the players.

    Parameters
    ----------
    - order_r : orders of the red player (str)
    - order_b : orders of the blue player (str)
    - redfleet : the fleet of the red player (dict)
    - bluefleet : the fleet of the blue player (dict)
    - asteroids : list of asteroids (list)
    - store: the data structure used to stock information on ships based on their types (dict)
    - mapsize : list containing the number of rows and columns of the map (list)

    Return
    ------
    - redfleet : the fleet of the red player (dict)
    - bluefleet : the fleet of the blue player (dict)
    - asteroids : list of asteroids (list)

    Version
    -------
    - specification: Simon Defrenne (v.1 23/03/18)
    - implementation: Simon Defrenne (v.1 23/03/18)

    """

    # resolve every orders and the harvest of ore

    r_attack_orders, r_move_orders, r_buy_orders, r_lock_orders = orders_prep(order_r)
    b_attack_orders, b_move_orders, b_buy_orders, b_lock_orders = orders_prep(order_b)

    redfleet = buy_resolution(r_buy_orders, redfleet,store)
    bluefleet = buy_resolution(b_buy_orders, bluefleet,store)

    redfleet,asteroids = locking_resolution(r_lock_orders, redfleet, asteroids)
    bluefleet,asteroids = locking_resolution(b_lock_orders, bluefleet, asteroids)

    redfleet = move_resolution(r_move_orders, redfleet,mapsize)
    bluefleet = move_resolution(b_move_orders, bluefleet,mapsize)

    redfleet,bluefleet = attack_resolution(r_attack_orders, redfleet, bluefleet, store, asteroids)
    bluefleet,redfleet = attack_resolution(b_attack_orders, bluefleet, redfleet, store, asteroids)
    
    if "portal" in redfleet and "portal" in bluefleet:
        redfleet,bluefleet,asteroids = harvest(redfleet,bluefleet,asteroids,store)

    # prepare the next turn

    for ship in redfleet:
        if redfleet[ship]["type"] != "portal":
            redfleet[ship]["action"] = False
    for ship in bluefleet:
        if bluefleet[ship]["type"] != "portal":
            bluefleet[ship]["action"] = False

    return redfleet, bluefleet, asteroids

def orders_prep(list_orders):
    """ Split the string of orders into four lists, based on the type of order.

    Parameters
    ----------
    List_orders: the sequence of order the player has given (str)

    Return
    ------
    attack_order: the attack orders (list)
    move_order: the moving orders (list)
    lock_order: the locking orders (list)
    buy_order: the buying orders (list)

    Version
    -------
    specification: Marien Dessy (v.1 10/04/18)
    implementation: Simon Defrenne (v.1 04/04/18)

    """

    list_orders = str.split(list_orders," ")
    attack_orders = []
    move_orders = []
    buy_orders = []
    lock_orders = []

    for order in list_orders:

        if "*" in order:
            attack_orders.append(order)
        elif "@" in order:
            move_orders.append(order)
        elif "lock" in order or "release" in order :
            lock_orders.append(order)
        elif "scout" in order or "warship" in order or "excavator-S" in order or "excavator-M" in order or "excavator-L" in order:
            buy_orders.append(order)

    return attack_orders, move_orders, buy_orders, lock_orders

def buy_resolution(buy_orders,fleet,store):
    """ Resolve the buying orders of a player.

    Parameters
    ----------
    - buy_orders: the buying orders (list)
    - fleet: the fleet of the  player who give the order (dict)
    - store: the data structure used to stock information on ships based on their types (dict

    Return
    ------
    - fleet: the fleet of the  player who give the order (dict)

    Version
    -------
    - specification: Marien Dessy (v.1 10/04/18)
    - implementation: Simon Defrenne (v.1 04/04/18)

    """
    for order in buy_orders:
        fleet = buy(str.split(order,":")[0],str.split(order,":")[1],fleet,store)
    return fleet

def locking_resolution(lock_orders,fleet,asteroids):
    """ Resolve the locking orders of a player.

    Parameters
    ----------
    - lock_orders: the locking orders (list)
    - fleet: the fleet of the  player who give the order (dict)
    - asteroids: the list of asteroids (list)

    Return
    ------
    - fleet: the fleet of the  player who give the order (dict)

    Version
    -------
    - specification: Marien Dessy (v.1 10/04/18)
    - implementation: Simon Defrenne (v.1 04/04/18)

    """

    for order in lock_orders:
        fleet,asteroids = locking(str.split(order,":")[0],str.split(order,":")[1],fleet,asteroids)
    return fleet,asteroids

def move_resolution(move_orders,fleet,mapsize):
    """ Resolve the move orders of a player.

    Parameters
    ----------
    - move_orders: the buying orders (list)
    - fleet: the fleet of the  player who give the order (dict)
    - mapsize : list containing the number of rows and columns of the map (list)

    Return
    ------
    - fleet: the fleet of the  player who give the order (dict)

    Version
    -------
    - specification: Marien Dessy (v.1 10/04/18)
    - implementation: Simon Defrenne (v.1 04/04/18)

    """

    for order in move_orders:
        ship = str.split(order,":@")[0]
        coordinates = str.split(order,":@")[1]
        coordinates = [int(str.split(coordinates, "-")[0]),int(str.split(coordinates, "-")[1])]

        fleet = move(ship,fleet,coordinates,mapsize)

    return fleet

def attack_resolution(attack_orders,fleet,enemy_fleet,store,asteroids):
    """ Resolve the attack orders of a player.

    Parameters
    ----------
    - buy_orders: the buying orders (list)
    - fleet: the fleet of the  player who give the order (dict)
    - enemy_fleet: the fleet of the enemy of the preceding player (dict)
    - asteroids: the list of asteroids (list)

    Return
    ------
    - fleet: the fleet of the  player who give the order (dict)
    - enemy_fleet: the fleet of the enemy of the preceding player (dict)

    Version
    -------
    - specification: Marien Dessy (v.1 10/04/18)
    - implementation: Simon Defrenne (v.1 04/04/18)

    """

    for order in attack_orders:
        ship = str.split(order,":*")[0]
        coordinates_attack = str.split(order,":*")[1]
        coordinates_attack_2 = str.split(coordinates_attack, "-")
        coordinates = [coordinates_attack_2[0],coordinates_attack_2[1]]
        fleet,enemy_fleet = attack(ship,coordinates,fleet,enemy_fleet,store)

    # delete the destroyed ships

    fleet_dead_ships = []
    enemy_fleet_dead_ships = []

    for ships in fleet:
        if fleet[ships]["health"] <= 0:
            fleet_dead_ships.append(ships)
    for ships in enemy_fleet:
        if enemy_fleet[ships]["health"] <= 0:
            enemy_fleet_dead_ships.append(ships)
            
    for ship in fleet_dead_ships:
        if "lock" in fleet[ship] and fleet[ship]["lock"]:
            if fleet[ship]["hitbox"] == fleet["portal"]["hitbox"] :
                if ship in fleet["portal"]["locked"]:
                    index = fleet["portal"]["locked"].index(ship)
                    del fleet["portal"]["locked"][index]
            else:
                for asteroid in asteroids:
                    if ship in asteroid["locked"]:
                        index = asteroid["locked"].index(ship)
                        del asteroid["locked"][index]
        del fleet[ship]
        
    for ship in enemy_fleet_dead_ships:
        if "lock" in enemy_fleet[ship] and enemy_fleet[ship]["lock"]:
            if enemy_fleet[ship]["hitbox"] == enemy_fleet["portal"]["hitbox"] :
                if ship in enemy_fleet["portal"]["locked"]:
                    index = enemy_fleet["portal"]["locked"].index(ship)
                    del enemy_fleet["portal"]["locked"][index]
            else:
                for asteroid in asteroids:
                    if ship in asteroid["locked"]:
                        index = asteroid["locked"].index(ship)
                        del asteroid["locked"][index]
        del enemy_fleet[ship]

    return fleet,enemy_fleet

def harvest(redfleet,bluefleet,asteroids,store):
    """ Resolve the harvesting of locked ships.

    Parameters
    ----------
    - redfleet: the fleet of the red player (dict)
    - bluefleet: the fleet of the blue player (dict)
    - asteroids: the list of asteroids (list)
    - store: the data structure used to stock information on ships based on their types (dict)

    Return
    ------
    - fleet: the fleet of the  player who give the order (dict)
    - enemy_fleet: the fleet of the enemy of the preceding player (dict)

    Version
    -------
    - specification: Marien Dessy (v.1 10/04/18)
    - implementation: Simon Defrenne (v.1 04/04/18)

    """

    for asteroid in asteroids:
        if asteroid["locked"] != []:
            red_lock = []
            blue_lock = []

            for ship in asteroid["locked"]:
                if ship in redfleet:
                    red_lock.append(ship)
                elif ship in bluefleet:
                    blue_lock.append(ship)

            potential_harvest = len(asteroid["locked"]) * asteroid["harvest"]
            if potential_harvest > asteroid["ore"]:
                potential_harvest = asteroid["ore"]
            ship_harvest = potential_harvest/len(asteroid["locked"])

            for ship in red_lock:
                tonnage = store[redfleet[ship]["type"]]["tonnage"]
                carried_weight = redfleet[ship]["tonnage"]
                if tonnage - carried_weight < ship_harvest:
                    redfleet[ship]["tonnage"] += tonnage - carried_weight
                    asteroid["ore"] -= tonnage - carried_weight
                else:
                    redfleet[ship]["tonnage"] += ship_harvest
                    asteroid["ore"] -= ship_harvest

            for ship in blue_lock:
                tonnage = store[bluefleet[ship]["type"]]["tonnage"]
                carried_weight = bluefleet[ship]["tonnage"]
                if tonnage - carried_weight < ship_harvest:
                    bluefleet[ship]["tonnage"] += tonnage - carried_weight
                    asteroid["ore"] -= tonnage - carried_weight
                else:
                    bluefleet[ship]["tonnage"] += ship_harvest
                    asteroid["ore"] -= ship_harvest

    for ship in redfleet["portal"]["locked"]:
        redfleet["portal"]["ore"] += redfleet[ship]["tonnage"]
        redfleet["portal"]["score"] += redfleet[ship]["tonnage"]
        redfleet[ship]["tonnage"] -= redfleet[ship]["tonnage"]

    for ship in bluefleet["portal"]["locked"]:
        bluefleet["portal"]["ore"] += bluefleet[ship]["tonnage"]
        bluefleet["portal"]["score"] += bluefleet[ship]["tonnage"]
        bluefleet[ship]["tonnage"] -= bluefleet[ship]["tonnage"]

    return redfleet,bluefleet,asteroids

def IA_buy(IA_fleet,enemy_fleet,store):
    """ Make the IA buy a new ship and name it to add this ship in his fleet.

    Parameters
    ----------
    - IA_fleet: the fleet of the IA (dict)
    - store: the database which contain all information about the ship's stats (dict)
    - Return
    ------
    - order: the buy order (str)

    Version
    -------
    - specification: Marien Dessy (v.2 27/04/18)
    - implementation: Marien Dessy, Simon Defrenne (v.4 04/05/18)
    """

    ship_count = {}
    ship_count["excavator-S"] = 0
    ship_count["excavator-M"] = 0
    ship_count["excavator-L"] = 0
    ship_count["scout"] = 0
    ship_count["warship"] = 0

    for ship in IA_fleet:
        if ship != "portal":
            s_type = IA_fleet[ship]["type"]
            ship_count[s_type] +=1

    order = ""
    buy = True
    stock = IA_fleet["portal"]["ore"]
    score = IA_fleet["portal"]["score"]
    ship_to_buy = {}


    while buy:
        if ship_count["excavator-M"] < 2:
            type_to_buy = "excavator-M"
            ship_count["excavator-M"] += 1
            stock -= 2
        elif ship_count["scout"] < 2 and score >= 8 and stock >= 3:
            type_to_buy = "scout"
            ship_count["scout"] += 1
            stock -= 3
        elif score >= 16 and stock >=9:
            type_to_buy = "warship"
            stock -= 9
        elif ship_count["excavator-S"] < 1 and score >= 8 and stock>=1:
            type_to_buy = "excavator-S"
            ship_count["excavator-S"] += 1
            stock -= 1
        elif ship_count["excavator-S"] < 2 and score >= 24 and stock>=1:
            type_to_buy = "excavator-S"
            ship_count["excavator-S"] += 1
            stock -= 1
        else:
            buy = False

        if buy:
            name = name_ships(type_to_buy,IA_fleet)
            while name in ship_to_buy:
                name = name[0:2] + str(int(name[2:])+1)
            ship_to_buy[name] = type_to_buy

    for ship in ship_to_buy:
        order += ship + ":" + ship_to_buy[ship] + " "
    
    return order

def calculate_trajectory(test,objectives,choice=True):
    """ Calculate the closest or furthest cases in a list from another defined case.

    Parameters
    ----------
    - test : the case that is compared (list)
    - objective : the list in which we look for the closest case (list)
    - choice : True for the closest cases, False for the furthest (bool)

    Return
    ------
    - target: one of the closest possibles points (list)

    Version
    -------
    specification: Simon Defrenne (v.1 27/04/18)
    implementation: Simon Defrenne (v.1 27/04/18)
    """

    target = []
    possible_distance = {}
    tested_distance = None
    
    for objective in objectives:

        tested_distance = calculate_turn_distance(test,objective)
        if not tested_distance in possible_distance:
            possible_distance[tested_distance] = []
        possible_distance[tested_distance].append(objective)

    possible_distance_2 = None
    for distance in possible_distance:
        if choice:
            if possible_distance_2 == None or possible_distance_2 > distance:
                possible_distance_2 = distance
        else:
            if possible_distance_2 == None or possible_distance_2 < distance:
                possible_distance_2 = distance

    target = possible_distance[possible_distance_2]

    return target

def calculate_turn_distance(case_1,case_2):
    """ Calculate the number of required turns to go between two case on the field.

    Parameters
    ----------
    - case_1 : a particular case on the field (list)
    - case_2 : a particular case on the field (list)

    Return
    ------
    - distance: the distance between the two case (int)

    Version
    -------
    - specification: Simon Defrenne (v.1 18/03/18)
    - implementation: Simon Defrenne (v.1 18/03/18)
    """

    x1,y1 = coordinates(case_1)
    x2,y2 = coordinates(case_2)
    distance = max(max(x1-x2,x2-x1),max(y1-y2,y2-y1))
    return distance
    
def overlay_trap(ship, IA_fleet,enemy_fleet,possible_moves,objectives):
    """ Make a ship go into an opponent battleship 
    
    Parameters
    ----------
    - ship: the ship not ordered yet (dict)
    - IA_fleet: the fleet of the IA (dict)
    - enemy_fleet : the fleet of the opposing player (dict)
    - possibles_moves : doable moves by the ship (list)
    - objectives : objectives of the ship (list)

    Return
    ------
    - objectives : objectives of the ship (list)

    Version
    -------
    - specification: Simon Defrenne (v.1 06/05/18)
    - implementation: Simon Defrenne (v.1 06/05/18)
    
    
    """
    
    battleships = []

    for e_ship in enemy_fleet:
        if enemy_fleet[e_ship]["type"] == "scout" or enemy_fleet[e_ship]["type"] == "warship":
            battleships.append(e_ship)

    for e_ship in battleships:

        overlay = False

        if IA_fleet[ship]["hitbox"] in hitbox(enemy_fleet[e_ship]):
            if not overlay:
                objectives = []
                overlay = True
            for hitbox_s in hitbox(enemy_fleet[e_ship]):
                if hitbox_s in possible_moves:
                    objectives.append(hitbox_s)

        elif not overlay:
            objectives.append(enemy_fleet[e_ship]["hitbox"])

    if objectives == []:
        objectives.append(enemy_fleet["portal"]["hitbox"])
                
    return objectives
    
def IA_move(ship_dict,IA_fleet,enemy_fleet,asteroids,store,mapsize):
    """ Generate move orders for a ship of the IA.

    Parameters
    ----------
    - ship_list: the list of ships not ordered yet (dict)
    - IA_fleet: the fleet of the IA (dict)
    - enemy_fleet : the fleet of the opposing player (dict)
    - asteroids : the list of asteroids (list)
    - store: the data structure used to stock information on ships based on their types (dict)
    - mapsize : list containing the number of rows and columns of the map (list)

    Return
    ------
    - order: the move order (str)

    Version
    -------
    specification: Marien Dessy, Simon Defrenne (v.3 04/05/18)
    implementation: Marien Dessy, Simon Defrenne (v.4 06/05/18)

    """
    order = ""

    for ship in ship_dict:

        # set up

        x_s,y_s = IA_fleet[ship]["hitbox"]
        possible_moves = []
        possible_moves.append([x_s+1,y_s])
        possible_moves.append([x_s+1,y_s+1])
        possible_moves.append([x_s,y_s+1])
        possible_moves.append([x_s-1,y_s])
        possible_moves.append([x_s,y_s-1])
        possible_moves.append([x_s-1,y_s-1])
        possible_moves.append([x_s+1,y_s-1])
        possible_moves.append([x_s-1,y_s+1])
        objectives = []

        # calculating objectives of each ship

        if IA_fleet[ship]["type"] == "excavator-M" or IA_fleet[ship]["type"] == "excavator-L":

            if IA_fleet[ship]["tonnage"] == 0:
                for asteroid in asteroids:
                    if asteroid["ore"] > 0:
                        objectives.append(asteroid["hitbox"])

            elif IA_fleet[ship]["tonnage"] == store[IA_fleet[ship]["type"]]["tonnage"]:
                objectives.append(IA_fleet["portal"]["hitbox"])

            elif IA_fleet[ship]["tonnage"] < store[IA_fleet[ship]["type"]]["tonnage"]:

                tested_distance = 0
                total_distance = 0
                for asteroid in asteroids:
                    if asteroid["ore"] > 0:
                        distance_a_s = calculate_turn_distance(asteroid["hitbox"],IA_fleet[ship]["hitbox"])
                        distance_a_p = calculate_turn_distance(asteroid["hitbox"],IA_fleet["portal"]["hitbox"])
                        tested_distance = distance_a_s + distance_a_p
                        if tested_distance < total_distance:
                            total_distance = distance_a_s + distance_a_p
                            objectives = []
                        objectives.append(asteroid["hitbox"])
                        
            if objectives == []:
                objectives = overlay_trap(ship, IA_fleet,enemy_fleet,possible_moves,objectives)

        elif IA_fleet[ship]["type"] == "scout":

            for e_ship in enemy_fleet:
                if enemy_fleet[e_ship]["type"] == "excavator-M" or enemy_fleet[e_ship]["type"] == "excavator-L":
                    objectives.append(enemy_fleet[e_ship]["hitbox"])
            if objectives == []:
                x_p, y_p = enemy_fleet["portal"]["hitbox"]
                objectives.append(x_p + 3, y_p)
                objectives.append(x_p + 2, y_p + 1)
                objectives.append(x_p + 2, y_p - 1)
                objectives.append(x_p + 1, y_p + 2)
                objectives.append(x_p + 1, y_p - 2)
                objectives.append(x_p, y_p)
                objectives.append(x_p, y_p)
                objectives.append(x_p - 1, y_p + 2)
                objectives.append(x_p - 1, y_p - 2)
                objectives.append(x_p - 2, y_p + 1)
                objectives.append(x_p - 2, y_p - 1)
                objectives.append(x_p - 3, y_p)

        elif IA_fleet[ship]["type"] == "warship":

            objectives.append(enemy_fleet["portal"]["hitbox"])

        elif IA_fleet[ship]["type"] == "excavator-S":

            objectives = overlay_trap(ship, IA_fleet,enemy_fleet,possible_moves,objectives)
            
        target = calculate_trajectory(IA_fleet[ship]["hitbox"],objectives)
        target = random.choice(target)

        possible_moves_2 = calculate_trajectory(target,possible_moves)
        x_final,y_final = random.choice(possible_moves_2)

        # correction of trajectory if needed

        if x_final <= 0:
            x_final += 2
        elif x_final >= mapsize[0]:
            x_final -= 2

        if y_final <= 0:
            y_final += 2
        elif y_final >= mapsize[1]:
            y_final -= 2

        # adding the order the string

        order += ship + ":@" + str(x_final) + "-" + str(y_final) + " "

    # return the move order

    return order

def target(ally_ship,enemy_fleet,store):
    """ The Artificial Intelligence choose a target for one of its ships.

    Parameters
    ----------
    - ally_ship : the ship that is checked to choose a target (dict)
    - enemy_fleet : the fleet of the enemy (dict)
    - store: the data structure used to stock information on ships based on their types (dict)

    Return
    ------
    - target: the targeted case on which the ship shoots (list)

    Version
    -------
    - specification: Simon Defrenne (v.1 09/03/18)
    - implementation: Simon Defrenne, Marien Dessy (v.2 04/05/18)
    """

    list_targets = []
    target = []
    s_range = store[ally_ship["type"]]["range"]

    for ship in enemy_fleet:
        distance = manhattan_distance(ally_ship["hitbox"],enemy_fleet[ship]["hitbox"])
        center_check = distance <= s_range
        type_check = enemy_fleet[ship]["type"] != "excavator-S"
        if center_check and type_check:
            list_targets.append(ship)
        
    if list_targets != []:
        health_test = None
        for ship in list_targets:
            if health_test == None or health_test < enemy_fleet[ship]["health"]:
                health_test = enemy_fleet[ship]["health"]
                target = enemy_fleet[ship]["hitbox"]
        return target
    return None
    
def IA_attack(ship_dict,IA_fleet,enemy_fleet,store):
    """ The IA choose randomly a ship to attack.

    Parameters
    ----------
    - ship_dict: the dictionnary of ships not ordered yet (dict)
    - IA_fleet: the fleet of the IA (dict)
    - fleet: the fleet of the player (dict)
    - store: the data structure used to stock information on ships based on their types (dict)

    Return
    ------
    - order: the attack orders

    Version
    -------
    - specification: Marien Dessy (v.1 11/04/18)
    - implementation: Marien Dessy, Simon Defrenne (v.1 11/04/18)
    """

    order = ""

    battleships = []
    for ship in ship_dict:
        if ship != "portal" and (not "tonnage" in IA_fleet[ship]):
            battleships.append(ship)

    for ship in battleships:
        attacked_case = target(IA_fleet[ship],enemy_fleet,store)
        if attacked_case != None and not(attacked_case in hitbox(IA_fleet[ship])):
            order += str(ship + ":*" + str(attacked_case[0]) + "-" + str(attacked_case[1]) + " ")
    
    return order

def IA_locking(ship_dict,IA_fleet,asteroids,store):
    """ The IA choose randomly a ship to attack.

    Parameters
    ----------
    - ship_list: the list of ships not ordered yet (dict)
    - IA_fleet: the fleet of the IA (dict)
    - asteroids: the fleet of the player (dict)
    - store: the data structure used to stock information on ships based on their types (dict)

    Return
    ------
    - order: the locking orders

    Version
    -------
    - specification: Marien Dessy (v.1 11/04/18)
    - implementation: Marien Dessy (v.1 11/04/18)
    """

    excavators = {}
    for ship in ship_dict:
        if "tonnage" in IA_fleet[ship]:
            excavators[ship] = IA_fleet[ship]

    locked_excavators = {}
    unlocked_excavators = {}

    for ship in excavators:
        if excavators[ship]["lock"]:
            locked_excavators[ship]=excavators[ship]
        else:
            unlocked_excavators[ship]=excavators[ship]

    order = ""

    for ship in locked_excavators:
        s_type = locked_excavators[ship]["type"]
        if locked_excavators[ship]["tonnage"] == 0 and locked_excavators[ship]["hitbox"] == IA_fleet["portal"]["hitbox"]:
            order += ship + ":release "
        else :
            for asteroid in asteroids:
                if ship in asteroid["locked"]:
                    if asteroid["ore"] <= 0 or locked_excavators[ship]["tonnage"] == store[s_type]["tonnage"]:
                        order += ship + ":release "

    for ship in unlocked_excavators:
        s_type = unlocked_excavators[ship]["type"]
        for asteroid in asteroids:
            ore_check = asteroid["ore"] > 0
            hitbox_check = unlocked_excavators[ship]["hitbox"] == asteroid["hitbox"]
            tonnage_check = excavators[ship]["tonnage"] < store[s_type]["tonnage"]
            if ore_check and hitbox_check and tonnage_check:
                order += ship + ":lock "
        if unlocked_excavators[ship]["hitbox"] == IA_fleet["portal"]["hitbox"] and excavators[ship]["tonnage"] > 0:
            order += ship + ":lock "

    return order

def IA_complete(fleet,enemy_fleet,asteroids,store,mapsize):
    """ Generate the orders for the IA.

    Parameters
    ----------
    - fleet: the fleet that will be used by the IA (dict)
    - enemy_fleet: the fleet of the enemy (dict)
    - asteroids: the fleet of the player (dict)
    - store: the data structure used to stock information on ships based on their types (dict)

    Return
    ------
    - order: the order given by the IA (str)

    Version
    -------
    - specification: Marien Dessy (v.1 12/04/18)
    """

    order = ""
    ship_dict = {}

    for ship in fleet:
        if ship != "portal":
            ship_dict[ship] = None

    order += IA_buy(fleet,enemy_fleet,store)

    order += IA_locking(ship_dict,fleet,asteroids,store)
    for ship in fleet:
        if ship in order:
            del ship_dict[ship]

    order += IA_attack(ship_dict,fleet,enemy_fleet,store)
    for ship in fleet:
        if ship in order and ship in ship_dict:
            del ship_dict[ship]

    order += IA_move(ship_dict,fleet,enemy_fleet,asteroids,store,mapsize)
        
    order = str.strip(order)
    
    return order

# Gui framework
# ==============================================================================
# framework for easy user interface creation.

# Canvas creation and printing.
# ------------------------------------------------------------------------------
# Create and print a canvas in the user console.


def create_canvas(width, height, enable_color = True):
    """
    Create a new char canvas.

    Parameters
    ----------
    height: height of the game view (int).
    width: width of the game view (int).
    enable_color: enable color in the game view (bool)

    Return
    ------
    canvas: 2D ascii canvas (dic).
    """

    # Initialize the canvas.
    canvas = {'size': (width, height), 'color': enable_color, 'grid': {}}

    # Create canvas's tiles.
    for x in range(width):
        for y in range(height):
            canvas['grid'][(x,y)] = {'color':None, 'back_color':None, 'char':' '}

    return canvas


def print_canvas(canvas, x = 0, y = 0):
    """
    Print canvas in the terminal.

    Parameters
    ----------
    canvas: canvas to print on screen (dic).
    (optional) x, y: coodinate in the terminal (int).
    """

    canvas_width = canvas['size'][0]
    canvas_height = canvas['size'][1]

    # Hide and set cursor coordinates.
    line = '\033[?25l'

    for y in range(canvas_height):
        for x in range(canvas_width):

            # Get coordinate.
            grid_item = canvas['grid'][(x,y)]

            # Get coordinate information.
            char = grid_item['char']
            color = grid_item['color']
            back_color = grid_item['back_color']

            if (canvas['color']):
                line = line + set_color(char, color, back_color)
            else:
                line = line + char

        line += '\n'

    # Print, remove the laste \n et reset the print cursor..
    print(line[:-1] + '\033[?25h')


# Canvas drawing.
# ------------------------------------------------------------------------------
# All tools and brush to draw on the canvas.


def put(canvas, x, y, char, color = None, back_color = None):
    """
    Put a character in the canvas.

    Parameters
    ----------
    canvas: canvas to draw in (dic).
    x, y: coordinate of were to put the char (int).
    char: char to put (str).
    (optiona) color, back_color: color for the char (string).

    Return
    ------
    canvas: canvas with the char put on it (dic).
    """

    # Check if the coordinate is in the bound of the canvas.
    if x < canvas['size'][0] and x >= 0 and\
       y < canvas['size'][1] and y >= 0:

        # Put the char a the coordinate.
        canvas['grid'][(x,y)]['char'] = char
        canvas['grid'][(x,y)]['color'] = color
        canvas['grid'][(x,y)]['back_color'] = back_color

    return canvas

def put_ship(canvas, x, y, char, color = None, back_color = None):
    """
    Put function, but for ships.

    Parameters
    ----------
    canvas: canvas to draw in (dic).
    x, y: coordinate of were to put the char (int).
    char: char to put (str).
    (optiona) color, back_color: color for the char (string).

    Return
    ------
    canvas: canvas with the char put on it (dic).
    """

    x -= 1
    y -= 1
    
    # Check if the coordinate is in the bound of the canvas.
    if x < canvas['size'][0] and x >= 0 and\
       y < canvas['size'][1] and y >= 0:

        # Put the char a the coordinate.
        canvas['grid'][(x,y)]['char'] = char
        canvas['grid'][(x,y)]['color'] = color
        canvas['grid'][(x,y)]['back_color'] = back_color

    return canvas

def put_canvas(canvas, canvas_bis, x, y):
    """
    Put a canvas in the canvas.

    Parameters
    ----------
    canvas: canvas to draw in (dic).
    canvas_bis: canvas to put in the main canvas (dic).
    x, y: coordinate of the canvas (int).

    Return
    ------
    canvas: the canvas with the other canvas on it (dic).
    """

    for cx in range(canvas_bis['size'][0]):
        for cy in range(canvas_bis['size'][1]):
            char = canvas_bis['grid'][(cx, cy)]
            canvas = put(canvas, cx + x, cy + y, char['char'], char['color'], char['back_color'])

    return canvas


def put_window(canvas, window_content, title, x, y, style="double", color = None, back_color = None):
    """
    Put a window with a windows content in the main canvas.

    Parameters
    ----------
    canvas: canvas to draw in (dic).
    window_content: content of the window (dic).
    title: title of the window (str).
    x, y: coordinate of the window (int).
    (optional) style: Style of the window (str).

    Return
    ------
    canvas: the canvas with the window on it (dic).
    """
    c = create_canvas(window_content["size"][0] + 2, window_content["size"][1] + 2, True)
    c = put_canvas(c, window_content, 1, 1)
    c = put_box(c, 0, 0, window_content["size"][0] + 2, window_content["size"][1] + 2, style)
    c = put_text(c, 1, 0, "| %s |" % title, color, back_color)

    canvas = put_canvas(canvas, c, x, y)
    return canvas


def put_box(canvas, x, y, width, height, mode = 'double', color = None, back_color = None):
    """
    Put a box in the canvas.

    Parameters
    ----------
    canvas: canvas to draw in (dic).
    x, y: coordinate of the rectangle (int).
    width, height: size of the rectangle (int).
    mode: double ou single line <'double'|'single'> (str).
    color, back_color: color for the char (string).

    Return
    ------
    canvas: canvas whith the box (dic).

    """

    rect_char = ()

    if mode == 'double':
        rect_char = ('═', '║', '╔', '╚', '╗', '╝')
    elif mode == 'single':
        rect_char = ('─', '│', '┌', '└', '┐', '┘')

    # Put borders.
    put_rectangle(canvas, x, y, width, 1, rect_char[0], color, back_color)
    put_rectangle(canvas, x, y + height - 1, width, 1, rect_char[0], color, back_color)

    put_rectangle(canvas, x, y, 1, height, rect_char[1], color, back_color)
    put_rectangle(canvas, x + width - 1, y, 1, height, rect_char[1], color, back_color)

    # Put corners.
    put(canvas, x, y, rect_char[2], color, back_color)
    put(canvas, x, y + height - 1, rect_char[3], color, back_color)
    put(canvas, x + width - 1, y, rect_char[4], color, back_color)
    put(canvas, x + width - 1, y + height - 1, rect_char[5], color, back_color)

    return canvas


def put_rectangle(canvas, x, y, width, height, char, color = None, back_color = None):
    """
    Put a filled rectangle in the canvas.

    Parameters
    ----------
    canvas: canvas to draw in (dic).
    x, y: coordinate of the rectangle (int).
    width, height: size of the rectangle (int).
    color, back_color: color for the char (string).

    Return
    ------
    canvas: canvas whith the rectangle (dic).

    """

    for w in range(width):
        for h in range(height): canvas = put(canvas, x + w, y + h, char, color, back_color)

    return canvas

def put_text(canvas, x, y, text, color = None, back_color = None):
    """
    Put a text in the canvas.

    Parameters
    ----------
    canvas: canvas to draw in (dic).
    x, y: coordinate of the string (int).
    direction_x, direction_y: direction to draw the string (int).

    Return
    ------
    canvas: game view with the new string (dic).

    Notes
    -----
    direction_x, direction_y: Muste be -1, 0 or 1.

    """

    for char in text:
        canvas = put(canvas, x, y, char, color, back_color)
        x += 1
        y += 0

    return canvas


def set_color(text, foreground_color, background_color):
    """
    Change the color of a text.

    Parameters
    ----------
    text: string to color (str).
    fore_color: name of the foreground color (str).
    back_color: name of the background color (str).

    Return
    ------
    colored_text: colored string (str).

    Notes
    -----
    Colors: grey, red, green, yellow, blue, magenta, cyan, white.

    ANSI color escape sequences: http://ascii-table.com/ansi-escape-sequences.php

    """
    color = { 'grey': 0, 'red': 1, 'green': 2, 'yellow': 3, 'blue': 4, 'magenta': 5, 'cyan': 6, 'white': 7 }
    reset = '\033[0m'
    format_string = '\033[%dm%s'

    if foreground_color is not None: text = format_string % (color[foreground_color] + 30, text)
    if background_color is not None: text = format_string % (color[background_color] + 40, text)

    text += reset

    return text

def slide_animation(canvas_foreground, canvas_background):
    """

    """
    out_canvas = create_canvas(canvas_background['size'][0], canvas_background['size'][1])
    slide_value = 0

    while slide_value <= canvas_background['size'][1]:
        put_canvas(out_canvas, canvas_background, 0, 0)
        put_canvas(out_canvas, canvas_foreground, 0, 0 - slide_value)
        print_canvas(out_canvas)
        slide_value += 10

def show_game(red_team, blue_team, asteroids, mapsize, store):
    """ 
    show the UI for the game
    
    parameters
    ----------
    red_team: show the red team
    blue_team: show the blue team
    asteroids: show the asteroids
    mapsize: give the size for the visual map
    store: show the store
    
    Version
    -------
    specification: Alexis Losenko (v.1 6/05/18)
    implementation: Alexis Losenko(v.1 01/05/18)

    """
    X = 0
    Y = 1
    
    tsize = shutil.get_terminal_size((90, 60))
    tsize = (tsize[X]-1, tsize[Y]-1)
    c = create_canvas(tsize[X] , tsize[Y])

    game_window = create_canvas(*mapsize)
    shop_window = create_canvas(20, len(store) * 2)

    red_window = render_team_window(red_team)
    blue_window = render_team_window(blue_team)

    for asteroid in asteroids:
        put_ship(game_window, *asteroid["hitbox"], "o", "magenta")

    #Now, it's the position of Portal
    for h in hitbox(blue_team["portal"]):
        put_ship(game_window, *h, "◘", "blue")
    for h in hitbox(red_team["portal"]):
        put_ship(game_window, *h, "◘", "red")

    #go to show every ship
    for ship in red_team:
        if ship != "portal":
            for h in hitbox(red_team[ship]):
                put_ship(game_window, *h, "■", "red")
            put_ship(game_window, *red_team[ship]["hitbox"], "X", "red")

    for ship in blue_team:
        if ship != "portal":
            for h in hitbox(blue_team[ship]):
                put_ship(game_window, *h, "■", "blue")
            put_ship(game_window, *blue_team[ship]["hitbox"], "X", "blue")

    line = 0

    for type in store:
        name = type
        type = store[type]
        put_text(shop_window, 0, line * 2, name, "yellow")

        if "excavator" in name:
            put_text(shop_window, 0, line * 2+1, "  P:%i T:%i" % (type["cost"], type["tonnage"]))
        else:
            put_text(shop_window, 0, line * 2+1, "  P:%i A:%i" % (type["cost"], type["attack"]))

        line += 1

    origin = (tsize[X] // 2 - game_window["size"][X] // 2, tsize[Y] // 2 - game_window["size"][Y] // 2)

    put_window(c, game_window, "Mining War", *origin)

    put_window(c, shop_window, "Shop", origin[X] - red_window["size"][X] - 2, origin[Y] + red_window["size"][Y] + 2)

    put_window(c, red_window, "Red",  origin[X] - red_window["size"][X] - 2, origin[Y], "double", "red")
    put_window(c, blue_window, "Blue", origin[X] + game_window["size"][X] + 2, origin[Y], "double", "blue")

    print_canvas(c)

def render_team_window(team):
    """
    show the text for each ships and detail
    
    parameters
    ----------
    team: take the information of each team to show you in window
    
    return
    ------
    return the game window
    
    """
    
    X = 0
    Y = 1
    
    team_window = create_canvas(20, 20)
    line = 0

    for ship in team:
        name = ship
        if ship != "portal":
            ship = team[ship]
            position = ship["hitbox"]
            if ( "excavator" in ship["type"]):
                put_text(team_window, 0, line, "%s %i-%i T:%i H:%i" % (name, position[X] + 1, position[Y] + 1, ship["tonnage"], ship["health"]))
            else:
                put_text(team_window, 0, line, "%s %i-%i H:%i" % (name, position[X] + 1, position[Y] + 1, ship["health"]))
            line += 1

    return team_window
    
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

def game(path, player_id, remote_IP='127.0.0.1', verbose=False):
    """ Run the game.

    Parameters
    ----------
    path: the file of the map (str)

    Version
    -------
    specification: Simon Defrenne (v.1 20/04/18)
    implementation: Simon Defrenne, Marien Dessy, Alexis Losenko (v.1 20-04-18)

    """

    redfleet,bluefleet,asteroids,store,mapsize = game_preparation(path)
    turn_count = 0
    game = True
    no_damage_check = False
    no_damage_count = 0

    connection = connect_to_player(player_id, remote_IP, verbose)

    while game:
        redfleet_health_data = {}
        for ship in redfleet:
            redfleet_health_data[ship] = redfleet[ship]["health"]
        bluefleet_health_data = {}
        for ship in bluefleet:
            bluefleet_health_data[ship] = bluefleet[ship]["health"]

        if player_id == 2:
            player_red = IA_complete(redfleet,bluefleet,asteroids,store,mapsize)
            notify_remote_orders(connection,player_red)
            player_blue = get_remote_orders(connection)
        elif player_id == 1:
            player_blue = IA_complete(bluefleet,redfleet,asteroids,store,mapsize)
            player_red = get_remote_orders(connection)
            notify_remote_orders(connection,player_blue)

        redfleet, bluefleet, asteroids = turn(player_red, player_blue, redfleet, bluefleet, store, asteroids,mapsize)

        turn_count += 1
        
        show_game(redfleet, bluefleet, asteroids, mapsize, store)
        
        # check if something has been damaged

        for ship in redfleet:
            if ship in redfleet_health_data:
                if redfleet_health_data[ship] != redfleet[ship]["health"]:
                    no_damage_check = True

        for ship in bluefleet:
            if ship in bluefleet_health_data:
                if bluefleet_health_data[ship] != bluefleet[ship]["health"]:
                    no_damage_check = True

        if no_damage_check:
            no_damage_count += 1
        else:
            no_damage_count = 0
            
        # win condition check
        
        if not "portal" in redfleet:
            game = False
            print("Red player wins.")
            disconnect_from_player(connection)
        elif not "portal" in bluefleet:
            print("Blue player wins.")
            game = False
            disconnect_from_player(connection)
        elif no_damage_count >= 200:
            if redfleet["portal"]["health"] > bluefleet["portal"]["health"]:
                print("Red player wins.")
            elif redfleet["portal"]["health"] < bluefleet["portal"]["health"]:
                print("Blue player wins.")
            else:
                if redfleet["portal"]["score"] > bluefleet["portal"]["score"]:
                    print("Red player wins.")
                elif redfleet["portal"]["score"] < bluefleet["portal"]["score"]:
                    print("Blue player wins.")
                else:
                    print("DRAW")
            game = False
            disconnect_from_player(connection)

        time.sleep(0.5)

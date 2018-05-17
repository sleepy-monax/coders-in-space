import random

def get_direction(source, destination):
    """Returns delta row/col to reach destination from source.
    
    Parameters
    ----------
    source: source coordinates (tuple)
    destination: destination coordinates (tuple)
    
    """
    
    if destination[0] > source[0]:
        drow = 1
    elif destination[0] < source[0]:
        drow = -1
    else:
        drow = 0
        
    if destination[1] > source[1]:
        dcol = 1
    elif destination[1] < source[1]:
        dcol = -1
    else:
        dcol = 0
    
    return drow, dcol
    
    
def get_AI_actions(game, player_id):
    """Return orders of AI.
    
    Parameters
    ----------
    game: game data structure (dict)
    player_id: player id of AI (int)

    Returns
    -------
    orders: orders of AI (str)
    
    """
    
    orders = ''
    
    # purchase orders
    ore = game['players'][player_id]['ore']
    while ore >= 1:
        ship_type = random.choice(('scout', 'warship', 'excavator-S', 'excavator-M', 'excavator-L'))
#        ship_type = random.choice(('excavator-S', 'excavator-M', 'excavator-L'))
        ship_name = str(random.randint(100, 999))
        ship_cost = game['specs'][ship_type]['cost']
        
        if ship_cost <= ore and ship_name not in game['ships'][player_id] :
            orders += '%s:%s ' % (ship_name, ship_type)
            ore -= ship_cost
    
    # ship orders
    for ship_name in game['ships'][player_id]:
        ship = game['ships'][player_id][ship_name]
        if ship['type'] in ('excavator-S', 'excavator-M', 'excavator-L'):
            # lock/release orders
            if ship['status'] == 'released' and ship['pos'] == game['portals'][player_id]['pos'] and ship['ore'] > 0:
                # lock portal
                orders += '%s:lock ' % ship_name
            elif ship['status'] == 'locked' and ship['pos'] == game['portals'][player_id]['pos'] and ship['ore'] == 0:
                # release portal
                orders += '%s:release ' % ship_name
            elif ship['status'] == 'released' and ship['pos'] in game['asteroids'] and game['asteroids'][ship['pos']]['ore'] > 0 and ship['ore'] < ship['tonnage']:
                # lock asteroid
                orders += '%s:lock ' % ship_name
            elif ship['status'] == 'locked' and ship['pos'] in game['asteroids'] and (game['asteroids'][ship['pos']]['ore'] == 0 or ship['ore'] == ship['tonnage']):
                # release asteroid
                orders += '%s:release ' % ship_name
            elif ship['status'] == 'released' and ship['ore'] < ship['tonnage']:
                # search for asteroids
                best_target = None
                best_distance = 2*(game['nb_rows']+game['nb_cols'])
                for target in game['asteroids']:
                    if game['asteroids'][target]['ore'] > 0:
                        distance = abs(target[0]-ship['pos'][0]) + abs(target[1]-ship['pos'][1])
                        if distance < best_distance:
                            best_target = target
                            best_distance = distance
                
                if best_target != None:
                    drow, dcol = get_direction(ship['pos'], best_target)                   
                    orders += '%s:@%d-%d ' % (ship_name, ship['pos'][0]+drow, ship['pos'][1]+dcol)
                else:
                    # go home (no more asteroids to mine)
                    if ship['pos'] != game['portals'][player_id]['pos']:
                        drow, dcol = get_direction(ship['pos'], game['portals'][player_id]['pos'])  
                        orders += '%s:@%d-%d ' % (ship_name, ship['pos'][0]+drow, ship['pos'][1]+dcol)
            elif ship['status'] == 'released' and ship['ore'] == ship['tonnage']:
                # search for portal               
                drow, dcol = get_direction(ship['pos'], game['portals'][player_id]['pos'])  
                orders += '%s:@%d-%d ' % (ship_name, ship['pos'][0]+drow, ship['pos'][1]+dcol)
                
        else:
            # search for fight location
            target = None
            
            portal = game['portals'][3-player_id]
            for drow in (-2, -1, 0, 1, 2):
                for dcol in (-2, -1, 0, 1, 2):
                    if abs(portal['pos'][0]+drow-ship['pos'][0]) + abs(portal['pos'][1]+dcol-ship['pos'][1]) <= ship['range']:
                        target = (portal['pos'][0]+drow, portal['pos'][1]+dcol)
                        
            for foe_name in game['ships'][3-player_id]:
                foe = game['ships'][3-player_id][foe_name]
                
                for (drow, dcol) in foe['mask']:
                    if abs(foe['pos'][0]+drow-ship['pos'][0]) + abs(foe['pos'][1]+dcol-ship['pos'][1]) <= ship['range']:
                        target = (foe['pos'][0]+drow, foe['pos'][1]+dcol)

            if target != None:
                orders += '%s:*%d-%d ' % (ship_name, target[0], target[1])
            else:
                # search for move location
                portal = game['portals'][3-player_id]
                
                best_target = portal['pos']
                best_distance = abs(portal['pos'][0]-ship['pos'][0]) + abs(portal['pos'][1]-ship['pos'][1])
                
                for foe_name in game['ships'][3-player_id]:
                    foe = game['ships'][3-player_id][foe_name]
                    
                    distance = abs(foe['pos'][0]-ship['pos'][0]) + abs(foe['pos'][1]-ship['pos'][1])
                    if distance < best_distance:
                        best_target = foe['pos']
                        best_distance = distance
                
                drow, dcol = get_direction(ship['pos'], best_target)                   
                orders += '%s:@%d-%d ' % (ship_name, ship['pos'][0]+drow, ship['pos'][1]+dcol)
            
    return orders[:-1]

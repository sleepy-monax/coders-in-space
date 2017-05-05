import random

def get_AI_purchase(game, player_id):
    """Return purchase order of AI.
    
    Parameters
    ----------
    game: game data structure (dict)
    player_id: player id of AI (int)

    Returns
    -------
    orders: purchase order of AI (str)
    
    """
    
    return 'ad:fighter ju:destroyer nes:destroyer moua:battlecruiser'


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
    
    if player_id == 1:
        for ship_name in game['ships'][player_id]:
            order_id = random.randint(1, 4)
            
            if order_id == 1:
                orders += '%s:slower' % ship_name
            elif order_id == 2:
                orders += '%s:faster' % ship_name
            elif order_id == 3:
                orders += '%s:left' % ship_name
            else:
                orders += '%s:right' % ship_name
            
            orders += ' '
    else:
        for ship_name in game['ships'][2]:
            pos_s = game['ships'][2][ship_name]['pos']
            
            best_target_pos = None
            best_distance = game['nb_rows'] + game['nb_cols']
            for target_name in game['ships'][1]:
                pos_t = game['ships'][1][target_name]['pos']
                dr = abs(pos_t[0]-pos_s[0])
                dc = abs(pos_t[1]-pos_s[1])
                
                distance = min(dr, game['nb_rows']-dr) + min(dc, game['nb_cols']-dc) 
                if distance <= game['ships'][2][ship_name]['range'] and distance < best_distance:
                    best_target_pos = pos_t
                    best_distance = distance
            
            if best_target_pos != None:
                orders += '%s:%d-%d' % (ship_name, best_target_pos[0]+1, best_target_pos[1]+1)
            else:
                order_id = random.randint(1, 4)
            
                if order_id == 1:
                    orders += '%s:slower' % ship_name
                elif order_id == 2:
                    orders += '%s:faster' % ship_name
                elif order_id == 3:
                    orders += '%s:left' % ship_name
                else:
                    orders += '%s:right' % ship_name
                
            orders += ' '
                
    return orders[:-1]

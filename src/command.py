def parse_command(command, game_stats):
    """
    Parse a command from a player and run it.

    Parameters
    ----------
    command : command from the player (str).
    game_stats : stat of the game (dic).

    Return
    ------
    new_game_stats : game stat after the command execution (dic).
    """
    raise NotImplementedError

def command_change_speed(ship, change, game_stats):
    """
    Increase the speed of a ship.

    Parameters
    ----------
    ship : name of the ship to Increase the speed (str).
    change : the way to change the speed <"slower"|"faster"> (str).
    game_stats : stats of the game (dic).

    Returns
    -------
    game_stats : the game after the command execution (dic)
    """
    type= gamestats['ship'][ship]['type']
    if change == 'faster' and gamestats['ship'][ship]['speed'] < gamestats['model_ship'][type]['max_speed']:
        gamestats['ship'][ship]['speed']+=1
    elif change == 'slower' and gamestats['ship'][ship]['speed'] > 0:
        gamestats['ship'][ship]['speed']-=1
    else:
        print 'you cannot make that change on the speed of this ship'
    return gamestats

def command_rotate(ship, direction, game_stats):
    """
    Rotate the ship.

    Parameters
    ----------
    ship : name of the ship to Increase the speed.
    direction : the direction to rotate the ship <"left"|"right">(str)
    game_stats : stats of the game (dic).

    Returns
    -------
    new_game_stats : the game after the command execution.
    """
    raise NotImplementedError

def command_attack(ship, coordinate, game_stats):
    """
    Rotate the ship.

    Parameters
    ----------
    ship : name of the ship to Increase the speed.
    coordinate : coordinate of the tile to attack (tuple(int,int)).
    game_stats : stats of the game (dic).

    Returns
    -------
    new_game_stats : the game after the command execution.
    """
    raise NotImplementedError

import string

def new_game(path):
    """
    Create a new game from a '.cis' file.

    Parameters
    ----------
    path : to the cis file (str).

    Return
    -------
    game_stats : new game stats (dic).
    """
    raise NotImplementedError
	

def parse_game_file(path):
    """
    Parse a cis file give us his content.

    Parameter
    ---------
    path : path of the cis file (str).

    Return
    ------
    parsed_data : data containe in the cis file (dic).

    Version
    -------
    specification : Nicolas Van Bossuyt (v1. 09/02/2017)
    implementation : Nicolas Van Bossuyt (v1. 09/02/2017)
    """

    # Split file lines and remove '\n' chars.
    with file(path,'r') as f:
        file_content = [i.strip() for i in f]

    # Get the size of the gameboard.
    size_str = file_content[0].split(' ')
    size = (int(size_str[0]),int(size_str[1]))

    # Get lost space ship in the new game.
    ships_list = []
    for i in range(len(file_content)):
        ship_str = file_content[i].split(' ')
        ship = (int(ship_str[0]), int(ship_str[1]), ship_str[2])
        ships_list.append(ship)

    # Create parsed data dictionary and return it.
    parsed_data = {'size':size,'ships':ships_list}
    return parsed_data

def play_game():
    """
    Main game function thats run the game loop.
    """
    raise NotImplementedError

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
    new_game_stats : the game after the command execution (dic).
    """
    raise NotImplementedError

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

def show_board(game_stats):
    """
    Show the game to the user screen.

    Parameter
    ---------
    game_stats : game to show on screen (dic).
    """
    raise NotImplementedError

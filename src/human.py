from gui import *

def get_human_input(player_name, buy_ship, game_stats):
    """
    Get input from a human player.

    Parameters
    ----------
    player_name : Name of the player to get input from (str).
    buy_ship : the player need to buy a ship (str).
    game_stats : stats of the game (dic).

    Returns
    -------
    player_input : input from the player (str).
    """

    # Show header.
    c = create_canvas(190, 1)
    put_box(c, 0, 0, 190, 3)
    put_string(c, 3, 0, '| It\'s %s\'s turn |' % player_name)
    print_canvas(c)

def move_away(game_data, ship, coords):
def move_to(game_data, ship, coords):
    """
    Move a ship to a specified location.

    Parameters
    ----------
    game_data: data of the game (dic).
    """
def make_something_random(game_data, ship, actions):
    """
    Do a random actions.

    Parameters
    ----------
    game_data: data of the game (dic).
    ship: ship that make a random thing (str).
    actions: list of allowed action(list(str)).

    Return
    ------
    action: the randomly generated action (str).
    """
    pass

def nearest_ship(game_data, coords, ship_type, ship_owner, max_search_range):
    """
    Get the nearest ship of a specified type and owner.

    Parameters
    ----------
    game_data: data of the game (dic).
    coords: center of the search range (tuple(int, int)).
    ship_type: type of the ship to search (str). ("all" if you whant all ship)
    ship_owner: owner of the ship to find (str). ("all" if you whant all ship)

    Return
    ------
    finded_ships: list of ship finded (list(str)).
    """
    pass

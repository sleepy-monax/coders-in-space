# -*- coding: utf-8 -*-
from neural import *
from coders_in_space import *
import random
import os

def ai_learn(max_gen, random_strength):
    """
    Learn the ai to play Coders In Space.

    Parameters
    ----------
    max_gen : maximue number of generation (int).
    random_strength : strength of mutation (int).

    Return
    ------
    The Best ever ai to playe Codes in Space.
    """

    ai_players = {}
    dumb_ai = []
    best_ai = -1
    best_ai_score = 0

    for gen in range(max_gen):
        print '-' * 10
        print 'Gen :' + str(gen)
        print '-' * 10

        # Create neural network.
        for ai_id in range(10):
            ai_path = 'neural/' + str(ai_id) + '_bot.mind'
            if gen == 0:
                ai_players[ai_id] = {'nb_win' : 0}
                save_network(create_network((53, 300, 7 + 16)), ai_path)

            else:
                if ai_id in ai_players.keys():
                    # Creat a mutated baby AI... So cute (^ω^).
                    baby_ai = randomize_network(load_network(ai_path), random_strength)
                    baby_ai_id = dumb_ai[0]
                    dumb_ai = dumb_ai[1:]
                    save_network(baby_ai, 'neural/' + str(baby_ai_id) + '_bot.mind')
                    ai_players[baby_ai_id] = {'nb_win' : 0}

        # We make a tournament between AI and keep the winner.
        for ai_id in ai_players:
            for ennemy_ai_id in ai_players:
                print '%d vs %d' % (ai_id, ennemy_ai_id)
                if not ai_id == ennemy_ai_id:
                    winners = play_game('board/test_board.cis', (str(ai_id) + '_bot', str(ennemy_ai_id) + '_bot'),no_splash = True, no_gui = False)
                    for winner in winners:
                        winner_id = int(winner.split('_')[0])
                        ai_players[winner_id]['nb_win'] += 1

                        if ai_players[winner_id]['nb_win'] > best_ai_score:
                            best_ai_score = ai_players[winner_id]['nb_win']
                            best_ai = winner

        # Kill dumbes AI.
        max_kill = 25
        for ai_id in ai_players:
            if ai_id == best_ai:
                # Keep it safe :)
                pass

            else:
                if max_kill != 0 and random.randint(0, 2) >= 2:
                    # You kill it :).
                    del ai_players[ai_id]
                    os.remove('neural/' + str(ai_id) + '_bot.mind')
                    dumb_ai.append(ai_id)

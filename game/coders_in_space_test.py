from coders_in_space import *

def game_test():
	try:
		play_game('board/test_board.cis', ('bob_bot', 'john_bot'), no_splash = True)
		assert True
	except Exception as e:
		raise
		assert False

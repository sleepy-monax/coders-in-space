import pytest
import codeinspace
import os

def test_parse_game_file():
    try:
        codeinspace.parse_game_file('board/test0.cis')
        assert True
    except Exception as e:
        raise
        assert False
        
def test_new_game():
    try:
        codeinspace.new_game('board/test0.cis', ('Vador','ai'))
        assert True
    except Exception as e:
        assert False

def test_show_board():
    try:
        codeinspace.show_board(codeinspace.new_game('board/test0.cis', ('Vador', 'ai')))
        assert True
    except Exception as e:
        raise
        assert False

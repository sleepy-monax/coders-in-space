import pytest
import codeinspace

def test_new_game():
    try:
        codeinspace.new_game('board\test0.py', ('Vador','ai'))
        assert True
    except Exception as e:
        assert False

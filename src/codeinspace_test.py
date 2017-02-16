import pytest
import codeinspace
import os

def test_new_game():
    print os.getcwd()


    try:
        codeinspace.new_game('board/test0.cis', ('Vador','ai'))
        assert True
    except Exception as e:
        print e
        assert False

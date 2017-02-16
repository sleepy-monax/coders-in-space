import pytest
import gui

def test_creat_canvas():

    for x in [1, 2, 4, 8, 16, 20, 40, 60]:
            gui.creat_canvas(x, x, True)

    assert True

def test_put():
    c = gui.creat_canvas(50, 50, True)

    gui.put_box(c, 0, 0, 50, 50)
    gui.put_rectangle(c, 0, 0, 25, 25, 'A')
    gui.put_ascii_art(c, 0, 0, 'alien')
    gui.put_string(c, 0, 0, 'hello world !')

    gui.print_canvas(c)

    assert True

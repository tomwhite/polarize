import numpy as np

from polarize.model import Domino, DominoOrientation, PolarizingFilter, ALL_DOMINOS

def test_domino():
    for domino in ALL_DOMINOS:
        print(domino)


def test_board():
    values = np.zeros((4, 4), dtype=np.int8)

    def add_domino(domino, i, j):
        values[i, j] = domino.filter1.value
        if domino.orientation == DominoOrientation.HORIZONTAL:
            values[i + 1, j] = domino.filter2.value
        else:
            values[i, j + 1] = domino.filter2.value

    add_domino(ALL_DOMINOS[4], 1, 1)
    add_domino(ALL_DOMINOS[5], 2, 2)
    print(values)

    print(np.bitwise_or.reduce(values, axis=0) == 3)
    print(np.bitwise_or.reduce(values, axis=1) == 3)


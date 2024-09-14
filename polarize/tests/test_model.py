import numpy as np

from polarize.model import Board, Domino, DominoOrientation, PlacedDomino, PolarizingFilter, ALL_DOMINOES

def test_domino():
    for domino in ALL_DOMINOES:
        print(domino)


def test_board():
    board = Board(
        PlacedDomino(ALL_DOMINOES[4], 1, 1),
        PlacedDomino(ALL_DOMINOES[5], 2, 2),
    )
    print(board)

    print(np.bitwise_or.reduce(board.values, axis=1) == 3)
    print(np.bitwise_or.reduce(board.values, axis=0) == 3)


import numpy as np
from numpy.testing import assert_array_equal
from rich.console import Console

from polarize.model import Board, PlacedDomino, ALL_DOMINOES


def test_all_dominoes():
    assert len(ALL_DOMINOES) == 8


def test_add_domino():
    board = Board()

    d1 = PlacedDomino(ALL_DOMINOES[4], 0, 2)
    d2 = PlacedDomino(ALL_DOMINOES[5], 2, 2)

    assert board.can_add(d1)
    assert board.can_add(d2)
    board.add_domino(d1)
    assert not board.can_add(d1)
    assert board.can_add(d2)
    board.add_domino(d2)
    assert not board.can_add(d1)
    assert not board.can_add(d2)


def test_board_to_puzzle():
    board = Board(
        PlacedDomino(ALL_DOMINOES[4], 0, 2),
        PlacedDomino(ALL_DOMINOES[5], 2, 2),
    )

    assert_array_equal(board.values, np.array(
        [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [2, 1, 2, 0],
            [0, 0, 1, 0,]
        ]
    ))
    assert board.lights() == 0b00100010


    puzzle = board.to_puzzle()

    assert puzzle.lights == board.lights()
    assert puzzle.dominoes == [ALL_DOMINOES[4], ALL_DOMINOES[5]]

    # print the puzzle
    console = Console()
    console.print(puzzle)

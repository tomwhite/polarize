import numpy as np
from numpy.testing import assert_array_equal
from rich.console import Console

from polarize.model import Board, PlacedDomino, ALL_DOMINOES


def test_all_dominoes():
    assert len(ALL_DOMINOES) == 8


def test_add_domino():
    board = Board()

    d1 = PlacedDomino(ALL_DOMINOES[2], 0, 2)
    d2 = PlacedDomino(ALL_DOMINOES[6], 2, 2)

    assert board.can_add(d1)
    assert not board.can_remove(d1)
    assert board.can_add(d2)
    assert not board.can_remove(d2)

    board.add_domino(d1)
    assert not board.can_add(d1)
    assert board.can_remove(d1)
    assert board.can_add(d2)
    assert not board.can_remove(d2)

    board.add_domino(d2)
    assert not board.can_add(d1)
    assert board.can_remove(d1)
    assert not board.can_add(d2)
    assert board.can_remove(d2)

    board.remove_domino(d2)
    assert not board.can_add(d1)
    assert board.can_remove(d1)
    assert board.can_add(d2)
    assert not board.can_remove(d2)

    board.remove_domino(d1)
    assert board.can_add(d1)
    assert not board.can_remove(d1)
    assert board.can_add(d2)
    assert not board.can_remove(d2)


def test_board_to_puzzle():
    board = Board()
    board.add_domino(PlacedDomino(ALL_DOMINOES[2], 0, 2))
    board.add_domino(PlacedDomino(ALL_DOMINOES[6], 2, 2))

    assert_array_equal(
        board.values,
        np.array(
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [2, 1, 2, 0],
                [0, 0, 1, 0],
            ]
        ),
    )
    assert_array_equal(board.lights, [0, 0, 2, 1, 1, 1, 2, 0])
    assert board.lights_int == 0b0000_1001_0101_1000

    assert_array_equal(
        board.paths_horizontal,
        [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 2, 2, 2],
            [0, 0, 0, 1, 1],
        ],
    )
    assert_array_equal(
        board.paths_vertical,
        [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [1, 1, 1, 0], [1, 1, 2, 0]],
    )

    puzzle = board.to_puzzle()

    assert_array_equal(puzzle.lights, board.lights)
    assert puzzle.lights_int == board.lights_int
    assert puzzle.dominoes == [ALL_DOMINOES[2], ALL_DOMINOES[6]]

    # print the puzzle
    console = Console()
    console.print(puzzle)


def test_board_to_puzzle_size_3():
    board = Board(n=3)
    board.add_domino(PlacedDomino(ALL_DOMINOES[4], 1, 0))
    board.add_domino(PlacedDomino(ALL_DOMINOES[1], 0, 2))

    # fmt: off
    assert_array_equal(
        board.values,
        np.array(
            [
                [0, 1, 0],
                [0, 1, 0],
                [1, 2, 0],
            ]
        ),
    )
    # fmt: on
    assert_array_equal(board.lights, [1, 1, 2, 1, 2, 0])
    assert board.lights_int == 0b0101_1001_1000

    puzzle = board.to_puzzle()

    assert_array_equal(puzzle.lights, board.lights)
    assert puzzle.lights_int == board.lights_int
    assert puzzle.dominoes == [ALL_DOMINOES[4], ALL_DOMINOES[1]]

    # print the puzzle
    console = Console()
    console.print(puzzle)

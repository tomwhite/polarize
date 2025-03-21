import numpy as np
from numpy.testing import assert_array_equal
import pytest
from rich.console import Console

from polarize.model import (
    Board,
    Filter,
    Orientation,
    PlacedDomino,
    Puzzle,
    ALL_DOMINOES,
)


@pytest.fixture
def board():
    # set on 21 Mar 2025
    puzzle = Puzzle.from_json_str(
        """{"n": 4, "lights": [2, 2, 1, 2, 2, 2, 0, 1], "dominoes": [7, 1, 0, 4], "initial_placed_dominoes": [{"domino": 7, "i": 0, "j": 0}, {"domino": 4, "i": 1, "j": 0}, {"domino": 0, "i": 2, "j": 1}, {"domino": 1, "i": 2, "j": 0}], "solution": {"values": [[2, 0, 0, 1], [2, 0, 0, 1], [1, 1, 0, 0], [1, 2, 0, 0]], "placed_dominoes": [{"domino": 7, "i": 0, "j": 0}, {"domino": 1, "i": 0, "j": 3}, {"domino": 0, "i": 0, "j": 2}, {"domino": 4, "i": 3, "j": 0}]}}"""
    )
    return puzzle.solution


def test_filter():
    assert Filter.POS_45.value == 1
    assert Filter.NEG_45.value == 2
    assert Filter.POS_45 < Filter.NEG_45


def test_orientation():
    assert Orientation.H.value == 1
    assert Orientation.V.value == 2
    assert Orientation.H < Orientation.V


def test_all_dominoes():
    assert len(ALL_DOMINOES) == 8
    for i in range(len(ALL_DOMINOES) - 1):
        assert ALL_DOMINOES[i] < ALL_DOMINOES[i + 1]


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


def test_reflect_vertically(board):
    boardTransformed = board.reflect_vertically()

    # constructed using trial and error (and `console.print(boardTransformed)`)
    boardTransformed_expected = Board()
    boardTransformed_expected.add_domino(PlacedDomino(ALL_DOMINOES[2], 0, 0))
    boardTransformed_expected.add_domino(PlacedDomino(ALL_DOMINOES[3], 0, 1))
    boardTransformed_expected.add_domino(PlacedDomino(ALL_DOMINOES[4], 0, 2))
    boardTransformed_expected.add_domino(PlacedDomino(ALL_DOMINOES[7], 3, 2))

    assert boardTransformed == boardTransformed_expected


def test_transpose(board):
    boardT = board.transpose()

    # constructed using trial and error (and `console.print(boardT)`)
    boardT_expected = Board()
    boardT_expected.add_domino(PlacedDomino(ALL_DOMINOES[3], 0, 0))
    boardT_expected.add_domino(PlacedDomino(ALL_DOMINOES[4], 2, 0))
    boardT_expected.add_domino(PlacedDomino(ALL_DOMINOES[0], 0, 3))
    boardT_expected.add_domino(PlacedDomino(ALL_DOMINOES[5], 3, 0))

    assert boardT == boardT_expected


def test_transforms(board):
    for i, boardTransformed in enumerate(board.transforms()):
        if i == 0:
            assert board == boardTransformed
        else:
            assert not np.array_equal(board.values, boardTransformed.values)
            assert board.placed_dominoes != boardTransformed.placed_dominoes


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
    assert len(puzzle.dominoes) == len(board.placed_dominoes)
    assert set(puzzle.dominoes) == set([ALL_DOMINOES[2], ALL_DOMINOES[6]])

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
    assert len(puzzle.dominoes) == len(board.placed_dominoes)
    assert set(puzzle.dominoes) == set([ALL_DOMINOES[4], ALL_DOMINOES[1]])

    # print the puzzle
    console = Console()
    console.print(puzzle)

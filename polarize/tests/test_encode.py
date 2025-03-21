from itertools import combinations_with_replacement

import numpy as np
import pytest
from numpy.testing import assert_array_equal

from polarize.encode import (
    all_boards,
    canonicalize_board,
    decode_board,
    encode_board,
    encode_dominoes_from_ints,
    encode_lights,
    reflect_horizontally,
    reflect_vertically,
    transpose,
    transforms,
)
from polarize.generate import all_boards_with_dominoes
from polarize.model import ALL_DOMINOES, Puzzle


@pytest.fixture
def board():
    # set on 21 Mar 2025
    puzzle = Puzzle.from_json_str(
        """{"n": 4, "lights": [2, 2, 1, 2, 2, 2, 0, 1], "dominoes": [7, 1, 0, 4], "initial_placed_dominoes": [{"domino": 7, "i": 0, "j": 0}, {"domino": 4, "i": 1, "j": 0}, {"domino": 0, "i": 2, "j": 1}, {"domino": 1, "i": 2, "j": 0}], "solution": {"values": [[2, 0, 0, 1], [2, 0, 0, 1], [1, 1, 0, 0], [1, 2, 0, 0]], "placed_dominoes": [{"domino": 7, "i": 0, "j": 0}, {"domino": 1, "i": 0, "j": 3}, {"domino": 0, "i": 0, "j": 2}, {"domino": 4, "i": 3, "j": 0}]}}"""
    )
    return puzzle.solution


def test_encode_decode_board(board):
    assert_array_equal(
        board.values,
        np.array(
            [
                [2, 0, 0, 1],
                [2, 0, 0, 1],
                [1, 1, 0, 0],
                [1, 2, 0, 0],
            ]
        ),
    )

    val = encode_board(board)
    filters = val >> 32
    orientations = val & 0xFFFFFFFF
    assert filters == 0b_10000001_10000001_01010000_01100000
    assert orientations == 0b_10000010_10000010_01010000_01010000

    decoded_board = decode_board(val)
    assert decoded_board == board


def test_reflect_horizontally(board):
    val = encode_board(board)
    transformed_val = reflect_horizontally(val)
    transformed_board = decode_board(transformed_val)
    assert transformed_board == board.rot90().transpose()


def test_reflect_vertically(board):
    val = encode_board(board)
    transformed_val = reflect_vertically(val)
    transformed_board = decode_board(transformed_val)
    assert transformed_board == board.reflect_vertically()


def test_transpose(board):
    val = encode_board(board)
    transformed_val = transpose(val)
    transformed_board = decode_board(transformed_val)
    assert transformed_board == board.transpose()


def test_transforms(board):
    val = encode_board(board)
    for tb, tv in zip(board.transforms(), transforms(val)):
        assert decode_board(tv) == tb


def test_canonicalize_board(board):
    val = encode_board(board)
    assert canonicalize_board(val) in transforms(val)


def test_all_boards():
    for num_pieces in range(1, 4):
        boards, _, _ = all_boards(num_pieces=num_pieces)

        # check all boards are unique
        assert len(np.unique(boards)) == len(boards)

        # check number of boards tallies with other (slower) way of enumerating them
        boards_check = []
        for dominoes in combinations_with_replacement(ALL_DOMINOES, num_pieces):
            boards_check.extend(all_boards_with_dominoes(n=4, dominoes=dominoes))
        assert len(boards) == len(boards_check)


def test_encode_lights(board):
    board_val = encode_board(board)
    filters = board_val >> 32 & 0xFFFFFFFF
    assert encode_lights(filters) == board.lights_int


def test_encode_dominoes_from_ints(board):
    dominoes = np.array(
        [pd.domino.value for pd in board.placed_dominoes], dtype=np.int8
    )
    assert set(dominoes) == set([0, 1, 4, 7])

    val = encode_dominoes_from_ints(dominoes)
    assert val == 0b_00010001_00000000_00010000_00000001

from itertools import combinations_with_replacement

import numpy as np
import pytest
from numpy.testing import assert_array_equal

from polarize.encode import (
    all_boards,
    canonical_boards,
    canonical_puzzles_with_unique_solution,
    canonicalize_board,
    canonicalize_puzzle,
    decode_board,
    decode_dominoes,
    decode_puzzle,
    encode_board,
    encode_dominoes,
    encode_lights_from_filters,
    reflect_dominoes_horizontally,
    reflect_dominoes_vertically,
    reflect_horizontally,
    reflect_lights_horizontally,
    reflect_lights_vertically,
    reflect_vertically,
    transpose,
    transpose_dominoes,
    transpose_lights,
    transforms,
)
from polarize.generate import all_boards_with_dominoes
from polarize.model import ALL_DOMINOES, Board, Puzzle, PlacedDomino
from polarize.solve import has_unique_solution


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
    assert transformed_board == board.reflect_horizontally()


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


def test_canonical_boards():
    boards, _, _ = canonical_boards(num_pieces=1)
    assert len(boards) == 14


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


def test_encode_lights_from_filters(board):
    board_val = encode_board(board)
    filters = board_val >> 32 & 0xFFFFFFFF
    assert encode_lights_from_filters(filters) == board.lights_int


def test_reflect_lights_horizontally(board):
    board_val = encode_board(board)
    filters = board_val >> 32 & 0xFFFFFFFF
    val = encode_lights_from_filters(filters)
    assert reflect_lights_horizontally(val) == encode_lights_from_filters(reflect_horizontally(board_val) >> 32 & 0xFFFFFFFF)


def test_reflect_lights_vertically(board):
    board_val = encode_board(board)
    filters = board_val >> 32 & 0xFFFFFFFF
    val = encode_lights_from_filters(filters)

    assert reflect_lights_vertically(val) == encode_lights_from_filters(reflect_vertically(board_val) >> 32 & 0xFFFFFFFF)


def test_transpose_lights(board):
    board_val = encode_board(board)
    filters = board_val >> 32 & 0xFFFFFFFF
    val = encode_lights_from_filters(filters)

    assert transpose_lights(val) == encode_lights_from_filters(transpose(board_val) >> 32 & 0xFFFFFFFF)


def test_encode_decode_dominoes(board):
    dominoes = np.array(
        [pd.domino.value for pd in board.placed_dominoes], dtype=np.int8
    )
    assert set(dominoes) == set([0, 1, 4, 7])

    val = encode_dominoes(dominoes)
    assert val == 0b_00010001_00000000_00010000_00000001

    dominoes_decoded = decode_dominoes(val)
    assert_array_equal(set(dominoes_decoded), set(dominoes))


def test_reflect_dominoes_horizontally(board):
    dominoes = np.array(
        [pd.domino.value for pd in board.placed_dominoes], dtype=np.int8
    )
    val = encode_dominoes(dominoes)

    dominoes = np.array(
        [pd.domino.value for pd in board.reflect_horizontally().placed_dominoes], dtype=np.int8
    )
    assert reflect_dominoes_horizontally(val) == encode_dominoes(dominoes)


def test_reflect_dominoes_vertically(board):
    dominoes = np.array(
        [pd.domino.value for pd in board.placed_dominoes], dtype=np.int8
    )
    val = encode_dominoes(dominoes)

    dominoes = np.array(
        [pd.domino.value for pd in board.reflect_vertically().placed_dominoes], dtype=np.int8
    )
    assert reflect_dominoes_vertically(val) == encode_dominoes(dominoes)


def test_transpose_dominoes(board):
    dominoes = np.array(
        [pd.domino.value for pd in board.placed_dominoes], dtype=np.int8
    )
    val = encode_dominoes(dominoes)

    dominoes = np.array(
        [pd.domino.value for pd in board.transpose().placed_dominoes], dtype=np.int8
    )
    assert transpose_dominoes(val) == encode_dominoes(dominoes)


def test_canonicalize_puzzle():
    board1 = Board()
    board1.add_domino(PlacedDomino(ALL_DOMINOES[5], 0, 0))
    board1.add_domino(PlacedDomino(ALL_DOMINOES[6], 1, 0))

    board2 = Board()
    board2.add_domino(PlacedDomino(ALL_DOMINOES[2], 0, 0))
    board2.add_domino(PlacedDomino(ALL_DOMINOES[1], 0, 1))

    # the boards are distinct...
    board1_val = encode_board(board1)
    board2_val = encode_board(board2)
    canonical_board1_val = canonicalize_board(board1_val)
    canonical_board2_val = canonicalize_board(board2_val)
    assert canonical_board1_val != canonical_board2_val

    # ... but the puzzles resulting from them are not
    filters1 = board1_val >> 32 & 0xFFFFFFFF
    lights1_val = encode_lights_from_filters(filters1)
    dominoes1 = np.array(
        [pd.domino.value for pd in board1.placed_dominoes], dtype=np.int8
    )
    dominoes1_val = encode_dominoes(dominoes1)

    filters2 = board2_val >> 32 & 0xFFFFFFFF
    lights2_val = encode_lights_from_filters(filters2)
    dominoes2 = np.array(
        [pd.domino.value for pd in board2.placed_dominoes], dtype=np.int8
    )
    dominoes2_val = encode_dominoes(dominoes2)

    # and the dominoes are too...
    assert dominoes1_val != dominoes2_val

    # ... but the puzzles resulting from them are not
    # (in other words, the puzzle doesn't have a unique solution)
    assert canonicalize_puzzle(lights1_val, dominoes1_val) == canonicalize_puzzle(lights2_val, dominoes2_val)


def test_canonical_puzzles_with_unique_solution():
    canonical_lights, canonical_dominoes = canonical_puzzles_with_unique_solution(
        num_pieces=1
    )
    assert len(canonical_lights) == len(canonical_dominoes)
    assert len(canonical_lights) == 14

    # check the puzzles all have a unique solution
    for i in range(len(canonical_lights)):
        puzzle = decode_puzzle(canonical_lights[i], canonical_dominoes[i])
        assert has_unique_solution(puzzle)

    canonical_lights, canonical_dominoes = canonical_puzzles_with_unique_solution(
        num_pieces=2
    )
    assert len(canonical_lights) == len(canonical_dominoes)
    assert len(canonical_lights) == 238  # TODO: can we check this?

    # check the puzzles all have a unique solution
    for i in range(len(canonical_lights)):
        puzzle = decode_puzzle(canonical_lights[i], canonical_dominoes[i])
        assert has_unique_solution(puzzle)

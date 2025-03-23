import itertools

import numba as nb
import numpy as np
import pandas as pd

from polarize.model import (
    ALL_DOMINOES,
    Board,
    Domino,
    Filter,
    Orientation,
    PlacedDomino,
    Puzzle,
    decode_lights,
)
from polarize.util import cproduct_idx


def _encode_bit_pairs(values):
    shift = 15 * 2
    val = 0
    # cast to int64 so that val has same type
    value_ints = values.astype(np.uint64)
    for i in range(4):
        for j in range(4):
            val |= value_ints[i, j] << shift
            shift -= 2
    return val


def _decode_bit_pairs(val):
    shift = 15 * 2
    values = np.zeros((4, 4), dtype=np.int8)
    for i in range(4):
        for j in range(4):
            values[i, j] = val >> shift & 0b11
            shift -= 2
    return values


def encode_board(board):
    """Encode a board as an unsigned 64-bit int by packing bits.

    The first 32 bits represents the filters on the board, the second 32 bits the orientation of the dominoes.
    Together, the two provide enough information to reconstruct the placed dominoes on the board.
    """
    assert board.n == 4
    return (_encode_bit_pairs(board.values) << 32) | _encode_bit_pairs(
        board.orientations
    )


def decode_board(val):
    """Decode an unsigned 64-bit int representing filters and domino orientations
    to a board by unpacking bits."""
    filters = _decode_bit_pairs(val >> 32)
    orientations = _decode_bit_pairs(val & 0xFFFFFFFF)

    # find placed dominoes from values and orientations
    placed_dominoes = set()
    scanned = np.zeros(
        (4, 4), dtype=np.int8
    )  # keep a list of positions that have been dealt with
    for y in range(4):
        for x in range(4):
            orient = orientations[y, x]
            if orientations[y, x] != 0 and scanned[y, x] == 0:
                orient = Orientation(orientations[y, x])
                if orient == Orientation.H:
                    domino = Domino(
                        orient, Filter(filters[y, x]), Filter(filters[y, x + 1])
                    )
                else:
                    domino = Domino(
                        orient, Filter(filters[y, x]), Filter(filters[y + 1, x])
                    )
                pd = PlacedDomino(domino, x, y)
                scanned[pd.np_index] = 1
                placed_dominoes.add(pd)

    return Board(values=filters, placed_dominoes=placed_dominoes)


def decode_puzzle(lights_val, dominoes_val):
    lights = decode_lights(lights_val)
    dominoes = [ALL_DOMINOES[d] for d in decode_dominoes(dominoes_val)]
    return Puzzle(4, lights, dominoes, initial_placed_dominoes=None)


@nb.njit(nb.uint64(nb.uint64), cache=True)
def reflect_horizontally(val):
    """Reflect the encoded board horizontally"""

    # Note that we reflect each bit, not a pair of bits,
    # since each filter is reflected too:
    #
    # / = 0b01 -> \ = 0b10
    # \ = 0b10 -> / = 0b01

    v = val >> 32

    c1 = v & 0b_10000000_10000000_10000000_10000000
    c2 = v & 0b_01000000_01000000_01000000_01000000
    c3 = v & 0b_00100000_00100000_00100000_00100000
    c4 = v & 0b_00010000_00010000_00010000_00010000
    c5 = v & 0b_00001000_00001000_00001000_00001000
    c6 = v & 0b_00000100_00000100_00000100_00000100
    c7 = v & 0b_00000010_00000010_00000010_00000010
    c8 = v & 0b_00000001_00000001_00000001_00000001

    filters = (
        (c1 >> 7)
        | (c2 >> 5)
        | (c3 >> 3)
        | (c4 >> 1)
        | (c5 << 1)
        | (c6 << 3)
        | (c7 << 5)
        | (c8 << 7)
    )

    # We reflect each pair of bits since orientations do not change

    v = val & 0xFFFFFFFF

    c12 = v & 0b_11000000_11000000_11000000_11000000
    c34 = v & 0b_00110000_00110000_00110000_00110000
    c56 = v & 0b_00001100_00001100_00001100_00001100
    c78 = v & 0b_00000011_00000011_00000011_00000011

    orientations = (c12 >> 6) | (c34 >> 2) | (c56 << 2) | (c78 << 6)

    return (filters << 32) | orientations


@nb.njit(nb.uint64(nb.uint64), cache=True)
def reflect_vertically(val):
    """Reflect the encoded board vertically"""

    # pieces are reflected like in reflect_horizontally

    v = val >> 32

    r1 = v & 0b_10101010_00000000_00000000_00000000
    r2 = v & 0b_01010101_00000000_00000000_00000000
    r3 = v & 0b_00000000_10101010_00000000_00000000
    r4 = v & 0b_00000000_01010101_00000000_00000000
    r5 = v & 0b_00000000_00000000_10101010_00000000
    r6 = v & 0b_00000000_00000000_01010101_00000000
    r7 = v & 0b_00000000_00000000_00000000_10101010
    r8 = v & 0b_00000000_00000000_00000000_01010101

    filters = (
        (r1 >> 25)
        | (r2 >> 23)
        | (r3 >> 9)
        | (r4 >> 7)
        | (r5 << 7)
        | (r6 << 9)
        | (r7 << 23)
        | (r8 << 25)
    )

    # We reflect each pair of bits since orientations do not change

    v = val & 0xFFFFFFFF

    r1 = v & 0b_11111111_00000000_00000000_00000000
    r2 = v & 0b_00000000_11111111_00000000_00000000
    r3 = v & 0b_00000000_00000000_11111111_00000000
    r4 = v & 0b_00000000_00000000_00000000_11111111

    orientations = (r1 >> 24) | (r2 >> 8) | (r3 << 8) | (r4 << 24)

    return (filters << 32) | orientations


@nb.njit(nb.uint32(nb.uint32), cache=True)
def _transpose_values(val):
    """Reflect the encoded board values in y=x"""

    # pieces are *not* reflected

    # Based on https://github.com/jdleesmiller/twenty48/blob/479f646e81c38f1967e4fc5942617f9650d2c735/ext/twenty48/state.hpp#L191-L198

    # First move cells as follows (D = leave, L = 3 left, R = 3 right)
    #
    # [D R D R]
    # [L D L D]
    # [D R D R]
    # [L D L D]
    #
    # Consider the following example, where numbers are cell labels (not values in the array):
    #
    # [ 0  1  2  3]      [ 0  4  2  6]
    # [ 4  5  6  7]  ->  [ 1  5  3  7]
    # [ 8  9 10 11]      [ 8 12 10 14]
    # [12 13 14 15]      [ 9 13 11 15]

    a1 = val & 0b_11001100_00110011_11001100_00110011  # diagonal
    a2 = val & 0b_00000000_11001100_00000000_11001100  # move 3 left
    a3 = val & 0b_00110011_00000000_00110011_00000000  # move 3 right
    a = a1 | (a2 << 6) | (a3 >> 6)

    # Then move cells as follows (D = leave, L = 6 left, R = 6 right)
    #
    # [D D R R]
    # [D D R R]
    # [L L D D]
    # [L L D D]
    #
    # Continuing the example:
    #
    # [ 0  4  2  6]      [ 0  4  8 12]
    # [ 1  5  3  7]  ->  [ 1  5  9 13]
    # [ 8 12 10 14]      [ 2  6 10 14]
    # [ 9 13 11 15]      [ 3  7 11 15]
    #
    # which is the transposed array.

    b1 = a & 0b_11110000_11110000_00001111_00001111  # diagonal
    b2 = a & 0b_00000000_00000000_11110000_11110000  # move 6 left
    b3 = a & 0b_00001111_00001111_00000000_00000000  # move 6 right

    return b1 | (b2 << 12) | (b3 >> 12)


@nb.njit(nb.uint64(nb.uint64), cache=True)
def transpose(val):
    """Reflect the encoded board in y=x"""

    v = val >> 32
    filters = _transpose_values(v)

    # Orientations are reflected, which we do before transposing

    v = val & 0xFFFFFFFF

    c1 = v & 0b_10101010_10101010_10101010_10101010
    c2 = v & 0b_01010101_01010101_01010101_01010101
    orientations = _transpose_values((c1 >> 1) | (c2 << 1))

    return (filters << 32) | orientations


@nb.njit(nb.uint64[:](nb.uint64), cache=True)
def transforms(val):
    """Return all the transforms of the encoded board."""
    horizontal_reflection = reflect_horizontally(val)
    vertical_reflection = reflect_vertically(val)
    transposition = transpose(val)

    rotated_90 = reflect_horizontally(transposition)
    rotated_180 = reflect_vertically(horizontal_reflection)
    rotated_270 = reflect_vertically(transposition)

    anti_transposition = reflect_vertically(rotated_90)

    # the order doesn't really matter, but match board.transforms()
    return np.array(
        [
            val,
            rotated_270,
            rotated_180,
            rotated_90,
            transposition,
            vertical_reflection,
            anti_transposition,
            horizontal_reflection,
        ],
        dtype=np.uint64,
    )


@nb.njit(nb.uint64(nb.uint64), cache=True)
def canonicalize_board(val):
    """Return the canonical encoded board from the set of transforms of the given board."""

    # don't call transforms here to avoid allocating an array
    horizontal_reflection = reflect_horizontally(val)
    vertical_reflection = reflect_vertically(val)
    transposition = transpose(val)

    rotated_90 = reflect_horizontally(transposition)
    rotated_180 = reflect_vertically(horizontal_reflection)
    rotated_270 = reflect_vertically(transposition)

    anti_transposition = reflect_vertically(rotated_90)

    return min(
        val,
        rotated_270,
        rotated_180,
        rotated_90,
        transposition,
        vertical_reflection,
        anti_transposition,
        horizontal_reflection,
    )


@nb.njit(nb.uint64[:](nb.uint64[:]), cache=True)
def canonicalize_boards(boards):
    canonicalized = np.empty(boards.shape[0], dtype=np.uint64)
    for i in range(boards.shape[0]):
        canonicalized[i] = canonicalize_board(boards[i])
    return canonicalized


@nb.njit(nb.uint32(nb.uint32), cache=True)
def encode_lights_from_filters(filters):
    """Return an int encoding the lights, determined by the dominoes placed on this board."""

    li = 0

    # horizontal lights
    shift = 15 * 2
    for _ in range(4):
        val = 0
        for _ in range(4):
            val |= filters >> shift & 0b11
            shift -= 2
        bit_count = (val & 1) + (val >> 1 & 1)
        li = li << 2 | bit_count

    # vertical lights
    for i in range(4):
        shift = (15 - i) * 2
        val = 0
        for _ in range(4):
            val |= filters >> shift & 0b11
            shift -= 8
        bit_count = (val & 1) + (val >> 1 & 1)
        li = li << 2 | bit_count

    return li


@nb.njit(nb.uint32(nb.uint32), cache=True)
def reflect_lights_horizontally(val):
    """Reflect the encoded lights horizontally"""

    h = val >> 8 & 0b11111111
    v1 = val & 0b_11000000
    v2 = val & 0b_00110000
    v3 = val & 0b_00001100
    v4 = val & 0b_00000011

    return (h << 8) | (v1 >> 6) | (v2 >> 2) | (v3 << 2) | (v4 << 6)


@nb.njit(nb.uint32(nb.uint32), cache=True)
def reflect_lights_vertically(val):
    """Reflect the encoded lights vertically"""

    h1 = val >> 8 & 0b_11000000
    h2 = val >> 8 & 0b_00110000
    h3 = val >> 8 & 0b_00001100
    h4 = val >> 8 & 0b_00000011
    v = val & 0b11111111

    return (h1 << 2) | (h2 << 6) | (h3 << 10) | (h4 << 14) | v


@nb.njit(nb.uint32(nb.uint32), cache=True)
def transpose_lights(val):
    """Reflect the encoded lights in y=x"""

    h = val >> 8 & 0b11111111
    v = val & 0b11111111

    return (v << 8) | h


@nb.njit(nb.uint32(nb.int8[:]), cache=True)
def encode_dominoes(dominoes):
    """Encode a multiset of dominoes from an array of domino indexes as an unsigned int by packing bits.
    Each distinct domino is represented by a 4-bit count.
    """
    val = 0
    for i in range(8):  # total number of dominoes
        val = val << 4 | np.sum(dominoes == i)
    return val


def decode_dominoes(val):
    """Decode an unsigned 32-bit int representing a multiset of dominoes by unpacking bits."""
    dominoes = []
    for i in range(8):
        count = val & 0b1111
        val = val >> 4
        for _ in range(count):
            dominoes.append(7 - i)
    dominoes.reverse()
    return np.array(dominoes, dtype=np.int8)


@nb.njit(nb.uint32(nb.uint32), cache=True)
def reflect_dominoes_horizontally(val):
    """Reflect the encoded dominoes horizontally"""
    r0 = (val & 0x0000000F) >> 0
    r1 = (val & 0x000000F0) >> 4
    r2 = (val & 0x00000F00) >> 8
    r3 = (val & 0x0000F000) >> 12
    r4 = (val & 0x000F0000) >> 16
    r5 = (val & 0x00F00000) >> 20
    r6 = (val & 0x0F000000) >> 24
    r7 = (val & 0xF0000000) >> 28
    return r3 | (r2 << 4) | (r1 << 8) | (r0 << 12) | (r7 << 16) | (r5 << 20) | (r6 << 24) | (r4 << 28)


@nb.njit(nb.uint32(nb.uint32), cache=True)
def reflect_dominoes_vertically(val):
    """Reflect the encoded dominoes vertically"""
    r0 = (val & 0x0000000F) >> 0
    r1 = (val & 0x000000F0) >> 4
    r2 = (val & 0x00000F00) >> 8
    r3 = (val & 0x0000F000) >> 12
    r4 = (val & 0x000F0000) >> 16
    r5 = (val & 0x00F00000) >> 20
    r6 = (val & 0x0F000000) >> 24
    r7 = (val & 0xF0000000) >> 28
    return r3 | (r1 << 4) | (r2 << 8) | (r0 << 12) | (r7 << 16) | (r6 << 20) | (r5 << 24) | (r4 << 28)


@nb.njit(nb.uint32(nb.uint32), cache=True)
def transpose_dominoes(val):
    """Reflect the encoded dominoes in y=x"""
    r0 = (val & 0x0000000F) >> 0
    r1 = (val & 0x000000F0) >> 4
    r2 = (val & 0x00000F00) >> 8
    r3 = (val & 0x0000F000) >> 12
    r4 = (val & 0x000F0000) >> 16
    r5 = (val & 0x00F00000) >> 20
    r6 = (val & 0x0F000000) >> 24
    r7 = (val & 0xF0000000) >> 28
    return r4 | (r5 << 4) | (r6 << 8) | (r7 << 12) | (r0 << 16) | (r1 << 20) | (r2 << 24) | (r3 << 28)


def all_boards(num_pieces):
    """Return an array containing all the boards - and their corresponding lights and dominoes - containing `num_pieces`."""
    product = itertools.product(range(len(ALL_DOMINOES)), repeat=num_pieces)
    selections = np.array(list(product), dtype=np.int8)
    return _all_boards(selections)


# The order is the same as the order in ALL_DOMINOES
DOMINOES_FILTER1 = np.array([1, 1, 2, 2, 1, 1, 2, 2], dtype=np.int8)
DOMINOES_FILTER2 = np.array([1, 2, 1, 2, 1, 2, 1, 2], dtype=np.int8)
DOMINOES_ORIENTATION = np.array([1, 1, 1, 1, 2, 2, 2, 2], dtype=np.int8)
DOMINOES_FILTER2_SHIFT = np.array([1, 1, 1, 1, 4, 4, 4, 4], dtype=np.int8)


@nb.njit(
    nb.types.Tuple((nb.uint64[:], nb.uint32[:], nb.uint32[:]))(nb.int8[:, :]),
    locals={"filters": nb.uint64, "orientations": nb.uint64},
    cache=True,
)
def _all_boards(selections):
    num_selections = selections.shape[0]
    length = selections.shape[1]
    sizes = np.asarray([16] * length, dtype=np.int32)
    tuples = cproduct_idx(sizes)

    max_num_boards = len(tuples) * num_selections
    boards = np.zeros(max_num_boards, dtype=np.uint64)
    lights = np.zeros(max_num_boards, dtype=np.uint32)
    dominoes = np.zeros(max_num_boards, dtype=np.uint32)

    board_idx = 0
    for i in range(len(tuples)):
        for p in range(num_selections):
            filters = 0
            orientations = 0
            valid_board = True

            # set filters and orientations for this tuple/selection
            for j in range(length):
                sel = selections[p][j]

                # check if either horizontal or vertical dominoes are out of bounds
                if DOMINOES_ORIENTATION[sel] == 1 and (tuples[i, j] + 1) % 4 == 0:
                    valid_board = False
                    break
                if DOMINOES_ORIENTATION[sel] == 2 and tuples[i, j] >= 12:
                    valid_board = False
                    break

                # find the bit shifts for each filter
                filter1_shift = (15 - tuples[i, j]) * 2
                filter2_shift = (15 - (tuples[i, j] + DOMINOES_FILTER2_SHIFT[sel])) * 2

                # if the bits at either filter 1 or 2 are not 0 then we have an overlap
                if (filters >> filter1_shift) & 0b11 != 0 or (
                    filters >> filter2_shift
                ) & 0b11 != 0:
                    valid_board = False
                    break

                # update the filters and orientations bits
                filters |= DOMINOES_FILTER1[sel] << filter1_shift
                filters |= DOMINOES_FILTER2[sel] << filter2_shift
                orientations |= DOMINOES_ORIENTATION[sel] << filter1_shift
                orientations |= DOMINOES_ORIENTATION[sel] << filter2_shift

            if valid_board:
                val = (filters << 32) | orientations
                boards[board_idx] = val
                lights[board_idx] = encode_lights_from_filters(filters)
                dominoes[board_idx] = encode_dominoes(selections[p])
                board_idx += 1

    return boards[:board_idx], lights[:board_idx], dominoes[:board_idx]


def canonical_boards(num_pieces):
    """Return an array containing all the canonical boards - and their corresponding lights and dominoes - containing `num_pieces`."""

    boards, lights, dominoes = all_boards(num_pieces)
    canonicalized_boards, indices, _, _ = np.unique_all(canonicalize_boards(boards))
    return canonicalized_boards, lights[indices], dominoes[indices]


def all_puzzles_with_unique_solution(num_pieces):
    """Compute all the puzzles containing `num_pieces` with a unique solution.

    Note that symmetries are _not_ taken into account, so puzzles that can be transformed into one another
    will all be returned.
    """

    board_vals, lights_vals, dominoes_vals = all_boards(num_pieces=num_pieces)

    df = pd.DataFrame({"boards": board_vals, "lights": lights_vals, "dominoes": dominoes_vals})

    # remove any duplicates ('keep=False') since these are puzzles for which the same lights and dominoes
    # have different board values so they do not have unique solutions
    df_uniq_solns = df.drop_duplicates(["lights", "dominoes"], keep=False)

    board_vals = df_uniq_solns["boards"].to_numpy().astype(np.uint64)
    lights_vals = df_uniq_solns["lights"].to_numpy().astype(np.uint32)
    dominoes_vals = df_uniq_solns["dominoes"].to_numpy().astype(np.uint32)

    return board_vals, lights_vals, dominoes_vals


@nb.njit(nb.types.Tuple((nb.uint32, nb.uint32))(nb.uint32, nb.uint32), cache=True)
def canonicalize_puzzle(lights, dominoes):

    horizontal_reflection = reflect_lights_horizontally(lights)
    vertical_reflection = reflect_lights_vertically(lights)
    transposition = transpose_lights(lights)

    rotated_90 = reflect_lights_horizontally(transposition)
    rotated_180 = reflect_lights_vertically(horizontal_reflection)
    rotated_270 = reflect_lights_vertically(transposition)

    anti_transposition = reflect_lights_vertically(rotated_90)

    transformed_lights = np.array(
        [
            lights,
            rotated_270,
            rotated_180,
            rotated_90,
            transposition,
            vertical_reflection,
            anti_transposition,
            horizontal_reflection,
        ],
        dtype=np.uint64,
    )
    canonical_lights = min(transformed_lights)

    horizontal_reflection = reflect_dominoes_horizontally(dominoes)
    vertical_reflection = reflect_dominoes_vertically(dominoes)
    transposition = transpose_dominoes(dominoes)

    rotated_90 = reflect_dominoes_horizontally(transposition)
    rotated_180 = reflect_dominoes_vertically(horizontal_reflection)
    rotated_270 = reflect_dominoes_vertically(transposition)

    anti_transposition = reflect_dominoes_vertically(rotated_90)

    transformed_pieces = np.array(
        [
            dominoes,
            rotated_270,
            rotated_180,
            rotated_90,
            transposition,
            vertical_reflection,
            anti_transposition,
            horizontal_reflection,
        ],
        dtype=np.uint32,
    )

    # to restrict transformed lights to all the canonical (minimum) lights in case there are ties
    canonical_pieces = min(transformed_pieces[transformed_lights == canonical_lights])

    return canonical_lights, canonical_pieces


def canonical_puzzles_with_unique_solution(num_pieces):
    """Compute all canonical puzzles with a unique solution containing `num_pieces`, taking symmetries into account."""

    _, single_solution_lights, single_solution_dominoes = all_puzzles_with_unique_solution(num_pieces)
    n_puzzles = len(single_solution_lights)

    canonical_lights = np.empty(n_puzzles, dtype=np.uint32)
    canonical_dominoes = np.empty(n_puzzles, dtype=np.uint32)
    for i, (lights, dominoes) in enumerate(
        zip(single_solution_lights, single_solution_dominoes)
    ):
        canonical_lights[i], canonical_dominoes[i] = canonicalize_puzzle(lights, dominoes)

    # remove duplicate canonical puzzles
    canonical_puzzles = np.stack((canonical_lights, canonical_dominoes), axis=1)
    canonical_puzzles = np.unique(canonical_puzzles, axis=0)
    canonical_lights = canonical_puzzles[:, 0]
    canonical_dominoes = canonical_puzzles[:, 1]

    return canonical_lights, canonical_dominoes

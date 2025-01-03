import random

from itertools import permutations, product

import numpy as np

from polarize.model import ALL_DOMINOES, Board, DominoOrientation, PlacedDomino

def _coord_lt(n, coord1, coord2):
    y1, x1 = coord1
    y2, x2 = coord2
    return x1 + n * y1 < x2 + n * y2

def _coords_increasing(n, coords):
    for i in range(len(coords) - 1):
        if not _coord_lt(n, coords[i], coords[i + 1]):
            return False
    return True

def all_boards(n, dominoes):
    for domino_perm in set(permutations(domino for domino in dominoes)):
        for coords in product(*(domino.places() for domino in domino_perm)):
            # skip if coords are not strictly increasing (in pos)
            if not _coords_increasing(n, coords):
                continue

            try:
                board = Board(n=n)
                for domino, coord in zip(domino_perm, coords):
                    y, x = coord
                    pd = PlacedDomino(domino, x, y)
                    if board.can_add(pd):
                        board.add_domino(pd)
                    else:
                        raise ValueError()
                yield board
            except ValueError:
                pass  # try next coords


def layout(n, dominoes):
    # Find a layout of the dominoes on an nxn board.
    # This is useful for the "off-board" pieces at the beginning.

    # Place all the vertical dominoes first - a heuristic which seems
    # to produce a good layout
    def sort_vert_first(domino):
        return 0 if domino.orientation is DominoOrientation.VERTICAL else 1

    sorted_dominoes = sorted(dominoes, key=sort_vert_first)

    for coords in product(*(domino.places() for domino in sorted_dominoes)):
        # skip if coords are not strictly increasing (in pos)
        if not _coords_increasing(n, coords):
            continue

        try:
            board = Board(n=n)
            for domino, coord in zip(sorted_dominoes, coords):
                y, x = coord
                pd = PlacedDomino(domino, x, y)
                if board.can_add(pd):
                    board.add_domino(pd)
                else:
                    raise ValueError()
            return board
        except ValueError:
            pass  # try next coords


def generate(n, n_pieces=None):
    n_pieces = n_pieces or 3

    while True:
        # choose some dominoes
        dominoes = random.choices(ALL_DOMINOES, k=n_pieces)

        # find all the boards and lights for these dominoes
        boards = list(all_boards(n, dominoes))
        lights = np.asarray([board.lights_int for board in boards])

        # find unique lights
        u, ui, uii, uc = np.unique_all(lights)

        # check there are some unique puzzles
        if np.count_nonzero(uc == 1) == 0:
            continue

        # choose a random puzzle
        li = np.random.choice(u[uc == 1])

        inds = np.nonzero(lights == li)[0]
        assert len(inds) == 1
        ind = inds[0]
        board = boards[ind]

        break

    puzzle = board.to_puzzle()

    return puzzle, board

from itertools import combinations_with_replacement, permutations, product

import numpy as np

from polarize.model import ALL_DOMINOES, Board, PlacedDomino


def all_boards(dominoes):
    def coord_lt(coord1, coord2):
        y1, x1 = coord1
        y2, x2 = coord2
        return x1 + 4 * y1 < x2 + 4 * y2

    def coords_increasing(coords):
        for i in range(len(coords) - 1):
            if not coord_lt(coords[i], coords[i + 1]):
                return False
        return True

    for domino_perm in set(permutations(domino for domino in dominoes)):
        for coords in product(*(domino.places() for domino in domino_perm)):
            # skip if coords are not strictly increasing (in pos)
            if not coords_increasing(coords):
                continue

            try:
                board = Board()
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


def count_puzzles(num_pieces):
    count = 0
    for dominoes in combinations_with_replacement(ALL_DOMINOES, num_pieces):
        # find all the boards and lights for these dominoes
        boards = list(all_boards(dominoes))
        lights = np.asarray([board.lights for board in boards])

        # find unique lights
        _, uc = np.unique_counts(lights)

        count += np.count_nonzero(uc == 1)
    return count
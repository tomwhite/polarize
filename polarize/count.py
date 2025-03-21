from itertools import combinations_with_replacement

import numpy as np

from polarize.generate import all_boards_with_dominoes
from polarize.model import ALL_DOMINOES


def count_puzzles(n, num_pieces):
    # Note that this doesn't take symmetries into account (so it double counts)
    count = 0
    for dominoes in combinations_with_replacement(ALL_DOMINOES, num_pieces):
        # find all the boards and lights for these dominoes
        boards = list(all_boards_with_dominoes(n, dominoes))
        lights = np.asarray([board.lights_int for board in boards])

        # find unique lights
        _, uc = np.unique_counts(lights)

        count += np.count_nonzero(uc == 1)
    return count

import random

import numpy as np

from polarize.count import all_boards
from polarize.model import ALL_DOMINOES


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

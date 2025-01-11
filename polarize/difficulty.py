import numpy as np


def puzzle_features(puzzle):
    """
    Compute various puzzle features, which can be used to characterize its difficulty.
    """
    num_dominoes = len(puzzle.dominoes)
    num_yellow_spots = np.count_nonzero(np.asarray(puzzle.lights) == 0)

    return dict(
        num_dominoes=num_dominoes,
        num_yellow_spots=num_yellow_spots,
    )
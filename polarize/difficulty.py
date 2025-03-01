import numpy as np

from polarize.model import Board, PlacedDomino

def puzzle_features(puzzle):
    """
    Compute various puzzle features, which can be used to characterize its difficulty.
    """
    num_dominoes = len(puzzle.dominoes)
    num_distinct_dominoes = len(set(puzzle.dominoes))
    num_yellow_spots = np.count_nonzero(np.asarray(puzzle.lights) == 0)
    total_num_valid_domino_places = sum(num_valid_domino_places(puzzle, domino) for domino in puzzle.dominoes)

    return dict(
        num_dominoes=num_dominoes,
        num_distinct_dominoes=num_distinct_dominoes,
        num_yellow_spots=num_yellow_spots,
        total_num_valid_domino_places=total_num_valid_domino_places,
    )


def num_valid_domino_places(puzzle, domino):
    """
    The number of places that a given domino can be placed on a board by itself
    to be consistent with a given puzzle.
    """
    num = 0
    for coord in domino.places():
        board = Board(n=puzzle.n)
        y, x = coord
        pd = PlacedDomino(domino, x, y)
        board.add_domino(pd)
        if np.all(board.lights <= puzzle.lights):
            num += 1
    return num

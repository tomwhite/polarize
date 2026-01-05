from itertools import product

import numpy as np

from polarize.model import Board, PlacedDomino


def puzzle_features(puzzle):
    """
    Compute various puzzle features, which can be used to characterize its difficulty.
    """
    num_dominoes = len(puzzle.dominoes)
    num_distinct_dominoes = len(set(puzzle.dominoes))
    num_yellow_spots = np.count_nonzero(np.asarray(puzzle.lights) == 0)
    total_num_valid_domino_places = sum(
        num_valid_domino_places(puzzle, domino) for domino in puzzle.dominoes
    )
    total_candidate_boards = num_candidate_boards(puzzle)

    return dict(
        num_dominoes=num_dominoes,
        num_distinct_dominoes=num_distinct_dominoes,
        num_yellow_spots=num_yellow_spots,
        total_num_valid_domino_places=total_num_valid_domino_places,
        total_candidate_boards=total_candidate_boards
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


def num_candidate_boards(puzzle):
    """
    The number of boards that are candidate solutions, built up from placed dominoes
    that are individually consistent.
    """
    all_pds = []
    for domino in puzzle.dominoes:
        pds = list(valid_domino_places(puzzle, domino))
        all_pds.append(pds)

    valid_boards = set()
    for placed_dominoes in product(*all_pds):
        board = valid_board(puzzle.n, placed_dominoes)
        if board is not None:
            valid_boards.add(board)

    return len(valid_boards)


def valid_domino_places(puzzle, domino):
    for coord in domino.places():
        board = Board(n=puzzle.n)
        y, x = coord
        pd = PlacedDomino(domino, x, y)
        board.add_domino(pd)
        if np.all(board.lights <= puzzle.lights):
            yield pd


def valid_board(n, placed_dominoes):
    board = Board(n)
    for pd in placed_dominoes:
        if board.can_add(pd):
            board.add_domino(pd)
        else:
            return None
    return board

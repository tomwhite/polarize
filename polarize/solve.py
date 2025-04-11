from functools import cache
from itertools import chain, combinations

import numpy as np

from polarize.encode import decode_board, encode_dominoes, all_puzzles
from polarize.generate import all_boards_with_dominoes


# from https://docs.python.org/3/library/itertools.html#itertools-recipes
def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def solve(puzzle, *, fewer_pieces_allowed=False):
    solution_boards = []

    def sort_tuple(t):
        return tuple(sorted(t))

    if fewer_pieces_allowed:
        dominoes_subsets = set(sort_tuple(s) for s in powerset(puzzle.dominoes))
    else:
        dominoes_subsets = [puzzle.dominoes]

    for dominoes_subset in dominoes_subsets:
        for board in all_boards_with_dominoes(puzzle.n, dominoes_subset):
            if board.lights_int == puzzle.lights_int:
                solution_boards.append(board)

    return solution_boards


def has_unique_solution(puzzle, *, fewer_pieces_allowed=False):
    solutions = solve(puzzle, fewer_pieces_allowed=fewer_pieces_allowed)
    return len(solutions) == 1

# The "quick" solve functions use the code from encode.py which pre-compute all boards
# of a certain size

@cache
def _get_all_puzzles(num_pieces, fewer_pieces_allowed=False):
    if not fewer_pieces_allowed:
        return all_puzzles(num_pieces)

    # concat all arrays for all puzzles up to num_pieces
    all_boards_list = []
    all_lights_list = []
    all_dominoes_list = []
    for n in range(num_pieces + 1):
        _, all_boards, all_lights, all_dominoes = all_puzzles(n)
        all_boards_list.append(all_boards)
        all_lights_list.append(all_lights)
        all_dominoes_list.append(all_dominoes)

    all_boards = np.concatenate(all_boards_list)
    all_lights = np.concatenate(all_lights_list)
    all_dominoes = np.concatenate(all_dominoes_list)

    return None, all_boards, all_lights, all_dominoes

def _boards_and_lights_for_dominoes(puzzle, *, fewer_pieces_allowed=False):
    num_pieces = len(puzzle.dominoes)

    _, all_boards, all_lights, all_dominoes = _get_all_puzzles(
        num_pieces, fewer_pieces_allowed=fewer_pieces_allowed
    )

    if not fewer_pieces_allowed:
        # simple case: use exactly num_pieces
        dominoes_val = encode_dominoes(np.array([d.value for d in puzzle.dominoes], dtype=np.int8))
        dominoes_index = all_dominoes == dominoes_val

    else:
        # use num_pieces or fewer
        dominoes_subsets = set(powerset([d.value for d in puzzle.dominoes]))
        dominoes_vals = np.empty(len(dominoes_subsets), dtype=np.uint32)
        for i, dominoes_subset in enumerate(dominoes_subsets):
            dominoes_ints_subset = np.array(list(dominoes_subset), dtype=np.int8)
            dominoes_vals[i] = encode_dominoes(dominoes_ints_subset)
        dominoes_index = np.isin(all_dominoes, dominoes_vals)
    
    # restrict to boards and lights with desired dominoes
    boards_with_pieces = all_boards[dominoes_index]
    lights_with_dominoes = all_lights[dominoes_index]

    return boards_with_pieces, lights_with_dominoes


def _quick_solve(puzzle, *, fewer_pieces_allowed=False):
    # restrict to boards and lights with desired dominoes
    boards_with_dominoes, lights_with_dominoes = _boards_and_lights_for_dominoes(
        puzzle, fewer_pieces_allowed=fewer_pieces_allowed
    )

    # restrict to lights in puzzle
    lights_val = puzzle.lights_int
    matching_boards = boards_with_dominoes[lights_with_dominoes == lights_val]
    
    return matching_boards

def quick_solve(puzzle, *, fewer_pieces_allowed=False):
    matching_boards = _quick_solve(puzzle, fewer_pieces_allowed=fewer_pieces_allowed)
    return [decode_board(b) for b in matching_boards]


def quick_has_unique_solution(puzzle, *, fewer_pieces_allowed=False):
    return len(quick_solve(puzzle, fewer_pieces_allowed=fewer_pieces_allowed)) == 1

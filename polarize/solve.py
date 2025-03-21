from itertools import chain, combinations

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

from polarize.model import Puzzle
from polarize.solve import has_unique_solution, solve

def test_solve_unique():
    # set on 18 Jan 2025
    puzzle = Puzzle.from_json_str(
        """{"n": 4, "lights": [2, 0, 1, 2, 1, 1, 2, 2], "dominoes": [4, 2, 1, 3], "initial_placed_dominoes": [{"domino": 1, "i": 1, "j": 1}, {"domino": 2, "i": 1, "j": 0}, {"domino": 4, "i": 0, "j": 0}, {"domino": 3, "i": 0, "j": 2}], "solution": {"values": [[0, 0, 1, 2], [0, 0, 0, 0], [2, 2, 0, 0], [0, 0, 2, 1]], "placed_dominoes": [{"domino": 1, "i": 2, "j": 0}, {"domino": 2, "i": 2, "j": 3}, {"domino": 3, "i": 0, "j": 2}]}}"""
    )

    assert has_unique_solution(puzzle)
    # assert has_unique_solution(puzzle, fewer_pieces_allowed=True)
    for solution in solve(puzzle, fewer_pieces_allowed=True):
        print(solution)

def test_solve_not_unique():
    # set on 19 Jan 2025
    puzzle = Puzzle.from_json_str(
        """{"n": 4, "lights": [1, 1, 1, 1, 2, 0, 1, 1], "dominoes": [6, 0, 6, 0], "initial_placed_dominoes": [{"domino": 6, "i": 1, "j": 0}, {"domino": 0, "i": 2, "j": 0}, {"domino": 0, "i": 2, "j": 1}, {"domino": 6, "i": 0, "j": 0}], "solution": {"values": [[2, 0, 0, 0], [1, 0, 0, 0], [2, 0, 0, 0], [1, 0, 1, 1]], "placed_dominoes": [{"domino": 6, "i": 0, "j": 2}, {"domino": 0, "i": 2, "j": 3}, {"domino": 6, "i": 0, "j": 0}]}}"""
    )
    assert has_unique_solution(puzzle)
    assert not has_unique_solution(puzzle, fewer_pieces_allowed=True)

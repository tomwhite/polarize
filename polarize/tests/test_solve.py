from polarize.model import Puzzle
from polarize.solve import has_unique_solution, quick_has_unique_solution


def test_solve_unique():
    # set on 20 Jan 2025
    puzzle = Puzzle.from_json_str(
        """{"n": 4, "lights": [2, 2, 1, 1, 0, 2, 2, 1], "dominoes": [5, 0, 5, 1], "initial_placed_dominoes": [{"domino": 5, "i": 0, "j": 0}, {"domino": 0, "i": 2, "j": 0}, {"domino": 5, "i": 1, "j": 0}, {"domino": 1, "i": 2, "j": 1}], "solution": {"values": [[0, 1, 1, 2], [0, 2, 1, 0], [0, 0, 2, 0], [0, 1, 1, 0]], "placed_dominoes": [{"domino": 1, "i": 2, "j": 0}, {"domino": 0, "i": 1, "j": 3}, {"domino": 5, "i": 2, "j": 1}, {"domino": 5, "i": 1, "j": 0}]}}"""
    )
    assert has_unique_solution(puzzle)
    assert has_unique_solution(puzzle, fewer_pieces_allowed=True)


def test_solve_not_unique_with_fewer_pieces():
    # set on 18 Jan 2025
    puzzle = Puzzle.from_json_str(
        """{"n": 4, "lights": [2, 0, 1, 2, 1, 1, 2, 2], "dominoes": [4, 2, 1, 3], "initial_placed_dominoes": [{"domino": 1, "i": 1, "j": 1}, {"domino": 2, "i": 1, "j": 0}, {"domino": 4, "i": 0, "j": 0}, {"domino": 3, "i": 0, "j": 2}], "solution": {"values": [[0, 0, 1, 2], [0, 0, 0, 0], [2, 2, 0, 0], [0, 0, 2, 1]], "placed_dominoes": [{"domino": 1, "i": 2, "j": 0}, {"domino": 2, "i": 2, "j": 3}, {"domino": 3, "i": 0, "j": 2}]}}"""
    )
    assert has_unique_solution(puzzle)
    assert not has_unique_solution(puzzle, fewer_pieces_allowed=True)


def test_quick_solve_unique():
    # set on 20 Jan 2025
    puzzle = Puzzle.from_json_str(
        """{"n": 4, "lights": [2, 2, 1, 1, 0, 2, 2, 1], "dominoes": [5, 0, 5, 1], "initial_placed_dominoes": [{"domino": 5, "i": 0, "j": 0}, {"domino": 0, "i": 2, "j": 0}, {"domino": 5, "i": 1, "j": 0}, {"domino": 1, "i": 2, "j": 1}], "solution": {"values": [[0, 1, 1, 2], [0, 2, 1, 0], [0, 0, 2, 0], [0, 1, 1, 0]], "placed_dominoes": [{"domino": 1, "i": 2, "j": 0}, {"domino": 0, "i": 1, "j": 3}, {"domino": 5, "i": 2, "j": 1}, {"domino": 5, "i": 1, "j": 0}]}}"""
    )
    assert quick_has_unique_solution(puzzle)
    assert quick_has_unique_solution(puzzle, fewer_pieces_allowed=True)


def test_quick_solve_not_unique_with_fewer_pieces():
    # set on 18 Jan 2025
    puzzle = Puzzle.from_json_str(
        """{"n": 4, "lights": [2, 0, 1, 2, 1, 1, 2, 2], "dominoes": [4, 2, 1, 3], "initial_placed_dominoes": [{"domino": 1, "i": 1, "j": 1}, {"domino": 2, "i": 1, "j": 0}, {"domino": 4, "i": 0, "j": 0}, {"domino": 3, "i": 0, "j": 2}], "solution": {"values": [[0, 0, 1, 2], [0, 0, 0, 0], [2, 2, 0, 0], [0, 0, 2, 1]], "placed_dominoes": [{"domino": 1, "i": 2, "j": 0}, {"domino": 2, "i": 2, "j": 3}, {"domino": 3, "i": 0, "j": 2}]}}"""
    )
    assert quick_has_unique_solution(puzzle)
    assert not quick_has_unique_solution(puzzle, fewer_pieces_allowed=True)

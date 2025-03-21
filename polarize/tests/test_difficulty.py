from polarize.model import Puzzle
from polarize.difficulty import num_valid_domino_places, puzzle_features


def test_puzzle_features():
    # set on 11 Jan 2025
    puzzle = Puzzle.from_json_str(
        """{"n": 4, "lights": [1, 2, 2, 0, 0, 1, 2, 2], "dominoes": [2, 6, 6], "initial_placed_dominoes": [{"domino": 6, "i": 0, "j": 0}, {"domino": 2, "i": 2, "j": 0}, {"domino": 6, "i": 1, "j": 0}], "solution": {"values": [[0, 0, 2, 0], [0, 0, 1, 2], [0, 2, 1, 1], [0, 0, 0, 0]], "placed_dominoes": [{"domino": 2, "i": 1, "j": 2}, {"domino": 6, "i": 3, "j": 1}, {"domino": 6, "i": 2, "j": 0}]}}"""
    )

    features = puzzle_features(puzzle)

    assert features["num_dominoes"] == 3
    assert features["num_distinct_dominoes"] == 2
    assert features["num_yellow_spots"] == 2


def test_num_valid_domino_places():
    # set on 1 Feb 2025
    puzzle = Puzzle.from_json_str(
        """{"n": 4, "lights": [2, 2, 1, 2, 2, 1, 0, 2], "dominoes": [4, 5, 3, 1], "initial_placed_dominoes": [{"domino": 1, "i": 2, "j": 1}, {"domino": 3, "i": 2, "j": 0}, {"domino": 5, "i": 1, "j": 0}, {"domino": 4, "i": 0, "j": 0}], "solution": {"values": [[2, 2, 0, 1], [1, 0, 0, 2], [1, 0, 0, 0], [1, 2, 0, 0]], "placed_dominoes": [{"domino": 4, "i": 0, "j": 1}, {"domino": 5, "i": 3, "j": 0}, {"domino": 3, "i": 0, "j": 0}, {"domino": 1, "i": 0, "j": 3}]}}"""
    )
    dominoes = puzzle.dominoes
    assert num_valid_domino_places(puzzle, dominoes[0]) == 9
    assert num_valid_domino_places(puzzle, dominoes[1]) == 6
    assert num_valid_domino_places(puzzle, dominoes[2]) == 4
    assert num_valid_domino_places(puzzle, dominoes[3]) == 3

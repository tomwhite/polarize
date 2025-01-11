from polarize.model import Puzzle
from polarize.difficulty import puzzle_features


def test_puzzle_features():
    # set on 11 Jan 2025
    puzzle = Puzzle.from_json_str(
        """{"n": 4, "lights": [1, 1, 1, 2, 2, 1, 0, 0], "dominoes": [6, 6, 7], "initial_placed_dominoes": [{"domino": 6, "i": 0, "j": 0}, {"domino": 6, "i": 1, "j": 0}, {"domino": 7, "i": 2, "j": 0}], "solution": [[2, 0, 0, 0], [1, 0, 0, 0], [2, 2, 0, 0], [1, 2, 0, 0]]}"""
    )

    features = puzzle_features(puzzle)

    assert features["num_dominoes"] == 3
    assert features["num_yellow_spots"] == 2

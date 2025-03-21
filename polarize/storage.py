import json

from polarize.model import Puzzle


def load_puzzle(filename):
    with open(filename) as f:
        return Puzzle.from_json_file(f)


def save_puzzle(puzzle, filename):
    with open(filename, "w") as f:
        json.dump(puzzle.to_json_dict(), f)

from polarize.model import Puzzle

def load_puzzle(filename):
    with open(filename) as f:
        return Puzzle.from_json_file(f)

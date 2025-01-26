from polarize.generate import generate
from polarize.storage import load_puzzle, save_puzzle

def test_storage(tmp_path):
    puzzle, _ = generate(4)

    filename = tmp_path / "puzzle.json"
    save_puzzle(puzzle, filename)
    load_puzzle(filename)

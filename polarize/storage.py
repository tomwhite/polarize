import datetime
import json
from pathlib import Path

from polarize.model import Puzzle


def load_puzzle(filename):
    with open(filename) as f:
        return Puzzle.from_json_file(f)


def save_puzzle(puzzle, filename):
    with open(filename, "w") as f:
        json.dump(puzzle.to_json_dict(), f)


def first_missing_puzzle_path(puzzles_dir="puzzles"):
    """Return the path for the next puzzle to be set."""
    day = datetime.datetime.today()
    num_days = 0
    while True:
        date = day.strftime("%Y-%m-%d")
        full_board_file = Path(puzzles_dir) / f"puzzle-{date}.json"
        if not full_board_file.exists():
            return full_board_file
        num_days += 1
        day = day + datetime.timedelta(days=1)
import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from polarize.encode import encode_dominoes
from polarize.solve import has_unique_solution
from polarize.storage import load_puzzle, first_missing_puzzle_path


def test_puzzles_have_unique_solution(request):
    today = datetime.datetime.today()
    start_date = (today - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    end_date = (today + datetime.timedelta(days=5)).strftime("%Y-%m-%d")
    start_puzzle = f"puzzle-{start_date}.json"
    end_puzzle = f"puzzle-{end_date}.json"

    for full_puzzle_file in sorted((request.config.rootdir / "puzzles").listdir()):
        if full_puzzle_file.isfile():
            filename = Path(full_puzzle_file).name
            if filename < start_puzzle or filename > end_puzzle:
                continue
            if filename in (
                "puzzle-2025-01-17.json",
                "puzzle-2025-01-18.json",
                "puzzle-2025-01-19.json",
            ):
                continue
            puzzle = load_puzzle(full_puzzle_file)
            assert has_unique_solution(puzzle, fewer_pieces_allowed=True)


def test_puzzles_are_unique(request):
    puzzles = {}
    for full_puzzle_file in sorted((request.config.rootdir / "puzzles").listdir()):
        if full_puzzle_file.isfile():
            filename = Path(full_puzzle_file).name
            if filename in ("puzzle-2025-03-28.json"):  # dup of puzzle-2025-03-21.json
                continue
            puzzle = load_puzzle(full_puzzle_file)
            puzzles[filename] = puzzle

    lights_vals = np.zeros(len(puzzles), dtype=np.uint32)
    dominoes_vals = np.zeros(len(puzzles), dtype=np.uint32)
    for i, puzzle in enumerate(puzzles.values()):
        lights_vals[i] = puzzle.lights_int
        dominoes_vals[i] = encode_dominoes(np.array([d.value for d in puzzle.dominoes], dtype=np.int8))

    df = pd.DataFrame({"files": puzzles.keys(), "lights": lights_vals, "dominoes": dominoes_vals})
    df["duplicated"] = df.duplicated(["lights", "dominoes"], keep=False)

    duplicates = df[df["duplicated"] == True]

    assert len(duplicates) == 0


def test_puzzles_in_future(request):
    day = datetime.datetime.today()
    num_days = 0
    while True:
        date = day.strftime("%Y-%m-%d")
        full_puzzle_file = request.config.rootdir / "puzzles" / f"puzzle-{date}.json"
        if not full_puzzle_file.exists():
            break
        assert load_puzzle(full_puzzle_file) is not None
        num_days += 1
        day = day + datetime.timedelta(days=1)
    assert num_days >= 3, f"Missing {full_puzzle_file}"
    assert first_missing_puzzle_path().name == Path(full_puzzle_file).name
import datetime
from pathlib import Path

from polarize.solve import has_unique_solution
from polarize.storage import load_puzzle


def test_puzzles_have_unique_solution(request):
    today = datetime.datetime.today()
    start_date = "2025-01-11"
    end_date = (today + datetime.timedelta(days=5)).strftime("%Y-%m-%d")
    start_puzzle = f"puzzle-{start_date}.json"
    end_puzzle = f"puzzle-{end_date}.json"

    for full_puzzle_file in sorted((request.config.rootdir / "puzzles").listdir()):
        if full_puzzle_file.isfile():
            filename = Path(full_puzzle_file).name
            if filename < start_puzzle or filename > end_puzzle:
                continue
            if filename in ("puzzle-2025-01-17.json", "puzzle-2025-01-18.json", "puzzle-2025-01-19.json"):
                continue
            puzzle = load_puzzle(full_puzzle_file)
            assert has_unique_solution(puzzle, fewer_pieces_allowed=True)

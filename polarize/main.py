import csv
from pathlib import Path
from pprint import pprint

import click
from rich.console import Console

from polarize.difficulty import puzzle_features
from polarize.game import play_game
from polarize.generate import puzzle_generator, generate as generate_puzzle
from polarize.solve import solve
from polarize.storage import load_puzzle, save_puzzle, first_missing_puzzle_path


@click.group()
def cli():
    pass


@cli.command()
@click.argument("filename", required=False)
@click.option("--number", default=1)
@click.option("--pieces", default=3)
@click.option("--max-yellow-spots", default=8)  # unlimited
@click.option("--min-distinct-dominoes", default=1)
def generate(filename, number, pieces, max_yellow_spots, min_distinct_dominoes):
    """Generate puzzles according to specified criteria"""

    if filename is not None and number != 1:
        raise ValueError("Can't set `filename` when `number` is not 1")
    generator = puzzle_generator(4, pieces)
    for _ in range(number):
        while True:
            puzzle, _ = next(generator)
            features = puzzle_features(puzzle)
            if (
                features["num_yellow_spots"] <= max_yellow_spots
                and features["num_distinct_dominoes"] >= min_distinct_dominoes
            ):
                break
        console = Console()
        console.print(puzzle)
        pprint(features)

        if filename:
            f = filename
        else:
            # save directly as next puzzle
            f = first_missing_puzzle_path()
        save_puzzle(puzzle, f)


@cli.command()
@click.argument("filename", required=False)
@click.option("--pieces", default=3)
def play(filename, pieces):
    """Play Polarize puzzles"""
    if filename is not None:
        puzzle = load_puzzle(filename)
        solutions = solve(puzzle)
        assert len(solutions) == 1
        solution = solutions[0]
    else:
        puzzle, solution = generate_puzzle(4, pieces)

    play_game(puzzle, solution)


@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.argument("output")
def features(directory, output):
    """Write puzzle features to a CSV file"""
    all_features = []
    files = Path(directory).glob("*.json")
    for filename in sorted(files):
        puzzle = load_puzzle(filename)
        features = puzzle_features(puzzle)
        features["filename"] = filename.name
        all_features.append(features)

    with open(output, "w", newline="") as csvfile:
        fieldnames = list(all_features[0].keys())
        # make sure "filename is first
        fieldnames.remove("filename")
        fieldnames.insert(0, "filename")
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for feature in all_features:
            writer.writerow(feature)


if __name__ == "__main__":
    cli()

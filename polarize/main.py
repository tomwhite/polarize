import csv
from pathlib import Path
from pprint import pprint

import click

from polarize.difficulty import puzzle_features
from polarize.game import play_game
from polarize.generate import generate as generate_puzzle
from polarize.solve import solve
from polarize.storage import load_puzzle, save_puzzle


@click.group()
def cli():
    pass

@cli.command()
@click.argument("filename", required=False)
@click.option("--pieces", default=3)
def generate(filename, pieces):
    """Generate puzzles according to specified criteria"""
    puzzle, _ = generate_puzzle(4, pieces)
    pprint(puzzle_features(puzzle))
    save_puzzle(puzzle, filename)

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

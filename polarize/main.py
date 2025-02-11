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


if __name__ == "__main__":
    cli()

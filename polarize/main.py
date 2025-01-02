import click

from polarize.game import play_game
from polarize.generate import generate
from polarize.solve import solve
from polarize.storage import load_puzzle


@click.group()
def cli():
    pass


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
        puzzle, solution = generate(4, pieces)

    play_game(puzzle, solution)


if __name__ == "__main__":
    cli()

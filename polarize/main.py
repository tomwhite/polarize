import click

from polarize.game import play_game


@click.group()
def cli():
    pass


@cli.command()
@click.option("--pieces", default=3)
def play(pieces):
    """Play Polarize puzzles"""
    play_game(pieces)


if __name__ == "__main__":
    cli()

import click

from polarize.game import play_game 

@click.group()
def cli():
    pass

@cli.command()
@click.argument("filename", required=False)
def play(filename):
    """Play Polarize puzzles"""
    play_game()


if __name__ == "__main__":
    cli()

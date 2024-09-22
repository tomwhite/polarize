from rich.console import Console

from polarize.model import Board, PlacedDomino, ALL_DOMINOES


def test_domino():
    for domino in ALL_DOMINOES:
        print(domino)


def test_board():
    board = Board(
        PlacedDomino(ALL_DOMINOES[4], 0, 2),
        PlacedDomino(ALL_DOMINOES[5], 2, 2),
    )
    print(board)

    print(f"{board.lights()}, {board.lights():08b}")

    puzzle = board.to_puzzle()

    console = Console()

    console.print(puzzle)

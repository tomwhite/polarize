import numpy as np

from polarize.count import all_boards
from polarize.model import ALL_DOMINOES

def generate(n_pieces=None):

    # choose some dominoes (TOOD: randomise)
    dominoes = [ALL_DOMINOES[0], ALL_DOMINOES[3]]

    # find all the boards and lights for these dominoes
    boards = list(all_boards(dominoes))
    lights = np.asarray([board.lights for board in boards])

    # find unique lights
    u, ui, uii, uc = np.unique_all(lights)

    # choose a random puzzle
    li = np.random.choice(u[uc == 1])

    inds = np.nonzero(lights == li)[0]
    assert len(inds) == 1
    ind = inds[0]
    board = boards[ind]

    from rich.console import Console

    console = Console()
    console.print(board)

    print(f"{board.lights}, {board.lights:08b}")

    puzzle = board.to_puzzle()
    console.print(puzzle)
    print(f"{puzzle.lights}, {puzzle.lights:08b}")

    return puzzle

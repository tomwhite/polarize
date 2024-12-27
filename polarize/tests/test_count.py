import numpy as np

from polarize.count import all_boards, count_puzzles
from polarize.model import ALL_DOMINOES


def test_all_boards():
    from rich.console import Console

    console = Console()

    dominoes = [ALL_DOMINOES[0], ALL_DOMINOES[3]]

    for board in all_boards(dominoes):
        # print(board)
        console.print(board)
        print(board.lights)

    boards = list(all_boards(dominoes))
    lights = np.asarray([board.lights for board in boards])

    print("Total boards:", len(boards))
    print(lights)

    u, ui, uii, uc = np.unique_all(lights)
    print(u)
    print(ui)
    print(uii)
    print(uc)

    # pick a non-unique solution at random and print the boards to see what we get
    print(uc[-1], u[-1], np.nonzero(lights == u[-1])[0])

    for ind in np.nonzero(lights == u[-1])[0]:
        board = boards[ind]
        console.print(board)
        print(f"{board.lights:08b}")

    # find unique lights
    print("unique puzzles")
    print(u[uc == 1])
    for li in u[uc == 1]:
        inds = np.nonzero(lights == li)[0]
        assert len(inds) == 1
        ind = inds[0]
        board = boards[ind]
        console.print(board)
        print(f"{board.lights}, {board.lights:08b}")


def test_count_puzzles():
    assert count_puzzles(1) == 0
    assert count_puzzles(2) == 64
    assert count_puzzles(3) == 488
    # assert count_puzzles(4) == 1032
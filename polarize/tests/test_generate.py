import numpy as np

from polarize.generate import all_boards, generate, layout
from polarize.model import ALL_DOMINOES, DominoOrientation
from polarize.solve import solve


def test_all_boards():
    from rich.console import Console

    console = Console()

    dominoes = [ALL_DOMINOES[0], ALL_DOMINOES[3]]

    for board in all_boards(n=4, dominoes=dominoes):
        # print(board)
        console.print(board)
        print(board.lights_int)

    boards = list(all_boards(n=4, dominoes=dominoes))
    lights = np.asarray([board.lights_int for board in boards])

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
        print(f"{board.lights_int:08b}")

    # find unique lights
    print("unique puzzles")
    print(u[uc == 1])
    for li in u[uc == 1]:
        inds = np.nonzero(lights == li)[0]
        assert len(inds) == 1
        ind = inds[0]
        board = boards[ind]
        console.print(board)
        print(f"{board.lights_int}, {board.lights_int:08b}")

def test_layout():
    dominoes = [ALL_DOMINOES[2], ALL_DOMINOES[7], ALL_DOMINOES[1]]
    board = layout(4, dominoes)
    assert board is not None


def test_generate():
    puzzle, solution = generate(4)
    solutions = solve(puzzle)
    assert len(solutions) == 1
    assert solutions[0].placed_dominoes == solution.placed_dominoes


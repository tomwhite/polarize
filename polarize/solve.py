from polarize.generate import all_boards

def solve(puzzle):
    solution_boards = []
    for board in all_boards(puzzle.n, puzzle.dominoes):
        if board.lights_int == puzzle.lights_int:
            solution_boards.append(board)
    return solution_boards
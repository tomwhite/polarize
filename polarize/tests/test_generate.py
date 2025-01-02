from polarize.generate import generate
from polarize.solve import solve

def test_generate():
    puzzle, solution = generate(4)
    solutions = solve(puzzle)
    assert len(solutions) == 1
    assert solutions[0].placed_dominoes == solution.placed_dominoes


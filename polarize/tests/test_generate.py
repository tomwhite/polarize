from polarize.generate import generate


def test_generate():
    puzzle, solution = generate()
    print(puzzle)

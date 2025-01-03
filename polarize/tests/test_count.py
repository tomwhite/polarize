from polarize.count import count_puzzles


def test_count_puzzles():
    assert count_puzzles(4, 1) == 96
    assert count_puzzles(4, 2) == 1824
    # assert count_puzzles(4, 3) == 12816
    # assert count_puzzles(4, 4) == 25240

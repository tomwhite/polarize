from itertools import permutations, product

from polarize.model import Board, PlacedDomino


def all_boards(dominoes):
    def coord_lt(coord1, coord2):
        y1, x1 = coord1
        y2, x2 = coord2
        return x1 + 4 * y1 < x2 + 4 * y2

    def coords_increasing(coords):
        for i in range(len(coords) - 1):
            if not coord_lt(coords[i], coords[i + 1]):
                return False
        return True

    for domino_perm in set(permutations(domino for domino in dominoes)):
        for coords in product(*(domino.places() for domino in domino_perm)):
            # skip if coords are not strictly increasing (in pos)
            if not coords_increasing(coords):
                continue

            try:
                board = Board()
                for domino, coord in zip(domino_perm, coords):
                    y, x = coord
                    pd = PlacedDomino(domino, x, y)
                    if board.can_add(pd):
                        board.add_domino(pd)
                    else:
                        raise ValueError()
                yield board
            except ValueError:
                pass  # try next coords

from dataclasses import dataclass
from enum import Enum
from itertools import product

import numpy as np

class PolarizingFilter(Enum):
    def __new__(cls, value, char):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.char = char
        return obj

    POS_45 = (1, "/")
    NEG_45 = (2, "\\")

DominoOrientation = Enum("DominoOrientation", ["HORIZONTAL", "VERTICAL"])

@dataclass(frozen=True)
class Domino:
    filter1: PolarizingFilter
    filter2: PolarizingFilter
    orientation: DominoOrientation

    def places(self, n=4):
        # return y, x values of where this domino can be placed on a board
        if self.orientation == DominoOrientation.HORIZONTAL:
            x_max, y_max = n - 1, n
        else:
            x_max, y_max = n, n - 1
        return product(range(y_max), range(x_max))

    @property
    def value(self):
        return ((self.orientation.value - 1) << 2) | ((self.filter2.value - 1) << 1) | (self.filter1.value - 1)

ALL_DOMINOES = [Domino(*p) for p in product(PolarizingFilter, PolarizingFilter, DominoOrientation)]

@dataclass(frozen=True)
class PlacedDomino:
    domino: Domino
    x: int  # across
    y: int  # down

class Board:
    def __init__(self, *placed_dominoes):
        self.values = np.zeros((4, 4), dtype=np.int8)
        self.n = 4  # assume board of size 4
        for placed_domino in placed_dominoes:
            self.add_domino(placed_domino)


    def add_domino(self, placed_domino):
        domino = placed_domino.domino
        x, y = placed_domino.x, placed_domino.y
        self.values[y, x] = domino.filter1.value
        if domino.orientation == DominoOrientation.HORIZONTAL:
            x2, y2 = x + 1, y
        else:
            x2, y2 = x, y + 1
        self.values[y2, x2] = domino.filter2.value

    def can_add(self, placed_domino):
        x, y = placed_domino.x, placed_domino.y
        if self.values[y, x] != 0:
            return False
        domino = placed_domino.domino
        if domino.orientation == DominoOrientation.HORIZONTAL:
            x2, y2 = x + 1, y
        else:
            x2, y2 = x, y + 1
        return self.values[y2, x2] == 0

    def on_board(self, x, y):
        """Return True if x, y is on the inner board (not outer edge or corners)"""
        return 0 < x <= self.n and 0 < y <= self.n

    def __str__(self):
        return str(self.values)
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

@dataclass
class Domino:
    filter1: PolarizingFilter
    filter2: PolarizingFilter
    orientation: DominoOrientation

ALL_DOMINOS = [Domino(*p) for p in product(PolarizingFilter, PolarizingFilter, DominoOrientation)]

@dataclass
class PlacedDomino:
    domino: Domino
    i: int
    j: int

class Board:
    def __init__(self, *placed_dominos):
        self.placed_dominos = placed_dominos
        self.values = np.zeros((4, 4), dtype=np.int8)
        for placed_domino in placed_dominos:
            self._add_domino(placed_domino)


    def _add_domino(self, placed_domino):
        domino = placed_domino.domino
        i = placed_domino.i
        j = placed_domino.j
        self.values[i, j] = domino.filter1.value
        if domino.orientation == DominoOrientation.HORIZONTAL:
            self.values[i + 1, j] = domino.filter2.value
        else:
            self.values[i, j + 1] = domino.filter2.value

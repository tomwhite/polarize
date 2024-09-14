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
class Board:
    values: np.ndarray
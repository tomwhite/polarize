from dataclasses import dataclass
from enum import Enum
from itertools import product

import numpy as np
from rich.text import Text

BLOCK = "\u2588"


class PolarizingFilter(Enum):
    """A polarizing filter with a set orientation."""
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
    """A domino is made up of two polarizing filters, and is oriented either
    horizontally or vertically."""
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
        return (
            ((self.orientation.value - 1) << 2)
            | ((self.filter2.value - 1) << 1)
            | (self.filter1.value - 1)
        )

    def __str__(self):
        if self.orientation == DominoOrientation.HORIZONTAL:
            return f"{self.filter1.char}{self.filter2.char}"
        else:
            return f"{self.filter1.char}\n{self.filter2.char}"


ALL_DOMINOES = [
    Domino(*p) for p in product(PolarizingFilter, PolarizingFilter, DominoOrientation)
]


class Puzzle:
    """A Polarize puzzle consists of lights and a set of dominoes."""

    def __init__(self, lights, dominoes):
        self.n = 4
        self.lights = lights
        self.dominoes = dominoes

    def __str__(self):
        return f"{self.lights:08b}, {self.dominoes}"

    def __rich__(self):
        text = Text()
        li = self.lights
        for y in range(6):
            for x in range(6):
                if 1 <= x <= 4 and 1 <= y <= 4:
                    text.append(".")
                elif x in (0, 5) and 1 <= y <= 4:
                    if (li >> (y + 2)) & 1:
                        text.append(BLOCK)
                    else:
                        text.append(BLOCK, style="#ffff00")
                elif y in (0, 5) and 1 <= x <= 4:
                    if (li >> (4 - x)) & 1:
                        text.append(BLOCK)
                    else:
                        text.append(BLOCK, style="#ffff00")
                else:
                    text.append(" ")
            text.append("\n")
        for i, domino in enumerate(self.dominoes):
            text.append(str(domino), style=f"reverse color({i + 1})")
            text.append("\n")
        return text


@dataclass(frozen=True)
class PlacedDomino:
    """A domino placed in a fixed position on a board."""
    domino: Domino
    x: int  # across
    y: int  # down

    @property
    def np_index(self):
        x, y = self.x, self.y
        if self.domino.orientation == DominoOrientation.HORIZONTAL:
            x2, y2 = x + 1, y
        else:
            x2, y2 = x, y + 1
        return np.array([y, y2]), np.array([x, x2])

class Board:
    """A Polarize board consists of a set of placed dominoes."""

    def __init__(self, *placed_dominoes):
        self.values = np.zeros((4, 4), dtype=np.int8)
        self.colours = np.zeros((4, 4), dtype=np.int8)
        self.n = 4  # assume board of size 4
        self.n_dominoes = 0
        self.placed_dominoes = placed_dominoes
        for placed_domino in placed_dominoes:
            self.add_domino(placed_domino)

    def can_add(self, placed_domino):
        return np.all(self.values[placed_domino.np_index] == 0)

    def add_domino(self, placed_domino):
        domino = placed_domino.domino
        self.values[placed_domino.np_index] = [domino.filter1.value, domino.filter2.value]
        self.colours[placed_domino.np_index] = self.n_dominoes + 1
        self.n_dominoes += 1

    def can_remove(self, placed_domino):
        domino = placed_domino.domino
        return np.all(self.values[placed_domino.np_index] == [domino.filter1.value, domino.filter2.value])

    def remove_domino(self, placed_domino):
        self.values[placed_domino.np_index] = 0
        self.colours[placed_domino.np_index] = 0
        self.n_dominoes -= 1

    def on_board(self, x, y):
        """Return True if x, y is on the inner board (not outer edge or corners)"""
        return 0 < x <= self.n and 0 < y <= self.n

    def lights(self):
        """Return an int encoding the lights, determined by the dominoes placed on this board."""
        lo = np.bitwise_or.reduce(self.values, axis=0) == 3
        lo = np.astype(lo, np.uint8)
        hi = np.bitwise_or.reduce(self.values, axis=1) == 3
        hi = np.astype(hi, np.uint8)
        return (
            hi[0] << 7
            | hi[1] << 6
            | hi[2] << 5
            | hi[3] << 4
            | lo[0] << 3
            | lo[1] << 2
            | lo[2] << 1
            | lo[3]
        )

    def to_puzzle(self):
        dominoes = [pd.domino for pd in self.placed_dominoes]
        return Puzzle(self.lights(), dominoes)

    def __str__(self):
        return str(self.values)

    def __rich__(self):
        text = Text()
        for y in range(4):
            for x in range(4):
                v = self.values[y, x]
                c = self.colours[y, x]
                if v == 0:
                    text.append(".")
                else:
                    text.append(PolarizingFilter(v).char, style=f"color({c})")
            text.append("\n")
        return text

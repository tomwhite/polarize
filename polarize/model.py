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

    def __init__(self, n, lights, dominoes):
        self.n = n
        self.lights = lights
        self.dominoes = dominoes

    @property
    def lights_int(self):
        return encode_lights(self.lights)

    def __str__(self):
        return f"{self.lights_int:016b}, {self.dominoes}"

    def __rich__(self):
        n = self.n
        text = Text()
        li = self.lights
        for y in range(n + 2):
            for x in range(n + 2):
                if 1 <= x <= n and 1 <= y <= n:
                    text.append(".")
                elif x in (0, n + 1) and 1 <= y <= n:
                    if li[y - 1] == 0:
                        text.append(BLOCK, style="#ffff00")
                    elif li[y - 1] == 1:
                        # ARYLIDE_YELLOW
                        text.append(BLOCK, style="#E9D66B")
                    else:
                        text.append(BLOCK)
                elif y in (0, n + 1) and 1 <= x <= n:
                    if li[n + (x - 1)] == 0:
                        text.append(BLOCK, style="#ffff00")
                    elif li[n + (x - 1)] == 1:
                        text.append(BLOCK, style="#E9D66B")
                    else:
                        text.append(BLOCK)
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

    def __init__(self, n=4):
        self.n = n
        self.values = np.zeros((self.n, self.n), dtype=np.int8)
        self.colours = np.zeros((self.n, self.n), dtype=np.int8)
        self.n_dominoes = 0
        self.placed_dominoes = []

    def can_add(self, placed_domino):
        try:
            return np.all(self.values[placed_domino.np_index] == 0)
        except IndexError:
            return False

    def add_domino(self, placed_domino):
        domino = placed_domino.domino
        self.values[placed_domino.np_index] = [
            domino.filter1.value,
            domino.filter2.value,
        ]
        self.colours[placed_domino.np_index] = self.n_dominoes + 1
        self.n_dominoes += 1
        self.placed_dominoes.append(placed_domino)

    def can_remove(self, placed_domino):
        domino = placed_domino.domino
        try:
            return np.all(
                self.values[placed_domino.np_index]
                == [domino.filter1.value, domino.filter2.value]
            )
        except IndexError:
            return False

    def remove_domino(self, placed_domino):
        self.values[placed_domino.np_index] = 0
        self.colours[placed_domino.np_index] = 0
        self.n_dominoes -= 1
        self.placed_dominoes.remove(placed_domino)

    def on_board(self, x, y):
        """Return True if x, y is on the inner board (not outer edge or corners)"""
        return 0 < x <= self.n and 0 < y <= self.n

    @property
    def lights(self):
        li = np.empty(self.n * 2, dtype=np.uint8)
        lo = np.bitwise_count(np.bitwise_or.reduce(self.values, axis=0))
        hi = np.bitwise_count(np.bitwise_or.reduce(self.values, axis=1))
        li[: self.n] = hi
        li[self.n :] = lo
        return li

    @property
    def lights_int(self):
        """Return an int encoding the lights, determined by the dominoes placed on this board."""
        return encode_lights(self.lights)

    @property
    def paths_horizontal(self):
        paths = np.zeros((self.n, self.n + 1), dtype=np.uint8)
        for i in range(self.n):
            paths[:, i + 1] = np.bitwise_or(paths[:, i], self.values[:, i])
        paths = np.bitwise_count(paths)
        return paths

    @property
    def paths_vertical(self):
        paths = np.zeros((self.n + 1, self.n), dtype=np.uint8)
        for i in range(self.n):
            paths[i + 1, :] = np.bitwise_or(paths[i, :], self.values[i, :])
        paths = np.bitwise_count(paths)
        return paths

    def to_puzzle(self):
        dominoes = [pd.domino for pd in self.placed_dominoes]
        return Puzzle(self.n, self.lights, dominoes)

    def __str__(self):
        return str(self.values)

    def __rich__(self):
        text = Text()
        for y in range(self.n):
            for x in range(self.n):
                v = self.values[y, x]
                c = self.colours[y, x]
                if v == 0:
                    text.append(".")
                else:
                    text.append(PolarizingFilter(v).char, style=f"color({c})")
            text.append("\n")
        return text


def encode_lights(lights):
    ret = 0
    for b in lights:
        ret = ret << 2
        ret = ret | int(b)
    return ret

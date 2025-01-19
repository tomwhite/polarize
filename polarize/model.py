from dataclasses import dataclass
from enum import Enum
import functools
from itertools import product
import json

import numpy as np
from rich.text import Text

BLOCK = "\u2588"


@functools.total_ordering
class Filter(Enum):
    """A polarizing filter fixed at a given angle."""

    def __new__(cls, value, char):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.char = char
        return obj

    POS_45 = (1, "/")
    NEG_45 = (2, "\\")

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


@functools.total_ordering
class Orientation(Enum):
    def __new__(cls, value, char):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.char = char
        return obj

    H = (1, "H")
    V = (2, "V")

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


@dataclass(frozen=True, order=True)
class Domino:
    """A domino is made up of two polarizing filters, and is oriented either
    horizontally or vertically."""

    orientation: Orientation
    filter1: Filter
    filter2: Filter

    def places(self, n=4):
        # return y, x values of where this domino can be placed on a board
        if self.orientation == Orientation.H:
            x_max, y_max = n - 1, n
        else:
            x_max, y_max = n, n - 1
        return product(range(y_max), range(x_max))

    @property
    def value(self):
        return (
            ((self.orientation.value - 1) << 2)
            | ((self.filter1.value - 1) << 1)
            | (self.filter2.value - 1)
        )

    def __str__(self):
        if self.orientation == Orientation.H:
            return f"{self.filter1.char}{self.filter2.char}"
        else:
            return f"{self.filter1.char}\n{self.filter2.char}"


ALL_DOMINOES = [
    Domino(*p) for p in product(Orientation, Filter, Filter)
]


class Puzzle:
    """A Polarize puzzle consists of lights and a multi-set of dominoes."""

    def __init__(self, n, lights, dominoes, initial_placed_dominoes, solution):
        # initial_placed_dominoes is used to arrange the dominoes on the off-board cells
        self.n = n
        self.lights = lights
        self.dominoes = dominoes
        self.initial_placed_dominoes = initial_placed_dominoes
        self.solution = solution

    @classmethod
    def from_json_str(cls, json_str):
        data = json.loads(json_str)
        return cls(n=data["n"], lights=data["lights"], dominoes=[ALL_DOMINOES[d] for d in data["dominoes"]], initial_placed_dominoes=[PlacedDomino(ALL_DOMINOES[d["domino"]],d["i"], d["j"]) for d in data["initial_placed_dominoes"]], solution=data["solution"])

    # TODO: reduce duplication
    @classmethod
    def from_json_file(cls, filename):
        data = json.load(filename)
        return cls(n=data["n"], lights=data["lights"], dominoes=[ALL_DOMINOES[d] for d in data["dominoes"]], initial_placed_dominoes=[PlacedDomino(ALL_DOMINOES[d["domino"]],d["i"], d["j"]) for d in data["initial_placed_dominoes"]], solution=data["solution"])

    def to_json_dict(self):
        return {
            "n": self.n,
            "lights": self.lights.tolist(),
            "dominoes": [d.value for d in self.dominoes],
            "initial_placed_dominoes": [{"domino": pd.domino.value, "i": pd.x, "j": pd.y} for pd in self.initial_placed_dominoes],
            "solution": self.solution,
        }
    
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
        if self.domino.orientation == Orientation.H:
            x2, y2 = x + 1, y
        else:
            x2, y2 = x, y + 1
        return np.array([y, y2]), np.array([x, x2])


class Board:
    """A Polarize board consists of a set of placed dominoes."""

    def __init__(self, n=4):
        self.n = n
        self.values = np.zeros((n, n), dtype=np.int8)
        self.colours = np.zeros((n, n), dtype=np.int8)
        self.n_dominoes = 0
        self.placed_dominoes = set()

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
        self.placed_dominoes.add(placed_domino)

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

        # find an initial placement of the dominoes (off the board)
        from polarize.generate import layout

        initial_board = layout(self.n, dominoes)
        return Puzzle(self.n, self.lights, dominoes, initial_board.placed_dominoes, self.values.tolist())

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
                    text.append(Filter(v).char, style=f"color({c})")
            text.append("\n")
        return text


def encode_lights(lights):
    ret = 0
    for b in lights:
        ret = ret << 2
        ret = ret | int(b)
    return ret

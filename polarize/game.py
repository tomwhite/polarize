"""
Polarize puzzle.
"""
import datetime
import math
from time import time

import arcade

from polarize.model import Board, PlacedDomino, ALL_DOMINOES

# Screen title and size
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 360
SCREEN_TITLE = "Polarize"

BLOCK_SIZE = 40
CELL_SIZE = 38

SPRITE_NAMES = {
    "/": "oblique_mirror",
    "\\": "reverse_oblique_mirror",
    "o": "mirror_ball",
}

# https://sashamaps.net/docs/resources/20-colors/
COLOURS = [
    arcade.color_from_hex_string(colour)
    for colour in [
        "#e6194B",
        "#3cb44b",
        "#ffe119",
        "#4363d8",
        "#f58231",
        "#42d4f4",
        "#f032e6",
        "#fabed4",
        "#469990",
        "#dcbeff",
        "#9A6324",
        "#fffac8",
        "#800000",
        "#aaffc3",
        "#000075",
        "#a9a9a9",
    ]
]


class BlockSprite(arcade.Sprite):
    """Block sprite"""

    def __init__(self, piece, name, scale=1):
        self.piece = piece
        self.name = name

        # TODO: need to package these and use :resources: ?
        self.image_file_name = f"sprites/{self.name}_tr.png"

        super().__init__(self.image_file_name, scale, hit_box_algorithm="None")


class PolarizePuzzle(arcade.Window):
    def __init__(self, puzzle):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.background = None

        self.puzzle = puzzle

        self.shape_list = None

        self.block_list = None

        arcade.set_background_color(arcade.color.WHITE)

    def setup(self):
        # self.background = arcade.load_texture("sprites/reflect.png")

        self.shape_list = arcade.ShapeElementList()

        n = self.puzzle.n
        for x in range(BLOCK_SIZE, BLOCK_SIZE * (n + 2), BLOCK_SIZE):
            line = arcade.create_line(
                x,
                flip_y(BLOCK_SIZE + 40),
                x,
                flip_y(BLOCK_SIZE * (n + 1) + 40),
                arcade.color.BLACK,
                1,
            )
            self.shape_list.append(line)
        for y in range(BLOCK_SIZE, BLOCK_SIZE * (n + 2), BLOCK_SIZE):
            line = arcade.create_line(
                BLOCK_SIZE,
                flip_y(y + 40),
                BLOCK_SIZE * (n + 1),
                flip_y(y + 40),
                arcade.color.BLACK,
                1,
            )
            self.shape_list.append(line)

        self.block_list = arcade.SpriteList()

        for i, domino in enumerate(self.puzzle.dominoes):
            print(i, domino)

        block = BlockSprite(None, "oblique_mirror")
        x, y = block_index_to_coord((i % 4) + 1, i // 4)
        y -= 240
        block.position = x, y
        self.block_list.append(block)


    def on_draw(self):
        self.clear()
        # arcade.draw_lrwh_rectangle_textured(
        #     0, flip_y(40), SCREEN_WIDTH, 40, self.background
        # )
        self.shape_list.draw()

        self.block_list.draw()

def block_index_to_coord(i, j, x_offset=0, y_offset=40):
    x = int(i) * BLOCK_SIZE + BLOCK_SIZE // 2 + x_offset
    y = flip_y(int(j) * BLOCK_SIZE + BLOCK_SIZE // 2 + y_offset)
    return x, y


def flip_y(y):
    # convenience to flip y coordinate
    return SCREEN_HEIGHT - y


def play_game():

    board = Board(
        PlacedDomino(ALL_DOMINOES[4], 0, 2),
        PlacedDomino(ALL_DOMINOES[5], 2, 2),
    )
    puzzle = board.to_puzzle()

    window = PolarizePuzzle(puzzle)
    window.setup()
    arcade.run()

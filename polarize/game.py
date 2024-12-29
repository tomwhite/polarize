"""
Polarize puzzle.
"""
import datetime
import math
from time import time

import arcade

from polarize.generate import generate
from polarize.model import Board, DominoOrientation, PlacedDomino, ALL_DOMINOES

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


from rich.console import Console

console = Console()


class DominoSprite(arcade.Sprite):
    """Domino sprite"""

    def __init__(self, domino, scale=1):
        self.domino = domino

        # TODO: need to package these and use :resources: ?
        self.image_file_name = f"sprites/domino_{domino.value}_tr.png"

        super().__init__(self.image_file_name, scale, hit_box_algorithm="None")


class PolarizePuzzle(arcade.Window):
    def __init__(self, puzzle):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.background = None

        self.puzzle = puzzle
        self.board = Board()

        self.shape_list = None
        self.light_list = None

        # domino sprites
        self.domino_list = None
        self.domino_cells = None

        # domino currently being held (dragged)
        self.held_domino = None
        self.held_domino_original_position = None

        # cell sprites
        self.cell_list = None
        # dict mapping cell to index on board
        self.cell_indexes = None

        arcade.set_background_color(arcade.color.WHITE)

        # TODO
        console.print(puzzle)

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

        self.light_list = arcade.SpriteList()
        li = self.puzzle.lights_bool
        i = 0
        for j in range(n):
            dark = li[j]
            colour = arcade.color.BLACK if dark else arcade.color.ELECTRIC_YELLOW
            for i in (0, 5):
                x, y = block_index_to_coord(i, j + 1)
                light = arcade.SpriteCircle(
                    CELL_SIZE // 2 - 4, colour
                )
                light.position = x, y
                self.light_list.append(light)

        for i in range(n):
            dark = li[4 + i]
            colour = arcade.color.BLACK if dark else arcade.color.ELECTRIC_YELLOW
            for j in (0, 5):
                x, y = block_index_to_coord(i + 1, j)
                light = arcade.SpriteCircle(
                    CELL_SIZE // 2 - 4, colour
                )
                light.position = x, y
                self.light_list.append(light)

        self.domino_list = arcade.SpriteList()
        self.domino_cells = {}

        self.cell_list: arcade.SpriteList = arcade.SpriteList()
        self.cell_indexes = {}

        for i, domino in enumerate(self.puzzle.dominoes):
            domino_sprite = DominoSprite(domino)
            x, y = block_index_to_coord(((2 * i) % 4) + 1, i // 2)
            y -= 240
            # correction since we want position to refer to center of first block in domino
            if domino.orientation == DominoOrientation.HORIZONTAL:
                x += (32 // 2)
            else:
                y -= (32 // 2)
            domino_sprite.position = x, y
            self.domino_list.append(domino_sprite)
            cell = arcade.SpriteSolidColor(
                CELL_SIZE, CELL_SIZE, arcade.color.ALICE_BLUE
            )
            cell.position = domino_sprite.position
            self.cell_list.append(cell)
            self.domino_cells[cell] = domino_sprite
        self.held_domino = None
        self.held_domnio_original_position = None

        for i in range(self.puzzle.n):
            for j in range(self.puzzle.n):
                cell = arcade.SpriteSolidColor(
                    CELL_SIZE, CELL_SIZE, arcade.color.ALICE_BLUE
                )
                self.cell_indexes[cell] = (i, j)
                x, y = block_index_to_coord(i + 1, j + 1)
                cell.position = x, y
                self.cell_list.append(cell)

    def on_draw(self):
        self.clear()
        # arcade.draw_lrwh_rectangle_textured(
        #     0, flip_y(40), SCREEN_WIDTH, 40, self.background
        # )
        self.shape_list.draw()
        self.light_list.draw()
        self.cell_list.draw()
        self.domino_list.draw()

    def pull_to_top(self, domino: arcade.Sprite):
        self.domino_list.remove(domino)
        self.domino_list.append(domino)

    def get_prev_cell(self, domino):
        for c, d in dict(self.domino_cells).items():
            if d == domino:
                return c
        return None

    def move_domino_to_cell(self, domino, cell):
        prev_cell = None
        for c, d in dict(self.domino_cells).items():
            if d == domino:
                prev_cell = c
                break
        self.domino_cells.pop(prev_cell)
        self.domino_cells[cell] = domino

        # update the board
        if prev_cell in self.cell_indexes:
            i, j = self.cell_indexes[prev_cell]
            # TODO
            # self.board.set_value(i + 1, j + 1, ".")

        if cell in self.cell_indexes:
            i, j = self.cell_indexes[cell]
            # TODO
            # self.board.set_value(i + 1, j + 1, self.held_block.piece)

    def on_mouse_press(self, x, y, button, key_modifiers):
        dominoes = arcade.get_sprites_at_point((x, y), self.domino_list)

        if len(dominoes) > 0:
            domino = dominoes[-1]  # they don't overlap, but get top one
            self.held_domino = domino
            self.held_domino_original_position = self.held_domino.position
            self.pull_to_top(self.held_domino)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        if self.held_domino is None:
            return

        cell, _ = arcade.get_closest_sprite(self.held_domino, self.cell_list)
        reset_position = True
        if arcade.check_for_collision(self.held_domino, cell):
            x = cell.center_x
            y = cell.center_y
            # correction since we want position to refer to center of first block in domino
            if self.held_domino.domino.orientation == DominoOrientation.HORIZONTAL:
                x += (32 // 2)
            else:
                y -= (32 // 2)
            self.held_domino.position = x, y
            prev_cell = self.get_prev_cell(self.held_domino)
            if cell != prev_cell:
                print("moved", prev_cell, cell)
    
                if prev_cell is not None:
                    self.domino_cells.pop(prev_cell)

                if prev_cell in self.cell_indexes:
                    i, j = self.cell_indexes[prev_cell]
                    print("prev", i, j)
                    placed_domino = PlacedDomino(self.held_domino.domino, i, j)
                    if self.board.can_remove(placed_domino):
                        self.board.remove_domino(placed_domino)

    
                if cell in self.cell_indexes:
                    i, j = self.cell_indexes[cell]
                    print("new", i, j)
                    placed_domino = PlacedDomino(self.held_domino.domino, i, j)
                    if self.board.can_add(placed_domino):
                        self.board.add_domino(placed_domino)
                        reset_position = False

                    self.domino_cells[cell] = self.held_domino
            # if cell not in self.domino_cells:  # not occupied
            #     self.domino_cells[cell] = self.held_domino
            #     self.move_domino_to_cell(self.held_domino, cell)
            #     reset_position = False

                print(self.board)
                console.print(self.board)
                if self.board.lights == self.puzzle.lights:
                    print("YOU SOLVED IT!")
        if reset_position:
            self.held_domino.position = self.held_domino_original_position

        self.held_domino = None

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        if self.held_domino:
            self.held_domino.center_x += dx
            self.held_domino.center_y += dy

def block_index_to_coord(i, j, x_offset=0, y_offset=40):
    x = int(i) * BLOCK_SIZE + BLOCK_SIZE // 2 + x_offset
    y = flip_y(int(j) * BLOCK_SIZE + BLOCK_SIZE // 2 + y_offset)
    return x, y


def flip_y(y):
    # convenience to flip y coordinate
    return SCREEN_HEIGHT - y


def play_game():

    puzzle = generate(3)
    # board = Board(
    #     PlacedDomino(ALL_DOMINOES[4], 0, 2),
    #     PlacedDomino(ALL_DOMINOES[5], 2, 2),
    # )
    # puzzle = board.to_puzzle()

    window = PolarizePuzzle(puzzle)
    window.setup()
    arcade.run()

"""
Polarize puzzle.
"""

import arcade
from rich.console import Console

from polarize.generate import generate
from polarize.model import Board, DominoOrientation, PlacedDomino

# Screen title and size
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 440
SCREEN_TITLE = "Polarize"

BLOCK_SIZE = 40
CELL_SIZE = 38


console = Console()


class DominoSprite(arcade.Sprite):
    """Domino sprite"""

    def __init__(self, domino, scale=1):
        self.domino = domino

        # TODO: need to package these and use :resources: ?
        self.image_file_name = f"sprites/domino_{domino.value}_tr.png"

        super().__init__(self.image_file_name, scale, hit_box_algorithm="None")


class PolarizePuzzle(arcade.Window):
    def __init__(self, puzzle, solution):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.background = None

        self.puzzle = puzzle
        self.solution = solution
        self.board = Board()

        self.shape_list = None
        self.light_list = None
        self.path_list = None

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

        self.game_over = False

        arcade.set_background_color(arcade.color.BLACK_OLIVE)

        # TODO
        console.print(puzzle)

    def setup(self):
        self.shape_list = arcade.ShapeElementList()

        n = self.puzzle.n
        for x in range(BLOCK_SIZE, BLOCK_SIZE * (n + 2), BLOCK_SIZE):
            line = arcade.create_line(
                x,
                flip_y(BLOCK_SIZE + 40),
                x,
                flip_y(BLOCK_SIZE * (n + 1) + 40),
                arcade.color.WHITE,
                1,
            )
            self.shape_list.append(line)
        for y in range(BLOCK_SIZE, BLOCK_SIZE * (n + 2), BLOCK_SIZE):
            line = arcade.create_line(
                BLOCK_SIZE,
                flip_y(y + 40),
                BLOCK_SIZE * (n + 1),
                flip_y(y + 40),
                arcade.color.WHITE,
                1,
            )
            self.shape_list.append(line)

        self.light_list = arcade.SpriteList()

        li = self.puzzle.lights
        i = 0
        for j in range(n):
            if li[j] == 0:
                colour = arcade.color.ELECTRIC_YELLOW
            elif li[j] == 1:
                colour = arcade.color.MIKADO_YELLOW
            else:
                colour = arcade.color.BLACK
            for i in (0, 5):
                x, y = block_index_to_coord(i, j + 1)
                if i == 0:
                    light = arcade.SpriteSolidColor(
                        CELL_SIZE, CELL_SIZE // 4, arcade.color.ELECTRIC_YELLOW
                    )
                else:
                    light = arcade.SpriteCircle(CELL_SIZE // 2 - 4, colour)
                light.position = x, y
                self.light_list.append(light)

        for i in range(n):
            if li[4 + i] == 0:
                colour = arcade.color.ELECTRIC_YELLOW
            elif li[4 + i] == 1:
                colour = arcade.color.MIKADO_YELLOW
            else:
                colour = arcade.color.BLACK
            for j in (0, 5):
                x, y = block_index_to_coord(i + 1, j)
                if j == 0:
                    light = arcade.SpriteSolidColor(
                        CELL_SIZE // 4, CELL_SIZE, arcade.color.ELECTRIC_YELLOW
                    )
                else:
                    light = arcade.SpriteCircle(CELL_SIZE // 2 - 4, colour)
                light.position = x, y
                self.light_list.append(light)

        self.path_list = arcade.ShapeElementList()
        width = 10
        paths_horizontal = self.solution.paths_horizontal
        paths_vertical = self.solution.paths_vertical
        for i in range(n + 1):
            for j in range(n):
                if paths_horizontal[j, i] == 0:
                    colour = arcade.color.ELECTRIC_YELLOW
                elif paths_horizontal[j, i] == 1:
                    colour = arcade.color.MIKADO_YELLOW
                else:
                    colour = None

                if colour is not None:
                    x, y = block_index_to_coord(i, j + 1)
                    x0, y0 = x - 1, y
                    x1, y1 = x + CELL_SIZE + 1, y
                    line = arcade.create_line(x0, y0, x1, y1, colour, width)
                    self.path_list.append(line)

        for i in range(n):
            for j in range(n + 1):
                if paths_vertical[j, i] == 0:
                    colour = arcade.color.ELECTRIC_YELLOW
                elif paths_vertical[j, i] == 1:
                    colour = arcade.color.MIKADO_YELLOW
                else:
                    colour = None

                if colour is not None:
                    x, y = block_index_to_coord(i + 1, j)
                    x0, y0 = x, y + 1
                    x1, y1 = x, y - CELL_SIZE - 1
                    line = arcade.create_line(x0, y0, x1, y1, colour, width)
                    self.path_list.append(line)

        self.domino_list = arcade.SpriteList()
        self.domino_cells = {}

        self.cell_list: arcade.SpriteList = arcade.SpriteList()
        self.cell_indexes = {}

        # off board
        for i in range(self.puzzle.n + 2):
            for j in range(self.puzzle.n + 2):
                cell = arcade.SpriteSolidColor(
                    CELL_SIZE + 1, CELL_SIZE + 1, arcade.color.LIGHT_GRAY
                )
                x, y = block_index_to_coord(i, j)
                y -= 240
                cell.position = x, y
                self.cell_list.append(cell)

        def sort_vert_first(domino):
            return 0 if domino.orientation is DominoOrientation.VERTICAL else 1

        sorted_dominoes = sorted(self.puzzle.dominoes, key=sort_vert_first)
        i, j = 0, 0
        for domino in sorted_dominoes:
            if domino.orientation is DominoOrientation.VERTICAL and i > 5:
                i = 0
                j += 2
            elif domino.orientation is DominoOrientation.HORIZONTAL and i > 4:
                i = 0
                j += 2

            domino_sprite = DominoSprite(domino)
            x, y = block_index_to_coord(i, j)
            y -= 240
            # correction since we want position to refer to center of first block in domino
            if domino.orientation == DominoOrientation.HORIZONTAL:
                x += BLOCK_SIZE // 2
            else:
                y -= BLOCK_SIZE // 2
            domino_sprite.position = x, y
            self.domino_list.append(domino_sprite)

            cell, _ = arcade.get_closest_sprite(domino_sprite, self.cell_list)
            self.domino_cells[cell] = domino_sprite

            # update next i, j
            if domino.orientation is DominoOrientation.VERTICAL:
                i += 1
            else:
                i += 2

        self.held_domino = None
        self.held_domnio_original_position = None

        # board cells
        for i in range(self.puzzle.n):
            for j in range(self.puzzle.n):
                cell = arcade.SpriteSolidColor(
                    CELL_SIZE + 1, CELL_SIZE + 1, arcade.color.LIGHT_GRAY
                )
                self.cell_indexes[cell] = (i, j)
                x, y = block_index_to_coord(i + 1, j + 1)
                cell.position = x, y
                self.cell_list.append(cell)

        self.game_over = False

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "POLARIZE",
            0,
            SCREEN_HEIGHT - 30,
            arcade.color.ELECTRIC_YELLOW,
            20,
            width=SCREEN_WIDTH,
            align="center",
        )
        # arcade.draw_lrwh_rectangle_textured(
        #     0, flip_y(40), SCREEN_WIDTH, 40, self.background
        # )
        self.light_list.draw()
        if self.game_over:
            self.path_list.draw()
        else:
            self.shape_list.draw()
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

    def on_mouse_press(self, x, y, button, key_modifiers):
        if self.game_over:
            return

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
                x += 32 // 2
            else:
                y -= 32 // 2
            self.held_domino.position = x, y
            prev_cell = self.get_prev_cell(self.held_domino)
            if cell != prev_cell:
                if prev_cell is not None:
                    self.domino_cells.pop(prev_cell)

                if prev_cell in self.cell_indexes:
                    i, j = self.cell_indexes[prev_cell]
                    placed_domino = PlacedDomino(self.held_domino.domino, i, j)
                    if self.board.can_remove(placed_domino):
                        self.board.remove_domino(placed_domino)

                if cell in self.cell_indexes:
                    i, j = self.cell_indexes[cell]
                    placed_domino = PlacedDomino(self.held_domino.domino, i, j)
                    if self.board.can_add(placed_domino):
                        self.board.add_domino(placed_domino)
                        reset_position = False

                    self.domino_cells[cell] = self.held_domino
                else:
                    self.domino_cells[cell] = self.held_domino
                    self.move_domino_to_cell(self.held_domino, cell)
                    reset_position = False

                if self.board.lights_int == self.puzzle.lights_int:
                    self.game_over = True
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


def play_game(pieces):
    puzzle, solution = generate(pieces)
    window = PolarizePuzzle(puzzle, solution)
    window.setup()
    arcade.run()

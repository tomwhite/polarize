// Constants

// Scale sprites so we can have a high resolution for other graphics (text, lines)
const SCALE = 2;

const SCREEN_WIDTH = 240 * SCALE;
const SCREEN_HEIGHT = 440 * SCALE;

const BLOCK_SIZE = 40 * SCALE;
const CELL_SIZE = 38 * SCALE;

const LIGHT_WIDTH = 10 * SCALE;
const SPOT_RADIUS = 12 * SCALE;

// Names are from https://api.arcade.academy/en/2.6.17/arcade.color.html
const WHITE = 0xffffff;
const BLACK = 0x000000;
const BACKGROUND_COLOUR = 0x1484cd; // sky colour
const CELL_COLOUR = 0xb3c6d2; // blue-ish grey
const LIGHT_COLOUR = 0xffff00; // ELECTRIC_YELLOW
const DIM_LIGHT_COLOUR = 0xffc40c; // MIKADO_YELLOW
const DARK_COLOUR = BLACK;

// Model classes

const Filter = Object.freeze({
  // values from here are used in the board values
  POS_45: 1,
  NEG_45: 2,
});

const Orientation = Object.freeze({
  H: Symbol("H"),
  V: Symbol("V"),
});

class Domino {
  constructor(value, orientation, filter1, filter2) {
    this.value = value;
    this.orientation = orientation;
    this.filter1 = filter1;
    this.filter2 = filter2;
  }
}

// order is the same as Python
const ALL_DOMINOES = [
  new Domino(0, Orientation.H, Filter.POS_45, Filter.POS_45),
  new Domino(1, Orientation.H, Filter.POS_45, Filter.NEG_45),
  new Domino(2, Orientation.H, Filter.NEG_45, Filter.POS_45),
  new Domino(3, Orientation.H, Filter.NEG_45, Filter.NEG_45),
  new Domino(4, Orientation.V, Filter.POS_45, Filter.POS_45),
  new Domino(5, Orientation.V, Filter.POS_45, Filter.NEG_45),
  new Domino(6, Orientation.V, Filter.NEG_45, Filter.POS_45),
  new Domino(7, Orientation.V, Filter.NEG_45, Filter.NEG_45),
];

class Puzzle {
  constructor(data) {
    this.n = data.n;
    this.lights = data.lights;
    this.dominoes = data.dominoes.map((d) => ALL_DOMINOES[d]);
    this.initial_placed_dominoes = data.initial_placed_dominoes.map(
      (d) => new PlacedDomino(ALL_DOMINOES[d.domino], d.i, d.j)
    );
    this.solution = new Board(data.n, data.solution);
  }
}

class PlacedDomino {
  constructor(domino, i, j) {
    this.domino = domino;
    this.i = i;
    this.j = j;
  }
  index() {
    let [i1, j1] = [this.i, this.j];
    let i2, j2;
    if (this.domino.orientation == Orientation.H) {
      [i2, j2] = [this.i + 1, this.j];
    } else {
      [i2, j2] = [this.i, this.j + 1];
    }
    return [
      [i1, j1],
      [i2, j2],
    ];
  }
}

class Board {
  constructor(n = 4, values = zeros2D(n, n)) {
    this.n = n;
    this.values = values;
  }

  canAdd(placedDomino) {
    const n = this.n;
    const [[i1, j1], [i2, j2]] = placedDomino.index();
    if (0 <= i1 && i1 < n && 0 <= j1 && j1 < n) {
      if (0 <= i2 && i2 < n && 0 <= j2 && j2 < n) {
        return this.values[j1][i1] == 0 && this.values[j2][i2] == 0;
      }
    }
    return false;
  }

  add(placedDomino) {
    const [[i1, j1], [i2, j2]] = placedDomino.index();
    this.values[j1][i1] = placedDomino.domino.filter1;
    this.values[j2][i2] = placedDomino.domino.filter2;
  }

  canRemove(placedDomino) {
    const n = this.n;
    const [[i1, j1], [i2, j2]] = placedDomino.index();
    if (0 <= i1 && i1 < n && 0 <= j1 && j1 < n) {
      if (0 <= i2 && i2 < n && 0 <= j2 && j2 < n) {
        return (
          this.values[j1][i1] == placedDomino.domino.filter1 &&
          this.values[j2][i2] == placedDomino.domino.filter2
        );
      }
    }
    return false;
  }

  remove(placedDomino) {
    const [[i1, j1], [i2, j2]] = placedDomino.index();
    this.values[j1][i1] = 0;
    this.values[j2][i2] = 0;
  }

  lights() {
    const n = this.n;
    const li = new Array(n * 2).fill(0);
    // bitwise-or for axis=0
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        li[i + n] = li[i + n] | this.values[j][i];
      }
    }
    // bitwise-or for axis=1
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        li[j] = li[j] | this.values[j][i];
      }
    }
    // bitwise-count
    return li.map(bitwise_count);
  }

  pathsHorizontal() {
    const n = this.n;
    const paths = zeros2D(n, n + 1);
    // bitwise-or for axis=0
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        paths[j][i + 1] = paths[j][i] | this.values[j][i];
      }
    }
    // bitwise-count
    for (let i = 0; i < n + 1; i++) {
      for (let j = 0; j < n; j++) {
        paths[j][i] = bitwise_count(paths[j][i]);
      }
    }
    return paths;
  }

  pathsVertical() {
    const n = this.n;
    const paths = zeros2D(n + 1, n);
    // bitwise-or for axis=0
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        paths[j + 1][i] = paths[j][i] | this.values[j][i];
      }
    }
    // bitwise-count
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n + 1; j++) {
        paths[j][i] = bitwise_count(paths[j][i]);
      }
    }
    return paths;
  }
}

function zeros2D(m, n) {
  return Array.from(Array(m), () => Array(n).fill(0));
}

function bitwise_count(n) {
  let c = 0;
  while (n) {
    c += n & 1;
    n = n >> 1;
  }
  return c;
}

// Drawing functions

function blockIndexToCoord(i, j, y_offset = BLOCK_SIZE) {
  const x = i * BLOCK_SIZE + BLOCK_SIZE / 2;
  const y = j * BLOCK_SIZE + BLOCK_SIZE / 2;
  return [x, y + y_offset];
}

function light_to_colour(li) {
  if (li == 0) {
    return LIGHT_COLOUR;
  } else if (li == 1) {
    return DIM_LIGHT_COLOUR;
  } else {
    return DARK_COLOUR;
  }
}

function drawDomino(graphics, domino) {
  const BLOCK_H = BLOCK_SIZE / 2;
  const BLOCK_3Q = BLOCK_SIZE + BLOCK_H;
  const CIRCLE_R = 14 * SCALE;
  const OFF1 = BLOCK_H - CIRCLE_R;
  const OFF2 = BLOCK_H + CIRCLE_R;

  let dx, dy;
  if (domino.orientation == Orientation.H) {
    [dx, dy] = [BLOCK_SIZE, 0];
  } else {
    [dx, dy] = [0, BLOCK_SIZE];
  }

  graphics.clear();
  graphics.lineStyle(3 * SCALE, BLACK);
  graphics.fillStyle(WHITE);

  // joining lines
  if (domino.orientation == Orientation.H) {
    graphics.lineBetween(BLOCK_H, OFF1, BLOCK_3Q, OFF1);
    graphics.lineBetween(BLOCK_H, OFF2, BLOCK_3Q, OFF2);
  } else {
    graphics.lineBetween(OFF1, BLOCK_H, OFF1, BLOCK_3Q);
    graphics.lineBetween(OFF2, BLOCK_H, OFF2, BLOCK_3Q);
  }

  // circles
  graphics.fillCircle(BLOCK_H, BLOCK_H, CIRCLE_R);
  graphics.fillCircle(BLOCK_H + dx, BLOCK_H + dy, CIRCLE_R);
  graphics.strokeCircle(BLOCK_H, BLOCK_H, CIRCLE_R);
  graphics.strokeCircle(BLOCK_H + dx, BLOCK_H + dy, CIRCLE_R);

  // filters
  const A = (10 - 3) * SCALE;
  const B = (30 - 3) * SCALE;
  const C = (10 + 3) * SCALE;
  const D = (30 + 3) * SCALE;
  if (domino.filter1 == Filter.POS_45) {
    graphics.lineBetween(A, B, B, A);
    graphics.lineBetween(C, D, D, C);
  } else {
    graphics.lineBetween(C, A, D, B);
    graphics.lineBetween(A, C, B, D);
  }
  if (domino.filter2 == Filter.POS_45) {
    graphics.lineBetween(A + dx, B + dy, B + dx, A + dy);
    graphics.lineBetween(C + dx, D + dy, D + dx, C + dy);
  } else {
    graphics.lineBetween(C + dx, A + dy, D + dx, B + dy);
    graphics.lineBetween(A + dx, C + dy, B + dx, D + dy);
  }
}

function drawLights(n, lightsGraphics, puzzle, board_y_offset) {
  li = puzzle.lights;
  // TODO: make the following more consistent
  let i = 0;
  for (let j = 0; j < n; j++) {
    let [x, y] = blockIndexToCoord(i, j, board_y_offset);
    // arrow
    lightsGraphics.fillStyle(LIGHT_COLOUR);
    const triangle = new Phaser.Geom.Polygon([
      BLOCK_SIZE - 1.5 * LIGHT_WIDTH,
      BLOCK_SIZE / 2 + LIGHT_WIDTH / 2 + y,
      BLOCK_SIZE - 1.5 * LIGHT_WIDTH,
      BLOCK_SIZE + BLOCK_SIZE / 2 - LIGHT_WIDTH / 2 + y,
      BLOCK_SIZE,
      BLOCK_SIZE + y,
    ]);
    lightsGraphics.fillPoints(triangle.points, true);
    // line
    lightsGraphics.lineStyle(LIGHT_WIDTH, LIGHT_COLOUR);
    lightsGraphics.lineBetween(
      LIGHT_WIDTH,
      BLOCK_SIZE + y,
      BLOCK_SIZE - LIGHT_WIDTH,
      BLOCK_SIZE + y
    );
    // spot
    i = n + 1;
    [x, y] = blockIndexToCoord(i, j, board_y_offset);
    lightsGraphics.fillStyle(light_to_colour(li[j]));
    lightsGraphics.fillCircle(x, BLOCK_SIZE + y, SPOT_RADIUS);
  }
  let j = 0;
  for (let i = 0; i < n; i++) {
    let [x, y] = blockIndexToCoord(i, j, board_y_offset);
    // arrow
    lightsGraphics.fillStyle(LIGHT_COLOUR);
    const triangle = new Phaser.Geom.Polygon([
      BLOCK_SIZE / 2 + LIGHT_WIDTH / 2 + x,
      BLOCK_SIZE - 1.5 * LIGHT_WIDTH + board_y_offset,
      BLOCK_SIZE + BLOCK_SIZE / 2 - LIGHT_WIDTH / 2 + x,
      BLOCK_SIZE - 1.5 * LIGHT_WIDTH + board_y_offset,
      BLOCK_SIZE + x,
      BLOCK_SIZE + board_y_offset,
    ]);
    lightsGraphics.fillPoints(triangle.points, true);
    // line
    lightsGraphics.lineStyle(LIGHT_WIDTH, LIGHT_COLOUR);
    lightsGraphics.lineBetween(
      BLOCK_SIZE + x,
      LIGHT_WIDTH + board_y_offset,
      BLOCK_SIZE + x,
      BLOCK_SIZE - LIGHT_WIDTH + board_y_offset
    );
    // spot
    j = n;
    [x, y] = blockIndexToCoord(i, j, board_y_offset);
    lightsGraphics.fillStyle(light_to_colour(li[n + i]));
    lightsGraphics.fillCircle(BLOCK_SIZE + x, BLOCK_SIZE + y, SPOT_RADIUS);
  }
}

function drawLightPaths(n, lightPathGraphics, solution, board_y_offset) {
  // iterate over colours from dark to light, so darker ones are at back
  const pathsHorizontal = solution.pathsHorizontal();
  const pathsVertical = solution.pathsVertical();
  const colours = [DARK_COLOUR, DIM_LIGHT_COLOUR, LIGHT_COLOUR];
  for (const c of colours) {
    for (let i = 0; i < n + 1; i++) {
      for (let j = 0; j < n; j++) {
        const colour = light_to_colour(pathsHorizontal[j][i]);
        if (colour == c) {
          // TODO: can we change j + 1 to j?
          const [x0, y0] = blockIndexToCoord(i, j + 1, board_y_offset);
          const [x1, y1] = blockIndexToCoord(i + 1, j + 1, board_y_offset);
          lightPathGraphics.lineStyle(LIGHT_WIDTH, colour);
          lightPathGraphics.lineBetween(x0, y0, x1, y1);
        }
      }
    }
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n + 1; j++) {
        const colour = light_to_colour(pathsVertical[j][i]);
        if (colour == c) {
          // TODO: can we change i + 1 to i?
          const [x0, y0] = blockIndexToCoord(i + 1, j, board_y_offset);
          const [x1, y1] = blockIndexToCoord(i + 1, j + 1, board_y_offset);
          lightPathGraphics.lineStyle(LIGHT_WIDTH, colour);
          lightPathGraphics.lineBetween(x0, y0, x1, y1);
        }
      }
    }
  }
}

// Utility functions

// Format a date in ISO format (YYYY-MM-DD) according to local time
// From https://stackoverflow.com/a/50130338
function formatDate(date) {
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000)
    .toISOString()
    .split("T")[0];
}

// Return "today" in YYYY-MM-DD
// Allow overriding with url param ?date=YYYY-MM-DD
function getEffectiveDate() {
  const urlParams = new URLSearchParams(window.location.search);
  const dateParam = urlParams.get("date");
  return dateParam ? dateParam : formatDate(new Date());
}

// Scenes

class PlayScene extends Phaser.Scene {
  constructor() {
    super({ key: "PlayScene" });
  }

  preload() {
    const today = getEffectiveDate();
    this.load.image("help", "sprites/help.png");
    this.load.json("puzzle", `puzzles/puzzle-${today}.json`);
  }

  create() {
    const puzzle = new Puzzle(this.cache.json.get("puzzle"));
    console.log(puzzle);
    const solution = puzzle.solution;
    const n = puzzle.n;
    const board = new Board();
    const offBoard = new Board();
    const board_y_offset = BLOCK_SIZE;

    let gameOver = false;
    //   let seenFirstMove = false;

    // Title
    const titleStyle = {
      fontFamily: "monospace",
      fontSize: 30 * SCALE,
      color: "yellow",
      padding: {
        bottom: 2,
      },
    };
    this.add
      .text(SCREEN_WIDTH / 2, BLOCK_SIZE / 2, "POLARIZE", titleStyle)
      .setOrigin(0.5);

    // Lights
    const lightsGraphics = this.add.graphics();
    drawLights(n, lightsGraphics, puzzle, board_y_offset);

    //   // Board lines
    //   const boardGraphics = this.add.graphics();
    //   drawBoardLines(n, boardGraphics, board_y_offset);

    // Light paths
    const lightPathGraphics = this.add.graphics();
    lightPathGraphics.visible = false;
    drawLightPaths(n, lightPathGraphics, solution, board_y_offset);

    // Cells (board)
    const cellGraphics = this.add.graphics();
    cellGraphics.fillStyle(CELL_COLOUR);
    for (var i = 0; i < n; i++) {
      for (var j = 0; j < n; j++) {
        const [x, y] = blockIndexToCoord(i + 1, j + 1);
        cellGraphics.fillRect(
          x - CELL_SIZE / 2,
          y - CELL_SIZE / 2,
          CELL_SIZE,
          CELL_SIZE
        );
      }
    }

    // Cells (off board)
    cellGraphics.fillStyle(CELL_COLOUR);
    for (var i = 0; i < n; i++) {
      for (var j = 0; j < n - 1; j++) {
        // TODO: clearer way of specifiying offset
        const [x, y] = blockIndexToCoord(i + 1, j + 1, BLOCK_SIZE * (n + 2));
        cellGraphics.fillRect(
          x - CELL_SIZE / 2,
          y - CELL_SIZE / 2,
          CELL_SIZE,
          CELL_SIZE
        );
      }
    }

    // Dominoes
    const dominoGraphics = this.make.graphics({ x: 0, y: 0, add: false });
    for (const pd of puzzle.initial_placed_dominoes) {
      offBoard.add(pd);
      const domino = pd.domino;
      drawDomino(dominoGraphics, domino);
      const dominoName = `domino_${domino.value}`;
      // TODO: make this a bit more concise
      if (domino.orientation == Orientation.H) {
        dominoGraphics.generateTexture(dominoName, BLOCK_SIZE * 2, BLOCK_SIZE);
      } else {
        dominoGraphics.generateTexture(dominoName, BLOCK_SIZE, BLOCK_SIZE * 2);
      }

      // TODO: arithmetic is a mess here again
      let [x, y] = blockIndexToCoord(
        pd.i + 1,
        pd.j,
        BLOCK_SIZE * (n + 2) + board_y_offset
      );
      const dominoSprite = this.add
        .image(x - CELL_SIZE / 2, y - CELL_SIZE / 2, dominoName)
        .setInteractive();
      dominoSprite.setOrigin(0, 0);
      dominoSprite.setData("domino", domino);
      dominoSprite.setData("board", offBoard);
      dominoSprite.setData("placedDomino", pd);
      this.input.setDraggable(dominoSprite);
    }

    // Help button
    // let [x, y] = blockIndexToCoord(5, 0);
    // const help = this.add.image(x, y, "help").setInteractive();
    // help.setScale(SCALE);
    // help.on("pointerup", (e) => {
    //   this.scene.setVisible(false, "PlayScene");
    //   this.scene.launch("MenuScene");
    //   this.scene.pause();
    // });

    this.input.on(
      "dragstart",
      function (pointer, gameObject) {
        // make sure domino being dragged is on top
        this.children.bringToTop(gameObject);
      },
      this
    );

    this.input.on("drag", function (pointer, gameObject, dragX, dragY) {
      // update image coordinates as it is dragged
      gameObject.x = dragX;
      gameObject.y = dragY;
    });

    this.input.on(
      "dragend",
      function (pointer, gameObject, dropped) {
        // snap to board coordinates
        const x = Phaser.Math.Snap.To(gameObject.x, BLOCK_SIZE);
        const y = Phaser.Math.Snap.To(gameObject.y, BLOCK_SIZE);
        // find board index
        i = x / BLOCK_SIZE - 1;
        j = y / BLOCK_SIZE - 2;
        // find whether the main board or the off board is the target
        let targetBoard;
        if (j < 5) {
          targetBoard = board;
        } else {
          targetBoard = offBoard;
          j -= 5;
        }
        // remove domino from board if already on there
        const prevBoard = gameObject.data.get("board");
        const prevPlacedDomino = gameObject.data.get("placedDomino");
        if (prevPlacedDomino !== undefined) {
          if (prevBoard.canRemove(prevPlacedDomino)) {
            prevBoard.remove(prevPlacedDomino);
          }
        }
        // try to add domino to board in new position
        const domino = gameObject.data.get("domino");
        const newPlacedDomino = new PlacedDomino(domino, i, j);
        if (targetBoard.canAdd(newPlacedDomino)) {
          // can add to board
          targetBoard.add(newPlacedDomino);
          gameObject.setData("board", targetBoard);
          gameObject.setData("placedDomino", newPlacedDomino);
          gameObject.x = x;
          gameObject.y = y;
        } else {
          // cannot add to board - reset to previous
          if (prevPlacedDomino !== undefined) {
            prevBoard.add(prevPlacedDomino);
          }
          gameObject.x = gameObject.input.dragStartX;
          gameObject.y = gameObject.input.dragStartY;
        }
        console.log(board.values);
        console.log(board.lights());
        console.log(offBoard.values);
        if (JSON.stringify(board.lights()) == JSON.stringify(puzzle.lights)) {
          cellGraphics.visible = false;
          lightPathGraphics.visible = true;
          gameOver = true;
          // disable dragging
          let images = this.children.list.filter(
            (x) => x instanceof Phaser.GameObjects.Image
          );
          images.forEach((image) =>
            image.input ? this.input.setDraggable(image, false) : null
          );
        }
      },
      this
    );
  }
}

const config = {
  type: Phaser.AUTO,
  width: SCREEN_WIDTH,
  height: SCREEN_HEIGHT,
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH,
  },
  backgroundColor: BACKGROUND_COLOUR,
  scene: [PlayScene],
};

const game = new Phaser.Game(config);

// Constants

// Scale sprites so we can have a high resolution for other graphics (text, lines)
const SCALE = 2;

const SCREEN_WIDTH = 240 * SCALE;
const SCREEN_HEIGHT = 440 * SCALE;

const BLOCK_SIZE = 40 * SCALE;
const CELL_SIZE = 38 * SCALE;

const LIGHT_WIDTH = 10 * SCALE;
const SPOT_RADIUS = 12 * SCALE;

const FILTER_R = 14 * SCALE;

const BLOCK_H = BLOCK_SIZE / 2;
const BLOCK_3Q = BLOCK_SIZE + BLOCK_H;

// Names are from https://api.arcade.academy/en/2.6.17/arcade.color.html
const WHITE = 0xffffff;
const BLACK = 0x000000;
const BACKGROUND_COLOUR = 0x1484cd; // sky colour
const CELL_COLOUR = 0xb3c6d2; // blue-ish grey
const LIGHT_COLOUR = 0xffff00; // ELECTRIC_YELLOW
const DIM_LIGHT_COLOUR = 0xffc40c; // MIKADO_YELLOW
const DARK_COLOUR = BLACK;

const BUTTON_STYLE = {
  fontFamily: "Arial",
  fontSize: 16 * SCALE,
  color: "black",
  backgroundColor: "#f0f8ff",
  textDecoration: "none",
  padding: {
    y: 12 * SCALE,
  },
  align: "center",
  fixedWidth: 170 * SCALE,
};

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
    this.solution = new Board(
      data.n,
      data.n,
      data.solution.values,
      data.solution.placed_dominoes.map(
        (d) => new PlacedDomino(ALL_DOMINOES[d.domino], d.i, d.j)
      )
    );
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
  // Note: m != n is for offBoard (which isn't square) - so it only supports
  // canAdd, canRemove, but not methods for lights and paths.
  constructor(n = 4, m = 4, values = zeros2D(n, n), placedDominoes = []) {
    this.n = n;
    this.m = m;
    this.values = values;
    this.placedDominoes = placedDominoes;
  }

  canAdd(placedDomino) {
    const n = this.n;
    const m = this.m;
    const [[i1, j1], [i2, j2]] = placedDomino.index();
    if (0 <= i1 && i1 < n && 0 <= j1 && j1 < m) {
      if (0 <= i2 && i2 < n && 0 <= j2 && j2 < m) {
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
    const m = this.m;
    const [[i1, j1], [i2, j2]] = placedDomino.index();
    if (0 <= i1 && i1 < n && 0 <= j1 && j1 < m) {
      if (0 <= i2 && i2 < n && 0 <= j2 && j2 < m) {
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

  reset() {
    this.values = zeros2D(this.n, this.n);
    this.placedDominoes = [];
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
  const x = i * BLOCK_SIZE + BLOCK_H;
  const y = j * BLOCK_SIZE + BLOCK_H;
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

function drawTitle(scene) {
  const titleStyle = {
    fontFamily: "monospace",
    fontSize: 30 * SCALE,
    color: "yellow",
    padding: {
      bottom: 2,
    },
  };
  scene.add
    .text(SCREEN_WIDTH / 2, BLOCK_H, "POLARIZE", titleStyle)
    .setOrigin(0.5);
}

function drawText(scene, text, x, y, fontSize = 12) {
  const textStyle = {
    fontFamily: "Arial",
    fontSize: fontSize * SCALE,
    color: "white",
    padding: {
      bottom: 2,
    },
  };
  scene.add.text(x, y, text, textStyle).setOrigin(0.5);
}

function drawFilter(graphics, filter, dx, dy) {
  graphics.lineStyle(3 * SCALE, BLACK);
  graphics.fillStyle(WHITE);

  graphics.fillCircle(BLOCK_H + dx, BLOCK_H + dy, FILTER_R);
  graphics.strokeCircle(BLOCK_H + dx, BLOCK_H + dy, FILTER_R);

  const A = (10 - 3) * SCALE;
  const B = (30 - 3) * SCALE;
  const C = (10 + 3) * SCALE;
  const D = (30 + 3) * SCALE;
  if (filter == Filter.POS_45) {
    graphics.lineBetween(A + dx, B + dy, B + dx, A + dy);
    graphics.lineBetween(C + dx, D + dy, D + dx, C + dy);
  } else {
    graphics.lineBetween(C + dx, A + dy, D + dx, B + dy);
    graphics.lineBetween(A + dx, C + dy, B + dx, D + dy);
  }
}

function drawDomino(graphics, domino, dominoName) {
  const OFF1 = BLOCK_H - FILTER_R;
  const OFF2 = BLOCK_H + FILTER_R;

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

  // filters
  drawFilter(graphics, domino.filter1, 0, 0);
  drawFilter(graphics, domino.filter2, dx, dy);

  if (domino.orientation == Orientation.H) {
    graphics.generateTexture(dominoName, BLOCK_SIZE * 2, BLOCK_SIZE);
  } else {
    graphics.generateTexture(dominoName, BLOCK_SIZE, BLOCK_SIZE * 2);
  }
}

// Used only for help pages
function drawHorizonatalLightSourceAndSpot(n, graphics, light, board_y_offset) {
  let [x, y] = blockIndexToCoord(0, 0, board_y_offset + BLOCK_SIZE);
  graphics.lineStyle(LIGHT_WIDTH, LIGHT_COLOUR);
  graphics.lineBetween(LIGHT_WIDTH, y, BLOCK_SIZE, y);
  [x, y] = blockIndexToCoord(n + 1, 0, board_y_offset);
  graphics.fillStyle(light_to_colour(light));
  graphics.fillCircle(x, BLOCK_SIZE + y, SPOT_RADIUS);
}

// Used only for help pages
function drawHorizontalLightPath(n, graphics, pathsHorizontal, board_y_offset) {
  for (let i = 0; i < n + 1; i++) {
    const colour = light_to_colour(pathsHorizontal[i]);
    const [x0, y0] = blockIndexToCoord(i, 1, board_y_offset);
    const [x1, y1] = blockIndexToCoord(i + 1, 1, board_y_offset);
    graphics.lineStyle(LIGHT_WIDTH, colour);
    graphics.lineBetween(x0, y0, x1, y1);
  }
}

function drawLightSourcesAndSpots(n, graphics, puzzle, board_y_offset) {
  li = puzzle.lights;
  let i = 0;
  for (let j = 0; j < n; j++) {
    let [x, y] = blockIndexToCoord(i, j, board_y_offset + BLOCK_SIZE);
    graphics.lineStyle(LIGHT_WIDTH, LIGHT_COLOUR);
    graphics.lineBetween(LIGHT_WIDTH, y, BLOCK_SIZE, y);
    i = n + 1;
    [x, y] = blockIndexToCoord(i, j, board_y_offset);
    graphics.fillStyle(light_to_colour(li[j]));
    graphics.fillCircle(x, BLOCK_SIZE + y, SPOT_RADIUS);
  }
  let j = 0;
  for (let i = 0; i < n; i++) {
    let [x, y] = blockIndexToCoord(i + 1, j, board_y_offset);
    graphics.lineStyle(LIGHT_WIDTH, LIGHT_COLOUR);
    graphics.lineBetween(
      x,
      LIGHT_WIDTH + board_y_offset,
      x,
      BLOCK_SIZE + board_y_offset
    );
    j = n;
    [x, y] = blockIndexToCoord(i, j, board_y_offset);
    graphics.fillStyle(light_to_colour(li[n + i]));
    graphics.fillCircle(BLOCK_SIZE + x, BLOCK_SIZE + y, SPOT_RADIUS);
  }
}

function drawLightPaths(n, graphics, solution, board_y_offset) {
  // iterate over colours from dark to light, so darker ones are at back
  const pathsHorizontal = solution.pathsHorizontal();
  const pathsVertical = solution.pathsVertical();
  const colours = [DARK_COLOUR, DIM_LIGHT_COLOUR, LIGHT_COLOUR];
  for (const c of colours) {
    for (let i = 0; i < n + 1; i++) {
      for (let j = 0; j < n; j++) {
        const colour = light_to_colour(pathsHorizontal[j][i]);
        if (colour == c) {
          const [x0, y0] = blockIndexToCoord(i, j + 1, board_y_offset);
          const [x1, y1] = blockIndexToCoord(i + 1, j + 1, board_y_offset);
          graphics.lineStyle(LIGHT_WIDTH, colour);
          graphics.lineBetween(x0, y0, x1, y1);
        }
      }
    }
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n + 1; j++) {
        const colour = light_to_colour(pathsVertical[j][i]);
        if (colour == c) {
          const [x0, y0] = blockIndexToCoord(i + 1, j, board_y_offset);
          const [x1, y1] = blockIndexToCoord(i + 1, j + 1, board_y_offset);
          graphics.lineStyle(LIGHT_WIDTH, colour);
          graphics.lineBetween(x0, y0, x1, y1);
        }
      }
    }
  }
}

function drawCells(n, m, graphics, board_y_offset = BLOCK_SIZE) {
  graphics.fillStyle(CELL_COLOUR);
  for (var i = 0; i < n; i++) {
    for (var j = 0; j < m; j++) {
      const [x, y] = blockIndexToCoord(i + 1, j + 1, board_y_offset);
      graphics.fillRect(
        x - CELL_SIZE / 2,
        y - CELL_SIZE / 2,
        CELL_SIZE,
        CELL_SIZE
      );
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

// From https://stackoverflow.com/a/2117523
// prettier-ignore
function uuidv4() {
    return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
    }

function getDeviceId() {
  let deviceId = localStorage.getItem("deviceId");
  if (deviceId == null) {
    deviceId = uuidv4();
    localStorage.setItem("deviceId", deviceId);
  }
  return deviceId;
}

function isLocalhost() {
  return location.hostname === "localhost" || location.hostname === "127.0.0.1";
}

// Return "today" in YYYY-MM-DD
// Allow overriding with url param ?date=YYYY-MM-DD
function getEffectiveDate() {
  const urlParams = new URLSearchParams(window.location.search);
  const dateParam = urlParams.get("date");
  return dateParam ? dateParam : formatDate(new Date());
}

// Events

const firebaseConfig = {
  apiKey: "AIzaSyCN6Bwe0azsRuU9s4iCFC4e5DguQLlQx2M",
  authDomain: "polarize-73191.firebaseapp.com",
  projectId: "polarize-73191",
  storageBucket: "polarize-73191.firebasestorage.app",
  messagingSenderId: "1063397566968",
  appId: "1:1063397566968:web:aa71a02ea4eeea0edd8e0d"
};

const app = firebase.initializeApp(firebaseConfig);

const db = firebase.firestore();

const today = getEffectiveDate();
const deviceId = getDeviceId();

function saveEvent(name) {
  const eventHistoryJson = localStorage.getItem("eventHistory");
  const eventHistory =
    eventHistoryJson == null ? [] : JSON.parse(eventHistoryJson);
  const event = {
    puzzle: today,
    name: name,
    timestamp: Date.now(),
  };
  eventHistory.push(event);
  localStorage.setItem("eventHistory", JSON.stringify(eventHistory));

  event.device = deviceId;
  if (isLocalhost()) {
    console.log("Ignoring event on localhost");
  } else {
    db.collection("puzzles")
      .doc(today)
      .collection("events")
      .add(event)
      .then((docRef) => {
        console.log("Event written to firestore with ID: ", docRef.id);
      })
      .catch((error) => {
        console.error("Error adding event to firestore: ", error);
      });
  }
}

function savePlayed() {
  const solvedHistoryJson = localStorage.getItem("polarizeSolvedHistory");
  const solvedHistory =
    solvedHistoryJson == null
      ? []
      : Array.from(new Set(JSON.parse(solvedHistoryJson))).sort();
  const playedHistoryJson = localStorage.getItem("polarizePlayedHistory");
  const playedHistory =
    playedHistoryJson == null
      ? solvedHistory // init from solved history
      : Array.from(new Set(JSON.parse(playedHistoryJson))).sort();
  if (!playedHistory.includes(today)) {
    playedHistory.push(today);
    localStorage.setItem("polarizePlayedHistory", JSON.stringify(playedHistory));
  }
}

function saveSolved() {
  const solvedHistoryJson = localStorage.getItem("polarizeSolvedHistory");
  const solvedHistory =
    solvedHistoryJson == null
      ? []
      : Array.from(new Set(JSON.parse(solvedHistoryJson))).sort();
  if (!solvedHistory.includes(today)) {
    solvedHistory.push(today);
    localStorage.setItem("polarizeSolvedHistory", JSON.stringify(solvedHistory));
  }
}

function getStats() {
  const playedHistoryJson = localStorage.getItem("polarizePlayedHistory");
  const playedHistory =
    playedHistoryJson == null
      ? []
      : Array.from(new Set(JSON.parse(playedHistoryJson))).sort();
  const played = Array.from(new Set(playedHistory)).length;
  console.log(`Played: ${played}`);

  const solvedHistoryJson = localStorage.getItem("polarizeSolvedHistory");
  const solvedHistory =
    solvedHistoryJson == null
      ? []
      : Array.from(new Set(JSON.parse(solvedHistoryJson))).sort();
  const solved = Array.from(new Set(solvedHistory)).length;
  console.log(`Solved: ${solved}`);

  let currentStreak = 0;
  Array.from(new Set(solvedHistory))
    .sort()
    .reverse()
    .map((d) => new Date(d))
    .forEach((d, i) => {
      if (new Date(today) - d === i * 60 * 60 * 24 * 1000) {
        currentStreak++;
      }
    });
  console.log(`Streak: ${currentStreak}`);
  return { played: played, solved: solved, currentStreak: currentStreak };
}

// Scenes

class PlayScene extends Phaser.Scene {
  constructor() {
    super({ key: "PlayScene" });
  }

  preload() {
    this.load.image("reset", "sprites/reset.png");
    this.load.image("help", "sprites/help.png");
    this.load.json("puzzle", `puzzles/puzzle-${today}.json`);
    savePlayed(); // assume played if loaded today's puzzle
    plausible("preload");
    saveEvent("preload");
  }

  create() {
    const puzzle = new Puzzle(this.cache.json.get("puzzle"));
    const solution = puzzle.solution;
    const n = puzzle.n;
    const board = new Board();
    const offBoard = new Board(4, 3);
    const board_y_offset = BLOCK_SIZE;

    let gameOver = false;
    let seenFirstMove = false;

    // Title
    drawTitle(this);

    // Lights
    const lightsGraphics = this.add.graphics();
    drawLightSourcesAndSpots(n, lightsGraphics, puzzle, board_y_offset);

    // Light paths
    const lightPathGraphics = this.add.graphics();
    lightPathGraphics.visible = false;
    drawLightPaths(n, lightPathGraphics, solution, board_y_offset);

    // Cells (board)
    const cellGraphics = this.add.graphics();
    drawCells(n, n, cellGraphics)

    // Cells (off board)
    drawCells(n, n - 1, cellGraphics, BLOCK_SIZE * (n + 2))

    // Dominoes
    let dominoSprites = [];
    const dominoGraphics = this.make.graphics({ x: 0, y: 0, add: false });
    for (const pd of puzzle.initial_placed_dominoes) {
      offBoard.add(pd);
      const domino = pd.domino;
      const dominoName = `domino_${domino.value}`;
      drawDomino(dominoGraphics, domino, dominoName);

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
      dominoSprites.push(dominoSprite);
    }

    // Reset button
    // {
    //   let [x, y] = blockIndexToCoord(5, 6);
    //   const reset = this.add.image(x, y, "reset").setInteractive();
    //   reset.setScale(SCALE);
    //   reset.on("pointerup", (e) => {
    //     board.reset();
    //     offBoard.reset();
    //     for (let i = 0; i < puzzle.initial_placed_dominoes.length; i++) {
    //       const pd = puzzle.initial_placed_dominoes[i];
    //       const dominoSprite = dominoSprites[i];
    //       offBoard.add(pd);
    //       dominoSprite.setData("board", offBoard);
    //       dominoSprite.setData("placedDomino", pd);
    //       let [x, y] = blockIndexToCoord(
    //         pd.i + 1,
    //         pd.j,
    //         BLOCK_SIZE * (n + 2) + board_y_offset
    //       );
    //       dominoSprite.x = x - CELL_SIZE / 2;
    //       dominoSprite.y = y - CELL_SIZE / 2;
    //     }
    //   });
    //   this.reset = reset;
    // }

    // Help button
    {
      let [x, y] = blockIndexToCoord(5, 0);
      const help = this.add.image(x, y, "help").setInteractive();
      help.setScale(SCALE);
      help.on("pointerup", (e) => {
        this.scene.setVisible(false, "PlayScene");
        this.scene.launch("MenuScene");
        this.scene.pause();
      });
    }

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
        var i = x / BLOCK_SIZE - 1;
        var j = y / BLOCK_SIZE - 2;
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
        if (!seenFirstMove) {
          saveEvent("firstMove");
          seenFirstMove = true;
        }
        if (JSON.stringify(board.lights()) == JSON.stringify(puzzle.lights)) {
          cellGraphics.visible = false;
          lightPathGraphics.visible = true;
          gameOver = true;
          // hide reset button
          // this.reset.setVisible(false);
          // disable dragging
          let images = this.children.list.filter(
            (x) => x instanceof Phaser.GameObjects.Image
          );
          images.forEach((image) =>
            image.input ? this.input.setDraggable(image, false) : null
          );
          saveSolved();
          const stats = getStats();
          drawText(
            this,
            stats.played,
            BLOCK_SIZE * 1.5,
            BLOCK_SIZE * (n + 2) + BLOCK_SIZE / 2 + board_y_offset,
            24
          );
          drawText(
            this,
            "Played",
            BLOCK_SIZE * 1.5,
            BLOCK_SIZE * (n + 2) + BLOCK_SIZE + board_y_offset,
            10
          );
          drawText(
            this,
            stats.solved,
            BLOCK_SIZE * 3,
            BLOCK_SIZE * (n + 2) + BLOCK_SIZE / 2 + board_y_offset,
            24
          );
          drawText(
            this,
            "Solved",
            BLOCK_SIZE * 3,
            BLOCK_SIZE * (n + 2) + BLOCK_SIZE + board_y_offset,
            10
          );
          drawText(
            this,
            stats.currentStreak,
            BLOCK_SIZE * 4.5,
            BLOCK_SIZE * (n + 2) + BLOCK_SIZE / 2 + board_y_offset,
            24
          );
          drawText(
            this,
            "Current",
            BLOCK_SIZE * 4.5,
            BLOCK_SIZE * (n + 2) + BLOCK_SIZE + board_y_offset,
            10
          );
          drawText(
            this,
            "Streak",
            BLOCK_SIZE * 4.5,
            BLOCK_SIZE * (n + 2) + BLOCK_SIZE * 1.3 + board_y_offset,
            10
          );
          plausible("solved");
          saveEvent("solved");
        }
      },
      this
    );
  }
}

class MenuScene extends Phaser.Scene {
  constructor() {
    super({ key: "MenuScene" });
  }

  preload() {}

  create() {
    // Title
    drawTitle(this);

    let y_offset = BLOCK_SIZE * 2;
    this.add
      .text(SCREEN_WIDTH / 2, y_offset, "Play", BUTTON_STYLE)
      .setOrigin(0.5)
      .setInteractive()
      .on("pointerup", (e) => {
        this.scene.resume("PlayScene");
        this.scene.stop();
        this.scene.setVisible(true, "PlayScene");
      });
    y_offset += BLOCK_SIZE * 1.5;
    this.add
      .text(SCREEN_WIDTH / 2, y_offset, "How to play", BUTTON_STYLE)
      .setOrigin(0.5)
      .setInteractive()
      .on("pointerup", (e) => {
        this.scene.launch("HowToPlayScene1");
        this.scene.stop();
      });
    y_offset += BLOCK_SIZE * 1.5;
    this.add
      .text(SCREEN_WIDTH / 2, y_offset, "Yesterday's solution", BUTTON_STYLE)
      .setOrigin(0.5)
      .setInteractive()
      .on("pointerup", (e) => {
        this.scene.launch("SolutionScene");
        this.scene.stop();
      });
    y_offset += BLOCK_SIZE * 1.5;
    this.add
      .text(SCREEN_WIDTH / 2, y_offset, "About", BUTTON_STYLE)
      .setOrigin(0.5)
      .setInteractive()
      .on("pointerup", (e) => {
        this.scene.launch("AboutScene");
        this.scene.stop();
      });
  }
}

class HowToPlayScene1 extends Phaser.Scene {
  constructor() {
    super({ key: "HowToPlayScene1" });
  }

  preload() {}

  create() {
    // Title
    drawTitle(this);

    // Lights
    const n = 4;
    const graphics = this.add.graphics();
    let board_y_offset = BLOCK_SIZE;
    drawText(
      this,
      "A yellow light beam shines on a spot",
      SCREEN_WIDTH / 2,
      board_y_offset + BLOCK_H
    );
    drawHorizonatalLightSourceAndSpot(n, graphics, 0, board_y_offset);
    drawHorizontalLightPath(n, graphics, [0, 0, 0, 0, 0], board_y_offset);

    board_y_offset += 2 * BLOCK_SIZE;
    drawText(
      this,
      "Adding a filter dims the beam to orange",
      SCREEN_WIDTH / 2,
      board_y_offset + BLOCK_H
    );
    drawHorizonatalLightSourceAndSpot(n, graphics, 1, board_y_offset);
    drawHorizontalLightPath(n, graphics, [0, 0, 1, 1, 1], board_y_offset);
    drawFilter(
      graphics,
      Filter.POS_45,
      2 * BLOCK_SIZE,
      board_y_offset + BLOCK_SIZE
    );

    board_y_offset += 2 * BLOCK_SIZE;
    drawText(
      this,
      "Identical filters have the same effect",
      SCREEN_WIDTH / 2,
      board_y_offset + BLOCK_H
    );
    drawHorizonatalLightSourceAndSpot(n, graphics, 1, board_y_offset);
    drawHorizontalLightPath(n, graphics, [0, 0, 1, 1, 1], board_y_offset);
    drawFilter(
      graphics,
      Filter.POS_45,
      2 * BLOCK_SIZE,
      board_y_offset + BLOCK_SIZE
    );
    drawFilter(
      graphics,
      Filter.POS_45,
      3 * BLOCK_SIZE,
      board_y_offset + BLOCK_SIZE
    );

    board_y_offset += 2 * BLOCK_SIZE;
    drawText(
      this,
      "While opposing filters cut out all light",
      SCREEN_WIDTH / 2,
      board_y_offset + BLOCK_H
    );
    drawHorizonatalLightSourceAndSpot(n, graphics, 2, board_y_offset);
    drawHorizontalLightPath(n, graphics, [0, 0, 1, 2, 2], board_y_offset);
    drawFilter(
      graphics,
      Filter.POS_45,
      2 * BLOCK_SIZE,
      board_y_offset + BLOCK_SIZE
    );
    drawFilter(
      graphics,
      Filter.NEG_45,
      3 * BLOCK_SIZE,
      board_y_offset + BLOCK_SIZE
    );

    board_y_offset += 3 * BLOCK_SIZE;
    this.add
      .text(SCREEN_WIDTH / 2, board_y_offset, "Next", BUTTON_STYLE)
      .setOrigin(0.5)
      .setInteractive()
      .on("pointerup", (e) => {
        this.scene.launch("HowToPlayScene2");
        this.scene.stop();
      });
  }
}

class HowToPlayScene2 extends Phaser.Scene {
  constructor() {
    super({ key: "HowToPlayScene2" });
  }

  preload() {
    this.load.json("helpPuzzle", "puzzles/puzzle-2025-01-13.json");
  }

  create() {
    const puzzle = new Puzzle(this.cache.json.get("helpPuzzle"));
    const solution = puzzle.solution;
    const n = puzzle.n;

    let board_y_offset = BLOCK_SIZE;
    drawText(
      this,
      "Light beams shine across and down",
      SCREEN_WIDTH / 2,
      board_y_offset + BLOCK_H
    );

    board_y_offset += BLOCK_SIZE;

    // Title
    drawTitle(this);

    // Lights
    const lightsGraphics = this.add.graphics();
    drawLightSourcesAndSpots(n, lightsGraphics, puzzle, board_y_offset);

    // Light paths
    const lightPathGraphics = this.add.graphics();
    drawLightPaths(n, lightPathGraphics, solution, board_y_offset);

    // Dominoes
    const dominoGraphics = this.make.graphics({ x: 0, y: 0, add: false });
    for (const pd of solution.placedDominoes) {
      const domino = pd.domino;
      const dominoName = `domino_${domino.value}`;
      drawDomino(dominoGraphics, domino, dominoName);

      let [x, y] = blockIndexToCoord(
        pd.i + 1,
        pd.j,
        BLOCK_SIZE + board_y_offset
      );
      const dominoSprite = this.add.image(
        x - CELL_SIZE / 2,
        y - CELL_SIZE / 2,
        dominoName
      );
      dominoSprite.setOrigin(0, 0);
    }

    board_y_offset += (n + 1.5) * BLOCK_SIZE;
    drawText(
      this,
      "The goal is to place the paired filters",
      SCREEN_WIDTH / 2,
      board_y_offset + BLOCK_H
    );

    board_y_offset += BLOCK_H;
    drawText(
      this,
      "so the lights and the spots match",
      SCREEN_WIDTH / 2,
      board_y_offset + BLOCK_H
    );

    board_y_offset += 2 * BLOCK_SIZE;
    this.add
      .text(SCREEN_WIDTH / 2, board_y_offset, "Done", BUTTON_STYLE)
      .setOrigin(0.5)
      .setInteractive()
      .on("pointerup", (e) => {
        this.scene.resume("PlayScene");
        this.scene.stop();
        this.scene.setVisible(true, "PlayScene");
      });
  }
}

class SolutionScene extends Phaser.Scene {
  constructor() {
    super({ key: "SolutionScene" });
  }

  preload() {
    const yesterdayDate = new Date();
    yesterdayDate.setDate(yesterdayDate.getDate() - 1);
    const yesterday = formatDate(yesterdayDate);
    this.load.json("yesterdayPuzzle", `puzzles/puzzle-${yesterday}.json`);
    this.load.image("close", "sprites/close-circle-line.png");
  }

  create() {
    const puzzle = new Puzzle(this.cache.json.get("yesterdayPuzzle"));
    const solution = puzzle.solution;
    const n = puzzle.n;

    let board_y_offset = BLOCK_SIZE;
    drawText(
      this,
      "Yesterday's solution",
      SCREEN_WIDTH / 2,
      board_y_offset + BLOCK_H
    );

    board_y_offset += BLOCK_SIZE;

    // Title
    drawTitle(this);

    let [x, y] = blockIndexToCoord(5, 0);
    const close = this.add.image(x, y, "close").setInteractive();
    close.setScale(SCALE);
    close.on("pointerup", (e) => {
      this.scene.resume("PlayScene");
      this.scene.stop();
      this.scene.setVisible(true, "PlayScene");
    });

    // Lights
    const lightsGraphics = this.add.graphics();
    drawLightSourcesAndSpots(n, lightsGraphics, puzzle, board_y_offset);

    // Light paths
    const lightPathGraphics = this.add.graphics();
    drawLightPaths(n, lightPathGraphics, solution, board_y_offset);

    // Dominoes
    const dominoGraphics = this.make.graphics({ x: 0, y: 0, add: false });
    for (const pd of solution.placedDominoes) {
      const domino = pd.domino;
      const dominoName = `domino_${domino.value}`;
      drawDomino(dominoGraphics, domino, dominoName);

      let [x, y] = blockIndexToCoord(
        pd.i + 1,
        pd.j,
        BLOCK_SIZE + board_y_offset
      );
      const dominoSprite = this.add.image(
        x - CELL_SIZE / 2,
        y - CELL_SIZE / 2,
        dominoName
      );
      dominoSprite.setOrigin(0, 0);
    }
  }
}

class AboutScene extends Phaser.Scene {
  constructor() {
    super({ key: "AboutScene" });
  }

  preload() {}

  create() {
    // Title
    drawTitle(this);

    let board_y_offset = BLOCK_SIZE;
    drawText(
      this,
      "A light puzzle by Tom White",
      SCREEN_WIDTH / 2,
      board_y_offset + BLOCK_H
    );

    board_y_offset += BLOCK_SIZE;
    drawText(
      this,
      "A new puzzle is released every day",
      SCREEN_WIDTH / 2,
      board_y_offset + BLOCK_H
    );


    board_y_offset += BLOCK_SIZE;
    drawText(
      this,
      "Send any comments or feedback to",
      SCREEN_WIDTH / 2,
      board_y_offset + BLOCK_H
    );

    board_y_offset += BLOCK_H;
    drawText(
      this,
      "tom.e.white@gmail.com",
      SCREEN_WIDTH / 2,
      board_y_offset + BLOCK_H
    );

    board_y_offset += 2 * BLOCK_SIZE;
    this.add
      .text(SCREEN_WIDTH / 2, board_y_offset, "Done", BUTTON_STYLE)
      .setOrigin(0.5)
      .setInteractive()
      .on("pointerup", (e) => {
        this.scene.resume("PlayScene");
        this.scene.stop();
        this.scene.setVisible(true, "PlayScene");
      });
  }
}

const config = {
  type: Phaser.AUTO,
  width: SCREEN_WIDTH,
  height: SCREEN_HEIGHT,
  scale: {
    parent: "phaser-game",
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH,
  },
  backgroundColor: BACKGROUND_COLOUR,
  scene: [PlayScene, MenuScene, HowToPlayScene1, HowToPlayScene2, SolutionScene, AboutScene],
};

const game = new Phaser.Game(config);

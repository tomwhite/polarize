import { test } from 'node:test';
import assert from 'node:assert/strict';
import { Filter, ALL_DOMINOES, PlacedDomino, Board, Puzzle, bitwise_count, formatDate } from './polarize.js';
import puzzleData from './puzzles/puzzle-2025-01-02.json' with { type: 'json' };

// bitwise_count

test('bitwise_count(0) === 0', () => {
  assert.equal(bitwise_count(0), 0);
});

test('bitwise_count(1) === 1', () => {
  assert.equal(bitwise_count(1), 1);
});

test('bitwise_count(2) === 1', () => {
  assert.equal(bitwise_count(2), 1);
});

test('bitwise_count(3) === 2', () => {
  assert.equal(bitwise_count(3), 2);
});

// Board - empty state

test('empty board has all-zero lights', () => {
  const board = new Board(4);
  assert.deepEqual(board.lights(), [0, 0, 0, 0, 0, 0, 0, 0]);
});

test('canAdd returns true for empty board', () => {
  const board = new Board(4);
  const pd = new PlacedDomino(ALL_DOMINOES[0], 0, 0);
  assert.equal(board.canAdd(pd), true);
});

test('canAdd returns false out of bounds', () => {
  const board = new Board(4);
  const pd = new PlacedDomino(ALL_DOMINOES[0], 3, 0); // horizontal domino would need cols 3 and 4
  assert.equal(board.canAdd(pd), false);
});

// Board - add and remove

test('add then canAdd same cell returns false', () => {
  const board = new Board(4);
  const pd = new PlacedDomino(ALL_DOMINOES[0], 0, 0);
  board.add(pd);
  const pd2 = new PlacedDomino(ALL_DOMINOES[1], 0, 0);
  assert.equal(board.canAdd(pd2), false);
});

test('add then remove restores empty lights', () => {
  const board = new Board(4);
  const pd = new PlacedDomino(ALL_DOMINOES[0], 0, 0);
  board.add(pd);
  board.remove(pd);
  assert.deepEqual(board.lights(), [0, 0, 0, 0, 0, 0, 0, 0]);
});

test('canRemove returns false when cell not occupied', () => {
  const board = new Board(4);
  const pd = new PlacedDomino(ALL_DOMINOES[0], 0, 0);
  assert.equal(board.canRemove(pd), false);
});

// Light physics

test('single POS_45 filter dims one row and one col', () => {
  const board = new Board(4);
  // domino 0: horizontal POS_45 + POS_45 at (0,0) occupies cells (0,0) and (1,0)
  board.add(new PlacedDomino(ALL_DOMINOES[0], 0, 0));
  const lights = board.lights();
  // row 0 (index 0) sees both POS_45 filters — OR of 1|1 = 1, bitwise_count = 1
  assert.equal(lights[0], 1);
  // col 0 (index 4) sees POS_45 — value 1
  assert.equal(lights[4], 1);
  // col 1 (index 5) sees POS_45 — value 1
  assert.equal(lights[5], 1);
  // other rows/cols are unaffected
  assert.equal(lights[1], 0);
  assert.equal(lights[6], 0);
});

test('opposing filters in same row block light (value 2)', () => {
  const board = new Board(4);
  // domino 1: horizontal POS_45 + NEG_45 at (0,0)
  board.add(new PlacedDomino(ALL_DOMINOES[1], 0, 0));
  const lights = board.lights();
  // row 0: OR of POS_45(1) | NEG_45(2) = 3, bitwise_count = 2
  assert.equal(lights[0], 2);
});

// Board - pathsHorizontal

test('pathsHorizontal of empty board is all zeros', () => {
  const board = new Board(4);
  const paths = board.pathsHorizontal();
  assert.deepEqual(paths, [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
  ]);
});

test('pathsHorizontal accumulates identical filters along a row', () => {
  const board = new Board(4);
  // domino 0: H POS_45+POS_45 at (0,0) — fills col 0 and col 1 of row 0
  board.add(new PlacedDomino(ALL_DOMINOES[0], 0, 0));
  // row 0: 0 before col 0, 1 after col 0, still 1 after col 1 (OR 1|1=1), then unchanged
  assert.deepEqual(board.pathsHorizontal()[0], [0, 1, 1, 1, 1]);
  // other rows untouched
  assert.deepEqual(board.pathsHorizontal()[1], [0, 0, 0, 0, 0]);
});

test('pathsHorizontal shows beam blocking when opposing filters in same row', () => {
  const board = new Board(4);
  // domino 1: H POS_45+NEG_45 at (0,0)
  board.add(new PlacedDomino(ALL_DOMINOES[1], 0, 0));
  // row 0: 0 → 1 (after POS_45) → 2 (after NEG_45, OR 1|2=3 → count 2) → 2 → 2
  assert.deepEqual(board.pathsHorizontal()[0], [0, 1, 2, 2, 2]);
});

test('pathsHorizontal final column matches lights() for each row', () => {
  const board = new Board(4);
  board.add(new PlacedDomino(ALL_DOMINOES[1], 0, 0));
  board.add(new PlacedDomino(ALL_DOMINOES[3], 0, 2));
  const paths = board.pathsHorizontal();
  const lights = board.lights();
  for (let j = 0; j < 4; j++) {
    assert.equal(paths[j][4], lights[j]);
  }
});

// Board - pathsVertical

test('pathsVertical of empty board is all zeros', () => {
  const board = new Board(4);
  const paths = board.pathsVertical();
  assert.deepEqual(paths, [
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ]);
});

test('pathsVertical accumulates identical filters down a column', () => {
  const board = new Board(4);
  // domino 4: V POS_45+POS_45 at (0,0) — fills row 0 and row 1 of col 0
  board.add(new PlacedDomino(ALL_DOMINOES[4], 0, 0));
  // col 0: 0 before row 0, 1 after row 0, still 1 after row 1 (OR 1|1=1), then unchanged
  assert.deepEqual(board.pathsVertical().map(row => row[0]), [0, 1, 1, 1, 1]);
  // other cols untouched
  assert.deepEqual(board.pathsVertical().map(row => row[1]), [0, 0, 0, 0, 0]);
});

test('pathsVertical shows beam blocking when opposing filters in same column', () => {
  const board = new Board(4);
  // domino 5: V POS_45+NEG_45 at (0,0)
  board.add(new PlacedDomino(ALL_DOMINOES[5], 0, 0));
  // col 0: 0 → 1 (after POS_45) → 2 (after NEG_45) → 2 → 2
  assert.deepEqual(board.pathsVertical().map(row => row[0]), [0, 1, 2, 2, 2]);
});

test('pathsVertical final row matches lights() for each column', () => {
  const board = new Board(4);
  board.add(new PlacedDomino(ALL_DOMINOES[5], 0, 0));
  board.add(new PlacedDomino(ALL_DOMINOES[4], 2, 0));
  const paths = board.pathsVertical();
  const lights = board.lights();
  for (let i = 0; i < 4; i++) {
    assert.equal(paths[4][i], lights[4 + i]);
  }
});

// formatDate

test('formatDate formats a basic date as YYYY-MM-DD', () => {
  assert.equal(formatDate(new Date(2025, 0, 13)), '2025-01-13');
});

test('formatDate zero-pads single-digit day', () => {
  assert.equal(formatDate(new Date(2025, 0, 5)), '2025-01-05');
});

test('formatDate zero-pads single-digit month', () => {
  assert.equal(formatDate(new Date(2025, 8, 1)), '2025-09-01');
});

test('formatDate handles year-end date', () => {
  assert.equal(formatDate(new Date(2024, 11, 31)), '2024-12-31');
});

test('formatDate handles leap day', () => {
  assert.equal(formatDate(new Date(2024, 1, 29)), '2024-02-29');
});

// Puzzle integration: place solution dominoes, verify lights match puzzle.lights

test('solution dominoes produce the correct lights for a real puzzle', () => {
  const puzzle = new Puzzle(puzzleData);
  const board = new Board(puzzle.n);
  for (const pd of puzzle.solution.placedDominoes) {
    board.add(pd);
  }
  assert.deepEqual(board.lights(), puzzle.lights);
});

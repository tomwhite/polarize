const { test } = require('node:test');
const assert = require('node:assert/strict');
const { Filter, Orientation, ALL_DOMINOES, PlacedDomino, Board, Puzzle, bitwise_count, zeros2D } = require('./polarize.js');

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
  const pd = new PlacedDomino(ALL_DOMINOES[0], 0, 0); // horizontal POS_45+POS_45 at (0,0)
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

// Puzzle integration: place solution dominoes, verify lights match puzzle.lights

test('solution dominoes produce the correct lights for a real puzzle', () => {
  const data = require('./puzzles/puzzle-2025-01-02.json');
  const puzzle = new Puzzle(data);
  const board = new Board(puzzle.n);
  for (const pd of puzzle.solution.placedDominoes) {
    board.add(pd);
  }
  assert.deepEqual(board.lights(), puzzle.lights);
});

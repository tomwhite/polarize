const { test, expect } = require('@playwright/test');

// Use a fixed date so tests are independent of the current day's puzzle
const TEST_DATE = '2025-01-02';
const URL = `/?date=${TEST_DATE}`;

// Wait for Phaser to finish loading the puzzle
async function waitForGame(page) {
  await page.waitForFunction(() => window.game?.scene?.isActive('PlayScene'));
}

async function drag(page, fromX, fromY, toX, toY) {
  await page.mouse.move(fromX, fromY);
  await page.mouse.down();
  // Move in steps so Phaser's drag tracking fires
  await page.mouse.move(toX, toY, { steps: 10 });
  await page.mouse.up();
}

// --- Basic load tests ---

test('page loads without console errors', async ({ page }) => {
  const errors = [];
  page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
  page.on('pageerror', err => errors.push(err.message));
  await page.goto(URL);
  await waitForGame(page);
  expect(errors).toHaveLength(0);
});

test('canvas is rendered', async ({ page }) => {
  await page.goto(URL);
  await waitForGame(page);
  await expect(page.locator('canvas')).toBeVisible();
});

// --- Interaction tests ---

test('help button opens menu and play returns to game', async ({ page }) => {
  await page.goto(URL);
  await waitForGame(page);

  // Help button is at blockIndexToCoord(5, 0) = (440, 120)
  await page.mouse.click(440, 120);
  await expect(page.locator('canvas')).toBeVisible(); // still rendered

  // MenuScene has a "Play" button rendered as a Phaser text object at (240, 160)
  await page.mouse.click(240, 160);
  await page.waitForFunction(() => window.game?.scene?.isActive('PlayScene'));
});

// --- Solve test ---

// Puzzle 2025-01-02 solution:
//   domino 7 (V) moves from tray (i=0,j=0) → board (i=1,j=2)
//   domino 1 (H) moves from tray (i=1,j=1) → board (i=2,j=2)
//   domino 2 (H) moves from tray (i=1,j=0) → board (i=0,j=1)
//
// Coordinate system: viewport is 480x880 = game canvas size, so 1:1 mapping.
// BLOCK_SIZE = 80, off-board tray y_origin = 560.
// Tray sprite top-left: x = (pd.i+1)*80+2, y = pd.j*80+562  (setOrigin(0,0))
// Board snap target: x = (i+1)*80, y = (j+2)*80
//
// Phaser drag: dragX = pointer.x - (grabX - spriteX), so:
//   dropX = snapTargetX + (grabX - spriteX)
//   dropY = snapTargetY + (grabY - spriteY)

test('solving the puzzle records a solve in localStorage', async ({ page }) => {
  await page.goto(URL);
  await waitForGame(page);

  // domino 7 (V, 80x160): sprite (82,562), centre (122,642), offset (40,80)
  //   snap target (160,320) + offset → drop at (200,400)
  await drag(page, 122, 642, 200, 400);

  // domino 1 (H, 160x80): sprite (162,642), centre (242,682), offset (80,40)
  //   snap target (240,320) + offset → drop at (320,360)
  await drag(page, 242, 682, 320, 360);

  // domino 2 (H, 160x80): sprite (162,562), centre (242,602), offset (80,40)
  //   snap target (80,240) + offset → drop at (160,280)
  await drag(page, 242, 602, 160, 280);

  // Win state: saveSolved() writes the date to polarizeSolvedHistory
  const solved = await page.evaluate(() =>
    JSON.parse(localStorage.getItem('polarizeSolvedHistory') ?? '[]')
  );
  expect(solved).toContain(TEST_DATE);
});

test('already-solved puzzle restores win state on reload', async ({ page }) => {
  // Seed localStorage with a prior solve, then load the page fresh
  await page.goto(URL);
  await page.evaluate((date) => {
    localStorage.setItem('polarizeSolvedHistory', JSON.stringify([date]));
  }, TEST_DATE);

  await page.reload();
  await waitForGame(page);

  // In win state all domino images have dragging disabled.
  // Phaser sets input.isDraggable = false on each image when setDraggable(img, false) is called.
  const draggableCount = await page.evaluate(() => {
    const scene = window.game.scene.getScene('PlayScene');
    return scene.children.list.filter(x => x.input?.isDraggable).length;
  });
  expect(draggableCount).toBe(0);
});

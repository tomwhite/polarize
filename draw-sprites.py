# create sprites for dominoes by joining constituent images
# TODO: replace by vector graphics with custom polarizing filter images

from PIL import Image, ImageDraw

from polarize.model import Orientation, Filter, ALL_DOMINOES

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

BLOCK_SIZE = 40
BLOCK_HALF = BLOCK_SIZE // 2
CIRCLE_RADIUS = 14
OFF1 = BLOCK_HALF - CIRCLE_RADIUS
OFF2 = BLOCK_HALF + CIRCLE_RADIUS

if __name__ == "__main__":
    for domino in ALL_DOMINOES:
        if domino.orientation == Orientation.H:
            dx, dy = BLOCK_SIZE, 0
        else:
            dx, dy = 0, BLOCK_SIZE

        im = Image.new("RGBA", (BLOCK_SIZE + dx, BLOCK_SIZE + dy))
        draw = ImageDraw.Draw(im)

        # joining lines
        if domino.orientation == Orientation.H:
            draw.line(
                ((BLOCK_HALF, OFF1), (BLOCK_SIZE + BLOCK_HALF, OFF1)),
                fill=BLACK,
                width=3,
            )
            draw.line(
                ((BLOCK_HALF, OFF2), (BLOCK_SIZE + BLOCK_HALF, OFF2)),
                fill=BLACK,
                width=3,
            )
        else:
            draw.line(
                ((OFF1, BLOCK_HALF), (OFF1, BLOCK_SIZE + BLOCK_HALF)),
                fill=BLACK,
                width=3,
            )
            draw.line(
                ((OFF2, BLOCK_HALF), (OFF2, BLOCK_SIZE + BLOCK_HALF)),
                fill=BLACK,
                width=3,
            )

        # circles
        draw.ellipse((OFF1, OFF1, OFF2, OFF2), fill=WHITE, outline=BLACK, width=2)
        draw.ellipse(
            (OFF1 + dx, OFF1 + dy, OFF2 + dx, OFF2 + dy),
            fill=WHITE,
            outline=BLACK,
            width=2,
        )

        # filter 1 lines
        if domino.filter1 == Filter.POS_45:
            draw.line(((10 - 3, 30 - 3), (30 - 3, 10 - 3)), fill=BLACK, width=3)
            draw.line(((10 + 3, 30 + 3), (30 + 3, 10 + 3)), fill=BLACK, width=3)
        else:
            draw.line(((10 + 3, 10 - 3), (30 + 3, 30 - 3)), fill=BLACK, width=3)
            draw.line(((10 - 3, 10 + 3), (30 - 3, 30 + 3)), fill=BLACK, width=3)

        # filter 2 lines
        if domino.filter2 == Filter.POS_45:
            draw.line(
                ((10 - 3 + dx, 30 - 3 + dy), (30 - 3 + dx, 10 - 3 + dy)),
                fill=BLACK,
                width=3,
            )
            draw.line(
                ((10 + 3 + dx, 30 + 3 + dy), (30 + 3 + dx, 10 + 3 + dy)),
                fill=BLACK,
                width=3,
            )
        else:
            draw.line(
                ((10 + 3 + dx, 10 - 3 + dy), (30 + 3 + dx, 30 - 3 + dy)),
                fill=BLACK,
                width=3,
            )
            draw.line(
                ((10 - 3 + dx, 10 + 3 + dy), (30 - 3 + dx, 30 + 3 + dy)),
                fill=BLACK,
                width=3,
            )

        im.save(f"sprites/domino_{domino.value}_tr.png")

# create sprites for dominoes by joining constituent images
# TODO: replace by vector graphics with custom polarizing filter images

from PIL import Image

from polarize.model import DominoOrientation, PolarizingFilter, ALL_DOMINOES

if __name__ == "__main__":

    images = {
        PolarizingFilter.POS_45: Image.open("sprites/oblique_mirror_tr.png"),
        PolarizingFilter.NEG_45: Image.open("sprites/reverse_oblique_mirror_tr.png"),
    }

    for domino in ALL_DOMINOES:
        if domino.orientation == DominoOrientation.HORIZONTAL:
            im = Image.new("RGB", (64, 32))
            im.paste(images[domino.filter1], (0, 0))
            im.paste(images[domino.filter2], (32, 0))
        else:
            im = Image.new("RGB", (32, 64))
            im.paste(images[domino.filter1], (0, 0))
            im.paste(images[domino.filter2], (0, 32))

        im.save(f"sprites/domino_{domino.value}_tr.png")
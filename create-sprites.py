# create sprites for dominoes by joining constituent images
# TODO: replace by vector graphics with custom polarizing filter images

from PIL import Image

from polarize.model import Orientation, Filter, ALL_DOMINOES

if __name__ == "__main__":
    images = {
        Filter.POS_45: Image.open("sprites/polarize-pos45.png"),
        Filter.NEG_45: Image.open("sprites/polarize-neg45.png"),
    }

    for domino in ALL_DOMINOES:
        if domino.orientation == Orientation.H:
            im = Image.new("RGBA", (80, 40))
            im.paste(images[domino.filter1], (4, 4))
            im.paste(images[domino.filter2], (40, 4))
        else:
            im = Image.new("RGBA", (40, 80))
            im.paste(images[domino.filter1], (4, 4))
            im.paste(images[domino.filter2], (4, 40))

        im.save(f"sprites/domino_{domino.value}_tr.png")

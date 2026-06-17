"""Screenshot scenes for the Avatar widget."""

from pathlib import Path

import bootstack as bs

_PHOTO = Path(__file__).parent.parent / "_static" / "examples" / "avatar-profile.jpg"


def hero():
    with bs.App(title="Avatar", padding=20, gap=14) as app:
        with bs.Row(gap=12, vertical_items="center"):
            bs.Avatar(_PHOTO, size=64, shape="circle")
            bs.Avatar(_PHOTO, size=64, shape="rounded")
            bs.Avatar(name="Ada Lovelace", size=64, background="primary")
            bs.Avatar(name="Grace Hopper", size=64, background="info")
            bs.Avatar(name="Alan Turing", size=64, background="success")
    app.run()


def shapes():
    with bs.App(title="Avatar — shapes", padding=20, gap=14) as app:
        with bs.Row(gap=16, vertical_items="center"):
            for shape in ("circle", "rounded", "square"):
                with bs.Column(gap=4):
                    bs.Avatar(_PHOTO, size=72, shape=shape)
                    bs.Label(shape, font="caption", horizontal="center")
    app.run()


SCENES = {
    "hero": hero,
    "shapes": shapes,
}

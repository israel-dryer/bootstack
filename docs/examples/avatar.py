"""Avatar — a small identity badge showing a picture or initials.

Run this directly to see the widget. It uses a bundled sample photo for the
image avatars and derives initials from names for the rest.
"""

from pathlib import Path

import bootstack as bs

# The sample photo lives alongside the docs' example media.
_PHOTO = Path(__file__).parent.parent / "_static" / "examples" / "avatar-profile.jpg"

with bs.App(title="Avatar", padding=20, gap=16) as app:
    bs.Label("From an image", font="heading-md")
    with bs.HStack(gap=12, anchor_items="center"):
        bs.Avatar(_PHOTO, size=64, shape="circle")
        bs.Avatar(_PHOTO, size=64, shape="rounded")
        bs.Avatar(_PHOTO, size=64, shape="square")
        bs.Avatar(_PHOTO, size=40)
        bs.Avatar(_PHOTO, size=28)

    bs.Separator()

    bs.Label("From initials", font="heading-md")
    with bs.HStack(gap=12, anchor_items="center"):
        bs.Avatar(name="Ada Lovelace", size=64, background="primary")
        bs.Avatar(name="Grace Hopper", size=64, background="info")
        bs.Avatar(name="Alan Turing", size=64, background="success")
        bs.Avatar(initials="JD", size=64, background="warning")
        bs.Avatar(name="Katherine Johnson", size=64, background="#7c4dff", shape="rounded")

    bs.Separator()

    bs.Label("Clickable (prints to the console)", font="heading-md")
    avatar = bs.Avatar(_PHOTO, size=56)
    avatar.on_click(lambda e: print("avatar clicked"))

app.run()

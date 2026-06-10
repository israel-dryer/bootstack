"""Hero scene for the App page — a full OS-window capture (titlebar + chrome).

Sets ``app._capture_full_window`` so the screenshot runner grabs the whole
window, showing what a real bootstack window looks like on the platform.
"""

import bootstack as bs


def hero():
    with bs.App(title="Bootstack", size=(560, 400), padding=24, gap=14) as app:
        app._capture_full_window = True

        bs.Label("Welcome to bootstack", font="heading-lg")
        bs.Label(
            "Build native desktop apps in pure Python.",
            font="body",
            accent="secondary",
        )
        bs.TextField(label="Project name", value="my-app")
        with bs.HStack(gap=8):
            bs.Button("Create", accent="primary")
            bs.Button("Cancel", variant="outline")

    app.run()


SCENES = {"hero": hero}

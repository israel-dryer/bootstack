import bootstack as bs


def hero():
    with bs.App(title="Spacer", minsize=(560, 1), padding=20) as app:
        with bs.Row(gap=4, show_border=True, padding=8, horizontal="stretch"):
            bs.Button("New")
            bs.Button("Open")
            bs.Spacer()
            bs.Button("Settings")
            bs.Button("Profile")
    app.run()


def fixed():
    with bs.App(title="Spacer — Fixed", minsize=(560, 1), padding=20) as app:
        with bs.Row(gap=4, show_border=True, padding=8):
            bs.Button("One")
            bs.Spacer(size=48)
            bs.Button("Two")
            bs.Spacer(size=48)
            bs.Button("Three")
    app.run()


def weighted():
    with bs.App(title="Spacer — Weighted", minsize=(640, 1), padding=20) as app:
        with bs.Row(gap=4, show_border=True, padding=8, horizontal="stretch"):
            bs.Button("Left")
            bs.Spacer(weight=1)
            bs.Button("Center")
            bs.Spacer(weight=2)
            bs.Button("Right")
    app.run()


def column():
    with bs.App(title="Spacer — Column", minsize=(360, 1), padding=20) as app:
        with bs.Column(gap=6, show_border=True, padding=8, height=180,
                       horizontal="stretch", horizontal_items="stretch"):
            bs.Label("Title", font="heading-md")
            bs.Label("Body content.")
            bs.Spacer()
            bs.Button("Save", accent="primary")
    app.run()


SCENES = {
    "hero":     hero,
    "fixed":    fixed,
    "weighted": weighted,
    "column":   column,
}

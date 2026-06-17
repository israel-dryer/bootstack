import bootstack as bs


def hero():
    with bs.App(title="SplitView", size=(680, 260), padding=20) as app:
        sv = bs.SplitView(grow=True, horizontal="stretch")
        with sv.add(weight=1, padding=12, gap=4, horizontal_items="stretch"):
            for item in ("Home", "Documents", "Images", "Settings"):
                bs.Button(item, variant="ghost", horizontal="stretch")
        with sv.add(weight=2, padding=12, gap=8):
            bs.Label("Content", font="heading-md")
            bs.Label("Select an item from the navigation pane.")
    app.run()


def vertical():
    with bs.App(title="SplitView — Vertical", size=(480, 300), padding=20) as app:
        sv = bs.SplitView(orient="vertical", grow=True, horizontal="stretch")
        with sv.add(weight=1, padding=12, gap=4):
            bs.Label("Top pane", font="heading-md")
            bs.Label("Upper content area.")
        with sv.add(weight=1, padding=12, gap=4):
            bs.Label("Bottom pane", font="heading-md")
            bs.Label("Lower content area.")
    app.run()


SCENES = {
    "hero":     hero,
    "vertical": vertical,
}

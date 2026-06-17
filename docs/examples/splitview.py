import bootstack as bs

with bs.App(title="SplitView", size=(680, 680), padding=20, gap=16) as app:

    # ── Horizontal split (default) ─────────────────────────────────────────
    with bs.Column(horizontal="stretch", gap=0):
        bs.Label("Horizontal", font="heading-md")

    sv = bs.SplitView(grow=True, horizontal="stretch")
    with sv.add(weight=1, padding=12, gap=8, horizontal_items="stretch"):
        bs.Label("Navigation", font="heading-md")
        bs.Divider()
        for item in ("Home", "Documents", "Images", "Settings", "Help"):
            bs.Button(item, variant="ghost")
    with sv.add(weight=2, padding=12, gap=8):
        bs.Label("Content", font="heading-md")
        bs.Label("Select an item from the navigation pane.")

    # ── Vertical split ─────────────────────────────────────────────────────
    with bs.Column(horizontal="stretch", gap=0):
        bs.Label("Vertical", font="heading-md")

    sv2 = bs.SplitView(orient="vertical", horizontal="stretch")
    with sv2.add(weight=1, padding=12, gap=4):
        bs.Label("Top pane", font="heading-md")
        bs.Label("Upper content area.")
    with sv2.add(weight=1, padding=12, gap=4):
        bs.Label("Bottom pane", font="heading-md")
        bs.Label("Lower content area.")

app.run()

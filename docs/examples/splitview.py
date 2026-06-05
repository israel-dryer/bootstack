import bootstack as bs

with bs.App(title="SplitView", size=(680, 680), padding=20, gap=16) as app:

    # ── Horizontal split (default) ─────────────────────────────────────────
    with bs.VStack(fill="x", gap=0):
        bs.Label("Horizontal", font="heading-md")

    sv = bs.SplitView(fill="both", expand=True)
    with sv.add(weight=1, padding=12, gap=8, fill_items="x"):
        bs.Label("Navigation", font="heading-md")
        bs.Separator(fill="x")
        for item in ("Home", "Documents", "Images", "Settings", "Help"):
            bs.Button(item, variant="ghost", fill="x")
    with sv.add(weight=2, padding=12, gap=8):
        bs.Label("Content", font="heading-md")
        bs.Label("Select an item from the navigation pane.")

    # ── Vertical split ─────────────────────────────────────────────────────
    with bs.VStack(fill="x", gap=0):
        bs.Label("Vertical", font="heading-md")

    sv2 = bs.SplitView(orient="vertical", fill="x")
    with sv2.add(weight=1, padding=12, gap=4):
        bs.Label("Top pane", font="heading-md")
        bs.Label("Upper content area.")
    with sv2.add(weight=1, padding=12, gap=4):
        bs.Label("Bottom pane", font="heading-md")
        bs.Label("Lower content area.")

app.run()

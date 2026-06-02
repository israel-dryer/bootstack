import bootstack as bs

with bs.App(title="ScrollView", size=(680, 900), padding=20, gap=16) as app:

    # ── Vertical scroll ────────────────────────────────────────────────────
    with bs.VStack(fill="x", gap=0):
        bs.Label("Vertical", font="heading-md")

    with bs.ScrollView(scroll_direction="vertical", scrollbar_visibility="always",
                       fill="both", expand=True):
        for i in range(1, 24):
            with bs.HStack(fill="x", padding=8):
                bs.Label(f"Row {i:02d}")
            bs.Separator(fill="x")

    # ── Square scrollbar variant ───────────────────────────────────────────
    with bs.VStack(fill="x", gap=0):
        bs.Label("scrollbar_variant='square'", font="heading-md")

    with bs.ScrollView(scroll_direction="vertical", scrollbar_visibility="always",
                       scrollbar_variant="square", fill="both", expand=True):
        for i in range(1, 24):
            with bs.HStack(fill="x", padding=8):
                bs.Label(f"Row {i:02d}")
            bs.Separator(fill="x")

    # ── Horizontal scroll ──────────────────────────────────────────────────
    with bs.VStack(fill="x", gap=0):
        bs.Label("Horizontal", font="heading-md")

    with bs.ScrollView(scroll_direction="horizontal", scrollbar_visibility="always",
                       fill="x"):
        with bs.HStack(gap=8, padding=8):
            for i in range(1, 25):
                bs.Button(f"Section {i:02d}", variant="outline")

app.run()

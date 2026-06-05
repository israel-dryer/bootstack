import bootstack as bs

with bs.App(title="ScrollView", size=(680, 500), padding=20, gap=16) as app:

    # ── Vertical scroll ────────────────────────────────────────────────────
    with bs.VStack(fill="x", gap=0):
        bs.Label("Vertical", font="heading-md")

    with bs.ScrollView(
            scroll_direction="vertical",
            scrollbar_visibility="always",
            fill="both", expand=True
    ):
        for i in range(1, 30):
            with bs.HStack(fill="x", padding=8):
                bs.Label(f"Row {i:02d}")
            bs.Separator(fill="x")

    # ── Horizontal scroll ──────────────────────────────────────────────────
    with bs.VStack(fill="x", gap=0):
        bs.Label("Horizontal (with border)", font="heading-md")

    with bs.ScrollView(
            scroll_direction="horizontal",
            scrollbar_visibility="always",
            fill="x",
            height=100,
            padding=3,
            show_border=True,
    ):
        with bs.HStack(gap=8, padding=8):
            for i in range(1, 25):
                bs.Button(f"Section {i:02d}", variant="outline")

app.run()

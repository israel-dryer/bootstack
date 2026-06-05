import bootstack as bs

with bs.App(title="Tabs", size=(680, 520), padding=20, gap=28) as app:

    # ── Horizontal (default) ──────────────────────────────────────────────────
    with bs.VStack(fill="x", gap=6):
        bs.Label("Horizontal (default)", font="heading-md")

        tabs = bs.Tabs(fill="x")
        with tabs.add("home", label="Home", padding=16, gap=8):
            bs.Label("Home", font="heading-md")
            bs.Label("Welcome to the Home tab.")
        with tabs.add("files", label="Files", padding=16, gap=8):
            bs.Label("Files", font="heading-md")
            bs.Label("Manage your files here.")
        with tabs.add("settings", label="Settings", padding=16, gap=8):
            bs.Label("Settings", font="heading-md")
            bs.Label("Adjust your preferences.")

    # ── Icons ─────────────────────────────────────────────────────────────────
    with bs.VStack(fill="x", gap=6):
        bs.Label("Icons", font="heading-md")

        tabs2 = bs.Tabs(fill="x")
        with tabs2.add("home", label="Home", icon="house", padding=16, gap=8):
            bs.Label("Home tab with icon.")
        with tabs2.add("files", label="Files", icon="folder", padding=16, gap=8):
            bs.Label("Files tab with icon.")
        with tabs2.add("settings", label="Settings", icon="gear", padding=16, gap=8):
            bs.Label("Settings tab with icon.")

    # ── Stretch tab width ─────────────────────────────────────────────────────
    with bs.VStack(fill="x", gap=6):
        bs.Label("tab_width='stretch'", font="heading-md")

        tabs3 = bs.Tabs(tab_width="stretch", fill="x")
        with tabs3.add("alpha", label="Alpha", padding=16, gap=8):
            bs.Label("Each tab shares the full bar width equally.")
        with tabs3.add("beta", label="Beta", padding=16, gap=8):
            bs.Label("Beta page.")
        with tabs3.add("gamma", label="Gamma", padding=16, gap=8):
            bs.Label("Gamma page.")

app.run()

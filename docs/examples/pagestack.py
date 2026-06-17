import bootstack as bs

with bs.App(title="PageStack", size=(680, 500), padding=20, gap=12) as app:

    bs.Label("PageStack — one page visible at a time", font="heading-md")

    # ── Navigation bar ────────────────────────────────────────────────────────
    with bs.Row(gap=6):
        btn_home = bs.Button("Home", accent="primary")
        btn_settings = bs.Button("Settings")
        btn_about = bs.Button("About")

    bs.Divider()

    # ── Page container ────────────────────────────────────────────────────────
    ps = bs.PageStack(grow=True, horizontal="stretch")

    with ps.add("home", gap=12):
        bs.Label("Welcome", font="heading-lg")
        bs.Label("This is the Home page.")
        bs.Label("Use the buttons above to switch pages.")
        bs.Divider()
        with bs.Row(gap=8):
            bs.Button("Get Started", accent="primary")
            bs.Button("Learn More", variant="outline")

    with ps.add("settings", layout="grid", columns=["auto", 1], gap=8):
        bs.Label("Username")
        bs.TextField(placeholder="your-username")
        bs.Label("Theme")
        bs.Select(options=["Light", "Dark", "System"])
        bs.Label("Language")
        bs.Select(options=["English", "Spanish", "French"])

    with ps.add("about", gap=12):
        bs.Label("About bootstack", font="heading-lg")
        bs.Label("A batteries-included Python desktop UI framework.")
        bs.Label("Build modern desktop apps without touching Tkinter.")

    ps.navigate("home")

    btn_home.on_click(lambda e: ps.navigate("home"))
    btn_settings.on_click(lambda e: ps.navigate("settings"))
    btn_about.on_click(lambda e: ps.navigate("about"))

app.run()

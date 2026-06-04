import bootstack as bs


def hero():
    with bs.App(title="PageStack", size=(680, 320), padding=20, gap=12) as app:
        with bs.HStack(fill="x", gap=6):
            btn_home     = bs.Button("Home",     accent="primary")
            btn_settings = bs.Button("Settings")
            btn_about    = bs.Button("About")
        bs.Separator()
        ps = bs.PageStack(fill="both", expand=True)
        with ps.add("home", gap=10):
            bs.Label("Welcome", font="heading-lg")
            bs.Label("This is the Home page.")
            with bs.HStack(gap=8):
                bs.Button("Get Started", accent="primary")
                bs.Button("Learn More", variant="outline")
        with ps.add("settings", layout="grid", columns=["auto", 1], gap=8, sticky_items="ew"):
            bs.Label("Username")
            bs.TextField(placeholder="your-username")
            bs.Label("Theme")
            bs.Select(values=["Light", "Dark", "System"])
        with ps.add("about", gap=8):
            bs.Label("About bootstack", font="heading-lg")
            bs.Label("A batteries-included Python desktop UI framework.")
        ps.navigate("home")
        btn_home.on_click(    lambda e: ps.navigate("home"))
        btn_settings.on_click(lambda e: ps.navigate("settings"))
        btn_about.on_click(   lambda e: ps.navigate("about"))
    app.run()


SCENES = {
    "hero": hero,
}

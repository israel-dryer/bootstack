import bootstack as bs


def metric_card(label, value):
    """A reusable builder — paints one metric card into the active container."""
    with bs.Card(padding=16, gap=4):
        bs.Label(label, font="caption")
        bs.Label(value, font="heading-md")


with bs.AppShell(title="My App", size=(800, 540)) as shell:

    # ── Toolbar ───────────────────────────────────────────────────────────────
    with shell.add_toolbar() as bar:
        bar.add_spacer()
        bar.add_theme_toggle()

    # ── Pages ─────────────────────────────────────────────────────────────────
    # Each page IS a column — set padding/gap on add_page; no inner wrapper.
    with shell.page_nav() as nav:
        with nav.add_page("dashboard", text="Dashboard", icon="speedometer2", padding=24, gap=12):
            bs.Label("Dashboard", font="heading-lg")
            bs.Label("Welcome back. Here is your overview.")
            with bs.Grid(columns=3, gap=12, horizontal="stretch"):
                metric_card("Revenue", "$12,400")
                metric_card("Users", "1,280")
                metric_card("Orders", "340")

        with nav.add_page("inbox", text="Inbox", icon="inbox", padding=24, gap=8):
            bs.Label("Inbox", font="heading-lg")
            bs.Label("No new messages.")

        nav.add_divider()
        nav.add_header("Documents")

        with nav.add_page("files", text="Files", icon="folder", padding=24, gap=8):
            bs.Label("Files", font="heading-lg")
            bs.Label("Your documents will appear here.")

        with nav.add_page("images", text="Images", icon="image", padding=24, gap=8):
            bs.Label("Images", font="heading-lg")
            bs.Label("Your images will appear here.")

        with nav.add_page("settings", text="Settings", icon="gear", pin_to_footer=True, padding=24, gap=8):
            bs.Label("Settings", font="heading-lg")
            bs.Label("Adjust your preferences.")

    shell.navigate("dashboard")

shell.run()
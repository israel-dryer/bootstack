import bootstack as bs

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
                with bs.Card(padding=16, gap=4):
                    bs.Label("Revenue", font="caption")
                    bs.Label("$12,400", font="heading-md")
                with bs.Card(padding=16, gap=4):
                    bs.Label("Users", font="caption")
                    bs.Label("1,280", font="heading-md")
                with bs.Card(padding=16, gap=4):
                    bs.Label("Orders", font="caption")
                    bs.Label("340", font="heading-md")

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
import bootstack as bs

with bs.AppShell(title="My App", size=(800, 540)) as shell:

    # ── Toolbar ───────────────────────────────────────────────────────────────
    shell.commandbar.add_spacer()
    shell.commandbar.add_button(icon="circle-half", command=bs.toggle_theme)

    # ── Pages ─────────────────────────────────────────────────────────────────
    with shell.add_page("dashboard", text="Dashboard", icon="speedometer2"):
        with bs.VStack(fill="x", gap=12, padding=24):
            bs.Label("Dashboard", font="heading-lg")
            bs.Label("Welcome back. Here is your overview.")
            with bs.Grid(columns=3, gap=12, fill="x", sticky_items="ew"):
                with bs.Card(padding=16, gap=4):
                    bs.Label("Revenue", font="caption")
                    bs.Label("$12,400", font="heading-md")
                with bs.Card(padding=16, gap=4):
                    bs.Label("Users", font="caption")
                    bs.Label("1,280", font="heading-md")
                with bs.Card(padding=16, gap=4):
                    bs.Label("Orders", font="caption")
                    bs.Label("340", font="heading-md")

    with shell.add_page("inbox", text="Inbox", icon="inbox"):
        with bs.VStack(fill="x", gap=8, padding=24):
            bs.Label("Inbox", font="heading-lg")
            bs.Label("No new messages.")

    shell.add_separator()
    shell.add_header("Documents")

    with shell.add_page("files", text="Files", icon="folder"):
        with bs.VStack(fill="x", gap=8, padding=24):
            bs.Label("Files", font="heading-lg")
            bs.Label("Your documents will appear here.")

    with shell.add_page("images", text="Images", icon="image"):
        with bs.VStack(fill="x", gap=8, padding=24):
            bs.Label("Images", font="heading-lg")
            bs.Label("Your images will appear here.")

    with shell.add_footer_page("settings", text="Settings", icon="gear"):
        with bs.VStack(fill="x", gap=8, padding=24):
            bs.Label("Settings", font="heading-lg")
            bs.Label("Adjust your preferences.")

    shell.navigate("dashboard")

shell.run()

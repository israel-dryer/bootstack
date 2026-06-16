import bootstack as bs


def hero():
    with bs.AppShell(title="My App", size=(720, 520)) as shell:
        shell._capture_full_window = True
        with shell.add_toolbar() as bar:
            with bar.add_menu("File") as file:
                file.add_action("New", shortcut="Mod+N", on_click=lambda: None)
                file.add_action("Open", shortcut="Mod+O", on_click=lambda: None)
                file.add_separator()
                file.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
            with bar.add_menu("View") as view:
                view.add_action("Refresh", shortcut="Mod+R", on_click=lambda: None)
            bar.add_spacer()
            bar.add_button(icon="search", on_click=lambda: None)
            bar.add_theme_toggle()

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

        with shell.add_footer_page("settings", text="Settings", icon="gear"):
            with bs.VStack(fill="x", gap=8, padding=24):
                bs.Label("Settings", font="heading-lg")
                bs.Label("Adjust your preferences.")

        shell.navigate("dashboard")
    shell.run()


def compact():
    with bs.AppShell(title="My App", size=(720, 520), sidebar_mode="compact") as shell:
        shell._capture_full_window = True
        with shell.add_toolbar() as bar:
            with bar.add_menu("File") as file:
                file.add_action("New", shortcut="Mod+N", on_click=lambda: None)
                file.add_action("Open", shortcut="Mod+O", on_click=lambda: None)
                file.add_separator()
                file.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
            with bar.add_menu("View") as view:
                view.add_action("Refresh", shortcut="Mod+R", on_click=lambda: None)
            bar.add_spacer()
            bar.add_button(icon="search", on_click=lambda: None)
            bar.add_theme_toggle()

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

        with shell.add_page("files", text="Files", icon="folder"):
            with bs.VStack(fill="x", gap=8, padding=24):
                bs.Label("Files", font="heading-lg")

        with shell.add_footer_page("settings", text="Settings", icon="gear"):
            with bs.VStack(fill="x", gap=8, padding=24):
                bs.Label("Settings", font="heading-lg")

        shell.navigate("dashboard")
    shell.run()


SCENES = {
    "hero":    hero,
    "compact": compact,
}

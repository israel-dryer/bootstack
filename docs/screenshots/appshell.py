import bootstack as bs


def _toolbar(shell):
    with shell.add_toolbar() as bar:
        with bar.add_menu("File") as file:
            file.add_action("New", shortcut="Mod+N", on_click=lambda: None)
            file.add_action("Open", shortcut="Mod+O", on_click=lambda: None)
            file.add_divider()
            file.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
        with bar.add_menu("View") as view:
            view.add_action("Refresh", shortcut="Mod+R", on_click=lambda: None)
        bar.add_spacer()
        bar.add_button(icon="search", on_click=lambda: None)
        bar.add_theme_toggle()


def hero():
    with bs.AppShell(title="My App", size=(720, 520)) as shell:
        shell._capture_full_window = True
        _toolbar(shell)

        with shell.page_nav() as nav:
            with nav.add_page("dashboard", text="Dashboard", icon="speedometer2", gap=12, padding=24):
                bs.Label("Dashboard", font="heading-lg")
                bs.Label("Welcome back. Here is your overview.")
                with bs.Grid(columns=3, gap=12, horizontal="stretch", horizontal_items="stretch"):
                    with bs.Card(padding=16, gap=4):
                        bs.Label("Revenue", font="caption")
                        bs.Label("$12,400", font="heading-md")
                    with bs.Card(padding=16, gap=4):
                        bs.Label("Users", font="caption")
                        bs.Label("1,280", font="heading-md")
                    with bs.Card(padding=16, gap=4):
                        bs.Label("Orders", font="caption")
                        bs.Label("340", font="heading-md")

            with nav.add_page("inbox", text="Inbox", icon="inbox", gap=8, padding=24):
                bs.Label("Inbox", font="heading-lg")
                bs.Label("No new messages.")

            nav.add_divider()
            nav.add_header("Documents")

            with nav.add_page("files", text="Files", icon="folder", gap=8, padding=24):
                bs.Label("Files", font="heading-lg")
                bs.Label("Your documents will appear here.")

            with nav.add_page("settings", text="Settings", icon="gear", pin_to_footer=True, gap=8, padding=24):
                bs.Label("Settings", font="heading-lg")
                bs.Label("Adjust your preferences.")

        shell.navigate("dashboard")
    shell.run()


def compact():
    with bs.AppShell(title="My App", size=(720, 520), sidebar_mode="compact") as shell:
        shell._capture_full_window = True
        _toolbar(shell)

        with shell.page_nav() as nav:
            with nav.add_page("dashboard", text="Dashboard", icon="speedometer2", gap=12, padding=24):
                bs.Label("Dashboard", font="heading-lg")
                bs.Label("Welcome back. Here is your overview.")
                with bs.Grid(columns=3, gap=12, horizontal="stretch", horizontal_items="stretch"):
                    with bs.Card(padding=16, gap=4):
                        bs.Label("Revenue", font="caption")
                        bs.Label("$12,400", font="heading-md")
                    with bs.Card(padding=16, gap=4):
                        bs.Label("Users", font="caption")
                        bs.Label("1,280", font="heading-md")
                    with bs.Card(padding=16, gap=4):
                        bs.Label("Orders", font="caption")
                        bs.Label("340", font="heading-md")

            with nav.add_page("inbox", text="Inbox", icon="inbox", gap=8, padding=24):
                bs.Label("Inbox", font="heading-lg")

            with nav.add_page("files", text="Files", icon="folder", gap=8, padding=24):
                bs.Label("Files", font="heading-lg")

            with nav.add_page("settings", text="Settings", icon="gear", pin_to_footer=True, gap=8, padding=24):
                bs.Label("Settings", font="heading-lg")

        shell.navigate("dashboard")
    shell.run()


def _selection(variant):
    # A focused shell foregrounding the sidebar, so the selection treatment is the
    # subject — identical except for page_nav(variant=).
    with bs.AppShell(title="My App", size=(460, 380), nav_accent="primary") as shell:
        shell._capture_full_window = True
        with shell.page_nav(variant=variant) as nav:
            with nav.add_page("home", text="Home", icon="house", padding=20, gap=8):
                bs.Label("Home", font="heading-md")
            with nav.add_page("reports", text="Reports", icon="bar-chart", padding=20):
                bs.Label("Reports", font="heading-md")
            with nav.add_page("team", text="Team", icon="people", padding=20):
                bs.Label("Team", font="heading-md")
        shell.navigate("home")
    shell.run()


def selection_ghost():
    _selection("ghost")


def selection_solid():
    _selection("solid")


SCENES = {
    "hero":    hero,
    "compact": compact,
    "selection-ghost": selection_ghost,
    "selection-solid": selection_solid,
}

if __name__ == '__main__':
    compact()
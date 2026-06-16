"""Hero screenshot for the undecorated-window / custom-titlebar docs.

A borderless AppShell whose title bar is the first toolbar
(``add_toolbar(show_window_controls=True)``) — it carries the app icon + label,
the min/max/close controls, and drag-to-move. A menu/command toolbar sits below
it, then the rail/sidebar/content body.

Regenerate with::

    py -3.12 docs/scripts/take_screenshots.py undecorated
"""
import bootstack as bs


def hero():
    with bs.AppShell(title="My App", size=(720, 480), undecorated=True) as shell:
        shell._capture_full_window = True
        # The title bar IS the first toolbar — it carries the window controls.
        with shell.add_toolbar(show_window_controls=True) as title:
            title.add_label("My App", icon="stack", font="caption")
            title.add_spacer()
            title.add_theme_toggle()
        # A menu / command toolbar below the title bar.
        with shell.add_toolbar() as bar:
            with bar.add_menu("File") as file:
                file.add_action("New", shortcut="Mod+N", on_click=lambda: None)
                file.add_separator()
                file.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
            with bar.add_menu("View") as view:
                view.add_action("Refresh", shortcut="Mod+R", on_click=lambda: None)
            bar.add_spacer()
            bar.add_button(icon="search", on_click=lambda: None)

        with shell.add_page("dashboard", text="Dashboard", icon="speedometer2"):
            with bs.VStack(fill="x", gap=12, padding=24):
                bs.Label("Dashboard", font="heading-lg")
                bs.Label("A borderless window with a custom title bar.")
        with shell.add_page("settings", text="Settings", icon="gear"):
            with bs.VStack(fill="x", gap=8, padding=24):
                bs.Label("Settings", font="heading-lg")
        shell.navigate("dashboard")
    shell.run()


SCENES = {
    "hero": hero,
}

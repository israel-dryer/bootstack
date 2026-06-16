"""Hero screenshots for the App Structures getting-started guide.

Two scenes contrasting the structural difference: a single-window App versus a
sidebar AppShell. Each captures the full OS window. Regenerate with::

    py -3.12 docs/scripts/take_screenshots.py app-structures
"""
import bootstack as bs


def app():
    with bs.App(title="Notes", size=(480, 340), padding=20, gap=10) as a:
        a._capture_full_window = True
        bs.Label("Notes", font="heading-lg")
        bs.Label("A single window you fill with widgets.", accent="secondary")
        bs.TextField(placeholder="Title", fill="x")
        bs.TextArea(value="Reach for App first — it covers anything that fits on one screen.",
                    fill="both", expand=True)
        with bs.HStack(fill="x", gap=8, anchor_items="e"):
            bs.Button("Discard", variant="ghost")
            bs.Button("Save", accent="primary")
    a.run()


def appshell():
    with bs.AppShell(title="Acme", size=(720, 460)) as shell:
        shell._capture_full_window = True
        with shell.add_toolbar() as bar:
            with bar.add_menu("File") as file:
                file.add_action("New", shortcut="Mod+N", on_click=lambda: None)
                file.add_separator()
                file.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
            bar.add_spacer()
            bar.add_theme_toggle()
        with shell.add_page("home", text="Home", icon="house"):
            with bs.VStack(fill="both", expand=True, anchor_items="w", gap=12, padding=20):
                bs.Label("Home", font="heading-lg")
                bs.Label("A window with a sidebar and swappable pages.", accent="secondary")
        with shell.add_page("reports", text="Reports", icon="bar-chart"):
            bs.Label("Reports", font="heading-lg")
        with shell.add_page("team", text="Team", icon="people"):
            bs.Label("Team", font="heading-lg")
        with shell.add_footer_page("settings", text="Settings", icon="gear"):
            bs.Label("Settings", font="heading-lg")
        shell.navigate("home")
    shell.run()


SCENES = {
    "app": app,
    "appshell": appshell,
}

"""Menu-bar screenshots — captured as the full OS window (titlebar + chrome),
like the Application category, since the menu bar / toolbar is window chrome."""
import bootstack as bs


def hero():
    """The menu bar with a menu open, plus a theme toggle in the toolbar."""
    with bs.App(title="Menu bar", size=(560, 340), padding=12) as app:
        app._capture_full_window = True
        with app.menubar.add_menu("File") as file:
            file.add_action("New", icon="file-earmark-plus", shortcut="Mod+N")
            file.add_action("Open", icon="folder2-open", shortcut="Mod+O")
            file.add_separator()
            file.add_action("Quit", shortcut="Mod+Q")
        with app.menubar.add_menu("Edit") as edit:
            edit.add_action("Undo", shortcut="Mod+Z")
            edit.add_action("Redo", shortcut="Mod+Shift+Z")
        with app.menubar.add_menu("View") as view:
            view.add_radio("Light", value="light", group="theme")
            view.add_radio("Dark", value="dark", group="theme")
        app.commandbar.add_spacer()
        app.commandbar.add_button(icon="circle-half")
        bs.Label("A cross-platform menu bar.", font="heading-md")

        # Open the File menu so the hero shows a dropdown (after the runner sets
        # topmost at t=800ms, before it grabs at t=950ms). It opens downward
        # into the window body, so it stays within the captured window rect.
        def open_first_menu():
            triggers = app.menubar._renderer._triggers
            if triggers:
                triggers[0].show_menu()

        app._tk_root.after(850, open_first_menu)
    app.run()


def _build_chrome(app):
    with app.menubar.add_menu("File") as file:
        file.add_action("Quit", shortcut="Mod+Q")
    with app.menubar.add_menu("Edit") as edit:
        edit.add_action("Undo", shortcut="Mod+Z")
    app.commandbar.add_button("Bold", icon="type-bold")
    app.commandbar.add_button("Italic", icon="type-italic")
    app.commandbar.add_separator()
    app.commandbar.add_button("Align", icon="text-left")
    app.commandbar.add_spacer()
    app.commandbar.add_button(icon="circle-half")


def fused():
    """menu_layout='fused' (default) — menus and toolbar share one row."""
    with bs.App(title="Menu bar — Fused", size=(560, 220), padding=12,
                menu_layout="fused") as app:
        app._capture_full_window = True
        _build_chrome(app)
        bs.Label("One row: menus on the left, toolbar on the right.", font="body")
    app.run()


def stacked():
    """menu_layout='stacked' — a menu row above a dedicated toolbar row."""
    with bs.App(title="Menu bar — Stacked", size=(560, 240), padding=12,
                menu_layout="stacked") as app:
        app._capture_full_window = True
        _build_chrome(app)
        bs.Label("Two rows: menus, then the toolbar.", font="body")
    app.run()


def surface():
    """chrome_surface='background' (+ chrome_divider=False) — bar blends in."""
    with bs.App(title="Menu bar — Surface", size=(560, 220), padding=12,
                chrome_surface="background", chrome_divider=False) as app:
        app._capture_full_window = True
        with app.menubar.add_menu("File") as file:
            file.add_action("Quit", shortcut="Mod+Q")
        with app.menubar.add_menu("Edit") as edit:
            edit.add_action("Undo", shortcut="Mod+Z")
        app.commandbar.add_spacer()
        app.commandbar.add_button(icon="circle-half")
        bs.Label("chrome_surface='background' blends the bar into the body.",
                 font="body")
    app.run()


SCENES = {
    "hero":     hero,
    "fused":    fused,
    "stacked":  stacked,
    "surface":  surface,
}

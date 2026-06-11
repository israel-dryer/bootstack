"""Menu bar demo — runnable on Windows, Linux (WSL), and macOS.

    python docs/examples/menu.py

On Windows/Linux the menus render as a themed in-window strip at the top of the
window. On macOS they relocate to the native global menu bar.
"""
import bootstack as bs

with bs.App(title="Menu demo", size=(560, 360), window_style=None) as app:

    with app.menu.add_menu("File") as file:
        file.add_action("New", shortcut="Mod+N", on_click=lambda: bs.toast("New"))
        file.add_action("Open", icon="folder2-open", shortcut="Mod+O",
                        on_click=lambda: bs.toast("Open"))
        file.add_separator()
        file.add_action("Quit", shortcut="Mod+Q", on_click=app.close)

    with app.menu.add_menu("Edit") as edit:
        edit.add_action("Undo", shortcut="Mod+Z", on_click=lambda: bs.toast("Undo"))
        edit.add_action("Redo", shortcut="Mod+Shift+Z", on_click=lambda: bs.toast("Redo"))
        edit.add_separator()
        edit.add_check("Word wrap", checked=True,
                       on_click=lambda: bs.toast("Toggled word wrap"))

    with app.menu.add_menu("View") as view:
        view.add_radio("Light", value="light", group="theme",
                       on_click=lambda: bs.set_theme("bootstrap-light"))
        view.add_radio("Dark", value="dark", group="theme",
                       on_click=lambda: bs.set_theme("bootstrap-dark"))

    bs.Label("Use the menus above. Shortcuts (e.g. Ctrl+N) fire too.",
             font="heading-md")

app.run()
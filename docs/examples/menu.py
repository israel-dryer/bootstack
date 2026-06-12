"""Menu bar demo — runnable on Windows, Linux (WSL), and macOS.

    python docs/examples/menu.py

On Windows/Linux the menus render as a themed strip at the top of the window;
on macOS they relocate to the native global menu bar. The theme switcher sits
in the toolbar, fused to the right of the menus.
"""
import bootstack as bs

with bs.App(title="Menu demo", size=(600, 380)) as app:

    with app.menubar.add_menu("File") as file:
        file.add_action("New", icon="file-earmark-plus", shortcut="Mod+N",
                        on_click=lambda: bs.toast("New"))
        file.add_action("Open", icon="folder2-open", shortcut="Mod+O",
                        on_click=lambda: bs.toast("Open"))
        file.add_action("Save", icon="floppy", shortcut="Mod+S",
                        on_click=lambda: bs.toast("Saved"))
        file.add_separator()
        file.add_action("Quit", shortcut="Mod+Q", on_click=app.close)

    with app.menubar.add_menu("Edit") as edit:
        edit.add_action("Undo", shortcut="Mod+Z", on_click=lambda: bs.toast("Undo"))
        edit.add_action("Redo", shortcut="Mod+Shift+Z", on_click=lambda: bs.toast("Redo"))
        edit.add_separator()
        edit.add_check("Word wrap", checked=True,
                       on_click=lambda: bs.toast("Toggled word wrap"))

    with app.menubar.add_menu("View") as view:
        view.add_radio("Zoom 50%",  value=0.5, group="zoom")
        view.add_radio("Zoom 100%", value=1.0, group="zoom")
        view.add_radio("Zoom 150%", value=1.5, group="zoom")

    # Theme switcher: a toggle in the toolbar, fused to the right of the menus.
    app.commandbar.add_spacer()
    app.commandbar.add_button(icon="circle-half", on_click=bs.toggle_theme)

    bs.Label("A sample menu, with a theme switcher in the toolbar.",
             font="heading-md")

app.run()

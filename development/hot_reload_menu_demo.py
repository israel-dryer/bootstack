"""Hot-reload demo with menus — for verifying the macOS native menu bar.

Run it live:   bootstack dev development/hot_reload_menu_demo.py

On macOS the File/Edit menus bridge to the native global menu bar; on
Windows/Linux they render as in-window dropdowns. This demo exists to verify
that a reload rebuilds the menu chrome cleanly on every platform — edit a menu
(add `file.add_action("New", on_click=lambda: None)`, rename an item, add an
Edit-menu entry) and save, then check the menu bar reflects the change and
isn't doubled or stale.
"""
import bootstack as bs

with bs.App(title="Hot Reload — Menus", padding=24, gap=12) as app:
    with app.add_toolbar() as tb:
        with tb.add_menu("File") as file:
            file.add_action("Open", shortcut="Mod+O", on_click=lambda: None)
            file.add_divider()
            file.add_action("Quit", shortcut="Mod+Q", on_click=app.close)
        with tb.add_menu("Edit") as edit:
            edit.add_action("Copy", shortcut="Mod+C", on_click=lambda: None)
            edit.add_action("Paste", shortcut="Mod+V", on_click=lambda: None)
        tb.add_spacer()
        tb.add_theme_toggle()

    bs.Label("Edit a menu and save — the menu bar should update cleanly.",
             font="heading-md")
    bs.Label("On macOS, watch the native menu bar at the top of the screen.")

app.run()

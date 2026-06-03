import bootstack as bs


def hero():
    with bs.App(title="ContextMenu", padding=20, size=(360, 280)) as app:
        with bs.VStack(gap=2, fill="x"):
            bs.Label("Project Proposal.docx", fill="x")
            bs.Label("Budget Report Q4.xlsx", fill="x")
            bs.Label("Meeting Notes.txt",     fill="x")

        menu = bs.ContextMenu(trigger=None)
        menu.add_item("Open",      icon="folder2-open")
        menu.add_item("Duplicate", icon="copy")
        menu.add_separator()
        menu.add_check_item("Starred", value=True)
        menu.add_separator()
        menu.add_item("Delete",    icon="trash")

        def _show():
            x = app.tk.winfo_rootx() + 80
            y = app.tk.winfo_rooty() + 70
            menu.show(position=(x, y))

        app.tk.after(850, _show)
    app.run()


def item_types():
    with bs.App(title="ContextMenu — Item Types", padding=20, size=(300, 280)) as app:
        menu = bs.ContextMenu(trigger=None)
        menu.add_item("Command item", icon="pencil")
        menu.add_separator()
        menu.add_check_item("Check item (on)",  value=True)
        menu.add_check_item("Check item (off)")
        menu.add_separator()
        menu.add_radio_item("Radio item A", value="a")
        menu.add_radio_item("Radio item B", value="b")

        def _show():
            x = app.tk.winfo_rootx() + 20
            y = app.tk.winfo_rooty() + 20
            menu.show(position=(x, y))

        app.tk.after(850, _show)
    app.run()


def shortcuts():
    with bs.App(title="ContextMenu — Shortcuts", padding=20, size=(300, 220)) as app:
        menu = bs.ContextMenu(trigger=None)
        menu.add_item("Cut",        icon="scissors",  shortcut="Mod+X")
        menu.add_item("Copy",       icon="copy",      shortcut="Mod+C")
        menu.add_item("Paste",      icon="clipboard", shortcut="Mod+V")
        menu.add_separator()
        menu.add_item("Select All",                   shortcut="Mod+A")

        def _show():
            x = app.tk.winfo_rootx() + 20
            y = app.tk.winfo_rooty() + 20
            menu.show(position=(x, y))

        app.tk.after(850, _show)
    app.run()


SCENES = {
    "hero":       hero,
    "item-types": item_types,
    "shortcuts":  shortcuts,
}

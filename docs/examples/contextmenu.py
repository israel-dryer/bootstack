"""ContextMenu — full feature demo.

Demonstrates basic usage, global callback, item types (command, check,
radio, separator), keyboard shortcuts, and dynamic item management.

Run with:
    python docs/examples/contextmenu.py
"""

import bootstack as bs


with bs.App(title="ContextMenu Demo", padding=20, gap=16) as app:

    # Basic — right-click trigger
    bs.Label("Basic (right-click the card)", font="heading-sm[bold]")
    with bs.Card(fill="x", padding=12) as card:
        bs.Label("Right-click anywhere in this card to open the menu.")

    menu = bs.ContextMenu(card, trigger="right_click")
    menu.add_item("Edit",      icon="pencil",  on_click=lambda: print("Edit"))
    menu.add_item("Duplicate", icon="copy",    on_click=lambda: print("Duplicate"))
    menu.add_separator()
    menu.add_item("Delete",    icon="trash",   on_click=lambda: print("Delete"))

    # Global on_select callback
    bs.Label("Global callback (right-click)", font="heading-sm[bold]")
    with bs.Card(fill="x", padding=12) as card2:
        bs.Label("Right-click for a menu with a shared callback.")

    def on_action(event):
        print("selected:", event["text"])

    menu2 = bs.ContextMenu(card2, on_select=on_action)
    menu2.add_item("Archive")
    menu2.add_item("Export")
    menu2.add_item("Delete")

    # Check and radio items
    bs.Label("Check and radio items (right-click)", font="heading-sm[bold]")
    with bs.Card(fill="x", padding=12) as card3:
        bs.Label("Right-click for a menu with toggleable and selectable items.")

    menu3 = bs.ContextMenu(card3)
    menu3.add_check_item("Bold",   value=True, on_click=lambda: print("Bold toggled"))
    menu3.add_check_item("Italic",             on_click=lambda: print("Italic toggled"))
    menu3.add_separator()
    menu3.add_radio_item("Small",  value="sm", on_click=lambda: print("Small"))
    menu3.add_radio_item("Medium", value="md", on_click=lambda: print("Medium"))
    menu3.add_radio_item("Large",  value="lg", on_click=lambda: print("Large"))

    # Keyboard shortcuts
    bs.Label("Keyboard shortcuts (right-click)", font="heading-sm[bold]")
    with bs.Card(fill="x", padding=12) as card4:
        bs.Label("Shortcut labels are display-only — bind handlers separately.")

    menu4 = bs.ContextMenu(card4)
    menu4.add_item("Cut",   icon="scissors",  shortcut="Mod+X")
    menu4.add_item("Copy",  icon="copy",      shortcut="Mod+C")
    menu4.add_item("Paste", icon="clipboard", shortcut="Mod+V")

    # Disabled items
    bs.Label("Disabled items (right-click)", font="heading-sm[bold]")
    with bs.Card(fill="x", padding=12) as card5:
        bs.Label("Items can be disabled at construction.")

    menu5 = bs.ContextMenu(card5)
    menu5.add_item("Save",    icon="floppy",       on_click=lambda: print("Save"))
    menu5.add_item("Publish", icon="cloud-upload", disabled=True)
    menu5.add_separator()
    menu5.add_item("Delete",  icon="trash",        disabled=True)

    # Dynamic item management
    bs.Label("Dynamic management (manual show button)", font="heading-sm[bold]")
    with bs.HStack(gap=8, anchor_items="center"):
        menu6 = bs.ContextMenu(trigger=None)
        menu6.add_item("Option A", key="a")
        menu6.add_item("Option B", key="b")
        key_c = menu6.add_item("Option C", key="c")
        menu6.remove_item(key_c)

        def _open_manual():
            btn_root = btn.tk
            x = btn_root.winfo_rootx()
            y = btn_root.winfo_rooty() + btn_root.winfo_height()
            menu6.show(position=(x, y))

        btn = bs.Button("Open menu", on_click=_open_manual)

app.run()

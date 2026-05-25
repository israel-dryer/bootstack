"""Demonstrate ContextMenu configuration helpers (configure_item, insert_item, remove_item, move_item)."""

import bootstack as bs
from bootstack import ContextMenu


def main():
    app = bs.Window("ContextMenu config demo",  minsize=(480, 320))

    status = bs.Label(app, text="Right-click inside the box to open the menu.", anchor='w')
    status.pack(fill='x', padx=10, pady=(10, 0))

    target = bs.Frame(app, surface='content[2]', padding=30)
    target.pack(fill='both', expand=True, padx=10, pady=10)
    bs.Label(target, text="Right-click here").pack()

    menu = ContextMenu(app, target=target, anchor="nw", attach="nw", offset=(4, 4))
    menu.add_command(text="Open", command=lambda: status.config(text="Open clicked"))
    menu.add_command(text="Save", command=lambda: status.config(text="Save clicked"))
    menu.add_separator()
    menu.add_checkbutton(text="Show Grid", value=True, command=lambda: status.config(text="Toggled grid"))

    def show_menu(event):
        menu.show(position=(event.x_root, event.y_root))

    target.bind("<Button-3>", show_menu)

    # --- demo controls -----------------------------------------------------
    control_frame = bs.Frame(app, padding=10)
    control_frame.pack(fill='x', padx=10, pady=10)

    def configure_first_item():
        """Use configure_item getter/setter."""
        try:
            menu.configure_item(0, text="Configured Open")
            cfg = menu.configure_item(0, "text")
            status.config(text=f"Item 0 text now: {cfg[-1]}")
        except IndexError as exc:
            status.config(text=str(exc))

    def insert_new_item():
        menu.insert_item(1, "command", text="Inserted", command=lambda: status.config(text="Inserted clicked"))
        status.config(text="Inserted item at index 1")

    def move_last_to_first():
        try:
            menu.move_item(len(menu.items()) - 1, 0)
            status.config(text="Moved last item to first")
        except IndexError as exc:
            status.config(text=str(exc))

    def remove_second():
        try:
            menu.remove_item(1)
            status.config(text="Removed item at index 1")
        except IndexError as exc:
            status.config(text=str(exc))

    bs.Button(control_frame, text="Configure first item", command=configure_first_item).pack(side='left', padx=5)
    bs.Button(control_frame, text="Insert item @1", command=insert_new_item).pack(side='left', padx=5)
    bs.Button(control_frame, text="Move last -> first", command=move_last_to_first).pack(side='left', padx=5)
    bs.Button(control_frame, text="Remove item @1", command=remove_second).pack(side='left', padx=5)

    app.mainloop()


if __name__ == "__main__":
    main()

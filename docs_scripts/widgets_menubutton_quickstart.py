import bootstack as bs

app = bs.App(minsize=(300, 200))

items = [
    {
        "label": "File",
        "items": [
            {"label": "New",  "icon": "file-plus",    "command": lambda: print("New")},
            {"label": "Open", "icon": "folder2-open", "command": lambda: print("Open")},
            {"type": "separator"},
            {"label": "Exit", "icon": "x-circle",     "command": app.destroy},
        ],
    },
    {
        "label": "Edit",
        "items": [
            {"label": "Undo", "icon": "arrow-counterclockwise", "command": lambda: print("Undo")},
            {"label": "Redo", "icon": "arrow-clockwise",        "command": lambda: print("Redo")},
        ],
    },
]

bs.MenuButton(app, text="Menu", menu=bs.create_menu(items)).pack(padx=20, pady=20)

app.mainloop()
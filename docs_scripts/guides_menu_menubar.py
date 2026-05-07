import bootstack as bs

def new_file(): ...
def open_file(): ...

app = bs.App(title="Editor")

app['menu'] = bs.create_menu([
    {
        "label": "File",
        "items": [
            {"label": "New",  "icon": "file-plus",    "command": new_file},
            {"label": "Open", "icon": "folder2-open", "command": open_file},
            {"type": "separator"},
            {"label": "Exit", "icon": "x-circle",     "command": app.destroy},
        ],
    },
    {
        "label": "Edit",
        "items": [
            {"label": "Undo", "icon": "arrow-counterclockwise", "shortcut": "Mod+Z"},
            {"label": "Redo", "icon": "arrow-clockwise",        "shortcut": "Mod+Shift+Z"},
        ],
    },
])

app.mainloop()
import bootstack as bs

app = bs.App()

container = bs.Frame(app, padding=24)
container.pack()

def stateful_icon(off_name, on_name):
    return {"name": off_name, "state": [("selected", on_name)]}

items = [
    ("Push alerts",  "bell-slash",       "bell-fill",         "primary"),
    ("Email digest", "envelope-slash",   "envelope-fill",     "primary"),
    ("Sound",        "volume-mute",      "volume-up",         "primary"),
    ("Microphone",   "mic-mute",         "mic-fill",          "danger"),
    ("Camera",       "camera-video-off", "camera-video-fill", "danger"),
    ("Tracking",     "eye-slash",        "eye-fill",          "warning"),
    ("Favorites",    "heart",            "heart-fill",        "danger"),
    ("Bookmarks",    "bookmark",         "bookmark-fill",     "primary"),
    ("Starred",      "star",             "star-fill",         "warning"),
]

grid = bs.GridFrame(container, columns=2, gap=32)
grid.pack()

checked_col   = bs.PackFrame(grid, direction="vertical", gap=4).grid()
unchecked_col = bs.PackFrame(grid, direction="vertical", gap=4).grid()

bs.Label(checked_col,   text="Checked",   font="body[bold]").pack(anchor="w", pady=(0, 6))
bs.Label(unchecked_col, text="Unchecked", font="body[bold]").pack(anchor="w", pady=(0, 6))

for text, off_icon, on_icon, accent in items:
    icon = stateful_icon(off_icon, on_icon)
    bs.CheckButton(checked_col,   text=text, icon=icon, value=True,  accent=accent).pack(anchor="w")
    bs.CheckButton(unchecked_col, text=text, icon=icon, value=False, accent=accent).pack(anchor="w")

app.mainloop()
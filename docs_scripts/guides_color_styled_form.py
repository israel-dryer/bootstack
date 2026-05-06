import bootstack as bs

app = bs.App(theme="ocean-light")

form = bs.LabelFrame(app, text="User settings", padding=20)
form.pack(padx=20, pady=20, fill="x")

grid = bs.GridFrame(form, columns=["auto", 1], gap=(10, 8), sticky_items='ew')
grid.pack(fill="x")

bs.Label(grid, text="Username:").grid()
bs.Entry(grid).grid()

bs.Label(grid, text="Email:").grid()
bs.Entry(grid).grid()

bs.Label(grid, text="Role:").grid()
bs.OptionMenu(grid, options=["User", "Admin", "Guest"]).grid()

toggles = bs.PackFrame(form, gap=5, fill_items='x')
toggles.pack(fill="x", pady=(15, 0))
bs.Switch(toggles, text="Email notifications").pack()
bs.Switch(toggles, text="Two-factor auth", accent="success").pack()

actions = bs.PackFrame(form, direction="horizontal", gap=10)
actions.pack(anchor="e", pady=(16, 0))

bs.Button(actions, text="Cancel", accent="secondary", variant="outline").pack()
bs.Button(actions, text="Save changes", accent="primary").pack()

app.mainloop()
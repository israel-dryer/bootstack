import bootstack as bs

app = bs.App()

# fixed width and padding
bs.Button(app, text="Wide", width=18, padding=(12, 6)).pack(pady=6)

# underline a keyboard shortcut character
bs.Button(app, text="Exit", underline=1).pack(pady=6)

# left-aligned content — useful for nav-item style buttons
bs.Button(app, text="Dashboard", icon="grid", anchor="w").pack(fill="x")

# compact density for toolbars
bs.Button(app, icon="gear", icon_only=True, density="compact").pack(pady=6)

app.mainloop()
import bootstack as bs

app = bs.App(title="Settings", minsize=(420, 360))

page = bs.PackFrame(app, direction="vertical", gap=12, padding=12)
page.pack(fill="both", expand=True)

# General card
general = bs.Card(page)
general.pack(fill="x")

bs.Label(general, text="General", font="heading-sm").pack(anchor="w")

form = bs.GridFrame(general, columns=["auto", 1], gap=(12, 8))
form.pack(fill="x", pady=(8, 0))

bs.Label(form, text="Name").grid(sticky="e")
bs.Entry(form).grid(sticky="ew")
bs.Label(form, text="Email").grid(sticky="e")
bs.Entry(form).grid(sticky="ew")

# Notifications card
notifications = bs.Card(page)
notifications.pack(fill="x")

bs.Label(notifications, text="Notifications", font="heading-sm").pack(anchor="w")
bs.CheckButton(notifications, text="Email me about activity").pack(anchor="w", pady=(8, 0))
bs.CheckButton(notifications, text="Email me about security").pack(anchor="w")

app.mainloop()
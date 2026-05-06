import bootstack as bs

app = bs.App(title="Sections Form")

container = bs.PackFrame(app, gap=12, padding=20)
container.pack(fill="both", expand=True)

account = bs.Card(container)
account.pack(fill="x")
bs.Label(account, text="Account", font="heading-sm").pack(anchor="w", pady=(0, 8))
bs.TextEntry(account, label="Email", required=True).pack(fill="x", pady=4)
bs.PasswordEntry(account, label="Password", required=True).pack(fill="x", pady=4)

profile = bs.Card(container)
profile.pack(fill="x")
bs.Label(profile, text="Profile", font="heading-sm").pack(anchor="w", pady=(0, 8))
bs.TextEntry(profile, label="Display name").pack(fill="x", pady=4)
bs.DateEntry(profile, label="Date of birth").pack(fill="x", pady=4)

app.mainloop()
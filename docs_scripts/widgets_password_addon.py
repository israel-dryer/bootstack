import bootstack as bs

app = bs.App()

pwd = bs.PasswordEntry(
    app,
    label="Password",
)
pwd.insert_addon(
    bs.Label,
    position="before",
    icon="lock",
    icon_only=True,
)
pwd.pack(padx=16, pady=16)

app.mainloop()
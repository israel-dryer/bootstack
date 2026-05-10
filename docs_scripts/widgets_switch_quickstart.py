import bootstack as bs

app = bs.App()

bs.Switch(app, text="Enable dark mode",    value=True).pack(padx=20, pady=6)
bs.Switch(app, text="Send notifications",  value=False).pack(padx=20, pady=6)

app.mainloop()
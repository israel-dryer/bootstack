import bootstack as bs

app = bs.App()

bs.CheckButton(app, text="Enable notifications",      value=True).pack(padx=20, pady=6)
bs.CheckButton(app, text="Send anonymous usage data", value=False).pack(padx=20, pady=6)

app.mainloop()
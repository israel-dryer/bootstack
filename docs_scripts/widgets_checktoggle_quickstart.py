import bootstack as bs

app = bs.App()

bs.CheckToggle(app, text="Bold",   value=False).pack(side="left", padx=4, pady=10)
bs.CheckToggle(app, text="Italic", value=True).pack(side="left", padx=4, pady=10)

app.mainloop()
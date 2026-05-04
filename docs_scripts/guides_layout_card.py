import bootstack as bs

app = bs.App()

card = bs.Card(app)
card.pack(fill="x", padx=12, pady=12)

bs.Label(card, text="User Settings", font="label").pack(anchor="w")
bs.CheckButton(card, text="Enable notifications").pack(anchor="w")
bs.CheckButton(card, text="Dark mode").pack(anchor="w")

app.mainloop()
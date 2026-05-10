import bootstack as bs

app = bs.App()

d = bs.DateEntry(app, label="Birthday")

d.insert_addon(
    bs.Label,
    position="before",
    icon="cake-fill",
    name="icon"
)

d.pack(padx=16, pady=16)

app.mainloop()
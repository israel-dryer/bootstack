import bootstack as bs

app = bs.App()

sb = bs.SelectBox(
    app,
    label="Status",
    items=["New", "In Progress", "Blocked", "Done"],
    value="New",
)
sb.pack(fill="x", padx=20, pady=20)

app.mainloop()
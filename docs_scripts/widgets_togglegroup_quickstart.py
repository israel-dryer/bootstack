import bootstack as bs

app = bs.App()

group = bs.ToggleGroup(app, mode="single", value="grid")
group.add("Grid",  value="grid")
group.add("List",  value="list")
group.add("Cards", value="cards")
group.pack(padx=20, pady=20)

app.mainloop()
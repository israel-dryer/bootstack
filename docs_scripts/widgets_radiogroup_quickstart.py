import bootstack as bs

app = bs.App()

group = bs.RadioGroup(app, text="Choose a plan", orient="vertical", value="basic")
group.add("Basic",      "basic")
group.add("Pro",        "pro")
group.add("Enterprise", "enterprise")
group.pack(padx=20, pady=20, fill="x")

app.mainloop()
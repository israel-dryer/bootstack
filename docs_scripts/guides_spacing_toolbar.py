import bootstack as bs

app = bs.App(title="Toolbar", minsize=(560, 80))

bar = bs.Frame(app, padding=8)
bar.pack(fill="x")

left = bs.PackFrame(bar, direction="row", gap=4)
left.pack(side="left")
bs.Button(left, text="Open").pack()
bs.Button(left, text="Save", accent="primary").pack()

right = bs.PackFrame(bar, direction="row", gap=4)
right.pack(side="right")
bs.Button(right, text="Profile").pack()
bs.Button(right, text="Sign out", variant="ghost").pack()

app.mainloop()
import bootstack as bs

app = bs.App(minsize=(400, 0))

toolbar = bs.PackFrame(app, direction="horizontal", padding=8, anchor_items="w").pack(fill='x')

bs.Button(toolbar, icon="folder2", icon_only=True).pack()
bs.Button(toolbar, icon="save", icon_only=True).pack()
bs.Button(toolbar, icon="printer", icon_only=True).pack()

app.mainloop()
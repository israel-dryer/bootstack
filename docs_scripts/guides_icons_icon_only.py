import bootstack as bs

app = bs.App()

frm = bs.PackFrame(app, direction="horizontal", padding=16, gap=16).pack()

bs.Button(frm, icon="plus", icon_only=True).pack()
bs.Button(frm, icon="x-lg", icon_only=True, accent="secondary").pack()

app.mainloop()
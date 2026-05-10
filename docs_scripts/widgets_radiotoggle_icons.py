import bootstack as bs

app = bs.App()

view = bs.Signal("grid")

frm = bs.PackFrame(app, direction="horizontal", padding=16).pack()

bs.RadioToggle(frm, text="Grid", icon="grid", signal=view, value="grid").pack()
bs.RadioToggle(frm, icon="grid", icon_only=True, signal=view, value="grid").pack()

app.mainloop()
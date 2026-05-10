import bootstack as bs

app = bs.App()

view = bs.Signal("grid")

frm = bs.PackFrame(app, direction="horizontal", padding=16).pack()

bs.RadioToggle(frm, text="Grid", signal=view, value="grid").pack()
bs.RadioToggle(frm, text="List", signal=view, value="list").pack()

app.mainloop()
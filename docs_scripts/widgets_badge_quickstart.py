import bootstack as bs

app = bs.App()

frm = bs.PackFrame(app, direction='horizontal', padding=16, gap=16).pack()

bs.Badge(frm, text="New").pack()
bs.Badge(frm, text="3", accent="primary").pack()

app.mainloop()
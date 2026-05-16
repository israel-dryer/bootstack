import bootstack as bs

app = bs.App()

frm = bs.PackFrame(app, direction='horizontal', padding=16, gap=16).pack()

bs.Badge(frm, text="Verified", icon="check").pack()
bs.Badge(frm, icon="bell", icon_only=True, accent="info").pack()

app.mainloop()
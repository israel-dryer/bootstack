import bootstack as bs

app = bs.App()

frm = bs.PackFrame(app, padding=16, gap=16, fill_items='x').pack(fill='x')

bs.Label(frm, text="Status", icon="check-circle", compound="left").pack()
bs.Label(frm, icon="gear", icon_only=True).pack()

app.mainloop()
import bootstack as bs

app = bs.App()

frm = bs.PackFrame(app, padding=16, gap=16, fill_items='x').pack(fill='x')

bs.Label(frm, text=1234.56, value_format="currency").pack()
bs.Label(frm, text=0.42,    value_format="percent").pack()

app.mainloop()
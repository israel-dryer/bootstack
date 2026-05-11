import bootstack as bs

app = bs.App(minsize=(300, 0))

frm = bs.PackFrame(app, padding=16, gap=16, fill_items='x').pack(fill='x')

bs.Label(frm, text="Left aligned",  anchor="w").pack()
bs.Label(frm, text="Centered",      anchor="center").pack()
bs.Label(frm, text="Right aligned", anchor="e").pack()

app.mainloop()
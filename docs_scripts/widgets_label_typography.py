import bootstack as bs

app = bs.App(minsize=(250, 0))

frm = bs.PackFrame(app, padding=16, gap=16, fill_items='x').pack(fill='x')

bs.Label(frm, text="Section heading", font="heading-lg[bold]").pack()
bs.Label(frm, text="Body copy",       font="body").pack()
bs.Label(frm, text="Caption text",    font="label[9]").pack()

app.mainloop()
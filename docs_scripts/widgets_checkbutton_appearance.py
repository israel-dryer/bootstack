import bootstack as bs

app = bs.App()

frm = bs.PackFrame(app, direction="horizontal", gap=16, padding=16).pack()

bs.CheckButton(frm).pack()
bs.CheckButton(frm, accent="secondary").pack()
bs.CheckButton(frm, accent="success").pack()
bs.CheckButton(frm, accent="info").pack()
bs.CheckButton(frm, accent="warning").pack()
bs.CheckButton(frm, accent="danger").pack()
bs.CheckButton(frm, accent="dark").pack()
bs.CheckButton(frm, accent="light").pack()

app.mainloop()
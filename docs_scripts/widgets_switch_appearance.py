import bootstack as bs

app = bs.App()

frm = bs.PackFrame(app, direction="horizontal", gap=16, padding=16).pack()

bs.Switch(frm).pack()
bs.Switch(frm, accent="secondary").pack()
bs.Switch(frm, accent="success").pack()
bs.Switch(frm, accent="info").pack()
bs.Switch(frm, accent="warning").pack()
bs.Switch(frm, accent="danger").pack()
bs.Switch(frm, accent="dark").pack()
bs.Switch(frm, accent="light").pack()

app.mainloop()
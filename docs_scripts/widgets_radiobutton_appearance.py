import bootstack as bs

app = bs.App()

frm = bs.PackFrame(app, direction="horizontal", gap=16, padding=16).pack()

bs.RadioButton(frm).pack()
bs.RadioButton(frm, accent="secondary").pack()
bs.RadioButton(frm, accent="success").pack()
bs.RadioButton(frm, accent="info").pack()
bs.RadioButton(frm, accent="warning").pack()
bs.RadioButton(frm, accent="danger").pack()
bs.RadioButton(frm, accent="dark").pack()
bs.RadioButton(frm, accent="light").pack()

app.mainloop()
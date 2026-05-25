import bootstack as bs

app = bs.App(theme='light')


frm = bs.PackFrame(app, padding=16, gap=16, fill_items='x').pack()

bs.Button(frm, text='default').pack()

bs.Button(frm, accent='primary', text='primary').pack()

bs.Button(frm, accent='success', text='success').pack()

bs.Button(frm, accent='warning', text='warning').pack()

bs.Button(frm, accent='danger', text='danger').pack()

bs.MenuButton(frm, accent='light', text='light').pack()

bs.TextEntry(frm, label="Text Entry").pack()

bs.Button(frm, text='default outline', variant='outline').pack()
bs.Button(frm, text='primary outline', accent='primary', variant='outline').pack()

bs.Button(frm, text='default ghost', variant='ghost').pack()
bs.Button(frm, text='primary ghost', accent='primary', variant='ghost').pack()


app.mainloop()

# default, primary, success, warning, danger
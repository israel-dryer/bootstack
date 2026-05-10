import bootstack as bs

app = bs.App()

frm = bs.PackFrame(app, direction='horizontal', gap=16, padding=16).pack()

email = bs.TextEntry(frm, label="Email")
email.insert_addon(bs.Label, position='before', icon='envelope')
email.pack(side='left', padx=10, anchor='s')

def handle_search():
    ...

search = bs.TextEntry(frm)
search.insert_addon(bs.Button, position='after', icon='search', command=handle_search)
search.pack(side='left', padx=10, anchor='s')

app.mainloop()
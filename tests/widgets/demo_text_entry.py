import bootstack as bs
from bootstack import TextEntry

app = bs.Window(theme="dark")


te = TextEntry(app, value="Israel", label="First Name", required=True, message="What shall we call you?")
te.pack(padx=16, pady=(8, 4), fill='x')

te = TextEntry(app, label="First Name", required=True)
te.insert_addon(bs.Button, 'before', icon='binoculars-fill')
te.pack(fill='x', padx=16, pady=(4, 8))

te.insert('end', 'Something')

bs.Button(app, text="Disable Text Entry", command=te.disable).pack(padx=16, pady=(4, 8))
bs.Button(app, text="Readonly Text Entry", command=te.readonly).pack(padx=16, pady=(4, 8))

te['show'] = '*'


app.mainloop()

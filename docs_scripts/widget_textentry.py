import bootstack as bs

app = bs.App(theme="docs-dark")

r1 = bs.Frame(app, padding=16)
r1.pack(side='top')

# entry states
bs.TextEntry(r1, value='Active', label='Label', show_message=True).pack(side='left', padx=10)
bs.TextEntry(r1, value='Normal', label='Label', required=True, message='This field is required', show_message=True).pack(side='left', padx=10)
bs.TextEntry(r1, value='Readonly', state='readonly', label='Label', show_message=True).pack(side='left', padx=10)
bs.TextEntry(r1, value='Disabled', state='disabled', label='Label', show_message=True).pack(side='left', padx=10)


# prefix example

r2 = bs.Frame(app, padding=16)
r2.pack(side='top')

email = bs.TextEntry(r2, label="Email")
email.insert_addon(bs.Label, position='before', icon='envelope')
email.pack(side='left', padx=10, anchor='s')

def handle_search():
    ...

search = bs.TextEntry(r2)
search.insert_addon(bs.Button, position='after', icon='search', command=handle_search)
search.pack(side='left', padx=10, anchor='s')

# localization and value format
r3 = bs.Frame(app, padding=16)
r3.pack(side='top')

bs.TextEntry(r3, label="Currency", value=1234.56, value_format="currency").pack(side='left', padx=10)
bs.TextEntry(r3, label="Short Date", value='March 14, 1981', value_format='shortDate').pack(side='left', padx=10)
bs.TextEntry(r3, label="Fixed Point", value=15422354, value_format="fixedPoint").pack(side='left', padx=10)


# colors
r4 = bs.Frame(app, padding=16)
r4.pack(side='top')

for color in ['primary', 'secondary', 'success']:
    te = bs.TextEntry(r4, value=color, bootstyle=color)
    te.pack(side='left', padx=10)

r5 = bs.Frame(app, padding=16)
r5.pack(side='top')

for color in ['info', 'warning', 'danger']:
    te = bs.TextEntry(r5, value=color, bootstyle=color)
    te.pack(side='left', padx=10)

app.mainloop()
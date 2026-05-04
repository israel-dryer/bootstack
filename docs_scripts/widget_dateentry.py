import bootstack as bs

app = bs.App(theme="docs-light")

r1 = bs.Frame(app, padding=16)
r1.pack(side='top')

r2 = bs.Frame(app, padding=16)
r2.pack(side='top')

# entry states
bs.DateEntry(r1, value='2030-12-31', label='Active', show_message=True, width=16).pack(side='left', padx=10)
bs.DateEntry(r1, value='2030-12-31', label='Normal', required=True, message='This field is required', show_message=True, width=16).pack(side='left', padx=10)
bs.DateEntry(r1, value='2030-12-31', state='readonly', label='Readonly', show_message=True, width=16).pack(side='left', padx=10)
bs.DateEntry(r1, value='2030-12-31', state='disabled', label='Disabled', show_message=True, width=16).pack(side='left', padx=10)


# colors
r3 = bs.Frame(app, padding=16)
r3.pack(side='top')

for color in ['primary', 'secondary', 'success']:
    te = bs.DateEntry(r3, value='2030-12-31', bootstyle=color)
    te.pack(side='left', padx=10)

r5 = bs.Frame(app, padding=16)
r5.pack(side='top')

for color in ['info', 'warning', 'danger']:
    te = bs.DateEntry(r5, value='2030-12-31', bootstyle=color)
    te.pack(side='left', padx=10)

# prefix example

r2 = bs.Frame(app, padding=16)
r2.pack(side='top')

birthday = bs.DateEntry(r2, label="Birthday")
birthday.insert_addon(bs.Label, position='before', icon='cake-fill')
birthday.pack(side='left', padx=10, anchor='s')


# localization and value format
r7 = bs.Frame(app, padding=16)
r7.pack(side='top')


bs.DateEntry(
    r7,
    label="Short Date",
    value="March 14, 1981",
    value_format="shortDate",
).pack(side="left", padx=10)

bs.DateEntry(
    r7,
    label="Long Date",
    value="1981-03-14",
    value_format="longDate",
).pack(side="left", padx=10)



bs.DateEntry(app, label='Due Date', value='2025-12-31', message='Pick a date or type one').pack(padx=10, pady=20)




app.mainloop()

import bootstack as bs

app = bs.App(theme="docs-dark")

r1 = bs.Frame(app, padding=16)
r1.pack(side='top')

r2 = bs.Frame(app, padding=16)
r2.pack(side='top')

# entry states
bs.NumericEntry(r1, value=123456, label='Active', show_message=True, width=15).pack(side='left', padx=10)
bs.NumericEntry(r1, value=123456, label='Normal', required=True, message='This field is required', show_message=True, width=15).pack(side='left', padx=10)
bs.NumericEntry(r1, value=123456, state='readonly', label='Readonly', show_message=True, width=15).pack(side='left', padx=10)
bs.NumericEntry(r1, value=123456, state='disabled', label='Disabled', show_message=True, width=15).pack(side='left', padx=10)


# colors
r3 = bs.Frame(app, padding=16)
r3.pack(side='top')

for color in ['primary', 'secondary', 'success']:
    te = bs.NumericEntry(r3, value=123456, bootstyle=color)
    te.pack(side='left', padx=10)

r5 = bs.Frame(app, padding=16)
r5.pack(side='top')

for color in ['info', 'warning', 'danger']:
    te = bs.NumericEntry(r5, value=123456, bootstyle=color)
    te.pack(side='left', padx=10)

# prefix example

r2 = bs.Frame(app, padding=16)
r2.pack(side='top')

salary = bs.NumericEntry(r2, label="Salary")
salary.insert_addon(bs.Label, position='before', icon='currency-euro')
salary.pack(side='left', padx=10, anchor='s')

size = bs.NumericEntry(r2, label="Size", show_spin_buttons=False)
size.insert_addon(bs.Button, position='before', icon='rulers')
size.insert_addon(bs.Label, position='after', text='cm', font='label[9]')
size.pack(side='left', padx=10, anchor='s')


# localization and value format
r7 = bs.Frame(app, padding=16)
r7.pack(side='top')


bs.NumericEntry(
    r7,
    label="Currency",
    value=1234.56,
    value_format="currency",
).pack(side="left", padx=10)

bs.NumericEntry(
    r7,
    label="Fixed Point",
    value=15422354,
    value_format="fixedPoint",
).pack(side="left", padx=10)

bs.NumericEntry(
    r7,
    label="Percent",
    value=0.35,
    value_format="percent",
).pack(side="left", padx=10)

app.mainloop()
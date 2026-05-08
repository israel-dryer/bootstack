import bootstack as bs

app = bs.App()

r1 = bs.Frame(app, padding=16)
r1.pack(side='top')

r2 = bs.Frame(app, padding=16)
r2.pack(side='top')

# entry states
bs.SpinnerEntry(r1, value='Active', label='Label', show_message=True).pack(side='left', padx=10)
bs.SpinnerEntry(r1, value='Normal', label='Label', required=True, message='This field is required', show_message=True).pack(side='left', padx=10)
bs.SpinnerEntry(r1, value='Readonly', state='readonly', label='Label', show_message=True).pack(side='left', padx=10)
bs.SpinnerEntry(r1, value='Disabled', state='disabled', label='Label', show_message=True).pack(side='left', padx=10)


# prefix example

r2 = bs.Frame(app, padding=16)
r2.pack(side='top')

salary = bs.SpinnerEntry(r2, label="Salary")
salary.insert_addon(bs.Label, position='before', icon='currency-euro')
salary.pack(side='left', padx=10, anchor='s')

size = bs.SpinnerEntry(r2, label="Size", values=['Small', 'Med', 'Large'], value='Small')
size.insert_addon(bs.Button, position='before', icon='rulers')
size.pack(side='left', padx=10, anchor='s')


# localization and value format
r7 = bs.Frame(app, padding=16)
r7.pack(side='top')


bs.SpinnerEntry(
    r7,
    label="Currency",
    value=9.99,
    increment=0.01,
    value_format="currency",
).pack(side="left", padx=10)

bs.SpinnerEntry(
    r7,
    label="Fixed Point",
    value=1500,
    increment=10,
    value_format="fixedPoint",
).pack(side="left", padx=10)

bs.SpinnerEntry(
    r7,
    label="Percent",
    value=0.25,
    increment=0.05,
    value_format="percent",
).pack(side="left", padx=10)

app.mainloop()
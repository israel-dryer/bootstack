import bootstack as bs

app = bs.App()

# prefix example

r2 = bs.Frame(app, padding=16)
r2.pack(side='top')

salary = bs.SpinnerEntry(r2, label="Salary")
salary.insert_addon(bs.Label, position='before', icon='currency-euro')
salary.pack(side='left', padx=10, anchor='s')

size = bs.SpinnerEntry(r2, label="Size", values=['Small', 'Med', 'Large'], value='Small')
size.insert_addon(bs.Button, position='before', icon='rulers')
size.pack(side='left', padx=10, anchor='s')


app.mainloop()
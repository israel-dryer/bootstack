import bootstack as bs



app = bs.App(theme="docs-light")

r1 = bs.Frame(app, padding=10)
r1.pack(side='top')

r2 = bs.Frame(app, padding=10)
r2.pack(side='top')

r3 = bs.Frame(app, padding=10)
r3.pack(side='top')

r4 = bs.Frame(app, padding=10)
r4.pack(side='top')


# unchecked
b1 = bs.CheckButton(r1)
b1.pack(side='left', padx=10)
b1.invoke()
b1.invoke()

# checked
b2 = bs.CheckButton(r1)
b2.pack(side='left', padx=10)
b2.invoke()

# unchecked disabled
b1 = bs.CheckButton(r1)
b1.pack(side='left', padx=10)
b1.invoke()
b1.invoke()
b1['state'] = 'disabled'

# checked
b2 = bs.CheckButton(r1)
b2.pack(side='left', padx=10)
b2.invoke()
b2['state'] = 'disabled'

# indeterminate
b3 = bs.CheckButton(r2)
b3.pack(side='left', padx=10)

# indeterminate disable
b3 = bs.CheckButton(r2)
b3.pack(side='left', padx=10)
b3['state'] = 'disabled'


# toggles

b4 = bs.CheckButton(r3, bootstyle='toggle')
b4.pack(side='left', padx=10)
b4.state(['!selected'])

b4 = bs.CheckButton(r3, bootstyle='toggle')
b4.pack(side='left', padx=10)
b4.state(['selected'])

# with labels

b4 = bs.CheckButton(r4, text="checkbutton")
b4.pack(side='left', padx=10)
b4.state(['!selected'])

b4 = bs.CheckButton(r4, text="toggle", bootstyle='toggle')
b4.pack(side='left', padx=10)
b4.state(['selected'])


# colors
colors = bs.Frame(app, padding=(16, 8))
colors.pack(side='top')
for color in ['primary', 'secondary', 'success', 'info', 'warning', 'danger', 'light', 'dark']:
    b = bs.CheckButton(colors, bootstyle=color)
    b.pack(side='left', padx=8)
    b.invoke()

colors = bs.Frame(app, padding=(16, 8))
colors.pack(side='top')
for color in ['primary', 'secondary', 'success', 'info', 'warning', 'danger', 'light', 'dark']:
    b = bs.CheckButton(colors, bootstyle=color + '-toggle')
    b.pack(side='left')
    b.invoke()

icons = bs.Frame(app, padding=(16, 8))
icons.pack(side='top')

bs.CheckButton(icons, value=None, icon='mic-fill', text='Volume').pack()

app.mainloop()
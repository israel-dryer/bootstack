import bootstack as bs

app = bs.App()

colors = ['primary', 'secondary', 'success', 'info', 'warning', 'danger']

def change_theme():
    if bs.get_theme() == 'dark':
        bs.set_theme('light')
    else:
        bs.set_theme('dark')

bs.Button(app, text="Change Theme", command=change_theme).pack(pady=10)

for color in colors:
    b = bs.Combobox(app, bootstyle=color, width=20, values=colors)
    b.set(color)
    b.pack(padx=20, pady=20)

app.mainloop()
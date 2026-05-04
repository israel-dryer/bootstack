import bootstack as bs

app = bs.Window()

colors = ['default', 'primary', 'secondary', 'success', 'info', 'warning', 'danger']

nb = bs.Notebook(app)
nb.pack(padx=20, pady=20)

for c in colors:
    nb.insert('end', bs.Frame(nb, width=100, height=100), text=c)

nb = bs.Notebook(app, bootstyle="success-underline")
nb.pack(padx=20, pady=20)

for c in colors:
    nb.insert('end', bs.Frame(nb, width=100, height=100), text=c)

nb = bs.Notebook(app, bootstyle="danger-underline")
nb.pack(padx=20, pady=20)

for c in colors:
    nb.insert('end', bs.Frame(nb, width=100, height=100), text=c)

app.mainloop()

import bootstack as bs

app = bs.Window(theme="flatly")


menu = bs.Menu(app)
file_menu = bs.Menu(menu)
menu.add_cascade(label="File", menu=file_menu)
for command in ['Open', 'New', 'Closed']:
    file_menu.add_command(label=command)

other_menu = bs.Menu(file_menu)
file_menu.add_cascade(label="Other", menu=other_menu)
for command in ['Exit', 'Quit']:
    other_menu.add_command(label=command)

app['menu'] = menu


app.mainloop()
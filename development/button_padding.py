import bootstack as bs


app = bs.App()

f = bs.Frame(app, padding=16).pack(fill='both')

btn = bs.CheckToggle(f, icon='bootstrap', text='Destination', accent='primary', variant='ghost', padding=(64, 4, 16, 4)).pack()

app.mainloop()
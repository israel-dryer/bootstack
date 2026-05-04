import bootstack as bs



app = bs.App()

f1 = bs.Frame(width=100, height=100)
f1.pack()

f2 = bs.Frame(width=200, height=200, bootstyle='danger')
f2.pack(fill='both', expand=True)

b1 = bs.Button(f2, text='Test')
b1.pack()

#f2.configure_style_options(surface_color='primary')
f2.configure(bootstyle='primary')

app.mainloop()
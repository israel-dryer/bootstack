import bootstack as bs

app = bs.Window()

sf = bs.ScrollView(app, padding=16, scrollbar_variant='rounded')
sf.pack(fill='both', expand=True)

text = bs.Text(sf)

text.insert('end', 'Hello world')

sf.add(text)

app.mainloop()
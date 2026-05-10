import bootstack as bs

app = bs.App(minsize=(300, 0))

scale = bs.Scale(app, from_=0, to=100, value=50)
scale.pack(fill="x", padx=20, pady=10)

app.mainloop()
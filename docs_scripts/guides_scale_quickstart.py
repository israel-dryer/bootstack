import bootstack as bs

app = bs.App(minsize=(300, 0))

slider = bs.Slider(app, minvalue=0, maxvalue=100, value=50)
slider.pack(fill="x", padx=20, pady=10)

app.mainloop()

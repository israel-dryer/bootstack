import bootstack as bs

app = bs.App(title="Hello", minsize=(400, 200), settings=bs.AppSettings(locale="es_ES"))

bs.Button(app, text="OK").pack(pady=20)
bs.Label(app, text="Saludos").pack()

app.mainloop()
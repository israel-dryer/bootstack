import bootstack as bs

app = bs.App()

bs.Label(app, text="Hello world").pack(padx=20, pady=20)

app.mainloop()
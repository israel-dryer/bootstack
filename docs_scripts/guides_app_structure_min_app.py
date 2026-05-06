import bootstack as bs

app = bs.App(title="Hello", minsize=(400, 300))

bs.Label(app, text="Hello, bootstack!").pack(padx=20, pady=20)
bs.Button(app, text="Close", command=app.destroy).pack(pady=10)

app.mainloop()
import bootstack as bs

app = bs.App(title="Quick Start", minsize=(300, 200))

frame = bs.Frame(app, padding=20)
frame.pack(fill="both", expand=True)

bs.Label(frame, text="Hello, bootstack!").pack(pady=10)
bs.Button(frame, text="Close", command=app.destroy).pack()

app.mainloop()
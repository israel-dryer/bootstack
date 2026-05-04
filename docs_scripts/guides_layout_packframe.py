import bootstack as bs

app = bs.App()

form = bs.PackFrame(app, direction="vertical", gap=8, padding=12)
form.pack(fill="both", expand=True)

bs.Label(form, text="Username").pack()
bs.Entry(form).pack()
bs.Label(form, text="Password").pack()
bs.Entry(form, show="*").pack()
bs.Button(form, text="Login", accent="primary").pack()

app.mainloop()
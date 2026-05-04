import bootstack as bs

app = bs.App(theme='dark')


pw1 = bs.PanedWindow(app, orient='horizontal', accent="primary")
pw1.pack(fill='both', expand=True, padx=20, pady=20)

pw1.add(bs.Frame(pw1, width=100, height=100))
pw1.add(bs.Frame(pw1, width=100, height=100))


pw2 = bs.PanedWindow(app, orient='horizontal')
pw2.pack(fill='both', expand=True, padx=20, pady=20)

pw2.add(bs.Frame(pw2, width=100, height=100))
pw2.add(bs.Frame(pw2, width=100, height=100))

app.update_idletasks()

app.mainloop()
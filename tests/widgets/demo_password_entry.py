import bootstack as bs

app = bs.App()


pe = bs.PasswordEntry(accent='info')
pe.pack(padx=10, pady=10, fill='x')


app.mainloop()
import bootstack as bs

app = bs.App()

bs.TextEntry().pack(padx=10, pady=10)
bs.PasswordEntry().pack(padx=10, pady=10)

app.mainloop()
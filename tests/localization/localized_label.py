import bootstack as bs

app = bs.App()

bs.MessageCatalog.locale("zh")

lf = bs.LabelFrame(app, text='Close', padding=8)
lf.pack(padx=20, pady=20)

# disabling localization on this field
bs.Label(lf, text='Cancel', localize=False).pack(padx=20, pady=20)

# allow default localization
bs.Label(lf, text='Cancel').pack(padx=20, pady=20)

# use a specific value format in the current locale
bs.Label(lf, text=12456, value_format='currency').pack(padx=20, pady=20)

bs.Button(lf, text='Submit', command=lambda: bs.MessageCatalog.locale('fr')).pack(padx=20, pady=20)

bs.CheckButton(lf, text='Close').pack(padx=20, pady=20)

bs.TextEntry(lf, label="Submit").pack(padx=20, pady=20, fill='x')

bs.NumericEntry(lf, label="Cancel", value_format="currency").pack(padx=20, pady=20, fill='x')

bs.DateEntry(lf, label="Birthday", value="March 14, 1981").pack(padx=20, pady=20, fill='x')



app.mainloop()

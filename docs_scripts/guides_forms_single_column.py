import bootstack as bs

app = bs.App(title="Single Column Form")

form = bs.Card(app, padding=20)
form.pack(fill="both", expand=True, padx=20, pady=20)

bs.TextEntry(form, label="Name", required=True).pack(fill="x", pady=4)
bs.TextEntry(form, label="Email", required=True).pack(fill="x", pady=4)
bs.NumericEntry(form, label="Age", value=18, minvalue=0).pack(fill="x", pady=4)

app.mainloop()
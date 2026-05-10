import bootstack as bs

app = bs.App(minsize=(275, 375))

bs.DateEntry(app, label='Due Date', value_format="longDate").pack(padx=16, pady=16, anchor='nw')

app.mainloop()
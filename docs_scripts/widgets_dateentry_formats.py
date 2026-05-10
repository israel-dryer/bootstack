import bootstack as bs

app = bs.App()

frm = bs.GridFrame(app, columns=3, gap=16, padding=16).pack()

bs.DateEntry(frm, label="Short Date", value="2025-01-15", value_format="shortDate").grid()
bs.DateEntry(frm, label="ISO Format", value="2025-01-15", value_format="yyyy-MM-dd").grid()
bs.DateEntry(frm, label="Long Date",  value="2025-01-15", value_format="longDate").grid()

app.mainloop()
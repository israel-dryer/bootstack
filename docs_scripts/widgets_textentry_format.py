import bootstack as bs

app = bs.App()

frm = bs.GridFrame(app, columns=2, padding=16, gap=16).pack()

bs.TextEntry(frm, label="Amount",    value=1234.56,        value_format="currency").grid()
bs.TextEntry(frm, label="Date",      value="March 14 1981", value_format="shortDate").grid()
bs.TextEntry(frm, label="Percent",   value=0.42,           value_format="percent").grid()

# Precision control via dict
bs.TextEntry(frm, label="Rate", value=0.0875, value_format={"type": "percent", "precision": 1}).grid()

# Custom ICU pattern
bs.TextEntry(frm, label="Code", value_format="000-000").grid()

app.mainloop()
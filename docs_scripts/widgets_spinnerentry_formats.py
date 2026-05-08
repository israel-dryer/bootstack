import bootstack as bs

app = bs.App()

frm = bs.GridFrame(app, columns=2, gap=16, padding=16).pack()

bs.SpinnerEntry(
    frm,
    label="Currency",
    value=1234.56,
    value_format="currency",
).grid()

bs.SpinnerEntry(
    frm,
    label="Fixed Point",
    value=15422354,
    value_format="fixedPoint",
).grid()

bs.SpinnerEntry(
    frm,
    label="Percent",
    value=0.35,
    value_format="percent",
).grid()

bs.SpinnerEntry(
    frm,
    label="Rate",
    value=0.0875,
    value_format={"type": "percent", "precision": 1}
).grid()

app.mainloop()
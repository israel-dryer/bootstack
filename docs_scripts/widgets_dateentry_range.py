from datetime import date
import bootstack as bs

app = bs.App()

frm = bs.PackFrame(app, direction="vertical", gap=12, padding=16)
frm.pack(fill="x")

bs.DateEntry(
    frm,
    label="Report period",
    selection_mode="range",
    start_date=date(2025, 1, 1),
    end_date=date(2025, 3, 31),
).pack(fill="x")

bs.DateEntry(
    frm,
    label="Booking window",
    selection_mode="range",
    value_format="shortDate",
    min_date=date.today(),
).pack(fill="x")

app.mainloop()
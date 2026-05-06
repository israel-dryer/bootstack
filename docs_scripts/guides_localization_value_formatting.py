import bootstack as bs
from bootstack import LV
from datetime import date

app = bs.App(title="Formatting", minsize=(400, 250), settings=bs.AppSettings(locale="de_DE"))

# Currency (uses locale's currency symbol and conventions)
bs.Label(app, text=LV(1234.56, "currency")).pack(pady=10)
# → "1.234,56 €" in de_DE; "$1,234.56" in en_US

# Decimal (locale-aware separators)
bs.Label(app, text=LV(1234567.89, "decimal")).pack()
# → "1.234.567,89" in de_DE

# Percent
bs.Label(app, text=LV(0.875, "percent")).pack()
# → "87,5 %" in de_DE

# Short date
bs.Label(app, text=LV(date.today(), "shortDate")).pack()
# → "05.05.26" in de_DE; "5/5/26" in en_US

# Long date
bs.Label(app, text=LV(date.today(), "longDate")).pack()
# → "5. Mai 2026" in de_DE; "May 5, 2026" in en_US

app.mainloop()
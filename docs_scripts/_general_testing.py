import bootstack as bs
from bootstack import MessageCatalog
from datetime import date

app = bs.App(title="Switcher", minsize=(400, 200), settings=bs.AppSettings(locale="en_US"))

bs.Label(app, text=1234.56,      value_format="currency", font="heading-md").pack(pady=10)
bs.Label(app, text=date.today(), value_format="longDate").pack()

bar = bs.PackFrame(app, direction="horizontal", gap=8)
bar.pack(pady=10)
bs.Button(bar, text="English", command=lambda: MessageCatalog.locale("en_US")).pack(side="left")
bs.Button(bar, text="EspaÃ±ol", command=lambda: MessageCatalog.locale("es_ES")).pack(side="left")
bs.Button(bar, text="Deutsch", command=lambda: MessageCatalog.locale("de_DE")).pack(side="left")

app.mainloop()
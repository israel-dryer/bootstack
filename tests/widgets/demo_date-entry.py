import bootstack as bs
from bootstack import DateEntry


app = bs.App()

de = DateEntry()
de.pack(padx=20, pady=20)
de = DateEntry(accent='info')
de.pack(padx=20, pady=20)


app.mainloop()

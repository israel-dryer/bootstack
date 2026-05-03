import bootstack as bs
from bootstack import NumericEntry


app = bs.Window()


ne = NumericEntry(app, accent='danger')
ne.pack(padx=20, pady=20)


app.mainloop()

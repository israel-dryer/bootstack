import bootstack as ttk
from bootstack import NumericEntry


app = ttk.Window()


ne = NumericEntry(app, accent='danger')
ne.pack(padx=20, pady=20)


app.mainloop()

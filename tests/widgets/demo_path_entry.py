import bootstack as ttk
from bootstack import PathEntry

app = ttk.Window()


pe = PathEntry(label="Manager Files", accent='success')
pe.pack(fill='x', padx=20, pady=20)

pe.on_changed(lambda e: print(e.data))


app.mainloop()

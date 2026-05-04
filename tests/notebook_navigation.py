import bootstack as bs


app = bs.Window()

nb = bs.Notebook(app)
f1 = nb.add(text="Options", key="options", sticky="nsew", width=300, height=300)
bs.Button(f1, text="On Frame 1").pack(padx=20, pady=20)

f2 = nb.add(text="Configuration", key="configuration", sticky="nsew")
bs.Button(f2, text="On Frame 2", command=lambda: nb.select("options")).pack(padx=20, pady=20)

nb.pack(fill='both', expand=True)

nb.on_tab_changed(print)

app.mainloop()
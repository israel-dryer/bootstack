import bootstack as bs

app = bs.App(title="Gallery", size=(560, 420))

gallery = bs.GridFrame(app, columns=4, gap=8, padding=12,
                       sticky_items="nsew", auto_flow="row-dense")
gallery.pack(fill="both", expand=True)

# Make each row stretch evenly. Rows are created on demand by auto-flow,
# so we configure weights on the GridFrame after-the-fact.
for r in range(3):
    gallery.configure_row(r, weight=1)
for c in range(4):
    gallery.configure_column(c, weight=1)

bs.Card(gallery).grid()
bs.Card(gallery).grid(columnspan=2)   # wide tile
bs.Card(gallery).grid()
bs.Card(gallery).grid(rowspan=2)      # tall tile
bs.Card(gallery).grid()
bs.Card(gallery).grid()
bs.Card(gallery).grid(columnspan=2)
bs.Card(gallery).grid()

app.mainloop()
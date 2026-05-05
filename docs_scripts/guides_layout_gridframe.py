import bootstack as bs

app = bs.App()

grid = bs.GridFrame(app, columns=["auto", 1], gap=(12, 6), padding=12, sticky_items="e")
grid.pack(fill="both", expand=True)

# Auto-placement: wraps to next row after filling columns
bs.Label(grid, text="Name").grid()
bs.Entry(grid).grid()
bs.Label(grid, text="Email").grid()
bs.Entry(grid).grid()
bs.Button(grid, text="Save", accent="primary").grid(columnspan=2)

app.mainloop()
import bootstack as bs


with bs.App(title="Bootstack Demo") as app:
    select = bs.Select(["One", "Two", "Three"])
    select.on_change(print)

app.mainloop()
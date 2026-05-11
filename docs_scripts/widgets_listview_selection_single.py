import bootstack as bs

app = bs.App(size=(400, 350))

files = [
    {
        "id": i,
        "text": f"Item {i}",
    }
    for i in range(1000)
]

lv = bs.ListView(
    app,
    items=files,
    selection_mode="single",
    show_selection_controls=True,
    show_separator=True
)
lv.pack(fill="both", expand=True, padx=20, pady=20)

app.mainloop()
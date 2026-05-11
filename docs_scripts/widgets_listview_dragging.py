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
    accent="success",
    enable_dragging=True,
    enable_removing=True,
)
lv.pack(fill="both", expand=True, padx=20, pady=20)

app.mainloop()
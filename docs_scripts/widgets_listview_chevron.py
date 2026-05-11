import bootstack as bs

app = bs.App(size=(400, 350))

files = [
    {
        "id": i,
        "title": f"Item {i}",
        "text": f"This is the description of item {i}"
    }
    for i in range(1000)
]

lv = bs.ListView(
    app,
    items=files,
    show_chevron=True
)
lv.pack(fill="both", expand=True, padx=20, pady=20)

app.mainloop()
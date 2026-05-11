import bootstack as bs

app = bs.App()

items = [
    {"id": 1, "title": "Item 1", "text": "Description 1"},
    {"id": 2, "title": "Item 2", "text": "Description 2"},
    {"id": 3, "title": "Item 3", "text": "Description 3"},
    {"id": 4, "title": "Item 4", "text": "Description 4"},
]

lv = bs.ListView(
    app,
    items=items,
    striped=True,
    striped_background="background[+1]",
    show_separator=True,
    scrollbar_visibility="always",   # or 'never' (mousewheel only)
    density="compact",               # 'default' or 'compact'
)
lv.pack(fill="both", expand=True, padx=20, pady=20)

app.mainloop()
import bootstack as bs

app = bs.App(title="Readings", size=(720, 360))

bs.TableView(
    app,
    columns=[
        {"text": "ID",       "key": "run_id",  "width": 90},
        {"text": "Channel",  "key": "channel", "width": 90,  "anchor": "center"},
        {"text": "Reading",  "key": "reading", "width": 100, "anchor": "e"},
        {"text": "Status",   "key": "status",  "width": 100, "anchor": "center"},
    ],
    rows=[
        ("R-1042", "CH-1", "1.0438", "Pass"),
        ("R-1043", "CH-2", "0.8794", "Warning"),
        ("R-1044", "CH-3", "1.2104", "Pass"),
        ("R-1045", "CH-4", "2.1583", "Fail"),
    ],
    page_size=25,
).pack(fill="both", expand=True, padx=12, pady=12)

app.mainloop()
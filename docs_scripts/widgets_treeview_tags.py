import bootstack as bs

app = bs.App()

records = [
    ("Alice", "Johnson", "alice.johnson@example.com", "active"),
    ("Bob", "Smith", "bob.smith@example.com", "active"),
    ("Carol", "Williams", "carol.williams@example.com", "stale"),
    ("David", "Brown", "david.brown@example.com", "active"),
    ("Emma", "Davis", "emma.davis@example.com"),
    ("Frank", "Miller", "frank.miller@example.com", "stale"),
    ("Grace", "Wilson", "grace.wilson@example.com"),
    ("Henry", "Moore", "henry.moore@example.com"),
    ("Irene", "Taylor", "irene.taylor@example.com"),
    ("Jack", "Anderson", "jack.anderson@example.com"),
]

tree = bs.TreeView(
    app,
    columns=("first", "last", "email", "status"),
    show="headings",
    height=8,
).pack()

tree.heading("first", text="First Name")
tree.heading("last",  text="Last Name")
tree.heading("email", text="Email")
tree.heading("status", text="Status")

tree.column("first", width=120)
tree.column("last",  width=120)
tree.column("email", width=240, stretch=True)
tree.column("status", anchor="center")

tree.tag_configure("ok",      background="#d4edda", foreground="#155724")
tree.tag_configure("warning", background="#fff3cd", foreground="#856404")
tree.tag_configure("error",   background="#f8d7da", foreground="#721c24")

for row in records:
    tag = {"active": "ok", "stale": "warning"}.get(row[-1], "error")
    tree.insert("", "end", values=row, tags=(tag,))

app.mainloop()
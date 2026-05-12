import bootstack as bs

app = bs.App()

records = [
    ("Alice", "Johnson", "alice.johnson@example.com"),
    ("Bob", "Smith", "bob.smith@example.com"),
    ("Carol", "Williams", "carol.williams@example.com"),
    ("David", "Brown", "david.brown@example.com"),
    ("Emma", "Davis", "emma.davis@example.com"),
    ("Frank", "Miller", "frank.miller@example.com"),
    ("Grace", "Wilson", "grace.wilson@example.com"),
    ("Henry", "Moore", "henry.moore@example.com"),
    ("Irene", "Taylor", "irene.taylor@example.com"),
    ("Jack", "Anderson", "jack.anderson@example.com"),
]

tree = bs.TreeView(
    app,
    columns=("first", "last", "email"),
    show="headings",
    height=8,
).pack()

tree.heading("first", text="First Name")
tree.heading("last",  text="Last Name")
tree.heading("email", text="Email")

tree.column("first", width=120)
tree.column("last",  width=120)
tree.column("email", width=240, stretch=True)

for row in records:
    tree.insert("", "end", values=row)

app.mainloop()
import bootstack as bs

with bs.App(title="Sign In") as app:
    with bs.Grid(columns=["auto", 1], gap=(12, 6), sticky_items="ew", padding=16):
        bs.Label("Name:")
        bs.TextField(placeholder="Full name")
        bs.Label("Email:")
        bs.TextField(placeholder="email@example.com")
        bs.Label("Role:")
        bs.Select(options=["Admin", "User", "Viewer"], value="User")
        bs.Button("Submit", accent="primary", columnspan=2)

app.run()

import bootstack as bs

with bs.App(title="Hello", padding=16, gap=16, theme="dark") as app:
    bs.Label("Hello from bootstack!")
    bs.Button("Primary", accent="primary")
    bs.Button("Success", accent="success")
    bs.Button("Danger Outline", accent="danger", variant="outline")

app.run()

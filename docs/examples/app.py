import bootstack as bs

with bs.App(title="Bootstack", size=(560, 400), padding=24, gap=14) as app:
    bs.Label("Welcome to bootstack", font="heading-lg")
    bs.Label(
        "Build native desktop apps in pure Python.",
        font="body",
        accent="secondary",
    )
    bs.TextField(label="Project name", value="my-app")
    with bs.HStack(gap=8):
        bs.Button("Create", accent="primary")
        bs.Button("Cancel", variant="outline", on_click=app.close)
app.run()

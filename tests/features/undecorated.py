import bootstack as bs

with bs.App(size=(500, 500), undecorated=True) as app:
    bs.Button("Hello World")

app.run()

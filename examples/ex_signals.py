import bootstack as bs

with bs.App(title="Reactive Signals", size=(400, 180)) as app:
    name = bs.Signal("World")
    with bs.VStack(padding=20, gap=10):
        bs.Label("Live preview:", font="caption", accent="secondary")
        bs.Label(textsignal=name, font="heading-md[bold]", accent="primary")
        bs.TextField(placeholder="Type a name…", textsignal=name)

app.run()

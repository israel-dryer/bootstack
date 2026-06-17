import bootstack as bs

with bs.App(title="Window demo", size=(360, 220), padding=24, gap=12) as app:

    def open_preferences():
        win = bs.Window(title="Preferences", size=(420, 300), padding=24, gap=14)
        with win:
            bs.Label("Preferences", font="heading-md")
            bs.Switch("Enable notifications", value=True)
            bs.Select(label="Theme", options=["System", "Light", "Dark"], value="System")
            with bs.Row(gap=8):
                bs.Button("Cancel", variant="outline", on_click=win.close)
                bs.Button("Save", accent="primary", on_click=win.close)
        win.show()

    bs.Label("Settings", font="heading-lg")
    bs.Button("Open preferences…", accent="primary", on_click=open_preferences)
app.run()

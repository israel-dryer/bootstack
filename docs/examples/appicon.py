import bootstack as bs
from bootstack.images import AppIcon

# An AppIcon is a glyph on a rounded, colored tile. Pass it as `icon=` to give a
# window its title-bar / taskbar icon — no .ico file needed. Colors accept theme
# tokens ("primary", "info", ...) or hex strings.
launcher_icon = AppIcon("rocket", background="primary")

with bs.App(title="Launcher", size=(420, 340), icon=launcher_icon, padding=24, gap=12) as app:

    # Show the same icon inside the app (e.g. a header / about panel).
    bs.Label(image=launcher_icon.to_image(96, tiled=True))
    bs.Label("Launcher", font="heading-lg")
    bs.Label("Ready for liftoff.", accent="secondary")

    def open_about():
        about_icon = AppIcon("info-circle", background="info")
        # A secondary Window carries its own AppIcon and opens over the app.
        with bs.Window(title="About", size=(300, 220), parent=app,
                       icon=about_icon, padding=20, gap=8) as win:
            bs.Label(image=about_icon.to_image(64, tiled=True))
            bs.Label("About Launcher", font="heading-md")
            bs.Label("A tiny demo.", accent="secondary")
        win.show(anchor_to=app, anchor_point="center", window_point="center")

    bs.Button("About…", accent="primary", on_click=open_about)

app.run()

import bootstack as bs


def hero():
    with bs.App(title="Accordion", minsize=(720, 1), padding=20) as app:
        acc = bs.Accordion()
        with acc.add("Introduction", expanded=True):
            bs.Label("Only one section can be open at a time.")
            bs.Label("Opening another collapses this one.")
        with acc.add("Details"):
            bs.Label("Opening this collapses Introduction.")
        with acc.add("Summary"):
            bs.Label("Third section body.")
    app.run()


def accent():
    with bs.App(title="Accordion — Accent", minsize=(720, 1), padding=20) as app:
        acc = bs.Accordion(accent="primary")
        with acc.add("Features", expanded=True):
            bs.Label("Feature list.")
        with acc.add("Pricing"):
            bs.Label("Pricing details.")
    app.run()


def icons():
    with bs.App(title="Accordion — Icons", minsize=(720, 1), padding=20) as app:
        acc = bs.Accordion(accent="primary")
        with acc.add("Documents", icon="folder", expanded=True):
            bs.Label("PDF reports, spreadsheets, and presentations.")
        with acc.add("Images", icon="image"):
            bs.Label("Photos and exported graphics.")
        with acc.add("Music", icon="file-music"):
            bs.Label("Audio files and playlists.")
    app.run()


SCENES = {
    "hero":   hero,
    "accent": accent,
    "icons":  icons,
}

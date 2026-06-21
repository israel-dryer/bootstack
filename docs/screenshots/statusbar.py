import bootstack as bs


def hero():
    with bs.App(title="report.md — Editor", size=(720, 320), padding=0) as app:
        app._capture_full_window = True
        with bs.Column(grow=True, horizontal="stretch", padding=24, gap=10):
            bs.Label("Q3 Summary", font="heading-lg")
            bs.Label("Draft the quarterly report and share it with the team.")
            bs.Label("- Revenue up 18% over Q2", font="body")
            bs.Label("- Two new enterprise accounts", font="body")
        sb = bs.StatusBar(horizontal="stretch")
        sb.add_text("Ready", icon="check-circle")
        sb.add_text("Ln 12, Col 5", side="right")
        sb.add_text("Spaces: 4", side="right")
        sb.add_text("UTF-8", side="right")
        sb.add_text("main", icon="git", side="right")
    app.run()


def segments():
    with bs.App(title="StatusBar — Segments", minsize=(720, 1), padding=0) as app:
        sb = bs.StatusBar(horizontal="stretch")
        sb.add_text("Ready", icon="check-circle")
        sb.add_text("Errors: 0", icon="x-circle", side="right")
        sb.add_text("Warnings: 2", icon="exclamation-triangle", side="right")
        sb.add_text("UTF-8", side="right")
        sb.add_text("main", icon="git", side="right")
    app.run()


def surface():
    with bs.App(title="StatusBar — Surface", minsize=(720, 1), padding=8) as app:
        sb = bs.StatusBar(horizontal="stretch", surface="card")
        sb.add_text("Card surface", icon="layers")
        sb.add_text("3 warnings", icon="exclamation-triangle", side="right")
        sb.add_text("main", icon="git", side="right")
    app.run()


def embedding():
    with bs.App(title="StatusBar — Embedding", minsize=(720, 1), padding=0) as app:
        sb = bs.StatusBar(horizontal="stretch")
        sb.add_text("Syncing", icon="arrow-repeat")
        bs.ProgressBar(parent=sb, value=65)
        sb.add_text("main", icon="git", side="right")
    app.run()


SCENES = {
    "hero":      hero,
    "segments":  segments,
    "surface":   surface,
    "embedding": embedding,
}

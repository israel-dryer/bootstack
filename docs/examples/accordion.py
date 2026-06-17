import bootstack as bs

with bs.App(title="Accordion", size=(680, 950), padding=20, gap=16) as app:

    # ── Single open (default) ─────────────────────────────────────────────────
    with bs.Column(gap=0, horizontal="stretch"):
        bs.Label("Single open (default)", font="heading-md")

    acc = bs.Accordion()
    with acc.add("Introduction", expanded=True):
        bs.Label("Only one section can be open at a time.")
        bs.Label("Opening another collapses this one.")
    with acc.add("Details"):
        bs.Label("Opening this collapses Introduction.")
    with acc.add("Summary"):
        bs.Label("Third section body.")

    # ── Multiple open ─────────────────────────────────────────────────────────
    with bs.Column(gap=0, horizontal="stretch"):
        bs.Label("allow_multiple=True", font="heading-md")

    acc2 = bs.Accordion(allow_multiple=True)
    with acc2.add("Section A", expanded=True):
        bs.Label("Multiple sections can be open simultaneously.")
    with acc2.add("Section B", expanded=True):
        bs.Label("A and B both start expanded.")
    with acc2.add("Section C"):
        bs.Label("C starts collapsed.")

    # ── Accent ────────────────────────────────────────────────────────────────
    with bs.Column(gap=0, horizontal="stretch"):
        bs.Label("accent=", font="heading-md")

    with bs.Accordion(accent='primary').add('Primary', expanded=True):
        bs.Label("All headers share the same accent selection color.")

    # ── Icons ────────────────────────────────────────────────────────────────
    with bs.Column(gap=0, horizontal="stretch"):
        bs.Label("icon=", font="heading-md")

    bicon = bs.Accordion(accent='info')
    with bicon.add('Documents', icon='folder'):
        bs.Label("Documents here")
    with bicon.add('Images', icon='image'):
        bs.Label("Images here")
    with bicon.add('Music', icon='file-music'):
        bs.Label("Music here")

app.run()
import bootstack as bs

with bs.App(title="CommandBar demo", minsize=(700, 300), padding=16) as app:

    with bs.VStack(fill="both", expand=True, gap=16):

        # ── Default density ────────────────────────────────────────────────
        with bs.VStack(fill="x", padding=(16, 12, 16, 4)):
            bs.Label("Default", font="heading-sm")

            tb1 = bs.CommandBar(fill="x")
            tb1.add_label("Editor", font="heading-md")
            tb1.add_separator()
            tb1.add_button("New", icon="file-earmark-plus")
            tb1.add_button("Open", icon="folder2-open")
            tb1.add_button("Save", icon="floppy")
            tb1.add_spacer()
            tb1.add_theme_toggle()
            tb1.add_button(icon="gear")

        # ── Compact density ────────────────────────────────────────────────
        with bs.VStack(fill="x", padding=(16, 12, 16, 4)):
            bs.Label("Compact density", font="heading-sm")

            tb2 = bs.CommandBar(fill="x", density="compact")
            tb2.add_button(icon="type-bold")
            tb2.add_button(icon="type-italic")
            tb2.add_button(icon="type-underline")
            tb2.add_separator()
            tb2.add_button(icon="text-left")
            tb2.add_button(icon="text-center")
            tb2.add_button(icon="text-right")
            tb2.add_separator()
            tb2.add_button(icon="list-ul")
            tb2.add_button(icon="list-ol")
            tb2.add_spacer()
            tb2.add_button(icon="arrow-counterclockwise")
            tb2.add_button(icon="arrow-clockwise")

        # ── Accents and variants ───────────────────────────────────────────
        with bs.VStack(fill="x", padding=(16, 12, 16, 4)):
            bs.Label("Accents and variants", font="heading-sm")
            tb3 = bs.CommandBar(fill="x")
            tb3.add_button("Publish", icon="cloud-upload", accent="primary")
            tb3.add_button("Preview", icon="eye")
            tb3.add_button("Draft", icon="pencil")
            tb3.add_spacer()
            tb3.add_button("Discard", icon="trash", accent="danger")

        # ── Border & Surface ────────────────────────────────────────────────
        with bs.VStack(fill="x", padding=(16, 12, 16, 4)):
            bs.Label("Border and Surface", font="heading-sm")

            tb1 = bs.CommandBar(fill="x", show_border=True, surface="card")
            tb1.add_button("New", icon="file-earmark-plus")
            tb1.add_button("Open", icon="folder2-open")
            tb1.add_button("Save", icon="floppy")


app.run()
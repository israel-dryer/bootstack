import bootstack as bs


def hero():
    with bs.App(title="CommandBar", size=(720, 50), padding=0) as app:
        tb = bs.CommandBar(fill="x")
        tb.add_button("New",  icon="file-earmark-plus")
        tb.add_button("Open", icon="folder2-open")
        tb.add_button("Save", icon="floppy")
        tb.add_separator()
        tb.add_button(icon="type-bold")
        tb.add_button(icon="type-italic")
        tb.add_button(icon="type-underline")
        tb.add_separator()
        tb.add_button(icon="text-left")
        tb.add_button(icon="text-center")
        tb.add_button(icon="text-right")
        tb.add_spacer()
        tb.add_button(icon="circle-half")
        tb.add_button(icon="gear")
    app.run()


def separators():
    with bs.App(title="CommandBar — Separators", minsize=(720, 1), padding=0) as app:
        tb = bs.CommandBar(fill="x")
        tb.add_button("Bold",   icon="type-bold")
        tb.add_button("Italic", icon="type-italic")
        tb.add_separator()
        tb.add_button("Align left",   icon="text-left")
        tb.add_button("Align center", icon="text-center")
        tb.add_button("Align right",  icon="text-right")
        tb.add_spacer()
        tb.add_button(icon="gear")
    app.run()


def density():
    with bs.App(title="CommandBar — Density", minsize=(720, 1), padding=0) as app:
        tb = bs.CommandBar(fill="x", density="compact")
        tb.add_button(icon="type-bold")
        tb.add_button(icon="type-italic")
        tb.add_button(icon="type-underline")
        tb.add_separator()
        tb.add_button(icon="text-left")
        tb.add_button(icon="text-center")
        tb.add_button(icon="text-right")
        tb.add_separator()
        tb.add_button(icon="list-ul")
        tb.add_button(icon="list-ol")
        tb.add_spacer()
        tb.add_button(icon="arrow-counterclockwise")
        tb.add_button(icon="arrow-clockwise")
    app.run()


def accents():
    with bs.App(title="CommandBar — Accents", minsize=(720, 1), padding=0) as app:
        tb = bs.CommandBar(fill="x")
        tb.add_button("Publish", icon="cloud-upload", accent="primary")
        tb.add_button("Preview", icon="eye")
        tb.add_button("Draft",   icon="pencil")
        tb.add_spacer()
        tb.add_button("Discard", icon="trash", accent="danger")
    app.run()


def surface():
    with bs.App(title="CommandBar — Surface", minsize=(720, 1), padding=8) as app:
        tb = bs.CommandBar(fill="x", show_border=True, surface="card")
        tb.add_button("New",  icon="file-earmark-plus")
        tb.add_button("Open", icon="folder2-open")
        tb.add_button("Save", icon="floppy")
        tb.add_spacer()
        tb.add_button(icon="gear")
    app.run()


SCENES = {
    "hero":       hero,
    "separators": separators,
    "density":    density,
    "accents":    accents,
    "surface":    surface,
}

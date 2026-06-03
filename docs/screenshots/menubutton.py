import bootstack as bs


def hero():
    with bs.App(title="MenuButton", size=(260, 230), padding=20) as app:
        with bs.HStack(fill="x"):
            mb1 = bs.MenuButton("Actions")
            mb1.add_item("Edit",      icon="pencil")
            mb1.add_item("Duplicate", icon="copy")
            mb1.add_item("Archive",   icon="archive")
            mb1.add_separator()
            mb1.add_item("Delete",    icon="trash")

    app.tk.after(850, mb1.show_menu)
    app.run()


def shortcuts():
    with bs.App(title="MenuButton — Shortcuts", size=(220, 230), padding=20) as app:
        with bs.HStack(fill="x"):
            mb1 = bs.MenuButton("File", icon="folder2")
            mb1.add_item("New",  icon="file-earmark-plus", shortcut="Mod+N")
            mb1.add_item("Open", icon="folder2-open",       shortcut="Mod+O")
            mb1.add_item("Save", icon="floppy",             shortcut="Mod+S")
            mb1.add_separator()
            mb1.add_item("Exit", icon="box-arrow-right")

    app.tk.after(850, mb1.show_menu)
    app.run()


def check_radio():
    with bs.App(title="MenuButton — Check and Radio", size=(400, 220), padding=20) as app:
        with bs.HStack(gap=80, anchor_items="n", fill="x"):
            mb_view = bs.MenuButton("View", icon="eye")
            mb_view.add_check_item("Show toolbar",   value=True)
            mb_view.add_check_item("Show sidebar",   value=True)
            mb_view.add_check_item("Show status bar")

            mb_zoom = bs.MenuButton("Zoom")
            mb_zoom.add_radio_item("100%", value=100)
            mb_zoom.add_radio_item("150%", value=150, selected=True)
            mb_zoom.add_radio_item("200%", value=200)

    def open_both():
        mb_view.show_menu()
        mb_zoom.show_menu()

    app.tk.after(850, open_both)
    app.run()


def variants():
    with bs.App(title="MenuButton — Variants", size=(480, 80), padding=20) as app:
        with bs.HStack(gap=8, anchor_items="center", fill="x"):
            for variant in ("solid", "outline", "ghost"):
                mb = bs.MenuButton(variant.capitalize(), accent="primary", variant=variant)
                mb.add_item("Option A")
                mb.add_item("Option B")

    app.run()


def accents():
    with bs.App(title="MenuButton — Accents", size=(700, 80), padding=20) as app:
        with bs.HStack(gap=8, anchor_items="center", fill="x"):
            for accent in ("primary", "secondary", "success", "warning", "danger"):
                mb = bs.MenuButton(accent.capitalize(), accent=accent)
                mb.add_item("Option A")
                mb.add_item("Option B")

    app.run()


def states():
    with bs.App(title="MenuButton — States", size=(460, 80), padding=20) as app:
        with bs.HStack(gap=8, anchor_items="center", fill="x"):
            mb_on = bs.MenuButton("Enabled")
            mb_on.add_item("Option A")
            mb_on.add_item("Option B")

            mb_off = bs.MenuButton("Disabled", disabled=True)
            mb_off.add_item("Option A")

            mb_acc = bs.MenuButton("Disabled", accent="primary", variant="outline", disabled=True)
            mb_acc.add_item("Option A")

    app.run()


def icon_only():
    with bs.App(title="MenuButton — Icon-Only", size=(320, 80), padding=20) as app:
        with bs.HStack(gap=8, anchor_items="center", fill="x"):
            for icon in ("three-dots", "three-dots-vertical", "grid", "gear"):
                mb = bs.MenuButton(icon=icon, show_arrow=False)
                mb.add_item("Option A")
                mb.add_item("Option B")
                mb.add_item("Option C")

    app.run()


SCENES = {
    "hero":        hero,
    "shortcuts":   shortcuts,
    "check-radio": check_radio,
    "variants":    variants,
    "accents":     accents,
    "states":      states,
    "icon-only":   icon_only,
}

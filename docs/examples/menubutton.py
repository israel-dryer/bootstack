"""MenuButton — full feature demo.

Demonstrates basic usage, accent colors, style variants, icons, icon-only
mode, density, and disabled state.

Run with:
    python docs/examples/menubutton.py
"""

import bootstack as bs


def _make_file_menu(parent):
    mb = bs.MenuButton("File", icon="folder2", parent=parent)
    mb.add_item("New",   icon="file-earmark-plus", shortcut="Ctrl+N")
    mb.add_item("Open",  icon="folder2-open",       shortcut="Ctrl+O")
    mb.add_item("Save",  icon="floppy",             shortcut="Ctrl+S")
    mb.add_separator()
    mb.add_item("Exit",  icon="box-arrow-right")
    return mb


def _make_view_menu(parent):
    mb = bs.MenuButton("View", icon="eye", parent=parent)
    mb.add_check_item("Show toolbar",  value=True)
    mb.add_check_item("Show sidebar",  value=True)
    mb.add_check_item("Show status bar")
    mb.add_separator()
    mb.add_item("Zoom in",  icon="zoom-in",  shortcut="Ctrl++")
    mb.add_item("Zoom out", icon="zoom-out", shortcut="Ctrl+-")
    return mb


with bs.App(title="MenuButton Demo", padding=20, gap=16) as app:

    # Basic
    bs.Label("Basic", font="heading-sm")
    with bs.Row(gap=8):
        _make_file_menu(None)
        _make_view_menu(None)

    # Accents
    bs.Label("Accent Colors", font="heading-sm")
    with bs.Row(gap=8):
        for accent in ("primary", "secondary", "success", "warning", "danger"):
            mb = bs.MenuButton(accent.capitalize(), accent=accent)
            mb.add_item("Option A")
            mb.add_item("Option B")

    # Style variants
    bs.Label("Style Variants", font="heading-sm")
    with bs.Row(gap=8):
        for variant in ("solid", "outline", "ghost"):
            mb = bs.MenuButton(variant.capitalize(), accent="primary", variant=variant)
            mb.add_item("Option A")
            mb.add_item("Option B")

    # With icon
    bs.Label("With Icon", font="heading-sm")
    with bs.Row(gap=8):
        mb = bs.MenuButton("Share", icon="share")
        mb.add_item("Copy link",    icon="link-45deg")
        mb.add_item("Send email",   icon="envelope")
        mb.add_item("Export PDF",   icon="file-pdf")

        mb2 = bs.MenuButton(icon="gear", show_arrow=False)
        mb2.add_item("Settings",  icon="sliders")
        mb2.add_item("Profile",   icon="person")
        mb2.add_separator()
        mb2.add_item("Sign out",  icon="box-arrow-right", disabled=True)

    # Icon-only (inferred — no label provided)
    bs.Label("Icon-Only", font="heading-sm")
    with bs.Row(gap=8):
        for icon in ("three-dots", "three-dots-vertical", "grid"):
            mb = bs.MenuButton(icon=icon, show_arrow=False)
            mb.add_item("Option A")
            mb.add_item("Option B")

    # Density
    bs.Label("Density", font="heading-sm")
    with bs.Row(gap=8, vertical_items="center"):
        mb_d = bs.MenuButton("Default", density="default")
        mb_d.add_item("Option A")
        mb_d.add_item("Option B")

        mb_c = bs.MenuButton("Compact", density="compact")
        mb_c.add_item("Option A")
        mb_c.add_item("Option B")

    # Disabled
    bs.Label("Disabled", font="heading-sm")
    with bs.Row(gap=8):
        mb = bs.MenuButton("Actions", disabled=True)
        mb.add_item("Option A")

        mb2 = bs.MenuButton("Primary", accent="primary", variant="outline", disabled=True)
        mb2.add_item("Option A")

app.run()

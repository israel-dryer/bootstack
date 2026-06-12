"""Visual test for ButtonGroup, ContextMenu, MenuButton, and Toolbar."""
from bootstack import (
    App, VStack, HStack, Label, Button, Separator,
    ButtonGroup, ContextMenu, MenuButton, CommandBar,
)


def on_select(data):
    print("selected:", data)


with App(title="Action / Toolbar", minsize=(700, 500), padding=16, gap=12) as app:

    # --- Toolbar ---
    tb = CommandBar(draggable=False)
    tb.add_button(icon="house", on_click=lambda: print("home"))
    tb.add_button(icon="folder2-open", on_click=lambda: print("open"))
    tb.add_button(icon="floppy", on_click=lambda: print("save"))
    tb.add_separator()
    tb.add_button(icon="scissors", on_click=lambda: print("cut"))
    tb.add_button(icon="copy", on_click=lambda: print("copy"))
    tb.add_button(icon="clipboard", on_click=lambda: print("paste"))
    tb.add_spacer()
    tb.add_button(icon="question-circle", on_click=lambda: print("help"))

    Separator()

    # --- ButtonGroup ---
    Label("ButtonGroup (horizontal):")
    with HStack(gap=4):
        bg = ButtonGroup(accent="primary")
        bg.add("Day", key="day", on_click=lambda: print("day"))
        bg.add("Week", key="week", on_click=lambda: print("week"))
        bg.add("Month", key="month", on_click=lambda: print("month"))

    Label("ButtonGroup (vertical):")
    with HStack(gap=4):
        bg2 = ButtonGroup(orient="vertical", variant="outline", accent="primary")
        bg2.add("Option A", key="a")
        bg2.add("Option B", key="b")
        bg2.add("Option C", key="c")

    Separator()

    # --- MenuButton ---
    Label("MenuButton:")
    with HStack(gap=8):
        mb = MenuButton("File", on_select=on_select)
        mb.add_item("New", icon="file-earmark", shortcut="Ctrl+N", key="new",
                    on_click=lambda: print("new"))
        mb.add_item("Open...", icon="folder2-open", shortcut="Ctrl+O", key="open",
                    on_click=lambda: print("open"))
        mb.add_separator()
        mb.add_item("Save", icon="floppy", shortcut="Ctrl+S", key="save",
                    on_click=lambda: print("save"))
        mb.add_item("Exit", key="exit", on_click=lambda: print("exit"))

        mb2 = MenuButton("View", variant="outline")
        mb2.add_check_item("Status Bar", value=True, key="statusbar")
        mb2.add_check_item("Line Numbers", value=False, key="linenums")
        mb2.add_separator()
        mb2.add_item("Zoom In", shortcut="Ctrl++")
        mb2.add_item("Zoom Out", shortcut="Ctrl+-")

    Separator()

    # --- ContextMenu ---
    lbl = Label("Right-click me for a context menu", accent="primary")
    cm = ContextMenu(target=lbl, on_select=on_select)
    cm.add_item("Copy", icon="copy", shortcut="Ctrl+C", key="copy")
    cm.add_item("Paste", icon="clipboard", shortcut="Ctrl+V", key="paste")
    cm.add_separator()
    cm.add_item("Select All", shortcut="Ctrl+A", key="select_all")

app.run()

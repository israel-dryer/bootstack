"""Visual test for public AppShell and Window."""
from bootstack import (
    AppShell, Window,
    VStack, HStack, Label, Button, Separator, TextField, ToggleGroup,
)
from bootstack.signals import Signal


with AppShell(
    title="Public AppShell",
    size=(960, 640),
    nav_accent="primary",
) as shell:

    # Toolbar extras
    theme_sig = Signal("Light")

    def toggle_theme():
        import bootstack as bs
        bs.toggle_theme()

    shell.toolbar.add_button(icon="sun", command=toggle_theme)

    # --- Home page ---
    with shell.add_page("home", text="Home", icon="house"):
        with VStack(padding=24, gap=12, fill="both", expand=True):
            Label("Welcome", font="heading-lg")
            Label("This is the Home page.")
            Separator(fill="x")
            Button("Open Window", on_click=lambda: _open_window())

    # --- Inputs page ---
    with shell.add_page("inputs", text="Inputs", icon="input-cursor-text"):
        with VStack(padding=24, gap=10, fill="both", expand=True):
            Label("Text inputs", font="heading-md")
            name_sig = Signal("")
            TextField(text_signal=name_sig, label="Name", fill="x")
            Label("Toggle group:")
            tg = ToggleGroup(options=["Option A", "Option B", "Option C"])

    # --- Settings page (footer) ---
    with shell.add_page("settings", text="Settings", icon="gear", is_footer=True):
        with VStack(padding=24, gap=10, fill="both", expand=True):
            Label("Settings", font="heading-md")
            Label("Application settings go here.")

def _open_window():
    with Window(
        title="Details",
        size=(400, 280),
        modal=True,
        center_on_parent=True,
        padding=20,
        gap=10,
    ) as win:
        Label("Secondary Window", font="heading-md")
        Separator(fill="x")
        Label("This is a modal Window opened from a page.")
        with HStack(gap=8, anchor="e"):
            Button("Close", on_click=win.close)
    win.show()

shell.run()

"""Visual test for public GroupBox, SplitView, and PageStack widgets."""
from bootstack.widgets import (
    App, VStack, HStack, Label, Button, Separator,
    GroupBox, SplitView, PageStack, TextField, RadioGroup,
)
from bootstack.signals import Signal


def main():
    with App(title="GroupBox + SplitView + PageStack", minsize=(620, 560), padding=20, gap=16) as app:

        # --- GroupBox ---
        Label("GroupBox", font="heading-lg")
        with HStack(gap=12, fill="x"):
            with GroupBox("Personal Info", fill="x", expand=True):
                TextField(label="Name")
                TextField(label="Email")

            with GroupBox("Preferences", fill="x", expand=True):
                RadioGroup(
                    options=[("Light", "light"), ("Dark", "dark"), ("System", "system")],
                    value="system",
                )

        Separator(fill="x")

        # --- SplitView ---
        Label("SplitView — drag the sash to resize panes", font="heading-lg")
        sv = SplitView(orient="horizontal", fill="x")
        with sv.add(weight=1):
            with VStack(padding=8, gap=4, fill="both", expand=True):
                Label("Left pane", font="body[bold]")
                Label("weight=1")
        with sv.add(weight=2):
            with VStack(padding=8, gap=4, fill="both", expand=True):
                Label("Right pane", font="body[bold]")
                Label("weight=2 — starts wider")

        Separator(fill="x")

        # --- PageStack ---
        Label("PageStack — browser-style navigation", font="heading-lg")

        ps = PageStack(fill="x", expand=False)
        with ps.add("home"):
            with VStack(padding=12, gap=8, fill="x"):
                Label("Home Page", font="heading-lg")
                Label("Navigate using the buttons below.")

        with ps.add("profile"):
            with VStack(padding=12, gap=8, fill="x"):
                Label("Profile Page", font="heading-lg")
                TextField(label="Display name")

        with ps.add("settings"):
            with VStack(padding=12, gap=8, fill="x"):
                Label("Settings Page", font="heading-lg")
                RadioGroup(
                    options=[("Light", "light"), ("Dark", "dark")],
                    value="light",
                )

        ps.navigate("home")

        with HStack(gap=8, fill="x"):
            Button("← Back", variant="outline",
                   on_click=lambda: ps.back() if ps.can_back else None)
            Button("Home", on_click=lambda: ps.navigate("home"))
            Button("Profile", on_click=lambda: ps.navigate("profile"))
            Button("Settings", on_click=lambda: ps.navigate("settings"))
            Button("Forward →", variant="outline",
                   on_click=lambda: ps.forward() if ps.can_forward else None)

    app.run()


if __name__ == "__main__":
    main()
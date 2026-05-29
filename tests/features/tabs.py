"""Visual test for public Tabs widget."""
from bootstack.widgets.public import (
    App, VStack, HStack, Label, Button, Separator, TextField, Tabs,
)
from bootstack.signals import Signal


def main():
    with App(title="Tabs", minsize=(600, 400), padding=0, gap=0) as app:
        status = Signal("(no change yet)")

        # Horizontal tabs (default) — fills the window
        tabs = Tabs(fill="both", expand=True)

        with tabs.add("home", text="Home"):
            with VStack(padding=24, gap=12, fill="both", expand=True):
                Label("Welcome to the Home tab", font="heading-lg")
                Label("Select another tab to switch pages.")
                Separator(fill="x")
                with HStack(gap=8):
                    Button("Go to Settings", accent="primary",
                           on_click=lambda: tabs.select("settings"))
                    Button("Go to About", variant="outline",
                           on_click=lambda: tabs.select("about"))

        with tabs.add("settings", text="Settings"):
            with VStack(padding=24, gap=12, fill="both", expand=True):
                Label("Settings", font="heading-lg")
                TextField(label="Username")
                TextField(label="Email")
                Separator(fill="x")
                with HStack(gap=8):
                    Button("Save", accent="success")
                    Button("Reset", variant="ghost")

        with tabs.add("about", text="About"):
            with VStack(padding=24, gap=12, fill="both", expand=True):
                Label("About", font="heading-lg")
                Label("bootstack — batteries-included Python desktop UI framework.")
                Label("Public API — Tabs widget demo.")

        tabs.on_change(lambda e: status.set(f"active tab: {tabs.current}"))

        # Status bar at the bottom
        Separator(fill="x")
        with HStack(padding=(8, 12), gap=8, fill="x"):
            Label("Status:", font="body[bold]")
            Label(textsignal=status)


    # --- Vertical tabs demo ---
    with App(title="Tabs — vertical", minsize=(600, 350), padding=0, gap=0) as app2:
        tabs2 = Tabs(orient="vertical", fill="both", expand=True)

        with tabs2.add("dashboard", text="Dashboard"):
            with VStack(padding=24, gap=8, fill="both", expand=True):
                Label("Dashboard", font="heading-lg")
                Label("Vertical tab layout demo.")

        with tabs2.add("reports", text="Reports"):
            with VStack(padding=24, gap=8, fill="both", expand=True):
                Label("Reports", font="heading-lg")
                Label("Charts and summaries would go here.")

        with tabs2.add("users", text="Users"):
            with VStack(padding=24, gap=8, fill="both", expand=True):
                Label("Users", font="heading-lg")
                Label("User management would go here.")

    app.run()


if __name__ == "__main__":
    main()
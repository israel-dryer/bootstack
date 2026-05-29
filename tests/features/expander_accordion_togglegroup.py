"""Visual test for public Expander, Accordion, and ToggleGroup widgets."""
from bootstack.widgets.public import (
    App, VStack, HStack, Label, Button, Separator,
    Expander, Accordion, ToggleGroup, TextField,
)
from bootstack.signals import Signal


def main():
    with App(title="Expander + Accordion + ToggleGroup", minsize=(500, 100), padding=24, gap=16) as app:

        readout = Signal("(no change yet)")

        # Expander
        Label("Expander")
        with Expander("Settings", fill="x", expand=True):
            TextField(label="API key", mask_char="*")
            with HStack(gap=8):
                Button("Save", accent="primary", variant="outline")
                Button("Cancel", variant="outline")

        with Expander("Collapsed by default", expanded=False, fill="x", expand=True):
            Label("Hidden until expanded")

        Separator(fill="x")

        # Accordion
        Label("Accordion — single open at a time")
        acc = Accordion(fill="x", expand=True)
        with acc.add("Personal info"):
            TextField(label="Name")
            TextField(label="Email")
        with acc.add("Preferences", expanded=False):
            ToggleGroup(["Light", "Dark", "System"], value="System")
        with acc.add("Advanced", expanded=False):
            Label("Advanced settings go here")

        Separator(fill="x")

        # ToggleGroup — single
        Label("ToggleGroup — single select")
        tg = ToggleGroup(
            ["Day", "Week", "Month", "Year"],
            value="Week",
            accent="primary",
        )
        tg.on_change(lambda e: readout.set(f"view: {tg.value}"))

        # ToggleGroup — multi
        Label("ToggleGroup — multi select")
        tg2 = ToggleGroup(
            [("Bold", "bold"), ("Italic", "italic"), ("Underline", "underline")],
            mode="multi",
            value={"bold"},
        )
        tg2.on_change(lambda e: readout.set(f"format: {tg2.value}"))

        # ToggleGroup — vertical
        Label("ToggleGroup — vertical")
        ToggleGroup(["Option A", "Option B", "Option C"], orient="vertical", value="Option A")

        # Readout
        with HStack(gap=8, anchor_items="center"):
            Label("Last change:")
            Label(text_signal=readout, color="#0d6efd")

    app.run()


if __name__ == "__main__":
    main()

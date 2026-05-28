"""Visual test for public RadioGroup widget."""
from bootstack.widgets.public import App, VStack, HStack, RadioGroup, Label, Button
from bootstack.signals import Signal


def main():
    with App(title="RadioGroup — visual test", minsize=(480, 100), padding=24, gap=16) as app:

        selection = Signal("(none)")

        # Horizontal, string options
        Label("Horizontal — string options")
        rg1 = RadioGroup(["Small", "Medium", "Large"], value="Medium", accent="primary")
        rg1.on_change(lambda e: selection.set(f"Size: {rg1.value}"))

        # Horizontal, tuple options
        Label("Horizontal — (label, value) options")
        rg2 = RadioGroup(
            [("Option A", "a"), ("Option B", "b"), ("Option C", "c")],
            value="b",
        )
        rg2.on_change(lambda e: selection.set(f"Option: {rg2.value}"))

        # Vertical
        Label("Vertical orientation")
        RadioGroup(
            ["Red", "Green", "Blue"],
            orient="vertical",
            value="Green",
            accent="success",
        )

        # With group label
        Label("With label")
        RadioGroup(
            ["Daily", "Weekly", "Monthly"],
            label="Frequency",
            value="Weekly",
        )

        # Disabled
        Label("Disabled")
        RadioGroup(["Yes", "No"], value="Yes", disabled=True)

        # Signal-driven
        Label("Signal-driven")
        sig = Signal("b")
        with HStack(gap=12, anchor_items="center"):
            RadioGroup(
                [("Alpha", "a"), ("Beta", "b"), ("Gamma", "c")],
                signal=sig,
            )
            Button("→ Beta", on_click=lambda: sig.set("b"), variant="outline")

        # Last selection readout
        with HStack(gap=8, anchor_items="center"):
            Label("Last change:")
            Label(text_signal=selection, color="#0d6efd")

    app.run()


if __name__ == "__main__":
    main()

"""Visual test for public Select and NumericEntry widgets."""
from bootstack.widgets.public import (
    App, VStack, HStack, Label, Select, NumericEntry, Button
)
from bootstack.signals import Signal


def main():
    with App(title="Select + NumericEntry — visual test", minsize=(480, 100), padding=24, gap=14) as app:

        readout = Signal("(nothing committed yet)")

        # Basic select
        Label("Select — basic")
        sel = Select(["Apple", "Banana", "Cherry", "Date"], value="Banana", label="Fruit")
        sel.on_change(lambda e: readout.set(f"fruit: {sel.value}"))

        # Searchable
        Label("Select — searchable")
        Select(
            ["Python", "JavaScript", "Rust", "Go", "TypeScript", "C++"],
            label="Language",
            value="Python",
            searchable=True,
        )

        # Allow custom
        Label("Select — allow custom values")
        Select(["Option A", "Option B"], label="Custom allowed", allow_custom=True)

        # Disabled
        Label("Select — disabled")
        Select(["One", "Two", "Three"], value="Two", disabled=True)

        # NumericEntry — basic
        Label("NumericEntry — basic")
        num = NumericEntry(10, label="Quantity", min_value=0, max_value=100, step=5)
        num.on_change(lambda e: readout.set(f"qty: {num.value}"))

        # NumericEntry — no spin buttons
        Label("NumericEntry — no spin buttons")
        NumericEntry(3.14, label="Float value", step=0.1, show_spin_buttons=False)

        # NumericEntry — disabled
        Label("NumericEntry — disabled")
        NumericEntry(99, label="Disabled", disabled=True)

        # Inline controls
        with HStack(gap=8, anchor_items="center"):
            Button("−5", on_click=lambda: num.decrement(), variant="outline")
            Button("+5", on_click=lambda: num.increment(), variant="outline")

        # Readout
        with HStack(gap=8, anchor_items="center"):
            Label("Last committed:")
            Label(text_signal=readout, color="#0d6efd")

    app.run()


if __name__ == "__main__":
    main()

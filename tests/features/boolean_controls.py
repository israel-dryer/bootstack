"""Visual test for public Checkbox, Switch, and ToggleButton widgets."""
from bootstack.widgets.public import (
    App, VStack, HStack, Label, Checkbox, Switch, ToggleButton, Button
)
from bootstack.signals import Signal


def main():
    with App(title="Boolean controls — visual test", minsize=(480, 100), padding=24, gap=16) as app:

        status = Signal("(none changed yet)")

        def report(name):
            return lambda: status.set(f"{name} toggled")

        # Checkboxes
        Label("Checkbox")
        with HStack(gap=16):
            Checkbox("Default", on_change=report("Checkbox default"))
            Checkbox("Checked", value=True, on_change=report("Checkbox checked"))
            Checkbox("Primary", accent="primary", value=True)
            Checkbox("Disabled", disabled=True)
            Checkbox("Disabled on", value=True, disabled=True)

        # Switches
        Label("Switch")
        with HStack(gap=16):
            Switch("Default", on_change=report("Switch default"))
            Switch("On", value=True, on_change=report("Switch on"))
            Switch("Primary", accent="primary", value=True)
            Switch("Disabled", disabled=True)
            Switch("Disabled on", value=True, disabled=True)

        # Toggle buttons
        Label("ToggleButton")
        with HStack(gap=8):
            ToggleButton("Bold", accent="primary", on_change=report("Bold"))
            ToggleButton("Italic", on_change=report("Italic"))
            ToggleButton("Underline", value=True, on_change=report("Underline"))
            ToggleButton("Disabled", disabled=True)

        # Signal-driven checkbox
        Label("Signal-driven")
        sig = Signal(False)
        state_label_sig = Signal("off")
        def _flip():
            sig.set(not sig.get())
            state_label_sig.set("ON" if sig.get() else "off")
        with HStack(gap=12, anchor_items="center"):
            Checkbox("Controlled", signal=sig)
            Button("Flip", on_click=_flip, variant="outline")
            Label(text_signal=state_label_sig)

        # Last changed readout
        with HStack(gap=8, anchor_items="center"):
            Label("Last change:")
            Label(text_signal=status, color="#0d6efd")

    app.run()


if __name__ == "__main__":
    main()

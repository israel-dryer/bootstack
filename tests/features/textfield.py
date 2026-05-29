"""Visual test for public TextField widget."""
from bootstack import App, VStack, HStack, TextField, Label, Button
from bootstack.signals import Signal


def main():
    with App(title="TextField — visual test", minsize=(480, 100), padding=24, gap=12) as app:

        output = Signal("(waiting for input)")

        def on_committed(e):
            output.set(f"committed: {tf_basic.value!r}")

        # Basic text field — subscribe via .on_change()
        tf_basic = TextField(label="Name")
        tf_basic.on_change(on_committed)

        # With placeholder-style default value
        TextField("default text", label="Pre-filled")

        # Password field
        TextField(mask_char="*", label="Password")

        # Read-only
        TextField("cannot edit this", label="Read-only", read_only=True)

        # Disabled
        TextField("greyed out", label="Disabled", disabled=True)

        # Required — known issue: message area background may not match surface
        # on first validation trigger. Pre-existing bug in internal Field composite.
        TextField(label="Required field", required=True)

        # Committed value readout
        with HStack(gap=8, anchor_items="center"):
            Label("Last committed:")
            Label(text_signal=output, color="#0d6efd")

    app.run()


if __name__ == "__main__":
    main()
